"""Conversation manager for handling test conversations."""

import logging
from datetime import datetime
from typing import List, Optional

from usersim.a2a_client import A2AClient
from usersim.llm_client import LLMClient
from usersim.models import (
    CriterionStatus,
    Message,
    SystemConfig,
    TerminationReason,
    TestConfig,
    TestOutcome,
    TestResult,
)

logger = logging.getLogger(__name__)


class ConversationManager:
    """Manages the lifecycle of test conversations."""

    def __init__(self, system_config: SystemConfig):
        """Initialize the conversation manager.

        Args:
            system_config: System-wide configuration
        """
        self.system_config = system_config
        self.llm_client = LLMClient(system_config)
        self.a2a_client: Optional[A2AClient] = None

    async def run_test(self, test_config: TestConfig) -> TestResult:
        """Run a complete test conversation.

        Args:
            test_config: Test configuration

        Returns:
            TestResult with outcome and details
        """
        start_time = datetime.now()
        conversation_history: List[Message] = []
        max_turns = test_config.max_turns or self.system_config.max_turns

        logger.info(f"Starting test: {test_config.name}")
        logger.info(f"Goal: {test_config.goal}")
        logger.info(f"Max turns: {max_turns}")

        # Initialize A2A client
        timeout = test_config.timeout_seconds or self.system_config.timeout_seconds
        self.a2a_client = A2AClient(timeout=timeout)

        try:
            # Step 1: Discover target agent
            await self.a2a_client.discover_agent(test_config.target_endpoint)

            # Step 2: Run conversation loop
            for turn in range(max_turns):
                logger.info(f"Turn {turn + 1}/{max_turns}")

                # Generate user message
                user_message = await self.llm_client.generate_user_message(
                    goal=test_config.goal,
                    success_criteria=test_config.success_criteria,
                    conversation_history=conversation_history,
                    context=test_config.context,
                )

                # Add to history
                conversation_history.append(
                    Message(role="user", content=user_message, timestamp=datetime.now().isoformat())
                )

                # Send to target agent
                try:
                    agent_response = await self.a2a_client.send_message(
                        user_message, conversation_history[:-1]
                    )
                except Exception as e:
                    logger.error(f"Agent communication failed: {e}")
                    return self._create_error_result(
                        conversation_history,
                        turn + 1,
                        test_config,
                        str(e),
                        start_time
                    )

                # Add agent response to history
                conversation_history.append(
                    Message(role="assistant", content=agent_response,
                           timestamp=datetime.now().isoformat())
                )

                # Evaluate progress
                progress_score, criteria_evals = await self.llm_client.evaluate_progress(
                    goal=test_config.goal,
                    success_criteria=test_config.success_criteria,
                    conversation_history=conversation_history,
                )

                # Check for success
                criteria_status = [
                    CriterionStatus(criterion=crit, met=met, evaluation=eval_text)
                    for crit, met, eval_text in criteria_evals
                ]

                all_met = all(cs.met for cs in criteria_status)
                any_met = any(cs.met for cs in criteria_status)

                if all_met:
                    logger.info("All success criteria met!")
                    return TestResult(
                        outcome=TestOutcome.SUCCESS,
                        termination_reason=TerminationReason.OBJECTIVE_MET,
                        turn_count=turn + 1,
                        transcript=conversation_history,
                        criteria_status=criteria_status,
                        progress_score=progress_score,
                        duration_seconds=(datetime.now() - start_time).total_seconds(),
                    )

                # Check for no progress (abandonment)
                if turn >= 3 and progress_score < 0.2:
                    logger.warning(f"No significant progress after {turn + 1} turns")
                    outcome = TestOutcome.PARTIAL_SUCCESS if any_met else TestOutcome.ABANDONED
                    return TestResult(
                        outcome=outcome,
                        termination_reason=TerminationReason.NO_PROGRESS,
                        turn_count=turn + 1,
                        transcript=conversation_history,
                        criteria_status=criteria_status,
                        progress_score=progress_score,
                        duration_seconds=(datetime.now() - start_time).total_seconds(),
                    )

            # Max turns reached
            logger.info(f"Max turns ({max_turns}) reached")
            progress_score, criteria_evals = await self.llm_client.evaluate_progress(
                goal=test_config.goal,
                success_criteria=test_config.success_criteria,
                conversation_history=conversation_history,
            )

            criteria_status = [
                CriterionStatus(criterion=crit, met=met, evaluation=eval_text)
                for crit, met, eval_text in criteria_evals
            ]

            any_met = any(cs.met for cs in criteria_status)
            outcome = TestOutcome.PARTIAL_SUCCESS if any_met else TestOutcome.FAILURE

            return TestResult(
                outcome=outcome,
                termination_reason=TerminationReason.MAX_TURNS_REACHED,
                turn_count=max_turns,
                transcript=conversation_history,
                criteria_status=criteria_status,
                progress_score=progress_score,
                duration_seconds=(datetime.now() - start_time).total_seconds(),
            )

        except Exception as e:
            logger.error(f"Test execution failed: {e}")
            return self._create_error_result(
                conversation_history,
                len(conversation_history) // 2,
                test_config,
                str(e),
                start_time
            )

        finally:
            if self.a2a_client:
                await self.a2a_client.close()

    def _create_error_result(
        self,
        conversation_history: List[Message],
        turn_count: int,
        test_config: TestConfig,
        error_message: str,
        start_time: datetime,
    ) -> TestResult:
        """Create a test result for an error scenario."""
        return TestResult(
            outcome=TestOutcome.ERROR,
            termination_reason=TerminationReason.CRITICAL_ERROR,
            turn_count=turn_count,
            transcript=conversation_history,
            criteria_status=[
                CriterionStatus(criterion=c, met=False, evaluation="Test error")
                for c in test_config.success_criteria
            ],
            progress_score=0.0,
            duration_seconds=(datetime.now() - start_time).total_seconds(),
            error_message=error_message,
        )
