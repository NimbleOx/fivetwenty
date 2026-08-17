# Dynamic Order Management

Learn trailing stops, scaling strategies, and adaptive position management for automated trading systems.

## Learning Objectives

By the end of this guide, you will:

- Implement trailing stop mechanisms for profit protection
- Build scaling strategies for position size management
- Create adaptive order systems that respond to market conditions
- Design dynamic risk management systems
- Handle complex position lifecycle management

## Trailing Stop Implementation

Trailing stops dynamically adjust stop-loss levels as price moves in your favor, protecting accumulated profits while giving positions room to grow. Unlike fixed stop losses that remain static, trailing stops "follow" price at a specified distance, automatically tightening protection as profits increase. This creates an asymmetric risk profile where losses are limited but profits can run indefinitely - the holy grail of position management.

OANDA provides native trailing stop functionality that automatically adjusts stop levels server-side as price moves favorably. The FiveTwenty SDK exposes this through `TrailingStopLossOrderRequest`, which attaches trailing stops to existing trades at a specified distance. OANDA's platform handles all trailing logic automatically - no client-side monitoring required. The examples demonstrate both native trailing stops and advanced custom implementations for volatility-adjusted strategies.

### Basic Trailing Stop System

The simplest and most effective trailing stop is OANDA's native implementation. Rather than manually monitoring prices and updating stop orders, you attach a trailing stop to a trade and OANDA's platform handles everything automatically. The stop trails at a fixed distance behind the current price, moving only when price improves, never when it reverses. This server-side automation eliminates the need for continuous client polling and ensures stops update instantly as market moves.

Native trailing stops work by specifying a distance parameter - the number of price units the stop should trail behind current market price. For EUR/USD with 5 decimal places, a distance of 0.0020 means the stop trails 20 pips behind. As price moves favorably, OANDA automatically adjusts the stop to maintain that distance. If price reverses, the stop remains at its most favorable level, never moving further away.

The following example demonstrates opening a position, attaching a native trailing stop with a specified distance, and showing how the stop automatically trails as price moves:

<!-- filepath: example_native_trailing_stop.py -->
```python
import asyncio
from decimal import Decimal

from dotenv import load_dotenv

from fivetwenty import AsyncClient
from fivetwenty.models import InstrumentName, TrailingStopLossOrderRequest

load_dotenv()

# ==============================================================================
# NATIVE TRAILING STOP IMPLEMENTATION
# ==============================================================================

# This example demonstrates OANDA's native trailing stop functionality:
#
# KEY CONCEPTS:
# 1. Native Trailing Stops - OANDA automatically trails stops as price moves favorably
# 2. Distance-Based Trailing - Stop trails at fixed distance (in price units) from current price
# 3. Trade-Linked Orders - Trailing stops attach to existing trades, not positions
# 4. Automatic Management - OANDA handles all trailing logic server-side
#
# HOW IT WORKS:
# OANDA's trailing stops automatically adjust stop-loss levels as price moves in your
# favor. You specify a trailing distance (in price units), and OANDA's server continuously
# monitors price and updates the stop level to maintain that distance. Unlike manual
# trailing systems, this requires no client-side monitoring or order replacements - the
# trailing happens entirely on OANDA's platform.
#
# This code is fully executable and demonstrates native trailing stop usage with SDK.


async def main() -> None:
    """Demonstrate OANDA's native trailing stop functionality with real trade example."""

    print("=" * 60)
    print("NATIVE TRAILING STOP IMPLEMENTATION")
    print("=" * 60)

    # ==============================================================================
    # CONNECT TO OANDA
    # ==============================================================================

    # AsyncClient automatically reads FIVETWENTY_OANDA_* environment variables
    # Context manager ensures proper cleanup of HTTP connections
    async with AsyncClient() as client:
        # ==============================================================================
        # STEP 1: OPEN A POSITION WITH MARKET ORDER
        # ==============================================================================

        # ==============================================================================
        # SDK METHOD: client.orders.post_market_order()
        # ==============================================================================
        #
        # Place a market order to enter a position
        #
        # Parameters:
        #   - account_id: Your OANDA account ID
        #   - instrument: Currency pair (InstrumentName enum)
        #   - units: Position size (positive=buy, negative=sell)
        #
        # Returns: OrderResponse with trade creation details

        print("\nOpening EUR/USD position...")

        market_order = await client.orders.post_market_order(
            account_id=client.account_id,
            instrument=InstrumentName("EUR_USD"),
            units=10000,  # Long position
        )

        # Extract trade ID from market order fill transaction
        assert market_order.get("order_fill_transaction") is not None
        assert market_order.order_fill_transaction.trade_opened is not None
        trade_id = market_order.order_fill_transaction.trade_opened.trade_id
        fill_price = Decimal(str(market_order.order_fill_transaction.price))

        print(" Position opened:")
        print(f"  Trade ID: {trade_id}")
        print(f"  Fill Price: {fill_price:.5f}")
        print("  Size: 10,000 units long")

        # ==============================================================================
        # STEP 2: ATTACH NATIVE TRAILING STOP TO THE TRADE
        # ==============================================================================

        # ==============================================================================
        # SDK METHOD: client.orders.post_order(TrailingStopLossOrderRequest(...))
        # ==============================================================================
        #
        # Create a trailing stop loss order for an existing trade
        #
        # Parameters:
        #   - trade_id: The trade ID to protect (from step 1)
        #   - distance: Trailing distance in price units (Decimal)
        #   - time_in_force: Order lifetime (default "GTC")
        #
        # Returns: OrderResponse with trailing stop order details
        #
        # NOTE: OANDA automatically trails the stop as price moves favorably
        #       The stop maintains the specified distance from the current price

        trailing_distance = Decimal("0.0030")  # 30 pips trailing distance

        print(
            f"\nAttaching native trailing stop (distance: {trailing_distance * 10000:.0f} pips)..."
        )

        trailing_stop_request = TrailingStopLossOrderRequest(
            tradeID=trade_id,  # Use camelCase alias for Pydantic
            distance=trailing_distance,
        )

        trailing_stop_response = await client.orders.post_order(
            account_id=client.account_id, order_request=trailing_stop_request
        )

        # Extract trailing stop order details
        assert trailing_stop_response.order_create_transaction is not None
        trailing_stop_id = trailing_stop_response.order_create_transaction["id"]

        print(" Trailing stop attached:")
        print(f"  Order ID: {trailing_stop_id}")
        print(f"  Trailing Distance: {trailing_distance * 10000:.0f} pips")
        print(f"  Initial Stop Level: {fill_price - trailing_distance:.5f}")

        # ==============================================================================
        # STEP 3: DEMONSTRATE HOW TRAILING WORKS
        # ==============================================================================

        print("\nTrailing Stop Behavior:")
        print(f"  Current Price: {fill_price:.5f}")
        print(f"  Stop Level: {fill_price - trailing_distance:.5f}")
        print(f"\n  If price rises to {fill_price + Decimal('0.0020'):.5f} (+20 pips):")
        print(
            f"   Stop automatically trails to {fill_price + Decimal('0.0020') - trailing_distance:.5f}"
        )
        print(f"\n  If price rises to {fill_price + Decimal('0.0050'):.5f} (+50 pips):")
        print(
            f"   Stop automatically trails to {fill_price + Decimal('0.0050') - trailing_distance:.5f}"
        )
        print("\n  Stop never moves down - only trails upward!")

        # ==============================================================================
        # STEP 4: VERIFY TRADE HAS TRAILING STOP ATTACHED
        # ==============================================================================

        # Fetch trade details to confirm trailing stop
        trade_details = await client.trades.get_trade(
            account_id=client.account_id, trade_specifier=trade_id
        )

        if trade_details["trade"].trailing_stop_loss_order:
            print(f"\n Trade {trade_id} confirmed with trailing stop:")
            print(
                f"  Trailing Stop Order ID: {trade_details['trade'].trailing_stop_loss_order.id}"
            )
            print("  Protection: OANDA manages trailing automatically")

        # ==============================================================================
        # PRODUCTION ENHANCEMENTS
        # ==============================================================================

        print("\n" + "=" * 60)
        print("PRODUCTION ENHANCEMENTS TO CONSIDER")
        print("=" * 60)
        print("\nTo make this strategy production-ready, add:")
        print("  • Calculate trailing distance based on ATR (volatility-adjusted)")
        print(
            "  • Use trailing_stop_loss_on_fill parameter for one-step order+protection"
        )
        print("  • Monitor trade unrealized P/L to assess trailing effectiveness")
        print(
            "  • Implement different trailing distances for different market conditions"
        )
        print("  • Add position size calculation based on trailing distance")
        print("  • Track trailing stop trigger rates and average profit capture")
        print("  • Consider using minimum_distance from instrument details")
        print("  • Implement multi-level trailing (tighten distance as profits grow)")


if __name__ == "__main__":
    # Run the native trailing stop demonstration
    asyncio.run(main())
```

### Advanced Trailing Stop Strategies

#### Volatility-Adjusted Trailing

Market volatility changes constantly - what works as a trailing distance in calm conditions can cause premature exits during volatile periods, while wide stops in quiet markets leave profits on the table. Volatility-adjusted trailing solves this by dynamically calculating trail distances based on current market conditions using the Average True Range (ATR) indicator.

This approach measures recent price volatility and adjusts your trailing stop distance accordingly. During high volatility, the system widens the trailing distance to avoid getting stopped out by normal market noise. During low volatility, it tightens the distance to lock in profits more aggressively. The result is a trailing stop that adapts to market conditions rather than using a fixed, arbitrary distance.

The following example demonstrates calculating ATR from real OANDA historical candles, computing a volatility ratio against a baseline, applying practical bounds, and attaching a native OANDA trailing stop with the calculated distance:

<!-- filepath: example_volatility_adjusted_trailing.py -->
```python
import asyncio
from decimal import Decimal

from dotenv import load_dotenv

from fivetwenty import AsyncClient
from fivetwenty.models import (
    CandlestickGranularity,
    InstrumentName,
    TrailingStopLossOrderRequest,
)

load_dotenv()

# ==============================================================================
# VOLATILITY-ADJUSTED TRAILING STOP IMPLEMENTATION
# ==============================================================================

# This example demonstrates volatility-adaptive trailing stops using ATR:
#
# KEY CONCEPTS:
# 1. ATR Calculation - Measure market volatility from recent price action
# 2. Dynamic Distance - Adjust trailing distance based on current volatility
# 3. Risk Bounds - Apply min/max limits to prevent extreme trail distances
# 4. Native Trailing - Use OANDA's server-side trailing with calculated distance
#
# HOW IT WORKS:
# Calculate Average True Range (ATR) from historical candles to measure volatility.
# Use volatility ratio (current ATR / baseline ATR) to scale the base trailing
# distance. Apply bounds to keep distances practical. Attach native OANDA trailing
# stop with the volatility-adjusted distance. This ensures wider stops in volatile
# markets (reducing false exits) and tighter stops in calm markets (locking profits).
#
# This code is fully executable and calculates real ATR from OANDA candle data.


def calculate_atr(candles: list, period: int = 14) -> Decimal:
    """
    Calculate Average True Range (ATR) for volatility measurement.

    ATR measures market volatility by averaging the true range over a period.
    True Range = max(high-low, abs(high-previous_close), abs(low-previous_close))

    Args:
        candles: List of candle objects with high, low, close prices
        period: Number of periods for ATR calculation (default 14)

    Returns:
        Average True Range as Decimal
    """
    if len(candles) < period + 1:
        raise ValueError(f"Need at least {period + 1} candles for ATR calculation")

    true_ranges = []

    # Calculate True Range for each candle (starting from index 1)
    for i in range(1, len(candles)):
        high = Decimal(candles[i].mid.h)
        low = Decimal(candles[i].mid.l)
        prev_close = Decimal(candles[i - 1].mid.c)

        # True Range = max of three values:
        # 1. Current high - current low
        # 2. Absolute value of current high - previous close
        # 3. Absolute value of current low - previous close
        tr = max(high - low, abs(high - prev_close), abs(low - prev_close))
        true_ranges.append(tr)

    # Average the most recent 'period' true ranges
    recent_trs = true_ranges[-period:]
    atr = sum(recent_trs, Decimal("0")) / Decimal(len(recent_trs))

    return atr


async def main() -> None:
    """Demonstrate volatility-adjusted trailing stops with real ATR calculation."""

    print("=" * 70)
    print("VOLATILITY-ADJUSTED TRAILING STOP IMPLEMENTATION")
    print("=" * 70)

    # ==============================================================================
    # CONNECT TO OANDA
    # ==============================================================================

    # AsyncClient automatically reads FIVETWENTY_OANDA_* environment variables
    # Context manager ensures proper cleanup of HTTP connections
    async with AsyncClient() as client:
        instrument = InstrumentName("EUR_USD")

        # ==============================================================================
        # STEP 1: FETCH HISTORICAL CANDLES FOR ATR CALCULATION
        # ==============================================================================

        print(f"\nFetching historical data for {instrument}...")

        # ==============================================================================
        # SDK METHOD: client.instruments.get_instrument_candles()
        # ==============================================================================
        #
        # Fetch historical price candles for volatility analysis
        #
        # Parameters:
        #   - instrument: Currency pair (InstrumentName enum)
        #   - granularity: Candle timeframe (H1 = 1-hour candles)
        #   - count: Number of candles to fetch (need 15+ for 14-period ATR)
        #
        # Returns: CandlesResponse with list of candle objects

        candles_response = await client.instruments.get_instrument_candles(
            instrument=instrument,
            granularity=CandlestickGranularity.H1,  # 1-hour candles
            count=20,  # Fetch 20 candles for ATR calculation
        )

        candles = candles_response["candles"]
        print(f"Retrieved {len(candles)} hourly candles for volatility analysis")

        # ==============================================================================
        # STEP 2: CALCULATE CURRENT MARKET VOLATILITY (ATR)
        # ==============================================================================

        print("\nCalculating market volatility (ATR)...")

        # Calculate 14-period ATR from candle data
        current_atr = calculate_atr(candles, period=14)

        # Define baseline ATR and base trailing distance
        # Baseline ATR represents "normal" market conditions
        # Base trail is what we'd use in normal volatility
        baseline_atr = Decimal("0.0030")  # 30 pips baseline
        base_trail_distance = Decimal("0.0020")  # 20 pips base trail

        print(f"  Current ATR: {current_atr:.5f} ({current_atr * 10000:.1f} pips)")
        print(f"  Baseline ATR: {baseline_atr:.5f} ({baseline_atr * 10000:.1f} pips)")
        print(
            f"  Base Trail: {base_trail_distance:.5f} ({base_trail_distance * 10000:.1f} pips)"
        )

        # ==============================================================================
        # STEP 3: CALCULATE VOLATILITY-ADJUSTED TRAILING DISTANCE
        # ==============================================================================

        print("\nAdjusting trail distance for current volatility...")

        # Calculate volatility multiplier
        # If current ATR > baseline: multiplier > 1 (wider stops)
        # If current ATR < baseline: multiplier < 1 (tighter stops)
        volatility_multiplier = current_atr / baseline_atr
        adjusted_trail = base_trail_distance * volatility_multiplier

        print(f"  Volatility Ratio: {volatility_multiplier:.2f}x")
        print(
            f"  Raw Adjusted Trail: {adjusted_trail:.5f} ({adjusted_trail * 10000:.1f} pips)"
        )

        # Apply reasonable bounds to prevent extreme distances
        min_trail = Decimal("0.0015")  # 15 pips minimum
        max_trail = Decimal("0.0060")  # 60 pips maximum

        trail_distance = max(min_trail, min(max_trail, adjusted_trail))

        print(
            f"  Final Trail Distance: {trail_distance:.5f} ({trail_distance * 10000:.1f} pips)"
        )

        if trail_distance == min_trail:
            print("   (Capped at minimum - very low volatility)")
        elif trail_distance == max_trail:
            print("   (Capped at maximum - very high volatility)")
        else:
            print(f"   (Within bounds - {volatility_multiplier:.0%} of baseline)")

        # ==============================================================================
        # STEP 4: OPEN POSITION WITH MARKET ORDER
        # ==============================================================================

        print(f"\nOpening {instrument} position...")

        market_order = await client.orders.post_market_order(
            account_id=client.account_id,
            instrument=instrument,
            units=10000,  # Long position
        )

        # Check if order filled successfully
        if market_order.get("order_fill_transaction") is None:
            print("\nOrder was not filled - market is likely closed")
            print("Forex market hours: Sunday 5 PM ET - Friday 5 PM ET")
            print("\nThis example demonstrates the calculation and would attach")
            print("the trailing stop when the market is open.")
            return

        # Extract trade ID from fill transaction
        assert market_order.order_fill_transaction.trade_opened is not None
        trade_id = market_order.order_fill_transaction.trade_opened.trade_id
        fill_price = market_order.order_fill_transaction.price  # Already a Decimal from SDK
        assert fill_price is not None

        print("Position opened:")
        print(f"  Trade ID: {trade_id}")
        print(f"  Fill Price: {fill_price:.5f}")
        print("  Size: 10,000 units long")

        # ==============================================================================
        # STEP 5: ATTACH VOLATILITY-ADJUSTED TRAILING STOP
        # ==============================================================================

        print("\nAttaching volatility-adjusted trailing stop...")
        print(f"  Distance: {trail_distance * 10000:.1f} pips (ATR-based)")

        trailing_stop_request = TrailingStopLossOrderRequest(
            tradeID=trade_id,
            distance=trail_distance,  # Use volatility-adjusted distance
        )

        trailing_stop_response = await client.orders.post_order(
            account_id=client.account_id, order_request=trailing_stop_request
        )

        assert trailing_stop_response.order_create_transaction is not None
        trailing_stop_id = trailing_stop_response.order_create_transaction["id"]

        print("Trailing stop attached:")
        print(f"  Order ID: {trailing_stop_id}")
        print(f"  Distance: {trail_distance * 10000:.1f} pips")
        print(f"  Initial Stop: {fill_price - trail_distance:.5f}")

        # ==============================================================================
        # STEP 6: EXPLAIN VOLATILITY-ADAPTIVE BEHAVIOR
        # ==============================================================================

        print("\n" + "=" * 70)
        print("VOLATILITY-ADAPTIVE TRAILING BEHAVIOR")
        print("=" * 70)

        print("\nHow volatility affects trailing distance:")

        # Show examples with different volatility scenarios
        scenarios = [
            (Decimal("0.0015"), "Low Volatility (15 pips ATR)"),
            (Decimal("0.0030"), "Normal Volatility (30 pips ATR - baseline)"),
            (Decimal("0.0060"), "High Volatility (60 pips ATR)"),
        ]

        for scenario_atr, description in scenarios:
            multiplier = scenario_atr / baseline_atr
            scenario_trail = base_trail_distance * multiplier
            scenario_trail = max(min_trail, min(max_trail, scenario_trail))

            print(f"\n{description}:")
            print(f"  Multiplier: {multiplier:.2f}x")
            print(f"  Trail Distance: {scenario_trail * 10000:.1f} pips")
            print(
                f"  Logic: {'Tighter stops lock profits faster' if multiplier < 1 else 'Wider stops avoid noise' if multiplier > 1 else 'Standard distance'}"
            )

        # ==============================================================================
        # PRODUCTION ENHANCEMENTS
        # ==============================================================================

        print("\n" + "=" * 70)
        print("PRODUCTION ENHANCEMENTS TO CONSIDER")
        print("=" * 70)
        print("\nTo make this strategy production-ready, add:")
        print("  • Recalculate ATR periodically to adapt to changing volatility")
        print("  • Use multiple timeframes (H1, H4, D1) for ATR validation")
        print("  • Implement different bounds for different instruments")
        print("  • Add volatility regime detection (trending vs ranging)")
        print("  • Track relationship between ATR and trailing stop effectiveness")
        print("  • Consider using Bollinger Bands or standard deviation as alternative")
        print("  • Implement dynamic recalculation when ATR changes significantly")
        print("  • Add minimum hold time before allowing trail adjustment")


if __name__ == "__main__":
    # Run the volatility-adjusted trailing stop demonstration
    asyncio.run(main())
```

#### Accelerated Trailing System

Fixed trailing distances create a dilemma - wide enough to avoid premature exits but tight enough to lock in meaningful profits. Accelerated trailing solves this by starting with a generous trailing distance that gives trades room to develop, then progressively tightening as profits accumulate. This approach protects early-stage trades from normal volatility while aggressively locking in gains once positions prove themselves.

