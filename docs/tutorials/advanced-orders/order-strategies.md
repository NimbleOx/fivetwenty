# Order Strategies & Combinations

Master sophisticated order combinations, bracket orders, and advanced trading strategies for professional-grade position management.

## Learning Objectives

By the end of this guide, you will:

- Implement comprehensive bracket order systems
- Design complex order combinations and sequences
- Create conditional order strategies
- Build hedge and arbitrage order systems
- Develop portfolio-level order coordination

## Bracket Order Systems

Bracket orders combine entry, stop-loss, and take-profit orders for complete position management.

### Complete Bracket Order Implementation

```python
import asyncio
from datetime import datetime
from decimal import Decimal
from typing import Dict, Optional

from fivetwenty import AsyncClient


class BracketOrderManager:
    def __init__(self, client: AsyncClient, account_id: str):
        self.client = client
        self.account_id = account_id
        self.active_brackets = {}

    async def place_bracket_order(
        self,
        instrument: str,
        entry_type: str,  # "LIMIT" or "MARKET" or "STOP"
        units: int,
        entry_price: Decimal | None = None,
        stop_loss_price: Decimal = None,
        take_profit_price: Decimal = None,
        risk_reward_ratio: Decimal | None = None,
    ) -> dict[str, str]:
        """Place a complete bracket order with entry, stop, and target."""

        bracket_id = f"bracket_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"

        # Calculate prices if risk/reward ratio provided
        if risk_reward_ratio and entry_price and stop_loss_price and not take_profit_price:
            stop_distance = abs(entry_price - stop_loss_price)
            target_distance = stop_distance * risk_reward_ratio

            if units > 0:  # Long position
                take_profit_price = entry_price + target_distance
            else:  # Short position
                take_profit_price = entry_price - target_distance

        # 1. Place entry order
        entry_order_id = await self._place_entry_order(
            instrument, entry_type, units, entry_price,
        )

        # Store bracket configuration
        bracket_config = {
            "bracket_id": bracket_id,
            "instrument": instrument,
            "entry_order_id": entry_order_id,
            "units": units,
            "stop_loss_price": stop_loss_price,
            "take_profit_price": take_profit_price,
            "entry_filled": False,
            "stop_order_id": None,
            "target_order_id": None,
            "status": "PENDING_ENTRY",
        }

        self.active_brackets[bracket_id] = bracket_config

        # 2. Start monitoring for entry fill
        asyncio.create_task(self._monitor_bracket_entry(bracket_id))

        print(f"Bracket order placed: {bracket_id}")
        return bracket_config

    async def _place_entry_order(
        self,
        instrument: str,
        entry_type: str,
        units: int,
        entry_price: Decimal | None,
    ) -> str:
        """Place the entry order component."""

        if entry_type == "MARKET":
            response = await self.client.orders.post_market_order(
                account_id=self.account_id,
                instrument=instrument,
                units=units,
                time_in_force="FOK",
            )
        elif entry_type == "LIMIT":
            response = await self.client.orders.post_limit_order(
                account_id=self.account_id,
                instrument=instrument,
                units=units,
                price=entry_price,
                time_in_force="GTC",
            )
        elif entry_type == "STOP":
            response = await self.client.orders.post_stop_order(
                account_id=self.account_id,
                instrument=instrument,
                units=units,
                price=entry_price,
                time_in_force="GTC",
            )

        return response.order_create_transaction.id

    async def _monitor_bracket_entry(self, bracket_id: str):
        """Monitor entry order and place protective orders when filled."""

        bracket = self.active_brackets[bracket_id]
        entry_order_id = bracket["entry_order_id"]

        while not bracket["entry_filled"]:
            try:
                # Check entry order status
                order = await self.client.orders.get_order(
                    account_id=self.account_id,
                    order_id=entry_order_id,
                )

                if order.state == "FILLED":
                    bracket["entry_filled"] = True
                    bracket["status"] = "ENTRY_FILLED"

                    # Get actual fill price
                    fill_price = Decimal(order.filling_transaction.price)
                    bracket["actual_entry_price"] = fill_price

                    # Place protective orders
                    await self._place_protective_orders(bracket_id, fill_price)

                    print(f"Bracket {bracket_id} entry filled at {fill_price}")
                    break

                elif order.state == "CANCELLED":
                    bracket["status"] = "CANCELLED"
                    print(f"Bracket {bracket_id} entry order cancelled")
                    break

            except Exception as e:
                print(f"Error monitoring bracket entry: {e}")

            await asyncio.sleep(5)  # Check every 5 seconds

    async def _place_protective_orders(self, bracket_id: str, entry_price: Decimal):
        """Place stop-loss and take-profit orders after entry fills."""

        bracket = self.active_brackets[bracket_id]
        instrument = bracket["instrument"]
        units = bracket["units"]

        # Place stop-loss order
        if bracket["stop_loss_price"]:
            stop_response = await self.client.orders.post_stop_order(
                account_id=self.account_id,
                instrument=instrument,
                units=-units,  # Opposite direction to close position
                price=bracket["stop_loss_price"],
                time_in_force="GTC",
            )

            bracket["stop_order_id"] = stop_response.order_create_transaction.id
            print(f"Stop-loss placed: {bracket['stop_loss_price']}")

        # Place take-profit order
        if bracket["take_profit_price"]:
            target_response = await self.client.orders.post_limit_order(
                account_id=self.account_id,
                instrument=instrument,
                units=-units,  # Opposite direction to close position
                price=bracket["take_profit_price"],
                time_in_force="GTC",
            )

            bracket["target_order_id"] = target_response.order_create_transaction.id
            print(f"Take-profit placed: {bracket['take_profit_price']}")

        bracket["status"] = "PROTECTIVE_ORDERS_PLACED"

        # Start monitoring protective orders
        asyncio.create_task(self._monitor_protective_orders(bracket_id))

    async def _monitor_protective_orders(self, bracket_id: str):
        """Monitor stop-loss and take-profit orders."""

        bracket = self.active_brackets[bracket_id]

        while bracket["status"] not in ["STOPPED_OUT", "TARGET_HIT", "MANUALLY_CLOSED"]:
            try:
                # Check stop-loss order
                if bracket["stop_order_id"]:
                    stop_order = await self.client.orders.get_order(
                        account_id=self.account_id,
                        order_id=bracket["stop_order_id"],
                    )

                    if stop_order.state == "FILLED":
                        bracket["status"] = "STOPPED_OUT"
                        await self._cleanup_remaining_orders(bracket_id)
                        print(f"Bracket {bracket_id} stopped out")
                        break

                # Check take-profit order
                if bracket["target_order_id"]:
                    target_order = await self.client.orders.get_order(
                        account_id=self.account_id,
                        order_id=bracket["target_order_id"],
                    )

                    if target_order.state == "FILLED":
                        bracket["status"] = "TARGET_HIT"
                        await self._cleanup_remaining_orders(bracket_id)
                        print(f"Bracket {bracket_id} target hit")
                        break

            except Exception as e:
                print(f"Error monitoring protective orders: {e}")

            await asyncio.sleep(10)  # Check every 10 seconds

    async def _cleanup_remaining_orders(self, bracket_id: str):
        """Cancel remaining orders when one protective order fills."""

        bracket = self.active_brackets[bracket_id]

        # Cancel remaining protective orders
        orders_to_cancel = []

        if bracket["stop_order_id"] and bracket["status"] != "STOPPED_OUT":
            orders_to_cancel.append(bracket["stop_order_id"])

        if bracket["target_order_id"] and bracket["status"] != "TARGET_HIT":
            orders_to_cancel.append(bracket["target_order_id"])

        for order_id in orders_to_cancel:
            try:
                await self.client.orders.cancel_order(
                    account_id=self.account_id,
                    order_id=order_id,
                )
            except Exception as e:
                print(f"Failed to cancel order {order_id}: {e}")
```

