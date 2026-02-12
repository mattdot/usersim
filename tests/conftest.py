"""Test fixtures and configuration."""

import pytest


@pytest.fixture
def sample_test_config():
    """Sample test configuration."""
    from usersim.models import TestConfig

    return TestConfig(
        name="Sample Test",
        description="A sample test",
        target_endpoint="https://example.com/.well-known/agent.json",
        goal="Test the agent",
        success_criteria=["Agent responds", "Agent is helpful"],
    )


@pytest.fixture
def sample_system_config():
    """Sample system configuration."""
    from usersim.models import SystemConfig

    return SystemConfig(
        provider="openai",
        model_name="gpt-4",
        api_key="test-key",
        temperature=0.7,
        max_turns=10,
    )
