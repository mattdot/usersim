"""Core UserSim class and main API."""

from typing import Optional, Dict, Any
from usersim.conversation import ConversationManager, ConversationError, MaxTurnsReachedError
from usersim.a2a_protocol import ConversationHistory


class ConversationResult:
    """Result of a UserSim conversation."""
    
    def __init__(
        self,
        outcome: str,
        turn_count: int,
        history: ConversationHistory,
        termination_reason: str,
        error: Optional[str] = None
    ):
        """Initialize conversation result.
        
        Args:
            outcome: The outcome ("success", "failure", "error")
            turn_count: Number of turns in the conversation
            history: The conversation history
            termination_reason: Why the conversation ended
            error: Optional error message if outcome is "error"
        """
        self.outcome = outcome
        self.turn_count = turn_count
        self.history = history
        self.termination_reason = termination_reason
        self.error = error
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary format."""
        return {
            "outcome": self.outcome,
            "turn_count": self.turn_count,
            "termination_reason": self.termination_reason,
            "error": self.error,
            "messages": [
                {
                    "role": msg.role,
                    "content": msg.content,
                    "metadata": msg.metadata
                }
                for msg in self.history.messages
            ]
        }


class UserSim:
    """Main UserSim class for running agent tests."""
    
    @staticmethod
    async def run(
        target: str,
        messages: list[str],
        max_turns: Optional[int] = None,
        timeout: Optional[float] = None
    ) -> ConversationResult:
        """Run a conversation with a target agent.
        
        This is a basic implementation for Step 1 that allows sending
        predefined messages to test the conversation loop.
        
        Args:
            target: URL to the target agent's Agent Card
            messages: List of messages to send
            max_turns: Maximum number of turns (default: 20)
            timeout: Request timeout in seconds (default: 30.0)
            
        Returns:
            ConversationResult with outcome and history
        """
        max_turns = max_turns or 20
        timeout = timeout or 30.0
        
        try:
            async with ConversationManager(target, max_turns, timeout) as manager:
                # Send each message in sequence
                for message in messages:
                    try:
                        await manager.send_message(message)
                    except MaxTurnsReachedError:
                        # Max turns reached during conversation
                        return ConversationResult(
                            outcome="failure",
                            turn_count=manager.get_turn_count(),
                            history=manager.get_history(),
                            termination_reason="max_turns_reached"
                        )
                
                # Successfully completed all messages
                return ConversationResult(
                    outcome="success",
                    turn_count=manager.get_turn_count(),
                    history=manager.get_history(),
                    termination_reason="completed"
                )
                
        except ConversationError as e:
            # Handle conversation-specific errors
            return ConversationResult(
                outcome="error",
                turn_count=0,
                history=ConversationHistory(),
                termination_reason="conversation_error",
                error=str(e)
            )
        except Exception as e:
            # Handle unexpected errors
            return ConversationResult(
                outcome="error",
                turn_count=0,
                history=ConversationHistory(),
                termination_reason="unexpected_error",
                error=str(e)
            )
