# Stop Orders & Market-If-Touched

Learn breakout and mean reversion strategies using stop orders and market-if-touched (MIT) orders for systematic trading approaches.

## Learning Objectives

By the end of this guide, you will:

- Implement breakout strategies with stop orders
- Design mean reversion systems with MIT orders
- Create adaptive trigger mechanisms
- Build momentum and reversal detection systems
- Handle order triggers and execution management

## Stop Orders for Breakout Strategies

Stop orders excel at capturing momentum when price breaks through key levels.

### Basic Breakout Implementation

```python
import asyncio
from decimal import Decimal
from datetime import datetime, timedelta
from fivetwenty import AsyncClient


async def breakout_stop_strategy() -> Any:
    """Implement basic breakout strategy using stop orders."""
    async with AsyncClient() as client:
        # Define breakout levels
        resistance_level = Decimal("1.0900")  # EUR/USD resistance
        support_level = Decimal("1.0800")     # EUR/USD support

        # Place stop orders above resistance and below support
        # Buy stop above resistance (bullish breakout)
        buy_stop_response = await client.orders.post_stop_order(
            account_id="your_account_id",
            instrument="EUR_USD",
            units=10000,  # Long position
            price=resistance_level + Decimal("0.0005"),  # 0.5 pips above
            time_in_force="GTC"
        )

        # Sell stop below support (bearish breakout)
        sell_stop_response = await client.orders.post_stop_order(
            account_id="your_account_id",
            instrument="EUR_USD",
            units=-10000,  # Short position
            price=support_level - Decimal("0.0005"),  # 0.5 pips below
            time_in_force="GTC"
        )

        print(f"Breakout stops placed:")
        print(f"Buy stop: {resistance_level + Decimal('0.0005')}")
        print(f"Sell stop: {support_level - Decimal('0.0005')}")

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
    """Calculate breakout levels based on recent price action."""
    async with AsyncClient() as client:
        # Get recent price data (simplified - you'd use a proper data source)
        # For this example, we'll simulate price analysis

        # Calculate Average True Range (ATR) for volatility
        atr_period = 14
        current_atr = Decimal("0.0045")  # Example 4.5 pip ATR

        # Get current price
        pricing = await client.pricing.get_pricing(
            account_id="your_account_id",
            instruments=["EUR_USD"]
        )

        current_price = Decimal(pricing.prices[0].asks[0].price)

        # Dynamic breakout levels based on ATR
        breakout_buffer = current_atr * Decimal("0.5")  # 50% of ATR

        upper_breakout = current_price + breakout_buffer
        lower_breakout = current_price - breakout_buffer

        # Place adaptive stop orders
        buy_stop = await client.orders.post_stop_order(
            account_id="your_account_id",
            instrument="EUR_USD",
            units=15000,
            price=upper_breakout,
            time_in_force="GTC"
        )

        sell_stop = await client.orders.post_stop_order(
            account_id="your_account_id",
            instrument="EUR_USD",
            units=-15000,
            price=lower_breakout,
            time_in_force="GTC"
        )

        print(f"Dynamic breakouts (ATR: {current_atr}):")
        print(f"Upper: {upper_breakout}, Lower: {lower_breakout}")

        return buy_stop, sell_stop
```

### Multi-Timeframe Breakout System

Combine multiple timeframe signals for robust breakouts:

