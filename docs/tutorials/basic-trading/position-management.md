# Position Management

!!! tip "Target Learning Goal"
    Master advanced position management techniques including stop losses, take profits, and risk-to-reward optimization.

---

## Understanding Position Management

Position management is the art of maximizing profits while controlling risk after entering a trade. Once you've entered a position, your success depends on how well you manage it through to exit - setting protective stop losses to limit downside risk, placing take profit targets to lock in gains, and monitoring your trades to make informed decisions about when to exit or adjust. Effective position management involves understanding your position's current profit and loss, calculating appropriate exit levels based on your risk tolerance, and implementing a risk-to-reward ratio that ensures your winning trades outweigh your losses.

In this comprehensive tutorial, you'll master position management using the FiveTwenty SDK with complete, executable examples. You'll learn to monitor open positions using `client.trades.get_trades()`, implement multiple stop loss strategies with `client.trades.put_trade_orders()`, calculate risk-to-reward ratios programmatically, and determine optimal position sizes based on account balance and volatility. Each code example demonstrates real SDK integration with OANDA, complete with proper error handling, type safety, and production-ready patterns you can use immediately in your trading systems.

This example demonstrates the fundamentals of position monitoring and exit planning. You'll learn to retrieve open trades, analyze their current state, calculate appropriate stop loss and take profit levels, and understand how to implement these protective orders using FiveTwenty's order management features:

```python
import asyncio
from decimal import Decimal

from dotenv import load_dotenv
from fivetwenty import AsyncClient

# ==============================================================================
# ENVIRONMENT SETUP
# ==============================================================================

# Load API credentials from .env file
# The AsyncClient automatically reads these environment variables:
#   - FIVETWENTY_OANDA_TOKEN: Your OANDA API token
#   - FIVETWENTY_OANDA_ACCOUNT: Your OANDA account ID
#   - FIVETWENTY_OANDA_ENVIRONMENT: "practice" or "live" (defaults to practice)
load_dotenv()


# ==============================================================================
# POSITION MONITORING AND EXIT LEVEL CALCULATION
# ==============================================================================

async def main() -> None:
    """
    Monitor an open position and calculate exit levels.

    This example demonstrates fundamental position management:
    1. Retrieving open trades using the SDK
    2. Analyzing current position state (P&L, direction, entry price)
    3. Calculating appropriate stop loss and take profit levels
    4. Implementing a 1:1.5 risk-to-reward ratio
    """

    # ==============================================================================
    # CONNECT TO OANDA
    # ==============================================================================

    # AsyncClient automatically reads FIVETWENTY_OANDA_* environment variables
    # Context manager ensures proper cleanup of HTTP connections
    async with AsyncClient() as client:

        # ==============================================================================
        # STEP 1: RETRIEVE ALL OPEN TRADES
        # ==============================================================================

        # The SDK method: client.trades.get_trades()
        #
        # Parameters:
        #   - account_id: Your OANDA account ID (available as client.account_id)
        #
        # Returns: TypedDict with structure:
        #   {
        #       "trades": list[Trade],        # List of Pydantic Trade models
        #       "lastTransactionID": str
        #   }
        #
        # NOTE: Response is a TypedDict, so use dictionary access: response["trades"]
        #       Each Trade is a Pydantic model, so use attribute access: trade.price
        response = await client.trades.get_trades(client.account_id)
        trades = response["trades"]

        if not trades:
            print("No open trades found. Open a position first to try this example.")
            print("\nTo open a position, you can use:")
            print("  await client.orders.post_market_order(")
            print("      account_id=client.account_id,")
            print("      instrument='EUR_USD',")
            print("      units=1000")
            print("  )")
            return

        # ==============================================================================
        # STEP 2: ANALYZE THE FIRST OPEN TRADE
        # ==============================================================================

        # Each Trade model is a Pydantic model with attributes:
        #   - trade.id: str - Unique trade identifier
        #   - trade.instrument: str - Currency pair (e.g., "EUR_USD")
        #   - trade.price: Decimal - Entry price
        #   - trade.current_units: str - Position size (positive = long, negative = short)
        #   - trade.unrealized_pl: str - Current profit/loss (as string from API)
        #   - trade.initial_units: str - Original position size
        #   - trade.open_time: datetime - When position was opened
        trade = trades[0]

        print("=" * 60)
        print("POSITION MONITORING")
        print("=" * 60)
        print(f"\nMonitoring: {trade.instrument}")
        print(f"Trade ID: {trade.id}")
        print(f"Entry Price: {trade.price}")  # Already a Decimal from SDK
        print(f"Position Size: {trade.current_units} units")
        print(f"Current P&L: ${trade.unrealized_pl}")  # String from API

        # ==============================================================================
        # STEP 3: CALCULATE EXIT LEVELS BASED ON POSITION DIRECTION
        # ==============================================================================

        # Determine position direction from current_units
        # Positive units = long position (bought the base currency)
        # Negative units = short position (sold the base currency)
        is_long = int(trade.current_units) > 0

        # Define pip value for most forex pairs (4th decimal place)
        # For JPY pairs, you would use Decimal("0.01") (2nd decimal place)
        pip_value = Decimal("0.0001")

        print(f"\nPosition Direction: {'LONG (Buy)' if is_long else 'SHORT (Sell)'}")
        print("\nCalculating Exit Levels...")

        if is_long:
            # ==============================================================================
            # LONG POSITION EXIT LEVELS
            # ==============================================================================
            # For a long position:
            # - Stop loss goes BELOW entry price to limit downside
            # - Take profit goes ABOVE entry price to capture upside
            # - We use 20 pips for stop, 30 pips for profit (1:1.5 risk/reward)

            stop_loss = trade.price - (20 * pip_value)  # Risk 20 pips
            take_profit = trade.price + (30 * pip_value)  # Target 30 pips

            print(f"  Stop Loss:   {stop_loss:.5f} (20 pips below entry)")
            print(f"  Take Profit: {take_profit:.5f} (30 pips above entry)")
        else:
            # ==============================================================================
            # SHORT POSITION EXIT LEVELS
            # ==============================================================================
            # For a short position:
            # - Stop loss goes ABOVE entry price to limit downside
            # - Take profit goes BELOW entry price to capture profit
            # - We use 20 pips for stop, 30 pips for profit (1:1.5 risk/reward)

            stop_loss = trade.price + (20 * pip_value)  # Risk 20 pips
            take_profit = trade.price - (30 * pip_value)  # Target 30 pips

            print(f"  Stop Loss:   {stop_loss:.5f} (20 pips above entry)")
            print(f"  Take Profit: {take_profit:.5f} (30 pips below entry)")

        # ==============================================================================
        # DISPLAY RISK-REWARD ANALYSIS
        # ==============================================================================

        # Calculate risk and reward in pips
        risk_pips = abs(trade.price - stop_loss) / pip_value
        reward_pips = abs(take_profit - trade.price) / pip_value
        risk_reward_ratio = reward_pips / risk_pips

        print("\nRisk-Reward Analysis:")
        print(f"  Risk:   {risk_pips:.0f} pips")
        print(f"  Reward: {reward_pips:.0f} pips")
        print(f"  Ratio:  1:{risk_reward_ratio:.1f}")

        # Explain the ratio
        if risk_reward_ratio >= 1.5:
            print("\n Good risk-reward ratio!")
            print(f"  With 1:{risk_reward_ratio:.1f} R/R, you can be profitable even with <50% win rate.")
        else:
            print("\n⚠ Risk-reward ratio below 1.5:1 is suboptimal")
            print("  Consider widening your take profit or tightening your stop loss.")

        # ==============================================================================
        # NEXT STEPS
        # ==============================================================================

        print("\n" + "=" * 60)
        print("NEXT STEPS")
        print("=" * 60)
        print("\nTo implement these exit levels on your trade, use:")
        print("  Import StopLossDetails and TakeProfitDetails from fivetwenty.models")
        print()
        print("  stop_loss_details = StopLossDetails(price=stop_loss)")
        print("  take_profit_details = TakeProfitDetails(price=take_profit)")
        print()
        print("  await client.trades.put_trade_orders(")
        print("      account_id=client.account_id,")
        print("      trade_specifier=trade.id,")
        print("      stop_loss=stop_loss_details.model_dump(by_alias=True, exclude_none=True),")
        print("      take_profit=take_profit_details.model_dump(by_alias=True, exclude_none=True)")
        print("  )")


if __name__ == "__main__":
    # Run the async main function
    asyncio.run(main())
```