### Advanced Bracket Strategies

#### Scaling Bracket Orders

```python
from decimal import Decimal
from fivetwenty import AsyncClient

async def scaling_bracket_strategy():
    """Implement scaling bracket orders with multiple entry and exit levels."""
    async with AsyncClient() as client:
        bracket_manager = BracketOrderManager(client, "your_account_id")

        # Define scaling entry levels
        base_price = Decimal("1.0850")
        scale_levels = [
            {"price": base_price, "units": 5000},
            {"price": base_price - Decimal("0.0010"), "units": 7500},
            {"price": base_price - Decimal("0.0020"), "units": 10000},
        ]

        # Calculate average stop and target levels
        total_units = sum(level["units"] for level in scale_levels)
        weighted_entry = sum(
            level["price"] * level["units"] for level in scale_levels
        ) / total_units

        stop_distance = Decimal("0.0030")  # 3.0 pip stop
        target_distance = Decimal("0.0060")  # 6.0 pip target (2:1 R/R)

        stop_price = weighted_entry - stop_distance
        target_price = weighted_entry + target_distance

        # Place scaling bracket orders
        placed_brackets = []

        for level in scale_levels:
            bracket = await bracket_manager.place_bracket_order(
                instrument="EUR_USD",
                entry_type="LIMIT",
                units=level["units"],
                entry_price=level["price"],
                stop_loss_price=stop_price,
                take_profit_price=target_price
            )

            placed_brackets.append(bracket)

        print(f"Scaling bracket strategy deployed: {len(placed_brackets)} levels")
        return placed_brackets
```

