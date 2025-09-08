"""Test internal utilities."""

from decimal import Decimal
import pytest

from oanda._internal.utils import (
    backoff_with_jitter,
    stringify_decimals,
    quantize_price,
    MonotonicTimeout,
)


def test_backoff_with_jitter():
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


def test_stringify_decimals():
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


def test_quantize_price():
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


def test_monotonic_timeout():
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
    assert timeout.remaining <= 0
    
    # Sleep remaining should be 0 when expired
    assert timeout.sleep_remaining() == 0