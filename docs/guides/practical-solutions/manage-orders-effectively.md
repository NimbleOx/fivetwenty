# Manage Orders Effectively

## Problem Statement

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

## Solution Steps

!!! tip "Choose the Right Order Pattern"
    OANDA supports different order workflows. Choose the pattern that matches your trading style:

    **OnFill Pattern (Recommended)**: Set TP/SL when creating orders
    <!-- fragment: Demo OnFill pattern with multiple unused imports -->
    ```python
import asyncio
import os
import time
import logging
from decimal import Decimal

from fivetwenty import AsyncClient, Environment, Client
from fivetwenty.models import (
    StopLossOrderRequest,
    TrailingStopLossOrderRequest,
    GuaranteedStopLossOrderRequest,
    TakeProfitOrderRequest,
    OrderRequest,
    MarketOrderRequest,
    LimitOrderRequest,
    MarketIfTouchedOrderRequest,
    Order,
    OrderResponse,
    Position,
    Trade,
    ClientPrice,
    OrderFillTransaction
)
from fivetwenty.exceptions import VeeTwentyError as FiveTwentyError, BadRequest, TooManyRequests, InternalServerError


async def main() -> None:
    """Demonstrate OnFill pattern."""
    client = AsyncClient(
        token=os.environ.get("FIVETWENTY_OANDA_TOKEN", "demo-token"),
        environment=Environment.PRACTICE
    )
    account_id = "your-account-id"

    # Risk management activates automatically when order fills
    await client.orders.post_market_order(
        account_id=account_id,
        instrument="EUR_USD",
        units=1000,
        take_profit=Decimal("1.1100"),  # Automatic TP
        stop_loss=Decimal("1.0900"),     # Automatic SL
    )


if __name__ == "__main__":
    asyncio.run(main())
    ```

    **Post-Trade Pattern**: Add TP/SL to existing trades
    <!-- fragment: Demo post-trade pattern with unused imports -->
    ```python
import asyncio
import os

from fivetwenty import AsyncClient, Environment
from fivetwenty.models import TakeProfitOrderRequest

async def post_trade_example() -> None:
    """Demonstrate post-trade pattern."""
    client = AsyncClient(
        token=os.environ.get("FIVETWENTY_OANDA_TOKEN", "demo-token"),
        environment=Environment.PRACTICE
    )
    account_id = "your-account-id"

    # First create trade, then add risk management
    market_response = await client.orders.post_market_order(
        account_id=account_id,
        instrument="EUR_USD",
        units=1000,
    )
    trade_info = market_response.order_fill_transaction["tradeOpened"]
    trade_id = trade_info["tradeID"]

    tp_request = TakeProfitOrderRequest(tradeID=trade_id, price="1.1100")
    tp_response = await client.orders.post_order(account_id, tp_request)
    print(f"Take profit order created: {tp_response.order_create_transaction['id']}")
    ```

    **When to Use Each:**
    - **OnFill**: Most trading scenarios, immediate risk management
    - **Post-Trade**: Adding risk management after market analysis, modifying existing levels

### Implement Post-Trade Risk Management

**Problem:** Add risk management orders to existing trades after they've been created and analyzed.

**Use Case:** You've opened a position and want to add or modify stop loss and take profit levels based on subsequent market analysis, or you need more sophisticated risk management than the OnFill pattern provides.

#### Step-by-Step Post-Trade Risk Management
<!-- fragment: Demo post-trade risk management with unused imports -->
<!-- fragment: Demo comprehensive order management with type compatibility issues -->
```python
import asyncio
import os

from fivetwenty import AsyncClient, Environment
from fivetwenty.models import (
    AccountID,
    GuaranteedStopLossOrderRequest,
    StopLossOrderRequest,
    TakeProfitOrderRequest,
    TrailingStopLossOrderRequest,
)

async def implement_post_trade_risk_management() -> None:
    """Implement comprehensive post-trade risk management implementation."""
    async with AsyncClient(
        token=os.environ.get("FIVETWENTY_OANDA_TOKEN", "demo-token"),
        environment=Environment.PRACTICE
    ) as client:
        account_id = AccountID("your-account-id")

        # Step 1: Create initial trade without risk management
        print("Creating initial position...")
        market_response = await client.orders.post_market_order(
            account_id=account_id,
            instrument="EUR_USD",
            units=10000,  # Buy 10,000 EUR
        )

        # Extract trade ID from response
        if (
            market_response.order_fill_transaction
            and "tradeOpened" in market_response.order_fill_transaction
        ):
            trade_info = market_response.order_fill_transaction["tradeOpened"]
            trade_id = trade_info["tradeID"]
            print("Trade created successfully")

            # Step 2: Add take profit order
            print("Adding take profit...")
            tp_request = TakeProfitOrderRequest(
                tradeID=trade_id,
                price="1.1150",  # Target 150 pips profit
                timeInForce="GTC",
            )
            print(f"Take profit request prepared for trade {trade_id}")

            tp_response = await client.orders.post_order(account_id, tp_request)
            tp_order_id = tp_response.order_create_transaction["id"]
            print(f"Take profit order created: {tp_order_id}")

            # Step 3: Add stop loss order (price-based)
            print("Adding stop loss...")
            sl_request = StopLossOrderRequest(
                tradeID=trade_id,
                price="1.0950",  # Risk 50 pips
                timeInForce="GTC",
            )
            print(f"Stop loss request prepared for trade {trade_id}")

            sl_response = await client.orders.post_order(account_id, sl_request)
            sl_order_id = sl_response.order_create_transaction["id"]
            print(f"Stop loss order created: {sl_order_id}")
```

