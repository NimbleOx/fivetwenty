# Stop Orders & Market-If-Touched

Learn breakout and mean reversion strategies using stop orders and market-if-touched (MIT) orders for systematic trading approaches.

## Learning Objectives

By the end of this guide, you will:

- Implement breakout strategies with stop orders
- Design mean reversion systems with MIT orders
- Build momentum and reversal detection systems

## Stop Orders for Breakout Strategies

Stop orders capture breakout momentum when price breaks through support or resistance levels. Unlike limit orders that execute at or better than a specified price, stop orders become market orders when price reaches your trigger level, so they execute during momentum moves. That makes them a fit for trend-following and breakout strategies, where you want to enter as price confirms directional movement rather than trying to predict the breakout in advance.

Implementing stop order strategies with the FiveTwenty SDK involves using `client.orders.post_stop_order()` to place orders that trigger when price reaches your specified breakout levels. You'll learn how to identify key technical levels from chart analysis, calculate appropriate trigger prices with buffers to avoid false breakouts, and manage position sizing based on breakout significance. The SDK handles order placement, monitoring, and execution automatically, so you can focus on strategy logic.

The implementations below cover simple resistance/support breakouts, multi-timeframe confirmation systems, and volatility-adaptive strategies that adjust trigger levels based on current market conditions:

### Basic Breakout Implementation

```python
import asyncio
from decimal import Decimal

from dotenv import load_dotenv

from fivetwenty import AsyncClient
from fivetwenty.models import InstrumentName

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
# BASIC BREAKOUT IMPLEMENTATION WITH STOP ORDERS
# ==============================================================================

# This example demonstrates a fundamental breakout trading strategy using stop orders:
#
# KEY CONCEPTS:
# 1. Stop Orders - Trigger when price reaches a specified level, becoming market orders
# 2. Breakout Trading - Capture momentum when price breaks through support/resistance
# 3. Bidirectional Setup - Place orders both above resistance and below support
# 4. Technical Levels - Identify key price levels from chart analysis
#
# HOW IT WORKS:
# The strategy places two stop orders: a buy stop above resistance to capture bullish
# breakouts, and a sell stop below support to capture bearish breakouts. When price
# decisively breaks through either level, the corresponding stop order triggers and
# enters a position in the direction of the breakout, riding the momentum.
#
# This code is fully executable and demonstrates real SDK integration with OANDA.


async def main() -> None:
    """Implement basic breakout strategy using stop orders for momentum capture."""

    print("=" * 60)
    print("BASIC BREAKOUT STRATEGY WITH STOP ORDERS")
    print("=" * 60)

    # ==============================================================================
    # CONNECT TO OANDA
    # ==============================================================================

    # AsyncClient automatically reads FIVETWENTY_OANDA_* environment variables
    # Context manager ensures proper cleanup of HTTP connections
    async with AsyncClient() as client:
        # ==============================================================================
        # STEP 1: DEFINE KEY PRICE LEVELS
        # ==============================================================================

        # In practice, these levels would be identified through technical analysis
        # using chart patterns, previous highs/lows, or indicator signals
        resistance_level = Decimal("1.0900")  # EUR/USD resistance from chart analysis
        support_level = Decimal("1.0800")     # EUR/USD support from chart analysis

        print("\nBreakout Strategy Configuration:")
        print(f"  Resistance Level: {resistance_level:.5f}")
        print(f"  Support Level: {support_level:.5f}")
        print(f"  Range: {(resistance_level - support_level) * 10000:.0f} pips")

        # ==============================================================================
        # STEP 2: CALCULATE BREAKOUT TRIGGER PRICES
        # ==============================================================================

        # Add small buffer beyond key levels to confirm genuine breakout
        # This reduces false signals from brief price touches without follow-through
        breakout_buffer = Decimal("0.0005")  # 0.5 pip buffer for confirmation

        bullish_trigger = resistance_level + breakout_buffer  # Buy trigger
        bearish_trigger = support_level - breakout_buffer     # Sell trigger

        print(f"\nTrigger Levels (with {breakout_buffer * 10000:.1f} pip buffer):")
        print(f"  Bullish Breakout: {bullish_trigger:.5f}")
        print(f"  Bearish Breakout: {bearish_trigger:.5f}")

        # ==============================================================================
        # STEP 3: PLACE STOP ORDERS FOR BREAKOUT CAPTURE
        # ==============================================================================

        # ==============================================================================
        # SDK METHOD: client.orders.post_stop_order()
        # ==============================================================================
        #
        # Place a stop order that triggers when price reaches specified level
        #
        # Parameters:
        #   - account_id: Your OANDA account ID (available as client.account_id)
        #   - instrument: Currency pair to trade (InstrumentName enum)
        #   - units: Position size (positive=buy, negative=sell)
        #   - price: Trigger price level (Decimal)
        #   - time_in_force: Order lifetime ("GTC" = Good Till Cancelled)
        #
        # Returns: OrderResponse (Pydantic model) with order creation details
        #
        # NOTE: Stop orders become market orders when price reaches trigger level

        print("\nPlacing breakout stop orders...")

        # Buy stop above resistance (bullish breakout strategy)
        # Triggers when price breaks ABOVE resistance, indicating upward momentum
        buy_stop_response = await client.orders.post_stop_order(
            account_id=client.account_id,          # Use authenticated account
            instrument=InstrumentName("EUR_USD"),  # Currency pair (enum type)
            units=10000,                           # Long position (positive = buy)
            price=bullish_trigger,                 # Trigger above resistance
            time_in_force="GTC"                    # Stays active until triggered/cancelled
        )

        # Sell stop below support (bearish breakout strategy)
        # Triggers when price breaks BELOW support, indicating downward momentum
        sell_stop_response = await client.orders.post_stop_order(
            account_id=client.account_id,          # Use authenticated account
            instrument=InstrumentName("EUR_USD"),  # Currency pair (enum type)
            units=-10000,                          # Short position (negative = sell)
            price=bearish_trigger,                 # Trigger below support
            time_in_force="GTC"                    # Stays active until triggered/cancelled
        )

        # ==============================================================================
        # STEP 4: CONFIRM ORDER PLACEMENT AND DISPLAY STRATEGY
        # ==============================================================================

        # OrderResponse is a Pydantic model with order_create_transaction field
        # order_create_transaction is a dict with transaction details
        assert buy_stop_response.order_create_transaction is not None
        assert sell_stop_response.order_create_transaction is not None
        buy_stop_id = buy_stop_response.order_create_transaction["id"]
        sell_stop_id = sell_stop_response.order_create_transaction["id"]

        print("\n Breakout stops successfully placed:")
        print(f"  Buy Stop Order ID: {buy_stop_id}")
        print(f"    Trigger: {bullish_trigger:.5f} (bullish breakout)")
        print("    Size: 10,000 units")
        print(f"\n  Sell Stop Order ID: {sell_stop_id}")
        print(f"    Trigger: {bearish_trigger:.5f} (bearish breakout)")
        print("    Size: 10,000 units")

        print("\nStrategy Logic:")
        print("  • Buy stop captures upward breakouts above resistance")
        print("  • Sell stop captures downward breakouts below support")
        print("  • Orders remain active until triggered or manually cancelled")
        print(f"  • Momentum confirmed by {breakout_buffer * 10000:.1f} pip buffer")

        # ==============================================================================
        # PRODUCTION ENHANCEMENTS
        # ==============================================================================

        print("\n" + "=" * 60)
        print("PRODUCTION ENHANCEMENTS TO CONSIDER")
        print("=" * 60)
        print("\nTo make this strategy production-ready, add:")
        print("  • Stop loss orders to limit risk on each breakout trade")
        print("  • Take profit targets based on expected move distance")
        print("  • Dynamic level calculation from recent price action")
        print("  • Volatility-based position sizing (smaller in high vol)")
        print("  • Multi-timeframe confirmation before placing orders")
        print("  • Order monitoring to track fills and manage positions")
        print("  • Re-calculation of levels after breakouts occur")


if __name__ == "__main__":
    # Run the breakout strategy demonstration
    asyncio.run(main())
```

