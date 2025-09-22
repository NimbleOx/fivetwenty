# Advanced Limit Orders

Master sophisticated limit order techniques including time controls, protective mechanisms, and conditional execution strategies.

## Learning Objectives

By the end of this guide, you will:

- Implement advanced time controls for limit orders
- Use protective orders and contingent execution
- Apply price improvement strategies
- Build sophisticated entry/exit logic
- Handle partial fills and order management

## Time Control Mechanisms

### Good-Till-Date (GTD) Orders

GTD orders provide precise time control for strategic entries and exits:

```python
import asyncio
from datetime import datetime, timedelta
from decimal import Decimal
from fivetwenty import AsyncClient

async def place_gtd_limit_order():
    async with AsyncClient() as client:
        # Order expires at market close Friday
        friday_close = datetime(2024, 3, 15, 21, 0, 0)  # 9 PM UTC

        response = await client.orders.post_limit_order(
            account_id="your_account_id",
            instrument="EUR_USD",
            units=10000,
            price=Decimal("1.0850"),
            time_in_force="GTD",
            gtd_time=friday_close
        )

        print(f"GTD order expires: {friday_close}")
        return response
```

### Session-Based Time Controls

Align orders with specific trading sessions:

```python
async def session_based_orders():
    """Place orders that align with trading sessions."""
    from datetime import timezone

    async with AsyncClient() as client:
        # London session order (8 AM - 5 PM GMT)
        london_open = datetime.now(timezone.utc).replace(hour=8, minute=0, second=0)
        london_close = datetime.now(timezone.utc).replace(hour=17, minute=0, second=0)

        # Order active only during London session
        response = await client.orders.post_limit_order(
            account_id="your_account_id",
            instrument="GBP_USD",
            units=15000,
            price=Decimal("1.2650"),
            time_in_force="GTD",
            gtd_time=london_close
        )

        return response
```

### Immediate-or-Cancel (IOC) Strategies

Use IOC for immediate partial fills in fast markets:

```python
async def ioc_limit_strategy():
    """Use IOC for immediate execution with price protection."""
    async with AsyncClient() as client:
        # Large order that might not fill completely
        response = await client.orders.post_limit_order(
            account_id="your_account_id",
            instrument="EUR_USD",
            units=100000,  # Large size
            price=Decimal("1.0851"),  # Slightly favorable price
            time_in_force="IOC"  # Fill what you can, cancel rest
        )

        if response.order_fill_transaction:
            filled_units = response.order_fill_transaction.units
            print(f"Filled {filled_units} of 100,000 units")

        return response
```

## Protective Order Mechanisms

### Stop-Loss Protection for Limit Orders

Combine limit orders with automatic stop-loss protection:

```python
async def protected_limit_entry():
    """Place limit order with immediate stop-loss protection."""
    async with AsyncClient() as client:
        entry_price = Decimal("1.0850")
        stop_price = Decimal("1.0820")  # 30 pip stop
        target_price = Decimal("1.0920")  # 70 pip target

        # 1. Place limit entry order
        entry_response = await client.orders.post_limit_order(
            account_id="your_account_id",
            instrument="EUR_USD",
            units=10000,
            price=entry_price,
            time_in_force="GTC"
        )

        entry_order_id = entry_response.order_create_transaction.id

        # 2. Place contingent stop-loss (only if entry fills)
        stop_response = await client.orders.post_stop_order(
            account_id="your_account_id",
            instrument="EUR_USD",
            units=-10000,  # Close position
            price=stop_price,
            time_in_force="GTC",
            # This would be contingent on entry order filling
            # (Note: OANDA doesn't support true contingent orders,
            # so you'd need to monitor and place after entry fills)
        )

        return entry_order_id, stop_response.order_create_transaction.id
```

### Bracket Order Implementation

Create comprehensive position management with entry, stop, and target:

```python
class BracketOrder:
    def __init__(self, client: AsyncClient, account_id: str):
        self.client = client
        self.account_id = account_id
        self.entry_id = None
        self.stop_id = None
        self.target_id = None

    async def place_bracket_order(
        self,
        instrument: str,
        units: int,
        entry_price: Decimal,
        stop_price: Decimal,
        target_price: Decimal
    ):
        """Place a complete bracket order system."""

        # 1. Place entry limit order
        entry_response = await self.client.orders.post_limit_order(
            account_id=self.account_id,
            instrument=instrument,
            units=units,
            price=entry_price,
            time_in_force="GTC"
        )

        self.entry_id = entry_response.order_create_transaction.id
        print(f"Entry order placed: {self.entry_id}")

        return self.entry_id

    async def monitor_and_complete_bracket(self):
        """Monitor entry order and place protective orders when filled."""
        while True:
            # Check entry order status
            entry_order = await self.client.orders.get_order(
                account_id=self.account_id,
                order_id=self.entry_id
            )

            if entry_order.state == "FILLED":
                # Place stop-loss and take-profit orders
                await self._place_protective_orders(entry_order)
                break
            elif entry_order.state == "CANCELLED":
                print("Entry order cancelled")
                break

            await asyncio.sleep(1)  # Check every second

    async def _place_protective_orders(self, entry_order):
        """Place stop and target orders after entry fills."""
        # Implementation would place stop and target orders
        # based on the filled entry order details
        pass
```

## Price Improvement Strategies

### Dynamic Price Adjustment

Adjust limit prices based on market conditions:

```python
async def dynamic_limit_pricing():
    """Adjust limit order prices based on market movement."""
    async with AsyncClient() as client:
        instrument = "EUR_USD"
        base_price = Decimal("1.0850")

        # Get current market price
        pricing = await client.pricing.get_pricing(
            account_id="your_account_id",
            instruments=[instrument]
        )

        current_ask = Decimal(pricing.prices[0].asks[0].price)

        # Adjust limit price for better execution probability
        if current_ask < base_price:
            # Market moved favorably, improve our limit price
            adjusted_price = current_ask + Decimal("0.0005")  # Add 0.5 pips
        else:
            # Use original price
            adjusted_price = base_price

        response = await client.orders.post_limit_order(
            account_id="your_account_id",
            instrument=instrument,
            units=10000,
            price=adjusted_price,
            time_in_force="GTC"
        )

        print(f"Dynamic price: {adjusted_price} (market: {current_ask})")
        return response
```

### Iceberg Order Implementation

Break large orders into smaller chunks to hide size:

```python
class IcebergOrder:
    def __init__(self, client: AsyncClient, account_id: str):
        self.client = client
        self.account_id = account_id
        self.active_orders = []

    async def place_iceberg_order(
        self,
        instrument: str,
        total_units: int,
        price: Decimal,
        chunk_size: int = 10000
    ):
        """Place large order as series of smaller limit orders."""

        remaining_units = total_units

        while remaining_units > 0:
            # Calculate this chunk size
            current_chunk = min(chunk_size, remaining_units)

            # Place limit order for this chunk
            response = await self.client.orders.post_limit_order(
                account_id=self.account_id,
                instrument=instrument,
                units=current_chunk,
                price=price,
                time_in_force="GTC"
            )

            order_id = response.order_create_transaction.id
            self.active_orders.append(order_id)

            print(f"Iceberg chunk placed: {current_chunk} units, Order: {order_id}")

            remaining_units -= current_chunk

            # Wait before placing next chunk (avoid detection)
            await asyncio.sleep(2)

        return self.active_orders

    async def monitor_iceberg_execution(self):
        """Monitor and replace filled iceberg orders."""
        while self.active_orders:
            for order_id in self.active_orders[:]:  # Copy list for iteration
                order = await self.client.orders.get_order(
                    account_id=self.account_id,
                    order_id=order_id
                )

                if order.state == "FILLED":
                    print(f"Iceberg chunk filled: {order_id}")
                    self.active_orders.remove(order_id)
                    # Could place next chunk here if needed

            await asyncio.sleep(5)  # Check every 5 seconds
```

## Conditional Execution Logic

### Price Level Strategies

Implement sophisticated price-based conditions:

```python
async def conditional_limit_strategy():
    """Place limit orders based on technical levels."""
    async with AsyncClient() as client:
        instrument = "EUR_USD"

        # Define key levels
        support_level = Decimal("1.0800")
        resistance_level = Decimal("1.0900")
        current_price = Decimal("1.0850")

        # Strategy: Buy limit near support, sell limit near resistance
        if current_price > support_level + Decimal("0.0020"):  # 2 pips above support
            # Place buy limit near support
            buy_response = await client.orders.post_limit_order(
                account_id="your_account_id",
                instrument=instrument,
                units=10000,
                price=support_level + Decimal("0.0010"),  # 1 pip above support
                time_in_force="GTC"
            )
            print("Buy limit placed near support")

        if current_price < resistance_level - Decimal("0.0020"):  # 2 pips below resistance
            # Place sell limit near resistance
            sell_response = await client.orders.post_limit_order(
                account_id="your_account_id",
                instrument=instrument,
                units=-10000,
                price=resistance_level - Decimal("0.0010"),  # 1 pip below resistance
                time_in_force="GTC"
            )
            print("Sell limit placed near resistance")
```

