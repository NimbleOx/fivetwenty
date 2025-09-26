# Async vs Sync Design

Understanding FiveTwenty's dual client architecture and choosing the right approach for your application.

## Client Architecture

FiveTwenty provides two client interfaces:

- **AsyncClient**: Primary async interface built on httpx async client
- **Client**: Sync wrapper that runs AsyncClient in a background thread

Both clients share the same API surface but differ in execution model and performance characteristics.

## Quick Comparison

| Feature | AsyncClient | Client (Sync) |
|---------|------------|---------------|
| **Performance** | High (concurrent requests) | Lower (sequential) |
| **Use Case** | Production, high-frequency | Scripts, notebooks |
| **Streaming** | Native async iteration | Thread-based iteration |
| **Resource Usage** | Lower memory/CPU overhead | Background thread overhead |
| **Error Handling** | Direct exception propagation | Exception marshalling across threads |

## AsyncClient Architecture

### Design Principles

- **Event Loop Integration**: Uses the current asyncio event loop
- **Connection Pooling**: Maintains persistent HTTP connections via httpx
- **Zero-Copy Streaming**: Direct async iteration over streaming responses
- **Context Management**: Automatic resource cleanup on exit

### When to Use AsyncClient

- Production trading systems requiring high throughput
- Applications already using asyncio/async frameworks
- Real-time streaming data processing
- Multiple concurrent API operations
- Web applications (FastAPI, aiohttp)

### Streaming Implementation

AsyncClient provides native async iteration for streaming:

```python
import os
from fivetwenty import AsyncClient, Environment

# Setup
token = os.getenv("OANDA_TOKEN")
account_id = "101-001-0000000-001"

async def async_streaming_example():
    async with AsyncClient(token=token, environment=Environment.PRACTICE) as client:
        async for price in client.pricing.get_pricing_stream(
            account_id=account_id,
            instruments=["EUR_USD"]
        ):
            # Process price immediately
            process_price(price)

def process_price(price):
    """Process incoming price data."""
    pass
```

Benefits:
- No buffering or queuing overhead
- Direct backpressure to OANDA servers
- Immediate cancellation support
- Memory-efficient for long-running streams

## Sync Client Architecture

### Design Principles

- **Thread Isolation**: Runs AsyncClient in dedicated background thread
- **Queue-Based Communication**: Uses bounded queues for data transfer
- **Iterator Interface**: Provides familiar for-loop syntax
- **Thread Safety**: All operations are thread-safe

### Implementation Details

The sync client manages:
- Background asyncio event loop in separate thread
- Bounded queue (default 1000 items) for streaming data
- Exception marshalling between async and sync contexts
- Automatic cleanup when iterator exits

### When to Use Sync Client

- Jupyter notebooks and interactive development
- Legacy codebases without async support
- Simple scripts and prototypes
- Learning and experimentation

### Streaming Implementation

Sync client provides iterator-based streaming:

```python
import os
from fivetwenty import Client, Environment

# Setup
token = os.getenv("OANDA_TOKEN")
account_id = "101-001-0000000-001"

def sync_streaming_example():
    with Client(token=token, environment=Environment.PRACTICE) as client:
        for price in client.pricing.get_pricing_stream(
            account_id=account_id,
            instruments=["EUR_USD"]
        ):
            # Process price from queue
            process_price(price)

def process_price(price):
    """Process incoming price data."""
    pass
```

Characteristics:
- Bounded queue prevents memory leaks
- Background thread handles OANDA connection
- Natural blocking behavior for sequential processing

## Performance Characteristics

### Concurrent Operations

**AsyncClient**: Truly concurrent using asyncio.gather()
```python
import asyncio
import os
from fivetwenty import AsyncClient, Environment

# Setup
token = os.getenv("OANDA_TOKEN")
account_id = "101-001-0000000-001"

async def async_concurrent_example():
    async with AsyncClient(token=token, environment=Environment.PRACTICE) as client:
        # Multiple operations execute simultaneously
        account, positions, orders = await asyncio.gather(
            client.accounts.get_account(account_id),
            client.positions.get_positions(account_id),
            client.orders.get_orders(account_id),
        )
        return account, positions, orders
```

