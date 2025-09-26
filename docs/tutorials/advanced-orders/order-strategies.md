# Order Strategies & Combinations

Learn to combine FiveTwenty's order types effectively for common trading scenarios.

## Learning Objectives

By the end of this tutorial, you will:

- Use market orders with automatic stop-loss and take-profit
- Implement entry orders with protective stops
- Combine multiple order types for complete strategies
- Handle order fills and automatic order creation

## Basic Order Combinations

### Market Entry with Protective Orders

Place a market order with automatic stop-loss and take-profit:

```python
import os
from fivetwenty import AsyncClient, Environment

# Setup
token = os.getenv("OANDA_TOKEN")
account_id = "101-001-0000000-001"

async def market_order_with_protection():
    async with AsyncClient(token=token, environment=Environment.PRACTICE) as client:
        # Market order with both stop loss and take profit
        order = await client.orders.post_market_order(
            account_id=account_id,
            instrument="EUR_USD",
            units=10000,
            stop_loss_on_fill={
                "price": "1.0800",  # Risk 50 pips
                "time_in_force": "GTC"
            },
            take_profit_on_fill={
                "price": "1.0950",  # Target 100 pips (2:1 reward/risk)
                "time_in_force": "GTC"
            }
        )

        print(f"Order filled at: {order.order_fill_transaction.price}")
        print(f"Stop loss: {order.order_fill_transaction.stop_loss_order_transaction.price}")
        print(f"Take profit: {order.order_fill_transaction.take_profit_order_transaction.price}")

        return order
```

### Pending Entry with Protection

Set up a limit order that automatically adds stops when filled:

```python
import os
from decimal import Decimal
from fivetwenty import AsyncClient, Environment

# Setup
token = os.getenv("OANDA_TOKEN")
account_id = "101-001-0000000-001"

async def limit_entry_with_protection():
    async with AsyncClient(token=token, environment=Environment.PRACTICE) as client:
        # Limit order to buy on pullback with protective orders
        order = await client.orders.post_limit_order(
            account_id=account_id,
            instrument="EUR_USD",
            units=10000,
            price=Decimal("1.0850"),  # Entry level
            time_in_force="GTC",
            stop_loss_on_fill={
                "price": "1.0800",  # 50 pip stop
                "time_in_force": "GTC"
            },
            take_profit_on_fill={
                "price": "1.0950",  # 100 pip target
                "time_in_force": "GTC"
            }
        )

        print(f"Limit order placed at: {order.order_create_transaction.price}")
        return order
```

## Multiple Position Management

### Scaling Into Positions

Build positions with multiple entries:

```python
import os
from decimal import Decimal
from fivetwenty import AsyncClient, Environment

# Setup
token = os.getenv("OANDA_TOKEN")
account_id = "101-001-0000000-001"

async def scale_into_position():
    async with AsyncClient(token=token, environment=Environment.PRACTICE) as client:
        orders = []

        # First entry - smaller size
        order1 = await client.orders.post_limit_order(
            account_id=account_id,
            instrument="EUR_USD",
            units=5000,  # Half position
            price=Decimal("1.0850"),
            time_in_force="GTC",
            stop_loss_on_fill={
                "price": "1.0800",
                "time_in_force": "GTC"
            }
        )
        orders.append(order1)

        # Second entry - lower price, larger size
        order2 = await client.orders.post_limit_order(
            account_id=account_id,
            instrument="EUR_USD",
            units=10000,  # Full position
            price=Decimal("1.0825"),  # Better entry
            time_in_force="GTC",
            stop_loss_on_fill={
                "price": "1.0800",
                "time_in_force": "GTC"
            }
        )
        orders.append(order2)

        print("Scaling orders placed")
        return orders
```

### Scaling Out of Positions

Take partial profits at multiple levels:

```python
import os
from decimal import Decimal
from fivetwenty import AsyncClient, Environment

# Setup
token = os.getenv("OANDA_TOKEN")
account_id = "101-001-0000000-001"

async def scale_out_of_position():
    async with AsyncClient(token=token, environment=Environment.PRACTICE) as client:
        # First take partial profit at initial target
        profit1 = await client.orders.post_limit_order(
            account_id=account_id,
            instrument="EUR_USD",
            units=-5000,  # Sell half position
            price=Decimal("1.0925"),  # First target
            time_in_force="GTC"
        )

        # Second take profit at extended target
        profit2 = await client.orders.post_limit_order(
            account_id=account_id,
            instrument="EUR_USD",
            units=-5000,  # Sell remaining
            price=Decimal("1.0975"),  # Extended target
            time_in_force="GTC"
        )

        print("Profit-taking orders placed")
        return [profit1, profit2]
```

## Advanced Stop Management

### Trailing Stops for Trend Following

```python
import os
from fivetwenty import AsyncClient, Environment

# Setup
token = os.getenv("OANDA_TOKEN")
account_id = "101-001-0000000-001"

async def trailing_stop_strategy():
    async with AsyncClient(token=token, environment=Environment.PRACTICE) as client:
        # Enter position with trailing stop
        entry = await client.orders.post_market_order(
            account_id=account_id,
            instrument="EUR_USD",
            units=10000,
            trailing_stop_loss_on_fill={
                "distance": "0.0030",  # 30 pip trailing distance
                "time_in_force": "GTC"
            }
        )

        print(f"Trailing stop order placed with {entry.order_fill_transaction.trailing_stop_loss_order_transaction.distance} distance")
        return entry
```

### Stop Loss Modification

