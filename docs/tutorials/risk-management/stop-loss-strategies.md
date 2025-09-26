# Stop Loss Strategies

!!! tip "🎯 Learning Goal"
    Master advanced stop loss techniques to protect capital while maximizing profit potential in different market conditions.

---

## Why Stop Losses Are Non-Negotiable

Stop losses are your insurance policy against catastrophic losses. They:

- **Limit downside risk** on every trade
- **Preserve capital** for future opportunities
- **Remove emotion** from loss-cutting decisions
- **Enable position sizing** calculations
- **Protect against** market gaps and black swan events

!!! warning "⚠️ Never Trade Without Stops"
    Every professional trader uses stop losses. The question isn't whether to use them, but which type to use and where to place them.

---

## Fixed Pip Stop Loss Strategy

The most straightforward approach - set stops at a fixed pip distance.

### Implementation

```python
from decimal import Decimal
from fivetwenty import AsyncClient, Environment
from fivetwenty.exceptions import FiveTwentyError, FiveTwentyErrorCode


"""Comprehensive module for trading operations."""
async def place_order_with_fixed_stop(account_id: str, instrument: str, units: int, stop_pips: Decimal, take_profit_pips: Decimal = None) -> Any:
    """Place order with fixed pip-based stop loss."""

    async with AsyncClient(token=TOKEN, account_id="your-account-id", environment=ENVIRONMENT) as client:
        try:
            # Get current price
            prices = await client.pricing.get_pricing(account_id=account_id, instruments=[instrument])

            if units > 0:  # Buy order
                entry_price = Decimal(str(prices[0].asks[0].price))
                pip_value = Decimal("0.01") if instrument.endswith('JPY') else Decimal("0.0001")
                stop_loss_price = entry_price - (stop_pips * pip_value)
                take_profit_price = entry_price + (take_profit_pips * pip_value) if take_profit_pips else None
            else:  # Sell order
                entry_price = Decimal(str(prices[0].bids[0].price))
                pip_value = Decimal("0.01") if instrument.endswith('JPY') else Decimal("0.0001")
                stop_loss_price = entry_price + (stop_pips * pip_value)
                take_profit_price = entry_price - (take_profit_pips * pip_value) if take_profit_pips else None

            print(f"🎯 Fixed Stop Order:")
            print(f"   Entry: ~{entry_price:.5f}")
            print(f"   Stop: {stop_loss_price:.5f} ({stop_pips} pips)")
            if take_profit_price:
                print(f"   Target: {take_profit_price:.5f} ({take_profit_pips} pips)")

            # Place order with stops
            order_params = {
                'account_id': account_id,
                'instrument': instrument,
                'units': units,
                'stop_loss_on_fill': {'price': f"{stop_loss_price:.5f}"}
            }

            if take_profit_price:
                order_params['take_profit_on_fill'] = {'price': f"{take_profit_price:.5f}"}

            response = await client.orders.post_market_order(**order_params)

            if response.order_fill_transaction:
                fill = response.order_fill_transaction
                print(f"✅ Order executed with protective stops!")
                print(f"   Fill Price: {fill.price}")
                print(f"   Trade ID: {fill.trade_opened.trade_id if fill.trade_opened else 'N/A'}")

                return fill

        except FiveTwentyError as e:
            print(f"❌ Stop order error: {e.message}")
            return None
```

### Fixed Pip Guidelines

| Instrument Type | Typical Stop Range | Rationale |
|----------------|-------------------|----------|
| Major Pairs (EUR/USD) | 15-30 pips | Lower volatility, tighter stops |
| Minor Pairs (EUR/GBP) | 20-40 pips | Moderate volatility |
| Exotic Pairs (USD/TRY) | 50-100 pips | Higher volatility, wider stops |
| JPY Pairs | 15-30 pips (150-300 points) | Adjust for JPY decimal places |

### Advantages
- **Straightforward to implement** and understand
- **Consistent across** all trades
- **Practical to backtest** and optimize

### Disadvantages
- **Ignores market volatility** changes
- **May be too tight** in volatile conditions
- **May be too wide** in calm conditions

---

## Percentage-Based Stop Loss Strategy

Set stops as a percentage of entry price - adapts to different price levels.

