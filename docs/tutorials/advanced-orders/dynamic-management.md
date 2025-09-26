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

Trailing stops protect profits while allowing positions to run in favorable directions.

### Basic Trailing Stop System

```python
import asyncio
from datetime import datetime, timedelta
from decimal import Decimal

from fivetwenty import AsyncClient



"""Comprehensive module for trading operations."""
class TrailingStopManager:
    def __init__(self, client: AsyncClient, account_id: str) -> None:
        self.client = client
        self.account_id = account_id
        self.active_trails = {}  # Track trailing stops

    async def create_trailing_stop(self, position_id: str, initial_stop: Decimal, trail_distance: Decimal, instrument: str) -> Any:
        """Create and manage a trailing stop for a position."""

        # Place initial stop-loss order
        initial_stop_response = await self.client.orders.post_stop_order(
            account_id=self.account_id,
            instrument=instrument,
            units=-10000,  # Assume long position to close
            price=initial_stop,
            time_in_force="GTC",
        )

        # Store trailing stop configuration
        trail_config = {
            "position_id": position_id,
            "instrument": instrument,
            "current_stop": initial_stop,
            "trail_distance": trail_distance,
            "stop_order_id": initial_stop_response.order_create_transaction.id,
            "highest_price": initial_stop + trail_distance,  # Starting reference
            "direction": "long",  # Assume long position
        }

        self.active_trails[position_id] = trail_config
        print(f"Trailing stop created: {initial_stop} (trail: {trail_distance})")

        return trail_config

    async def update_trailing_stops(self) -> Any:
        """Update all active trailing stops based on current prices."""

        for position_id, config in self.active_trails.items():
            # Get current market price
            pricing = await self.client.pricing.get_pricing(
                account_id=self.account_id,
                instruments=[config["instrument"]],
            )

            current_price = Decimal(pricing.prices[0].bids[0].price)

            # Check if we need to update the trailing stop
            if config["direction"] == "long":
                # For long positions, trail up when price moves favorably
                if current_price > config["highest_price"]:
                    # Update highest price
                    config["highest_price"] = current_price

                    # Calculate new stop level
                    new_stop = current_price - config["trail_distance"]

                    # Only move stop up, never down
                    if new_stop > config["current_stop"]:
                        await self._update_stop_order(config, new_stop)

    async def _update_stop_order(self, config: dict, new_stop: Decimal) -> Any:
        """Update the actual stop order price."""
        try:
            # Cancel existing stop order
            await self.client.orders.cancel_order(
                account_id=self.account_id,
                order_id=config["stop_order_id"],
            )

            # Place new stop order at updated level
            new_stop_response = await self.client.orders.post_stop_order(
                account_id=self.account_id,
                instrument=config["instrument"],
                units=-10000,  # Close position size
                price=new_stop,
                time_in_force="GTC",
            )

            # Update configuration
            config["current_stop"] = new_stop
            config["stop_order_id"] = new_stop_response.order_create_transaction.id

            print(f"Trailing stop updated: {new_stop}")

        except Exception as e:
            print(f"Failed to update trailing stop: {e}")

    async def monitor_trailing_stops(self, monitoring_duration: int = 3600) -> Any:
        """Continuously monitor and update trailing stops."""
        end_time = datetime.utcnow() + timedelta(seconds=monitoring_duration)

        while datetime.utcnow() < end_time and self.active_trails:
            await self.update_trailing_stops()
            await asyncio.sleep(30)  # Update every 30 seconds

        print("Trailing stop monitoring completed")
```

### Advanced Trailing Stop Strategies

#### Volatility-Adjusted Trailing

Adjust trail distance based on market volatility:

```python
from decimal import Decimal
from fivetwenty import AsyncClient


"""Comprehensive module for trading operations."""
async def volatility_adjusted_trailing() -> Any:
    """Implement trailing stops that adapt to market volatility."""
    async with AsyncClient() as client:
        # Calculate current volatility (simplified ATR calculation)
        current_atr = Decimal("0.0045")  # Example 4.5 pip ATR
        base_trail_distance = Decimal("0.0020")  # Base 2.0 pip trail

        # Adjust trail distance based on volatility
        volatility_multiplier = current_atr / Decimal("0.0030")  # Normalize to 3.0 pip base
        adjusted_trail = base_trail_distance * volatility_multiplier

        # Ensure reasonable bounds
        min_trail = Decimal("0.0015")  # Minimum 1.5 pips
        max_trail = Decimal("0.0060")  # Maximum 6.0 pips

        trail_distance = max(min_trail, min(max_trail, adjusted_trail))

        # Get current position details (simplified)
        current_price = Decimal("1.0875")
        initial_stop = current_price - trail_distance

        # Create volatility-adjusted trailing stop
        trail_manager = TrailingStopManager(client, "your_account_id")
        config = await trail_manager.create_trailing_stop(
            position_id="pos_123",
            initial_stop=initial_stop,
            trail_distance=trail_distance,
            instrument="EUR_USD"
        )

        print(f"Volatility-adjusted trail: {trail_distance} (ATR: {current_atr})")
        return config
```

#### Accelerated Trailing System

Tighten trail distance as profits increase:

```python
from decimal import Decimal

from fivetwenty import AsyncClient



"""Comprehensive module for trading operations."""
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

Build and reduce positions systematically based on market conditions.

### Scale-In Strategy Implementation

```python
from decimal import Decimal

from fivetwenty import AsyncClient



