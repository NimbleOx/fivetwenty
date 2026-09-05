# Forex Trading Concepts for FiveTwenty SDK

Understanding how forex market concepts map to FiveTwenty SDK models and operations.

## Currency Pairs and Instruments

### Instrument Representation

FiveTwenty uses OANDA's instrument naming convention:

<!-- fragment: Demo instrument identification with currency pair analysis -->
```python
# Step 1: Understand OANDA's instrument naming convention for forex pairs
# Each instrument follows BASE_QUOTE format where:
# - BASE: Currency being traded (numerator)
# - QUOTE: Currency used for pricing (denominator)
instrument = "EUR_USD"  # Euro vs US Dollar
print(f"Trading instrument: {instrument}")
print(f"   Base currency: EUR (Euro) - what you're buying/selling")
print(f"   Quote currency: USD (US Dollar) - what you're paying with")
print(f"   Price interpretation: How many USD needed to buy 1 EUR")

# Step 2: Practical examples of different instrument types
# Major pairs involve USD and have highest liquidity
major_pairs = ["EUR_USD", "GBP_USD", "USD_JPY", "USD_CHF"]
print(f"\nMajor pairs (highest liquidity): {major_pairs}")

# Minor pairs (crosses) don't include USD but involve major currencies
minor_pairs = ["EUR_GBP", "GBP_JPY", "EUR_CHF"]
print(f"Minor pairs (cross-currency): {minor_pairs}")

# Exotic pairs include emerging market currencies
exotic_pairs = ["USD_TRY", "EUR_ZAR", "USD_MXN"]
print(f"Exotic pairs (emerging markets): {exotic_pairs}")

# Step 3: Trading implications for different instrument categories
print(f"\nTrading Considerations:")
print(f"   Majors: Tightest spreads, best execution, 24/5 liquidity")
print(f"   Minors: Wider spreads, good liquidity during overlapping sessions")
print(f"   ⚠️ Exotics: Widest spreads, lower liquidity, higher volatility")

```

Key instrument categories:

- **Majors**: EUR_USD, GBP_USD, USD_JPY, USD_CHF, AUD_USD, USD_CAD, NZD_USD
- **Minors**: Cross-currency pairs like EUR_GBP, GBP_JPY
- **Exotics**: Emerging market currencies

## Positions vs Trades in the SDK

### Trade Objects

Individual order executions represented by `Trade` models:

<!-- fragment: Demo individual trade creation with FiveTwenty SDK trade tracking -->
```python
import asyncio
from typing import Any

from fivetwenty import AsyncClient


async def main() -> Any:
    """Example showing individual trades and their tracking in FiveTwenty SDK."""
    # Step 1: Initialize FiveTwenty AsyncClient for trade management
    # AsyncClient provides async interface for all OANDA v20 API operations
    client = AsyncClient()
    account_id = "your-account-id"  # Replace with your actual OANDA account ID
    print(f"Initializing trade management for account: {account_id}")

    # Step 2: Execute multiple market orders to demonstrate individual trade creation
    # Each order execution creates a separate Trade object in OANDA's system
    print(f"\nExecuting multiple EUR_USD orders to demonstrate trade tracking...")

    # First trade: Buy 10,000 EUR (long position establishment)
    trade1 = await client.orders.post_market_order(
            account_id=account_id,
            instrument="EUR_USD",
            units=10000,  # Positive units = buy EUR, sell USD
    )
    print(f"   Trade 1: Buy 10,000 EUR - Order ID: {trade1.order_create_transaction.id}")

    # Second trade: Buy additional 15,000 EUR (position size increase)
    trade2 = await client.orders.post_market_order(
            account_id=account_id,
            instrument="EUR_USD",
            units=15000,  # Additional long position
    )
    print(f"   Trade 2: Buy 15,000 EUR - Order ID: {trade2.order_create_transaction.id}")

    # Third trade: Sell 5,000 EUR (partial position reduction)
    trade3 = await client.orders.post_market_order(
            account_id=account_id,
            instrument="EUR_USD",
            units=-5000,  # Negative units = sell EUR, buy USD
    )
    print(f"   Trade 3: Sell 5,000 EUR - Order ID: {trade3.order_create_transaction.id}")

    # Step 3: Retrieve and analyze all open trades
    # FiveTwenty SDK tracks each trade separately for detailed P/L analysis
    trades = await client.trades.get_open_trades(account_id)
    print(f"\nIndividual Trade Analysis:")
    print(f"   Total open trades: {len(trades)} separate Trade objects")

    # Step 4: Display detailed information for each trade
    for i, trade in enumerate(trades, 1):
            print(f"   Trade {i}:")
            print(f"ID: {trade.id}")
            print(f"Size: {trade.current_units} EUR")
            print(f"Entry: {trade.price}")
            print(f"Unrealized P/L: {trade.unrealized_pl}")
            print(f"Open time: {trade.open_time}")

    # Step 5: Explain trade vs position concept
    print(f"\nKey Concept: Trade vs Position")
    print(f"   Trades: {len(trades)} individual executions tracked separately")
    print(f"   Position: Net exposure = 10,000 + 15,000 - 5,000 = 20,000 EUR long")
    print(f"   Each trade maintains its own entry price and P/L calculation")
    print(f"   Useful for strategy analysis and individual trade performance")


if __name__ == "__main__":
    asyncio.run(main())

```

**Trade Properties**:

- `id` - Unique trade identifier
- `initial_units` - Original trade size
- `current_units` - Current size (after partial closes)
- `price` - Entry price for this specific trade
- `unrealized_pl` - P/L for this individual trade

### Positions (Aggregated View)

A **position** is the net exposure for an instrument:

<!-- fragment: Demo position aggregation with detailed exposure analysis -->
```python
from fivetwenty import AsyncClient


async def check_position() -> None:
    """Example showing position aggregation and net exposure calculation."""
    # Step 1: Initialize client for position analysis
    # Position represents aggregated view of all trades for an instrument
    client = AsyncClient()
    account_id = "your-account-id"
    print(f"Analyzing position aggregation for EUR_USD...")

    # Step 2: Retrieve aggregated position data from FiveTwenty SDK
    # Position object consolidates all individual trades into net exposure
    position = await client.positions.get_position(account_id, "EUR_USD")
    print(f"Retrieved position data for {position.instrument}")

    # Step 3: Analyze long side exposure (buy trades aggregation)
    # Long side represents all EUR purchases (positive units)
    # From trades above: 10,000 + 15,000 = 25,000 EUR purchased
    long_units = int(position.long.units) if position.long.units else 0
    print(f"\nLong Side Analysis:")
    print(f"   Total EUR purchased: {long_units:,} EUR")
    print(f"   Average entry price: {position.long.average_price}")
    print(f"   Unrealized P/L: {position.long.unrealized_pl}")
    print(f"   Source: Aggregation of all buy orders (10k + 15k EUR)")

    # Step 4: Analyze short side exposure (sell trades aggregation)
    # Short side represents all EUR sales (negative units)
    # From trades above: -5,000 EUR sold
    short_units = int(position.short.units) if position.short.units else 0
    print(f"\nShort Side Analysis:")
    print(f"   Total EUR sold: {abs(short_units):,} EUR")
    print(f"   Average entry price: {position.short.average_price}")
    print(f"   Unrealized P/L: {position.short.unrealized_pl}")
    print(f"   Source: Aggregation of all sell orders (5k EUR)")

    # Step 5: Calculate and display net position exposure
    # Net position = Long units + Short units (short is negative)
    net_exposure = long_units + short_units  # short_units is negative
    print(f"\nNet Position Summary:")
    print(f"   Long exposure: {long_units:,} EUR")
    print(f"   Short exposure: {abs(short_units):,} EUR")
    print(f"   Net exposure: {net_exposure:,} EUR ({'long' if net_exposure > 0 else 'short' if net_exposure < 0 else 'flat'})")
    print(f"   Total unrealized P/L: {position.unrealized_pl}")

    # Step 6: Explain practical implications of position aggregation
    print(f"\nPosition vs Trades Key Differences:")
    print(f"   Individual trades: 3 separate Trade objects with distinct entry prices")
    print(f"   Aggregated position: Single net exposure with average pricing")
    print(f"   Risk management: Position shows total instrument exposure")
    print(f"   P/L tracking: Position provides consolidated profit/loss view")
    print(f"   Trading decisions: Use position for overall exposure management")

```

**Position Properties**:

- `instrument` - The currency pair
- `long` - Long side details (PositionSide)
- `short` - Short side details (PositionSide)
- `pl` - Total realized P/L for this instrument
- `unrealized_pl` - Current unrealized P/L

### Visual Example: Trades vs Positions

```text
TRADES (Individual Orders):POSITION (Net Exposure):

Trade 1: Buy 10,000 EUR @ 1.1234   ┌─────────────────────────┐
Trade 2: Buy 15,000 EUR @ 1.1245   │EUR_USD Position    │
Trade 3: Sell 5,000 EUR @ 1.1250   ││
 │  Long Side:   25,000    │
┌─── Individual Trade Records ───┐  │  Short Side:  -5,000    │
│ Trade 1: +10,000 EUR @ 1.1234  │  │  Net:   +20,000    │
│ Trade 2: +15,000 EUR @ 1.1245  │  ││
│ Trade 3:  -5,000 EUR @ 1.1250  │  │  Unrealized P/L: $45.30 │
│   │  └─────────────────────────┘
│ Each tracked separately    │
│ for P/L and management    │
└─────────────────────────────────┘
```

### Why This Distinction Matters

**For Risk Management**:
<!-- fragment: Demo risk calculation with generic type parameters -->
<!-- fragment: Demo comprehensive risk exposure calculation with trade-level and position-level analysis -->
```python
from decimal import Decimal
from typing import Any


def calculate_risk_exposure(trades: list, position: Any, stop_loss_distance: float) -> None:
    """Calculate individual and total risk exposure for comprehensive risk management."""
    print(f"Comprehensive Risk Exposure Analysis")
    print(f"Stop loss distance: {stop_loss_distance} pips")

    # Step 1: Calculate individual trade risk exposure
    # Each trade has separate entry price and risk profile
    print(f"\nIndividual Trade Risk Analysis:")
    total_trade_risk = Decimal("0")

    for i, trade in enumerate(trades, 1):
            # Step 2: Calculate risk for each individual trade
            # Risk = Position size × Stop loss distance × Pip value
            trade_units = abs(int(trade.current_units))  # Use absolute value for risk calculation
            individual_risk = trade_units * stop_loss_distance
            total_trade_risk += Decimal(str(individual_risk))

            print(f"   Trade {trade.id}:")
            print(f"Position size: {trade_units:,} units")
            print(f"Entry price: {trade.price}")
            print(f"⚠️ Risk exposure: {individual_risk:,.0f} USD (if stop triggered)")
            print(f"Risk ratio: {(individual_risk / trade_units * 10000):.1f} pips per 10k units")

    # Step 3: Calculate position-level risk exposure
    # Position aggregates all trades for total instrument exposure
    print(f"\nPosition-Level Risk Analysis:")

    # Total exposure = sum of all long and short positions (absolute values)
    long_units = abs(int(position.long.units)) if position.long.units else 0
    short_units = abs(int(position.short.units)) if position.short.units else 0
    total_exposure = long_units + short_units

    # Net exposure = algebraic sum (short units are negative)
    net_exposure = int(position.long.units or 0) + int(position.short.units or 0)

    # Position-level risk based on net exposure
    net_risk = abs(net_exposure) * stop_loss_distance

    print(f"   Long exposure: {long_units:,} units")
    print(f"   Short exposure: {short_units:,} units")
    print(f"   Total exposure: {total_exposure:,} units")
    print(f"   Net exposure: {net_exposure:,} units ({'LONG' if net_exposure > 0 else 'SHORT' if net_exposure < 0 else 'FLAT'})")
    print(f"   ⚠️ Net risk exposure: {net_risk:,.0f} USD")

    # Step 4: Risk exposure comparison and insights
    print(f"\nRisk Management Insights:")
    print(f"   Sum of individual trade risks: {total_trade_risk:,.0f} USD")
    print(f"   Net position risk: {net_risk:,.0f} USD")

    # Risk interpretation based on exposure type
    if total_trade_risk > Decimal(str(net_risk)):
            print(f"   Hedge effect: Long/short positions offset some risk")
            hedging_benefit = total_trade_risk - net_risk
            print(f"   Risk reduction: {hedging_benefit:,.0f} USD from position offsetting")
    else:
            print(f"   Directional exposure: All trades in same direction")

    # Step 5: Risk management recommendations
    print(f"\nRisk Management Recommendations:")
    if net_risk > 1000:  # Example threshold
            print(f"   ⚠️ HIGH RISK: Consider reducing position size or tightening stops")
    elif net_risk > 500:
            print(f"   MODERATE RISK: Monitor closely and consider profit taking")
    else:
            print(f"   ACCEPTABLE RISK: Within normal risk parameters")

    # Risk per unit analysis for position sizing guidance
    if total_exposure > 0:
            risk_per_unit = net_risk / total_exposure
            print(f"   Risk per unit: {risk_per_unit:.4f} USD per unit")
            print(f"   Use for position sizing: Risk budget ÷ {risk_per_unit:.4f} = max units")

```

**For P/L Tracking**:
<!-- fragment: Demo P/L analysis with generic type parameters -->
<!-- fragment: Demo comprehensive P/L analysis with performance metrics and trading insights -->
```python
from decimal import Decimal
from typing import Any


def analyze_pnl(trades: list, position: Any) -> None:
    """Analyze P/L at different levels for comprehensive trading performance evaluation."""
    print(f"Comprehensive P/L Performance Analysis")

    # Step 1: Individual trade performance analysis
    # Trade-level P/L helps identify which entries were profitable
    print(f"\nIndividual Trade Performance:")
    trade_performance = []
    total_unrealized_pl = Decimal("0")
    winning_trades = 0
    losing_trades = 0

    for i, trade in enumerate(trades, 1):
            # Step 2: Analyze each trade's performance metrics
            trade_pl = Decimal(str(trade.unrealized_pl))
            trade_performance.append((trade.id, trade_pl))
            total_unrealized_pl += trade_pl

            # Categorize trade performance
            if trade_pl > 0:
                winning_trades += 1
                status = "WINNING"
            elif trade_pl < 0:
                losing_trades += 1
                status = "LOSING"
            else:
                status = "BREAKEVEN"

            # Calculate trade-specific metrics
            entry_price = Decimal(str(trade.price))
            current_units = int(trade.current_units)
            trade_size_usd = abs(current_units) * entry_price  # Approximate position value

            print(f"   Trade {trade.id} ({status}):")
            print(f"Size: {current_units:,} units")
            print(f"Entry: {entry_price}")
            print(f"P/L: {trade_pl:+.2f} USD")
            print(f"Return: {(trade_pl / trade_size_usd * 100):+.3f}%")
            print(f"Open since: {trade.open_time}")

    # Step 3: Trade performance statistics
    total_trades = len(trades)
    win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0

    print(f"\nTrade Performance Statistics:")
    print(f"   Total trades: {total_trades}")
    print(f"   Winning trades: {winning_trades}")
    print(f"   Losing trades: {losing_trades}")
    print(f"   Win rate: {win_rate:.1f}%")
    print(f"   Sum of individual P/L: {total_unrealized_pl:+.2f} USD")

    # Step 4: Position-level P/L analysis
    # Position P/L shows total instrument exposure performance
    print(f"\nPosition-Level Analysis:")
    total_instrument_pl = Decimal(str(position.unrealized_pl))

    # Calculate position metrics
    long_units = int(position.long.units) if position.long.units else 0
    short_units = int(position.short.units) if position.short.units else 0
    net_exposure = long_units + short_units  # short_units is negative

    print(f"   Long side P/L: {position.long.unrealized_pl} USD")
    print(f"   Short side P/L: {position.short.unrealized_pl} USD")
    print(f"   Total position P/L: {total_instrument_pl:+.2f} USD")
    print(f"   Net exposure: {net_exposure:,} units")

    # Step 5: P/L reconciliation and analysis
    print(f"\nP/L Reconciliation:")
    pl_difference = total_unrealized_pl - total_instrument_pl

    if abs(pl_difference) < Decimal("0.01"):  # Accounting for rounding
            print(f"   P/L matches: Trade sum = Position total")
    else:
            print(f"   ⚠️ P/L difference: {pl_difference:+.2f} USD (rounding or timing)")

    # Step 6: Performance insights and recommendations
    print(f"\nPerformance Insights:")

    if total_instrument_pl > 0:
            print(f"   Position Status: PROFITABLE (+{total_instrument_pl:.2f} USD)")
            if win_rate >= 60:
                print(f"   Strong Strategy: High win rate ({win_rate:.1f}%) with profits")
            else:
                print(f"   Large Winners: Lower win rate but profitable overall")
    elif total_instrument_pl < 0:
            print(f"   ⚠️ Position Status: LOSING ({total_instrument_pl:+.2f} USD)")
            if win_rate < 40:
                print(f"   Strategy Review: Low win rate ({win_rate:.1f}%) and losses")
            else:
                print(f"   Large Losers: Good win rate but big losing trades")
    else:
            print(f"   Position Status: BREAKEVEN")

    # Risk-adjusted performance metrics
    if abs(net_exposure) > 0:
            pl_per_unit = total_instrument_pl / abs(net_exposure)
            print(f"   P/L per unit: {pl_per_unit:+.5f} USD/unit")
            print(f"   Use for sizing: Scales with position size")

    # Step 7: Trading recommendations based on performance
    print(f"\nTrading Recommendations:")
    if total_instrument_pl > 100:  # Arbitrary threshold
            print(f"   Consider profit taking: Strong unrealized gains")
    elif total_instrument_pl < -100:
            print(f"   ⚠️ Review stop losses: Significant unrealized losses")

    if win_rate < 50 and total_instrument_pl < 0:
            print(f"   Strategy analysis needed: Both win rate and P/L are poor")
    elif win_rate > 70:
            print(f"   Strong entry timing: High win rate indicates good signals")

```

---

## Order Types and Market Mechanics

### Market Orders

Execute immediately at current market price:

<!-- fragment: Demo market order execution with immediate fill analysis -->
```python
import asyncio
from fivetwenty import AsyncClient


async def place_market_order() -> None:
    """Place a market order example with comprehensive execution analysis."""
    # Step 1: Initialize FiveTwenty client for immediate order execution
    # Market orders prioritize speed over price - execute at current market rates
    client = AsyncClient()
    account_id = "your-account-id"
    print(f"Initializing market order execution for EUR_USD...")

    # Step 2: Prepare market order parameters
    # Market orders execute immediately at best available market price
    instrument = "EUR_USD"
    order_size = 10000  # Buy 10,000 EUR (standard mini lot)
    print(f"Order details: {order_size:,} units of {instrument}")
    print(f"Order type: MARKET (immediate execution priority)")

    try:
            # Step 3: Execute market order through FiveTwenty SDK
            # post_market_order() sends order to OANDA for immediate execution
            print(f"\nExecuting market order...")
            order = await client.orders.post_market_order(
                account_id=account_id,
                instrument=instrument,
                units=order_size,  # Positive = buy EUR, negative = sell EUR
            )
            print(f"Market order submitted successfully")

            # Step 4: Analyze order fill results
            # Market orders typically fill immediately with fill transaction
            if order.order_fill_transaction:
                # Extract fill details for analysis
                fill_price = order.order_fill_transaction.price
                fill_time = order.order_fill_transaction.time
                trade_id = order.order_fill_transaction.trade_opened.trade_id if order.order_fill_transaction.trade_opened else "N/A"

                print(f"\nOrder Fill Analysis:")
                print(f"   Fill price: {fill_price}")
                print(f"   Fill time: {fill_time}")
                print(f"   Trade ID: {trade_id}")
                print(f"   Position: {order_size:,} EUR at {fill_price}")
                print(f"   Status: FILLED (immediate execution achieved)")

                # Step 5: Calculate immediate trading costs
                # Market orders pay the spread immediately
                print(f"\nTrading Cost Analysis:")
                print(f"   ⚠️ Spread cost: Paid ask price for immediate execution")
                print(f"   Immediate P/L: Negative due to bid-ask spread")
                print(f"   Breakeven: Price must move above entry + spread")

            else:
                # Rare case: market order didn't fill immediately
                print(f"\n⚠️ Unusual: Market order created but not filled immediately")
                print(f"   Possible causes: Market halt, extreme volatility, or system issues")
                print(f"   Order ID: {order.order_create_transaction.id}")

            # Step 6: Market order advantages and considerations
            print(f"\nMarket Order Characteristics:")
            print(f"   Advantages: Immediate execution, no 'missing the move' risk")
            print(f"   ⚠️ Considerations: Price uncertainty, spread costs, slippage risk")
            print(f"   Best for: High liquidity instruments, small sizes, urgent execution")

    except Exception as e:
            # Step 7: Handle market order execution errors
            print(f"\nMarket order execution failed: {e}")
            print(f"Common issues: Insufficient margin, market closed, invalid parameters")
            print(f"Recovery: Check account balance, verify market hours, adjust position size")


if __name__ == "__main__":
    asyncio.run(place_market_order())

```

**Use Cases**:
- When you want immediate execution
- High liquidity instruments
- Small position sizes relative to market depth

### Limit Orders

Execute only at specified price or better:

<!-- fragment: Demo limit order placement with price condition analysis -->
```python
import asyncio
from decimal import Decimal
from fivetwenty import AsyncClient


async def place_limit_order() -> None:
    """Place a limit order example with comprehensive price strategy analysis."""
    # Step 1: Initialize client for precise price-based order execution
    # Limit orders prioritize price over timing - only execute at specified price or better
    client = AsyncClient()
    account_id = "your-account-id"
    print(f"Initializing limit order placement for EUR_USD...")

    # Step 2: Analyze current market conditions for limit order strategy
    # Limit orders require understanding of current price vs desired price
    current_market_price = Decimal("1.1050")  # Example current EUR_USD price
    desired_entry_price = Decimal("1.1000")  # Target entry price (below market)
    price_difference = current_market_price - desired_entry_price

    print(f"\nMarket Analysis for Limit Order:")
    print(f" Current market price: {current_market_price}")
    print(f" Desired entry price: {desired_entry_price}")
    print(f" Price difference: {price_difference} ({price_difference * 10000:.0f} pips below market)")
    print(f"   Note: Strategy: Wait for price to drop to our favorable level")

    # Step 3: Set up limit order parameters
    # Buy limit below market = waiting for price to fall to our level
    instrument = "EUR_USD"
    order_size = 10000  # Standard position size
    limit_price = desired_entry_price

    print(f"\nLimit Order Configuration:")
    print(f"   Instrument: {instrument}")
    print(f" Position size: {order_size:,} units (Buy {order_size / 1000:.0f}k EUR)")
    print(f" Limit price: {limit_price} (execute only at this price or better)")
    print(f"   Order type: BUY LIMIT (below market - value seeking)")

    try:
            # Step 4: Place limit order through FiveTwenty SDK
            # post_limit_order() creates pending order waiting for price condition
            print(f"\nPlacing limit order...")
            limit_order = await client.orders.post_limit_order(
                account_id=account_id,
                instrument=instrument,
                units=order_size,
                price=limit_price,  # Will only buy at 1.1000 or lower (better price)
            )
            print(f" Limit order placed successfully")

            # Step 5: Analyze limit order creation details
            order_id = limit_order.order_create_transaction.id
            order_time = limit_order.order_create_transaction.time

            print(f"\nOrder Details:")
            print(f" Order ID: {order_id}")
            print(f"   Created: {order_time}")
            print(f"   Status: PENDING (waiting for price condition)")
            print(f" Execution condition: Market price ≤ {limit_price}")

            # Step 6: Explain limit order execution scenarios
            print(f"\nExecution Scenarios:")
            print(f" WILL EXECUTE if:")
            print(f"• EUR_USD drops to {limit_price} or lower")
            print(f"• Market becomes more favorable than our limit")
            print(f"• Sufficient liquidity available at limit price")
            print(f"   Error: WILL NOT EXECUTE if:")
            print(f"• Price stays above {limit_price}")
            print(f"• Price gaps below our limit (may get better fill)")
            print(f"• Order expires or is manually cancelled")

            # Step 7: Strategic implications of limit order
            print(f"\nNote: Limit Order Strategy Implications:")
            print(f" Patience required: May wait indefinitely for price")
            print(f" Price certainty: Know maximum price paid in advance")
            print(f"   ⚠️ Opportunity risk: May miss move if price doesn't reach limit")
            print(f" Value focus: Only execute at favorable pricing")

            # Step 8: Market condition analysis for limit success
            print(f"\nMarket Conditions Favoring Limit Fill:")
            print(f"   Ranging market: Price oscillates around current levels")
            print(f" Bearish momentum: Downward pressure toward limit")
            print(f"   Economic events: News that might push price to limit")
            print(f"   Time decay: Longer time horizon increases fill probability")

    except Exception as e:
            # Step 9: Handle limit order placement errors
            print(f"\nError: Limit order placement failed: {e}")
            print(f" Common issues: Invalid price, insufficient margin for pending order")
            print(f"Recovery: Verify price format, check account limits, adjust parameters")


if __name__ == "__main__":
    asyncio.run(place_limit_order())

```

**Market Scenarios**:

- **Buy Limit Below Market**: Wait for price to drop to your level
- **Sell Limit Above Market**: Wait for price to rise to your level
- **No Fill Risk**: Order may never execute if price doesn't reach your level

### Stop Orders

Triggered when market reaches specified price:

<!-- fragment: Demo stop order placement with breakout strategy analysis -->
```python
import asyncio
from decimal import Decimal
from fivetwenty import AsyncClient


async def place_stop_order() -> None:
    """Place a stop order example with comprehensive breakout strategy analysis."""
    # Step 1: Initialize client for momentum-based order execution
    # Stop orders activate when market reaches trigger price - used for breakout strategies
    client = AsyncClient()
    account_id = "your-account-id"
    print(f" Initializing stop order placement for breakout strategy...")

    # Step 2: Analyze market setup for stop order strategy
    # Stop orders capture momentum when price breaks through key levels
    current_market_price = Decimal("1.1050")  # Current EUR_USD price
    stop_trigger_price = Decimal("1.1100")  # Breakout level above market
    breakout_distance = stop_trigger_price - current_market_price

    print(f"\nBreakout Strategy Analysis:")
    print(f" Current market price: {current_market_price}")
    print(f" Stop trigger price: {stop_trigger_price}")
    print(f"   Breakout distance: {breakout_distance} ({breakout_distance * 10000:.0f} pips above market)")
    print(f"   Note: Strategy: Buy on upward momentum through resistance")

    # Step 3: Configure stop order parameters for breakout capture
    # Stop buy above market = momentum/breakout strategy
    instrument = "EUR_USD"
    order_size = 10000  # Position size for breakout trade
    stop_price = stop_trigger_price

    print(f"\nStop Order Configuration:")
    print(f"   Instrument: {instrument}")
    print(f" Position size: {order_size:,} units")
    print(f"   Stop price: {stop_price} (trigger level)")
    print(f"   Order type: STOP BUY (above market - momentum strategy)")
    print(f" Execution: Becomes market order when price hits {stop_price}")

    try:
            # Step 4: Place stop order through FiveTwenty SDK
            # post_stop_order() creates conditional order waiting for momentum trigger
            print(f"\nPlacing stop order for breakout capture...")
            stop_order = await client.orders.post_stop_order(
                account_id=account_id,
                instrument=instrument,
                units=order_size,
                price=stop_price,  # Buy if price breaks above 1.1100
            )
            print(f" Stop order placed successfully")

            # Step 5: Analyze stop order creation details
            order_id = stop_order.order_create_transaction.id
            order_time = stop_order.order_create_transaction.time

            print(f"\nOrder Details:")
            print(f" Order ID: {order_id}")
            print(f"   Created: {order_time}")
            print(f"   Status: PENDING (waiting for breakout trigger)")
            print(f"   Trigger condition: Market price ≥ {stop_price}")
            print(f"   Becomes: MARKET ORDER when triggered")

            # Step 6: Explain stop order activation scenarios
            print(f"\nActivation Scenarios:")
            print(f" WILL TRIGGER if:")
            print(f"• EUR_USD rises to {stop_price} or higher")
            print(f"• Price gaps above trigger level (may cause slippage)")
            print(f"• Strong upward momentum breaks resistance")
            print(f"   Error: WILL NOT TRIGGER if:")
            print(f"• Price stays below {stop_price}")
            print(f"• Resistance level holds and price reverses")
            print(f"• Order is cancelled before breakout occurs")

            # Step 7: Strategic implications of stop order breakout strategy
            print(f"\nNote: Breakout Strategy Implications:")
            print(f"   Momentum capture: Enter on confirmed upward movement")
            print(f"   ⚠️ Slippage risk: May fill above stop price in fast markets")
            print(f" Trend following: Assumes breakout continues in same direction")
            print(f" False breakout risk: Price may reverse after trigger")

            # Step 8: Market conditions favoring stop order success
            print(f"\nOptimal Market Conditions:")
            print(f" Strong trend: Established upward momentum")
            print(f" High volume: Institutional buying supporting breakout")
            print(f"   Technical setup: Clear resistance level at {stop_price}")
            print(f"   Fundamental catalyst: News supporting EUR strength")

            # Step 9: Risk management considerations
            print(f"\nRisk Management for Breakout Trade:")
            print(f"   ⚠️ Consider stop loss: Place below breakout level if triggered")
            print(f" Position sizing: Account for potential slippage")
            print(f"   Time limits: Consider order expiration to avoid stale setups")
            print(f"   Confirmation: Look for volume confirmation on breakout")

    except Exception as e:
            # Step 10: Handle stop order placement errors
            print(f"\nError: Stop order placement failed: {e}")
            print(f" Common issues: Invalid trigger price, margin requirements")
            print(f"Recovery: Verify price above market, check account capacity")


if __name__ == "__main__":
    asyncio.run(place_stop_order())

```


**Common Strategies**:

- **Stop Buy Above Market**: Momentum/breakout trading
- **Stop Sell Below Market**: Trend following on breaks
- **Becomes Market Order**: When triggered, executes at current market price

---

## Margin and Leverage

### How Forex Margin Works

Unlike stocks, forex trading uses **leverage** - you can control large positions with small amounts:
```text
Leverage & Margin Example
    (30:1 Leverage)

┌─────────────────────────┐┌──────────────────────────┐
│Your Account   ││    Your Position    │
││────▶│ │
│  Balance:   $10,000││  Size: $300,000 EUR_USD  │
│  Used: $3,333 ││ │
│  Available: $6,667 ││  Margin Required: 3.33%  │
│││  = $300,000 × 0.0333│
│  Risk: If position ││  = $10,000 ÷ 30│
│  moves 333 pips    ││  = $3,333 │
│  against you = 100%││ │
│  account loss ││  Control: 30× your money │
└─────────────────────────┘└──────────────────────────┘

⚠️  Higher leverage = Higher risk & reward
```

<!-- fragment: Demo margin analysis with leverage impact and risk assessment -->
```python
from decimal import Decimal
from fivetwenty import AsyncClient
import asyncio

# Setup example variables for comprehensive margin analysis
client = AsyncClient()
account_id = "your-account-id"


async def main() -> None:
    """Check your account margin situation with comprehensive leverage analysis."""
    print(f" Comprehensive Margin and Leverage Analysis")

    # Step 1: Retrieve account margin information from FiveTwenty SDK
    # Account object contains all margin-related data for risk management
    account = await client.accounts.get_account(account_id)
    print(f"\nAccount Margin Status:")

    # Step 2: Analyze core margin metrics
    # These metrics determine trading capacity and risk exposure
    account_balance = Decimal(str(account.balance))
    margin_used = Decimal(str(account.margin_used))
    margin_available = Decimal(str(account.margin_available))

    print(f" Account Balance: {account_balance} USD (your actual money)")
    print(f"   Margin Used: {margin_used} USD (tied up in positions)")
    print(f" Margin Available: {margin_available} USD (available for new trades)")

    # Step 3: Calculate margin utilization ratio
    # High utilization indicates elevated risk exposure
    if account_balance > 0:
            margin_utilization = (margin_used / account_balance) * 100
            print(f" Margin Utilization: {margin_utilization:.1f}%")

            # Risk assessment based on utilization
            if margin_utilization > 80:
                risk_level = "HIGH RISK"
                recommendation = "Consider reducing positions"
            elif margin_utilization > 50:
                risk_level = "MODERATE RISK"
                recommendation = "Monitor closely"
            else:
                risk_level = "LOW RISK"
                recommendation = "Healthy margin levels"

            print(f"   ⚠️ Risk Level: {risk_level}")
            print(f"   Recommendation: {recommendation}")

    # Step 4: Demonstrate margin calculation with real example
    # OANDA typically uses 30:1 leverage (3.33% margin requirement)
    print(f"\nMargin Calculation Example:")

    position_size = 100000  # 100,000 EUR_USD (1 standard lot)
    leverage_ratio = 30  # 30:1 leverage typical for major pairs
    margin_rate = Decimal("1") / Decimal(str(leverage_ratio))  # 1/30 = 3.33%

    required_margin = position_size * margin_rate

    print(f" Example Position: {position_size:,} EUR_USD")
    print(f"   Leverage: {leverage_ratio}:1 (margin rate: {margin_rate * 100:.2f}%)")
    print(f" Required Margin: {position_size:,} × {margin_rate:.4f} = {required_margin:,.0f} USD")
    print(f" Position Value: ~{position_size:,} USD (at 1.0000 EUR_USD)")
    print(f" Control Ratio: ${position_size:,} position with ${required_margin:,.0f} margin")

    # Step 5: Calculate maximum position size based on available margin
    if margin_available > 0:
            max_position_size = int(margin_available / margin_rate)
            max_lots = max_position_size / 100000

            print(f"\nMaximum Position Capacity:")
            print(f" Available margin: {margin_available} USD")
            print(f" Max position size: {max_position_size:,} units")
            print(f"   Max standard lots: {max_lots:.2f} lots")
            print(f"   ⚠️ Conservative size: {max_position_size // 2:,} units (50% margin usage)")

    # Step 6: Analyze leverage impact on risk
    print(f"\nLeverage Risk Analysis:")

    # Calculate risk per pip for different position sizes
    pip_values = {
            10000: 1.0,  # Mini lot: $1 per pip
            100000: 10.0,  # Standard lot: $10 per pip
            1000000: 100.0,  # 10 standard lots: $100 per pip
    }

    print(f" Pip Value Analysis (EUR_USD):")
    for size, pip_value in pip_values.items():
            margin_required = size * margin_rate
            risk_percent_per_pip = (pip_value / account_balance) * 100 if account_balance > 0 else 0

            print(f"{size:,} units: ${pip_value}/pip, ${margin_required:,.0f} margin, {risk_percent_per_pip:.3f}% risk/pip")

    # Step 7: Margin call and stop-out warnings
    print(f"\nMargin Safety Thresholds:")

    # OANDA typically has margin call at 100% and stop-out at 50%
    margin_call_threshold = account_balance  # 100% - margin call warning
    stop_out_threshold = account_balance * Decimal("0.5")  # 50% - automatic position closure

    current_equity = account_balance + Decimal(str(account.unrealized_pl))

    print(f" Current equity: {current_equity} USD (balance + unrealized P/L)")
    print(f"   ⚠️ Margin call level: {margin_call_threshold} USD (100% of balance)")
    print(f"   Stop-out level: {stop_out_threshold} USD (50% of balance)")

    # Calculate distance to danger levels
    if margin_used > 0:
            equity_to_margin_call = current_equity - margin_used
            equity_to_stop_out = current_equity - stop_out_threshold

            print(f" Distance to margin call: {equity_to_margin_call:+.2f} USD")
            print(f" Distance to stop-out: {equity_to_stop_out:+.2f} USD")

            if equity_to_margin_call < 100:
                print(f"   Alert WARNING: Approaching margin call territory!")
            if equity_to_stop_out < 50:
                print(f"   DANGER: Risk of automatic position closure!")

    # Step 8: Best practices for margin management
    print(f"\nNote: Margin Management Best Practices:")
    print(f" Keep margin usage below 30% for safety buffer")
    print(f"   Monitor unrealized P/L impact on equity")
    print(f" Size positions based on risk, not maximum leverage")
    print(f"   ⚠️ Understand that leverage amplifies both gains and losses")
    print(f"   Use stop losses to limit downside risk")


if __name__ == "__main__":
    asyncio.run(main())

```

