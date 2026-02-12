"""A2A Protocol models and types."""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class AgentCard(BaseModel):
    """Represents an Agent Card for A2A protocol discovery."""
    
    id: str
    name: str
    description: Optional[str] = None
    version: Optional[str] = None
    capabilities: List[str] = Field(default_factory=list)
    endpoint: str
    protocol: str = "a2a"
    metadata: Dict[str, Any] = Field(default_factory=dict)


class A2AMessage(BaseModel):
    """Represents an A2A message."""
    
    role: str  # "user" or "assistant"
    content: str
    metadata: Dict[str, Any] = Field(default_factory=dict)


class A2ARequest(BaseModel):
    """Represents an A2A JSON-RPC 2.0 request."""
    
    jsonrpc: str = "2.0"
    method: str
    params: Dict[str, Any]
    id: Optional[str] = None


class A2AResponse(BaseModel):
    """Represents an A2A JSON-RPC 2.0 response."""
    
    jsonrpc: str = "2.0"
    result: Optional[Dict[str, Any]] = None
    error: Optional[Dict[str, Any]] = None
    id: Optional[str] = None


class ConversationHistory(BaseModel):
    """Maintains conversation history."""
    
    messages: List[A2AMessage] = Field(default_factory=list)
    turn_count: int = 0
    
    def add_message(self, role: str, content: str, metadata: Optional[Dict[str, Any]] = None):
        """Add a message to the conversation history."""
        message = A2AMessage(role=role, content=content, metadata=metadata or {})
        self.messages.append(message)
        if role == "user":
            self.turn_count += 1
    
    def get_messages(self) -> List[A2AMessage]:
        """Get all messages in the conversation."""
        return self.messages
