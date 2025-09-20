# Advanced Order Types Tutorial

This tutorial covers sophisticated order types and execution strategies that give you precise control over your trading. You'll learn about pending orders, conditional execution, and advanced order management techniques.

## Prerequisites

- Completed [Basic Trading Tutorial](basic-trading.md)
- Understanding of order types and market mechanics
- FiveTwenty setup with practice account

## Learning Objectives

By the end of this tutorial, you will:

- ✅ Master all OANDA order types
- ✅ Implement conditional order strategies
- ✅ Use trailing stops and dynamic exits
- ✅ Create complex order combinations
- ✅ Build automated order management systems

---

## 1. Order Types Overview

### Market Orders
Execute immediately at current market price.

### Pending Orders
Execute only when specific conditions are met:

- **Limit Orders**: Execute at specified price or better
- **Stop Orders**: Execute when price reaches trigger level
- **Market-If-Touched (MIT)**: Becomes market order when price reached
- **Stop-Limit**: Becomes limit order when stop triggered

### Conditional Orders
- **Stop Loss**: Close losing position automatically
- **Take Profit**: Close profitable position automatically
- **Trailing Stop**: Dynamic stop that follows favorable price movement

---

## 2. Advanced Limit Orders

### Basic Limit Order

```python
import asyncio
from decimal import Decimal
from datetime import datetime, timedelta

from fivetwenty import AsyncClient, Environment
from fivetwenty.models import TimeInForce, OrderType
from fivetwenty.exceptions import FiveTwentyError

# Configuration
TOKEN = "your-api-token-here"
ENVIRONMENT = Environment.PRACTICE

async def place_limit_order_advanced(account_id: str, instrument: str, units: int,
                                   price: float, time_in_force: TimeInForce = TimeInForce.GTC,
                                   gtd_time: datetime = None):
    """Place an advanced limit order with time controls."""

    async with AsyncClient(token=TOKEN, environment=ENVIRONMENT) as client:
        try:
            order_params = {
                'account_id': account_id,
                'instrument': instrument,
                'units': units,
                'price': f"{price:.5f}",
                'time_in_force': time_in_force
            }

            # Add GTD time if specified
            if time_in_force == TimeInForce.GTD and gtd_time:
                order_params['gtd_time'] = gtd_time.strftime('%Y-%m-%dT%H:%M:%S.%fZ')

            print(f"📋 Placing Advanced Limit Order:")
            print(f"   Instrument: {instrument}")
            print(f"   Units: {units}")
            print(f"   Price: {price:.5f}")
            print(f"   Time in Force: {time_in_force.value}")
            if gtd_time:
                print(f"   Good Till: {gtd_time}")

            response = await client.orders.post_limit_order(**order_params)

            if response.order_create_transaction:
                order = response.order_create_transaction
                print(f"✅ Limit order created!")
                print(f"   Order ID: {order.id}")
                print(f"   Status: {order.state}")

                return order
            else:
                print("❌ Failed to create limit order")
                return None

        except FiveTwentyError as e:
            print(f"❌ Limit order error: {e.message}")
            return None

# Example: Limit order good for 24 hours
async def demo_time_limited_order(account_id: str):
    """Demo of time-limited order."""

    if not account_id:
        print("❌ No account ID")
        return

    # Get current price to set limit below market
    async with AsyncClient(token=TOKEN, environment=ENVIRONMENT) as client:
        prices = await client.pricing.get(account_id=account_id, instruments=["EUR_USD"])

        if prices and prices[0].bids:
            current_bid = float(prices[0].bids[0].price)
            limit_price = current_bid - 0.0020  # 20 pips below current

            # Order expires in 24 hours
            expiry_time = datetime.utcnow() + timedelta(hours=24)

            await place_limit_order_advanced(
                account_id, "EUR_USD", 1000, limit_price,
                time_in_force=TimeInForce.GTD, gtd_time=expiry_time
            )
```

### Limit Order with Protective Orders

```python
from decimal import Decimal
from fivetwenty import AsyncClient, Environment
from fivetwenty.exceptions import FiveTwentyError, FiveTwentyErrorCode

async def limit_order_with_protection(account_id: str, instrument: str, units: int,
                                    entry_price: float, stop_loss_price: float,
                                    take_profit_price: float):
    """Place limit order with automatic stop loss and take profit."""

    async with AsyncClient(token=TOKEN, environment=ENVIRONMENT) as client:
        try:
            print(f"🎯 Placing Protected Limit Order:")
            print(f"   Entry: {entry_price:.5f}")
            print(f"   Stop Loss: {stop_loss_price:.5f}")
            print(f"   Take Profit: {take_profit_price:.5f}")

            response = await client.orders.post_limit_order(
                account_id=account_id,
                instrument=instrument,
                units=units,
                price=f"{entry_price:.5f}",
                time_in_force=TimeInForce.GTC,
                stop_loss_on_fill={'price': f"{stop_loss_price:.5f}"},
                take_profit_on_fill={'price': f"{take_profit_price:.5f}"}
            )

            if response.order_create_transaction:
                order = response.order_create_transaction
                print(f"✅ Protected limit order created!")
                print(f"   Order ID: {order.id}")

                return order

        except FiveTwentyError as e:
            print(f"❌ Protected order error: {e.message}")
            return None

# Example usage
async def demo_protected_limit_order(account_id: str):
    """Demo protected limit order."""

    if not account_id:
        return

    # Example prices for EUR/USD
    entry_price=Decimal("1.1000")    # Enter at 1.1000
    stop_loss=Decimal("1.0950")     # Stop at 1.0950 (50 pip loss)
    take_profit=Decimal("1.1100")   # Profit at 1.1100 (100 pip gain)

    await limit_order_with_protection(
        account_id, "EUR_USD", 1000, entry_price, stop_loss, take_profit
    )
```

