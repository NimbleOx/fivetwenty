# FiveTwenty Documentation

Welcome to **FiveTwenty** - the modern, secure Python SDK for OANDA's v20 REST API. Built for forex trading with first-class async support and robust security.

## What is FiveTwenty?

**FiveTwenty** is a robust Python SDK that makes forex trading through the OANDA v20 REST API accessible and reliable. Whether you're building automated trading systems, creating analytical tools, or developing trading applications, FiveTwenty provides the foundation you need.

FiveTwenty bridges the gap between OANDA's powerful v20 API and your Python applications. It handles the complexity of financial data types, connection management, and error handling so you can focus on your trading logic.

**Key benefits:**

- **Financial precision** - All monetary values use `Decimal` types to prevent floating-point errors
- **Type safety** - Complete type hints help catch errors before they reach production
- **Async-first design** - Built for high-performance applications with sync wrapper available
- **Robust design** - Comprehensive error handling, automatic retries, and rate limiting

## Key Features

### **Modern Python Design**
- **Async & sync clients** - Choose the right tool for your application
- **Type-safe APIs** - Complete type hints with modern Python syntax
- **Pydantic models** - Reliable data validation and serialization
- **Context managers** - Automatic resource cleanup
- **Environment variable support** - Secure deployment patterns
- **Real-time streaming** - Live price feeds with automatic reconnection
- **Intelligent retries** - Exponential back-off with jitter
- **Rate limit handling** - Automatic compliance with OANDA limits
- **Comprehensive error handling** - Structured exception hierarchy

### **Complete OANDA v20 Coverage**
- **All endpoints supported** - Accounts, orders, trades, positions, pricing
- **Advanced order types** - Market, limit, stop with risk management
- **Historical data** - Candlestick charts and order book snapshots
- **Transaction streaming** - Real-time account activity

## Architecture Overview

FiveTwenty provides a robust architecture for trading applications:

### **Configuration System**
- **AccountConfig** - Secure credential management with automatic masking
- **Environment variables** - Zero-config deployment with `FIVETWENTY_*` variables
- **Multi-account support** - Custom prefixes for complex trading systems
- **Configuration validation** - Runtime validation with helpful error messages

### **Client Architecture**
- **AsyncClient** - High-performance async client for concurrent operations
- **Client** - Synchronous wrapper for scripts and legacy applications
- **Automatic retry logic** - Intelligent handling of network issues and rate limits
- **Configurable timeouts** - Fine-tune performance for your use case

### **Data Models**
- **75+ Pydantic models** - Complete coverage of OANDA API request and response objects
- **Decimal precision** - Financial-grade decimal arithmetic throughout
- **Type validation** - Catch errors at runtime with meaningful messages

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
from fivetwenty.models import AccountSummary, ClientPrice, InstrumentName, OrderResponse

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
        if order.order_fill_transaction:
            print(f"Trade executed at {order.order_fill_transaction.price}")

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
        if close_order.order_fill_transaction:
            print(f"Position closed at {close_order.order_fill_transaction.price}")


# Run the async function
asyncio.run(main())
```

## Next Steps

Our documentation is organized to serve different user needs effectively:

### Learn (Tutorials)
**When you want to build skills through guided practice**

Start with [Tutorials](tutorials/index.md) for hands-on learning that builds your confidence with the FiveTwenty step by step.

### Understand & Solve (Guides)
**When you need comprehensive guidance - both understanding and solutions**

Use [Guides](guides/index.md) for both conceptual understanding and practical solutions to trading challenges.

### Reference (API Docs)
**When you need to look up specific details**

Check [API Reference](api-reference/index.md) for comprehensive method signatures, parameters, and return values.

---

**Ready to start?** Let's [install FiveTwenty](tutorials/getting-started/installation.md) and get you trading!