### Implementation

```python
from decimal import Decimal
from fivetwenty import AsyncClient, Environment
from fivetwenty.exceptions import FiveTwentyError, FiveTwentyErrorCode


"""Comprehensive module for trading operations."""
async def place_order_with_percentage_stop(account_id: str, instrument: str, units: int,
                                          stop_percentage: Decimal = Decimal("1.0")):
    """Place order with percentage-based stop loss."""

    async with AsyncClient(token=TOKEN, account_id="your-account-id", environment=ENVIRONMENT) as client:
        try:
            # Get current price
            prices = await client.pricing.get_pricing(account_id=account_id, instruments=[instrument])

            if units > 0:  # Buy order
                entry_price = Decimal(str(prices[0].asks[0].price))
                stop_loss_price = entry_price * (Decimal("1") - stop_percentage / Decimal("100"))
            else:  # Sell order
                entry_price = Decimal(str(prices[0].bids[0].price))
                stop_loss_price = entry_price * (Decimal("1") + stop_percentage / Decimal("100"))

            stop_distance = abs(entry_price - stop_loss_price)
            pip_value = Decimal("0.01") if instrument.endswith('JPY') else Decimal("0.0001")
            stop_pips = stop_distance / pip_value

            print(f"📊 Percentage Stop Order:")
            print(f"   Entry: ~{entry_price:.5f}")
            print(f"   Stop: {stop_loss_price:.5f} ({stop_percentage}% / {stop_pips:.1f} pips)")

            response = await client.orders.post_market_order(
                account_id=account_id,
                instrument=instrument,
                units=units,
                stop_loss_on_fill={'price': f"{stop_loss_price:.5f}"}
            )

            if response.order_fill_transaction:
                fill = response.order_fill_transaction
                print(f"✅ Percentage stop order executed!")
                return fill

        except FiveTwentyError as e:
            print(f"❌ Percentage stop error: {e.message}")
            return None
```

### Percentage Guidelines

| Risk Tolerance | Stop Percentage | Use Case |
|----------------|-----------------|----------|
| Conservative | 0.5-1.0% | Stable markets, low volatility |
| Moderate | 1.0-2.0% | Normal market conditions |
| Aggressive | 2.0-3.0% | High volatility, swing trading |

---

## ATR-Based Stop Loss Strategy

The most sophisticated approach - adapts to current market volatility.

### Implementation

