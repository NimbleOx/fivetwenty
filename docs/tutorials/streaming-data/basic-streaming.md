# Basic Streaming Implementation

Implement your first real-time data streams using FiveTwenty for price feeds and account monitoring.

---

## Prerequisites

- Completed [Streaming Fundamentals](streaming-fundamentals.md)
- FiveTwenty SDK with streaming access
- Understanding of async/await patterns

---

## Price Stream Implementation

```python
import asyncio
from datetime import datetime
from decimal import Decimal
from typing import Dict, List, Optional
from fivetwenty import AsyncClient, Environment
from fivetwenty.models import ClientPrice

class BasicPriceStreamer:
    """Basic implementation of price streaming."""

    def __init__(self, client: AsyncClient, account_id: str):
        self.client = client
        self.account_id = account_id
        self.is_streaming = False
        self.price_cache = {}

    async def stream_prices(self, instruments: List[str]):
        """Stream real-time prices for instruments."""

        print(f"Starting price stream for: {', '.join(instruments)}")
        self.is_streaming = True

        try:
            async for price in self.client.pricing.stream(
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

    async def _process_price_update(self, price: ClientPrice):
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

    async def _analyze_price_movement(self, price: ClientPrice):
        """Basic price movement analysis."""

        instrument = price.instrument
        current_bid = Decimal(str(price.bids[0].price))

        print(f"{instrument}: {current_bid:.5f}")

        # Example: detect significant price moves
        # Implementation would include more sophisticated analysis

    async def _handle_streaming_error(self, error: Exception):
        """Handle streaming errors with reconnection."""

        print(f"Stream error: {error}")
        await asyncio.sleep(5)  # Wait before reconnect

        if self.is_streaming:
            print("Attempting to reconnect...")
            # Implement reconnection logic

    def stop_streaming(self):
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

```python
from fivetwenty import AsyncClient
from fivetwenty import Environment

class AccountStreamer:
    """Stream account changes and transactions."""

    def __init__(self, client: AsyncClient, account_id: str):
        self.client = client
        self.account_id = account_id
        self.is_streaming = False

    async def stream_account_changes(self):
        """Stream account and transaction updates."""

        print("Starting account stream...")
        self.is_streaming = True

        try:
            async for transaction in self.client.transactions.stream(
                account_id=self.account_id
            ):
                if self.is_streaming:
                    await self._process_transaction(transaction)
                else:
                    break

        except Exception as e:
            print(f"Account streaming error: {e}")

    async def _process_transaction(self, transaction):
        """Process account transaction updates."""

        print(f"Transaction: {transaction.type} - {transaction.id}")

        # Handle different transaction types
        if hasattr(transaction, 'order_fill_transaction'):
            await self._handle_order_fill(transaction.order_fill_transaction)

    async def _handle_order_fill(self, fill_transaction):
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

Continue to [Advanced Data Management](advanced-data-management.md) to build robust data processing systems.

---

## Related Tutorials

- [Streaming Fundamentals](streaming-fundamentals.md) - Core concepts
- [Advanced Data Management](advanced-data-management.md) - Data processing
- [Signal Generation](signal-generation.md) - Trading signals