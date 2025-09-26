# Basic Streaming Implementation

Implement your first real-time data streams using FiveTwenty for price feeds and account monitoring.

---

## Prerequisites

- Completed [Streaming Fundamentals](streaming-fundamentals.md)
- FiveTwenty SDK with streaming access
- Understanding of async/await patterns

---

## Price Stream Implementation

This example shows how to connect to OANDA's pricing stream and process real-time market data. The stream provides live bid/ask prices for specified instruments with automatic heartbeat monitoring.

```python
import asyncio
from datetime import datetime
from decimal import Decimal
from typing import Dict, List, Optional
from fivetwenty import AsyncClient, Environment
from fivetwenty.models import ClientPrice


class BasicPriceStreamer:
    """Basic implementation of price streaming."""

    def __init__(self, client: AsyncClient, account_id: str) -> None:
        self.client = client
        self.account_id = account_id
        self.is_streaming = False
        self.price_cache = {}

    async def stream_prices(self, instruments: List[str]) -> Any:
        """Stream real-time prices for instruments."""

        print(f"Starting price stream for: {', '.join(instruments)}")
        self.is_streaming = True

        try:
            async for price in self.client.pricing.get_pricing_stream(
                account_id=self.account_id,
                instruments=instruments
            ):
                if self.is_streaming:
                    await self._process_price_update(price)
                else:
                    break

        except Exception as e:
            print(f"Streaming error: {e}")
            await self._handle_streaming_error(e)

    async def _process_price_update(self, price: ClientPrice) -> Any:
        """Process incoming price update."""

        # Cache the latest price
        self.price_cache[price.instrument] = {
            'bid': Decimal(str(price.bids[0].price)),
            'ask': Decimal(str(price.asks[0].price)),
            'spread': Decimal(str(price.asks[0].price)) - Decimal(str(price.bids[0].price)),
            'timestamp': datetime.now()
        }

        # Basic processing example
        await self._analyze_price_movement(price)

    async def _analyze_price_movement(self, price: ClientPrice) -> Any:
        """Basic price movement analysis."""

        instrument = price.instrument
        current_bid = Decimal(str(price.bids[0].price))

        print(f"{instrument}: {current_bid:.5f}")

        # Example: detect significant price moves
        # Implementation would include more sophisticated analysis

    async def _handle_streaming_error(self, error: Exception) -> Any:
        """Handle streaming errors with reconnection."""

        print(f"Stream error: {error}")
        await asyncio.sleep(5)  # Wait before reconnect

        if self.is_streaming:
            print("Attempting to reconnect...")
            # Implement reconnection logic

    def stop_streaming(self) -> Any:
        """Stop the price stream."""
        self.is_streaming = False
        print("Price streaming stopped")

# Example usage
async def basic_streaming_example():
    """Demonstrate basic streaming implementation."""

    TOKEN = "your-api-token"
    ACCOUNT_ID = "your-account-id"

    async with AsyncClient(token=TOKEN, environment=Environment.PRACTICE) as client:
        streamer = BasicPriceStreamer(client, ACCOUNT_ID)

        # Start streaming
        instruments = ["EUR_USD", "GBP_USD", "USD_JPY"]
        await streamer.stream_prices(instruments)

# Run example
# await basic_streaming_example()
```

## Account Stream Monitoring

Account streams provide real-time updates about trades, orders, and account changes. This is essential for monitoring position changes and order fills as they happen.

```python
from fivetwenty import AsyncClient
from fivetwenty import Environment


class AccountStreamer:
    """Stream account changes and transactions."""

    def __init__(self, client: AsyncClient, account_id: str) -> None:
        self.client = client
        self.account_id = account_id
        self.is_streaming = False

    async def stream_account_changes(self) -> Any:
        """Stream account and transaction updates."""

        print("Starting account stream...")
        self.is_streaming = True

        try:
            async for transaction in self.client.transactions.get_transactions_stream(
                account_id=self.account_id
            ):
                if self.is_streaming:
                    await self._process_transaction(transaction)
                else:
                    break

        except Exception as e:
            print(f"Account streaming error: {e}")

    async def _process_transaction(self, transaction: Any) -> Any:
        """Process account transaction updates."""

        print(f"Transaction: {transaction.type} - {transaction.id}")

        # Handle different transaction types
        if hasattr(transaction, 'order_fill_transaction'):
            await self._handle_order_fill(transaction.order_fill_transaction)

    async def _handle_order_fill(self, fill_transaction: Any) -> Any:
        """Handle order fill transactions."""

        print(f"Order filled: {fill_transaction.instrument} "
              f"{fill_transaction.units} @ {fill_transaction.price}")

# Combined streaming example
async def combined_streaming_example():
    """Example combining price and account streams."""

    TOKEN = "your-api-token"
    ACCOUNT_ID = "your-account-id"

    async with AsyncClient(token=TOKEN, environment=Environment.PRACTICE) as client:
        # Initialize streamers
        price_streamer = BasicPriceStreamer(client, ACCOUNT_ID)
        account_streamer = AccountStreamer(client, ACCOUNT_ID)

        # Start both streams concurrently
        await asyncio.gather(
            price_streamer.stream_prices(["EUR_USD", "GBP_USD"]),
            account_streamer.stream_account_changes()
        )

# Run combined example
# await combined_streaming_example()
```

---

## Next Steps

Continue to [Automated Trading](automated-trading.md) to build complete trading systems.

---

## Related Tutorials

- [Streaming Fundamentals](streaming-fundamentals.md) - Core concepts
- [Automated Trading](automated-trading.md) - Complete trading systems
- [Advanced Features](advanced-features.md) - Advanced streaming capabilities