"""Core UserSim class."""

import logging
import os
from typing import List, Optional

from usersim.conversation import ConversationManager
from usersim.models import SystemConfig, TestConfig, TestResult

logger = logging.getLogger(__name__)


class UserSim:
    """Main UserSim class for running agent tests."""

    @staticmethod
    async def run(
        target: str,
        objective: str,
        success_criteria: List[str],
        name: str = "Test",
        description: Optional[str] = None,
        context: Optional[str] = None,
        max_turns: Optional[int] = None,
        timeout_seconds: Optional[int] = None,
        system_config: Optional[SystemConfig] = None,
    ) -> TestResult:
        """Run a single test.

        Args:
            target: Target agent A2A endpoint URL
            objective: Test objective/goal
            success_criteria: List of success criteria
            name: Test name
            description: Test description
            context: Optional context information
            max_turns: Optional override for max turns
            timeout_seconds: Optional override for timeout
            system_config: Optional system configuration (uses defaults if not provided)

        Returns:
            TestResult with outcome and details

        Example:
            ```python
            result = await UserSim.run(
                target="https://agent/.well-known/agent.json",
                objective="Book a flight from Seattle to New York",
                success_criteria=["Booking confirmation received"],
            )
            assert result.outcome == TestOutcome.SUCCESS
            ```
        """
        # Use provided config or create default
        if system_config is None:
            system_config = SystemConfig(
                api_key=os.getenv("OPENAI_API_KEY"),
            )

        # Create test config
        test_config = TestConfig(
            name=name,
            description=description,
            target_endpoint=target,
            goal=objective,
            success_criteria=success_criteria,
            context=context,
            max_turns=max_turns,
            timeout_seconds=timeout_seconds,
        )

        # Run test
        manager = ConversationManager(system_config)
        result = await manager.run_test(test_config)

        return result


def configure_logging(level: str = "INFO"):
    """Configure logging for UserSim.

    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR)
    """
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
