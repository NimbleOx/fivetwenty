# Advanced Data Management

Build robust data processing systems for real-time streams with efficient buffering, aggregation, and memory management.

---

## Real-Time Data Buffer System

```python
import asyncio
import pandas as pd
from collections import deque
from typing import Dict, List, Callable
from datetime import datetime, timedelta

class StreamDataBuffer:
    """Efficient buffer for streaming data with windowing support."""

    def __init__(self, max_size: int = 10000, window_seconds: int = 300):
        self.max_size = max_size
        self.window_seconds = window_seconds
        self.data = deque(maxlen=max_size)
        self.indexed_data = {}

    async def add_data(self, timestamp: datetime, instrument: str, price_data: Dict):
        """Add new data point to buffer."""

        data_point = {
            'timestamp': timestamp,
            'instrument': instrument,
            **price_data
        }

        self.data.append(data_point)

        # Maintain indexed access by instrument
        if instrument not in self.indexed_data:
            self.indexed_data[instrument] = deque(maxlen=self.max_size)

        self.indexed_data[instrument].append(data_point)

        # Clean old data outside window
        await self._cleanup_old_data()

    async def get_windowed_data(self, instrument: str, window_seconds: int = None) -> List[Dict]:
        """Get data within specified time window."""

        window_seconds = window_seconds or self.window_seconds
        cutoff_time = datetime.now() - timedelta(seconds=window_seconds)

        if instrument in self.indexed_data:
            return [
                point for point in self.indexed_data[instrument]
                if point['timestamp'] > cutoff_time
            ]

        return []

    async def _cleanup_old_data(self):
        """Remove data outside the time window."""

        cutoff_time = datetime.now() - timedelta(seconds=self.window_seconds * 2)

        # Clean main buffer
        while self.data and self.data[0]['timestamp'] < cutoff_time:
            self.data.popleft()

        # Clean indexed buffers
        for instrument in self.indexed_data:
            buffer = self.indexed_data[instrument]
            while buffer and buffer[0]['timestamp'] < cutoff_time:
                buffer.popleft()

class RealTimeAggregator:
    """Real-time data aggregation with multiple timeframes."""

    def __init__(self, aggregation_intervals: List[int] = [60, 300, 900]):
        self.intervals = aggregation_intervals  # seconds
        self.aggregated_data = {interval: {} for interval in aggregation_intervals}
        self.last_aggregation = {interval: datetime.now() for interval in aggregation_intervals}

    async def aggregate_price_data(self, instrument: str, price_data: Dict):
        """Aggregate price data across multiple timeframes."""

        now = datetime.now()

        for interval in self.intervals:
            if (now - self.last_aggregation[interval]).total_seconds() >= interval:
                await self._perform_aggregation(instrument, interval, price_data)
                self.last_aggregation[interval] = now

    async def _perform_aggregation(self, instrument: str, interval: int, current_data: Dict):
        """Perform aggregation for specific interval."""

        if instrument not in self.aggregated_data[interval]:
            self.aggregated_data[interval][instrument] = []

        # Calculate OHLC for interval
        aggregated = {
            'timestamp': datetime.now(),
            'interval': interval,
            'open': current_data.get('bid', 0),
            'high': current_data.get('bid', 0),
            'low': current_data.get('bid', 0),
            'close': current_data.get('bid', 0),
            'volume': 1  # Simplified volume counting
        }

        self.aggregated_data[interval][instrument].append(aggregated)

        # Limit stored aggregations
        if len(self.aggregated_data[interval][instrument]) > 1000:
            self.aggregated_data[interval][instrument] = \
                self.aggregated_data[interval][instrument][-500:]

# Memory-efficient streaming processor
class StreamProcessor:
    """Process streaming data with memory optimization."""

    def __init__(self):
        self.buffer = StreamDataBuffer()
        self.aggregator = RealTimeAggregator()
        self.processors = []

    async def process_stream_data(self, instrument: str, price_data: Dict):
        """Main processing pipeline for streaming data."""

        timestamp = datetime.now()

        # Add to buffer
        await self.buffer.add_data(timestamp, instrument, price_data)

        # Perform aggregation
        await self.aggregator.aggregate_price_data(instrument, price_data)

        # Run custom processors
        for processor in self.processors:
            await processor(instrument, price_data, timestamp)

    def add_processor(self, processor: Callable):
        """Add custom data processor."""
        self.processors.append(processor)

# Example custom processors
async def volatility_processor(instrument: str, price_data: Dict, timestamp: datetime):
    """Calculate real-time volatility."""
    # Implementation for volatility calculation
    pass

async def trend_processor(instrument: str, price_data: Dict, timestamp: datetime):
    """Detect trend changes."""
    # Implementation for trend detection
    pass

# Usage example
async def advanced_data_management_example():
    """Demonstrate advanced data management."""

    processor = StreamProcessor()

    # Add custom processors
    processor.add_processor(volatility_processor)
    processor.add_processor(trend_processor)

    # Simulate streaming data
    while True:
        # Simulate price data
        price_data = {'bid': 1.1234, 'ask': 1.1236}
        await processor.process_stream_data("EUR_USD", price_data)

        await asyncio.sleep(0.1)  # 100ms interval

# Run example
# await advanced_data_management_example()
```

---

## Next Steps

Continue to [Real-time Signal Generation](signal-generation.md) to create trading signals from streaming data.

---

## Related Tutorials

- [Basic Streaming](basic-streaming.md) - Foundation
- [Signal Generation](signal-generation.md) - Trading signals
- [Best Practices](best-practices.md) - Production considerations