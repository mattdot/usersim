# Step 1 Implementation: Conversation Loop

## Overview

This document describes the implementation of Step 1 from PLAN.md: the core conversation loop that enables UserSim to connect to target agents and exchange messages via the A2A protocol.

## What Was Implemented

### ✅ Core Requirements (from PLAN.md Step 1)

1. **Connect to a target agent via the A2A (Agent-to-Agent) protocol**
   - Implemented in `usersim/a2a_client.py`
   - Uses httpx for async HTTP communication
   - Supports JSON-RPC 2.0 over HTTP(S)

2. **Discover the target agent's capabilities via its A2A Agent Card**
   - `A2AClient.discover_agent()` fetches and parses agent cards
   - Agent Card model defined in `usersim/a2a_protocol.py`
   - Validates agent card structure using Pydantic

3. **Send a message to the target agent and receive a response over A2A**
   - `A2AClient.send_message()` sends JSON-RPC 2.0 requests
   - Handles A2A response parsing and error detection
   - Returns structured A2AMessage objects

4. **Maintain conversation history across turns**
   - `ConversationHistory` class tracks all messages
   - Maintains turn count (increments on user messages)
   - Preserves message metadata throughout conversation

5. **Enforce a max turn limit so every conversation terminates**
   - `ConversationManager` enforces configurable max_turns
   - Raises `MaxTurnsReachedError` when limit is exceeded
   - Default max_turns is 20 (configurable)

6. **Handle errors from the target agent gracefully**
   - Timeout configuration (default 30 seconds)
   - HTTP error handling with httpx.raise_for_status()
   - A2A protocol error detection and reporting
   - Connection failure handling with ConversationError

## Architecture

### Package Structure

```
usersim/
├── __init__.py           # Package exports
├── a2a_protocol.py       # A2A data models (AgentCard, A2AMessage, etc.)
├── a2a_client.py         # A2A protocol client
├── conversation.py       # Conversation lifecycle manager
├── core.py              # Main UserSim API
└── cli.py               # CLI entry point (placeholder)

tests/
├── conftest.py          # Pytest fixtures
├── test_a2a_protocol.py # Protocol model tests
├── test_a2a_client.py   # Client tests
├── test_conversation.py # Conversation manager tests
└── test_core.py         # Core API tests

examples/
├── README.md
└── basic_conversation.py # Usage example
```

### Key Components

#### 1. A2A Protocol Layer (`a2a_protocol.py`)

Defines the data models for A2A communication:

- **AgentCard**: Represents agent metadata and capabilities
- **A2AMessage**: Represents a single message (user or assistant)
- **A2ARequest/A2AResponse**: JSON-RPC 2.0 protocol messages
- **ConversationHistory**: Tracks all messages and turn count

#### 2. A2A Client (`a2a_client.py`)

Handles low-level A2A communication:

- **Agent Discovery**: Fetches and validates agent cards
- **Message Exchange**: Sends messages and receives responses
- **Session Management**: Tracks session IDs across requests
- **Error Handling**: Manages HTTP and protocol errors

#### 3. Conversation Manager (`conversation.py`)

Manages conversation lifecycle:

- **Initialization**: Discovers target agent before conversation starts
- **Turn Management**: Enforces max turn limits
- **History Tracking**: Maintains complete conversation history
- **Error Recovery**: Provides structured error handling

#### 4. Core API (`core.py`)

Main UserSim interface:

- **UserSim.run()**: Async method for running conversations
- **ConversationResult**: Structured result with outcome and history
- **Error Categorization**: Distinguishes between success, failure, and error states

## API Usage

### Basic Usage

```python
from usersim import UserSim

result = await UserSim.run(
    target="https://agent.example.com/.well-known/agent.json",
    messages=["Hello", "How are you?"],
    max_turns=10,
    timeout=30.0
)

print(f"Outcome: {result.outcome}")
print(f"Turns: {result.turn_count}")
print(f"Reason: {result.termination_reason}")
```

### Result Structure

```python
{
    "outcome": "success" | "failure" | "error",
    "turn_count": 2,
    "termination_reason": "completed" | "max_turns_reached" | "conversation_error" | "unexpected_error",
    "error": None or error message,
    "messages": [
        {"role": "user", "content": "...", "metadata": {}},
        {"role": "assistant", "content": "...", "metadata": {}}
    ]
}
```

## Testing

### Test Coverage

18 tests covering all Step 1 requirements:

- **Protocol Tests** (5 tests): Data model validation
- **Client Tests** (4 tests): A2A client functionality
- **Conversation Tests** (5 tests): Conversation management
- **Core Tests** (4 tests): UserSim API behavior

### Running Tests

```bash
# Install with dev dependencies
pip install -e ".[dev]"

# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=usersim --cov-report=html
```

All tests pass successfully (18/18).

## Limitations (By Design for Step 1)

The following are **intentionally not implemented** in Step 1:

1. **No LLM Integration**: Messages are provided as a list, not generated
2. **No Objective Evaluation**: No success criteria checking (Step 3)
3. **No Persona Support**: User behavior is not persona-driven (Step 5)
4. **No CLI**: CLI is a placeholder (Step 4)
5. **No Configuration Files**: No YAML config support (Step 6)

These features are planned for subsequent steps as outlined in PLAN.md.

## Dependencies

- **httpx**: Async HTTP client for A2A communication
- **pydantic**: Data validation and parsing
- **pytest**: Testing framework
- **pytest-asyncio**: Async test support
- **pytest-httpx**: HTTP mocking for tests

## Compliance with SPEC.md

This implementation adheres to SPEC.md sections:

- **Architecture** (lines 17-66): Core components defined
- **A2A Protocol** (lines 381-388): JSON-RPC 2.0 over HTTP(S)
- **Conversation Lifecycle** (lines 119-155): Initialization, engagement, termination
- **Error Handling**: Graceful error management per spec

## Next Steps

With Step 1 complete, the foundation is in place for:

- **Step 2**: Objective-driven message generation with LLM
- **Step 3**: Objective evaluation and intelligent termination
- **Step 4**: Result output, CLI, and library API enhancements
- **Step 5+**: Persona support, configuration schema, observability

## Status

✅ **Step 1 Complete** - All requirements met, tests passing, ready for Step 2.