The acceleration works through profit thresholds. A position might start with a 30-pip trailing distance, tighten to 24 pips after reaching +20 pips profit, drop to 18 pips at +40 pips profit, and finally lock to 12 pips at +60 pips profit. Each threshold ensures larger profits are protected more carefully, reducing risk as the reward grows.

The following example demonstrates defining profit thresholds, opening a position, attaching an initial trailing stop, and simulating how the trail distance would tighten as the position becomes more profitable:

<!-- filepath: example_accelerated_trailing.py -->
```python
import asyncio
from decimal import Decimal

from dotenv import load_dotenv

from fivetwenty import AsyncClient
from fivetwenty.models import (
    InstrumentName,
    TrailingStopLossOrderRequest,
)

load_dotenv()

# ==============================================================================
# ACCELERATED TRAILING STOP IMPLEMENTATION
# ==============================================================================

# This example demonstrates profit-based trailing stop acceleration:
#
# KEY CONCEPTS:
# 1. Profit Thresholds - Tighten trail distance as position becomes more profitable
# 2. Progressive Acceleration - Trail distance reduces in stages as profit increases
# 3. Lock-In Strategy - Tighter trails lock in more profit as position proves itself
# 4. Risk Reduction - Downside risk decreases as profits accumulate
#
# HOW IT WORKS:
# Start with a wider trailing distance to give the trade room to develop. As the
# position becomes profitable and hits profit thresholds, progressively tighten
# the trailing distance. This locks in more profit while still allowing the trade
# to run. For example: start at 30 pips trailing, tighten to 24 pips at +20 pips
# profit, then to 18 pips at +40 pips profit, and finally to 12 pips at +60 pips
# profit. This ensures larger profits are protected more aggressively.
#
# This code is fully executable and demonstrates accelerated trailing with OANDA.


async def main() -> None:
    """Demonstrate accelerated trailing stops that tighten as profits increase."""

    print("=" * 70)
    print("ACCELERATED TRAILING STOP IMPLEMENTATION")
    print("=" * 70)

    # ==============================================================================
    # CONNECT TO OANDA
    # ==============================================================================

    # AsyncClient automatically reads FIVETWENTY_OANDA_* environment variables
    # Context manager ensures proper cleanup of HTTP connections
    async with AsyncClient() as client:
        instrument = InstrumentName("EUR_USD")

        # ==============================================================================
        # STEP 1: DEFINE ACCELERATION THRESHOLDS
        # ==============================================================================

        print("\nConfiguring accelerated trailing thresholds...")

        # Define initial trailing distance and profit-based acceleration levels
        initial_trail = Decimal("0.0030")  # 30 pips initial trail

        # Profit thresholds progressively tighten the trail distance
        # Format: (profit_threshold, new_trail_distance)
        acceleration_levels = [
            (Decimal("0.0020"), Decimal("0.0024")),  # At +20 pips profit -> 24 pips trail (20% tighter)
            (Decimal("0.0040"), Decimal("0.0018")),  # At +40 pips profit -> 18 pips trail (40% tighter)
            (Decimal("0.0060"), Decimal("0.0012")),  # At +60 pips profit -> 12 pips trail (60% tighter)
        ]

        print(f"  Initial Trail Distance: {initial_trail * 10000:.0f} pips")
        print("\n  Acceleration Thresholds:")
        for profit_threshold, trail_distance in acceleration_levels:
            print(f"    At +{profit_threshold * 10000:.0f} pips profit -> {trail_distance * 10000:.0f} pips trail")

        # ==============================================================================
        # STEP 2: OPEN POSITION WITH MARKET ORDER
        # ==============================================================================

        print(f"\nOpening {instrument} position...")

        market_order = await client.orders.post_market_order(
            account_id=client.account_id,
            instrument=instrument,
            units=10000,  # Long position
        )

        # Check if order filled successfully
        if market_order.get("order_fill_transaction") is None:
            print("\nOrder was not filled - market is likely closed")
            print("Forex market hours: Sunday 5 PM ET - Friday 5 PM ET")
            print("\nThis example demonstrates the acceleration logic and would")
            print("progressively tighten the trailing stop as profits increase.")
            return

        # Extract trade details
        assert market_order.order_fill_transaction.trade_opened is not None
        trade_id = market_order.order_fill_transaction.trade_opened.trade_id
        entry_price = market_order.order_fill_transaction.price  # Already a Decimal from SDK
        assert entry_price is not None

        print("Position opened:")
        print(f"  Trade ID: {trade_id}")
        print(f"  Entry Price: {entry_price:.5f}")
        print("  Size: 10,000 units long")

        # ==============================================================================
        # STEP 3: ATTACH INITIAL TRAILING STOP
        # ==============================================================================

        print(f"\nAttaching initial trailing stop ({initial_trail * 10000:.0f} pips)...")

        trailing_stop_request = TrailingStopLossOrderRequest(
            tradeID=trade_id,
            distance=initial_trail,
        )

        trailing_stop_response = await client.orders.post_order(
            account_id=client.account_id,
            order_request=trailing_stop_request,
        )

        assert trailing_stop_response.order_create_transaction is not None
        trailing_stop_id = trailing_stop_response.order_create_transaction["id"]

        print("Initial trailing stop attached:")
        print(f"  Order ID: {trailing_stop_id}")
        print(f"  Distance: {initial_trail * 10000:.0f} pips")
        print(f"  Initial Stop: {entry_price - initial_trail:.5f}")

        # ==============================================================================
        # STEP 4: DEMONSTRATE ACCELERATION LOGIC
        # ==============================================================================

        print("\n" + "=" * 70)
        print("ACCELERATED TRAILING BEHAVIOR")
        print("=" * 70)

        print("\nHow trailing distance adjusts with profit:")

        current_trail = initial_trail

        # Simulate price movements and show how trail distance accelerates
        profit_scenarios = [
            Decimal("0.0000"),  # Entry
            Decimal("0.0010"),  # +10 pips profit
            Decimal("0.0020"),  # +20 pips profit (first threshold)
            Decimal("0.0030"),  # +30 pips profit
            Decimal("0.0040"),  # +40 pips profit (second threshold)
            Decimal("0.0050"),  # +50 pips profit
            Decimal("0.0060"),  # +60 pips profit (third threshold)
        ]

        for profit in profit_scenarios:
            # Determine trail distance for current profit level
            new_trail = initial_trail
            for threshold, trail_distance in acceleration_levels:
                if profit >= threshold:
                    new_trail = trail_distance

            simulated_price = entry_price + profit
            stop_level = simulated_price - new_trail

            if new_trail != current_trail:
                print(f"\n  Profit: +{profit * 10000:.0f} pips (Price: {simulated_price:.5f})")
                print(f"    TRAIL TIGHTENED: {current_trail * 10000:.0f} pips -> {new_trail * 10000:.0f} pips")
                print(f"    New Stop Level: {stop_level:.5f}")
                print(f"    Protected Profit: {(simulated_price - stop_level) * 10000:.0f} pips")
                current_trail = new_trail
            else:
                print(f"\n  Profit: +{profit * 10000:.0f} pips (Price: {simulated_price:.5f})")
                print(f"    Trail Distance: {new_trail * 10000:.0f} pips")
                print(f"    Stop Level: {stop_level:.5f}")

        # ==============================================================================
        # PRODUCTION ENHANCEMENTS
        # ==============================================================================

        print("\n" + "=" * 70)
        print("PRODUCTION ENHANCEMENTS TO CONSIDER")
        print("=" * 70)
        print("\nTo make this strategy production-ready, add:")
        print("  • Monitor trade unrealized P/L and replace trailing stop when thresholds hit")
        print("  • Use webhooks or streaming pricing for real-time profit monitoring")
        print("  • Implement smooth acceleration (gradual tightening vs stepped changes)")
        print("  • Add maximum trail tightening limit to prevent over-optimization")
        print("  • Consider time-based acceleration (tighten after holding period)")
        print("  • Track acceleration effectiveness across different market conditions")
        print("  • Implement partial position scaling with different acceleration curves")
        print("  • Add minimum profit requirement before enabling acceleration")


if __name__ == "__main__":
    # Run the accelerated trailing stop demonstration
    asyncio.run(main())
```

#### Manual Stop Loss Modification

Trailing stops automate stop movement, but sometimes you need manual control to react to specific market conditions. A support level might hold stronger than expected, or news might change your risk tolerance. Manual stop modification lets you tighten risk after partial profits, move to breakeven once trades prove themselves, or adjust protection based on technical levels the market reveals.

The core workflow is simple: open a position with an initial stop, then update the stop price as conditions change using `client.trades.put_trade_orders()`. Start with a conservative stop to give the trade room. As it moves in your favor, progressively tighten the stop - first to breakeven to eliminate risk, then into profit to lock in gains. This transforms winning trades from risk exposure into risk-free opportunities.

The following example demonstrates opening a position, placing an initial stop loss, executing one real stop modification to demonstrate the API, then showing the full progression from initial risk through breakeven to locked profits:

<!-- filepath: example_stop_loss_modification.py -->
```python
import asyncio
from decimal import Decimal

from dotenv import load_dotenv

from fivetwenty import AsyncClient
from fivetwenty.models import InstrumentName, StopLossDetails

load_dotenv()

# ==============================================================================
# STOP LOSS MODIFICATION STRATEGY
# ==============================================================================

# This example demonstrates dynamic stop loss management:
#
# KEY CONCEPTS:
# 1. Breakeven Stops - Move stop to entry after initial profit
# 2. Trailing Stops - Update stops as position moves in favor
# 3. Risk Reduction - Lock in profits progressively
# 4. Dynamic Management - Adjust stops based on market movement
#
# HOW IT WORKS:
# Open a position with initial stop loss. As the trade moves in your favor,
# update the stop loss to reduce risk and lock in profits. First move stop to
# breakeven when position shows initial profit. Then trail the stop upward as
# profits increase. This transforms winning trades into risk-free positions while
# allowing profits to run.
#
# This code is fully executable and demonstrates stop modification with OANDA.


async def main() -> None:
    """Demonstrate dynamic stop loss modification."""

    print("=" * 70)
    print("STOP LOSS MODIFICATION STRATEGY")
    print("=" * 70)

    # ==============================================================================
    # CONNECT TO OANDA
    # ==============================================================================

    # AsyncClient automatically reads FIVETWENTY_OANDA_* environment variables
    # Context manager ensures proper cleanup of HTTP connections
    async with AsyncClient() as client:
        instrument = InstrumentName("EUR_USD")

        # ==============================================================================
        # STEP 1: OPEN POSITION WITH INITIAL STOP LOSS
        # ==============================================================================

        print(f"\nOpening {instrument} position with initial stop loss...")

        # Get current price for calculations
        pricing = await client.pricing.get_pricing(
            account_id=client.account_id,
            instruments=[instrument],
        )
        current_price = pricing["prices"][0].asks[0].price

        # Define initial stop loss below entry
        initial_stop_distance = Decimal("0.0050")  # 50 pips below entry
        initial_stop = current_price - initial_stop_distance

        print(f"  Entry Price: ~{current_price:.5f}")
        print(f"  Initial Stop: {initial_stop:.5f} (50 pips below entry)")
        print(f"  Initial Risk: {initial_stop_distance * 10000:.0f} pips")

        # Open position
        market_order = await client.orders.post_market_order(
            account_id=client.account_id,
            instrument=instrument,
            units=10000,
        )

        # Check if order filled
        if market_order.get("order_fill_transaction") is None:
            print("\nOrder was not filled - market is likely closed")
            print("Forex market hours: Sunday 5 PM ET - Friday 5 PM ET")
            print("\nThis example demonstrates stop modification logic")
            return

        # Extract trade details
        assert market_order.order_fill_transaction.trade_opened is not None
        trade_id = market_order.order_fill_transaction.trade_opened.trade_id
        entry_price = market_order.order_fill_transaction.price
        assert entry_price is not None

        # Recalculate initial stop based on actual entry
        initial_stop = entry_price - initial_stop_distance

        print("\n  Position Opened:")
        print(f"    Trade ID: {trade_id}")
        print(f"    Entry Price: {entry_price:.5f}")
        print("    Size: 10,000 units long")

        # Place initial stop loss order
        await client.trades.put_trade_orders(
            account_id=client.account_id,
            trade_specifier=trade_id,
            stop_loss=StopLossDetails(price=initial_stop),
        )

        print(f"    Stop Loss: {initial_stop:.5f}")
        print(f"    Risk: ${initial_stop_distance * 10000:.2f}")

        # ==============================================================================
        # STEP 2: DEMONSTRATE STOP MODIFICATION CAPABILITY
        # ==============================================================================

        print("\n" + "=" * 70)
        print("STOP LOSS MODIFICATION EXAMPLE")
        print("=" * 70)

        # Demonstrate one real stop update
        print("\n  Updating stop loss to demonstrate modification capability...")

        # Move stop slightly tighter (but not to breakeven to avoid immediate trigger)
        tighter_stop = entry_price - Decimal("0.0030")  # 30 pips below entry (was 50)

        await client.trades.put_trade_orders(
            account_id=client.account_id,
            trade_specifier=trade_id,
            stop_loss=StopLossDetails(price=tighter_stop),
        )

        print(f"    Original Stop: {initial_stop:.5f} (50 pips below)")
        print(f"    Updated Stop: {tighter_stop:.5f} (30 pips below)")
        print(f"    Risk Reduction: {(initial_stop_distance - Decimal('0.0030')) * 10000:.0f} pips (40% tighter)")

        # ==============================================================================
        # STEP 3: PROGRESSIVE STOP SCENARIOS (EDUCATIONAL)
        # ==============================================================================

        print("\n" + "=" * 70)
        print("PROGRESSIVE STOP LOSS STRATEGY")
        print("=" * 70)

        print("\nHow stops evolve as trade moves in favor:")

        # Define progressive stop levels for educational demonstration
        breakeven_stop = entry_price
        profit_lock_stop = entry_price + Decimal("0.0020")  # Lock in 20 pips
        increased_profit_stop = entry_price + Decimal("0.0045")  # Lock in 45 pips

        # Define stop progression scenarios
        scenarios = [
            ("Initial Setup", entry_price, initial_stop, "Set stop 50 pips below entry", -initial_stop_distance),
            ("Tighten Risk", entry_price, tighter_stop, "Tighten to 30 pips (already done above)", Decimal("0")),
            ("Move to Breakeven", entry_price + Decimal("0.0025"), breakeven_stop, "When +25 pips profit, move stop to entry", Decimal("0")),
            ("Lock First Profit", entry_price + Decimal("0.0050"), profit_lock_stop, "When +50 pips profit, lock in +20 pips", Decimal("0.0020")),
            ("Increase Locked Profit", entry_price + Decimal("0.0075"), increased_profit_stop, "When +75 pips profit, lock in +45 pips", Decimal("0.0045")),
        ]

        for i, (stage, market_price, stop_price, action, locked_profit) in enumerate(scenarios, 1):
            profit_pips = locked_profit * 10000
            distance_from_market = market_price - stop_price
            distance_pips = distance_from_market * 10000

            print(f"\n  Stage {i}: {stage}")
            print(f"    Action: {action}")
            print(f"    Market Price: {market_price:.5f}")
            print(f"    Stop Price: {stop_price:.5f}")
            print(f"    Distance: {abs(distance_pips):.0f} pips {'below' if distance_pips > 0 else 'above'} market")
            print(f"    Locked P/L: {profit_pips:+.0f} pips (${locked_profit * 10000:+.2f})")

        # ==============================================================================
        # STEP 4: COMPARE STATIC vs DYNAMIC STOPS
        # ==============================================================================

        print("\n" + "=" * 70)
        print("STATIC vs DYNAMIC STOP COMPARISON")
        print("=" * 70)

        print("\n  Static Stop Approach:")
        print(f"    Initial stop at {initial_stop:.5f} never moved")
        print(f"    Risk remains: ${initial_stop_distance * 10000:.2f}")
        print("    If market reverses to entry: Full risk still exposed")

        print("\n  Dynamic Stop Approach:")
        print(f"    Stop progressively moved from {initial_stop:.5f} to {increased_profit_stop:.5f}")
        print(f"    Risk reduced from ${initial_stop_distance * 10000:.2f} to ZERO")
        print(f"    Profit locked: ${Decimal('0.0045') * 10000:.2f} minimum")
        print("    If market reverses to entry: Exit with profit!")

        # ==============================================================================
        # STEP 5: CALCULATE IMPROVEMENT
        # ==============================================================================

        print("\n" + "=" * 70)
        print("RISK REDUCTION ANALYSIS")
        print("=" * 70)

        initial_risk = initial_stop_distance * 10000
        final_locked_profit = Decimal("0.0045") * 10000
        improvement = initial_risk + final_locked_profit

        print(f"\n  Initial Risk: ${initial_risk:.2f}")
        print(f"  Final Position: ${final_locked_profit:.2f} profit guaranteed")
        print(f"  Total Improvement: ${improvement:.2f}")
        print(f"  Risk Transformation: From -${initial_risk:.2f} exposure to +${final_locked_profit:.2f} locked")

        # ==============================================================================
        # PRODUCTION ENHANCEMENTS
        # ==============================================================================

        print("\n" + "=" * 70)
        print("PRODUCTION ENHANCEMENTS TO CONSIDER")
        print("=" * 70)
        print("\nTo make this strategy production-ready, add:")
        print("  • Automated trailing based on price movement detection")
        print("  • ATR-based trailing distance (volatility-adjusted)")
        print("  • Different trailing rules for different profit levels")
        print("  • Time-based stop tightening (tighten after X hours in profit)")
        print("  • News event protection (widen stops before major announcements)")
        print("  • Weekend gap protection (tighten stops before market close)")
        print("  • Partial position stop management (different stops per tier)")
        print("  • Rollback protection (prevent moving stop further from entry)")


if __name__ == "__main__":
    # Run the stop loss modification demonstration
    asyncio.run(main())
```

## Position Scaling Strategies

Position scaling strategies systematically build or reduce exposure based on price action and market confirmation. Scale-in approaches add to winning positions as they prove themselves, averaging up into strength rather than weakness. Scale-out strategies take partial profits at different levels, reducing risk while maintaining exposure to continued favorable moves. Both approaches improve average entry prices and optimize risk-adjusted returns compared to all-or-nothing position sizing.

The SDK's order placement methods (`client.orders.post_limit_order()`, `client.orders.post_market_order()`) enable precise scaling implementations by placing orders at calculated intervals. You'll learn to build scale-in pyramids that add positions as price confirms your thesis, and scale-out systems that systematically reduce exposure while locking in profits at predetermined levels.

### Scale-In Strategy Implementation

Entering a full position at a single price point exposes you to timing risk - what if you buy right before a dip? Scale-in strategies solve this by dividing your target position across multiple entry levels at different prices. Instead of buying 40,000 units at current market, you place four 10,000-unit orders spaced below the market. As price retraces and fills each level, you build the position at progressively better average prices.

This approach improves your cost basis while reducing entry timing risk. If price immediately rallies, you get partial exposure. If it dips first (which forex pairs often do), you accumulate at better prices and your average entry improves with each fill. The key is systematic execution - predetermined levels and sizes, not emotional averaging down.

The following example demonstrates fetching current market price, calculating scale-in levels, placing limit orders at each level, and analyzing how average cost improves as levels fill:

<!-- filepath: example_scale_in_strategy.py -->
```python
import asyncio
from decimal import Decimal

from dotenv import load_dotenv

from fivetwenty import AsyncClient
from fivetwenty.models import InstrumentName

load_dotenv()

# ==============================================================================
# SCALE-IN STRATEGY IMPLEMENTATION
# ==============================================================================

# This example demonstrates systematic position building through scale-in levels:
#
# KEY CONCEPTS:
# 1. Multiple Entry Levels - Spread entries across price range for better average
# 2. Position Pyramiding - Add to position as it proves itself
# 3. Risk Distribution - Divide capital across multiple price points
# 4. Average Cost Improvement - Lower entries improve overall position basis
#
# HOW IT WORKS:
# Instead of entering a full position at one price, divide it across multiple
# levels. For example, to build a 40,000 unit EUR/USD position, place four
# 10,000-unit limit orders spaced 20 pips apart below current price. As price
# moves down and fills each level, you accumulate position at progressively
# better prices. This improves your average entry cost compared to entering
# everything at the current market price.
#
# This code is fully executable and demonstrates scale-in with OANDA limit orders.


async def main() -> None:
    """Demonstrate scale-in strategy with multiple entry levels."""

    print("=" * 70)
    print("SCALE-IN STRATEGY IMPLEMENTATION")
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

        # ==============================================================================
        # SDK METHOD: client.pricing.get_pricing()
        # ==============================================================================
        #
        # Get current market prices for instruments
        #
        # Parameters:
        #   - account_id: Your OANDA account ID
        #   - instruments: List of instruments to price
        #
        # Returns: PricingResponse with current bid/ask prices

        pricing = await client.pricing.get_pricing(
            account_id=client.account_id,
            instruments=[instrument],
        )

        current_price = pricing["prices"][0].bids[0].price  # Already a Decimal from SDK
        print(f"Current market price: {current_price:.5f}")

        # ==============================================================================
        # STEP 2: CONFIGURE SCALE-IN LEVELS
        # ==============================================================================

        print("\nConfiguring scale-in levels...")

        # Total position target and division into levels
        total_units = 40000  # Total position size
        num_levels = 4  # Number of entry levels
        units_per_level = total_units // num_levels
        level_spacing = Decimal("0.0020")  # 20 pips between levels

        print(f"  Total position target: {total_units:,} units")
        print(f"  Divided into {num_levels} levels of {units_per_level:,} units each")
        print(f"  Level spacing: {level_spacing * 10000:.0f} pips")

        # Calculate entry price for each level
        # Levels are placed below current price to catch dips
        scale_levels: list[dict[str, Decimal | int]] = []
        for i in range(num_levels):
            level_price = current_price - (level_spacing * (i + 1))
            scale_levels.append({
                "level": i + 1,
                "price": level_price,
                "units": units_per_level,
            })

        print("\n  Scale-in levels:")
        for level in scale_levels:
            lvl_price = level["price"]
            lvl_units = level["units"]
            assert isinstance(lvl_price, Decimal)
            assert isinstance(lvl_units, int)
            pips_below = (current_price - lvl_price) * 10000
            print(f"    Level {level['level']}: {lvl_units:,} units @ {lvl_price:.5f} ({pips_below:.0f} pips below)")

        # ==============================================================================
        # STEP 3: PLACE LIMIT ORDERS AT EACH LEVEL
        # ==============================================================================

        print(f"\nPlacing {num_levels} limit orders...")

        placed_orders = []

        for level in scale_levels:
            level_price_val = level["price"]
            level_units_val = level["units"]
            level_num = level["level"]
            assert isinstance(level_price_val, Decimal)
            assert isinstance(level_units_val, int)
            assert isinstance(level_num, int)

            # ==============================================================================
            # SDK METHOD: client.orders.post_limit_order()
            # ==============================================================================
            #
            # Place a limit order at specific price
            #
            # Parameters:
            #   - account_id: Your OANDA account ID
            #   - instrument: Currency pair
            #   - units: Position size (positive for buy)
            #   - price: Limit price to execute at
            #
            # Returns: OrderResponse with order creation details

            order_response = await client.orders.post_limit_order(
                account_id=client.account_id,
                instrument=instrument,
                units=level_units_val,
                price=level_price_val,
            )

            assert order_response.order_create_transaction is not None
            order_id = order_response.order_create_transaction["id"]

            placed_orders.append({
                "level": level_num,
                "order_id": order_id,
                "price": level_price_val,
                "units": level_units_val,
            })

            print(f"  Level {level_num}: Order {order_id} placed at {level_price_val:.5f}")

        print(f"\nAll {num_levels} scale-in orders active")

        # ==============================================================================
        # STEP 4: DEMONSTRATE AVERAGE COST CALCULATION
        # ==============================================================================

        print("\n" + "=" * 70)
        print("SCALE-IN AVERAGE COST ANALYSIS")
        print("=" * 70)

        print("\nAs price moves down and fills levels, average cost improves:")

        # Simulate different fill scenarios
        cumulative_units = 0
        cumulative_cost = Decimal("0")

        for i, level in enumerate(scale_levels, 1):
            level_price_calc = level["price"]
            level_units_calc = level["units"]
            level_num_calc = level["level"]
            assert isinstance(level_price_calc, Decimal)
            assert isinstance(level_units_calc, int)
            assert isinstance(level_num_calc, int)

            # Add this level to cumulative position
            cumulative_units += level_units_calc
            cumulative_cost += level_price_calc * level_units_calc
            average_price = cumulative_cost / cumulative_units

            print(f"\n  After Level {level_num_calc} fills ({level_price_calc:.5f}):")
            print(f"    Accumulated position: {cumulative_units:,} units")
            print(f"    Average entry price: {average_price:.5f}")
            print(f"    Improvement vs market: {(current_price - average_price) * 10000:.1f} pips better")

            # Calculate profit if price returns to original level
            potential_profit = (current_price - average_price) * cumulative_units
            print(f"    If price returns to {current_price:.5f}: ${potential_profit:.2f} profit")

        # ==============================================================================
        # PRODUCTION ENHANCEMENTS
        # ==============================================================================

        print("\n" + "=" * 70)
        print("PRODUCTION ENHANCEMENTS TO CONSIDER")
        print("=" * 70)
        print("\nTo make this strategy production-ready, add:")
        print("  • Monitor filled orders and adjust remaining levels dynamically")
        print("  • Place protective stop for accumulated position after each fill")
        print("  • Implement dynamic level spacing based on ATR or volatility")
        print("  • Cancel unfilled levels if position reaches target size")
        print("  • Add time-based expiration for stale unfilled levels")
        print("  • Track fill rate and adjust level spacing for optimization")
        print("  • Implement partial fills handling for large positions")
        print("  • Consider scaling-in on confirmation vs dip-buying")


if __name__ == "__main__":
    # Run the scale-in strategy demonstration
    asyncio.run(main())
```

### Scale-Out Strategy Implementation

Taking all profits at a single target forces an uncomfortable choice - exit early and leave money on the table, or aim for large targets and risk giving back gains if price reverses. Scale-out strategies eliminate this dilemma by closing the position in stages at progressively higher profit targets. A portion exits early to lock in some profit (protecting against full reversals), while the remainder stays exposed to capture larger moves.

This creates an asymmetric payoff where you're protected if price reverses after modest gains, but still participating if it runs further. For example, closing 25% at +20 pips locks in profit, another 25% at +40 pips banks more, 25% at +60 pips continues building, and the final 25% at +80 pips captures the full move. Even if price only reaches the second target, you've realized profits on half the position - better than an all-or-nothing approach.

The following example demonstrates opening a position, configuring multiple take-profit levels, placing limit orders to close portions at each level, and analyzing profit realization compared to single-exit strategies:

<!-- filepath: example_scale_out_strategy.py -->
```python
import asyncio
from decimal import Decimal

from dotenv import load_dotenv

from fivetwenty import AsyncClient
from fivetwenty.models import InstrumentName

load_dotenv()

# ==============================================================================
# SCALE-OUT STRATEGY IMPLEMENTATION
# ==============================================================================

# This example demonstrates systematic profit-taking through scale-out levels:
#
# KEY CONCEPTS:
# 1. Partial Profit Taking - Close portions of position at different levels
# 2. Risk Reduction - Lock in gains while maintaining exposure
# 3. Tiered Exits - Multiple take-profit targets for optimal profit capture
# 4. Asymmetric Payoff - Small partial exits protect against reversals
#
# HOW IT WORKS:
# Instead of closing an entire position at one target, divide the exit across
# multiple profit levels. For example, with a 40,000 unit position, close 10,000
# units at +20 pips, another 10,000 at +40 pips, another 10,000 at +60 pips,
# and the final 10,000 at +80 pips. This locks in profits incrementally while
# allowing the remaining position to capture larger moves.
#
# This code is fully executable and demonstrates scale-out with OANDA limit orders.


async def main() -> None:
    """Demonstrate scale-out strategy with multiple profit-taking levels."""

    print("=" * 70)
    print("SCALE-OUT STRATEGY IMPLEMENTATION")
    print("=" * 70)

    # ==============================================================================
    # CONNECT TO OANDA
    # ==============================================================================

    # AsyncClient automatically reads FIVETWENTY_OANDA_* environment variables
    # Context manager ensures proper cleanup of HTTP connections
    async with AsyncClient() as client:
        instrument = InstrumentName("EUR_USD")

        # ==============================================================================
        # STEP 1: OPEN INITIAL POSITION
        # ==============================================================================

        print(f"\nOpening {instrument} position to demonstrate scale-out...")

        market_order = await client.orders.post_market_order(
            account_id=client.account_id,
            instrument=instrument,
            units=40000,  # Full position size
        )

        # Check if order filled successfully
        if market_order.get("order_fill_transaction") is None:
            print("\nOrder was not filled - market is likely closed")
            print("Forex market hours: Sunday 5 PM ET - Friday 5 PM ET")
            print("\nThis example demonstrates the scale-out logic and would")
            print("place take-profit orders at multiple levels when market is open.")
            return

        # Extract position details
        assert market_order.order_fill_transaction.trade_opened is not None
        trade_id = market_order.order_fill_transaction.trade_opened.trade_id
        entry_price = market_order.order_fill_transaction.price  # Already a Decimal from SDK
        assert entry_price is not None
        position_size = 40000

        print("Position opened:")
        print(f"  Trade ID: {trade_id}")
        print(f"  Entry Price: {entry_price:.5f}")
        print(f"  Size: {position_size:,} units long")

        # ==============================================================================
        # STEP 2: CONFIGURE SCALE-OUT LEVELS
        # ==============================================================================

        print("\nConfiguring scale-out profit targets...")

        # Define profit-taking levels and position sizes
        num_levels = 4
        units_per_level = position_size // num_levels

        # Profit targets progressively further from entry
        profit_targets = [
            Decimal("0.0020"),  # +20 pips
            Decimal("0.0040"),  # +40 pips
            Decimal("0.0060"),  # +60 pips
            Decimal("0.0080"),  # +80 pips
        ]

        print(f"  Total position: {position_size:,} units")
        print(f"  Divided into {num_levels} exit levels of {units_per_level:,} units each")

        # Calculate take-profit prices for each level
        scale_out_levels = []
        for i, target_distance in enumerate(profit_targets):
            target_price = entry_price + target_distance
            scale_out_levels.append({
                "level": i + 1,
                "price": target_price,
                "units": units_per_level,
                "distance": target_distance,
            })

        print("\n  Scale-out profit targets:")
        for level in scale_out_levels:
            assert isinstance(level["distance"], Decimal)
            assert isinstance(level["price"], Decimal)
            pips_profit = level["distance"] * 10000
            print(f"    Level {level['level']}: Close {level['units']:,} units @ {level['price']:.5f} (+{pips_profit:.0f} pips)")

        # ==============================================================================
        # STEP 3: PLACE TAKE-PROFIT ORDERS AT EACH LEVEL
        # ==============================================================================

        print(f"\nPlacing {num_levels} take-profit limit orders...")

        placed_orders = []

        for level in scale_out_levels:
            level_price_val = level["price"]
            level_units_val = level["units"]
            level_num = level["level"]
            assert isinstance(level_price_val, Decimal)
            assert isinstance(level_units_val, int)
            assert isinstance(level_num, int)

            # ==============================================================================
            # SDK METHOD: client.orders.post_limit_order()
            # ==============================================================================
            #
            # Place a limit order to close portion of position at profit target
            #
            # Parameters:
            #   - account_id: Your OANDA account ID
            #   - instrument: Currency pair
            #   - units: Negative units to close long position
            #   - price: Take-profit price level
            #
            # Returns: OrderResponse with order creation details

            order_response = await client.orders.post_limit_order(
                account_id=client.account_id,
                instrument=instrument,
                units=-level_units_val,  # Negative to close portion of long position
                price=level_price_val,
            )

            assert order_response.order_create_transaction is not None
            order_id = order_response.order_create_transaction["id"]

            placed_orders.append({
                "level": level_num,
                "order_id": order_id,
                "price": level_price_val,
                "units": level_units_val,
            })

            print(f"  Level {level_num}: Order {order_id} to close {level_units_val:,} units @ {level_price_val:.5f}")

        print(f"\nAll {num_levels} take-profit orders active")

        # ==============================================================================
        # STEP 4: DEMONSTRATE PROFIT REALIZATION ANALYSIS
        # ==============================================================================

        print("\n" + "=" * 70)
        print("SCALE-OUT PROFIT REALIZATION ANALYSIS")
        print("=" * 70)

        print("\nAs price rises and hits targets, profits are locked in:")

        # Simulate different scenarios
        cumulative_realized = Decimal("0")
        remaining_units = position_size

        for level in scale_out_levels:
            level_price_calc = level["price"]
            level_units_calc = level["units"]
            level_num_calc = level["level"]
            level_distance = level["distance"]
            assert isinstance(level_price_calc, Decimal)
            assert isinstance(level_units_calc, int)
            assert isinstance(level_num_calc, int)
            assert isinstance(level_distance, Decimal)

            # Calculate profit from this level
            profit_this_level = level_distance * level_units_calc
            cumulative_realized += profit_this_level
            remaining_units -= level_units_calc

            print(f"\n  After Level {level_num_calc} hits ({level_price_calc:.5f}):")
            print(f"    Closed: {level_units_calc:,} units at +{level_distance * 10000:.0f} pips profit")
            print(f"    Realized profit this level: ${profit_this_level:.2f}")
            print(f"    Total realized profit: ${cumulative_realized:.2f}")
            print(f"    Remaining position: {remaining_units:,} units")

            # Show potential for remaining position
            if remaining_units > 0:
                print(f"    Remaining exposure: {remaining_units:,} units can capture additional gains")

        print(f"\n  Total potential profit if all levels hit: ${cumulative_realized:.2f}")

        # ==============================================================================
        # STEP 5: COMPARE TO ALL-OR-NOTHING EXIT
        # ==============================================================================

        print("\n" + "=" * 70)
        print("SCALE-OUT vs ALL-OR-NOTHING COMPARISON")
        print("=" * 70)

        # Compare scale-out to single exit at different levels
        single_exit_scenarios = [
            (Decimal("0.0020"), "Conservative (+20 pips)"),
            (Decimal("0.0040"), "Moderate (+40 pips)"),
            (Decimal("0.0080"), "Aggressive (+80 pips)"),
        ]

        print("\nIf using single exit instead of scale-out:")
        for exit_distance, description in single_exit_scenarios:
            single_exit_profit = exit_distance * position_size
            print(f"\n  {description}:")
            print(f"    All-or-nothing profit: ${single_exit_profit:.2f}")
            print(f"    Scale-out equivalent: Locked ${cumulative_realized:.2f} across levels")
            if single_exit_profit < cumulative_realized:
                print(f"    Advantage: Scale-out captures ${cumulative_realized - single_exit_profit:.2f} more")
            else:
                print(f"    Trade-off: Gave up ${single_exit_profit - cumulative_realized:.2f} for risk reduction")

        # ==============================================================================
        # PRODUCTION ENHANCEMENTS
        # ==============================================================================

        print("\n" + "=" * 70)
        print("PRODUCTION ENHANCEMENTS TO CONSIDER")
        print("=" * 70)
        print("\nTo make this strategy production-ready, add:")
        print("  • Monitor filled take-profit orders in real-time")
        print("  • Move stop-loss to breakeven after first target hits")
        print("  • Implement trailing stop on remaining position after partial exits")
        print("  • Adjust remaining targets based on volatility changes")
        print("  • Use different scaling ratios (e.g., 25%/25%/25%/25% or 20%/30%/30%/20%)")
        print("  • Cancel remaining orders if price reverses significantly")
        print("  • Track which target levels have best fill rates historically")
        print("  • Consider time-based exits for unfilled levels")


if __name__ == "__main__":
    # Run the scale-out strategy demonstration
    asyncio.run(main())
```

## Adaptive Position Management

Adaptive position management systems monitor market conditions in real-time and adjust order parameters dynamically to match current volatility, trend strength, and risk levels. Rather than using static rules, these systems calculate optimal position sizes, stop distances, and profit targets based on live market data like ATR (Average True Range), price momentum, and volatility metrics. This responsiveness ensures your trading system remains properly calibrated regardless of changing market regimes.

Using the SDK's pricing and order management endpoints together, you can build systems that fetch current market conditions with `client.pricing.get_pricing()`, calculate adaptive parameters, and update orders accordingly. The examples show complete implementations that adjust position sizing based on volatility, modify stop distances when market conditions change, and dynamically manage risk exposure as trends develop or deteriorate.

### Market Condition Adaptive System

Static trading parameters work well in stable conditions but fail when market regimes shift. A position size and stop distance optimized for tight spreads becomes dangerously aggressive during volatile periods, while conservative parameters leave profits on the table during calm markets. Adaptive systems solve this by continuously monitoring market conditions and adjusting strategy parameters in real-time to match the current environment.

The key is identifying meaningful market regime indicators. Bid-ask spread serves as an excellent proxy for liquidity and volatility - tight spreads indicate high liquidity and stable conditions, while wide spreads signal low liquidity or high volatility. By classifying regimes based on spread characteristics, you can dynamically adjust position sizing, stop distances, and profit targets to optimize for current conditions.

The following example demonstrates fetching real-time pricing, calculating bid-ask spreads, classifying market regimes (tight/normal/wide), and adapting position sizing and risk parameters accordingly:

