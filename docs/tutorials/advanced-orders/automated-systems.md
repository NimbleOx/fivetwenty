# Automated Order Systems

Learn to use FiveTwenty's automated order features for managing orders efficiently without manual intervention.

## Learning Objectives

By the end of this tutorial, you will:

- Use stop-loss and take-profit orders for automated exits
- Implement trailing stops for profit protection
- Set up order cancellation based on conditions
- Monitor and manage multiple orders efficiently

## Automated Exit Orders

FiveTwenty supports automated order management through OANDA's built-in order types.

### Stop Loss and Take Profit Orders

Place orders with automatic exit conditions:

```python
import os
from decimal import Decimal
from fivetwenty import AsyncClient, Environment

# Setup
token = os.getenv("OANDA_TOKEN")
account_id = "101-001-0000000-001"

async def place_order_with_exits():
    async with AsyncClient(token=token, environment=Environment.PRACTICE) as client:
        # Market order with automatic stops
        order = await client.orders.post_market_order(
            account_id=account_id,
            instrument="EUR_USD",
            units=10000,
            stop_loss_on_fill={
                "price": "1.0800",  # Automatic stop loss
                "time_in_force": "GTC"
            },
            take_profit_on_fill={
                "price": "1.0950",  # Automatic take profit
                "time_in_force": "GTC"
            }
        )

        print(f"Order placed: {order.order_fill_transaction.id}")
        print(f"Stop loss set at: {order.order_fill_transaction.stop_loss_order_transaction.price}")
        print(f"Take profit set at: {order.order_fill_transaction.take_profit_order_transaction.price}")

        return order
```

### Trailing Stop Orders

Use trailing stops to protect profits automatically:

```python
from decimal import Decimal
from fivetwenty import AsyncClient

async def place_trailing_stop_order():
    async with AsyncClient(token=token, environment=Environment.PRACTICE) as client:
        # Place order with trailing stop
        order = await client.orders.post_market_order(
            account_id=account_id,
            instrument="EUR_USD",
            units=10000,
            trailing_stop_loss_on_fill={
                "distance": "0.0050",  # 50 pips trailing distance
                "time_in_force": "GTC"
            }
        )

        print(f"Trailing stop order placed: {order.order_fill_transaction.id}")
        return order
```

## Order Monitoring and Management

Monitor multiple orders and implement conditional logic:

### Bulk Order Management

```python
import asyncio
from typing import Any
from fivetwenty import AsyncClient

async def monitor_and_manage_orders():
    async with AsyncClient(token=token, environment=Environment.PRACTICE) as client:
        # Get all pending orders
        orders_response = await client.orders.get_orders(account_id=account_id)

        for order in orders_response.orders:
            if order.state == "PENDING":
                print(f"Order {order.id}: {order.instrument} at {order.price}")

                # Example: Cancel orders older than 1 hour
                order_age = order.create_time  # You would compare with current time
                # if order_age > threshold:
                #     await client.orders.cancel_order(account_id, order.id)

        return orders_response.orders

async def cancel_orders_by_instrument(instrument: str):
    async with AsyncClient(token=token, environment=Environment.PRACTICE) as client:
        # Get all orders for specific instrument
        orders_response = await client.orders.get_orders(account_id=account_id)
        cancelled_orders = []

        for order in orders_response.orders:
            if order.instrument == instrument and order.state == "PENDING":
                try:
                    await client.orders.cancel_order(
                        account_id=account_id,
                        order_id=order.id
                    )
                    cancelled_orders.append(order.id)
                    print(f"Cancelled order {order.id}")
                except Exception as e:
                    print(f"Failed to cancel order {order.id}: {e}")

        return cancelled_orders
```

### Order Modification

Update existing orders based on market conditions:

```python
from decimal import Decimal

async def modify_order_price(order_id: str, new_price: Decimal):
    async with AsyncClient(token=token, environment=Environment.PRACTICE) as client:
        # Modify order price
        response = await client.orders.put_order(
            account_id=account_id,
            order_id=order_id,
            order={
                "price": str(new_price),
                "time_in_force": "GTC"
            }
        )

        print(f"Order {order_id} modified to price: {new_price}")
        return response
```

## Error Handling for Automated Systems

Handle common issues in automated order management:

```python
import asyncio
from fivetwenty.exceptions import VeeTwentyError

async def robust_order_placement():
    async with AsyncClient(token=token, environment=Environment.PRACTICE) as client:
        max_retries = 3
        retry_count = 0

        while retry_count < max_retries:
            try:
                order = await client.orders.post_limit_order(
                    account_id=account_id,
                    instrument="EUR_USD",
                    units=10000,
                    price=Decimal("1.0850"),
                    time_in_force="GTC"
                )

                print(f"Order placed successfully: {order.order_create_transaction.id}")
                return order

            except VeeTwentyError as e:
                if "INSUFFICIENT_MARGIN" in str(e):
                    print("Insufficient margin - reducing position size")
                    return None  # Or implement position size reduction
                elif "MARKET_CLOSED" in str(e):
                    print("Market closed - waiting...")
                    await asyncio.sleep(300)  # Wait 5 minutes
                    retry_count += 1
                else:
                    print(f"Order failed: {e}")
                    break

        print("Failed to place order after retries")
        return None
```

## Complete Example

Putting it all together for a simple automated trading setup:

```python
import asyncio
import os
from decimal import Decimal
from fivetwenty import AsyncClient, Environment

async def automated_trading_example():
    """Example of automated order management with FiveTwenty."""
    token = os.getenv("OANDA_TOKEN")
    account_id = "101-001-0000000-001"

    async with AsyncClient(token=token, environment=Environment.PRACTICE) as client:
        # 1. Place initial order with automated exits
        order = await client.orders.post_market_order(
            account_id=account_id,
            instrument="EUR_USD",
            units=10000,
            stop_loss_on_fill={
                "price": "1.0800",
                "time_in_force": "GTC"
            },
            take_profit_on_fill={
                "price": "1.0950",
                "time_in_force": "GTC"
            }
        )

        print(f"Initial order placed: {order.order_fill_transaction.id}")

        # 2. Monitor order status
        await asyncio.sleep(5)  # Wait a bit

        # 3. Check if order was filled and stops are active
        orders = await client.orders.get_orders(account_id=account_id)
        active_stops = [o for o in orders.orders if o.type in ["STOP_LOSS", "TAKE_PROFIT"]]

        print(f"Active stop orders: {len(active_stops)}")
        for stop in active_stops:
            print(f"  {stop.type} at {stop.price}")

        return {"initial_order": order, "active_stops": active_stops}

# Run the example
if __name__ == "__main__":
    asyncio.run(automated_trading_example())
```

## Key Takeaways

1. **Use OANDA's built-in automation** - Stop losses, take profits, and trailing stops
2. **Monitor order states** - Check pending, filled, and cancelled orders
3. **Implement error handling** - Gracefully handle market conditions
4. **Keep it simple** - Focus on SDK capabilities rather than complex rule engines

## Next Steps

- Explore [Order Strategies](order-strategies.md) for combining multiple order types
- Review [Validation Best Practices](validation-best-practices.md) for robust order handling
- See [Best Practices](../../explanation/best-practices.md) for production deployment

FiveTwenty provides the tools for automated order management - use OANDA's proven order types rather than building complex custom systems.