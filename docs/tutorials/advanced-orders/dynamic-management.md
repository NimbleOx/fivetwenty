# Dynamic Order Management

Master trailing stops, scaling strategies, and adaptive position management for professional trading systems.

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

```python
import asyncio
from decimal import Decimal

from dotenv import load_dotenv

from fivetwenty import AsyncClient
from fivetwenty.models import InstrumentName, TrailingStopLossOrderRequest

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
        assert market_order.order_fill_transaction is not None
        assert market_order.order_fill_transaction.trade_opened is not None
        trade_id = market_order.order_fill_transaction.trade_opened.trade_id
        fill_price = Decimal(str(market_order.order_fill_transaction.price))

        print("✓ Position opened:")
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

        print("✓ Trailing stop attached:")
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
            f"  → Stop automatically trails to {fill_price + Decimal('0.0020') - trailing_distance:.5f}"
        )
        print(f"\n  If price rises to {fill_price + Decimal('0.0050'):.5f} (+50 pips):")
        print(
            f"  → Stop automatically trails to {fill_price + Decimal('0.0050') - trailing_distance:.5f}"
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
            print(f"\n✓ Trade {trade_id} confirmed with trailing stop:")
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

Adjust trail distance based on market volatility:

```python
from decimal import Decimal
from fivetwenty import AsyncClient


async def volatility_adjusted_trailing() -> Any:
    """Implement volatility-adaptive trailing stops for market-responsive risk management."""

    # Step 1: Initialize client for volatility-adjusted trailing implementation
    async with AsyncClient() as client:
        print(f"Data Implementing Volatility-Adjusted Trailing Stop")

        # Step 2: Calculate current market volatility using ATR (Average True Range)
        # ATR measures market volatility over recent periods
        current_atr = Decimal("0.0045")      # Current 4.5 pip ATR (would be calculated from real data)
        base_trail_distance = Decimal("0.0020")  # Base 2.0 pip trail distance
        baseline_atr = Decimal("0.0030")     # Baseline 3.0 pip ATR for normalization

        print(f"   Current ATR: {current_atr} ({current_atr * 10000:.1f} pips)")
        print(f"   Baseline ATR: {baseline_atr} ({baseline_atr * 10000:.1f} pips)")
        print(f"   Base Trail Distance: {base_trail_distance} ({base_trail_distance * 10000:.1f} pips)")

        # Step 3: Calculate volatility multiplier for trail adjustment
        # Higher volatility requires wider trails to avoid premature stops
        volatility_multiplier = current_atr / baseline_atr
        adjusted_trail = base_trail_distance * volatility_multiplier

        print(f"   Volatility Multiplier: {volatility_multiplier:.2f}")
        print(f"   Raw Adjusted Trail: {adjusted_trail} ({adjusted_trail * 10000:.1f} pips)")

        # Step 4: Apply reasonable bounds to prevent extreme trail distances
        # Bounds ensure trailing stops remain practical regardless of volatility
        min_trail = Decimal("0.0015")        # Minimum 1.5 pips (prevents overly tight trails)
        max_trail = Decimal("0.0060")        # Maximum 6.0 pips (prevents overly wide trails)
        trail_distance = max(min_trail, min(max_trail, adjusted_trail))

        print(f"   Final Trail Distance: {trail_distance} ({trail_distance * 10000:.1f} pips)")
        if trail_distance == min_trail:
            print(f"   ⚠️ Trail capped at minimum bound")
        elif trail_distance == max_trail:
            print(f"   ⚠️ Trail capped at maximum bound")

        # Step 5: Calculate initial stop level based on current market price
        current_price = Decimal("1.0875")   # Current market price (would be from real data)
        initial_stop = current_price - trail_distance

        print(f"\nTarget Position Setup:")
        print(f"   Current Price: {current_price}")
        print(f"   Initial Stop: {initial_stop}")
        print(f"   Initial Risk: {trail_distance} ({trail_distance * 10000:.1f} pips)")

        # Step 6: Create volatility-adjusted trailing stop system
        trail_manager = TrailingStopManager(client, "your_account_id")
        config = await trail_manager.create_trailing_stop(
            position_id="pos_123",            # Unique position identifier
            initial_stop=initial_stop,        # Calculated initial stop level
            trail_distance=trail_distance,    # Volatility-adjusted trail distance
            instrument="EUR_USD"              # Major currency pair
        )

        print(f"\nSuccess Volatility-Adjusted Trailing Stop Created")
        print(f"   Adapts to market conditions automatically")
        print(f"   Trail distance adjusts with volatility changes")

        return config
