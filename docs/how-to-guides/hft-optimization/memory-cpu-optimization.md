# Memory and CPU Optimization

**Problem**: You need efficient resource usage for sustained high-performance HFT operations.

**Solution**: Implement optimized data structures, memory pools, and CPU optimization techniques to minimize resource overhead.

---

## Efficient Data Structures

Use optimized data structures for HFT:

```python
import asyncio
import array
import time
from collections import defaultdict
from dataclasses import dataclass
from typing import NamedTuple, Optional, Any
from decimal import Decimal

import numpy as np


class FastPrice(NamedTuple):
    """Memory-efficient price representation."""
    bid: float
    ask: float
    timestamp: float

    @property
    def spread(self) -> float:
        return self.ask - self.bid

    @property
    def mid(self) -> float:
        return (self.bid + self.ask) / 2

class CircularBuffer:
    """Ultra-fast circular buffer for price history."""

    def __init__(self, size: int) -> None:
        self.size = size
        self.data = np.empty((size, 3), dtype=np.float64)  # bid, ask, timestamp
        self.index = 0
        self.count = 0

    def append(self, bid: float, ask: float, timestamp: float) -> None:
        """Add price point with O(1) complexity."""
        self.data[self.index] = [bid, ask, timestamp]
        self.index = (self.index + 1) % self.size
        if self.count < self.size:
            self.count += 1

    def get_latest(self) -> Optional[FastPrice]:
        """Get most recent price."""
        if self.count == 0:
            return None

        latest_idx = (self.index - 1) % self.size
        row = self.data[latest_idx]
        return FastPrice(row[0], row[1], row[2])

    def get_history(self, n: int | None = None) -> np.ndarray:
        """Get recent history efficiently."""
        if n is None:
            n = self.count

        n = min(n, self.count)
        if n == 0:
            return np.empty((0, 3))

        if self.count < self.size:
            return self.data[:self.count]
        else:
            # Handle circular buffer wrap-around
            return np.concatenate([
                self.data[self.index:],
                self.data[:self.index]
            ])[-n:]

class OptimizedPriceManager:
    """High-performance price management for HFT."""

    def __init__(self, buffer_size: int = 1000) -> None:
        self.buffers: dict[str, CircularBuffer] = {}
        self.buffer_size = buffer_size
        self.update_counts = defaultdict(int)
        self.last_update_times: dict[str, float] = {}

    def update_price(self, instrument: str, bid: float, ask: float, timestamp: float) -> None:
        """Ultra-fast price update."""

        if instrument not in self.buffers:
            self.buffers[instrument] = CircularBuffer(self.buffer_size)

        self.buffers[instrument].append(bid, ask, timestamp)
        self.update_counts[instrument] += 1
        self.last_update_times[instrument] = timestamp

    def get_current_price(self, instrument: str) -> Optional[FastPrice]:
        """Get current price with minimal latency."""
        buffer = self.buffers.get(instrument)
        return buffer.get_latest() if buffer else None

    def get_price_history(self, instrument: str, count: int = 100) -> np.ndarray:
        """Get price history as numpy array for fast analysis."""
        buffer = self.buffers.get(instrument)
        return buffer.get_history(count) if buffer else np.empty((0, 3))

    def calculate_volatility(self, instrument: str, window: int = 50) -> float:
        """Fast volatility calculation using numpy."""
        history = self.get_price_history(instrument, window)
        if len(history) < 2:
            return 0.0

        # Calculate mid prices
        mid_prices = (history[:, 0] + history[:, 1]) / 2

        # Calculate returns
        returns = np.diff(mid_prices) / mid_prices[:-1]

        # Return standard deviation (volatility)
        return float(np.std(returns))

# Integration with streaming
price_manager = OptimizedPriceManager(buffer_size=5000)

# Example price object structure for demonstration
class ClientPrice:
    def __init__(self, instrument: str, bids: list, asks: list):
        self.instrument = instrument
        self.bids = bids
        self.asks = asks

class PriceLevel:
    def __init__(self, price: str):
        self.price = price

async def optimized_price_callback(price: ClientPrice) -> Any:
    """Optimized callback using efficient data structures."""

    bid = Decimal(str(price.bids[0].price)) if price.bids else Decimal('0')
    ask = Decimal(str(price.asks[0].price)) if price.asks else Decimal('0')
    timestamp = time.perf_counter()

    # Ultra-fast update
    price_manager.update_price(price.instrument, bid, ask, timestamp)

    # Fast analysis
    current = price_manager.get_current_price(price.instrument)
    if current and current.spread < 0.0005:  # Tight spread opportunity
        print(f"🎯 Tight spread: {price.instrument} {current.spread:.5f}")
```

