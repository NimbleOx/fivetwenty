# 📋 Manage Orders Effectively

## 🎯 Problem Statement

You need to create, monitor, and manage trading orders efficiently using FiveTwenty. This guide provides practical solutions for common order management scenarios including creating different order types, handling order lifecycle, and implementing robust order management strategies.

**When you need this guide:**

- Creating market, limit, or stop orders programmatically
- Implementing order validation and error handling
- Building order management workflows
- Tracking order execution and lifecycle
- Handling order modifications and cancellations

**Prerequisites:**

- FiveTwenty installed and configured
- Valid OANDA account (practice or live)
- Basic understanding of trading order types

## 🛠️ Solution Steps

!!! tip "Choose the Right Order Pattern"
    OANDA supports different order workflows. Choose the pattern that matches your trading style:

    **🎯 OnFill Pattern (Recommended)**: Set TP/SL when creating orders
    ```python
    from decimal import Decimal

    # Risk management activates automatically when order fills
    await client.orders.post_market_order(
        account_id=account_id,
        instrument="EUR_USD",
        units=1000,
        take_profit=Decimal("1.1100"),  # Automatic TP
        stop_loss=Decimal("1.0900")     # Automatic SL
    )
    ```

    **🛠️ Post-Trade Pattern**: Add TP/SL to existing trades
    ```python
    # First create trade, then add risk management
    from fivetwenty.models import TakeProfitOrderRequest

    market_response = await client.orders.post_market_order(...)
    trade_id = market_response.order_fill_transaction['tradeOpened']['tradeID']

    tp_request = TakeProfitOrderRequest(tradeID=trade_id, price="1.1100")
    await client.orders.post_order(account_id, tp_request)
    ```

    **When to Use Each:**
    - **OnFill**: Most trading scenarios, immediate risk management
    - **Post-Trade**: Adding risk management after market analysis, modifying existing levels

### Implement Post-Trade Risk Management

**Problem:** Add risk management orders to existing trades after they've been created and analyzed.

**Use Case:** You've opened a position and want to add or modify stop loss and take profit levels based on subsequent market analysis, or you need more sophisticated risk management than the OnFill pattern provides.

#### Step-by-Step Post-Trade Risk Management

```python
from decimal import Decimal
from fivetwenty import AsyncClient
from fivetwenty.models import (
    AccountID, TakeProfitOrderRequest, StopLossOrderRequest,
    TrailingStopLossOrderRequest, GuaranteedStopLossOrderRequest
)

async def implement_post_trade_risk_management():
    """Comprehensive post-trade risk management implementation."""

    async with AsyncClient() as client:
        account_id = AccountID("your-account-id")

        # Step 1: Create initial trade without risk management
        print("Creating initial position...")
        market_response = await client.orders.post_market_order(
            account_id=account_id,
            instrument="EUR_USD",
            units=10000  # Buy 10,000 EUR
        )

        # Extract trade ID from response
        if (market_response.order_fill_transaction and
            'tradeOpened' in market_response.order_fill_transaction):
            trade_id = market_response.order_fill_transaction['tradeOpened']['tradeID']
            print(f"Trade created: {trade_id}")

            # Step 2: Add take profit order
            print("Adding take profit...")
            tp_request = TakeProfitOrderRequest(
                tradeID=trade_id,
                price="1.1150",  # Target 150 pips profit
                timeInForce="GTC"
            )

            tp_response = await client.orders.post_order(account_id, tp_request)
            tp_order_id = tp_response.order_create_transaction['id']
            print(f"Take profit order: {tp_order_id}")

            # Step 3: Add stop loss order (price-based)
            print("Adding stop loss...")
            sl_request = StopLossOrderRequest(
                tradeID=trade_id,
                price="1.0950",  # Risk 50 pips
                timeInForce="GTC"
            )

            sl_response = await client.orders.post_order(account_id, sl_request)
            sl_order_id = sl_response.order_create_transaction['id']
            print(f"Stop loss order: {sl_order_id}")
```

