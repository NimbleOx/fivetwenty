# Latency Optimization

**Problem**: You need to minimize order execution latency for competitive advantage in high-frequency trading.

**Solution**: Implement low-latency order management with ultra-fast execution techniques, timeout optimization, and performance monitoring.

---

## Low-Latency Order Execution

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

## Timeout Optimization

Configure timeouts for optimal latency:

```python
class AdaptiveTimeoutManager:
    """Dynamically adjust timeouts based on network conditions."""

    def __init__(self):
        self.network_latencies = deque(maxlen=100)
        self.success_rates = deque(maxlen=50)
        self.current_timeout = 100  # Start with 100ms

    def record_network_latency(self, latency_ms: float):
        """Record network latency measurement."""
        self.network_latencies.append(latency_ms)

    def record_order_result(self, success: bool, latency_ms: float):
        """Record order execution result."""
        self.success_rates.append(success)
        self.record_network_latency(latency_ms)

    def get_optimal_timeout(self) -> float:
        """Calculate optimal timeout based on recent performance."""

        if len(self.network_latencies) < 10:
            return self.current_timeout

        # Calculate statistics
        avg_latency = sum(self.network_latencies) / len(self.network_latencies)
        p95_latency = np.percentile(list(self.network_latencies), 95)
        success_rate = sum(self.success_rates) / len(self.success_rates) if self.success_rates else 0

        # Adjust timeout based on performance
        if success_rate > 0.95:
            # High success rate - can be more aggressive
            optimal_timeout = min(avg_latency * 2, p95_latency * 1.2)
        elif success_rate > 0.85:
            # Moderate success rate - be conservative
            optimal_timeout = p95_latency * 1.5
        else:
            # Low success rate - increase timeout
            optimal_timeout = p95_latency * 2

        # Smooth transition
        self.current_timeout = (self.current_timeout * 0.7) + (optimal_timeout * 0.3)

        return max(25, min(self.current_timeout, 500))  # Clamp between 25-500ms

# Usage with order manager
class AdaptiveLowLatencyOrderManager(LowLatencyOrderManager):
    """Order manager with adaptive timeout optimization."""

    def __init__(self, client: AsyncClient):
        super().__init__(client)
        self.timeout_manager = AdaptiveTimeoutManager()

    async def submit_adaptive_order(self, account_id: str, instrument: str, units: int) -> bool:
        """Submit order with adaptive timeout."""

        optimal_timeout = self.timeout_manager.get_optimal_timeout()

        success = await self.submit_ultra_fast_order(
            account_id, instrument, units, max_latency_ms=optimal_timeout
        )

        # Record result for adaptive learning
        if self.execution_stats['latency_samples']:
            last_latency = self.execution_stats['latency_samples'][-1]
            self.timeout_manager.record_order_result(success, last_latency)

        return success
```

---

## Pre-Trade Validation

Optimize pre-trade checks for speed:

```python
class FastPreTradeValidator:
    """Ultra-fast pre-trade validation."""

    def __init__(self, client: AsyncClient):
        self.client = client
        self.account_cache = {}
        self.instrument_cache = {}
        self.cache_expiry = 30  # seconds

    async def validate_order_fast(self, account_id: str, instrument: str,
                                units: int) -> tuple[bool, str]:
        """Fast order validation with caching."""

        current_time = time.time()

        # Check account details (cached)
        account_valid, account_msg = await self._validate_account_cached(
            account_id, current_time
        )
        if not account_valid:
            return False, account_msg

        # Check instrument validity (cached)
        instrument_valid, instrument_msg = await self._validate_instrument_cached(
            instrument, current_time
        )
        if not instrument_valid:
            return False, instrument_msg

        # Quick units validation
        if abs(units) < 1:
            return False, "Units too small"

        if abs(units) > 10000000:  # 10M units max
            return False, "Units too large"

        return True, "Valid"

    async def _validate_account_cached(self, account_id: str,
                                     current_time: float) -> tuple[bool, str]:
        """Validate account with caching."""

        cache_key = f"account_{account_id}"

        # Check cache first
        if cache_key in self.account_cache:
            cache_entry = self.account_cache[cache_key]
            if current_time - cache_entry['timestamp'] < self.cache_expiry:
                return cache_entry['valid'], cache_entry['message']

        # Fetch account details
        try:
            account = await asyncio.wait_for(
                self.client.accounts.get(account_id),
                timeout=0.5  # 500ms timeout
            )

            # Cache result
            self.account_cache[cache_key] = {
                'valid': True,
                'message': "Valid account",
                'timestamp': current_time,
                'balance': float(account.balance)
            }

            return True, "Valid account"

        except Exception as e:
            # Cache negative result for shorter time
            self.account_cache[cache_key] = {
                'valid': False,
                'message': f"Account error: {e}",
                'timestamp': current_time
            }

            return False, f"Account error: {e}"

    async def _validate_instrument_cached(self, instrument: str,
                                        current_time: float) -> tuple[bool, str]:
        """Validate instrument with caching."""

        # Simple instrument format validation (very fast)
        if '_' not in instrument or len(instrument) != 7:
            return False, "Invalid instrument format"

        # Cache validation (instruments don't change often)
        cache_key = f"instrument_{instrument}"

        if cache_key in self.instrument_cache:
            cache_entry = self.instrument_cache[cache_key]
            if current_time - cache_entry['timestamp'] < self.cache_expiry * 10:  # Longer cache
                return cache_entry['valid'], cache_entry['message']

        # For HFT, assume major pairs are valid to avoid API calls
        major_pairs = {
            'EUR_USD', 'GBP_USD', 'USD_JPY', 'USD_CHF', 'AUD_USD', 'USD_CAD',
            'NZD_USD', 'EUR_GBP', 'EUR_JPY', 'GBP_JPY', 'CHF_JPY', 'AUD_JPY'
        }

        is_valid = instrument in major_pairs

        # Cache result
        self.instrument_cache[cache_key] = {
            'valid': is_valid,
            'message': "Valid instrument" if is_valid else "Unknown instrument",
            'timestamp': current_time
        }

        return is_valid, "Valid instrument" if is_valid else "Unknown instrument"

# Usage
async def fast_order_execution_example(client: AsyncClient, account_id: str):
    """Example of fast order execution with validation."""

    validator = FastPreTradeValidator(client)
    order_manager = LowLatencyOrderManager(client)

    # Fast validation + execution
    start_time = time.perf_counter()

    # Validate quickly
    valid, message = await validator.validate_order_fast(
        account_id, "EUR_USD", 10000
    )

    if valid:
        # Execute immediately
        success = await order_manager.submit_ultra_fast_order(
            account_id, "EUR_USD", 10000, max_latency_ms=75
        )

        end_time = time.perf_counter()
        total_time = (end_time - start_time) * 1000

        print(f"⚡ Total execution time: {total_time:.1f}ms")
        print(f"   Validation: {valid}, Order: {success}")

    else:
        print(f"❌ Validation failed: {message}")
```