```

#### Accelerated Trailing System

Tighten trail distance as profits increase:

<!-- fragment: Demo accelerated trailing with undefined Any type -->
```python
from decimal import Decimal

from fivetwenty import AsyncClient



class AcceleratedTrailing:
    def __init__(self, client: AsyncClient, account_id: str) -> None:
        self.client = client
        self.account_id = account_id

    async def create_accelerated_trail(self, position_id: str, entry_price: Decimal, initial_trail: Decimal, instrument: str) -> Any:
        """Create trailing stop that tightens as profits increase."""

        config = {
            "position_id": position_id,
            "instrument": instrument,
            "entry_price": entry_price,
            "initial_trail": initial_trail,
            "current_trail": initial_trail,
            "profit_thresholds": [
                {"profit_pips": Decimal("0.0020"), "trail_pips": initial_trail * Decimal("0.8")},
                {"profit_pips": Decimal("0.0040"), "trail_pips": initial_trail * Decimal("0.6")},
                {"profit_pips": Decimal("0.0060"), "trail_pips": initial_trail * Decimal("0.4")},
            ],
        }

        return config

    async def update_accelerated_trail(self, config: dict) -> Any:
        """Update trail distance based on profit levels."""
        # Get current price
        pricing = await self.client.pricing.get_pricing(
            account_id=self.account_id,
            instruments=[config["instrument"]],
        )

        current_price = Decimal(pricing.prices[0].bids[0].price)
        current_profit = current_price - config["entry_price"]

        # Determine appropriate trail distance based on profit
        new_trail = config["initial_trail"]

        for threshold in config["profit_thresholds"]:
            if current_profit >= threshold["profit_pips"]:
                new_trail = threshold["trail_pips"]

        # Update trail distance if it has changed
        if new_trail != config["current_trail"]:
            config["current_trail"] = new_trail
            print(f"Trail accelerated to {new_trail} at profit {current_profit}")

        return new_trail
```

## Position Scaling Strategies

Position scaling strategies systematically build or reduce exposure based on price action and market confirmation. Scale-in approaches add to winning positions as they prove themselves, averaging up into strength rather than weakness. Scale-out strategies take partial profits at different levels, reducing risk while maintaining exposure to continued favorable moves. Both approaches improve average entry prices and optimize risk-adjusted returns compared to all-or-nothing position sizing.

The SDK's order placement methods (`client.orders.post_limit_order()`, `client.orders.post_market_order()`) enable precise scaling implementations by placing orders at calculated intervals. You'll learn to build scale-in pyramids that add positions as price confirms your thesis, and scale-out systems that systematically reduce exposure while locking in profits at predetermined levels.

### Scale-In Strategy Implementation

```python
from decimal import Decimal

from fivetwenty import AsyncClient



