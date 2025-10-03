# Foundation - FiveTwenty Trading Setup

!!! tip "Target Learning Goal"
    Understand the essential FiveTwenty concepts needed to start trading with OANDA.

## FiveTwenty Instrument Names

Currency trading requires precise instrument identification. FiveTwenty provides the `InstrumentName` enum to eliminate typos and ensure type safety when specifying currency pairs. Instead of using error-prone strings like `"EUR_USD"` or `"EURUSD"`, you use strongly-typed enum values that your IDE can autocomplete and your type checker can verify. This prevents common mistakes that could cause API errors or unexpected trading behavior.

The example below demonstrates how to use `InstrumentName` for major currency pairs, which typically offer the highest liquidity and tightest spreads:

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

## Understanding Decimal Precision in Trading

Floating-point arithmetic is fundamentally unsuitable for financial calculations. The classic example `0.1 + 0.2 = 0.30000000000000004` demonstrates how binary floating-point representation introduces rounding errors that can compound across thousands of trades, leading to incorrect account balances, position sizing errors, and regulatory compliance issues.

FiveTwenty enforces the use of Python's `Decimal` type for all monetary values. `Decimal` uses base-10 arithmetic with exact precision, ensuring that calculations involving money, prices, and quantities remain accurate. This is not just a best practice - it's essential for production trading systems.

The example below demonstrates the difference between float and Decimal arithmetic, then shows practical applications in position sizing, currency conversion, and profit/loss calculations:

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
risk_percentage = Decimal("0.02")  # 2% maximum risk per trade
position_value = account_balance * risk_percentage
print("\nBalance Position Sizing Example:")
print(f"   Account Balance: ${account_balance}")
print(f"   Risk Per Trade: {risk_percentage * 100}%")
print(f"   Position Size: ${position_value}")  # Exactly $200.00

# Step 5: Currency conversion with exact precision
# Exchange rates require precise calculation to avoid rounding errors
eur_usd_rate = Decimal("1.0875")  # Current EUR/USD exchange rate
eur_amount = Decimal("1000.00")  # 1,000 EUR to convert
usd_equivalent = eur_amount * eur_usd_rate
print("\nExchange Currency Conversion:")
print(f"   €{eur_amount} x {eur_usd_rate} = ${usd_equivalent}")  # Exactly $1087.50

# Step 6: Profit/Loss calculations for trade analysis
# P&L calculations must be exact for accurate performance tracking
entry_price = Decimal("1.0850")  # Price when entering trade
exit_price = Decimal("1.0920")  # Price when exiting trade
position_size = Decimal("10000")  # 10,000 EUR position size

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

Risk management is the foundation of successful trading. Position sizing determines how much capital you allocate to each trade based on your account size, risk tolerance, and stop loss distance. The calculation must be exact - a rounding error could expose you to more risk than intended or prevent you from taking valid trades.

This example demonstrates the standard position sizing formula: calculate your maximum risk amount (account equity × risk percentage), then divide by your stop loss distance to determine the maximum position size that keeps your risk within limits:

```python
from decimal import Decimal

# Step 1: Define account and risk parameters for position sizing
# Risk-based position sizing protects account from catastrophic losses
account_equity = Decimal("25000.00")  # Total account value
max_risk_percent = Decimal("0.01")  # 1% maximum risk per trade (conservative)
stop_loss_pips = Decimal("20")  # 20 pip stop loss distance
pip_value = Decimal("1.00")  # $1 per pip for standard lot (EUR/USD)

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

Professional traders use risk-reward ratios to ensure their strategy remains profitable over time. A 2:1 risk-reward ratio means you target twice as much profit as the amount you're risking. If you risk 50 pips with a stop loss, you aim for 100 pips of profit with your take profit level. Even with a 50% win rate, this ratio produces net positive returns.

The calculation requires exact precision to properly set take profit orders. This example shows how to calculate take profit levels based on your entry price, stop loss distance, and desired risk-reward ratio:

```python
from decimal import Decimal

# Step 1: Define trade parameters for take profit calculation
# Risk-reward ratios help ensure profitable trading over time
entry_price = Decimal("1.1250")  # Planned entry price for trade
stop_loss_price = Decimal("1.1200")  # Stop loss level (50 pips below entry)
risk_reward_ratio = Decimal("2.0")  # 2:1 risk-reward ratio (conservative target)

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
print(
    f"   Success This setup risks {risk_amount * 10000:.0f} pips to make {reward_amount * 10000:.0f} pips"
)
```

## Order Types in FiveTwenty

Different trading situations require different order types. Market orders execute immediately at the current price, useful when you need to enter or exit quickly. Limit orders only execute at your specified price or better, giving you price control at the cost of execution certainty. Stop loss and take profit orders automatically close positions when price targets are reached, essential for risk management and capital preservation.

FiveTwenty provides strongly-typed request models for each order type. These Pydantic models ensure you provide all required fields, validate your parameters, and serialize correctly for the OANDA API. The example below demonstrates how to construct different order types and understand their trade-offs:

```python
import asyncio
from decimal import Decimal