```python
from decimal import Decimal

from fivetwenty import AsyncClient



class MultiTimeframeBreakout:
    def __init__(self, client: AsyncClient, account_id: str) -> None:
        self.client = client
        self.account_id = account_id
        self.active_stops = []

    async def analyze_breakout_levels(self, instrument: str) -> Any:
        """Analyze breakout levels across multiple timeframes."""
        # This would integrate with your data provider
        # For demonstration, we'll use simulated levels

        breakout_levels = {
            "15min": {
                "resistance": Decimal("1.0890"),
                "support": Decimal("1.0810"),
            },
            "1hour": {
                "resistance": Decimal("1.0920"),
                "support": Decimal("1.0780"),
            },
            "4hour": {
                "resistance": Decimal("1.0950"),
                "support": Decimal("1.0750"),
            },
        }

        return breakout_levels

    async def place_layered_breakout_stops(self, instrument: str) -> Any:
        """Place stop orders at multiple timeframe levels."""
        levels = await self.analyze_breakout_levels(instrument)

        # Place stops at each timeframe level with scaled position sizes
        timeframe_weights = {"15min": 0.3, "1hour": 0.5, "4hour": 0.7}

        for timeframe, level_data in levels.items():
            weight = timeframe_weights[timeframe]
            base_units = 10000
            scaled_units = int(base_units * weight)

            # Bullish breakout stop
            buy_stop = await self.client.orders.post_stop_order(
                account_id=self.account_id,
                instrument=instrument,
                units=scaled_units,
                price=level_data["resistance"] + Decimal("0.0005"),
                time_in_force="GTC",
            )

            # Bearish breakout stop
            sell_stop = await self.client.orders.post_stop_order(
                account_id=self.account_id,
                instrument=instrument,
                units=-scaled_units,
                price=level_data["support"] - Decimal("0.0005"),
                time_in_force="GTC",
            )

            self.active_stops.extend([
                buy_stop.order_create_transaction.id,
                sell_stop.order_create_transaction.id,
            ])

            print(f"{timeframe} breakout stops: {scaled_units} units")

        return self.active_stops
```

## MIT Orders for Mean Reversion

Market-If-Touched orders are ideal for mean reversion strategies where you expect price to return to average levels.

### Basic Mean Reversion Setup

```python
from decimal import Decimal
from fivetwenty import AsyncClient


async def mean_reversion_mit_strategy() -> Any:
    """Implement mean reversion using MIT orders."""
    async with AsyncClient() as client:
        # Define mean reversion levels
        mean_price = Decimal("1.0850")  # 20-period moving average
        reversion_distance = Decimal("0.0030")  # 3 pips from mean

        upper_reversion = mean_price + reversion_distance
        lower_reversion = mean_price - reversion_distance

        # MIT orders for mean reversion entries
        # Sell MIT when price goes too high (expect reversion down)
        sell_mit_response = await client.orders.post_market_if_touched_order(
            account_id="your_account_id",
            instrument="EUR_USD",
            units=-10000,  # Short position
            price=upper_reversion,
            time_in_force="GTC"
        )

        # Buy MIT when price goes too low (expect reversion up)
        buy_mit_response = await client.orders.post_market_if_touched_order(
            account_id="your_account_id",
            instrument="EUR_USD",
            units=10000,  # Long position
            price=lower_reversion,
            time_in_force="GTC"
        )

        print(f"Mean reversion MITs:")
        print(f"Sell MIT: {upper_reversion} (fade strength)")
        print(f"Buy MIT: {lower_reversion} (fade weakness)")

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
    """Mean reversion strategy using Bollinger Band levels."""
    async with AsyncClient() as client:
        # Simplified Bollinger Band calculation
        # (In practice, you'd calculate from historical data)

        sma_20 = Decimal("1.0850")  # 20-period simple moving average
        std_dev = Decimal("0.0025")  # Standard deviation
        bb_multiplier = Decimal("2.0")  # Standard 2-sigma bands

        upper_band = sma_20 + (std_dev * bb_multiplier)
        lower_band = sma_20 - (std_dev * bb_multiplier)

        # MIT orders at Bollinger Band extremes
        # Sell when price touches upper band (overbought)
        sell_mit = await client.orders.post_market_if_touched_order(
            account_id="your_account_id",
            instrument="EUR_USD",
            units=-15000,
            price=upper_band,
            time_in_force="GTC"
        )

        # Buy when price touches lower band (oversold)
        buy_mit = await client.orders.post_market_if_touched_order(
            account_id="your_account_id",
            instrument="EUR_USD",
            units=15000,
            price=lower_band,
            time_in_force="GTC"
        )

        print(f"Bollinger Band reversion:")
        print(f"Upper band MIT: {upper_band}")
        print(f"Lower band MIT: {lower_band}")
        print(f"Middle (SMA): {sma_20}")

        return sell_mit, buy_mit
```

### RSI-Based Mean Reversion

Combine MIT orders with RSI signals for enhanced mean reversion:

