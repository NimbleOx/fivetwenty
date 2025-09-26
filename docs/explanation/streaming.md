# Streaming Data

Real-time data streaming is essential for live trading. The FiveTwenty provides robust streaming capabilities for prices and transactions.

## Overview

The SDK supports two types of streams:
- **Price Streaming**: Real-time bid/ask prices
- **Transaction Streaming**: Account updates and trade events

Both streams include:
- Automatic reconnection
- Heartbeat monitoring
- Stall detection
- Error recovery

## Price Streaming

### Basic Price Stream

Stream real-time prices for instruments:

```python
import asyncio

from fivetwenty import AsyncClient, Environment



async def stream_prices() -> Any:
    """Stream real-time prices."""
    async with AsyncClient(
        token="your-token",
        environment=Environment.PRACTICE,
    ) as client:
        # Stream EUR/USD and GBP/USD prices
        async for price in client.pricing.get_pricing_stream(
            account_id="101-001-1234567-001",
            instruments=["EUR_USD", "GBP_USD"],
        ):
            if price.type == "PRICE":
                print(f"{price.instrument}: Bid={price.bids[0].price}, Ask={price.asks[0].price}")
            elif price.type == "HEARTBEAT":
                print(f"Heartbeat at {price.time}")

asyncio.run(stream_prices())
```

### Processing Price Updates

```python
from decimal import Decimal

from fivetwenty.models import ClientPrice, PricingHeartbeat



async def process_price_stream(client: Any, account_id: str) -> Any:
    """Process streaming prices with business logic."""

    spreads = {}
    last_prices = {}

    async for event in client.pricing.get_pricing_stream(account_id, ["EUR_USD", "GBP_USD"]):
        if isinstance(event, ClientPrice):
            # Calculate spread
            if event.bids and event.asks:
                bid = Decimal(event.bids[0].price)
                ask = Decimal(event.asks[0].price)
                spread = ask - bid
                spreads[event.instrument] = spread

                # Detect price movement
                if event.instrument in last_prices:
                    movement = bid - last_prices[event.instrument]
                    if abs(movement) > Decimal("0.0010"):  # 10 pips
                        print(f"⚠️ Large movement in {event.instrument}: {movement}")

                last_prices[event.instrument] = bid

                # Trading logic
                if spread < Decimal("0.0002"):  # Tight spread
                    await consider_trade(event.instrument, bid, ask)

        elif isinstance(event, PricingHeartbeat):
            # Monitor stream health
            print(f"Stream alive at {event.time}")
```

### Multiple Instrument Streaming

```python
async def multi_instrument_stream(client: Any, account_id: str) -> Any:
    """Stream multiple instruments efficiently."""

    instruments = [
        "EUR_USD", "GBP_USD", "USD_JPY", "AUD_USD",
        "USD_CAD", "EUR_GBP", "EUR_JPY", "GBP_JPY",
    ]

    price_tracker = {}

    async for price in client.pricing.get_pricing_stream(account_id, instruments):
        if price.type == "PRICE":
            # Update price tracker
            price_tracker[price.instrument] = {
                "bid": price.bids[0].price if price.bids else None,
                "ask": price.asks[0].price if price.asks else None,
                "time": price.time,
                "liquidity": sum(b.liquidity for b in price.bids) if price.bids else 0,
            }

            # Check for arbitrage opportunities
            await check_arbitrage(price_tracker)
```

## Transaction Streaming

### Stream Account Changes

Monitor account updates in real-time:

```python
async def stream_transactions(client: Any, account_id: str) -> Any:
    """Stream transaction events."""

    async for event in client.transactions.get_transactions_stream(account_id):
        if event.type == "TRANSACTION":
            transaction = event.transaction

            match transaction.type:
                case "ORDER_FILL":
                    print(f"✅ Order filled: {transaction.instrument} "
                          f"{transaction.units} @ {transaction.price}")

                case "STOP_LOSS_TRIGGERED":
                    print(f"🛑 Stop loss triggered for {transaction.trade_id}")

                case "TAKE_PROFIT_TRIGGERED":
                    print(f"💰 Take profit triggered for {transaction.trade_id}")

                case "MARGIN_CLOSEOUT":
                    print(f"⚠️ Margin closeout: {transaction.reason}")

                case _:
                    print(f"Transaction: {transaction.type}")

        elif event.type == "HEARTBEAT":
            print(f"Transaction stream heartbeat: {event.time}")
```

## Stream Configuration

### Custom Stream Settings

Configure streaming behavior:

```python
from fivetwenty.models.streaming import ReconnectionPolicy, StreamingConfiguration

# Configure streaming

config = StreamingConfiguration(
    account_id="101-001-1234567-001",
    instruments=["EUR_USD", "GBP_USD"],
    snapshot=True,  # Include initial snapshot
    include_heartbeats=True,
    heartbeat_interval_ms=5000,  # 5 second heartbeats
    reconnection_policy=ReconnectionPolicy(
        max_reconnection_attempts=10,
        reconnection_delay_ms=1000,
        exponential_backoff=True,
        max_delay_ms=30000,
        heartbeat_timeout_ms=10000,
    ),
    compression=True,  # Enable compression
    buffer_size=1024,  # Message buffer size
)

# Use configuration (future enhancement)
# async for price in client.pricing.get_pricing_stream(config.account_id, config.instruments):
#     process_price(price)
```