---

## 3. Stop Orders and Market-If-Touched

### Stop Order (Stop Loss Entry)

```python
from fivetwenty import AsyncClient, Environment
from fivetwenty.exceptions import FiveTwentyError, FiveTwentyErrorCode

async def place_stop_order(account_id: str, instrument: str, units: int,
                          stop_price: float, price_bound: float = None):
    """Place a stop order (becomes market order when price reached)."""

    async with AsyncClient(token=TOKEN, environment=ENVIRONMENT) as client:
        try:
            order_params = {
                'account_id': account_id,
                'instrument': instrument,
                'units': units,
                'price': f"{stop_price:.5f}",
                'time_in_force': TimeInForce.GTC
            }

            # Add price bound for slippage protection
            if price_bound:
                order_params['price_bound'] = f"{price_bound:.5f}"

            print(f"🛑 Placing Stop Order:")
            print(f"   Instrument: {instrument}")
            print(f"   Units: {units}")
            print(f"   Stop Price: {stop_price:.5f}")
            if price_bound:
                print(f"   Price Bound: {price_bound:.5f}")

            response = await client.orders.post_stop_order(**order_params)

            if response.order_create_transaction:
                order = response.order_create_transaction
                print(f"✅ Stop order created!")
                print(f"   Order ID: {order.id}")

                return order

        except FiveTwentyError as e:
            print(f"❌ Stop order error: {e.message}")
            return None

# Breakout strategy using stop orders
async def breakout_strategy(account_id: str, instrument: str):
    """Implement breakout strategy using stop orders."""

    async with AsyncClient(token=TOKEN, environment=ENVIRONMENT) as client:
        try:
            # Get recent high/low levels
            from fivetwenty.models import CandlestickGranularity

            candles = await client.instruments.candles(
                instrument=instrument,
                count=20,
                granularity=CandlestickGranularity.H4
            )

            # Calculate resistance and support
            highs = [float(candle.mid.h) for candle in candles.candles if candle.mid]
            lows = [float(candle.mid.l) for candle in candles.candles if candle.mid]

            resistance = max(highs[-10:])  # 10-period high
            support = min(lows[-10:])      # 10-period low

            print(f"📊 Breakout Levels for {instrument}:")
            print(f"   Resistance: {resistance:.5f}")
            print(f"   Support: {support:.5f}")

            # Place breakout orders
            breakout_distance = 0.0005  # 5 pips above/below levels

            # Buy stop above resistance
            buy_stop_price = resistance + breakout_distance
            buy_stop = await place_stop_order(
                account_id, instrument, 1000, buy_stop_price
            )

            # Sell stop below support
            sell_stop_price = support - breakout_distance
            sell_stop = await place_stop_order(
                account_id, instrument, -1000, sell_stop_price
            )

            print(f"✅ Breakout strategy deployed!")
            return {'buy_stop': buy_stop, 'sell_stop': sell_stop}

        except FiveTwentyError as e:
            print(f"❌ Breakout strategy error: {e.message}")
            return None
```

### Market-If-Touched (MIT) Orders