class ScaleInStrategy:
    """Systematic position building through multiple entry levels for improved average pricing."""

    def __init__(self, client: AsyncClient, account_id: str) -> None:
        """Initialize scale-in strategy with FiveTwenty client and tracking systems."""
        self.client = client              # Authenticated FiveTwenty client for order management
        self.account_id = account_id      # Target account for scale-in execution
        self.scale_levels = []            # List of configured scale-in levels
        self.filled_levels = []           # Track successfully filled scale levels

    async def setup_scale_in_levels(
        self,
        instrument: str,
        base_price: Decimal,
        total_units: int,
        num_levels: int = 4,
        level_spacing: Decimal = Decimal("0.0020"),
    ):
        """Configure multiple scale-in entry levels below current market price."""

        # Step 1: Calculate position sizing for systematic scaling
        # Equal distribution ensures balanced exposure across levels
        units_per_level = total_units // num_levels
        print(f"Analysis Setting up {num_levels} scale-in levels for {instrument}")
        print(f"   Total position target: {total_units:,} units")
        print(f"   Units per level: {units_per_level:,} units")
        print(f"   Level spacing: {level_spacing} ({level_spacing * 10000:.0f} pips)")

        # Step 2: Create scale-in levels with descending prices
        # Lower prices provide better average entry cost
        for i in range(num_levels):
            # Step 3: Calculate price for each scale level
            # Each level is spaced below the previous level
            level_price = base_price - (level_spacing * (i + 1))

            # Step 4: Configure scale level parameters
            scale_level = {
                "level": i + 1,              # Level number for identification
                "price": level_price,        # Entry price for this level
                "units": units_per_level,    # Position size for this level
                "order_id": None,            # Order ID (set when placed)
                "filled": False,             # Fill status tracking
            }

            self.scale_levels.append(scale_level)
            print(f"   Level {i + 1}: {units_per_level:,} units at {level_price}")

        # Step 5: Place all scale-in limit orders simultaneously
        # Simultaneous placement ensures all levels are active
        print(f"\nStarting Placing scale-in orders...")
        await self._place_scale_orders(instrument)

    async def _place_scale_orders(self, instrument: str) -> Any:
        """Place limit orders for all configured scale-in levels."""

        # Step 1: Iterate through all scale levels for order placement
        # Sequential placement ensures proper order tracking
        for level in self.scale_levels:
            if not level["filled"]:
                # Step 2: Place limit order for current scale level
                # Limit orders ensure price control for each entry
                response = await self.client.orders.post_limit_order(
                    account_id=self.account_id,       # Account for order execution
                    instrument=instrument,            # Currency pair for scaling
                    units=level["units"],             # Position size for this level
                    price=level["price"],             # Specific entry price
                    time_in_force="GTC",              # Good Till Cancelled
                )

                # Step 3: Store order ID for monitoring and management
                level["order_id"] = response.order_create_transaction.id
                print(f"   Success Level {level['level']}: {level['units']:,} units @ {level['price']} (Order: {level['order_id']})")

        print(f"\nTarget Scale-in strategy active with {len(self.scale_levels)} levels")
        print(f"   Orders will fill as market reaches each level")
        print(f"   Average cost improves with each lower-level fill")

    async def monitor_scale_fills(self, instrument: str) -> Any:
        """Monitor scale-in orders and adjust strategy as they fill."""

        while len(self.filled_levels) < len(self.scale_levels):
            for level in self.scale_levels:
                if not level["filled"] and level["order_id"]:
                    # Check order status
                    order = await self.client.orders.get_order(
                        account_id=self.account_id,
                        order_id=level["order_id"],
                    )

                    if order.state == "FILLED":
                        level["filled"] = True
                        self.filled_levels.append(level)

                        print(f"Scale level {level['level']} filled at {level['price']}")

                        # Implement dynamic stop adjustment after each fill
                        await self._adjust_stops_after_fill(level, instrument)

            await asyncio.sleep(10)  # Check every 10 seconds

    async def _adjust_stops_after_fill(self, filled_level: dict, instrument: str) -> Any:
        """Adjust protective stops after a scale-in level fills."""

        # Calculate new average entry price
        total_units = sum(level["units"] for level in self.filled_levels)
        weighted_price = sum(
            level["price"] * level["units"] for level in self.filled_levels
        ) / total_units

        # Set stop below average entry
        stop_distance = Decimal("0.0030")  # 3.0 pip stop
        new_stop_price = weighted_price - stop_distance

        # Place/update stop order for accumulated position
        stop_response = await self.client.orders.post_stop_order(
            account_id=self.account_id,
            instrument=instrument,
            units=-total_units,  # Close entire accumulated position
            price=new_stop_price,
            time_in_force="GTC",
        )

        print(f"Updated stop: {new_stop_price} for {total_units} units (avg: {weighted_price})")
```

### Scale-Out Strategy Implementation

```python
from decimal import Decimal

from fivetwenty import AsyncClient