from dotenv import load_dotenv

from fivetwenty import AsyncClient
from fivetwenty.models import (
    InstrumentName,
    LimitOrderRequest,
    MarketOrderRequest,
    StopLossOrderRequest,
    TimeInForce,
)

# Load environment variables from .env file
load_dotenv()


async def main() -> None:
    """
    Tutorial: Working with Order Types in FiveTwenty.

    This example shows how to construct different order request models.
    Each order type serves a different trading purpose and has distinct
    execution characteristics.
    """

    print("=" * 60)
    print("FiveTwenty Order Types Tutorial")
    print("=" * 60)

    # Initialize AsyncClient with automatic environment-based configuration
    async with AsyncClient() as client:
        print(f"\nConnected to: {client.config.environment.name}")
        print(f"Account: {client.account_id}")

        # Step 1: Create market order for immediate position entry
        # Market orders guarantee execution but not price - use for urgent entries
        market_order = MarketOrderRequest(
            instrument=InstrumentName.EUR_USD,
            units=Decimal("1000"),  # Positive = buy, negative = sell
            timeInForce=TimeInForce.FOK,  # Fill or Kill
        )
        print(
            f"\n📊 Market Order: Buy {market_order.units} units of {market_order.instrument}"
        )
        print("   Execution: Immediate at best available price")
        print("   Use case: When speed matters more than price")

        # Step 2: Create limit order for precise entry price control
        # Limit orders control price but don't guarantee execution
        limit_order = LimitOrderRequest(
            instrument=InstrumentName.EUR_USD,
            units=Decimal("1000"),
            price=Decimal("1.0950"),  # Only execute at this price or better
            timeInForce=TimeInForce.GTC,  # Good Till Cancelled
        )
        print(f"\n⏳ Limit Order: Buy {limit_order.units} units at {limit_order.price}")
        print("   Execution: Only if market reaches your target price")
        print("   Use case: When price matters more than speed")

        # Step 3: Create stop loss order for risk management
        # Stop loss orders are essential for limiting losses on open positions
        stop_loss = StopLossOrderRequest(
            tradeID="12345",  # Links to specific open trade
            price=Decimal("1.0900"),  # Triggers closure at this level
            timeInForce=TimeInForce.GTC,
        )
        print(f"\n🛡️  Stop Loss Order: Protect trade 12345 at {stop_loss.price}")
        print("   Purpose: Automatic loss limitation")
        print("   Use case: Always - essential risk management")

        # Step 4: Order type selection guide
        print("\n" + "=" * 60)
        print("Order Type Selection Guide")
        print("=" * 60)
        print("📊 Market Orders: Immediate execution, price not guaranteed")
        print("⏳ Limit Orders: Price guaranteed, execution not guaranteed")
        print("🛡️  Stop Loss: Essential for every trade - limits downside risk")
        print("🎯 Take Profit: Lock in gains at predetermined levels")

        print("\n✓ Tutorial complete - order models created successfully")


# Run the tutorial when this script is executed
if __name__ == "__main__":
    asyncio.run(main())
```

## Quick Setup Test

Before building trading strategies, verify your FiveTwenty installation and API credentials are configured correctly. This test performs three critical checks: authenticating with OANDA's API using your credentials, retrieving your account information to confirm access permissions, and fetching real-time market data to verify data feed connectivity.

Run this example after completing your initial setup (creating a `.env` file with your OANDA token and account ID). If successful, you'll see your account balance, open positions, and current EUR/USD pricing, confirming you're ready to proceed with trading operations:


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
        account_response = await client.accounts.get_account(client.account_id)
        account = account_response["account"]
        print("\nBalance Account Verification:")
        print(f"   Balance: {account.balance} {account.currency}")
        print(f"   Open Trades: {account.open_trade_count}")
        print(f"   Margin Available: {account.margin_available} {account.currency}")

        # Step 4: Test market data access by retrieving real-time pricing
        # Pricing access confirms data feed connectivity and permissions
        pricing = await client.pricing.get_pricing(
            account_id=client.account_id,  # Account context for pricing data
            instruments=[InstrumentName.EUR_USD.value],  # Major pair for reliable data
        )

        # Step 5: Display current market data to confirm successful data access
        # Real-time pricing validates complete API functionality
        price = pricing["prices"][0]
        print("\nData Market Data Verification:")
        print(f"   Instrument: {price.instrument}")
        print(f"   Bid: {price.closeout_bid} (sell price)")
        print(f"   Ask: {price.closeout_ask} (buy price)")
        print(f"   Tradeable: {price.tradeable}")
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