### Dynamic Breakout Levels

Adapt breakout levels based on market volatility. This example demonstrates real-time price fetching and volatility-adaptive trigger placement:

```python
import asyncio
from decimal import Decimal

from dotenv import load_dotenv

from fivetwenty import AsyncClient
from fivetwenty.models import InstrumentName

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
# DYNAMIC BREAKOUT LEVELS WITH VOLATILITY ADAPTATION
# ==============================================================================

# This example demonstrates adaptive breakout strategies that adjust to market volatility:
#
# KEY CONCEPTS:
# 1. ATR (Average True Range) - Measure of market volatility
# 2. Dynamic Levels - Breakout triggers adjust based on current volatility
# 3. Volatility-Based Positioning - Wider levels in high volatility markets
# 4. Real-time Price Integration - Calculate levels from current market price
#
# HOW IT WORKS:
# Instead of fixed breakout levels, this strategy calculates trigger prices as a
# percentage of ATR from the current market price. In high volatility markets, the
# breakout levels are wider (avoiding false signals), while in low volatility they're
# tighter (capturing smaller moves). This adaptive approach improves signal quality
# across different market conditions.
#
# This code is fully executable and demonstrates real-time price fetching with SDK.


async def main() -> None:
    """Calculate adaptive breakout levels based on current market volatility."""

    print("=" * 60)
    print("DYNAMIC BREAKOUT LEVELS - VOLATILITY ADAPTIVE")
    print("=" * 60)

    # ==============================================================================
    # CONNECT TO OANDA
    # ==============================================================================

    # AsyncClient automatically reads FIVETWENTY_OANDA_* environment variables
    # Context manager ensures proper cleanup of HTTP connections
    async with AsyncClient() as client:
        # ==============================================================================
        # STEP 1: SET UP VOLATILITY MEASUREMENT PARAMETERS
        # ==============================================================================

        # ATR (Average True Range) measures recent price volatility
        # In production, you would calculate this from historical candle data
        atr_period = 14                      # Standard 14-period ATR
        current_atr = Decimal("0.0045")      # Example: 4.5 pip daily volatility

        print("\nVolatility Analysis:")
        print(f"  ATR Period: {atr_period}")
        print(f"  Current ATR: {current_atr * 10000:.1f} pips")
        print(f"  Interpretation: {'High' if current_atr > Decimal('0.004') else 'Normal'} volatility")

        # ==============================================================================
        # STEP 2: GET CURRENT MARKET PRICE
        # ==============================================================================

        # ==============================================================================
        # SDK METHOD: client.pricing.get_pricing()
        # ==============================================================================
        #
        # Get current market pricing to calculate dynamic levels
        #
        # Parameters:
        #   - account_id: Your OANDA account ID (available as client.account_id)
        #   - instruments: List of instruments to get pricing for
        #
        # Returns: TypedDict with structure:
        #   {
        #       "prices": list[ClientPrice],  # Pydantic models
        #       "time": datetime
        #   }
        #
        # NOTE: Response is TypedDict (use dictionary access: response["prices"])
        #       Each ClientPrice is a Pydantic model (use attribute access: price.asks)

        pricing = await client.pricing.get_pricing(
            account_id=client.account_id,
            instruments=["EUR_USD"]
        )

        # Extract current price from response
        # Use ask price as current market level for buy-side calculations
        current_price = Decimal(pricing["prices"][0].asks[0].price)

        print("\nCurrent Market Price:")
        print(f"  EUR/USD: {current_price:.5f}")

        # ==============================================================================
        # STEP 3: CALCULATE ADAPTIVE BREAKOUT LEVELS
        # ==============================================================================

        # Use percentage of ATR to set breakout distance from current price
        # 50% of ATR creates responsive levels that adapt to volatility
        atr_multiplier = Decimal("0.5")  # 50% of ATR
        breakout_buffer = current_atr * atr_multiplier

        # Dynamic levels adjust automatically to market conditions
        upper_breakout = current_price + breakout_buffer  # Bullish breakout level
        lower_breakout = current_price - breakout_buffer  # Bearish breakout level

        print("\nDynamic Breakout Calculation:")
        print(f"  ATR Multiplier: {atr_multiplier * 100:.0f}%")
        print(f"  Breakout Buffer: {breakout_buffer * 10000:.1f} pips")
        print(f"  Upper Level: {upper_breakout:.5f} (+{breakout_buffer * 10000:.1f} pips)")
        print(f"  Lower Level: {lower_breakout:.5f} (-{breakout_buffer * 10000:.1f} pips)")
        print(f"  Total Range: {(upper_breakout - lower_breakout) * 10000:.0f} pips")

        # ==============================================================================
        # STEP 4: PLACE VOLATILITY-ADAPTIVE STOP ORDERS
        # ==============================================================================

        # Order sizes can be adjusted based on volatility (higher vol = smaller size)
        # This maintains consistent risk across different market conditions
        base_position_size = 15000

        # Optional: Reduce position size in high volatility
        if current_atr > Decimal("0.005"):  # High volatility threshold (5 pips)
            position_size = int(base_position_size * 0.7)  # Reduce to 70%
            print(f"\n⚠ High volatility detected - reducing position size to {position_size:,} units")
        else:
            position_size = base_position_size

        print("\nPlacing volatility-adaptive stop orders...")

        # Bullish breakout order (triggers on upward momentum)
        buy_stop = await client.orders.post_stop_order(
            account_id=client.account_id,
            instrument=InstrumentName("EUR_USD"),
            units=position_size,
            price=upper_breakout,
            time_in_force="GTC"
        )

        # Bearish breakout order (triggers on downward momentum)
        sell_stop = await client.orders.post_stop_order(
            account_id=client.account_id,
            instrument=InstrumentName("EUR_USD"),
            units=-position_size,
            price=lower_breakout,
            time_in_force="GTC"
        )

        # ==============================================================================
        # STEP 5: CONFIRM ADAPTIVE STRATEGY DEPLOYMENT
        # ==============================================================================

        assert buy_stop.order_create_transaction is not None
        assert sell_stop.order_create_transaction is not None
        buy_id = buy_stop.order_create_transaction["id"]
        sell_id = sell_stop.order_create_transaction["id"]

        print("\n Dynamic breakout orders placed:")
        print(f"  Buy Stop ID: {buy_id}")
        print(f"    Trigger: {upper_breakout:.5f}")
        print(f"    Size: {position_size:,} units")
        print(f"\n  Sell Stop ID: {sell_id}")
        print(f"    Trigger: {lower_breakout:.5f}")
        print(f"    Size: {position_size:,} units")

        print("\nAdaptive Strategy Advantages:")
        print("  • Levels automatically adjust to current volatility")
        print("  • Wider triggers in volatile markets reduce false signals")
        print("  • Tighter triggers in calm markets capture smaller moves")
        print("  • Position sizing scales with volatility for risk control")

        # ==============================================================================
        # PRODUCTION ENHANCEMENTS
        # ==============================================================================

        print("\n" + "=" * 60)
        print("PRODUCTION ENHANCEMENTS TO CONSIDER")
        print("=" * 60)
        print("\nTo make this strategy production-ready, add:")
        print("  • Calculate actual ATR from historical candle data")
        print("  • Update levels periodically as volatility changes")
        print("  • Combine with trend filters (moving averages, ADX)")
        print("  • Add time-based filters to avoid low-liquidity periods")
        print("  • Implement order replacement when levels need updating")
        print("  • Track fill rates across different volatility regimes")
        print("  • Backtest optimal ATR multiplier for your timeframe")


if __name__ == "__main__":
    # Run the dynamic breakout strategy demonstration
    asyncio.run(main())
```

