# Streaming Optimization

**Problem**: You need to achieve minimal latency in real-time data processing for high-frequency trading.

**Solution**: Implement high-performance streaming with optimized buffers, non-blocking callbacks, and efficient data structures.

---

## High-Performance Price Streaming

Optimize streaming for minimal latency:

```python
import asyncio
import time
from collections import deque
from collections.abc import Callable
from decimal import Decimal
from typing import Dict, Optional
from fivetwenty import AsyncClient




"""Comprehensive module for trading operations."""
class HighPerformanceStreamer:
    """Optimized streaming client for HFT applications."""

    def __init__(self, client: AsyncClient, buffer_size: int = 10000) -> None:
        self.client = client
        self.buffer_size = buffer_size
        self.price_buffers: dict[str, deque] = {}
        self.callbacks: dict[str, List[Callable]] = {}
        self.streaming_active = False
        self.stats = {
            "messages_received": 0,
            "callbacks_executed": 0,
            "start_time": None,
            "last_price_time": {},
        }

    def add_price_callback(self, instrument: str, callback: Callable) -> Any:
        """Add callback for specific instrument price updates."""
        if instrument not in self.callbacks:
            self.callbacks[instrument] = []
            self.price_buffers[instrument] = deque(maxlen=self.buffer_size)

        self.callbacks[instrument].append(callback)

    async def start_optimized_streaming(self, account_id: str, instruments: List[str]) -> Any:
        """Start high-performance streaming with minimal latency."""

        self.streaming_active = True
        self.stats["start_time"] = time.perf_counter()

        print(f"🚀 Starting HFT streaming for {len(instruments)} instruments")

        try:
            async for price_data in self.client.pricing.get_pricing_stream(account_id, instruments):
                if not self.streaming_active:
                    break

                if price_data.type == "PRICE":
                    await self._process_price_update(price_data)
                elif price_data.type == "HEARTBEAT":
                    await self._process_heartbeat()

        except Exception as e:
            print(f"❌ Streaming error: {e}")
        finally:
            self.streaming_active = False

    async def _process_price_update(self, price: ClientPrice) -> Any:
        """Process price update with minimal latency."""

        instrument = price.instrument
        current_time = time.perf_counter()

        # Update statistics
        self.stats["messages_received"] += 1
        self.stats["last_price_time"][instrument] = current_time

        # Store in buffer
        if instrument in self.price_buffers:
            self.price_buffers[instrument].append({
                "price": price,
                "timestamp": current_time,
                "bid": price.bids[0].price if price.bids else None,
                "ask": price.asks[0].price if price.asks else None,
            })

        # Execute callbacks asynchronously (non-blocking)
        if instrument in self.callbacks:
            for callback in self.callbacks[instrument]:
                # Fire and forget - don't await to maintain speed
                asyncio.create_task(self._safe_callback_execution(callback, price))
                self.stats["callbacks_executed"] += 1

    async def _safe_callback_execution(self, callback: Callable, price: ClientPrice) -> Any:
        """Execute callback safely without blocking main stream."""
        try:
            if asyncio.iscoroutinefunction(callback):
                await callback(price)
            else:
                callback(price)
        except Exception as e:
            print(f"⚠️ Callback error: {e}")

    async def _process_heartbeat(self) -> Any:
        """Process heartbeat efficiently."""
        # Minimal heartbeat processing for HFT
        pass

    def get_latest_price(self, instrument: str) -> dict | None:
        """Get latest price from buffer with zero-copy access."""
        if instrument in self.price_buffers and self.price_buffers[instrument]:
            return self.price_buffers[instrument][-1]
        return None

    def get_streaming_stats(self) -> dict:
        """Get streaming performance statistics."""
        if self.stats["start_time"]:
            runtime = time.perf_counter() - self.stats["start_time"]
            return {
                "runtime_seconds": runtime,
                "messages_received": self.stats["messages_received"],
                "messages_per_second": self.stats["messages_received"] / runtime if runtime > 0 else 0,
                "callbacks_executed": self.stats["callbacks_executed"],
                "instruments_tracked": len(self.price_buffers),
                "buffer_utilization": {
                    inst: len(buf) / self.buffer_size
                    for inst, buf in self.price_buffers.items()
                },
            }
        return {}

    def stop_streaming(self) -> Any:
        """Stop streaming gracefully."""
        self.streaming_active = False

# High-frequency callback implementation
async def hft_price_callback(price: ClientPrice) -> Any:
    """Ultra-fast price processing callback."""

    # Minimal processing for maximum speed
    bid = Decimal(str(price.bids[0].price)) if price.bids else Decimal("0")
    ask = Decimal(str(price.asks[0].price)) if price.asks else Decimal("0")
    spread = ask - bid

    # Only log significant moves (reduce I/O)
    if spread > Decimal("0.0010"):  # 1 pip threshold
        print(f"⚡ {price.instrument}: {bid}/{ask} (spread: {spread:.5f})")

# Usage
async def optimize_streaming_example(client: AsyncClient, account_id: str):
    streamer = HighPerformanceStreamer(client, buffer_size=1000)

    # Add callbacks for major pairs
    major_pairs = ["EUR_USD", "GBP_USD", "USD_JPY"]
    for instrument in major_pairs:
        streamer.add_price_callback(instrument, hft_price_callback)

    # Start streaming
    streaming_task = asyncio.create_task(
        streamer.start_optimized_streaming(account_id, major_pairs),
    )

    # Monitor performance
    await asyncio.sleep(30)  # Stream for 30 seconds
    stats = streamer.get_streaming_stats()
    print(f"📊 Streaming stats: {stats}")

    streamer.stop_streaming()
    await streaming_task
```