**Key Concepts**:

- **Leverage**: Allows you to trade larger positions than your account balance
- **Margin Used**: Capital reserved for open positions
- **Free Margin**: Available for new positions
- **Margin Call**: When margin used approaches account balance

### SDK Margin Information

<!-- fragment: Demo multi-level margin analysis with position and trade breakdown -->
```python
from decimal import Decimal
from fivetwenty import AsyncClient
import asyncio

# Setup example variables for detailed margin analysis
client = AsyncClient()
account_id = "your-account-id"


async def main() -> None:
    """Check account margin levels across multiple analysis dimensions."""
    print(f" Multi-Level Margin Analysis Dashboard")

    # Step 1: Account-level margin overview
    # Provides portfolio-wide margin utilization and risk assessment
    account = await client.accounts.get_account(account_id)
    account_balance = Decimal(str(account.balance))
    margin_used = Decimal(str(account.margin_used))

    print(f"\nAccount-Level Margin Overview:")
    print(f" Total Balance: {account_balance} USD")
    print(f"   Total Margin Used: {margin_used} USD")

    # Calculate and categorize overall margin utilization
    if account_balance > 0:
            margin_utilization = (margin_used / account_balance) * 100
            print(f" Overall Utilization: {margin_utilization:.1f}%")

            # Risk categorization with visual indicators
            if margin_utilization > 75:
                risk_status = "CRITICAL - Reduce exposure immediately"
            elif margin_utilization > 50:
                risk_status = "HIGH - Monitor closely"
            elif margin_utilization > 25:
                risk_status = "🟠 MODERATE - Normal operations"
            else:
                risk_status = "LOW - Conservative positioning"

            print(f"   ⚠️ Risk Status: {risk_status}")

    # Step 2: Position-level margin breakdown
    # Shows margin allocation across different currency pairs
    print(f"\nPosition-Level Margin Breakdown:")
    positions = await client.positions.get_open_positions(account_id)

    total_position_margin = Decimal("0")
    position_count = 0

    for position in positions:
            # Analyze margin usage for each instrument position
            position_margin = Decimal(str(position.margin_used)) if position.margin_used else Decimal("0")
            total_position_margin += position_margin
            position_count += 1

            # Calculate position's share of total margin
            margin_percentage = (position_margin / margin_used * 100) if margin_used > 0 else 0

            # Determine position direction and size
            long_units = int(position.long.units) if position.long.units else 0
            short_units = int(position.short.units) if position.short.units else 0
            net_units = long_units + short_units  # short_units is negative

            direction = "LONG" if net_units > 0 else "SHORT" if net_units < 0 else "FLAT"

            print(f" {position.instrument}:")
            print(f"Margin used: {position_margin} USD ({margin_percentage:.1f}% of total)")
            print(f"   Net position: {abs(net_units):,} units {direction}")
            print(f"   Unrealized P/L: {position.unrealized_pl} USD")

            # Position-specific margin efficiency
            if abs(net_units) > 0:
                margin_per_unit = position_margin / abs(net_units)
                print(f"   Margin efficiency: {margin_per_unit:.5f} USD per unit")

    print(f"   Total positions: {position_count}")
    print(f" Sum of position margins: {total_position_margin} USD")

    # Step 3: Individual trade margin analysis
    # Provides granular view of margin allocation per trade execution
    print(f"\nIndividual Trade Margin Analysis:")
    trades = await client.trades.get_open_trades(account_id)

    total_trade_margin = Decimal("0")
    trade_margin_distribution = {}

    for trade in trades:
            # Analyze margin usage for each individual trade
            trade_margin = Decimal(str(trade.margin_used)) if trade.margin_used else Decimal("0")
            total_trade_margin += trade_margin

            # Group trades by instrument for distribution analysis
            instrument = trade.instrument
            if instrument not in trade_margin_distribution:
                trade_margin_distribution[instrument] = {"trades": 0, "margin": Decimal("0")}

            trade_margin_distribution[instrument]["trades"] += 1
            trade_margin_distribution[instrument]["margin"] += trade_margin

            # Calculate trade-specific metrics
            trade_units = int(trade.current_units)
            trade_direction = "BUY" if trade_units > 0 else "SELL"

            print(f"   Trade {trade.id}:")
            print(f"Instrument: {instrument}")
            print(f"Margin used: {trade_margin} USD")
            print(f"   Size: {abs(trade_units):,} units ({trade_direction})")
            print(f"   Entry price: {trade.price}")
            print(f"   Unrealized P/L: {trade.unrealized_pl} USD")

            # Trade efficiency metrics
            if abs(trade_units) > 0:
                pl_per_margin = trade.unrealized_pl / trade_margin if trade_margin > 0 else 0
                print(f"   P/L per margin USD: {pl_per_margin:+.3f}")

    # Step 4: Margin distribution summary
    print(f"\nMargin Distribution Summary:")
    print(f" Total individual trade margins: {total_trade_margin} USD")
    print(f"   Number of open trades: {len(trades)}")

    if len(trades) > 0:
            avg_margin_per_trade = total_trade_margin / len(trades)
            print(f" Average margin per trade: {avg_margin_per_trade:.2f} USD")

    # Step 5: Instrument-wise margin concentration
    print(f"\nMargin Concentration by Instrument:")
    for instrument, data in trade_margin_distribution.items():
            concentration = (data["margin"] / total_trade_margin * 100) if total_trade_margin > 0 else 0
            avg_margin_per_trade = data["margin"] / data["trades"] if data["trades"] > 0 else 0

            print(f"   {instrument}:")
            print(f"   Trades: {data['trades']}")
            print(f"Total margin: {data['margin']} USD")
            print(f"   Concentration: {concentration:.1f}% of total margin")
            print(f"   Avg per trade: {avg_margin_per_trade:.2f} USD")

    # Step 6: Margin efficiency and optimization insights
    print(f"\nNote: Margin Optimization Insights:")

    # Check for margin discrepancies
    margin_difference = abs(total_trade_margin - total_position_margin)
    if margin_difference > Decimal("0.01"):
            print(f"   ⚠️ Margin calculation difference: {margin_difference} USD")
            print(f"(Normal for complex positions with netting)")

    # Provide actionable recommendations
    print(f"   Optimization Opportunities:")
    if position_count > 5:
            print(f"• Consider consolidating {position_count} positions to reduce margin spread")

    if margin_utilization > 50:
            print(f"• High utilization ({margin_utilization:.1f}%) - consider position reduction")

    diversification_score = len(trade_margin_distribution) / max(len(trades), 1)
    if diversification_score < 0.3:
            print(f"• Low diversification - margin concentrated in few instruments")

    print(f"• Monitor unrealized P/L impact on margin availability")
    print(f"• Consider correlation between positions for risk assessment")


if __name__ == "__main__":
    asyncio.run(main())

```

---

## Profit and Loss Calculations

### Unrealized vs. Realized P/L

**Unrealized P/L**: Potential profit/loss on open positions
**Realized P/L**: Actual profit/loss from closed trades

<!-- fragment: Demo comprehensive P/L tracking with unrealized vs realized analysis -->
```python
async def check_pnl() -> None:
    """Check unrealized and realized P/L with comprehensive analysis."""
    # Step 1: Initialize client for P/L analysis across all levels
    # P/L tracking is crucial for performance evaluation and risk management
    client = AsyncClient()
    account_id = "your-account-id"
    print(f" Comprehensive Profit & Loss Analysis")

    # Step 2: Account-level unrealized P/L analysis
    # Unrealized P/L represents paper profits/losses on open positions
    account = await client.accounts.get_account(account_id)
    current_unrealized = account.unrealized_pl  # All open positions combined
    account_balance = account.balance
    total_equity = account_balance + current_unrealized

    print(f"\nAccount-Level P/L Overview:")
    print(f" Account balance: {account_balance} USD (cash)")
    print(f" Unrealized P/L: {current_unrealized:+} USD (paper profit/loss)")
    print(f" Total equity: {total_equity:+.2f} USD (balance + unrealized)")

    # Calculate portfolio performance metrics
    if account_balance > 0:
            unrealized_return = (current_unrealized / account_balance) * 100
            equity_return = ((total_equity - account_balance) / account_balance) * 100

            print(f" Unrealized return: {unrealized_return:+.2f}% of balance")
            print(f" Total portfolio return: {equity_return:+.2f}%")

            # Risk assessment based on P/L
            if abs(unrealized_return) > 10:
                risk_status = "Alert HIGH VOLATILITY - Monitor closely"
            elif abs(unrealized_return) > 5:
                risk_status = "MODERATE RISK - Normal trading range"
            else:
                risk_status = "Success STABLE - Low volatility"

            print(f"   ⚠️ Risk status: {risk_status}")

    # Step 3: Individual position unrealized P/L breakdown
    # Position-level P/L shows performance by currency pair
    print(f"\nPosition-Level P/L Breakdown:")

    try:
            position = await client.positions.get_position(account_id, "EUR_USD")
            eur_usd_unrealized = position.unrealized_pl

            # Analyze long and short side performance separately
            long_pl = position.long.unrealized_pl if position.long.unrealized_pl else 0
            short_pl = position.short.unrealized_pl if position.short.unrealized_pl else 0
            long_units = int(position.long.units) if position.long.units else 0
            short_units = int(position.short.units) if position.short.units else 0

            print(f"   EUR_USD Position Analysis:")
            print(f"   Long side P/L: {long_pl:+} USD ({long_units:,} units)")
            print(f"   Short side P/L: {short_pl:+} USD ({abs(short_units):,} units)")
            print(f"   Total position P/L: {eur_usd_unrealized:+} USD")

            # Calculate position efficiency metrics
            total_units = abs(long_units) + abs(short_units)
            if total_units > 0:
                pl_per_unit = eur_usd_unrealized / total_units
                print(f"   P/L per unit: {pl_per_unit:+.5f} USD/unit")

            # Position P/L as percentage of account
            if account_balance > 0:
                position_impact = (eur_usd_unrealized / account_balance) * 100
                print(f"📌 Account impact: {position_impact:+.2f}% of balance")

    except Exception as e:
            print(f"   ⚠️ No EUR_USD position found: {e}")

    # Step 4: Individual trade realized P/L analysis
    # Realized P/L shows actual profits/losses from closed portions
    print(f"\nIndividual Trade P/L Analysis:")
    trades = await client.trades.get_open_trades(account_id)

    total_trade_unrealized = 0
    total_trade_realized = 0
    profitable_trades = 0
    losing_trades = 0

    for trade in trades:
            trade_unrealized = trade.unrealized_pl
            trade_realized = trade.realized_pl if trade.realized_pl else Decimal("0")
            trade_units = int(trade.current_units)
            trade_direction = "LONG" if trade_units > 0 else "SHORT"

            total_trade_unrealized += trade_unrealized
            total_trade_realized += trade_realized

            # Categorize trade performance
            if trade_unrealized > 0:
                profitable_trades += 1
                status = "Success PROFITABLE"
            elif trade_unrealized < 0:
                losing_trades += 1
                status = "Error LOSING"
            else:
                status = "Scale BREAKEVEN"

            print(f"   Trade {trade.id} ({status}):")
            print(f"Instrument: {trade.instrument}")
            print(f"   Direction: {trade_direction} ({abs(trade_units):,} units)")
            print(f"   Entry price: {trade.price}")
            print(f"   Unrealized P/L: {trade_unrealized:+.2f} USD")
            print(f"   Realized P/L: {trade_realized:+.2f} USD")

            # Calculate trade performance metrics
            if abs(trade_units) > 0:
                pl_per_unit = trade_unrealized / abs(trade_units)
                print(f"   Performance: {pl_per_unit:+.5f} USD per unit")

    # Step 5: Trade performance statistics
    total_trades = len(trades)
    if total_trades > 0:
    win_rate = (profitable_trades / total_trades) * 100
    avg_unrealized_pl = total_trade_unrealized / total_trades
    avg_realized_pl = total_trade_realized / total_trades

    print(f"\nTrade Performance Statistics:")
    print(f" Total open trades: {total_trades}")
    print(f" Profitable trades: {profitable_trades} ({win_rate:.1f}% win rate)")
    print(f"   Error: Losing trades: {losing_trades}")
    print(f" Total unrealized: {total_trade_unrealized:+.2f} USD")
    print(f" Total realized: {total_trade_realized:+.2f} USD")
    print(f" Avg unrealized per trade: {avg_unrealized_pl:+.2f} USD")
    print(f" Avg realized per trade: {avg_realized_pl:+.2f} USD")

    # Step 6: P/L reconciliation and data integrity check
    print(f"\nP/L Reconciliation Check:")
    account_vs_trades_diff = current_unrealized - total_trade_unrealized

    if abs(account_vs_trades_diff) < Decimal("0.01"):  # Allow for rounding
    print(f" P/L reconciliation: Account and trade totals match")
    else:
    print(f"   ⚠️ P/L difference: {account_vs_trades_diff:+.2f} USD")
    print(f"(May be due to rounding, timing, or multiple instruments)")

    # Step 7: Performance insights and recommendations
    print(f"\nNote: Performance Insights & Recommendations:")

    if current_unrealized > 0:
    print(f" Overall Position: PROFITABLE (+{current_unrealized} USD)")
    if current_unrealized > account_balance * Decimal("0.05"):  # 5% gain
    print(f"   Strong performance - consider profit taking")
    elif current_unrealized < 0:
    print(f" Overall Position: LOSING ({current_unrealized} USD)")
    if abs(current_unrealized) > account_balance * Decimal("0.05"):  # 5% loss
    print(f"⚠️ Significant losses - review risk management")
    else:
    print(f" Overall Position: BREAKEVEN")

    # Win rate analysis
    if total_trades > 0:
    if win_rate >= 60:
    print(f" High win rate ({win_rate:.1f}%) - good entry timing")
    elif win_rate <= 40:
    print(f" Low win rate ({win_rate:.1f}%) - review strategy")

    # Risk management recommendations
    if abs(current_unrealized) > account_balance * Decimal("0.1"):  # 10% of balance
    print(f"   ⚠️ High P/L volatility - consider position sizing review")

    print(f"   Next steps: Monitor closely, consider stop losses, review correlation")

```

### P/L Calculation Example

<!-- fragment: Demo P/L calculation mechanics with step-by-step breakdown -->
```python
import asyncio
from decimal import Decimal
from fivetwenty import AsyncClient


async def main():
    """Demonstrate P/L calculation mechanics with detailed breakdown."""
    print(f" P/L Calculation Mechanics Example")

    # Step 1: Define trade scenario for P/L calculation demonstration
    # Manual calculation helps understand how FiveTwenty SDK computes P/L
    entry_price = Decimal("1.1000")  # Your entry price
    current_price = Decimal("1.1050")  # Current market price
    position_size = 10000  # Position size in base currency units

    print(f"\nTrade Scenario:")
    print(f" Entry price: {entry_price} EUR_USD")
    print(f" Current price: {current_price} EUR_USD")
    print(f" Position size: {position_size:,} EUR (1 mini lot)")
    print(f" Direction: LONG (bought EUR, sold USD)")

    # Step 2: Manual P/L calculation step-by-step
    # P/L = (Current Price - Entry Price) × Position Size
    price_difference = current_price - entry_price
    manual_pnl = price_difference * position_size

    print(f"\nManual P/L Calculation:")
    print(f" Price movement: {current_price} - {entry_price} = {price_difference}")
    print(f" Calculation: {price_difference} × {position_size:,} = {manual_pnl} USD")
    print(f" Result: {manual_pnl:+} USD profit")

    # Step 3: Explain the calculation in trading terms
    pips_moved = price_difference * 10000  # Convert to pips (4 decimal places)
    pip_value = Decimal("1.0")  # For EUR_USD, 1 pip = $1 per 10k units
    pip_profit = pips_moved * pip_value

    print(f"\nTrading Terms Breakdown:")
    print(f" Price moved: {pips_moved:+.0f} pips in your favor")
    print(f" Pip value: ${pip_value} per pip (for 10k EUR_USD)")
    print(f" Pip profit: {pips_moved:+.0f} pips × ${pip_value} = ${pip_profit:+.0f}")
    print(f" Manual calculation confirms: ${manual_pnl} profit")

    # Step 4: Verify with FiveTwenty SDK automatic calculation
    # The SDK calculates this automatically with real-time precision
    print(f"\n💻 FiveTwenty SDK Verification:")
    client = AsyncClient()
    account_id = "your-account-id"
    trade_id = "123"  # Replace with actual trade ID

    try:
            # Retrieve trade from FiveTwenty SDK for automatic P/L
            trade = await client.trades.get_trade(account_id, trade_id)
            sdk_pnl = trade.unrealized_pl

            print(f" SDK calculated P/L: {sdk_pnl} USD")
            print(f" Entry price: {trade.price}")
            print(f" Current units: {trade.current_units}")
            print(f"   Trade opened: {trade.open_time}")

            # Compare manual vs SDK calculation
            if abs(sdk_pnl - manual_pnl) < Decimal("0.01"):  # Allow rounding
                print(f" Calculation match: Manual and SDK results align")
            else:
                difference = sdk_pnl - manual_pnl
                print(f" Difference: {difference:+.2f} USD (real-time vs example prices)")

            # Step 5: Explain factors affecting P/L accuracy
            print(f"\nNote: P/L Calculation Factors:")
            print(f"   🕐 Real-time prices: SDK uses live market data")
            print(f" Price precision: Up to 5 decimal places for accuracy")
            print(f"   Currency conversion: Auto-converted to account currency")
            print(f"   Timing: P/L updates with every price tick")

    except Exception as e:
            print(f"   ⚠️ SDK verification failed: {e}")
            print(f"   Note: Trade ID '123' is example - use actual trade ID")
            print(f" Manual calculation shows expected result: ${manual_pnl}")

    # Step 6: Extended P/L scenarios for different market movements
    print(f"\nP/L Scenarios for Different Price Movements:")

    scenarios = [(Decimal("1.0950"), "50 pips loss"), (Decimal("1.1000"), "Breakeven"), (Decimal("1.1025"), "25 pips profit"), (Decimal("1.1100"), "100 pips profit"), (Decimal("1.0900"), "100 pips loss")]

    for scenario_price, description in scenarios:
            scenario_movement = scenario_price - entry_price
            scenario_pnl = scenario_movement * position_size
            scenario_pips = scenario_movement * 10000

            status = "Success" if scenario_pnl > 0 else "Error" if scenario_pnl < 0 else "Scale"
            print(f"   {status} Price {scenario_price}: {scenario_pnl:+.0f} USD ({description})")

    # Step 7: Key takeaways for P/L understanding
    print(f"\nKey P/L Calculation Takeaways:")
    print(f" Long positions: Profit when price rises, lose when price falls")
    print(f" Short positions: Profit when price falls, lose when price rises")
    print(f" Position size: Larger positions = larger P/L per pip")
    print(f" Currency matters: P/L calculated in quote currency, converted to account")
    print(f"   Real-time: P/L updates continuously with market movements")
    print(f"   Risk awareness: Understand P/L before opening positions")


if __name__ == "__main__":
    asyncio.run(main())

```