---

## Memory Pool Management

Pre-allocate objects to reduce allocation overhead:

```python
import time
from collections import deque
from typing import Any
from decimal import Decimal



class TradingObjectPool:
    """Object pool for common trading objects to reduce allocations."""

    def __init__(self, pool_size: int = 1000) -> None:
        self.pool_size = pool_size
        self.price_objects = deque(maxlen=pool_size)
        self.order_objects = deque(maxlen=pool_size)

        # Pre-populate pools
        for _ in range(pool_size):
            self.price_objects.append({'bid': 0.0, 'ask': 0.0, 'timestamp': 0.0, 'instrument': ''})
            self.order_objects.append({'instrument': '', 'units': 0, 'price': 0.0})

    def get_price_object(self) -> dict[str, Any]:
        """Get pre-allocated price object."""
        if self.price_objects:
            return self.price_objects.popleft()
        return {'bid': 0.0, 'ask': 0.0, 'timestamp': 0.0, 'instrument': ''}

    def return_price_object(self, obj: dict[str, Any]) -> None:
        """Return object to pool."""
        # Clear object data
        obj.clear()
        obj.update({'bid': 0.0, 'ask': 0.0, 'timestamp': 0.0, 'instrument': ''})

        if len(self.price_objects) < self.pool_size:
            self.price_objects.append(obj)

    def get_order_object(self) -> dict[str, Any]:
        """Get pre-allocated order object."""
        if self.order_objects:
            return self.order_objects.popleft()
        return {'instrument': '', 'units': 0, 'price': 0.0}

    def return_order_object(self, obj: dict[str, Any]) -> None:
        """Return order object to pool."""
        obj.clear()
        obj.update({'instrument': '', 'units': 0, 'price': 0.0})

        if len(self.order_objects) < self.pool_size:
            self.order_objects.append(obj)

# Usage example
object_pool = TradingObjectPool(pool_size=5000)

async def efficient_price_processing(price: Any) -> None:  # ClientPrice placeholder
    """Process price using object pool for efficiency."""

    # Get reusable object from pool
    price_obj = object_pool.get_price_object()

    try:
        # Populate with current data
        price_obj['bid'] = Decimal(str(price.bids[0].price)) if price.bids else Decimal('0')
        price_obj['ask'] = Decimal(str(price.asks[0].price)) if price.asks else Decimal('0')
        price_obj['timestamp'] = time.perf_counter()
        price_obj['instrument'] = price.instrument

        # Process the price data
        await process_price_data(price_obj)

    finally:
        # Return object to pool
        object_pool.return_price_object(price_obj)

async def process_price_data(price_obj: dict[str, Any]) -> None:
    """Process price data (your trading logic here)."""
    spread = price_obj['ask'] - price_obj['bid']
    if spread < 0.0005:
        print(f"Tight spread detected: {price_obj['instrument']} {spread:.5f}")
```

---

## CPU Optimization Techniques

### Minimize Function Calls

```python
# Efficient: Direct attribute access

from typing import Any

def fast_spread_calculation(price: Any) -> float:
    return price.asks[0].price - price.bids[0].price

def get_ask_price(price) -> float:
    """Extract ask price from price object."""
    return price.asks[0].price if price.asks else 0.0

def get_bid_price(price) -> float:
    """Extract bid price from price object."""
    return price.bids[0].price if price.bids else 0.0

def calculate_spread(ask: float, bid: float) -> float:
    """Calculate spread between ask and bid."""
    return ask - bid

# Less efficient: Multiple function calls
def slow_spread_calculation(price: Any) -> float:
    ask = get_ask_price(price)
    bid = get_bid_price(price)
    return calculate_spread(ask, bid)
```