## Error Handling in Streams

### Handle Stream Stalls

Detect and recover from stalled streams:

```python
from fivetwenty.exceptions import StreamStall
import asyncio


async def resilient_stream(client: Any, account_id: str, instruments: Any) -> Any:
    """Stream with automatic recovery from stalls."""

    max_retries = 5
    retry_count = 0

    while retry_count < max_retries:
        try:
            async for price in client.pricing.get_pricing_stream(
                account_id=account_id,
                instruments=instruments,
                stall_timeout=30.0  # Raise StreamStall after 30s without data
            ):
                # Reset retry count on successful data
                retry_count = 0

                if price.type == "PRICE":
                    yield price

        except StreamStall as e:
            retry_count += 1
            print(f"Stream stalled: {e}. Retry {retry_count}/{max_retries}")

            if retry_count >= max_retries:
                raise

            # Exponential backoff
            await asyncio.sleep(2 ** retry_count)

        except Exception as e:
            print(f"Stream error: {e}")
            retry_count += 1
            await asyncio.sleep(5)
```

### Connection Management

Manage long-lived connections:

```python
from datetime import datetime


class StreamManager:
    """Manage streaming connections with health monitoring."""

    def __init__(self, client: Any, account_id: str) -> None:
        self.client = client
        self.account_id = account_id
        self.streams = {}
        self.health_status = {}

    async def start_price_stream(self, instruments: Any) -> Any:
        """Start price streaming with monitoring."""

        stream_id = f"price_{'-'.join(instruments)}"
        self.health_status[stream_id] = {
            "started": datetime.now(),
            "last_data": None,
            "message_count": 0,
            "errors": 0,
        }

        try:
            async for price in self.client.pricing.get_pricing_stream(
                self.account_id,
                instruments,
            ):
                # Update health metrics
                self.health_status[stream_id]["last_data"] = datetime.now()
                self.health_status[stream_id]["message_count"] += 1

                # Process price
                await self.process_price(price)

        except StreamStall:
            self.health_status[stream_id]["errors"] += 1
            await self.restart_stream(stream_id, instruments)

    async def restart_stream(self, stream_id: str, instruments: Any) -> Any:
        """Restart a failed stream."""

        print(f"Restarting stream {stream_id}")
        await asyncio.sleep(5)  # Brief pause
        await self.start_price_stream(instruments)

    async def monitor_health(self) -> Any:
        """Monitor stream health."""

        while True:
            await asyncio.sleep(60)  # Check every minute

            for stream_id, status in self.health_status.items():
                if status["last_data"]:
                    idle_time = datetime.now() - status["last_data"]
                    if idle_time.total_seconds() > 120:
                        print(f"⚠️ Stream {stream_id} idle for {idle_time}")
```

## Synchronous Streaming

### Using the Sync Client

Stream with the sync client:

```python
from fivetwenty import Client, Environment



def sync_price_stream() -> Any:
    """Stream prices synchronously."""

    with Client(
        token="your-token",
        environment=Environment.PRACTICE,
    ) as client:
        # Iterator-based streaming
        for price in client.pricing.get_pricing_stream(
            account_id="101-001-1234567-001",
            instruments=["EUR_USD"],
        ):
            if price.type == "PRICE":
                print(f"Price: {price.asks[0].price}")

            # Can break to stop streaming
            if should_stop():
                break
```

### Thread-Safe Streaming

Handle streams in separate threads:

```python
import queue
import threading



class ThreadedStreamer:
    """Thread-safe streaming handler."""

    def __init__(self, client: Any) -> None:
        self.client = client
        self.price_queue = queue.Queue(maxsize=1000)
        self.running = False

    def start_stream(self, account_id: str, instruments: Any) -> Any:
        """Start streaming in background thread."""

        self.running = True
        thread = threading.Thread(
            target=self._stream_worker,
            args=(account_id, instruments),
            daemon=True,
        )
        thread.start()

    def _stream_worker(self, account_id: str, instruments: Any) -> Any:
        """Worker thread for streaming."""

        for price in self.client.pricing.get_pricing_stream(account_id, instruments):
            if not self.running:
                break

            try:
                self.price_queue.put_nowait(price)
            except queue.Full:
                # Drop oldest price if queue is full
                try:
                    self.price_queue.get_nowait()
                    self.price_queue.put_nowait(price)
                except queue.Empty:
                    pass

    def get_prices(self, timeout: Any = 1.0) -> Any:
        """Get prices from queue."""

        prices = []
        try:
            while True:
                price = self.price_queue.get(timeout=timeout)
                prices.append(price)
        except queue.Empty:
            pass

        return prices

    def stop(self) -> Any:
        """Stop streaming."""
        self.running = False
```

