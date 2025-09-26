# Error Handling

Robust error handling is critical for production trading systems. The FiveTwenty provides comprehensive error types and handling mechanisms.

## Error Hierarchy

The SDK uses a hierarchical error system:

```text
Exception
└── FiveTwentyError (base for all OANDA errors)
    ├── BadRequest (400 errors)
    ├── Unauthorized (401 errors)
    ├── Forbidden (403 errors)
    ├── NotFound (404 errors)
    ├── MethodNotAllowed (405 errors)
    ├── TooManyRequests (429 errors)
    └── InternalServerError (500+ errors)
```

## Basic Error Handling

### Basic Try-Catch

```python
from fivetwenty.exceptions import FiveTwentyError


async def safe_trade(client, account_id):
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

Handle different errors differently:

```python
import asyncio

from fivetwenty.exceptions import BadRequest, Forbidden, InternalServerError, NotFound, TooManyRequests, Unauthorized


async def handle_specific_errors(client, account_id):
    """Handle specific error types."""
    try:
        result = await client.orders.post_market_order(
            account_id=account_id,
            instrument="EUR_USD",
            units=1000000,  # Large position
        )

    except BadRequest as e:
        # Invalid request parameters
        print(f"Invalid request: {e.message}")
        if "INSUFFICIENT_FUNDS" in str(e):
            print("Not enough margin available")

    except Unauthorized as e:
        # Invalid or expired token
        print("Authentication failed - check your token")
        # Note: Implement token refresh logic based on your auth system
        # Example: await refresh_token() or restart with new token

    except Forbidden as e:
        # No permission for this operation
        print(f"Permission denied: {e.message}")

    except NotFound as e:
        # Resource not found
        print(f"Account or instrument not found: {e.message}")

    except TooManyRequests as e:
        # Rate limited
        retry_after = e.retry_after or 60
        print(f"Rate limited - retry after {retry_after} seconds")
        await asyncio.sleep(retry_after)

    except InternalServerError as e:
        # OANDA server error
        print(f"OANDA server error: {e.message}")
        # Note: Implement notification logic based on your monitoring system
        # Example: await send_alert(e) or log to monitoring service
```

## OANDA Error Codes

The SDK includes 67 specific OANDA error codes:

### Common Trading Errors

```python
from fivetwenty.exceptions import FiveTwentyErrorCode


# Check for specific error codes
async def handle_trading_errors(client, account_id):
    try:
        order = await client.orders.post_market_order(
            account_id=account_id,
            instrument="EUR_USD",
            units=1000000,
        )
    except FiveTwentyError as e:
        match e.code:
            case FiveTwentyErrorCode.INSUFFICIENT_FUNDS:
                print("Not enough margin")
                # Note: Implement position sizing logic
                # Example: reduce position size or wait for more margin

            case FiveTwentyErrorCode.MARKET_HALTED:
                print("Market is closed")
                # Note: Implement market hours checking
                # Example: wait until market opens or schedule for later

            case FiveTwentyErrorCode.INVALID_INSTRUMENT:
                print("Invalid instrument")

            case FiveTwentyErrorCode.CLOSEOUT_POSITION_DOESNT_EXIST:
                print("Position already closed")

            case FiveTwentyErrorCode.STOP_LOSS_ORDER_ALREADY_EXISTS:
                print("Stop loss already set")

            case _:
                print(f"Other error: {e.code}")
```

### Error Categories

```python
from fivetwenty.exceptions import FiveTwentyError, FiveTwentyErrorCode


