# Order Types Reference

Complete reference for OANDA order types available through the FiveTwenty SDK.

## OANDA Order Types

OANDA supports four primary order types, each designed for specific trading scenarios:

### Market Orders

**Definition**: Execute immediately at the best available market price.

**Characteristics**:

- Immediate execution (subject to liquidity)
- No price guarantee - executes at current market price
- Ideal for entering/exiting positions quickly
- Cannot be cancelled once submitted

**Use Cases**:
- Quick position entry when timing is critical
- Emergency position exits
- Market making operations
- High-frequency trading strategies

```python
import asyncio
from decimal import Decimal
from fivetwenty import AsyncClient


async def place_market_order() -> Any:
    async with AsyncClient() as client:
        # Buy 10,000 EUR/USD at market price
        response = await client.orders.post_market_order(
            account_id="your_account_id",
            instrument="EUR_USD",
            units=10000,
            time_in_force="FOK"  # Fill or Kill
        )

        print(f"Market order placed: {response.order_create_transaction.id}")
        return response
```

### Limit Orders

**Definition**: Execute only at a specified price or better.

**Characteristics**:

- Price guarantee - will not execute at worse price
- May not execute if price is not reached
- Can be modified or cancelled before execution
- Ideal for planning entry/exit points

**Use Cases**:
- Buying at support levels
- Selling at resistance levels
- Planned position entries with price discipline
- Scaling into/out of positions

```python
from decimal import Decimal
from fivetwenty import AsyncClient


async def place_limit_order() -> Any:
    async with AsyncClient() as client:
        # Buy EUR/USD only if price drops to 1.0850 or lower
        response = await client.orders.post_limit_order(
            account_id="your_account_id",
            instrument="EUR_USD",
            units=10000,
            price=Decimal("1.0850"),
            time_in_force="GTC"  # Good Till Cancelled
        )

        print(f"Limit order placed at {response.order_create_transaction.price}")
        return response
```

### Stop Orders

**Definition**: Become market orders when a specified trigger price is reached.

**Characteristics**:

- Converts to market order when triggered
- Used for breakout strategies or stop losses
- No price guarantee after trigger
- Triggers on bid/ask depending on direction

**Use Cases**:
- Stop-loss protection
- Breakout trading strategies
- Momentum-based entries
- Risk management automation

```python
from decimal import Decimal
from fivetwenty import AsyncClient


async def place_stop_order() -> Any:
    async with AsyncClient() as client:
        # Sell EUR/USD if price falls to 1.0800 (stop loss)
        response = await client.orders.post_stop_order(
            account_id="your_account_id",
            instrument="EUR_USD",
            units=-10000,  # Negative for sell
            price=Decimal("1.0800"),
            time_in_force="GTC"
        )

        print(f"Stop order placed with trigger at {response.order_create_transaction.price}")
        return response
```

### Market-If-Touched (MIT) Orders

**Definition**: Become market orders when price moves favorably to a specified level.

**Characteristics**:

- Triggers when price touches specified level
- Converts to market order for immediate execution
- Used for mean reversion strategies
- Opposite trigger logic to stop orders

**Use Cases**:
- Taking profits at target levels
- Mean reversion entries
- Counter-trend trading
- Automated profit-taking

```python
from decimal import Decimal
from fivetwenty import AsyncClient


async def place_mit_order() -> Any:
    async with AsyncClient() as client:
        # Take profit when EUR/USD rises to 1.0950
        response = await client.orders.post_market_if_touched_order(
            account_id="your_account_id",
            instrument="EUR_USD",
            units=-10000,  # Close long position
            price=Decimal("1.0950"),
            time_in_force="GTC"
        )

        print(f"MIT order placed with trigger at {response.order_create_transaction.price}")
        return response
```

## Order Classification

### Pending vs Immediate Orders

**Immediate Orders**:

- Market orders
- Execute right away at current market prices
- Cannot be modified or cancelled once submitted

**Pending Orders**:

- Limit, Stop, and MIT orders
- Wait for specific conditions before execution
- Can be modified, cancelled, or replaced while pending

### Entry vs Exit Orders

**Entry Orders**:

- Open new positions
- Increase existing position size
- Used for initial market participation

**Exit Orders**:

- Close existing positions
- Reduce position size
- Used for profit-taking or loss limitation

## Order Parameters

### Essential Parameters

All orders require these fundamental parameters:

```python
from decimal import Decimal

# Common order parameters

order_params = {
    "instrument": "EUR_USD",           # Trading pair
    "units": 10000,                   # Position size (+ buy, - sell)
    "type": "LIMIT",                  # Order type
    "price": Decimal("1.0850"),      # Execution price (if applicable)
    "time_in_force": "GTC",           # Time validity
}
```

### Time-In-Force Options

Control how long orders remain active:

- **GTC** (Good Till Cancelled): Remains active until filled or cancelled
- **GTD** (Good Till Date): Expires at specified date/time
- **FOK** (Fill or Kill): Must fill completely or cancel immediately
- **IOC** (Immediate or Cancel): Fill partial amount, cancel remainder