#### Distance-Based Stop Loss

```python
# Alternative: Distance-based stop loss (dynamic pricing)
async def add_distance_based_stop_loss(client, account_id, trade_id):
    """Add stop loss based on distance rather than fixed price."""

    distance_sl_request = StopLossOrderRequest(
        tradeID=trade_id,
        distance="0.0050",  # 50 pips from entry price
        timeInForce="GTC"
    )

    response = await client.orders.post_order(account_id, distance_sl_request)
    return response.order_create_transaction['id']
```

#### Trailing Stop Loss

```python
async def add_trailing_stop_loss(client, account_id, trade_id):
    """Add trailing stop loss that follows favorable price movement."""

    tsl_request = TrailingStopLossOrderRequest(
        tradeID=trade_id,
        distance="0.0030",  # 30 pips trailing distance
        timeInForce="GTC"
    )

    response = await client.orders.post_order(account_id, tsl_request)
    print(f"Trailing stop will follow price with 30 pip buffer")
    return response.order_create_transaction['id']
```

#### Guaranteed Stop Loss

```python
async def add_guaranteed_stop_loss(client, account_id, trade_id):
    """Add guaranteed stop loss with premium cost."""

    try:
        gsl_request = GuaranteedStopLossOrderRequest(
            tradeID=trade_id,
            price="1.0900",  # Guaranteed execution price
            timeInForce="GTC"
        )

        response = await client.orders.post_order(account_id, gsl_request)

        # Check premium cost
        if 'guaranteedExecutionPremium' in response.order_create_transaction:
            premium = response.order_create_transaction['guaranteedExecutionPremium']
            print(f"Guaranteed stop loss premium: {premium}")

        return response.order_create_transaction['id']

    except Exception as e:
        print(f"GSL not available: {e}")
        # Fallback to regular stop loss
        return await add_regular_stop_loss(client, account_id, trade_id)
```

#### Error Handling for Post-Trade Orders

```python
from fivetwenty.exceptions import FiveTwentyError

async def robust_post_trade_setup(client, account_id, trade_id):
    """Add risk management with comprehensive error handling."""

    try:
        # Attempt to add take profit
        tp_request = TakeProfitOrderRequest(
            tradeID=trade_id,
            price="1.1200",
            timeInForce="GTC"
        )

        tp_response = await client.orders.post_order(account_id, tp_request)
        print(f"✅ Take profit added: {tp_response.order_create_transaction['id']}")

    except FiveTwentyError as e:
        error_msg = str(e)

        if "TRADE_DOESNT_EXIST" in error_msg:
            print("❌ Trade no longer exists - may have been closed")
        elif "INSUFFICIENT_MARGIN" in error_msg:
            print("❌ Insufficient margin for risk management orders")
        elif "PRICE_INVALID" in error_msg:
            print("❌ Invalid price level - adjust take profit price")
        else:
            print(f"❌ Unexpected error: {error_msg}")

    except Exception as e:
        print(f"❌ System error: {e}")
```

#### When to Use Post-Trade Pattern

**Best for:**

- **Complex Strategies**: Multi-leg strategies requiring careful timing
- **Market Analysis**: Adding risk management after technical/fundamental analysis
- **Dynamic Management**: Adjusting levels based on market conditions
- **Position Scaling**: Adding risk management to partially closed positions

**Not Recommended for:**

- **Simple Strategies**: OnFill pattern is more efficient
- **High-Frequency Trading**: Additional API calls add latency
- **Basic Risk Management**: OnFill covers most use cases

### Create Market Orders for Immediate Execution

**Problem:** Execute trades immediately at current market price.

