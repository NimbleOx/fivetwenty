"""Internal utility functions."""

import random
import sys
from datetime import datetime
from decimal import Decimal
from time import monotonic
from typing import Any

from .datetime import format_datetime_for_oanda as format_datetime_for_oanda  # noqa: PLC0414 - keep the existing import path

try:
    import httpx

    from .. import __version__
except ImportError:
    # Handle cases where these aren't available during early setup
    httpx = None  # type: ignore
    __version__ = "20.1.0"


def backoff_with_jitter(attempt: int, base: float = 0.5, cap: float = 8.0) -> float:
    """
    Calculate exponential backoff with jitter.

    Args:
        attempt: The attempt number (0-indexed)
        base: Base delay in seconds
        cap: Maximum delay in seconds

    Returns:
        Delay in seconds with jitter applied
    """
    delay = min(cap, base * (2**attempt))
    # Add jitter: 50% to 100% of calculated delay
    jitter = random.random() / 2.0  # 0 to 0.5
    result: float = delay * (0.5 + jitter)
    return result


def build_user_agent() -> str:
    """Build User-Agent string with version info."""
    import os

    # Base user agent
    base = f"fivetwenty/{__version__} (python-{sys.version_info[0]}.{sys.version_info[1]}"
    if httpx:
        base += f"; httpx-{httpx.__version__}"
    base += ")"

    # Optional extra from environment
    extra = os.environ.get("FIVETWENTY_USER_AGENT_EXTRA")
    return f"{base} {extra}" if extra else base


def stringify_decimals(obj: Any, *, datetime_format: object | None = None) -> Any:
    """
    Recursively convert Decimals, and optionally datetimes, to wire strings.

    This prevents future misses when new Decimal fields appear in the API.

    Args:
        obj: The object to process
        datetime_format: When supplied, also format Python datetime values.

    Returns:
        The object with all Decimals converted to strings
    """
    if isinstance(obj, Decimal):
        return format(obj, "f")
    if isinstance(obj, datetime) and datetime_format is not None:
        return format_datetime_for_oanda(obj, datetime_format)
    if isinstance(obj, list):
        return [stringify_decimals(item, datetime_format=datetime_format) for item in obj]
    if isinstance(obj, dict):
        return {key: stringify_decimals(value, datetime_format=datetime_format) for key, value in obj.items()}
    return obj


def quantize_price(precision: int, value: Decimal) -> Decimal:
    """
    Round a price to the specified precision.

    Args:
        precision: Number of decimal places
        value: The price to quantize

    Returns:
        The quantized price
    """
    quantizer = Decimal(10) ** (-precision)
    return value.quantize(quantizer)


class MonotonicTimeout:
    """Helper for timeout tracking using monotonic time."""

    def __init__(self, timeout_seconds: float):
        self.timeout_seconds = timeout_seconds
        self.start_time = monotonic()

    @property
    def elapsed(self) -> float:
        """Get elapsed time in seconds."""
        return monotonic() - self.start_time

    @property
    def expired(self) -> bool:
        """Check if timeout has expired."""
        return self.elapsed >= self.timeout_seconds
