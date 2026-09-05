# Latency Optimization

**Problem**: You need to minimize order execution latency for competitive advantage in high-frequency trading.

**Solution**: Implement low-latency order management with ultra-fast execution techniques, timeout optimization, and performance monitoring.

---

## Low-Latency Order Execution

Minimize order execution latency:

```python
import asyncio
import time
from collections import deque
from typing import List, Dict
from fivetwenty import AsyncClient

class LowLatencyOrderManager:
    """Ultra-fast order execution system optimized for high-frequency trading applications."""

    def __init__(self, client: AsyncClient) -> None:
        # Step 1: Store FiveTwenty client for authenticated API access
        # Reusing the same client ensures connection pooling and optimal performance
        self.client = client

        # Step 2: Initialize high-performance async queue for order management
        # Bounded queue prevents memory exhaustion during high-volume periods
        self.order_queue = asyncio.Queue(maxsize=1000)  # 1000 pending orders max
        # Queue size balances memory usage vs. order buffering capacity

        # Step 3: Initialize comprehensive execution statistics for performance monitoring
        # Real-time metrics are crucial for HFT system optimization and compliance
        self.execution_stats = {
            'orders_submitted': 0,          # Total orders attempted
            'orders_filled': 0,             # Successfully executed orders
            'average_latency': 0,           # Mean execution time
            'latency_samples': deque(maxlen=1000)  # Rolling window of latency measurements
        }
        # deque with maxlen provides O(1) operations and automatic oldest-data eviction
        # 1000 samples = ~16 minutes of data at 1 order/second, sufficient for analysis

    async def submit_ultra_fast_order(self, account_id: str, instrument: str,
                                    units: int, max_latency_ms: float = 100) -> bool:
        """Submit order with microsecond-precision latency monitoring and HFT optimizations."""

        # Step 4: Start high-precision timing for latency measurement
        # time.perf_counter() provides highest resolution timing available
        start_time = time.perf_counter()

        try:
            # Step 5: Perform lightning-fast pre-validation to avoid API round trips
            # Every microsecond matters in HFT - validate locally before network calls
            if abs(units) < 1000:  # Minimum size check (OANDA requirement)
                return False
            # Pre-validation prevents:
            # - Unnecessary network round trips for invalid orders
            # - API rate limit consumption on guaranteed failures
            # - Latency from server-side validation errors

            # Step 6: Execute order with aggressive timeout for HFT requirements
            # asyncio.wait_for prevents hanging operations that could miss market opportunities
            response = await asyncio.wait_for(
                self.client.orders.post_market_order(
                    account_id=account_id,
                    instrument=instrument,
                    units=units,
                    time_in_force="FOK"  # Fill or Kill - critical for HFT strategies
                ),
                timeout=max_latency_ms / 1000  # Convert milliseconds to seconds
            )
            # FOK (Fill or Kill) ensures:
            # - Immediate execution or rejection - no partial fills
            # - No lingering orders that could affect future strategies
            # - Predictable execution outcomes for algorithmic trading

            # Step 7: Calculate precise execution latency for performance analysis
            end_time = time.perf_counter()
            latency_ms = (end_time - start_time) * 1000  # Convert to milliseconds
            # Precision: ~nanoseconds on modern systems, critical for HFT analysis

            # Step 8: Update real-time execution statistics for monitoring
            # These metrics drive trading system optimization and risk management
            self.execution_stats['orders_submitted'] += 1
            self.execution_stats['latency_samples'].append(latency_ms)
            # Rolling window automatically evicts old samples for memory efficiency

            # Step 9: Process order execution result with detailed success analysis
            if response.order_fill_transaction:
                # Order successfully executed - record fill details
                self.execution_stats['orders_filled'] += 1
                fill_price = response.order_fill_transaction.price

                print(f"Order filled: {instrument} @ {fill_price} ({latency_ms:.1f}ms)")
                # Good: metrics enable:
                # - Fill rate analysis for strategy optimization
                # - Price execution quality measurement
                # - Latency performance monitoring
                return True
            else:
                # Order rejected - analyze rejection for strategy improvement
                print(f"Error: Order rejected: {instrument} ({latency_ms:.1f}ms)")
                # Rejection analysis helps identify:
                # - Market conditions causing rejections
                # - Timing issues in strategy execution
                # - Account or instrument limitations
                return False

        except asyncio.TimeoutError:
            # Step 10: Handle timeout errors - critical for HFT system reliability
            print(f"Order timeout: {instrument} (>{max_latency_ms}ms)")
            # Timeout handling prevents:
            # - System hanging during network issues
            # - Missing subsequent trading opportunities
            # - Resource exhaustion from blocked operations
            # Strategy: Log timeout, adjust parameters, continue trading
            return False

        except Exception as e:
            # Step 11: Handle unexpected errors with comprehensive logging
            print(f"Error: Order error: {e}")
            # Exception types that might occur:
            # - Network connectivity issues
            # - OANDA API errors (insufficient funds, market closed)
            # - Authentication failures
            # - Rate limiting responses
            # Robust error handling ensures system stability during volatile markets
            return False

    async def batch_submit_orders(self, account_id: str, orders: List[Dict],
                                max_batch_time_ms: float = 200) -> List[bool]:
        """Submit multiple orders concurrently with sophisticated batch optimization."""

        # Step 12: Start batch timing for comprehensive performance analysis
        start_time = time.perf_counter()

        # Step 13: Create concurrent tasks for parallel order execution
        # Parallel execution provides massive performance benefits for multi-instrument strategies
        tasks = [
            self.submit_ultra_fast_order(
                account_id,
                order['instrument'],
                order['units'],
                max_latency_ms=50  # Aggressive individual timeout for batch efficiency
            )
            for order in orders
        ]
        # Concurrent execution benefits:
        # - Total time = max(individual_times) instead of sum(individual_times)
        # - Better utilization of network bandwidth
        # - Reduced market impact through simultaneous execution
        # - Lower slippage in volatile market conditions

        try:
            # Step 14: Execute batch with comprehensive timeout management
            # Batch timeout prevents entire strategy from hanging on slow orders
            results = await asyncio.wait_for(
                asyncio.gather(*tasks),  # Parallel execution of all orders
                timeout=max_batch_time_ms / 1000  # Convert to seconds
            )

            # Step 15: Calculate batch performance metrics
            end_time = time.perf_counter()
            batch_time = (end_time - start_time) * 1000

            # Step 16: Analyze batch execution success rate
            successful = sum(results)  # Count successful executions
            print(f"Batch complete: {successful}/{len(orders)} filled ({batch_time:.1f}ms)")
            # Batch metrics enable:
            # - Strategy performance evaluation
            # - Market impact analysis
            # - Execution quality monitoring
            # - System optimization feedback

            return results

        except asyncio.TimeoutError:
            # Step 17: Handle batch timeout with graceful degradation
            print(f"Batch timeout: {max_batch_time_ms}ms exceeded")
            # Batch timeout scenarios:
            # - Network congestion affecting multiple requests
            # - OANDA API slowdown during high volatility
            # - Individual order processing delays
            # Response: Return all failures, log event, adjust future batch sizes
            return [False] * len(orders)

    def get_execution_stats(self) -> Dict:
        """Generate comprehensive execution performance statistics for HFT analysis."""

        # Step 18: Calculate detailed latency statistics if data is available
        if self.execution_stats['latency_samples']:
            # Convert deque to list for statistical calculations
            latencies = list(self.execution_stats['latency_samples'])

            # Calculate comprehensive latency metrics
            avg_latency = sum(latencies) / len(latencies)  # Mean execution time
            min_latency = min(latencies)                   # Best case performance
            max_latency = max(latencies)                   # Worst case performance
            p95_latency = np.percentile(latencies, 95)     # 95th percentile (excludes outliers)
            # p95 is critical for HFT - represents typical worst-case performance
        else:
            # No data available - return zero metrics
            avg_latency = min_latency = max_latency = p95_latency = 0

        # Step 19: Return comprehensive performance analysis
        return {
            # Volume metrics
            'orders_submitted': self.execution_stats['orders_submitted'],
            'orders_filled': self.execution_stats['orders_filled'],

            # Good: rate analysis - critical for strategy evaluation
            'fill_rate': (
                self.execution_stats['orders_filled'] /
                max(self.execution_stats['orders_submitted'], 1)  # Avoid division by zero
            ),

            # Latency performance metrics - core HFT measurements
            'avg_latency_ms': avg_latency,     # Overall performance indicator
            'min_latency_ms': min_latency,     # System capability lower bound
            'max_latency_ms': max_latency,     # Worst case scenario
            'p95_latency_ms': p95_latency      # Service level agreement metric
        }
        # These statistics enable:
        # - Performance benchmarking against competitors
        # - System optimization and bottleneck identification
        # - SLA compliance monitoring
        # - Strategy profitability analysis

# Step 20: Comprehensive usage example demonstrating HFT execution patterns
async def hft_execution_example(client: AsyncClient, account_id: str):
    """Demonstrate high-frequency trading execution with performance monitoring."""

    # Initialize low-latency order management system
    order_manager = LowLatencyOrderManager(client)

    # Step 21: Execute single ultra-fast order with aggressive timing
    # 75ms timeout ensures competitive execution speed
    success = await order_manager.submit_ultra_fast_order(
        account_id, "EUR_USD", 25000, max_latency_ms=75
    )
    print(f"Single order result: {success}")

    # Step 22: Demonstrate batch execution for multi-instrument strategies
    # Batch execution enables complex trading strategies with coordinated timing
    batch_orders = [
        {'instrument': 'EUR_USD', 'units': 10000},   # Long EUR position
        {'instrument': 'GBP_USD', 'units': -15000},  # Short GBP position (hedge)
        {'instrument': 'USD_JPY', 'units': 20000}    # Long USD/JPY position
    ]
    # Strategy: Currency basket rebalancing with risk hedging

    # Step 23: Execute coordinated batch with tight timing constraints
    results = await order_manager.batch_submit_orders(
        account_id, batch_orders, max_batch_time_ms=150
    )
    print(f"Batch results: {results}")
    # 150ms batch timeout ensures all orders execute within acceptable window

    # Step 24: Analyze comprehensive execution performance
    stats = order_manager.get_execution_stats()
    print(f"Execution Stats: {stats}")
    # Performance analysis enables:
    # - Strategy optimization decisions
    # - System performance monitoring
    # - Competitive benchmarking
    # - Regulatory compliance reporting
```