class ScaleOutStrategy:
    def __init__(self, client: AsyncClient, account_id: str) -> None:
        self.client = client
        self.account_id = account_id
        self.take_profit_levels = []

    async def setup_scale_out_levels(self, instrument: str, entry_price: Decimal, position_units: int, profit_targets: list) -> Any:
        """Set up multiple take-profit levels above entry price."""

        remaining_units = position_units

        for i, target_distance in enumerate(profit_targets):
            # Calculate units to close at this level
            if i == len(profit_targets) - 1:  # Last level
                level_units = remaining_units  # Close remainder
            else:
                level_units = position_units // len(profit_targets)
                remaining_units -= level_units

            target_price = entry_price + target_distance

            tp_level = {
                "level": i + 1,
                "price": target_price,
                "units": level_units,
                "distance": target_distance,
                "order_id": None,
                "filled": False,
            }

            self.take_profit_levels.append(tp_level)

        # Place all take-profit orders
        await self._place_take_profit_orders(instrument)

    async def _place_take_profit_orders(self, instrument: str) -> Any:
        """Place limit orders for all take-profit levels."""

        for level in self.take_profit_levels:
            response = await self.client.orders.post_limit_order(
                account_id=self.account_id,
                instrument=instrument,
                units=-level["units"],  # Negative to close long position
                price=level["price"],
                time_in_force="GTC",
            )

            level["order_id"] = response.order_create_transaction.id
            print(f"Take profit {level['level']}: {level['units']} @ {level['price']}")

    async def monitor_scale_out_fills(self) -> Any:
        """Monitor take-profit orders and adjust trailing stops."""

        filled_levels = 0

        while filled_levels < len(self.take_profit_levels):
            for level in self.take_profit_levels:
                if not level["filled"] and level["order_id"]:
                    order = await self.client.orders.get_order(
                        account_id=self.account_id,
                        order_id=level["order_id"],
                    )

                    if order.state == "FILLED":
                        level["filled"] = True
                        filled_levels += 1

                        print(f"Take profit {level['level']} hit: {level['price']}")

                        # Tighten trailing stop after each partial close
                        await self._tighten_trail_after_tp(level)

            await asyncio.sleep(15)  # Check every 15 seconds

    async def _tighten_trail_after_tp(self, filled_level: dict) -> Any:
        """Tighten trailing stop after take-profit level hit."""

        # Calculate tighter trail based on level hit
        trail_reduction = Decimal("0.0005") * filled_level["level"]  # 0.5 pips per level

        print(f"Tightening trail by {trail_reduction} after TP{filled_level['level']}")
        # Implementation would update the trailing stop manager
```

## Adaptive Position Management

Adaptive position management systems monitor market conditions in real-time and adjust order parameters dynamically to match current volatility, trend strength, and risk levels. Rather than using static rules, these systems calculate optimal position sizes, stop distances, and profit targets based on live market data like ATR (Average True Range), price momentum, and volatility metrics. This responsiveness ensures your trading system remains properly calibrated regardless of changing market regimes.

Using the SDK's pricing and order management endpoints together, you can build systems that fetch current market conditions with `client.pricing.get_pricing()`, calculate adaptive parameters, and update orders accordingly. The examples show complete implementations that adjust position sizing based on volatility, modify stop distances when market conditions change, and dynamically manage risk exposure as trends develop or deteriorate.

### Market Condition Adaptive System

```python
from decimal import Decimal
from fivetwenty import AsyncClient


