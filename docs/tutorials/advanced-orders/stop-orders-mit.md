# Stop Orders & Market-If-Touched

Learn breakout and mean reversion strategies using stop orders and market-if-touched (MIT) orders for systematic trading approaches.

## Learning Objectives

By the end of this guide, you will:

- Implement breakout strategies with stop orders
- Design mean reversion systems with MIT orders
- Build momentum and reversal detection systems

## Stop Orders for Breakout Strategies

Stop orders excel at capturing momentum when price breaks through key levels.

### Basic Breakout Implementation

```python
from decimal import Decimal
from fivetwenty import AsyncClient


async def breakout_stop_strategy() -> Any:
    """Implement basic breakout strategy using stop orders for momentum capture."""
    # Step 1: Initialize client for breakout order placement
    async with AsyncClient() as client:
        # Step 2: Define key price levels for breakout strategy
        # These would typically be identified through technical analysis
        resistance_level = Decimal("1.0900")  # EUR/USD resistance level from chart analysis
        support_level = Decimal("1.0800")     # EUR/USD support level from chart analysis

        print(f"Setting up breakout strategy between {support_level} and {resistance_level}")

        # Step 3: Place stop orders for breakout capture
        # Stop orders trigger when price reaches specified level, capturing momentum

        # Buy stop above resistance (bullish breakout strategy)
        # Triggers when price breaks ABOVE resistance, indicating upward momentum
        buy_stop_response = await client.orders.post_stop_order(
            account_id="your_account_id",          # Replace with actual account ID
            instrument="EUR_USD",                  # Currency pair to trade
            units=10000,                           # Long position size (positive = buy)
            price=resistance_level + Decimal("0.0005"),  # Trigger 0.5 pips above resistance
            time_in_force="GTC"                    # Good Till Cancelled - stays active
        )

        # Sell stop below support (bearish breakout strategy)
        # Triggers when price breaks BELOW support, indicating downward momentum
        sell_stop_response = await client.orders.post_stop_order(
            account_id="your_account_id",          # Replace with actual account ID
            instrument="EUR_USD",                  # Currency pair to trade
            units=-10000,                          # Short position size (negative = sell)
            price=support_level - Decimal("0.0005"),  # Trigger 0.5 pips below support
            time_in_force="GTC"                    # Good Till Cancelled - stays active
        )

        # Step 4: Confirm order placement and display strategy setup
        print(f"Success Breakout stops successfully placed:")
        print(f"   Analysis Buy stop: {resistance_level + Decimal('0.0005')} (bullish breakout trigger)")
        print(f"   📉 Sell stop: {support_level - Decimal('0.0005')} (bearish breakout trigger)")
        print(f"   Data Range: {(resistance_level - support_level) * 10000:.0f} pips")
        print(f"   Note Strategy: Capture momentum when price breaks key levels")

        return {
            "buy_stop_id": buy_stop_response.order_create_transaction.id,
            "sell_stop_id": sell_stop_response.order_create_transaction.id
        }
```

### Dynamic Breakout Levels

Adapt breakout levels based on market volatility:

```python
from decimal import Decimal
from fivetwenty import AsyncClient


async def dynamic_breakout_levels() -> Any:
    """Calculate adaptive breakout levels based on current market volatility."""
    # Step 1: Initialize client for dynamic level calculation
    async with AsyncClient() as client:
        # Step 2: Set up volatility measurement parameters
        # ATR (Average True Range) measures recent price volatility
        atr_period = 14                          # Standard 14-period ATR
        current_atr = Decimal("0.0045")         # Example: 4.5 pip daily volatility

        print(f"Calculating dynamic breakout levels using {atr_period}-period ATR")
        print(f"Current market volatility (ATR): {current_atr * 10000:.1f} pips")

        # Step 3: Get current market price for level calculation
        pricing = await client.pricing.get_pricing(
            account_id="your_account_id",    # Replace with actual account ID
            instruments=["EUR_USD"]           # Currency pair for analysis
        )

        # Use ask price as current market level
        current_price = Decimal(pricing.prices[0].asks[0].price)
        print(f"Current market price: {current_price:.5f}")

        # Step 4: Calculate adaptive breakout levels based on volatility
        # Use percentage of ATR to set breakout distance from current price
        breakout_buffer = current_atr * Decimal("0.5")  # 50% of ATR creates responsive levels

        # Dynamic levels adjust automatically to market conditions
        upper_breakout = current_price + breakout_buffer  # Bullish breakout level
        lower_breakout = current_price - breakout_buffer  # Bearish breakout level

        print(f"Dynamic breakout buffer: {breakout_buffer * 10000:.1f} pips (50% of ATR)")

        # Step 5: Place volatility-adaptive stop orders
        # Order sizes can be adjusted based on volatility (higher vol = smaller size)
        position_size = 15000  # Base position size

        # Bullish breakout order (triggers on upward momentum)
        buy_stop = await client.orders.post_stop_order(
            account_id="your_account_id",    # Replace with actual account ID
            instrument="EUR_USD",            # Currency pair to trade
            units=position_size,             # Long position size
            price=upper_breakout,            # Adaptive trigger level
            time_in_force="GTC"              # Remains active until triggered or cancelled
        )

        # Bearish breakout order (triggers on downward momentum)
        sell_stop = await client.orders.post_stop_order(
            account_id="your_account_id",    # Replace with actual account ID
            instrument="EUR_USD",            # Currency pair to trade
            units=-position_size,            # Short position size
            price=lower_breakout,            # Adaptive trigger level
            time_in_force="GTC"              # Remains active until triggered or cancelled
        )

        # Step 6: Display adaptive strategy configuration
        print(f"\nSuccess Dynamic breakout orders placed:")
        print(f"   Data Volatility (ATR): {current_atr * 10000:.1f} pips")
        print(f"   Analysis Upper breakout: {upper_breakout:.5f} (+{breakout_buffer * 10000:.1f} pips)")
        print(f"   📉 Lower breakout: {lower_breakout:.5f} (-{breakout_buffer * 10000:.1f} pips)")
        print(f"   Target Position size: {position_size:,} units each direction")
        print(f"   Note Advantage: Levels adapt automatically to market volatility")

        return buy_stop, sell_stop
```

### Multi-Timeframe Breakout System

Combine multiple timeframe signals for robust breakouts:

<!-- fragment: Demo multi-timeframe breakout with undefined Any types and unused arguments -->
```python
from decimal import Decimal

from fivetwenty import AsyncClient



class MultiTimeframeBreakout:
    """Multi-timeframe breakout system for robust signal confirmation."""

    def __init__(self, client: AsyncClient, account_id: str) -> None:
        # Step 1: Initialize multi-timeframe analysis framework
        self.client = client                # Authenticated client for order execution
        self.account_id = account_id        # Account for trading operations
        self.active_stops = []             # Track all placed stop orders

        print("Initializing multi-timeframe breakout system")
        print("Strategy: Align breakout signals across multiple time horizons")

    async def analyze_breakout_levels(self, instrument: str) -> Any:
        """Analyze breakout levels across multiple timeframes for comprehensive signals."""
        # Step 1: Multi-timeframe analysis framework
        # In production, this would integrate with your preferred data provider
        # Different timeframes reveal different market structure levels

        print(f"Analyzing {instrument} breakout levels across timeframes:")

        # Step 2: Define breakout levels for each timeframe
        # Each timeframe provides different significance levels
        breakout_levels = {
            "15min": {                                    # Short-term intraday levels
                "resistance": Decimal("1.0890"),         # Recent high resistance
                "support": Decimal("1.0810"),            # Recent low support
                "significance": "Intraday momentum"      # Level importance
            },
            "1hour": {                                    # Medium-term trend levels
                "resistance": Decimal("1.0920"),         # Hourly trend resistance
                "support": Decimal("1.0780"),            # Hourly trend support
                "significance": "Short-term trend"       # Level importance
            },
            "4hour": {                                    # Long-term structural levels
                "resistance": Decimal("1.0950"),         # Major structural high
                "support": Decimal("1.0750"),            # Major structural low
                "significance": "Major trend structure"  # Level importance
            },
        }

        # Step 3: Display multi-timeframe analysis
        for timeframe, levels in breakout_levels.items():
            range_pips = (levels["resistance"] - levels["support"]) * 10000
            print(f"   {timeframe}: {levels['support']:.5f} - {levels['resistance']:.5f} ({range_pips:.0f} pips)")
            print(f"      Significance: {levels['significance']}")

        return breakout_levels

    async def place_layered_breakout_stops(self, instrument: str) -> Any:
        """Place layered stop orders across multiple timeframes with scaled position sizing."""
        # Step 1: Get multi-timeframe breakout analysis
        levels = await self.analyze_breakout_levels(instrument)

        # Step 2: Define position sizing strategy for each timeframe
        # Longer timeframes get larger allocations due to higher significance
        timeframe_weights = {
            "15min": 0.3,    # 30% allocation - short-term signals
            "1hour": 0.5,    # 50% allocation - medium-term signals
            "4hour": 0.7     # 70% allocation - long-term signals
        }

        print(f"\nPlacing layered breakout stops with timeframe-weighted sizing:")

        # Step 3: Place stops at each timeframe level with appropriate sizing
        for timeframe, level_data in levels.items():
            weight = timeframe_weights[timeframe]
            base_units = 10000                        # Base position size
            scaled_units = int(base_units * weight)   # Scale by timeframe importance

            print(f"\n{timeframe} timeframe ({level_data['significance']}):")
            print(f"   Position allocation: {weight * 100:.0f}% = {scaled_units:,} units")

            # Step 4: Place breakout stops for this timeframe
            breakout_buffer = Decimal("0.0005")  # 0.5 pip buffer beyond key levels

            # Bullish breakout stop (long position trigger)
            buy_stop = await self.client.orders.post_stop_order(
                account_id=self.account_id,                           # Account for execution
                instrument=instrument,                               # Currency pair
                units=scaled_units,                                  # Timeframe-weighted size
                price=level_data["resistance"] + breakout_buffer,    # Trigger above resistance
                time_in_force="GTC",                                # Active until triggered
            )

            # Bearish breakout stop (short position trigger)
            sell_stop = await self.client.orders.post_stop_order(
                account_id=self.account_id,                          # Account for execution
                instrument=instrument,                              # Currency pair
                units=-scaled_units,                                # Timeframe-weighted size
                price=level_data["support"] - breakout_buffer,      # Trigger below support
                time_in_force="GTC",                               # Active until triggered
            )

            # Step 5: Track placed orders and display confirmation
            self.active_stops.extend([
                buy_stop.order_create_transaction.id,
                sell_stop.order_create_transaction.id,
            ])

            print(f"   Success Stops placed: {scaled_units:,} units each direction")
            print(f"   Analysis Buy trigger: {level_data['resistance'] + breakout_buffer:.5f}")
            print(f"   📉 Sell trigger: {level_data['support'] - breakout_buffer:.5f}")

        print(f"\nTarget Multi-timeframe strategy advantages:")
        print(f"   • Higher timeframe breaks have stronger follow-through")
        print(f"   • Position sizing reflects signal strength and duration")
        print(f"   • Captures both intraday momentum and longer-term moves")
        print(f"   • Reduces false signals through timeframe confirmation")

        return self.active_stops
```

## MIT Orders for Mean Reversion

Market-If-Touched orders are ideal for mean reversion strategies where you expect price to return to average levels.

### Basic Mean Reversion Setup

