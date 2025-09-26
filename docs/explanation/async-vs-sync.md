# Async vs Sync

The FiveTwenty provides both asynchronous and synchronous clients. This guide helps you choose the right approach for your application.

## Quick Comparison

| Feature | AsyncClient | Client (Sync) |
|---------|------------|---------------|
| **Performance** | High (concurrent requests) | Lower (sequential) |
| **Complexity** | Moderate | Straightforward |
| **Use Case** | Production, high-frequency | Scripts, notebooks |
| **Streaming** | Native support | Thread-based |
| **Python Version** | 3.9+ with asyncio | 3.9+ |

## AsyncClient (Recommended)

The `AsyncClient` is the primary interface, offering superior performance and scalability.

### When to Use Async

Use `AsyncClient` when you need:

- ✅ Concurrent API requests
- ✅ Real-time streaming data
- ✅ High-frequency trading
- ✅ Production trading systems
- ✅ Web applications (FastAPI, aiohttp)
- ✅ Multiple account management

### Basic Async Usage

```python
import asyncio

from fivetwenty import AsyncClient, Environment



async def async_example():
    """Async client example."""
    async with AsyncClient(
        token="your-token",
        environment=Environment.PRACTICE,
    ) as client:
        # Concurrent requests (fast!)
        accounts, instruments = await asyncio.gather(
            client.accounts.get_accounts(),
            client.instruments.get_instrument_candles("101-001-1234567-001"),
        )

        print(f"Found {len(accounts)} accounts")
        print(f"Available instruments: {len(instruments)}")

# Run async function
asyncio.run(async_example())
```

### Concurrent Operations

Async shines with multiple concurrent operations:

```python
import asyncio
from typing import Any


async def concurrent_operations(client: Any, account_id: str) -> Any:
    """Execute multiple operations simultaneously."""

    # All requests happen in parallel - much faster!
    results = await asyncio.gather(
        client.accounts.get_account(account_id),
        client.positions.get_open_positions(account_id),
        client.orders.get_pending_orders(account_id),
        client.trades.get_open_trades(account_id),
        client.pricing.get_pricing(account_id, ["EUR_USD", "GBP_USD", "USD_JPY"]),
    )

    account, positions, orders, trades, prices = results

    return {
        "account": account,
        "positions": positions,
        "orders": orders,
        "trades": trades,
        "prices": prices,
    }

# This takes ~200ms instead of ~1000ms sequential
```

### Streaming with Async

Async streaming is natural and efficient:

```python
import asyncio
from typing import Any


async def stream_prices(client: Any, account_id: str) -> Any:
    """Stream real-time prices."""
    async for price in client.pricing.get_pricing_stream(account_id, ["EUR_USD"]):
        if price.type == "PRICE":
            print(f"EUR/USD: Bid={price.bids[0].price}, Ask={price.asks[0].price}")
        elif price.type == "HEARTBEAT":
            print("♥ Heartbeat")

        # Process prices asynchronously
        await process_price(price)

async def process_price(price: Any) -> Any:
    """Process price updates asynchronously."""
    # Can do other async operations while streaming continues
    await asyncio.sleep(0.01)  # Simulate processing
```

## Client (Sync)

The synchronous `Client` wraps `AsyncClient` for simpler usage.

### When to Use Sync

Use `Client` when you have:

- ✅ Straightforward scripts
- ✅ Jupyter notebooks
- ✅ Quick analysis tasks
- ✅ Legacy synchronous code
- ✅ Learning/prototyping

### Basic Sync Usage

```python
from fivetwenty import Client, Environment

# Sync client - simpler but slower

with Client(
    token="your-token",
    environment=Environment.PRACTICE,
) as client:
    # Sequential requests
    accounts = client.accounts.get_accounts()
    account = client.accounts.get_account(accounts[0].id)

    print(f"Account balance: {account.balance}")
```

### Sync Streaming

Sync client provides streaming via iterator:

```python
from typing import Any


def stream_prices_sync(client: Any, account_id: str) -> Any:
    """Stream prices synchronously."""
    for price in client.pricing.get_pricing_stream(account_id, ["EUR_USD"]):
        if price.type == "PRICE":
            print(f"Price: {price.asks[0].price}")

        # Blocking - can't do other operations
        process_price_sync(price)
```

## Detailed Comparison

### Performance Comparison