```python
from decimal import Decimal
from fivetwenty import AsyncClient
from fivetwenty.models import AccountID, InstrumentName

async def place_market_order():
    async with AsyncClient() as client:
        # Simple market order
        response = await client.orders.post_market_order(
            account_id=AccountID("101-004-12345678"),
            instrument=InstrumentName("EUR_USD"),
            units=1000,  # Positive = buy, negative = sell
            client_request_id="market-order-001"
        )

        # With protective stops
        response = await client.orders.post_market_order(
            account_id=AccountID("101-004-12345678"),
            instrument=InstrumentName("EUR_USD"),
            units=1000,
            take_profit=Decimal("1.1050"),  # Exit at profit
            stop_loss=Decimal("1.0950"),   # Limit losses
        )

        print(f"Order ID: {response.order_create_transaction.id}")
        print(f"Fill Price: {response.order_fill_transaction.price}")
```

### Create Limit Orders for Precise Entry

**Problem:** Enter positions only when price reaches your target level.

```python
from decimal import Decimal
from fivetwenty import AsyncClient
from fivetwenty.models import AccountID, InstrumentName

async def place_limit_order():
    async with AsyncClient() as client:
        response = await client.orders.post_limit_order(
            account_id=AccountID("101-004-12345678"),
            instrument=InstrumentName("GBP_USD"),
            units=500,
            price=Decimal("1.2500"),  # Buy when price drops to 1.2500
            time_in_force="GTC",      # Good Till Cancelled
            take_profit=Decimal("1.2600"),
            stop_loss=Decimal("1.2400"),
        )

        print(f"Pending Order ID: {response.order_create_transaction.id}")
```

### Create Stop Orders for Breakout Trading

**Problem:** Enter positions when price breaks above/below key levels.

```python
from decimal import Decimal
from fivetwenty import AsyncClient
from fivetwenty.models import AccountID, InstrumentName

async def place_stop_order():
    async with AsyncClient() as client:
        # Buy stop order - enter long when price breaks above resistance
        response = await client.orders.post_stop_order(
            account_id=AccountID("101-004-12345678"),
            instrument=InstrumentName("EUR_USD"),
            units=1000,
            price=Decimal("1.1100"),        # Stop activation price
            price_bound=Decimal("1.1110"),  # Maximum slippage
            time_in_force="GFD",           # Good for day
            take_profit=Decimal("1.1150"), # Target 50 pips profit
            stop_loss=Decimal("1.1050"),   # Limit loss to 50 pips
            client_request_id="breakout-strategy-001"
        )

        print(f"Stop Order ID: {response.order_create_transaction.id}")
```

### Create Market-If-Touched Orders for Support/Resistance Trading

**Problem:** Enter positions when price touches support/resistance levels.

```python
from decimal import Decimal
from fivetwenty import AsyncClient
from fivetwenty.models import AccountID, InstrumentName

async def place_market_if_touched_order():
    async with AsyncClient() as client:
        # MIT order - buy when price touches support level
        response = await client.orders.post_market_if_touched_order(
            account_id=AccountID("101-004-12345678"),
            instrument=InstrumentName("GBP_USD"),
            units=750,
            price=Decimal("1.2400"),        # Support level trigger
            price_bound=Decimal("1.2390"),  # Allow 10 pip slippage
            time_in_force="GTC",           # Good till cancelled
            take_profit=Decimal("1.2500"), # Target 100 pips
            stop_loss=Decimal("1.2350"),   # Stop 50 pips below support
            client_request_id="support-bounce-001"
        )

        print(f"MIT Order ID: {response.order_create_transaction.id}")
```

### Use the Unified Order Interface for Flexibility

**Problem:** Need to create different order types programmatically based on strategy logic.

```python
from fivetwenty import AsyncClient, Environment

from fivetwenty.models import (
    MarketOrderRequest,
    LimitOrderRequest,
    StopOrderRequest,
    TimeInForce
)

async def create_order_by_type(order_type: str, price: Decimal = None):
    async with AsyncClient() as client:
        account_id = AccountID("101-004-12345678")
        instrument = InstrumentName("USD_JPY")
        units = 1000

        # Build order request based on type
        if order_type == "market":
            order_request = MarketOrderRequest(
                instrument=instrument,
                units=units
            )
        elif order_type == "limit":
            order_request = LimitOrderRequest(
                instrument=instrument,
                units=units,
                price=str(price),
                timeInForce=TimeInForce.GTC
            )
        elif order_type == "stop":
            order_request = StopOrderRequest(
                instrument=instrument,
                units=units,
                price=str(price),
                timeInForce=TimeInForce.GTC
            )

        # Use unified interface
        response = await client.orders.post_order(
            account_id=account_id,
            order_request=order_request,
            client_request_id=f"{order_type}-order-{int(time.time())}"
        )

        return response
```