```python
from fivetwenty import AsyncClient, Environment
from fivetwenty.exceptions import FiveTwentyError, FiveTwentyErrorCode

async def place_mit_order(account_id: str, instrument: str, units: int, price: float):
    """Place a Market-If-Touched order."""

    async with AsyncClient(token=TOKEN, environment=ENVIRONMENT) as client:
        try:
            print(f"📍 Placing MIT Order:")
            print(f"   Instrument: {instrument}")
            print(f"   Units: {units}")
            print(f"   Touch Price: {price:.5f}")

            response = await client.orders.post_market_if_touched_order(
                account_id=account_id,
                instrument=instrument,
                units=units,
                price=f"{price:.5f}",
                time_in_force=TimeInForce.GTC
            )

            if response.order_create_transaction:
                order = response.order_create_transaction
                print(f"✅ MIT order created!")
                print(f"   Order ID: {order.id}")

                return order

        except FiveTwentyError as e:
            print(f"❌ MIT order error: {e.message}")
            return None

# Mean reversion strategy with MIT orders
async def mean_reversion_strategy(account_id: str, instrument: str):
    """Implement mean reversion using MIT orders."""

    async with AsyncClient(token=TOKEN, environment=ENVIRONMENT) as client:
        try:
            # Calculate moving average
            from fivetwenty.models import CandlestickGranularity

            candles = await client.instruments.candles(
                instrument=instrument,
                count=50,
                granularity=CandlestickGranularity.H1
            )

            closes = [float(candle.mid.c) for candle in candles.candles if candle.mid]
            ma_20 = sum(closes[-20:]) / 20
            current_price = closes[-1]

            # Calculate standard deviation
            import math
            variance = sum((price - ma_20) ** 2 for price in closes[-20:]) / 20
            std_dev = math.sqrt(variance)

            print(f"📊 Mean Reversion Setup for {instrument}:")
            print(f"   Current Price: {current_price:.5f}")
            print(f"   20-period MA: {ma_20:.5f}")
            print(f"   Standard Deviation: {std_dev:.5f}")

            # Set MIT orders at 2 standard deviations
            upper_level = ma_20 + (2 * std_dev)
            lower_level = ma_20 - (2 * std_dev)

            # Sell MIT at upper level (expect reversion down)
            sell_mit = await place_mit_order(
                account_id, instrument, -1000, upper_level
            )

            # Buy MIT at lower level (expect reversion up)
            buy_mit = await place_mit_order(
                account_id, instrument, 1000, lower_level
            )

            return {'sell_mit': sell_mit, 'buy_mit': buy_mit}

        except FiveTwentyError as e:
            print(f"❌ Mean reversion error: {e.message}")
            return None
```

---

## 4. Trailing Stops and Dynamic Orders

### Trailing Stop Orders

```python
from fivetwenty import AsyncClient, Environment
from fivetwenty.exceptions import FiveTwentyError, FiveTwentyErrorCode

async def set_trailing_stop(account_id: str, trade_id: str, trail_distance_pips: float):
    """Set a trailing stop loss on an existing trade."""

    async with AsyncClient(token=TOKEN, environment=ENVIRONMENT) as client:
        try:
            # Get trade details
            trade = await client.trades.get(account_id, trade_id)

            if not trade:
                print(f"❌ Trade {trade_id} not found")
                return False

            # Calculate trailing distance
            instrument = trade.instrument
            trail_distance = trail_distance_pips * (0.01 if instrument.endswith('JPY') else 0.0001)

            print(f"📈 Setting Trailing Stop:")
            print(f"   Trade ID: {trade_id}")
            print(f"   Instrument: {instrument}")
            print(f"   Trail Distance: {trail_distance_pips} pips")

            # Update trade with trailing stop
            response = await client.trades.update(
                account_id=account_id,
                trade_id=trade_id,
                stop_loss={'distance': f"{trail_distance:.5f}"}
            )

            if response.trade_state:
                print(f"✅ Trailing stop set successfully!")
                print(f"   Current Stop Level: {response.trade_state.stop_loss_order.price}")
                return True

        except FiveTwentyError as e:
            print(f"❌ Trailing stop error: {e.message}")
            return False

# Advanced trailing stop with break-even protection
async def advanced_trailing_stop(account_id: str, trade_id: str,
                                trail_distance_pips: float, breakeven_pips: float):
    """Set trailing stop that moves to break-even first."""

    async with AsyncClient(token=TOKEN, environment=ENVIRONMENT) as client:
        try:
            trade = await client.trades.get(account_id, trade_id)

            if not trade:
                return False

            entry_price = float(trade.price)
            current_units = int(trade.current_units)
            instrument = trade.instrument

            # Get current price
            prices = await client.pricing.get(account_id=account_id, instruments=[instrument])
            current_price = float(prices[0].asks[0].price) if current_units > 0 else float(prices[0].bids[0].price)

            pip_value = 0.01 if instrument.endswith('JPY') else 0.0001
            trail_distance = trail_distance_pips * pip_value

            print(f"🎯 Advanced Trailing Stop:")
            print(f"   Entry Price: {entry_price:.5f}")
            print(f"   Current Price: {current_price:.5f}")

            # Check if profitable enough for break-even
            if current_units > 0:  # Long position
                profit_pips = (current_price - entry_price) / pip_value
                if profit_pips >= breakeven_pips:
                    # Move stop to break-even + small buffer
                    stop_price = entry_price + (5 * pip_value)  # 5 pip buffer
                    print(f"   Moving to break-even: {stop_price:.5f}")
                else:
                    # Use trailing distance from entry
                    stop_price = entry_price - trail_distance
                    print(f"   Initial stop: {stop_price:.5f}")
            else:  # Short position
                profit_pips = (entry_price - current_price) / pip_value
                if profit_pips >= breakeven_pips:
                    stop_price = entry_price - (5 * pip_value)
                    print(f"   Moving to break-even: {stop_price:.5f}")
                else:
                    stop_price = entry_price + trail_distance
                    print(f"   Initial stop: {stop_price:.5f}")

            # Update stop loss
            response = await client.trades.update(
                account_id=account_id,
                trade_id=trade_id,
                stop_loss={'price': f"{stop_price:.5f}"}
            )

            return response.trade_state is not None

        except FiveTwentyError as e:
            print(f"❌ Advanced trailing stop error: {e.message}")
            return False
```