```python
from decimal import Decimal
from fivetwenty import AsyncClient, Environment
from fivetwenty.models import CandlestickGranularity
import numpy as np


"""Comprehensive module for trading operations."""
class ATRStopCalculator:
    """Calculate stop losses based on Average True Range."""

    async def calculate_atr_stop(self, client: AsyncClient, instrument: str,
                               atr_multiplier: Decimal = Decimal("2.0"), periods: int = 14) -> dict:
        """Calculate ATR-based stop loss level."""

        try:
            # Get historical data
            candles = await client.instruments.get_instrument_candles(
                instrument=instrument,
                count=periods + 20,  # Extra data for stable calculation
                granularity=CandlestickGranularity.H4
            )

            if len(candles.candles) < periods + 1:
                print(f"❌ Insufficient data for ATR calculation")
                return None

            # Calculate True Range for each period
            true_ranges = []
            for i in range(1, len(candles.candles)):
                curr = candles.candles[i]
                prev = candles.candles[i-1]

                if curr.mid and prev.mid:
                    high = Decimal(str(curr.mid.h))
                    low = Decimal(str(curr.mid.l))
                    prev_close = Decimal(str(prev.mid.c))

                    # True Range = max(H-L, |H-Cp|, |L-Cp|)
                    tr1 = high - low
                    tr2 = abs(high - prev_close)
                    tr3 = abs(low - prev_close)

                    true_range = max(tr1, tr2, tr3)
                    true_ranges.append(true_range)

            # Calculate ATR (Simple Moving Average of True Range)
            atr = sum(true_ranges[-periods:]) / Decimal(str(periods))

            # Get current price
            current_price = Decimal(str(candles.candles[-1].mid.c))

            # Calculate stop distances
            atr_distance = atr * atr_multiplier

            pip_value = Decimal("0.01") if instrument.endswith('JPY') else Decimal("0.0001")
            atr_pips = atr_distance / pip_value

            result = {
                'current_price': current_price,
                'atr': atr,
                'atr_multiplier': atr_multiplier,
                'stop_distance': atr_distance,
                'stop_pips': atr_pips,
                'long_stop': current_price - atr_distance,
                'short_stop': current_price + atr_distance
            }

            print(f"📊 ATR Stop Calculation:")
            print(f"   Current Price: {current_price:.5f}")
            print(f"   ATR ({periods} periods): {atr:.5f}")
            print(f"   ATR Distance: {atr_distance:.5f} ({atr_pips:.1f} pips)")
            print(f"   Long Stop: {result['long_stop']:.5f}")
            print(f"   Short Stop: {result['short_stop']:.5f}")

            return result

        except Exception as e:
            print(f"❌ ATR calculation error: {e}")
            return None

async def place_order_with_atr_stop(account_id: str, instrument: str, units: int,
                                   atr_multiplier: Decimal = Decimal("2.0")):
    """Place order with ATR-based stop loss."""

    async with AsyncClient(token=TOKEN, environment=ENVIRONMENT) as client:
        calculator = ATRStopCalculator()

        # Calculate ATR stop
        atr_data = await calculator.calculate_atr_stop(client, instrument, atr_multiplier)

        if not atr_data:
            print("❌ Could not calculate ATR stop")
            return None

        # Determine stop price based on position direction
        if units > 0:  # Long position
            stop_price = atr_data['long_stop']
        else:  # Short position
            stop_price = atr_data['short_stop']

        try:
            response = await client.orders.post_market_order(
                account_id=account_id,
                instrument=instrument,
                units=units,
                stop_loss_on_fill={'price': f"{stop_price:.5f}"}
            )

            if response.order_fill_transaction:
                fill = response.order_fill_transaction
                print(f"✅ ATR stop order executed!")
                print(f"   Fill Price: {fill.price}")
                print(f"   ATR Stop: {stop_price:.5f}")
                return fill

        except FiveTwentyError as e:
            print(f"❌ ATR stop order error: {e.message}")
            return None
```

### ATR Multiplier Guidelines

| Market Condition | ATR Multiplier | Stop Distance | Purpose |
|------------------|----------------|---------------|----------|
| Trending Strong | 2.5-3.0 | Wider | Avoid getting stopped by normal retracements |
| Trending Weak | 2.0-2.5 | Moderate | Balance protection and trend participation |
| Ranging Market | 1.5-2.0 | Tighter | Quick exits from failed breakouts |
| High Volatility | 3.0+ | Extremely Wide | Account for volatility expansion |

---

## Trailing Stop Implementation

Capture more profit by moving stops in your favor as price moves.

### Basic Trailing Stop Manager

