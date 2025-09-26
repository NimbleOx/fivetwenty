# FiveTwenty SDK Best Practices

Essential patterns and practices for building robust applications with the FiveTwenty SDK.

## Client Architecture Patterns

### Context Manager Usage

Always use context managers for proper resource cleanup:

```python
import os
from fivetwenty import AsyncClient, Client, Environment

# Setup
token = os.getenv("OANDA_TOKEN")
account_id = "101-001-0000000-001"

# AsyncClient
async def example_async():
    async with AsyncClient(token=token, environment=Environment.PRACTICE) as client:
        # Client automatically cleaned up on exit
        return await client.accounts.get_account(account_id)

# Sync Client
def example_sync():
    with Client(token=token, environment=Environment.PRACTICE) as client:
        # Background thread and queues automatically cleaned up
        return client.accounts.get_account(account_id)
```

### Connection Reuse

Reuse client instances across multiple operations:

```python
import os
from fivetwenty import AsyncClient, Environment

# Setup
token = os.getenv("OANDA_TOKEN")
account_id = "101-001-0000000-001"

# Good: Reuse client for multiple operations
async def good_example():
    async with AsyncClient(token=token, environment=Environment.PRACTICE) as client:
        account = await client.accounts.get_account(account_id)
        positions = await client.positions.get_positions(account_id)
        orders = await client.orders.get_orders(account_id)
        return account, positions, orders

# Bad: Create new client for each operation
async def get_account():
    async with AsyncClient(token=token, environment=Environment.PRACTICE) as client:
        return await client.accounts.get_account(account_id)
```

### Concurrent Operations

Use asyncio.gather() for concurrent API calls:

```python
import asyncio
import os
from fivetwenty import AsyncClient, Environment

# Setup
token = os.getenv("OANDA_TOKEN")
account_id = "101-001-0000000-001"

async def concurrent_example():
    async with AsyncClient(token=token, environment=Environment.PRACTICE) as client:
        # Efficient: Concurrent requests
        account, positions, orders = await asyncio.gather(
            client.accounts.get_account(account_id),
            client.positions.get_positions(account_id),
            client.orders.get_orders(account_id)
        )

        # Inefficient: Sequential requests
        account = await client.accounts.get_account(account_id)
        positions = await client.positions.get_positions(account_id)
        orders = await client.orders.get_orders(account_id)

        return account, positions, orders
```

## Financial Precision

### Decimal Usage

Always use Decimal for financial calculations:

```python
from decimal import Decimal

# Example account balance (typically from OANDA API)
account_balance = Decimal("10000.00")

# Good: Exact precision
position_size = Decimal("10000")
risk_amount = account_balance * Decimal("0.02")  # 2% risk
stop_distance = Decimal("0.0050")  # 50 pips

# Bad: Floating point errors (commented out)
# position_size = 10000.0
# risk_amount = float(account_balance) * 0.02
# stop_distance = 0.0050
```

### Price Calculation Precision

Handle OANDA's price precision requirements:

```python
from decimal import Decimal

# OANDA price precision (5 decimal places for majors)
price = Decimal("1.08456").quantize(Decimal("0.00001"))

# Position sizing with exact arithmetic
def calculate_position_size(
    account_balance: str,  # AccountUnits from OANDA
    risk_percentage: Decimal,
    stop_loss_pips: int,
    pip_value: Decimal,
) -> Decimal:
    """Calculate position size with exact precision."""
    balance = Decimal(account_balance)
    risk_amount = balance * (risk_percentage / 100)
    risk_per_unit = stop_loss_pips * pip_value
    position_size = risk_amount / risk_per_unit
    return position_size.quantize(Decimal("1"))  # Round to whole units
```

### Field Type Handling

FiveTwenty automatically converts between Decimal and string fields:

```python
import os
from decimal import Decimal
from fivetwenty import AsyncClient, Environment

# Setup
token = os.getenv("OANDA_TOKEN")
account_id = "101-001-0000000-001"

async def example_order():
    async with AsyncClient(token=token, environment=Environment.PRACTICE) as client:
        # SDK handles conversion automatically
        order = await client.orders.post_limit_order(
            account_id=account_id,
            instrument="EUR_USD",
            units=Decimal("10000"),  # Converted to string for API
            price=Decimal("1.0850")  # Converted to string for API
        )

        # Response fields are properly typed
        filled_price = Decimal(order.order_fill_transaction.price)  # string -> Decimal
        return order, filled_price
```

## Error Handling Patterns

### Exception Hierarchy

Use specific exception types for targeted handling:

