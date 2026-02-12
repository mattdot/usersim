"""A2A (Agent-to-Agent) protocol client."""

import logging
from typing import Any, Dict, Optional

import httpx

from usersim.models import AgentCard, Message

logger = logging.getLogger(__name__)


class A2AClient:
    """Client for communicating with agents via A2A protocol."""

    def __init__(self, timeout: int = 300):
        """Initialize the A2A client.

        Args:
            timeout: Request timeout in seconds
        """
        self.timeout = timeout
        self.client = httpx.AsyncClient(timeout=timeout)
        self._agent_card: Optional[AgentCard] = None
        self._task_endpoint: Optional[str] = None

    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()

    async def discover_agent(self, endpoint_url: str) -> AgentCard:
        """Discover agent capabilities via Agent Card.

        Args:
            endpoint_url: URL to the agent's .well-known/agent.json

        Returns:
            AgentCard with agent information

        Raises:
            httpx.HTTPError: If discovery fails
        """
        logger.info(f"Discovering agent at {endpoint_url}")
        try:
            response = await self.client.get(endpoint_url)
            response.raise_for_status()
            data = response.json()

            # Extract task endpoint from agent card
            self._task_endpoint = data.get("endpoint", endpoint_url.replace(
                "/.well-known/agent.json", "/task"
            ))

            self._agent_card = AgentCard(
                name=data.get("name", "Unknown"),
                description=data.get("description"),
                capabilities=data.get("capabilities", []),
                endpoint=self._task_endpoint,
                metadata=data.get("metadata", {}),
            )
            logger.info(f"Discovered agent: {self._agent_card.name}")
            return self._agent_card

        except httpx.HTTPError as e:
            logger.error(f"Agent discovery failed: {e}")
            raise

    async def send_message(self, message: str, conversation_history: list[Message]) -> str:
        """Send a message to the target agent.

        Args:
            message: User message to send
            conversation_history: Previous messages in the conversation

        Returns:
            Agent's response text

        Raises:
            httpx.HTTPError: If message sending fails
        """
        if not self._task_endpoint:
            raise RuntimeError("Agent not discovered. Call discover_agent() first.")

        # Build JSON-RPC 2.0 request
        messages = [
            {"role": msg.role, "content": msg.content}
            for msg in conversation_history
        ]
        messages.append({"role": "user", "content": message})

        request_payload = {
            "jsonrpc": "2.0",
            "method": "task",
            "params": {
                "messages": messages
            },
            "id": 1
        }

        logger.debug(f"Sending message to {self._task_endpoint}")
        try:
            response = await self.client.post(
                self._task_endpoint,
                json=request_payload,
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()
            data = response.json()

            # Extract response from JSON-RPC format
            if "error" in data:
                error_msg = data["error"].get("message", "Unknown error")
                logger.error(f"Agent returned error: {error_msg}")
                raise RuntimeError(f"Agent error: {error_msg}")

            result = data.get("result", {})
            # Handle different response formats
            if isinstance(result, dict):
                response_text = result.get("message", result.get("content", str(result)))
            else:
                response_text = str(result)

            logger.debug(f"Received response: {response_text[:100]}...")
            return response_text

        except httpx.HTTPError as e:
            logger.error(f"Failed to send message: {e}")
            raise
