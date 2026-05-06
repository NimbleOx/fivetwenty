# Streaming Optimization

**Problem**: You need to achieve minimal latency in real-time data processing for high-frequency trading.

**Solution**: Implement high-performance streaming with optimized buffers, non-blocking callbacks, and efficient data structures.

---

## High-Performance Price Streaming

Optimize streaming for minimal latency:

<!-- fragment: partial streaming imports example -->
```python
import asyncio
import time
from collections import deque
from collections.abc import Callable
from decimal import Decimal
from typing import Any, List

from fivetwenty import AsyncClient
from fivetwenty.models import ClientPrice


class HighPerformanceStreamer:
    """Optimized streaming client for HFT applications with minimal latency design."""

    def __init__(self, client: AsyncClient, buffer_size: int = 10000) -> None:
        """Initialize high-performance streamer with optimized data structures."""
        # Step 1: Store client reference and configure performance parameters
        # Buffer size affects memory usage vs. data retention balance
        self.client = client                                     # FiveTwenty AsyncClient for streaming
        self.buffer_size = buffer_size                          # Maximum buffer size per instrument
        print(f"Starting Initializing HFT streamer with {buffer_size} message buffer per instrument")

        # Step 2: Initialize optimized data structures for minimal latency
        # deque provides O(1) append/pop operations vs. list's O(n) for large datasets
        self.price_buffers: dict[str, deque] = {}               # Circular buffers per instrument
        self.callbacks: dict[str, list[Callable]] = {}          # Callback chains per instrument
        self.streaming_active = False                           # Streaming state control

        # Step 3: Initialize comprehensive performance monitoring
        # Statistics help optimize streaming performance for HFT requirements
        self.stats = {
            "messages_received": 0,      # Total message count for throughput analysis
            "callbacks_executed": 0,     # Callback execution count for bottleneck detection
            "start_time": None,          # Streaming start timestamp for uptime calculation
            "last_price_time": {},       # Per-instrument last update time for latency monitoring
        }
        print(f"List Performance monitoring initialized for streaming optimization")

    def add_price_callback(self, instrument: str, callback: Callable) -> Any:
        """Add callback for specific instrument price updates with efficient registration."""
        # Step 4: Register callback with lazy initialization of data structures
        # Lazy initialization prevents memory waste for unused instruments
        if instrument not in self.callbacks:
            print(f"Analysis Registering new instrument for streaming: {instrument}")
            self.callbacks[instrument] = []                          # Initialize callback list
            self.price_buffers[instrument] = deque(maxlen=self.buffer_size)  # Initialize circular buffer
            print(f"   List Buffer allocated: {self.buffer_size} messages max")

        # Step 5: Add callback to instrument-specific callback chain
        # Multiple callbacks per instrument enable parallel processing strategies
        self.callbacks[instrument].append(callback)
        callback_count = len(self.callbacks[instrument])
        print(f"   Success Callback registered for {instrument} (total: {callback_count} callbacks)")

    async def start_optimized_streaming(self, account_id: str, instruments: list[str]) -> Any:
        """Start high-performance streaming with minimal latency for real-time market data."""

        # Step 6: Activate streaming and initialize performance monitoring
        # High-precision timing is critical for HFT latency measurement
        self.streaming_active = True
        self.stats["start_time"] = time.perf_counter()  # High-precision timestamp

        print(f"Starting Starting HFT streaming for {len(instruments)} instruments...")
        print(f"Analysis Monitoring: {', '.join(instruments)}")
        print(f"Time Timestamp: {self.stats['start_time']:.6f}")

        try:
            # Step 7: Enter streaming loop with optimized message processing
            # async for provides efficient iteration over streaming price data
            async for price_data in self.client.pricing.get_pricing_stream(account_id, instruments):
                # Step 8: Check streaming state for graceful shutdown capability
                if not self.streaming_active:
                    print("Red Streaming shutdown requested - exiting gracefully")
                    break

                # Step 9: Route messages by type for optimized processing
                # Type-based routing minimizes processing overhead for each message
                if price_data.type == "PRICE":
                    await self._process_price_update(price_data)  # Price data processing
                elif price_data.type == "HEARTBEAT":
                    await self._process_heartbeat()              # Connection health monitoring
                # Other message types (DISCONNECT, etc.) handled implicitly

        except Exception as e:
            # Step 10: Handle streaming errors with detailed logging
            print(f"Error Streaming error occurred: {e}")
            print(f"Note Check network connectivity and API token validity")
            # Streaming errors may include network issues, API limits, or authentication problems
        finally:
            # Step 11: Ensure clean shutdown regardless of exit reason
            self.streaming_active = False
            runtime = time.perf_counter() - self.stats["start_time"]
            print(f"Red HFT streaming stopped after {runtime:.2f} seconds")
            print(f"Data Final stats: {self.stats['messages_received']} messages processed")

    async def _process_price_update(self, price: ClientPrice) -> Any:
        """Process price update with minimal latency for high-frequency trading."""

        # Step 12: Extract instrument and capture high-precision timestamp
        # Nanosecond precision timing critical for HFT latency analysis
        instrument = price.instrument
        current_time = time.perf_counter()  # High-precision timestamp

        # Step 13: Update performance statistics for monitoring
        # Statistics collection has minimal overhead but provides crucial insights
        self.stats["messages_received"] += 1
        self.stats["last_price_time"][instrument] = current_time

        # Step 14: Store price data in optimized circular buffer
        # deque with maxlen provides O(1) append and automatic oldest-data eviction
        if instrument in self.price_buffers:
            # Extract critical price components for fast access
            bid_price = price.bids[0].price if price.bids else None
            ask_price = price.asks[0].price if price.asks else None

            # Create optimized price record with minimal memory footprint
            price_record = {
                "price": price,           # Full price object for complete data access
                "timestamp": current_time, # High-precision timestamp for latency analysis
                "bid": bid_price,         # Quick bid access for spread calculations
                "ask": ask_price,         # Quick ask access for spread calculations
            }

            # O(1) append operation - critical for HFT performance
            self.price_buffers[instrument].append(price_record)

        # Step 15: Execute callbacks asynchronously to maintain stream performance
        # Non-blocking callback execution prevents slow callbacks from affecting stream
        if instrument in self.callbacks:
            callback_count = len(self.callbacks[instrument])

            for callback in self.callbacks[instrument]:
                # Fire-and-forget pattern: create_task doesn't block main stream
                # This is critical - awaiting callbacks would destroy HFT performance
                asyncio.create_task(self._safe_callback_execution(callback, price))
                self.stats["callbacks_executed"] += 1

            # Optional: Log high callback counts that might affect performance
            if callback_count > 5:
                print(f"⚠️ High callback count for {instrument}: {callback_count} callbacks")

    async def _safe_callback_execution(self, callback: Callable, price: ClientPrice) -> Any:
        """Execute callback safely without blocking main stream for fault-tolerant processing."""
        try:
            # Step 16: Handle both synchronous and asynchronous callbacks efficiently
            # Type detection ensures proper execution without performance penalty
            if asyncio.iscoroutinefunction(callback):
                # Asynchronous callback - await for completion
                await callback(price)
            else:
                # Synchronous callback - direct execution
                callback(price)

        except Exception as e:
            # Step 17: Isolate callback errors to prevent stream disruption
            # Individual callback failures must not affect other callbacks or main stream
            print(f"⚠️ Callback error for {price.instrument}: {e}")
            print(f"Note Callback error isolated - main stream continues normally")
            # Note: In production, consider more sophisticated error handling like:
            # - Callback retry mechanisms
            # - Error rate monitoring
            # - Automatic callback disabling for persistent failures

    async def _process_heartbeat(self) -> Any:
        """Process heartbeat efficiently."""
        # Minimal heartbeat processing for HFT
        pass

    def get_latest_price(self, instrument: str) -> dict | None:
        """Get latest price from buffer with zero-copy access for minimal latency."""
        # Step 18: Provide O(1) access to latest price data
        # Zero-copy access pattern avoids memory allocation overhead
        if instrument in self.price_buffers and self.price_buffers[instrument]:
            # deque[-1] provides O(1) access to most recent price
            return self.price_buffers[instrument][-1]
        return None

    def get_streaming_stats(self) -> dict:
        """Get comprehensive streaming performance statistics for optimization analysis."""
        # Step 19: Calculate detailed performance metrics for HFT optimization
        if self.stats["start_time"]:
            runtime = time.perf_counter() - self.stats["start_time"]

            # Calculate throughput metrics
            messages_per_second = self.stats["messages_received"] / runtime if runtime > 0 else 0
            callbacks_per_second = self.stats["callbacks_executed"] / runtime if runtime > 0 else 0

            return {
                "runtime_seconds": runtime,                                    # Total streaming duration
                "messages_received": self.stats["messages_received"],          # Total message count
                "messages_per_second": messages_per_second,                   # Throughput metric
                "callbacks_executed": self.stats["callbacks_executed"],       # Callback execution count
                "callbacks_per_second": callbacks_per_second,                 # Callback throughput
                "instruments_tracked": len(self.price_buffers),               # Active instrument count
                "buffer_utilization": {                                       # Memory usage analysis
                    inst: len(buf) / self.buffer_size                         # Utilization per instrument
                    for inst, buf in self.price_buffers.items()
                },
                "avg_callbacks_per_instrument": (
                    sum(len(callbacks) for callbacks in self.callbacks.values()) /
                    len(self.callbacks) if self.callbacks else 0
                ),
            }
        return {}

    def stop_streaming(self) -> Any:
        """Stop streaming gracefully."""
        self.streaming_active = False

# Step 20: High-frequency callback implementation example
async def hft_price_callback(price: ClientPrice) -> Any:
    """Ultra-fast price processing callback optimized for minimal latency."""

    # Step 21: Extract price data with minimal computational overhead
    # Decimal conversion ensures precision but has performance cost - optimize as needed
    bid = Decimal(str(price.bids[0].price)) if price.bids else Decimal("0")
    ask = Decimal(str(price.asks[0].price)) if price.asks else Decimal("0")
    spread = ask - bid  # Calculate bid-ask spread for market quality assessment

    # Step 22: Implement intelligent filtering to reduce I/O overhead
    # Only log significant spread movements to minimize performance impact
    if spread > Decimal("0.0010"):  # 1 pip threshold for major pairs
        # Selective logging reduces console I/O which can impact HFT performance
        print(f"Lightning {price.instrument}: {bid}/{ask} (spread: {spread:.5f})")

    # Note: In production HFT systems, consider:
    # - Using structured logging instead of print statements
    # - Implementing price-based triggers for automated trading
    # - Calculating derived metrics (momentum, volatility indicators)
    # - Storing critical data in memory for ultra-fast access

# Step 23: Comprehensive usage example for high-frequency trading
async def optimize_streaming_example(client: AsyncClient, account_id: str):
    """Demonstrate optimized streaming setup for HFT applications."""
    print(f"Starting Starting HFT streaming optimization example...")

    # Step 24: Initialize high-performance streamer with HFT-appropriate buffer size
    streamer = HighPerformanceStreamer(client, buffer_size=1000)  # 1K messages per instrument
    print(f"List Streamer configured with 1,000 message buffer per instrument")

    # Step 25: Configure streaming for major currency pairs with high liquidity
    # Major pairs provide best execution and minimal slippage for HFT strategies
    major_pairs = ["EUR_USD", "GBP_USD", "USD_JPY"]
    print(f"Analysis Configuring callbacks for {len(major_pairs)} major pairs...")

    for instrument in major_pairs:
        streamer.add_price_callback(instrument, hft_price_callback)
        print(f"   Success {instrument} callback registered")

    # Step 26: Start streaming with background task execution
    # Background task prevents blocking main execution thread
    print(f"Lightning Starting optimized streaming...")
    streaming_task = asyncio.create_task(
        streamer.start_optimized_streaming(account_id, major_pairs),
    )
    print(f"📄 Streaming task created - prices will be processed asynchronously")

    # Step 27: Monitor streaming performance for optimization analysis
    await asyncio.sleep(30)  # Stream for 30 seconds to collect performance data
    stats = streamer.get_streaming_stats()

    # Step 28: Display comprehensive performance analysis
    print(f"\nData HFT Streaming Performance Analysis:")
    print(f"   Time Runtime: {stats.get('runtime_seconds', 0):.2f} seconds")
    print(f"   📬 Messages: {stats.get('messages_received', 0)} total")
    print(f"   Starting Throughput: {stats.get('messages_per_second', 0):.1f} msg/sec")
    print(f"   Processing Callbacks: {stats.get('callbacks_executed', 0)} executed")
    print(f"   List Instruments: {stats.get('instruments_tracked', 0)} active")

    # Display buffer utilization for memory optimization
    buffer_util = stats.get('buffer_utilization', {})
    print(f"\nAnalysis Buffer Utilization Analysis:")
    for instrument, utilization in buffer_util.items():
        percentage = utilization * 100
        status = "Success" if percentage < 80 else "⚠️" if percentage < 95 else "Error"
        print(f"   {status} {instrument}: {percentage:.1f}% utilized")

    # Step 29: Graceful shutdown with performance summary
    print(f"\nRed Stopping streaming gracefully...")
    streamer.stop_streaming()
    await streaming_task

    final_stats = streamer.get_streaming_stats()
    final_throughput = final_stats.get('messages_per_second', 0)
    print(f"Success Streaming optimization example completed")
    print(f"Target Final throughput: {final_throughput:.1f} messages/second")
    print(f"Note HFT Performance Status: {'OPTIMAL' if final_throughput > 100 else 'NEEDS_OPTIMIZATION'}")
```

---

## Streaming Performance Patterns

### Non-Blocking Callback Pattern

Execute callbacks without blocking the main stream:

<!-- fragment: partial non-blocking callback execution example -->
```python
# Good: Non-blocking callback execution

import asyncio
from typing import Any
from fivetwenty.models import ClientPrice

async def _process_price_update(self, price: ClientPrice) -> Any:
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

<!-- fragment: Demo circular buffer usage with deque patterns -->
```python
from collections import deque

# Efficient: Fixed-size circular buffer
price_buffer = deque(maxlen=10000)

# Inefficient: Unlimited list growth
price_list = []  # Can grow without bounds
```

### Message Filtering

Filter messages at the earliest point:

<!-- fragment: partial message filtering example -->
```python


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

<!-- fragment: partial NamedTuple memory efficiency example -->
```python
# Use NamedTuple for memory efficiency
from typing import NamedTuple
from decimal import Decimal




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

<!-- fragment: partial batch processing example -->
```python
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