### Multi-Timeframe Breakout System

Combine signals from multiple timeframes to filter out weak breakouts. This example demonstrates class-based strategy organization with timeframe-weighted position sizing:

```python
import asyncio
from decimal import Decimal

from dotenv import load_dotenv

from fivetwenty import AsyncClient
from fivetwenty.models import InstrumentName

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
# MULTI-TIMEFRAME BREAKOUT SYSTEM
# ==============================================================================

# This example demonstrates a sophisticated multi-timeframe breakout strategy:
#
# KEY CONCEPTS:
# 1. Multi-Timeframe Analysis - Identify key levels across different time horizons
# 2. Timeframe-Weighted Sizing - Larger positions for higher timeframe breakouts
# 3. Layered Order Placement - Multiple stop orders at different significance levels
# 4. Signal Confirmation - Higher timeframes provide stronger trend signals
#
# HOW IT WORKS:
# The system analyzes breakout levels on three timeframes (15min, 1hour, 4hour),
# with each timeframe revealing different market structure. Orders are placed at
# each timeframe's key levels with position sizes weighted by timeframe significance.
# This captures both short-term intraday momentum and longer-term structural breaks,
# while reducing false signals through multi-timeframe confirmation.
#
# This code is fully executable and demonstrates class-based strategy organization.


# ==============================================================================
# MULTI-TIMEFRAME BREAKOUT STRATEGY CLASS
# ==============================================================================


class MultiTimeframeBreakout:
    """
    Multi-timeframe breakout system for robust signal confirmation.

    This class manages breakout analysis across multiple timeframes and places
    layered stop orders with position sizing based on timeframe significance.
    """

    def __init__(self, client: AsyncClient, account_id: str) -> None:
        """
        Initialize multi-timeframe analysis framework.

        Args:
            client: Authenticated AsyncClient for order execution
            account_id: Account ID for trading operations

        """
        self.client = client
        self.account_id = account_id
        self.active_stops: list[str] = []  # Track all placed stop order IDs

        print("Initializing multi-timeframe breakout system")
        print("Strategy: Align breakout signals across multiple time horizons")

    async def analyze_breakout_levels(
        self, instrument: str
    ) -> dict[str, dict[str, Decimal | str]]:
        """
        Analyze breakout levels across multiple timeframes.

        In production, these levels would be calculated from historical candle data
        using technical analysis. Different timeframes reveal different market structure.

        Args:
            instrument: Currency pair to analyze

        Returns:
            Dictionary mapping timeframes to their breakout levels and metadata

        """
        print(f"\nAnalyzing {instrument} breakout levels across timeframes:")

        # ==============================================================================
        # MULTI-TIMEFRAME LEVEL DEFINITION
        # ==============================================================================

        # Each timeframe provides different significance levels
        # In production, calculate these from historical price data
        # These levels assume current price around 1.1740
        breakout_levels: dict[str, dict[str, Decimal | str]] = {
            "15min": {
                "resistance": Decimal("1.1750"),        # Recent high resistance (10 pips away)
                "support": Decimal("1.1730"),           # Recent low support (10 pips away)
                "significance": "Intraday momentum",    # Level importance
            },
            "1hour": {
                "resistance": Decimal("1.1760"),        # Hourly trend resistance (20 pips away)
                "support": Decimal("1.1720"),           # Hourly trend support (20 pips away)
                "significance": "Short-term trend",     # Level importance
            },
            "4hour": {
                "resistance": Decimal("1.1780"),        # Major structural high (40 pips away)
                "support": Decimal("1.1700"),           # Major structural low (40 pips away)
                "significance": "Major trend structure",  # Level importance
            },
        }

        # Display multi-timeframe analysis
        for timeframe, levels in breakout_levels.items():
            resistance = levels["resistance"]
            support = levels["support"]
            if not isinstance(resistance, Decimal) or not isinstance(support, Decimal):
                msg = f"Expected Decimal types for resistance and support in {timeframe}"
                raise TypeError(msg)

            range_pips = (resistance - support) * 10000
            print(f"  {timeframe}: {support:.5f} - {resistance:.5f} ({range_pips:.0f} pips)")
            print(f"    Significance: {levels['significance']}")

        return breakout_levels

    async def place_layered_breakout_stops(
        self, instrument: InstrumentName
    ) -> list[str]:
        """
        Place layered stop orders across multiple timeframes.

        Position sizes are weighted by timeframe significance - higher timeframes
        get larger allocations because their signals have stronger follow-through.

        Args:
            instrument: Currency pair to trade

        Returns:
            List of order IDs for all placed stop orders

        """
        # ==============================================================================
        # STEP 1: GET MULTI-TIMEFRAME BREAKOUT ANALYSIS
        # ==============================================================================

        levels = await self.analyze_breakout_levels(instrument.value)

        # ==============================================================================
        # STEP 2: DEFINE TIMEFRAME-WEIGHTED POSITION SIZING
        # ==============================================================================

        # Longer timeframes get larger allocations due to higher significance
        # These weights reflect the reliability and expected move size
        timeframe_weights = {
            "15min": 0.3,  # 30% allocation - short-term signals
            "1hour": 0.5,  # 50% allocation - medium-term signals
            "4hour": 0.7,  # 70% allocation - long-term signals
        }

        print("\nPlacing layered breakout stops with timeframe-weighted sizing:")

        # ==============================================================================
        # STEP 3: PLACE STOPS AT EACH TIMEFRAME LEVEL
        # ==============================================================================

        for timeframe, level_data in levels.items():
            weight = timeframe_weights[timeframe]
            base_units = 10000  # Base position size
            scaled_units = int(base_units * weight)  # Scale by timeframe importance

            print(f"\n{timeframe} timeframe ({level_data['significance']}):")
            print(f"  Position allocation: {weight * 100:.0f}% = {scaled_units:,} units")

            # Calculate breakout trigger prices with small buffer
            breakout_buffer = Decimal("0.0005")  # 0.5 pip buffer beyond key levels

            resistance = level_data["resistance"]
            support = level_data["support"]
            if not isinstance(resistance, Decimal) or not isinstance(support, Decimal):
                msg = f"Expected Decimal types for resistance and support in {timeframe}"
                raise TypeError(msg)

            buy_trigger = resistance + breakout_buffer   # Bullish breakout
            sell_trigger = support - breakout_buffer     # Bearish breakout

            # ==============================================================================
            # PLACE TIMEFRAME-SPECIFIC STOP ORDERS
            # ==============================================================================

            # Bullish breakout stop (long position trigger)
            buy_stop = await self.client.orders.post_stop_order(
                account_id=self.account_id,
                instrument=instrument,
                units=scaled_units,
                price=buy_trigger,
                time_in_force="GTC",
            )

            # Bearish breakout stop (short position trigger)
            sell_stop = await self.client.orders.post_stop_order(
                account_id=self.account_id,
                instrument=instrument,
                units=-scaled_units,
                price=sell_trigger,
                time_in_force="GTC",
            )

            # ==============================================================================
            # TRACK ORDERS AND CONFIRM PLACEMENT
            # ==============================================================================

            # Extract order IDs from responses
            if buy_stop.get("orderCreateTransaction") is None or sell_stop.get("orderCreateTransaction") is None:
                msg = "Order creation transaction missing from response"
                raise ValueError(msg)
            buy_id = buy_stop["orderCreateTransaction"].id
            sell_id = sell_stop["orderCreateTransaction"].id

            self.active_stops.extend([buy_id, sell_id])

            print(f"   Stops placed: {scaled_units:,} units each direction")
            print(f"    Buy trigger: {buy_trigger:.5f} (Order ID: {buy_id})")
            print(f"    Sell trigger: {sell_trigger:.5f} (Order ID: {sell_id})")

        # ==============================================================================
        # DISPLAY MULTI-TIMEFRAME STRATEGY ADVANTAGES
        # ==============================================================================

        print("\nMulti-timeframe strategy advantages:")
        print("  • Higher timeframe breaks have stronger follow-through")
        print("  • Position sizing reflects signal strength and duration")
        print("  • Captures both intraday momentum and longer-term moves")
        print("  • Reduces false signals through timeframe confirmation")
        print(f"\nTotal orders placed: {len(self.active_stops)}")

        return self.active_stops


# ==============================================================================
# DEMONSTRATION MAIN FUNCTION
# ==============================================================================


async def main() -> None:
    """Demonstrate multi-timeframe breakout system with real SDK integration."""

    print("=" * 60)
    print("MULTI-TIMEFRAME BREAKOUT SYSTEM DEMONSTRATION")
    print("=" * 60)

    # ==============================================================================
    # CONNECT TO OANDA
    # ==============================================================================

    # AsyncClient automatically reads FIVETWENTY_OANDA_* environment variables
    # Context manager ensures proper cleanup of HTTP connections
    async with AsyncClient() as client:
        # ==============================================================================
        # CREATE AND EXECUTE MULTI-TIMEFRAME STRATEGY
        # ==============================================================================

        # Initialize the multi-timeframe breakout system
        strategy = MultiTimeframeBreakout(
            client=client,
            account_id=client.account_id
        )

        # Place layered breakout stops across all timeframes
        order_ids = await strategy.place_layered_breakout_stops(
            instrument=InstrumentName("EUR_USD")
        )

        # ==============================================================================
        # DISPLAY FINAL STRATEGY SUMMARY
        # ==============================================================================

        print("\n" + "=" * 60)
        print("STRATEGY DEPLOYMENT SUMMARY")
        print("=" * 60)
        print("\nInstrument: EUR/USD")
        print("Timeframes analyzed: 3 (15min, 1hour, 4hour)")
        print(f"Total orders placed: {len(order_ids)}")
        print("Order management: All orders active until triggered or cancelled")

        # ==============================================================================
        # PRODUCTION ENHANCEMENTS
        # ==============================================================================

        print("\n" + "=" * 60)
        print("PRODUCTION ENHANCEMENTS TO CONSIDER")
        print("=" * 60)
        print("\nTo make this strategy production-ready, add:")
        print("  • Calculate actual levels from historical candle data")
        print("  • Add timeframe confirmation (only trade when multiple align)")
        print("  • Implement order cancellation when lower timeframe triggers")
        print("  • Add stop loss and take profit to each breakout order")
        print("  • Monitor fill rates and adjust timeframe weights accordingly")
        print("  • Implement order replacement when levels change significantly")
        print("  • Add trend filters to avoid counter-trend breakouts")
        print("  • Track correlation between timeframe signals and outcomes")


if __name__ == "__main__":
    # Run the multi-timeframe breakout demonstration
    asyncio.run(main())
```

