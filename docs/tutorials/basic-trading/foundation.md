# Foundation - FiveTwenty Trading Setup

!!! tip "Target Learning Goal"
    Understand the essential FiveTwenty concepts needed to start trading with OANDA.

## FiveTwenty Instrument Names

FiveTwenty uses standardized instrument names for currency pairs. Here's how to work with the most common trading instruments:

```python
# Step 1: Import standardized instrument enumeration for type safety
# InstrumentName enum ensures correct currency pair names and prevents typos
from fivetwenty.models import InstrumentName

# Step 2: Define major currency pairs using type-safe enumerations
# Major pairs have highest liquidity and tightest spreads for optimal trading
major_pairs = [
    InstrumentName.EUR_USD,  # Euro vs US Dollar - world's most traded pair
    InstrumentName.GBP_USD,  # British Pound vs US Dollar - "Cable"
    InstrumentName.USD_JPY,  # US Dollar vs Japanese Yen - popular Asian pair
    InstrumentName.AUD_USD,  # Australian Dollar vs US Dollar - commodity currency
]

# Step 3: Demonstrate proper instrument usage in trading applications
# Enum values automatically convert to OANDA-compatible string format
print(f"Data Trading {InstrumentName.EUR_USD}")  # Outputs: EUR_USD
print(f"Feature Available major pairs: {len(major_pairs)} instruments")

# Step 4: Show how enums prevent common trading errors
# Type safety catches instrument name mistakes before they reach the API
for pair in major_pairs:
    print(f"   Success {pair.value} - Ready for trading")
```

## Essential Trading Concepts for FiveTwenty

**Units**: Position size in FiveTwenty
- Positive units = Buy (long) position
- Negative units = Sell (short) position
- Example: `units=1000` buys 1000 units of base currency

**Decimal Precision**: FiveTwenty uses `Decimal` for exact calculations
- Always use `Decimal("1000")` instead of `1000.0` for financial values
- Prevents floating-point precision errors in trading calculations
- Critical for accurate profit/loss calculations and position sizing

**Environment Types**: Practice vs Live trading
- `Environment.PRACTICE` - Safe testing with virtual money
- `Environment.LIVE` - Real trading with actual funds

## Understanding Decimal Precision in Trading

Financial calculations require exact precision to avoid costly errors. FiveTwenty enforces `Decimal` usage for all monetary values to ensure accuracy:

```python
# Step 1: Import Decimal for exact financial precision
# Decimal eliminates floating-point errors that can cost money in trading
from decimal import Decimal

# Step 2: Demonstrate why floats are dangerous in financial calculations
# Error NEVER use floats for financial calculations - they introduce precision errors
bad_calculation = 0.1 + 0.2  # Results in 0.30000000000000004 (imprecise!)
print(f"Error Float precision error: {bad_calculation}")  # Shows 0.30000000000000004
print("   This precision error could cost real money in trading!")

# Step 3: Show correct approach using Decimal for exact calculations
# Success ALWAYS use Decimal for financial values - guarantees exact precision
good_calculation = Decimal("0.1") + Decimal("0.2")  # Exactly 0.3
print(f"Success Decimal precision: {good_calculation}")  # Shows exactly 0.3
print("   Exact calculations protect your trading capital")

# Step 4: Real trading example - Risk-based position sizing
# Position sizing determines how much capital to risk per trade
account_balance = Decimal("10000.00")  # $10,000 account balance
risk_percentage = Decimal("0.02")      # 2% maximum risk per trade
position_value = account_balance * risk_percentage
print("\nBalance Position Sizing Example:")
print(f"   Account Balance: ${account_balance}")
print(f"   Risk Per Trade: {risk_percentage * 100}%")
print(f"   Position Size: ${position_value}")  # Exactly $200.00

# Step 5: Currency conversion with exact precision
# Exchange rates require precise calculation to avoid rounding errors
eur_usd_rate = Decimal("1.0875")       # Current EUR/USD exchange rate
eur_amount = Decimal("1000.00")        # 1,000 EUR to convert
usd_equivalent = eur_amount * eur_usd_rate
print("\nExchange Currency Conversion:")
print(f"   €{eur_amount} x {eur_usd_rate} = ${usd_equivalent}")  # Exactly $1087.50

# Step 6: Profit/Loss calculations for trade analysis
# P&L calculations must be exact for accurate performance tracking
entry_price = Decimal("1.0850")         # Price when entering trade
exit_price = Decimal("1.0920")          # Price when exiting trade
position_size = Decimal("10000")        # 10,000 EUR position size

# Step 7: Calculate exact profit for long position
# Price difference multiplied by position size gives precise profit
price_difference = exit_price - entry_price  # 0.0070 (70 pips)
profit_usd = price_difference * position_size  # Exact profit calculation
print("\nAnalysis Profit/Loss Calculation:")
print(f"   Entry Price: {entry_price}")
print(f"   Exit Price: {exit_price}")
print(f"   Price Movement: {price_difference} ({price_difference * 10000:.0f} pips)")
print(f"   Position Size: {position_size} EUR")
print(f"   Profit: ${profit_usd}")  # Exactly $70.00
```