---

## Timeout Optimization

Configure timeouts for optimal latency:

```python
from collections import deque
import numpy as np
from typing import Any
from fivetwenty import AsyncClient

class AdaptiveTimeoutManager:
    """Intelligent timeout management system that learns from network performance."""

    def __init__(self) -> None:
        # Step 1: Initialize rolling windows for performance data collection
        # Separate tracking enables precise timeout optimization
        self.network_latencies = deque(maxlen=100)  # 100 recent latency measurements
        self.success_rates = deque(maxlen=50)       # 50 recent success/failure results
        self.current_timeout = 100                  # Start with conservative 100ms
        # Adaptive timeouts balance speed vs. reliability based on actual conditions

    def record_network_latency(self, latency_ms: float) -> Any:
        """Record network latency measurement for adaptive learning."""
        # Step 2: Store network latency data for statistical analysis
        self.network_latencies.append(latency_ms)
        # Rolling window automatically evicts old measurements
        # Keeps data relevant to current network conditions

    def record_order_result(self, success: bool, latency_ms: float) -> Any:
        """Record order execution result for success rate analysis."""
        # Step 3: Track both success rate and latency for comprehensive optimization
        self.success_rates.append(success)          # Boolean success/failure
        self.record_network_latency(latency_ms)     # Associated latency measurement
        # Correlation between success and latency informs timeout decisions

    def get_optimal_timeout(self) -> float:
        """Calculate optimal timeout using machine learning principles."""

        # Step 4: Ensure sufficient data for reliable statistics
        if len(self.network_latencies) < 10:
            return self.current_timeout  # Insufficient data - use current setting
        # Minimum sample size prevents decisions based on insufficient evidence

        # Step 5: Calculate comprehensive performance statistics
        avg_latency = sum(self.network_latencies) / len(self.network_latencies)
        p95_latency = np.percentile(list(self.network_latencies), 95)
        success_rate = sum(self.success_rates) / len(self.success_rates) if self.success_rates else 0
        # Statistics provide different perspectives:
        # - avg_latency: typical performance
        # - p95_latency: worst-case performance (excludes extreme outliers)
        # - success_rate: overall reliability

        # Step 6: Apply intelligent timeout adjustment based on performance patterns
        if success_rate > 0.95:
            # High success rate (>95%) - can be more aggressive for competitive advantage
            optimal_timeout = min(avg_latency * 2, p95_latency * 1.2)
            # Strategy: Use tighter timeouts to maximize speed
        elif success_rate > 0.85:
            # Moderate success rate (85-95%) - balance speed with reliability
            optimal_timeout = p95_latency * 1.5
            # Strategy: Conservative approach to maintain acceptable fill rates
        else:
            # Low success rate (<85%) - prioritize reliability over speed
            optimal_timeout = p95_latency * 2
            # Strategy: Increase timeouts to improve execution success

        # Step 7: Apply exponential smoothing for stable timeout transitions
        # Prevents rapid timeout oscillations that could destabilize trading
        self.current_timeout = (self.current_timeout * 0.7) + (optimal_timeout * 0.3)
        # 70% weight on current, 30% on new - provides stability with adaptation

        # Step 8: Enforce reasonable timeout bounds for HFT operations
        return max(25, min(self.current_timeout, 500))  # Clamp between 25-500ms
        # Bounds prevent:
        # - Excessively fast timeouts that guarantee failure
        # - Excessively slow timeouts that miss trading opportunities

# Step 9: Implement adaptive order manager that learns from execution history
class AdaptiveLowLatencyOrderManager(LowLatencyOrderManager):
    """Advanced order manager with machine learning-based timeout optimization."""

    def __init__(self, client: AsyncClient) -> None:
        # Step 10: Initialize base order manager with adaptive enhancements
        super().__init__(client)  # Inherit all low-latency capabilities
        self.timeout_manager = AdaptiveTimeoutManager()  # Add adaptive intelligence
        # Composition pattern: combines base functionality with adaptive learning

    async def submit_adaptive_order(self, account_id: str, instrument: str, units: int) -> bool:
        """Submit order with dynamically optimized timeout based on historical performance."""

        # Step 11: Calculate optimal timeout based on recent network performance
        optimal_timeout = self.timeout_manager.get_optimal_timeout()
        # Adaptive timeout considers:
        # - Recent network latency patterns
        # - Current success rate trends
        # - Historical performance data

        # Step 12: Execute order with dynamically optimized timeout
        success = await self.submit_ultra_fast_order(
            account_id, instrument, units, max_latency_ms=optimal_timeout
        )
        # Benefits of adaptive timeouts:
        # - Faster execution during good network conditions
        # - Higher success rates during network congestion
        # - Automatic adjustment to changing market conditions

        # Step 13: Feed execution results back into adaptive learning system
        if self.execution_stats['latency_samples']:
            last_latency = self.execution_stats['latency_samples'][-1]
            self.timeout_manager.record_order_result(success, last_latency)
            # Feedback loop enables continuous optimization:
            # - Success -> can be more aggressive
            # - Failure -> need more conservative timeouts
            # - High latency -> adjust timeout upward
            # - Low latency -> can reduce timeout for speed

        return success

        # Adaptive system benefits:
        # - Self-optimizing performance without manual tuning
        # - Responds to changing network and market conditions
        # - Balances speed vs. reliability automatically
        # - Provides competitive advantage through continuous learning
```