---

## Advanced Stop Loss Strategies

Stop losses are your primary defense against catastrophic losses in trading. A well-placed stop loss exits your position automatically when the market moves against you, protecting your capital from excessive drawdowns. However, not all stop loss strategies work equally well in all market conditions - volatile markets require wider stops to avoid premature exits, while ranging markets benefit from tighter stops placed just beyond recent support or resistance levels.

Professional traders use multiple stop loss methodologies depending on their strategy and market conditions. Fixed pip stops provide consistency and predictability, making them ideal for systematic strategies. Percentage-based stops scale with price levels, working well across different instruments and price ranges. ATR (Average True Range) based stops adapt to current market volatility, widening during volatile periods and tightening during quiet markets. Support and resistance stops leverage technical analysis, placing exits just beyond key price levels where the market has historically reversed.

The following example demonstrates four essential stop loss calculation methods. Each strategy has specific use cases: fixed pip stops for consistency, percentage stops for cross-instrument trading, ATR stops for volatility adaptation, and technical level stops for chart-based strategies. Understanding when to apply each method is crucial for effective risk management:

```python
import asyncio
from decimal import Decimal

from dotenv import load_dotenv
from fivetwenty import AsyncClient

# ==============================================================================
# ENVIRONMENT SETUP
# ==============================================================================

# Load API credentials from .env file
# The AsyncClient automatically reads these environment variables:
#   - FIVETWENTY_OANDA_TOKEN: Your OANDA API token
#   - FIVETWENTY_OANDA_ACCOUNT: Your OANDA account ID
#   - FIVETWENTY_OANDA_ENVIRONMENT: "practice" or "live" (defaults to practice)
load_dotenv()


# ==============================================================================
# ADVANCED STOP LOSS STRATEGIES
# ==============================================================================

async def main() -> None:
    """
    Demonstrate multiple stop loss calculation strategies using real trade data.

    This example covers four professional stop loss methodologies:
    1. Fixed Pip Stop: Simple, consistent risk across all trades
    2. Percentage Stop: Scales with price level for cross-instrument trading
    3. Technical Level Stop: Based on support/resistance chart analysis
    4. SDK Implementation: Actually setting the stop loss on a live trade

    Each strategy has specific use cases and trade-offs that traders must understand.
    """

    # ==============================================================================
    # CONNECT TO OANDA
    # ==============================================================================

    # AsyncClient automatically reads FIVETWENTY_OANDA_* environment variables
    # Context manager ensures proper cleanup of HTTP connections
    async with AsyncClient() as client:

        # ==============================================================================
        # STEP 1: RETRIEVE OPEN TRADES
        # ==============================================================================

        # The SDK method: client.trades.get_trades()
        #
        # Returns: TypedDict with structure:
        #   {
        #       "trades": list[Trade],        # List of Pydantic Trade models
        #       "lastTransactionID": str
        #   }
        #
        # Each Trade model contains:
        #   - trade.id: str - Unique identifier for the trade
        #   - trade.price: Decimal - Entry price (SDK provides as Decimal)
        #   - trade.current_units: str - Position size (positive=long, negative=short)
        #   - trade.instrument: str - Currency pair (e.g., "EUR_USD")
        response = await client.trades.get_trades(client.account_id)
        trades = response["trades"]

        if not trades:
            print("No open trades found. Open a position first to try this example.")
            return

        # ==============================================================================
        # STEP 2: ANALYZE TRADE FOR STOP LOSS CALCULATION
        # ==============================================================================

        # Get the first open trade - SDK provides complete position details
        trade = trades[0]
        entry_price = trade.price  # Already a Decimal from SDK (no conversion needed)
        is_long = int(trade.current_units) > 0  # Positive units = long, negative = short
        pip_value = Decimal("0.0001")  # Standard pip for most forex pairs

        print(f"Analyzing {trade.instrument} position:")
        print(f"Entry Price: {entry_price}")
        print(f"Direction: {'Long' if is_long else 'Short'}\n")

        print("Stop Loss Strategy Options:\n")

        # ==============================================================================
        # STRATEGY 1: FIXED PIP STOP
        # ==============================================================================
        # Simple and predictable - risk a fixed number of pips regardless of market conditions
        #
        # Use case: Systematic strategies that require consistent risk per trade
        # Pros: Easy to calculate, predictable risk, simple to backtest
        # Cons: Doesn't adapt to volatility or market structure

        if is_long:
            # For long positions, stop loss goes BELOW entry price
            fixed_stop = entry_price - (20 * pip_value)
        else:
            # For short positions, stop loss goes ABOVE entry price
            fixed_stop = entry_price + (20 * pip_value)
        print(f"1. Fixed 20-pip stop: {fixed_stop:.5f}")

        # ==============================================================================
        # STRATEGY 2: PERCENTAGE STOP
        # ==============================================================================
        # Scales with price level - useful when trading multiple instruments
        #
        # Use case: Trading instruments with vastly different price ranges
        # Pros: Scales automatically with price, works across all instruments
        # Cons: Same percentage = different pip amounts on different instruments

        if is_long:
            # Risk 0.5% below entry for long positions
            percentage_stop = entry_price * Decimal("0.995")  # 0.5% below entry
        else:
            # Risk 0.5% above entry for short positions
            percentage_stop = entry_price * Decimal("1.005")  # 0.5% above entry

        # Calculate how many pips this represents for comparison
        risk_pips = abs(entry_price - percentage_stop) / pip_value
        print(f"2. 0.5% stop: {percentage_stop:.5f} (Risk: {risk_pips:.1f} pips)")

        # ==============================================================================
        # STRATEGY 3: TECHNICAL LEVEL STOP (SUPPORT/RESISTANCE)
        # ==============================================================================
        # Based on chart technical levels where price historically reverses
        #
        # Use case: Discretionary trading based on technical analysis
        # Pros: Respects market structure, logical invalidation point
        # Cons: Requires chart analysis, subjective, varies per trade
        #
        # In practice, you would identify support/resistance from price action
        # Here we use an example level for demonstration purposes

        support_resistance = entry_price - Decimal("0.0050")  # Example: key level 50 pips below
        buffer = 5 * pip_value  # Add small buffer beyond the level (common practice)

        if is_long:
            # For long: stop below support with buffer
            tech_stop = support_resistance - buffer
        else:
            # For short: stop above resistance with buffer
            tech_stop = support_resistance + buffer
        print(f"3. Technical stop: {tech_stop:.5f} (5 pips beyond key level)")

        # ==============================================================================
        # STEP 3: IMPLEMENT STOP LOSS USING THE SDK
        # ==============================================================================

        print("\nSetting stop loss on trade using FiveTwenty SDK...")

        # We'll use the fixed 20-pip stop (simplest and most common approach)
        # Import the necessary model and exception types from FiveTwenty
        from fivetwenty.exceptions import FiveTwentyError
        from fivetwenty.models import StopLossDetails

        # Create StopLossDetails Pydantic model with our calculated price
        # This model validates the stop loss configuration before sending to API
        stop_loss_details = StopLossDetails(price=fixed_stop)

        try:
            # ==============================================================================
            # SDK METHOD: client.trades.put_trade_orders()
            # ==============================================================================
            #
            # This method updates an existing trade with protective orders
            #
            # Parameters:
            #   - account_id: Your OANDA account ID (available as client.account_id)
            #   - trade_specifier: Trade ID to update (from trade.id)
            #   - stop_loss: Stop loss configuration as dict
            #       * Must use model_dump(by_alias=True, exclude_none=True)
            #       * by_alias=True: Converts Python snake_case to API camelCase
            #       * exclude_none=True: Omits None values from the request
            #   - take_profit: Optional take profit configuration (not used here)
            #
            # The model_dump() method is crucial for Pydantic  API conversion:
            # - Converts Decimal to string (required by OANDA API)
            # - Maps field aliases (price  price for stop loss)
            # - Removes None values to avoid API errors

            await client.trades.put_trade_orders(
                account_id=client.account_id,
                trade_specifier=trade.id,
                stop_loss=stop_loss_details.model_dump(by_alias=True, exclude_none=True),
            )

            print(f" Stop loss set at {fixed_stop:.5f} (20 pips from entry)")
            print("  Your risk is now limited to approximately 20 pips on this trade.")

        except FiveTwentyError as e:
            # ==============================================================================
            # ERROR HANDLING: COMMON OANDA RESTRICTIONS
            # ==============================================================================
            #
            # OANDA has specific rules that can prevent stop loss placement:
            #
            # 1. FIFO (First In, First Out) violations:
            #    - Cannot have multiple positions of same size in same instrument
            #    - Must close oldest position first before modifying others
            #
            # 2. Minimum distance requirements:
            #    - Stop loss must be certain minimum pips from current price
            #    - Varies by instrument and market conditions
            #
            # 3. Position already closed:
            #    - Trade may have been closed between retrieval and update

            if "FIFO" in str(e):
                print("Note: Cannot set stop loss due to OANDA FIFO restrictions.")
                print("      (Multiple same-sized positions for same instrument)")
            else:
                print(f"Could not set stop loss: {e.message}")
            print(f"      Calculated stop loss level: {fixed_stop:.5f}")


if __name__ == "__main__":
    # Run the async main function
    asyncio.run(main())
```