#### Trailing Bracket System

```python
from decimal import Decimal


class TrailingBracketManager(BracketOrderManager):
    """Bracket manager with trailing stop functionality."""

    async def _place_protective_orders(self, bracket_id: str, entry_price: Decimal):
        """Place protective orders with trailing stop capability."""

        await super()._place_protective_orders(bracket_id, entry_price)

        # Start trailing stop management
        bracket = self.active_brackets[bracket_id]
        if bracket["stop_order_id"]:
            asyncio.create_task(self._manage_trailing_stop(bracket_id))

    async def _manage_trailing_stop(self, bracket_id: str):
        """Manage trailing stop for the bracket order."""

        bracket = self.active_brackets[bracket_id]
        instrument = bracket["instrument"]
        units = bracket["units"]

        trail_distance = Decimal("0.0020")  # 2.0 pip trail
        highest_favorable = bracket["actual_entry_price"]

        while bracket["status"] == "PROTECTIVE_ORDERS_PLACED":
            try:
                # Get current price
                pricing = await self.client.pricing.get_pricing(
                    account_id=self.account_id,
                    instruments=[instrument],
                )

                if units > 0:  # Long position
                    current_price = Decimal(pricing.prices[0].bids[0].price)
                    if current_price > highest_favorable:
                        highest_favorable = current_price
                        new_stop = current_price - trail_distance

                        # Only move stop up, never down
                        if new_stop > bracket["stop_loss_price"]:
                            await self._update_stop_order(bracket_id, new_stop)

                else:  # Short position
                    current_price = Decimal(pricing.prices[0].asks[0].price)
                    if current_price < highest_favorable:
                        highest_favorable = current_price
                        new_stop = current_price + trail_distance

                        # Only move stop down, never up
                        if new_stop < bracket["stop_loss_price"]:
                            await self._update_stop_order(bracket_id, new_stop)

            except Exception as e:
                print(f"Trailing stop error: {e}")

            await asyncio.sleep(30)  # Update every 30 seconds

    async def _update_stop_order(self, bracket_id: str, new_stop_price: Decimal):
        """Update the stop-loss order price."""

        bracket = self.active_brackets[bracket_id]

        try:
            # Cancel existing stop order
            await self.client.orders.cancel_order(
                account_id=self.account_id,
                order_id=bracket["stop_order_id"],
            )

            # Place new stop order
            stop_response = await self.client.orders.post_stop_order(
                account_id=self.account_id,
                instrument=bracket["instrument"],
                units=-bracket["units"],
                price=new_stop_price,
                time_in_force="GTC",
            )

            bracket["stop_order_id"] = stop_response.order_create_transaction.id
            bracket["stop_loss_price"] = new_stop_price

            print(f"Trailing stop updated: {new_stop_price}")

        except Exception as e:
            print(f"Failed to update trailing stop: {e}")
```

## Complex Order Combinations

Create sophisticated order sequences and conditional strategies.

### Conditional Order Chains