### Currency Conversion in P/L

When your account currency differs from the quote currency:

<!-- fragment: Demo currency conversion in P/L with multi-currency trading examples -->
```python
async def check_currency_conversion() -> None:
    """Check currency conversion in P/L with comprehensive cross-currency analysis."""
    # Step 1: Initialize client for cross-currency P/L analysis
    # Currency conversion is crucial when trading pairs different from account currency
    client = AsyncClient()
    account_id = "your-account-id"
    print(f"Currency Conversion in P/L Analysis")

    # Step 2: Explain cross-currency trading scenario
    # Trading GBP_JPY with USD account demonstrates currency conversion complexity
    print(f"\nCross-Currency Trading Scenario:")
    print(f" Account currency: USD (your base currency)")
    print(f" Trading pair: GBP_JPY (British Pound vs Japanese Yen)")
    print(f"   Conversion chain: JPY P/L → USD account currency")
    print(f"   Note: Challenge: Neither GBP nor JPY is your account currency")

    try:
            # Step 3: Retrieve GBP_JPY position for currency conversion analysis
            position = await client.positions.get_position(account_id, "GBP_JPY")
            account_currency_pl = position.unrealized_pl  # Already converted to USD

            print(f"\nPosition Analysis:")
            print(f"   Instrument: GBP_JPY")
            print(f" Unrealized P/L: {account_currency_pl} USD (auto-converted)")
            print(f" Conversion: FiveTwenty SDK handles JPY → USD automatically")

            # Step 4: Explain the conversion process step-by-step
            print(f"\nCurrency Conversion Process:")
            print(f"   Step 1: Calculate P/L in quote currency (JPY)")
            print(f"   Step 2: Get current USD_JPY exchange rate")
            print(f"   Step 3: Convert JPY P/L to USD using current rate")
            print(f"   Step 4: Display result in account currency (USD)")

            # Step 5: Demonstrate conversion impact with hypothetical numbers
            # Show how exchange rate fluctuations affect P/L
            print(f"\n📉 Conversion Impact Example:")

            # Hypothetical scenario to illustrate conversion effects
            hypothetical_jpy_pl = 1000  # 1,000 JPY profit
            usd_jpy_rate_1 = 110.00# 1 USD = 110 JPY
            usd_jpy_rate_2 = 115.00# 1 USD = 115 JPY (JPY weakened)

            usd_pl_rate_1 = hypothetical_jpy_pl / usd_jpy_rate_1
            usd_pl_rate_2 = hypothetical_jpy_pl / usd_jpy_rate_2

            print(f"   Scenario: +1,000 JPY profit from GBP_JPY trade")
            print(f" USD_JPY at 110.00: 1,000 ÷ 110 = ${usd_pl_rate_1:.2f} USD")
            print(f" USD_JPY at 115.00: 1,000 ÷ 115 = ${usd_pl_rate_2:.2f} USD")
    print(f"   ⚠️ Currency impact: {(usd_pl_rate_2 - usd_pl_rate_1):+.2f} USD difference")
    print(f"   Note: Insight: JPY weakening reduces USD value of JPY profits")

    # Step 6: Position composition analysis
    if position.long.units or position.short.units:
    long_units = int(position.long.units) if position.long.units else 0
    short_units = int(position.short.units) if position.short.units else 0
    net_units = long_units + short_units

    print(f"\nPosition Composition:")
    print(f" Long GBP: {long_units:,} units")
    print(f" Short GBP: {abs(short_units):,} units")
    print(f" Net exposure: {net_units:,} GBP")

    # Currency exposure analysis
    direction = "LONG GBP/SHORT JPY" if net_units > 0 else "SHORT GBP/LONG JPY" if net_units < 0 else "FLAT"
    print(f"   Direction: {direction}")

    # Triple currency exposure explanation
    print(f"\nTriple Currency Exposure:")
    print(f"   1️⃣ GBP exposure: {abs(net_units):,} units ({'LONG' if net_units > 0 else 'SHORT' if net_units < 0 else 'NONE'})")
    print(f"   2️⃣ JPY exposure: Opposite to GBP (quote currency)")
    print(f"   3️⃣ USD exposure: Account currency conversion risk")

    except Exception as e:
    print(f"\n⚠️ No GBP_JPY position found: {e}")
    print(f"   Note: This demonstrates the concept with hypothetical position")

    # Step 7: Multi-currency trading considerations
    print(f"\nNote: Multi-Currency Trading Considerations:")
    print(f"   Auto-conversion: FiveTwenty SDK handles all currency conversions")
    print(f"   Real-time rates: P/L updates with currency exchange rate changes")
    print(f" Hidden risk: Currency conversion can add/reduce P/L")
    print(f" Correlation: Some currency pairs move together (EUR_USD vs GBP_USD)")

    # Step 8: Currency conversion examples for different account types
    print(f"\nCurrency Conversion Examples:")
    conversion_examples = [
    ("USD account", "EUR_USD", "Direct - no conversion needed"),
    ("USD account", "GBP_JPY", "JPY P/L → USD via USD_JPY rate"),
    ("EUR account", "USD_JPY", "JPY P/L → EUR via EUR_JPY rate"),
    ("GBP account", "AUD_CAD", "CAD P/L → GBP via GBP_CAD rate")
    ]

    for account_curr, pair, conversion in conversion_examples:
    print(f"   • {account_curr} trading {pair}: {conversion}")

    # Step 9: Best practices for multi-currency trading
    print(f"\nMulti-Currency Best Practices:")
    print(f" Understand: Know how your P/L is calculated and converted")
    print(f" Monitor: Watch currency correlations affecting conversion")
    print(f"   ⚠️ Risk: Consider currency hedging for large cross-currency positions")
    print(f" Simplify: Trade pairs involving your account currency when possible")
    print(f" Educate: Learn major currency relationships and correlations")

    # Step 10: Advanced currency risk concepts
    print(f"\nEducation Advanced Currency Risk Concepts:")
    print(f"   Currency overlay: Additional currency risk on top of trading risk")
    print(f" Correlation risk: Currency movements can amplify/reduce trading P/L")
    print(f"   Volatility: Some currencies more volatile than others")
    print(f"   Geographic: Consider time zones for currency pair liquidity")
    print(f" Hedging: Advanced traders may hedge currency exposure separately")

```

---

## Market Data and Pricing

### Bid-Ask Spreads

Forex markets have two prices:

```text
 Market Depth & Pricing

   SELL ORDERS (Asks)  BUY ORDERS (Bids)
    Price    |    Volume    Price    |    Volume
    ---------|----------    ---------|----------
    1.1055   |   100K  ← ASK1.1049   |   150K  ← BID
    1.1054   |   200K    (You pay1.1048   |   100K    (You receive
    1.1053   |   150Khigher)1.1047   |   200Klower)
    1.1052   |   300K  1.1046   |   250K

  ↕ SPREAD ↕
    (1.1055 - 1.1049 = 0.0006 = 0.6 pips)

Trading Cost: You immediately lose the spread when opening a position
```

<!-- fragment: Demo bid-ask spread analysis with trading cost implications -->
```python
async def check_spread() -> None:
    """Check bid-ask spread with comprehensive trading cost analysis."""
    # Step 1: Initialize client for real-time pricing data
    # Spread analysis is crucial for understanding trading costs
    client = AsyncClient()
    account_id = "your-account-id"
    print(f" Bid-Ask Spread Analysis for Trading Costs")

    try:
            # Step 2: Retrieve real-time pricing data from FiveTwenty SDK
            # Pricing data includes bid/ask prices and spread information
            prices = await client.pricing.get_pricing(account_id, ["EUR_USD"])
            eur_usd_price = prices.prices[0]
            print(f"\nEUR_USD Real-Time Pricing:")

            # Step 3: Extract and analyze bid/ask prices
            # Bid = price you can sell at, Ask = price you can buy at
            bid_price = eur_usd_price.bids[0].price # Price you can SELL at
            ask_price = eur_usd_price.asks[0].price # Price you can BUY at
            spread = ask_price - bid_price  # Market maker profit

            print(f" Bid price: {bid_price} (you can SELL EUR at this price)")
            print(f" Ask price: {ask_price} (you can BUY EUR at this price)")
            print(f" Spread: {spread:.5f} ({spread * 10000:.1f} pips)")
            print(f"   Quote time: {eur_usd_price.time}")

            # Step 4: Calculate trading cost implications
            # Spread represents immediate cost of opening any position
            spread_pips = spread * 10000  # Convert to pips for easier understanding
            spread_percentage = (spread / ask_price) * 100

            print(f"\nTrading Cost Analysis:")
            print(f" Spread in pips: {spread_pips:.1f} pips")
            print(f" Spread percentage: {spread_percentage:.4f}% of price")
            print(f" Immediate cost: Must overcome spread to be profitable")

            # Step 5: Position size impact on spread costs
            position_sizes = [10000, 100000, 1000000]  # Different position sizes
            print(f"\nSpread Cost by Position Size:")

            for size in position_sizes:
                # Calculate spread cost in USD for different position sizes
                spread_cost_usd = spread * size
                lot_description = f"{size//10000}0k" if size >= 10000 else f"{size}"

                print(f"   {lot_description} units: ${spread_cost_usd:.2f} immediate cost")
                print(f"• Must move {spread_pips:.1f} pips in your favor to breakeven")

            # Step 6: Trading strategy implications
            print(f"\nNote: Trading Implications:")
            print(f" Buying (going long):")
            print(f"• You pay the ASK price: {ask_price}")
            print(f"• Position immediately shows loss equal to spread")
            print(f"• Need price to rise above {ask_price} + spread costs")

            print(f" Selling (going short):")
            print(f"• You receive the BID price: {bid_price}")
            print(f"• Position immediately shows loss equal to spread")
            print(f"• Need price to fall below {bid_price} - spread costs")

            print(f"   ⚠️ Initial P/L: Every position starts -{spread_cost_usd:.2f} USD (for 10k units)")

            # Step 7: Spread quality assessment
            print(f"\nSpread Quality Assessment:")

    # Typical spread ranges for EUR_USD (most liquid pair)
    if spread_pips <= 0.5:
    quality = "Success EXCELLENT - Institutional level"
    elif spread_pips <= 1.0:
    quality = "GOOD - Retail competitive"
    elif spread_pips <= 2.0:
    quality = "AVERAGE - Standard retail"
    elif spread_pips <= 3.0:
    quality = "🟠 FAIR - Higher cost broker"
    else:
    quality = "POOR - Avoid if possible"

    print(f" Spread quality: {quality}")
    print(f" EUR_USD typical range: 0.5-2.0 pips")
    print(f"   Best spreads: London/NY overlap (12-17 UTC)")

    # Step 8: Market conditions affecting spreads
    print(f"\nMarket Conditions Affecting Spreads:")
    print(f" Tighter spreads during: High liquidity, major sessions, normal volatility")
    print(f" Wider spreads during: Low liquidity, news events, market open/close")
    print(f"   ⚠️ Volatile times: Spreads can widen significantly (5-10+ pips)")
    print(f"   Geographic: Better spreads during overlapping market sessions")

    # Step 9: Spread impact on different trading styles
    print(f"\nTrading Style Impact:")
    print(f"   Scalping: Spread is major cost - need tight spreads (<1 pip)")
    print(f" Day trading: Moderate impact - consider spread in profit targets")
    print(f" Swing trading: Minor impact - spread less relevant for larger moves")
    print(f" Position trading: Minimal impact - focus on fundamentals")

    # Step 10: Cost optimization strategies
    print(f"\nSpread Cost Optimization:")
    print(f"   Timing: Trade during high liquidity periods")
    print(f" Pairs: Focus on major pairs for tightest spreads")
    print(f" Size: Consider spread cost in position sizing")
    print(f"   Broker: Compare spread offerings across brokers")
    print(f"   Speed: Use limit orders to potentially get better prices")

    except Exception as e:
    print(f"\nError: Pricing data retrieval failed: {e}")
    print(f" Common issues: Market closed, connectivity, invalid instrument")
    print(f"Note: Spread analysis requires active market hours")

```

### Market Depth (Order Book)

See available liquidity at different price levels:

<!-- fragment: Demo market depth analysis with liquidity assessment techniques -->
```python
async def check_order_book() -> None:
    """Check order book depth using available market data indicators."""
    # Step 1: Initialize client for market depth analysis
    # Note: OANDA doesn't provide full order book data, so we use proxies
    client = AsyncClient()
    account_id = "your-account-id"
    print(f" Market Depth and Liquidity Analysis")
    print(f" Note: Using market data proxies (OANDA doesn't provide order book)")

    try:
            # Step 2: Retrieve current market data as liquidity proxy
            # Candle data provides volume and price action insights
            print(f"\nRetrieving market data for liquidity assessment...")
            candles = await client.instruments.get_instrument_candles(
                instrument="EUR_USD",
                count=5,  # Get recent candles for trend analysis
                granularity="M1"  # 1-minute candles for detailed view
            )

            if candles.candles:
                latest_candle = candles.candles[-1]  # Most recent candle
                print(f"\nLatest Market Data (1-minute candle):")
                print(f"   Time: {latest_candle.time}")
                print(f" Open: {latest_candle.mid.o}")
                print(f"   🔺 High: {latest_candle.mid.h}")
                print(f"   🔻 Low: {latest_candle.mid.l}")
                print(f"   🔲 Close: {latest_candle.mid.c}")
                print(f" Volume: {latest_candle.volume} trades")

                # Step 3: Analyze price action for liquidity indicators
                high_low_range = latest_candle.mid.h - latest_candle.mid.l
                range_pips = high_low_range * 10000

                print(f"\n📉 Liquidity Indicators:")
                print(f" Price range: {range_pips:.1f} pips (High-Low)")
                print(f" Volume: {latest_candle.volume} trades in 1 minute")

                # Volume-based liquidity assessment
                if latest_candle.volume > 100:
                    liquidity_status = "Success HIGH - Strong trading activity"
                elif latest_candle.volume > 50:
                    liquidity_status = "MODERATE - Normal activity"
                elif latest_candle.volume > 20:
                    liquidity_status = "LOW - Light trading"
                else:
                    liquidity_status = "VERY LOW - Minimal activity"

                print(f" Liquidity status: {liquidity_status}")

                # Step 4: Analyze recent price action for depth insights
                print(f"\nRecent Price Action Analysis:")
                for i, candle in enumerate(candles.candles[-3:], 1):
                    candle_range = candle.mid.h - candle.mid.l
                    candle_pips = candle_range * 10000
                    body = abs(candle.mid.c - candle.mid.o)
                    body_pips = body * 10000

                    # Determine candle color
                    if candle.mid.c > candle.mid.o:
                            candle_color = "GREEN (bullish)"
                    elif candle.mid.c < candle.mid.o:
                            candle_color = "RED (bearish)"
                    else:
                            candle_color = "⬜ DOJI (neutral)"

                    print(f"   Candle {i}: {candle_color}")
                    print(f"Range: {candle_pips:.1f} pips, Body: {body_pips:.1f} pips")
                    print(f"Volume: {candle.volume} trades")

                # Step 5: Pricing data for bid-ask depth analysis
                print(f"\nCurrent Bid-Ask Depth Analysis:")
                pricing = await client.pricing.get_pricing(account_id, ["EUR_USD"])
                price_data = pricing.prices[0]

                # Analyze bid and ask depth (limited in retail forex)
                print(f" Available bid levels: {len(price_data.bids)}")
                print(f" Available ask levels: {len(price_data.asks)}")

                # Display available price levels
                for i, bid in enumerate(price_data.bids[:3]):
                    print(f"Bid {i+1}: {bid.price} (liquidity indicator)")

                for i, ask in enumerate(price_data.asks[:3]):
                    print(f"Ask {i+1}: {ask.price} (liquidity indicator)")

                # Step 6: Market depth implications for trading
                print(f"\nNote: Market Depth Trading Implications:")

                current_spread = price_data.asks[0].price - price_data.bids[0].price
                spread_pips = current_spread * 10000

                print(f" Current spread: {spread_pips:.1f} pips")
                print(f"   Depth factors affecting your trades:")
                print(f"• Tight spread ({spread_pips:.1f} pips) suggests good liquidity")
                print(f"• Recent volume ({latest_candle.volume} trades) shows activity")
                print(f"• Price stability indicates sufficient market depth")

                # Step 7: Slippage risk assessment
                print(f"\n⚠️ Slippage Risk Assessment:")
                if spread_pips <= 1.0 and latest_candle.volume > 50:
                    slippage_risk = "LOW - Good execution expected"
                elif spread_pips <= 2.0 and latest_candle.volume > 30:
                    slippage_risk = "MODERATE - Normal conditions"
                else:
                    slippage_risk = "HIGH - Consider smaller positions"

                print(f" Slippage risk: {slippage_risk}")
                print(f" Factors: Spread tightness + trading volume")

                # Step 8: Order size recommendations based on depth
                print(f"\nPosition Sizing Based on Market Depth:")
    if latest_candle.volume > 100:
    max_recommended = "Large positions (100k+ units) acceptable"
    elif latest_candle.volume > 50:
    max_recommended = "Medium positions (50k units) recommended"
    elif latest_candle.volume > 20:
    max_recommended = "Small positions (10k units) safer"
    else:
    max_recommended = "Mini positions (1k units) only"

    print(f" Recommended sizing: {max_recommended}")
    print(f"   Note: Logic: Higher volume = better ability to absorb orders")

    # Step 9: Best practices for depth-aware trading
    print(f"\nMarket Depth Best Practices:")
    print(f"   Timing: Trade during high-volume periods")
    print(f" Sizing: Adjust position size to market depth")
    print(f"   Orders: Use limit orders in thin markets")
    print(f" Monitoring: Watch spread and volume for liquidity changes")
    print(f"   Speed: Fast execution in good liquidity, patience in thin markets")

    except Exception as e:
    print(f"\nError: Market data retrieval failed: {e}")
    print(f" Common issues: Market closed, connectivity problems")
    print(f"Note: Market depth analysis requires active trading hours")

    # Step 10: Alternative depth analysis methods
    print(f"\n📚 Alternative Market Depth Analysis:")
    print(f" Volume indicators: Use trading volume as liquidity proxy")
    print(f" Spread monitoring: Tight spreads indicate good depth")
    print(f"   Time analysis: Depth varies by session (London/NY best)")
    print(f"   Economic calendar: Major news affects market depth")
    print(f" Historical patterns: Learn typical depth for your trading times")

```