---

## Pre-Trade Validation

Optimize pre-trade checks for speed:

```python
from fivetwenty import AsyncClient
from decimal import Decimal
import time
import asyncio


class FastPreTradeValidator:
    """Ultra-fast pre-trade validation system optimized for microsecond-critical HFT operations."""

    def __init__(self, client: AsyncClient) -> None:
        # Step 1: Store FiveTwenty client for authenticated API access when needed
        self.client = client

        # Step 2: Initialize high-performance caching system for validation data
        # Caching eliminates API round trips for repeated validation checks
        self.account_cache = {}      # Account details and balance information
        self.instrument_cache = {}   # Instrument validation and metadata
        self.cache_expiry = 30       # Cache TTL in seconds
        # Cache strategy balances freshness vs. performance:
        # - 30 seconds: Recent enough for account balance accuracy
        # - Long enough to avoid redundant API calls during burst trading

    async def validate_order_fast(self, account_id: str, instrument: str,
                                units: int) -> tuple[bool, str]:
        """Lightning-fast order validation using intelligent caching and early exit patterns."""

        # Step 3: Capture current time for cache timestamp comparisons
        current_time = time.time()

        # Step 4: Validate account details with intelligent caching
        # Account validation checks: existence, status, balance sufficiency
        account_valid, account_msg = await self._validate_account_cached(
            account_id, current_time
        )
        if not account_valid:
            return False, account_msg  # Early exit on account failure
        # Early exit pattern saves processing time when validation fails

        # Step 5: Validate instrument with cached metadata
        # Instrument validation checks: format, availability, trading status
        instrument_valid, instrument_msg = await self._validate_instrument_cached(
            instrument, current_time
        )
        if not instrument_valid:
            return False, instrument_msg  # Early exit on instrument failure

        # Step 6: Perform ultra-fast local units validation
        # No API calls needed - pure computational validation
        if abs(units) < 1:
            return False, "Units too small"  # OANDA minimum requirement

        if abs(units) > 10000000:  # 10M units maximum
            return False, "Units too large"  # Risk management limit
        # Local validation benefits:
        # - Microsecond execution time
        # - No network latency
        # - No API rate limit consumption

        return True, "Valid"  # All validations passed

    async def _validate_account_cached(self, account_id: str,
                                     current_time: float) -> tuple[bool, str]:
        """Validate account with intelligent caching to minimize API calls."""

        # Step 7: Generate cache key for account-specific data
        cache_key = f"account_{account_id}"

        # Step 8: Check cache first for maximum performance
        if cache_key in self.account_cache:
            cache_entry = self.account_cache[cache_key]
            # Verify cache entry is still fresh
            if current_time - cache_entry['timestamp'] < self.cache_expiry:
                return cache_entry['valid'], cache_entry['message']
            # Cache hit eliminates network round trip - major performance gain

        # Step 9: Cache miss - fetch fresh account details from API
        try:
            # Aggressive timeout for HFT requirements
            account = await asyncio.wait_for(
                self.client.accounts.get_account(account_id),
                timeout=0.5  # 500ms timeout - balance speed vs. reliability
            )

            # Step 10: Cache successful validation result
            self.account_cache[cache_key] = {
                'valid': True,
                'message': "Valid account",
                'timestamp': current_time,
                'balance': Decimal(str(account.balance))  # Store for future reference
            }
            # Successful caching benefits subsequent validations

            return True, "Valid account"

        except Exception as e:
            # Step 11: Cache negative results to avoid repeated failures
            # Shorter cache time for negative results allows faster recovery
            self.account_cache[cache_key] = {
                'valid': False,
                'message': f"Account error: {e}",
                'timestamp': current_time  # Same timestamp but will expire sooner
            }

            return False, f"Account error: {e}"
            # Negative caching prevents repeated API calls for known bad accounts

    async def _validate_instrument_cached(self, instrument: str,
                                        current_time: float) -> tuple[bool, str]:
        """Validate instrument with optimized caching and format checking."""

        # Step 12: Ultra-fast local format validation (microsecond execution)
        # Format check: Must be "XXX_YYY" (3 chars + underscore + 3 chars)
        if '_' not in instrument or len(instrument) != 7:
            return False, "Invalid instrument format"
        # Local validation benefits:
        # - No network calls
        # - Instant rejection of malformed inputs
        # - Prevents wasted API calls

        # Step 13: Check instrument cache with extended TTL
        cache_key = f"instrument_{instrument}"

        if cache_key in self.instrument_cache:
            cache_entry = self.instrument_cache[cache_key]
            # Instruments change rarely - use longer cache (10x normal TTL)
            if current_time - cache_entry['timestamp'] < self.cache_expiry * 10:
                return cache_entry['valid'], cache_entry['message']
        # Extended caching for instruments: they rarely become invalid

        # Step 14: HFT optimization - whitelist major pairs to avoid API calls
        # Major currency pairs are always available and highly liquid
        major_pairs = {
            'EUR_USD', 'GBP_USD', 'USD_JPY', 'USD_CHF', 'AUD_USD', 'USD_CAD',
            'NZD_USD', 'EUR_GBP', 'EUR_JPY', 'GBP_JPY', 'CHF_JPY', 'AUD_JPY'
        }
        # Major pairs represent ~80% of forex trading volume
        # HFT systems typically focus on these highly liquid instruments

        is_valid = instrument in major_pairs

        # Step 15: Cache validation result for future use
        self.instrument_cache[cache_key] = {
            'valid': is_valid,
            'message': "Valid instrument" if is_valid else "Unknown instrument",
            'timestamp': current_time
        }
        # Caching benefits:
        # - Subsequent validations are instantaneous
        # - Reduces API load for repeated instrument checks
        # - Enables burst trading on validated instruments

        return is_valid, "Valid instrument" if is_valid else "Unknown instrument"

# Step 16: Comprehensive usage example demonstrating optimized validation workflow
async def fast_order_execution_example(client: AsyncClient, account_id: str):
    """Demonstrate ultra-fast order execution with comprehensive pre-trade validation."""

    # Step 17: Initialize validation and execution systems
    validator = FastPreTradeValidator(client)      # Cached validation system
    order_manager = LowLatencyOrderManager(client) # Low-latency execution system

    # Step 18: Begin end-to-end execution timing
    start_time = time.perf_counter()

    # Step 19: Perform lightning-fast validation with caching
    valid, message = await validator.validate_order_fast(
        account_id, "EUR_USD", 10000
    )
    # Validation checks (cached where possible):
    # - Account existence and status
    # - Instrument availability and format
    # - Units within acceptable range

    if valid:
        # Step 20: Execute order immediately upon validation success
        success = await order_manager.submit_ultra_fast_order(
            account_id, "EUR_USD", 10000, max_latency_ms=75
        )
        # Immediate execution maximizes trading opportunity capture

        # Step 21: Calculate complete execution pipeline timing
        end_time = time.perf_counter()
        total_time = (end_time - start_time) * 1000

        print(f"Total execution time: {total_time:.1f}ms")
        print(f"   Validation: {valid}, Order: {success}")
        # Total time includes:
        # - Validation processing (with caching benefits)
        # - Network round trip to OANDA
        # - Order processing and response

    else:
        # Step 22: Handle validation failure with detailed feedback
        print(f"Error: Validation failed: {message}")
        # Early validation failure prevents:
        # - Wasted API calls for invalid orders
        # - API rate limit consumption
        # - Unnecessary network latency
        # - OANDA server processing load

    # Performance benefits of this approach:
    # - Sub-millisecond validation for cached data
    # - Early exit on validation failures
    # - Optimized execution path for valid orders
    # - Comprehensive timing measurement for optimization
```