---

## Take Profit Strategies

Take profit orders are equally important as stop losses for successful trading. While stop losses protect you from losses, take profits ensure you actually realize gains instead of watching profitable trades reverse against you. The challenge lies in balancing greed and prudence - exit too early and you leave money on the table, exit too late and you risk giving back hard-earned profits. Professional traders solve this dilemma through systematic take profit strategies rather than emotional decisions.

The most fundamental approach is the fixed target, where you exit at a predetermined pip level based on typical market moves for the instrument you're trading. More sophisticated traders use risk-reward ratios, ensuring their take profit target is at least 1.5 to 2 times their stop loss distance. This mathematical edge ensures that even with a 50% win rate, you remain profitable over time. Advanced traders often employ multiple take profit levels, scaling out of positions by taking partial profits at successive targets while letting a portion of the position run for larger gains.

This example demonstrates three key take profit methodologies. You'll see fixed pip targets for straightforward exit planning, risk-reward ratio calculations that maintain mathematical edge, and multiple target strategies for scaling out of positions. Understanding these approaches helps you exit trades strategically rather than emotionally:

```python
import asyncio
from decimal import Decimal

from dotenv import load_dotenv

from fivetwenty import AsyncClient
from fivetwenty.exceptions import FiveTwentyError
from fivetwenty.models import TakeProfitDetails

# ==============================================================================
# TAKE PROFIT STRATEGY CALCULATIONS
# ==============================================================================

# This example demonstrates three essential take profit calculation methodologies
# that professional traders use to exit positions strategically. Unlike stop losses
# which protect against losses, take profits lock in gains before market reversals.
#
# The calculations shown here apply to any trading framework, and can be integrated
# with the FiveTwenty SDK when implementing actual trades.

# ==============================================================================
# POSITION SETUP
# ==============================================================================

# Example scenario: Long EUR/USD position with 20-pip stop loss
#
# Position parameters:
#   - Entry Price: 1.1000 (price where we bought EUR/USD)
#   - Stop Loss: 1.0980 (20 pips below entry, limits downside risk)
#   - Direction: Long (we profit when price rises)
#   - Pip Value: 0.0001 (standard for most forex pairs)

entry_price = Decimal("1.1000")
stop_loss = Decimal("1.0980")
pip_value = Decimal("0.0001")

print("Take Profit Strategies for Long Position:")
print(f"Entry: {entry_price}")
print(f"Stop: {stop_loss}\n")

# ==============================================================================
# STRATEGY 1: FIXED PIP TARGET
# ==============================================================================
#
# Simple predetermined exit level based on average market movement
#
# Use case: Scalping or short-term trading with consistent profit targets
# Pros: Simple to calculate, easy to backtest, consistent approach
# Cons: Doesn't consider market structure or current volatility
#
# Formula: Target = Entry + (Target_Pips × Pip_Value)
#
# Example: For 30-pip target on long position
# Target = 1.1000 + (30 × 0.0001) = 1.1030

fixed_target = entry_price + (30 * pip_value)
print(f"Fixed 30-pip target: {fixed_target}")

# ==============================================================================
# STRATEGY 2: RISK-REWARD RATIO
# ==============================================================================
#
# Ensures mathematical edge by targeting profit that's a multiple of risk
#
# Use case: Systematic trading where you want positive expected value
# Pros: Ensures profitability even with <50% win rate, mathematically sound
# Cons: May not align with market structure, could miss larger moves
#
# Formula:
#   Risk = Entry - Stop_Loss
#   Reward = Risk × Ratio
#   Target = Entry + Reward
#
# Why this matters:
# - With 2:1 R/R, you only need 34% win rate to break even
# - With 2:1 R/R and 50% win rate, you have significant profit
#
# Calculation for 2:1 risk-reward:
#   Risk = 1.1000 - 1.0980 = 0.0020 (20 pips)
#   Reward = 0.0020 × 2 = 0.0040 (40 pips)
#   Target = 1.1000 + 0.0040 = 1.1040

risk = entry_price - stop_loss  # 20 pips (our maximum loss)
reward = risk * 2  # 40 pips (2:1 ratio = double the risk)
rr_target = entry_price + reward

# Calculate pips for display
risk_pips = risk / pip_value
reward_pips = reward / pip_value

print(f"2:1 R/R target: {rr_target} ({reward_pips:.0f} pips)")
print(f"  Risk: {risk_pips:.0f} pips | Reward: {reward_pips:.0f} pips")

# ==============================================================================
# STRATEGY 3: MULTIPLE TARGETS (SCALING OUT)
# ==============================================================================
#
# Scale out of position gradually to balance certainty and opportunity
#
# Use case: Trend trading where you want to capture both quick and extended moves
# Pros: Guarantees some profit while allowing for bigger wins, reduces stress
# Cons: More complex to manage, may exit too early on strong trends
#
# Common scaling approach: Close 1/3 of position at each target
# - Target 1: Conservative exit (locks in some profit quickly)
# - Target 2: Medium-term target (reasonable profit objective)
# - Target 3: Aggressive target (captures extended moves)
#
# Example for EUR/USD with initial position of 30,000 units:
# - At +15 pips: Close 10,000 units (lock in early profit)
# - At +30 pips: Close 10,000 units (take reasonable profit)
# - At +50 pips: Close 10,000 units (capture extended move)
#
# Benefit: Even if price only reaches target 1, you secured some profit
# If price reaches all targets, you maximize returns

target_1 = entry_price + (15 * pip_value)  # Close 1/3 at +15 pips (quick profit)
target_2 = entry_price + (30 * pip_value)  # Close 1/3 at +30 pips (1:1.5 R/R)
target_3 = entry_price + (50 * pip_value)  # Close 1/3 at +50 pips (2.5:1 R/R)

print(f"Scale-out targets: {target_1}, {target_2}, {target_3}")
print("  Strategy: Close 1/3 position at each target level")


# ==============================================================================
# REAL-WORLD SDK IMPLEMENTATION
# ==============================================================================
#
# Now let's see how to actually implement these take profit strategies on a live
# trade using the FiveTwenty SDK. This demonstrates the complete workflow from
# retrieving an open position to setting a take profit order based on risk-reward
# ratio calculations.


async def main() -> None:
    """Implement take profit strategies on an actual trade."""
    load_dotenv()

    async with AsyncClient() as client:
        # ======================================================================
        # STEP 1: RETRIEVE OPEN TRADE
        # ======================================================================
        #
        # SDK METHOD: client.trades.get_trades()
        #
        # Returns: TypedDict with structure:
        #   {
        #       "trades": list[Trade],        # List of Pydantic Trade models
        #       "lastTransactionID": str
        #   }
        #
        # We need an open trade to demonstrate take profit implementation

        response = await client.trades.get_trades(client.account_id)
        trades = response["trades"]

        if not trades:
            print("\nNo open trades found. Open a position first to try this example.")
            return

        trade = trades[0]
        print(f"\nWorking with trade: {trade.instrument}")
        print(f"Entry price: {trade.price}")
        print(f"Current units: {trade.current_units}")

        # ======================================================================
        # STEP 2: CALCULATE TAKE PROFIT USING RISK-REWARD RATIO
        # ======================================================================
        #
        # Use the 2:1 risk-reward ratio approach from Strategy 2 above
        # This ensures mathematical edge even with 50% win rate

        # Determine if this is a long or short position
        is_long = int(trade.current_units) > 0

        # Get current stop loss if one exists
        if trade.stop_loss_order and trade.stop_loss_order.price:
            current_stop = Decimal(trade.stop_loss_order.price)
        else:
            # If no stop loss exists, use a conservative 20-pip stop for calculation
            current_stop = (
                Decimal(trade.price) - (Decimal("20") * pip_value)
                if is_long
                else Decimal(trade.price) + (Decimal("20") * pip_value)
            )
            print("Note: No stop loss found, using 20-pip stop for calculation")

        entry = Decimal(trade.price)
        print("\nCalculating 2:1 R/R take profit:")
        print(f"  Entry: {entry}")
        print(f"  Stop:  {current_stop}")

        # Calculate risk and reward
        risk_amount = abs(entry - current_stop)
        reward_amount = risk_amount * 2

        # Calculate take profit price
        if is_long:
            calculated_tp = entry + reward_amount
        else:
            calculated_tp = entry - reward_amount

        risk_pips_calc = risk_amount / pip_value
        reward_pips_calc = reward_amount / pip_value

        print(f"  Risk:   {risk_pips_calc:.0f} pips")
        print(f"  Reward: {reward_pips_calc:.0f} pips (2:1 ratio)")
        print(f"  Target: {calculated_tp:.5f}")

        # ======================================================================
        # STEP 3: SET TAKE PROFIT ORDER ON THE TRADE
        # ======================================================================
        #
        # SDK METHOD: client.trades.put_trade_orders()
        #
        # Parameters:
        #   - account_id: Your OANDA account identifier
        #   - trade_specifier: Trade ID to attach the order to
        #   - take_profit: Serialized TakeProfitDetails dictionary
        #
        # The TakeProfitDetails Pydantic model validates our price and converts
        # it to the proper format for OANDA's API. We serialize it using
        # model_dump(by_alias=True, exclude_none=True) to convert Python field
        # names to API camelCase format and remove empty fields.

        take_profit_details = TakeProfitDetails(price=calculated_tp)

        try:
            await client.trades.put_trade_orders(
                account_id=client.account_id,
                trade_specifier=trade.id,
                take_profit=take_profit_details.model_dump(
                    by_alias=True, exclude_none=True
                ),
            )
            print(f"\n Take profit successfully set at {calculated_tp:.5f}")
            print(
                "  Your trade will automatically close when price reaches this level"
            )

        except FiveTwentyError as e:
            print(f"\nCould not set take profit: {e.message}")
            print("This may occur if:")
            print("  - The price is too close to current market price")
            print("  - Account has trading restrictions")


# ==============================================================================
# NOTE: SCALING OUT WITH MULTIPLE TARGETS
# ==============================================================================
#
# For Strategy 3 (multiple targets), you would:
#
# 1. Split your initial order into multiple smaller trades
#    Example: Instead of one 30,000 unit order, place three 10,000 unit orders
#
# 2. Set different take profit levels on each trade:
#    - Trade 1: TakeProfitDetails(price=target_1)  # Conservative +15 pips
#    - Trade 2: TakeProfitDetails(price=target_2)  # Medium +30 pips
#    - Trade 3: TakeProfitDetails(price=target_3)  # Aggressive +50 pips
#
# 3. As each target is hit, that portion closes automatically while
#    the remaining trades continue running
#
# This approach guarantees some profit even if price doesn't reach all targets,
# while still allowing you to capture extended moves.


if __name__ == "__main__":
    asyncio.run(main())
```