def categorize_error(error: FiveTwentyError) -> str:
    """Categorize errors for different handling."""

    # Account errors
    account_errors = {
        FiveTwentyErrorCode.INSUFFICIENT_FUNDS,
        FiveTwentyErrorCode.ACCOUNT_NOT_ACTIVE,
        FiveTwentyErrorCode.ACCOUNT_LOCKED,
        FiveTwentyErrorCode.INSUFFICIENT_MARGIN,
    }

    # Market errors
    market_errors = {
        FiveTwentyErrorCode.MARKET_HALTED,
        FiveTwentyErrorCode.INVALID_INSTRUMENT,
        FiveTwentyErrorCode.INSTRUMENT_NOT_TRADEABLE,
    }

    # Order errors
    order_errors = {
        FiveTwentyErrorCode.INVALID_ORDER,
        FiveTwentyErrorCode.ORDER_DOESNT_EXIST,
        FiveTwentyErrorCode.PENDING_ORDER_ALREADY_EXISTS,
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
from typing import TypeVar

T = TypeVar("T")

async def retry_with_backoff(
    func: Callable[[], T],
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
) -> T:
    """Retry with exponential backoff."""

    for attempt in range(max_retries):
        try:
            return await func()

        except TooManyRequests as e:
            # Use server's retry-after if available
            delay = e.retry_after or (base_delay * (2 ** attempt))
            delay = min(delay, max_delay)

            # Add jitter
            delay += random.uniform(0, delay * Decimal("0.1"))

            if attempt == max_retries - 1:
                raise

            print(f"Retry {attempt + 1}/{max_retries} after {delay:.1f}s")
            await asyncio.sleep(delay)

        except (InternalServerError, httpx.TimeoutException) as e:
            # Retry on server errors and timeouts
            if attempt == max_retries - 1:
                raise

            delay = base_delay * (2 ** attempt)
            await asyncio.sleep(delay)

    raise RuntimeError("Max retries exceeded")

# Usage
async def place_order_with_retry():
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

    async def call(self, func, *args, **kwargs):
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
class TradingSystem:
    def __init__(self, client):
        self.client = client
        self.reconnect_attempts = 0
        self.max_reconnects = 5

    async def place_order_with_recovery(self, account_id, instrument, units):
        """Place order with automatic recovery."""

        while self.reconnect_attempts < self.max_reconnects:
            try:
                return await self._place_order(account_id, instrument, units)

            except Unauthorized:
                # Token might be expired
                await self.refresh_authentication()
                self.reconnect_attempts += 1

            except TooManyRequests as e:
                # Rate limited - wait and retry
                await asyncio.sleep(e.retry_after or 60)

            except InternalServerError:
                # Server error - exponential backoff
                await asyncio.sleep(2 ** self.reconnect_attempts)
                self.reconnect_attempts += 1

            except StreamStall:
                # Stream disconnected - reconnect
                await self.reconnect_stream()

        raise Exception("Max recovery attempts exceeded")

    async def refresh_authentication(self):
        """Refresh authentication token."""
        print("Refreshing authentication...")
        # Implement token refresh logic

    async def reconnect_stream(self):
        """Reconnect to streaming endpoint."""
        print("Reconnecting stream...")
        # Implement stream reconnection
```

### State Recovery

Recover state after errors:

```python
from fivetwenty.exceptions import FiveTwentyError, FiveTwentyErrorCode


class StatefulTrader:
    def __init__(self):
        self.pending_orders = []
        self.completed_orders = []

    async def execute_orders(self, client, orders):
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
                if e.code == FiveTwentyErrorCode.INSUFFICIENT_FUNDS:
                    # Reduce position size and retry
                    order["units"] = order["units"] // 2
                    self.pending_orders.append(order)

        # Retry pending orders
        if self.pending_orders:
            await self.retry_pending_orders(client)

    async def retry_pending_orders(self, client):
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
from datetime import datetime

from fivetwenty.exceptions import FiveTwentyError, FiveTwentyErrorCode


class ErrorLogger:
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def log_error(self, error: FiveTwentyError, context: dict):
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
        """Determine error severity."""

        critical_errors = {
            FiveTwentyErrorCode.ACCOUNT_NOT_ACTIVE,
            FiveTwentyErrorCode.ACCOUNT_LOCKED,
            FiveTwentyErrorCode.INSUFFICIENT_FUNDS,
        }

        if error.code in critical_errors:
            return "CRITICAL"
        elif isinstance(error, (Unauthorized, Forbidden)):
            return "ERROR"
        else:
            return "WARNING"

    def send_alert(self, error_data):
        """Send alerts for critical errors."""
        # Implement alerting (email, SMS, Slack, etc.)
        pass
```

### Error Metrics

Track error patterns:

```python
from fivetwenty.exceptions import FiveTwentyError, FiveTwentyErrorCode

from collections import Counter, deque
from datetime import datetime, timedelta

class ErrorMetrics:
    def __init__(self, window_minutes: int = 60):
        self.window = timedelta(minutes=window_minutes)
        self.errors = deque()
        self.error_counts = Counter()

    def record_error(self, error: FiveTwentyError):
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

    def get_top_errors(self, n: int = 5) -> list:
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

from fivetwenty.exceptions import FiveTwentyError


@pytest.mark.asyncio
async def test_insufficient_funds_handling():
    """Test handling of insufficient funds error."""

    # Mock client to raise error
    mock_client = AsyncMock()
    mock_client.orders.post_market_order.side_effect = FiveTwentyError(
        code=FiveTwentyErrorCode.INSUFFICIENT_FUNDS,
        message="Not enough margin",
    )

    # Test error handling
    with pytest.raises(FiveTwentyError) as exc_info:
        await place_order(mock_client, "account", "EUR_USD", 1000000)

    assert exc_info.value.code == FiveTwentyErrorCode.INSUFFICIENT_FUNDS

@pytest.mark.asyncio
async def test_retry_on_server_error():
    """Test retry logic for server errors."""

    mock_client = AsyncMock()

    # Fail twice, then succeed
    mock_client.orders.post_market_order.side_effect = [
        InternalServerError("Server error"),
        InternalServerError("Server error"),
        {"order_fill_transaction": {"id": "123"}},
    ]

    result = await place_order_with_retry(mock_client, "account", "EUR_USD", 1000)

    assert result["order_fill_transaction"]["id"] == "123"
    assert mock_client.orders.post_market_order.call_count == 3
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

- Review [streaming](streaming.md) for handling stream errors
- Check [best practices](best-practices.md) for production systems
- Understand [configuration](configuration.md) options