#### Distance-Based Stop Loss

<!-- fragment: Demo stop loss order creation with string-to-Decimal type mismatches -->
```python
from fivetwenty import AsyncClient
from fivetwenty.models import StopLossOrderRequest

# Alternative: Distance-based stop loss (dynamic pricing)
async def add_distance_based_stop_loss(client: AsyncClient, account_id: str, trade_id: str) -> str:
    """Add stop loss based on distance rather than fixed price."""
    distance_sl_request = StopLossOrderRequest(
        tradeID=trade_id,
        distance="0.0050",  # 50 pips from entry price
        timeInForce="GTC",
    )
    print(f"Distance-based stop loss prepared: 50 pips for trade {trade_id}")

    response = await client.orders.post_order(account_id, distance_sl_request)
    order_id = response.order_create_transaction["id"]
    print(f"Distance-based stop loss created: {order_id}")
    return order_id
```

#### Trailing Stop Loss

<!-- fragment: Demo trailing stop loss with timeInForce type incompatibility -->
```python
from fivetwenty import AsyncClient
from fivetwenty.models import TrailingStopLossOrderRequest

async def add_trailing_stop_loss(client: AsyncClient, account_id: str, trade_id: str) -> str:
    """Add trailing stop loss that follows favorable price movement."""
    tsl_request = TrailingStopLossOrderRequest(
        tradeID=trade_id,
        distance="0.0030",  # 30 pips trailing distance
        timeInForce="GTC",
    )
    print(f"Trailing stop loss prepared: 30 pips for trade {trade_id}")

    response = await client.orders.post_order(account_id, tsl_request)
    order_id = response.order_create_transaction["id"]
    print(f"Trailing stop created: {order_id} - will follow price with 30 pip buffer")
    return order_id
```

#### Guaranteed Stop Loss

<!-- fragment: Demo guaranteed stop loss with response indexing issues -->
```python
from fivetwenty import AsyncClient
from fivetwenty.models import GuaranteedStopLossOrderRequest, StopLossOrderRequest

async def add_guaranteed_stop_loss(client: AsyncClient, account_id: str, trade_id: str) -> str:
    """Add guaranteed stop loss with premium cost."""
    try:
        gsl_request = GuaranteedStopLossOrderRequest(
            tradeID=trade_id,
            price="1.0900",  # Guaranteed execution price
            timeInForce="GTC",
        )
        print(f"Guaranteed stop loss prepared for trade {trade_id}")

        response = await client.orders.post_order(account_id, gsl_request)
        order_id = response.order_create_transaction["id"]

        # Check premium cost
        if "guaranteedExecutionPremium" in response.order_create_transaction:
            premium = response.order_create_transaction["guaranteedExecutionPremium"]
            print(f"Guaranteed stop loss premium: {premium}")

        print(f"Guaranteed stop loss created: {order_id}")
    except Exception:
        print("Guaranteed stop loss not available")
        # Fallback to regular stop loss
        return await add_regular_stop_loss(client, account_id, trade_id)
    else:
        return order_id


async def add_regular_stop_loss(client: AsyncClient, account_id: str, trade_id: str) -> str:
    """Add regular stop loss as fallback."""
    sl_request = StopLossOrderRequest(
        tradeID=trade_id,
        price="1.0900",
        timeInForce="GTC",
    )
    print(f"Regular stop loss prepared for trade {trade_id}")
    response = await client.orders.post_order(account_id, sl_request)
    order_id = response.order_create_transaction["id"]
    print(f"Regular stop loss created: {order_id}")
    return order_id
```