"""Comprehensive module for trading operations."""
class ScaleInStrategy:
    def __init__(self, client: AsyncClient, account_id: str) -> None:
        self.client = client
        self.account_id = account_id
        self.scale_levels = []
        self.filled_levels = []

    async def setup_scale_in_levels(
        self,
        instrument: str,
        base_price: Decimal,
        total_units: int,
        num_levels: int = 4,
        level_spacing: Decimal = Decimal("0.0020"),
    ):
        """Set up multiple scale-in levels below current price."""

        units_per_level = total_units // num_levels

        for i in range(num_levels):
            level_price = base_price - (level_spacing * (i + 1))

            scale_level = {
                "level": i + 1,
                "price": level_price,
                "units": units_per_level,
                "order_id": None,
                "filled": False,
            }

            self.scale_levels.append(scale_level)

        # Place all scale-in limit orders
        await self._place_scale_orders(instrument)

    async def _place_scale_orders(self, instrument: str) -> Any:
        """Place limit orders for all scale-in levels."""

        for level in self.scale_levels:
            if not level["filled"]:
                response = await self.client.orders.post_limit_order(
                    account_id=self.account_id,
                    instrument=instrument,
                    units=level["units"],
                    price=level["price"],
                    time_in_force="GTC",
                )

                level["order_id"] = response.order_create_transaction.id
                print(f"Scale level {level['level']} placed: {level['units']} @ {level['price']}")

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



"""Comprehensive module for trading operations."""
class ScaleOutStrategy:
    def __init__(self, client: AsyncClient, account_id: str) -> None:
        self.client = client
        self.account_id = account_id
        self.take_profit_levels = []

    async def setup_scale_out_levels(self, instrument: str, entry_price: Decimal, position_units: int, profit_targets: list, # List of profit distances in pips: Any) -> Any:
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

Create systems that respond intelligently to changing market conditions.

### Market Condition Adaptive System

```python
from decimal import Decimal
from fivetwenty import AsyncClient


"""Comprehensive module for trading operations."""
class AdaptivePositionManager:
    def __init__(self, client: AsyncClient, account_id: str) -> None:
        self.client = client
        self.account_id = account_id
        self.current_regime = "neutral"

    async def analyze_market_conditions(self, instrument: str) -> Any:
        """Analyze current market conditions to adapt strategy."""

        # Get current market data
        pricing = await self.client.pricing.get_pricing(
            account_id=self.account_id,
            instruments=[instrument]
        )

        current_spread = (
            Decimal(pricing.prices[0].asks[0].price) -
            Decimal(pricing.prices[0].bids[0].price)
        )

        # Simplified market condition analysis
        # In practice, you'd use more sophisticated indicators

        if current_spread < Decimal("0.0002"):  # Tight spread
            if self.current_regime != "tight":
                self.current_regime = "tight"
                return await self._adapt_to_tight_conditions(instrument)

        elif current_spread > Decimal("0.0005"):  # Wide spread
            if self.current_regime != "wide":
                self.current_regime = "wide"
                return await self._adapt_to_wide_conditions(instrument)

        else:  # Normal conditions
            if self.current_regime != "normal":
                self.current_regime = "normal"
                return await self._adapt_to_normal_conditions(instrument)

        return None  # No regime change

    async def _adapt_to_tight_conditions(self, instrument: str) -> Any:
        """Adapt strategy for tight spread conditions."""
        print("Adapting to tight spread conditions")

        # Tight conditions: Use aggressive pricing, smaller stops
        strategy_params = {
            "position_size_multiplier": Decimal("1.2"),  # Larger positions
            "stop_distance": Decimal("0.0015"),  # Tighter stops
            "take_profit_distance": Decimal("0.0025"),  # Closer targets
            "trail_distance": Decimal("0.0010")  # Tight trailing
        }

        return strategy_params

    async def _adapt_to_wide_conditions(self, instrument: str) -> Any:
        """Adapt strategy for wide spread conditions."""
        print("Adapting to wide spread conditions")

        # Wide conditions: Use conservative sizing, wider stops
        strategy_params = {
            "position_size_multiplier": Decimal("0.7"),  # Smaller positions
            "stop_distance": Decimal("0.0040"),  # Wider stops
            "take_profit_distance": Decimal("0.0060"),  # Distant targets
            "trail_distance": Decimal("0.0030")  # Loose trailing
        }

        return strategy_params

    async def _adapt_to_normal_conditions(self, instrument: str) -> Any:
        """Adapt strategy for normal market conditions."""
        print("Adapting to normal market conditions")

        strategy_params = {
            "position_size_multiplier": Decimal("1.0"),  # Standard positions
            "stop_distance": Decimal("0.0025"),  # Standard stops
            "take_profit_distance": Decimal("0.0040"),  # Standard targets
            "trail_distance": Decimal("0.0020")  # Standard trailing
        }

        return strategy_params
```

### Dynamic Risk Adjustment

Adjust risk parameters based on account performance:

```python
from decimal import Decimal
from fivetwenty import AsyncClient


"""Comprehensive module for trading operations."""
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

### Order Performance Analytics

```python
from decimal import Decimal

from fivetwenty import AsyncClient



"""Comprehensive module for trading operations."""
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

- **[Automated Order Systems](automated-systems.md)** - Rule-based management and monitoring
- **[Order Strategies & Combinations](order-strategies.md)** - Bracket orders and advanced techniques
- **[Validation & Best Practices](validation-best-practices.md)** - Risk management and error handling

## Key Takeaways

1. **Trailing stops** protect profits while maintaining upside potential
2. **Position scaling** enables systematic risk and reward management
3. **Adaptive systems** respond intelligently to changing market conditions
4. **Dynamic risk management** adjusts to account performance and market regime
5. **Performance monitoring** enables continuous strategy improvement
6. **Modular design** supports flexible and maintainable trading systems

Master these dynamic management techniques to build sophisticated trading systems that adapt intelligently to market conditions while maintaining robust risk controls.