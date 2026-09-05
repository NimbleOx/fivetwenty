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

<!-- fragment: partial async streaming example -->
```python
import os
from fivetwenty import AsyncClient, Environment

# Step 1: Configure authentication and account parameters
token = os.getenv("OANDA_TOKEN")  # API token from environment for security
account_id = "101-001-0000000-001"  # Replace with your OANDA account ID

async def async_streaming_example():
    """Demonstrate AsyncClient native streaming for high-performance real-time data processing."""
    # Step 2: Initialize AsyncClient with context manager for proper resource management
    # AsyncClient provides zero-copy streaming directly from OANDA servers
    async with AsyncClient(token=token, environment=Environment.PRACTICE) as client:
        print(f"AsyncClient: Starting native async streaming...")
        print(f"Direct connection to OANDA servers - no buffering overhead")

        # Step 3: Use async for loop for native streaming iteration
        # This provides immediate price processing with minimal latency
        async for price in client.pricing.get_pricing_stream(
            account_id=account_id,        # Account for price stream access
            instruments=["EUR_USD"]       # Major currency pair for high liquidity
        ):
            # Step 4: Process price data immediately as it arrives
            # No queue buffering - direct processing from async iterator
            print(f"Price received: {price.instrument} at {price.time}")
            process_price(price)
            print(f"Zero-copy processing - minimal memory overhead")

        print(f"AsyncClient streaming provides optimal performance for production systems")

def process_price(price):
    """Process incoming price data with immediate execution."""
    # Step 5: Implement actual price processing logic
    # This function executes immediately when price data arrives
    if hasattr(price, 'bids') and hasattr(price, 'asks'):
        bid = price.bids[0].price if price.bids else "N/A"
        ask = price.asks[0].price if price.asks else "N/A"
        print(f"   {price.instrument}: Bid {bid} / Ask {ask}")
    print(f"   Processing latency: minimal (direct async iteration)")
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

<!-- fragment: partial sync streaming example -->
```python
import os
from fivetwenty import Client, Environment

# Step 1: Configure authentication and account parameters
token = os.getenv("OANDA_TOKEN")  # API token from environment for security
account_id = "101-001-0000000-001"  # Replace with your OANDA account ID

def sync_streaming_example():
    """Demonstrate Sync Client streaming with background thread and queue management."""
    # Step 2: Initialize Sync Client with automatic background thread management
    # Sync Client runs AsyncClient in background thread with bounded queue
    with Client(token=token, environment=Environment.PRACTICE) as client:
        print(f"Sync Client: Starting background thread for streaming...")
        print(f"Bounded queue (1000 items) prevents memory overflow")
        print(f"🧵 Background asyncio thread handles OANDA connection")

        # Step 3: Use standard for loop for synchronous iteration
        # Data flows from async thread through queue to sync iterator
        for price in client.pricing.get_pricing_stream(
            account_id=account_id,        # Account for price stream access
            instruments=["EUR_USD"]       # Major currency pair for demonstration
        ):
            # Step 4: Process price data from queue with automatic blocking
            # Queue-based approach provides natural backpressure handling
            print(f"Price dequeued: {price.instrument} at {price.time}")
            process_price(price)
            print(f"Package Queue-based processing - thread-safe data transfer")

        print(f"Sync Client ideal for notebooks and legacy code integration")

def process_price(price):
    """Process incoming price data from background thread queue."""
    # Step 5: Implement synchronous price processing logic
    # Data has been marshalled from async thread through bounded queue
    if hasattr(price, 'bids') and hasattr(price, 'asks'):
        bid = price.bids[0].price if price.bids else "N/A"
        ask = price.asks[0].price if price.asks else "N/A"
        print(f"   {price.instrument}: Bid {bid} / Ask {ask}")
    print(f"   Processing latency: +5-10ms (thread + queue overhead)")
    print(f"   Thread-safe processing with automatic synchronization")
```

Characteristics:

- Bounded queue prevents memory leaks
- Background thread handles OANDA connection
- Natural blocking behavior for sequential processing

## Performance Characteristics

### Concurrent Operations

**AsyncClient**: Truly concurrent using asyncio.gather()
<!-- fragment: partial async concurrent operations example -->
```python
import asyncio
import os
import time
from fivetwenty import AsyncClient, Environment

# Step 1: Configure authentication and account parameters
token = os.getenv("OANDA_TOKEN")  # API token from environment for security
account_id = "101-001-0000000-001"  # Replace with your OANDA account ID

