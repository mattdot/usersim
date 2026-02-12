"""Example usage of UserSim conversation loop."""

import asyncio
from usersim import UserSim


async def main():
    """Run a simple example conversation."""
    # This is a basic example showing the conversation loop
    # In Step 1, we're testing the mechanics of the conversation loop,
    # not the objective-driven behavior (that comes in Step 2)
    
    result = await UserSim.run(
        target="https://example-agent.com/.well-known/agent.json",
        messages=[
            "Hello, I need help booking a flight",
            "I want to fly from Seattle to New York",
            "Next Tuesday would be great"
        ],
        max_turns=10,
        timeout=30.0
    )
    
    print(f"Outcome: {result.outcome}")
    print(f"Turn count: {result.turn_count}")
    print(f"Termination reason: {result.termination_reason}")
    
    if result.error:
        print(f"Error: {result.error}")
    
    print("\nConversation history:")
    for msg in result.history.messages:
        print(f"  {msg.role}: {msg.content}")


if __name__ == "__main__":
    asyncio.run(main())
