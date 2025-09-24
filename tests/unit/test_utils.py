"""Test internal utilities."""

import os
from decimal import Decimal
from unittest.mock import patch

from fivetwenty._internal.utils import (
    MonotonicTimeout,
    backoff_with_jitter,
    build_user_agent,
    quantize_price,
    stringify_decimals,
)


def test_backoff_with_jitter() -> None:
    """Test exponential backoff calculation."""
    # First attempt should be small
    delay0 = backoff_with_jitter(0)
    assert 0.25 <= delay0 <= 0.75  # 0.5 * (0.5 to 1.0)

    # Should increase exponentially
    delay1 = backoff_with_jitter(1)
    delay2 = backoff_with_jitter(2)
    assert delay1 > delay0
    assert delay2 > delay1

    # Should be capped
    delay_big = backoff_with_jitter(10)
    assert delay_big <= 8.0


def test_stringify_decimals() -> None:
    """Test recursive Decimal to string conversion."""
    data = {
        "price": Decimal("1.23456"),
        "nested": {
            "amount": Decimal("100.50"),
            "values": [Decimal("1.1"), Decimal("2.2"), "not_decimal"],
        },
        "string": "keep_me",
        "number": 42,
    }

    result = stringify_decimals(data)

    assert result["price"] == "1.23456"
    assert result["nested"]["amount"] == "100.50"
    assert result["nested"]["values"] == ["1.1", "2.2", "not_decimal"]
    assert result["string"] == "keep_me"
    assert result["number"] == 42


def test_quantize_price() -> None:
    """Test price quantization."""
    # 5 decimal precision (like EUR/USD)
    price = quantize_price(5, Decimal("1.234567"))
    assert price == Decimal("1.23457")

    # 3 decimal precision (like USD/JPY)
    price = quantize_price(3, Decimal("110.1234"))
    assert price == Decimal("110.123")

    # Already at correct precision
    price = quantize_price(2, Decimal("1.23"))
    assert price == Decimal("1.23")


def test_monotonic_timeout() -> None:
    """Test monotonic timeout helper."""
    import time

    timeout = MonotonicTimeout(0.1)  # 100ms

    # Should not be expired initially
    assert not timeout.expired
    assert timeout.remaining > 0

    # Sleep and check
    time.sleep(0.05)
    assert not timeout.expired
    assert 0 < timeout.remaining < 0.1

    # Sleep more and should expire
    time.sleep(0.1)
    assert timeout.expired
    # When expired, sleep_remaining should return 0
    assert timeout.sleep_remaining() == 0  # type: ignore[unreachable]


def test_build_user_agent_basic() -> None:
    """Test user agent string generation."""
    user_agent = build_user_agent()

    # Should contain package name and version
    assert "fivetwenty/" in user_agent
    assert "python-" in user_agent
    assert "httpx-" in user_agent

    # Should be a reasonable format
    assert user_agent.startswith("fivetwenty/")
    assert ")" in user_agent


def test_build_user_agent_with_extra() -> None:
    """Test user agent with extra environment variable."""
    extra = "MyTradingBot/1.0"

    with patch.dict(os.environ, {"FIVETWENTY_USER_AGENT_EXTRA": extra}):
        user_agent = build_user_agent()
        assert extra in user_agent
        assert user_agent.endswith(f" {extra}")


def test_build_user_agent_without_extra() -> None:
    """Test user agent without extra environment variable."""
    # Ensure the env var is not set
    with patch.dict(os.environ, {}, clear=False):
        if "FIVETWENTY_USER_AGENT_EXTRA" in os.environ:
            del os.environ["FIVETWENTY_USER_AGENT_EXTRA"]

        user_agent = build_user_agent()
        assert not user_agent.endswith(" ")  # No trailing space
        assert "fivetwenty/" in user_agent


def test_stringify_decimals_edge_cases() -> None:
    """Test stringify_decimals with edge cases."""
    # Test with None
    assert stringify_decimals(None) is None

    # Test with empty structures
    assert stringify_decimals([]) == []
    assert stringify_decimals({}) == {}

    # Test with nested empty structures
    data = {"empty_list": [], "empty_dict": {}, "nested": {"deep": {"decimal": Decimal("1.5")}}}
    result = stringify_decimals(data)
    assert result["empty_list"] == []
    assert result["empty_dict"] == {}
    assert result["nested"]["deep"]["decimal"] == "1.5"

    # Test with very large and very small decimals
    large_decimal = Decimal("999999999999.999999999")
    small_decimal = Decimal("0.000000001")

    assert stringify_decimals(large_decimal) == "999999999999.999999999"
    assert stringify_decimals(small_decimal) == "0.000000001"


def test_backoff_with_jitter_edge_cases() -> None:
    """Test backoff with jitter edge cases."""
    # Test with attempt 0
    delay = backoff_with_jitter(0)
    assert delay > 0

    # Test with custom base and cap
    delay = backoff_with_jitter(1, base=1.0, cap=2.0)
    assert delay <= 2.0

    # Test jitter range
    delays = [backoff_with_jitter(1) for _ in range(100)]
    # All delays should be different due to jitter
    assert len(set(delays)) > 1  # Should have variety

    # All delays should be within expected range for attempt 1
    for delay in delays:
        assert 0.5 <= delay <= 1.5  # base=0.5, attempt 1: 0.5 * 2^1 = 1.0, jitter 0.5-1.0


def test_quantize_price_edge_cases() -> None:
    """Test price quantization edge cases."""
    # Test with zero precision
    price = quantize_price(0, Decimal("1.999"))
    assert price == Decimal("2")

    # Test with negative numbers
    price = quantize_price(2, Decimal("-1.999"))
    assert price == Decimal("-2.00")

    # Test with very small numbers
    price = quantize_price(5, Decimal("0.000001"))
    assert price == Decimal("0.00000")

    # Test with large precision
    price = quantize_price(10, Decimal("1.123456789012345"))
    assert price == Decimal("1.1234567890")


def test_monotonic_timeout_edge_cases() -> None:
    """Test MonotonicTimeout edge cases."""
    # Test with very small timeout
    timeout = MonotonicTimeout(0.001)  # 1ms
    assert not timeout.expired

    # Test sleep_remaining with max_sleep
    timeout = MonotonicTimeout(10.0)  # 10 seconds
    sleep_time = timeout.sleep_remaining(max_sleep=0.5)
    assert sleep_time == 0.5  # Should be capped

    # Test sleep_remaining when expired
    timeout = MonotonicTimeout(0.0)  # Immediately expired
    assert timeout.expired
    assert timeout.sleep_remaining() == 0.0

    # Test elapsed property
    timeout = MonotonicTimeout(1.0)
    assert timeout.elapsed >= 0
    assert timeout.elapsed < 0.1  # Should be very small initially