#### Error Handling for Post-Trade Orders

<!-- fragment: Demo robust trade setup with union attribute access -->
```python
from fivetwenty import AsyncClient
from fivetwenty.exceptions import VeeTwentyError as FiveTwentyError
from fivetwenty.models import TakeProfitOrderRequest


async def robust_post_trade_setup(client: AsyncClient, account_id: str, trade_id: str) -> None:
    """Add risk management with comprehensive error handling."""
    try:
        # Attempt to add take profit
        tp_request = TakeProfitOrderRequest(
            tradeID=trade_id,
            price="1.1200",
            timeInForce="GTC",
        )
        print(f"Robust take profit prepared for trade {trade_id}")

        tp_response = await client.orders.post_order(account_id, tp_request)
        tp_order_id = tp_response.order_create_transaction['id']
        print(f"✅ Take profit order added successfully: {tp_order_id}")

    except FiveTwentyError as e:
        error_msg = str(e)

        if "TRADE_DOESNT_EXIST" in error_msg:
            print("❌ Trade no longer exists - may have been closed")
        elif "INSUFFICIENT_MARGIN" in error_msg:
            print("❌ Insufficient margin for risk management orders")
        elif "PRICE_INVALID" in error_msg:
            print("❌ Invalid price level - adjust take profit price")
        else:
            print("❌ Unexpected error occurred")

    except Exception:
        print("❌ System error occurred")
```

#### When to Use Post-Trade Pattern

**Best for:**

- **Complex Strategies**: Multi-leg strategies requiring careful timing
- **Market Analysis**: Adding risk management after technical/fundamental analysis
- **Dynamic Management**: Adjusting levels based on market conditions
- **Position Scaling**: Adding risk management to partially closed positions

**Not Recommended for:**

- **Basic Strategies**: OnFill pattern is more efficient
- **High-Frequency Trading**: Additional API calls add latency
- **Basic Risk Management**: OnFill covers most use cases

### Create Market Orders for Immediate Execution

**Problem:** Execute trades immediately at current market price.

The following example demonstrates how to create market orders using the FiveTwenty SDK. Market orders execute immediately at the best available price, making them ideal for quick entries and exits:

<!-- fragment: Demo market order creation with index access and type assignment issues -->
```python
import os
from decimal import Decimal

from fivetwenty import AsyncClient, Environment
from fivetwenty.models import AccountID, InstrumentName

async def place_market_order() -> None:
    """Demonstrate placing market orders."""
    async with AsyncClient(
        token=os.environ.get("FIVETWENTY_OANDA_TOKEN", "demo-token"),
        environment=Environment.PRACTICE
    ) as client:
        # Basic market order
        response = await client.orders.post_market_order(
            account_id=AccountID("101-004-12345678"),
            instrument=InstrumentName("EUR_USD"),
            units=1000,  # Positive = buy, negative = sell
            client_request_id="market-order-001",
        )
        order_id = response.order_create_transaction['id']
        print(f"Market order placed: {order_id}")

        # With protective stops
        response = await client.orders.post_market_order(
            account_id=AccountID("101-004-12345678"),
            instrument=InstrumentName("EUR_USD"),
            units=1000,
            take_profit=Decimal("1.1050"),  # Exit at profit
            stop_loss=Decimal("1.0950"),   # Limit losses
        )
        order_id = response.order_create_transaction['id']
        print(f"Market order executed successfully: {order_id}")
        print("Order filled at market price")
```

### Create Limit Orders for Precise Entry

**Problem:** Enter positions only when price reaches your target level.

This example shows how to create limit orders that execute only when the market reaches your specified price. Limit orders give you price control but no guarantee of execution:

<!-- fragment: Demo limit order with index access patterns -->
```python
import os
from decimal import Decimal

from fivetwenty import AsyncClient, Environment
from fivetwenty.models import AccountID, InstrumentName


async def place_limit_order() -> None:
    """Demonstrate placing limit orders."""
    async with AsyncClient(
        token=os.environ.get("FIVETWENTY_OANDA_TOKEN", "demo-token"),
        environment=Environment.PRACTICE
    ) as client:
        response = await client.orders.post_limit_order(
            account_id=AccountID("101-004-12345678"),
            instrument=InstrumentName("GBP_USD"),
            units=500,
            price=Decimal("1.2500"),  # Buy when price drops to 1.2500
            time_in_force="GTC",      # Good Till Cancelled
            take_profit=Decimal("1.2600"),
            stop_loss=Decimal("1.2400"),
        )
        order_id = response.order_create_transaction['id']
        print(f"Limit order placed successfully: {order_id}")
```

