# Order Strategies & Combinations

Learn to combine FiveTwenty's order types effectively for common trading scenarios.

## Learning Objectives

By the end of this tutorial, you will:

- Scale into and out of positions using multiple order layers
- Implement advanced stop management techniques
- Build conditional order logic and position reversal strategies
- Combine multiple order types for complete trading strategies

## Order Coordination Patterns

### If-Then Order Logic

Simulate conditional orders with monitoring. OANDA doesn't natively support "if-then" order logic (e.g., "IF price crosses X THEN place order"), so you implement it by monitoring prices and placing orders when conditions are met.

The following example demonstrates monitoring market price for a breakout condition, automatically executing an order when the condition triggers, and including protective stop loss:

<!-- filepath: example_conditional_order_logic.py -->
```python
import asyncio
from decimal import Decimal

from dotenv import load_dotenv

from fivetwenty import AsyncClient
from fivetwenty.models import InstrumentName, StopLossDetails

load_dotenv()

# ==============================================================================
# CONDITIONAL ORDER LOGIC (IF-THEN MONITORING)
# ==============================================================================

# This example demonstrates conditional order execution using price monitoring:
#
# KEY CONCEPTS:
# 1. Price Monitoring - Continuously check market price against target level
# 2. Breakout Detection - Identify when price crosses threshold
# 3. Conditional Execution - Place order only when condition is satisfied
# 4. Automated Response - Immediate execution upon condition trigger
#
# HOW IT WORKS:
# Monitor real-time prices in a loop. When price reaches or exceeds target breakout
# level, automatically place market order with protective stop loss. This simulates
# "if-then" conditional order logic: "IF price >= target THEN execute order".
# Useful for breakout strategies where you want to enter only when price confirms
# directional move.
#
# This code is fully executable and demonstrates conditional logic with OANDA.


async def main() -> None:
    """Demonstrate conditional order logic with price monitoring."""

    print("=" * 70)
    print("CONDITIONAL ORDER LOGIC (IF-THEN MONITORING)")
    print("=" * 70)

    # ==============================================================================
    # CONNECT TO OANDA
    # ==============================================================================

    # AsyncClient automatically reads FIVETWENTY_OANDA_* environment variables
    # Context manager ensures proper cleanup of HTTP connections
    async with AsyncClient() as client:
        instrument = InstrumentName("EUR_USD")

        # ==============================================================================
        # STEP 1: DEFINE BREAKOUT CONDITION
        # ==============================================================================

        print(f"\nConfiguring breakout monitoring for {instrument}...")

        # Get current price to set realistic target
        pricing = await client.pricing.get_pricing(
            account_id=client.account_id,
            instruments=[instrument],
        )
        current_price = pricing["prices"][0].asks[0].price

        # Set breakout target slightly above current price for demo
        target_price = current_price + Decimal("0.0010")  # 10 pips above current

        print(f"  Current Price: {current_price:.5f}")
        print(f"  Breakout Target: {target_price:.5f} (10 pips above)")
        print(f"  Stop Loss Level: {target_price - Decimal('0.0050'):.5f} (50 pips below target)")

        # ==============================================================================
        # STEP 2: MONITOR PRICE FOR BREAKOUT
        # ==============================================================================

        print("\nStarting conditional monitoring...")
        print(f"  Condition: IF price >= {target_price:.5f} THEN execute breakout order")
        print("  Checking every 5 seconds (max 12 checks = 60 seconds)...\n")

        max_checks = 12  # Limit monitoring duration for demo
        check_count = 0

        while check_count < max_checks:
            check_count += 1

            # Fetch current market price
            pricing = await client.pricing.get_pricing(
                account_id=client.account_id,
                instruments=[instrument],
            )
            current_price = pricing["prices"][0].asks[0].price

            print(f"  Check {check_count}/{max_checks}: Price = {current_price:.5f} (target: {target_price:.5f})")

            # ==============================================================================
            # STEP 3: EVALUATE BREAKOUT CONDITION
            # ==============================================================================

            if current_price >= target_price:
                # Condition satisfied - execute breakout order
                print(f"\n{'='*70}")
                print(f"BREAKOUT DETECTED! Price hit {current_price:.5f}")
                print(f"{'='*70}")

                stop_loss_price = target_price - Decimal("0.0050")

                print("\nExecuting breakout order...")
                print("  Entry: Market order for 10,000 units long")
                print(f"  Stop Loss: {stop_loss_price:.5f}")

                # Place market order
                market_order = await client.orders.post_market_order(
                    account_id=client.account_id,
                    instrument=instrument,
                    units=10000,
                )

                # Check if order filled
                if market_order.order_fill_transaction is None:
                    print("\nOrder was not filled - market is likely closed")
                    print("Forex market hours: Sunday 5 PM ET - Friday 5 PM ET")
                    print("\nThis example demonstrates conditional monitoring logic")
                    return

                # Extract trade details
                assert market_order.order_fill_transaction.trade_opened is not None
                trade_id = market_order.order_fill_transaction.trade_opened.trade_id
                entry_price = market_order.order_fill_transaction.price
                assert entry_price is not None

                print("\n  Breakout Order Filled:")
                print(f"    Trade ID: {trade_id}")
                print(f"    Entry Price: {entry_price:.5f}")
                print("    Size: 10,000 units long")

                # Place stop loss
                await client.trades.put_trade_orders(
                    account_id=client.account_id,
                    trade_specifier=trade_id,
                    stop_loss=StopLossDetails(price=stop_loss_price),
                )

                print(f"    Stop Loss: {stop_loss_price:.5f} (protecting breakout)")

                # ==============================================================================
                # STEP 4: ANALYZE BREAKOUT EXECUTION
                # ==============================================================================

                print(f"\n{'='*70}")
                print("BREAKOUT EXECUTION ANALYSIS")
                print(f"{'='*70}")

                target_distance = (entry_price - (target_price - Decimal("0.0010"))) * 10000
                risk_distance = (entry_price - stop_loss_price) * 10000

                print("\n  Trigger Analysis:")
                print(f"    Initial Price: {current_price - Decimal('0.0010'):.5f}")
                print(f"    Breakout Target: {target_price:.5f}")
                print(f"    Entry Price: {entry_price:.5f}")
                print(f"    Price Movement: {target_distance:+.1f} pips to trigger")

                print("\n  Risk Management:")
                print(f"    Stop Loss: {stop_loss_price:.5f}")
                print(f"    Risk Distance: {risk_distance:.1f} pips")
                print(f"    Risk Amount: ${risk_distance * 10000 / 10000:.2f}")

                print("\n  Conditional Logic Success:")
                print("    ✓ Price monitoring active")
                print("    ✓ Breakout condition detected")
                print("    ✓ Order executed automatically")
                print("    ✓ Stop loss protection active")

                return

            # Condition not yet met - wait and check again
            await asyncio.sleep(5)

        # ==============================================================================
        # STEP 5: HANDLE TIMEOUT (CONDITION NOT MET)
        # ==============================================================================

        print(f"\n{'='*70}")
        print("MONITORING TIMEOUT")
        print(f"{'='*70}")

        print("\n  Breakout condition was not met within monitoring period")
        print(f"  Final Price: {current_price:.5f}")
        print(f"  Target Price: {target_price:.5f}")
        print(f"  Distance to Target: {(target_price - current_price) * 10000:.1f} pips")

        print("\n  Conditional Logic Demonstration:")
        print(f"    • Monitored price for {check_count} intervals")
        print("    • Condition was never satisfied")
        print("    • No order was placed (correct behavior)")
        print("    • In production, monitoring would continue indefinitely")

        # ==============================================================================
        # PRODUCTION ENHANCEMENTS
        # ==============================================================================

        print("\n" + "=" * 70)
        print("PRODUCTION ENHANCEMENTS TO CONSIDER")
        print("=" * 70)
        print("\nTo make this conditional logic production-ready, add:")
        print("  • Persistent monitoring with database state tracking")
        print("  • Multiple concurrent condition monitoring")
        print("  • Condition timeout and expiration handling")
        print("  • Price streaming instead of polling for efficiency")
        print("  • Complex conditions (price AND volume, multiple timeframes)")
        print("  • Condition modification and cancellation support")
        print("  • Notification system when conditions trigger")
        print("  • Retry logic for failed order execution")


if __name__ == "__main__":
    # Run the conditional order logic demonstration
    asyncio.run(main())
```

