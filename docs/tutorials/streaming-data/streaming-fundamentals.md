# Streaming Fundamentals

Understand the basics of real-time market data streaming and the foundational concepts for building robust streaming systems.

---

## Prerequisites

- Basic understanding of async programming
- FiveTwenty SDK setup
- Knowledge of market data concepts

---

## Learning Objectives

- ✅ Understand types of streaming data
- ✅ Learn key streaming concepts and patterns
- ✅ Master connection management principles
- ✅ Identify streaming system requirements

---

## Understanding Market Data Streams

**Types of Streaming Data:**

- **Price Streams**: Real-time bid/ask prices
- **Account Streams**: Account changes and trade updates
- **Transaction Streams**: Order fills and position changes

**Key Concepts:**

- **Heartbeats**: Keep-alive messages from server
- **Reconnection**: Automatic recovery from disconnections
- **Backpressure**: Handling fast-moving data
- **Stall Detection**: Identifying connection issues

## Streaming Architecture Patterns

### Producer-Consumer Pattern

This pattern separates data generation from data processing. The producer handles the streaming connection while consumers process the data without blocking the stream. This architecture provides better performance and reliability.

```python
import asyncio
from typing import Any, Callable
from collections.abc import AsyncIterator



class StreamProducer:
    """Base producer for streaming data."""

    def __init__(self, stream_config: dict) -> None:
        self.config = stream_config
        self.is_streaming = False
        self.consumers = []

    async def start_stream(self) -> AsyncIterator[Any]:
        """Start the data stream."""
        self.is_streaming = True

        while self.is_streaming:
            try:
                # Fetch data from source
                data = await self._fetch_data()

                # Yield to consumers
                yield data

                # Control flow rate
                await asyncio.sleep(self.config.get("poll_interval", 0.1))

            except Exception as e:
                await self._handle_error(e)

    async def _fetch_data(self) -> Any:
        """Fetch data from streaming source."""
        # Implementation specific to data source
        pass

    async def _handle_error(self, error: Exception) -> None:
        """Handle streaming errors."""
        print(f"Stream error: {error}")
        await asyncio.sleep(1)  # Backoff before retry

class StreamConsumer:
    """Base consumer for processing streaming data."""

    def __init__(self, processor: Callable) -> None:
        self.processor = processor
        self.buffer = asyncio.Queue()

    async def consume_stream(self, stream: AsyncIterator[Any]) -> None:
        """Consume data from stream."""
        async for data in stream:
            await self.buffer.put(data)
            await self._process_data()

    async def _process_data(self) -> None:
        """Process buffered data."""
        while not self.buffer.empty():
            data = await self.buffer.get()
            await self.processor(data)
```

### Event-Driven Architecture

Event-driven systems respond to data as it arrives rather than polling for updates. This approach provides lower latency and better resource utilization for real-time trading systems.

```python
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any
from collections.abc import Callable



class StreamEventType(Enum):
    PRICE_UPDATE = "price_update"
    HEARTBEAT = "heartbeat"
    CONNECTION_LOST = "connection_lost"
    CONNECTION_RESTORED = "connection_restored"
    ERROR = "error"

@dataclass
class StreamEvent:
    event_type: StreamEventType
    timestamp: datetime
    data: Any
    source: str

class EventHandler:
    """Handle specific types of streaming events."""

    def __init__(self) -> None:
        self.handlers = {}

    def register_handler(self, event_type: StreamEventType, handler: Callable) -> Any:
        """Register handler for specific event type."""
        if event_type not in self.handlers:
            self.handlers[event_type] = []
        self.handlers[event_type].append(handler)

    async def handle_event(self, event: StreamEvent) -> Any:
        """Process incoming event."""
        handlers = self.handlers.get(event.event_type, [])

        for handler in handlers:
            try:
                await handler(event)
            except Exception as e:
                print(f"Handler error: {e}")

# Example event handlers
async def price_update_handler(event: StreamEvent) -> Any:
    """Handle price update events."""
    print(f"Price update: {event.data}")

async def connection_lost_handler(event: StreamEvent) -> Any:
    """Handle connection loss events."""
    print(f"Connection lost: {event.source}")
    # Implement reconnection logic

async def heartbeat_handler(event: StreamEvent) -> Any:
    """Handle heartbeat events."""
    # Update last heartbeat timestamp
    # Check for stall conditions
    pass
```

## Connection Management

### Reconnection Strategies

Network connections can fail unexpectedly in trading systems. This class implements exponential backoff reconnection with configurable retry limits to maintain stable streaming connections.