<!-- filepath: example_market_adaptive_system.py -->
```python
import asyncio
from decimal import Decimal

from dotenv import load_dotenv

from fivetwenty import AsyncClient
from fivetwenty.models import InstrumentName

load_dotenv()

# ==============================================================================
# MARKET CONDITION ADAPTIVE SYSTEM
# ==============================================================================

# This example demonstrates adaptive position management based on market conditions:
#
# KEY CONCEPTS:
# 1. Market Regime Detection - Classify market conditions (tight/normal/wide spreads)
# 2. Dynamic Parameter Adjustment - Adapt position size, stops, and targets to conditions
# 3. Real-Time Analysis - Monitor spreads and volatility continuously
# 4. Responsive Strategy - Different parameters for different market regimes
#
# HOW IT WORKS:
# Analyze current market conditions by measuring bid-ask spreads. Classify the market
# into regimes (tight spreads = high liquidity, wide spreads = low liquidity/high volatility).
# Adjust position sizing, stop distances, and profit targets accordingly. Tight spreads
# enable aggressive strategies with larger positions and tighter stops. Wide spreads
# require defensive approaches with smaller positions and wider stops. The system
# continuously monitors and adapts as market conditions change.
#
# This code is fully executable and demonstrates adaptive management with OANDA.


async def analyze_market_conditions(client: AsyncClient, instrument: InstrumentName) -> dict[str, Decimal | str]:
    """
    Analyze current market conditions and return adaptive strategy parameters.

    Args:
        client: Authenticated AsyncClient
        instrument: Currency pair to analyze

    Returns:
        Dictionary of strategy parameters adapted to current market conditions
    """
    # Fetch current pricing to analyze market conditions
    pricing = await client.pricing.get_pricing(
        account_id=client.account_id,
        instruments=[instrument],
    )

    # Calculate bid-ask spread as primary market condition indicator
    current_bid = pricing["prices"][0].bids[0].price
    current_ask = pricing["prices"][0].asks[0].price
    current_spread = current_ask - current_bid

    print(f"  Current Bid: {current_bid:.5f}")
    print(f"  Current Ask: {current_ask:.5f}")
    print(f"  Spread: {current_spread:.5f} ({current_spread * 10000:.1f} pips)")

    # Classify market regime based on spread characteristics
    # Tight spreads = high liquidity, low volatility
    # Wide spreads = low liquidity, high volatility
    params: dict[str, Decimal | str]

    if current_spread < Decimal("0.0002"):  # Less than 0.2 pips
        regime = "tight"
        print("\n  REGIME: TIGHT SPREAD (High Liquidity)")
        print("  Market characteristics: Precise execution, low volatility")

        # Aggressive parameters for tight spread environment
        params = {
            "position_size_multiplier": Decimal("1.2"),  # 20% larger positions
            "stop_distance": Decimal("0.0015"),         # Tight 15 pip stops
            "take_profit_distance": Decimal("0.0025"),  # Close 25 pip targets
            "trail_distance": Decimal("0.0010"),        # Aggressive 10 pip trailing
        }

        print("  Strategy: Aggressive (taking advantage of low execution risk)")
        print(f"    Position sizing: +20% (multiplier: {params['position_size_multiplier']})")
        print(f"    Stop distance: {params['stop_distance'] * 10000:.0f} pips")
        print(f"    Profit target: {params['take_profit_distance'] * 10000:.0f} pips")
        print(f"    Trail distance: {params['trail_distance'] * 10000:.0f} pips")

    elif current_spread > Decimal("0.0005"):  # More than 0.5 pips
        regime = "wide"
        print("\n  REGIME: WIDE SPREAD (Low Liquidity / High Volatility)")
        print("  Market characteristics: Execution risk, high volatility")

        # Conservative parameters for wide spread environment
        params = {
            "position_size_multiplier": Decimal("0.7"),  # 30% smaller positions
            "stop_distance": Decimal("0.0040"),         # Wide 40 pip stops
            "take_profit_distance": Decimal("0.0060"),  # Distant 60 pip targets
            "trail_distance": Decimal("0.0030"),        # Loose 30 pip trailing
        }

        print("  Strategy: Defensive (reducing exposure due to execution risk)")
        print(f"    Position sizing: -30% (multiplier: {params['position_size_multiplier']})")
        print(f"    Stop distance: {params['stop_distance'] * 10000:.0f} pips")
        print(f"    Profit target: {params['take_profit_distance'] * 10000:.0f} pips")
        print(f"    Trail distance: {params['trail_distance'] * 10000:.0f} pips")

    else:  # Between 0.2 and 0.5 pips
        regime = "normal"
        print("\n  REGIME: NORMAL CONDITIONS (Standard Liquidity)")
        print("  Market characteristics: Balanced execution, moderate volatility")

        # Balanced parameters for normal market environment
        params = {
            "position_size_multiplier": Decimal("1.0"),  # Standard position sizing
            "stop_distance": Decimal("0.0025"),         # Standard 25 pip stops
            "take_profit_distance": Decimal("0.0040"),  # Standard 40 pip targets
            "trail_distance": Decimal("0.0020"),        # Standard 20 pip trailing
        }

        print("  Strategy: Balanced (using proven parameters)")
        print(f"    Position sizing: Baseline (multiplier: {params['position_size_multiplier']})")
        print(f"    Stop distance: {params['stop_distance'] * 10000:.0f} pips")
        print(f"    Profit target: {params['take_profit_distance'] * 10000:.0f} pips")
        print(f"    Trail distance: {params['trail_distance'] * 10000:.0f} pips")

    params["regime"] = regime
    return params


async def main() -> None:
    """Demonstrate market condition adaptive position management."""

    print("=" * 70)
    print("MARKET CONDITION ADAPTIVE SYSTEM")
    print("=" * 70)

    # ==============================================================================
    # CONNECT TO OANDA
    # ==============================================================================

    # AsyncClient automatically reads FIVETWENTY_OANDA_* environment variables
    # Context manager ensures proper cleanup of HTTP connections
    async with AsyncClient() as client:
        instrument = InstrumentName("EUR_USD")

        # ==============================================================================
        # STEP 1: ANALYZE CURRENT MARKET CONDITIONS
        # ==============================================================================

        print(f"\nAnalyzing market conditions for {instrument}...")

        strategy_params = await analyze_market_conditions(client, instrument)

        # ==============================================================================
        # STEP 2: CALCULATE POSITION SIZE BASED ON REGIME
        # ==============================================================================

        print("\n" + "=" * 70)
        print("ADAPTIVE POSITION SIZING")
        print("=" * 70)

        # Define base position size
        base_units = 10000  # Base position size

        # Apply regime-based multiplier
        multiplier = strategy_params["position_size_multiplier"]
        adapted_units = int(base_units * multiplier)

        print(f"\n  Base position size: {base_units:,} units")
        print(f"  Regime multiplier: {multiplier}")
        print(f"  Adapted position size: {adapted_units:,} units")

        # ==============================================================================
        # STEP 3: OPEN POSITION WITH ADAPTED SIZE
        # ==============================================================================

        print(f"\nOpening {instrument} position with adapted sizing...")

        market_order = await client.orders.post_market_order(
            account_id=client.account_id,
            instrument=instrument,
            units=adapted_units,
        )

        # Check if order filled successfully
        if market_order.get("order_fill_transaction") is None:
            print("\nOrder was not filled - market is likely closed")
            print("Forex market hours: Sunday 5 PM ET - Friday 5 PM ET")
            print("\nThis example demonstrates the adaptive logic and would")
            print("adjust position sizing based on market conditions when open.")
            return

        # Extract trade details
        assert market_order.order_fill_transaction.trade_opened is not None
        trade_id = market_order.order_fill_transaction.trade_opened.trade_id
        entry_price = market_order.order_fill_transaction.price
        assert entry_price is not None

        print("Position opened with adaptive parameters:")
        print(f"  Trade ID: {trade_id}")
        print(f"  Entry Price: {entry_price:.5f}")
        print(f"  Size: {adapted_units:,} units (adapted for {strategy_params['regime']} regime)")

        # ==============================================================================
        # STEP 4: CALCULATE ADAPTIVE STOP AND TARGET LEVELS
        # ==============================================================================

        print("\n" + "=" * 70)
        print("ADAPTIVE RISK MANAGEMENT LEVELS")
        print("=" * 70)

        stop_distance = strategy_params["stop_distance"]
        tp_distance = strategy_params["take_profit_distance"]
        assert isinstance(stop_distance, Decimal)
        assert isinstance(tp_distance, Decimal)

        stop_price = entry_price - stop_distance
        target_price = entry_price + tp_distance

        print(f"\n  Entry Price: {entry_price:.5f}")
        print(f"  Stop Distance: {stop_distance * 10000:.0f} pips (adapted for {strategy_params['regime']} regime)")
        print(f"  Stop Price: {stop_price:.5f}")
        print(f"  Take Profit Distance: {tp_distance * 10000:.0f} pips")
        print(f"  Target Price: {target_price:.5f}")

        # Calculate risk/reward ratio
        risk_reward = tp_distance / stop_distance
        print(f"  Risk/Reward Ratio: 1:{risk_reward:.2f}")

        # ==============================================================================
        # STEP 5: DEMONSTRATE REGIME COMPARISON
        # ==============================================================================

        print("\n" + "=" * 70)
        print("REGIME PARAMETER COMPARISON")
        print("=" * 70)

        print("\nHow parameters differ across market regimes:")

        regimes = [
            ("tight", Decimal("1.2"), Decimal("0.0015"), Decimal("0.0025")),
            ("normal", Decimal("1.0"), Decimal("0.0025"), Decimal("0.0040")),
            ("wide", Decimal("0.7"), Decimal("0.0040"), Decimal("0.0060")),
        ]

        for regime_name, pos_mult, stop_dist, tp_dist in regimes:
            position = int(base_units * pos_mult)
            print(f"\n  {regime_name.upper()} Regime:")
            print(f"    Position: {position:,} units ({pos_mult}x base)")
            print(f"    Stop: {stop_dist * 10000:.0f} pips")
            print(f"    Target: {tp_dist * 10000:.0f} pips")
            print(f"    R:R: 1:{(tp_dist / stop_dist):.2f}")

        # ==============================================================================
        # PRODUCTION ENHANCEMENTS
        # ==============================================================================

        print("\n" + "=" * 70)
        print("PRODUCTION ENHANCEMENTS TO CONSIDER")
        print("=" * 70)
        print("\nTo make this strategy production-ready, add:")
        print("  • Monitor market conditions continuously and adjust active positions")
        print("  • Use multiple indicators (ATR, volatility, volume) for regime detection")
        print("  • Implement regime change alerts and position adjustment logic")
        print("  • Track regime persistence and avoid over-adjusting to noise")
        print("  • Add time-of-day and session-based regime adjustments")
        print("  • Backtest regime parameters across historical market conditions")
        print("  • Implement gradual parameter transitions during regime changes")
        print("  • Add risk limits that adapt to account equity and drawdown")


if __name__ == "__main__":
    # Run the market condition adaptive system demonstration
    asyncio.run(main())
```

### Dynamic Risk Adjustment

Fixed position sizing ignores the fact that your risk tolerance should adapt to your actual trading performance. Risking 2% per trade makes sense during winning streaks when confidence is high and the account is growing, but becomes reckless during drawdowns when capital preservation matters most. Dynamic risk adjustment solves this by continuously monitoring account performance and scaling risk exposure up during good periods and down during poor ones.

The system tracks performance indicators like win rate and drawdown percentage. During strong performance (high win rate, low drawdown), the risk budget increases slightly. During poor performance (low win rate or significant drawdown), risk drops sharply to protect remaining capital. The damping effect limits catastrophic losses while letting profitable strategies compound.

The following example demonstrates fetching account details, calculating performance-based risk budgets, dynamically sizing positions based on adjusted risk, and comparing position sizes across different performance scenarios:

<!-- filepath: example_dynamic_risk_adjustment.py -->
```python
import asyncio
from decimal import Decimal

from dotenv import load_dotenv

from fivetwenty import AsyncClient
from fivetwenty.models import InstrumentName

load_dotenv()

# ==============================================================================
# DYNAMIC RISK ADJUSTMENT SYSTEM
# ==============================================================================

# This example demonstrates dynamic risk management based on account performance:
#
# KEY CONCEPTS:
# 1. Performance-Based Risk - Adjust risk exposure based on recent trading results
# 2. Dynamic Position Sizing - Scale positions based on account equity and performance
# 3. Risk Budget Management - Adapt risk percentage based on win rate and drawdown
# 4. Protective Scaling - Reduce risk during drawdowns, increase during winning streaks
#
# HOW IT WORKS:
# Monitor account performance metrics (balance, equity, unrealized P/L). Analyze
# recent trading performance (simulated here, real implementation would track actual
# trade history). Adjust risk budget based on performance - increase risk slightly
# during good performance (>70% win rate, <2% drawdown), reduce risk during poor
# performance (<50% win rate or >5% drawdown). Calculate position sizes based on
# the dynamic risk budget to ensure consistent risk management.
#
# This code is fully executable and demonstrates dynamic risk adjustment with OANDA.


async def calculate_risk_budget(
    client: AsyncClient, base_risk_pct: Decimal
) -> tuple[Decimal, Decimal]:
    """
    Calculate dynamic risk budget based on account performance.

    Args:
        client: Authenticated AsyncClient
        base_risk_pct: Base risk percentage per trade (e.g., 0.02 for 2%)

    Returns:
        Tuple of (adjusted_risk_pct, risk_multiplier)
    """
    # Fetch account details
    account = await client.accounts.get_account(
        account_id=client.account_id,
    )

    current_balance = Decimal(str(account["account"].balance))
    unrealized_pl = Decimal(str(account["account"].unrealized_pl))

    print(f"  Account Balance: ${current_balance:.2f}")
    print(f"  Unrealized P/L: ${unrealized_pl:.2f}")

    # Simulate performance analysis
    # In production, track actual trade history
    recent_win_rate = Decimal("0.65")  # 65% win rate (simulated)
    recent_drawdown = abs(unrealized_pl) / current_balance if current_balance > 0 else Decimal("0")

    print(f"  Recent Win Rate: {recent_win_rate * 100:.0f}% (simulated)")
    print(f"  Current Drawdown: {recent_drawdown * 100:.2f}%")

    # Classify performance and adjust risk
    if recent_win_rate > Decimal("0.70") and recent_drawdown < Decimal("0.02"):
        # Good performance: increase risk slightly
        risk_multiplier = Decimal("1.2")
        performance_status = "EXCELLENT"
        print(f"\n  Performance: {performance_status}")
        print("  Action: Increasing risk budget by 20%")

    elif recent_win_rate < Decimal("0.50") or recent_drawdown > Decimal("0.05"):
        # Poor performance: reduce risk
        risk_multiplier = Decimal("0.7")
        performance_status = "POOR"
        print(f"\n  Performance: {performance_status}")
        print("  Action: Reducing risk budget by 30%")

    else:
        # Normal performance: standard risk
        risk_multiplier = Decimal("1.0")
        performance_status = "NORMAL"
        print(f"\n  Performance: {performance_status}")
        print("  Action: Maintaining baseline risk budget")

    adjusted_risk = base_risk_pct * risk_multiplier

    return adjusted_risk, risk_multiplier


async def calculate_position_size(
    current_price: Decimal,
    stop_price: Decimal,
    account_balance: Decimal,
    risk_per_trade: Decimal,
) -> int:
    """
    Calculate position size based on dynamic risk budget.

    Args:
        current_price: Entry price
        stop_price: Stop loss price
        account_balance: Current account balance
        risk_per_trade: Risk percentage per trade

    Returns:
        Position size in units
    """
    # Calculate risk amount in dollars
    risk_amount = account_balance * risk_per_trade

    # Calculate stop distance
    stop_distance = abs(current_price - stop_price)

    # Calculate position size
    # For EUR/USD: 1 pip = $0.0001, and pip value = $1 per 10,000 units
    # Position size = Risk amount / (stop distance in pips × pip value)
    pip_value = Decimal("1.0")  # $1 per pip for 10,000 units
    position_size_in_10k = risk_amount / (stop_distance * 10000 * pip_value)
    position_size = int(position_size_in_10k * 10000)

    # Cap position size at reasonable limits
    max_position = 100000  # 10 standard lots maximum
    position_size = min(position_size, max_position)

    return position_size


async def main() -> None:
    """Demonstrate dynamic risk adjustment based on account performance."""

    print("=" * 70)
    print("DYNAMIC RISK ADJUSTMENT SYSTEM")
    print("=" * 70)

    # ==============================================================================
    # CONNECT TO OANDA
    # ==============================================================================

    # AsyncClient automatically reads FIVETWENTY_OANDA_* environment variables
    # Context manager ensures proper cleanup of HTTP connections
    async with AsyncClient() as client:
        instrument = InstrumentName("EUR_USD")

        # ==============================================================================
        # STEP 1: ANALYZE ACCOUNT PERFORMANCE AND CALCULATE RISK BUDGET
        # ==============================================================================

        print("\nAnalyzing account performance...")

        base_risk_pct = Decimal("0.02")  # 2% base risk per trade
        print(f"  Base Risk Per Trade: {base_risk_pct * 100:.0f}%")

        adjusted_risk, risk_multiplier = await calculate_risk_budget(
            client, base_risk_pct
        )

        print(f"\n  Adjusted Risk Per Trade: {adjusted_risk * 100:.2f}%")
        print(f"  Risk Multiplier: {risk_multiplier}x")

        # ==============================================================================
        # STEP 2: GET CURRENT MARKET PRICE
        # ==============================================================================

        print(f"\nFetching current {instrument} price...")

        pricing = await client.pricing.get_pricing(
            account_id=client.account_id,
            instruments=[instrument],
        )

        current_price = pricing["prices"][0].asks[0].price
        print(f"  Current Price: {current_price:.5f}")

        # ==============================================================================
        # STEP 3: CALCULATE DYNAMIC POSITION SIZE
        # ==============================================================================

        print("\n" + "=" * 70)
        print("DYNAMIC POSITION SIZING")
        print("=" * 70)

        # Define stop loss distance
        stop_distance = Decimal("0.0025")  # 25 pips
        stop_price = current_price - stop_distance

        print(f"\n  Entry Price: {current_price:.5f}")
        print(f"  Stop Distance: {stop_distance * 10000:.0f} pips")
        print(f"  Stop Price: {stop_price:.5f}")

        # Get account balance for position sizing
        account = await client.accounts.get_account(
            account_id=client.account_id,
        )
        account_balance = Decimal(str(account["account"].balance))

        # Calculate position size based on dynamic risk
        position_size = await calculate_position_size(
            current_price, stop_price, account_balance, adjusted_risk
        )

        print(f"\n  Account Balance: ${account_balance:.2f}")
        print(f"  Risk Per Trade: {adjusted_risk * 100:.2f}% (${account_balance * adjusted_risk:.2f})")
        print(f"  Calculated Position Size: {position_size:,} units")

        # ==============================================================================
        # STEP 4: DEMONSTRATE RISK SCENARIOS
        # ==============================================================================

        print("\n" + "=" * 70)
        print("RISK ADJUSTMENT SCENARIOS")
        print("=" * 70)

        scenarios = [
            (
                Decimal("0.75"),
                Decimal("0.01"),
                "Excellent Performance",
                "Win rate: 75%, Drawdown: 1%",
            ),
            (
                Decimal("0.60"),
                Decimal("0.03"),
                "Normal Performance",
                "Win rate: 60%, Drawdown: 3%",
            ),
            (
                Decimal("0.45"),
                Decimal("0.06"),
                "Poor Performance",
                "Win rate: 45%, Drawdown: 6%",
            ),
        ]

        for win_rate, drawdown, status, description in scenarios:
            # Determine risk multiplier for scenario
            if win_rate > Decimal("0.70") and drawdown < Decimal("0.02"):
                multiplier = Decimal("1.2")
            elif win_rate < Decimal("0.50") or drawdown > Decimal("0.05"):
                multiplier = Decimal("0.7")
            else:
                multiplier = Decimal("1.0")

            scenario_risk = base_risk_pct * multiplier
            scenario_position = await calculate_position_size(
                current_price, stop_price, account_balance, scenario_risk
            )

            print(f"\n  {status}:")
            print(f"    {description}")
            print(f"    Risk Multiplier: {multiplier}x")
            print(f"    Adjusted Risk: {scenario_risk * 100:.2f}%")
            print(f"    Position Size: {scenario_position:,} units")

        # ==============================================================================
        # STEP 5: OPEN POSITION WITH DYNAMIC SIZING
        # ==============================================================================

        print("\n" + "=" * 70)
        print("OPENING POSITION WITH DYNAMIC SIZING")
        print("=" * 70)

        print(f"\nOpening {instrument} position with dynamically sized units...")
        print(f"  Position Size: {position_size:,} units (risk-adjusted)")

        market_order = await client.orders.post_market_order(
            account_id=client.account_id,
            instrument=instrument,
            units=position_size,
        )

        # Check if order filled successfully
        if market_order.get("order_fill_transaction") is None:
            print("\nOrder was not filled - market is likely closed")
            print("Forex market hours: Sunday 5 PM ET - Friday 5 PM ET")
            print("\nThis example demonstrates the dynamic sizing logic and would")
            print("adjust position sizes based on account performance when open.")
            return

        # Extract trade details
        assert market_order.order_fill_transaction.trade_opened is not None
        trade_id = market_order.order_fill_transaction.trade_opened.trade_id
        entry_price = market_order.order_fill_transaction.price
        assert entry_price is not None

        print("\nPosition opened with dynamic risk management:")
        print(f"  Trade ID: {trade_id}")
        print(f"  Entry Price: {entry_price:.5f}")
        print(f"  Size: {position_size:,} units (performance-adjusted)")
        print(f"  Risk: {adjusted_risk * 100:.2f}% of account")

        # ==============================================================================
        # PRODUCTION ENHANCEMENTS
        # ==============================================================================

        print("\n" + "=" * 70)
        print("PRODUCTION ENHANCEMENTS TO CONSIDER")
        print("=" * 70)
        print("\nTo make this strategy production-ready, add:")
        print("  • Track actual trade history for real performance metrics")
        print("  • Implement rolling window for win rate calculation (e.g., last 20 trades)")
        print("  • Add maximum daily drawdown limits that pause trading")
        print("  • Implement gradual risk scaling (not step functions)")
        print("  • Track correlation between risk adjustments and subsequent performance")
        print("  • Add minimum sample size before adjusting risk (e.g., 10+ trades)")
        print("  • Implement separate risk budgets for different strategies")
        print("  • Add risk ceiling that limits maximum position size regardless of performance")


if __name__ == "__main__":
    # Run the dynamic risk adjustment demonstration
    asyncio.run(main())
```

## Next Steps

Continue building advanced order management capabilities:

- **[Order Strategies & Combinations](order-strategies.md)** - Bracket orders and advanced techniques
- **[Best Practices](../../guides/understanding/best-practices.md)** - Risk management and error handling

## Key Takeaways

1. **Trailing stops** protect profits while maintaining upside potential
2. **Position scaling** enables systematic risk and reward management
3. **Adaptive systems** respond to changing market conditions
4. **Dynamic risk management** adjusts to account performance and market regime
5. **Performance monitoring** enables continuous strategy improvement
6. **Modular design** supports flexible and maintainable trading systems

Next, continue to [Order Strategies & Combinations](order-strategies.md) to combine these techniques with bracket orders and coordinated entries.