---


## Position Sizing and Risk Management

Position sizing is the mathematical foundation of risk management - it determines how much capital you risk on each trade relative to your account size. The cardinal rule of trading is to never risk more than you can afford to lose on a single trade. Most professional traders risk between 0.5% to 2% of their account on any individual position. This conservative approach ensures that even a string of losses won't devastate your account, giving you the staying power needed to remain in the game long enough for your edge to materialize.

Two primary position sizing methodologies dominate professional trading. Fixed risk sizing calculates position size based on your account balance, risk tolerance, and stop loss distance. If you have a $10,000 account and want to risk 1% ($100) on a trade with a 20 pip stop loss, the math determines your exact position size. Volatility-adjusted sizing goes further by dynamically modifying your position size based on current market conditions - reducing size during volatile periods and increasing during quiet markets. This adaptive approach helps maintain consistent risk exposure regardless of market conditions.

The following example implements both methodologies. You'll learn to calculate position size based on fixed risk percentage, understanding how stop loss distance affects the units you should trade. The volatility adjustment component shows how to scale positions up or down based on current versus average volatility, helping you maintain consistent risk profiles across varying market conditions:

```python
import asyncio
from decimal import Decimal

from dotenv import load_dotenv

from fivetwenty import AsyncClient
from fivetwenty.exceptions import FiveTwentyError  # noqa: F401 (used in commented example)
from fivetwenty.models import StopLossDetails  # noqa: F401 (used in commented example)

# ==============================================================================
# POSITION SIZING AND RISK MANAGEMENT
# ==============================================================================

# Position sizing is the mathematical foundation of risk management. It determines
# how much capital you risk on each trade relative to your account size. The
# cardinal rule: never risk more than you can afford to lose on a single trade.
#
# Professional traders typically risk 0.5% to 2% per trade. This conservative
# approach ensures that even a string of losses won't devastate your account.

# ==============================================================================
# STRATEGY 1: FIXED RISK SIZING
# ==============================================================================
#
# Calculate position size based on:
#   1. Account balance (how much capital you have)
#   2. Risk percentage (how much you're willing to lose)
#   3. Stop loss distance (how far away your stop is)
#
# Formula:
#   Risk Amount = Account Balance × (Risk Percent / 100)
#   Price Risk = |Entry Price - Stop Loss|
#   Pip Risk = Price Risk / 0.0001
#   Risk Per Pip = Risk Amount / Pip Risk
#   Position Size = Risk Per Pip × 10,000
#
# Example with $10,000 account, 1% risk, 20 pip stop:
#   Risk Amount = $10,000 × 0.01 = $100
#   Price Risk = |1.1000 - 1.0980| = 0.0020 (20 pips)
#   Pip Risk = 0.0020 / 0.0001 = 20 pips
#   Risk Per Pip = $100 / 20 = $5 per pip
#   Position Size = $5 × 10,000 = 50,000 units
#
# Explanation: With 50,000 units and a 20 pip stop loss, if stopped out,
# you lose exactly $100 (1% of your account)


def calculate_position_size(
    account_balance: Decimal,
    risk_percent: Decimal,
    entry_price: Decimal,
    stop_loss: Decimal,
) -> int:
    """
    Calculate position size based on fixed risk percentage.

    This is the most important calculation in trading. It ensures you never
    risk more than your predetermined amount, regardless of how far away
    your stop loss is.
    """
    # Calculate dollar amount you're willing to risk
    risk_amount = account_balance * (risk_percent / Decimal("100"))

    # Calculate price distance to stop loss
    price_risk = abs(entry_price - stop_loss)

    if price_risk <= 0:
        return 0

    # Convert to pip risk (for forex pairs with 4 decimal places)
    pip_value = Decimal("0.0001")
    pip_risk = price_risk / pip_value

    # Calculate how much you can risk per pip
    # For standard forex pairs: 1 pip = $1 per 10,000 units
    risk_per_pip = risk_amount / pip_risk

    # Convert to position size in units
    position_size = int(risk_per_pip * Decimal("10000"))

    return position_size


# Example calculation
account_balance = Decimal("10000")
risk_percent = Decimal("1.0")  # Risk 1% per trade
entry_price = Decimal("1.1000")
stop_loss = Decimal("1.0980")  # 20 pips away

position_size = calculate_position_size(
    account_balance, risk_percent, entry_price, stop_loss
)

print("Fixed Risk Position Sizing:")
print(f"Account Balance: ${account_balance}")
print(f"Risk Percentage: {risk_percent}%")
print(f"Risk Amount: ${account_balance * risk_percent / 100}")
print(f"Entry Price: {entry_price:.5f}")
print(f"Stop Loss: {stop_loss:.5f}")
print(f"Stop Distance: {abs(entry_price - stop_loss) / Decimal('0.0001'):.0f} pips")
print(f"Calculated Position Size: {position_size} units\n")

# ==============================================================================
# STRATEGY 2: VOLATILITY-ADJUSTED SIZING
# ==============================================================================
#
# Adjust position size based on current market volatility to maintain
# consistent risk across different market conditions.
#
# When volatility is HIGH: Reduce position size (price moves more)
# When volatility is LOW: Increase position size (price moves less)
#
# Formula:
#   Volatility Ratio = Average Volatility / Current Volatility
#   Adjusted Size = Base Position × Volatility Ratio
#
# Example with 5,000 base units:
#   Current volatility = 0.0015 (high)
#   Average volatility = 0.0012 (normal)
#   Ratio = 0.0012 / 0.0015 = 0.8
#   Adjusted = 5,000 × 0.8 = 4,000 units (reduced due to high volatility)
#
# We cap adjustments between 50% and 150% of base size to avoid extremes


def adjust_for_volatility(
    base_position: int, current_volatility: Decimal, average_volatility: Decimal
) -> int:
    """
    Adjust position size based on current market volatility.

    This helps maintain consistent risk when market conditions change.
    High volatility = smaller position, Low volatility = larger position
    """
    if current_volatility <= 0:
        return base_position

    # Calculate volatility ratio (inverse relationship)
    volatility_ratio = average_volatility / current_volatility

    # Apply ratio to base position
    adjusted_size = int(base_position * volatility_ratio)

    # Cap adjustments to reasonable range (50% to 150% of base)
    min_size = int(base_position * Decimal("0.5"))
    max_size = int(base_position * Decimal("1.5"))

    return max(min_size, min(adjusted_size, max_size))


# Example volatility adjustment
base_position = 5000
current_vol = Decimal("0.0015")  # Current volatility (higher than average)
average_vol = Decimal("0.0012")  # Average volatility

adjusted_size = adjust_for_volatility(base_position, current_vol, average_vol)

print("Volatility-Adjusted Position Sizing:")
print(f"Base Position: {base_position} units")
print(f"Current Volatility: {current_vol:.4f}")
print(f"Average Volatility: {average_vol:.4f}")
print(
    f"Volatility Ratio: {(average_vol / current_vol):.2f} ({'high' if current_vol > average_vol else 'low'} volatility)"
)
print(f"Adjusted Position: {adjusted_size} units")
print(f"Size Change: {((adjusted_size - base_position) / base_position * 100):.1f}%\n")


# ==============================================================================
# REAL-WORLD SDK IMPLEMENTATION
# ==============================================================================
#
# Now let's implement these position sizing calculations with the FiveTwenty SDK.
# This example demonstrates the complete workflow:
#   1. Get account balance from OANDA
#   2. Calculate position size based on risk parameters
#   3. Place a market order with calculated size and stop loss


async def main() -> None:
    """Demonstrate position sizing with live account data."""
    load_dotenv()

    async with AsyncClient() as client:
        # ======================================================================
        # STEP 1: GET ACCOUNT BALANCE
        # ======================================================================
        #
        # SDK METHOD: client.accounts.get_account_summary()
        #
        # Returns: TypedDict with structure:
        #   {
        #       "account": AccountSummary    # Pydantic model
        #   }
        #
        # AccountSummary contains balance, equity, margin info

        print("\n" + "=" * 70)
        print("REAL-WORLD POSITION SIZING WITH FIVETWENTY SDK")
        print("=" * 70 + "\n")

        response = await client.accounts.get_account_summary(client.account_id)
        account = response["account"]

        # Get account balance (use 'balance' not 'NAV' for conservative sizing)
        balance = Decimal(account.balance)

        print(f"Account Balance: ${balance:,.2f}")
        print(f"Account Currency: {account.currency}")

        # ======================================================================
        # STEP 2: CALCULATE POSITION SIZE
        # ======================================================================
        #
        # Define trade parameters and calculate appropriate position size

        # Trade parameters
        instrument = "EUR_USD"
        risk_percentage = Decimal("1.0")  # Risk 1% of account per trade
        planned_entry = Decimal("1.1000")  # Example entry price
        planned_stop = Decimal("1.0980")  # 20 pip stop loss

        print("\nTrade Setup:")
        print(f"  Instrument: {instrument}")
        print(f"  Risk: {risk_percentage}% of account")
        print(f"  Entry: {planned_entry:.5f}")
        print(f"  Stop:  {planned_stop:.5f}")
        print(
            f"  Stop Distance: {abs(planned_entry - planned_stop) / Decimal('0.0001'):.0f} pips"
        )

        # Calculate position size using our function
        calculated_units = calculate_position_size(
            balance, risk_percentage, planned_entry, planned_stop
        )

        risk_amount = balance * (risk_percentage / Decimal("100"))

        print("\nPosition Sizing Calculation:")
        print(f"  Max Risk Amount: ${risk_amount:.2f}")
        print(f"  Calculated Units: {calculated_units:,}")

        # ======================================================================
        # STEP 3: PLACE ORDER WITH CALCULATED SIZE (DEMONSTRATION)
        # ======================================================================
        #
        # SDK METHOD: client.orders.post_market_order()
        #
        # In a real scenario, you would place the order here. For this example,
        # we'll show the code but not execute it to avoid unintended trades.
        #
        # The key insight: Your position size is mathematically calculated to
        # ensure you never risk more than your predetermined percentage,
        # regardless of stop loss distance.

        print("\nOrder that would be placed:")
        print("  Type: Market Order")
        print(f"  Instrument: {instrument}")
        print(f"  Units: {calculated_units} (calculated for {risk_percentage}% risk)")
        print(f"  Stop Loss: {planned_stop:.5f}")

        # Example order placement (commented out for safety):
        #
        # stop_loss_details = StopLossDetails(price=planned_stop)
        #
        # try:
        #     order_response = await client.orders.post_market_order(
        #         account_id=client.account_id,
        #         instrument=instrument,
        #         units=calculated_units,  # Our calculated size!
        #         stop_loss=stop_loss_details.model_dump(
        #             by_alias=True, exclude_none=True
        #         ),
        #     )
        #
        #     print("\n Order placed successfully")
        #     print(f"  Order ID: {order_response['orderFillTransaction']['id']}")
        #
        # except FiveTwentyError as e:
        #     print(f"\nCould not place order: {e.message}")

        print(
            "\n Key Insight: By calculating position size this way, you ensure that"
        )
        print(
            "   if your stop loss is hit, you lose exactly $"
            + f"{risk_amount:.2f} ({risk_percentage}% of account),"
        )
        print("   regardless of how far away the stop loss is placed.")


# ==============================================================================
# POSITION SIZING BEST PRACTICES
# ==============================================================================
#
# 1. NEVER risk more than 2% per trade (1% is better)
#    - Protects you from catastrophic losses
#    - Allows recovery from losing streaks
#
# 2. ALWAYS calculate position size BEFORE entering
#    - Never enter a trade without knowing your risk
#    - Use stop loss distance as a primary factor
#
# 3. Adjust for volatility when appropriate
#    - Reduce size in choppy markets
#    - Can increase slightly in calm markets
#
# 4. Consider correlation risk
#    - Don't risk 1% on EUR/USD and 1% on EUR/GBP simultaneously
#    - Correlated positions multiply your actual risk
#
# 5. Account for spread and slippage
#    - Real stop loss may be slightly worse than planned
#    - Add small buffer to calculations in volatile markets


if __name__ == "__main__":
    asyncio.run(main())
```