### Monitor and Track Order Status

**Problem:** Track order execution and handle different outcomes.

```python
from fivetwenty import AsyncClient, Environment

async def monitor_order_execution(account_id: AccountID, order_id: str):
    async with AsyncClient() as client:
        # Get current order status
        order = await client.orders.get_order(account_id, order_id)

        print(f"Order State: {order['state']}")
        print(f"Filled Units: {order.get('filledUnits', 0)}")

        # Check if order is still pending
        if order['state'] == 'PENDING':
            print("Order is waiting for execution")

            # Get all pending orders for context
            pending = await client.orders.get_pending_orders(account_id)
            print(f"Total pending orders: {len(pending['orders'])}")

        elif order['state'] == 'FILLED':
            print(f"Order executed at price: {order['fillingTransactionIDs']}")

        elif order['state'] == 'CANCELLED':
            print("Order was cancelled")
```

### Implement Order Validation and Error Handling

**Problem:** Robust order validation to prevent common errors.

```python
from decimal import Decimal
from fivetwenty import AsyncClient
from fivetwenty.models import AccountID, InstrumentName
from fivetwenty.exceptions import FiveTwentyError

async def place_validated_order(
    account_id: AccountID,
    instrument: InstrumentName,
    units: int,
    order_type: str = "market",
    price: Decimal = None
):
    async with AsyncClient() as client:
        try:
            # Validate account has sufficient balance
            account = await client.accounts.get_account(account_id)
            available_balance = Decimal(account.nav)

            # Validate instrument is tradeable
            instruments = await client.accounts.get_instruments(
                account_id,
                instruments=[instrument]
            )

            if not instruments:
                raise ValueError(f"Instrument {instrument} not available")

            instrument_info = instruments[0]
            if not instrument_info.tradeable:
                raise ValueError(f"Instrument {instrument} not currently tradeable")

            # Validate order size
            min_units = abs(int(instrument_info.minimum_trade_size))
            max_units = abs(int(instrument_info.maximum_order_units))

            if abs(units) < min_units:
                raise ValueError(f"Order size {units} below minimum {min_units}")
            if abs(units) > max_units:
                raise ValueError(f"Order size {units} exceeds maximum {max_units}")

            # Place order based on type
            if order_type == "market":
                response = await client.orders.post_market_order(
                    account_id=account_id,
                    instrument=instrument,
                    units=units,
                    client_request_id=f"validated-{order_type}-{int(time.time())}"
                )
            elif order_type == "limit" and price:
                response = await client.orders.post_limit_order(
                    account_id=account_id,
                    instrument=instrument,
                    units=units,
                    price=price,
                    client_request_id=f"validated-{order_type}-{int(time.time())}"
                )
            else:
                raise ValueError("Invalid order type or missing price for limit order")

            return response

        except FiveTwentyError as e:
            print(f"OANDA API Error: {e.error_message}")
            print(f"Error Code: {e.error_code}")
            raise
        except ValueError as e:
            print(f"Validation Error: {e}")
            raise
```

### Cancel and Modify Orders

**Problem:** Manage pending orders by cancelling or replacing them.

