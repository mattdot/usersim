"""CLI for UserSim."""

import asyncio
import json
import logging
import sys
from pathlib import Path
from typing import Optional

import click
import yaml

from usersim.core import UserSim, configure_logging
from usersim.models import SystemConfig, TestConfig, TestOutcome

logger = logging.getLogger(__name__)


@click.group()
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose logging")
def main(verbose: bool):
    """UserSim - Intelligent agent testing tool."""
    log_level = "DEBUG" if verbose else "INFO"
    configure_logging(log_level)


@main.command()
@click.argument("test_file", type=click.Path(exists=True))
@click.option("--config", "-c", type=click.Path(exists=True), help="System config file")
@click.option("--format", "-f", type=click.Choice(["text", "json"]), default="text",
              help="Output format")
def run(test_file: str, config: Optional[str], format: str):
    """Run a test from a YAML configuration file.

    TEST_FILE: Path to test configuration YAML file
    """
    try:
        # Load test config
        with open(test_file, "r") as f:
            test_data = yaml.safe_load(f)

        # Load system config if provided
        system_config = None
        if config:
            with open(config, "r") as f:
                config_data = yaml.safe_load(f)
                system_config = SystemConfig(**config_data.get("usersim_system", {}))

        # Parse test config
        test_config_data = test_data.get("usersim_test", test_data)
        test_config = TestConfig(
            name=test_config_data.get("name", "Test"),
            description=test_config_data.get("description"),
            target_endpoint=test_config_data["target"]["connection"]["endpoint"],
            goal=test_config_data["objective"]["goal"],
            success_criteria=test_config_data["objective"]["success_criteria"],
            context=test_config_data["objective"].get("context"),
            max_turns=test_config_data.get("constraints", {}).get("max_turns"),
            timeout_seconds=test_config_data.get("constraints", {}).get("timeout_seconds"),
        )

        # Run test
        result = asyncio.run(
            UserSim.run(
                target=test_config.target_endpoint,
                objective=test_config.goal,
                success_criteria=test_config.success_criteria,
                name=test_config.name,
                description=test_config.description,
                context=test_config.context,
                max_turns=test_config.max_turns,
                timeout_seconds=test_config.timeout_seconds,
                system_config=system_config,
            )
        )

        # Output results
        if format == "json":
            print(json.dumps(result.model_dump(), indent=2))
        else:
            _print_text_result(result)

        # Exit with appropriate code
        if result.outcome == TestOutcome.SUCCESS:
            sys.exit(0)
        elif result.outcome == TestOutcome.ERROR:
            sys.exit(2)
        else:
            sys.exit(1)

    except Exception as e:
        logger.error(f"Failed to run test: {e}", exc_info=True)
        click.echo(f"Error: {e}", err=True)
        sys.exit(2)


@main.command()
@click.argument("test_file", type=click.Path(exists=True))
def validate(test_file: str):
    """Validate a test configuration file without running it.

    TEST_FILE: Path to test configuration YAML file
    """
    try:
        with open(test_file, "r") as f:
            test_data = yaml.safe_load(f)

        # Try to parse as TestConfig
        test_config_data = test_data.get("usersim_test", test_data)
        TestConfig(
            name=test_config_data.get("name", "Test"),
            description=test_config_data.get("description"),
            target_endpoint=test_config_data["target"]["connection"]["endpoint"],
            goal=test_config_data["objective"]["goal"],
            success_criteria=test_config_data["objective"]["success_criteria"],
            context=test_config_data["objective"].get("context"),
            max_turns=test_config_data.get("constraints", {}).get("max_turns"),
            timeout_seconds=test_config_data.get("constraints", {}).get("timeout_seconds"),
        )

        click.echo(f"✓ Test configuration is valid: {test_file}")
        sys.exit(0)

    except Exception as e:
        click.echo(f"✗ Test configuration is invalid: {e}", err=True)
        sys.exit(1)


def _print_text_result(result):
    """Print test result in human-readable format."""
    click.echo("\n" + "=" * 80)
    click.echo(f"Test Result: {result.outcome.value.upper()}")
    click.echo("=" * 80)

    click.echo(f"\nTermination Reason: {result.termination_reason.value}")
    click.echo(f"Turn Count: {result.turn_count}")
    click.echo(f"Progress Score: {result.progress_score:.2f}")

    if result.duration_seconds:
        click.echo(f"Duration: {result.duration_seconds:.1f}s")

    click.echo("\nSuccess Criteria:")
    for criterion in result.criteria_status:
        status = "✓" if criterion.met else "✗"
        click.echo(f"  {status} {criterion.criterion}")
        if criterion.evaluation:
            click.echo(f"    → {criterion.evaluation}")

    if result.error_message:
        click.echo(f"\nError: {result.error_message}")

    click.echo("\n" + "-" * 80)
    click.echo("Conversation Transcript:")
    click.echo("-" * 80)

    for i, msg in enumerate(result.transcript, 1):
        role = "USER" if msg.role == "user" else "AGENT"
        click.echo(f"\n[Turn {(i + 1) // 2}] {role}:")
        click.echo(msg.content)

    click.echo("\n" + "=" * 80)


if __name__ == "__main__":
    main()