```python
from decimal import Decimal
from fivetwenty import AsyncClient
from datetime import datetime



async def order_with_time_controls() -> Any:
    from datetime import datetime, timedelta

    async with AsyncClient() as client:
        # Order expires in 24 hours
        expiry_time = datetime.utcnow() + timedelta(hours=24)

        response = await client.orders.post_limit_order(
            account_id="your_account_id",
            instrument="EUR_USD",
            units=10000,
            price=Decimal("1.0850"),
            time_in_force="GTD",
            gtd_time=expiry_time
        )

        return response
```

## Order State Management

### Order Lifecycle

Orders progress through predictable states:

1. **PENDING** - Waiting for trigger conditions
2. **FILLED** - Successfully executed
3. **CANCELLED** - Manually cancelled or expired
4. **REJECTED** - Failed validation or execution

### Monitoring Order Status

```python
from fivetwenty import AsyncClient


async def monitor_order_status(order_id: str) -> Any:
    async with AsyncClient() as client:
        # Check current order status
        order = await client.orders.get_order(
            account_id="your_account_id",
            order_id=order_id
        )

        print(f"Order {order_id} status: {order.state}")

        if order.state == "PENDING":
            print(f"Waiting for price: {order.price}")
        elif order.state == "FILLED":
            print(f"Filled at: {order.filling_transaction.price}")
        elif order.state == "CANCELLED":
            print(f"Cancelled reason: {order.cancelling_transaction.reason}")

        return order
```

### Modifying Pending Orders

```python
from decimal import Decimal
from fivetwenty import AsyncClient


async def modify_pending_order(order_id: str, new_price: Decimal) -> Any:
    async with AsyncClient() as client:
        # Update order price
        response = await client.orders.put_order(
            account_id="your_account_id",
            order_id=order_id,
            order={
                "price": str(new_price),
                "time_in_force": "GTC"
            }
        )

        print(f"Order modified to price: {new_price}")
        return response
```

## Practical Order Selection

### Market Conditions Guide

**Trending Markets**:

- Use stop orders for breakout entries
- Use trailing stops for trend following
- Limit orders for counter-trend positions

**Range-Bound Markets**:

- Use limit orders at support/resistance
- Use MIT orders for profit-taking
- Avoid stop orders (prone to whipsaws)

**Volatile Markets**:

- Use market orders for quick execution
- Wider stop levels to avoid noise
- Consider FOK orders to ensure fills

**Low Liquidity**:

- Prefer limit orders for price control
- Use smaller position sizes
- Monitor bid/ask spreads closely

## Error Handling

### Common Order Errors

```python
from decimal import Decimal
from fivetwenty import AsyncClient
from fivetwenty.exceptions import VeeTwentyError


async def robust_order_placement() -> Any:
    async with AsyncClient() as client:
        try:
            response = await client.orders.post_limit_order(
                account_id="your_account_id",
                instrument="EUR_USD",
                units=10000,
                price=Decimal("1.0850"),
                time_in_force="GTC"
            )
            return response

        except VeeTwentyError as e:
            if "INSUFFICIENT_MARGIN" in str(e):
                print("Reduce position size - insufficient margin")
            elif "INVALID_PRICE" in str(e):
                print("Price is outside allowed bounds")
            elif "MARKET_CLOSED" in str(e):
                print("Market is closed - try later")
            else:
                print(f"Order failed: {e}")
            raise
```

## Best Practices

### Order Validation

Always validate parameters before submission:

```python

from typing import Any
from decimal import Decimal




def validate_order_params(instrument: str, units: int, price: Decimal) -> Any:
    # Check minimum/maximum units
    if abs(units) < 1:
        raise ValueError("Units must be at least 1")

    # Validate price precision (5 decimal places for EUR/USD)
    if price.as_tuple().exponent < -5:
        raise ValueError("Price precision too high")

    # Check instrument format
    if "_" not in instrument:
        raise ValueError("Invalid instrument format")
```

### Position Size Management

```python
from decimal import Decimal




async def calculate_position_size(risk_amount: Decimal, stop_distance: Decimal) -> int:
    """Calculate position size based on risk management rules."""

    # Risk amount in account currency
    # Stop distance in price units

    units_per_pip = 10000  # Standard lot for major pairs
    pip_value = Decimal("1.0")  # USD per pip for EUR/USD

    # Calculate position size
    position_size = int(risk_amount / (stop_distance * pip_value))

    return min(position_size, 100000)  # Cap at maximum allowed
```

## Next Steps

Now that you understand the fundamental order types, you're ready to explore:

- **[Advanced Limit Orders](../tutorials/advanced-orders/advanced-limit-orders.md)** - Time controls and protective mechanisms
- **[Stop Orders & Market-If-Touched](../tutorials/advanced-orders/stop-orders-mit.md)** - Breakout and mean reversion strategies
- **[Dynamic Order Management](../tutorials/advanced-orders/dynamic-management.md)** - Trailing stops and adaptive sizing

## Key Takeaways

1. **Market orders** provide speed, **limit orders** provide price control
2. **Stop orders** trigger on unfavorable moves, **MIT orders** trigger on favorable moves
3. Choose **time-in-force** settings based on your strategy timeframe
4. Always validate order parameters before submission
5. Monitor order states and handle errors gracefully
6. Select order types based on market conditions and strategy goals

Understanding these fundamentals enables you to build sophisticated trading systems with proper order management and risk controls.