**Sync Client**: Sequential execution only
```python
import os
from fivetwenty import Client, Environment

# Setup
token = os.getenv("OANDA_TOKEN")
account_id = "101-001-0000000-001"

def sync_sequential_example():
    with Client(token=token, environment=Environment.PRACTICE) as client:
        # Operations execute one after another
        account = client.accounts.get_account(account_id)
        positions = client.positions.get_positions(account_id)
        orders = client.orders.get_orders(account_id)
        return account, positions, orders
```

### Resource Utilization

**AsyncClient**:
- Single thread execution
- Event loop overhead (~1-2MB memory)
- Direct HTTP connection management

**Sync Client**:
- Additional background thread
- Queue memory overhead (bounded)
- Thread synchronization costs

### Latency Impact

**AsyncClient**: ~10-20ms per operation
**Sync Client**: ~15-30ms per operation (thread marshalling overhead)

## Error Handling Differences

### AsyncClient

Exceptions propagate directly through the call stack:
```python
import os
from fivetwenty import AsyncClient, Environment
from fivetwenty.exceptions import VeeTwentyError

# Setup
token = os.getenv("OANDA_TOKEN")
account_id = "101-001-0000000-001"

async def async_error_example():
    async with AsyncClient(token=token, environment=Environment.PRACTICE) as client:
        try:
            order = await client.orders.post_market_order(
                account_id=account_id,
                instrument="EUR_USD",
                units=1000
            )
        except VeeTwentyError as e:
            # Handle OANDA API error
            pass
        return order
```

### Sync Client

Exceptions are marshalled across thread boundaries:
```python
import os
from fivetwenty import Client, Environment
from fivetwenty.exceptions import VeeTwentyError

# Setup
token = os.getenv("OANDA_TOKEN")
account_id = "101-001-0000000-001"

def sync_error_example():
    with Client(token=token, environment=Environment.PRACTICE) as client:
        try:
            order = client.orders.post_market_order(
                account_id=account_id,
                instrument="EUR_USD",
                units=1000
            )
        except VeeTwentyError as e:
            # Same exception, but marshalled from background thread
            pass
        return order
```

## Integration Patterns

### AsyncClient Integration

Best suited for async frameworks:
- FastAPI endpoints
- aiohttp applications
- asyncio-based trading systems
- Real-time data processing pipelines

### Sync Client Integration

Best suited for traditional applications:
- Flask web applications
- Jupyter notebooks
- Data analysis scripts
- Legacy system integration

## Resource Management

Both clients require proper cleanup:

```python
import os
from fivetwenty import AsyncClient, Client, Environment

# Setup
token = os.getenv("OANDA_TOKEN")

# AsyncClient
async def async_context_example():
    async with AsyncClient(token=token, environment=Environment.PRACTICE) as client:
        # Automatic cleanup of connections
        pass

# Sync Client
def sync_context_example():
    with Client(token=token, environment=Environment.PRACTICE) as client:
        # Automatic cleanup of background thread and queue
        pass
```

The context managers ensure:
- HTTP connections are properly closed
- Background threads are terminated
- Event loops are cleaned up
- Memory is released

## Choosing the Right Client

**Use AsyncClient when**:
- Building production trading systems
- Need maximum performance/throughput
- Already using async/await in your application
- Processing real-time streaming data at scale

**Use Sync Client when**:
- Prototyping or learning
- Working in Jupyter notebooks
- Integrating with legacy synchronous code
- Building simple scripts or analysis tools

Both clients provide identical functionality - the choice depends on your application's concurrency model and performance requirements.

For detailed implementation examples, see the [tutorials](../../tutorials/index.md) and [practical guides](../index.md).
