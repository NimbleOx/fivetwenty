# Practice vs Live Trading

Learn when to use OANDA's practice environment for safe development versus the live environment for real trading.

## Quick Environment Setup

Choose your environment when creating the client:

```python
from fivetwenty import AsyncClient, Environment

# Practice trading (safe for learning)
async with AsyncClient(
    token="your-practice-token",
    environment=Environment.PRACTICE  # No real money risk
) as client:
    # All your trading code here - safe to experiment!
    accounts = await client.accounts.get_accounts()

# Live trading (real money - use with caution!)
async with AsyncClient(
    token="your-live-token",
    environment=Environment.LIVE  # Real money at risk
) as client:
    # Production trading code only
    accounts = await client.accounts.get_accounts()
```

## When to Use Each Environment

### Practice Environment ✅

**Perfect for:**
- Learning OANDA trading concepts
- Testing new trading strategies
- Developing and debugging code
- Experimenting with position sizes

**Benefits:**
- $100,000 virtual starting balance
- Real-time market data
- No risk to real money
- Instant account setup

### Live Environment ⚠️

**Use only when:**
- Strategy is thoroughly tested in practice
- Code is production-ready and error-handled
- You understand the financial risks
- Account is properly funded

**Requirements:**
- OANDA live account with KYC verification
- Real money deposit
- Production-ready risk management

!!! tip "Development Workflow"
    **Always start with practice environment** to test your strategies safely, then gradually move to live trading with small position sizes.

!!! info "Complete Environment Guide"
    For comprehensive environment concepts, safety considerations, and deployment workflows, see [Configuration Guide](../../explanation/configuration.md#environment-concepts).

## Getting Started

### 1. Create Practice Account
1. Sign up at [OANDA](https://www.oanda.com)
2. Create a practice account (no credit card needed)
3. Generate API token from account settings
4. Start developing with virtual funds!

### 2. Basic Practice Example

```python
import asyncio
import os
from fivetwenty import AsyncClient, Environment

async def my_first_practice_trade():
    async with AsyncClient(
        token=os.environ["OANDA_PRACTICE_TOKEN"],
        environment=Environment.PRACTICE
    ) as client:
        # Safe to experiment - virtual money only!
        account = (await client.accounts.get_accounts())[0]
        print(f"Virtual Balance: ${account.balance}")

        # Place a practice trade
        order = await client.orders.post_market_order(
            account_id=account.id,
            instrument="EUR_USD",
            units=1000  # Small test position
        )
        print("Practice trade successful!")

asyncio.run(my_first_practice_trade())
```

## Next Steps

Once you're comfortable with the practice environment:

- [Make your first trade](first-trade.md) to learn the basic trading workflow
- [Set up authentication](authentication.md) for production-ready configuration
- [Review configuration options](../../explanation/configuration.md) for comprehensive environment guidance