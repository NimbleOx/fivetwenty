# FiveTwenty SDK Best Practices

Essential patterns and practices for building robust applications with the FiveTwenty SDK.

## Client Architecture Patterns

### Context Manager Usage

Always use context managers for proper resource cleanup:

```python
# AsyncClient
async with AsyncClient(token=token, environment=Environment.PRACTICE) as client:
    # Client automatically cleaned up on exit
    account = await client.accounts.get_account(account_id)

# Sync Client
with Client(token=token, environment=Environment.PRACTICE) as client:
    # Background thread and queues automatically cleaned up
    account = client.accounts.get_account(account_id)
```

### Connection Reuse

Reuse client instances across multiple operations:

```python
# Good: Reuse client for multiple operations
async with AsyncClient(...) as client:
    account = await client.accounts.get_account(account_id)
    positions = await client.positions.get_positions(account_id)
    orders = await client.orders.get_orders(account_id)

# Bad: Create new client for each operation
async def get_account():
    async with AsyncClient(...) as client:
        return await client.accounts.get_account(account_id)
```

### Concurrent Operations

Use asyncio.gather() for concurrent API calls:

```python
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
```

## Financial Precision

### Decimal Usage

Always use Decimal for financial calculations:

```python
from decimal import Decimal

# Good: Exact precision
position_size = Decimal("10000")
risk_amount = account_balance * Decimal("0.02")  # 2% risk
stop_distance = Decimal("0.0050")  # 50 pips

# Bad: Floating point errors
position_size = 10000.0
risk_amount = float(account_balance) * 0.02
stop_distance = 0.0050
```

### Price Calculation Precision

Handle OANDA's price precision requirements:

```python
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
# SDK handles conversion automatically
order = await client.orders.post_limit_order(
    account_id=account_id,
    instrument="EUR_USD",
    units=Decimal("10000"),  # Converted to string for API
    price=Decimal("1.0850")  # Converted to string for API
)

# Response fields are properly typed
filled_price = Decimal(order.order_fill_transaction.price)  # string -> Decimal
```

## Error Handling Patterns

### Exception Hierarchy

Use specific exception types for targeted handling:

```python
from fivetwenty.exceptions import (
    VeeTwentyError, BadRequest, TooManyRequests, InternalServerError
)

try:
    order = await client.orders.post_market_order(...)
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
```

### Retry Patterns

Implement exponential backoff for retryable errors:

```python
import random

async def retry_with_backoff(
    operation,
    max_retries: int = 3,
    base_delay: float = 1.0
) -> Any:
    """Retry operation with exponential backoff."""
    for attempt in range(max_retries):
        try:
            return await operation()
        except (InternalServerError, TooManyRequests) as e:
            if attempt == max_retries - 1:
                raise

            # Exponential backoff with jitter
            delay = base_delay * (2 ** attempt)
            jitter = random.uniform(0.1, 0.3) * delay
            await asyncio.sleep(delay + jitter)
```

## Streaming Best Practices

### Stream Resource Management

Properly handle streaming connections:

```python
async def robust_price_stream(client, account_id, instruments):
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
# AsyncClient: Direct processing (no buffering)
async for price in client.pricing.get_pricing_stream(...):
    # Process immediately - don't block the stream
    await process_price_async(price)

# Sync Client: Bounded queues prevent memory issues
for price in client.pricing.get_pricing_stream(...):
    # Queue automatically manages backpressure
    process_price_sync(price)
```

## Environment Management

### Environment-Specific Configuration

Use different settings for practice vs live:

```python
from fivetwenty import Environment

def create_client(is_live: bool = False):
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
# Good: Single request for multiple instruments
prices = await client.pricing.get_pricing(
    account_id=account_id,
    instruments=["EUR_USD", "GBP_USD", "USD_JPY"]
)

# Less efficient: Multiple requests
eur_usd = await client.pricing.get_pricing(account_id, ["EUR_USD"])
gbp_usd = await client.pricing.get_pricing(account_id, ["GBP_USD"])
usd_jpy = await client.pricing.get_pricing(account_id, ["USD_JPY"])
```

## Common Anti-Patterns

### Avoid These Patterns

```python
# ❌ Creating clients in loops
for symbol in symbols:
    async with AsyncClient(...) as client:  # Expensive!
        price = await client.pricing.get_pricing(...)

# ❌ Blocking operations in async context
async def bad_async():
    time.sleep(1)  # Blocks entire event loop

# ❌ Float arithmetic for money
profit_loss = 1234.56 + 0.1  # Precision errors!

# ❌ Ignoring error details
try:
    order = await client.orders.post_market_order(...)
except Exception:
    pass  # Lost important error information

# ❌ Not handling rate limits
while True:
    await client.accounts.get_account(account_id)  # Will hit rate limits
```

### Correct Alternatives

```python
# ✅ Reuse client across operations
async with AsyncClient(...) as client:
    for symbol in symbols:
        price = await client.pricing.get_pricing(...)

# ✅ Async operations in async context
async def good_async():
    await asyncio.sleep(1)  # Non-blocking

# ✅ Decimal arithmetic for money
profit_loss = Decimal("1234.56") + Decimal("0.1")

# ✅ Specific error handling
try:
    order = await client.orders.post_market_order(...)
except VeeTwentyError as e:
    logger.error(f"Order failed: {e.message}")

# ✅ Respect rate limits
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

@pytest.mark.asyncio
async def test_trading_logic():
    # Mock the client
    mock_client = AsyncMock()
    mock_client.orders.post_market_order.return_value = mock_response

    # Test your logic
    result = await trading_function(mock_client, account_id, "EUR_USD", 1000)

    # Verify calls
    mock_client.orders.post_market_order.assert_called_once_with(
        account_id=account_id,
        instrument="EUR_USD",
        units=1000
    )
```

### Integration Testing

Test against practice environment:

```python
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