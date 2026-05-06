"""Test configuration and fixtures."""

import os
from pathlib import Path

import pytest
from dotenv import load_dotenv

# Load .env file from project root if it exists
env_path = Path(__file__).parent.parent / ".env"
if env_path.exists():
    load_dotenv(env_path)


def pytest_addoption(parser: pytest.Parser) -> None:
    """Register integration-suite opt-in flags."""
    parser.addoption(
        "--run-integration-live",
        action="store_true",
        default=False,
        help="Run live OANDA practice integration tests.",
    )


def pytest_collection_modifyitems(config: pytest.Config, items: list[pytest.Item]) -> None:
    """Skip live integration tests unless they are explicitly requested."""
    if os.getenv("SKIP_INTEGRATION") == "1":
        reason = "Integration tests skipped (SKIP_INTEGRATION=1)"
    elif config.getoption("--run-integration-live"):
        return
    else:
        reason = "Live integration tests require --run-integration-live"

    skip_live_integration = pytest.mark.skip(reason=reason)
    for item in items:
        path_parts = set(item.path.parts)
        if "integration" in path_parts or item.get_closest_marker("integration") is not None:
            item.add_marker(skip_live_integration)