---


## Using FiveTwenty for Position Management

Throughout this tutorial, you've seen how to use FiveTwenty SDK methods for complete position management:

**Position Monitoring:**
- `client.trades.get_trades()` - Retrieve all open positions with current P&L
- Access trade details via Pydantic models (`.price`, `.current_units`, `.unrealized_pl`)

**Setting Stop Loss and Take Profit:**
- `client.trades.put_trade_orders()` - Attach or modify protective orders on existing trades
- Use `StopLossDetails` and `TakeProfitDetails` Pydantic models for type-safe order creation
- Serialize with `.model_dump(by_alias=True, exclude_none=True)` for API compatibility

**Account Information:**
- `client.accounts.get_account_summary()` - Get balance, equity, and margin for position sizing calculations

**Order Placement:**
- `client.orders.post_market_order()` - Open new positions with calculated size and protective orders

All examples demonstrate proper error handling with `FiveTwentyError`, type safety with `Decimal` for financial calculations, and async/await patterns with `AsyncClient` context managers.

---

## What You've Learned

-  **Position Monitoring with `client.trades.get_trades()`** - Retrieve and analyze open positions, calculate unrealized P&L, and determine appropriate exit levels using live trade data

-  **Stop Loss Implementation with `client.trades.put_trade_orders()`** - Set protective orders using fixed pip targets, percentage-based stops, and ATR-based dynamic stops with proper error handling for OANDA restrictions