## MIT Orders for Mean Reversion

Market-If-Touched (MIT) orders suit mean reversion strategies, where you expect price to return toward its average after reaching extreme levels. Unlike stop orders that chase momentum, MIT orders become market orders when price touches your specified level from the opposite direction, which lets you fade extremes. When price stretches too far from its mean (measured by moving averages, Bollinger Bands, or statistical indicators), MIT orders enter counter-trend positions automatically.

The FiveTwenty SDK's `client.orders.post_market_if_touched_order()` method places orders at calculated extreme levels. You'll identify overbought and oversold conditions using technical indicators, determine entry points, and size positions for counter-trend trading. The SDK manages order placement and execution, so entries trigger at your predefined extremes without constant monitoring.

Building effective mean reversion systems requires understanding when markets are likely to revert versus trend. The examples demonstrate practical implementations using Bollinger Bands for statistical extremes, RSI for momentum exhaustion signals, and intelligent filtering to avoid counter-trend trading during strong directional moves:

### Basic Mean Reversion Setup

```python
import asyncio
from decimal import Decimal

from dotenv import load_dotenv

from fivetwenty import AsyncClient
from fivetwenty.models import InstrumentName

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
# BASIC MEAN REVERSION WITH MIT ORDERS
# ==============================================================================

# This example demonstrates mean reversion trading using MIT (Market-If-Touched) orders:
#
# KEY CONCEPTS:
# 1. Mean Reversion - Price tendency to return to average after extremes
# 2. MIT Orders - Trigger when price touches level, becoming market orders
# 3. Counter-Trend Trading - Fade extremes rather than chase momentum
# 4. Statistical Extremes - Identify overbought/oversold conditions
#
# HOW IT WORKS:
# The strategy places MIT orders at calculated distances from the mean price
# (moving average). When price reaches extreme levels (upper/lower bounds), the
# MIT order triggers and enters a position expecting price to revert back toward
# the mean. Unlike stop orders that chase breakouts, MIT orders fade extremes.
#
# This code is fully executable and demonstrates MIT order placement with SDK.


async def main() -> None:
    """Implement mean reversion strategy using MIT orders to fade extreme moves."""

    print("=" * 60)
    print("BASIC MEAN REVERSION STRATEGY WITH MIT ORDERS")
    print("=" * 60)

    # ==============================================================================
    # CONNECT TO OANDA
    # ==============================================================================

    # AsyncClient automatically reads FIVETWENTY_OANDA_* environment variables
    # Context manager ensures proper cleanup of HTTP connections
    async with AsyncClient() as client:
        # ==============================================================================
        # STEP 1: DEFINE MEAN REVERSION PARAMETERS
        # ==============================================================================

        # Mean reversion assumes price will return to average after extreme moves
        # In production, calculate mean_price from historical data (e.g., 20 SMA)
        mean_price = Decimal("1.1740")           # 20-period moving average (fair value)
        reversion_distance = Decimal("0.0030")   # 30 pips from mean (extreme threshold)

        # Calculate reversion trigger levels
        upper_reversion = mean_price + reversion_distance  # Overbought level (1.1770)
        lower_reversion = mean_price - reversion_distance  # Oversold level (1.1710)

        print("\nMean Reversion Configuration:")
        print(f"  Mean Price (20 SMA): {mean_price:.5f}")
        print(f"  Reversion Distance: ±{reversion_distance * 10000:.0f} pips")
        print(f"  Upper Extreme: {upper_reversion:.5f} (30 pips above mean)")
        print(f"  Lower Extreme: {lower_reversion:.5f} (30 pips below mean)")

        # ==============================================================================
        # STEP 2: PLACE MIT ORDERS FOR MEAN REVERSION ENTRIES
        # ==============================================================================

        # ==============================================================================
        # SDK METHOD: client.orders.post_market_if_touched_order()
        # ==============================================================================
        #
        # Place a Market-If-Touched order that triggers when price reaches level
        #
        # Parameters:
        #   - account_id: Your OANDA account ID (available as client.account_id)
        #   - instrument: Currency pair to trade (InstrumentName enum)
        #   - units: Position size (positive=buy, negative=sell)
        #   - price: Trigger price level (Decimal)
        #   - time_in_force: Order lifetime ("GTC" = Good Till Cancelled)
        #
        # Returns: OrderResponse (Pydantic model) with order creation details
        #
        # NOTE: MIT orders become market orders when price touches the trigger level
        #       Unlike stop orders, MIT orders are for mean reversion (counter-trend)

        print("\nPlacing MIT orders for mean reversion...")

        # Sell MIT when price reaches upper extreme (expecting reversion down)
        # Logic: Price too high relative to mean, expect downward correction
        sell_mit_response = await client.orders.post_market_if_touched_order(
            account_id=client.account_id,
            instrument=InstrumentName("EUR_USD"),
            units=-10000,                  # Short position (fade the strength)
            price=upper_reversion,         # Trigger at overbought level
            time_in_force="GTC"            # Remains active until triggered
        )

        # Buy MIT when price reaches lower extreme (expecting reversion up)
        # Logic: Price too low relative to mean, expect upward correction
        buy_mit_response = await client.orders.post_market_if_touched_order(
            account_id=client.account_id,
            instrument=InstrumentName("EUR_USD"),
            units=10000,                   # Long position (fade the weakness)
            price=lower_reversion,         # Trigger at oversold level
            time_in_force="GTC"            # Remains active until triggered
        )

        # ==============================================================================
        # STEP 3: CONFIRM ORDER PLACEMENT AND DISPLAY STRATEGY
        # ==============================================================================

        assert sell_mit_response.order_create_transaction is not None
        assert buy_mit_response.order_create_transaction is not None
        sell_mit_id = sell_mit_response.order_create_transaction["id"]
        buy_mit_id = buy_mit_response.order_create_transaction["id"]

        print("\n Mean reversion MIT orders placed:")
        print(f"  Sell MIT Order ID: {sell_mit_id}")
        print(f"    Trigger: {upper_reversion:.5f} (fade overbought)")
        print("    Size: 10,000 units short")
        print(f"\n  Buy MIT Order ID: {buy_mit_id}")
        print(f"    Trigger: {lower_reversion:.5f} (fade oversold)")
        print("    Size: 10,000 units long")

        print("\nStrategy Logic:")
        print("  • Sell when price extends too far above mean (overbought)")
        print("  • Buy when price extends too far below mean (oversold)")
        print(f"  • Expect price to revert back toward {mean_price:.5f}")
        print("  • Counter-trend approach (opposite of breakout strategies)")

        print("\nRisk Considerations:")
        print("  • Works best in ranging/sideways markets")
        print("  • Can suffer losses during strong trending markets")
        print("  • Requires stop losses to limit exposure in trends")
        print("  • Consider adding trend filters (e.g., ADX, MA slope)")

        # ==============================================================================
        # PRODUCTION ENHANCEMENTS
        # ==============================================================================

        print("\n" + "=" * 60)
        print("PRODUCTION ENHANCEMENTS TO CONSIDER")
        print("=" * 60)
        print("\nTo make this strategy production-ready, add:")
        print("  • Calculate actual mean price from historical candles")
        print("  • Add volatility-based reversion distance (use ATR)")
        print("  • Implement trend filters to avoid counter-trending")
        print("  • Add stop losses at further extremes")
        print("  • Include take profit targets near the mean price")
        print("  • Monitor mean reversion success rate by market regime")
        print("  • Consider time-of-day filters (ranges during specific sessions)")
        print("  • Track correlation between reversion distance and success")


if __name__ == "__main__":
    # Run the mean reversion strategy demonstration
    asyncio.run(main())
```

