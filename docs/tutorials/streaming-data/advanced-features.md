# Advanced Streaming Features

Implement sophisticated streaming capabilities including connection management, error recovery, and high-availability systems.

---

## Connection Management and Error Recovery

```python
import asyncio
from datetime import datetime, timedelta
from typing import Optional, Callable, Dict, Any
from fivetwenty import AsyncClient
from fivetwenty.models import StreamingConfiguration, ReconnectionPolicy


class AdvancedStreamManager:
    """Advanced streaming with robust connection management."""

    def __init__(self, client: AsyncClient, account_id: str) -> None:
        self.client = client
        self.account_id = account_id
        self.is_streaming = False
        self.reconnection_policy = ReconnectionPolicy(
            max_attempts=10,
            base_delay=1.0,
            max_delay=60.0
        )
        self.stream_callbacks = {}
        self.connection_state = "disconnected"

    async def start_resilient_streaming(self, instruments: list, stream_type: str = "pricing") -> Any:
        """Start streaming with automatic reconnection."""

        self.is_streaming = True

        while self.is_streaming:
            try:
                await self._establish_stream(instruments, stream_type)
            except Exception as e:
                print(f"Stream error: {e}")
                if await self._should_reconnect():
                    delay = self.reconnection_policy.get_delay()
                    await asyncio.sleep(delay)
                else:
                    break

    async def _establish_stream(self, instruments: list, stream_type: str) -> Any:
        """Establish streaming connection."""

        self.connection_state = "connecting"

        if stream_type == "pricing":
            async for data in self.client.pricing.get_pricing_stream(
                account_id=self.account_id,
                instruments=instruments
            ):
                if not self.is_streaming:
                    break

                self.connection_state = "connected"
                self.reconnection_policy.reset()

                await self._process_stream_data("pricing", data)

        elif stream_type == "transactions":
            async for data in self.client.transactions.get_transactions_stream(
                account_id=self.account_id
            ):
                if not self.is_streaming:
                    break

                self.connection_state = "connected"
                await self._process_stream_data("transactions", data)

    async def _process_stream_data(self, stream_type: str, data: Any) -> Any:
        """Process incoming stream data."""

        # Call registered callbacks
        if stream_type in self.stream_callbacks:
            for callback in self.stream_callbacks[stream_type]:
                try:
                    await callback(data)
                except Exception as e:
                    print(f"Callback error: {e}")

    def register_callback(self, stream_type: str, callback: Callable) -> Any:
        """Register callback for stream data."""

        if stream_type not in self.stream_callbacks:
            self.stream_callbacks[stream_type] = []

        self.stream_callbacks[stream_type].append(callback)

    async def _should_reconnect(self) -> bool:
        """Determine if should attempt reconnection."""

        return (self.is_streaming and
                self.reconnection_policy.should_reconnect())

# High-availability streaming with failover
class HAStreamingCluster:
    """High-availability streaming with multiple connections."""

    def __init__(self, clients: list, account_id: str) -> None:
        self.clients = clients
        self.account_id = account_id
        self.active_streams = {}
        self.backup_streams = {}
        self.is_running = False

    async def start_ha_streaming(self, instruments: list) -> Any:
        """Start high-availability streaming."""

        self.is_running = True

        # Start primary and backup streams
        tasks = []

        for i, client in enumerate(self.clients):
            if i == 0:
                # Primary stream
                task = asyncio.create_task(
                    self._run_primary_stream(client, instruments)
                )
            else:
                # Backup streams
                task = asyncio.create_task(
                    self._run_backup_stream(client, instruments, i)
                )

            tasks.append(task)

        await asyncio.gather(*tasks, return_exceptions=True)

    async def _run_primary_stream(self, client: AsyncClient, instruments: list) -> Any:
        """Run primary streaming connection."""

        try:
            async for price in client.pricing.get_pricing_stream(
                account_id=self.account_id,
                instruments=instruments
            ):
                if not self.is_running:
                    break

                # Process primary data
                await self._process_primary_data(price)

        except Exception as e:
            print(f"Primary stream failed: {e}")
            await self._failover_to_backup()

    async def _run_backup_stream(self, client: AsyncClient, instruments: list, backup_id: int) -> Any:
        """Run backup streaming connection."""

        # Keep backup connection warm but don't process data unless needed
        # Implementation details for backup stream management

        pass

    async def _failover_to_backup(self) -> Any:
        """Failover to backup stream."""

        print("Failing over to backup stream...")
        # Implementation for seamless failover

# Stream multiplexing for multiple data sources
class StreamMultiplexer:
    """Multiplex multiple streams with synchronization."""

    def __init__(self) -> None:
        self.streams = {}
        self.output_queue = asyncio.Queue()
        self.sync_window = 1.0  # 1 second sync window

    async def add_stream_source(self, name: str, stream_generator: Callable) -> Any:
        """Add stream source to multiplexer."""

        self.streams[name] = {
            'generator': stream_generator,
            'buffer': [],
            'last_timestamp': None
        }

        # Start consuming stream
        asyncio.create_task(self._consume_stream(name))

    async def _consume_stream(self, name: str) -> Any:
        """Consume individual stream."""

        stream_info = self.streams[name]

        async for data in stream_info['generator']():
            # Add timestamp if not present
            if not hasattr(data, 'timestamp'):
                data.timestamp = datetime.now()

            # Buffer data
            stream_info['buffer'].append(data)
            stream_info['last_timestamp'] = data.timestamp

            # Trigger synchronization
            await self._synchronize_streams()

    async def _synchronize_streams(self) -> Any:
        """Synchronize data from multiple streams."""

        # Find common time window
        now = datetime.now()
        sync_cutoff = now - timedelta(seconds=self.sync_window)

        synchronized_data = {}

        for name, stream_info in self.streams.items():
            # Get data within sync window
            window_data = [
                data for data in stream_info['buffer']
                if data.timestamp >= sync_cutoff
            ]

            if window_data:
                synchronized_data[name] = window_data

            # Clean old data
            stream_info['buffer'] = [
                data for data in stream_info['buffer']
                if data.timestamp >= sync_cutoff
            ]

        # Output synchronized data
        if synchronized_data:
            await self.output_queue.put({
                'timestamp': now,
                'streams': synchronized_data
            })

    async def get_synchronized_stream(self) -> Any:
        """Get synchronized output stream."""

        while True:
            data = await self.output_queue.get()
            yield data

# Performance monitoring for streaming systems
class StreamPerformanceMonitor:
    """Monitor streaming system performance."""

    def __init__(self) -> None:
        self.metrics = {
            'messages_processed': 0,
            'processing_times': [],
            'error_count': 0,
            'connection_drops': 0,
            'last_message_time': None
        }

    async def record_message_processing(self, processing_time: float) -> Any:
        """Record message processing metrics."""

        self.metrics['messages_processed'] += 1
        self.metrics['processing_times'].append(processing_time)
        self.metrics['last_message_time'] = datetime.now()

        # Keep only recent processing times
        if len(self.metrics['processing_times']) > 1000:
            self.metrics['processing_times'] = self.metrics['processing_times'][-500:]

    def get_performance_stats(self) -> Dict:
        """Get current performance statistics."""

        processing_times = self.metrics['processing_times']

        if processing_times:
            avg_processing_time = sum(processing_times) / len(processing_times)
            max_processing_time = max(processing_times)
        else:
            avg_processing_time = 0
            max_processing_time = 0

        return {
            'messages_processed': self.metrics['messages_processed'],
            'avg_processing_time_ms': avg_processing_time * 1000,
            'max_processing_time_ms': max_processing_time * 1000,
            'error_count': self.metrics['error_count'],
            'connection_drops': self.metrics['connection_drops'],
            'last_message_age_seconds': (
                (datetime.now() - self.metrics['last_message_time']).total_seconds()
                if self.metrics['last_message_time'] else None
            )
        }

# Example usage
async def advanced_streaming_example():
    """Demonstrate advanced streaming features."""

    # Example of advanced stream manager
    print("Advanced Streaming Features:")
    print("1. Resilient connection management")
    print("2. High-availability clustering")
    print("3. Stream multiplexing")
    print("4. Performance monitoring")

    # Implementation would integrate with actual streaming

# Run example
# await advanced_streaming_example()
```

---

## Next Steps

Complete the series with [Best Practices & Production](best-practices.md) for deployment guidance.

---

## Related Tutorials

- [Automated Trading](automated-trading.md) - Trading systems
- [Basic Streaming](basic-streaming.md) - Foundation concepts
- [Best Practices](../../explanation/best-practices.md) - Production deployment