async def async_concurrent_example():
    """Demonstrate AsyncClient's true concurrency with simultaneous API operations."""
    async with AsyncClient(token=token, environment=Environment.PRACTICE) as client:
        print(f"AsyncClient: Starting concurrent API operations...")

        # Step 2: Record start time for performance measurement
        start_time = time.perf_counter()

        # Step 3: Execute multiple operations simultaneously using asyncio.gather
        # All three API calls execute concurrently, not sequentially
        print(f"Launching 3 concurrent API requests...")
        account, positions, orders_response = await asyncio.gather(
            client.accounts.get_account(account_id),     # Executes concurrently
            client.positions.get_positions(account_id),  # Executes concurrently
            client.orders.get_orders(account_id),        # Executes concurrently
        )
        orders = orders_response["orders"]

        # Step 4: Calculate and display performance metrics
        end_time = time.perf_counter()
        total_time = end_time - start_time
        print(f"Concurrent execution completed in {total_time:.3f} seconds")
        print(f"Three API calls executed simultaneously")
        print(f"Performance: ~3x faster than sequential execution")
        print(f"HTTP connection pooling shared across all requests")

        # Step 5: Display retrieved data summary
        print(f"\nRetrieved Data Summary:")
        print(f"   Account: {account.id} (Balance: {account.balance})")
        print(f"   Positions: {len(positions.positions)} open positions")
        print(f"   Orders: {len(orders)} pending orders")

        return account, positions, orders
```

**Sync Client**: Sequential execution only
<!-- fragment: partial sync sequential operations example -->
```python
import os
import time
from fivetwenty import Client, Environment

# Step 1: Configure authentication and account parameters
token = os.getenv("OANDA_TOKEN")  # API token from environment for security
account_id = "101-001-0000000-001"  # Replace with your OANDA account ID

def sync_sequential_example():
    """Demonstrate Sync Client's sequential execution pattern."""
    with Client(token=token, environment=Environment.PRACTICE) as client:
        print(f"Sync Client: Starting sequential API operations...")

        # Step 2: Record start time for performance comparison
        start_time = time.perf_counter()

        # Step 3: Execute operations sequentially - each waits for previous to complete
        print(f"Step 1: Retrieving account information...")
        account = client.accounts.get_account(account_id)  # Blocks until complete
        print(f"   Account retrieved: {account.id}")

        print(f"Step 2: Retrieving positions (waits for account)...")
        positions = client.positions.get_positions(account_id)  # Blocks until complete
        print(f"   Positions retrieved: {len(positions.positions)} found")

        print(f"Step 3: Retrieving orders (waits for positions)...")
        orders_response = client.orders.get_orders(account_id)  # Blocks until complete
        orders = orders_response["orders"]
        print(f"   Orders retrieved: {len(orders)} found")

        # Step 4: Calculate and display performance metrics
        end_time = time.perf_counter()
        total_time = end_time - start_time
        print(f"\n🐌 Sequential execution completed in {total_time:.3f} seconds")
        print(f"Each API call waited for previous to complete")
        print(f"Background thread handled async operations internally")
        print(f"Simple synchronous programming model")

        # Step 5: Display execution model benefits
        print(f"\nSync Client Benefits:")
        print(f"   Familiar synchronous programming model")
        print(f"   No async/await syntax required")
        print(f"   Perfect for scripts and notebooks")
        print(f"   Automatic thread and queue management")

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
<!-- fragment: partial async error handling example -->
```python
import os
from fivetwenty import AsyncClient, Environment
from fivetwenty.exceptions import FiveTwentyError

# Step 1: Configure authentication and account parameters
token = os.getenv("OANDA_TOKEN")  # API token from environment for security
account_id = "101-001-0000000-001"  # Replace with your OANDA account ID

async def async_error_example():
    """Demonstrate AsyncClient's direct exception propagation for clean error handling."""
    async with AsyncClient(token=token, environment=Environment.PRACTICE) as client:
        print(f"AsyncClient: Attempting order with direct error handling...")
        order = None
        try:
            # Step 2: Attempt order placement with direct async execution
            # Exceptions propagate directly through the async call stack
            order = await client.orders.post_market_order(
                account_id=account_id,
                instrument="EUR_USD",
                units=1000
            )
            print(f"Order placed successfully: {order.id}")

        except FiveTwentyError as e:
            # Step 3: Handle OANDA API errors with direct exception access
            # No thread marshalling - original exception with full context
            print(f"⚠️ AsyncClient: Direct OANDA API error")
            print(f"   Error: {e}")
            print(f"   Full exception context preserved")
            print(f"   No thread boundary complications")
            print(f"   Stack trace points to actual error location")
            # Handle error appropriately (reduce position size, retry, etc.)

        except Exception as e:
            # Step 4: Handle other potential errors (network, etc.)
            print(f"AsyncClient: Network or system error")
            print(f"   Error: {e}")
            print(f"   Direct exception handling - no complexity")

        print(f"✨ AsyncClient provides clean, direct error handling")
        return order
```

