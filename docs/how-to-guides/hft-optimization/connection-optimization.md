# Connection Optimization

**Problem**: You need to minimize connection latency and maximize throughput for high-frequency trading operations.

**Solution**: Implement persistent connection pooling, request batching, and pipelining strategies to optimize network communication.

---

## Persistent Connection Pooling

Reuse connections to minimize latency:

```python
import asyncio
import time
from typing import Any

from fivetwenty import AsyncClient, Environment
from fivetwenty.models import ClientPrice



class OptimizedTradingClient:
    """High-performance OANDA client for HFT applications."""

    def __init__(self, token: str, environment: Environment, max_connections: int = 10) -> None:
        self.token = token
        self.environment = environment
        self.max_connections = max_connections
        self.client: AsyncClient | None = None
        self._connection_pool_initialized = False

    async def initialize(self) -> Any:
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

    async def close(self) -> Any:
        """Clean up connections."""
        if self.client:
            await self.client.__aexit__(None, None, None)
            self._connection_pool_initialized = False

    async def __aenter__(self) -> Any:
        await self.initialize()
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> Any:
        await self.close()

# Usage with optimized settings
async def setup_hft_client() -> Any:
    async with OptimizedTradingClient(
        token="your-token",
        environment=Environment.PRACTICE,
        max_connections=20,  # Higher connection limit for HFT
    ) as hft_client:
        return hft_client.client

# client = await setup_hft_client()
```

## Request Batching and Pipelining

Batch multiple operations to reduce round trips:

```python
from fivetwenty import AsyncClient


class BatchRequestManager:
    """Batch multiple requests for improved throughput."""

    def __init__(self, client: AsyncClient, batch_size: int = 10) -> None:
        self.client = client
        self.batch_size = batch_size
        self.pending_requests: list = []

    async def batch_get_prices(self, account_id: str, instrument_batches: list[list[str]]) -> list[list[ClientPrice]]:
        """Get prices for multiple instrument sets concurrently."""

        start_time = time.perf_counter()

        # Create concurrent price requests
        tasks = [
            self.client.pricing.get_pricing(account_id, instruments)
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

    async def batch_market_orders(self, account_id: str, order_requests: list[dict]) -> list:
        """Execute multiple market orders concurrently."""

        start_time = time.perf_counter()

        # Create order tasks
        tasks = []
        for order_req in order_requests:
            task = self.client.orders.post_market_order(
                account_id=account_id,
                instrument=order_req["instrument"],
                units=order_req["units"],
                **order_req.get("extra_params", {}),
            )
            tasks.append(task)

        # Execute concurrently with timeout
        try:
            results = await asyncio.wait_for(
                asyncio.gather(*tasks, return_exceptions=True),
                timeout=2.0,  # 2-second timeout for HFT
            )
        except asyncio.TimeoutError:
            print("⚠️ Batch order timeout - some orders may have failed")
            return []

        end_time = time.perf_counter()

        # Analyze results
        successful_orders = [r for r in results if not isinstance(r, Exception) and hasattr(r, "order_fill_transaction")]

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
        account_id, [major_pairs, minor_pairs, exotic_pairs],
    )

    # Batch order execution based on price analysis
    orders = [
        {"instrument": "EUR_USD", "units": 10000},
        {"instrument": "GBP_USD", "units": -5000},
        {"instrument": "USD_JPY", "units": 15000},
    ]

    order_results = await batch_manager.batch_market_orders(account_id, orders)
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
- [Production Integration](../production-deployment/index.md) - Complete system setup