```python
from datetime import datetime
from decimal import Decimal
from fivetwenty import AsyncClient

class ConditionalOrderChain:
    def __init__(self, client: AsyncClient, account_id: str):
        self.client = client
        self.account_id = account_id
        self.chain_configs = {}

    async def create_if_then_order_chain(
        self,
        trigger_condition: Dict[str, Any],
        primary_orders: List[Dict[str, Any]],
        secondary_orders: List[Dict[str, Any]]
    ) -> str:
        """Create conditional order chain: if trigger, then primary, then secondary."""

        chain_id = f"chain_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"

        chain_config = {
            "chain_id": chain_id,
            "trigger_condition": trigger_condition,
            "primary_orders": primary_orders,
            "secondary_orders": secondary_orders,
            "status": "WAITING_TRIGGER",
            "triggered_time": None,
            "primary_filled": [],
            "secondary_filled": []
        }

        self.chain_configs[chain_id] = chain_config

        # Start monitoring trigger condition
        asyncio.create_task(self._monitor_trigger_condition(chain_id))

        return chain_id

    async def _monitor_trigger_condition(self, chain_id: str):
        """Monitor for trigger condition to be met."""

        chain = self.chain_configs[chain_id]
        trigger = chain["trigger_condition"]

        while chain["status"] == "WAITING_TRIGGER":
            try:
                if await self._evaluate_trigger(trigger):
                    chain["status"] = "TRIGGERED"
                    chain["triggered_time"] = datetime.utcnow()

                    # Execute primary orders
                    await self._execute_primary_orders(chain_id)
                    break

            except Exception as e:
                print(f"Trigger monitoring error: {e}")

            await asyncio.sleep(10)  # Check every 10 seconds

    async def _evaluate_trigger(self, trigger: Dict[str, Any]) -> bool:
        """Evaluate if trigger condition is met."""

        trigger_type = trigger["type"]

        if trigger_type == "price_level":
            # Price crosses specific level
            instrument = trigger["instrument"]
            target_price = trigger["price"]
            direction = trigger["direction"]  # "above" or "below"

            pricing = await self.client.pricing.get_pricing(
                account_id=self.account_id,
                instruments=[instrument]
            )

            current_price = Decimal(pricing.prices[0].asks[0].price)

            if direction == "above":
                return current_price >= target_price
            else:
                return current_price <= target_price

        elif trigger_type == "time_based":
            # Time-based trigger
            target_time = trigger["trigger_time"]
            return datetime.utcnow() >= target_time

        elif trigger_type == "order_fill":
            # Another order fills
            order_id = trigger["order_id"]
            order = await self.client.orders.get_order(
                account_id=self.account_id,
                order_id=order_id
            )
            return order.state == "FILLED"

        return False

    async def _execute_primary_orders(self, chain_id: str):
        """Execute primary orders after trigger."""

        chain = self.chain_configs[chain_id]
        primary_orders = chain["primary_orders"]

        for order_spec in primary_orders:
            try:
                order_id = await self._place_order_from_spec(order_spec)
                chain["primary_filled"].append(order_id)
                print(f"Primary order placed: {order_id}")

            except Exception as e:
                print(f"Failed to place primary order: {e}")

        # Start monitoring primary orders for secondary trigger
        asyncio.create_task(self._monitor_primary_completion(chain_id))

    async def _place_order_from_spec(self, order_spec: Dict[str, Any]) -> str:
        """Place order from specification dictionary."""

        order_type = order_spec["type"]
        instrument = order_spec["instrument"]
        units = order_spec["units"]

        if order_type == "MARKET":
            response = await self.client.orders.post_market_order(
                account_id=self.account_id,
                instrument=instrument,
                units=units,
                time_in_force="FOK"
            )

        elif order_type == "LIMIT":
            response = await self.client.orders.post_limit_order(
                account_id=self.account_id,
                instrument=instrument,
                units=units,
                price=order_spec["price"],
                time_in_force="GTC"
            )

        elif order_type == "STOP":
            response = await self.client.orders.post_stop_order(
                account_id=self.account_id,
                instrument=instrument,
                units=units,
                price=order_spec["price"],
                time_in_force="GTC"
            )

        return response.order_create_transaction.id

    async def _monitor_primary_completion(self, chain_id: str):
        """Monitor primary orders and trigger secondary when appropriate."""

        chain = self.chain_configs[chain_id]

        # Wait for all primary orders to fill or specific condition
        while chain["status"] == "TRIGGERED":
            # Check if condition met for secondary orders
            if await self._check_secondary_trigger(chain_id):
                await self._execute_secondary_orders(chain_id)
                break

            await asyncio.sleep(15)

    async def _check_secondary_trigger(self, chain_id: str) -> bool:
        """Check if secondary orders should be triggered."""

        chain = self.chain_configs[chain_id]

        # Example: trigger secondary when any primary order fills
        for order_id in chain["primary_filled"]:
            try:
                order = await self.client.orders.get_order(
                    account_id=self.account_id,
                    order_id=order_id
                )

                if order.state == "FILLED":
                    return True

            except Exception:
                continue

        return False

    async def _execute_secondary_orders(self, chain_id: str):
        """Execute secondary orders."""

        chain = self.chain_configs[chain_id]
        secondary_orders = chain["secondary_orders"]

        for order_spec in secondary_orders:
            try:
                order_id = await self._place_order_from_spec(order_spec)
                chain["secondary_filled"].append(order_id)
                print(f"Secondary order placed: {order_id}")

            except Exception as e:
                print(f"Failed to place secondary order: {e}")

        chain["status"] = "COMPLETED"
```

