# UserSim Examples

This directory contains example test configurations and usage patterns.

## Files

- `sample_test.yaml` - Example test configuration for a flight booking scenario
- `system_config.yaml` - Example system configuration file

## Usage

### Running a test from the command line:

```bash
# With environment variable for API key
export OPENAI_API_KEY=your-api-key-here
usersim run examples/sample_test.yaml

# With custom system config
usersim run examples/sample_test.yaml --config examples/system_config.yaml

# With JSON output
usersim run examples/sample_test.yaml --format json
```

### Using the Python API:

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
        print(f"Test passed in {result.turn_count} turns!")
    else:
        print(f"Test failed: {result.termination_reason.value}")
        for criterion in result.criteria_status:
            print(f"  {'✓' if criterion.met else '✗'} {criterion.criterion}")

asyncio.run(main())
```
