# Foundation - FiveTwenty Trading Setup

!!! tip "🎯 Learning Goal"
    Understand the essential FiveTwenty concepts needed to start trading with OANDA.

## FiveTwenty Instrument Names

FiveTwenty uses standardized instrument names for currency pairs:

```python
from fivetwenty.models import InstrumentName

# Major pairs available in FiveTwenty
major_pairs = [
    InstrumentName.EUR_USD,  # Euro vs US Dollar
    InstrumentName.GBP_USD,  # British Pound vs US Dollar
    InstrumentName.USD_JPY,  # US Dollar vs Japanese Yen
    InstrumentName.AUD_USD,  # Australian Dollar vs US Dollar
]

# Use these in your trading code
print(f"Trading {InstrumentName.EUR_USD}")  # Outputs: EUR_USD
```

## Essential Trading Concepts for FiveTwenty

**Units**: Position size in FiveTwenty
- Positive units = Buy (long) position
- Negative units = Sell (short) position
- Example: `units=1000` buys 1000 units of base currency

**Decimal Precision**: FiveTwenty uses `Decimal` for exact calculations
- Always use `Decimal("1000")` instead of `1000.0` for financial values
- Prevents floating-point precision errors in trading calculations

**Environment Types**: Practice vs Live trading
- `Environment.PRACTICE` - Safe testing with virtual money
- `Environment.LIVE` - Real trading with actual funds

## Order Types in FiveTwenty

FiveTwenty provides models for all major order types:

```python
from fivetwenty.models import (
    MarketOrderRequest,
    LimitOrderRequest,
    StopLossOrderRequest,
    TakeProfitOrderRequest,
    InstrumentName,
    TimeInForce
)

# Market Order - Execute immediately
market_order = MarketOrderRequest(
    instrument=InstrumentName.EUR_USD,
    units=1000,  # Buy 1000 units
    time_in_force=TimeInForce.FOK,  # Fill or Kill
)

# Limit Order - Buy only at specific price or better
limit_order = LimitOrderRequest(
    instrument=InstrumentName.EUR_USD,
    units=1000,
    price="1.0950",  # Only buy at 1.0950 or lower
    time_in_force=TimeInForce.GTC,  # Good till cancelled
)

# Stop Loss - Protect against losses
stop_loss = StopLossOrderRequest(
    tradeID="12345",
    price="1.0900",  # Close if price hits 1.0900
    timeInForce="GTC",
)
```

## Quick Setup Test

Test your FiveTwenty setup with this simple example:

```python
import asyncio
from dotenv import load_dotenv
from fivetwenty import AsyncClient
from fivetwenty.models import InstrumentName

# Load environment variables from .env file
load_dotenv()

async def test_fivetwenty_setup():
    """Verify your FiveTwenty setup works."""

    # Zero-config - automatically uses environment variables
    async with AsyncClient() as client:
        # Get account info
        account = await client.accounts.get_account(client.account_id)
        print(f"Account balance: {account.balance}")

        # Get current EUR/USD price
        pricing = await client.pricing.get_pricing(
            account_id=client.account_id,
            instruments=[InstrumentName.EUR_USD]
        )

        price = pricing.prices[0]
        print(f"{price.instrument}: {price.asks[0].price}")

# Run the test
asyncio.run(test_fivetwenty_setup())
```

## What You've Learned

**FiveTwenty Instrument Names** - Using `InstrumentName` enum for currency pairs

**Order Models** - Creating market, limit, and stop loss orders with proper types

**Decimal Precision** - Using `Decimal` for exact financial calculations

**Environment Setup** - Distinguishing between practice and live trading

## Next Steps

Ready to start trading? Continue to [Market Data & Analysis](market-data.md) to learn how to analyze market conditions before placing trades.

## Related Resources

- [SDK Architecture](../../guides/understanding/sdk-architecture.md) - Deep dive into FiveTwenty design
- [API Reference](../../api-reference/index.md) - Complete model documentation
- [Configuration Guide](../../guides/understanding/configuration.md) - Environment setup patterns