---

## Streaming Performance Patterns

### Non-Blocking Callback Pattern

Execute callbacks without blocking the main stream:

```python
# Good: Non-blocking callback execution

from typing import Any

"""Comprehensive module for trading operations."""
async def _process_price_update(self, price) -> Any:
    # Store data first (fast)
    self.store_price_data(price)

    # Execute callbacks asynchronously (non-blocking)
    for callback in self.callbacks:
        asyncio.create_task(callback(price))

# Bad: Blocking callback execution
async def _process_price_update(self, price) -> Any:
    # This blocks the main stream
    for callback in self.callbacks:
        await callback(price)  # Blocks here
```

### Buffer Optimization

Use circular buffers for memory efficiency:

```python
from collections import deque

# Efficient: Fixed-size circular buffer
price_buffer = deque(maxlen=10000)

# Inefficient: Unlimited list growth
price_list = []  # Can grow without bounds
```

### Message Filtering

Filter messages at the earliest point:

```python

"""Module docstring."""

from typing import Any
from decimal import Decimal

async def _process_price_update(self, price) -> Any:
    # Filter early to reduce processing
    if not self._should_process_price(price):
        return

    # Process only relevant updates
    await self._handle_price_update(price)

def _should_process_price(self, price) -> Any:
    # Only process prices with tight spreads
    if price.bids and price.asks:
        spread = Decimal(str(price.asks[0].price)) - Decimal(str(price.bids[0].price))
        return spread < 0.0005  # 0.5 pip threshold
    return False
```

---

## Performance Metrics

### Key Streaming Metrics

Monitor these metrics for optimal performance:

- **Messages per second**: Target > 100/sec
- **Callback execution time**: Target < 1ms
- **Buffer utilization**: Keep < 80%
- **Memory growth**: Should remain stable

### Streaming Latency Breakdown

Understand latency sources:

1. **Network latency**: 5-50ms (varies by location)
2. **Processing latency**: < 1ms (your code)
3. **Callback latency**: < 1ms (your callbacks)
4. **Total latency**: < 100ms end-to-end

---

## Optimization Techniques

### Memory-Efficient Data Storage

```python
# Use NamedTuple for memory efficiency
from typing import NamedTuple
from decimal import Decimal




"""Comprehensive module for trading operations."""
class FastPrice(NamedTuple):
    """Class docstring."""
    bid: float
    ask: float
    timestamp: float

    @property
    def spread(self) -> float:
        return self.ask - self.bid

# Store as FastPrice instead of dict
price_data = FastPrice(Decimal("1.1234"), Decimal("1.1236"), time.perf_counter())
```

### Batch Processing

Process multiple updates together when possible:

```python

"""Module docstring."""

from typing import Any
async def batch_process_prices(self, prices: List[ClientPrice]) -> Any:
    """Process multiple prices in a batch for efficiency."""

    # Group by instrument
    by_instrument = {}
    for price in prices:
        if price.instrument not in by_instrument:
            by_instrument[price.instrument] = []
        by_instrument[price.instrument].append(price)

    # Process each instrument's prices together
    for instrument, price_list in by_instrument.items():
        await self._process_instrument_batch(instrument, price_list)
```

---

## Next Steps

Continue to [Memory and CPU Optimization](memory-cpu-optimization.md) for efficient resource usage.

---

## Related Guides

- [Connection Optimization](connection-optimization.md) - Connection pooling strategies
- [Latency Optimization](latency-optimization.md) - Low-latency order execution
- [Performance Monitoring](latency-optimization.md) - Streaming performance monitoring