```python
from fivetwenty import AsyncClient, Environment
from fivetwenty.exceptions import FiveTwentyError, FiveTwentyErrorCode

async def manage_pending_orders(account_id: AccountID):
    async with AsyncClient() as client:
        # Get all pending orders
        pending_response = await client.orders.get_pending_orders(account_id)
        pending_orders = pending_response['orders']

        for order in pending_orders:
            order_id = order['id']

            # Cancel old orders (example: cancel orders older than 1 hour)
            order_time = datetime.fromisoformat(order['createTime'].replace('Z', '+00:00'))
            if datetime.now(timezone.utc) - order_time > timedelta(hours=1):

                try:
                    cancel_response = await client.orders.cancel_order(
                        account_id,
                        order_id
                    )
                    print(f"Cancelled order {order_id}")

                except FiveTwentyError as e:
                    if e.error_code == "ORDER_DOESNT_EXIST":
                        print(f"Order {order_id} already cancelled or filled")
                    else:
                        raise
```

### Implement Batch Order Operations

**Problem:** Create multiple related orders efficiently.

```python
from fivetwenty import AsyncClient, Environment

import asyncio

async def create_bracket_order(
    account_id: AccountID,
    instrument: InstrumentName,
    entry_price: Decimal,
    take_profit: Decimal,
    stop_loss: Decimal,
    units: int
):
    """Create a bracket order: entry + take profit + stop loss"""
    async with AsyncClient() as client:

        # Create entry order
        entry_order = await client.orders.post_limit_order(
            account_id=account_id,
            instrument=instrument,
            units=units,
            price=entry_price,
            client_request_id=f"bracket-entry-{int(time.time())}"
        )

        entry_order_id = entry_order.order_create_transaction.id
        print(f"Entry order created: {entry_order_id}")

        # Wait for entry order to fill, then create protective orders
        # In practice, you'd use webhooks or streaming for real-time updates
        await asyncio.sleep(1)  # Brief pause for demo

        # Check if entry filled
        order_status = await client.orders.get_order(account_id, entry_order_id)

        if order_status['state'] == 'FILLED':
            # Create protective orders
            tasks = []

            # Take profit order (opposite direction)
            tp_task = client.orders.post_limit_order(
                account_id=account_id,
                instrument=instrument,
                units=-units,  # Opposite direction to close position
                price=take_profit,
                client_request_id=f"bracket-tp-{int(time.time())}"
            )
            tasks.append(tp_task)

            # Stop loss order (opposite direction)
            sl_task = client.orders.post_limit_order(
                account_id=account_id,
                instrument=instrument,
                units=-units,  # Opposite direction to close position
                price=stop_loss,
                client_request_id=f"bracket-sl-{int(time.time())}"
            )
            tasks.append(sl_task)

            # Execute protective orders concurrently
            results = await asyncio.gather(*tasks, return_exceptions=True)

            for i, result in enumerate(results):
                order_type = "Take Profit" if i == 0 else "Stop Loss"
                if isinstance(result, Exception):
                    print(f"{order_type} order failed: {result}")
                else:
                    print(f"{order_type} order created: {result.order_create_transaction.id}")

        return entry_order
```

## ✅ Verification

### Confirm Order Creation
```python
# Check order was created successfully
assert response.order_create_transaction is not None
assert response.order_create_transaction.id is not None

# For market orders, verify immediate fill
if order_type == "market":
    assert response.order_fill_transaction is not None
    print(f"Filled at price: {response.order_fill_transaction.price}")
```

### Verify Order Parameters
```python
# Confirm order details match your request
order_details = await client.orders.get_order(account_id, order_id)
assert order_details['instrument'] == str(instrument)
assert int(order_details['units']) == units
```

### Monitor Account Impact
```python
from decimal import Decimal

# Check account balance and positions after order
account = await client.accounts.get_account(account_id)
print(f"Account NAV: {account.nav}")
print(f"Unrealized P&L: {account.unrealized_pl}")
```

## 🔍 Troubleshooting

### Common Order Errors

**"INSUFFICIENT_MARGIN" Error:**
```python
from decimal import Decimal

# Check available margin before placing order
account = await client.accounts.get_account(account_id)
if Decimal(account.margin_available) < required_margin:
    print("Insufficient margin for order")
```

**"INSTRUMENT_NOT_TRADEABLE" Error:**
```python
# Verify instrument is currently tradeable
instruments = await client.accounts.get_instruments(account_id)
tradeable_instruments = [i for i in instruments if i.tradeable]
```

