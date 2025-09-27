# Order Strategies & Combinations

Learn to combine FiveTwenty's order types effectively for common trading scenarios.

## Learning Objectives

By the end of this tutorial, you will:

- Scale into and out of positions using multiple order layers
- Implement advanced stop management techniques
- Build conditional order logic and position reversal strategies
- Combine multiple order types for complete trading strategies


## Multiple Position Management

### Scaling Into Positions

Build positions with multiple entries:

```python
from decimal import Decimal
from dotenv import load_dotenv
from fivetwenty import AsyncClient
# Setup
# Load environment variables from .env file
load_dotenv()

async def scale_into_position():
    # Zero-config - automatically uses environment variables
    async with AsyncClient() as client:
        orders = []

        # First entry - smaller size
        order1 = await client.orders.post_limit_order(
            account_id=client.account_id,
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
            account_id=client.account_id,
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
from decimal import Decimal
from dotenv import load_dotenv
from fivetwenty import AsyncClient
# Setup
# Load environment variables from .env file
load_dotenv()

async def scale_out_of_position():
    # Zero-config - automatically uses environment variables
    async with AsyncClient() as client:
        # First take partial profit at initial target
        profit1 = await client.orders.post_limit_order(
            account_id=client.account_id,
            instrument="EUR_USD",
            units=-5000,  # Sell half position
            price=Decimal("1.0925"),  # First target
            time_in_force="GTC"
        )

        # Second take profit at extended target
        profit2 = await client.orders.post_limit_order(
            account_id=client.account_id,
            instrument="EUR_USD",
            units=-5000,  # Sell remaining
            price=Decimal("1.0975"),  # Extended target
            time_in_force="GTC"
        )

        print("Profit-taking orders placed")
        return [profit1, profit2]
```

## Advanced Stop Management


### Stop Loss Modification

Update stop levels as trades move in your favor:

```python
from decimal import Decimal
from dotenv import load_dotenv
from fivetwenty import AsyncClient
# Setup
# Load environment variables from .env file
load_dotenv()

async def update_stop_loss(trade_id: str, new_stop_price: Decimal):
    # Zero-config - automatically uses environment variables
    async with AsyncClient() as client:
        # Update the stop loss for an existing trade
        response = await client.trades.put_trade_orders(
            account_id=client.account_id,
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
from decimal import Decimal
from dotenv import load_dotenv
from fivetwenty import AsyncClient
# Setup
# Load environment variables from .env file
load_dotenv()

async def conditional_order_logic():
    # Zero-config - automatically uses environment variables
    async with AsyncClient() as client:
        # Monitor a condition and place order when met
        target_price = Decimal("1.0875")

        while True:
            # Get current price
            pricing = await client.pricing.get_pricing(
                account_id=client.account_id,
                instruments=["EUR_USD"]
            )

            current_price = Decimal(pricing.prices[0].mid.o)
            print(f"Current price: {current_price}")

            # Check condition
            if current_price >= target_price:
                # Place order when condition is met
                order = await client.orders.post_market_order(
                    account_id=client.account_id,
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
from dotenv import load_dotenv
from fivetwenty import AsyncClient
# Setup
# Load environment variables from .env file
load_dotenv()

async def position_reversal():
    # Zero-config - automatically uses environment variables
    async with AsyncClient() as client:
        # Get current positions
        positions = await client.positions.get_positions(account_id=account_id)

        for position in positions.positions:
            if position.instrument == "EUR_USD" and position.long.units != "0":
                # Close long position and open short
                close_size = int(position.long.units)
                new_position_size = close_size * 2  # Double to reverse

                order = await client.orders.post_market_order(
                    account_id=client.account_id,
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
from dotenv import load_dotenv
from fivetwenty import AsyncClient
# Setup
# Load environment variables from .env file
load_dotenv()

async def scaling_strategy_example():
    """Complete scaling strategy using order combinations covered in this guide."""
    # Zero-config - automatically uses environment variables
    async with AsyncClient() as client:
        # Demonstrate scaling into and out of positions
        base_size = 5000
        entry_prices = [Decimal("1.0850"), Decimal("1.0825"), Decimal("1.0800")]
        exit_prices = [Decimal("1.0925"), Decimal("1.0950"), Decimal("1.0975")]

        scaling_orders = []

        # Scale into position with multiple limit orders
        for i, price in enumerate(entry_prices):
            order = await client.orders.post_limit_order(
                account_id=client.account_id,
                instrument="EUR_USD",
                units=base_size * (i + 1),  # Increasing size
                price=price,
                time_in_force="GTC",
                stop_loss_on_fill={
                    "price": str(price - Decimal("0.0050")),  # 50 pip stop
                    "time_in_force": "GTC"
                }
            )
            scaling_orders.append(order)
            print(f"Entry order {i+1}: {base_size * (i + 1)} units at {price}")

        # Scale out of position with profit targets
        for i, price in enumerate(exit_prices):
            order = await client.orders.post_limit_order(
                account_id=client.account_id,
                instrument="EUR_USD",
                units=-base_size,  # Partial exit
                price=price,
                time_in_force="GTC"
            )
            scaling_orders.append(order)
            print(f"Exit order {i+1}: {base_size} units at {price}")

        return scaling_orders

# Run the strategy
if __name__ == "__main__":
    asyncio.run(scaling_strategy_example())
```

## Key Takeaways

1. **Use OANDA's built-in combinations** - `stop_loss_on_fill` and `take_profit_on_fill`
2. **Keep strategies simple** - Focus on proven order type combinations
3. **Monitor order fills** - Build logic around order state changes
4. **Plan your exits** - Always include protective stops

## Next Steps

- Review [Best Practices](../../guides/understanding/best-practices.md) for robust order handling
- Check [Best Practices](../../guides/understanding/best-practices.md) for production deployment

FiveTwenty provides powerful order combinations through OANDA's proven order types - use these building blocks rather than complex custom strategies.