## Momentum Detection Systems

Effective breakout trading requires distinguishing between genuine momentum moves and false breakouts that quickly reverse. Momentum detection systems use stop orders with confirmation buffers - placing triggers beyond key levels to ensure price demonstrates sustained directional movement before entry. This approach filters out noise and whipsaws that occur when price briefly touches a level without commitment, significantly improving win rates by waiting for the market to prove its directional intent through follow-through action.

The key to momentum confirmation lies in strategic trigger placement using `client.orders.post_stop_order()` with calculated buffers beyond support and resistance levels. Rather than triggering immediately at a key level, these systems require additional price movement (typically measured in pips or as a percentage of average volatility) to confirm genuine momentum. This conservative approach sacrifices some profit potential from immediate breakouts in exchange for higher quality trades with better success rates and reduced false signal frequency.

Implementing momentum detection combines technical analysis for level identification with SDK order management for precise execution. The examples show how to calculate momentum thresholds based on historical volatility, monitor breakout quality after order triggers, and adjust confirmation requirements based on market conditions and timeframe:

### Momentum Confirmation with Stop Orders

```python
import asyncio
from decimal import Decimal

from dotenv import load_dotenv

from fivetwenty import AsyncClient
from fivetwenty.models import InstrumentName

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
# MOMENTUM CONFIRMATION BREAKOUT STRATEGY
# ==============================================================================

# This example demonstrates momentum confirmation to reduce false breakouts:
#
# KEY CONCEPTS:
# 1. Momentum Confirmation - Require price movement beyond key levels before entry
# 2. False Breakout Filter - Small buffer beyond resistance/support filters noise
# 3. Trigger Offset - Distance beyond key level confirms genuine directional intent
# 4. Quality Over Speed - Trade slower but more reliable breakout signals
#
# HOW IT WORKS:
# Rather than triggering immediately when price touches resistance or support,
# the strategy requires additional price movement (momentum threshold) beyond the
# key level. This confirms the breakout has genuine momentum and isn't just a
# brief spike that will quickly reverse. Stop orders are placed at resistance +
# buffer (bullish) or support - buffer (bearish), ensuring only confirmed
# momentum breakouts trigger positions.
#
# This code is fully executable and demonstrates momentum-confirmed stop orders.


# ==============================================================================
# MOMENTUM BREAKOUT STRATEGY CLASS
# ==============================================================================


class MomentumBreakout:
    """
    Momentum confirmation breakout system using stop orders with trigger buffers.

    This class places stop orders beyond key levels to ensure genuine momentum
    confirmation before entry, reducing false breakout signals.
    """

    def __init__(self, client: AsyncClient, account_id: str) -> None:
        """
        Initialize momentum confirmation framework.

        Args:
            client: Authenticated AsyncClient for order execution
            account_id: Account ID for trading operations

        """
        self.client = client
        self.account_id = account_id
        self.momentum_threshold = Decimal("0.0015")  # 1.5 pip confirmation buffer

        print("Momentum Confirmation System initialized:")
        print(f"  Momentum threshold: {self.momentum_threshold * 10000:.1f} pips")
        print("  Strategy: Confirm breakouts with price movement beyond key levels")

    async def place_momentum_confirmed_stops(
        self, instrument: InstrumentName
    ) -> tuple[str, str]:
        """
        Place stop orders requiring momentum confirmation to reduce false breakouts.

        Args:
            instrument: Currency pair to trade

        Returns:
            Tuple of (buy_stop_id, sell_stop_id)

        """
        # ==============================================================================
        # STEP 1: GET CURRENT MARKET PRICE FOR CONTEXT
        # ==============================================================================

        # ==============================================================================
        # SDK METHOD: client.pricing.get_pricing()
        # ==============================================================================
        #
        # Get current market pricing for instruments
        #
        # Parameters:
        #   - account_id: Your OANDA account ID
        #   - instruments: List of instrument names to get pricing for
        #
        # Returns: TypedDict with prices (list of Price models)

        pricing = await self.client.pricing.get_pricing(
            account_id=self.account_id,
            instruments=[instrument.value]
        )

        # Access pricing data from TypedDict response
        current_price = Decimal(pricing["prices"][0].asks[0].price)
        print(f"\nCurrent {instrument.value} price: {current_price:.5f}")

        # ==============================================================================
        # STEP 2: CALCULATE DYNAMIC TECHNICAL LEVELS
        # ==============================================================================

        # Calculate resistance/support levels relative to current price
        # In production, use actual chart analysis or historical swing points
        level_distance = Decimal("0.0020")  # 20 pips from current price

        resistance = current_price + level_distance     # Resistance above current
        support = current_price - level_distance        # Support below current

        print(f"\nDynamic key levels (±{level_distance * 10000:.0f} pips from current):")
        print(f"  Resistance: {resistance:.5f} (+{level_distance * 10000:.0f} pips)")
        print(f"  Support: {support:.5f} (-{level_distance * 10000:.0f} pips)")
        print(f"  Momentum threshold: {self.momentum_threshold * 10000:.1f} pips buffer")

        # ==============================================================================
        # STEP 3: CALCULATE MOMENTUM-CONFIRMED TRIGGER LEVELS
        # ==============================================================================

        # Require additional price movement beyond key level to confirm breakout
        # This reduces false breakouts and ensures genuine momentum
        bullish_trigger = resistance + self.momentum_threshold  # Resistance + buffer
        bearish_trigger = support - self.momentum_threshold     # Support - buffer

        print("\nMomentum-confirmed triggers:")
        print(f"  Bullish: {bullish_trigger:.5f} (resistance + {self.momentum_threshold * 10000:.1f} pips)")
        print(f"  Bearish: {bearish_trigger:.5f} (support - {self.momentum_threshold * 10000:.1f} pips)")

        # ==============================================================================
        # STEP 4: PLACE MOMENTUM-CONFIRMED STOP ORDERS
        # ==============================================================================

        # ==============================================================================
        # SDK METHOD: client.orders.post_stop_order()
        # ==============================================================================
        #
        # Place a stop order that triggers when price reaches specified level
        #
        # Parameters:
        #   - account_id: Your OANDA account ID
        #   - instrument: Currency pair (InstrumentName enum)
        #   - units: Position size (positive=buy, negative=sell)
        #   - price: Trigger price (Decimal - with momentum buffer)
        #   - time_in_force: Order lifetime ("GTC" = Good Till Cancelled)
        #
        # Returns: OrderResponse with order creation details

        position_size = 12000  # Position size for confirmed breakouts

        # Bullish momentum-confirmed stop order
        buy_stop_response = await self.client.orders.post_stop_order(
            account_id=self.account_id,
            instrument=instrument,
            units=position_size,              # Long position
            price=bullish_trigger,            # Requires momentum confirmation
            time_in_force="GTC"
        )

        # Bearish momentum-confirmed stop order
        sell_stop_response = await self.client.orders.post_stop_order(
            account_id=self.account_id,
            instrument=instrument,
            units=-position_size,             # Short position
            price=bearish_trigger,            # Requires momentum confirmation
            time_in_force="GTC"
        )

        # ==============================================================================
        # STEP 5: EXTRACT ORDER IDS AND CONFIRM PLACEMENT
        # ==============================================================================

        if buy_stop_response.get("orderCreateTransaction") is None or sell_stop_response.get("orderCreateTransaction") is None:
            msg = "Order creation transaction missing from response"
            raise ValueError(msg)
        buy_stop_id = buy_stop_response["orderCreateTransaction"].id
        sell_stop_id = sell_stop_response["orderCreateTransaction"].id

        print("\n Momentum-confirmed breakout orders placed:")
        print(f"  Buy Stop Order ID: {buy_stop_id}")
        print(f"    Trigger: {bullish_trigger:.5f} (resistance + {self.momentum_threshold * 10000:.1f} pips)")
        print(f"    Size: {position_size:,} units long")
        print(f"\n  Sell Stop Order ID: {sell_stop_id}")
        print(f"    Trigger: {bearish_trigger:.5f} (support - {self.momentum_threshold * 10000:.1f} pips)")
        print(f"    Size: {position_size:,} units short")

        print("\nStrategy Advantages:")
        print("  • Reduces false breakouts by requiring momentum confirmation")
        print("  • Filters out brief spikes and whipsaws at key levels")
        print("  • Ensures genuine directional intent before entry")
        print("  • Higher win rate at cost of missing some rapid moves")

        return buy_stop_id, sell_stop_id


# ==============================================================================
# DEMONSTRATION MAIN FUNCTION
# ==============================================================================


async def main() -> None:
    """Demonstrate momentum confirmation breakout strategy with stop orders."""

    print("=" * 60)
    print("MOMENTUM CONFIRMATION BREAKOUT STRATEGY")
    print("=" * 60)

    # ==============================================================================
    # CONNECT TO OANDA
    # ==============================================================================

    # AsyncClient automatically reads FIVETWENTY_OANDA_* environment variables
    # Context manager ensures proper cleanup of HTTP connections
    async with AsyncClient() as client:
        # ==============================================================================
        # CREATE AND EXECUTE MOMENTUM STRATEGY
        # ==============================================================================

        # Initialize momentum confirmation system
        strategy = MomentumBreakout(
            client=client,
            account_id=client.account_id
        )

        # Place momentum-confirmed stop orders
        buy_id, sell_id = await strategy.place_momentum_confirmed_stops(
            instrument=InstrumentName("EUR_USD")
        )

        # ==============================================================================
        # DISPLAY STRATEGY SUMMARY
        # ==============================================================================

        print("\n" + "=" * 60)
        print("STRATEGY DEPLOYMENT SUMMARY")
        print("=" * 60)
        print("\nInstrument: EUR/USD")
        print(f"Order IDs: {buy_id}, {sell_id}")
        print("Confirmation method: Momentum threshold beyond key levels")
        print("Trade-off: Quality over speed - fewer but better signals")

        # ==============================================================================
        # PRODUCTION ENHANCEMENTS
        # ==============================================================================

        print("\n" + "=" * 60)
        print("PRODUCTION ENHANCEMENTS TO CONSIDER")
        print("=" * 60)
        print("\nTo make this strategy production-ready, add:")
        print("  • Calculate actual resistance/support from chart analysis")
        print("  • Adjust momentum threshold based on current volatility (ATR)")
        print("  • Implement post-trigger momentum validation")
        print("  • Add volume confirmation for breakout quality")
        print("  • Track false breakout rates and adjust thresholds accordingly")
        print("  • Implement time-based filters (avoid low-liquidity periods)")
        print("  • Add stop loss and take profit to each breakout order")
        print("  • Monitor breakout follow-through distance for optimization")


if __name__ == "__main__":
    # Run the momentum confirmation demonstration
    asyncio.run(main())
```