---

## Order Queue Management

Implement efficient order queuing:

```python
import heapq
from dataclasses import dataclass, field
from typing import Any

@dataclass
class PriorityOrder:
    """Order with priority for queue management."""
    priority: int
    timestamp: float
    order_data: Dict[str, Any] = field(compare=False)

    def __lt__(self, other):
        # Higher priority orders first, then by timestamp
        if self.priority != other.priority:
            return self.priority > other.priority
        return self.timestamp < other.timestamp

class PriorityOrderQueue:
    """Priority queue for order execution."""

    def __init__(self, max_size: int = 1000):
        self.max_size = max_size
        self.queue = []
        self.queue_stats = {
            'orders_queued': 0,
            'orders_processed': 0,
            'queue_overflows': 0
        }

    def add_order(self, order_data: Dict, priority: int = 5) -> bool:
        """Add order to priority queue."""

        if len(self.queue) >= self.max_size:
            self.queue_stats['queue_overflows'] += 1
            return False

        priority_order = PriorityOrder(
            priority=priority,
            timestamp=time.perf_counter(),
            order_data=order_data
        )

        heapq.heappush(self.queue, priority_order)
        self.queue_stats['orders_queued'] += 1

        return True

    def get_next_order(self) -> Optional[Dict]:
        """Get highest priority order."""

        if not self.queue:
            return None

        priority_order = heapq.heappop(self.queue)
        self.queue_stats['orders_processed'] += 1

        return priority_order.order_data

    def get_queue_size(self) -> int:
        """Get current queue size."""
        return len(self.queue)

    def clear_old_orders(self, max_age_seconds: float = 5.0):
        """Remove orders that are too old."""

        current_time = time.perf_counter()
        cutoff_time = current_time - max_age_seconds

        # Rebuild queue without old orders
        old_queue = self.queue
        self.queue = []

        for priority_order in old_queue:
            if priority_order.timestamp > cutoff_time:
                heapq.heappush(self.queue, priority_order)

# Usage with order manager
class QueuedOrderManager(LowLatencyOrderManager):
    """Order manager with priority queuing."""

    def __init__(self, client: AsyncClient):
        super().__init__(client)
        self.order_queue = PriorityOrderQueue()
        self.processing_orders = False

    async def queue_order(self, account_id: str, instrument: str, units: int,
                         priority: int = 5) -> bool:
        """Queue order for execution."""

        order_data = {
            'account_id': account_id,
            'instrument': instrument,
            'units': units,
            'timestamp': time.perf_counter()
        }

        return self.order_queue.add_order(order_data, priority)

    async def process_order_queue(self):
        """Process queued orders in priority order."""

        if self.processing_orders:
            return

        self.processing_orders = True

        try:
            while True:
                # Clean old orders
                self.order_queue.clear_old_orders()

                # Get next order
                order_data = self.order_queue.get_next_order()
                if not order_data:
                    await asyncio.sleep(0.001)  # 1ms wait
                    continue

                # Execute order
                await self.submit_ultra_fast_order(
                    order_data['account_id'],
                    order_data['instrument'],
                    order_data['units']
                )

        finally:
            self.processing_orders = False

# Example usage
async def queued_execution_example(client: AsyncClient, account_id: str):
    """Example of queued order execution."""

    queued_manager = QueuedOrderManager(client)

    # Start queue processing
    queue_task = asyncio.create_task(queued_manager.process_order_queue())

    # Queue orders with different priorities
    await queued_manager.queue_order(account_id, "EUR_USD", 10000, priority=8)  # High priority
    await queued_manager.queue_order(account_id, "GBP_USD", 5000, priority=3)   # Low priority
    await queued_manager.queue_order(account_id, "USD_JPY", 15000, priority=9)  # Highest priority

    # Orders will be processed in priority order: USD_JPY, EUR_USD, GBP_USD

    await asyncio.sleep(5)  # Let orders process
    queue_task.cancel()
```