```python
from decimal import Decimal
from fivetwenty import AsyncClient


async def mean_reversion_mit_strategy() -> Any:
    """Implement mean reversion strategy using MIT orders to fade extreme moves."""
    # Step 1: Initialize client for mean reversion strategy
    async with AsyncClient() as client:
        # Step 2: Define mean reversion parameters
        # Mean reversion assumes price will return to average after extreme moves
        mean_price = Decimal("1.0850")           # 20-period moving average (fair value)
        reversion_distance = Decimal("0.0030")   # 30 pips from mean (extreme threshold)

        # Calculate reversion trigger levels
        upper_reversion = mean_price + reversion_distance  # Overbought level
        lower_reversion = mean_price - reversion_distance  # Oversold level

        print(f"Setting up mean reversion strategy around {mean_price:.5f}")
        print(f"Reversion range: ±{reversion_distance * 10000:.0f} pips from mean")

        # Step 3: Place MIT orders for mean reversion entries
        # MIT (Market-If-Touched) orders become market orders when price is reached

        # Sell MIT when price reaches upper extreme (expecting reversion down)
        # Logic: Price too high relative to mean, expect downward correction
        sell_mit_response = await client.orders.post_market_if_touched_order(
            account_id="your_account_id",    # Replace with actual account ID
            instrument="EUR_USD",            # Currency pair to trade
            units=-10000,                    # Short position (fade the strength)
            price=upper_reversion,           # Trigger at overbought level
            time_in_force="GTC"              # Remains active until triggered
        )

        # Buy MIT when price reaches lower extreme (expecting reversion up)
        # Logic: Price too low relative to mean, expect upward correction
        buy_mit_response = await client.orders.post_market_if_touched_order(
            account_id="your_account_id",    # Replace with actual account ID
            instrument="EUR_USD",            # Currency pair to trade
            units=10000,                     # Long position (fade the weakness)
            price=lower_reversion,           # Trigger at oversold level
            time_in_force="GTC"              # Remains active until triggered
        )

        # Step 4: Display mean reversion strategy setup
        print(f"\nSuccess Mean reversion MIT orders placed:")
        print(f"   Data Mean price (20 SMA): {mean_price:.5f}")
        print(f"   Analysis Sell MIT: {upper_reversion:.5f} (fade strength when overbought)")
        print(f"   📉 Buy MIT: {lower_reversion:.5f} (fade weakness when oversold)")
        print(f"   Target Strategy: Counter-trend trading expecting price return to mean")
        print(f"   ⚠️  Risk: Works best in ranging markets, avoid in strong trends")

        return {
            "sell_mit_id": sell_mit_response.order_create_transaction.id,
            "buy_mit_id": buy_mit_response.order_create_transaction.id
        }
```

### Bollinger Band Reversion Strategy

Use Bollinger Bands for systematic mean reversion:

```python
from decimal import Decimal
from fivetwenty import AsyncClient


async def bollinger_band_reversion() -> Any:
    """Mean reversion strategy using Bollinger Bands for statistical extreme detection."""
    # Step 1: Initialize client for Bollinger Band mean reversion
    async with AsyncClient() as client:
        # Step 2: Calculate Bollinger Band parameters
        # Bollinger Bands use standard deviation to identify statistical extremes
        # In practice, these would be calculated from historical price data

        sma_20 = Decimal("1.0850")      # 20-period simple moving average (center line)
        std_dev = Decimal("0.0025")     # Standard deviation of recent prices
        bb_multiplier = Decimal("2.0")  # 2 standard deviations (captures ~95% of price action)

        # Calculate Bollinger Band levels
        upper_band = sma_20 + (std_dev * bb_multiplier)  # Upper band (resistance)
        lower_band = sma_20 - (std_dev * bb_multiplier)  # Lower band (support)

        print(f"Bollinger Band Mean Reversion Setup:")
        print(f"   Center (20 SMA): {sma_20:.5f}")
        print(f"   Standard deviation: {std_dev * 10000:.1f} pips")
        print(f"   Band width: {(upper_band - lower_band) * 10000:.0f} pips")

        # Step 3: Place MIT orders at Bollinger Band extremes
        # Statistical theory: Price has high probability of returning toward mean

        # Sell MIT at upper band (statistically overbought condition)
        # When price reaches 2 standard deviations above mean, expect reversion
        sell_mit = await client.orders.post_market_if_touched_order(
            account_id="your_account_id",    # Replace with actual account ID
            instrument="EUR_USD",            # Currency pair to trade
            units=-15000,                    # Short position (fade the extreme high)
            price=upper_band,                # Trigger at upper Bollinger Band
            time_in_force="GTC"              # Active until triggered or cancelled
        )

        # Buy MIT at lower band (statistically oversold condition)
        # When price reaches 2 standard deviations below mean, expect reversion
        buy_mit = await client.orders.post_market_if_touched_order(
            account_id="your_account_id",    # Replace with actual account ID
            instrument="EUR_USD",            # Currency pair to trade
            units=15000,                     # Long position (fade the extreme low)
            price=lower_band,                # Trigger at lower Bollinger Band
            time_in_force="GTC"              # Active until triggered or cancelled
        )

        # Step 4: Display Bollinger Band strategy configuration
        print(f"\nSuccess Bollinger Band reversion orders placed:")
        print(f"   Analysis Upper band MIT: {upper_band:.5f} (sell when statistically overbought)")
        print(f"   📉 Lower band MIT: {lower_band:.5f} (buy when statistically oversold)")
        print(f"   Data Middle (20 SMA): {sma_20:.5f} (mean reversion target)")
        print(f"   Ruler Band separation: {(upper_band - lower_band) * 10000:.0f} pips")
        print(f"   Target Statistical edge: Price returns to mean ~68% of time from 2-sigma extremes")

        return sell_mit, buy_mit
```

