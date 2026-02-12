"""Tests for A2A protocol models."""

import pytest
from usersim.a2a_protocol import (
    AgentCard,
    A2AMessage,
    A2ARequest,
    A2AResponse,
    ConversationHistory
)


def test_agent_card_creation():
    """Test creating an AgentCard."""
    card = AgentCard(
        id="test-agent",
        name="Test Agent",
        description="A test agent",
        endpoint="https://example.com/agent",
        capabilities=["chat", "search"]
    )
    assert card.id == "test-agent"
    assert card.name == "Test Agent"
    assert card.endpoint == "https://example.com/agent"
    assert len(card.capabilities) == 2


def test_a2a_message_creation():
    """Test creating an A2A message."""
    msg = A2AMessage(role="user", content="Hello")
    assert msg.role == "user"
    assert msg.content == "Hello"
    assert msg.metadata == {}


def test_conversation_history():
    """Test conversation history tracking."""
    history = ConversationHistory()
    assert history.turn_count == 0
    assert len(history.messages) == 0
    
    # Add user message
    history.add_message("user", "Hello")
    assert history.turn_count == 1
    assert len(history.messages) == 1
    
    # Add assistant message
    history.add_message("assistant", "Hi there")
    assert history.turn_count == 1  # Turn count only increments for user messages
    assert len(history.messages) == 2
    
    # Add another user message
    history.add_message("user", "How are you?")
    assert history.turn_count == 2
    assert len(history.messages) == 3


def test_a2a_request_creation():
    """Test creating an A2A request."""
    request = A2ARequest(
        method="sendMessage",
        params={"content": "Hello"},
        id="test-id"
    )
    assert request.jsonrpc == "2.0"
    assert request.method == "sendMessage"
    assert request.params["content"] == "Hello"
    assert request.id == "test-id"


def test_a2a_response_creation():
    """Test creating an A2A response."""
    response = A2AResponse(
        result={"content": "Hello back"},
        id="test-id"
    )
    assert response.jsonrpc == "2.0"
    assert response.result["content"] == "Hello back"
    assert response.error is None