```python
import asyncio
import os
from fivetwenty import AsyncClient, Environment
from fivetwenty.exceptions import (
    BadRequest, InternalServerError, TooManyRequests
)

# Setup
token = os.getenv("OANDA_TOKEN")
account_id = "101-001-0000000-001"

async def example_error_handling():
    async with AsyncClient(token=token, environment=Environment.PRACTICE) as client:
        try:
            order = await client.orders.post_market_order(
                account_id=account_id,
                instrument="EUR_USD",
                units=1000
            )
        except BadRequest as e:
            if "INSUFFICIENT_MARGIN" in str(e):
                # Reduce position size
                await handle_margin_error(e)
            elif "INVALID_INSTRUMENT" in str(e):
                # Skip this instrument
                return None
        except TooManyRequests as e:
            # Respect rate limits
            await asyncio.sleep(e.retry_after or 60)
        except InternalServerError:
            # OANDA server error - retry with backoff
            await retry_with_backoff()
        return order

async def handle_margin_error(error) -> None:
    """Handle margin errors."""
    pass

async def retry_with_backoff() -> None:
    """Retry with backoff."""
    pass
```

### Retry Patterns

Implement exponential backoff for retryable errors:

```python
import asyncio
import random
from collections.abc import Callable
from typing import Any
from fivetwenty.exceptions import InternalServerError, TooManyRequests

async def retry_with_backoff(
    operation: Callable[[], Any],
    max_retries: int = 3,
    base_delay: float = 1.0
) -> Any:
    """Retry operation with exponential backoff."""
    for attempt in range(max_retries):
        try:
            return await operation()
        except (InternalServerError, TooManyRequests):
            if attempt == max_retries - 1:
                raise

            # Exponential backoff with jitter
            delay = base_delay * (2 ** attempt)
            jitter = random.random() * 0.3 * delay
            await asyncio.sleep(delay + jitter)
    return None  # Explicit return for all code paths
```

## Streaming Best Practices

### Stream Resource Management

Properly handle streaming connections:

```python
import asyncio
from collections.abc import AsyncIterator
from fivetwenty import AsyncClient
from fivetwenty.exceptions import StreamStall

async def robust_price_stream(
    client: AsyncClient,
    account_id: str,
    instruments: list[str]
) -> AsyncIterator:
    """Streaming with proper error handling."""
    max_retries = 5
    retry_count = 0

    while retry_count < max_retries:
        try:
            async for price in client.pricing.get_pricing_stream(
                account_id=account_id,
                instruments=instruments
            ):
                # Reset retry count on successful data
                retry_count = 0
                yield price

        except StreamStall:
            retry_count += 1
            if retry_count >= max_retries:
                raise
            await asyncio.sleep(2 ** retry_count)  # Exponential backoff
```

### Backpressure Management

Handle fast-moving data appropriately:

```python
import os
from fivetwenty import AsyncClient, Client, Environment

# Setup
token = os.getenv("OANDA_TOKEN")
account_id = "101-001-0000000-001"

async def async_stream_example():
    async with AsyncClient(token=token, environment=Environment.PRACTICE) as client:
        # AsyncClient: Direct processing (no buffering)
        async for price in client.pricing.get_pricing_stream(
            account_id=account_id,
            instruments=["EUR_USD"]
        ):
            # Process immediately - don't block the stream
            await process_price_async(price)

def sync_stream_example():
    with Client(token=token, environment=Environment.PRACTICE) as client:
        # Sync Client: Bounded queues prevent memory issues
        for price in client.pricing.get_pricing_stream(
            account_id=account_id,
            instruments=["EUR_USD"]
        ):
            # Queue automatically manages backpressure
            process_price_sync(price)

async def process_price_async(price) -> None:
    """Process price data asynchronously."""
    pass

def process_price_sync(price) -> None:
    """Process price data synchronously."""
    pass
```

## Environment Management

### Environment-Specific Configuration

Use different settings for practice vs live:

```python
import os
from fivetwenty import AsyncClient, Environment

def get_token(is_live: bool) -> str:
    """Get appropriate token for environment."""
    import os
    if is_live:
        return os.environ["OANDA_LIVE_TOKEN"]
    return os.environ["OANDA_PRACTICE_TOKEN"]

def create_client(is_live: bool = False) -> AsyncClient:
    """Create client with environment-appropriate settings."""
    env = Environment.LIVE if is_live else Environment.PRACTICE
    timeout = 30.0 if is_live else 10.0  # Longer timeout for live

    return AsyncClient(
        token=get_token(is_live),
        environment=env,
        timeout=timeout
    )
```

### Token Security

Never hardcode tokens or log sensitive data:

```python
import os
import logging

logger = logging.getLogger(__name__)

# Good: Environment variables
token = os.environ["OANDA_TOKEN"]

# Good: Masked logging
logger.info(f"Using token: {token[:8]}...")

# Bad: Hardcoded token
token = "your-actual-token-here"

# Bad: Token in logs
logger.info(f"Token: {token}")
```

## Performance Optimization

### Instrument Selection

Only stream instruments you actively use:

```python
# Good: Specific instruments only
instruments = ["EUR_USD", "GBP_USD"]  # Only what you need

# Bad: Too many instruments
instruments = [f"{base}_{quote}" for base in bases for quote in quotes]
```

### Request Batching

Batch related operations when possible:

