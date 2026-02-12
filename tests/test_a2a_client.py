"""Tests for A2A client."""

import pytest
from pytest_httpx import HTTPXMock

from usersim.a2a_client import A2AClient
from usersim.models import Message


@pytest.mark.asyncio
async def test_discover_agent(httpx_mock: HTTPXMock):
    """Test agent discovery."""
    # Mock agent card response
    httpx_mock.add_response(
        url="https://example.com/.well-known/agent.json",
        json={
            "name": "Test Agent",
            "description": "A test agent",
            "capabilities": ["chat"],
            "endpoint": "https://example.com/task",
        }
    )

    client = A2AClient()
    try:
        agent_card = await client.discover_agent("https://example.com/.well-known/agent.json")

        assert agent_card.name == "Test Agent"
        assert agent_card.description == "A test agent"
        assert "chat" in agent_card.capabilities
        assert agent_card.endpoint == "https://example.com/task"
    finally:
        await client.close()


@pytest.mark.asyncio
async def test_discover_agent_no_endpoint(httpx_mock: HTTPXMock):
    """Test agent discovery without explicit endpoint."""
    # Mock agent card response without endpoint
    httpx_mock.add_response(
        url="https://example.com/.well-known/agent.json",
        json={
            "name": "Test Agent",
            "capabilities": [],
        }
    )

    client = A2AClient()
    try:
        agent_card = await client.discover_agent("https://example.com/.well-known/agent.json")

        # Should derive endpoint from agent card URL
        assert agent_card.endpoint == "https://example.com/task"
    finally:
        await client.close()


@pytest.mark.asyncio
async def test_send_message(httpx_mock: HTTPXMock):
    """Test sending a message."""
    # Mock agent discovery
    httpx_mock.add_response(
        url="https://example.com/.well-known/agent.json",
        json={
            "name": "Test Agent",
            "endpoint": "https://example.com/task",
        }
    )

    # Mock task response
    httpx_mock.add_response(
        url="https://example.com/task",
        json={
            "jsonrpc": "2.0",
            "result": {
                "message": "Hello from the agent!"
            },
            "id": 1
        }
    )

    client = A2AClient()
    try:
        await client.discover_agent("https://example.com/.well-known/agent.json")

        history = [Message(role="user", content="Previous message")]
        response = await client.send_message("Hello", history)

        assert response == "Hello from the agent!"
    finally:
        await client.close()


@pytest.mark.asyncio
async def test_send_message_error_response(httpx_mock: HTTPXMock):
    """Test handling error response from agent."""
    # Mock agent discovery
    httpx_mock.add_response(
        url="https://example.com/.well-known/agent.json",
        json={
            "name": "Test Agent",
            "endpoint": "https://example.com/task",
        }
    )

    # Mock error response
    httpx_mock.add_response(
        url="https://example.com/task",
        json={
            "jsonrpc": "2.0",
            "error": {
                "code": -32000,
                "message": "Internal error"
            },
            "id": 1
        }
    )

    client = A2AClient()
    try:
        await client.discover_agent("https://example.com/.well-known/agent.json")

        with pytest.raises(RuntimeError, match="Agent error"):
            await client.send_message("Hello", [])
    finally:
        await client.close()


@pytest.mark.asyncio
async def test_send_message_without_discovery():
    """Test sending message without agent discovery."""
    client = A2AClient()
    try:
        with pytest.raises(RuntimeError, match="Agent not discovered"):
            await client.send_message("Hello", [])
    finally:
        await client.close()