### Position Reversal Strategy

Close existing position and open opposite position in a single transaction. This is useful when market conditions change and you want to quickly switch direction without the latency of closing then re-entering separately.

The following example demonstrates creating an initial position (if needed), calculating the reversal order size, executing the reversal in one transaction, and analyzing the results:

<!-- filepath: example_position_reversal.py -->
```python
import asyncio
from decimal import Decimal

from dotenv import load_dotenv

from fivetwenty import AsyncClient
from fivetwenty.models import InstrumentName, StopLossDetails, TradeStateFilter

load_dotenv()

# ==============================================================================
# POSITION REVERSAL STRATEGY
# ==============================================================================

# This example demonstrates position reversal for trend change scenarios:
#
# KEY CONCEPTS:
# 1. Position Analysis - Check existing positions for reversal candidates
# 2. Reversal Calculation - Determine size needed to close and reverse
# 3. Single Transaction - Close existing and open opposite in one order
# 4. Direction Change - Switch from long to short (or vice versa)
#
# HOW IT WORKS:
# Check current positions for EUR_USD. If you find a long position, calculate
# the order size needed to close it AND open an equal short position (2x the
# current size). Place single market order with negative units to accomplish
# both in one transaction. This is useful when market conditions change and
# you want to quickly switch direction without closing then re-entering.
#
# This code is fully executable and demonstrates position reversal with OANDA.


async def main() -> None:
    """Demonstrate position reversal strategy."""

    print("=" * 70)
    print("POSITION REVERSAL STRATEGY")
    print("=" * 70)

    # ==============================================================================
    # CONNECT TO OANDA
    # ==============================================================================

    # AsyncClient automatically reads FIVETWENTY_OANDA_* environment variables
    # Context manager ensures proper cleanup of HTTP connections
    async with AsyncClient() as client:
        instrument = InstrumentName("EUR_USD")

        # ==============================================================================
        # STEP 1: CREATE INITIAL POSITION FOR REVERSAL DEMO
        # ==============================================================================

        print(f"\nSetting up initial {instrument} position for reversal demonstration...")

        # First, check if we already have a position
        positions = await client.positions.get_positions(account_id=client.account_id)

        existing_long_units = 0
        for position in positions["positions"]:
            if position.instrument == instrument:
                existing_long_units = int(position.long.units)
                break

        if existing_long_units == 0:
            # No existing position - create one for demo
            print("  No existing position found - creating demo position...")

            market_order = await client.orders.post_market_order(
                account_id=client.account_id,
                instrument=instrument,
                units=10000,  # Create 10k long position
            )

            if market_order.order_fill_transaction is None:
                print("\nOrder was not filled - market is likely closed")
                print("Forex market hours: Sunday 5 PM ET - Friday 5 PM ET")
                print("\nThis example demonstrates position reversal logic")
                return

            entry_price = market_order.order_fill_transaction.price
            assert entry_price is not None

            # Check if trade was opened or if it closed/reduced an opposite position
            if market_order.order_fill_transaction.trade_opened is not None:
                existing_long_units = 10000
                print("  Created Position:")
                print(f"    Instrument: {instrument}")
                print("    Direction: LONG")
                print(f"    Size: {existing_long_units:,} units")
                print(f"    Entry: {entry_price:.5f}")
            else:
                # Order closed/reduced opposite position - re-check positions
                print("  Order closed/reduced existing opposite position")
                positions = await client.positions.get_positions(account_id=client.account_id)
                for position in positions["positions"]:
                    if position.instrument == instrument:
                        existing_long_units = int(position.long.units)
                        break

                if existing_long_units == 0:
                    print("  No long position after order - exiting demo")
                    return

                print(f"  Current long position: {existing_long_units:,} units")
        else:
            print("  Found Existing Position:")
            print(f"    Instrument: {instrument}")
            print("    Direction: LONG")
            print(f"    Size: {existing_long_units:,} units")

        # ==============================================================================
        # STEP 2: CALCULATE REVERSAL ORDER SIZE
        # ==============================================================================

        print(f"\n{'='*70}")
        print("POSITION REVERSAL CALCULATION")
        print(f"{'='*70}")

        # To reverse: need to close existing AND open opposite
        # If long 10,000 units, need to sell 20,000 to end up short 10,000
        reversal_units = existing_long_units * 2

        print(f"\n  Current Position: {existing_long_units:,} units LONG")
        print(f"  Reversal Order: {reversal_units:,} units SHORT (negative)")
        print(f"  Net Result: {existing_long_units:,} units SHORT")

        print("\n  Calculation:")
        print(f"    Close Long: -{existing_long_units:,} units")
        print(f"    Open Short: -{existing_long_units:,} units")
        print(f"    Total Order: -{reversal_units:,} units")

        # ==============================================================================
        # STEP 3: EXECUTE POSITION REVERSAL
        # ==============================================================================

        print(f"\n{'='*70}")
        print("EXECUTING POSITION REVERSAL")
        print(f"{'='*70}")

        print("\n  Placing reversal order...")

        # Get current price for stop loss calculation
        pricing = await client.pricing.get_pricing(
            account_id=client.account_id,
            instruments=[instrument],
        )
        current_price = pricing["prices"][0].bids[0].price  # Use bid for short position

        # Calculate stop loss above current price (short position protection)
        stop_loss_price = current_price + Decimal("0.0050")  # 50 pips above entry

        # Execute reversal with single market order
        reversal_order = await client.orders.post_market_order(
            account_id=client.account_id,
            instrument=instrument,
            units=-reversal_units,  # Negative for short
        )

        if reversal_order.order_fill_transaction is None:
            print("\nReversal order was not filled - market may be closed")
            return

        # Extract reversal details
        reversal_price = reversal_order.order_fill_transaction.price
        assert reversal_price is not None

        print("\n  Reversal Executed:")
        print(f"    Order ID: {reversal_order.order_fill_transaction.id}")
        print(f"    Reversal Price: {reversal_price:.5f}")
        print(f"    Order Size: {reversal_units:,} units SHORT")

        # Get new position to confirm reversal
        new_positions = await client.positions.get_positions(
            account_id=client.account_id
        )

        new_short_units = 0
        for position in new_positions["positions"]:
            if position.instrument == instrument:
                new_short_units = int(position.short.units)
                break

        # Place stop loss on new short position
        if new_short_units != 0:
            # Find the short trade
            trades = await client.trades.get_trades(
                account_id=client.account_id,
                state=TradeStateFilter.OPEN,
                instrument=instrument,
            )

            for trade in trades["trades"]:
                if int(trade.current_units) < 0:  # Short trade
                    await client.trades.put_trade_orders(
                        account_id=client.account_id,
                        trade_specifier=trade.id,
                        stop_loss=StopLossDetails(price=stop_loss_price),
                    )
                    print(f"    Stop Loss: {stop_loss_price:.5f} (protecting short)")
                    break

        # ==============================================================================
        # STEP 4: VERIFY REVERSAL RESULT
        # ==============================================================================

        print(f"\n{'='*70}")
        print("REVERSAL RESULT VERIFICATION")
        print(f"{'='*70}")

        print("\n  Before Reversal:")
        print(f"    Position: {existing_long_units:,} units LONG")

        print("\n  After Reversal:")
        print(f"    Position: {abs(new_short_units):,} units SHORT")

        print("\n  Reversal Success:")
        print("    ✓ Closed long position")
        print("    ✓ Opened short position")
        print("    ✓ Single transaction execution")
        print("    ✓ Stop loss protection active")

        # ==============================================================================
        # STEP 5: REVERSAL USE CASES
        # ==============================================================================

        print(f"\n{'='*70}")
        print("POSITION REVERSAL USE CASES")
        print(f"{'='*70}")

        print("\n  When to use position reversal:")
        print("    • Trend reversal detected (e.g., support becomes resistance)")
        print("    • News event changes market bias")
        print("    • Technical breakout in opposite direction")
        print("    • Stop loss hit and you want to trade the reversal")
        print("    • Mean reversion strategy flips direction")

        print("\n  Advantages:")
        print("    • Single transaction (lower latency)")
        print("    • No gap between closing and opening")
        print("    • Reduced slippage vs separate orders")
        print("    • Immediate directional exposure")

        print("\n  Considerations:")
        print("    • Doubles your risk if market reverses again")
        print("    • No opportunity to reassess between close and open")
        print("    • Should only use when conviction is high")
        print("    • Always include protective stop on new position")

        # ==============================================================================
        # PRODUCTION ENHANCEMENTS
        # ==============================================================================

        print("\n" + "=" * 70)
        print("PRODUCTION ENHANCEMENTS TO CONSIDER")
        print("=" * 70)
        print("\nTo make this reversal strategy production-ready, add:")
        print("  • Confirmation signals before reversing (multiple indicators)")
        print("  • Position size adjustment based on volatility")
        print("  • Partial reversal option (reverse 50% instead of 100%)")
        print("  • Cooldown period to prevent excessive reversals")
        print("  • Track reversal performance vs close-and-reenter")
        print("  • Maximum reversal frequency limits")
        print("  • Pre-reversal position P&L analysis")
        print("  • Reversal notification and logging")


if __name__ == "__main__":
    # Run the position reversal demonstration
    asyncio.run(main())
```