```python
import os
from fivetwenty import AsyncClient, Environment

# Setup
token = os.getenv("OANDA_TOKEN")
account_id = "101-001-0000000-001"

async def batch_pricing_example():
    async with AsyncClient(token=token, environment=Environment.PRACTICE) as client:
        # Good: Single request for multiple instruments
        prices = await client.pricing.get_pricing(
            account_id=account_id,
            instruments=["EUR_USD", "GBP_USD", "USD_JPY"]
        )

        # Less efficient: Multiple requests
        eur_usd = await client.pricing.get_pricing(account_id, ["EUR_USD"])
        gbp_usd = await client.pricing.get_pricing(account_id, ["GBP_USD"])
        usd_jpy = await client.pricing.get_pricing(account_id, ["USD_JPY"])

        return prices, eur_usd, gbp_usd, usd_jpy
```

## Common Anti-Patterns

### Avoid These Patterns

```python
import time
from fivetwenty import AsyncClient, Environment

# ❌ Creating clients in loops
async def bad_pattern_example():
    symbols = ["EUR_USD", "GBP_USD"]
    for symbol in symbols:
        async with AsyncClient(token=token, environment=Environment.PRACTICE) as client:  # Expensive!
            price = await client.pricing.get_pricing(account_id, [symbol])

# ❌ Blocking operations in async context
async def bad_async():
    time.sleep(1)  # Blocks entire event loop

# ❌ Float arithmetic for money
profit_loss = 1234.56 + 0.1  # Precision errors!

# ❌ Ignoring error details
async def bad_error_handling():
    async with AsyncClient(token=token, environment=Environment.PRACTICE) as client:
        try:
            order = await client.orders.post_market_order(
                account_id=account_id,
                instrument="EUR_USD",
                units=1000
            )
        except Exception:
            pass  # Lost important error information

# ❌ Not handling rate limits
async def bad_rate_limit_handling():
    async with AsyncClient(token=token, environment=Environment.PRACTICE) as client:
        while True:
            await client.accounts.get_account(account_id)  # Will hit rate limits
```

### Correct Alternatives

```python
import asyncio
import logging
from decimal import Decimal
from fivetwenty import AsyncClient, Environment
from fivetwenty.exceptions import VeeTwentyError, TooManyRequests

logger = logging.getLogger(__name__)

# ✅ Reuse client across operations
async def good_pattern_example():
    symbols = ["EUR_USD", "GBP_USD"]
    async with AsyncClient(token=token, environment=Environment.PRACTICE) as client:
        for symbol in symbols:
            price = await client.pricing.get_pricing(account_id, [symbol])

# ✅ Async operations in async context
async def good_async():
    await asyncio.sleep(1)  # Non-blocking

# ✅ Decimal arithmetic for money
profit_loss = Decimal("1234.56") + Decimal("0.1")

# ✅ Specific error handling
async def good_error_handling():
    async with AsyncClient(token=token, environment=Environment.PRACTICE) as client:
        try:
            order = await client.orders.post_market_order(
                account_id=account_id,
                instrument="EUR_USD",
                units=1000
            )
        except VeeTwentyError as e:
            logger.error(f"Order failed: {e.message}")

# ✅ Respect rate limits
async def good_rate_limit_handling():
    async with AsyncClient(token=token, environment=Environment.PRACTICE) as client:
        try:
            await client.accounts.get_account(account_id)
        except TooManyRequests as e:
            await asyncio.sleep(e.retry_after or 60)
```

## Testing Considerations

### Mock Testing

Use proper mocking for unit tests:

```python
from unittest.mock import AsyncMock
import pytest

# Mock response object
mock_response = AsyncMock()

# Example trading function to test
async def trading_function(client, account_id: str, instrument: str, units: int):
    return await client.orders.post_market_order(
        account_id=account_id,
        instrument=instrument,
        units=units
    )

@pytest.mark.asyncio
async def test_trading_logic():
    # Mock the client
    mock_client = AsyncMock()
    mock_client.orders.post_market_order.return_value = mock_response

    # Test your logic
    result = await trading_function(mock_client, "101-001-0000000-001", "EUR_USD", 1000)

    # Verify calls
    mock_client.orders.post_market_order.assert_called_once_with(
        account_id="101-001-0000000-001",
        instrument="EUR_USD",
        units=1000
    )
```

### Integration Testing

Test against practice environment:

```python
import os
import pytest
from fivetwenty import AsyncClient, Environment

@pytest.mark.integration
async def test_live_api():
    """Test against OANDA practice environment."""
    async with AsyncClient(
        token=os.environ["OANDA_PRACTICE_TOKEN"],
        environment=Environment.PRACTICE
    ) as client:
        # Test real API calls
        accounts = await client.accounts.get_accounts()
        assert len(accounts) > 0
```

## Summary

Key principles for FiveTwenty SDK usage:

1. **Use context managers** for automatic resource cleanup
2. **Always use Decimal** for financial calculations
3. **Handle specific exceptions** rather than generic Exception
4. **Reuse client instances** for better performance
5. **Implement proper retry logic** with exponential backoff
6. **Secure token management** - never hardcode or log tokens
7. **Test thoroughly** in practice environment before live trading

Following these patterns ensures robust, maintainable, and secure trading applications.