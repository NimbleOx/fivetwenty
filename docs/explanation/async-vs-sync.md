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
async for price in client.pricing.get_pricing_stream(...):
    # Process price immediately
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
for price in client.pricing.get_pricing_stream(...):
    # Process price from queue
```

Characteristics:
- Bounded queue prevents memory leaks
- Background thread handles OANDA connection
- Natural blocking behavior for sequential processing

## Performance Characteristics

### Concurrent Operations

**AsyncClient**: Truly concurrent using asyncio.gather()
```python
# Multiple operations execute simultaneously
account, positions, orders = await asyncio.gather(
    client.accounts.get_account(account_id),
    client.positions.get_positions(account_id),
    client.orders.get_orders(account_id),
)
```

**Sync Client**: Sequential execution only
```python
# Operations execute one after another
account = client.accounts.get_account(account_id)
positions = client.positions.get_positions(account_id)
orders = client.orders.get_orders(account_id)
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
try:
    order = await client.orders.post_market_order(...)
except VeeTwentyError as e:
    # Handle OANDA API error
```

### Sync Client

Exceptions are marshalled across thread boundaries:
```python
try:
    order = client.orders.post_market_order(...)
except VeeTwentyError as e:
    # Same exception, but marshalled from background thread
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
# AsyncClient
async with AsyncClient(...) as client:
    # Automatic cleanup of connections

# Sync Client
with Client(...) as client:
    # Automatic cleanup of background thread and queue
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

For detailed implementation examples, see the [tutorials](../tutorials/index.md) and [how-to guides](../how-to-guides/index.md).