**Market Depth Insights**:

- **Liquidity**: How much volume available at each price
- **Support/Resistance**: Large orders may act as price barriers
- **Slippage Risk**: Low liquidity = potential price impact

---

## Risk Management Concepts

### Position Sizing

Never risk more than a small percentage of your account:
<!-- fragment: Demo comprehensive position sizing with risk management calculations -->
```python
from decimal import Decimal
from fivetwenty import AsyncClient

async def calculate_position_size() -> None:
    """Calculate position size based on risk with comprehensive risk management."""
    # Step 1: Initialize client for account-based position sizing
    # Position sizing is the foundation of risk management
    client = AsyncClient()
    account_id = "your-account-id"
    print(f"Comprehensive Position Sizing & Risk Management")

    # Step 2: Retrieve account information for risk calculations
    # Account balance is the base for all risk percentage calculations
    account = await client.accounts.get_account(account_id)
    account_balance = Decimal(str(account.balance))
    account_equity = account_balance + Decimal(str(account.unrealized_pl))

    print(f"\nAccount Risk Assessment:")
    print(f" Account balance: {account_balance} USD")
    print(f" Current equity: {account_equity} USD")
    print(f" Unrealized P/L: {account.unrealized_pl} USD")

    # Step 3: Apply the 2% risk rule (industry standard)
    # Never risk more than 2% of account on a single trade
    risk_percentage = Decimal("0.02")  # 2% risk rule
    max_risk_per_trade = account_balance * risk_percentage
    conservative_risk = account_balance * Decimal("0.01")  # 1% for conservative approach

    print(f"\n📉 Risk Budget Calculation:")
    print(f" Risk percentage: {risk_percentage * 100:.1f}% per trade")
    print(f"   Maximum risk: {max_risk_per_trade} USD (2% rule)")
    print(f" Conservative risk: {conservative_risk} USD (1% rule)")
    print(f"   Note: Rule: This protects you from catastrophic losses")

    # Step 4: Define trade setup parameters
    # Stop loss distance determines position size for given risk
    instrument = "EUR_USD"
    entry_price = Decimal("1.1050")# Example entry price
    stop_loss_price = Decimal("1.1000") # Stop loss 50 pips away
    stop_loss_pips = (entry_price - stop_loss_price) * 10000  # Convert to pips

    print(f"\nTrade Setup Parameters:")
    print(f"   Instrument: {instrument}")
    print(f" Entry price: {entry_price}")
    print(f"   Stop loss: {stop_loss_price}")
    print(f" Stop distance: {stop_loss_pips} pips")
    print(f" Risk/reward setup ready for position sizing")

    # Step 5: Calculate pip value for position sizing
    # For EUR_USD: 1 pip = $1 per 10,000 units (mini lot)
    pip_value_per_10k = Decimal("1.0")  # $1 per pip for 10k EUR_USD
    pip_value_per_1k = pip_value_per_10k / 10  # $0.10 per pip for 1k units

    print(f"\nPip Value Calculation:")
    print(f" EUR_USD pip value: ${pip_value_per_10k} per 10k units")
    print(f" Pip value per 1k: ${pip_value_per_1k} per 1k units")
    print(f" Formula: Position size = Risk ÷ (Stop pips × Pip value)")

    # Step 6: Calculate position size using risk management formula
    # Position Size = Maximum Risk ÷ (Stop Loss Pips × Pip Value per Unit)
    risk_per_pip = stop_loss_pips * pip_value_per_1k  # Risk per 1k units
    optimal_position_size = int(max_risk_per_trade / risk_per_pip)  # In thousands
    conservative_position_size = int(conservative_risk / risk_per_pip)

    # Convert to standard units
    optimal_units = optimal_position_size * 1000
    conservative_units = conservative_position_size * 1000

    print(f"\nPosition Size Calculations:")
    print(f" Risk per 1k units: ${risk_per_pip:.2f}")
    print(f"   Optimal position (2% risk): {optimal_units:,} units")
    print(f" Conservative position (1% risk): {conservative_units:,} units")

    # Express in trading terms (lots)
    optimal_lots = optimal_units / 100000  # Standard lots
    conservative_lots = conservative_units / 100000

    print(f" Optimal in lots: {optimal_lots:.2f} standard lots")
    print(f"   Conservative in lots: {conservative_lots:.2f} standard lots")

    # Step 7: Risk validation and safety checks
    print(f"\nRisk Validation:")

    # Check if position size is reasonable for account
    margin_required = optimal_units * entry_price * Decimal("0.0333")  # 30:1 leverage
    margin_percentage = (margin_required / account_balance) * 100

    print(f" Required margin: {margin_required:.2f} USD")
    print(f" Margin utilization: {margin_percentage:.1f}%")

    # Safety assessments
    if margin_percentage > 50:
    safety_status = "HIGH RISK - Reduce position size"
    elif margin_percentage > 30:
    safety_status = "MODERATE - Monitor closely"
    else:
    safety_status = "SAFE - Good margin buffer"

    print(f"   ⚠️ Safety status: {safety_status}")

    # Step 8: Execute trade with calculated position size
    # Use conservative size for demonstration
    final_position_size = conservative_units  # Choose conservative approach

    print(f"\nTrade Execution Plan:")
    print(f" Chosen position: {final_position_size:,} units")
    print(f" Maximum loss: ${conservative_risk:.2f} (1% of account)")
    print(f" Entry: {entry_price}")
    print(f"   Stop loss: {stop_loss_price}")

    try:
    # Place order with calculated position size and risk management
    order = await client.orders.post_market_order(
    account_id=account_id,
    instrument=instrument,
    units=final_position_size,
    stop_loss_on_fill={
"price": str(stop_loss_price),
"time_in_force": "GTC"  # Good Till Cancelled
    }
    )

    print(f" Order executed successfully")
    print(f" Order ID: {order.order_create_transaction.id}")
    if order.order_fill_transaction:
    print(f" Fill price: {order.order_fill_transaction.price}")
    print(f"   Stop loss attached: {stop_loss_price}")

    except Exception as e:
    print(f"   Error: Order execution failed: {e}")
    print(f"   Note: Check margin availability and market conditions")

    # Step 9: Position sizing variations for different scenarios
    print(f"\nPosition Sizing Scenarios:")

    scenarios = [
    (25, "Tight stop - larger position"),
    (50, "Standard stop - medium position"),
    (100, "Wide stop - smaller position")
    ]

    for stop_pips, description in scenarios:
    scenario_risk_per_pip = stop_pips * pip_value_per_1k
    scenario_position = int(conservative_risk / scenario_risk_per_pip) * 1000
    scenario_lots = scenario_position / 100000

    print(f"   {stop_pips} pip stop: {scenario_position:,} units ({scenario_lots:.2f} lots) - {description}")

    # Step 10: Advanced position sizing considerations
    print(f"\nEducation Advanced Position Sizing Concepts:")
    print(f" Correlation: Reduce size for correlated positions")
    print(f"   Volatility: Adjust for high/low volatility instruments")
    print(f"   Time: Consider holding period in sizing decision")
    print(f" Portfolio: Total risk across all positions <10% of account")
    print(f" Scaling: Increase position size as account grows")
    print(f"   Psychology: Size positions to sleep well at night")

```

### Correlation Risk

Be aware of correlated positions:

<!-- fragment: Demo correlation risk analysis with portfolio diversification assessment -->
```python
async def check_correlation_risk() -> None:
    """Check correlation risk across positions with comprehensive portfolio analysis."""
    # Step 1: Initialize client for portfolio-wide correlation analysis
    # Correlation risk occurs when multiple positions move in same direction
    client = AsyncClient()
    account_id = "your-account-id"
    print(f"Portfolio Correlation Risk Analysis")

    try:
    # Step 2: Retrieve positions for major correlated pairs
    # EUR_USD and GBP_USD often show high correlation (0.7-0.9)
    print(f"\nRetrieving positions for correlation analysis...")
    eur_position = await client.positions.get_position(account_id, "EUR_USD")
    gbp_position = await client.positions.get_position(account_id, "GBP_USD")

    # Step 3: Calculate net exposure for each position
    # Net exposure shows true directional risk per currency pair
    eur_long = int(eur_position.long.units) if eur_position.long.units else 0
    eur_short = int(eur_position.short.units) if eur_position.short.units else 0
    eur_net = eur_long + eur_short  # short.units is negative

    gbp_long = int(gbp_position.long.units) if gbp_position.long.units else 0
    gbp_short = int(gbp_position.short.units) if gbp_position.short.units else 0
    gbp_net = gbp_long + gbp_short  # short.units is negative

    print(f"\nIndividual Position Analysis:")
    print(f"   EUR_USD Position:")
    print(f"   Long: {eur_long:,} units")
    print(f"   Short: {abs(eur_short):,} units")
    print(f"   Net: {eur_net:,} units ({'LONG' if eur_net > 0 else 'SHORT' if eur_net < 0 else 'FLAT'})")
    print(f"   P/L: {eur_position.unrealized_pl} USD")

    print(f"   GBP_USD Position:")
    print(f"   Long: {gbp_long:,} units")
    print(f"   Short: {abs(gbp_short):,} units")
    print(f"   Net: {gbp_net:,} units ({'LONG' if gbp_net > 0 else 'SHORT' if gbp_net < 0 else 'FLAT'})")
    print(f"   P/L: {gbp_position.unrealized_pl} USD")

    # Step 4: Analyze USD exposure and correlation risk
    # Both EUR_USD and GBP_USD involve USD, creating correlation
    print(f"\nUSD Exposure Analysis:")

    # Determine USD exposure direction for each pair
    eur_usd_direction = "LONG USD" if eur_net < 0 else "SHORT USD" if eur_net > 0 else "NEUTRAL"
    gbp_usd_direction = "LONG USD" if gbp_net < 0 else "SHORT USD" if gbp_net > 0 else "NEUTRAL"

    print(f"   EUR_USD: {eur_usd_direction} ({abs(eur_net):,} units exposure)")
    print(f"   GBP_USD: {gbp_usd_direction} ({abs(gbp_net):,} units exposure)")

    # Step 5: Calculate total USD exposure and correlation impact
    # Same-direction positions amplify risk, opposite directions hedge
    total_usd_exposure = abs(eur_net) + abs(gbp_net)  # Total USD exposure
    net_usd_exposure = -eur_net - gbp_net  # Net USD position (negative of others)

    print(f" Total USD exposure: {total_usd_exposure:,} units")
    print(f" Net USD exposure: {net_usd_exposure:,} units")

    # Step 6: Assess correlation risk level
    print(f"\n⚠️ Correlation Risk Assessment:")

    # Analyze directional alignment
    if (eur_net > 0 and gbp_net > 0) or (eur_net < 0 and gbp_net < 0):
    # Same direction = high correlation risk
    correlation_risk = "HIGH CORRELATION RISK"
    risk_explanation = "Both positions move together - amplified risk"
    hedge_status = "CONCENTRATED - Consider diversification"
    elif (eur_net > 0 and gbp_net < 0) or (eur_net < 0 and gbp_net > 0):
    # Opposite directions = natural hedge
    correlation_risk = "NATURAL HEDGE"
    risk_explanation = "Positions offset each other - reduced risk"
    hedge_status = "HEDGED - Good risk management"
    else:
    # One or both positions are flat
    correlation_risk = "MINIMAL RISK"
    risk_explanation = "Limited exposure - low correlation impact"
    hedge_status = "NEUTRAL - No significant correlation exposure"

    print(f" Risk level: {correlation_risk}")
    print(f"   Note: Explanation: {risk_explanation}")
    print(f"   Portfolio status: {hedge_status}")

    # Step 7: Calculate correlation impact on portfolio P/L
    total_correlation_pl = eur_position.unrealized_pl + gbp_position.unrealized_pl
    print(f"\nPortfolio P/L Impact:")
    print(f" Combined P/L: {total_correlation_pl:+.2f} USD")

    if total_correlation_pl > 0:
    print(f" Correlation benefit: Positions are profitable together")
    elif total_correlation_pl < 0:
    print(f"   ⚠️ Correlation risk: Both positions losing simultaneously")
    else:
    print(f" Correlation neutral: Minimal combined impact")

    # Step 8: Position sizing recommendations
    print(f"\nPosition Sizing Recommendations:")

    # Calculate position concentration
    if total_usd_exposure > 0:
    eur_concentration = (abs(eur_net) / total_usd_exposure) * 100
    gbp_concentration = (abs(gbp_net) / total_usd_exposure) * 100

    print(f" EUR_USD concentration: {eur_concentration:.1f}% of USD exposure")
    print(f" GBP_USD concentration: {gbp_concentration:.1f}% of USD exposure")

    if max(eur_concentration, gbp_concentration) > 70:
sizing_advice = "Reduce dominant position for better balance"
    elif abs(eur_concentration - gbp_concentration) < 20:
sizing_advice = "Well-balanced USD exposure"
    else:
sizing_advice = "Consider rebalancing positions"

    print(f" Sizing advice: {sizing_advice}")

    # Step 9: Additional correlation pairs to monitor
    print(f"\nOther High-Correlation Pairs to Monitor:")
    correlation_groups = [
    (["EUR_USD", "GBP_USD"], "High positive correlation (0.7-0.9)"),
    (["AUD_USD", "NZD_USD"], "Commodity currencies - strong correlation"),
    (["USD_CHF", "EUR_USD"], "High negative correlation (-0.8)"),
    (["EUR_GBP", "GBP_USD"], "GBP exposure correlation"),
    (["USD_JPY", "USD_CHF"], "USD strength pairs")
    ]

    for pairs, description in correlation_groups:
    print(f"   • {' vs '.join(pairs)}: {description}")

    # Step 10: Risk management strategies for correlated positions
    print(f"\nCorrelation Risk Management Strategies:")
    print(f" Diversification: Spread risk across uncorrelated pairs")
    print(f" Position sizing: Reduce size when holding correlated positions")
    print(f" Hedging: Use opposite positions to reduce correlation risk")
    print(f"   Timing: Avoid simultaneous entry in correlated pairs")
    print(f" Monitoring: Track correlation changes during market stress")
    print(f" Limits: Set maximum exposure per currency or correlation group")

    # Final recommendations based on current analysis
    print(f"\nCurrent Portfolio Recommendations:")
    if abs(eur_net) > 0 and abs(gbp_net) > 0:
    if (eur_net > 0) == (gbp_net > 0):  # Same direction
print(f"   ⚠️ High correlation exposure detected")
print(f" Consider reducing one position or adding hedge")
    else:
print(f" Natural hedge in place - good risk management")
print(f" Monitor for changing correlations")
    else:
    print(f"   Limited correlation exposure - acceptable risk")

    except Exception as e:
    print(f"\nError: Correlation analysis failed: {e}")
    print(f" Note: Ensure you have positions in EUR_USD and GBP_USD")
    print(f"General rule: Monitor correlation between all USD pairs")

```

### Drawdown Management

Track account performance:

<!-- fragment: Demo comprehensive drawdown monitoring with equity curve analysis -->
```python
from decimal import Decimal
from datetime import datetime, timedelta
from fivetwenty import AsyncClient

async def monitor_drawdown() -> None:
    """Monitor account drawdown with comprehensive equity curve analysis."""
    # Step 1: Initialize client for equity and drawdown monitoring
    # Drawdown monitoring is critical for protecting trading capital
    client = AsyncClient()
    account_id = "your-account-id"
    print(f" Comprehensive Drawdown & Equity Monitoring")

    # Step 2: Define account high-water mark (peak equity)
    # This should be stored/tracked in your trading system
    peak_equity = Decimal("10000")  # Example peak equity - replace with actual tracking
    peak_date = datetime.now() - timedelta(days=30)  # Example peak date

    print(f"\nAccount High-Water Mark:")
    print(f"   Peak equity: {peak_equity} USD")
    print(f"   Peak date: {peak_date.strftime('%Y-%m-%d %H:%M')} (example)")
    print(f"   Note: Track this in your system for accurate monitoring")

    # Step 3: Calculate current account equity
    # Equity = Balance + Unrealized P/L (total available capital)
    account = await client.accounts.get_account(account_id)
    account_balance = Decimal(str(account.balance))
    unrealized_pl = Decimal(str(account.unrealized_pl))
    current_equity = account_balance + unrealized_pl

    print(f"\nCurrent Account Status:")
    print(f" Account balance: {account_balance} USD (cash)")
    print(f" Unrealized P/L: {unrealized_pl:+} USD (open positions)")
    print(f" Current equity: {current_equity} USD (total value)")
    print(f"   Analysis time: {datetime.now().strftime('%Y-%m-%d %H:%M')}")

    # Step 4: Calculate drawdown metrics
    # Drawdown = (Peak Equity - Current Equity) / Peak Equity
    if peak_equity > 0:
    drawdown_amount = peak_equity - current_equity
    drawdown_percentage = (drawdown_amount / peak_equity) * 100
    equity_recovery_needed = drawdown_amount
    recovery_percentage_needed = (current_equity / peak_equity - 1) * 100 if current_equity < peak_equity else 0

    print(f"\n📉 Drawdown Analysis:")
    print(f" Drawdown amount: {drawdown_amount:+.2f} USD")
    print(f" Drawdown percentage: {drawdown_percentage:+.2f}%")
    print(f" Recovery needed: {equity_recovery_needed:.2f} USD")

    # Update peak if current equity is higher
    if current_equity > peak_equity:
    print(f" NEW HIGH: Current equity exceeds previous peak!")
    print(f"   New peak equity: {current_equity} USD")
    # In practice, update your peak_equity tracking here
    peak_equity = current_equity
    drawdown_percentage = 0

    # Step 5: Categorize drawdown severity
    print(f"\n⚠️ Drawdown Severity Assessment:")

    if drawdown_percentage <= 2:
    severity = "MINIMAL - Normal trading fluctuations"
    action = "Continue normal operations"
    alert_level = "GREEN"
    elif drawdown_percentage <= 5:
    severity = "MINOR - Monitor closely"
    action = "Review recent trades for improvements"
    alert_level = "YELLOW"
    elif drawdown_percentage <= 10:
    severity = "🟠 MODERATE - Caution advised"
    action = "Consider reducing position sizes"
    alert_level = "ORANGE"
    elif drawdown_percentage <= 20:
    severity = "SIGNIFICANT - Take action"
    action = "Reduce position sizes, review strategy"
    alert_level = "RED"
    else:
    severity = "Alert SEVERE - Emergency measures"
    action = "Stop trading, reassess completely"
    alert_level = "CRITICAL"

    print(f" Severity: {severity}")
    print(f"   Recommended action: {action}")
    print(f"   Alert Alert level: {alert_level}")

    # Step 6: Risk management triggers
    print(f"\nRisk Management Triggers:")

    # Define multiple drawdown thresholds
    thresholds = [
    (5, "Review trading plan"),
    (10, "Reduce position sizes by 50%"),
    (15, "Reduce position sizes by 75%"),
    (20, "Stop new positions"),
    (25, "Close all positions, take break")
    ]

    for threshold, action in thresholds:
    status = "SAFE" if drawdown_percentage < threshold else "TRIGGERED"
    print(f"   {threshold}% threshold: {status} - {action}")

    # Step 7: Position size adjustment recommendations
    if drawdown_percentage > 5:
    print(f"\n📉 Position Size Adjustments:")

    # Calculate recommended position size reduction
    if drawdown_percentage <= 10:
    size_reduction = 0.25  # 25% reduction
    elif drawdown_percentage <= 15:
    size_reduction = 0.50  # 50% reduction
    elif drawdown_percentage <= 20:
    size_reduction = 0.75  # 75% reduction
    else:
    size_reduction = 1.0   # 100% reduction (stop trading)

    print(f" Recommended size reduction: {size_reduction * 100:.0f}%")
    print(f" New position multiplier: {1 - size_reduction:.2f}x")
    print(f" Example: If normal size is 10k, trade {int(10000 * (1 - size_reduction)):,} units")

    # Step 8: Equity curve momentum analysis
    print(f"\nEquity Curve Analysis:")

    # Compare current vs previous periods (simulated)
    days_in_drawdown = (datetime.now() - peak_date).days
    print(f"   Days since peak: {days_in_drawdown} days")

    if days_in_drawdown > 30:
    momentum_status = "CONCERNING - Extended drawdown period"
    elif days_in_drawdown > 14:
    momentum_status = "MONITORING - Moderate drawdown duration"
    else:
    momentum_status = "NORMAL - Recent drawdown"

    print(f" Momentum status: {momentum_status}")

    # Step 9: Recovery scenarios and projections
    if drawdown_percentage > 0:
    print(f"\nRecovery Scenarios:")

    recovery_targets = [50, 75, 100]  # Percentage recovery levels
    for recovery_pct in recovery_targets:
    target_equity = peak_equity - (drawdown_amount * (1 - recovery_pct / 100))
    recovery_amount = target_equity - current_equity
    recovery_return_needed = (recovery_amount / current_equity) * 100 if current_equity > 0 else 0

    print(f"   {recovery_pct}% recovery: {target_equity:.2f} USD (+{recovery_return_needed:.1f}% needed)")

    # Step 10: Automated monitoring recommendations
    print(f"\n💻 Automated Monitoring Setup:")
    print(f"   Daily equity tracking: Record equity at market close")
    print(f" Peak tracking: Update high-water mark automatically")
    print(f"   ⚠️ Alert system: Email/SMS alerts at key thresholds")
    print(f" Position sizing: Auto-adjust based on drawdown level")
    print(f" Recovery tracking: Monitor progress back to peak")
    print(f"   Reporting: Weekly/monthly drawdown reports")

    # Step 11: Psychological aspects of drawdown
    print(f"\n🧠 Psychological Considerations:")
    print(f" Emotional impact: Drawdowns test trading discipline")
    print(f"   Revenge trading: Avoid increasing size to recover quickly")
    print(f"   Patience: Recovery takes time - don't force it")
    print(f"   📚 Learning: Analyze what caused the drawdown")
    print(f"   Adaptation: Adjust strategy if market conditions changed")

    # Final assessment and recommendations
    print(f"\nFinal Assessment:")
    if drawdown_percentage > 15:
    print(f"   Alert PRIORITY: Immediate risk reduction required")
    print(f"   Action: Implement emergency risk management measures")
    elif drawdown_percentage > 5:
    print(f"   ⚠️ CAUTION: Enhanced monitoring and risk reduction")
    print(f" Action: Reduce position sizes and review strategy")
    else:
    print(f" HEALTHY: Normal account fluctuations")
    print(f" Action: Continue with standard risk management")

```

---

## Market Sessions and Timing

### Global Forex Sessions

Forex markets trade 24/5, but activity varies:

<!-- fragment: partial market session example -->
<!-- fragment: Demo market session analysis with optimal trading times -->
```python
from datetime import datetime, timezone


def get_market_session(dt: datetime) -> str:
    """Determine current forex market session with comprehensive analysis."""
    # Step 1: Convert input time to UTC for consistent session analysis
    # Forex market operates on UTC time zones for session determination
    utc_time = dt.replace(tzinfo=timezone.utc) if dt.tzinfo is None else dt.astimezone(timezone.utc)
    utc_hour = utc_time.hour

    print(f"Market Session Analysis for {utc_time.strftime('%Y-%m-%d %H:%M UTC')}")

    # Step 2: Determine primary trading session based on UTC hours
    # Each session has distinct characteristics and currency preferences
    if 0 <= utc_hour < 7:
    session = "Sydney/Tokyo"    # Asian session
    session_emoji = "🌏"
    characteristics = "Lower volatility, JPY/AUD focus, thin liquidity"
    best_pairs = ["USD_JPY", "AUD_USD", "NZD_USD"]
    elif 7 <= utc_hour < 15:
    session = "London"# European session
    session_emoji = "🇬🇧"
    characteristics = "High volatility, EUR/GBP focus, excellent liquidity"
    best_pairs = ["EUR_USD", "GBP_USD", "EUR_GBP", "USD_CHF"]
    elif 15 <= utc_hour < 22:
    session = "New York"   # US session
    session_emoji = "🇺🇸"
    characteristics = "High volatility, USD focus, strong trends"
    best_pairs = ["EUR_USD", "GBP_USD", "USD_JPY", "USD_CAD"]
    else:
    session = "Sydney"# Asian session starts
    session_emoji = "🇦🇺"
    characteristics = "Market opening, moderate volatility, AUD focus"
    best_pairs = ["AUD_USD", "NZD_USD", "AUD_JPY"]

    print(f"\n{session_emoji} Current Session: {session} ({utc_hour:02d}:00 UTC)")
    print(f" Characteristics: {characteristics}")
    print(f" Best pairs: {', '.join(best_pairs)}")

    return session


def analyze_session_overlaps(dt: datetime) -> None:
    """Analyze trading session overlaps for optimal timing."""
    # Step 3: Identify session overlaps for maximum liquidity
    # Overlaps provide highest liquidity and tightest spreads
    utc_time = dt.replace(tzinfo=timezone.utc) if dt.tzinfo is None else dt.astimezone(timezone.utc)
    utc_hour = utc_time.hour

    print(f"\nSession Overlap Analysis:")

    # Check for session overlaps
    if 7 <= utc_hour < 8:
    overlap = "🌏🇬🇧 Tokyo/London Opening"
    liquidity = "Moderate - European markets opening"
    strategy = "Watch for breakouts as European traders enter"
    elif 12 <= utc_hour < 17:
    overlap = "🇬🇧🇺🇸 London/New York PRIME TIME"
    liquidity = "MAXIMUM - Highest volume period"
    strategy = "Best time for scalping and day trading"
    elif 21 <= utc_hour < 22:
    overlap = "🇺🇸🌏 New York/Sydney Transition"
    liquidity = "Low - End of NY session"
    strategy = "Avoid major trades, prepare for Asian session"
    else:
    overlap = "No Major Overlap"
    liquidity = "Single session - standard liquidity"
    strategy = "Trade session-specific currency pairs"

    print(f" Current overlap: {overlap}")
    print(f" Liquidity level: {liquidity}")
    print(f"   Note: Trading strategy: {strategy}")


def get_session_trading_hours() -> None:
    """Display comprehensive trading session schedule."""
    # Step 4: Provide complete session schedule for planning
    print(f"\nComplete Session Schedule (UTC):")

    sessions = [
    ("Sydney", "22:00-07:00", "🇦🇺", "AUD/NZD focus, weekend gaps"),
    ("Tokyo", "00:00-09:00", "🇯🇵", "JPY pairs, moderate volatility"),
    ("London", "07:00-16:00", "🇬🇧", "EUR/GBP focus, high volatility"),
    ("New York", "12:00-21:00", "🇺🇸", "USD focus, trend continuation")
    ]

    for session, hours, flag, description in sessions:
    print(f"   {flag} {session}: {hours} UTC - {description}")

    # Step 5: Highlight optimal trading windows
    print(f"\n🎆 OPTIMAL Trading Windows:")
    print(f"   BEST: 12:00-17:00 UTC (London/NY overlap)")
    print(f"• Highest liquidity and volume")
    print(f"• Tightest spreads on major pairs")
    print(f"• Best for scalping and day trading")

    print(f"   GOOD: 07:00-12:00 UTC (London session)")
    print(f"• Strong European activity")
    print(f"• Good for EUR/GBP pairs")
    print(f"• Economic news impact")

    print(f"   MODERATE: 00:00-07:00 UTC (Asian session)")
    print(f"• JPY and commodity currency focus")
    print(f"• Lower volatility but consistent trends")
    print(f"• Good for swing trading")


# Step 6: Execute comprehensive session analysis
print(f"Comprehensive Forex Market Session Analysis")

# Check current session
current_time = datetime.now()
current_session = get_market_session(current_time)

# Analyze overlaps
analyze_session_overlaps(current_time)

# Display full schedule
get_session_trading_hours()

# Step 7: Trading implications and recommendations
print(f"\nNote: Session-Based Trading Implications:")
print(f"   Timing matters: Trade during your target currency's active session")
print(f" Volume patterns: Higher volume = better execution and tighter spreads")
print(f"   Pair selection: Match currency pairs to active sessions")
print(f"   ⚠️ Spread awareness: Spreads widen during session transitions")
print(f" Volatility cycles: Plan strategies around session characteristics")

# Market closure reminder
print(f"\n📍 Market Closure Schedule:")
print(f"   🚫 Weekend closure: Friday 22:00 UTC - Sunday 22:00 UTC")
print(f"   🎄 Holiday closures: Reduced activity during major holidays")
print(f"   ⚠️ Thin liquidity: Avoid major trades during closures")

```

### Economic Calendar Impact

Major news events affect volatility:

<!-- fragment: Demo news adjustment with assignment type patterns -->
<!-- fragment: Demo news event adjustment with comprehensive economic calendar integration -->
```python
from datetime import datetime, timedelta


def adjust_for_news() -> dict[str, int]:
    """Adjust trading parameters for nearby economic news events."""
    print("Economic News Event Risk Management")

    current_time = datetime.now()
    upcoming_news = [
        {
            "time": current_time + timedelta(hours=2),
            "event": "US Non-Farm Payrolls",
            "currency": "USD",
            "impact": "HIGH",
            "expected_volatility": "50-100 pips",
        },
        {
            "time": current_time + timedelta(hours=6),
            "event": "ECB Interest Rate Decision",
            "currency": "EUR",
            "impact": "HIGH",
            "expected_volatility": "75-150 pips",
        },
        {
            "time": current_time + timedelta(hours=24),
            "event": "UK GDP Quarterly",
            "currency": "GBP",
            "impact": "MEDIUM",
            "expected_volatility": "30-60 pips",
        },
    ]

    print("\nUpcoming High-Impact Events:")
    for news in upcoming_news:
        time_until = news["time"] - current_time
        hours_until = time_until.total_seconds() / 3600

        print(f"   {news['impact']} impact: {news['event']}")
        print(f"   Time: {news['time'].strftime('%Y-%m-%d %H:%M')} ({hours_until:.1f}h away)")
        print(f"   Currency: {news['currency']}")
        print(f"   Expected volatility: {news['expected_volatility']}")

    print("\nCurrent Trading Setup:")
    original_params = {
        "stop_loss_distance": 50,  # pips
        "position_size": 10000,  # units
        "take_profit": 100,  # pips
        "risk_per_trade": 200,  # USD
    }

    for param, value in original_params.items():
        print(f"   {param.replace('_', ' ').title()}: {value}")

    print("\nNews Impact Assessment:")
    news_within_1h = [
        n for n in upcoming_news if (n["time"] - current_time).total_seconds() < 3600
    ]
    news_within_4h = [
        n for n in upcoming_news if (n["time"] - current_time).total_seconds() < 14400
    ]
    high_impact_news = [n for n in upcoming_news if n["impact"] == "HIGH"]

    if news_within_1h:
        risk_level = "EXTREME"
        adjustment_factor = 0.25
    elif high_impact_news and news_within_4h:
        risk_level = "HIGH"
        adjustment_factor = 0.5
    elif news_within_4h:
        risk_level = "MODERATE"
        adjustment_factor = 0.75
    else:
        risk_level = "LOW"
        adjustment_factor = 1.0

    stop_adjustment = 1.5 if risk_level in {"HIGH", "EXTREME"} else 1.0

    print(f"   Risk level: {risk_level}")
    print(f"   Position size adjustment: {adjustment_factor}x normal size")
    print(f"   Stop loss adjustment: {stop_adjustment}x normal distance")

    print("\nAdjusted Trading Parameters:")
    adjusted_params = {
        "position_size": int(original_params["position_size"] * adjustment_factor),
        "stop_loss_distance": int(original_params["stop_loss_distance"] * stop_adjustment),
        "take_profit": int(original_params["take_profit"] * stop_adjustment),
        "risk_per_trade": int(original_params["risk_per_trade"] * adjustment_factor),
    }

    for param, value in adjusted_params.items():
        original_value = original_params[param]
        change = ((value - original_value) / original_value) * 100
        status = "increase" if change > 0 else "decrease" if change < 0 else "unchanged"
        print(f"   {param.replace('_', ' ').title()}: {value} ({status}, {change:+.0f}%)")

    print("\nCurrency-Specific Considerations:")
    affected_currencies = {news["currency"] for news in upcoming_news}
    currency_pairs_affected = {
        "USD": ["EUR_USD", "GBP_USD", "USD_JPY", "USD_CHF", "AUD_USD", "USD_CAD"],
        "EUR": ["EUR_USD", "EUR_GBP", "EUR_JPY", "EUR_CHF", "EUR_AUD"],
        "GBP": ["GBP_USD", "EUR_GBP", "GBP_JPY", "GBP_CHF", "GBP_AUD"],
    }

    for currency in sorted(affected_currencies):
        pairs = currency_pairs_affected.get(currency, [])
        suffix = "..." if len(pairs) > 4 else ""
        print(f"   {currency} news affects: {', '.join(pairs[:4])}{suffix}")

        if currency == "USD":
            print("      USD events affect most major pairs.")
        elif currency == "EUR":
            print("      EUR events primarily affect European session pairs.")
        elif currency == "GBP":
            print("      GBP events can produce sharp volatility.")

    print("\nPre-News Trading Strategies:")
    if risk_level == "EXTREME":
        strategy = "Avoid trading until after the news event"
        actions = [
            "Close or reduce open positions",
            "Cancel stale pending orders",
            "Wait 30-60 minutes after the release",
            "Watch for market stabilization",
        ]
    elif risk_level == "HIGH":
        strategy = "Trade defensively with minimal exposure"
        actions = [
            "Reduce position sizes by 50%",
            "Widen stops only if the wider risk is still acceptable",
            "Avoid new positions two hours before news",
            "Consider hedging existing positions",
        ]
    elif risk_level == "MODERATE":
        strategy = "Use adjusted parameters"
        actions = [
            "Reduce position sizes by 25%",
            "Monitor news closely",
            "Be ready to exit quickly",
            "Avoid counter-trend trades",
        ]
    else:
        strategy = "Continue normal operations"
        actions = [
            "Monitor the economic calendar",
            "Stay alert for unexpected news",
            "Maintain disciplined risk limits",
        ]

    print(f"   Strategy: {strategy}")
    print("   Action items:")
    for action in actions:
        print(f"   - {action}")

    print("\nPost-News Trading Guidelines:")
    print("   Wait 15-30 minutes for the market to digest the release")
    print("   Expect increased volatility for one to two hours")
    print("   Look for clear trend establishment")
    print("   Treat the initial reaction as unreliable until confirmed")

    print("\nRisk Monitoring During News:")
    print("   Watch spreads; they may widen significantly")
    print("   Expect slippage in fast markets")
    print("   Watch for temporary liquidity gaps")
    print("   Do not assume stop orders will fill at the trigger price")

    print("\nFinal News Trading Recommendations:")
    print("   Understand what each economic indicator means")
    print("   Use a reliable economic calendar with impact ratings")
    print("   Adjust positions before the news window")
    print("   Follow reduced-size rules during high-risk periods")
    print("   Never assume market direction; manage risk first")

    return adjusted_params


print("Executing Economic News Risk Assessment...")
adjusted_parameters = adjust_for_news()
print("\nNews risk assessment complete; parameters adjusted for current conditions")

```

