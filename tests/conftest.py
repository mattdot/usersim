"""Pytest configuration."""

import pytest


@pytest.fixture
def agent_card_url():
    """Fixture for agent card URL."""
    return "https://example.com/.well-known/agent.json"


@pytest.fixture
def sample_agent_card_data():
    """Fixture for sample agent card data."""
    return {
        "id": "test-agent",
        "name": "Test Agent",
        "description": "A test agent for testing",
        "endpoint": "https://example.com/agent",
        "capabilities": ["chat", "search"],
        "protocol": "a2a"
    }
