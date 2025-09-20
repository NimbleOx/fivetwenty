# How to Optimize for High-Frequency Trading

**Problem**: You need to optimize the FiveTwenty for high-frequency trading applications with minimal latency and maximum throughput.

**Solution**: Implement performance optimization techniques including connection pooling, request batching, streaming optimization, and efficient data structures.

---

## Prerequisites

- OANDA account with sufficient API rate limits
- Understanding of async programming patterns
- Knowledge of Python performance optimization
- Network connectivity with low latency to OANDA servers
- Adequate system resources (CPU, memory, network)

---

## Connection Optimization

### Persistent Connection Pooling

Reuse connections to minimize latency:

```python
import asyncio
import time
from typing import Dict, List, Optional
from fivetwenty import AsyncClient, Environment
from fivetwenty.models import ClientPrice

class OptimizedTradingClient:
    """High-performance OANDA client for HFT applications."""

    def __init__(self, token: str, environment: Environment, max_connections: int = 10):
        self.token = token
        self.environment = environment
        self.max_connections = max_connections
        self.client: Optional[AsyncClient] = None
        self._connection_pool_initialized = False

    async def initialize(self):
        """Initialize optimized client with persistent connections."""

        # Create client with optimized settings
        self.client = AsyncClient(
            token=self.token,
            environment=self.environment,
            timeout=5.0,  # Shorter timeout for HFT
            # Connection pool optimization
            limits_max_connections=self.max_connections,
            limits_max_keepalive_connections=self.max_connections,
            limits_keepalive_expiry=300,  # Keep connections alive for 5 minutes
        )

        await self.client.__aenter__()
        self._connection_pool_initialized = True
        print(f"✅ Optimized client initialized with {self.max_connections} connections")

    async def close(self):
        """Clean up connections."""
        if self.client:
            await self.client.__aexit__(None, None, None)
            self._connection_pool_initialized = False

    async def __aenter__(self):
        await self.initialize()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

# Usage with optimized settings
async def setup_hft_client():
    async with OptimizedTradingClient(
        token="your-token",
        environment=Environment.PRACTICE,
        max_connections=20  # Higher connection limit for HFT
    ) as hft_client:
        return hft_client.client

# client = await setup_hft_client()
```

### Request Batching and Pipelining

Batch multiple operations to reduce round trips:

```python
class BatchRequestManager:
    """Batch multiple requests for improved throughput."""

    def __init__(self, client: AsyncClient, batch_size: int = 10):
        self.client = client
        self.batch_size = batch_size
        self.pending_requests: List = []

    async def batch_get_prices(self, account_id: str, instrument_batches: List[List[str]]) -> List[List[ClientPrice]]:
        """Get prices for multiple instrument sets concurrently."""

        start_time = time.perf_counter()

        # Create concurrent price requests
        tasks = [
            self.client.pricing.get(account_id, instruments)
            for instruments in instrument_batches
        ]

        # Execute all requests concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)

        end_time = time.perf_counter()

        # Filter successful results
        successful_results = [r for r in results if not isinstance(r, Exception)]
        failed_count = len(results) - len(successful_results)

        print(f"⚡ Batch pricing: {len(successful_results)} successful, {failed_count} failed")
        print(f"   Time: {(end_time - start_time) * 1000:.1f}ms")
        print(f"   Throughput: {len(instrument_batches) / (end_time - start_time):.1f} req/sec")

        return successful_results

    async def batch_market_orders(self, account_id: str, order_requests: List[Dict]) -> List:
        """Execute multiple market orders concurrently."""

        start_time = time.perf_counter()

        # Create order tasks
        tasks = []
        for order_req in order_requests:
            task = self.client.orders.post_market_order(
                account_id=account_id,
                instrument=order_req['instrument'],
                units=order_req['units'],
                **order_req.get('extra_params', {})
            )
            tasks.append(task)

        # Execute concurrently with timeout
        try:
            results = await asyncio.wait_for(
                asyncio.gather(*tasks, return_exceptions=True),
                timeout=2.0  # 2-second timeout for HFT
            )
        except asyncio.TimeoutError:
            print("⚠️ Batch order timeout - some orders may have failed")
            return []

        end_time = time.perf_counter()

        # Analyze results
        successful_orders = [r for r in results if not isinstance(r, Exception) and hasattr(r, 'order_fill_transaction')]

        print(f"⚡ Batch orders: {len(successful_orders)}/{len(order_requests)} successful")
        print(f"   Execution time: {(end_time - start_time) * 1000:.1f}ms")

        return successful_orders

# Usage example
async def hft_batch_example(client: AsyncClient, account_id: str):
    batch_manager = BatchRequestManager(client, batch_size=15)

    # Batch price requests for different instrument groups
    major_pairs = ["EUR_USD", "GBP_USD", "USD_JPY"]
    minor_pairs = ["EUR_GBP", "AUD_USD", "USD_CAD"]
    exotic_pairs = ["USD_TRY", "EUR_TRY", "GBP_TRY"]

    price_results = await batch_manager.batch_get_prices(
        account_id, [major_pairs, minor_pairs, exotic_pairs]
    )

    # Batch order execution based on price analysis
    orders = [
        {'instrument': 'EUR_USD', 'units': 10000},
        {'instrument': 'GBP_USD', 'units': -5000},
        {'instrument': 'USD_JPY', 'units': 15000}
    ]

    order_results = await batch_market_orders(account_id, orders)
    return price_results, order_results
```