class AdaptivePositionManager:
    """Intelligent position management that adapts to changing market conditions."""

    def __init__(self, client: AsyncClient, account_id: str) -> None:
        """Initialize adaptive manager with market regime tracking."""
        self.client = client              # Authenticated FiveTwenty client
        self.account_id = account_id      # Target account for management
        self.current_regime = "neutral"   # Current market regime classification

    async def analyze_market_conditions(self, instrument: str) -> Any:
        """Analyze current market conditions and adapt strategy parameters accordingly."""

        # Step 1: Retrieve current market data for condition analysis
        # Real-time data enables responsive strategy adaptation
        pricing = await self.client.pricing.get_pricing(
            account_id=self.account_id,       # Account context for pricing
            instruments=[instrument]          # Target instrument for analysis
        )

        # Step 2: Calculate current spread as market condition indicator
        # Spread indicates market liquidity and trading conditions
        current_spread = (
            Decimal(pricing.prices[0].asks[0].price) -   # Ask price (buy price)
            Decimal(pricing.prices[0].bids[0].price)    # Bid price (sell price)
        )

        print(f"Analysis Market Condition Analysis for {instrument}:")
        print(f"   Current Spread: {current_spread} ({current_spread * 10000:.1f} pips)")
        print(f"   Previous Regime: {self.current_regime}")

        # Step 3: Classify market regime based on spread characteristics
        # Different regimes require different strategy parameters

        # Step 4: Tight spread regime (high liquidity, low volatility)
        if current_spread < Decimal("0.0002"):  # Less than 0.2 pips
            if self.current_regime != "tight":
                print(f"   Green Regime Change: TIGHT SPREAD detected")
                self.current_regime = "tight"
                return await self._adapt_to_tight_conditions(instrument)

        # Step 5: Wide spread regime (low liquidity, high volatility)
        elif current_spread > Decimal("0.0005"):  # More than 0.5 pips
            if self.current_regime != "wide":
                print(f"   Red Regime Change: WIDE SPREAD detected")
                self.current_regime = "wide"
                return await self._adapt_to_wide_conditions(instrument)

        # Step 6: Normal spread regime (standard trading conditions)
        else:  # Between 0.2 and 0.5 pips
            if self.current_regime != "normal":
                print(f"   Yellow Regime Change: NORMAL CONDITIONS detected")
                self.current_regime = "normal"
                return await self._adapt_to_normal_conditions(instrument)

        # Step 7: No regime change detected
        print(f"   ⏩ No regime change - continuing with {self.current_regime} parameters")
        return None

    async def _adapt_to_tight_conditions(self, instrument: str) -> Any:
        """Optimize strategy parameters for tight spread (high liquidity) conditions."""
        print(f"Green Adapting to TIGHT SPREAD conditions")
        print(f"   Market characteristics: High liquidity, low volatility, precise execution")

        # Step 1: Configure parameters for tight spread environment
        # Tight spreads enable aggressive strategies with precise execution
        strategy_params = {
            "position_size_multiplier": Decimal("1.2"),  # 20% larger positions (low execution risk)
            "stop_distance": Decimal("0.0015"),         # Tighter 1.5 pip stops (precise execution)
            "take_profit_distance": Decimal("0.0025"),  # Closer 2.5 pip targets (frequent fills)
            "trail_distance": Decimal("0.0010")         # Tight 1.0 pip trailing (lock profits quickly)
        }

        print(f"   Position sizing: +20% (taking advantage of low execution risk)")
        print(f"   Stop distance: 1.5 pips (tight due to precise execution)")
        print(f"   Profit targets: 2.5 pips (frequent fills in liquid market)")
        print(f"   Trail distance: 1.0 pip (aggressive profit protection)")

        return strategy_params

    async def _adapt_to_wide_conditions(self, instrument: str) -> Any:
        """Optimize strategy parameters for wide spread (low liquidity) conditions."""
        print(f"Red Adapting to WIDE SPREAD conditions")
        print(f"   Market characteristics: Low liquidity, high volatility, execution risk")

        # Step 1: Configure conservative parameters for wide spread environment
        # Wide spreads require defensive strategies with larger buffers
        strategy_params = {
            "position_size_multiplier": Decimal("0.7"),  # 30% smaller positions (reduce execution risk)
            "stop_distance": Decimal("0.0040"),         # Wider 4.0 pip stops (account for volatility)
            "take_profit_distance": Decimal("0.0060"),  # Distant 6.0 pip targets (reduce noise)
            "trail_distance": Decimal("0.0030")         # Loose 3.0 pip trailing (avoid whipsaws)
        }

        print(f"   Position sizing: -30% (reducing exposure due to execution risk)")
        print(f"   Stop distance: 4.0 pips (wider due to volatility)")
        print(f"   Profit targets: 6.0 pips (avoiding market noise)")
        print(f"   Trail distance: 3.0 pips (preventing whipsaw exits)")

        return strategy_params

    async def _adapt_to_normal_conditions(self, instrument: str) -> Any:
        """Apply balanced strategy parameters for normal market conditions."""
        print(f"Yellow Adapting to NORMAL CONDITIONS")
        print(f"   Market characteristics: Standard liquidity, moderate volatility, balanced execution")

        # Step 1: Configure balanced parameters for normal market environment
        # Normal conditions allow for standard strategy parameters
        strategy_params = {
            "position_size_multiplier": Decimal("1.0"),  # Standard position sizing (baseline)
            "stop_distance": Decimal("0.0025"),         # Standard 2.5 pip stops (balanced protection)
            "take_profit_distance": Decimal("0.0040"),  # Standard 4.0 pip targets (reasonable expectations)
            "trail_distance": Decimal("0.0020")         # Standard 2.0 pip trailing (balanced profit capture)
        }

        print(f"   Position sizing: Baseline (standard risk exposure)")
        print(f"   Stop distance: 2.5 pips (balanced risk protection)")
        print(f"   Profit targets: 4.0 pips (reasonable profit expectations)")
        print(f"   Trail distance: 2.0 pips (balanced profit capture)")
        print(f"   Success Using proven parameters for stable market conditions")

        return strategy_params