### Dynamic Order Management

```python
from fivetwenty import AsyncClient, Environment
from fivetwenty.exceptions import FiveTwentyError, FiveTwentyErrorCode

class DynamicOrderManager:
    """Manage orders dynamically based on market conditions."""

    def __init__(self, client: AsyncClient, account_id: str):
        self.client = client
        self.account_id = account_id
        self.active_strategies = {}

    async def scale_out_strategy(self, trade_id: str, scale_levels: list):
        """Scale out of position at multiple levels."""

        try:
            trade = await self.client.trades.get(self.account_id, trade_id)
            if not trade:
                return False

            current_units = int(trade.current_units)
            instrument = trade.instrument

            print(f"📊 Scaling Out Strategy:")
            print(f"   Trade ID: {trade_id}")
            print(f"   Current Units: {current_units}")
            print(f"   Scale Levels: {len(scale_levels)}")

            scale_orders = []

            for i, (percentage, target_price) in enumerate(scale_levels):
                # Calculate units to close
                units_to_close = int(abs(current_units) * percentage / 100)
                if current_units < 0:
                    units_to_close = -units_to_close

                # Create limit order to close partial position
                response = await self.client.orders.post_limit_order(
                    account_id=self.account_id,
                    instrument=instrument,
                    units=-units_to_close,  # Opposite direction
                    price=f"{target_price:.5f}",
                    time_in_force=TimeInForce.GTC
                )

                if response.order_create_transaction:
                    order = response.order_create_transaction
                    scale_orders.append({
                        'order_id': order.id,
                        'percentage': percentage,
                        'target_price': target_price,
                        'units': units_to_close
                    })

                    print(f"   ✅ Scale order {i+1}: {percentage}% at {target_price:.5f}")

            return scale_orders

        except FiveTwentyError as e:
            print(f"❌ Scale out error: {e.message}")
            return []

    async def pyramid_strategy(self, base_trade_id: str, add_levels: list, max_total_units: int):
        """Add to winning position at specific levels."""

        try:
            base_trade = await self.client.trades.get(self.account_id, base_trade_id)
            if not base_trade:
                return False

            instrument = base_trade.instrument
            current_units = int(base_trade.current_units)
            entry_price = float(base_trade.price)

            print(f"🔺 Pyramid Strategy:")
            print(f"   Base Trade: {abs(current_units)} units at {entry_price:.5f}")
            print(f"   Add Levels: {len(add_levels)}")

            pyramid_orders = []
            total_units = abs(current_units)

            for level_price, add_units in add_levels:
                if total_units + add_units > max_total_units:
                    print(f"   ⚠️ Skipping level {level_price:.5f} - would exceed max units")
                    continue

                # Same direction as original trade
                units = add_units if current_units > 0 else -add_units

                # Create limit order to add to position
                response = await self.client.orders.post_limit_order(
                    account_id=self.account_id,
                    instrument=instrument,
                    units=units,
                    price=f"{level_price:.5f}",
                    time_in_force=TimeInForce.GTC
                )

                if response.order_create_transaction:
                    order = response.order_create_transaction
                    pyramid_orders.append({
                        'order_id': order.id,
                        'add_price': level_price,
                        'add_units': add_units
                    })

                    total_units += add_units
                    print(f"   ✅ Pyramid order: +{add_units} at {level_price:.5f}")

            return pyramid_orders

        except FiveTwentyError as e:
            print(f"❌ Pyramid error: {e.message}")
            return []

# Example usage of dynamic order manager
async def demo_dynamic_orders(account_id: str):
    """Demonstrate dynamic order management."""

    if not account_id:
        return

    async with AsyncClient(token=TOKEN, environment=ENVIRONMENT) as client:
        manager = DynamicOrderManager(client, account_id)

        # Example: Scale out at 25%, 50%, and 100% profit levels
        # Assuming we have a trade ID from previous examples
        scale_levels = [
            (25, 1.1050),  # Close 25% at 1.1050
            (50, 1.1100),  # Close 50% at 1.1100
            (25, 1.1150),  # Close remaining 25% at 1.1150
        ]

        # Note: Replace 'example_trade_id' with actual trade ID
        # scale_orders = await manager.scale_out_strategy('example_trade_id', scale_levels)

        print("💡 Scale out strategy configured (need active trade to execute)")
```

---

## 5. Order Monitoring and Management

### Order Status Monitoring