---

## Streaming Optimization

### High-Performance Price Streaming

Optimize streaming for minimal latency:

```python
import asyncio
from collections import deque
from typing import Dict, Callable, Optional
import time

class HighPerformanceStreamer:
    """Optimized streaming client for HFT applications."""

    def __init__(self, client: AsyncClient, buffer_size: int = 10000):
        self.client = client
        self.buffer_size = buffer_size
        self.price_buffers: Dict[str, deque] = {}
        self.callbacks: Dict[str, List[Callable]] = {}
        self.streaming_active = False
        self.stats = {
            'messages_received': 0,
            'callbacks_executed': 0,
            'start_time': None,
            'last_price_time': {}
        }

    def add_price_callback(self, instrument: str, callback: Callable):
        """Add callback for specific instrument price updates."""
        if instrument not in self.callbacks:
            self.callbacks[instrument] = []
            self.price_buffers[instrument] = deque(maxlen=self.buffer_size)

        self.callbacks[instrument].append(callback)

    async def start_optimized_streaming(self, account_id: str, instruments: List[str]):
        """Start high-performance streaming with minimal latency."""

        self.streaming_active = True
        self.stats['start_time'] = time.perf_counter()

        print(f"🚀 Starting HFT streaming for {len(instruments)} instruments")

        try:
            async for price_data in self.client.pricing.stream(account_id, instruments):
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

    async def _process_price_update(self, price: ClientPrice):
        """Process price update with minimal latency."""

        instrument = price.instrument
        current_time = time.perf_counter()

        # Update statistics
        self.stats['messages_received'] += 1
        self.stats['last_price_time'][instrument] = current_time

        # Store in buffer
        if instrument in self.price_buffers:
            self.price_buffers[instrument].append({
                'price': price,
                'timestamp': current_time,
                'bid': price.bids[0].price if price.bids else None,
                'ask': price.asks[0].price if price.asks else None
            })

        # Execute callbacks asynchronously (non-blocking)
        if instrument in self.callbacks:
            for callback in self.callbacks[instrument]:
                # Fire and forget - don't await to maintain speed
                asyncio.create_task(self._safe_callback_execution(callback, price))
                self.stats['callbacks_executed'] += 1

    async def _safe_callback_execution(self, callback: Callable, price: ClientPrice):
        """Execute callback safely without blocking main stream."""
        try:
            if asyncio.iscoroutinefunction(callback):
                await callback(price)
            else:
                callback(price)
        except Exception as e:
            print(f"⚠️ Callback error: {e}")

    async def _process_heartbeat(self):
        """Process heartbeat efficiently."""
        # Minimal heartbeat processing for HFT
        pass

    def get_latest_price(self, instrument: str) -> Optional[Dict]:
        """Get latest price from buffer with zero-copy access."""
        if instrument in self.price_buffers and self.price_buffers[instrument]:
            return self.price_buffers[instrument][-1]
        return None

    def get_streaming_stats(self) -> Dict:
        """Get streaming performance statistics."""
        if self.stats['start_time']:
            runtime = time.perf_counter() - self.stats['start_time']
            return {
                'runtime_seconds': runtime,
                'messages_received': self.stats['messages_received'],
                'messages_per_second': self.stats['messages_received'] / runtime if runtime > 0 else 0,
                'callbacks_executed': self.stats['callbacks_executed'],
                'instruments_tracked': len(self.price_buffers),
                'buffer_utilization': {
                    inst: len(buf) / self.buffer_size
                    for inst, buf in self.price_buffers.items()
                }
            }
        return {}

    def stop_streaming(self):
        """Stop streaming gracefully."""
        self.streaming_active = False

# High-frequency callback implementation
async def hft_price_callback(price: ClientPrice):
    """Ultra-fast price processing callback."""

    # Minimal processing for maximum speed
    bid = float(price.bids[0].price) if price.bids else 0
    ask = float(price.asks[0].price) if price.asks else 0
    spread = ask - bid

    # Only log significant moves (reduce I/O)
    if spread > 0.0010:  # 1 pip threshold
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
        streamer.start_optimized_streaming(account_id, major_pairs)
    )

    # Monitor performance
    await asyncio.sleep(30)  # Stream for 30 seconds
    stats = streamer.get_streaming_stats()
    print(f"📊 Streaming stats: {stats}")

    streamer.stop_streaming()
    await streaming_task
```