Update stop levels as trades move in your favor:

```python
import os
from decimal import Decimal
from fivetwenty import AsyncClient, Environment

# Setup
token = os.getenv("OANDA_TOKEN")
account_id = "101-001-0000000-001"

async def update_stop_loss(trade_id: str, new_stop_price: Decimal):
    async with AsyncClient(token=token, environment=Environment.PRACTICE) as client:
        # Update the stop loss for an existing trade
        response = await client.trades.put_trade_orders(
            account_id=account_id,
            trade_id=trade_id,
            stop_loss={
                "price": str(new_stop_price),
                "time_in_force": "GTC"
            }
        )

        print(f"Stop loss updated to: {new_stop_price}")
        return response
```

## Order Coordination Patterns

### If-Then Order Logic

Simulate conditional orders with monitoring:

```python
import asyncio
import os
from decimal import Decimal
from fivetwenty import AsyncClient, Environment

# Setup
token = os.getenv("OANDA_TOKEN")
account_id = "101-001-0000000-001"

async def conditional_order_logic():
    async with AsyncClient(token=token, environment=Environment.PRACTICE) as client:
        # Monitor a condition and place order when met
        target_price = Decimal("1.0875")

        while True:
            # Get current price
            pricing = await client.pricing.get_pricing(
                account_id=account_id,
                instruments=["EUR_USD"]
            )

            current_price = Decimal(pricing.prices[0].mid.o)
            print(f"Current price: {current_price}")

            # Check condition
            if current_price >= target_price:
                # Place order when condition is met
                order = await client.orders.post_market_order(
                    account_id=account_id,
                    instrument="EUR_USD",
                    units=10000,
                    stop_loss_on_fill={
                        "price": "1.0825",
                        "time_in_force": "GTC"
                    }
                )

                print(f"Conditional order triggered at: {current_price}")
                return order

            # Wait before checking again
            await asyncio.sleep(10)
```

### Position Reversal Strategy

Close existing position and open opposite position:

```python
import os
from fivetwenty import AsyncClient, Environment

# Setup
token = os.getenv("OANDA_TOKEN")
account_id = "101-001-0000000-001"

async def position_reversal():
    async with AsyncClient(token=token, environment=Environment.PRACTICE) as client:
        # Get current positions
        positions = await client.positions.get_positions(account_id=account_id)

        for position in positions.positions:
            if position.instrument == "EUR_USD" and position.long.units != "0":
                # Close long position and open short
                close_size = int(position.long.units)
                new_position_size = close_size * 2  # Double to reverse

                order = await client.orders.post_market_order(
                    account_id=account_id,
                    instrument="EUR_USD",
                    units=-new_position_size,  # Negative to go short
                    stop_loss_on_fill={
                        "price": "1.0925",  # Stop above current price
                        "time_in_force": "GTC"
                    }
                )

                print(f"Position reversed: {close_size} long → {new_position_size//2} short")
                return order
```

## Complete Strategy Example

Here's a complete breakout strategy using multiple order types:

```python
import asyncio
from decimal import Decimal
from fivetwenty import AsyncClient, Environment

async def breakout_strategy():
    """Complete breakout strategy using FiveTwenty order combinations."""
    token = os.getenv("OANDA_TOKEN")
    account_id = "101-001-0000000-001"

    async with AsyncClient(token=token, environment=Environment.PRACTICE) as client:
        # Define breakout levels
        breakout_high = Decimal("1.0900")
        breakout_low = Decimal("1.0800")
        position_size = 10000

        # Place buy stop above resistance
        buy_stop = await client.orders.post_stop_order(
            account_id=account_id,
            instrument="EUR_USD",
            units=position_size,
            price=breakout_high,
            time_in_force="GTC",
            stop_loss_on_fill={
                "price": str(breakout_high - Decimal("0.0050")),  # 50 pip stop
                "time_in_force": "GTC"
            },
            take_profit_on_fill={
                "price": str(breakout_high + Decimal("0.0100")),  # 100 pip target
                "time_in_force": "GTC"
            }
        )

        # Place sell stop below support
        sell_stop = await client.orders.post_stop_order(
            account_id=account_id,
            instrument="EUR_USD",
            units=-position_size,
            price=breakout_low,
            time_in_force="GTC",
            stop_loss_on_fill={
                "price": str(breakout_low + Decimal("0.0050")),  # 50 pip stop
                "time_in_force": "GTC"
            },
            take_profit_on_fill={
                "price": str(breakout_low - Decimal("0.0100")),  # 100 pip target
                "time_in_force": "GTC"
            }
        )

        print(f"Breakout strategy set:")
        print(f"  Buy stop at: {breakout_high}")
        print(f"  Sell stop at: {breakout_low}")

        return {"buy_stop": buy_stop, "sell_stop": sell_stop}

# Run the strategy
if __name__ == "__main__":
    asyncio.run(breakout_strategy())
```

## Key Takeaways

1. **Use OANDA's built-in combinations** - `stop_loss_on_fill` and `take_profit_on_fill`
2. **Keep strategies simple** - Focus on proven order type combinations
3. **Monitor order fills** - Build logic around order state changes
4. **Plan your exits** - Always include protective stops

## Next Steps

- Review [Validation Best Practices](validation-best-practices.md) for robust order handling
- See [Automated Systems](automated-systems.md) for order monitoring
- Check [Best Practices](../../explanation/best-practices.md) for production deployment

FiveTwenty provides powerful order combinations through OANDA's proven order types - use these building blocks rather than complex custom strategies.