```python
from decimal import Decimal

from fivetwenty import AsyncClient



class RSIMeanReversion:
    def __init__(self, client: AsyncClient, account_id: str) -> None:
        self.client = client
        self.account_id = account_id
        self.rsi_period = 14
        self.overbought_level = 70
        self.oversold_level = 30

    async def calculate_rsi_levels(self, instrument: str) -> Any:
        """Calculate price levels corresponding to RSI extremes."""
        # This would use your preferred data source for RSI calculation
        # For demonstration, we'll use simulated RSI-based price levels

        current_rsi = 65  # Example current RSI

        # Price levels that correspond to RSI extremes
        rsi_price_levels = {
            "overbought_price": Decimal("1.0920"),  # Price at RSI 70
            "oversold_price": Decimal("1.0780"),    # Price at RSI 30
            "current_rsi": current_rsi,
        }

        return rsi_price_levels

    async def place_rsi_reversion_orders(self, instrument: str) -> Any:
        """Place MIT orders at RSI extreme levels."""
        rsi_data = await self.calculate_rsi_levels(instrument)

        # Only place orders if RSI is in middle range
        if 35 < rsi_data["current_rsi"] < 65:

            # Sell MIT at overbought level
            sell_mit = await self.client.orders.post_market_if_touched_order(
                account_id=self.account_id,
                instrument=instrument,
                units=-12000,
                price=rsi_data["overbought_price"],
                time_in_force="GTC",
            )

            # Buy MIT at oversold level
            buy_mit = await self.client.orders.post_market_if_touched_order(
                account_id=self.account_id,
                instrument=instrument,
                units=12000,
                price=rsi_data["oversold_price"],
                time_in_force="GTC",
            )

            print(f"RSI reversion orders placed:")
            print(f"Sell MIT @ RSI 70: {rsi_data['overbought_price']}")
            print(f"Buy MIT @ RSI 30: {rsi_data['oversold_price']}")

            return sell_mit, buy_mit
        else:
            print(f"RSI {rsi_data['current_rsi']} not in neutral range - no orders placed")
            return None, None
```

## Adaptive Trigger Mechanisms

### Volatility-Adjusted Triggers

Adjust trigger distances based on market volatility:

```python
from decimal import Decimal
from fivetwenty import AsyncClient


async def volatility_adjusted_triggers() -> Any:
    """Adjust order triggers based on current market volatility."""
    async with AsyncClient() as client:
        # Calculate current volatility (simplified)
        current_volatility = Decimal("0.0040")  # Example 4.0 pip volatility
        base_trigger_distance = Decimal("0.0020")  # Base 2.0 pip distance

        # Adjust trigger distance based on volatility
        volatility_multiplier = current_volatility / Decimal("0.0030")  # Normalize to 3.0 pip base
        adjusted_distance = base_trigger_distance * volatility_multiplier

        # Ensure reasonable bounds
        min_distance = Decimal("0.0010")  # Minimum 1.0 pip
        max_distance = Decimal("0.0050")  # Maximum 5.0 pips

        trigger_distance = max(min_distance, min(max_distance, adjusted_distance))

        # Get current price for reference
        pricing = await client.pricing.get_pricing(
            account_id="your_account_id",
            instruments=["EUR_USD"]
        )

        current_price = Decimal(pricing.prices[0].asks[0].price)

        # Place volatility-adjusted stop orders
        buy_stop = await client.orders.post_stop_order(
            account_id="your_account_id",
            instrument="EUR_USD",
            units=10000,
            price=current_price + trigger_distance,
            time_in_force="GTC"
        )

        sell_stop = await client.orders.post_stop_order(
            account_id="your_account_id",
            instrument="EUR_USD",
            units=-10000,
            price=current_price - trigger_distance,
            time_in_force="GTC"
        )

        print(f"Volatility-adjusted triggers:")
        print(f"Distance: {trigger_distance} (volatility: {current_volatility})")
        print(f"Buy stop: {current_price + trigger_distance}")
        print(f"Sell stop: {current_price - trigger_distance}")

        return buy_stop, sell_stop
```

### Time-Based Trigger Adjustments