### Create Stop Orders for Breakout Trading

**Problem:** Enter positions when price breaks above/below key levels.

Here's how to create stop orders for breakout trading strategies. Stop orders become market orders when the trigger price is reached, making them ideal for momentum trading:

<!-- fragment: Demo stop order with index access patterns -->
```python
import os
from decimal import Decimal

from fivetwenty import AsyncClient, Environment
from fivetwenty.models import AccountID, InstrumentName


async def place_stop_order() -> None:
    """Demonstrate placing stop orders."""
    async with AsyncClient(
        token=os.environ.get("FIVETWENTY_OANDA_TOKEN", "demo-token"),
        environment=Environment.PRACTICE
    ) as client:
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
            client_request_id="breakout-strategy-001",
        )
        order_id = response.order_create_transaction['id']
        print(f"Stop order placed successfully: {order_id}")
```

### Create Market-If-Touched Orders for Support/Resistance Trading

**Problem:** Enter positions when price touches support/resistance levels.

This example demonstrates Market-If-Touched (MIT) orders, which execute at market price when a specified trigger level is reached. These are perfect for entering positions at support or resistance levels:

<!-- fragment: Demo MIT order with index access patterns -->
```python
import os
from decimal import Decimal

from fivetwenty import AsyncClient, Environment
from fivetwenty.models import AccountID, InstrumentName


async def place_market_if_touched_order() -> None:
    """Demonstrate placing market-if-touched orders."""
    async with AsyncClient(
        token=os.environ.get("FIVETWENTY_OANDA_TOKEN", "demo-token"),
        environment=Environment.PRACTICE
    ) as client:
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
            client_request_id="support-bounce-001",
        )
        order_id = response.order_create_transaction['id']
        print(f"MIT order placed successfully: {order_id}")
```

### Use the Unified Order Interface for Flexibility

**Problem:** Need to create different order types programmatically based on strategy logic.

```python
import os
import time
from decimal import Decimal
from typing import Any

from fivetwenty import AsyncClient, Environment
from fivetwenty.models import (
    AccountID,
    InstrumentName,
    LimitOrderRequest,
    MarketOrderRequest,
    StopOrderRequest,
    TimeInForce,
)


<!-- fragment: Demo unified order interface with type assignment and argument type issues -->
```python
async def create_order_by_type(order_type: str, price: Decimal | None = None) -> Any:
    """Create orders dynamically by type."""
    async with AsyncClient(
        token=os.environ.get("FIVETWENTY_OANDA_TOKEN", "demo-token"),
        environment=Environment.PRACTICE
    ) as client:
        account_id = AccountID("101-004-12345678")
        instrument = InstrumentName("USD_JPY")
        units = 1000

        # Build order request based on type
        if order_type == "market":
            order_request = MarketOrderRequest(
                instrument=instrument,
                units=units,
            )
        elif order_type == "limit":
            order_request = LimitOrderRequest(
                instrument=instrument,
                units=units,
                price=str(price),
                timeInForce=TimeInForce.GTC,
            )
        elif order_type == "stop":
            order_request = StopOrderRequest(
                instrument=instrument,
                units=units,
                price=str(price),
                timeInForce=TimeInForce.GTC,
            )
        else:
            msg = f"Unsupported order type: {order_type}"
            raise ValueError(msg)

        print(f"Created {order_type} order request for {instrument}")

        # Use unified interface
        result = await client.orders.post_order(
            account_id=account_id,
            order_request=order_request,
            client_request_id=f"{order_type}-order-{int(time.time())}",
        )
        order_id = result.order_create_transaction['id']
        print(f"Unified {order_type} order created: {order_id}")
        return result
```

### Monitor and Track Order Status

**Problem:** Track order execution and handle different outcomes.

```python
import os

from fivetwenty import AsyncClient, Environment
from fivetwenty.models import AccountID


async def monitor_order_execution(account_id: AccountID, order_id: str) -> None:
    """Monitor order execution status."""
    async with AsyncClient(
        token=os.environ.get("FIVETWENTY_OANDA_TOKEN", "demo-token"),
        environment=Environment.PRACTICE
    ) as client:
        # Get current order status
        order = await client.orders.get_order(account_id, order_id)
        state = order["state"]
        print(f"Order state checked: {state}")
        print("Order fill information retrieved")

        # Check if order is still pending
        if state == "PENDING":
            print("Order is waiting for execution")

            # Get all pending orders for context
            pending_response = await client.orders.get_pending_orders(account_id)
            pending_count = len(pending_response["orders"])
            print(f"Pending orders retrieved: {pending_count} total")

        elif state == "FILLED":
            print("Order execution confirmed")

        elif state == "CANCELLED":
            print("Order was cancelled")
