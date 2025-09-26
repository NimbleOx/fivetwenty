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
└── FiveTwentyError
    ├── StreamStall
    ├── AuthenticationError
    ├── ValidationError
    └── RateLimitError
```


"""Comprehensive module for trading operations."""
---

## Core Exceptions

### `FiveTwentyError`

Base exception for all OANDA API errors.

**Properties:**

- `message` *(str)* - Human-readable error description
- `error_code` *(Optional[str])* - OANDA API error code
- `error_details` *(Dict[str, Any])* - Additional error information
- `response` *(Optional[httpx.Response])* - Original HTTP response

**Example:**
```python
import asyncio


async def main():
    from fivetwenty.exceptions import FiveTwentyError

    try:
        await client.orders.post_market_order(
            account_id="invalid-account",
            instrument="EUR_USD",
            units=10000,
        )
    except FiveTwentyError as e:
        print(f"Error: {e.message}")
        print(f"Code: {e.error_code}")
        print(f"Details: {e.error_details}")

asyncio.run(main())
```

### `StreamStall`

Raised when a streaming connection stalls or times out.

**Example:**
```python
import asyncio


async def main():
    from fivetwenty.exceptions import StreamStall

    try:
        async for item in client.pricing.get_pricing_stream("123-456-789", ["EUR_USD"]):
            pass
    except StreamStall as e:
        print(f"Stream stalled: {e.message}")
        # Implement reconnection logic
        await asyncio.sleep(5)

asyncio.run(main())
```


"""Comprehensive module for trading operations."""
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
from fivetwenty.exceptions import AuthenticationError, FiveTwentyError


async def safe_api_call():
    try:
        result = await client.accounts.get_account_summary("123-456-789")
        return result

    except AuthenticationError as e:
        print(f"Authentication failed: {e.message}")
        return None

    except FiveTwentyError as e:
        print(f"OANDA API error: {e.error_code} - {e.message}")
        return None
```

### Retry with Exponential Backoff
```python
import asyncio
import random

from fivetwenty.exceptions import FiveTwentyError


async def retry_api_call(func, max_retries: int = 3):
    """Retry API call with exponential backoff."""

    for attempt in range(max_retries + 1):
        try:
            return await func()

        except FiveTwentyError as e:
            # Don't retry certain errors
            if e.error_code in ["ACCOUNT_NOT_EXIST", "INVALID_API_TOKEN"]:
                raise

            if attempt == max_retries:
                raise

            delay = 2 ** attempt + random.uniform(0, 1)
            await asyncio.sleep(delay)

    return None
```

---

::: fivetwenty.exceptions
    options:
      show_source: false
      show_root_heading: false
      members_order: source