```python
from fivetwenty import AsyncClient, Environment
from decimal import Decimal



"""Comprehensive module for trading operations."""
class TrailingStopManager:
    """Advanced trailing stop management system."""

    def __init__(self, client: AsyncClient, account_id: str) -> None:
        self.client = client
        self.account_id = account_id
        self.active_trails = {}

    async def set_trailing_stop(self, trade_id: str, trail_distance_pips: Decimal, breakeven_pips: Decimal = None) -> Any:
        """Set trailing stop with optional break-even protection."""

        try:
            trade = await self.client.trades.get_trade(self.account_id, trade_id)

            if not trade:
                print(f"❌ Trade {trade_id} not found")
                return False

            entry_price = Decimal(str(trade.price))
            current_units = int(trade.current_units)
            instrument = trade.instrument

            # Store trailing parameters
            self.active_trails[trade_id] = {
                'instrument': instrument,
                'entry_price': entry_price,
                'units': current_units,
                'trail_distance_pips': trail_distance_pips,
                'breakeven_pips': breakeven_pips,
                'best_price': entry_price,
                'in_breakeven': False
            }

            print(f"📈 Trailing Stop Activated:")
            print(f"   Trade ID: {trade_id}")
            print(f"   Trail Distance: {trail_distance_pips} pips")
            if breakeven_pips:
                print(f"   Break-even at: {breakeven_pips} pips profit")

            return True

        except Exception as e:
            print(f"❌ Trailing stop error: {e}")
            return False

    async def update_trailing_stops(self) -> Any:
        """Update all active trailing stops."""

        for trade_id, trail_info in list(self.active_trails.items()):
            try:
                # Get current price
                instrument = trail_info['instrument']
                prices = await self.client.pricing.get_pricing(
                    account_id=self.account_id,
                    instruments=[instrument]
                )

                if trail_info['units'] > 0:  # Long position
                    current_price = Decimal(str(prices[0].bids[0].price))
                else:  # Short position
                    current_price = Decimal(str(prices[0].asks[0].price))

                # Update best price
                if trail_info['units'] > 0:
                    if current_price > trail_info['best_price']:
                        trail_info['best_price'] = current_price
                else:
                    if current_price < trail_info['best_price']:
                        trail_info['best_price'] = current_price

                # Calculate new stop level
                pip_value = Decimal("0.01") if instrument.endswith('JPY') else Decimal("0.0001")
                trail_distance = trail_info['trail_distance_pips'] * pip_value

                if trail_info['units'] > 0:  # Long position
                    new_stop = trail_info['best_price'] - trail_distance

                    # Check break-even condition
                    if (trail_info['breakeven_pips'] and
                        not trail_info['in_breakeven'] and
                        current_price >= trail_info['entry_price'] + (trail_info['breakeven_pips'] * pip_value)):

                        new_stop = trail_info['entry_price'] + (Decimal("5") * pip_value)  # 5 pip buffer
                        trail_info['in_breakeven'] = True
                        print(f"🛡️ Trade {trade_id} moved to break-even protection")

                else:  # Short position
                    new_stop = trail_info['best_price'] + trail_distance

                    if (trail_info['breakeven_pips'] and
                        not trail_info['in_breakeven'] and
                        current_price <= trail_info['entry_price'] - (trail_info['breakeven_pips'] * pip_value)):

                        new_stop = trail_info['entry_price'] - (Decimal("5") * pip_value)
                        trail_info['in_breakeven'] = True
                        print(f"🛡️ Trade {trade_id} moved to break-even protection")

                # Update stop loss if beneficial
                trade = await self.client.trades.get_trade(self.account_id, trade_id)

                if not trade:
                    # Trade closed - remove from tracking
                    del self.active_trails[trade_id]
                    continue

                if trade.stop_loss_order:
                    current_stop = Decimal(str(trade.stop_loss_order.price))

                    # Only update if new stop is better
                    should_update = False
                    if trail_info['units'] > 0 and new_stop > current_stop:
                        should_update = True
                    elif trail_info['units'] < 0 and new_stop < current_stop:
                        should_update = True

                    if should_update:
                        await self.client.trades.put_trade_orders(
                            account_id=self.account_id,
                            trade_id=trade_id,
                            stop_loss={'price': f"{new_stop:.5f}"}
                        )

                        print(f"📈 Trail updated for {trade_id}: {current_stop:.5f} → {new_stop:.5f}")

            except Exception as e:
                print(f"❌ Error updating trail for {trade_id}: {e}")

    async def monitor_trailing_stops(self, update_interval: int = 30) -> Any:
        """Continuously monitor and update trailing stops."""

        print(f"🔄 Starting trailing stop monitoring (interval: {update_interval}s)")

        while self.active_trails:
            await self.update_trailing_stops()
            await asyncio.sleep(update_interval)

        print(f"🛁 No more active trailing stops - monitoring stopped")

# Demo trailing stops
async def demo_trailing_stops(account_id: str) -> Any:
    """Demonstrate trailing stop functionality."""

    if not account_id:
        return

    async with AsyncClient(token=TOKEN, environment=ENVIRONMENT) as client:
        manager = TrailingStopManager(client, account_id)

        # Note: This requires an existing trade
        # In practice, you'd get the trade_id from a previous order
        print("💡 Trailing stop manager created")
        print("Use manager.set_trailing_stop(trade_id, trail_pips) to activate")

        return manager
```

### Trailing Stop Variations

#### 1. Fixed Distance Trailing
**Maintains constant pip distance from best price**
- Straightforward to implement
- Consistent protection level
- May be too mechanical for all conditions