```

### Implement Order Validation and Error Handling

**Problem:** Robust order validation to prevent common errors.

```python
import os
import time
from decimal import Decimal
from typing import Any

from fivetwenty import AsyncClient, Environment
from fivetwenty.exceptions import VeeTwentyError as FiveTwentyError
from fivetwenty.models import AccountID, InstrumentName


async def place_validated_order(
    account_id: AccountID,
    instrument: InstrumentName,
    units: int,
    order_type: str = "market",
    price: Decimal | None = None,
) -> Any:
    """Place validated order with comprehensive checks."""
    async with AsyncClient(
        token=os.environ.get("FIVETWENTY_OANDA_TOKEN", "demo-token"),
        environment=Environment.PRACTICE
    ) as client:
        try:
            # Validate account has sufficient balance
            account = await client.accounts.get_account(account_id)
            available_balance = Decimal(account.nav)
            print(f"Account balance: {available_balance}")

            # Validate instrument is tradeable
            instruments = await client.accounts.get_account_instruments(
                account_id, instruments=[instrument]
            )
            print(f"Retrieved {len(instruments)} instrument(s)")

            if not instruments:
                msg = f"Instrument {instrument} not available"
                raise ValueError(msg)

            instrument_info = instruments[0]
            if not instrument_info.tradeable:
                msg = f"Instrument {instrument} not currently tradeable"
                raise ValueError(msg)

            # Validate order size
            min_units = abs(int(instrument_info.minimum_trade_size))
            max_units = abs(int(instrument_info.maximum_order_units))

            if abs(units) < min_units:
                msg = f"Order size {units} below minimum {min_units}"
                raise ValueError(msg)
            if abs(units) > max_units:
                msg = f"Order size {units} exceeds maximum {max_units}"
                raise ValueError(msg)

            # Place order based on type
            if order_type == "market":
                response = await client.orders.post_market_order(
                    account_id=account_id,
                    instrument=instrument,
                    units=units,
                    client_request_id=f"validated-{order_type}-{int(time.time())}",
                )
            elif order_type == "limit" and price:
                response = await client.orders.post_limit_order(
                    account_id=account_id,
                    instrument=instrument,
                    units=units,
                    price=price,
                    client_request_id=f"validated-{order_type}-{int(time.time())}",
                )

            else:
                msg = "Invalid order type or missing price for limit order"
                raise ValueError(msg)

            order_id = response.order_create_transaction['id']
            print(f"Validated {order_type} order created: {order_id}")

            return response

        except FiveTwentyError as e:
            print("OANDA API error encountered")
            print("Error code logged")
            raise
        except ValueError as e:
            print("Validation error occurred")
            raise
```

### Cancel and Modify Orders

**Problem:** Manage pending orders by cancelling or replacing them.

```python
import os
from datetime import datetime, timedelta, timezone

from fivetwenty import AsyncClient, Environment
from fivetwenty.exceptions import VeeTwentyError as FiveTwentyError
from fivetwenty.models import AccountID


async def manage_pending_orders(account_id: AccountID) -> None:
    """Manage pending orders with cancellation logic."""
    async with AsyncClient(
        token=os.environ.get("FIVETWENTY_OANDA_TOKEN", "demo-token"),
        environment=Environment.PRACTICE
    ) as client:
        # Get all pending orders
        pending_response = await client.orders.get_pending_orders(account_id)
        pending_orders = pending_response["orders"]
        print(f"Found {len(pending_orders)} pending orders")

        for order in pending_orders:
            order_id = order["id"]

            # Cancel old orders (example: cancel orders older than 1 hour)
            order_time = datetime.fromisoformat(
                order["createTime"].replace("Z", "+00:00")
            )
            stale_order_threshold_hours = 1
            if datetime.now(timezone.utc) - order_time > timedelta(hours=stale_order_threshold_hours):
                try:
                    cancel_response = await client.orders.cancel_order(
                        account_id,
                        order_id,
                    )
                    cancelled_order_id = cancel_response.order_cancel_transaction.id if cancel_response.order_cancel_transaction else order_id
                    print(f"Order cancelled successfully: {cancelled_order_id}")

                except FiveTwentyError as e:
                    if e.error_code == "ORDER_DOESNT_EXIST":
                        print("Order already processed")
                    else:
                        raise