### Common Decimal Use Cases in Trading

**Position Sizing**: Calculate exact position sizes based on risk management
```python
from decimal import Decimal

# Step 1: Define account and risk parameters for position sizing
# Risk-based position sizing protects account from catastrophic losses
account_equity = Decimal("25000.00")   # Total account value
max_risk_percent = Decimal("0.01")     # 1% maximum risk per trade (conservative)
stop_loss_pips = Decimal("20")         # 20 pip stop loss distance
pip_value = Decimal("1.00")            # $1 per pip for standard lot (EUR/USD)

# Step 2: Calculate maximum risk amount based on account percentage
# This ensures we never risk more than our predetermined limit
max_risk_amount = account_equity * max_risk_percent  # $250 maximum risk

# Step 3: Calculate maximum position size based on stop loss risk
# Position size = Risk Amount / (Stop Distance x Pip Value)
max_position_lots = max_risk_amount / (stop_loss_pips * pip_value)

print("Target Risk-Based Position Sizing:")
print(f"   Account Equity: ${account_equity}")
print(f"   Maximum Risk: {max_risk_percent * 100}% = ${max_risk_amount}")
print(f"   Stop Loss: {stop_loss_pips} pips")
print(f"   Pip Value: ${pip_value} per pip")
print(f"   Maximum Position: {max_position_lots} lots")  # Exactly 12.5 lots
print(f"   Success This position size limits loss to exactly ${max_risk_amount}")
```

**Profit Target Calculations**: Set precise take profit levels
```python
from decimal import Decimal

# Step 1: Define trade parameters for take profit calculation
# Risk-reward ratios help ensure profitable trading over time
entry_price = Decimal("1.1250")        # Planned entry price for trade
stop_loss_price = Decimal("1.1200")    # Stop loss level (50 pips below entry)
risk_reward_ratio = Decimal("2.0")     # 2:1 risk-reward ratio (conservative target)

# Step 2: Calculate risk amount (distance from entry to stop loss)
# Risk amount determines how much we could lose on this trade
risk_amount = entry_price - stop_loss_price  # 0.0050 (50 pips risk)

# Step 3: Calculate reward amount based on desired risk-reward ratio
# 2:1 ratio means we target twice the reward for every unit of risk
reward_amount = risk_amount * risk_reward_ratio  # 0.0100 (100 pips reward)

# Step 4: Calculate exact take profit level
# Take profit = Entry + (Risk x Ratio) for long positions
take_profit_price = entry_price + reward_amount

print("Target Risk-Reward Calculation:")
print(f"   Entry Price: {entry_price}")
print(f"   Stop Loss: {stop_loss_price} ({risk_amount * 10000:.0f} pips risk)")
print(f"   Risk-Reward Ratio: {risk_reward_ratio}:1")
print(f"   Reward Target: {reward_amount * 10000:.0f} pips")
print(f"   Take Profit: {take_profit_price}")  # Exactly 1.1350
print(f"   Success This setup risks {risk_amount * 10000:.0f} pips to make {reward_amount * 10000:.0f} pips")
```

## Order Types in FiveTwenty

FiveTwenty provides models for all major order types:

<!-- fragment: Demo order models with unused imports and type argument patterns -->
```python
# Step 1: Import essential order model classes for comprehensive trading
# These models provide type safety and validation for all order types
from fivetwenty.models import (
    MarketOrderRequest,     # Immediate execution at current market price
    LimitOrderRequest,      # Entry orders at specific price levels
    StopLossOrderRequest,   # Risk management and loss protection orders
    TakeProfitOrderRequest, # Profit-taking and target price orders
    InstrumentName,         # Type-safe currency pair enumeration
    TimeInForce            # Order duration and execution control
)

# Step 2: Create market order for immediate position entry
# Market orders guarantee execution but not price - use for urgent entries
market_order = MarketOrderRequest(
    instrument=InstrumentName.EUR_USD,        # Major currency pair with high liquidity
    units=1000,                               # 1,000 units long position (positive = buy)
    time_in_force=TimeInForce.FOK,           # Fill or Kill: execute completely or cancel
)
print(f"Analysis Market Order: Buy {market_order.units} units of {market_order.instrument}")
print("   Execution: Immediate at best available price")
print("   Risk: Price may move against you during execution")

# Step 3: Create limit order for precise entry price control
# Limit orders control price but don't guarantee execution - use for planned entries
limit_order = LimitOrderRequest(
    instrument=InstrumentName.EUR_USD,        # Same currency pair for consistency
    units=1000,                               # Same position size for comparison
    price="1.0950",                          # Will only buy if price reaches 1.0950 or better
    time_in_force=TimeInForce.GTC,           # Good Till Cancelled: stays active until filled
)
print(f"\nWait Limit Order: Buy {limit_order.units} units at {limit_order.price}")
print("   Execution: Only if market reaches your target price")
print("   Benefit: Price protection and potential better fills")

# Step 4: Create stop loss order for risk management and capital protection
# Stop loss orders are essential for limiting losses on open positions
stop_loss = StopLossOrderRequest(
    tradeID="12345",                         # Links to specific open trade for protection
    price="1.0900",                          # Triggers closure if price hits this level
    timeInForce="GTC",                       # Remains active until trade is closed
)
print(f"\nSecurity Stop Loss Order: Protect trade 12345 at {stop_loss.price}")
print("   Purpose: Automatic loss limitation and capital preservation")
print("   Trigger: Activates if market moves against your position")

# Step 5: Demonstrate order type selection strategy
print("\nTarget Order Type Selection Guide:")
print("   Analysis Market Orders: When speed matters more than price")
print("   Wait Limit Orders: When price matters more than speed")
print("   Security Stop Loss: Always use for risk management")
print("   Balance Take Profit: Lock in gains at target levels")
```

## Quick Setup Test

Test your FiveTwenty setup with this simple example:

<!-- fragment: Demo setup test with return type annotations and attribute access patterns -->
```python
import asyncio
from dotenv import load_dotenv
from fivetwenty import AsyncClient
from fivetwenty.models import InstrumentName

# Step 1: Load configuration from environment variables
# This reads your API token, account ID, and environment from .env file
load_dotenv()

async def test_fivetwenty_setup():
    """Comprehensive verification of FiveTwenty setup and API connectivity."""

    # Step 2: Initialize AsyncClient with automatic environment-based configuration
    # Zero-config approach reads OANDA credentials from environment variables
    async with AsyncClient() as client:
        print("Config Testing FiveTwenty Setup...")
        print(f"List Configuration: {client.config.summary()}")

        # Step 3: Test API authentication by retrieving account information
        # Account access confirms successful authentication and authorization
        account = await client.accounts.get_account(client.account_id)
        print(f"\nBalance Account Verification:")
        print(f"   Balance: {account.balance} {account.currency}")
        print(f"   Open Trades: {account.open_trade_count}")
        print(f"   Margin Available: {account.margin_available} {account.currency}")

        # Step 4: Test market data access by retrieving real-time pricing
        # Pricing access confirms data feed connectivity and permissions
        pricing = await client.pricing.get_pricing(
            account_id=client.account_id,        # Account context for pricing data
            instruments=[InstrumentName.EUR_USD] # Major pair for reliable data
        )

        # Step 5: Display current market data to confirm successful data access
        # Real-time pricing validates complete API functionality
        price = pricing.prices[0]
        print(f"\nData Market Data Verification:")
        print(f"   Instrument: {price.instrument}")
        print(f"   Bid: {price.bids[0].price} (sell price)")
        print(f"   Ask: {price.asks[0].price} (buy price)")
        print(f"   Spread: {price.spread} (trading cost)")
        print(f"   Time: {price.time}")

        print("\nSuccess FiveTwenty setup verification complete!")
        print("Starting Ready for live trading operations")

# Step 6: Execute comprehensive setup verification
# This test validates authentication, account access, and market data connectivity
if __name__ == "__main__":
    print("Test Starting FiveTwenty Setup Verification...")
    asyncio.run(test_fivetwenty_setup())
    print("Target Setup test completed - review results above")
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