---

## Memory and CPU Optimization

### Efficient Data Structures

Use optimized data structures for HFT:

```python
import numpy as np
from collections import defaultdict
from dataclasses import dataclass
from typing import NamedTuple
import array

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

    def __init__(self, size: int):
        self.size = size
        self.data = np.empty((size, 3), dtype=np.float64)  # bid, ask, timestamp
        self.index = 0
        self.count = 0

    def append(self, bid: float, ask: float, timestamp: float):
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

    def get_history(self, n: int = None) -> np.ndarray:
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

    def __init__(self, buffer_size: int = 1000):
        self.buffers: Dict[str, CircularBuffer] = {}
        self.buffer_size = buffer_size
        self.update_counts = defaultdict(int)
        self.last_update_times = {}

    def update_price(self, instrument: str, bid: float, ask: float, timestamp: float):
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

async def optimized_price_callback(price: ClientPrice):
    """Optimized callback using efficient data structures."""

    bid = float(price.bids[0].price) if price.bids else 0
    ask = float(price.asks[0].price) if price.asks else 0
    timestamp = time.perf_counter()

    # Ultra-fast update
    price_manager.update_price(price.instrument, bid, ask, timestamp)

    # Fast analysis
    current = price_manager.get_current_price(price.instrument)
    if current and current.spread < 0.0005:  # Tight spread opportunity
        print(f"🎯 Tight spread: {price.instrument} {current.spread:.5f}")
```

---

## Latency Optimization

### Low-Latency Order Execution

Minimize order execution latency:

```python
class LowLatencyOrderManager:
    """Optimized order execution for HFT."""

    def __init__(self, client: AsyncClient):
        self.client = client
        self.order_queue = asyncio.Queue(maxsize=1000)
        self.execution_stats = {
            'orders_submitted': 0,
            'orders_filled': 0,
            'average_latency': 0,
            'latency_samples': deque(maxlen=1000)
        }

    async def submit_ultra_fast_order(self, account_id: str, instrument: str,
                                    units: int, max_latency_ms: float = 100) -> bool:
        """Submit order with latency monitoring."""

        start_time = time.perf_counter()

        try:
            # Pre-validate order parameters for speed
            if abs(units) < 1000:  # Minimum size check
                return False

            # Use timeout to prevent hanging
            response = await asyncio.wait_for(
                self.client.orders.post_market_order(
                    account_id=account_id,
                    instrument=instrument,
                    units=units,
                    time_in_force="FOK"  # Fill or Kill for HFT
                ),
                timeout=max_latency_ms / 1000  # Convert to seconds
            )

            end_time = time.perf_counter()
            latency_ms = (end_time - start_time) * 1000

            # Update statistics
            self.execution_stats['orders_submitted'] += 1
            self.execution_stats['latency_samples'].append(latency_ms)

            if response.order_fill_transaction:
                self.execution_stats['orders_filled'] += 1
                fill_price = response.order_fill_transaction.price

                print(f"⚡ Order filled: {instrument} @ {fill_price} ({latency_ms:.1f}ms)")
                return True
            else:
                print(f"❌ Order rejected: {instrument} ({latency_ms:.1f}ms)")
                return False

        except asyncio.TimeoutError:
            print(f"⏰ Order timeout: {instrument} (>{max_latency_ms}ms)")
            return False
        except Exception as e:
            print(f"❌ Order error: {e}")
            return False

    async def batch_submit_orders(self, account_id: str, orders: List[Dict],
                                max_batch_time_ms: float = 200) -> List[bool]:
        """Submit multiple orders with batch timeout."""

        start_time = time.perf_counter()

        # Create tasks for concurrent execution
        tasks = [
            self.submit_ultra_fast_order(
                account_id,
                order['instrument'],
                order['units'],
                max_latency_ms=50  # Tighter individual timeout in batch
            )
            for order in orders
        ]

        try:
            # Execute with batch timeout
            results = await asyncio.wait_for(
                asyncio.gather(*tasks),
                timeout=max_batch_time_ms / 1000
            )

            end_time = time.perf_counter()
            batch_time = (end_time - start_time) * 1000

            successful = sum(results)
            print(f"⚡ Batch complete: {successful}/{len(orders)} filled ({batch_time:.1f}ms)")

            return results

        except asyncio.TimeoutError:
            print(f"⏰ Batch timeout: {max_batch_time_ms}ms exceeded")
            return [False] * len(orders)

    def get_execution_stats(self) -> Dict:
        """Get execution performance statistics."""

        if self.execution_stats['latency_samples']:
            latencies = list(self.execution_stats['latency_samples'])
            avg_latency = sum(latencies) / len(latencies)
            min_latency = min(latencies)
            max_latency = max(latencies)
            p95_latency = np.percentile(latencies, 95)
        else:
            avg_latency = min_latency = max_latency = p95_latency = 0

        return {
            'orders_submitted': self.execution_stats['orders_submitted'],
            'orders_filled': self.execution_stats['orders_filled'],
            'fill_rate': (
                self.execution_stats['orders_filled'] /
                max(self.execution_stats['orders_submitted'], 1)
            ),
            'avg_latency_ms': avg_latency,
            'min_latency_ms': min_latency,
            'max_latency_ms': max_latency,
            'p95_latency_ms': p95_latency
        }

# Usage example
async def hft_execution_example(client: AsyncClient, account_id: str):
    order_manager = LowLatencyOrderManager(client)

    # Single ultra-fast order
    success = await order_manager.submit_ultra_fast_order(
        account_id, "EUR_USD", 25000, max_latency_ms=75
    )

    # Batch orders
    batch_orders = [
        {'instrument': 'EUR_USD', 'units': 10000},
        {'instrument': 'GBP_USD', 'units': -15000},
        {'instrument': 'USD_JPY', 'units': 20000}
    ]

    results = await order_manager.batch_submit_orders(
        account_id, batch_orders, max_batch_time_ms=150
    )

    # Performance analysis
    stats = order_manager.get_execution_stats()
    print(f"📊 Execution Stats: {stats}")
```