### RSI-Based Mean Reversion

Combine MIT orders with RSI signals for enhanced mean reversion:

<!-- fragment: Demo RSI mean reversion with undefined Any types and magic number patterns -->
```python
from decimal import Decimal

from fivetwenty import AsyncClient



class RSIMeanReversion:
    """RSI-based mean reversion system using MIT orders for precise entry timing."""

    def __init__(self, client: AsyncClient, account_id: str) -> None:
        # Step 1: Initialize RSI mean reversion framework
        self.client = client                    # Authenticated trading client
        self.account_id = account_id           # Account for order execution

        # Step 2: Configure RSI parameters for mean reversion signals
        self.rsi_period = 14                   # Standard 14-period RSI calculation
        self.overbought_level = 70             # RSI level indicating overbought condition
        self.oversold_level = 30               # RSI level indicating oversold condition

        print(f"RSI Mean Reversion System initialized:")
        print(f"   RSI period: {self.rsi_period}")
        print(f"   Overbought threshold: {self.overbought_level}")
        print(f"   Oversold threshold: {self.oversold_level}")
        print(f"   Strategy: Fade extremes, expecting mean reversion")

    async def calculate_rsi_levels(self, instrument: str) -> Any:
        """Calculate price levels corresponding to RSI extreme conditions for MIT placement."""
        # Step 1: RSI-to-price level mapping
        # In production, this would calculate actual RSI from historical price data
        # and determine price levels where RSI reaches extreme values

        current_rsi = 65  # Example: Current RSI reading (neutral zone)

        print(f"Calculating RSI-based price levels for {instrument}:")
        print(f"   Current RSI: {current_rsi} (neutral zone: 30-70)")

        # Step 2: Define price levels where RSI reaches extreme values
        # These levels are calculated from historical RSI-price relationships
        rsi_price_levels = {
            "overbought_price": Decimal("1.0920"),  # Price level where RSI typically reaches 70
            "oversold_price": Decimal("1.0780"),    # Price level where RSI typically reaches 30
            "current_rsi": current_rsi,             # Current RSI reading for decision logic
            "neutral_upper": 65,                    # Upper neutral zone boundary
            "neutral_lower": 35                     # Lower neutral zone boundary
        }

        print(f"   Overbought price target: {rsi_price_levels['overbought_price']:.5f} (RSI ~70)")
        print(f"   Oversold price target: {rsi_price_levels['oversold_price']:.5f} (RSI ~30)")

        return rsi_price_levels

    async def place_rsi_reversion_orders(self, instrument: str) -> Any:
        """Place MIT orders at RSI extreme levels with intelligent market condition filtering."""
        # Step 1: Get RSI-based price level analysis
        rsi_data = await self.calculate_rsi_levels(instrument)

        # Step 2: Apply RSI-based market condition filter
        # Only place mean reversion orders when RSI is in neutral zone
        # This prevents counter-trend trading during strong momentum
        current_rsi = rsi_data["current_rsi"]

        if rsi_data["neutral_lower"] < current_rsi < rsi_data["neutral_upper"]:
            print(f"Success RSI {current_rsi} in neutral zone - placing reversion orders")

            position_size = 12000  # Position size for mean reversion trades

            # Step 3: Sell MIT at overbought level (fade strength)
            # When price reaches overbought RSI level, expect downward reversion
            sell_mit = await self.client.orders.post_market_if_touched_order(
                account_id=self.account_id,              # Account for execution
                instrument=instrument,                   # Currency pair to trade
                units=-position_size,                    # Short position (fade strength)
                price=rsi_data["overbought_price"],     # Trigger at RSI ~70 price level
                time_in_force="GTC",                    # Active until triggered
            )

            # Step 4: Buy MIT at oversold level (fade weakness)
            # When price reaches oversold RSI level, expect upward reversion
            buy_mit = await self.client.orders.post_market_if_touched_order(
                account_id=self.account_id,              # Account for execution
                instrument=instrument,                   # Currency pair to trade
                units=position_size,                     # Long position (fade weakness)
                price=rsi_data["oversold_price"],       # Trigger at RSI ~30 price level
                time_in_force="GTC",                    # Active until triggered
            )

            # Step 5: Confirm RSI mean reversion strategy deployment
            print(f"\nSuccess RSI reversion orders successfully placed:")
            print(f"   Analysis Sell MIT @ RSI 70: {rsi_data['overbought_price']:.5f} (fade overbought)")
            print(f"   📉 Buy MIT @ RSI 30: {rsi_data['oversold_price']:.5f} (fade oversold)")
            print(f"   Target Position size: {position_size:,} units each direction")
            print(f"   Note Logic: RSI extremes often lead to mean reversion")
            print(f"   Data Risk management: Only trade when RSI in neutral zone")

            return sell_mit, buy_mit
        else:
            print(f"⚠️ RSI {current_rsi} outside neutral range ({rsi_data['neutral_lower']}-{rsi_data['neutral_upper']})")
            print(f"   Reason: Avoid counter-trend trading during strong momentum")
            if current_rsi >= rsi_data["neutral_upper"]:
                print(f"   Market condition: Bullish momentum - wait for RSI cooling")
            else:
                print(f"   Market condition: Bearish momentum - wait for RSI recovery")
            return None, None
```