### Sync Client

Exceptions are marshalled across thread boundaries:
<!-- fragment: Demo sync error handling with contextlib suppress patterns -->
```python
import os
from fivetwenty import Client, Environment
from fivetwenty.exceptions import FiveTwentyError

# Step 1: Configure authentication and account parameters
token = os.getenv("OANDA_TOKEN")  # API token from environment for security
account_id = "101-001-0000000-001"  # Replace with your OANDA account ID

def sync_error_example():
    """Demonstrate Sync Client's thread-marshalled exception handling."""
    with Client(token=token, environment=Environment.PRACTICE) as client:
        print(f"Sync Client: Attempting order with thread-marshalled errors...")
        order = None
        try:
            # Step 2: Attempt order placement through sync wrapper
            # Operation executes in background thread, exceptions marshalled back
            order = client.orders.post_market_order(
                account_id=account_id,
                instrument="EUR_USD",
                units=1000
            )
            print(f"Order placed successfully: {order.id}")

        except FiveTwentyError as e:
            # Step 3: Handle OANDA API errors marshalled from background thread
            # Same exception type, but transferred across thread boundary
            print(f"⚠️ Sync Client: OANDA API error (thread-marshalled)")
            print(f"   Error: {e}")
            print(f"   Exception marshalled from background async thread")
            print(f"   Original async exception converted for sync context")
            print(f"   Same exception handling, transparent to user")
            # Handle error appropriately (same as async version)

        except Exception as e:
            # Step 4: Handle other errors transferred from background thread
            print(f"Sync Client: Network/system error (thread-marshalled)")
            print(f"   Error: {e}")
            print(f"   🧵 Background thread handled actual async operation")
            print(f"   Exception transferred to main thread safely")

        print(f"✨ Sync Client provides familiar sync error handling")
        print(f"Complex thread marshalling handled transparently")
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

<!-- fragment: partial resource management example -->
```python
import os
from fivetwenty import AsyncClient, Client, Environment

# Step 1: Configure authentication parameters
token = os.getenv("OANDA_TOKEN")  # API token from environment for security

# Step 2: AsyncClient resource management demonstration
async def async_context_example():
    """Demonstrate AsyncClient's direct resource management."""
    print(f"AsyncClient: Entering context manager...")
    async with AsyncClient(token=token, environment=Environment.PRACTICE):
        # Step 3: AsyncClient manages resources directly
        print(f"HTTP connection pool created")
        print(f"Persistent connections established to OANDA")
        print(f"Event loop integration active")
        print(f"Memory footprint: minimal (single thread)")

        # Your trading operations would go here
        print(f"Ready for high-performance trading operations")

    # Step 4: Automatic cleanup on context exit
    print(f"AsyncClient: Context exited - resources cleaned up")
    print(f"HTTP connections closed gracefully")
    print(f"Memory released immediately")

# Step 5: Sync Client resource management demonstration
def sync_context_example():
    """Demonstrate Sync Client's background thread and queue management."""
    print(f"Sync Client: Entering context manager...")
    with Client(token=token, environment=Environment.PRACTICE):
        # Step 6: Sync Client manages complex background infrastructure
        print(f"🧵 Background asyncio thread started")
        print(f"Bounded queue (1000 items) allocated")
        print(f"AsyncClient running in background thread")
        print(f"HTTP connections managed by background thread")
        print(f"Memory footprint: higher (thread + queue overhead)")

        # Your trading operations would go here
        print(f"Ready for synchronous trading operations")

    # Step 7: Comprehensive cleanup on context exit
    print(f"Sync Client: Context exited - complex cleanup completed")
    print(f"🧵 Background thread terminated gracefully")
    print(f"Queue drained and deallocated")
    print(f"HTTP connections closed in background thread")
    print(f"Event loop in background thread stopped")
    print(f"All memory released (thread stack + queue + connections)")
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