---

## Order Queue Management

Implement efficient order queuing:

```python
import heapq
import time
from dataclasses import dataclass, field
from typing import Any, Dict, Optional
from fivetwenty import AsyncClient


@dataclass
class PriorityOrder:
    """Order with priority metadata for advanced queue management in HFT systems."""

    # Step 1: Define order priority and timing metadata
    priority: int                                # Higher numbers = higher priority
    timestamp: float                             # Creation time for FIFO within priority
    order_data: Dict[str, Any] = field(compare=False)  # Actual order parameters
    # field(compare=False) excludes order_data from comparison operations
    # Only priority and timestamp determine queue ordering

    def __lt__(self, other) -> bool:
        """Define ordering logic for priority queue (Python heapq uses min-heap)."""
        # Step 2: Implement sophisticated priority comparison logic
        if self.priority != other.priority:
            # Higher priority numbers should come first (reversed for min-heap)
            return self.priority > other.priority
        # Step 3: Use timestamp for FIFO ordering within same priority level
        return self.timestamp < other.timestamp
        # Priority queue behavior:
        # - Priority 9 orders execute before Priority 5 orders
        # - Within same priority, older orders execute first
        # - Ensures fair execution while respecting urgency

class PriorityOrderQueue:
    """High-performance priority queue optimized for HFT order management."""

    def __init__(self, max_size: int = 1000) -> None:
        # Step 4: Initialize queue with capacity management
        self.max_size = max_size    # Maximum orders to prevent memory exhaustion
        self.queue = []             # Python heapq-compatible list
        # heapq provides O(log n) insertion and O(log n) extraction
        # Optimal for high-frequency order processing

        # Step 5: Initialize comprehensive queue performance statistics
        self.queue_stats = {
            'orders_queued': 0,        # Total orders added to queue
            'orders_processed': 0,     # Total orders removed from queue
            'queue_overflows': 0       # Orders rejected due to capacity
        }
        # Statistics enable:
        # - Queue performance monitoring
        # - Capacity planning and optimization
        # - System load analysis
        # - SLA compliance tracking

    def add_order(self, order_data: Dict, priority: int = 5) -> bool:
        """Add order to priority queue with overflow protection."""

        # Step 6: Implement capacity protection to prevent memory exhaustion
        if len(self.queue) >= self.max_size:
            self.queue_stats['queue_overflows'] += 1
            return False
        # Overflow protection prevents:
        # - Memory exhaustion during high-volume trading
        # - System crashes from unbounded queue growth
        # - Performance degradation from excessive queue operations

        # Step 7: Create priority order with high-precision timestamp
        priority_order = PriorityOrder(
            priority=priority,                    # User-specified priority level
            timestamp=time.perf_counter(),        # High-precision creation time
            order_data=order_data                 # Complete order parameters
        )
        # time.perf_counter() provides nanosecond precision for exact ordering

        # Step 8: Insert into priority queue with O(log n) performance
        heapq.heappush(self.queue, priority_order)
        self.queue_stats['orders_queued'] += 1
        # heapq maintains heap invariant automatically
        # Ensures highest priority order is always at index 0

        return True  # Successfully queued

    def get_next_order(self) -> Optional[Dict]:
        """Extract highest priority order with O(log n) performance."""

        # Step 9: Check for empty queue condition
        if not self.queue:
            return None  # No orders available

        # Step 10: Extract highest priority order
        priority_order = heapq.heappop(self.queue)
        self.queue_stats['orders_processed'] += 1
        # heapq.heappop() maintains heap property after extraction
        # Next highest priority order automatically moves to index 0

        # Step 11: Return order data for execution
        return priority_order.order_data
        # Only order data is returned - priority metadata stays internal
        # Execution system doesn't need to handle priority logic

    def get_queue_size(self) -> int:
        """Get current queue depth for monitoring and capacity planning."""
        return len(self.queue)
        # Queue size monitoring enables:
        # - Load balancing decisions
        # - Capacity planning
        # - Performance optimization
        # - Alert thresholds for system health

    def clear_old_orders(self, max_age_seconds: float = 5.0) -> None:
        """Remove stale orders to prevent execution of outdated trading decisions."""

        # Step 12: Calculate age cutoff threshold
        current_time = time.perf_counter()
        cutoff_time = current_time - max_age_seconds
        # Default 5-second threshold balances:
        # - Preventing stale order execution
        # - Allowing reasonable execution delays

        # Step 13: Rebuild queue excluding stale orders
        # Note: This is O(n) operation - use sparingly
        old_queue = self.queue
        self.queue = []

        # Step 14: Re-add fresh orders to maintain priority ordering
        for priority_order in old_queue:
            if priority_order.timestamp > cutoff_time:
                heapq.heappush(self.queue, priority_order)
        # Queue rebuild maintains heap property
        # Stale order removal prevents:
        # - Execution of outdated market decisions
        # - Trading on obsolete price information
        # - Strategy logic based on old market conditions

# Step 15: Advanced order manager with intelligent priority queuing
class QueuedOrderManager(LowLatencyOrderManager):
    """Advanced order manager that combines low-latency execution with intelligent priority queuing."""

    def __init__(self, client: AsyncClient) -> None:
        # Step 16: Initialize base low-latency capabilities
        super().__init__(client)  # Inherit ultra-fast execution

        # Step 17: Add priority queuing capabilities
        self.order_queue = PriorityOrderQueue()  # High-performance priority queue
        self.processing_orders = False           # Prevent concurrent queue processing
        # Combination provides:
        # - Intelligent order prioritization
        # - Ultra-fast execution for high-priority orders
        # - Queue management during high-volume periods
        # - Controlled execution flow

    async def queue_order(self, account_id: str, instrument: str, units: int,
                         priority: int = 5) -> bool:
        """Queue order with specified priority for intelligent execution scheduling."""

        # Step 18: Create comprehensive order data structure
        order_data = {
            'account_id': account_id,           # Account for execution
            'instrument': instrument,           # Currency pair
            'units': units,                     # Position size and direction
            'timestamp': time.perf_counter()    # Queuing timestamp
        }
        # Order data contains all information needed for execution

        # Step 19: Add to priority queue with specified priority
        return self.order_queue.add_order(order_data, priority)
        # Priority levels (suggested usage):
        # - 9-10: Emergency/stop-loss orders
        # - 7-8:  High-priority strategy orders
        # - 5-6:  Normal trading orders
        # - 1-4:  Low-priority/experimental orders

    async def process_order_queue(self) -> None:
        """Process queued orders in priority order with comprehensive error handling."""

        # Step 20: Prevent concurrent queue processing
        if self.processing_orders:
            return  # Another processor is already running
        # Prevents race conditions and duplicate order execution

        self.processing_orders = True

        try:
            # Step 21: Main order processing loop
            while True:
                # Step 22: Periodic cleanup of stale orders
                self.order_queue.clear_old_orders()
                # Prevents execution of outdated trading decisions

                # Step 23: Get highest priority order from queue
                order_data = self.order_queue.get_next_order()
                if not order_data:
                    # Step 24: No orders available - brief wait before retry
                    await asyncio.sleep(0.001)  # 1ms wait - balance responsiveness vs CPU
                    continue
                # Minimal sleep prevents busy-waiting while maintaining responsiveness

                # Step 25: Execute order with ultra-fast processing
                await self.submit_ultra_fast_order(
                    order_data['account_id'],
                    order_data['instrument'],
                    order_data['units']
                )
                # Orders execute in strict priority order:
                # 1. Highest priority number first
                # 2. Oldest timestamp within same priority
                # 3. Immediate execution for market responsiveness

        finally:
            # Step 26: Ensure processing flag is cleared even on exceptions
            self.processing_orders = False
            # Proper cleanup allows queue processing to restart after errors

# Step 27: Comprehensive example demonstrating intelligent priority queue management
async def queued_execution_example(client: AsyncClient, account_id: str) -> None:
    """Demonstrate advanced queued order execution with priority management."""

    # Step 28: Initialize queued order management system
    queued_manager = QueuedOrderManager(client)

    # Step 29: Start background queue processing
    queue_task = asyncio.create_task(queued_manager.process_order_queue())
    # Background processing ensures continuous order execution

    # Step 30: Queue orders with different priorities to demonstrate intelligent scheduling
    await queued_manager.queue_order(account_id, "EUR_USD", 10000, priority=8)   # High priority
    await queued_manager.queue_order(account_id, "GBP_USD", 5000, priority=3)    # Low priority
    await queued_manager.queue_order(account_id, "USD_JPY", 15000, priority=9)   # Highest priority

    # Step 31: Execution order will be intelligently prioritized:
    # 1. USD_JPY (priority 9) - executes first
    # 2. EUR_USD (priority 8) - executes second
    # 3. GBP_USD (priority 3) - executes last
    # Within same priority: FIFO order (first queued, first executed)

    print("Orders queued with priorities: USD_JPY(9), EUR_USD(8), GBP_USD(3)")
    print("Expected execution order: USD_JPY → EUR_USD → GBP_USD")

    # Step 32: Allow time for queue processing and order execution
    await asyncio.sleep(5)  # 5 seconds processing window

    # Step 33: Clean shutdown of queue processing
    queue_task.cancel()
    print("Queue processing stopped")

    # Priority queue benefits demonstrated:
    # - Critical orders execute before routine orders
    # - Fair scheduling within priority levels
    # - Continuous background processing
    # - Graceful system shutdown
```