## Momentum Detection Systems

### Momentum Confirmation with Stop Orders

Wait for momentum confirmation before triggering breakouts:

```python
from decimal import Decimal
from fivetwenty import AsyncClient


class MomentumBreakout:
    def __init__(self, client: AsyncClient, account_id: str) -> None:
        self.client = client
        self.account_id = account_id
        self.momentum_threshold = Decimal("0.0015")  # 1.5 pip momentum

    async def place_momentum_confirmed_stops(self, instrument: str) -> Any:
        """Place stop orders requiring momentum confirmation to reduce false breakouts."""

        # Step 1: Get current market price for context
        pricing = await self.client.pricing.get_pricing(
            account_id=self.account_id,      # Account for pricing access
            instruments=[instrument]         # Currency pair to analyze
        )

        current_price = Decimal(pricing.prices[0].asks[0].price)
        print(f"Current {instrument} price: {current_price:.5f}")

        # Step 2: Define key technical levels (from chart analysis)
        resistance = Decimal("1.0900")     # Key resistance level
        support = Decimal("1.0800")        # Key support level

        print(f"Key levels: Support {support:.5f}, Resistance {resistance:.5f}")
        print(f"Momentum threshold: {self.momentum_threshold * 10000:.1f} pips")

        # Step 3: Calculate momentum-confirmed trigger levels
        # Require additional price movement beyond key level to confirm breakout
        # This reduces false breakouts and ensures genuine momentum
        bullish_trigger = resistance + self.momentum_threshold  # Resistance + buffer
        bearish_trigger = support - self.momentum_threshold     # Support - buffer

        print(f"Momentum-confirmed triggers:")
        print(f"   Bullish: {bullish_trigger:.5f} (resistance + {self.momentum_threshold * 10000:.1f} pips)")
        print(f"   Bearish: {bearish_trigger:.5f} (support - {self.momentum_threshold * 10000:.1f} pips)")

        # Step 4: Place momentum-confirmed stop orders
        # These orders only trigger after genuine momentum is confirmed
        position_size = 12000  # Position size for confirmed breakouts

        # Bullish momentum-confirmed stop order
        buy_stop = await self.client.orders.post_stop_order(
            account_id=self.account_id,      # Account for order placement
            instrument=instrument,           # Currency pair to trade
            units=position_size,             # Long position size
            price=bullish_trigger,           # Requires momentum confirmation
            time_in_force="GTC"              # Remains active until triggered
        )

        # Bearish momentum-confirmed stop order
        sell_stop = await self.client.orders.post_stop_order(
            account_id=self.account_id,      # Account for order placement
            instrument=instrument,           # Currency pair to trade
            units=-position_size,            # Short position size
            price=bearish_trigger,           # Requires momentum confirmation
            time_in_force="GTC"              # Remains active until triggered
        )

        # Step 5: Confirm momentum-based strategy deployment
        print(f"\nSuccess Momentum-confirmed breakout orders placed:")
        print(f"   Analysis Bullish trigger: {bullish_trigger:.5f} (resistance + {self.momentum_threshold * 10000:.1f} pips)")
        print(f"   📉 Bearish trigger: {bearish_trigger:.5f} (support - {self.momentum_threshold * 10000:.1f} pips)")
        print(f"   Target Position size: {position_size:,} units each direction")
        print(f"   Note Advantage: Reduces false breakouts by requiring momentum confirmation")
        print(f"   ⚠️  Trade-off: May miss some rapid reversals but improves win rate")

        return buy_stop, sell_stop

    async def monitor_momentum_quality(self, order_id: str) -> Any:
        """Monitor the quality of momentum after stop trigger."""

        # This would implement post-trigger momentum analysis
        # to validate the breakout quality

        order = await self.client.orders.get_order(
            account_id=self.account_id,
            order_id=order_id
        )

        if order.state == "FILLED":
            fill_price = Decimal(order.filling_transaction.price)

            # Analyze momentum quality after fill
            # (This would integrate with your momentum indicators)

            print(f"Order {order_id} filled at {fill_price}")
            print("Analyzing post-breakout momentum...")

            # Implementation would include momentum validation logic
            return True  # Valid momentum

        return False  # No fill yet or invalid momentum
```

