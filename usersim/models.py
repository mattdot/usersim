"""Data models for UserSim."""

from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class TestOutcome(str, Enum):
    """Test outcome types."""

    SUCCESS = "success"
    PARTIAL_SUCCESS = "partial_success"
    FAILURE = "failure"
    ABANDONED = "abandoned"
    ERROR = "error"


class TerminationReason(str, Enum):
    """Reasons for conversation termination."""

    OBJECTIVE_MET = "objective_met"
    MAX_TURNS_REACHED = "max_turns_reached"
    NO_PROGRESS = "no_progress"
    CRITICAL_ERROR = "critical_error"


class Message(BaseModel):
    """A conversation message."""

    role: str = Field(description="Message role: 'user' or 'assistant'")
    content: str = Field(description="Message content")
    timestamp: Optional[str] = None


class CriterionStatus(BaseModel):
    """Status of a single success criterion."""

    criterion: str = Field(description="The success criterion text")
    met: bool = Field(description="Whether this criterion was met")
    evaluation: str = Field(description="Explanation of why the criterion was or was not met")


class TestResult(BaseModel):
    """Result of a test execution."""

    outcome: TestOutcome
    termination_reason: TerminationReason
    turn_count: int
    transcript: List[Message]
    criteria_status: List[CriterionStatus]
    progress_score: float = Field(
        ge=0.0,
        le=1.0,
        description="Overall progress toward objective completion, from 0.0 to 1.0"
    )
    duration_seconds: Optional[float] = None
    error_message: Optional[str] = None


class SystemConfig(BaseModel):
    """System-wide configuration."""

    provider: str = Field(default="openai", description="LLM provider")
    model_name: str = Field(default="gpt-4", description="Model name")
    api_key: Optional[str] = Field(default=None, description="API key")
    api_base: Optional[str] = Field(default=None, description="API base URL")
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    top_p: float = Field(default=0.95, ge=0.0, le=1.0)
    max_tokens: int = Field(default=1024, gt=0)
    max_turns: int = Field(default=20, gt=0)
    timeout_seconds: int = Field(default=300, gt=0)


class TestConfig(BaseModel):
    """Configuration for a single test."""

    name: str
    description: Optional[str] = None
    target_endpoint: str = Field(description="Target agent A2A endpoint URL")
    goal: str = Field(description="Test objective goal statement")
    success_criteria: List[str] = Field(description="List of success criteria")
    context: Optional[str] = Field(default=None, description="Background context")
    max_turns: Optional[int] = Field(default=None, description="Override max turns")
    timeout_seconds: Optional[int] = Field(default=None, description="Override timeout")


class AgentCard(BaseModel):
    """A2A Agent Card."""

    name: str
    description: Optional[str] = None
    capabilities: List[str] = Field(default_factory=list)
    endpoint: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
