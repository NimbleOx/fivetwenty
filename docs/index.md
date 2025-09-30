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
from fivetwenty.models import InstrumentName

# Load environment variables from .env file
load_dotenv()

async def main() -> None:
    # Create async client - automatically reads FIVETWENTY_* environment variables
    # Uses context manager for proper cleanup
    async with AsyncClient() as client:
        # Fetch current account information
        # client.account_id is automatically set from FIVETWENTY_OANDA_ACCOUNT
        result = await client.accounts.get_account_summary(client.account_id)
        account = result["account"]
        print(f"Balance: {account.balance} {account.currency}")

        # Get current pricing for EUR/USD
        pricing = await client.pricing.get_pricing(
            account_id=client.account_id,
            instruments=[InstrumentName.EUR_USD],
        )
        price = pricing["prices"][0]
        print(f"Current EUR/USD - Bid: {price.bids[0].price}, Ask: {price.asks[0].price}")

        # Place a market order for 1000 units of EUR/USD
        # Positive units = buy, negative units = sell
        order = await client.orders.post_market_order(
            account_id=client.account_id,
            instrument=InstrumentName.EUR_USD,
            units=1000,  # Buy 1000 units
        )

        # Check if order was filled and print execution price
        if order.order_fill_transaction:
            fill_price = order.order_fill_transaction.get("price", "N/A")
            print(f"Trade executed at {fill_price}")

        # Close the position by selling the same amount
        close_order = await client.orders.post_market_order(
            account_id=client.account_id,
            instrument=InstrumentName.EUR_USD,
            units=-1000,  # Negative units = sell to close
        )

        # Check the closing trade execution
        if close_order.order_fill_transaction:
            close_price = close_order.order_fill_transaction.get("price", "N/A")
            print(f"Position closed at {close_price}")

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