```python
import random
from typing import Optional


class ReconnectionPolicy:
    """Manages reconnection attempts with exponential backoff."""

    def __init__(self, max_attempts: int = 10, base_delay: float = 1.0, max_delay: float = 60.0, jitter: bool = True) -> None:
        self.max_attempts = max_attempts
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.jitter = jitter
        self.attempt_count = 0

    def should_reconnect(self) -> bool:
        """Determine if should attempt reconnection."""
        return self.attempt_count < self.max_attempts

    def get_delay(self) -> float:
        """Calculate delay before next reconnection attempt."""
        if not self.should_reconnect():
            return 0

        # Exponential backoff
        delay = min(self.base_delay * (2 ** self.attempt_count), self.max_delay)

        # Add jitter to prevent thundering herd
        if self.jitter:
            delay *= (0.5 + random.random() * 0.5)

        self.attempt_count += 1
        return delay

    def reset(self) -> Any:
        """Reset reconnection state after successful connection."""
        self.attempt_count = 0

class ConnectionManager:
    """Manage streaming connections with automatic reconnection."""

    def __init__(self, reconnection_policy: ReconnectionPolicy) -> None:
        self.policy = reconnection_policy
        self.is_connected = False
        self.connection = None

    async def connect(self) -> bool:
        """Establish connection to streaming service."""
        try:
            # Attempt connection
            self.connection = await self._establish_connection()
            self.is_connected = True
            self.policy.reset()
            return True

        except Exception as e:
            print(f"Connection failed: {e}")
            return False

    async def reconnect(self) -> bool:
        """Attempt reconnection with backoff."""
        while self.policy.should_reconnect():
            delay = self.policy.get_delay()
            print(f"Reconnecting in {delay:.1f} seconds...")
            await asyncio.sleep(delay)

            if await self.connect():
                return True

        print("Max reconnection attempts reached")
        return False

    async def _establish_connection(self) -> Any:
        """Establish the actual connection."""
        # Implementation specific to streaming service
        pass
```

## Stall Detection

### Heartbeat Monitoring

Heartbeats are periodic messages that indicate the connection is alive. This monitor tracks heartbeat timing and can detect when a connection has stalled, triggering reconnection if needed.

```python
import asyncio
from datetime import datetime
from typing import Any



class StallDetector:
    """Detect streaming connection stalls."""

    def __init__(self, stall_timeout: float = 30.0, heartbeat_interval: float = 5.0) -> None:
        self.stall_timeout = stall_timeout
        self.heartbeat_interval = heartbeat_interval
        self.last_heartbeat = None
        self.is_monitoring = False

    async def start_monitoring(self) -> Any:
        """Start stall detection monitoring."""
        self.is_monitoring = True
        self.last_heartbeat = datetime.now()

        while self.is_monitoring:
            await asyncio.sleep(self.heartbeat_interval)

            if self._is_stalled():
                await self._handle_stall()

    def update_heartbeat(self) -> Any:
        """Update heartbeat timestamp."""
        self.last_heartbeat = datetime.now()

    def _is_stalled(self) -> bool:
        """Check if connection is stalled."""
        if not self.last_heartbeat:
            return True

        time_since_heartbeat = datetime.now() - self.last_heartbeat
        return time_since_heartbeat.total_seconds() > self.stall_timeout

    async def _handle_stall(self) -> Any:
        """Handle detected stall condition."""
        print("Stream stall detected - triggering reconnection")
        self.is_monitoring = False
        # Trigger reconnection logic
```

## Data Flow Patterns

### Stream Multiplexing

When you need to handle multiple data streams simultaneously, multiplexing allows you to process different types of data (prices, account updates, etc.) in a coordinated way without blocking any single stream.

```python
import asyncio
from collections.abc import AsyncIterator
from datetime import datetime
from typing import Any





class StreamMultiplexer:
    """Class docstring."""
    """Multiplex multiple streams into single output."""

    def __init__(self) -> None:
        self.streams = {}
        self.output_queue = asyncio.Queue()

    async def add_stream(self, name: str, stream: AsyncIterator) -> Any:
        """Add stream to multiplexer."""
        self.streams[name] = stream
        asyncio.create_task(self._consume_stream(name, stream))

    async def _consume_stream(self, name: str, stream: AsyncIterator) -> Any:
        """Consume individual stream."""
        async for data in stream:
            enriched_data = {
                "stream_name": name,
                "timestamp": datetime.now(),
                "data": data,
            }
            await self.output_queue.put(enriched_data)

    async def get_multiplexed_stream(self) -> AsyncIterator:
        """Get multiplexed output stream."""
        while True:
            data = await self.output_queue.get()
            yield data
```

## Performance Considerations

### Latency Optimization
- **Minimize processing overhead**: Efficient data structures
- **Reduce network latency**: Optimize connection settings
- **Async processing**: Non-blocking operations
- **Buffer management**: Appropriate buffer sizes

### Memory Management
- **Bounded queues**: Prevent memory leaks
- **Data cleanup**: Remove old data regularly
- **Efficient serialization**: Minimize memory copies
- **GC optimization**: Reduce garbage collection pressure

---

## Next Steps

Now that you understand the fundamentals, proceed to [Basic Streaming Implementation](basic-streaming.md) to build your first streaming application.

---

## Related Tutorials

- [Basic Streaming Implementation](basic-streaming.md) - Build first streams
- [Automated Trading](automated-trading.md) - Complete trading systems
- [Best Practices](../../explanation/best-practices.md) - Production considerations