```

### Dynamic Risk Adjustment

Adjust risk parameters based on account performance:

```python
from decimal import Decimal
from fivetwenty import AsyncClient


class DynamicRiskManager:
    def __init__(self, client: AsyncClient, account_id: str) -> None:
        self.client = client
        self.account_id = account_id
        self.base_risk_per_trade = Decimal("0.02")  # 2% base risk

    async def calculate_current_risk_budget(self) -> Any:
        """Calculate current risk budget based on account performance."""

        # Get account summary
        account = await self.client.accounts.get_account(
            account_id=self.account_id
        )

        current_balance = Decimal(account.balance)
        current_equity = Decimal(account.margin_available)  # Simplified

        # Calculate recent performance (would need historical data)
        # For this example, we'll simulate performance analysis

        recent_win_rate = Decimal("0.65")  # 65% win rate
        recent_drawdown = Decimal("0.03")  # 3% drawdown

        # Adjust risk based on performance
        if recent_win_rate > Decimal("0.70") and recent_drawdown < Decimal("0.02"):
            # Good performance: increase risk slightly
            risk_multiplier = Decimal("1.2")
        elif recent_win_rate < Decimal("0.50") or recent_drawdown > Decimal("0.05"):
            # Poor performance: reduce risk
            risk_multiplier = Decimal("0.7")
        else:
            # Normal performance: standard risk
            risk_multiplier = Decimal("1.0")

        adjusted_risk = self.base_risk_per_trade * risk_multiplier

        print(f"Risk adjusted: {adjusted_risk} (multiplier: {risk_multiplier})")
        return adjusted_risk

    async def calculate_position_size(
        self,
        instrument: str,
        entry_price: Decimal,
        stop_price: Decimal
    ) -> int:
        """Calculate position size based on dynamic risk budget."""

        # Get current risk budget
        risk_per_trade = await self.calculate_current_risk_budget()

        # Get account balance
        account = await self.client.accounts.get_account(
            account_id=self.account_id
        )

        account_balance = Decimal(account.balance)
        risk_amount = account_balance * risk_per_trade

        # Calculate position size
        stop_distance = abs(entry_price - stop_price)
        pip_value = Decimal("1.0")  # USD per pip for EUR/USD

        position_size = int(risk_amount / (stop_distance * pip_value))

        # Cap position size at reasonable limits
        max_position = 100000  # 10 standard lots maximum
        position_size = min(position_size, max_position)

        print(f"Dynamic position size: {position_size} (risk: {risk_per_trade})")
        return position_size
