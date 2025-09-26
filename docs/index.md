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

## Quick Start

Get trading in minutes with FiveTwenty's flexible configuration system. By default, the client will look for three environment variables that must be set. The `FIVETWENTY_OANDA_TOKEN` and `FIVETWENTY_OANDA_ACCOUNT` environment variables represent your token and account number, needed to authenticate.  `FIVETWENTY_OANDA_ENVIRONMENT` is needed to know which OANDA url to connect to.

The example below places environment variables in place using the package `python-dotenv`

```bash
# Install python-dotenv for .env file support (recommended)
uv add python-dotenv
```

Once python-dotenv is installed, you can create a `.env` file in your project root, and the example below will work properly.

```bash
# File: .env
FIVETWENTY_OANDA_TOKEN=your-practice-token
FIVETWENTY_OANDA_ACCOUNT=your-account-id
FIVETWENTY_OANDA_ENVIRONMENT=practice
```

Alternatively, you can set the environment variables manually by adding them to your `.bashrc` or `.zshrc`, or by otherwise setting them in your environment as needed.

With `python-dotenv` installed, you can run this minimal example which will print out your account balance and open a trade for 1000 EUR_USD. You do not need to import `load_dotenv`, nor execute `load_dotenv()`

Make sure this is your practice account, obviously.


```python
import asyncio

from dotenv import load_dotenv

from fivetwenty import AsyncClient
from fivetwenty.models import InstrumentName

load_dotenv()

async def main() -> None:
    async with AsyncClient() as client:
        result = await client.accounts.get_account_summary(client.account_id)  # No type warnings!
        account = result["account"]
        print(f"Balance: {account.balance} {account.currency}")

        # Place your first trade
        order = await client.orders.post_market_order(
            account_id=client.account_id, instrument=InstrumentName.EUR_USD, units=1000,
        )

        if order.order_fill_transaction:
            fill_price = order.order_fill_transaction.get("price", "N/A")
            print(f"Trade executed at {fill_price}")

asyncio.run(main())
```

## Next Steps

Our documentation follows the **[Diátaxis framework](https://diataxis.fr/)** to serve different user needs effectively:

### Learn (Tutorials)
**When you want to build skills through guided practice**

Start with [Tutorials](tutorials/index.md) for hands-on learning that builds your confidence with the FiveTwenty step by step.

### Understand & Solve (Guides)
**When you need comprehensive guidance - both understanding and solutions**

Use [Guides](guides/index.md) for both conceptual understanding and practical solutions to trading challenges.

### Reference (API Docs)
**When you need to look up specific details**

Check [API Reference](api-reference/index.md) for comprehensive method signatures, parameters, and return values.

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

## Getting Started Paths

Choose your learning journey based on your experience level:

### **New to OANDA Trading**
1. [Install FiveTwenty](tutorials/getting-started/installation.md)
2. [Set up authentication](tutorials/getting-started/authentication.md)
3. [Understand environments](tutorials/getting-started/environments.md)
4. [Place your first trade](tutorials/getting-started/first-trade.md)

### **Production Applications**
Build production trading systems with confidence:

- [Configuration patterns](guides/understanding/configuration.md) - Multi-account, multi-environment setup
- [Best practices](guides/understanding/best-practices.md) - Security, performance, and reliability
- [Error handling](api-reference/error-handling.md) - Robust production error management
- [Streaming guide](guides/trading-concepts/streaming.md) - Real-time data processing

## Support & Community

- **Documentation**: Complete guides and references here
- **Issues**: [GitHub Issues](#) for bug reports
- **Discussions**: [GitHub Discussions](#) for questions

---

**Ready to start?** Let's [install FiveTwenty](tutorials/getting-started/installation.md) and get you trading!