---

## Latency Monitoring

Monitor and analyze execution latency:

```python
class LatencyMonitor:
    """Monitor and analyze order execution latency."""

    def __init__(self):
        self.latency_data = {
            'order_latencies': deque(maxlen=1000),
            'network_latencies': deque(maxlen=1000),
            'processing_latencies': deque(maxlen=1000)
        }

    def record_order_latency(self, total_ms: float, network_ms: float, processing_ms: float):
        """Record comprehensive latency data."""

        self.latency_data['order_latencies'].append({
            'total_ms': total_ms,
            'timestamp': time.perf_counter()
        })

        self.latency_data['network_latencies'].append({
            'latency_ms': network_ms,
            'timestamp': time.perf_counter()
        })

        self.latency_data['processing_latencies'].append({
            'latency_ms': processing_ms,
            'timestamp': time.perf_counter()
        })

    def get_latency_analysis(self) -> Dict:
        """Analyze latency patterns."""

        if not self.latency_data['order_latencies']:
            return {'error': 'No latency data available'}

        # Order latency analysis
        order_latencies = [d['total_ms'] for d in self.latency_data['order_latencies']]
        network_latencies = [d['latency_ms'] for d in self.latency_data['network_latencies']]
        processing_latencies = [d['latency_ms'] for d in self.latency_data['processing_latencies']]

        return {
            'order_latency': {
                'avg_ms': np.mean(order_latencies),
                'min_ms': np.min(order_latencies),
                'max_ms': np.max(order_latencies),
                'p50_ms': np.percentile(order_latencies, 50),
                'p95_ms': np.percentile(order_latencies, 95),
                'p99_ms': np.percentile(order_latencies, 99),
                'std_ms': np.std(order_latencies)
            },
            'network_latency': {
                'avg_ms': np.mean(network_latencies),
                'p95_ms': np.percentile(network_latencies, 95)
            },
            'processing_latency': {
                'avg_ms': np.mean(processing_latencies),
                'p95_ms': np.percentile(processing_latencies, 95)
            },
            'sample_count': len(order_latencies)
        }

    def detect_latency_spikes(self, threshold_percentile: float = 95) -> List[Dict]:
        """Detect unusual latency spikes."""

        if len(self.latency_data['order_latencies']) < 50:
            return []

        latencies = [d['total_ms'] for d in self.latency_data['order_latencies']]
        threshold = np.percentile(latencies, threshold_percentile)

        spikes = []
        for data in self.latency_data['order_latencies']:
            if data['total_ms'] > threshold:
                spikes.append({
                    'latency_ms': data['total_ms'],
                    'timestamp': data['timestamp'],
                    'severity': 'high' if data['total_ms'] > threshold * 1.5 else 'medium'
                })

        return sorted(spikes, key=lambda x: x['latency_ms'], reverse=True)

# Integration example
latency_monitor = LatencyMonitor()

async def monitored_order_execution(client: AsyncClient, account_id: str,
                                  instrument: str, units: int):
    """Execute order with comprehensive latency monitoring."""

    total_start = time.perf_counter()

    # Simulate network latency measurement
    network_start = time.perf_counter()
    # Network operation would go here
    network_end = time.perf_counter()
    network_latency = (network_end - network_start) * 1000

    # Processing latency
    processing_start = time.perf_counter()
    # Order processing
    processing_end = time.perf_counter()
    processing_latency = (processing_end - processing_start) * 1000

    # Execute order
    order_manager = LowLatencyOrderManager(client)
    success = await order_manager.submit_ultra_fast_order(
        account_id, instrument, units
    )

    total_end = time.perf_counter()
    total_latency = (total_end - total_start) * 1000

    # Record latency data
    latency_monitor.record_order_latency(
        total_latency, network_latency, processing_latency
    )

    # Check for spikes
    spikes = latency_monitor.detect_latency_spikes()
    if spikes:
        print(f"⚠️ Latency spike detected: {spikes[0]['latency_ms']:.1f}ms")

    return success
```

---

## Next Steps

Continue to [System Resource Management](system-resource-management.md) for advanced resource optimization.

---

## Related Guides

- [Connection Optimization](connection-optimization.md) - Connection pooling strategies
- [Performance Monitoring](performance-monitoring.md) - Comprehensive monitoring
- [Production Integration](production-integration.md) - Complete system integration