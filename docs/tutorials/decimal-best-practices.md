# Financial Precision with Decimal Types

!!! success "🎓 Best Practices - Learning-oriented content"
    **Use this guide when:** You want to understand how to work with financial precision in FiveTwenty

    **Learning outcome:** Mastery of native Decimal types for exact financial calculations

    **Time commitment:** 15-20 minutes of focused reading and practice

This guide demonstrates how to leverage FiveTwenty's native Decimal support for exact financial calculations and precision-safe trading operations.

## Why Decimal Matters in Finance

### The Float Problem
```python
from decimal import Decimal

# ❌ Float arithmetic can be imprecise
float_sum = 0.1 + 0.2
print(float_sum)  # 0.30000000000000004 (not exactly 0.3!)

# This imprecision compounds in financial calculations
balance = Decimal("1000.00")
for i in range(100):
    balance += 0.01  # Adding 1 cent 100 times
print(balance)  # 1000.9999999999999 (should be 1001.00)
```

### The Decimal Solution
```python
from decimal import Decimal

# ✅ Decimal arithmetic is exact
decimal_sum = Decimal('0.1') + Decimal('0.2')
print(decimal_sum)  # 0.3 (exact!)

# Financial calculations maintain precision
balance = Decimal('1000.00')
for i in range(100):
    balance += Decimal('0.01')
print(balance)  # 1001.00 (exact!)
```

## FiveTwenty's Decimal Integration

### Automatic Decimal Fields
FiveTwenty automatically handles Decimal conversion for financial fields:

```python
from decimal import Decimal
from fivetwenty import AsyncClient
from fivetwenty.models import MarketOrderRequest, InstrumentName, TimeInForce

# ✅ All these inputs work seamlessly
order1 = MarketOrderRequest(
    instrument=InstrumentName.EUR_USD,
    units=1000,           # int → Decimal
    time_in_force=TimeInForce.GTC,
)

order2 = MarketOrderRequest(
    instrument=InstrumentName.EUR_USD,
    units="1500.25",      # str → Decimal
    time_in_force=TimeInForce.GTC,
)

order3 = MarketOrderRequest(
    instrument=InstrumentName.EUR_USD,
    units=Decimal("2000.123456"),  # Decimal (direct)
    time_in_force=TimeInForce.GTC,
)

# All units fields are now native Decimal objects
assert isinstance(order1.units, Decimal)
assert isinstance(order2.units, Decimal)
assert isinstance(order3.units, Decimal)
```

### Field Type Reference

#### Decimal Fields
These fields accept various inputs and store as Decimal:
- **Order quantities**: `units` in all order requests
- **Position calculations**: `units` in position data
- **Financial rates**: `margin_rate`, percentage fields
- **Liquidity values**: `liquidity` in price buckets
- **Transaction amounts**: `pl`, `commission`, `financing` in transactions

#### AccountUnits Fields (String)
Account-level monetary values remain strings:
- **Account balances**: `balance`, `margin_available`
- **Trade P&L**: `realized_pl`, `unrealized_pl` in trades
- **Margin amounts**: `margin_used` at account level

#### PriceValue Fields (String)
Price fields remain strings for OANDA precision:
- **Market prices**: `price`, `closeout_bid`, `closeout_ask`
- **Order prices**: All price thresholds and levels

## Best Practices for Trading

### 1. Position Sizing with Decimal Precision
```python
from fivetwenty.models import InstrumentName
from fivetwenty.models import MarketOrderRequest
from fivetwenty.models import TimeInForce
from decimal import Decimal

async def calculate_position_size(
    account_balance: str,
    risk_percentage: Decimal,
    stop_loss_pips: int,
    pip_value: Decimal
) -> Decimal:
    """Calculate position size with exact precision."""
    balance = Decimal(account_balance)
    risk_amount = balance * (risk_percentage / 100)
    risk_per_unit = stop_loss_pips * pip_value

    position_size = risk_amount / risk_per_unit
    return position_size.quantize(Decimal('1'))  # Round to whole units

# Usage example
async def position_sizing_example():
    account = await client.accounts.get(account_id)
    position_size = await calculate_position_size(
        account_balance=account.balance,
        risk_percentage=Decimal('2'),     # 2% risk
        stop_loss_pips=20,
        pip_value=Decimal('0.10')         # For EUR/USD standard lot
    )

    order = MarketOrderRequest(
        instrument=InstrumentName.EUR_USD,
        units=position_size,              # Exact Decimal units
        time_in_force=TimeInForce.GTC,
    )
    return order
```