---

## System Resource Optimization

### Memory Pool Management

Efficient memory usage for HFT applications:

```python
from decimal import Decimal
from collections import deque
import gc
from typing import Any, Dict, List
import psutil
import os

class HFTResourceManager:
    """Manage system resources for optimal HFT performance."""

    def __init__(self):
        self.process = psutil.Process(os.getpid())
        self.baseline_memory = self.process.memory_info().rss / 1024 / 1024  # MB
        self.gc_threshold = 100  # MB increase before GC

    def optimize_python_runtime(self):
        """Optimize Python runtime for HFT."""

        # Disable automatic garbage collection for consistent timing
        gc.disable()
        print("🔧 Disabled automatic garbage collection")

        # Set GC thresholds for manual control
        gc.set_threshold(700, 10, 10)

        # Pre-allocate common objects to reduce allocation overhead
        self.pre_allocated_decimals = [Decimal(str(i/10000)) for i in range(-50000, 50001)]
        print("🔧 Pre-allocated decimal pool")

    def manual_gc_if_needed(self):
        """Perform garbage collection only when necessary."""

        current_memory = self.process.memory_info().rss / 1024 / 1024
        memory_increase = current_memory - self.baseline_memory

        if memory_increase > self.gc_threshold:
            collected = gc.collect()
            new_memory = self.process.memory_info().rss / 1024 / 1024

            print(f"🧹 GC: {collected} objects, {current_memory:.1f}→{new_memory:.1f}MB")
            self.baseline_memory = new_memory

    def get_resource_usage(self) -> Dict[str, float]:
        """Monitor system resource usage."""

        cpu_percent = self.process.cpu_percent()
        memory_info = self.process.memory_info()
        memory_mb = memory_info.rss / 1024 / 1024

        return {
            'cpu_percent': cpu_percent,
            'memory_mb': memory_mb,
            'memory_increase_mb': memory_mb - self.baseline_memory,
            'threads': self.process.num_threads(),
            'file_descriptors': self.process.num_fds() if hasattr(self.process, 'num_fds') else 0
        }

    def set_process_priority(self, priority: str = 'high'):
        """Set process priority for better performance."""

        try:
            if priority == 'high':
                if os.name == 'nt':  # Windows
                    self.process.nice(psutil.HIGH_PRIORITY_CLASS)
                else:  # Unix-like
                    self.process.nice(-10)
                print("🚀 Set HIGH process priority")
            elif priority == 'realtime':
                if os.name == 'nt':
                    self.process.nice(psutil.REALTIME_PRIORITY_CLASS)
                else:
                    self.process.nice(-20)
                print("🚀 Set REALTIME process priority")
        except Exception as e:
            print(f"⚠️ Could not set priority: {e}")

# Pre-allocation for common trading operations
class TradingObjectPool:
    """Object pool for common trading objects to reduce allocations."""

    def __init__(self, pool_size: int = 1000):
        self.pool_size = pool_size
        self.price_objects = deque(maxlen=pool_size)
        self.order_objects = deque(maxlen=pool_size)

        # Pre-populate pools
        for _ in range(pool_size):
            self.price_objects.append({'bid': 0.0, 'ask': 0.0, 'timestamp': 0.0, 'instrument': ''})
            self.order_objects.append({'instrument': '', 'units': 0, 'price': 0.0})

    def get_price_object(self) -> Dict[str, Any]:
        """Get pre-allocated price object."""
        if self.price_objects:
            return self.price_objects.popleft()
        return {'bid': 0.0, 'ask': 0.0, 'timestamp': 0.0, 'instrument': ''}

    def return_price_object(self, obj: Dict[str, Any]):
        """Return object to pool."""
        # Clear object data
        obj.clear()
        obj.update({'bid': 0.0, 'ask': 0.0, 'timestamp': 0.0, 'instrument': ''})

        if len(self.price_objects) < self.pool_size:
            self.price_objects.append(obj)

# Usage
resource_manager = HFTResourceManager()
object_pool = TradingObjectPool(pool_size=5000)

async def optimized_hft_setup():
    """Setup optimized HFT environment."""

    # System optimization
    resource_manager.optimize_python_runtime()
    resource_manager.set_process_priority('high')

    # Monitor resources
    resources = resource_manager.get_resource_usage()
    print(f"📊 Initial resources: {resources}")

    return resource_manager, object_pool
```

