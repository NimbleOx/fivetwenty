# FiveTwenty Documentation

FiveTwenty is a Python SDK for OANDA's v20 REST API, built async-first with a synchronous wrapper. It covers all seven v20 endpoint groups and keeps every monetary value in `Decimal`.

## What is FiveTwenty?

OANDA's v20 API speaks JSON with string-encoded decimals, camelCase field names, and long-lived HTTP streams. FiveTwenty translates that into typed Python: Pydantic models for every request and response object, async iterators for price and transaction streams, and structured exceptions for every error the API can return. Your code works with `Decimal` prices and enum order types; the SDK handles serialization, connection management, and reconnection.

Two runtime dependencies: httpx and pydantic.

**What you get:**

- Every monetary value is a `Decimal`. No floats, anywhere.
- Full type hints under mypy strict, with a `py.typed` marker.
- An async-first `AsyncClient` and a thread-backed synchronous `Client` with the same surface.
- Price and transaction streaming with stall detection and configurable reconnection.
- Retries with exponential backoff for safe requests only; writes are never retried, so a timed-out order can't be silently double-submitted.
- 130+ Pydantic models and 41 enums matching the OANDA specification, verified by an automated parity pipeline against OANDA's published docs.

## What's covered

All seven v20 endpoint groups: accounts, instruments (candles, order book, position book), orders, trades, positions, pricing and streaming, and transactions. Order support includes market, limit, stop, and market-if-touched orders with take-profit, stop-loss, trailing, and guaranteed-stop attachments.

Configuration comes from constructor arguments, an `AccountConfig` object, or `FIVETWENTY_*` environment variables, with credentials held in `SecretStr` so they never appear in logs or reprs.

## Quick Start

Get trading in minutes with a minimal example.

### Installation

```bash
uv add fivetwenty python-dotenv
```

### Configuration

Create a `.env` file in your project root:

```bash
FIVETWENTY_OANDA_TOKEN=your-practice-token
FIVETWENTY_OANDA_ACCOUNT=your-account-id
FIVETWENTY_OANDA_ENVIRONMENT=practice
```

### Your First Trade

```python
import asyncio

from dotenv import load_dotenv
from fivetwenty import AsyncClient
from fivetwenty.endpoints.orders import OrderResponse
from fivetwenty.models import AccountSummary, ClientPrice, InstrumentName

# Load environment variables from .env file
load_dotenv()


async def main() -> None:
    # Step 1: Initialize the client
    # The AsyncClient automatically reads FIVETWENTY_* environment variables
    # Using 'async with' ensures proper cleanup of connections
    async with AsyncClient() as client:
        # Step 2: Check account balance before trading
        # Always verify you have sufficient funds before placing orders
        result = await client.accounts.get_account_summary(client.account_id)
        account: AccountSummary = result["account"]
        print(f"Balance: {account.balance} {account.currency}")

        # Step 3: Get current market prices
        # This shows the bid (sell) and ask (buy) prices
        # The difference between them is the spread (your transaction cost)
        pricing = await client.pricing.get_pricing(
            account_id=client.account_id,
            instruments=[InstrumentName.EUR_USD],
        )
        price: ClientPrice = pricing["prices"][0]
        print(
            f"Current EUR/USD - Bid: {price.bids[0].price}, Ask: {price.asks[0].price}"
        )

        # Step 4: Place a market order to open a position
        # Market orders execute immediately at the current market price
        # Positive units = BUY (go long), Negative units = SELL (go short)
        order: OrderResponse = await client.orders.post_market_order(
            account_id=client.account_id,
            instrument=InstrumentName.EUR_USD,
            units=1000,  # Buy 1000 units
        )

        # Step 5: Verify the order was filled
        # The order_fill_transaction contains execution details
        if order.get("orderFillTransaction"):
            print(f"Trade executed at {order['orderFillTransaction'].price}")

        # Step 6: Close the position
        # To close, place an order with the opposite sign (-1000 sells what we bought)
        # This demonstrates a complete trade cycle: open → close
        close_order: OrderResponse = await client.orders.post_market_order(
            account_id=client.account_id,
            instrument=InstrumentName.EUR_USD,
            units=-1000,  # Negative units = sell to close
        )

        # Step 7: Confirm the position was closed
        # Check the closing price to calculate profit/loss manually if needed
        if close_order.get("orderFillTransaction"):
            print(f"Position closed at {close_order['orderFillTransaction'].price}")


# Run the async function
asyncio.run(main())
```

## Next Steps

- [Tutorials](tutorials/index.md) teach the SDK step by step, starting with [installation](tutorials/getting-started/installation.md) and a first practice-account trade.
- [Guides](guides/index.md) explain how the SDK works (architecture, environments, async vs sync) and solve specific problems (connection failures, stop-loss strategies, multi-account setups).
- The [API Reference](api-reference/index.md) documents every method signature, parameter, and model field.

New here? Start with [installation](tutorials/getting-started/installation.md).
