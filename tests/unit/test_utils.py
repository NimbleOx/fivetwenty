"""Test internal utilities."""

import os
from datetime import datetime, timezone
from decimal import Decimal
from unittest.mock import patch

import pytest

from fivetwenty._internal.utils import (
    MonotonicTimeout,
    backoff_with_jitter,
    build_user_agent,
    format_datetime_for_oanda,
    quantize_price,
    stringify_decimals,
)


@pytest.mark.parametrize(("attempt", "base", "cap", "random_value", "expected"), [(0, 0.5, 8, 0, 0.25), (0, 0.5, 8, 1, 0.5), (2, 0.5, 8, 0.5, 1.5), (10, 0.5, 8, 1, 8), (4, 3, 5, 0, 2.5)])
def test_backoff_exponential_growth_jitter_and_cap(monkeypatch, attempt, base, cap, random_value, expected):
    monkeypatch.setattr("fivetwenty._internal.utils.random.random", lambda: random_value)
    assert backoff_with_jitter(attempt, base, cap) == expected


@pytest.mark.parametrize(("elapsed", "expired"), [(0, False), (9.75, False), (10, True), (11, True)])
def test_timeout_boundaries_use_a_monotonic_clock(monkeypatch, elapsed, expired):
    now = 100.0
    monkeypatch.setattr("fivetwenty._internal.utils.monotonic", lambda: now)
    timeout = MonotonicTimeout(10)
    now += elapsed
    assert timeout.elapsed == elapsed
    assert timeout.expired is expired


def test_recursive_wire_conversion_does_not_mutate_input():
    when = datetime(2024, 1, 1, tzinfo=timezone.utc)
    original = {"items": [{"units": Decimal("1E-8"), "gtdTime": when}], "optional": None, "flag": False}
    assert stringify_decimals(original, datetime_format="UNIX") == {"items": [{"units": "0.00000001", "gtdTime": "1704067200.000000000"}], "optional": None, "flag": False}
    assert original["items"][0]["gtdTime"] is when
    assert original["items"][0]["units"] == Decimal("1E-8")


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


def test_format_datetime_for_oanda_rfc3339_preserves_existing_isoformat() -> None:
    """Test RFC3339 formatting preserves the existing isoformat behavior."""
    value = datetime(2024, 1, 1, 12, 0, 0, 123456, tzinfo=timezone.utc)

    assert format_datetime_for_oanda(value, "RFC3339") == value.isoformat()


def test_format_datetime_for_oanda_unix_uses_nanosecond_precision() -> None:
    """Test UNIX formatting uses OANDA's seconds.nanoseconds representation."""
    value = datetime(2024, 1, 1, 12, 0, 0, 123456, tzinfo=timezone.utc)

    assert format_datetime_for_oanda(value, "UNIX") == "1704110400.123456000"


def test_format_datetime_for_oanda_unix_treats_naive_datetimes_as_utc() -> None:
    """Test UNIX formatting avoids local-timezone dependent output."""
    value = datetime(2024, 1, 1, 12, 0, 0, 123456)

    assert format_datetime_for_oanda(value, "UNIX") == "1704110400.123456000"


@pytest.mark.parametrize(("value", "expected"), [(datetime(1969, 12, 31, 23, 59, 59, 750000, tzinfo=timezone.utc), "-0.250000000"), (datetime(9999, 1, 1, 0, 0, 0, 999999, tzinfo=timezone.utc), "253370764800.999999000")])
def test_unix_datetime_conversion_avoids_float_rounding(value, expected):
    assert format_datetime_for_oanda(value, "UNIX") == expected


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