---

## Network Optimization

### Connection Quality Monitoring

Monitor and optimize network performance:

```python
import ping3
import statistics
from typing import List

class NetworkOptimizer:
    """Monitor and optimize network connectivity for HFT."""

    def __init__(self, oanda_endpoints: List[str] = None):
        self.endpoints = oanda_endpoints or [
            "api-fxpractice.oanda.com",
            "api-fxtrade.oanda.com",
            "stream-fxpractice.oanda.com"
        ]
        self.latency_history = defaultdict(deque)

    async def measure_network_latency(self) -> Dict[str, float]:
        """Measure latency to OANDA endpoints."""

        latencies = {}

        for endpoint in self.endpoints:
            try:
                # Measure ping latency
                ping_times = []
                for _ in range(5):  # 5 pings for average
                    ping_time = ping3.ping(endpoint, timeout=1)
                    if ping_time is not None:
                        ping_times.append(ping_time * 1000)  # Convert to ms

                if ping_times:
                    avg_latency = statistics.mean(ping_times)
                    latencies[endpoint] = avg_latency

                    # Store history
                    self.latency_history[endpoint].append(avg_latency)
                    if len(self.latency_history[endpoint]) > 100:
                        self.latency_history[endpoint].popleft()
                else:
                    latencies[endpoint] = float('inf')  # Unreachable

            except Exception as e:
                print(f"⚠️ Cannot ping {endpoint}: {e}")
                latencies[endpoint] = float('inf')

        return latencies

    def analyze_network_stability(self) -> Dict[str, Dict]:
        """Analyze network stability over time."""

        analysis = {}

        for endpoint, history in self.latency_history.items():
            if len(history) >= 10:
                latencies = list(history)
                analysis[endpoint] = {
                    'avg_latency_ms': statistics.mean(latencies),
                    'min_latency_ms': min(latencies),
                    'max_latency_ms': max(latencies),
                    'std_dev_ms': statistics.stdev(latencies),
                    'stability_score': 1.0 / (1.0 + statistics.stdev(latencies)),
                    'sample_count': len(latencies)
                }
            else:
                analysis[endpoint] = {'insufficient_data': True}

        return analysis

    async def optimize_connection_settings(self, client: AsyncClient):
        """Recommend optimal connection settings based on network analysis."""

        latencies = await self.measure_network_latency()
        min_latency = min(latencies.values())

        recommendations = {
            'timeout_ms': max(min_latency * 5, 100),  # 5x min latency or 100ms minimum
            'keepalive_enabled': True,
            'connection_pool_size': 20 if min_latency < 50 else 10,
            'retry_attempts': 2 if min_latency < 100 else 1
        }

        print(f"🌐 Network Analysis:")
        for endpoint, latency in latencies.items():
            status = "🟢" if latency < 50 else "🟡" if latency < 100 else "🔴"
            print(f"   {status} {endpoint}: {latency:.1f}ms")

        print(f"💡 Recommended settings: {recommendations}")
        return recommendations

# Usage
async def network_optimization_example():
    network_optimizer = NetworkOptimizer()

    # Measure initial network quality
    latencies = await network_optimizer.measure_network_latency()

    # Monitor over time (in background)
    for _ in range(10):  # 10 measurements over time
        await asyncio.sleep(30)  # 30-second intervals
        await network_optimizer.measure_network_latency()

    # Analyze and optimize
    stability = network_optimizer.analyze_network_stability()
    print(f"📊 Network stability: {stability}")

    return network_optimizer
```

