"""Tests for A2A client."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import httpx
from usersim.a2a_client import A2AClient
from usersim.a2a_protocol import AgentCard, A2AMessage


@pytest.mark.asyncio
async def test_discover_agent_success():
    """Test successful agent discovery."""
    client = A2AClient("https://example.com/.well-known/agent.json")
    
    mock_response = {
        "id": "test-agent",
        "name": "Test Agent",
        "endpoint": "https://example.com/agent",
        "capabilities": ["chat"]
    }
    
    with patch("httpx.AsyncClient") as mock_client_class:
        mock_client = AsyncMock()
        mock_client_class.return_value.__aenter__.return_value = mock_client
        
        mock_http_response = MagicMock()
        mock_http_response.json.return_value = mock_response
        mock_http_response.raise_for_status = MagicMock()
        mock_client.get.return_value = mock_http_response
        
        agent_card = await client.discover_agent()
        
        assert isinstance(agent_card, AgentCard)
        assert agent_card.id == "test-agent"
        assert agent_card.name == "Test Agent"
        assert client.agent_card is not None


@pytest.mark.asyncio
async def test_send_message_without_discovery():
    """Test that sending a message without discovery raises an error."""
    client = A2AClient("https://example.com/.well-known/agent.json")
    
    with pytest.raises(ValueError, match="Agent card must be discovered"):
        await client.send_message("Hello")


@pytest.mark.asyncio
async def test_send_message_success():
    """Test successful message sending."""
    client = A2AClient("https://example.com/.well-known/agent.json")
    
    # Mock agent card
    client.agent_card = AgentCard(
        id="test-agent",
        name="Test Agent",
        endpoint="https://example.com/agent",
        capabilities=["chat"]
    )
    
    mock_response = {
        "jsonrpc": "2.0",
        "result": {
            "content": "Hello back",
            "metadata": {}
        },
        "id": "msg-001"
    }
    
    with patch("httpx.AsyncClient") as mock_client_class:
        mock_client = AsyncMock()
        mock_client_class.return_value.__aenter__.return_value = mock_client
        
        mock_http_response = MagicMock()
        mock_http_response.json.return_value = mock_response
        mock_http_response.raise_for_status = MagicMock()
        mock_client.post.return_value = mock_http_response
        
        response = await client.send_message("Hello")
        
        assert isinstance(response, A2AMessage)
        assert response.role == "assistant"
        assert response.content == "Hello back"


@pytest.mark.asyncio
async def test_send_message_with_error():
    """Test handling of A2A error response."""
    client = A2AClient("https://example.com/.well-known/agent.json")
    
    # Mock agent card
    client.agent_card = AgentCard(
        id="test-agent",
        name="Test Agent",
        endpoint="https://example.com/agent",
        capabilities=["chat"]
    )
    
    mock_response = {
        "jsonrpc": "2.0",
        "error": {
            "code": -32000,
            "message": "Internal error"
        },
        "id": "msg-001"
    }
    
    with patch("httpx.AsyncClient") as mock_client_class:
        mock_client = AsyncMock()
        mock_client_class.return_value.__aenter__.return_value = mock_client
        
        mock_http_response = MagicMock()
        mock_http_response.json.return_value = mock_response
        mock_http_response.raise_for_status = MagicMock()
        mock_client.post.return_value = mock_http_response
        
        with pytest.raises(ValueError, match="A2A Error"):
            await client.send_message("Hello")
