# Connection Optimization

**Problem**: You need to minimize connection latency and maximize throughput for high-frequency trading operations.

**Solution**: Implement persistent connection pooling, request batching, and pipelining strategies to optimize network communication.

---

## Persistent Connection Pooling

Reuse connections to minimize latency:

<!-- fragment: Demo optimized client with undefined imports and unused variables -->
```python
import asyncio
import time
from typing import Any

from fivetwenty import AsyncClient, Environment
from fivetwenty.models import ClientPrice


class OptimizedTradingClient:
    """High-performance OANDA client for HFT applications with connection pool optimization."""

    def __init__(self, token: str, environment: Environment, max_connections: int = 10) -> None:
        """Initialize optimized trading client with performance parameters."""
        # Step 1: Store connection parameters for high-frequency trading optimization
        # Connection pooling reduces latency by reusing established connections
        self.token = token                                # OANDA API authentication token
        self.environment = environment                    # Trading environment (practice/live)
        self.max_connections = max_connections            # Maximum concurrent connections for pool
        self.client: AsyncClient | None = None            # FiveTwenty client instance
        self._connection_pool_initialized = False         # Pool initialization state
        print(f"Config Configuring optimized client for {max_connections} concurrent connections")

    async def initialize(self) -> Any:
        """Initialize optimized client with persistent connections for minimal latency."""

        # Step 2: Create AsyncClient with optimized settings for high-frequency trading
        # Persistent connections eliminate handshake overhead for subsequent requests
        print(f"Lightning Initializing high-performance connection pool...")
        self.client = AsyncClient(
            token=self.token,                    # API authentication
            environment=self.environment         # Environment configuration
            # Note: Connection pool parameters shown for conceptual example
            # Real optimization depends on httpx client configuration within FiveTwenty
            # limits_max_connections=self.max_connections,        # Total connection pool size
            # limits_max_keepalive_connections=self.max_connections,  # Persistent connections
            # limits_keepalive_expiry=300,      # Keep connections alive for 5 minutes
        )
        print(f"Global Connection pool configured with {self.max_connections} max connections")

        # Step 3: Enter client context to establish connection pool
        # Context manager ensures proper connection lifecycle management
        await self.client.__aenter__()
        self._connection_pool_initialized = True
        print(f"Success Optimized client initialized - connection pool active")
        print(f"Starting Ready for high-frequency trading operations")

    async def close(self) -> Any:
        """Clean up connections and release pool resources."""
        # Step 4: Properly close connections to prevent resource leaks
        # Important for long-running HFT applications
        if self.client:
            print(f"Secure Closing connection pool...")
            await self.client.__aexit__(None, None, None)
            self._connection_pool_initialized = False
            print(f"Success Connection pool closed - resources released")

    async def __aenter__(self) -> Any:
        """Context manager entry for automatic client initialization."""
        await self.initialize()
        return self

    async def __aexit__(self, exc_type: object, exc_val: object, exc_tb: object) -> Any:
        """Context manager exit for automatic client cleanup."""
        await self.close()

# Step 5: Usage example with optimized settings for high-frequency trading
async def setup_hft_client() -> Any:
    """Setup high-frequency trading client with optimized connection pooling."""
    print(f"Target Setting up HFT-optimized client...")
    async with OptimizedTradingClient(
        token="your-token",               # Replace with your OANDA API token
        environment=Environment.PRACTICE, # Use practice for testing, live for production
        max_connections=20,              # Higher connection limit for HFT (adjust based on needs)
    ) as hft_client:
        print(f"Lightning HFT client ready with persistent connection pool")
        print(f"Hot Optimized for minimal latency and maximum throughput")
        return hft_client.client

# Step 6: Initialize optimized client for high-frequency operations
# client = await setup_hft_client()
```

## Request Batching and Pipelining

Batch multiple operations to reduce round trips:

<!-- fragment: Demo batch request manager with performance timing and undefined imports -->
```python
import asyncio
import time
from fivetwenty import AsyncClient
from fivetwenty.models import ClientPrice


class BatchRequestManager:
    """Batch multiple requests for improved throughput in high-frequency trading scenarios."""

    def __init__(self, client: AsyncClient, batch_size: int = 10) -> None:
        """Initialize batch request manager for optimized API throughput."""
        # Step 1: Configure batch processing parameters for optimal performance
        # Batching reduces API round trips and improves overall throughput
        self.client = client                    # FiveTwenty AsyncClient instance
        self.batch_size = batch_size           # Maximum requests per batch
        self.pending_requests: list = []       # Queue for pending batch operations
        print(f"Package Batch manager configured with batch size: {batch_size}")

    async def batch_get_prices(self, account_id: str, instrument_batches: list[list[str]]) -> list[list[ClientPrice]]:
        """Get prices for multiple instrument sets concurrently for efficient market data retrieval."""

        # Step 2: Start performance timing for batch pricing operation
        # High-frequency trading requires sub-millisecond performance monitoring
        start_time = time.perf_counter()
        print(f"Lightning Starting concurrent pricing for {len(instrument_batches)} instrument batches...")

        # Step 3: Create concurrent price request tasks
        # Concurrent execution eliminates sequential API call overhead
        tasks = [
            self.client.pricing.get_pricing(account_id, instruments)
            for instruments in instrument_batches
        ]
        print(f"Processing Created {len(tasks)} concurrent pricing tasks")

        # Step 4: Execute all price requests concurrently with exception handling
        # asyncio.gather enables true parallel execution of multiple API calls
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Step 5: Calculate performance metrics for optimization feedback
        end_time = time.perf_counter()
        execution_time_ms = (end_time - start_time) * 1000

        # Step 6: Analyze and filter successful results
        # Exception handling ensures partial failures don't break entire batch
        successful_results = [r for r in results if not isinstance(r, Exception)]
        failed_count = len(results) - len(successful_results)
        throughput = len(instrument_batches) / (end_time - start_time)

        # Step 7: Display detailed performance metrics for HFT optimization
        print(f"Lightning Batch pricing results:")
        print(f"   Success Successful: {len(successful_results)}")
        print(f"   Error Failed: {failed_count}")
        print(f"   Time Total time: {execution_time_ms:.1f}ms")
        print(f"   Starting Throughput: {throughput:.1f} req/sec")
        print(f"   Data Average per request: {execution_time_ms/len(tasks):.1f}ms")

        return successful_results

    async def batch_market_orders(self, account_id: str, order_requests: list[dict]) -> list:
        """Execute multiple market orders concurrently for high-frequency order placement."""

        # Step 8: Start performance timing for batch order execution
        # Order execution timing is critical for HFT strategy success
        start_time = time.perf_counter()
        print(f"Analysis Executing {len(order_requests)} concurrent market orders...")

        # Step 9: Create concurrent order execution tasks
        # Parallel order execution minimizes market impact and slippage
        tasks = []
        for i, order_req in enumerate(order_requests):
            print(f"   Processing Task {i+1}: {order_req['instrument']} {order_req['units']} units")
            task = self.client.orders.post_market_order(
                account_id=account_id,
                instrument=order_req["instrument"],    # Currency pair for order
                units=order_req["units"],              # Position size and direction
                **order_req.get("extra_params", {}),   # Additional order parameters
            )
            tasks.append(task)

        # Step 10: Execute orders concurrently with HFT-appropriate timeout
        # Timeout prevents hanging operations in fast-moving markets
        try:
            print(f"Lightning Executing {len(tasks)} orders with 2-second timeout...")
            results = await asyncio.wait_for(
                asyncio.gather(*tasks, return_exceptions=True),
                timeout=2.0,  # 2-second timeout appropriate for HFT operations
            )
        except asyncio.TimeoutError:
            print("⚠️ Batch order timeout - some orders may have failed")
            print("Note Consider reducing batch size or increasing timeout for volatile markets")
            return []

        # Step 11: Calculate execution performance metrics
        end_time = time.perf_counter()
        execution_time_ms = (end_time - start_time) * 1000

        # Step 12: Analyze order execution success rates
        # Success rate analysis helps optimize batch sizes and timing
        successful_orders = [
            r for r in results
            if not isinstance(r, Exception) and hasattr(r, "order_fill_transaction")
        ]
        failed_orders = len(order_requests) - len(successful_orders)
        success_rate = (len(successful_orders) / len(order_requests)) * 100

        # Step 13: Display comprehensive execution metrics
        print(f"Analysis Batch order execution results:")
        print(f"   Success Successful: {len(successful_orders)}/{len(order_requests)}")
        print(f"   Data Success rate: {success_rate:.1f}%")
        print(f"   Time Execution time: {execution_time_ms:.1f}ms")
        print(f"   Target Average per order: {execution_time_ms/len(order_requests):.1f}ms")
        if failed_orders > 0:
            print(f"   ⚠️ Failed orders: {failed_orders} (check account balance and market conditions)")

        return successful_orders

# Step 14: Comprehensive usage example for high-frequency trading
async def hft_batch_example(client: AsyncClient, account_id: str):
    """Demonstrate batch processing for high-frequency trading operations."""
    print(f"Starting Starting HFT batch processing example...")

    # Step 15: Initialize batch manager with HFT-optimized batch size
    batch_manager = BatchRequestManager(client, batch_size=15)

    # Step 16: Define instrument groups for concurrent price retrieval
    # Grouping by market characteristics optimizes request patterns
    major_pairs = ["EUR_USD", "GBP_USD", "USD_JPY"]      # High liquidity, tight spreads
    minor_pairs = ["EUR_GBP", "AUD_USD", "USD_CAD"]      # Medium liquidity
    exotic_pairs = ["USD_TRY", "EUR_TRY", "GBP_TRY"]     # Lower liquidity, wider spreads

    print(f"Data Instrument groups: {len(major_pairs)} major, {len(minor_pairs)} minor, {len(exotic_pairs)} exotic")

    # Step 17: Execute concurrent price requests across instrument groups
    price_results = await batch_manager.batch_get_prices(
        account_id, [major_pairs, minor_pairs, exotic_pairs],
    )
    print(f"Balance Retrieved pricing data for {len(price_results)} instrument groups")

    # Step 18: Define order batch based on market analysis
    # Order batching enables rapid execution of coordinated trading strategies
    orders = [
        {"instrument": "EUR_USD", "units": 10000},    # Long EUR position
        {"instrument": "GBP_USD", "units": -5000},    # Short GBP position
        {"instrument": "USD_JPY", "units": 15000},    # Long USD/JPY position
    ]
    print(f"Analysis Preparing {len(orders)} coordinated market orders...")

    # Step 19: Execute batch orders with performance monitoring
    order_results = await batch_manager.batch_market_orders(account_id, orders)

    # Step 20: Return results for further analysis
    print(f"Success Batch processing complete: {len(price_results)} price batches, {len(order_results)} orders executed")
    return price_results, order_results
```

---

## Performance Considerations

### Connection Pool Sizing

- **Low latency networks**: Use 15-25 connections
- **High latency networks**: Use 8-12 connections
- **Memory constrained**: Use 5-8 connections

### Batch Size Optimization

- **Price requests**: 3-5 instrument batches
- **Order execution**: 5-10 concurrent orders
- **Account queries**: 2-3 concurrent requests

### Timeout Configuration

- **Individual requests**: 50-100ms for HFT
- **Batch operations**: 150-300ms total
- **Connection timeout**: 5-10 seconds

---

## Next Steps

Continue to [Streaming Optimization](streaming-optimization.md) to optimize real-time data processing.

---

## Related Guides

- [Latency Optimization](latency-optimization.md) - Ultra-fast order execution
- [Network Optimization](connection-optimization.md) - Connection quality monitoring
- [Memory & CPU Optimization](memory-cpu-optimization.md) - System resource optimization