```python
from fivetwenty import AsyncClient, Environment
from fivetwenty.exceptions import FiveTwentyError, FiveTwentyErrorCode

async def monitor_pending_orders(account_id: str):
    """Monitor all pending orders and their status."""

    async with AsyncClient(token=TOKEN, environment=ENVIRONMENT) as client:
        try:
            orders = await client.orders.list_pending(account_id)

            if not orders:
                print("📋 No pending orders")
                return []

            print(f"📋 Pending Orders ({len(orders)}):")

            for order in orders:
                print(f"\n   🔸 Order ID: {order.id}")
                print(f"     Type: {order.type}")
                print(f"     Instrument: {order.instrument}")
                print(f"     Units: {order.units}")
                print(f"     Price: {order.price}")
                print(f"     State: {order.state}")
                print(f"     Time in Force: {order.time_in_force}")
                print(f"     Created: {order.create_time}")

                # Show GTD time if applicable
                if hasattr(order, 'gtd_time') and order.gtd_time:
                    print(f"     Expires: {order.gtd_time}")

            return orders

        except FiveTwentyError as e:
            print(f"❌ Error monitoring orders: {e.message}")
            return []

async def cancel_order(account_id: str, order_id: str):
    """Cancel a pending order."""

    async with AsyncClient(token=TOKEN, environment=ENVIRONMENT) as client:
        try:
            print(f"🗑️ Cancelling order {order_id}...")

            response = await client.orders.cancel(account_id, order_id)

            if response.order_cancel_transaction:
                print(f"✅ Order cancelled successfully!")
                print(f"   Cancelled at: {response.order_cancel_transaction.time}")
                return True
            else:
                print(f"❌ Failed to cancel order")
                return False

        except FiveTwentyError as e:
            print(f"❌ Cancel error: {e.message}")
            return False

async def modify_order(account_id: str, order_id: str, new_price: float = None,
                      new_units: int = None):
    """Modify a pending order."""

    async with AsyncClient(token=TOKEN, environment=ENVIRONMENT) as client:
        try:
            # Get current order details
            orders = await client.orders.list_pending(account_id)
            order = next((o for o in orders if o.id == order_id), None)

            if not order:
                print(f"❌ Order {order_id} not found")
                return False

            print(f"🔧 Modifying order {order_id}:")
            print(f"   Current: {order.units} units at {order.price}")

            # Prepare update parameters
            update_params = {}
            if new_price:
                update_params['price'] = f"{new_price:.5f}"
                print(f"   New Price: {new_price:.5f}")
            if new_units:
                update_params['units'] = new_units
                print(f"   New Units: {new_units}")

            # Update order based on type
            if order.type == 'LIMIT':
                response = await client.orders.update_limit(
                    account_id, order_id, **update_params
                )
            elif order.type == 'STOP':
                response = await client.orders.update_stop(
                    account_id, order_id, **update_params
                )
            else:
                print(f"❌ Order type {order.type} not supported for modification")
                return False

            if response.order_create_transaction:
                print(f"✅ Order modified successfully!")
                return True

        except FiveTwentyError as e:
            print(f"❌ Modify error: {e.message}")
            return False
```

### Automated Order Management System

```python
from fivetwenty import AsyncClient, Environment

class AutomatedOrderManager:
    """Fully automated order management system."""

    def __init__(self, client: AsyncClient, account_id: str):
        self.client = client
        self.account_id = account_id
        self.monitoring = False
        self.rules = []

    def add_rule(self, rule_func, description: str):
        """Add a management rule."""
        self.rules.append({'function': rule_func, 'description': description})
        print(f"📜 Added rule: {description}")

    async def start_monitoring(self, check_interval: int = 60):
        """Start automated monitoring and management."""

        print(f"🤖 Starting automated order management...")
        print(f"   Check interval: {check_interval} seconds")
        print(f"   Active rules: {len(self.rules)}")

        self.monitoring = True

        while self.monitoring:
            try:
                # Apply all rules
                for rule in self.rules:
                    await rule['function'](self.client, self.account_id)

                # Wait before next check
                await asyncio.sleep(check_interval)

            except Exception as e:
                print(f"❌ Monitoring error: {e}")
                await asyncio.sleep(check_interval)

    def stop_monitoring(self):
        """Stop automated monitoring."""
        self.monitoring = False
        print("🛑 Stopped automated monitoring")

# Example management rules
async def cancel_old_orders_rule(client: AsyncClient, account_id: str):
    """Cancel orders older than 24 hours."""

    try:
        orders = await client.orders.list_pending(account_id)
        current_time = datetime.utcnow()

        for order in orders:
            create_time = datetime.fromisoformat(order.create_time.replace('Z', '+00:00'))
            age_hours = (current_time - create_time.replace(tzinfo=None)).total_seconds() / 3600

            if age_hours > 24:
                print(f"🗑️ Cancelling old order {order.id} (age: {age_hours:.1f}h)")
                await client.orders.cancel(account_id, order.id)

    except Exception as e:
        print(f"❌ Old orders rule error: {e}")

async def adjust_stops_rule(client: AsyncClient, account_id: str):
    """Adjust stops based on volatility."""

    try:
        trades = await client.trades.list_open(account_id)

        for trade in trades:
            if not trade.stop_loss_order:
                continue

            # Get recent volatility
            from fivetwenty.models import CandlestickGranularity

            candles = await client.instruments.candles(
                instrument=trade.instrument,
                count=20,
                granularity=CandlestickGranularity.H1
            )

            # Calculate ATR (simplified)
            if len(candles.candles) >= 14:
                ranges = []
                for candle in candles.candles[-14:]:
                    if candle.mid:
                        tr = float(candle.mid.h) - float(candle.mid.l)
                        ranges.append(tr)

                atr = sum(ranges) / len(ranges)

                # Adjust stop based on ATR
                current_price = float(candles.candles[-1].mid.c)
                units = int(trade.current_units)

                if units > 0:  # Long position
                    new_stop = current_price - (2 * atr)  # 2 ATR stop
                else:  # Short position
                    new_stop = current_price + (2 * atr)

                # Update if significantly different
                current_stop = float(trade.stop_loss_order.price)
                if abs(new_stop - current_stop) / current_stop > 0.1:  # 10% difference
                    print(f"📊 Adjusting stop for {trade.instrument}: {current_stop:.5f} → {new_stop:.5f}")

                    await client.trades.update(
                        account_id=account_id,
                        trade_id=trade.id,
                        stop_loss={'price': f"{new_stop:.5f}"}
                    )

    except Exception as e:
        print(f"❌ Adjust stops rule error: {e}")

# Demo automated manager
async def demo_automated_manager(account_id: str):
    """Demonstrate automated order management."""

    if not account_id:
        return

    async with AsyncClient(token=TOKEN, environment=ENVIRONMENT) as client:
        manager = AutomatedOrderManager(client, account_id)

        # Add management rules
        manager.add_rule(cancel_old_orders_rule, "Cancel orders older than 24 hours")
        manager.add_rule(adjust_stops_rule, "Adjust stops based on volatility")

        print("🤖 Automated manager configured")
        print("💡 Use manager.start_monitoring() to begin automation")

        return manager
```