```

## Performance Monitoring and Optimization

Effective order management requires continuous performance monitoring to identify what's working and what needs adjustment. By tracking metrics like fill rates, slippage, order execution times, and profit/loss per order type, you gain insights into system efficiency and can optimize order placement strategies. Performance analytics reveal patterns like which order types perform best in different market conditions, optimal trigger distances, and timing factors that impact execution quality.

The SDK provides transaction history and order details through `client.transactions.get_transactions()` and `client.orders.get_order()`, enabling comprehensive performance analysis. The examples demonstrate building analytics systems that track order performance metrics, calculate execution statistics, and identify optimization opportunities in your order management workflows.

### Order Performance Analytics

<!-- fragment: Demo order performance tracking with undefined types -->
```python
from decimal import Decimal

from fivetwenty import AsyncClient



class OrderPerformanceAnalyzer:
    def __init__(self, client: AsyncClient, account_id: str) -> None:
        self.client = client
        self.account_id = account_id
        self.order_history = []

    async def track_order_performance(self, order_id: str, strategy_type: str) -> Any:
        """Track individual order performance metrics."""

        order = await self.client.orders.get_order(
            account_id=self.account_id,
            order_id=order_id,
        )

        if order.state == "FILLED":
            fill_data = {
                "order_id": order_id,
                "strategy_type": strategy_type,
                "fill_time": order.filling_transaction.time,
                "fill_price": Decimal(order.filling_transaction.price),
                "requested_price": Decimal(order.price),
                "slippage": Decimal(order.filling_transaction.price) - Decimal(order.price),
                "units": order.units,
            }

            self.order_history.append(fill_data)
            print(f"Order tracked: {order_id} slippage: {fill_data['slippage']}")

            return fill_data

    async def analyze_strategy_performance(self, strategy_type: str) -> Any:
        """Analyze performance metrics for a specific strategy type."""

        strategy_orders = [
            order for order in self.order_history
            if order["strategy_type"] == strategy_type
        ]

        if not strategy_orders:
            return None

        # Calculate performance metrics
        total_orders = len(strategy_orders)
        avg_slippage = sum(order["slippage"] for order in strategy_orders) / total_orders

        slippage_variance = sum(
            (order["slippage"] - avg_slippage) ** 2
            for order in strategy_orders
        ) / total_orders

        performance_metrics = {
            "strategy_type": strategy_type,
            "total_orders": total_orders,
            "average_slippage": avg_slippage,
            "slippage_variance": slippage_variance,
            "max_slippage": max(order["slippage"] for order in strategy_orders),
            "min_slippage": min(order["slippage"] for order in strategy_orders),
        }

        print(f"Strategy {strategy_type} performance:")
        print(f"  Avg slippage: {avg_slippage}")
        print(f"  Max slippage: {performance_metrics['max_slippage']}")

        return performance_metrics
```

## Best Practices Summary

### Trailing Stop Management
- Use volatility-adjusted trail distances
- Implement accelerated trailing for large profits
- Monitor and update trails regularly
- Consider market session characteristics

### Position Scaling
- Plan scale-in levels before position entry
- Adjust stops after each scale level fills
- Use scale-out for systematic profit taking
- Balance between risk and opportunity

### Adaptive Systems
- Monitor market conditions continuously
- Adjust strategy parameters based on regime
- Implement dynamic risk management
- Track and analyze performance metrics

### System Architecture
- Design modular, reusable components
- Implement comprehensive error handling
- Use asynchronous operations for efficiency
- Maintain detailed performance logs

## Next Steps

Continue building advanced order management capabilities:

- **[Order Strategies & Combinations](order-strategies.md)** - Bracket orders and advanced techniques
- **[Best Practices](../../guides/understanding/best-practices.md)** - Risk management and error handling

## Key Takeaways

1. **Trailing stops** protect profits while maintaining upside potential
2. **Position scaling** enables systematic risk and reward management
3. **Adaptive systems** respond intelligently to changing market conditions
4. **Dynamic risk management** adjusts to account performance and market regime
5. **Performance monitoring** enables continuous strategy improvement
6. **Modular design** supports flexible and maintainable trading systems

Master these dynamic management techniques to build sophisticated trading systems that adapt intelligently to market conditions while maintaining robust risk controls.