```python
import time
import asyncio
from typing import Any
from fivetwenty import AsyncClient, Client, Environment

# ASYNC: Fast concurrent requests

async def async_performance_test() -> Any:
    async with AsyncClient(token=token, account_id="your-account-id", environment=Environment.PRACTICE) as client:
        start = time.time()

        # 10 concurrent requests
        results = await asyncio.gather(*[
            client.accounts.get_accounts() for _ in range(10)
        ])

        print(f"Async time: {time.time() - start:.2f}s")  # ~0.5s

# SYNC: Slow sequential requests
def sync_performance_test() -> Any:
    with Client(token=token, environment=Environment.PRACTICE) as client:
        start = time.time()

        # 10 sequential requests
        results = [client.accounts.get_accounts() for _ in range(10)]

        print(f"Sync time: {time.time() - start:.2f}s")  # ~5.0s
```

### Error Handling

#### Async Error Handling

```python
import asyncio
from typing import Any
from fivetwenty import AsyncClient, Environment


async def async_error_handling() -> Any:
    async with AsyncClient(token=token, account_id="your-account-id", environment=Environment.PRACTICE) as client:
        try:
            # Multiple operations with individual error handling
            results = await asyncio.gather(
                client.orders.post_market_order(account_id, "EUR_USD", 1000),
                client.orders.post_market_order(account_id, "INVALID", 1000),
                return_exceptions=True  # Don't fail everything
            )

            for result in results:
                if isinstance(result, Exception):
                    print(f"Error: {result}")
                else:
                    print(f"Success: {result.order_fill_transaction.id}")

        except Exception as e:
            print(f"Unexpected error: {e}")
```

#### Sync Error Handling

```python
from typing import Any
from fivetwenty.exceptions import FiveTwentyError
from fivetwenty import Environment, Client


def sync_error_handling() -> Any:
    with Client(token=token, environment=Environment.PRACTICE) as client:
        try:
            order = client.orders.post_market_order(account_id, "EUR_USD", 1000)
            print(f"Success: {order.order_fill_transaction.id}")
        except FiveTwentyError as e:
            print(f"OANDA error: {e}")
        except Exception as e:
            print(f"Unexpected error: {e}")
```

## Conversion Patterns

### Converting Sync to Async

If you have sync code and want to upgrade:

```python
import asyncio
from typing import Any

# OLD: Synchronous code

def get_account_sync(client: Any, account_id: str) -> Any:
    account = client.accounts.get_account(account_id)
    positions = client.positions.get_open_positions(account_id)
    return account, positions

# NEW: Asynchronous code
async def get_account_async(client: Any, account_id: str) -> Any:
    account, positions = await asyncio.gather(
        client.accounts.get_account(account_id),
        client.positions.get_open_positions(account_id),
    )
    return account, positions
```

### Using Async in Sync Context

If you need to call async from sync code:

```python
import asyncio



def sync_wrapper() -> Any:
    """Call async code from sync context."""
    # Create new event loop
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    try:
        # Run async function
        result = loop.run_until_complete(async_function())
        return result
    finally:
        loop.close()

# Or simpler in Python 3.7+
def sync_wrapper_simple() -> Any:
    return asyncio.run(async_function())
```

## Integration Examples

### FastAPI (Async)

```python
from fastapi import FastAPI
from fivetwenty import AsyncClient, Environment


app = FastAPI()
client = AsyncClient(token="your-token", account_id="your-account-id", environment=Environment.PRACTICE)

@app.on_event("startup")
async def startup() -> Any:
    """Initialize client on startup."""
    await client.__aenter__()

@app.on_event("shutdown")
async def shutdown() -> Any:
    """Clean up on shutdown."""
    await client.__aexit__(None, None, None)

@app.get("/account/{account_id}")
async def get_account(account_id: str) -> Any:
    """Async endpoint."""
    account = await client.accounts.get_account(account_id)
    return {"balance": account.balance, "currency": account.currency}
```

### Flask (Sync)

```python
from flask import Flask, jsonify
from fivetwenty import Client, Environment


app = Flask(__name__)

def get_client() -> Any:
    """Create client per request."""
    return Client(token="your-token", environment=Environment.PRACTICE)

@app.route("/account/<account_id>")
def get_account(account_id: str) -> Any:
    """Sync endpoint."""
    with get_client() as client:
        account = client.accounts.get_account(account_id)
        return jsonify({
            "balance": account.balance,
            "currency": account.currency
        })
```

### Jupyter Notebooks

Both work in Jupyter, but sync is simpler:

