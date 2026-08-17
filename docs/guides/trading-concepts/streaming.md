# Streaming Data Architecture

Understanding the architectural principles and design patterns behind FiveTwenty's streaming capabilities.

## Overview

FiveTwenty provides two primary streaming data types:

- **Price Streaming**: Real-time market data (bid/ask prices, spreads, liquidity)
- **Transaction Streaming**: Account state changes (order fills, position updates)

Both streams share the same connection and recovery machinery.

## Stream Architecture Design

### Connection Management

FiveTwenty implements a persistent HTTP/HTTPS connection model with the OANDA servers. Each stream maintains:

- **Keep-alive connections** to minimize connection overhead
- **Heartbeat mechanism** to detect connection health
- **Automatic reconnection** with exponential backoff
- **Stall detection** to identify unresponsive connections

### Data Flow Patterns

**Producer-Consumer Pattern**: Streaming connections produce data; your application logic consumes it. The SDK manages the connection, and your code decides how fast to process.

**Event-Driven Architecture**: Both async and sync clients deliver data as it arrives, so you can react message by message.

**Backpressure Handling**: The sync client uses bounded queues to prevent memory issues when processing cannot keep up with incoming data rates.

## Streaming Models

### Async Streaming

The primary async interface uses Python's async iterator protocol:

<!-- fragment: Demo async streaming architecture with comprehensive flow analysis -->
```python
from fivetwenty import AsyncClient, Environment
import asyncio
from typing import AsyncIterator


async def demonstrate_async_streaming_architecture() -> None:
    """Demonstrate async streaming architecture with comprehensive flow analysis."""
    # Step 1: Initialize async client for streaming architecture
    # AsyncClient provides native async/await streaming interface
    print(f" Async Streaming Architecture Demonstration")

    async with AsyncClient(
        environment=Environment.PRACTICE  # Use practice for demonstration
    ) as client:

        # Step 2: Configure streaming parameters for architecture demo
        account_id = client.account_id
        instruments = ["EUR_USD", "GBP_USD"]  # Multiple instruments for flow analysis

        print(f"\nAnalysis Streaming Configuration:")
        print(f" Account: {account_id}")
        print(f" Instruments: {', '.join(instruments)}")
        print(f" Stream type: Price streaming (real-time market data)")
        print(f" Architecture: Async iterator pattern")

        # Step 3: Implement streaming with architectural awareness
        stream_stats = {
            "messages_received": 0,
            "heartbeats": 0,
            "price_updates": 0,
            "errors": 0
        }

        try:
            print(f"\nStarting Starting Async Streaming Loop...")

            # Step 4: Enter async iterator streaming pattern
            # This demonstrates the core async streaming architecture
            async for price_data in client.pricing.get_pricing_stream(account_id, instruments):
                stream_stats["messages_received"] += 1

                # Step 5: Process different message types in streaming architecture
                if hasattr(price_data, 'type'):
                    if price_data.type == "PRICE":
                        # Price data processing
                        stream_stats["price_updates"] += 1

                        print(f" Price Update #{stream_stats['price_updates']}:")
                        print(f"     Business Instrument: {price_data.instrument}")
                        print(f"     Balance Bid: {price_data.bids[0].price}")
                        print(f"     Analysis Ask: {price_data.asks[0].price}")
                        print(f"     Time Time: {price_data.time}")

                        # Demonstrate architectural flow control
                        await process_price_architecturally(price_data)

                    elif price_data.type == "HEARTBEAT":
                        # Heartbeat processing for connection health
                        stream_stats["heartbeats"] += 1

                        if stream_stats["heartbeats"] % 5 == 0:  # Log every 5th heartbeat
                            print(f"   Heart Heartbeat #{stream_stats['heartbeats']} - Connection healthy")

                # Step 6: Architectural flow control - limit demo duration
                if stream_stats["price_updates"] >= 10:  # Limit for demonstration
                    print(f"\nRed Demo limit reached - stopping stream")
                    break

        except Exception as e:
            stream_stats["errors"] += 1
            print(f"\nError Streaming error: {e}")
            print(f"Note Architecture handles errors gracefully with reconnection")

        # Step 7: Display architectural performance metrics
        print(f"\nAsync Streaming Architecture Results:")
        print(f"   Total messages: {stream_stats['messages_received']}")
        print(f"   Price updates: {stream_stats['price_updates']}")
        print(f"   Heartbeats: {stream_stats['heartbeats']}")
        print(f"   Errors: {stream_stats['errors']}")

        print(f"\nAsync Architecture Benefits:")
        print(f"   Non-blocking: Doesn't block other async operations")
        print(f"   Efficient: Minimal memory overhead")
        print(f"   Reactive: Immediate processing of incoming data")
        print(f"   Scalable: Can handle multiple concurrent streams")


async def process_price_architecturally(price_data) -> None:
    """Demonstrate architectural price processing patterns."""
    # Step 8: Architectural processing patterns
    # This shows how streaming data flows through application architecture

    # Simulated processing time (non-blocking)
    await asyncio.sleep(0.001)  # 1ms processing simulation

    # Architectural pattern: Event-driven processing
    # In real applications, this would trigger:
    # - Risk management checks
    # - Trading signal generation
    # - Position management updates
    # - Real-time analytics

    pass  # Placeholder for actual trading logic


# Step 9: Run async streaming architecture demonstration
print(f" Starting Async Streaming Architecture Demo")
try:
    asyncio.run(demonstrate_async_streaming_architecture())
except KeyboardInterrupt:
    print(f"\nRed Demo stopped by user")
print(f"Success Async streaming architecture demonstration complete")
```

