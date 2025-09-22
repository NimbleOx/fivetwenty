# FiveTwenty Documentation

Welcome to **FiveTwenty** - the modern, secure Python SDK for OANDA's v20 REST API. Built for forex trading with first-class async support and robust security.

## Quick Start

Get trading in minutes with FiveTwenty's flexible configuration system:

```bash
# Zero-config with environment variables (recommended)
export FIVETWENTY_OANDA_TOKEN="your-practice-token"
export FIVETWENTY_OANDA_ACCOUNT="your-account-id"
export FIVETWENTY_OANDA_ENVIRONMENT="practice"
```

```python
from fivetwenty import AsyncClient, Environment

# Start trading immediately
async def main():
    async with AsyncClient() as client:
        print(f"Connected: {client.config.summary()}")

        # Check account balance
        account = await client.accounts.get(client.account_id)
        print(f"Balance: {account.balance} {account.currency}")

        # Place your first trade
        order = await client.orders.post_market_order(
            account_id=client.account_id,
            instrument="EUR_USD",
            units=1000
        )

        if order.order_fill_transaction:
            print(f"Trade executed at {order.order_fill_transaction.price}")

# Run the async function
import asyncio
asyncio.run(main())
```

### Alternative Configuration Patterns

```python
import asyncio
from fivetwenty import AsyncClient, Environment, AccountConfig

async def main():
    # Direct parameters (basic scripts)
    async with AsyncClient(
        token="your-token",
        environment=Environment.PRACTICE
    ) as client:
        pass

    # Configuration objects (structured applications)
    config = AccountConfig(
        token="your-token",
        account_id="your-account-id",
        environment=Environment.PRACTICE,
        alias="my_trading_bot"
    )

    async with AsyncClient(config=config) as client:
        print(f"Trading with: {client.config.summary()}")

# Run the async function
asyncio.run(main())
```

## Key Features

### **Modern Python Design**
- **Async & sync clients** - Choose the right tool for your application
- **Type-safe APIs** - Complete type hints with modern Python syntax
- **Pydantic models** - Reliable data validation and serialization
- **Context managers** - Automatic resource cleanup
- **Environment variable support** - Secure deployment patterns

### **Production Ready**
- **Real-time streaming** - Live price feeds with automatic reconnection
- **Intelligent retries** - Exponential back-off with jitter
- **Rate limit handling** - Automatic compliance with OANDA limits
- **Comprehensive error handling** - Structured exception hierarchy

### **Complete OANDA v20 Coverage**
- **All endpoints supported** - Accounts, orders, trades, positions, pricing
- **Advanced order types** - Market, limit, stop with risk management
- **Historical data** - Candlestick charts and order book snapshots
- **Transaction streaming** - Real-time account activity

## Next Steps

Our documentation follows the **[Diátaxis framework](https://diataxis.fr/)** to serve different user needs effectively:

### Learn (Tutorials)
**When you want to build skills through guided practice**

Start with [Tutorials](tutorials/index.md) for hands-on learning that builds your confidence with the FiveTwenty step by step.

### Solve (How-to Guides)
**When you have a specific problem to solve**

Use [How-to Guides](how-to-guides/index.md) for direct, practical solutions to specific trading tasks and challenges.

### Reference (API Docs)
**When you need to look up specific details**

Check [API Reference](api-reference/index.md) for comprehensive method signatures, parameters, and return values.

### Understand (Explanations)
**When you want to understand concepts and design decisions**

Explore [Explanations](explanation/index.md) for background knowledge and deeper understanding of trading concepts.

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

- [Configuration patterns](explanation/configuration.md) - Multi-account, multi-environment setup
- [Best practices](explanation/best-practices.md) - Security, performance, and reliability
- [Error handling](explanation/error-handling.md) - Robust production error management
- [Streaming guide](explanation/streaming.md) - Real-time data processing

## Support & Community

- **Documentation**: Complete guides and references here
- **Issues**: [GitHub Issues](#) for bug reports
- **Discussions**: [GitHub Discussions](#) for questions

---

**Ready to start?** Let's [install FiveTwenty](tutorials/getting-started/installation.md) and get you trading!