Modify trigger sensitivity based on time of day:

```python
from decimal import Decimal
from fivetwenty import AsyncClient
from datetime import datetime



async def time_based_trigger_strategy() -> Any:
    """Adjust trigger sensitivity based on trading session."""
    from datetime import datetime, timezone

    async with AsyncClient() as client:
        current_hour = datetime.now(timezone.utc).hour

        # Define session characteristics
        if 8 <= current_hour <= 17:  # London session
            session = "london"
            trigger_multiplier = Decimal("1.2")  # More aggressive
            position_size = 15000
        elif 13 <= current_hour <= 22:  # New York session
            session = "new_york"
            trigger_multiplier = Decimal("1.0")  # Standard
            position_size = 12000
        elif 23 <= current_hour <= 8:  # Asia session
            session = "asia"
            trigger_multiplier = Decimal("0.8")  # More conservative
            position_size = 8000
        else:  # Overlap or quiet periods
            session = "overlap"
            trigger_multiplier = Decimal("1.5")  # Very aggressive
            position_size = 18000

        base_distance = Decimal("0.0025")  # 2.5 pips base
        session_distance = base_distance * trigger_multiplier

        pricing = await client.pricing.get_pricing(
            account_id="your_account_id",
            instruments=["EUR_USD"]
        )

        current_price = Decimal(pricing.prices[0].asks[0].price)

        # Place session-specific orders
        buy_stop = await client.orders.post_stop_order(
            account_id="your_account_id",
            instrument="EUR_USD",
            units=position_size,
            price=current_price + session_distance,
            time_in_force="GTC"
        )

        print(f"{session.title()} session strategy:")
        print(f"Trigger distance: {session_distance}")
        print(f"Position size: {position_size}")
        print(f"Buy stop: {current_price + session_distance}")

        return buy_stop
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
        """Place stop orders that require momentum confirmation."""

        # Get current price action
        pricing = await self.client.pricing.get_pricing(
            account_id=self.account_id,
            instruments=[instrument]
        )

        current_price = Decimal(pricing.prices[0].asks[0].price)

        # Define key levels
        resistance = Decimal("1.0900")
        support = Decimal("1.0800")

        # Calculate momentum-confirmed trigger levels
        # Require price to move beyond level + momentum threshold
        bullish_trigger = resistance + self.momentum_threshold
        bearish_trigger = support - self.momentum_threshold

        # Place momentum-confirmed stop orders
        buy_stop = await self.client.orders.post_stop_order(
            account_id=self.account_id,
            instrument=instrument,
            units=12000,
            price=bullish_trigger,
            time_in_force="GTC"
        )

        sell_stop = await self.client.orders.post_stop_order(
            account_id=self.account_id,
            instrument=instrument,
            units=-12000,
            price=bearish_trigger,
            time_in_force="GTC"
        )

        print(f"Momentum-confirmed breakouts:")
        print(f"Bullish trigger: {bullish_trigger} (resistance + {self.momentum_threshold})")
        print(f"Bearish trigger: {bearish_trigger} (support - {self.momentum_threshold})")

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

## Advanced Order Combinations

### Stop-MIT Combination Strategy

Combine stop and MIT orders for comprehensive market coverage:

```python
from decimal import Decimal
from fivetwenty import AsyncClient


