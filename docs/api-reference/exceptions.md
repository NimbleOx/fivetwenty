# Exceptions API Reference

!!! note "📚 Reference - Information-oriented content"
    **Use this reference when:** You need to look up exception types, error codes, or error handling patterns

    **Content type:** Comprehensive technical specifications for SDK exception handling

    **Assumed knowledge:** Basic Python exception handling and FiveTwenty usage

Complete reference for FiveTwenty exception types and error handling patterns.

---

## Exception Hierarchy

```text
Exception
├── FiveTwentyError
└── StreamStall
```

---

## Core Exceptions

### `FiveTwentyError`

Enhanced exception for all OANDA API errors with comprehensive error information.

**Constructor Parameters:**

- `status` *(int)* - HTTP status code
- `code` *(str | None)* - OANDA API error code
- `message` *(str)* - Human-readable error description
- `request_id` *(str | None)* - Request ID from response headers
- `retryable` *(bool)* - Whether the error is retryable (default: False)
- `response` *(httpx.Response | None)* - Original HTTP response
- `details` *(ErrorDetails | None)* - Structured error details with validation errors

**Properties:**

- `status` *(int)* - HTTP status code
- `code` *(str | None)* - OANDA API error code
- `message` *(str)* - Human-readable error description
- `request_id` *(str | None)* - Request ID for debugging
- `retryable` *(bool)* - Whether this error can be retried
- `response` *(httpx.Response | None)* - Original HTTP response
- `details` *(ErrorDetails | None)* - Structured error details

**Computed Properties:**

- `error_category` *(ErrorCategory | None)* - Error category (AUTHENTICATION, VALIDATION, etc.)
- `error_severity` *(ErrorSeverity)* - Error severity (INFO, WARNING, ERROR, CRITICAL)
- `is_client_error` *(bool)* - True if 4xx status code
- `is_server_error` *(bool)* - True if 5xx status code
- `is_authentication_error` *(bool)* - True if authentication/authorization error
- `is_validation_error` *(bool)* - True if validation error
- `is_rate_limited` *(bool)* - True if rate limiting error
- `is_not_found` *(bool)* - True if 404 or not found error
- `retry_after` *(int | None)* - Seconds to wait before retrying (from Retry-After header)

**Methods:**

- `get_validation_errors() -> dict[str, list[str]]` - Get validation errors grouped by field
- `get_remediation_message() -> str | None` - Get suggested fix for common errors

**Example:**
```python
import asyncio

from fivetwenty import AsyncClient, FiveTwentyError


async def main() -> None:
    async with AsyncClient() as client:
        try:
            await client.orders.post_market_order(
                account_id=client.account_id,
                instrument="EUR_USD",
                units=10000,
            )
        except FiveTwentyError as e:
            print(f"Status: {e.status}")
            print(f"Code: {e.code}")
            print(f"Message: {e.message}")
            print(f"Request ID: {e.request_id}")

            # Check error type
            if e.is_authentication_error:
                print("Authentication issue")
            elif e.is_validation_error:
                print("Validation errors:", e.get_validation_errors())
            elif e.is_rate_limited:
                print(f"Rate limited - retry after {e.retry_after}s")

            # Get remediation advice
            if remediation := e.get_remediation_message():
                print(f"Fix: {remediation}")


asyncio.run(main())
```

### `StreamStall`

Exception raised when a stream stalls (no data received within timeout period).

**Inheritance:** Inherits from `Exception` (not `FiveTwentyError`)

**Example:**
```python
import asyncio

from fivetwenty import AsyncClient, StreamStall


async def main() -> None:
    async with AsyncClient() as client:
        try:
            async for price in client.pricing.get_pricing_stream(
                account_id=client.account_id,
                instruments=["EUR_USD"],
                stall_timeout=30.0,
            ):
                print(f"Price: {price}")
        except StreamStall as e:
            print(f"Stream stalled: {e}")
            # Implement reconnection logic here
            print("Reconnecting in 5 seconds...")
            await asyncio.sleep(5)


asyncio.run(main())
```


---

## Common Error Codes

### Account Errors
| Error Code | Description |
|------------|-------------|
| `ACCOUNT_NOT_EXIST` | Account doesn't exist |
| `ACCOUNT_NOT_TRADEABLE` | Account cannot trade |
| `INSUFFICIENT_AUTHORIZATION` | Lack permissions |

### Order Errors
| Error Code | Description |
|------------|-------------|
| `INSUFFICIENT_MARGIN` | Not enough margin |
| `INSTRUMENT_NOT_TRADEABLE` | Cannot trade instrument |
| `ORDER_DOESNT_EXIST` | Order not found |
| `PRICE_OUT_OF_BOUNDS` | Price too far from market |

### Trade Errors
| Error Code | Description |
|------------|-------------|
| `TRADE_DOESNT_EXIST` | Trade not found |
| `CLOSEOUT_POSITION_DOESNT_EXIST` | No position to close |
| `INSUFFICIENT_LIQUIDITY` | Market liquidity issues |

---

## Error Handling Patterns

### Basic Error Handling
```python
from fivetwenty import AsyncClient, FiveTwentyError


async def safe_api_call(client: AsyncClient, account_id: str):
    """Safely call API with error handling."""
    try:
        result = await client.accounts.get_account_summary(account_id)
        return result

    except FiveTwentyError as e:
        # Check specific error types using properties
        if e.is_authentication_error:
            print(f"Authentication failed: {e.message}")
        elif e.is_not_found:
            print(f"Account not found: {account_id}")
        else:
            print(f"OANDA API error: {e.code} - {e.message}")

        return None
```

### Retry with Exponential Backoff
```python
import asyncio
import random
from collections.abc import Awaitable, Callable
from typing import TypeVar

from fivetwenty import FiveTwentyError

T = TypeVar("T")


async def retry_api_call(
    func: Callable[[], Awaitable[T]], max_retries: int = 3
) -> T | None:
    """Retry API call with exponential backoff."""

    for attempt in range(max_retries + 1):
        try:
            return await func()

        except FiveTwentyError as e:
            # Don't retry non-retryable errors
            if not e.retryable:
                raise

            # Don't retry client errors (4xx)
            if e.is_client_error and not e.is_rate_limited:
                raise

            if attempt == max_retries:
                raise

            # Use retry_after for rate limiting, otherwise exponential backoff
            if e.retry_after:
                delay = float(e.retry_after)
            else:
                delay = 2**attempt + random.uniform(0, 1)

            print(f"Retry attempt {attempt + 1}/{max_retries} after {delay:.1f}s")
            await asyncio.sleep(delay)

    return None
```

---

::: fivetwenty.exceptions
    options:
      show_source: false
      show_root_heading: false
      members_order: source