#### 2. Percentage Trailing
**Maintains percentage distance from best price**
- Adapts to different price levels
- Good for long-term positions
- More logical for equity-like instruments

#### 3. ATR-Based Trailing
**Uses volatility-adjusted distances**
- Most sophisticated approach
- Adapts to market conditions
- Requires more computation

---

## Support and Resistance Stop Losses

Place stops based on key technical levels rather than arbitrary distances.

### Implementation

```python
from fivetwenty import AsyncClient
from decimal import Decimal



"""Comprehensive module for trading operations."""
class TechnicalStopCalculator:
    """Calculate stops based on support/resistance levels."""

    def __init__(self, buffer_pips: int = 5) -> None:
        self.buffer_pips = buffer_pips

    async def find_support_resistance_levels(self, client: AsyncClient,
                                           instrument: str) -> dict:
        """Find key support and resistance levels."""

        try:
            # Get recent price data
            candles = await client.instruments.get_instrument_candles(
                instrument=instrument,
                count=100,
                granularity=CandlestickGranularity.H4
            )

            if len(candles.candles) < 20:
                return None

            # Extract price data
            highs = [Decimal(str(c.mid.h)) for c in candles.candles if c.mid]
            lows = [Decimal(str(c.mid.l)) for c in candles.candles if c.mid]
            closes = [Decimal(str(c.mid.c)) for c in candles.candles if c.mid]

            current_price = closes[-1]

            # Simple support/resistance calculation
            # Find recent significant highs and lows
            recent_high = max(highs[-20:])  # Highest high in last 20 periods
            recent_low = min(lows[-20:])    # Lowest low in last 20 periods

            # Find price levels that have been tested multiple times
            price_levels = []

            # Look for levels within small ranges that price has touched multiple times
            for i in range(len(closes) - 10):
                level = closes[i]
                touches = 0

                # Count how many times price came close to this level
                for j in range(max(0, i-10), min(len(closes), i+10)):
                    if abs(closes[j] - level) < Decimal("0.0020"):  # Within 20 pips
                        touches += 1

                if touches >= 3:  # Level tested at least 3 times
                    price_levels.append(level)

            # Remove duplicates and sort
            price_levels = sorted(list(set([round(p, 5) for p in price_levels])))

            # Classify levels as support or resistance
            support_levels = [level for level in price_levels if level < current_price]
            resistance_levels = [level for level in price_levels if level > current_price]

            # Find nearest levels
            nearest_support = max(support_levels) if support_levels else recent_low
            nearest_resistance = min(resistance_levels) if resistance_levels else recent_high

            result = {
                'current_price': current_price,
                'nearest_support': nearest_support,
                'nearest_resistance': nearest_resistance,
                'all_support': support_levels,
                'all_resistance': resistance_levels,
                'recent_high': recent_high,
                'recent_low': recent_low
            }

            print(f"📈 Support/Resistance Analysis:")
            print(f"   Current Price: {current_price:.5f}")
            print(f"   Nearest Support: {nearest_support:.5f}")
            print(f"   Nearest Resistance: {nearest_resistance:.5f}")

            return result

        except Exception as e:
            print(f"❌ S/R calculation error: {e}")
            return None

    def calculate_technical_stop(self, levels_data: dict, is_long: bool,
                               instrument: str) -> Decimal:
        """Calculate stop based on technical levels."""

        pip_value = Decimal("0.01") if instrument.endswith('JPY') else Decimal("0.0001")
        buffer = Decimal(str(self.buffer_pips)) * pip_value

        if is_long:
            # For long positions, place stop below nearest support
            stop_price = levels_data['nearest_support'] - buffer
        else:
            # For short positions, place stop above nearest resistance
            stop_price = levels_data['nearest_resistance'] + buffer

        print(f"🎯 Technical Stop Calculation:")
        print(f"   Position: {'Long' if is_long else 'Short'}")
        print(f"   Key Level: {levels_data['nearest_support'] if is_long else levels_data['nearest_resistance']:.5f}")
        print(f"   Buffer: {self.buffer_pips} pips")
        print(f"   Stop Price: {stop_price:.5f}")

        return stop_price

# Example usage
async def demo_technical_stops(account_id: str, instrument: str = "EUR_USD") -> Any:
    """Demonstrate technical stop calculation."""

    async with AsyncClient(token=TOKEN, environment=ENVIRONMENT) as client:
        calculator = TechnicalStopCalculator(buffer_pips=5)

        # Find support/resistance levels
        levels = await calculator.find_support_resistance_levels(client, instrument)

        if levels:
            # Calculate stops for both directions
            long_stop = calculator.calculate_technical_stop(levels, is_long=True, instrument=instrument)
            short_stop = calculator.calculate_technical_stop(levels, is_long=False, instrument=instrument)

            return {
                'levels': levels,
                'long_stop': long_stop,
                'short_stop': short_stop
            }

        return None
```

