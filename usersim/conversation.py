"""Conversation manager for handling multi-turn interactions."""

from typing import Optional
from usersim.a2a_client import A2AClient
from usersim.a2a_protocol import ConversationHistory, A2AMessage


class ConversationError(Exception):
    """Base exception for conversation errors."""
    pass


class MaxTurnsReachedError(ConversationError):
    """Raised when max turn limit is reached."""
    pass


class ConversationManager:
    """Manages the lifecycle of test conversations."""
    
    def __init__(
        self,
        agent_card_url: str,
        max_turns: int = 20,
        timeout: float = 30.0
    ):
        """Initialize the conversation manager.
        
        Args:
            agent_card_url: URL to the target agent's Agent Card
            max_turns: Maximum number of turns before termination
            timeout: Request timeout in seconds
        """
        self.agent_card_url = agent_card_url
        self.max_turns = max_turns
        self.timeout = timeout
        self.history = ConversationHistory()
        self.client: Optional[A2AClient] = None
        self.is_initialized = False
    
    async def initialize(self):
        """Initialize the conversation by discovering the target agent."""
        self.client = A2AClient(self.agent_card_url, self.timeout)
        try:
            await self.client.discover_agent()
            self.is_initialized = True
        except Exception as e:
            raise ConversationError(f"Failed to discover agent: {str(e)}")
    
    async def send_message(self, content: str) -> A2AMessage:
        """Send a message to the target agent and track it in history.
        
        Args:
            content: The message to send
            
        Returns:
            The agent's response message
            
        Raises:
            ConversationError: If conversation is not initialized
            MaxTurnsReachedError: If max turns limit is reached
        """
        if not self.is_initialized or not self.client:
            raise ConversationError("Conversation not initialized. Call initialize() first.")
        
        # Check turn limit before sending
        if self.history.turn_count >= self.max_turns:
            raise MaxTurnsReachedError(f"Maximum turn limit of {self.max_turns} reached")
        
        # Add user message to history
        self.history.add_message("user", content)
        
        try:
            # Send message and get response
            response = await self.client.send_message(content)
            
            # Add agent response to history
            self.history.add_message("assistant", response.content, response.metadata)
            
            return response
        except Exception as e:
            raise ConversationError(f"Failed to send message: {str(e)}")
    
    def get_turn_count(self) -> int:
        """Get the current turn count."""
        return self.history.turn_count
    
    def get_history(self) -> ConversationHistory:
        """Get the conversation history."""
        return self.history
    
    def has_reached_max_turns(self) -> bool:
        """Check if the conversation has reached the max turn limit."""
        return self.history.turn_count >= self.max_turns
    
    async def __aenter__(self):
        await self.initialize()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        # Cleanup is automatic with async context managers
        pass
