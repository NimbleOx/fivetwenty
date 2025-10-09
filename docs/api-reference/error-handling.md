# Error Handling Reference

Complete reference for FiveTwenty SDK exception types, error codes, and handling patterns.

## Exception Classes

The SDK provides two exception classes:

### `FiveTwentyError`

Base exception class for all OANDA API errors.

**Attributes:**
- `status` *(int)* - HTTP status code (400, 401, 404, 429, 500, etc.)
- `code` *(str | None)* - OANDA error code (e.g., "INSUFFICIENT_MARGIN")
- `message` *(str)* - Human-readable error description
- `request_id` *(str | None)* - Request ID for debugging
- `retryable` *(bool)* - Whether the error can be retried
- `response` *(httpx.Response | None)* - Original HTTP response
- `details` *(ErrorDetails | None)* - Structured error details

**Properties for Error Classification:**
- `is_client_error` - True for 4xx status codes
- `is_server_error` - True for 5xx status codes
- `is_authentication_error` - True for auth/permission errors
- `is_validation_error` - True for validation errors
- `is_rate_limited` - True for rate limiting (429)
- `is_not_found` - True for 404 errors
- `retry_after` - Seconds to wait (from Retry-After header)

### `StreamStall`

Exception raised when a stream stalls (no data received within timeout).

**Inheritance:** Directly inherits from `Exception`, not `FiveTwentyError`

## Error Handling Patterns

### Basic Exception Handling

```python
import os
from fivetwenty import AsyncClient
from fivetwenty.exceptions import FiveTwentyError

# Setup
token = os.getenv("OANDA_TOKEN")
account_id = "101-001-0000000-001"

async def safe_trade(client: AsyncClient, account_id: str) -> None:
    """Place a trade with error handling."""
    try:
        order = await client.orders.post_market_order(
            account_id=account_id,
            instrument="EUR_USD",
            units=1000,
        )
        print(f"Order placed: {order.order_fill_transaction.id}")

    except FiveTwentyError as e:
        print(f"OANDA error: {e}")
        print(f"Error code: {e.code}")
        print(f"Error message: {e.message}")

    except Exception as e:
        print(f"Unexpected error: {e}")
```

### Specific Error Types

Handle different errors using property-based checking:

```python
import asyncio

from fivetwenty import AsyncClient
from fivetwenty.exceptions import FiveTwentyError


async def handle_specific_errors(client: AsyncClient, account_id: str) -> None:
    """Handle specific error types using properties."""
    try:
        _ = await client.orders.post_market_order(
            account_id=account_id,
            instrument="EUR_USD",
            units=1000000,  # Large position
        )

    except FiveTwentyError as e:
        # Check error type using properties
        if e.is_authentication_error:
            # Invalid or expired token
            print("Authentication failed - check your token")
            # Note: Implement token refresh logic based on your auth system
            # Example: await refresh_token() or restart with new token

        elif e.is_validation_error:
            # Invalid request parameters
            print(f"Invalid request: {e.message}")
            validation_errors = e.get_validation_errors()
            if validation_errors:
                print(f"Validation errors: {validation_errors}")

        elif e.is_not_found:
            # Resource not found
            print(f"Account or instrument not found: {e.message}")

        elif e.is_rate_limited:
            # Rate limited
            retry_after = e.retry_after or 60
            print(f"Rate limited - retry after {retry_after} seconds")
            await asyncio.sleep(retry_after)

        elif e.is_server_error:
            # OANDA server error
            print(f"OANDA server error: {e.message}")
            # Note: Implement notification logic based on your monitoring system
            # Example: await send_alert(e) or log to monitoring service

        else:
            # Other client errors
            print(f"API error: {e.code} - {e.message}")
```

## OANDA Error Codes

The SDK includes 67 specific OANDA error codes:

### Common Trading Errors

```python
from fivetwenty import AsyncClient
from fivetwenty.exceptions import FiveTwentyError, FiveTwentyErrorCode


# Check for specific error codes
async def handle_trading_errors(client: AsyncClient, account_id: str) -> None:
    try:
        _ = await client.orders.post_market_order(
            account_id=account_id,
            instrument="EUR_USD",
            units=1000000,
        )
    except FiveTwentyError as e:
        # Check for specific error codes using if/elif
        if e.code == FiveTwentyErrorCode.INSUFFICIENT_FUNDS.value:
            print("Not enough margin")
            # Note: Implement position sizing logic
            # Example: reduce position size or wait for more margin

        elif e.code == FiveTwentyErrorCode.MARKET_HALTED.value:
            print("Market is closed")
            # Note: Implement market hours checking
            # Example: wait until market opens or schedule for later

        elif e.code == FiveTwentyErrorCode.INVALID_INSTRUMENT.value:
            print("Invalid instrument")

        elif e.code == FiveTwentyErrorCode.CLOSEOUT_POSITION_DOESNT_EXIST.value:
            print("Position already closed")

        elif e.code == FiveTwentyErrorCode.STOP_LOSS_ORDER_ALREADY_EXISTS.value:
            print("Stop loss already set")

        else:
            print(f"Other error: {e.code}")
```