### OCO (One-Cancels-Other) Orders

```python
from datetime import datetime

from fivetwenty import AsyncClient


class OCOOrderManager:
    def __init__(self, client: AsyncClient, account_id: str):
        self.client = client
        self.account_id = account_id
        self.oco_groups = {}

    async def place_oco_orders(
        self,
        instrument: str,
        order1_spec: Dict[str, Any],
        order2_spec: Dict[str, Any],
    ) -> str:
        """Place two orders where filling one cancels the other."""

        oco_id = f"oco_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"

        # Place both orders
        order1_id = await self._place_order_from_spec(order1_spec)
        order2_id = await self._place_order_from_spec(order2_spec)

        # Store OCO configuration
        oco_config = {
            "oco_id": oco_id,
            "instrument": instrument,
            "order1_id": order1_id,
            "order2_id": order2_id,
            "order1_spec": order1_spec,
            "order2_spec": order2_spec,
            "status": "ACTIVE",
        }

        self.oco_groups[oco_id] = oco_config

        # Start monitoring
        asyncio.create_task(self._monitor_oco_group(oco_id))

        print(f"OCO orders placed: {order1_id}, {order2_id}")
        return oco_id

    async def _monitor_oco_group(self, oco_id: str):
        """Monitor OCO orders and cancel the other when one fills."""

        oco = self.oco_groups[oco_id]

        while oco["status"] == "ACTIVE":
            try:
                # Check both orders
                order1 = await self.client.orders.get_order(
                    account_id=self.account_id,
                    order_id=oco["order1_id"],
                )

                order2 = await self.client.orders.get_order(
                    account_id=self.account_id,
                    order_id=oco["order2_id"],
                )

                # If order1 fills, cancel order2
                if order1.state == "FILLED":
                    await self._cancel_order_safe(oco["order2_id"])
                    oco["status"] = "ORDER1_FILLED"
                    print(f"OCO {oco_id}: Order1 filled, Order2 cancelled")
                    break

                # If order2 fills, cancel order1
                elif order2.state == "FILLED":
                    await self._cancel_order_safe(oco["order1_id"])
                    oco["status"] = "ORDER2_FILLED"
                    print(f"OCO {oco_id}: Order2 filled, Order1 cancelled")
                    break

                # If either order is cancelled externally
                elif order1.state == "CANCELLED" or order2.state == "CANCELLED":
                    oco["status"] = "EXTERNALLY_CANCELLED"
                    break

            except Exception as e:
                print(f"OCO monitoring error: {e}")

            await asyncio.sleep(5)

    async def _cancel_order_safe(self, order_id: str):
        """Cancel order with error handling."""
        try:
            await self.client.orders.cancel_order(
                account_id=self.account_id,
                order_id=order_id,
            )
        except Exception as e:
            print(f"Failed to cancel order {order_id}: {e}")

    async def _place_order_from_spec(self, order_spec: Dict[str, Any]) -> str:
        """Place order from specification (same as ConditionalOrderChain)."""
        # Implementation same as above
        pass
```

## Hedge and Arbitrage Strategies

Implement sophisticated multi-instrument strategies.

### Pairs Trading System