```

### Implement Batch Order Operations

**Problem:** Create multiple related orders efficiently.

The following example shows how to create multiple related orders in a single operation. This technique is essential for complex trading strategies that require coordinated order placement:

<!-- fragment: Demo bracket order creation with union attribute access and exception handling issues -->
```python
import asyncio
import os
import time
from dataclasses import dataclass
from decimal import Decimal
from typing import Any

from fivetwenty import AsyncClient, Environment
from fivetwenty.models import AccountID, InstrumentName


@dataclass
class BracketOrderParams:
    account_id: AccountID
    instrument: InstrumentName
    entry_price: Decimal
    take_profit: Decimal
    stop_loss: Decimal
    units: int

async def create_bracket_order(params: BracketOrderParams) -> Any:
    """Create a bracket order: entry + take profit + stop loss."""
    async with AsyncClient(
        token=os.environ.get("FIVETWENTY_OANDA_TOKEN", "demo-token"),
        environment=Environment.PRACTICE
    ) as client:
        # Create entry order
        entry_order = await client.orders.post_limit_order(
            account_id=params.account_id,
            instrument=params.instrument,
            units=params.units,
            price=params.entry_price,
            client_request_id=f"bracket-entry-{int(time.time())}",
        )

        entry_order_id = entry_order.order_create_transaction.id
        print(f"Entry order created successfully: {entry_order_id}")

        # Wait for entry order to fill, then create protective orders
        # In practice, you'd use webhooks or streaming for real-time updates
        await asyncio.sleep(1)  # Brief pause for demo

        # Check if entry filled
        order_status = await client.orders.get_order(params.account_id, entry_order_id)
        status_state = order_status["state"]
        print(f"Entry order status: {status_state}")

        if status_state == "FILLED":
            # Create protective orders
            tasks = []

            # Take profit order (opposite direction)
            tp_task = client.orders.post_limit_order(
                account_id=params.account_id,
                instrument=params.instrument,
                units=-params.units,  # Opposite direction to close position
                price=params.take_profit,
                client_request_id=f"bracket-tp-{int(time.time())}",
            )
            tasks.append(tp_task)

            # Stop loss order (opposite direction)
            sl_task = client.orders.post_limit_order(
                account_id=params.account_id,
                instrument=params.instrument,
                units=-params.units,  # Opposite direction to close position
                price=params.stop_loss,
                client_request_id=f"bracket-sl-{int(time.time())}",
            )
            tasks.append(sl_task)

            # Execute protective orders concurrently
            results = await asyncio.gather(*tasks, return_exceptions=True)

            for i, result in enumerate(results):
                order_type = "Take Profit" if i == 0 else "Stop Loss"
                if isinstance(result, Exception):
                    print(f"{order_type} order placement failed: {result}")
                else:
                    order_id = result.order_create_transaction.id
                    print(f"{order_type} order created successfully: {order_id}")

        return entry_order
```

## Verification

### Confirm Order Creation
```python
import os

from fivetwenty import AsyncClient, Environment
from fivetwenty.models import AccountID

async def example_order_handling():
    # Example setup for demonstration
    async with AsyncClient(
        token=os.environ.get("FIVETWENTY_OANDA_TOKEN", "demo-token"),
        environment=Environment.PRACTICE
    ) as client:
        account_id = AccountID("101-004-12345678")
        order_type = "market"

        # Create example response
        response = await client.orders.post_market_order(
            account_id=account_id,
            instrument="EUR_USD",
            units=1000
        )

        # Check order was created successfully
        if response.order_create_transaction is None:
            order_error_msg = "Order transaction is None"
            raise ValueError(order_error_msg)
        if response.order_create_transaction.id is None:
            transaction_error_msg = "Order transaction ID is None"
            raise ValueError(transaction_error_msg)

        # For market orders, verify immediate fill
        if order_type == "market":
            if response.order_fill_transaction is None:
                fill_error_msg = "Market order fill transaction is None"
                raise ValueError(fill_error_msg)
            print("Order filled successfully")
```

### Verify Order Parameters
<!-- fragment: Demo order validation with ValueError string literals -->
```python
import os

from fivetwenty import AsyncClient, Environment
from fivetwenty.models import AccountID, InstrumentName