### 2. Precise P&L Calculations
```python
from decimal import Decimal

async def calculate_trade_performance(trade_id: str, account_id: str) -> dict:
    """Calculate exact trade performance metrics."""
    trade = await client.trades.get(account_id=account_id, trade_id=trade_id)

    # Decimal fields are already Decimal
    initial_units = trade.initial_units
    current_units = trade.current_units

    # AccountUnits fields need conversion
    realized_pl = Decimal(trade.realized_pl)
    unrealized_pl = Decimal(trade.unrealized_pl)

    # Exact calculations
    total_pl = realized_pl + unrealized_pl
    units_closed = initial_units - current_units

    # Per-unit performance (avoid division by zero)
    pl_per_unit = total_pl / initial_units if initial_units != 0 else Decimal('0')

    return {
        'total_pl': total_pl,
        'pl_per_unit': pl_per_unit,
        'units_closed': units_closed,
        'close_percentage': (units_closed / initial_units * 100) if initial_units != 0 else Decimal('0')
    }
```

### 3. Commission and Fee Calculations
```python
from decimal import Decimal

def calculate_total_trading_costs(
    base_units: Decimal,
    spread_pips: int,
    pip_value: Decimal,
    commission_per_unit: Decimal = Decimal('0')
) -> Decimal:
    """Calculate total trading costs with precision."""

    # Spread cost (paid on entry and exit)
    spread_cost = base_units * spread_pips * pip_value * 2

    # Commission cost (if applicable)
    commission_cost = base_units * commission_per_unit * 2  # Entry + exit

    # Total cost
    total_cost = spread_cost + commission_cost

    return total_cost.quantize(Decimal('0.01'))  # Round to cents

# Usage
units = Decimal('10000')  # 1 standard lot
spread = 2  # 2 pip spread
pip_val = Decimal('1.00')  # EUR/USD pip value for standard lot
commission = Decimal('0.05')  # $0.05 per 1000 units

total_cost = calculate_total_trading_costs(units, spread, pip_val, commission)
print(f"Total trading cost: ${total_cost}")  # Exact cost calculation
```

### 4. Portfolio Position Weighting
```python
from decimal import Decimal

async def rebalance_portfolio(
    target_weights: dict[str, Decimal],
    total_capital: Decimal,
    account_id: str
) -> list[dict]:
    """Rebalance portfolio with exact precision."""

    # Get current positions
    positions = await client.positions.get_positions(account_id=account_id)
    current_values = {}

    for position in positions.positions:
        if position.instrument in target_weights:
            # Calculate current position value
            long_units = position.long.units if position.long.units != "0" else Decimal('0')
            short_units = position.short.units if position.short.units != "0" else Decimal('0')
            net_units = long_units + short_units

            # Get current price
            pricing = await client.pricing.get_pricing(
                account_id=account_id,
                instruments=[position.instrument]
            )
            current_price = Decimal(pricing.prices[0].asks[0].price)

            current_values[position.instrument] = net_units * current_price

    # Calculate required trades
    trades = []
    for instrument, target_weight in target_weights.items():
        target_value = total_capital * target_weight
        current_value = current_values.get(instrument, Decimal('0'))
        value_difference = target_value - current_value

        if abs(value_difference) > Decimal('10'):  # Minimum trade threshold
            # Get current price for unit calculation
            pricing = await client.pricing.get_pricing(
                account_id=account_id,
                instruments=[instrument]
            )
            current_price = Decimal(pricing.prices[0].asks[0].price)

            # Calculate exact units needed
            units_to_trade = (value_difference / current_price).quantize(Decimal('1'))

            trades.append({
                'instrument': instrument,
                'units': units_to_trade,
                'value_difference': value_difference
            })

    return trades
```

### 5. Stop Loss and Take Profit Precision
```python
from decimal import Decimal

def calculate_stop_levels(
    entry_price: str,  # PriceValue from trade
    direction: str,    # "long" or "short"
    stop_pips: int,
    target_pips: int,
    pip_location: int = 4  # Decimal places for price
) -> tuple[str, str]:
    """Calculate exact stop loss and take profit levels."""

    entry = Decimal(entry_price)
    pip_value = Decimal('10') ** (-pip_location)

    if direction.lower() == "long":
        stop_loss = entry - (stop_pips * pip_value)
        take_profit = entry + (target_pips * pip_value)
    else:  # short
        stop_loss = entry + (stop_pips * pip_value)
        take_profit = entry - (target_pips * pip_value)

    # Format back to string with proper precision
    price_format = f"{{:.{pip_location}f}}"
    return (
        price_format.format(stop_loss),
        price_format.format(take_profit)
    )

# Usage with a trade
async def demo_stop_loss_calculation():
    trade = await client.trades.get(account_id=account_id, trade_id=trade_id)
    direction = "long" if trade.initial_units > 0 else "short"

    stop_price, target_price = calculate_stop_levels(
        entry_price=trade.price,
        direction=direction,
        stop_pips=20,
        target_pips=40,
        pip_location=5  # EUR/USD uses 5 decimal places
    )

    # Create stop loss order
    # Create stop loss using post_order with StopLossOrderRequest
    from fivetwenty.models import StopLossOrderRequest

    sl_request = StopLossOrderRequest(
        tradeID=trade_id,
        price=str(stop_price),
        timeInForce="GTC"
    )
    stop_order = await client.orders.post_order(account_id, sl_request)
    return stop_order

# Run the example
import asyncio
asyncio.run(demo_stop_loss_calculation())
```