---

## Stop Loss Strategy Comparison

### Performance Characteristics

| Strategy | Adaptability | Complexity | Best For | Drawdown Risk |
|----------|-------------|------------|----------|---------------|
| Fixed Pip | Low | Minimal | Beginners, Scalping | Medium |
| Percentage | Medium | Low | Swing Trading | Medium |
| ATR-Based | High | Medium | All Timeframes | Low |
| Trailing | High | High | Trending Markets | Low |
| Technical | Medium | Medium | Discretionary Trading | Low |

### Choosing Your Strategy

**For Day Trading:**
- Fixed pip stops (15-25 pips for majors)
- Quick decisions, consistent risk

**For Swing Trading:**
- ATR-based stops (2.0-2.5x ATR)
- Adapts to volatility changes

**For Position Trading:**
- Technical stops with trailing
- Captures long-term trends

**For Trend Following:**
- Trailing stops with ATR distance
- Maximizes trend participation

---

## ✅ Skill Checkpoint: Stop Loss Strategies

Test your understanding of stop loss techniques:

!!! question "🧠 Test Your Understanding"
    1. **Why is ATR-based stop loss superior to fixed pip stops?**
       <details>
       <summary>Click to reveal answer</summary>
       **Adapts to market volatility automatically**. ATR increases in volatile markets (wider stops) and decreases in calm markets (tighter stops), maintaining consistent risk while avoiding premature exit from normal market noise.
       </details>

    2. **When should you use trailing stops vs fixed stops?**
       <details>
       <summary>Click to reveal answer</summary>
       **Trailing stops for trending markets, fixed stops for ranging markets**. Trailing stops capture more profit in trends but can give back gains in choppy conditions. Fixed stops provide consistent protection regardless of market direction.
       </details>

    3. **What's the main advantage of technical stops over mathematical stops?**
       <details>
       <summary>Click to reveal answer</summary>
       **Based on actual market structure rather than arbitrary distances**. Technical stops respect where other traders are likely to place orders, making them less likely to be hit by random market noise and more likely to indicate genuine trend changes.
       </details>

---

## Stop Loss Best Practices

### Placement Guidelines

1. **Set Before Entry**
   - Always know your stop before entering
   - Calculate position size based on stop distance
   - Never enter without a predetermined exit plan

2. **Honor Your Stops**
   - Execute stops without hesitation
   - Don't move stops against you
   - Treat stop hits as part of the business

3. **Consider Market Context**
   - Wider stops before major news
   - Tighter stops in ranging markets
   - Adjust for overnight/weekend risk

4. **Test and Optimize**
   - Backtest different stop strategies
   - Track stop hit frequency
   - Optimize for your trading style

### Common Stop Loss Mistakes

#### ❌ **Moving Stops Against You**
```python
# WRONG: Moving stop further away when losing
original_stop = 1.0950
losing_position_stop = 1.0940  # Moved against you

# RIGHT: Only move stops in your favor
original_stop = 1.0950
winning_position_stop = 1.0960  # Moved in your favor
```

#### ❌ **No Stop Loss**
```python
# WRONG: Hoping position will recover
position_without_stop = {
    "entry": 1.1000,
    "stop": None,  # Dangerous!
    "hope": "Price will come back",
}

# RIGHT: Always have a stop
position_with_stop = {
    "entry": 1.1000,
    "stop": 1.0950,  # Risk defined
    "risk_amount": "Known and acceptable",
}
```