---

## Performance Monitoring and Alerting

### Real-Time Performance Dashboard

Monitor HFT system performance:

```python
import logging
from datetime import datetime, timedelta

class HFTPerformanceMonitor:
    """Comprehensive performance monitoring for HFT systems."""

    def __init__(self, alert_thresholds: Dict[str, float] = None):
        self.thresholds = alert_thresholds or {
            'max_latency_ms': 100,
            'min_fill_rate': 0.95,
            'max_memory_mb': 1000,
            'max_cpu_percent': 80,
            'min_messages_per_sec': 50
        }

        self.metrics = {
            'order_latencies': deque(maxlen=1000),
            'fill_rates': deque(maxlen=100),
            'stream_rates': deque(maxlen=100),
            'system_resources': deque(maxlen=100),
            'alerts': []
        }

        self.start_time = time.perf_counter()

    def record_order_latency(self, latency_ms: float):
        """Record order execution latency."""
        self.metrics['order_latencies'].append({
            'latency_ms': latency_ms,
            'timestamp': time.perf_counter()
        })

        # Check for alerts
        if latency_ms > self.thresholds['max_latency_ms']:
            self._trigger_alert('HIGH_LATENCY', f"Order latency: {latency_ms:.1f}ms")

    def record_fill_rate(self, filled: int, submitted: int):
        """Record order fill rate."""
        fill_rate = filled / max(submitted, 1)
        self.metrics['fill_rates'].append({
            'fill_rate': fill_rate,
            'timestamp': time.perf_counter()
        })

        if fill_rate < self.thresholds['min_fill_rate']:
            self._trigger_alert('LOW_FILL_RATE', f"Fill rate: {fill_rate:.2%}")

    def record_streaming_rate(self, messages_per_second: float):
        """Record streaming message rate."""
        self.metrics['stream_rates'].append({
            'rate': messages_per_second,
            'timestamp': time.perf_counter()
        })

        if messages_per_second < self.thresholds['min_messages_per_sec']:
            self._trigger_alert('LOW_STREAM_RATE', f"Stream rate: {messages_per_second:.1f}/sec")

    def record_system_resources(self, cpu_percent: float, memory_mb: float):
        """Record system resource usage."""
        self.metrics['system_resources'].append({
            'cpu_percent': cpu_percent,
            'memory_mb': memory_mb,
            'timestamp': time.perf_counter()
        })

        if memory_mb > self.thresholds['max_memory_mb']:
            self._trigger_alert('HIGH_MEMORY', f"Memory usage: {memory_mb:.1f}MB")

        if cpu_percent > self.thresholds['max_cpu_percent']:
            self._trigger_alert('HIGH_CPU', f"CPU usage: {cpu_percent:.1f}%")

    def _trigger_alert(self, alert_type: str, message: str):
        """Trigger performance alert."""
        alert = {
            'type': alert_type,
            'message': message,
            'timestamp': time.perf_counter(),
            'datetime': datetime.now().isoformat()
        }

        self.metrics['alerts'].append(alert)
        print(f"🚨 ALERT [{alert_type}]: {message}")

        # Keep only recent alerts
        cutoff_time = time.perf_counter() - 300  # 5 minutes
        self.metrics['alerts'] = [
            a for a in self.metrics['alerts']
            if a['timestamp'] > cutoff_time
        ]

    def get_performance_summary(self) -> Dict:
        """Get comprehensive performance summary."""

        current_time = time.perf_counter()
        uptime = current_time - self.start_time

        summary = {
            'uptime_seconds': uptime,
            'alerts_count': len(self.metrics['alerts']),
            'recent_alerts': self.metrics['alerts'][-5:] if self.metrics['alerts'] else []
        }

        # Order latency statistics
        if self.metrics['order_latencies']:
            latencies = [m['latency_ms'] for m in self.metrics['order_latencies']]
            summary['order_latency'] = {
                'avg_ms': statistics.mean(latencies),
                'min_ms': min(latencies),
                'max_ms': max(latencies),
                'p95_ms': np.percentile(latencies, 95),
                'p99_ms': np.percentile(latencies, 99),
                'sample_count': len(latencies)
            }

        # Fill rate statistics
        if self.metrics['fill_rates']:
            rates = [m['fill_rate'] for m in self.metrics['fill_rates']]
            summary['fill_rate'] = {
                'avg': statistics.mean(rates),
                'min': min(rates),
                'recent': rates[-1] if rates else 0,
                'sample_count': len(rates)
            }

        # Streaming rate statistics
        if self.metrics['stream_rates']:
            rates = [m['rate'] for m in self.metrics['stream_rates']]
            summary['streaming_rate'] = {
                'avg_per_sec': statistics.mean(rates),
                'current_per_sec': rates[-1] if rates else 0,
                'sample_count': len(rates)
            }

        # System resources
        if self.metrics['system_resources']:
            recent_resources = self.metrics['system_resources'][-1]
            summary['system_resources'] = recent_resources

        return summary

    def export_metrics(self, filepath: str):
        """Export metrics to file for analysis."""

        summary = self.get_performance_summary()

        with open(filepath, 'w') as f:
            f.write(f"HFT Performance Report - {datetime.now().isoformat()}\n")
            f.write("=" * 50 + "\n\n")

            for section, data in summary.items():
                f.write(f"{section.upper()}:\n")
                if isinstance(data, dict):
                    for key, value in data.items():
                        f.write(f"  {key}: {value}\n")
                else:
                    f.write(f"  {data}\n")
                f.write("\n")

        print(f"📊 Metrics exported to {filepath}")

# Usage example
async def hft_monitoring_example():
    monitor = HFTPerformanceMonitor()

    # Simulate HFT operations with monitoring
    for i in range(100):
        # Simulate order execution
        latency = np.random.normal(75, 25)  # Average 75ms, std 25ms
        monitor.record_order_latency(latency)

        # Simulate fill rates
        filled = np.random.binomial(10, 0.97)  # 97% fill rate
        monitor.record_fill_rate(filled, 10)

        # Simulate streaming
        stream_rate = np.random.normal(100, 20)  # 100 msg/sec average
        monitor.record_streaming_rate(stream_rate)

        # System resources
        cpu = np.random.normal(60, 15)
        memory = np.random.normal(500, 100)
        monitor.record_system_resources(cpu, memory)

        await asyncio.sleep(0.1)  # Simulate time passage

    # Generate performance report
    summary = monitor.get_performance_summary()
    print(f"📊 Performance Summary: {summary}")

    # Export detailed metrics
    monitor.export_metrics("hft_performance_report.txt")

    return monitor
```