### Error Categories

```python
from fivetwenty.exceptions import FiveTwentyError, FiveTwentyErrorCode


def categorize_error(error: FiveTwentyError) -> str:
    """Categorize errors for different handling."""

    # Account errors (using .value to get string representation)
    account_errors = {
        FiveTwentyErrorCode.INSUFFICIENT_FUNDS.value,
        FiveTwentyErrorCode.ACCOUNT_NOT_ACTIVE.value,
        FiveTwentyErrorCode.ACCOUNT_LOCKED.value,
        FiveTwentyErrorCode.INSUFFICIENT_MARGIN.value,
    }

    # Market errors
    market_errors = {
        FiveTwentyErrorCode.MARKET_HALTED.value,
        FiveTwentyErrorCode.INVALID_INSTRUMENT.value,
        FiveTwentyErrorCode.INSTRUMENT_NOT_TRADEABLE.value,
    }

    # Order errors
    order_errors = {
        FiveTwentyErrorCode.INVALID_ORDER.value,
        FiveTwentyErrorCode.ORDER_DOESNT_EXIST.value,
        FiveTwentyErrorCode.PENDING_ORDER_ALREADY_EXISTS.value,
    }

    if error.code in account_errors:
        return "ACCOUNT"
    elif error.code in market_errors:
        return "MARKET"
    elif error.code in order_errors:
        return "ORDER"
    else:
        return "OTHER"
```

## Retry Strategies

### Exponential Backoff

The SDK includes built-in retry logic, but you can add your own:

```python
import asyncio
import random
from collections.abc import Callable
from decimal import Decimal
from typing import Awaitable, TypeVar

from fivetwenty.exceptions import FiveTwentyError

T = TypeVar("T")

async def retry_with_backoff(
    func: Callable[[], Awaitable[T]],
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
) -> T:
    """Retry with exponential backoff."""

    for attempt in range(max_retries):
        try:
            return await func()

        except FiveTwentyError as e:
            # Only retry rate limiting and server errors
            if e.is_rate_limited:
                # Use server's retry-after if available
                delay = e.retry_after or (base_delay * (2 ** attempt))
                delay = min(float(delay), max_delay)

                # Add jitter
                delay += random.uniform(0, float(delay * Decimal("0.1")))

                if attempt == max_retries - 1:
                    raise

                print(f"Retry {attempt + 1}/{max_retries} after {delay:.1f}s")
                await asyncio.sleep(delay)

            elif e.is_server_error:
                # Retry on server errors
                if attempt == max_retries - 1:
                    raise

                delay = base_delay * (2 ** attempt)
                await asyncio.sleep(delay)

            else:
                # Don't retry client errors
                raise

    raise RuntimeError("Max retries exceeded")

# Usage
async def place_order_with_retry():
    from fivetwenty import AsyncClient
    client = AsyncClient(token="your-token", account_id="your-account")
    account_id = "your-account-id"

    return await retry_with_backoff(
        lambda: client.orders.post_market_order(
            account_id=account_id,
            instrument="EUR_USD",
            units=1000,
        ),
    )
```

### Circuit Breaker

Implement circuit breaker pattern for system protection:

```python
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Callable

from fivetwenty.exceptions import FiveTwentyError


class CircuitState(Enum):
    CLOSED = "closed"  # Normal operation
    OPEN = "open"      # Failing, reject requests
    HALF_OPEN = "half_open"  # Testing recovery

class CircuitBreaker:
    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: int = 60,
        expected_exception: type = FiveTwentyError,
    ):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception
        self.failure_count = 0
        self.last_failure_time = None
        self.state = CircuitState.CLOSED

    async def call(self, func: Callable[..., Any], *args: Any, **kwargs: Any) -> Any:
        """Execute function with circuit breaker protection."""

        if self.state == CircuitState.OPEN:
            if self._should_attempt_reset():
                self.state = CircuitState.HALF_OPEN
            else:
                raise Exception("Circuit breaker is OPEN")

        try:
            result = await func(*args, **kwargs)
            self._on_success()
            return result

        except self.expected_exception as e:
            self._on_failure()
            raise

    def _should_attempt_reset(self) -> bool:
        return (
            self.last_failure_time and
            datetime.now() - self.last_failure_time > timedelta(seconds=self.recovery_timeout)
        )

    def _on_success(self):
        self.failure_count = 0
        self.state = CircuitState.CLOSED

    def _on_failure(self):
        self.failure_count += 1
        self.last_failure_time = datetime.now()

        if self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN
            print(f"Circuit breaker opened after {self.failure_count} failures")

# Usage
breaker = CircuitBreaker(failure_threshold=3, recovery_timeout=30)

async def protected_trade():
    return await breaker.call(
        client.orders.post_market_order,
        account_id=account_id,
        instrument="EUR_USD",
        units=1000,
    )
```