## Performance Optimization

### Order Trigger Efficiency

Optimize order placement for fast trigger response:

```python
from decimal import Decimal
from fivetwenty import AsyncClient


async def efficient_trigger_placement() -> Any:
    """Optimize order placement for fast market response."""
    async with AsyncClient() as client:
        # Pre-calculate all order parameters
        orders_to_place = []

        # Batch order specifications
        base_price = Decimal("1.0850")
        distances = [Decimal("0.0010"), Decimal("0.0020"), Decimal("0.0030")]

        for i, distance in enumerate(distances):
            orders_to_place.extend([
                {
                    "type": "stop",
                    "units": 5000 * (i + 1),
                    "price": base_price + distance,
                    "direction": "buy"
                },
                {
                    "type": "stop",
                    "units": -5000 * (i + 1),
                    "price": base_price - distance,
                    "direction": "sell"
                }
            ])

        # Place all orders rapidly
        placed_orders = []

        for order_spec in orders_to_place:
            if order_spec["type"] == "stop":
                response = await client.orders.post_stop_order(
                    account_id="your_account_id",
                    instrument="EUR_USD",
                    units=order_spec["units"],
                    price=order_spec["price"],
                    time_in_force="GTC"
                )
                placed_orders.append(response.order_create_transaction.id)

        print(f"Efficiently placed {len(placed_orders)} trigger orders")
        return placed_orders
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
- Implement comprehensive error handling
- Use appropriate position sizing for strategy type

## Next Steps

Advance your order management capabilities:

- **[Dynamic Order Management](dynamic-management.md)** - Trailing stops and adaptive sizing
- **[Order Strategies & Combinations](order-strategies.md)** - Bracket orders and advanced techniques

## Key Takeaways

1. **Stop orders** capture momentum and breakouts effectively
2. **MIT orders** excel at mean reversion and profit-taking
3. **Momentum confirmation** reduces false breakout signals
4. **Performance optimization** ensures efficient order placement

Master these trigger-based order strategies to build sophisticated trading systems that respond intelligently to market momentum and mean reversion opportunities.