**"PRICE_PRECISION_EXCEEDED" Error:**
```python
# Use proper price precision for instrument
from fivetwenty._internal.utils import quantize_price

# Get instrument precision
instrument_info = await client.accounts.get_instruments(
    account_id,
    instruments=[instrument]
)
precision = instrument_info[0].display_precision

# Quantize price correctly
quantized_price = quantize_price(precision, your_price)
```

### Order Timing Issues

**Orders Not Filling:**

- Check market hours for the instrument
- Verify price is reasonable (not too far from current market)
- Consider using Market orders for immediate execution

**Order Rejection:**

- Validate all required parameters are provided
- Check account permissions and trading restrictions
- Ensure instrument symbols are correct (use InstrumentName enum)

### Performance Optimization

**Rate Limiting:**
```python
import asyncio
from asyncio import Semaphore

# Limit concurrent requests
semaphore = Semaphore(5)  # Max 5 concurrent orders

async def rate_limited_order(order_params):
    async with semaphore:
        return await client.orders.post_order(**order_params)
```

**Error Recovery:**
```python
from fivetwenty.exceptions import FiveTwentyError, FiveTwentyErrorCode

async def robust_order_placement(order_params, max_retries=3):
    for attempt in range(max_retries):
        try:
            return await client.orders.post_order(**order_params)
        except FiveTwentyError as e:
            if e.error_code in ["RATE_LIMIT_EXCEEDED", "SERVICE_UNAVAILABLE"]:
                wait_time = 2 ** attempt  # Exponential backoff
                await asyncio.sleep(wait_time)
                continue
            else:
                raise  # Don't retry for non-transient errors

    raise Exception(f"Order failed after {max_retries} attempts")
```

## 🎯 Advanced Patterns

### Order State Machine
```python
import asyncio
from datetime import datetime
from decimal import Decimal
from enum import Enum
from fivetwenty import AsyncClient
from fivetwenty.models import AccountID

class OrderState(Enum):
    CREATED = "created"
    PENDING = "pending"
    FILLED = "filled"
    CANCELLED = "cancelled"
    REJECTED = "rejected"

class OrderManager:
    def __init__(self, client: AsyncClient):
        self.client = client
        self.orders = {}

    async def track_order(self, account_id: AccountID, order_id: str):
        """Track order through its lifecycle"""
        while True:
            order = await self.client.orders.get_order(account_id, order_id)
            state = OrderState(order['state'].lower())

            self.orders[order_id] = {
                'state': state,
                'last_updated': datetime.now(),
                'details': order
            }

            if state in [OrderState.FILLED, OrderState.CANCELLED, OrderState.REJECTED]:
                break

            await asyncio.sleep(1)  # Poll every second
```

### Risk Management Integration
```python
from decimal import Decimal
from fivetwenty import AsyncClient
from fivetwenty.models import AccountID

class RiskManagedOrderSystem:
    def __init__(self, client: AsyncClient, max_daily_loss: Decimal):
        self.client = client
        self.max_daily_loss = max_daily_loss
        self.daily_loss = Decimal('0')

    async def place_order_with_risk_check(self, account_id: AccountID, **order_params):
        # Check daily loss limit
        if self.daily_loss >= self.max_daily_loss:
            raise ValueError("Daily loss limit exceeded")

        # Calculate potential loss for this order
        potential_loss = self._calculate_potential_loss(order_params)

        if self.daily_loss + potential_loss > self.max_daily_loss:
            raise ValueError("Order would exceed daily loss limit")

        # Place order if risk checks pass
        return await self.client.orders.post_order(
            account_id=account_id,
            **order_params
        )
```

---

**Need more specific help?** Check these related guides:
- [Implement Stop-Loss Strategies](implement-stop-loss-strategies.md) for protective order patterns
- [Close Positions](close-positions.md) for position exit strategies
- [Handle Connection Failures](handle-connection-failures.md) for robust error handling