## Error Recovery

### Automatic Recovery

Implement automatic recovery for common issues:

```python
import asyncio
from typing import Any
from fivetwenty import AsyncClient
from fivetwenty.exceptions import FiveTwentyError, StreamStall

class TradingSystem:
    def __init__(self, client: AsyncClient) -> None:
        self.client = client
        self.reconnect_attempts = 0
        self.max_reconnects = 5

    async def place_order_with_recovery(self, account_id: str, instrument: str, units: int) -> Any:
        """Place order with automatic recovery."""

        while self.reconnect_attempts < self.max_reconnects:
            try:
                return await self._place_order(account_id, instrument, units)

            except FiveTwentyError as e:
                if e.is_authentication_error:
                    # Token might be expired
                    await self.refresh_authentication()
                    self.reconnect_attempts += 1

                elif e.is_rate_limited:
                    # Rate limited - wait and retry
                    await asyncio.sleep(e.retry_after or 60)

                elif e.is_server_error:
                    # Server error - exponential backoff
                    await asyncio.sleep(2 ** self.reconnect_attempts)
                    self.reconnect_attempts += 1

                else:
                    # Don't retry other client errors
                    raise

            except StreamStall:
                # Stream disconnected - reconnect
                await self.reconnect_stream()

        raise Exception("Max recovery attempts exceeded")

    async def _place_order(self, account_id: str, instrument: str, units: int) -> Any:
        """Place order implementation."""
        return await self.client.orders.post_market_order(
            account_id=account_id,
            instrument=instrument,
            units=units,
        )

    async def refresh_authentication(self) -> None:
        """Refresh authentication token."""
        print("Refreshing authentication...")
        # Implement token refresh logic

    async def reconnect_stream(self) -> None:
        """Reconnect to streaming endpoint."""
        print("Reconnecting stream...")
        # Implement stream reconnection
```

### State Recovery

Recover state after errors:

```python
import asyncio
from typing import Any
from fivetwenty import AsyncClient
from fivetwenty.exceptions import FiveTwentyError, FiveTwentyErrorCode


class StatefulTrader:
    def __init__(self) -> None:
        self.pending_orders: list[dict[str, Any]] = []
        self.completed_orders: list[Any] = []

    async def execute_orders(self, client: AsyncClient, orders: list[dict[str, Any]]) -> None:
        """Execute orders with state recovery."""

        for order in orders:
            try:
                result = await client.orders.post_market_order(**order)
                self.completed_orders.append(result)

            except FiveTwentyError as e:
                # Save failed order for retry
                self.pending_orders.append(order)
                print(f"Order failed: {e.message}")

                # Try to recover based on error
                if e.code == FiveTwentyErrorCode.INSUFFICIENT_FUNDS.value:
                    # Reduce position size and retry
                    order["units"] = order["units"] // 2
                    self.pending_orders.append(order)

        # Retry pending orders
        if self.pending_orders:
            await self.retry_pending_orders(client)

    async def retry_pending_orders(self, client: AsyncClient) -> None:
        """Retry failed orders."""
        retry_orders = self.pending_orders.copy()
        self.pending_orders.clear()

        await asyncio.sleep(5)  # Wait before retry
        await self.execute_orders(client, retry_orders)
```

## Logging and Monitoring

### Structured Error Logging

```python
import json
import logging
import traceback
from datetime import datetime
from typing import Any

from fivetwenty.exceptions import FiveTwentyError, FiveTwentyErrorCode


class ErrorLogger:
    def __init__(self) -> None:
        self.logger = logging.getLogger(__name__)

    def log_error(self, error: FiveTwentyError, context: dict[str, Any]) -> None:
        """Log errors with structured context."""

        error_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "error_type": type(error).__name__,
            "error_code": error.code,
            "error_message": error.message,
            "severity": self._get_severity(error),
            "context": context,
            "stack_trace": traceback.format_exc(),
        }

        # Log based on severity
        if error_data["severity"] == "CRITICAL":
            self.logger.critical(json.dumps(error_data))
            self.send_alert(error_data)
        elif error_data["severity"] == "ERROR":
            self.logger.error(json.dumps(error_data))
        else:
            self.logger.warning(json.dumps(error_data))

    def _get_severity(self, error: FiveTwentyError) -> str:
        """Determine error severity using error properties."""

        critical_errors = {
            FiveTwentyErrorCode.ACCOUNT_NOT_ACTIVE.value,
            FiveTwentyErrorCode.ACCOUNT_LOCKED.value,
            FiveTwentyErrorCode.INSUFFICIENT_FUNDS.value,
        }

        if error.code in critical_errors:
            return "CRITICAL"
        elif error.is_authentication_error:
            return "ERROR"
        else:
            return "WARNING"

    def send_alert(self, error_data: dict[str, Any]) -> None:
        """Send alerts for critical errors."""
        # Implement alerting (email, SMS, Slack, etc.)
        pass
```

