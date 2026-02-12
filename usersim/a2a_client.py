"""A2A Protocol client for connecting to target agents."""

import httpx
from typing import Optional, Dict, Any
from usersim.a2a_protocol import AgentCard, A2ARequest, A2AResponse, A2AMessage


class A2AClient:
    """Client for communicating with agents via A2A protocol."""
    
    def __init__(self, agent_card_url: str, timeout: float = 30.0):
        """Initialize the A2A client.
        
        Args:
            agent_card_url: URL to the agent's .well-known/agent.json endpoint
            timeout: Request timeout in seconds
        """
        self.agent_card_url = agent_card_url
        self.timeout = timeout
        self.agent_card: Optional[AgentCard] = None
        self.session_id: Optional[str] = None
        self._client = httpx.Client(timeout=timeout)
    
    async def discover_agent(self) -> AgentCard:
        """Discover the target agent's capabilities via its Agent Card.
        
        Returns:
            AgentCard with agent information
            
        Raises:
            httpx.HTTPError: If the request fails
            ValueError: If the Agent Card is invalid
        """
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(self.agent_card_url)
            response.raise_for_status()
            
            data = response.json()
            self.agent_card = AgentCard(**data)
            return self.agent_card
    
    async def send_message(self, content: str, metadata: Optional[Dict[str, Any]] = None) -> A2AMessage:
        """Send a message to the target agent and receive a response.
        
        Args:
            content: The message content to send
            metadata: Optional metadata for the message
            
        Returns:
            A2AMessage containing the agent's response
            
        Raises:
            httpx.HTTPError: If the request fails
            ValueError: If no agent card has been discovered
        """
        if not self.agent_card:
            raise ValueError("Agent card must be discovered before sending messages. Call discover_agent() first.")
        
        # Construct A2A JSON-RPC 2.0 request
        request = A2ARequest(
            method="sendMessage",
            params={
                "content": content,
                "metadata": metadata or {},
                "session_id": self.session_id
            },
            id="msg-001"  # Simple ID for now
        )
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                self.agent_card.endpoint,
                json=request.model_dump(),
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()
            
            data = response.json()
            a2a_response = A2AResponse(**data)
            
            if a2a_response.error:
                raise ValueError(f"A2A Error: {a2a_response.error}")
            
            if not a2a_response.result:
                raise ValueError("No result in A2A response")
            
            # Extract the response message
            response_content = a2a_response.result.get("content", "")
            response_metadata = a2a_response.result.get("metadata", {})
            
            # Store session ID if provided
            if "session_id" in a2a_response.result:
                self.session_id = a2a_response.result["session_id"]
            
            return A2AMessage(role="assistant", content=response_content, metadata=response_metadata)
    
    def close(self):
        """Close the HTTP client."""
        self._client.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