---

## 6. Order Strategies and Combinations

### Bracket Orders Strategy

```python
from fivetwenty import AsyncClient, Environment
from fivetwenty.exceptions import FiveTwentyError, FiveTwentyErrorCode

async def advanced_bracket_strategy(account_id: str, instrument: str,
                                  entry_signal: str, support_resistance: dict):
    """Advanced bracket strategy with multiple scenarios."""

    async with AsyncClient(token=TOKEN, environment=ENVIRONMENT) as client:
        try:
            print(f"🎯 Advanced Bracket Strategy for {instrument}")

            # Get current price
            prices = await client.pricing.get(account_id=account_id, instruments=[instrument])
            current_price = float(prices[0].asks[0].price)

            resistance = support_resistance['resistance']
            support = support_resistance['support']

            print(f"   Current Price: {current_price:.5f}")
            print(f"   Resistance: {resistance:.5f}")
            print(f"   Support: {support:.5f}")

            if entry_signal == "BULLISH":
                # Buy at current market, stop below support, target at resistance
                entry_price = current_price
                stop_loss = support - 0.0010  # 10 pips below support
                take_profit = resistance - 0.0010  # 10 pips below resistance
                units = 1000

            elif entry_signal == "BEARISH":
                # Sell at current market, stop above resistance, target at support
                entry_price = current_price
                stop_loss = resistance + 0.0010  # 10 pips above resistance
                take_profit = support + 0.0010  # 10 pips above support
                units = -1000

            else:
                print(f"❌ Invalid signal: {entry_signal}")
                return None

            # Calculate risk/reward
            risk = abs(entry_price - stop_loss)
            reward = abs(take_profit - entry_price)
            risk_reward_ratio = reward / risk if risk > 0 else 0

            print(f"   📊 Trade Analysis:")
            print(f"     Entry: {entry_price:.5f}")
            print(f"     Stop: {stop_loss:.5f}")
            print(f"     Target: {take_profit:.5f}")
            print(f"     Risk: {risk:.5f} ({risk*10000:.1f} pips)")
            print(f"     Reward: {reward:.5f} ({reward*10000:.1f} pips)")
            print(f"     R:R Ratio: {risk_reward_ratio:.2f}:1")

            if risk_reward_ratio < 1.5:
                print(f"⚠️ Risk/reward ratio too low - skipping trade")
                return None

            # Place bracket order
            response = await client.orders.post_market_order(
                account_id=account_id,
                instrument=instrument,
                units=units,
                stop_loss_on_fill={'price': f"{stop_loss:.5f}"},
                take_profit_on_fill={'price': f"{take_profit:.5f}"}
            )

            if response.order_fill_transaction:
                fill = response.order_fill_transaction
                print(f"✅ Advanced bracket order executed!")
                print(f"   Trade ID: {fill.trade_opened.trade_id if fill.trade_opened else 'N/A'}")

                return fill

        except FiveTwentyError as e:
            print(f"❌ Advanced bracket error: {e.message}")
            return None

# Example usage
async def demo_bracket_strategy(account_id: str):
    """Demo advanced bracket strategy."""

    if not account_id:
        return

    # Example support/resistance levels
    levels = {
        'resistance': 1.1100,
        'support': 1.1000
    }

    await advanced_bracket_strategy(account_id, "EUR_USD", "BULLISH", levels)
```