### Volume-Based Conditions

Adjust orders based on market volume and activity:

```python
async def volume_based_limit_orders():
    """Adjust limit order strategy based on market activity."""
    async with AsyncClient() as client:
        # This would require external volume data
        # as OANDA doesn't provide tick volume in real-time

        # Simulated volume analysis
        high_volume_threshold = 1000  # trades per minute
        current_volume = 750  # Example current volume

        if current_volume > high_volume_threshold:
            # High volume: Use tighter spreads, shorter timeframes
            price_improvement = Decimal("0.0002")  # 0.2 pips
            time_limit = timedelta(minutes=15)
        else:
            # Low volume: Use wider spreads, longer timeframes
            price_improvement = Decimal("0.0005")  # 0.5 pips
            time_limit = timedelta(hours=2)

        current_ask = Decimal("1.0851")  # Example current price
        limit_price = current_ask - price_improvement

        expiry_time = datetime.utcnow() + time_limit

        response = await client.orders.post_limit_order(
            account_id="your_account_id",
            instrument="EUR_USD",
            units=10000,
            price=limit_price,
            time_in_force="GTD",
            gtd_time=expiry_time
        )

        print(f"Volume-based limit: {limit_price} (expires: {expiry_time})")
        return response
```

## Partial Fill Management

### Handling Incomplete Executions

Manage orders that fill partially:

```python
async def handle_partial_fills():
    """Monitor and manage partial order fills."""
    async with AsyncClient() as client:
        # Place large limit order that might fill partially
        response = await client.orders.post_limit_order(
            account_id="your_account_id",
            instrument="EUR_USD",
            units=50000,  # Large order
            price=Decimal("1.0850"),
            time_in_force="GTC"
        )

        order_id = response.order_create_transaction.id
        target_units = 50000
        filled_units = 0

        while filled_units < target_units:
            # Check order status
            order = await self.client.orders.get_order(
                account_id="your_account_id",
                order_id=order_id
            )

            if order.state == "FILLED":
                filled_units = target_units  # Completely filled
                print("Order completely filled")
                break
            elif order.state == "PARTIALLY_FILLED":
                # Get current fill amount
                filled_units = order.filled_units  # This field may vary by broker
                remaining = target_units - filled_units

                print(f"Partial fill: {filled_units}/{target_units}")

                # Decision: continue waiting or modify strategy
                if remaining < 10000:  # Small remainder
                    # Convert to market order for immediate fill
                    await client.orders.cancel_order(
                        account_id="your_account_id",
                        order_id=order_id
                    )

                    market_response = await client.orders.post_market_order(
                        account_id="your_account_id",
                        instrument="EUR_USD",
                        units=remaining,
                        time_in_force="FOK"
                    )
                    print(f"Remainder filled at market: {remaining}")
                    break

            await asyncio.sleep(10)  # Check every 10 seconds
```

## Performance Optimization

### Order Batching Strategies

Optimize execution by batching related orders:

```python
async def batch_limit_orders():
    """Place multiple related limit orders efficiently."""
    async with AsyncClient() as client:
        # Define multiple levels for scaling in
        orders_to_place = [
            {"price": Decimal("1.0840"), "units": 5000},
            {"price": Decimal("1.0830"), "units": 7500},
            {"price": Decimal("1.0820"), "units": 10000},
            {"price": Decimal("1.0810"), "units": 12500},
        ]

        placed_orders = []

        # Place all orders in sequence
        for order_spec in orders_to_place:
            response = await client.orders.post_limit_order(
                account_id="your_account_id",
                instrument="EUR_USD",
                units=order_spec["units"],
                price=order_spec["price"],
                time_in_force="GTC"
            )

            order_id = response.order_create_transaction.id
            placed_orders.append({
                "id": order_id,
                "price": order_spec["price"],
                "units": order_spec["units"]
            })

            print(f"Scaling order placed: {order_spec['units']} @ {order_spec['price']}")

        return placed_orders
```

### Smart Order Routing

Route orders based on market conditions:

```python
async def smart_limit_routing():
    """Route limit orders based on current market conditions."""
    async with AsyncClient() as client:
        # Get current market data
        pricing = await client.pricing.get_pricing(
            account_id="your_account_id",
            instruments=["EUR_USD"]
        )

        current_spread = (
            Decimal(pricing.prices[0].asks[0].price) -
            Decimal(pricing.prices[0].bids[0].price)
        )

        # Adjust strategy based on spread
        if current_spread < Decimal("0.0002"):  # Tight spread (0.2 pips)
            # Use aggressive pricing
            improvement = Decimal("0.0001")  # 0.1 pip improvement
            time_limit = timedelta(minutes=5)  # Short time limit
        else:
            # Use conservative pricing
            improvement = Decimal("0.0003")  # 0.3 pip improvement
            time_limit = timedelta(minutes=30)  # Longer time limit

        target_price = Decimal(pricing.prices[0].bids[0].price) + improvement
        expiry = datetime.utcnow() + time_limit

        response = await client.orders.post_limit_order(
            account_id="your_account_id",
            instrument="EUR_USD",
            units=10000,
            price=target_price,
            time_in_force="GTD",
            gtd_time=expiry
        )

        print(f"Smart routing: {target_price} (spread: {current_spread})")
        return response
```

## Error Handling and Validation

### Comprehensive Order Validation

```python
from fivetwenty.exceptions import VeeTwentyError

async def validated_limit_order(
    instrument: str,
    units: int,
    price: Decimal,
    max_spread_pips: int = 3
):
    """Place limit order with comprehensive validation."""
    async with AsyncClient() as client:
        try:
            # 1. Validate price is reasonable
            pricing = await client.pricing.get_pricing(
                account_id="your_account_id",
                instruments=[instrument]
            )

            current_ask = Decimal(pricing.prices[0].asks[0].price)
            current_bid = Decimal(pricing.prices[0].bids[0].price)
            current_spread = current_ask - current_bid

            # Check spread isn't too wide
            pip_value = Decimal("0.0001")  # For EUR/USD
            spread_pips = current_spread / pip_value

            if spread_pips > max_spread_pips:
                raise ValueError(f"Spread too wide: {spread_pips} pips")

            # 2. Validate price isn't too far from market
            if units > 0:  # Buy order
                max_price = current_ask * Decimal("1.01")  # 1% above ask
                if price > max_price:
                    raise ValueError(f"Buy price too high: {price}")
            else:  # Sell order
                min_price = current_bid * Decimal("0.99")  # 1% below bid
                if price < min_price:
                    raise ValueError(f"Sell price too low: {price}")

            # 3. Place order
            response = await client.orders.post_limit_order(
                account_id="your_account_id",
                instrument=instrument,
                units=units,
                price=price,
                time_in_force="GTC"
            )

            return response

        except VeeTwentyError as e:
            if "INSUFFICIENT_MARGIN" in str(e):
                print("Reduce position size - insufficient margin")
            elif "INVALID_PRICE" in str(e):
                print("Price outside valid bounds")
            elif "MARKET_CLOSED" in str(e):
                print("Market closed - order will be queued")
            else:
                print(f"Order validation failed: {e}")
            raise

        except ValueError as e:
            print(f"Pre-validation failed: {e}")
            raise
```

## Best Practices Summary

### Order Timing
- Use GTD orders for session-specific strategies
- Apply IOC for immediate execution needs
- Implement FOK for all-or-nothing requirements

### Price Management
- Always validate prices against current market
- Use dynamic pricing based on market conditions
- Implement price improvement strategies for better fills

### Risk Control
- Combine limit orders with protective stops
- Use position sizing based on account risk
- Monitor partial fills and adjust accordingly

### System Design
- Batch related orders for efficiency
- Implement smart routing based on conditions
- Use comprehensive error handling and validation

## Next Steps

Continue building your advanced order management skills:

- **[Stop Orders & Market-If-Touched](stop-orders-mit.md)** - Breakout and mean reversion strategies
- **[Dynamic Order Management](dynamic-management.md)** - Trailing stops and adaptive sizing
- **[Automated Order Systems](automated-systems.md)** - Rule-based management and monitoring

## Key Takeaways

1. **Time controls** enable precise order lifecycle management
2. **Protective mechanisms** reduce risk and automate responses
3. **Price improvement** strategies enhance execution quality
4. **Conditional logic** allows sophisticated entry/exit strategies
5. **Partial fill management** ensures complete position control
6. **Validation and error handling** prevent costly mistakes

Master these advanced limit order techniques to build professional-grade trading systems with sophisticated execution logic and robust risk management.