## Complete Strategy Example

Combining FiveTwenty's order types into a complete trading strategy. This example demonstrates a comprehensive scaling strategy that places multiple entry orders at different price levels AND multiple exit orders at profit targets - all in one coordinated approach.

The following example shows placing progressive entry orders (larger sizes at better prices), calculating weighted average entry, placing systematic profit-taking exits, and analyzing potential outcomes:

<!-- filepath: example_complete_scaling_strategy.py -->
```python
import asyncio
from decimal import Decimal

from dotenv import load_dotenv

from fivetwenty import AsyncClient
from fivetwenty.models import InstrumentName

load_dotenv()

# ==============================================================================
# COMPLETE SCALING STRATEGY
# ==============================================================================

# This example demonstrates a comprehensive scaling strategy with systematic entry
# and exit:
#
# KEY CONCEPTS:
# 1. Systematic Entry - Multiple limit orders at different price levels
# 2. Progressive Sizing - Larger positions at better prices
# 3. Systematic Exit - Multiple profit targets for staged exits
# 4. Risk Management - Consistent stop loss protection across entries
#
# HOW IT WORKS:
# Place limit orders for scaling into position at progressively better prices,
# with larger sizes at lower levels. Simultaneously place limit orders for scaling
# out at profit targets. Calculate weighted average entry and potential profit at
# each exit level. This demonstrates complete order combination strategy from entry
# through exit.
#
# This code is fully executable and demonstrates complete order strategy with OANDA.


async def main() -> None:
    """Demonstrate complete scaling strategy with entry and exit orders."""

    print("=" * 70)
    print("COMPLETE SCALING STRATEGY")
    print("=" * 70)

    # ==============================================================================
    # CONNECT TO OANDA
    # ==============================================================================

    # AsyncClient automatically reads FIVETWENTY_OANDA_* environment variables
    # Context manager ensures proper cleanup of HTTP connections
    async with AsyncClient() as client:
        instrument = InstrumentName("EUR_USD")

        # ==============================================================================
        # STEP 1: GET CURRENT MARKET PRICE
        # ==============================================================================

        print(f"\nFetching current {instrument} price...")

        pricing = await client.pricing.get_pricing(
            account_id=client.account_id,
            instruments=[instrument],
        )
        current_price = pricing["prices"][0].asks[0].price

        print(f"  Current Market Price: {current_price:.5f}")

        # ==============================================================================
        # STEP 2: DEFINE SCALING PARAMETERS
        # ==============================================================================

        print("\nConfiguring comprehensive scaling strategy...")

        base_size = 5000  # Base unit size for scaling calculations

        # Entry levels below current price (descending)
        entry_prices = [
            current_price - Decimal("0.0025"),  # 25 pips below
            current_price - Decimal("0.0050"),  # 50 pips below
            current_price - Decimal("0.0075"),  # 75 pips below
        ]

        # Exit levels above current price (ascending)
        exit_prices = [
            current_price + Decimal("0.0075"),  # 75 pips above
            current_price + Decimal("0.0100"),  # 100 pips above
            current_price + Decimal("0.0125"),  # 125 pips above
        ]

        # Stop loss below all entries
        stop_loss_price = current_price - Decimal("0.0100")  # 100 pips below

        scaling_orders = []  # Track all orders

        # ==============================================================================
        # STEP 3: PLACE SCALING ENTRY ORDERS
        # ==============================================================================

        print("\n  SCALING INTO POSITION:")

        for i, price in enumerate(entry_prices):
            # Calculate progressive position sizing - larger at better prices
            position_size = base_size * (i + 1)  # 5k, 10k, 15k

            # Place limit order with stop loss protection
            order = await client.orders.post_limit_order(
                account_id=client.account_id,
                instrument=instrument,
                units=position_size,
                price=price,
            )

            scaling_orders.append(order)
            pips_below = (current_price - price) * 10000

            print(f"    Entry {i+1}: {position_size:,} units @ {price:.5f} ({pips_below:.0f} pips below)")

        # Calculate average entry if all fill
        total_units = sum(base_size * (i + 1) for i in range(len(entry_prices)))
        weighted_sum = sum(
            ((entry_prices[i] * base_size * (i + 1))
            for i in range(len(entry_prices))),
            Decimal("0")
        )
        average_entry = weighted_sum / Decimal(total_units)

        print(f"\n    Total Position (if all fill): {total_units:,} units")
        print(f"    Weighted Average Entry: {average_entry:.5f}")
        print(f"    Stop Loss: {stop_loss_price:.5f}")

        # ==============================================================================
        # STEP 4: PLACE SCALING EXIT ORDERS
        # ==============================================================================

        print("\n  SCALING OUT OF POSITION:")

        for i, price in enumerate(exit_prices):
            # Equal exit sizes for balanced profit taking
            order = await client.orders.post_limit_order(
                account_id=client.account_id,
                instrument=instrument,
                units=-base_size,  # Negative to close position
                price=price,
            )

            scaling_orders.append(order)
            pips_profit = (price - average_entry) * 10000

            print(f"    Exit {i+1}: {base_size:,} units @ {price:.5f} ({pips_profit:.0f} pips profit)")

        # ==============================================================================
        # STEP 5: STRATEGY SUMMARY
        # ==============================================================================

        print(f"\n{'='*70}")
        print("STRATEGY SUMMARY")
        print(f"{'='*70}")

        print("\n  Entry Configuration:")
        print(f"    Levels: {len(entry_prices)} (progressive sizing)")
        print(f"    Price Range: {entry_prices[0]:.5f} to {entry_prices[-1]:.5f}")
        print(f"    Total Size: {total_units:,} units")
        print(f"    Average Entry: {average_entry:.5f}")

        print("\n  Exit Configuration:")
        print(f"    Levels: {len(exit_prices)} (equal sizing)")
        print(f"    Price Range: {exit_prices[0]:.5f} to {exit_prices[-1]:.5f}")
        print(f"    Exit Size per Level: {base_size:,} units")

        print("\n  Risk Management:")
        print(f"    Stop Loss: {stop_loss_price:.5f}")
        risk_pips = (average_entry - stop_loss_price) * 10000
        print(f"    Risk per Unit: {risk_pips:.1f} pips")
        print(f"    Total Risk (if all entries fill): ${risk_pips * total_units / 10000:.2f}")

        print(f"\n  Total Orders Placed: {len(scaling_orders)}")
        print(f"    Entry Orders: {len(entry_prices)}")
        print(f"    Exit Orders: {len(exit_prices)}")

        # ==============================================================================
        # STEP 6: EXECUTION SCENARIOS
        # ==============================================================================

        print(f"\n{'='*70}")
        print("EXECUTION SCENARIOS")
        print(f"{'='*70}")

        print("\n  Scenario 1: All Entries Fill, First Exit Hits")
        first_exit_profit = (exit_prices[0] - average_entry) * base_size
        print(f"    Exit at: {exit_prices[0]:.5f}")
        print(f"    Profit Realized: ${first_exit_profit:.2f}")
        print(f"    Remaining Position: {total_units - base_size:,} units")

        print("\n  Scenario 2: All Entries Fill, All Exits Hit")
        total_profit = sum(
            (((exit_price - average_entry) * base_size)
            for exit_price in exit_prices),
            Decimal("0")
        )
        print(f"    Total Profit: ${total_profit:.2f}")
        average_exit = sum(exit_prices, Decimal("0")) / Decimal(len(exit_prices))
        print(f"    Average Exit: {average_exit:.5f}")
        avg_profit_pips = (average_exit - average_entry) * 10000
        print(f"    Average Profit: {avg_profit_pips:.1f} pips per unit")

        print("\n  Scenario 3: Partial Fill (Only First Entry)")
        partial_entry_profit = (exit_prices[0] - entry_prices[0]) * base_size
        print(f"    Entry: {base_size:,} units @ {entry_prices[0]:.5f}")
        print(f"    Exit: {base_size:,} units @ {exit_prices[0]:.5f}")
        print(f"    Profit: ${partial_entry_profit:.2f}")

        # ==============================================================================
        # PRODUCTION ENHANCEMENTS
        # ==============================================================================

        print("\n" + "=" * 70)
        print("PRODUCTION ENHANCEMENTS TO CONSIDER")
        print("=" * 70)
        print("\nTo make this strategy production-ready, add:")
        print("  • Monitor fills in real-time and adjust remaining orders")
        print("  • Move stop loss to breakeven after first profit target hits")
        print("  • Cancel unfilled entry orders after significant market move")
        print("  • Adjust level spacing based on current volatility (ATR)")
        print("  • Implement time-based expiration for unfilled orders")
        print("  • Track fill rate and optimize level placement over time")
        print("  • Add partial position stop loss management")
        print("  • Consider market session characteristics for level placement")


if __name__ == "__main__":
    # Run the complete scaling strategy demonstration
    asyncio.run(main())
```