---

## 7. Best Practices and Risk Management

### Order Validation System

```python
from fivetwenty import AsyncClient, Environment

class OrderValidator:
    """Comprehensive order validation system."""

    def __init__(self, max_risk_per_trade: float = 0.02, max_daily_orders: int = 20):
        self.max_risk_per_trade = max_risk_per_trade
        self.max_daily_orders = max_daily_orders
        self.daily_order_count = 0
        self.last_reset_date = datetime.utcnow().date()

    def reset_daily_counters(self):
        """Reset daily counters if new day."""
        current_date = datetime.utcnow().date()
        if current_date > self.last_reset_date:
            self.daily_order_count = 0
            self.last_reset_date = current_date

    async def validate_order(self, client: AsyncClient, account_id: str,
                           instrument: str, units: int, entry_price: float,
                           stop_loss: float = None) -> dict:
        """Comprehensive order validation."""

        self.reset_daily_counters()

        validation_result = {
            'valid': True,
            'warnings': [],
            'errors': [],
            'risk_metrics': {}
        }

        try:
            # Get account info
            account = await client.accounts.get(account_id)
            account_balance = float(account.balance)

            # Check daily order limit
            if self.daily_order_count >= self.max_daily_orders:
                validation_result['valid'] = False
                validation_result['errors'].append(f"Daily order limit reached ({self.max_daily_orders})")

            # Calculate position risk
            if stop_loss:
                risk_per_unit = abs(entry_price - stop_loss)
                total_risk = abs(units) * risk_per_unit
                risk_percentage = (total_risk / account_balance) * 100

                validation_result['risk_metrics'] = {
                    'risk_amount': total_risk,
                    'risk_percentage': risk_percentage,
                    'position_size': abs(units),
                    'risk_per_unit': risk_per_unit
                }

                # Check risk limits
                if risk_percentage > self.max_risk_per_trade * 100:
                    validation_result['valid'] = False
                    validation_result['errors'].append(
                        f"Risk ({risk_percentage:.2f}%) exceeds limit ({self.max_risk_per_trade*100:.1f}%)"
                    )

            # Check market hours (simplified)
            current_hour = datetime.utcnow().hour
            if current_hour < 5 or current_hour > 21:  # UTC hours
                validation_result['warnings'].append("Trading outside major market hours")

            # Check existing exposure
            positions = await client.positions.list_open(account_id)
            existing_exposure = 0

            for position in positions:
                if position.instrument == instrument:
                    long_units = int(position.long.units) if position.long.units != "0" else 0
                    short_units = int(position.short.units) if position.short.units != "0" else 0
                    existing_exposure = long_units + short_units
                    break

            new_exposure = existing_exposure + units
            if abs(new_exposure) > 5000:  # Example limit
                validation_result['warnings'].append(
                    f"High exposure after trade: {new_exposure} units"
                )

            self.daily_order_count += 1
            return validation_result

        except Exception as e:
            validation_result['valid'] = False
            validation_result['errors'].append(f"Validation error: {e}")
            return validation_result

# Example validation usage
async def demo_order_validation(account_id: str):
    """Demonstrate order validation."""

    if not account_id:
        return

    async with AsyncClient(token=TOKEN, environment=ENVIRONMENT) as client:
        validator = OrderValidator(max_risk_per_trade=0.02, max_daily_orders=10)

        # Validate a potential order
        validation = await validator.validate_order(
            client, account_id, "EUR_USD", 2000, 1.1000, 1.0950
        )

        print("🔍 Order Validation Result:")
        print(f"   Valid: {'✅' if validation['valid'] else '❌'}")

        if validation['errors']:
            print("   🚨 Errors:")
            for error in validation['errors']:
                print(f"     - {error}")

        if validation['warnings']:
            print("   ⚠️ Warnings:")
            for warning in validation['warnings']:
                print(f"     - {warning}")

        if validation['risk_metrics']:
            metrics = validation['risk_metrics']
            print("   📊 Risk Metrics:")
            print(f"     Risk Amount: ${metrics['risk_amount']:.2f}")
            print(f"     Risk Percentage: {metrics['risk_percentage']:.2f}%")
            print(f"     Position Size: {metrics['position_size']} units")
```

---

## 8. Advanced Features and Error Handling

### Time-in-Force Options

OANDA supports sophisticated time-based order controls:

#### GTD (Good Till Date) Orders
```python
from datetime import datetime, timedelta, timezone

# Create order that expires in 2 hours
expiry_time = datetime.now(timezone.utc) + timedelta(hours=2)
gtd_time_str = expiry_time.strftime('%Y-%m-%dT%H:%M:%S.%fZ')

gtd_order = LimitOrderRequest(
    instrument="EUR_USD",
    units=1000,
    price="1.1000",
    timeInForce="GTD",
    gtdTime=gtd_time_str
)

response = await client.orders.post_order(account_id, gtd_order)
```