```python
from fivetwenty import AsyncClient, Environment

# Sync - Straightforward for notebooks
from fivetwenty import Client, Environment


client = Client(token=token, environment=Environment.PRACTICE)
accounts = client.accounts.get_accounts()
print(accounts)

# Async - Requires nest_asyncio
import nest_asyncio
nest_asyncio.apply()

async def notebook_async() -> Any:
    async with AsyncClient(token=token, account_id="your-account-id", environment=Environment.PRACTICE) as client:
        accounts = await client.accounts.get_accounts()
        return accounts

await notebook_async()  # Jupyter supports top-level await
```

## Best Practices

### 1. Choose Consistency

Stick to one pattern throughout your application:

```python

from typing import Any
from fivetwenty import AsyncClient, Environment

# Good: Consistent async throughout



class TradingSystem:
    """Class docstring."""
    def __init__(self) -> None:
        self.client = AsyncClient(...)

    async def analyze(self) -> Any:
        # All methods async
        pass

    async def trade(self) -> Any:
        # All methods async
        pass

# Bad: Mixed patterns
class MixedSystem:
    """Class docstring."""
    def __init__(self) -> None:
        self.async_client = AsyncClient(...)
        self.sync_client = Client(...)

    def analyze(self):  # Sync
        pass

    async def trade(self):  # Async
        pass
```

### 2. Resource Management

Always use context managers:

```python
from fivetwenty import AsyncClient, Environment

# Good: Proper cleanup
async with AsyncClient(...) as client:
    # Client automatically cleaned up
    pass

# Bad: Manual management
client = AsyncClient(...)
# ... code ...
# Forgot to close!
```

### 3. Timeout Configuration

Configure appropriate timeouts:

```python
from fivetwenty import AsyncClient, Environment

# Async with custom timeout

async_client = AsyncClient(
    token=token,
    environment=Environment.PRACTICE,
    timeout=60.0,  # Longer timeout for slow operations
)

# Sync with custom timeout
sync_client = Client(
    token=token,
    environment=Environment.PRACTICE,
    timeout=60.0,
)
```

## Performance Tips

### Async Performance

1. **Batch Operations**: Group related requests
2. **Connection Pooling**: Reuse client instances
3. **Avoid Blocking**: Never use blocking I/O in async
4. **Task Management**: Use `asyncio.TaskGroup` (Python 3.11+)

```python
# Efficient async pattern

from typing import Any

async def efficient_async(client, account_ids) -> Any:
    """Process multiple accounts efficiently."""
    async with asyncio.TaskGroup() as tg:
        tasks = [tg.create_task(process_account(client, aid))
                 for aid in account_ids]

    # All tasks complete here
    results = [task.result() for task in tasks]
    return results
```

### Sync Performance

1. **Connection Reuse**: Keep client alive for multiple requests
2. **Batch Processing**: Process in chunks
3. **Caching**: Cache frequently accessed data

```python
from typing import Any

# Efficient sync pattern
def efficient_sync(client: Any, instruments: Any) -> Any:
    """Cache frequently accessed data."""
    cache = {}

    for instrument in instruments:
        if instrument not in cache:
            cache[instrument] = client.pricing.get_pricing(account_id, [instrument])

        process_price(cache[instrument])
```

## Troubleshooting

### Common Async Issues

1. **"RuntimeError: This event loop is already running"**
   - Use `nest_asyncio` in Jupyter
   - Don't call `asyncio.run()` inside async function

2. **"coroutine was never awaited"**
   - Always use `await` with async functions
   - Check for missing `await` keywords

### Common Sync Issues

1. **Performance problems**
   - Consider switching to async
   - Reuse client connections
   - Implement caching

2. **Threading issues**
   - Sync client is not thread-safe
   - Use one client per thread

## Summary

- **Use async client** for production systems and when performance matters
- **Use Client** for straightforward scripts and learning
- **Don't mix** async and sync patterns unnecessarily
- **Always use** context managers for proper cleanup
- **Consider your use case** when choosing between async and sync

## Next Steps

After choosing your async/sync approach:

- **Understand the architecture**: Read [SDK Architecture](sdk-architecture.md) for comprehensive design overview
- **Handle errors robustly**: Study [Error Handling](error-handling.md) for production-ready error management
- **Implement streaming**: Explore [Streaming Data](streaming.md) for real-time market data
- **Follow best practices**: Review [Best Practices](best-practices.md) for production deployment patterns
- **Learn forex concepts**: Check [Forex Trading Concepts](forex-trading-concepts.md) for domain knowledge

## Related Resources

- **[How-to Guides](../how-to-guides/index.md)**: Step-by-step implementation guides
- **[API Reference](../api-reference/index.md)**: Detailed method documentation
- **[Tutorials](../tutorials/index.md)**: Learn by building complete examples