## Order Performance Analytics

You can't optimize what you don't measure. Every order placement strategy has execution characteristics - how much slippage occurs, how quickly orders fill, what percentage of limit orders actually execute. Without tracking these metrics, you're trading blind, unable to distinguish efficient strategies from costly ones. Performance analytics transform order execution from guesswork into data-driven optimization.

The core metric is slippage - the difference between your requested price and actual fill price. Market orders typically show slippage equal to the bid-ask spread plus any market impact. Limit orders may show negative slippage (price improvement) if filled at better prices than requested. By tracking slippage across different order types, position sizes, and market conditions, you identify which approaches minimize execution costs.

The following example demonstrates placing orders with different strategies, tracking execution details including slippage, analyzing performance by strategy type, and calculating aggregate execution quality metrics:

<!-- filepath: example_order_performance_analytics.py -->
```python
import asyncio
from decimal import Decimal

from dotenv import load_dotenv

from fivetwenty import AsyncClient
from fivetwenty.models import InstrumentName

load_dotenv()

# ==============================================================================
# ORDER PERFORMANCE ANALYTICS SYSTEM
# ==============================================================================

# This example demonstrates tracking and analyzing order execution performance:
#
# KEY CONCEPTS:
# 1. Order Tracking - Record execution details for all placed orders
# 2. Slippage Analysis - Measure difference between requested and filled prices
# 3. Strategy Performance - Compare execution quality across different strategies
# 4. Execution Statistics - Calculate aggregate metrics like avg/max/min slippage
#
# HOW IT WORKS:
# Place multiple orders with different strategy tags. Track execution details including
# requested price, fill price, and calculate slippage. Aggregate performance metrics
# by strategy type to identify which order strategies execute most efficiently. This
# data reveals optimal order placement approaches and helps optimize execution quality.
#
# This code is fully executable and demonstrates performance tracking with OANDA.


async def main() -> None:
    """Demonstrate order performance tracking and analysis."""

    print("=" * 70)
    print("ORDER PERFORMANCE ANALYTICS SYSTEM")
    print("=" * 70)

    # ==============================================================================
    # CONNECT TO OANDA
    # ==============================================================================

    # AsyncClient automatically reads FIVETWENTY_OANDA_* environment variables
    # Context manager ensures proper cleanup of HTTP connections
    async with AsyncClient() as client:
        instrument = InstrumentName("EUR_USD")

        # Storage for order performance tracking
        order_history: list[dict[str, str | Decimal | int]] = []

        # ==============================================================================
        # STEP 1: PLACE ORDERS WITH DIFFERENT STRATEGIES
        # ==============================================================================

        print("\nPlacing orders with different strategy approaches...")

        # Fetch current price to calculate limit order levels
        pricing = await client.pricing.get_pricing(
            account_id=client.account_id,
            instruments=[instrument],
        )
        current_price = pricing["prices"][0].asks[0].price

        print(f"  Current Market Price: {current_price:.5f}")

        # Strategy 1: Market Orders (immediate execution)
        print("\nStrategy 1: MARKET ORDER")
        print("  Approach: Immediate execution at current market price")

        market_order = await client.orders.post_market_order(
            account_id=client.account_id,
            instrument=instrument,
            units=5000,
        )

        if market_order.order_fill_transaction is not None:
            fill_price_market = market_order.order_fill_transaction.price
            assert fill_price_market is not None

            # Market orders fill at current market, so slippage is bid-ask spread
            slippage_market = fill_price_market - current_price

            order_history.append({
                "strategy": "MARKET",
                "order_id": str(market_order.order_fill_transaction.id),
                "requested_price": current_price,
                "fill_price": fill_price_market,
                "slippage": slippage_market,
                "units": 5000,
            })

            print(f"  Order Filled: {market_order.order_fill_transaction.id}")
            print(f"  Requested: ~{current_price:.5f}")
            print(f"  Filled: {fill_price_market:.5f}")
            print(f"  Slippage: {slippage_market * 10000:.2f} pips")

        # Strategy 2: Limit Orders (patient entry)
        print("\nStrategy 2: LIMIT ORDER (Patient Entry)")
        print("  Approach: Wait for better price below market")

        limit_price = current_price - Decimal("0.0010")  # 10 pips below market

        limit_order = await client.orders.post_limit_order(
            account_id=client.account_id,
            instrument=instrument,
            units=5000,
            price=limit_price,
        )

        assert limit_order.order_create_transaction is not None
        limit_order_id = limit_order.order_create_transaction["id"]

        print(f"  Order Placed: {limit_order_id}")
        print(f"  Limit Price: {limit_price:.5f} (10 pips below market)")
        print("  Status: Waiting for price to reach limit level...")

        # In real scenario, would monitor for fill
        # For demo, we'll cancel and note unfilled
        print("  Note: Order remains pending (market hasn't reached limit)")

        # Strategy 3: Market Order with Different Size
        print("\nStrategy 3: MARKET ORDER (Larger Size)")
        print("  Approach: Test execution quality with larger position")

        market_order_large = await client.orders.post_market_order(
            account_id=client.account_id,
            instrument=instrument,
            units=15000,  # 3x larger
        )

        if market_order_large.order_fill_transaction is not None:
            fill_price_large = market_order_large.order_fill_transaction.price
            assert fill_price_large is not None

            # Get fresh market price for comparison
            pricing_refresh = await client.pricing.get_pricing(
                account_id=client.account_id,
                instruments=[instrument],
            )
            reference_price = pricing_refresh["prices"][0].asks[0].price

            slippage_large = fill_price_large - reference_price

            order_history.append({
                "strategy": "MARKET_LARGE",
                "order_id": str(market_order_large.order_fill_transaction.id),
                "requested_price": reference_price,
                "fill_price": fill_price_large,
                "slippage": slippage_large,
                "units": 15000,
            })

            print(f"  Order Filled: {market_order_large.order_fill_transaction.id}")
            print(f"  Requested: ~{reference_price:.5f}")
            print(f"  Filled: {fill_price_large:.5f}")
            print(f"  Slippage: {slippage_large * 10000:.2f} pips")

        # ==============================================================================
        # STEP 2: ANALYZE ORDER PERFORMANCE BY STRATEGY
        # ==============================================================================

        print("\n" + "=" * 70)
        print("ORDER PERFORMANCE ANALYSIS")
        print("=" * 70)

        # Group orders by strategy
        strategies: dict[str, list[dict[str, str | Decimal | int]]] = {}
        for order in order_history:
            strategy = order["strategy"]
            assert isinstance(strategy, str)

            if strategy not in strategies:
                strategies[strategy] = []
            strategies[strategy].append(order)

        print(f"\nAnalyzing {len(order_history)} filled orders across {len(strategies)} strategies...\n")

        # Calculate metrics for each strategy
        for strategy_name, orders in strategies.items():
            print(f"  {strategy_name} Strategy:")
            print(f"    Total Orders: {len(orders)}")

            # Calculate slippage statistics
            slippages_raw = [order["slippage"] for order in orders]
            slippages = [s for s in slippages_raw if isinstance(s, Decimal)]

            avg_slippage = sum(slippages, Decimal("0")) / len(slippages)
            max_slippage = max(slippages)
            min_slippage = min(slippages)

            print(f"    Average Slippage: {avg_slippage * 10000:.2f} pips")
            print(f"    Max Slippage: {max_slippage * 10000:.2f} pips")
            print(f"    Min Slippage: {min_slippage * 10000:.2f} pips")

            # Calculate total units executed
            units_raw = [order["units"] for order in orders]
            units_list = [u for u in units_raw if isinstance(u, int)]
            total_units = sum(units_list)
            print(f"    Total Volume: {total_units:,} units")

            # Calculate execution cost (slippage in dollars)
            total_slippage_cost = sum(
                order["slippage"] * order["units"]  # type: ignore
                for order in orders
            )
            print(f"    Execution Cost: ${abs(total_slippage_cost):.2f}")
            print()

        # ==============================================================================
        # STEP 3: COMPARATIVE ANALYSIS
        # ==============================================================================

        print("=" * 70)
        print("COMPARATIVE EXECUTION QUALITY")
        print("=" * 70)

        print("\nKey Insights:")
        print("  • Market orders provide immediate execution but pay the spread")
        print("  • Larger orders may experience slightly worse slippage")
        print("  • Limit orders offer price improvement but require patience")
        print("  • Execution cost = slippage × position size")

        print("\nExecution Quality Ranking (lower slippage = better):")
        strategy_avg_slippage = [
            (strategy, sum(order["slippage"] for order in orders) / len(orders))  # type: ignore
            for strategy, orders in strategies.items()
        ]
        strategy_avg_slippage.sort(key=lambda x: x[1])

        for i, (strategy, avg_slip) in enumerate(strategy_avg_slippage, 1):
            print(f"  {i}. {strategy}: {avg_slip * 10000:.2f} pips average slippage")

        # ==============================================================================
        # STEP 4: AGGREGATED PERFORMANCE METRICS
        # ==============================================================================

        print("\n" + "=" * 70)
        print("AGGREGATE PERFORMANCE METRICS")
        print("=" * 70)

        all_slippages_raw = [order["slippage"] for order in order_history]
        all_slippages = [s for s in all_slippages_raw if isinstance(s, Decimal)]

        overall_avg = sum(all_slippages, Decimal("0")) / len(all_slippages)
        overall_total_units = sum(order["units"] for order in order_history)  # type: ignore
        overall_cost = sum(
            order["slippage"] * order["units"]  # type: ignore
            for order in order_history
        )

        print(f"\n  Total Orders Tracked: {len(order_history)}")
        print(f"  Total Volume: {overall_total_units:,} units")
        print(f"  Overall Average Slippage: {overall_avg * 10000:.2f} pips")
        print(f"  Total Execution Cost: ${abs(overall_cost):.2f}")

        # Calculate slippage variance
        squared_diffs = [(slip - overall_avg) ** 2 for slip in all_slippages]
        variance = sum(squared_diffs, Decimal("0")) / len(all_slippages)
        std_dev = variance ** Decimal("0.5")

        print(f"  Slippage Std Deviation: {std_dev * 10000:.2f} pips")
        print(f"  Execution Consistency: {'HIGH' if std_dev < Decimal('0.0001') else 'MODERATE' if std_dev < Decimal('0.0003') else 'LOW'}")

        # ==============================================================================
        # PRODUCTION ENHANCEMENTS
        # ==============================================================================

        print("\n" + "=" * 70)
        print("PRODUCTION ENHANCEMENTS TO CONSIDER")
        print("=" * 70)
        print("\nTo make this analytics system production-ready, add:")
        print("  • Store order history in database for persistent tracking")
        print("  • Track fill rate (percentage of limit orders that fill)")
        print("  • Monitor time-to-fill for limit orders")
        print("  • Compare execution quality across different instruments")
        print("  • Track execution quality by time of day and market session")
        print("  • Implement alerting for unusually high slippage")
        print("  • Calculate transaction cost analysis (TCA) metrics")
        print("  • Track order rejection rates and reasons")


if __name__ == "__main__":
    # Run the order performance analytics demonstration
    asyncio.run(main())
```

## Key Takeaways

1. **Use OANDA's built-in combinations** - `stop_loss_on_fill` and `take_profit_on_fill`
2. **Keep strategies simple** - Focus on proven order type combinations
3. **Monitor order fills** - Build logic around order state changes
4. **Plan your exits** - Always include protective stops

## Next Steps

- Review [Best Practices](../../guides/understanding/best-practices.md) for robust order handling
- Check [Best Practices](../../guides/understanding/best-practices.md) for production deployment

FiveTwenty provides powerful order combinations through OANDA's proven order types - use these building blocks rather than complex custom strategies.
