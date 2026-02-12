# UserSim

An intelligent agent testing system built on the Microsoft Agent Framework that simulates realistic user interactions with conversational agents.

## Overview

UserSim enables automated, objective-driven testing of agent capabilities through multi-turn conversations that mimic real user behavior. Each test session has a stated objective that UserSim seeks to achieve by chatting with the agent being tested.

## Features

- **Objective-Driven Testing**: Each conversation has clear goals and success criteria
- **Multi-Turn Conversations**: Supports realistic back-and-forth interactions
- **A2A Protocol**: Uses Agent-to-Agent protocol for framework-agnostic testing
- **Adaptive Strategy**: Adjusts approach based on agent responses
- **Comprehensive Reporting**: Detailed metrics and conversation analysis
- **Python Library + CLI**: Use as a library or command-line tool

## Installation

```bash
# Install from source
pip install -e .

# Install with development dependencies
pip install -e ".[dev]"
```

## Quick Start

### Using the CLI

1. Create a test configuration file (see `examples/sample_test.yaml`):

```yaml
usersim_test:
  name: "Flight Booking Test"
  target:
    connection:
      endpoint: "https://your-agent/.well-known/agent.json"
  objective:
    goal: "Book a flight from Seattle to New York"
    success_criteria:
      - "Booking confirmation received"
      - "Correct cities are confirmed"
  constraints:
    max_turns: 15
```

2. Set your API key:

```bash
export OPENAI_API_KEY=your-api-key
```

3. Run the test:

```bash
usersim run examples/sample_test.yaml
```

### Using the Python API

```python
import asyncio
from usersim import UserSim, TestOutcome

async def main():
    result = await UserSim.run(
        target="https://agent/.well-known/agent.json",
        objective="Book a flight from Seattle to New York",
        success_criteria=[
            "Booking confirmation received",
            "Correct cities are confirmed"
        ],
    )
    
    if result.outcome == TestOutcome.SUCCESS:
        print(f"✓ Test passed in {result.turn_count} turns!")
    else:
        print(f"✗ Test failed: {result.termination_reason.value}")

asyncio.run(main())
```

## Implementation Status

**Steps 1-4 (Tier 1 - Core) - ✅ Complete**

- ✅ Step 1: Conversation Loop - A2A protocol, message exchange, turn limits, error handling
- ✅ Step 2: Objective-Driven Message Generation - System config, LLM integration, prompting
- ✅ Step 3: Objective Evaluation & Termination - Progress evaluation, verdicts
- ✅ Step 4: Test Result Output - JSON output, Python API, CLI

**Next Steps (Tier 2 - Essential Enhancements)**

- Step 5: Persona Support - User simulation with different personas
- Step 6: Test Configuration Schema - Full YAML-based configuration

## Documentation

- [SPEC.md](SPEC.md) - Complete specification and architecture
- [PLAN.md](PLAN.md) - Implementation plan and roadmap
- [examples/](examples/) - Example configurations and usage

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=usersim

# Run specific test file
pytest tests/test_core.py -v
```

## License

See [LICENSE](LICENSE) file for details.