---

## Complete HFT System Integration

### Production-Ready HFT Framework

Integrate all optimizations into a complete system:

```python
from fivetwenty import AsyncClient, Environment

class ProductionHFTSystem:
    """Complete high-frequency trading system with all optimizations."""

    def __init__(self, token: str, environment: Environment, config: Dict = None):
        self.config = config or self._default_config()
        self.token = token
        self.environment = environment

        # Initialize components
        self.resource_manager = HFTResourceManager()
        self.network_optimizer = NetworkOptimizer()
        self.performance_monitor = HFTPerformanceMonitor(self.config['alert_thresholds'])
        self.price_manager = OptimizedPriceManager(self.config['buffer_size'])
        self.object_pool = TradingObjectPool(self.config['pool_size'])

        # Trading components
        self.client: Optional[AsyncClient] = None
        self.order_manager: Optional[LowLatencyOrderManager] = None
        self.streamer: Optional[HighPerformanceStreamer] = None

        # System state
        self.running = False
        self.performance_task = None
        self.streaming_task = None

    def _default_config(self) -> Dict:
        """Default configuration for HFT system."""
        return {
            'buffer_size': 10000,
            'pool_size': 5000,
            'max_connections': 25,
            'timeout_ms': 50,
            'batch_size': 20,
            'performance_check_interval': 10,  # seconds
            'alert_thresholds': {
                'max_latency_ms': 75,
                'min_fill_rate': 0.95,
                'max_memory_mb': 2000,
                'max_cpu_percent': 85,
                'min_messages_per_sec': 75
            }
        }

    async def initialize(self):
        """Initialize the complete HFT system."""

        print("🚀 Initializing Production HFT System...")

        # System optimization
        self.resource_manager.optimize_python_runtime()
        self.resource_manager.set_process_priority('high')

        # Network optimization
        await self.network_optimizer.measure_network_latency()

        # Initialize client
        self.client = AsyncClient(
            token=self.token,
            environment=self.environment,
            timeout=self.config['timeout_ms'] / 1000,
            limits_max_connections=self.config['max_connections'],
            limits_max_keepalive_connections=self.config['max_connections']
        )
        await self.client.__aenter__()

        # Initialize trading components
        self.order_manager = LowLatencyOrderManager(self.client)
        self.streamer = HighPerformanceStreamer(self.client, self.config['buffer_size'])

        print("✅ HFT System initialized successfully")

    async def start_trading(self, account_id: str, instruments: List[str]):
        """Start high-frequency trading operations."""

        if not self.client:
            await self.initialize()

        self.running = True
        print(f"📈 Starting HFT operations for {len(instruments)} instruments")

        # Start performance monitoring
        self.performance_task = asyncio.create_task(
            self._performance_monitoring_loop()
        )

        # Start price streaming
        self.streaming_task = asyncio.create_task(
            self._start_optimized_streaming(account_id, instruments)
        )

        # Wait for tasks
        try:
            await asyncio.gather(
                self.performance_task,
                self.streaming_task,
                return_exceptions=True
            )
        except Exception as e:
            print(f"❌ Trading error: {e}")
        finally:
            self.running = False

    async def _performance_monitoring_loop(self):
        """Background performance monitoring."""

        while self.running:
            try:
                # Collect system metrics
                resources = self.resource_manager.get_resource_usage()
                self.performance_monitor.record_system_resources(
                    resources['cpu_percent'],
                    resources['memory_mb']
                )

                # Manual GC if needed
                self.resource_manager.manual_gc_if_needed()

                # Order manager stats
                if self.order_manager:
                    stats = self.order_manager.get_execution_stats()
                    if stats['orders_submitted'] > 0:
                        self.performance_monitor.record_fill_rate(
                            stats['orders_filled'],
                            stats['orders_submitted']
                        )

                # Streaming stats
                if self.streamer:
                    stream_stats = self.streamer.get_streaming_stats()
                    if 'messages_per_second' in stream_stats:
                        self.performance_monitor.record_streaming_rate(
                            stream_stats['messages_per_second']
                        )

                await asyncio.sleep(self.config['performance_check_interval'])

            except Exception as e:
                print(f"⚠️ Performance monitoring error: {e}")
                await asyncio.sleep(5)

    async def _start_optimized_streaming(self, account_id: str, instruments: List[str]):
        """Start optimized price streaming."""

        # Add callbacks for all instruments
        for instrument in instruments:
            self.streamer.add_price_callback(instrument, self._hft_price_callback)

        # Start streaming
        await self.streamer.start_optimized_streaming(account_id, instruments)

    async def _hft_price_callback(self, price: ClientPrice):
        """High-performance price processing callback."""

        try:
            # Ultra-fast price update
            bid = float(price.bids[0].price) if price.bids else 0
            ask = float(price.asks[0].price) if price.asks else 0
            timestamp = time.perf_counter()

            self.price_manager.update_price(price.instrument, bid, ask, timestamp)

            # Trading logic would go here
            await self._evaluate_trading_opportunity(price)

        except Exception as e:
            print(f"⚠️ Price callback error: {e}")

    async def _evaluate_trading_opportunity(self, price: ClientPrice):
        """Evaluate trading opportunities (placeholder for strategy logic)."""

        # This is where your HFT strategy logic would go
        # For demonstration, we'll just check for tight spreads

        if price.bids and price.asks:
            spread = float(price.asks[0].price) - float(price.bids[0].price)
            if spread < 0.0002:  # Very tight spread
                print(f"🎯 Opportunity: {price.instrument} spread {spread:.5f}")

    async def stop_trading(self):
        """Stop all trading operations."""

        print("🛑 Stopping HFT operations...")
        self.running = False

        # Stop streaming
        if self.streamer:
            self.streamer.stop_streaming()

        # Cancel tasks
        if self.performance_task:
            self.performance_task.cancel()
        if self.streaming_task:
            self.streaming_task.cancel()

        # Generate final report
        summary = self.performance_monitor.get_performance_summary()
        print(f"📊 Final Performance Summary:")
        for key, value in summary.items():
            print(f"   {key}: {value}")

        # Cleanup
        if self.client:
            await self.client.__aexit__(None, None, None)

        print("✅ HFT system stopped")

# Complete usage example
async def run_production_hft_system():
    """Run the complete HFT system."""

    hft_system = ProductionHFTSystem(
        token="your-token",
        environment=Environment.PRACTICE,
        config={
            'buffer_size': 15000,
            'max_connections': 30,
            'timeout_ms': 40,
            'performance_check_interval': 5
        }
    )

    try:
        await hft_system.initialize()

        # Start trading major pairs
        major_pairs = ["EUR_USD", "GBP_USD", "USD_JPY", "USD_CHF", "AUD_USD"]

        # Run for 10 minutes
        trading_task = asyncio.create_task(
            hft_system.start_trading("101-001-1234567-001", major_pairs)
        )

        await asyncio.sleep(600)  # 10 minutes
        await hft_system.stop_trading()

    except KeyboardInterrupt:
        print("\n⚠️ Interrupted by user")
        await hft_system.stop_trading()
    except Exception as e:
        print(f"❌ System error: {e}")
        await hft_system.stop_trading()

# To run the complete HFT system:
# asyncio.run(run_production_hft_system())
```

**Task Complete**: High-frequency trading optimization guide provides comprehensive performance techniques for minimal latency and maximum throughput with FiveTwenty.