-  **Take Profit Strategies with SDK Integration** - Calculate risk-reward ratios, implement scaling out strategies, and attach take profit orders to maximize gains while protecting capital

-  **Position Sizing with `client.accounts.get_account_summary()`** - Calculate mathematically sound position sizes based on account balance, risk percentage, and stop loss distance to maintain consistent risk exposure

-  **Type-Safe SDK Patterns** - Use Pydantic models for requests (`StopLossDetails`, `TakeProfitDetails`), handle TypedDict responses correctly, serialize models with `.model_dump(by_alias=True, exclude_none=True)`, and use `Decimal` for all financial calculations

!!! success "Position Management Mastery Complete!"
    Excellent! You now have production-ready skills for managing trading positions with FiveTwenty SDK. You understand how to balance risk and reward programmatically while leveraging proper type safety and error handling. Next, you'll learn to build complete trading strategies that combine these position management techniques.

---

## Next Steps

Continue to [Strategy Building](strategy-building.md) to learn how to combine your skills into systematic trading approaches.

---

## Related Resources

- [Risk Management Fundamentals](../risk-management.md) - Comprehensive risk control
- [Advanced Stop-Loss Strategies](../../guides/practical-solutions/implement-stop-loss-strategies.md) - Detailed stop loss techniques
- [Trading Models](../../api-reference/models/trading-models.md) - Technical API documentation