---

## Advanced Concepts

### Carry Trades

Profit from interest rate differentials:

<!-- fragment: Demo carry trade analysis with interest rate differential calculations -->
```python
from decimal import Decimal
from fivetwenty import AsyncClient

# Step 1: Understand carry trade fundamentals
# High-yield currency vs. low-yield currency creates interest differential
# Example: AUD (higher rates) vs JPY (lower rates)
print(f" Carry Trade Analysis: Interest Rate Differential Strategy")

# Step 2: Explain carry trade mechanics
print(f"\nCarry Trade Fundamentals:")
print(f"   Concept: Borrow low-yield currency, invest in high-yield currency")
print(f" Example: Sell JPY (low rates), buy AUD (higher rates)")
print(f" Profit sources:")
print(f"1️⃣ Capital appreciation: AUD rises vs JPY")
print(f"2️⃣ Interest differential: Earn rollover/swap payments")
print(f"   ⚠️ Risk: Currency moves against you can overwhelm interest gains")

# Step 3: Interest rate differential example
print(f"\nInterest Rate Differential Analysis:")

# Example rates (would come from central bank data in practice)
interest_rates = {
    "AUD": 4.25,  # Australian Dollar rate
    "JPY": 0.10,  # Japanese Yen rate
    "USD": 5.25,  # US Dollar rate
    "EUR": 3.75,  # Euro rate
    "GBP": 5.00,  # British Pound rate
    "CHF": 1.50,  # Swiss Franc rate
    "CAD": 4.75,  # Canadian Dollar rate
    "NZD": 5.50   # New Zealand Dollar rate
}

# Calculate carry trade opportunities
carry_pairs = [
    ("AUD_JPY", "AUD", "JPY"),
    ("NZD_JPY", "NZD", "JPY"),
    ("GBP_JPY", "GBP", "JPY"),
    ("USD_CHF", "USD", "CHF"),
    ("AUD_CHF", "AUD", "CHF")
]

print(f" Popular Carry Trade Pairs:")
for pair, base, quote in carry_pairs:
    rate_diff = interest_rates[base] - interest_rates[quote]
    annual_carry = rate_diff
    daily_carry = annual_carry / 365

    direction = "LONG" if rate_diff > 0 else "SHORT"
    opportunity = "POSITIVE" if rate_diff > 2 else "MODERATE" if rate_diff > 0 else "NEGATIVE"

    print(f"{pair}: {base} {interest_rates[base]:.2f}% - {quote} {interest_rates[quote]:.2f}%")
    print(f"Rate differential: {rate_diff:+.2f}% annually")
    print(f"Daily carry: {daily_carry:+.4f}% per day")
    print(f"Strategy: {direction} {pair}")
    print(f"  {opportunity} Carry opportunity")
    print()

async def check_carry_trade() -> None:
    """Check carry trade financing with comprehensive analysis."""
    # Step 4: Initialize client for carry trade evaluation
    client = AsyncClient()
    account_id = "your-account-id"
    print(f"\nFiveTwenty SDK Carry Trade Analysis")

    try:
    # Step 5: Analyze AUD_JPY as classic carry trade example
    instrument = "AUD_JPY"
    print(f"\nAnalyzing {instrument} Carry Trade Setup:")

    # Get current market data
    candles = await client.instruments.get_instrument_candles(
    instrument=instrument,
    count=5,
    granularity="D"  # Daily candles for trend analysis
    )

    if candles.candles:
    latest_candle = candles.candles[-1]
    current_price = latest_candle.mid.c

    print(f" Current price: {current_price}")
    print(f"   Instrument: {instrument} (AUD = base, JPY = quote)")

    # Calculate recent price movement
    if len(candles.candles) >= 2:
prev_price = candles.candles[-2].mid.c
price_change = (current_price - prev_price) / prev_price * 100
trend_status = "Growth RISING" if price_change > 0 else "📉 FALLING" if price_change < 0 else "➖ FLAT"

print(f" Daily change: {price_change:+.2f}% ({trend_status})")

    # Step 6: Analyze carry trade viability
    print(f"\nCarry Trade Viability Analysis:")

    # Theoretical interest differential (AUD 4.25% - JPY 0.10% = 4.15%)
    theoretical_carry = 4.15  # Annual percentage
    daily_carry_rate = theoretical_carry / 365
    position_size = 100000  # 1 standard lot

    # Calculate potential daily earnings
    position_value_aud = position_size  # 100,000 AUD
    daily_carry_aud = position_value_aud * (daily_carry_rate / 100)
    daily_carry_jpy = daily_carry_aud * current_price  # Convert to JPY

    print(f" Position size: {position_size:,} AUD (1 standard lot)")
    print(f"   Interest differential: +{theoretical_carry:.2f}% annually")
    print(f" Daily carry estimate: {daily_carry_aud:.2f} AUD (~{daily_carry_jpy:.0f} JPY)")
    print(f" Monthly estimate: ~{daily_carry_aud * 30:.2f} AUD")
    print(f" Annual estimate: ~{daily_carry_aud * 365:.2f} AUD")

    # Step 7: Risk assessment for carry trades
    print(f"\n⚠️ Carry Trade Risk Assessment:")

    # Calculate risk scenarios
    daily_volatility = 0.5  # Typical daily volatility in %
    position_value_usd = position_size * current_price / 110  # Rough USD conversion
    daily_risk_usd = position_value_usd * (daily_volatility / 100)

    print(f" Daily carry income: ~${daily_carry_aud:.2f}")
    print(f"   ⚠️ Daily volatility risk: ~${daily_risk_usd:.2f} (1 standard deviation)")

    risk_reward_ratio = daily_risk_usd / daily_carry_aud if daily_carry_aud > 0 else Decimal('Infinity')
    print(f" Risk/Carry ratio: {risk_reward_ratio:.1f}:1")

    if risk_reward_ratio > 10:
risk_assessment = "HIGH RISK - Volatility overwhelms carry"
    elif risk_reward_ratio > 5:
risk_assessment = "MODERATE RISK - Manage position size"
    else:
risk_assessment = "REASONABLE - Good carry opportunity"

    print(f" Assessment: {risk_assessment}")

    # Step 8: Get account information for position sizing
    print(f"\nAccount Suitability for Carry Trading:")
    account = await client.accounts.get_account(account_id)
    account_balance = account.balance

    # Calculate appropriate position size for carry trading
    # Carry trades typically use lower leverage due to longer holding periods
    conservative_leverage = 5  # 5:1 leverage for carry trades
    max_position_value = account_balance * conservative_leverage
    max_aud_units = max_position_value / current_price * 110  # Rough calculation

    print(f" Account balance: ${account_balance:,.2f}")
    print(f" Conservative leverage: {conservative_leverage}:1 (lower for carry trades)")
    print(f" Max recommended position: {max_aud_units:,.0f} AUD units")
    print(f" Conservative position: {max_aud_units/2:,.0f} AUD units (50% of max)")

    # Step 9: Carry trade best practices
    print(f"\nCarry Trade Best Practices:")
    print(f"   Time horizon: Medium to long-term (weeks to months)")
    print(f" Leverage: Use conservative leverage (5:1 or less)")
    print(f"   Diversification: Don't put all capital in carry trades")
    print(f" Trend alignment: Best when currency trend supports carry")
    print(f"   ⚠️ Risk management: Set wide stops, expect volatility")
    print(f" Monitoring: Watch central bank policy changes")

    # Step 10: Market conditions affecting carry trades
    print(f"\nMarket Conditions for Carry Trades:")
    print(f" FAVORABLE:")
    print(f"• Stable/rising risk sentiment")
    print(f"• Widening interest rate differentials")
    print(f"• Low market volatility")
    print(f"• Supportive economic fundamentals")

    print(f"   Error: UNFAVORABLE:")
    print(f"• Risk-off sentiment / market stress")
    print(f"• Narrowing rate differentials")
    print(f"• High volatility periods")
    print(f"• Central bank policy uncertainty")

    except Exception as e:
    print(f"\nError: Carry trade analysis failed: {e}")
    print(f" Note: This demonstrates carry trade concepts with simulated data")
    print(f"Real implementation needs actual swap/rollover rates from broker")

    # Step 11: Provide educational information even if API fails
    print(f"\n📚 Carry Trade Educational Summary:")
    print(f"   Interest differential drives carry trade profitability")
    print(f" Popular pairs: AUD_JPY, NZD_JPY, GBP_JPY (high vs low yield)")
    print(f"   ⚠️ Major risk: Currency depreciation can overwhelm interest income")
    print(f"   Timeline: Longer holding periods to benefit from rollover")
    print(f" Strategy: Combine with technical/fundamental analysis")

# Execute carry trade analysis
await check_carry_trade()

```

### Currency Hedging

Protect against currency risk:

<!-- fragment: Demo currency hedging strategy with comprehensive exposure management -->
```python
from decimal import Decimal
from fivetwenty import AsyncClient

# Step 1: Understand currency hedging fundamentals
# If you have EUR exposure from business but trade with USD account, you have currency risk
print(f"Currency Hedging: Managing Cross-Currency Exposure")

async def hedge_currency_exposure() -> None:
    """Hedge currency exposure with comprehensive risk management analysis."""
    # Step 2: Initialize client and define business exposure scenario
    client = AsyncClient()
    account_id = "your-account-id"

    # Example business scenario: European client owes you 100,000 EUR
    business_eur_exposure = 100000  # EUR exposure from business operations
    payment_due_days = 30# Payment expected in 30 days

    print(f"\nBusiness Exposure Scenario:")
    print(f" EUR receivable: €{business_eur_exposure:,}")
    print(f"   Account currency: USD")
    print(f"   Payment timeline: {payment_due_days} days")
    print(f"   ⚠️ Currency risk: EUR might weaken vs USD before payment")

    # Step 3: Analyze current exchange rate and potential risk
    try:
    # Get current EUR_USD pricing
    pricing = await client.pricing.get_pricing(account_id, ["EUR_USD"])
    current_rate = pricing.prices[0].bids[0].price  # Use bid for selling EUR

    print(f"\nCurrent Market Analysis:")
    print(f" Current EUR_USD rate: {current_rate}")
    print(f" Current USD value: ${current_rate * business_eur_exposure:,.2f}")

    # Calculate potential currency risk scenarios
    risk_scenarios = [
    (0.95, "5% EUR decline"),
    (0.90, "10% EUR decline"),
    (0.85, "15% EUR decline")
    ]

    print(f"\n⚠️ Currency Risk Scenarios:")
    for multiplier, scenario in risk_scenarios:
    scenario_rate = current_rate * multiplier
    scenario_value = scenario_rate * business_eur_exposure
    value_loss = (current_rate * business_eur_exposure) - scenario_value

    print(f"   {scenario}: Rate {scenario_rate:.4f}")
    print(f"   USD value: ${scenario_value:,.2f}")
    print(f"   Loss: ${value_loss:,.2f}")

    # Step 4: Calculate optimal hedge position
    # Natural hedge: Go short EUR_USD to offset EUR exposure
    print(f"\nHedging Strategy Analysis:")

    hedge_position = -business_eur_exposure  # Opposite position (short EUR)
    hedge_percentage = 100  # 100% hedge for this example

    print(f" Strategy: SHORT EUR_USD to hedge EUR exposure")
    print(f" Hedge size: {abs(hedge_position):,} EUR units")
    print(f" Direction: SHORT (sell EUR, buy USD)")
    print(f" Hedge ratio: {hedge_percentage}% of exposure")

    # Step 5: Explain hedging mechanics
    print(f"\nHedging Mechanics:")
    print(f" exposure: +€{business_eur_exposure:,} (receive EUR)")
    print(f" Hedge position: {hedge_position:,} EUR units (short EUR_USD)")
    print(f" Net EUR exposure: €0 (fully hedged)")
    print(f" Result: Protected against EUR/USD rate changes")

    # Step 6: Calculate hedge effectiveness
    print(f"\nHedge Effectiveness Analysis:")

    # Simulate EUR decline scenario with hedge
    eur_decline_scenario = 0.90  # 10% decline
    new_rate = current_rate * eur_decline_scenario

    # Business exposure impact
    original_value = current_rate * business_eur_exposure
    new_business_value = new_rate * business_eur_exposure
    business_loss = original_value - new_business_value

    # Hedge position impact (profit on short position)
    hedge_entry_price = current_rate
    hedge_exit_price = new_rate
    hedge_profit = (hedge_entry_price - hedge_exit_price) * abs(hedge_position)

    net_result = hedge_profit - business_loss

    print(f" EUR declines 10% scenario:")
    print(f"   loss: ${business_loss:,.2f}")
    print(f"   Hedge profit: ${hedge_profit:,.2f}")
    print(f"   Net result: ${net_result:+.2f} (near zero = effective hedge)")

    # Step 7: Execute hedge position
    print(f"\nExecuting Hedge Position:")

    try:
    hedge_order = await client.orders.post_market_order(
account_id=account_id,
instrument="EUR_USD",
units=hedge_position  # Negative = short EUR
    )

    print(f" Hedge order executed successfully")
    print(f" Order ID: {hedge_order.order_create_transaction.id}")

    if hedge_order.order_fill_transaction:
fill_price = hedge_order.order_fill_transaction.price
print(f" Fill price: {fill_price}")
print(f"   Hedge active: EUR exposure now neutralized")

# Calculate hedge cost (spread)
spread_cost = (pricing.prices[0].asks[0].price - fill_price) * abs(hedge_position)
print(f" Hedge cost (spread): ${spread_cost:.2f}")

    except Exception as e:
    print(f"   Error: Hedge execution failed: {e}")
    print(f"   Note: Check margin requirements and market conditions")

    # Step 8: Alternative hedging strategies
    print(f"\nAlternative Hedging Approaches:")

    hedging_alternatives = [
    ("100% Hedge", "Full protection, no upside", hedge_position),
    ("75% Hedge", "Partial protection, some upside", int(hedge_position * 0.75)),
    ("50% Hedge", "Balanced approach", int(hedge_position * 0.50)),
    ("No Hedge", "Full exposure, maximum risk/reward", 0)
    ]

    for strategy, description, position_size in hedging_alternatives:
    hedge_ratio = abs(position_size) / business_eur_exposure * 100 if position_size != 0 else 0
    print(f"   • {strategy}: {description}")
    print(f"Position: {position_size:,} EUR units ({hedge_ratio:.0f}% hedge)")

    # Step 9: Hedging timeline considerations
    print(f"\nHedging Timeline Management:")
    print(f" Immediate hedge: Protect against adverse moves")
    print(f"   Rolling hedge: Adjust as payment date approaches")
    print(f"   Partial unwind: Reduce hedge if EUR strengthens")
    print(f" Full unwind: Close hedge when payment received")

    # Step 10: Cost-benefit analysis
    print(f"\nHedging Cost-Benefit Analysis:")

    # Estimate hedging costs
    estimated_spread = 0.0002  # 0.2 pips
    hedging_cost = estimated_spread * abs(hedge_position)
    protection_value = business_eur_exposure * 0.05 * current_rate  # 5% protection

    print(f" Estimated hedging cost: ${hedging_cost:.2f}")
    print(f"   Protection value (5% move): ${protection_value:.2f}")
    print(f" Cost/benefit ratio: {hedging_cost/protection_value:.3f}")

    if hedging_cost / protection_value < 0.1:  # Less than 10% of protection value
    recommendation = "RECOMMENDED - Low cost for good protection"
    elif hedging_cost / protection_value < 0.2:
    recommendation = "CONSIDER - Moderate cost for protection"
    else:
    recommendation = "⚠️ EXPENSIVE - High cost relative to protection"

    print(f" Recommendation: {recommendation}")

    except Exception as e:
    print(f"\nError: Currency hedging analysis failed: {e}")
    print(f" Note: This demonstrates hedging concepts")

    # Step 11: Educational summary even if API fails
    print(f"\n📚 Currency Hedging Summary:")
    print(f" Purpose: Reduce currency risk from business operations")
    print(f"   Method: Opposite forex position to offset exposure")
    print(f"   ⚠️ Trade-off: Protection vs potential upside")
    print(f" Timing: Balance cost vs risk tolerance")
    print(f"   Strategy: Can be partial or full hedge")

# Execute currency hedging analysis
print(f"Executing Currency Hedging Analysis...")
await hedge_currency_exposure()
print("\nCurrency hedging analysis complete")

```

---

## SDK-Specific Considerations

### Decimal Precision