```python
from datetime import datetime
from decimal import Decimal
from fivetwenty import AsyncClient

class PairsTradingStrategy:
    def __init__(self, client: AsyncClient, account_id: str):
        self.client = client
        self.account_id = account_id
        self.active_pairs = {}

    async def setup_pairs_trade(
        self,
        instrument1: str,
        instrument2: str,
        hedge_ratio: Decimal,
        entry_threshold: Decimal,
        exit_threshold: Decimal
    ) -> str:
        """Set up pairs trading strategy between two instruments."""

        pair_id = f"pair_{instrument1}_{instrument2}_{datetime.utcnow().strftime('%H%M%S')}"

        pair_config = {
            "pair_id": pair_id,
            "instrument1": instrument1,
            "instrument2": instrument2,
            "hedge_ratio": hedge_ratio,
            "entry_threshold": entry_threshold,
            "exit_threshold": exit_threshold,
            "status": "MONITORING",
            "position_open": False,
            "entry_spread": None,
            "orders": []
        }

        self.active_pairs[pair_id] = pair_config

        # Start monitoring spread
        asyncio.create_task(self._monitor_pairs_spread(pair_id))

        return pair_id

    async def _monitor_pairs_spread(self, pair_id: str):
        """Monitor spread between pair instruments."""

        pair = self.active_pairs[pair_id]

        while pair["status"] == "MONITORING":
            try:
                # Get current prices for both instruments
                pricing1 = await self.client.pricing.get_pricing(
                    account_id=self.account_id,
                    instruments=[pair["instrument1"]]
                )

                pricing2 = await self.client.pricing.get_pricing(
                    account_id=self.account_id,
                    instruments=[pair["instrument2"]]
                )

                price1 = Decimal(pricing1.prices[0].asks[0].price)
                price2 = Decimal(pricing2.prices[0].asks[0].price)

                # Calculate spread
                current_spread = price1 - (price2 * pair["hedge_ratio"])

                if not pair["position_open"]:
                    # Check for entry signal
                    if abs(current_spread) >= pair["entry_threshold"]:
                        await self._execute_pairs_entry(pair_id, current_spread)

                else:
                    # Check for exit signal
                    if abs(current_spread) <= pair["exit_threshold"]:
                        await self._execute_pairs_exit(pair_id)

            except Exception as e:
                print(f"Pairs monitoring error: {e}")

            await asyncio.sleep(30)  # Check every 30 seconds

    async def _execute_pairs_entry(self, pair_id: str, spread: Decimal):
        """Execute pairs trade entry."""

        pair = self.active_pairs[pair_id]
        base_units = 10000

        if spread > 0:
            # Spread too wide: sell instrument1, buy instrument2
            units1 = -base_units
            units2 = int(base_units * pair["hedge_ratio"])
        else:
            # Spread too narrow: buy instrument1, sell instrument2
            units1 = base_units
            units2 = -int(base_units * pair["hedge_ratio"])

        # Place both orders simultaneously
        try:
            order1 = await self.client.orders.post_market_order(
                account_id=self.account_id,
                instrument=pair["instrument1"],
                units=units1,
                time_in_force="FOK"
            )

            order2 = await self.client.orders.post_market_order(
                account_id=self.account_id,
                instrument=pair["instrument2"],
                units=units2,
                time_in_force="FOK"
            )

            pair["orders"].extend([order1.order_create_transaction.id, order2.order_create_transaction.id])
            pair["position_open"] = True
            pair["entry_spread"] = spread

            print(f"Pairs trade entered: {pair_id} at spread {spread}")

        except Exception as e:
            print(f"Failed to execute pairs entry: {e}")

    async def _execute_pairs_exit(self, pair_id: str):
        """Execute pairs trade exit."""

        pair = self.active_pairs[pair_id]

        # Get current positions to close
        positions = await self.client.positions.get_positions(
            account_id=self.account_id
        )

        try:
            # Close positions in both instruments
            for position in positions.positions:
                if position.instrument in [pair["instrument1"], pair["instrument2"]]:
                    if position.long.units != "0":
                        # Close long position
                        await self.client.orders.post_market_order(
                            account_id=self.account_id,
                            instrument=position.instrument,
                            units=-int(position.long.units),
                            time_in_force="FOK"
                        )

                    if position.short.units != "0":
                        # Close short position
                        await self.client.orders.post_market_order(
                            account_id=self.account_id,
                            instrument=position.instrument,
                            units=-int(position.short.units),
                            time_in_force="FOK"
                        )

            pair["position_open"] = False
            pair["status"] = "CLOSED"

            print(f"Pairs trade closed: {pair_id}")

        except Exception as e:
            print(f"Failed to execute pairs exit: {e}")
```

### Portfolio Hedging System

