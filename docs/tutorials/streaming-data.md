# Real-time Streaming Data with FiveTwenty

Learn to implement real-time market data streaming, automated trading systems, and live data processing using the FiveTwenty SDK.

## Learning Objectives

By the end of this tutorial, you will:

- Understand FiveTwenty's streaming data capabilities
- Implement price streams and account monitoring
- Build automated trading systems with real-time data
- Handle connection management and error recovery
- Create production-ready streaming applications

## Prerequisites

- Completed [Basic Trading Tutorial](basic-trading/index.md)
- Understanding of async programming in Python
- FiveTwenty setup with streaming access

## Types of Streaming Data

FiveTwenty supports three main types of streaming data:

### Price Streams
Real-time bid/ask prices for instruments:

```python
from dotenv import load_dotenv
from fivetwenty import AsyncClient

# Load environment variables from .env file
load_dotenv()

async def basic_price_stream():
    # Zero-config - automatically uses environment variables
    async with AsyncClient() as client:
        async for price in client.pricing.get_pricing_stream(
            account_id=client.account_id,
            instruments=["EUR_USD", "GBP_USD"]
        ):
            print(f"{price.instrument}: {price.bids[0].price} / {price.asks[0].price}")

            # Process price data
            await process_price_update(price)

async def process_price_update(price):
    """Process incoming price data."""
    # Your price processing logic here
    pass
```

### Account Streams
Monitor account changes and trade updates:

```python
from dotenv import load_dotenv
from fivetwenty import AsyncClient

# Load environment variables from .env file
load_dotenv()

async def account_stream():
    # Zero-config - automatically uses environment variables
    async with AsyncClient() as client:
        async for transaction in client.transactions.get_transaction_stream(
            account_id=client.account_id
        ):
            print(f"Transaction: {transaction.type} - {transaction.id}")

            # Handle different transaction types
            if transaction.type == "ORDER_FILL":
                await handle_order_fill(transaction)
            elif transaction.type == "MARKET_ORDER":
                await handle_market_order(transaction)

async def handle_order_fill(transaction):
    """Handle order fill transactions."""
    pass

async def handle_market_order(transaction):
    """Handle market order transactions."""
    pass
```

## Connection Management

### Basic Stream with Error Handling

```python
import asyncio
from dotenv import load_dotenv
from fivetwenty import AsyncClient
from fivetwenty.exceptions import StreamStall

# Load environment variables from .env file
load_dotenv()

async def process_price_update(price):
    """Process incoming price data."""
    pass

async def robust_price_stream():
    # Zero-config - automatically uses environment variables
    async with AsyncClient() as client:
        max_retries = 5
        retry_count = 0

        while retry_count < max_retries:
            try:
                async for price in client.pricing.get_pricing_stream(
                    account_id=client.account_id,
                    instruments=["EUR_USD"]
                ):
                    # Reset retry count on successful data
                    retry_count = 0
                    await process_price_update(price)

            except StreamStall:
                retry_count += 1
                if retry_count >= max_retries:
                    raise

                print(f"Stream stalled, retrying ({retry_count}/{max_retries})")
                await asyncio.sleep(2 ** retry_count)  # Exponential backoff
```

### Stream Monitoring

Monitor stream health and implement reconnection logic:

```python
import time
from dotenv import load_dotenv
from fivetwenty import AsyncClient

# Load environment variables from .env file
load_dotenv()

async def process_price_update(price):
    """Process incoming price data."""
    pass

class StreamMonitor:
    def __init__(self, stall_timeout: float = 30.0):
        self.stall_timeout = stall_timeout
        self.last_heartbeat = time.time()

    def on_data_received(self):
        """Call when data is received."""
        self.last_heartbeat = time.time()

    def is_stalled(self) -> bool:
        """Check if stream appears stalled."""
        return (time.time() - self.last_heartbeat) > self.stall_timeout

async def monitored_stream():
    monitor = StreamMonitor(stall_timeout=30.0)

    # Zero-config - automatically uses environment variables
    async with AsyncClient() as client:
        async for price in client.pricing.get_pricing_stream(
            account_id=client.account_id,
            instruments=["EUR_USD"]
        ):
            monitor.on_data_received()

            if monitor.is_stalled():
                print("Stream appears stalled, reconnecting...")
                break

            await process_price_update(price)
```