#### GFD (Good For Day) Orders
```python
# Order automatically expires at end of trading day
gfd_order = LimitOrderRequest(
    instrument="EUR_USD",
    units=1000,
    price="1.1000",
    timeInForce="GFD"  # Expires at end of trading day
)
```

### Trigger Conditions

Control exactly when orders activate:

```python
# BID-based trigger (for sell orders)
bid_order = LimitOrderRequest(
    instrument="EUR_USD",
    units=-1000,
    price="1.1050",
    triggerCondition="BID"  # Triggers when BID reaches price
)

# ASK-based trigger (for buy orders)
ask_order = StopOrderRequest(
    instrument="EUR_USD",
    units=1000,
    price="1.0950",
    triggerCondition="ASK"  # Triggers when ASK reaches price
)

# MID-based trigger (balanced approach)
mid_order = MarketIfTouchedOrderRequest(
    instrument="EUR_USD",
    units=1000,
    price="1.1000",
    triggerCondition="MID"  # Triggers when MID price reached
)

# INVERSE trigger (opposite logic)
inverse_order = StopOrderRequest(
    instrument="EUR_USD",
    units=1000,
    price="1.1100",
    triggerCondition="INVERSE"  # Advanced trigger logic
)
```

### Comprehensive Error Handling

Robust error handling for production systems:

```python
from fivetwenty.exceptions import FiveTwentyError

async def robust_order_placement(client, account_id, order_request):
    """Place order with comprehensive error handling."""

    try:
        response = await client.orders.post_order(
            account_id=account_id,
            order_request=order_request,
            timeout=10.0  # 10-second timeout
        )

        if response.order_create_transaction:
            order_id = response.order_create_transaction['id']
            print(f"✅ Order placed successfully: {order_id}")
            return order_id

    except FiveTwentyError as e:
        error_msg = str(e)

        # Handle specific error types
        if "INSUFFICIENT_MARGIN" in error_msg:
            print("❌ Not enough margin for this order")
            # Reduce position size or wait for margin

        elif "INSTRUMENT_NOT_TRADEABLE" in error_msg:
            print("❌ Instrument not currently tradeable")
            # Switch to alternative instrument

        elif "ORDER_RATE_LIMITED" in error_msg:
            print("❌ Order rate limited - too many orders")
            # Implement exponential backoff
            await asyncio.sleep(2)

        elif "MARKET_HALTED" in error_msg:
            print("❌ Market is currently halted")
            # Wait for market to resume

        else:
            print(f"❌ Order rejected: {error_msg}")

    except asyncio.TimeoutError:
        print("❌ Order request timed out")
        # Retry with longer timeout or check order status

    except Exception as e:
        print(f"❌ Unexpected error: {type(e).__name__}: {e}")
        # Log error and implement fallback strategy

    return None
```

### Complete Example

For a comprehensive demonstration of all advanced features, see:

📁 **Advanced Features Demo Script** (see `examples/scripts/advanced_features_demo.py`)

This example demonstrates:
- ✅ GTD/GFD time-based order expiration
- ✅ All trigger condition types with practical examples
- ✅ Comprehensive error scenario testing
- ✅ Timeout handling and recovery strategies
- ✅ Best practices for production environments

Run the example:
```bash
export FIVETWENTY_OANDA_TOKEN="your-token-here"
python docs/examples/scripts/advanced_features_demo.py
```

---

## 9. Summary and Next Steps

### Key Takeaways

You've mastered advanced order types and strategies:

- ✅ **Complex Order Types**: Limit, stop, MIT, and conditional orders
- ✅ **Dynamic Management**: Trailing stops, scaling, and pyramiding
- ✅ **Automated Systems**: Rule-based order management
- ✅ **Risk Validation**: Comprehensive order validation framework
- ✅ **Strategy Integration**: Combining orders into trading strategies

### Best Practices

1. **Always Validate**: Check orders against risk parameters
2. **Monitor Actively**: Use automated monitoring for open orders
3. **Manage Dynamically**: Adjust orders based on market conditions
4. **Control Exposure**: Limit total position size and correlation
5. **Plan Exits**: Always have stop loss and take profit levels

### Next Steps

Continue your learning journey:

- **[Risk Management](risk-management.md)** - Advanced risk control techniques
- **[Portfolio Analysis](portfolio-analysis.md)** - Multi-instrument strategies
- **[Streaming Data](streaming-data.md)** - Real-time order management
- **Data Analysis** (`https://github.com/NimbleOx/fivetwenty/blob/main/examples/notebooks/data-analysis.ipynb`) - Test order strategies with historical data

### Resources

- 📚 [Order Types Reference](../api-reference/endpoints/orders.md)
- 🎯 [Best Practices Guide](../explanation/best-practices.md)
- 📊 Interactive Examples (`https://github.com/NimbleOx/fivetwenty/blob/main/examples/notebooks/trading-strategies.ipynb`)

---

**Congratulations!** You now have the skills to implement sophisticated order management strategies. Remember to always test thoroughly in the practice environment before deploying to live trading.

**Happy Trading!** 🎯