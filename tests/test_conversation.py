"""Integration tests for conversation manager."""

import pytest
from pytest_httpx import HTTPXMock

from usersim.conversation import ConversationManager
from usersim.models import SystemConfig, TestConfig, TestOutcome


@pytest.mark.asyncio
async def test_successful_conversation(httpx_mock: HTTPXMock):
    """Test a successful conversation that meets all criteria."""
    # Mock agent discovery
    httpx_mock.add_response(
        url="https://example.com/.well-known/agent.json",
        json={
            "name": "Test Agent",
            "endpoint": "https://example.com/task",
        }
    )

    # Mock LLM call for message generation (first turn)
    httpx_mock.add_response(
        url="https://api.openai.com/v1/chat/completions",
        json={
            "choices": [{
                "message": {"content": "I'd like to book a flight from Seattle to New York."}
            }]
        }
    )

    # Mock agent response (first turn)
    httpx_mock.add_response(
        url="https://example.com/task",
        json={
            "jsonrpc": "2.0",
            "result": {"message": "Sure! I can help you book a flight. What date?"},
            "id": 1
        }
    )

    # Mock LLM evaluation (first turn)
    httpx_mock.add_response(
        url="https://api.openai.com/v1/chat/completions",
        json={
            "choices": [{
                "message": {
                    "content": """CRITERION: Booking confirmation received
MET: false
EVALUATION: Not yet confirmed

OVERALL_PROGRESS: 0.3"""
                }
            }]
        }
    )

    # Mock LLM call for message generation (second turn)
    httpx_mock.add_response(
        url="https://api.openai.com/v1/chat/completions",
        json={
            "choices": [{
                "message": {"content": "Next Tuesday please."}
            }]
        }
    )

    # Mock agent response (second turn)
    httpx_mock.add_response(
        url="https://example.com/task",
        json={
            "jsonrpc": "2.0",
            "result": {
                "message": "Great! I've booked your flight from Seattle to New York for next Tuesday. Confirmation: ABC123"
            },
            "id": 1
        }
    )

    # Mock LLM evaluation (second turn - success)
    httpx_mock.add_response(
        url="https://api.openai.com/v1/chat/completions",
        json={
            "choices": [{
                "message": {
                    "content": """CRITERION: Booking confirmation received
MET: true
EVALUATION: Confirmation ABC123 received

OVERALL_PROGRESS: 1.0"""
                }
            }]
        }
    )

    system_config = SystemConfig(api_key="test-key")
    test_config = TestConfig(
        name="Flight Booking",
        target_endpoint="https://example.com/.well-known/agent.json",
        goal="Book a flight from Seattle to New York",
        success_criteria=["Booking confirmation received"],
        max_turns=5,
    )

    manager = ConversationManager(system_config)
    result = await manager.run_test(test_config)

    assert result.outcome == TestOutcome.SUCCESS
    assert result.turn_count == 2
    assert len(result.transcript) == 4  # 2 user messages + 2 agent responses
    assert all(cs.met for cs in result.criteria_status)


@pytest.mark.asyncio
async def test_max_turns_reached(httpx_mock: HTTPXMock):
    """Test conversation that reaches max turns without success."""
    # Mock agent discovery
    httpx_mock.add_response(
        url="https://example.com/.well-known/agent.json",
        json={
            "name": "Test Agent",
            "endpoint": "https://example.com/task",
        }
    )

    # Mock multiple turns that don't meet criteria
    for _ in range(3):  # max_turns = 3
        # LLM message generation
        httpx_mock.add_response(
            url="https://api.openai.com/v1/chat/completions",
            json={
                "choices": [{
                    "message": {"content": "Can you help me?"}
                }]
            }
        )

        # Agent response
        httpx_mock.add_response(
            url="https://example.com/task",
            json={
                "jsonrpc": "2.0",
                "result": {"message": "I'm not sure how to help with that."},
                "id": 1
            }
        )

        # LLM evaluation
        httpx_mock.add_response(
            url="https://api.openai.com/v1/chat/completions",
            json={
                "choices": [{
                    "message": {
                        "content": """CRITERION: Help received
MET: false
EVALUATION: No help provided

OVERALL_PROGRESS: 0.1"""
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
                    "content": """CRITERION: Help received
MET: false
EVALUATION: No help provided

OVERALL_PROGRESS: 0.1"""
                }
            }]
        }
    )

    system_config = SystemConfig(api_key="test-key")
    test_config = TestConfig(
        name="Help Request",
        target_endpoint="https://example.com/.well-known/agent.json",
        goal="Get help",
        success_criteria=["Help received"],
        max_turns=3,
    )

    manager = ConversationManager(system_config)
    result = await manager.run_test(test_config)

    assert result.outcome == TestOutcome.FAILURE
    assert result.turn_count == 3
    assert not any(cs.met for cs in result.criteria_status)


@pytest.mark.asyncio
async def test_agent_error_handling(httpx_mock: HTTPXMock):
    """Test handling of agent errors."""
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
                "message": {"content": "Hello"}
            }]
        }
    )

    # Mock agent error response
    httpx_mock.add_response(
        url="https://example.com/task",
        status_code=500,
    )

    system_config = SystemConfig(api_key="test-key")
    test_config = TestConfig(
        name="Error Test",
        target_endpoint="https://example.com/.well-known/agent.json",
        goal="Test error handling",
        success_criteria=["Success"],
    )

    manager = ConversationManager(system_config)
    result = await manager.run_test(test_config)

    assert result.outcome == TestOutcome.ERROR
    assert result.error_message is not None