### Use Local Variables

```python
# Efficient: Cache frequently accessed attributes

from decimal import Decimal
from typing import Any

async def handle_price_update(instrument: str, bid_price: Decimal, ask_price: Decimal, spread: Decimal) -> None:
    """Handle price update processing."""
    print(f"Price update: {instrument} bid={bid_price:.5f} ask={ask_price:.5f} spread={spread:.5f}")

async def optimized_price_processing(price: Any) -> None:
    bids = price.bids
    asks = price.asks
    instrument = price.instrument

    if bids and asks:
        bid_price = bids[0].price
        ask_price = asks[0].price
        spread = ask_price - bid_price

        # Process with cached values
        await handle_price_update(instrument, bid_price, ask_price, spread)

# Less efficient: Repeated attribute lookups
async def unoptimized_price_processing(price: Any) -> None:
    if price.bids and price.asks:
        spread = price.asks[0].price - price.bids[0].price
        await handle_price_update(price.instrument, price.bids[0].price,
                                 price.asks[0].price, spread)
```

### Vectorized Operations

```python

from typing import Any
import numpy as np




def calculate_multiple_spreads(prices_array: np.ndarray) -> np.ndarray:
    """Calculate spreads for multiple prices efficiently."""

    # Vectorized calculation using numpy
    bids = prices_array[:, 0]
    asks = prices_array[:, 1]
    spreads = asks - bids

    return spreads

def calculate_moving_average(prices, window) -> Any:
    """Fast moving average using numpy."""
    return np.convolve(prices, np.ones(window)/window, mode="valid")

def detect_price_movements(prices, threshold=0.0001) -> Any:
    """Vectorized price movement detection."""
    price_changes = np.abs(np.diff(prices))
    significant_moves = price_changes > threshold
    return np.where(significant_moves)[0]
```

---

## Memory Management Strategies

### Avoid Memory Leaks

```python
import weakref
from typing import WeakSet, Any



class MemoryEfficientSubscriptionManager:
    """Manage price subscriptions without memory leaks."""

    def __init__(self) -> None:
        self.subscribers: WeakSet = weakref.WeakSet()
        self.active_subscriptions = {}

    def subscribe(self, callback: Any) -> Any:
        """Subscribe to price updates using weak references."""
        self.subscribers.add(callback)

    def notify_all(self, price_data: Any) -> Any:
        """Notify all subscribers efficiently."""
        # Use list() to avoid "set changed size during iteration"
        for subscriber in list(self.subscribers):
            try:
                subscriber(price_data)
            except Exception as e:
                print(f"Subscriber notification error: {e}")

    def cleanup_dead_references(self) -> Any:
        """Cleanup is automatic with WeakSet."""
        pass

# Usage
subscription_manager = MemoryEfficientSubscriptionManager()

# Callbacks will be automatically removed when they go out of scope
def price_callback(price: Any) -> Any:
    print(f"Price update: {price}")

subscription_manager.subscribe(price_callback)
```

### Limit Buffer Growth

```python
import time
from collections import deque
from decimal import Decimal
from typing import Any




class BoundedDataStorage:
    """Storage with automatic size limits."""

    def __init__(self, max_size: int = 10000) -> None:
        self.max_size = max_size
        self.data = deque(maxlen=max_size)
        self.overflow_count = 0

    def add_data(self, item: Any) -> Any:
        """Add data with automatic size management."""
        if len(self.data) >= self.max_size:
            self.overflow_count += 1

        self.data.append(item)

    def get_memory_stats(self) -> Any:
        """Get memory usage statistics."""
        return {
            "current_size": len(self.data),
            "max_size": self.max_size,
            "utilization": len(self.data) / self.max_size,
            "overflow_count": self.overflow_count,
        }

# Usage
price_storage = BoundedDataStorage(max_size=5000)

async def store_price_efficiently(price: Any) -> Any:
    """Store price with automatic memory management."""
    price_data = {
        "instrument": price.instrument,
        "bid": Decimal(str(price.bids[0].price)) if price.bids else Decimal("0"),
        "ask": Decimal(str(price.asks[0].price)) if price.asks else Decimal("0"),
        "timestamp": time.perf_counter(),
    }

    price_storage.add_data(price_data)

    # Monitor memory usage
    stats = price_storage.get_memory_stats()
    if stats["utilization"] > 0.9:
        print(f"Warning: Price storage {stats['utilization']:.1%} full")
```