## Advanced Decimal Patterns

### 1. Precision Context Management
```python
from decimal import Decimal, getcontext

# Set global precision for calculations
getcontext().prec = 28  # High precision for financial calculations

def safe_divide(numerator: Decimal, denominator: Decimal) -> Decimal:
    """Division with zero check and precision control."""
    if denominator == 0:
        return Decimal('0')

    # Perform division with specific precision
    result = numerator / denominator
    return result.quantize(Decimal('0.00000001'))  # 8 decimal places
```

### 2. Currency Conversion Precision
```python
from decimal import Decimal

async def convert_currency_precise(
    amount: Decimal,
    from_currency: str,
    to_currency: str,
    account_id: str
) -> Decimal:
    """Convert currency with exchange rate precision."""

    if from_currency == to_currency:
        return amount

    # Get exchange rate
    pair = f"{from_currency}_{to_currency}"
    try:
        pricing = await client.pricing.get_pricing(
            account_id=account_id,
            instruments=[pair]
        )
        rate = Decimal(pricing.prices[0].asks[0].price)
    except:
        # Try reverse pair
        reverse_pair = f"{to_currency}_{from_currency}"
        pricing = await client.pricing.get_pricing(
            account_id=account_id,
            instruments=[reverse_pair]
        )
        rate = Decimal('1') / Decimal(pricing.prices[0].bids[0].price)

    converted = amount * rate
    return converted.quantize(Decimal('0.01'))  # Round to cents
```

### 3. Performance Metrics with Exact Math
```python
from decimal import Decimal

def calculate_sharpe_ratio(
    returns: list[Decimal],
    risk_free_rate: Decimal = Decimal('0.02')
) -> Decimal:
    """Calculate Sharpe ratio with Decimal precision."""

    if not returns:
        return Decimal('0')

    # Convert annual risk-free rate to period rate
    periods_per_year = Decimal('252')  # Trading days
    period_risk_free = risk_free_rate / periods_per_year

    # Calculate excess returns
    excess_returns = [r - period_risk_free for r in returns]

    # Mean excess return
    mean_excess = sum(excess_returns) / len(excess_returns)

    # Standard deviation of excess returns
    variance = sum((r - mean_excess) ** 2 for r in excess_returns) / len(excess_returns)
    std_dev = variance.sqrt()  # Decimal has sqrt method

    if std_dev == 0:
        return Decimal('0')

    # Annualized Sharpe ratio
    sharpe = (mean_excess / std_dev) * periods_per_year.sqrt()
    return sharpe.quantize(Decimal('0.0001'))
```

## Common Pitfalls and Solutions

### ❌ Don't: Mix float and Decimal
```python
from decimal import Decimal

# This can introduce precision errors
price = Decimal('1.1000')
adjustment = 0.0001  # float
result = price + adjustment  # Decimal + float = float!
```

### ✅ Do: Keep everything as Decimal
```python
from decimal import Decimal

price = Decimal('1.1000')
adjustment = Decimal('0.0001')
result = price + adjustment  # Both Decimal = exact result
```

### ❌ Don't: Ignore rounding in final results
```python
from decimal import Decimal

# Uncontrolled precision
result = Decimal('10') / Decimal('3')  # 3.333333333...
```

### ✅ Do: Use quantize() for display/storage
```python
from decimal import Decimal

result = Decimal('10') / Decimal('3')
display_result = result.quantize(Decimal('0.01'))  # 3.33
```

### ❌ Don't: Convert unnecessarily
```python
# Unnecessary conversion

order = MarketOrderRequest(units=1000, instrument="EUR_USD")
units_float = float(order.units)  # Why convert to less precise type?
```

### ✅ Do: Work with native Decimal
```python
from fivetwenty.models import MarketOrderRequest
from decimal import Decimal

order = MarketOrderRequest(units=1000, instrument="EUR_USD")
calculation = order.units * Decimal('1.5')  # Direct Decimal arithmetic
```

## Summary

FiveTwenty's native Decimal integration provides:

- **Exact financial calculations** - No floating-point errors
- **Automatic type conversion** - Accepts strings, ints, and Decimals
- **API compatibility** - Automatic string serialization for OANDA
- **Type safety** - Full mypy support for compile-time checking
- **Performance** - Efficient operations with financial precision

Use Decimal types for all financial calculations to ensure your trading algorithms maintain the precision required for professional financial applications.

## Additional Resources

- [Python Decimal Documentation](https://docs.python.org/3/library/decimal.html)
- [Risk Management Tutorial](risk-management/index.md)
- [Advanced Order Management](advanced-orders/index.md)