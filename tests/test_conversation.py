"""Tests for conversation manager."""

import pytest
from unittest.mock import AsyncMock, patch
from usersim.conversation import (
    ConversationManager,
    ConversationError,
    MaxTurnsReachedError
)
from usersim.a2a_protocol import AgentCard, A2AMessage


@pytest.mark.asyncio
async def test_conversation_initialization():
    """Test conversation initialization."""
    manager = ConversationManager("https://example.com/.well-known/agent.json")
    
    with patch.object(manager, "client", create=True) as mock_client:
        mock_client = AsyncMock()
        mock_client.discover_agent = AsyncMock()
        
        with patch("usersim.conversation.A2AClient", return_value=mock_client):
            await manager.initialize()
            
            assert manager.is_initialized
            mock_client.discover_agent.assert_called_once()


@pytest.mark.asyncio
async def test_send_message_not_initialized():
    """Test that sending a message before initialization raises error."""
    manager = ConversationManager("https://example.com/.well-known/agent.json")
    
    with pytest.raises(ConversationError, match="not initialized"):
        await manager.send_message("Hello")


@pytest.mark.asyncio
async def test_send_message_success():
    """Test successful message sending."""
    manager = ConversationManager("https://example.com/.well-known/agent.json", max_turns=10)
    
    mock_client = AsyncMock()
    mock_client.discover_agent = AsyncMock()
    mock_response = A2AMessage(role="assistant", content="Hello back")
    mock_client.send_message = AsyncMock(return_value=mock_response)
    
    with patch("usersim.conversation.A2AClient", return_value=mock_client):
        await manager.initialize()
        response = await manager.send_message("Hello")
        
        assert response.content == "Hello back"
        assert manager.get_turn_count() == 1
        assert len(manager.history.messages) == 2  # User + assistant


@pytest.mark.asyncio
async def test_max_turns_limit():
    """Test that max turns limit is enforced."""
    manager = ConversationManager("https://example.com/.well-known/agent.json", max_turns=2)
    
    mock_client = AsyncMock()
    mock_client.discover_agent = AsyncMock()
    mock_response = A2AMessage(role="assistant", content="Response")
    mock_client.send_message = AsyncMock(return_value=mock_response)
    
    with patch("usersim.conversation.A2AClient", return_value=mock_client):
        await manager.initialize()
        
        # Send first message
        await manager.send_message("Message 1")
        assert manager.get_turn_count() == 1
        
        # Send second message
        await manager.send_message("Message 2")
        assert manager.get_turn_count() == 2
        
        # Third message should raise MaxTurnsReachedError
        with pytest.raises(MaxTurnsReachedError):
            await manager.send_message("Message 3")


@pytest.mark.asyncio
async def test_conversation_history():
    """Test that conversation history is maintained correctly."""
    manager = ConversationManager("https://example.com/.well-known/agent.json")
    
    mock_client = AsyncMock()
    mock_client.discover_agent = AsyncMock()
    mock_response = A2AMessage(role="assistant", content="Response")
    mock_client.send_message = AsyncMock(return_value=mock_response)
    
    with patch("usersim.conversation.A2AClient", return_value=mock_client):
        await manager.initialize()
        
        await manager.send_message("First message")
        await manager.send_message("Second message")
        
        history = manager.get_history()
        assert len(history.messages) == 4  # 2 user + 2 assistant
        assert history.messages[0].role == "user"
        assert history.messages[0].content == "First message"
        assert history.messages[1].role == "assistant"
        assert history.messages[2].role == "user"
        assert history.messages[2].content == "Second message"
