# Streaming Data Architecture

Understanding the architectural principles and design patterns behind FiveTwenty's streaming capabilities.

## Overview

FiveTwenty provides two primary streaming data types:

- **Price Streaming**: Real-time market data (bid/ask prices, spreads, liquidity)
- **Transaction Streaming**: Account state changes (order fills, position updates)

Both streams are built on common architectural principles for reliability, performance, and fault tolerance.

## Stream Architecture Design

### Connection Management

FiveTwenty implements a persistent HTTP/HTTPS connection model with the OANDA servers. Each stream maintains:

- **Keep-alive connections** to minimize connection overhead
- **Heartbeat mechanism** to detect connection health
- **Automatic reconnection** with exponential backoff
- **Stall detection** to identify unresponsive connections

### Data Flow Patterns

**Producer-Consumer Pattern**: Streaming connections act as data producers while your application logic acts as consumers. This separation allows for better resource management and processing flexibility.

**Event-Driven Architecture**: Both async and sync clients emit events as data arrives, enabling reactive programming patterns.

**Backpressure Handling**: The sync client uses bounded queues to prevent memory issues when processing cannot keep up with incoming data rates.

## Streaming Models

### Async Streaming

The primary async interface uses Python's async iterator protocol:

```python
async for price in client.pricing.get_pricing_stream(...):
    # Process price data
```

**Benefits**:
- Non-blocking I/O operations
- Efficient resource utilization
- Natural integration with async/await patterns
- Direct control over stream lifecycle

### Sync Streaming

The sync wrapper manages an async event loop in a background thread:

```python
for price in client.pricing.get_pricing_stream(...):
    # Process price data
```

**Benefits**:
- Familiar iterator interface
- No async/await syntax required
- Thread-safe operation
- Automatic resource cleanup

## Error Handling Architecture

### Connection Resilience

FiveTwenty implements multiple layers of error handling:

1. **Network Level**: HTTP connection errors, timeouts, DNS failures
2. **Protocol Level**: Invalid message formats, authentication failures
3. **Application Level**: Rate limiting, insufficient permissions
4. **Stream Level**: Stall detection, heartbeat timeouts

### Recovery Strategies

**Exponential Backoff**: Failed connections retry with increasing delays to prevent server overload.

**Circuit Breaker Pattern**: After consecutive failures, the stream enters a "circuit open" state to allow servers to recover.

**Graceful Degradation**: Applications can implement fallback strategies when streaming data becomes unavailable.

## Performance Characteristics

### Latency Considerations

- **Network Latency**: Typically 10-50ms depending on geographic location
- **Processing Latency**: Minimal overhead from SDK (~1-2ms)
- **Queue Latency**: Bounded queues in sync client add ~1ms per message

### Throughput Scaling

- **Price Streams**: Can handle 100+ price updates per second per instrument
- **Transaction Streams**: Lower volume, typically <10 events per second
- **Multiple Streams**: Each stream connection is independent

### Memory Management

- **Async Client**: Zero buffering, immediate processing required
- **Sync Client**: Bounded queue (default 1000 messages) prevents memory leaks
- **Heartbeat Handling**: Minimal memory footprint for connection monitoring

## Integration Patterns

### Single Stream Processing

Most applications need only one type of stream with straightforward processing.

### Multi-Stream Coordination

Advanced applications coordinate multiple streams using asyncio.gather() or similar concurrency patterns.

### Event Sourcing

Streaming data can be persisted to create event sourcing architectures for audit trails and replay capabilities.

## Security Considerations

### Authentication

Streams use the same token-based authentication as REST endpoints. Tokens are validated on connection establishment.

### Connection Security

All streaming connections use HTTPS/TLS encryption with certificate validation.

### Rate Limiting

OANDA applies rate limits to streaming connections to prevent abuse. The SDK handles rate limit responses gracefully.

## Monitoring and Observability

### Health Monitoring

Applications should monitor:
- Message receive rates
- Heartbeat intervals
- Connection uptime
- Error frequencies

### Performance Metrics

Key metrics include:
- End-to-end latency measurements
- Message processing throughput
- Memory usage patterns
- Network bandwidth utilization

For detailed implementation examples, see the [Streaming Data Tutorials](../tutorials/streaming-data/index.md).
