"""Tests for core UserSim class."""

import pytest
from pytest_httpx import HTTPXMock

from usersim import UserSim
from usersim.models import SystemConfig, TestOutcome


@pytest.mark.asyncio
async def test_usersim_run_basic(httpx_mock: HTTPXMock):
    """Test basic UserSim.run() usage."""
    # Mock agent discovery
    httpx_mock.add_response(
        url="https://example.com/.well-known/agent.json",
        json={
            "name": "Test Agent",
            "endpoint": "https://example.com/task",
        }
    )

    # Mock LLM call for message generation
    httpx_mock.add_response(
        url="https://api.openai.com/v1/chat/completions",
        json={
            "choices": [{
                "message": {"content": "Hello, I need help."}
            }]
        }
    )

    # Mock agent response
    httpx_mock.add_response(
        url="https://example.com/task",
        json={
            "jsonrpc": "2.0",
            "result": {"message": "Sure, I can help you! Task completed."},
            "id": 1
        }
    )

    # Mock LLM evaluation
    httpx_mock.add_response(
        url="https://api.openai.com/v1/chat/completions",
        json={
            "choices": [{
                "message": {
                    "content": """CRITERION: Task completed
MET: true
EVALUATION: Task was completed successfully

OVERALL_PROGRESS: 1.0"""
                }
            }]
        }
    )

    system_config = SystemConfig(api_key="test-key")
    result = await UserSim.run(
        target="https://example.com/.well-known/agent.json",
        objective="Complete a task",
        success_criteria=["Task completed"],
        system_config=system_config,
    )

    assert result.outcome == TestOutcome.SUCCESS
    assert result.turn_count == 1
    assert len(result.criteria_status) == 1
    assert result.criteria_status[0].met is True


@pytest.mark.asyncio
async def test_usersim_run_with_context(httpx_mock: HTTPXMock):
    """Test UserSim.run() with context."""
    # Mock agent discovery
    httpx_mock.add_response(
        url="https://example.com/.well-known/agent.json",
        json={
            "name": "Test Agent",
            "endpoint": "https://example.com/task",
        }
    )

    # Mock LLM call for message generation (with context)
    httpx_mock.add_response(
        url="https://api.openai.com/v1/chat/completions",
        json={
            "choices": [{
                "message": {"content": "I'm a budget traveler looking for a flight."}
            }]
        }
    )

    # Mock agent response
    httpx_mock.add_response(
        url="https://example.com/task",
        json={
            "jsonrpc": "2.0",
            "result": {"message": "Found a budget flight for you!"},
            "id": 1
        }
    )

    # Mock LLM evaluation
    httpx_mock.add_response(
        url="https://api.openai.com/v1/chat/completions",
        json={
            "choices": [{
                "message": {
                    "content": """CRITERION: Budget flight found
MET: true
EVALUATION: Agent found budget flight

OVERALL_PROGRESS: 1.0"""
                }
            }]
        }
    )

    system_config = SystemConfig(api_key="test-key")
    result = await UserSim.run(
        target="https://example.com/.well-known/agent.json",
        objective="Find a budget flight",
        success_criteria=["Budget flight found"],
        context="Budget-conscious traveler",
        system_config=system_config,
    )

    assert result.outcome == TestOutcome.SUCCESS


@pytest.mark.asyncio
async def test_usersim_run_with_custom_turns(httpx_mock: HTTPXMock):
    """Test UserSim.run() with custom max_turns."""
    # Mock agent discovery
    httpx_mock.add_response(
        url="https://example.com/.well-known/agent.json",
        json={
            "name": "Test Agent",
            "endpoint": "https://example.com/task",
        }
    )

    # Mock 2 turns
    for _ in range(2):
        # LLM message generation
        httpx_mock.add_response(
            url="https://api.openai.com/v1/chat/completions",
            json={
                "choices": [{
                    "message": {"content": "Help me"}
                }]
            }
        )

        # Agent response
        httpx_mock.add_response(
            url="https://example.com/task",
            json={
                "jsonrpc": "2.0",
                "result": {"message": "Working on it..."},
                "id": 1
            }
        )

        # LLM evaluation
        httpx_mock.add_response(
            url="https://api.openai.com/v1/chat/completions",
            json={
                "choices": [{
                    "message": {
                        "content": """CRITERION: Task done
MET: false
EVALUATION: Not done yet

OVERALL_PROGRESS: 0.5"""
                    }
                }]
            }
        )

    # Final evaluation
    httpx_mock.add_response(
        url="https://api.openai.com/v1/chat/completions",
        json={
            "choices": [{
                "message": {
                    "content": """CRITERION: Task done
MET: false
EVALUATION: Not done

OVERALL_PROGRESS: 0.5"""
                }
            }]
        }
    )

    system_config = SystemConfig(api_key="test-key")
    result = await UserSim.run(
        target="https://example.com/.well-known/agent.json",
        objective="Complete task",
        success_criteria=["Task done"],
        max_turns=2,  # Custom limit
        system_config=system_config,
    )

    # Should hit max turns
    assert result.turn_count == 2
    assert result.outcome in [TestOutcome.FAILURE, TestOutcome.PARTIAL_SUCCESS]