---

## Performance Benchmarking

### Measure Execution Time

```python
import asyncio
import functools
import numpy as np
import time
from typing import Any



def benchmark_function(func: Any) -> Any:
    """Decorator to benchmark function execution time."""

    @functools.wraps(func)
    async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
        start_time = time.perf_counter()
        result = await func(*args, **kwargs)
        end_time = time.perf_counter()

        execution_time = (end_time - start_time) * 1000  # Convert to ms
        print(f"{func.__name__} executed in {execution_time:.3f}ms")

        return result

    @functools.wraps(func)
    def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        end_time = time.perf_counter()

        execution_time = (end_time - start_time) * 1000
        print(f"{func.__name__} executed in {execution_time:.3f}ms")

        return result

    return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper

async def analyze_price_data(price: Any) -> None:
    """Analyze price data (example implementation)."""
    # Simulate some analysis work
    await asyncio.sleep(0.001)  # Simulate 1ms processing time

# Usage
@benchmark_function
async def process_price_update(price: Any) -> Any:
    """Benchmarked price processing."""
    # Your price processing logic here
    await analyze_price_data(price)

@benchmark_function
def calculate_technical_indicator(prices: Any) -> Any:
    """Benchmarked indicator calculation."""
    return np.mean(prices[-20:])  # 20-period moving average
```

### Memory Profiling

```python
import os
import time
from typing import Any

import psutil



class MemoryProfiler:
    """Monitor memory usage during HFT operations."""

    def __init__(self) -> None:
        self.process = psutil.Process(os.getpid())
        self.baseline_memory = self.get_memory_usage()
        self.peak_memory = self.baseline_memory
        self.measurements = []

    def get_memory_usage(self) -> float:
        """Get current memory usage in MB."""
        return self.process.memory_info().rss / 1024 / 1024

    def measure(self, label: str = "") -> Any:
        """Take memory measurement."""
        current_memory = self.get_memory_usage()

        if current_memory > self.peak_memory:
            self.peak_memory = current_memory

        measurement = {
            "label": label,
            "memory_mb": current_memory,
            "delta_mb": current_memory - self.baseline_memory,
            "timestamp": time.perf_counter(),
        }

        self.measurements.append(measurement)

        if len(self.measurements) > 1000:  # Limit measurement history
            self.measurements = self.measurements[-500:]

        return measurement

    def get_memory_report(self) -> Any:
        """Generate memory usage report."""
        if not self.measurements:
            return "No measurements taken"

        current = self.measurements[-1]
        return {
            "baseline_mb": self.baseline_memory,
            "current_mb": current["memory_mb"],
            "peak_mb": self.peak_memory,
            "total_increase_mb": current["memory_mb"] - self.baseline_memory,
            "measurement_count": len(self.measurements),
        }

# Usage
memory_profiler = MemoryProfiler()

async def simulate_price_processing() -> Any:
    """Simulate price processing for profiling."""
    # Create and process some data
    data = [{"price": i * 0.0001, "timestamp": time.time()} for i in range(100)]
    processed = [d["price"] * 1.1 for d in data]
    return processed

async def profiled_hft_operation() -> Any:
    """HFT operation with memory profiling."""

    memory_profiler.measure("start")

    # Simulate HFT operations
    for i in range(1000):
        # Simulate price processing
        await simulate_price_processing()

        if i % 100 == 0:
            memory_profiler.measure(f"iteration_{i}")

    memory_profiler.measure("end")

    # Generate report
    report = memory_profiler.get_memory_report()
    print(f"Memory Report: {report}")
```

---

## Next Steps

Continue to [Latency Optimization](latency-optimization.md) for ultra-fast order execution techniques.

---

## Related Guides

- [Streaming Optimization](streaming-optimization.md) - High-performance streaming
- [System Resource Management](memory-cpu-optimization.md) - Advanced resource control
- [Performance Monitoring](latency-optimization.md) - Comprehensive monitoring