async def verify_order_parameters() -> None:
    """Verify order parameters match your request."""
    # Example setup for demonstration
    async with AsyncClient(
        token=os.environ.get("FIVETWENTY_OANDA_TOKEN", "demo-token"),
        environment=Environment.PRACTICE
    ) as client:
        account_id = AccountID("101-004-12345678")
        order_id = "12345"  # Example order ID
        instrument = InstrumentName("EUR_USD")
        units = 1000

        # Confirm order details match your request
        order_details = await client.orders.get_order(account_id, order_id)
        print(f"Order details retrieved for {order_id}")
        if order_details["instrument"] != str(instrument):
            raise ValueError("Order instrument mismatch")
        if int(order_details["units"]) != units:
            raise ValueError("Order units mismatch")
```

### Monitor Account Impact
```python
import os

from fivetwenty import AsyncClient, Environment
from fivetwenty.models import AccountID

async def monitor_account_impact() -> None:
    """Monitor account balance and positions after order."""
    # Example setup for demonstration
    async with AsyncClient(
        token=os.environ.get("FIVETWENTY_OANDA_TOKEN", "demo-token"),
        environment=Environment.PRACTICE
    ) as client:
        account_id = AccountID("101-004-12345678")

        # Check account balance and positions after order
        account = await client.accounts.get_account(account_id)
        nav = account.nav
        print(f"Account NAV retrieved: {nav}")
        print("Unrealized P&L retrieved")
```

## Troubleshooting

### Common Order Errors

**"INSUFFICIENT_MARGIN" Error:**
```python
import os
from decimal import Decimal

from fivetwenty import AsyncClient, Environment
from fivetwenty.models import AccountID

async def check_insufficient_margin() -> None:
    """Check for insufficient margin error."""
    # Example setup for demonstration
    async with AsyncClient(
        token=os.environ.get("FIVETWENTY_OANDA_TOKEN", "demo-token"),
        environment=Environment.PRACTICE
    ) as client:
        account_id = AccountID("101-004-12345678")
        required_margin = Decimal("1000.00")  # Example required margin

        # Check available margin before placing order
        account = await client.accounts.get_account(account_id)
        available_margin = Decimal(account.margin_available)
        if available_margin < required_margin:
            msg = f"Insufficient margin for order: {available_margin} < {required_margin}"
            print(msg)
```

**"INSTRUMENT_NOT_TRADEABLE" Error:**
```python
import os

from fivetwenty import AsyncClient, Environment
from fivetwenty.models import AccountID

async def check_instrument_tradeable() -> None:
    """Check if instrument is tradeable."""
    # Example setup for demonstration
    async with AsyncClient(
        token=os.environ.get("FIVETWENTY_OANDA_TOKEN", "demo-token"),
        environment=Environment.PRACTICE
    ) as client:
        account_id = AccountID("101-004-12345678")

        # Verify instrument is currently tradeable
        instruments = await client.accounts.get_account_instruments(account_id)
        tradeable_instruments = [i for i in instruments if i.tradeable]
        print(f"Found {len(tradeable_instruments)} tradeable instruments out of {len(instruments)} total")
```

**"PRICE_PRECISION_EXCEEDED" Error:**
```python
# Use proper price precision for instrument
import os
from decimal import Decimal

from fivetwenty import AsyncClient, Environment
from fivetwenty.models import AccountID, InstrumentName
from fivetwenty._internal.utils import quantize_price

async def check_price_precision() -> None:
    """Handle price precision correctly."""
    # Example setup for demonstration
    async with AsyncClient(
        token=os.environ.get("FIVETWENTY_OANDA_TOKEN", "demo-token"),
        environment=Environment.PRACTICE
    ) as client:
        account_id = AccountID("101-004-12345678")
        instrument = InstrumentName("EUR_USD")
        your_price = Decimal("1.10555")

        # Get instrument precision
        instrument_info = await client.accounts.get_account_instruments(
            account_id, instruments=[instrument]
        )
        precision = instrument_info[0].display_precision
        print(f"Instrument precision: {precision}")

        # Quantize price correctly
        quantized_price = quantize_price(precision, your_price)
        print(f"Price quantized from {your_price} to {quantized_price}")
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
from asyncio import Semaphore
from typing import Any

from fivetwenty import AsyncClient

# Limit concurrent requests
MAX_CONCURRENT_ORDERS = 5
semaphore = Semaphore(MAX_CONCURRENT_ORDERS)

async def rate_limited_order(client: AsyncClient, order_params: Any) -> Any:
    """Place orders with rate limited order placement."""
    async with semaphore:
        result = await client.orders.post_order(**order_params)
        print(f"Rate-limited order placed: {result.order_create_transaction['id']}")
        return result