## Performance Optimization

High-performance trading systems require efficient order placement and management to minimize latency between market signals and trade execution. When placing multiple stop or MIT orders across different levels or timeframes, the speed and efficiency of your order placement logic directly impacts strategy performance. Batch order calculations, optimized API calls, and pre-computed trigger levels keep the delay between decision and placement small; slow placement can mean missed trades or worse entry prices.

The FiveTwenty SDK supports fast order management through its async architecture. By pre-calculating order parameters, batching order placements, and using Python's `asyncio`, you can place multiple orders rapidly with clean, maintainable code. This approach is particularly valuable for strategies that manage numerous orders simultaneously, such as multi-timeframe breakout systems or layered mean reversion setups with orders at various price levels.

Optimizing order trigger efficiency involves both code-level improvements and strategic design decisions. The examples demonstrate practical techniques for batch order preparation, efficient parameter calculation, and rapid sequential placement that minimize the time between strategy decision and order activation:

### Order Trigger Efficiency

```python
import asyncio
from decimal import Decimal

from dotenv import load_dotenv

from fivetwenty import AsyncClient
from fivetwenty.models import InstrumentName

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
# EFFICIENT BATCH ORDER PLACEMENT STRATEGY
# ==============================================================================

# This example demonstrates efficient batch order placement for rapid market response:
#
# KEY CONCEPTS:
# 1. Pre-Calculation - Compute all order parameters before placement
# 2. Batch Processing - Prepare multiple orders in a single pass
# 3. Async Execution - Leverage async/await for concurrent API calls
# 4. Layered Orders - Multiple trigger levels at varying distances
#
# HOW IT WORKS:
# The strategy pre-calculates all order specifications (price levels, position sizes)
# in a single loop before making any API calls. This minimizes computation time
# between market signal and order activation. Orders are then placed sequentially
# using async calls, ensuring rapid deployment of the complete order structure.
# This approach is ideal for strategies requiring multiple orders at different levels.
#
# This code is fully executable and demonstrates batch order efficiency techniques.


async def main() -> None:
    """Demonstrate efficient batch order placement for rapid market response."""

    print("=" * 60)
    print("EFFICIENT BATCH ORDER PLACEMENT")
    print("=" * 60)

    # ==============================================================================
    # CONNECT TO OANDA
    # ==============================================================================

    # AsyncClient automatically reads FIVETWENTY_OANDA_* environment variables
    # Context manager ensures proper cleanup of HTTP connections
    async with AsyncClient() as client:
        # ==============================================================================
        # STEP 1: GET CURRENT MARKET PRICE
        # ==============================================================================

        # Fetch real-time pricing to calculate dynamic order levels
        pricing = await client.pricing.get_pricing(
            account_id=client.account_id,
            instruments=["EUR_USD"]
        )

        base_price = Decimal(pricing["prices"][0].asks[0].price)
        print(f"\nCurrent EUR/USD price: {base_price:.5f}")

        # ==============================================================================
        # STEP 2: PRE-CALCULATE ALL ORDER PARAMETERS
        # ==============================================================================

        # Define layered distance levels from current price
        # Each distance represents a different significance level
        distances = [
            Decimal("0.0010"),  # 10 pips - short-term level
            Decimal("0.0020"),  # 20 pips - medium-term level
            Decimal("0.0030"),  # 30 pips - long-term level
        ]

        # Pre-compute all order specifications before placement
        # This minimizes time between signal and execution
        orders_to_place: list[dict[str, Decimal | int | str]] = []

        for i, distance in enumerate(distances):
            # Scale position size by level significance
            # Larger distances get larger allocations
            position_size = 5000 * (i + 1)

            # Calculate buy and sell trigger prices
            buy_price = base_price + distance   # Above current price
            sell_price = base_price - distance  # Below current price

            # Append buy stop specification
            orders_to_place.append({
                "type": "stop",
                "units": position_size,
                "price": buy_price,
                "direction": "buy"
            })

            # Append sell stop specification
            orders_to_place.append({
                "type": "stop",
                "units": -position_size,
                "price": sell_price,
                "direction": "sell"
            })

        print(f"\nPre-calculated {len(orders_to_place)} order specifications:")
        for i, order in enumerate(orders_to_place, 1):
            price = order["price"]
            units = order["units"]
            assert isinstance(price, Decimal)
            assert isinstance(units, int)
            direction = "BUY" if units > 0 else "SELL"
            distance_pips = abs(price - base_price) * 10000
            print(f"  {i}. {direction} {abs(units):,} units @ {price:.5f} ({distance_pips:.0f} pips)")

        # ==============================================================================
        # STEP 3: PLACE ALL ORDERS RAPIDLY
        # ==============================================================================

        # ==============================================================================
        # SDK METHOD: client.orders.post_stop_order()
        # ==============================================================================
        #
        # Place stop orders at pre-calculated levels
        #
        # Parameters:
        #   - account_id: Your OANDA account ID
        #   - instrument: Currency pair (InstrumentName enum)
        #   - units: Position size (positive=buy, negative=sell)
        #   - price: Trigger price (Decimal)
        #   - time_in_force: Order lifetime ("GTC" = Good Till Cancelled)
        #
        # Returns: OrderResponse with order creation details

        print(f"\nPlacing {len(orders_to_place)} orders...")

        placed_order_ids: list[str] = []

        for order_spec in orders_to_place:
            if order_spec["type"] == "stop":
                units = order_spec["units"]
                price = order_spec["price"]
                assert isinstance(units, int)
                assert isinstance(price, Decimal)

                response = await client.orders.post_stop_order(
                    account_id=client.account_id,
                    instrument=InstrumentName("EUR_USD"),
                    units=units,
                    price=price,
                    time_in_force="GTC"
                )

                # Extract and store order ID
                assert response.order_create_transaction is not None
                order_id = response.order_create_transaction["id"]
                placed_order_ids.append(order_id)

        # ==============================================================================
        # STEP 4: CONFIRM BATCH PLACEMENT
        # ==============================================================================

        print(f"\n Successfully placed {len(placed_order_ids)} trigger orders:")
        for i, order_id in enumerate(placed_order_ids, 1):
            order_spec = orders_to_place[i - 1]
            price = order_spec["price"]
            units = order_spec["units"]
            assert isinstance(price, Decimal)
            assert isinstance(units, int)
            direction = "BUY" if units > 0 else "SELL"
            print(f"  Order {order_id}: {direction} {abs(units):,} @ {price:.5f}")

        print("\nBatch Placement Advantages:")
        print("  • Pre-calculation minimizes execution time")
        print("  • All order parameters computed before API calls")
        print("  • Efficient async execution for rapid deployment")
        print("  • Suitable for multi-level order structures")

        # ==============================================================================
        # PRODUCTION ENHANCEMENTS
        # ==============================================================================

        print("\n" + "=" * 60)
        print("PRODUCTION ENHANCEMENTS TO CONSIDER")
        print("=" * 60)
        print("\nTo make this strategy production-ready, add:")
        print("  • Use asyncio.gather() for concurrent order placement")
        print("  • Implement retry logic for failed placements")
        print("  • Add order validation before placement")
        print("  • Track placement latency metrics")
        print("  • Implement order replacement on price updates")
        print("  • Add conditional order placement based on market state")
        print("  • Monitor order fill rates by distance level")
        print("  • Implement order cancellation when strategy exits")


if __name__ == "__main__":
    # Run the efficient batch order placement demonstration
    asyncio.run(main())
```

## Best Practices Summary

### Stop Order Usage
- Place stops beyond significant levels for momentum capture
- Implement momentum confirmation for quality breakouts

### MIT Order Usage
- Target mean reversion at statistical extremes
- Combine with technical indicators (RSI, Bollinger Bands)
- Use smaller position sizes than breakout strategies

### System Design
- Handle errors on every order operation
- Use appropriate position sizing for strategy type

## Next Steps

Advance your order management capabilities:

- **[Dynamic Order Management](dynamic-management.md)** - Trailing stops and adaptive sizing
- **[Order Strategies & Combinations](order-strategies.md)** - Bracket orders and advanced techniques

## Key Takeaways

1. **Stop orders** capture momentum and breakouts
2. **MIT orders** suit mean reversion and profit-taking
3. **Momentum confirmation** reduces false breakout signals
4. **Batched placement** reduces the delay between signal and execution

Next, continue to [Dynamic Order Management](dynamic-management.md) to add trailing stops and adaptive position sizing to these trigger-based strategies.