async def stop_mit_combination_strategy() -> Any:
    """Use both stop and MIT orders for complete market approach."""
    async with AsyncClient() as client:
        # Current market analysis
        current_price = Decimal("1.0850")
        volatility = Decimal("0.0035")  # 3.5 pip volatility

        # Define strategy levels
        breakout_distance = volatility * Decimal("1.5")  # 1.5x volatility
        reversion_distance = volatility * Decimal("0.8")  # 0.8x volatility

        # Breakout levels (stop orders)
        upper_breakout = current_price + breakout_distance
        lower_breakout = current_price - breakout_distance

        # Mean reversion levels (MIT orders)
        upper_reversion = current_price + reversion_distance
        lower_reversion = current_price - reversion_distance

        # Place stop orders for breakouts
        buy_stop = await client.orders.post_stop_order(
            account_id="your_account_id",
            instrument="EUR_USD",
            units=10000,
            price=upper_breakout,
            time_in_force="GTC"
        )

        sell_stop = await client.orders.post_stop_order(
            account_id="your_account_id",
            instrument="EUR_USD",
            units=-10000,
            price=lower_breakout,
            time_in_force="GTC"
        )

        # Place MIT orders for mean reversion
        sell_mit = await client.orders.post_market_if_touched_order(
            account_id="your_account_id",
            instrument="EUR_USD",
            units=-8000,  # Smaller size for reversion
            price=upper_reversion,
            time_in_force="GTC"
        )

        buy_mit = await client.orders.post_market_if_touched_order(
            account_id="your_account_id",
            instrument="EUR_USD",
            units=8000,
            price=lower_reversion,
            time_in_force="GTC"
        )

        print(f"Dual strategy deployed:")
        print(f"Breakout stops: {upper_breakout} / {lower_breakout}")
        print(f"Reversion MITs: {upper_reversion} / {lower_reversion}")

        return {
            "breakout_orders": [buy_stop, sell_stop],
            "reversion_orders": [sell_mit, buy_mit]
        }
```

## Order Trigger Management

### Intelligent Order Cancellation

Cancel orders based on changing market conditions:

```python
from datetime import datetime
from decimal import Decimal
from fivetwenty import AsyncClient


async def intelligent_order_management() -> Any:
    """Manage order lifecycle based on market conditions."""
    async with AsyncClient() as client:
        # Place initial orders
        initial_orders = await stop_mit_combination_strategy()

        # Monitor and manage orders
        monitoring_duration = 3600  # 1 hour
        check_interval = 60  # Check every minute

        start_time = datetime.utcnow()

        while (datetime.utcnow() - start_time).seconds < monitoring_duration:
            # Get current market conditions
            pricing = await client.pricing.get_pricing(
                account_id="your_account_id",
                instruments=["EUR_USD"]
            )

            current_price = Decimal(pricing.prices[0].asks[0].price)
            current_spread = (
                Decimal(pricing.prices[0].asks[0].price) -
                Decimal(pricing.prices[0].bids[0].price)
            )

            # Cancel orders if market conditions change significantly
            if current_spread > Decimal("0.0005"):  # Spread too wide
                print("Cancelling orders due to wide spreads")

                # Cancel all pending orders
                for order_group in initial_orders.values():
                    for order in order_group:
                        try:
                            await client.orders.cancel_order(
                                account_id="your_account_id",
                                order_id=order.order_create_transaction.id
                            )
                        except:
                            pass  # Order might already be filled/cancelled

                break

            await asyncio.sleep(check_interval)

        print("Order management cycle completed")
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
- Use volatility-adjusted trigger distances
- Implement momentum confirmation for quality breakouts
- Consider time-based adjustments for session characteristics

### MIT Order Usage
- Target mean reversion at statistical extremes
- Combine with technical indicators (RSI, Bollinger Bands)
- Use smaller position sizes than breakout strategies
- Monitor reversion quality after trigger

### Trigger Management
- Validate market conditions before placement
- Implement intelligent cancellation rules
- Monitor order quality after execution
- Use appropriate position sizing for strategy type

### System Design
- Batch related orders for efficiency
- Implement comprehensive error handling
- Monitor and adjust based on market regime
- Combine complementary strategies for market coverage

## Next Steps

Advance your order management capabilities:

- **[Dynamic Order Management](dynamic-management.md)** - Trailing stops and adaptive sizing
- **[Automated Order Systems](automated-systems.md)** - Rule-based management and monitoring
- **[Order Strategies & Combinations](order-strategies.md)** - Bracket orders and advanced techniques

## Key Takeaways

1. **Stop orders** capture momentum and breakouts effectively
2. **MIT orders** excel at mean reversion and profit-taking
3. **Adaptive triggers** improve strategy performance across market conditions
4. **Momentum confirmation** reduces false breakout signals
5. **Intelligent management** optimizes order lifecycle and performance
6. **Combined strategies** provide comprehensive market coverage

Master these trigger-based order strategies to build sophisticated trading systems that respond intelligently to market momentum and mean reversion opportunities.