---

## Latency Monitoring

Monitor and analyze execution latency:

```python
from collections import deque
import time
import numpy as np
from typing import Any, Dict, List
from fivetwenty import AsyncClient


class LatencyMonitor:
    """Comprehensive latency monitoring and analysis system for HFT performance optimization."""

    def __init__(self) -> None:
        # Step 1: Initialize multi-dimensional latency data collection
        # Separate tracking enables granular performance analysis
        self.latency_data = {
            'order_latencies': deque(maxlen=1000),      # End-to-end order execution times
            'network_latencies': deque(maxlen=1000),    # Network round-trip times
            'processing_latencies': deque(maxlen=1000)  # Local processing times
        }
        # Rolling windows with 1000 samples provide:
        # - Sufficient data for statistical analysis
        # - Recent performance focus (auto-evicts old data)
        # - Memory efficiency (bounded storage)
        # - Real-time monitoring capability

    def record_order_latency(self, total_ms: float, network_ms: float, processing_ms: float) -> None:
        """Record comprehensive latency measurements for multi-dimensional performance analysis."""

        # Step 2: Capture high-precision timestamp for all measurements
        current_timestamp = time.perf_counter()
        # Single timestamp ensures temporal consistency across all measurements

        # Step 3: Record end-to-end order execution latency
        self.latency_data['order_latencies'].append({
            'total_ms': total_ms,              # Complete order lifecycle time
            'timestamp': current_timestamp     # When measurement was taken
        })
        # Total latency includes: validation + network + processing + response parsing

        # Step 4: Record network communication latency
        self.latency_data['network_latencies'].append({
            'latency_ms': network_ms,          # Network round-trip time
            'timestamp': current_timestamp     # Measurement timestamp
        })
        # Network latency isolates communication overhead from processing time

        # Step 5: Record local processing latency
        self.latency_data['processing_latencies'].append({
            'latency_ms': processing_ms,       # Local computation time
            'timestamp': current_timestamp     # Measurement timestamp
        })
        # Processing latency measures internal computation efficiency
        # Enables identification of local vs. network bottlenecks

    def get_latency_analysis(self) -> Dict[str, Any]:
        """Generate comprehensive latency analysis with statistical insights for HFT optimization."""

        # Step 6: Validate sufficient data for meaningful analysis
        if not self.latency_data['order_latencies']:
            return {'error': 'No latency data available'}
        # Early return prevents statistical calculations on empty datasets

        # Step 7: Extract latency values for statistical analysis
        order_latencies = [d['total_ms'] for d in self.latency_data['order_latencies']]
        network_latencies = [d['latency_ms'] for d in self.latency_data['network_latencies']]
        processing_latencies = [d['latency_ms'] for d in self.latency_data['processing_latencies']]

        # Step 8: Generate comprehensive statistical analysis
        return {
            # End-to-end order execution analysis
            'order_latency': {
                'avg_ms': np.mean(order_latencies),      # Mean performance
                'min_ms': np.min(order_latencies),       # Best case performance
                'max_ms': np.max(order_latencies),       # Worst case performance
                'p50_ms': np.percentile(order_latencies, 50),  # Median (typical performance)
                'p95_ms': np.percentile(order_latencies, 95),  # 95th percentile (SLA metric)
                'p99_ms': np.percentile(order_latencies, 99),  # 99th percentile (outlier threshold)
                'std_ms': np.std(order_latencies)        # Standard deviation (consistency)
            },
            # Network communication analysis
            'network_latency': {
                'avg_ms': np.mean(network_latencies),    # Average network performance
                'p95_ms': np.percentile(network_latencies, 95)  # Network SLA metric
            },
            # Local processing analysis
            'processing_latency': {
                'avg_ms': np.mean(processing_latencies), # Average processing efficiency
                'p95_ms': np.percentile(processing_latencies, 95)  # Processing SLA metric
            },
            'sample_count': len(order_latencies)         # Data quality indicator
        }
        # Statistical insights enable:
        # - Performance trend identification
        # - Bottleneck isolation (network vs. processing)
        # - SLA compliance monitoring
        # - System optimization prioritization

    def detect_latency_spikes(self, threshold_percentile: float = 95) -> List[Dict[str, Any]]:
        """Detect and classify unusual latency spikes for performance anomaly analysis."""

        # Step 9: Ensure sufficient data for reliable spike detection
        if len(self.latency_data['order_latencies']) < 50:
            return []  # Insufficient data for statistical significance
        # Minimum sample size prevents false spike detection

        # Step 10: Calculate dynamic threshold based on recent performance
        latencies = [d['total_ms'] for d in self.latency_data['order_latencies']]
        threshold = np.percentile(latencies, threshold_percentile)
        # 95th percentile threshold adapts to current performance baseline
        # Higher percentiles = more sensitive spike detection

        # Step 11: Identify and classify latency spikes
        spikes = []
        for data in self.latency_data['order_latencies']:
            if data['total_ms'] > threshold:
                # Step 12: Classify spike severity for appropriate response
                severity = 'high' if data['total_ms'] > threshold * 1.5 else 'medium'
                # Severity classification:
                # - medium: 1.0x to 1.5x threshold (minor performance degradation)
                # - high: >1.5x threshold (significant performance issue)

                spikes.append({
                    'latency_ms': data['total_ms'],   # Actual spike latency
                    'timestamp': data['timestamp'],   # When spike occurred
                    'severity': severity              # Impact classification
                })

        # Step 13: Return spikes sorted by severity (worst first)
        return sorted(spikes, key=lambda x: x['latency_ms'], reverse=True)
        # Sorted output enables:
        # - Priority-based spike investigation
        # - Performance issue root cause analysis
        # - Alert threshold configuration
        # - System health monitoring

# Step 14: Comprehensive integration example demonstrating complete latency monitoring
latency_monitor = LatencyMonitor()  # Global monitor instance for system-wide tracking

async def monitored_order_execution(client: AsyncClient, account_id: str, instrument: str, units: int) -> bool:
    """Execute order with comprehensive multi-dimensional latency monitoring."""

    # Step 15: Start total execution timing
    total_start = time.perf_counter()

    # Step 16: Measure network communication latency
    network_start = time.perf_counter()
    # In real implementation: actual network operation timing
    # This could measure API call round-trip time specifically
    network_end = time.perf_counter()
    network_latency = (network_end - network_start) * 1000
    # Network latency isolation enables:
    # - Network performance monitoring
    # - Infrastructure bottleneck identification
    # - Carrier/ISP performance analysis

    # Step 17: Measure local processing latency
    processing_start = time.perf_counter()
    # In real implementation: validation, formatting, etc.
    processing_end = time.perf_counter()
    processing_latency = (processing_end - processing_start) * 1000
    # Processing latency measurement enables:
    # - Code optimization opportunities
    # - CPU performance analysis
    # - Algorithm efficiency evaluation

    # Step 18: Execute order with ultra-fast processing
    order_manager = LowLatencyOrderManager(client)
    success = await order_manager.submit_ultra_fast_order(
        account_id, instrument, units
    )

    # Step 19: Calculate total execution time
    total_end = time.perf_counter()
    total_latency = (total_end - total_start) * 1000

    # Step 20: Record comprehensive latency measurements
    latency_monitor.record_order_latency(
        total_latency, network_latency, processing_latency
    )
    # Multi-dimensional recording enables:
    # - Bottleneck identification
    # - Performance trend analysis
    # - System optimization prioritization

    # Step 21: Real-time spike detection and alerting
    spikes = latency_monitor.detect_latency_spikes()
    if spikes:
        print(f"⚠️ Latency spike detected: {spikes[0]['latency_ms']:.1f}ms")
        # Spike detection enables:
        # - Immediate performance issue awareness
        # - Automated alerting systems
        # - Performance degradation prevention
        # - System health monitoring

    # Step 22: Optional comprehensive analysis (periodic)
    # analysis = latency_monitor.get_latency_analysis()
    # print(f"Performance Analysis: {analysis}")

    return success

    # Comprehensive monitoring benefits:
    # - End-to-end performance visibility
    # - Multi-dimensional bottleneck identification
    # - Real-time performance anomaly detection
    # - Data-driven optimization opportunities
    # - Competitive performance benchmarking
```

---

## Next Steps

Continue to [System Resource Management](memory-cpu-optimization.md) for advanced resource optimization.

---

## Related Guides

- [Connection Optimization](connection-optimization.md) - Connection pooling strategies
- [Performance Monitoring](latency-optimization.md) - Latency measurement and analysis
- [Streaming Optimization](streaming-optimization.md) - Real-time data processing