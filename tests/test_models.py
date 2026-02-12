"""Tests for data models."""

import pytest
from pydantic import ValidationError

from usersim.models import (
    AgentCard,
    CriterionStatus,
    Message,
    SystemConfig,
    TestConfig,
    TestOutcome,
    TestResult,
    TerminationReason,
)


def test_message_creation():
    """Test Message model creation."""
    msg = Message(role="user", content="Hello")
    assert msg.role == "user"
    assert msg.content == "Hello"
    assert msg.timestamp is None


def test_system_config_defaults():
    """Test SystemConfig with defaults."""
    config = SystemConfig()
    assert config.provider == "openai"
    assert config.model_name == "gpt-4"
    assert config.temperature == 0.7
    assert config.max_turns == 20


def test_system_config_validation():
    """Test SystemConfig validation."""
    # Temperature out of range
    with pytest.raises(ValidationError):
        SystemConfig(temperature=3.0)

    # Invalid max_turns
    with pytest.raises(ValidationError):
        SystemConfig(max_turns=0)


def test_test_config_creation(sample_test_config):
    """Test TestConfig creation."""
    assert sample_test_config.name == "Sample Test"
    assert sample_test_config.goal == "Test the agent"
    assert len(sample_test_config.success_criteria) == 2


def test_test_config_required_fields():
    """Test TestConfig required fields."""
    with pytest.raises(ValidationError):
        TestConfig(name="Test")  # Missing required fields


def test_agent_card_creation():
    """Test AgentCard creation."""
    card = AgentCard(
        name="Test Agent",
        description="A test agent",
        capabilities=["chat", "search"],
        endpoint="https://example.com/task",
    )
    assert card.name == "Test Agent"
    assert len(card.capabilities) == 2


def test_criterion_status():
    """Test CriterionStatus."""
    status = CriterionStatus(
        criterion="Agent responds",
        met=True,
        evaluation="Agent provided a response"
    )
    assert status.met is True
    assert status.criterion == "Agent responds"


def test_test_result_creation():
    """Test TestResult creation."""
    result = TestResult(
        outcome=TestOutcome.SUCCESS,
        termination_reason=TerminationReason.OBJECTIVE_MET,
        turn_count=5,
        transcript=[Message(role="user", content="Hi")],
        criteria_status=[
            CriterionStatus(criterion="Test", met=True, evaluation="Pass")
        ],
        progress_score=1.0,
    )
    assert result.outcome == TestOutcome.SUCCESS
    assert result.turn_count == 5
    assert result.progress_score == 1.0


def test_test_result_progress_score_validation():
    """Test TestResult progress score validation."""
    # Progress score out of range
    with pytest.raises(ValidationError):
        TestResult(
            outcome=TestOutcome.SUCCESS,
            termination_reason=TerminationReason.OBJECTIVE_MET,
            turn_count=1,
            transcript=[],
            criteria_status=[],
            progress_score=1.5,  # Invalid
        )