## Advanced Streaming Patterns

### Aggregated Price Data

Aggregate streaming data for analysis:

```python
from decimal import Decimal

from collections import deque
from datetime import datetime, timedelta
import statistics


class PriceAggregator:
    """Aggregate streaming prices for analysis."""

    def __init__(self, window_seconds: int = 60) -> None:
        self.window = timedelta(seconds=window_seconds)
        self.price_windows = {}  # instrument -> deque of (time, price)

    async def process_stream(self, client: Any, account_id: str, instruments: Any) -> Any:
        """Process and aggregate price stream."""

        async for price in client.pricing.get_pricing_stream(account_id, instruments):
            if price.type != "PRICE":
                continue

            instrument = price.instrument
            if instrument not in self.price_windows:
                self.price_windows[instrument] = deque()

            # Add new price
            now = datetime.now()
            mid_price = (
                Decimal(price.bids[0].price) + Decimal(price.asks[0].price)
            ) / 2 if price.bids and price.asks else None

            if mid_price:
                self.price_windows[instrument].append((now, mid_price))

                # Remove old prices
                cutoff = now - self.window
                while (self.price_windows[instrument] and
                       self.price_windows[instrument][0][0] < cutoff):
                    self.price_windows[instrument].popleft()

                # Calculate statistics
                prices = [p for _, p in self.price_windows[instrument]]
                if len(prices) >= 2:
                    stats = {
                        "mean": statistics.mean(prices),
                        "stdev": statistics.stdev(prices),
                        "min": min(prices),
                        "max": max(prices),
                        "range": max(prices) - min(prices),
                        "count": len(prices)
                    }

                    # Detect unusual activity
                    if stats["stdev"] > 0.001:  # High volatility
                        await self.on_high_volatility(instrument, stats)
```

### Multi-Stream Coordination

Coordinate multiple streams:

```python
async def coordinate_streams(client: Any, account_id: str) -> Any:
    """Coordinate price and transaction streams."""

    price_task = asyncio.create_task(
        price_stream_handler(client, account_id),
    )
    transaction_task = asyncio.create_task(
        transaction_stream_handler(client, account_id),
    )

    # Run both streams concurrently
    try:
        await asyncio.gather(price_task, transaction_task)
    except Exception as e:
        print(f"Stream error: {e}")

        # Cancel remaining tasks
        price_task.cancel()
        transaction_task.cancel()

        # Wait for cleanup
        await asyncio.gather(
            price_task,
            transaction_task,
            return_exceptions=True,
        )
```

## Performance Optimization

### Efficient Stream Processing

```python
async def optimized_stream_processing(client: Any, account_id: str) -> Any:
    """Process streams efficiently."""

    # Use minimal instruments
    instruments = ["EUR_USD", "GBP_USD"]  # Don't stream unnecessary pairs

    # Batch processing
    batch = []
    batch_size = 10

    async for price in client.pricing.get_pricing_stream(account_id, instruments):
        if price.type != "PRICE":
            continue

        batch.append(price)

        if len(batch) >= batch_size:
            # Process batch asynchronously
            asyncio.create_task(process_batch(batch.copy()))
            batch.clear()

async def process_batch(prices: Any) -> Any:
    """Process a batch of prices."""
    # Perform calculations on batch
    pass
```

## Monitoring and Metrics

Track streaming performance:

```python


from typing import Any
from datetime import datetime

class StreamMetrics:
    """Class docstring."""
    """Track streaming metrics."""

    def __init__(self) -> None:
        self.metrics = {
            "messages_received": 0,
            "heartbeats_received": 0,
            "errors": 0,
            "reconnections": 0,
            "last_message_time": None,
            "stream_start_time": datetime.now(),
        }

    def update(self, event_type) -> Any:
        """Update metrics."""

        self.metrics["messages_received"] += 1
        self.metrics["last_message_time"] = datetime.now()

        if event_type == "HEARTBEAT":
            self.metrics["heartbeats_received"] += 1

    def get_uptime(self) -> Any:
        """Get stream uptime."""
        return datetime.now() - self.metrics["stream_start_time"]

    def get_message_rate(self) -> Any:
        """Get messages per second."""
        uptime = self.get_uptime().total_seconds()
        return self.metrics["messages_received"] / uptime if uptime > 0 else 0
```

## Best Practices

1. **Handle heartbeats** - They indicate stream health
2. **Implement reconnection** - Networks fail, be prepared
3. **Use appropriate timeouts** - Detect stalls quickly
4. **Process asynchronously** - Don't block the stream
5. **Monitor stream health** - Track metrics and errors
6. **Limit instruments** - Only stream what you need
7. **Handle backpressure** - Don't let queues grow unbounded

## Next Steps

- Review [error handling](error-handling.md) for stream errors
- Check [configuration](configuration.md) for stream settings
- See [best practices](best-practices.md) for production streaming
