"""Tests for core UserSim functionality."""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from usersim.core import UserSim, ConversationResult
from usersim.a2a_protocol import A2AMessage


@pytest.mark.asyncio
async def test_usersim_run_success():
    """Test successful UserSim run."""
    messages = ["Hello", "How are you?"]
    
    mock_manager = AsyncMock()
    mock_manager.get_turn_count.return_value = 2
    mock_manager.get_history.return_value = MagicMock(messages=[])
    mock_manager.__aenter__.return_value = mock_manager
    mock_manager.__aexit__.return_value = None
    
    mock_response = A2AMessage(role="assistant", content="I'm good")
    mock_manager.send_message = AsyncMock(return_value=mock_response)
    
    with patch("usersim.core.ConversationManager", return_value=mock_manager):
        result = await UserSim.run(
            target="https://example.com/.well-known/agent.json",
            messages=messages
        )
        
        assert isinstance(result, ConversationResult)
        assert result.outcome == "success"
        assert result.termination_reason == "completed"
        assert mock_manager.send_message.call_count == 2


@pytest.mark.asyncio
async def test_usersim_run_max_turns():
    """Test UserSim run hitting max turns limit."""
    from usersim.conversation import MaxTurnsReachedError
    
    messages = ["Hello", "Message 2", "Message 3"]
    
    mock_manager = AsyncMock()
    mock_manager.get_turn_count.return_value = 2
    mock_manager.get_history.return_value = MagicMock(messages=[])
    mock_manager.__aenter__.return_value = mock_manager
    mock_manager.__aexit__.return_value = None
    
    # First message succeeds, second raises MaxTurnsReachedError
    mock_manager.send_message = AsyncMock(side_effect=[
        A2AMessage(role="assistant", content="Response 1"),
        MaxTurnsReachedError("Max turns")
    ])
    
    with patch("usersim.core.ConversationManager", return_value=mock_manager):
        result = await UserSim.run(
            target="https://example.com/.well-known/agent.json",
            messages=messages,
            max_turns=2
        )
        
        assert result.outcome == "failure"
        assert result.termination_reason == "max_turns_reached"


@pytest.mark.asyncio
async def test_usersim_run_error_handling():
    """Test UserSim error handling."""
    from usersim.conversation import ConversationError
    
    messages = ["Hello"]
    
    mock_manager = AsyncMock()
    mock_manager.__aenter__.side_effect = ConversationError("Connection failed")
    
    with patch("usersim.core.ConversationManager", return_value=mock_manager):
        result = await UserSim.run(
            target="https://example.com/.well-known/agent.json",
            messages=messages
        )
        
        assert result.outcome == "error"
        assert result.termination_reason == "conversation_error"
        assert "Connection failed" in result.error


@pytest.mark.asyncio
async def test_conversation_result_to_dict():
    """Test ConversationResult to_dict conversion."""
    from usersim.a2a_protocol import ConversationHistory
    
    history = ConversationHistory()
    history.add_message("user", "Hello")
    history.add_message("assistant", "Hi there")
    
    result = ConversationResult(
        outcome="success",
        turn_count=1,
        history=history,
        termination_reason="completed"
    )
    
    result_dict = result.to_dict()
    
    assert result_dict["outcome"] == "success"
    assert result_dict["turn_count"] == 1
    assert result_dict["termination_reason"] == "completed"
    assert len(result_dict["messages"]) == 2
    assert result_dict["messages"][0]["role"] == "user"
    assert result_dict["messages"][0]["content"] == "Hello"