```python
from decimal import Decimal

from fivetwenty import AsyncClient


class PortfolioHedgeManager:
    def __init__(self, client: AsyncClient, account_id: str):
        self.client = client
        self.account_id = account_id
        self.hedge_instruments = ["USD_JPY", "EUR_USD", "GBP_USD"]  # Safe haven currencies

    async def calculate_portfolio_exposure(self) -> Dict[str, Decimal]:
        """Calculate current portfolio exposure by currency."""

        positions = await self.client.positions.get_positions(
            account_id=self.account_id,
        )

        exposure = {"USD": Decimal("0"), "EUR": Decimal("0"), "GBP": Decimal("0"), "JPY": Decimal("0")}

        for position in positions.positions:
            # Parse instrument for base and quote currencies
            base_currency, quote_currency = position.instrument.split("_")

            # Calculate exposure in base currency
            if position.long.units != "0":
                long_exposure = Decimal(position.long.units)
                exposure[base_currency] += long_exposure
                # Approximate quote currency exposure (negative)
                exposure[quote_currency] -= long_exposure

            if position.short.units != "0":
                short_exposure = Decimal(position.short.units)
                exposure[base_currency] += short_exposure  # Short units are negative
                exposure[quote_currency] -= short_exposure

        return exposure

    async def hedge_portfolio_risk(self, max_exposure: Decimal = Decimal("50000")):
        """Hedge portfolio to reduce overall currency exposure."""

        exposure = await self.calculate_portfolio_exposure()

        # Identify currencies with excessive exposure
        hedges_needed = []

        for currency, net_exposure in exposure.items():
            if abs(net_exposure) > max_exposure:
                hedges_needed.append({
                    "currency": currency,
                    "exposure": net_exposure,
                    "hedge_amount": -net_exposure * Decimal("0.7"),  # Hedge 70%
                })

        # Place hedge orders
        for hedge in hedges_needed:
            await self._place_hedge_order(hedge)

    async def _place_hedge_order(self, hedge: Dict[str, Any]):
        """Place hedge order for specific currency exposure."""

        currency = hedge["currency"]
        hedge_amount = hedge["hedge_amount"]

        # Find appropriate hedging instrument
        hedge_instrument = None
        hedge_units = hedge_amount

        if currency == "USD":
            hedge_instrument = "USD_JPY"  # Use JPY as hedge
        elif currency == "EUR":
            hedge_instrument = "EUR_USD"
            hedge_units = hedge_amount  # EUR exposure
        elif currency == "GBP":
            hedge_instrument = "GBP_USD"
            hedge_units = hedge_amount  # GBP exposure

        if hedge_instrument:
            try:
                hedge_response = await self.client.orders.post_market_order(
                    account_id=self.account_id,
                    instrument=hedge_instrument,
                    units=int(hedge_units),
                    time_in_force="FOK",
                )

                print(f"Portfolio hedge placed: {hedge_instrument} {hedge_units}")

            except Exception as e:
                print(f"Failed to place hedge: {e}")
```

## Best Practices Summary

### Bracket Order Design
- Always include protective stops and targets
- Use appropriate risk/reward ratios
- Implement trailing mechanisms for profit protection
- Monitor all components for completion

### Order Combinations
- Design modular, reusable order components
- Implement proper error handling and recovery
- Use conditional logic for market adaptation
- Maintain clear order state tracking

### Portfolio Strategies
- Calculate exposures accurately across instruments
- Use appropriate hedge ratios for pairs trading
- Monitor correlations and spread relationships
- Implement position sizing based on overall risk

### System Architecture
- Design asynchronous, scalable order management
- Implement comprehensive logging and monitoring
- Use event-driven patterns for responsiveness
- Maintain audit trails for all order actions

## Next Steps

Complete your advanced order management education:

- **[Validation & Best Practices](validation-best-practices.md)** - Risk management and error handling

## Key Takeaways

1. **Bracket orders** provide comprehensive position management with automatic protection
2. **Order combinations** enable sophisticated conditional trading strategies
3. **Multi-instrument strategies** require careful coordination and risk management
4. **Portfolio-level thinking** is essential for professional risk management
5. **Asynchronous design** enables scalable, responsive order systems
6. **Comprehensive monitoring** ensures reliable strategy execution and risk control

Master these advanced order strategies to build institutional-quality trading systems that handle complex multi-instrument positions with sophisticated risk management and automated execution logic.