#### ❌ **Stops Too Tight**
```python
from decimal import Decimal

# WRONG: Stop tighter than normal market noise
entry_price = Decimal("1.1000")
too_tight_stop = Decimal("1.0995")  # Only 5 pips - likely to be hit by noise

# RIGHT: Consider normal market movement
entry_price = Decimal("1.1000")
appropriate_stop = Decimal("1.0975")  # 25 pips - allows for normal volatility
```

---

## Advanced Stop Management

### Scaling Out Strategy

```python
class ScalingStopManager:
    """Manage stops with position scaling."""

    def __init__(self) -> None:
        self.position_scales = {}

    def setup_scaling_stops(self, trade_id: str, total_position: int, scale_levels: list) -> Any:
        """Setup stops for scaled position management."""

        # Example: Scale out 1/3 at each level
        position_per_scale = total_position // len(scale_levels)

        self.position_scales[trade_id] = {
            "remaining_position": total_position,
            "scale_levels": scale_levels,
            "position_per_scale": position_per_scale,
            "stops_hit": [],
        }

        print(f"🔄 Scaling Stops Setup:")
        print(f"   Total Position: {total_position:,} units")
        print(f"   Scale Levels: {len(scale_levels)}")
        print(f"   Position per Scale: {position_per_scale:,} units")

        return self.position_scales[trade_id]

# Example scaling setup
scaling_manager = ScalingStopManager()
scaling_setup = scaling_manager.setup_scaling_stops(
    trade_id="trade_123",
    total_position=3000,
    scale_levels=[1.1050, 1.1100, 1.1150],  # Three profit targets
)
```

### Time-Based Stops

```python
from datetime import datetime, timedelta



"""Comprehensive module for trading operations."""
class TimeBasedStopManager:
    """Manage stops based on time in trade."""

    def __init__(self) -> None:
        self.time_stops = {}

    def set_time_stop(self, trade_id: str, max_hours: int = 24) -> Any:
        """Set maximum time limit for trade."""

        entry_time = datetime.utcnow()
        exit_time = entry_time + timedelta(hours=max_hours)

        self.time_stops[trade_id] = {
            "entry_time": entry_time,
            "exit_time": exit_time,
            "max_hours": max_hours,
        }

        print(f"⏰ Time Stop Set:")
        print(f"   Trade ID: {trade_id}")
        print(f"   Max Duration: {max_hours} hours")
        print(f"   Exit Time: {exit_time.strftime('%Y-%m-%d %H:%M:%S')}")

    def check_time_stops(self) -> Any:
        """Check if any time stops should be triggered."""

        current_time = datetime.utcnow()
        expired_trades = []

        for trade_id, stop_info in self.time_stops.items():
            if current_time >= stop_info["exit_time"]:
                expired_trades.append(trade_id)
                print(f"⏰ Time stop triggered for {trade_id}")

        return expired_trades

# Example time-based stop
time_manager = TimeBasedStopManager()
time_manager.set_time_stop("trade_456", max_hours=48)  # 2-day maximum
```

---

## What You've Learned

✅ **Fixed Pip Stops**: Basic, consistent approach for all experience levels

✅ **Percentage Stops**: Adaptable to different price levels and instruments

✅ **ATR-Based Stops**: Sophisticated volatility-adjusted protection

✅ **Trailing Stops**: Dynamic profit protection for trending markets

✅ **Technical Stops**: Market structure-based exit points

✅ **Advanced Management**: Scaling, time-based, and multi-level approaches

!!! success "🎉 Stop Loss Mastery Complete!"
    You now have a comprehensive toolkit for protecting your capital in any market condition. These stop loss strategies will help you preserve capital while maximizing profit potential. Next, learn to manage risk across your entire portfolio.

---

## Next Steps

Continue to [Portfolio Risk Management](portfolio-risk.md) to learn how to monitor and control risk across multiple positions and instruments.

---

## Related Resources

- **[Position Sizing Strategies](position-sizing.md)** - Calculate optimal position sizes
- **[Risk Management Fundamentals](fundamentals.md)** - Core risk management principles
- **[Position Management](../basic-trading/lesson-5-position-management.md)** - Individual position management techniques
- **[Orders API Reference](../../api-reference/endpoints/orders.md)** - Technical order management documentation