The SDK uses `Decimal` for financial accuracy:
<!-- fragment: Demo decimal precision handling with forex-specific rounding -->
```python
from decimal import ROUND_HALF_UP, Decimal

# Step 1: Understand forex decimal precision requirements
# Different currency pairs require different decimal precision levels
print(f" FiveTwenty SDK Decimal Precision for Forex Trading")

# Step 2: Handle major currency pairs (5-decimal precision)
# Most major pairs like EUR_USD, GBP_USD use 5 decimal places
price = Decimal("1.10505")  # Raw price with 5-decimal precision
rounded_price = price.quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP)

print(f"\nMajor Pairs Precision (5 decimals):")
print(f" Original price: {price}")
print(f" Rounded to 4 decimals: {rounded_price}")
print(f"   Note: Examples: EUR_USD, GBP_USD, AUD_USD, NZD_USD")
print(f" Pip = 0.0001 (4th decimal place)")

# Step 3: Handle JPY pairs (3-decimal precision)
# JPY pairs like USD_JPY, EUR_JPY use 3 decimal places
jpy_price = Decimal("110.505")
jpy_rounded = jpy_price.quantize(Decimal("0.001"), rounding=ROUND_HALF_UP)

print(f"\n🇯🇵 JPY Pairs Precision (3 decimals):")
print(f" Original price: {jpy_price}")
print(f" Rounded to 3 decimals: {jpy_rounded}")
print(f"   Note: Examples: USD_JPY, EUR_JPY, GBP_JPY, AUD_JPY")
print(f" Pip = 0.01 (2nd decimal place)")

# Step 4: Demonstrate precision importance in trading calculations
print(f"\n⚠️ Why Precision Matters:")

# Example calculation showing precision impact
position_size = 100000  # 1 standard lot
price_difference = Decimal("0.0001")  # 1 pip movement

# Correct calculation with Decimal
decimal_calculation = price_difference * position_size

# Demonstrate precision by showing exact vs approximated calculations
approximate_result = 0.0001 * 100000  # Using regular numbers (imprecise)
exact_result = decimal_calculation  # Using Decimal (exact)

print(f" 1 pip movement on 100k units:")
print(f"   Decimal calculation: ${exact_result} (exact)")
print(f"Approximate calculation: ${approximate_result} (may have rounding errors)")
print(f"   Note: Always use Decimal for financial calculations!")

# Step 5: Practical precision examples for different scenarios
print(f"\nPractical Precision Examples:")

# Price precision examples
precision_examples = [
    ("EUR_USD", Decimal("1.23456"), Decimal("0.0001"), "Major pair"),
    ("USD_JPY", Decimal("145.678"), Decimal("0.01"), "JPY pair"),
    ("EUR_GBP", Decimal("0.87654"), Decimal("0.0001"), "Cross pair"),
    ("USD_CHF", Decimal("0.91234"), Decimal("0.0001"), "Major pair"),
]

for pair, price, precision, pair_type in precision_examples:
    rounded = price.quantize(precision, rounding=ROUND_HALF_UP)
    print(f"   {pair}: {price} → {rounded} ({pair_type})")

# Step 6: Position sizing with proper precision
print(f"\nPosition Sizing with Decimal Precision:")

# Example position sizing calculation
account_balance = Decimal("10000.00")  # $10,000 account
risk_percentage = Decimal("0.02")  # 2% risk
stop_loss_pips = Decimal("50")  # 50 pip stop loss
pip_value = Decimal("1.00")  # $1 per pip for 10k units

# Calculate position size using Decimal arithmetic
max_risk = account_balance * risk_percentage
risk_per_pip = stop_loss_pips * pip_value
position_size = max_risk / risk_per_pip * 10000  # Convert to units

print(f" Account balance: ${account_balance}")
print(f"   ⚠️ Max risk (2%): ${max_risk}")
print(f" Stop loss: {stop_loss_pips} pips")
print(f" Calculated position: {position_size:,.0f} units")
print(f" All calculations use Decimal for accuracy")

# Step 7: Common precision pitfalls to avoid
print(f"\n⚠️ Common Precision Pitfalls:")
print(f"   Using float for money: Introduces rounding errors")
print(f"   Error: Wrong pip size: Using 0.0001 for JPY pairs")
print(f"   ⚠️ String conversion: Converting Decimal to string loses precision")
print(f" formatting: Different from calculation precision")

# Step 8: FiveTwenty SDK integration
print(f"\n💻 FiveTwenty SDK Decimal Integration:")
print(f" Automatic handling: SDK converts Decimal to strings for API")
print(f" Price parsing: Convert API strings back to Decimal")
print(f"   Package stringify_decimals(): Utility function for API calls")
print(f" Best practice: Keep all calculations in Decimal throughout")

# Step 9: Rounding modes for different use cases
print(f"\nRounding Modes for Trading:")

rounding_examples = [
    (ROUND_HALF_UP, "Standard rounding (most common)"),
    # Note: Other rounding modes available but ROUND_HALF_UP is standard
]

test_price = Decimal("1.23455")
for rounding_mode, description in rounding_examples:
    rounded = test_price.quantize(Decimal("0.0001"), rounding=rounding_mode)
    print(f"   {description}: {test_price} → {rounded}")

print(f"   Note: ROUND_HALF_UP is standard for forex pricing")

# Step 10: Performance considerations
print(f"\nPerformance Considerations:")
print(f" Decimal vs float: Slightly slower but necessary for accuracy")
print(f"   Memory usage: Decimal uses more memory than float")
print(f" Trade-off: Accuracy is essential for financial calculations")
print(f" Conclusion: Always use Decimal for money and prices")

```

### Streaming Data Usage

Real-time price feeds for active trading:

<!-- fragment: Demo real-time streaming data with comprehensive price monitoring -->
```python
import asyncio
from datetime import datetime
from fivetwenty import AsyncClient


async def main() -> None:
    """Main streaming example with comprehensive real-time price monitoring."""
    # Step 1: Initialize streaming setup for real-time market data
    # Streaming provides live price feeds essential for active trading
    client = AsyncClient()
    account_id = "your-account-id"
    instruments = ["EUR_USD", "GBP_USD"]

    print(f"Signal FiveTwenty Real-Time Streaming Setup")
    print(f"   Instruments: {', '.join(instruments)}")
    print(f"   Starting live price monitoring...")

    # Step 2: Initialize streaming statistics
    stream_stats = {
    "price_updates": 0,
    "heartbeats": 0,
    "start_time": datetime.now(),
    "last_prices": {}
    }

    async def price_monitor() -> None:
    """Monitor real-time prices for trading signals with comprehensive analysis."""
    print(f"\nLive Price Stream Active:")

    try:
    # Step 3: Enter streaming loop for continuous price updates
    async for price_data in client.pricing.get_pricing_stream(account_id, instruments):

# Step 4: Handle price updates with detailed analysis
if hasattr(price_data, 'type') and price_data.type == "PRICE":
# Extract price components for analysis
instrument = price_data.instrument
current_bid = price_data.bids[0].price
current_ask = price_data.asks[0].price
timestamp = price_data.time

# Update streaming statistics
stream_stats["price_updates"] += 1
stream_stats["last_prices"][instrument] = {
    "bid": current_bid,
    "ask": current_ask,
    "time": timestamp
}

# Calculate spread for market quality assessment
spread = current_ask - current_bid
spread_pips = spread * 10000

# Display price update with market analysis
print(f" {instrument}: {current_bid}/{current_ask}")
print(f"   Spread: {spread_pips:.1f} pips")
print(f"Time: {timestamp}")
print(f"   Updates: {stream_stats['price_updates']}")

# Step 5: Implement basic trading signal detection
await analyze_price_movement(instrument, current_bid, current_ask, stream_stats)

# Step 6: Monitor streaming performance
if stream_stats["price_updates"] % 10 == 0:  # Every 10 updates
    await display_streaming_stats(stream_stats)

# Step 7: Handle heartbeat messages for connection health
elif hasattr(price_data, 'type') and price_data.type == "HEARTBEAT":
# Keep-alive signal - connection is healthy
stream_stats["heartbeats"] += 1

# Periodic heartbeat logging
if stream_stats["heartbeats"] % 5 == 0:
    print(f"   Heart Heartbeat #{stream_stats['heartbeats']} - Connection healthy")

# Step 8: Handle other message types
else:
message_type = getattr(price_data, 'type', 'UNKNOWN')
print(f"   Note: Other message: {message_type}")

    except Exception as e:
    print(f"\nError: Streaming error: {e}")
    print(f" Check connection, credentials, and market hours")

    async def analyze_price_movement(instrument: str, bid: str, ask: str, stats: dict) -> None:
    """Analyze price movement for trading signals."""
    # Step 9: Implement simple trading signal logic
    # This is where your trading algorithms would analyze price data

    if instrument in stats["last_prices"]:
    previous_data = stats["last_prices"][instrument]

    # Calculate price change since last update
    mid_price = (bid + ask) / 2
    prev_bid = previous_data["bid"]
    prev_ask = previous_data["ask"]
    prev_mid = (prev_bid + prev_ask) / 2

    price_change = mid_price - prev_mid
    price_change_pips = price_change * 10000

    # Signal detection (basic example)
    if abs(price_change_pips) > 0.5:  # Significant move (>0.5 pips)
direction = "Growth UP" if price_change > 0 else "📉 DOWN"
print(f"MOVE: {direction} {abs(price_change_pips):.1f} pips")

# Here you would implement your trading logic:
# - Technical analysis
# - Risk management
# - Order placement
# await execute_trading_logic(instrument, direction, price_change_pips)

    async def display_streaming_stats(stats: dict) -> None:
    """Display comprehensive streaming performance statistics."""
    # Step 10: Calculate streaming performance metrics
    runtime = (datetime.now() - stats["start_time"]).total_seconds()
    updates_per_second = stats["price_updates"] / runtime if runtime > 0 else 0

    print(f"\nStreaming Performance:")
    print(f"   Runtime: {runtime:.1f} seconds")
    print(f" Price updates: {stats['price_updates']}")
    print(f"   Heart Heartbeats: {stats['heartbeats']}")
    print(f"   Update rate: {updates_per_second:.1f} updates/sec")

    # Display last known prices
    print(f" Last prices:")
    for instrument, data in stats["last_prices"].items():
    print(f"{instrument}: {data['bid']}/{data['ask']}")

    # Step 11: Start price monitoring with error handling
    try:
    await price_monitor()
    except KeyboardInterrupt:
    print(f"\nStreaming stopped by user")
    await display_streaming_stats(stream_stats)
    except Exception as e:
    print(f"\nError: Streaming failed: {e}")
    print(f"Ensure valid credentials and market hours")


if __name__ == "__main__":
    # Step 12: Run streaming with comprehensive setup
    print(f" FiveTwenty Real-Time Streaming Example")
    print(f" Press Ctrl+C to stop streaming gracefully")

    try:
    asyncio.run(main())
    except KeyboardInterrupt:
    print(f"\nStreaming session ended")
    except Exception as e:
    print(f"\nError: Streaming setup failed: {e}")
    print(f"Check your FiveTwenty configuration and try again")

```

### Error Handling in Trading Context

<!-- fragment: Demo comprehensive trading error handling with recovery strategies -->
```python
import asyncio
import logging
from datetime import datetime
from decimal import Decimal
from typing import Optional
from fivetwenty import AsyncClient
from fivetwenty.exceptions import FiveTwentyError


async def handle_trading_errors() -> None:
    """Handle trading errors properly with comprehensive recovery strategies."""
    # Step 1: Initialize comprehensive error handling system
    # Proper error handling prevents system failures and protects capital
    print(f"Comprehensive Trading Error Handling System")

    # Setup logging for error tracking
    logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger(__name__)

    client = AsyncClient()
    account_id = "your-account-id"

    # Step 2: Initialize error tracking statistics
    error_stats = {
    "total_attempts": 0,
    "successful_orders": 0,
    "errors_by_type": {},
    "recovery_attempts": 0,
    "session_start": datetime.now()
    }

    def calculate_affordable_size(balance: str) -> int:
    """Calculate affordable position size based on account balance."""
    # Conservative sizing: 1% of balance converted to position units
    balance_decimal = Decimal(balance)
    conservative_percentage = Decimal('0.01')  # 1% of balance
    affordable_value = balance_decimal * conservative_percentage

    # Convert to position units (rough calculation)
    # For EUR_USD at ~1.10, this gives reasonable position size
    position_units = int(affordable_value * 10)  # Rough conversion

    print(f" Balance: ${balance}")
    print(f" Affordable size: {position_units:,} units (1% risk)")
    return position_units

    async def attempt_order_with_recovery(instrument: str, units: int, max_retries: int = 3) -> Optional[dict]:
    """Attempt order placement with intelligent recovery strategies."""
    # Step 3: Implement robust order placement with retry logic

    for attempt in range(max_retries):
    error_stats["total_attempts"] += 1
    attempt_number = attempt + 1

    print(f"\nOrder Attempt #{attempt_number}:")
    print(f"   Instrument: {instrument}")
    print(f" Size: {units:,} units")

    try:
# Step 4: Attempt order placement
order = await client.orders.post_market_order(
account_id=account_id,
instrument=instrument,
units=units
)

# Good: path
error_stats["successful_orders"] += 1
print(f" Order successful on attempt #{attempt_number}")
print(f" Order ID: {order.order_create_transaction.id}")

if order.order_fill_transaction:
print(f" Fill price: {order.order_fill_transaction.price}")

return order

    except FiveTwentyError as e:
# Step 5: Analyze error type and implement specific recovery
error_type = str(e)
error_stats["errors_by_type"][error_type] = error_stats["errors_by_type"].get(error_type, 0) + 1

print(f"   Error: Attempt #{attempt_number} failed: {e}")
logger.error(f"Trading error on attempt {attempt_number}: {e}")

# Step 6: Implement error-specific recovery strategies
if "INSUFFICIENT_MARGIN" in error_type:
print(f"   ⚠️ INSUFFICIENT_MARGIN detected - reducing position size")

# Get current account status
account = await client.accounts.get_account(account_id)
available_margin = account.margin_available

print(f"   Available margin: ${available_margin}")

if available_margin > 100:  # Minimum margin threshold
    # Calculate smaller, affordable position size
    smaller_size = calculate_affordable_size(account.balance)

    if smaller_size < units:
    units = smaller_size
    error_stats["recovery_attempts"] += 1
    print(f"   Reduced size to: {units:,} units")
    print(f"Retrying with smaller position...")
    continue  # Retry with smaller size
    else:
    print(f"Error: Cannot reduce size further - insufficient funds")
    break
else:
    print(f"Error: Insufficient margin ({available_margin}) - cannot trade")
    break

elif "MARKET_HALTED" in error_type:
print(f"   ⏸️ MARKET_HALTED detected - implementing wait strategy")

if attempt < max_retries - 1:  # Don't wait on final attempt
    wait_time = 30 * (attempt + 1)  # Progressive wait: 30s, 60s, 90s
    print(f"Waiting {wait_time} seconds for market to reopen...")
    await asyncio.sleep(wait_time)
    error_stats["recovery_attempts"] += 1
    print(f"Retrying after market halt...")
    continue
else:
    print(f"Error: Market halt persists - abandoning order")
    break

elif "INVALID_INSTRUMENT" in error_type:
print(f"   Error: INVALID_INSTRUMENT - cannot recover")
print(f"Note: Check instrument name and market hours")
break

elif "ACCOUNT_NOT_ACTIVE" in error_type:
print(f"   Error: ACCOUNT_NOT_ACTIVE - cannot recover")
print(f"Note: Check account status with broker")
break

elif "INSUFFICIENT_AUTHORIZATION" in error_type:
print(f"   Error: INSUFFICIENT_AUTHORIZATION - cannot recover")
print(f"Note: Check API token permissions")
break

elif "PRICE_INVALID" in error_type:
print(f"   ⚠️ PRICE_INVALID - market conditions issue")

if attempt < max_retries - 1:
    wait_time = 5 * (attempt + 1)  # Short wait for price issues
    print(f"Waiting {wait_time}s for price stabilization...")
    await asyncio.sleep(wait_time)
    error_stats["recovery_attempts"] += 1
    continue
else:
    print(f"Error: Persistent pricing issues - abandoning order")
    break

else:
# Step 7: Handle unexpected errors with logging
print(f"   ⚠️ Unexpected error type: {error_type}")
logger.error(f"Unexpected trading error: {e}")

# Generic retry with exponential backoff for unknown errors
if attempt < max_retries - 1:
    wait_time = 2 ** attempt  # Exponential backoff: 1s, 2s, 4s
    print(f"Implementing exponential backoff: {wait_time}s")
    await asyncio.sleep(wait_time)
    error_stats["recovery_attempts"] += 1
    continue
else:
    print(f"Error: Max retries exceeded for unknown error")
    break

    # Step 8: All retry attempts exhausted
    print(f"\nError: Order placement failed after {max_retries} attempts")
    return None

    # Step 9: Execute comprehensive error handling demonstration
    print(f"\nError Handling Scenarios:")

    # Test scenarios with different error conditions
    test_scenarios = [
    ("EUR_USD", 10000, "Normal order attempt"),
    ("EUR_USD", 1000000, "Large order (may trigger margin error)"),
    ("INVALID_PAIR", 10000, "Invalid instrument test"),
    ]

    for instrument, units, description in test_scenarios:
    print(f"\nScenario: {description}")
    result = await attempt_order_with_recovery(instrument, units)

    if result:
    print(f" Scenario completed successfully")
    else:
    print(f"   Error: Scenario failed - all recovery attempts exhausted")

    # Step 10: Display comprehensive error handling statistics
    print(f"\nError: Handling Session Statistics:")
    session_duration = (datetime.now() - error_stats["session_start"]).total_seconds()
    success_rate = (error_stats["successful_orders"] / error_stats["total_attempts"]) * 100 if error_stats["total_attempts"] > 0 else 0

    print(f"   Session duration: {session_duration:.1f} seconds")
    print(f"   Total attempts: {error_stats['total_attempts']}")
    print(f" Successful orders: {error_stats['successful_orders']}")
    print(f"   Recovery attempts: {error_stats['recovery_attempts']}")
    print(f" rate: {success_rate:.1f}%")

    print(f"\n📉 Error Breakdown:")
    for error_type, count in error_stats["errors_by_type"].items():
    print(f"   • {error_type}: {count} occurrences")

    # Step 11: Provide error handling best practices summary
    print(f"\nNote: Error Handling Best Practices:")
    print(f"   Retry Logic: Implement intelligent retry with different strategies")
    print(f"   Backoff Strategy: Use progressive delays between retries")
    print(f" Position Sizing: Automatically reduce size for margin errors")
    print(f" Logging: Comprehensive error logging for analysis")
    print(f"   ⚠️ Error Classification: Different recovery strategies per error type")
    print(f"   Graceful Degradation: Fail safely when recovery isn't possible")
    print(f" Monitoring: Track error rates and patterns for improvement")


# Execute comprehensive error handling demonstration
print(f"Starting Comprehensive Trading Error Handling Demo")
print(f" This demonstrates robust error recovery strategies")

try:
    asyncio.run(handle_trading_errors())
except Exception as e:
    print(f"\nError: Demo failed: {e}")
    print(f"Note: Some errors are expected for demonstration purposes")

print(f"\nError: handling demonstration complete")

```

---

## Conclusion

These concepts map directly onto how you use FiveTwenty:

1. **Structure Your Code**: Know when to use trades vs. positions
2. **Manage Risk**: Implement proper position sizing and margin monitoring
3. **Handle Market Realities**: Account for spreads, slippage, and market sessions
4. **Handle Failures**: Write error handling that fits trading scenarios
5. **Optimize Performance**: Use appropriate order types and timing

The SDK hides much of the mechanical complexity, but knowing the forex mechanics underneath makes your applications safer.

Remember: Forex trading involves substantial risk. Always test thoroughly in the practice environment before using real money.