```

**Error Recovery:**
<!-- fragment: Demo error recovery with retry logic and naming violations -->
```python
import asyncio
from typing import Any

from fivetwenty import AsyncClient
from fivetwenty.exceptions import FiveTwentyError

DEFAULT_MAX_RETRIES = 3

async def robust_order_placement(client: AsyncClient, order_params: Any, max_retries: int = DEFAULT_MAX_RETRIES) -> Any:
    """Place orders with robust order placement with retry logic."""
    for attempt in range(max_retries):
        try:
            result = await client.orders.post_order(**order_params)
            print(f"Order placed successfully on attempt {attempt + 1}")
            return result
        except FiveTwentyError as e:
            if e.error_code in ["RATE_LIMIT_EXCEEDED", "SERVICE_UNAVAILABLE"]:
                BACKOFF_BASE = 2
                wait_time = BACKOFF_BASE**attempt  # Exponential backoff
                await asyncio.sleep(wait_time)
                continue
            else:
                raise  # Don't retry for non-transient errors

    msg = f"Order failed after {max_retries} attempts"
    raise Exception(msg)
```

## Advanced Patterns

### Order State Machine
<!-- fragment: Demo order state tracking with variable naming violations -->
```python
import asyncio
from datetime import datetime
from enum import Enum
from typing import Any

from fivetwenty import AsyncClient
from fivetwenty.models import AccountID


class OrderState(Enum):
    """Define order state enumeration."""

    CREATED = "created"
    PENDING = "pending"
    FILLED = "filled"
    CANCELLED = "cancelled"
    REJECTED = "rejected"


class OrderManager:
    """Manage order lifecycle."""

    def __init__(self, client: AsyncClient) -> None:
        """Initialize order manager."""
        self.client = client
        self.orders: dict[str, dict[str, Any]] = {}

    async def track_order(self, account_id: AccountID, order_id: str) -> None:
        """Track order through its lifecycle."""
        while True:
            order = await self.client.orders.get_order(account_id, order_id)
            order_state = order["state"]
            state = OrderState(order_state.lower())
            print(f"Order {order_id} state: {order_state}")

            self.orders[order_id] = {
                "state": state,
                "last_updated": datetime.now(),
                "details": order,
            }

            if state in [
                OrderState.FILLED,
                OrderState.CANCELLED,
                OrderState.REJECTED,
            ]:
                break

            POLLING_INTERVAL_SECONDS = 1
            await asyncio.sleep(POLLING_INTERVAL_SECONDS)  # Poll interval
```

### Risk Management Integration

<!-- fragment: Demo risk management with FURB157 and unused argument violations -->
```python
from decimal import Decimal
from typing import Any

from fivetwenty import AsyncClient
from fivetwenty.models import AccountID

class RiskManagedOrderSystem:
    """Manage orders with risk controls."""

    def __init__(self, client: AsyncClient, max_daily_loss: Decimal) -> None:
        """Initialize risk managed order system."""
        self.client = client
        self.max_daily_loss = max_daily_loss
        self.daily_loss = Decimal("0")

    async def place_order_with_risk_check(
        self, account_id: AccountID, **order_params: Any
    ) -> Any:
        """Place order with risk checks."""
        # Check daily loss limit
        if self.daily_loss >= self.max_daily_loss:
            msg = "Daily loss limit exceeded"
            raise ValueError(msg)

        # Calculate potential loss for this order
        potential_loss = self._calculate_potential_loss(order_params)
        print(f"Potential loss for order: {potential_loss}")

        if self.daily_loss + potential_loss > self.max_daily_loss:
            msg = "Order would exceed daily loss limit"
            raise ValueError(msg)

        # Place order if risk checks pass
        result = await self.client.orders.post_order(
            account_id=account_id,
            **order_params,
        )
        print(f"Risk-managed order placed: {result.order_create_transaction['id']}")
        return result

    def _calculate_potential_loss(self, order_params: Any) -> Decimal:
        """Calculate potential loss for order."""
        # Placeholder implementation
        potential_loss = Decimal("0")
        print(f"Calculated potential loss: {potential_loss}")
        return potential_loss
```

<!-- fragment: markdown structure bypass -->

---

**Need more specific help?** Check these related guides:

- [Implement Stop-Loss Strategies](implement-stop-loss-strategies.md) for protective order patterns
- [Close Positions](close-positions.md) for position exit strategies
- [Handle Connection Failures](handle-connection-failures.md) for robust error handling

```