**Benefits**:
- Non-blocking I/O operations
- Efficient resource utilization
- Natural integration with async/await patterns
- Direct control over stream lifecycle

### Sync Streaming

The sync wrapper manages an async event loop in a background thread:

<!-- fragment: Demo sync streaming architecture with thread management analysis -->
```python
from fivetwenty import Client, Environment
import time
from threading import current_thread
from typing import Iterator


def demonstrate_sync_streaming_architecture() -> None:
    """Demonstrate sync streaming architecture with thread management analysis."""
    # Step 1: Initialize sync client for streaming architecture
    # Sync Client wraps async operations in background thread
    print(f"Processing Sync Streaming Architecture Demonstration")
    print(f"   List Main thread: {current_thread().name}")

    with Client(
        environment=Environment.PRACTICE  # Use practice for demonstration
    ) as client:

        # Step 2: Configure sync streaming parameters
        account_id = client.account_id
        instruments = ["EUR_USD"]  # Single instrument for simplicity

        print(f"\nAnalysis Sync Streaming Configuration:")
        print(f" Account: {account_id}")
        print(f" Instruments: {', '.join(instruments)}")
        print(f"   Processing Architecture: Sync iterator with background async loop")
        print(f"   Data Queue: Bounded queue for thread-safe communication")

        # Step 3: Streaming statistics for architectural analysis
        stream_stats = {
            "messages_processed": 0,
            "heartbeats_received": 0,
            "price_updates": 0,
            "processing_time_total": 0.0,
            "start_time": time.time()
        }

        try:
            print(f"\nStarting Starting Sync Streaming Loop...")
            print(f"   List Processing thread: {current_thread().name}")

            # Step 4: Enter sync iterator streaming pattern
            # This demonstrates sync wrapper over async streaming
            for price_data in client.pricing.get_pricing_stream(account_id, instruments):
                process_start = time.time()
                stream_stats["messages_processed"] += 1

                # Step 5: Process different message types in sync architecture
                if hasattr(price_data, 'type'):
                    if price_data.type == "PRICE":
                        # Price data processing in sync context
                        stream_stats["price_updates"] += 1

                        print(f" Sync Price Update #{stream_stats['price_updates']}:")
                        print(f"     Business Instrument: {price_data.instrument}")
                        print(f"     Balance Bid: {price_data.bids[0].price}")
                        print(f"     Analysis Ask: {price_data.asks[0].price}")
                        print(f"     🗺️ Thread: {current_thread().name}")

                        # Demonstrate sync processing patterns
                        process_price_synchronously(price_data)

                    elif price_data.type == "HEARTBEAT":
                        # Heartbeat processing in sync context
                        stream_stats["heartbeats_received"] += 1

                        if stream_stats["heartbeats_received"] % 3 == 0:
                            print(f"   Heart Sync Heartbeat #{stream_stats['heartbeats_received']} - Thread-safe connection")

                # Step 6: Track processing performance
                process_time = time.time() - process_start
                stream_stats["processing_time_total"] += process_time

                # Step 7: Architectural flow control - limit demo duration
                if stream_stats["price_updates"] >= 8:  # Limit for demonstration
                    print(f"\nRed Sync demo limit reached - stopping stream")
                    break

        except Exception as e:
            print(f"\nError Sync streaming error: {e}")
            print(f"Note Sync architecture provides thread-safe error handling")

        # Step 8: Calculate architectural performance metrics
        total_runtime = time.time() - stream_stats["start_time"]
        avg_processing_time = (
            stream_stats["processing_time_total"] / stream_stats["messages_processed"]
            if stream_stats["messages_processed"] > 0 else 0
        )

        print(f"\nAnalysis Sync Streaming Architecture Results:")
        print(f"   Time Total runtime: {total_runtime:.2f} seconds")
        print(f"   List Messages processed: {stream_stats['messages_processed']}")
        print(f" Price updates: {stream_stats['price_updates']}")
        print(f"   Heart Heartbeats: {stream_stats['heartbeats_received']}")
        print(f" Avg processing time: {avg_processing_time*1000:.2f}ms per message")

        print(f"\nTarget Sync Architecture Benefits:")
        print(f"   📚 Familiar: Standard Python iterator interface")
        print(f"   Secure Thread-safe: Background async loop handled automatically")
        print(f"   Data Bounded: Queue prevents memory issues")
        print(f"   🆕 Simple: No async/await syntax required")

        print(f"\nConfig Sync Architecture Internals:")
        print(f"   Processing Background thread: Runs async event loop")
        print(f"   Data Bounded queue: Thread-safe message passing")
        print(f"   Secure Resource management: Automatic cleanup on context exit")
        print(f"   ⚠️ Blocking nature: Iterator blocks until next message")


def process_price_synchronously(price_data) -> None:
    """Demonstrate synchronous price processing patterns."""
    # Step 9: Sync processing patterns
    # This shows how streaming data is processed in sync context

    # Simulated processing time (blocking)
    time.sleep(0.001)  # 1ms processing simulation

    # Sync pattern: Sequential processing
    # In real applications, this would handle:
    # - Database operations
    # - File I/O
    # - Synchronous calculations
    # - Third-party API calls

    pass  # Placeholder for actual sync logic


# Step 10: Run sync streaming architecture demonstration
print(f"Processing Starting Sync Streaming Architecture Demo")
try:
    demonstrate_sync_streaming_architecture()
except KeyboardInterrupt:
    print(f"\nRed Demo stopped by user")
print(f"Success Sync streaming architecture demonstration complete")
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

For detailed implementation examples, see the [Streaming Data Tutorials](../../tutorials/streaming-data.md).