## Automated Trading with Streaming Data

### Signal Generation from Price Streams

```python
from decimal import Decimal
from collections import deque
from fivetwenty import AsyncClient, Environment

# Load environment variables from .env file
load_dotenv()

class MovingAverageSignal:
    def __init__(self, window_size: int = 20):
        self.window_size = window_size
        self.prices = deque(maxlen=window_size)

    def add_price(self, price: Decimal) -> Decimal | None:
        """Add price and return moving average if window is full."""
        self.prices.append(price)

        if len(self.prices) == self.window_size:
            return sum(self.prices) / len(self.prices)
        return None

async def automated_trading_system():
    signal = MovingAverageSignal(window_size=10)

    # Zero-config - automatically uses environment variables
    async with AsyncClient() as client:
        async for price in client.pricing.get_pricing_stream(
            account_id=client.account_id,
            instruments=["EUR_USD"]
        ):
            # Calculate signal
            mid_price = (Decimal(price.bids[0].price) + Decimal(price.asks[0].price)) / 2
            ma = signal.add_price(mid_price)

            if ma and mid_price > ma * Decimal("1.001"):  # Price 0.1% above MA
                # Buy signal
                await client.orders.post_market_order(
                    account_id=client.account_id,
                    instrument="EUR_USD",
                    units=1000,
                    stop_loss_on_fill={
                        "price": str(mid_price - Decimal("0.0050")),
                        "time_in_force": "GTC"
                    }
                )
                print(f"Buy signal executed at {mid_price}")
```

### Order Management with Real-time Updates

```python
import asyncio
from fivetwenty import AsyncClient, Environment

# Load environment variables from .env file
load_dotenv()

class PositionManager:
    def __init__(self):
        self.open_positions = {}
        self.pending_orders = {}

    async def handle_transaction(self, transaction):
        """Handle incoming transaction stream data."""
        if transaction.type == "ORDER_FILL":
            await self.update_position(transaction)
        elif transaction.type == "ORDER_CREATE":
            self.pending_orders[transaction.order_id] = transaction
        elif transaction.type == "ORDER_CANCEL":
            self.pending_orders.pop(transaction.order_id, None)

    async def update_position(self, fill_transaction):
        """Update position tracking on fill."""
        instrument = fill_transaction.instrument
        units = int(fill_transaction.units)

        if instrument not in self.open_positions:
            self.open_positions[instrument] = 0

        self.open_positions[instrument] += units
        print(f"Position updated: {instrument} = {self.open_positions[instrument]}")

async def managed_trading_system():
    position_manager = PositionManager()

    # Zero-config - automatically uses environment variables
    async with AsyncClient() as client:
        # Monitor both prices and transactions
        price_task = asyncio.create_task(monitor_prices(client, position_manager))
        transaction_task = asyncio.create_task(monitor_transactions(client, position_manager))

        await asyncio.gather(price_task, transaction_task)

async def monitor_prices(client, position_manager):
    """Monitor price streams."""
    async for price in client.pricing.get_pricing_stream(
        account_id=client.account_id,
        instruments=["EUR_USD"]
    ):
        # Price-based logic here
        pass

async def monitor_transactions(client, position_manager):
    """Monitor transaction streams."""
    async for transaction in client.transactions.get_transaction_stream(
        account_id=client.account_id
    ):
        await position_manager.handle_transaction(transaction)
```


## Complete Example

Here's a complete streaming trading system:

```python
import asyncio
import logging
import os
from decimal import Decimal
from collections import deque
from fivetwenty import AsyncClient, Environment
from fivetwenty.exceptions import StreamStall

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class StreamingTradingSystem:
    def __init__(self, token: str, account_id: str):
        self.token = token
        self.account_id = account_id
        self.prices = deque(maxlen=100)  # Keep last 100 prices
        self.positions = {}

    async def run(self):
        """Main trading system loop."""
        while True:
            try:
                async with AsyncClient(
                    token=self.token,
                    environment=Environment.PRACTICE
                ) as client:
                    logger.info("Starting streaming trading system")

                    # Create concurrent tasks for price and transaction monitoring
                    tasks = [
                        asyncio.create_task(self.monitor_prices(client)),
                        asyncio.create_task(self.monitor_transactions(client))
                    ]

                    await asyncio.gather(*tasks)

            except StreamStall:
                logger.warning("Stream stalled, reconnecting in 5 seconds...")
                await asyncio.sleep(5)
            except Exception as e:
                logger.error(f"System error: {e}")
                await asyncio.sleep(10)

    async def monitor_prices(self, client):
        """Monitor price streams and generate trading signals."""
        async for price in client.pricing.get_pricing_stream(
            account_id=self.account_id,
            instruments=["EUR_USD"]
        ):
            try:
                await self.process_price(client, price)
            except Exception as e:
                logger.error(f"Price processing error: {e}")

    async def monitor_transactions(self, client):
        """Monitor transaction streams for position updates."""
        async for transaction in client.transactions.get_transaction_stream(
            account_id=self.account_id
        ):
            try:
                await self.process_transaction(transaction)
            except Exception as e:
                logger.error(f"Transaction processing error: {e}")

    async def process_price(self, client, price):
        """Process incoming price data and generate signals."""
        mid_price = (Decimal(price.bids[0].price) + Decimal(price.asks[0].price)) / 2
        self.prices.append(mid_price)

        # Simple moving average signal
        if len(self.prices) >= 20:
            ma20 = sum(list(self.prices)[-20:]) / 20

            # Buy signal: price crosses above MA
            if mid_price > ma20 * Decimal("1.001"):
                await self.place_buy_order(client, price.instrument, mid_price)

    async def place_buy_order(self, client, instrument: str, price: Decimal):
        """Place a buy order with stop loss."""
        try:
            order = await client.orders.post_market_order(
                account_id=self.account_id,
                instrument=instrument,
                units=1000,
                stop_loss_on_fill={
                    "price": str(price - Decimal("0.0050")),
                    "time_in_force": "GTC"
                }
            )
            logger.info(f"Buy order placed: {order.order_fill_transaction.id}")
        except Exception as e:
            logger.error(f"Order placement failed: {e}")

    async def process_transaction(self, transaction):
        """Process transaction updates."""
        if transaction.type == "ORDER_FILL":
            logger.info(f"Order filled: {transaction.id}")
            # Update position tracking

# Run the system
async def main():
    token = os.getenv("OANDA_TOKEN")
    account_id = "101-001-0000000-001"

    system = StreamingTradingSystem(token, account_id)
    await system.run()

if __name__ == "__main__":
    asyncio.run(main())
```

## Key Takeaways

1. **Use async/await** - Essential for efficient streaming data handling
2. **Implement reconnection logic** - Streams can disconnect, plan for recovery
3. **Monitor stream health** - Detect stalls and connection issues
4. **Handle errors gracefully** - Don't let processing errors stop the stream
5. **Use proper logging** - Essential for debugging production systems
6. **Test thoroughly** - Start with practice environment, validate with live data

## Next Steps

- Review [Best Practices](../guides/understanding/best-practices.md) for production deployment
- Explore [Advanced Order Types](advanced-orders/index.md) for sophisticated strategies
- Check [HFT Optimization](../guides/performance-optimization/hft-optimization/index.md) for performance tuning

FiveTwenty provides robust streaming capabilities for real-time trading applications - focus on building reliable, maintainable systems that handle the inherent challenges of live market data.