### Error Metrics

Track error patterns:

```python
from collections import Counter, deque
from datetime import datetime, timedelta

from fivetwenty.exceptions import FiveTwentyError, FiveTwentyErrorCode

class ErrorMetrics:
    def __init__(self, window_minutes: int = 60) -> None:
        self.window = timedelta(minutes=window_minutes)
        self.errors: deque[tuple[datetime, FiveTwentyError]] = deque()
        self.error_counts: Counter[str] = Counter()

    def record_error(self, error: FiveTwentyError) -> None:
        """Record error for metrics."""
        now = datetime.now()

        # Add to deque
        self.errors.append((now, error))

        # Clean old errors
        cutoff = now - self.window
        while self.errors and self.errors[0][0] < cutoff:
            self.errors.popleft()

        # Update counts
        self.error_counts[error.code] += 1

    def get_error_rate(self) -> float:
        """Get errors per minute."""
        return len(self.errors) / (self.window.total_seconds() / 60)

    def get_top_errors(self, n: int = 5) -> list[tuple[str, int]]:
        """Get most common errors."""
        return self.error_counts.most_common(n)

    def should_alert(self) -> bool:
        """Check if error rate is concerning."""
        error_rate = self.get_error_rate()
        return error_rate > 10  # More than 10 errors per minute
```

## Testing Error Handling

### Unit Tests

```python
from unittest.mock import AsyncMock

import pytest

from fivetwenty import AsyncClient
from fivetwenty.exceptions import FiveTwentyError, FiveTwentyErrorCode


async def place_order(client: AsyncClient, account_id: str, instrument: str, units: int) -> dict:
    """Place order (stub for testing)."""
    return await client.orders.post_market_order(
        account_id=account_id,
        instrument=instrument,
        units=units,
    )

async def place_order_with_retry(client: AsyncClient, account_id: str, instrument: str, units: int) -> dict:
    """Place order with retry (stub for testing)."""
    return await client.orders.post_market_order(
        account_id=account_id,
        instrument=instrument,
        units=units,
    )

@pytest.mark.asyncio
async def test_insufficient_funds_handling() -> None:
    """Test handling of insufficient funds error."""

    # Mock client to raise error
    mock_client = AsyncMock()
    mock_client.orders.post_market_order.side_effect = FiveTwentyError(
        status=400,
        code=FiveTwentyErrorCode.INSUFFICIENT_FUNDS.value,
        message="Not enough margin",
    )

    # Test error handling
    with pytest.raises(FiveTwentyError) as exc_info:
        await place_order(mock_client, "account", "EUR_USD", 1000000)

    if exc_info.value.code != FiveTwentyErrorCode.INSUFFICIENT_FUNDS.value:
        raise ValueError(f"Expected error code INSUFFICIENT_FUNDS, got '{exc_info.value.code}'")

@pytest.mark.asyncio
async def test_retry_on_server_error() -> None:
    """Test retry logic for server errors."""

    mock_client = AsyncMock()

    # Fail twice with server error, then succeed
    mock_client.orders.post_market_order.side_effect = [
        FiveTwentyError(status=500, message="Server error"),
        FiveTwentyError(status=500, message="Server error"),
        {"order_fill_transaction": {"id": "123"}},
    ]

    result = await place_order_with_retry(mock_client, "account", "EUR_USD", 1000)

    if result["order_fill_transaction"]["id"] != "123":
        raise ValueError(f"Expected transaction id '123', got '{result['order_fill_transaction']['id']}'")
    if mock_client.orders.post_market_order.call_count != 3:
        raise ValueError(f"Expected 3 calls, got {mock_client.orders.post_market_order.call_count}")
```

## Best Practices

1. **Always handle FiveTwentyError** - Never let errors crash your system
2. **Log all errors** - Essential for debugging production issues
3. **Implement retry logic** - But with limits and backoff
4. **Monitor error rates** - Detect problems early
5. **Test error paths** - Error handling code needs testing too
6. **Graceful degradation** - System should handle partial failures
7. **Alert on critical errors** - Don't wait to discover problems

## Next Steps

- Review [streaming](../guides/trading-concepts/streaming.md) for handling stream errors
- Check [best practices](../guides/understanding/best-practices.md) for production systems
- Understand [configuration](../guides/understanding/configuration.md) options