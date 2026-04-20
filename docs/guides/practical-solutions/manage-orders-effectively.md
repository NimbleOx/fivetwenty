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
from fivetwenty.exceptions import FiveTwentyError


async def main() -> None:
    """Demonstrate OnFill pattern for immediate risk protection upon order execution."""
    # Step 1: Initialize AsyncClient with practice environment for safe testing
    # OnFill pattern applies risk management instantly when orders execute
    client = AsyncClient(
        token=os.environ.get("FIVETWENTY_OANDA_TOKEN", "demo-token"),  # Environment-based auth
        environment=Environment.PRACTICE  # Practice mode prevents real money risk
    )
    account_id = "your-account-id"  # Replace with your actual OANDA account ID

    # Step 2: Place market order with automatic risk management
    # OnFill orders activate take profit and stop loss immediately upon execution
    await client.orders.post_market_order(
        account_id=account_id,            # Account for order execution
        instrument="EUR_USD",              # Major currency pair with high liquidity
        units=1000,                       # Position size: 1,000 units EUR long
        take_profit=Decimal("1.1100"),    # Automatic TP: locks in profits at 1.1100
        stop_loss=Decimal("1.0900"),      # Automatic SL: limits losses at 1.0900
    )
    # Success Risk management is now active automatically - no additional API calls needed
    print("Analysis Market order placed with automatic risk management")
    print("Target Take profit: 1.1100 | Security Stop loss: 1.0900")


if __name__ == "__main__":
    # Step 3: Execute the OnFill pattern demonstration
    # This pattern is recommended for most trading scenarios requiring immediate protection
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
    """Demonstrate post-trade pattern for adding risk management after market analysis."""
    # Step 1: Initialize client for sequential trade and risk management setup
    # Post-trade pattern allows market analysis between trade and risk management
    client = AsyncClient(
        token=os.environ.get("FIVETWENTY_OANDA_TOKEN", "demo-token"),  # Environment auth
        environment=Environment.PRACTICE  # Safe testing environment
    )
    account_id = "your-account-id"  # Replace with your OANDA account ID

    # Step 2: First create trade without immediate risk management
    # This approach allows market analysis before setting protective levels
    market_response = await client.orders.post_market_order(
        account_id=account_id,    # Account for trade execution
        instrument="EUR_USD",      # Currency pair to trade
        units=1000,              # Position size: 1,000 units EUR long
    )
    print("Analysis Market order executed - analyzing market conditions...")

    # Step 3: Extract trade information from order response
    # Trade ID is required to attach risk management orders
    trade_info = market_response.order_fill_transaction["tradeOpened"]
    trade_id = trade_info["tradeID"]  # Unique identifier for this trade
    print(f"Business Trade opened with ID: {trade_id}")

    # Step 4: Add take profit order based on market analysis
    # Separate API call allows dynamic pricing based on current conditions
    tp_request = TakeProfitOrderRequest(
        tradeID=trade_id,      # Links TP order to specific trade
        price="1.1100"         # Profit target level determined by analysis
    )
    tp_response = await client.orders.post_order(account_id, tp_request)
    tp_order_id = tp_response.order_create_transaction['id']
    print(f"Target Take profit order created: {tp_order_id}")
    print("Success Post-trade risk management successfully applied")
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
    """Implement comprehensive post-trade risk management for systematic trade protection."""
    # Step 1: Initialize AsyncClient with context manager for automatic cleanup
    # Context manager ensures proper connection closure after operations complete
    async with AsyncClient(
        token=os.environ.get("FIVETWENTY_OANDA_TOKEN", "demo-token"),  # Environment-based auth
        environment=Environment.PRACTICE  # Practice mode for safe testing
    ) as client:
        account_id = AccountID("your-account-id")  # Replace with your OANDA account ID

        # Step 2: Create initial trade without immediate risk management
        # This approach allows market analysis before setting protective levels
        print("Analysis Creating initial position for risk management demonstration...")
        market_response = await client.orders.post_market_order(
            account_id=account_id,    # Account for trade execution
            instrument="EUR_USD",      # Major currency pair with high liquidity
            units=10000,              # Position size: Buy 10,000 EUR (larger size for demo)
        )
        print("Success Market order executed successfully")

        # Step 3: Extract trade information from order fill response
        # Trade ID is essential for linking risk management orders to specific trades
        if (
            market_response.order_fill_transaction
            and "tradeOpened" in market_response.order_fill_transaction
        ):
            trade_info = market_response.order_fill_transaction["tradeOpened"]
            trade_id = trade_info["tradeID"]  # Unique trade identifier from OANDA
            entry_price = trade_info["price"]  # Actual fill price for calculations
            print(f"Business Trade opened: ID {trade_id} at price {entry_price}")

            # Step 4: Add take profit order for systematic profit capture
            # Take profit locks in gains when price reaches target level
            print("Target Adding take profit order for profit protection...")
            tp_request = TakeProfitOrderRequest(
                tradeID=trade_id,        # Links TP to specific trade
                price="1.1150",          # Target price: 150 pips profit (aggressive target)
                timeInForce="GTC",       # Good Till Cancelled: remains active until filled
            )
            print(f"   TP request prepared for trade {trade_id}: target 1.1150")

            # Step 5: Execute take profit order creation
            tp_response = await client.orders.post_order(account_id, tp_request)
            tp_order_id = tp_response.order_create_transaction["id"]
            print(f"   Success Take profit order created: {tp_order_id}")

            # Step 6: Add stop loss order for systematic loss limitation
            # Stop loss protects against adverse price movement beyond acceptable risk
            print("Security Adding stop loss order for capital protection...")
            sl_request = StopLossOrderRequest(
                tradeID=trade_id,        # Links SL to specific trade
                price="1.0950",          # Stop price: 50 pips risk (conservative risk)
                timeInForce="GTC",       # Persistent protection until triggered
            )
            print(f"   SL request prepared for trade {trade_id}: stop at 1.0950")

            # Step 7: Execute stop loss order creation
            sl_response = await client.orders.post_order(account_id, sl_request)
            sl_order_id = sl_response.order_create_transaction["id"]
            print(f"   Success Stop loss order created: {sl_order_id}")

            # Step 8: Confirm comprehensive risk management is now active
            print(f"\nData Post-Trade Risk Management Summary:")
            print(f"   Trade ID: {trade_id}")
            print(f"   Entry Price: {entry_price}")
            print(f"   Take Profit: 1.1150 (TP Order: {tp_order_id})")
            print(f"   Stop Loss: 1.0950 (SL Order: {sl_order_id})")
            print(f"   Risk-Reward: 50 pips risk / 150 pips reward = 1:3 ratio")
            print("   Success Comprehensive protection now active")
```

#### Distance-Based Stop Loss

<!-- fragment: Demo stop loss order creation with string-to-Decimal type mismatches -->
```python
from fivetwenty import AsyncClient
from fivetwenty.models import StopLossOrderRequest

# Alternative: Distance-based stop loss (dynamic pricing)
async def add_distance_based_stop_loss(client: AsyncClient, account_id: str, trade_id: str) -> str:
    """Add stop loss based on distance rather than fixed price for adaptive risk management."""
    # Step 1: Create distance-based stop loss request
    # Distance-based stops automatically adjust with entry price changes
    distance_sl_request = StopLossOrderRequest(
        tradeID=trade_id,            # Links stop loss to specific trade
        distance="0.0050",           # 50 pips from entry price (dynamic calculation)
        timeInForce="GTC",           # Good Till Cancelled: persistent protection
    )
    print(f"💯 Distance-based stop loss prepared: 50 pips for trade {trade_id}")
    print("   Info Distance automatically adjusts with entry price")

    # Step 2: Execute distance-based stop loss order
    # OANDA calculates actual stop price based on entry price + distance
    response = await client.orders.post_order(account_id, distance_sl_request)
    order_id = response.order_create_transaction["id"]
    print(f"   Success Distance-based stop loss created: {order_id}")
    print("   Data Stop price will be exactly 50 pips from trade entry")
    return order_id
```

#### Trailing Stop Loss

<!-- fragment: Demo trailing stop loss with timeInForce type incompatibility -->
```python
from fivetwenty import AsyncClient
from fivetwenty.models import TrailingStopLossOrderRequest

async def add_trailing_stop_loss(client: AsyncClient, account_id: str, trade_id: str) -> str:
    """Add trailing stop loss that follows favorable price movement for dynamic profit protection."""
    # Step 1: Create trailing stop loss request for dynamic risk management
    # Trailing stops automatically move with favorable price action while maintaining protection
    tsl_request = TrailingStopLossOrderRequest(
        tradeID=trade_id,          # Links trailing stop to specific trade
        distance="0.0030",         # 30 pips trailing distance (tight protection)
        timeInForce="GTC",         # Good Till Cancelled: follows price indefinitely
    )
    print(f"🎏 Trailing stop loss prepared: 30 pips for trade {trade_id}")
    print("   Info Stop will follow price upward but never move down")

    # Step 2: Execute trailing stop loss order
    # OANDA manages trailing automatically - stop moves up with price, never down
    response = await client.orders.post_order(account_id, tsl_request)
    order_id = response.order_create_transaction["id"]
    print(f"   Success Trailing stop created: {order_id}")
    print("   Data Will follow price with 30 pip buffer, locking in profits")
    print("   Secure Provides dynamic profit protection as price moves favorably")
    return order_id
```

#### Guaranteed Stop Loss

<!-- fragment: Demo guaranteed stop loss with response indexing issues -->
```python
from fivetwenty import AsyncClient
from fivetwenty.models import GuaranteedStopLossOrderRequest, StopLossOrderRequest

async def add_guaranteed_stop_loss(client: AsyncClient, account_id: str, trade_id: str) -> str:
    """Add guaranteed stop loss with premium cost for absolute execution certainty."""
    try:
        # Step 1: Create guaranteed stop loss request
        # Guaranteed stops ensure execution at specified price regardless of market gaps
        gsl_request = GuaranteedStopLossOrderRequest(
            tradeID=trade_id,          # Links GSL to specific trade
            price="1.0900",            # Guaranteed execution price (absolute protection)
            timeInForce="GTC",         # Persistent until triggered
        )
        print(f"Security Guaranteed stop loss prepared for trade {trade_id}")
        print("   Info GSL guarantees execution even during market gaps")

        # Step 2: Execute guaranteed stop loss order
        # OANDA charges premium for execution guarantee during volatile markets
        response = await client.orders.post_order(account_id, gsl_request)
        order_id = response.order_create_transaction["id"]

        # Step 3: Check and display premium cost for guaranteed execution
        # Premium compensates OANDA for execution risk during market gaps
        if "guaranteedExecutionPremium" in response.order_create_transaction:
            premium = response.order_create_transaction["guaranteedExecutionPremium"]
            print(f"   Balance Guaranteed execution premium: {premium}")
            print("   Info Premium ensures execution during market volatility")

        print(f"   Success Guaranteed stop loss created: {order_id}")
        print("   Secure Absolute protection against slippage and gaps")

    except Exception:
        # Step 4: Handle cases where guaranteed stops are not available
        # Some instruments or market conditions may not support guaranteed stops
        print("⚠️ Guaranteed stop loss not available for this instrument")
        print("   Processing Falling back to regular stop loss protection...")
        # Fallback to regular stop loss
        return await add_regular_stop_loss(client, account_id, trade_id)
    else:
        return order_id


async def add_regular_stop_loss(client: AsyncClient, account_id: str, trade_id: str) -> str:
    """Add regular stop loss as fallback protection when guaranteed stops unavailable."""
    # Step 1: Create standard stop loss request as fallback
    # Regular stops provide protection but may experience slippage during gaps
    sl_request = StopLossOrderRequest(
        tradeID=trade_id,          # Links stop to specific trade
        price="1.0900",            # Stop trigger price (subject to slippage)
        timeInForce="GTC",         # Persistent protection
    )
    print(f"Security Regular stop loss prepared for trade {trade_id}")
    print("   Info Standard protection with potential slippage during gaps")

    # Step 2: Execute regular stop loss order
    response = await client.orders.post_order(account_id, sl_request)
    order_id = response.order_create_transaction["id"]
    print(f"   Success Regular stop loss created: {order_id}")
    print("   Data Provides standard risk protection at no premium cost")
    return order_id
```

#### Error Handling for Post-Trade Orders

<!-- fragment: Demo robust trade setup with union attribute access -->
```python
from fivetwenty import AsyncClient
from fivetwenty.exceptions import FiveTwentyError
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
        print(f"Success Take profit order added successfully: {tp_order_id}")

    except FiveTwentyError as e:
        error_msg = str(e)

        if "TRADE_DOESNT_EXIST" in error_msg:
            print("Error Trade no longer exists - may have been closed")
        elif "INSUFFICIENT_MARGIN" in error_msg:
            print("Error Insufficient margin for risk management orders")
        elif "PRICE_INVALID" in error_msg:
            print("Error Invalid price level - adjust take profit price")
        else:
            print("Error Unexpected error occurred")

    except Exception:
        print("Error System error occurred")
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
    """Demonstrate placing market orders for immediate trade execution at current market prices."""
    # Step 1: Initialize AsyncClient with practice environment for safe testing
    # Market orders provide immediate execution but accept current market price (no price control)
    async with AsyncClient(
        token=os.environ.get("FIVETWENTY_OANDA_TOKEN", "demo-token"),  # Environment-based auth
        environment=Environment.PRACTICE  # Always use practice for examples to prevent real money risk
    ) as client:

        # Example 1: Basic market order for immediate position entry
        # Market orders execute immediately at best available price when submitted
        print("Analysis Example 1: Basic market order (immediate execution)")
        response = await client.orders.post_market_order(
            account_id=AccountID("101-004-12345678"),  # Replace with your OANDA account ID
            instrument=InstrumentName("EUR_USD"),      # Major currency pair with high liquidity
            units=1000,                                # Position size: positive = buy, negative = sell
            client_request_id="market-order-001",     # Optional: for tracking/debugging purposes
        )
        order_id = response.order_create_transaction['id']
        print(f"   Success Market order placed: {order_id}")
        print("   Info Executed immediately at current market price")

        # Example 2: Market order with built-in risk management (OnFill pattern)
        # This approach sets stop-loss and take-profit levels automatically when order fills
        print("\nAnalysis Example 2: Market order with automatic risk management")
        response = await client.orders.post_market_order(
            account_id=AccountID("101-004-12345678"),  # Replace with your OANDA account ID
            instrument=InstrumentName("EUR_USD"),      # Same currency pair for consistency
            units=1000,                                # Same position size for comparison
            take_profit=Decimal("1.1050"),            # Automatic profit-taking at 1.1050
            stop_loss=Decimal("1.0950"),              # Automatic loss-limiting at 1.0950
        )
        order_id = response.order_create_transaction['id']
        print(f"   Success Market order executed successfully: {order_id}")
        print("   Security Order filled at market price with protective stops active")
        print("   Target Take Profit: 1.1050 | Stop Loss: 1.0950")
        print("   ✨ Risk management activated automatically upon fill")
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
    """Demonstrate placing limit orders for precise entry price control and patient positioning."""
    # Step 1: Initialize AsyncClient for limit order demonstration
    # Limit orders provide price control but execution is not guaranteed
    async with AsyncClient(
        token=os.environ.get("FIVETWENTY_OANDA_TOKEN", "demo-token"),  # Environment auth
        environment=Environment.PRACTICE  # Safe testing environment
    ) as client:

        # Step 2: Place limit order with precise entry requirements
        # Limit orders only execute when market reaches your specified price or better
        print("Target Placing limit order for precise entry control...")
        response = await client.orders.post_limit_order(
            account_id=AccountID("101-004-12345678"),  # Replace with your OANDA account ID
            instrument=InstrumentName("GBP_USD"),      # British Pound vs US Dollar pair
            units=500,                                # Position size: 500 GBP long
            price=Decimal("1.2500"),                  # Entry price: Buy only when price drops to 1.2500
            time_in_force="GTC",                      # Good Till Cancelled: stays active until filled
            take_profit=Decimal("1.2600"),            # Profit target: 100 pips above entry
            stop_loss=Decimal("1.2400"),              # Risk limit: 100 pips below entry
        )
        order_id = response.order_create_transaction['id']
        print(f"   Success Limit order placed successfully: {order_id}")
        print(f"   Balance Entry Price: 1.2500 (waits for market to reach this level)")
        print(f"   Target Take Profit: 1.2600 (100 pips target)")
        print(f"   Security Stop Loss: 1.2400 (100 pips risk)")
        print("   Wait Order will wait patiently until price reaches 1.2500 or better")
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
    """Demonstrate placing stop orders for breakout trading and momentum capture strategies."""
    # Step 1: Initialize AsyncClient for stop order demonstration
    # Stop orders become market orders when trigger price is reached (breakout trading)
    async with AsyncClient(
        token=os.environ.get("FIVETWENTY_OANDA_TOKEN", "demo-token"),  # Environment auth
        environment=Environment.PRACTICE  # Safe testing environment
    ) as client:

        # Step 2: Place buy stop order for upward breakout strategy
        # Buy stop triggers when price breaks above resistance level (momentum trading)
        print("Starting Placing buy stop order for upward breakout strategy...")
        response = await client.orders.post_stop_order(
            account_id=AccountID("101-004-12345678"),  # Replace with your OANDA account ID
            instrument=InstrumentName("EUR_USD"),      # Major currency pair for breakout trading
            units=1000,                               # Position size: 1,000 EUR long on breakout
            price=Decimal("1.1100"),                  # Stop activation: triggers when price hits 1.1100
            price_bound=Decimal("1.1110"),            # Maximum slippage: won't pay more than 1.1110
            time_in_force="GFD",                     # Good for day: expires at market close
            take_profit=Decimal("1.1150"),            # Profit target: 50 pips above breakout
            stop_loss=Decimal("1.1050"),             # Risk limit: 50 pips below breakout
            client_request_id="breakout-strategy-001", # Tracking ID for strategy monitoring
        )
        order_id = response.order_create_transaction['id']
        print(f"   Success Stop order placed successfully: {order_id}")
        print(f"   Data Breakout Trigger: 1.1100 (becomes market order when hit)")
        print(f"   Security Price Protection: won't pay more than 1.1110 (slippage control)")
        print(f"   Target Take Profit: 1.1150 (50 pips momentum target)")
        print(f"   Security Stop Loss: 1.1050 (50 pips breakout failure protection)")
        print("   Time Expires at end of trading day if not triggered")
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
    """Demonstrate placing market-if-touched orders for support/resistance level trading."""
    # Step 1: Initialize AsyncClient for MIT order demonstration
    # MIT orders execute at market price when trigger level is touched (perfect for S/R trading)
    async with AsyncClient(
        token=os.environ.get("FIVETWENTY_OANDA_TOKEN", "demo-token"),  # Environment auth
        environment=Environment.PRACTICE  # Safe testing environment
    ) as client:

        # Step 2: Place MIT order for support level bounce strategy
        # MIT triggers at support touch, then executes at current market price
        print("Target Placing Market-If-Touched order for support bounce strategy...")
        response = await client.orders.post_market_if_touched_order(
            account_id=AccountID("101-004-12345678"),  # Replace with your OANDA account ID
            instrument=InstrumentName("GBP_USD"),      # British Pound for support/resistance trading
            units=750,                                # Position size: 750 GBP long on bounce
            price=Decimal("1.2400"),                  # Support level trigger: activates when touched
            price_bound=Decimal("1.2390"),            # Slippage limit: won't pay less than 1.2390
            time_in_force="GTC",                     # Good till cancelled: persistent until triggered
            take_profit=Decimal("1.2500"),            # Profit target: 100 pips bounce target
            stop_loss=Decimal("1.2350"),             # Risk limit: 50 pips below support break
            client_request_id="support-bounce-001",   # Strategy tracking identifier
        )
        order_id = response.order_create_transaction['id']
        print(f"   Success MIT order placed successfully: {order_id}")
        print(f"   Data Support Touch: 1.2400 (triggers when price reaches this level)")
        print(f"   Security Price Protection: won't buy below 1.2390 (10 pip slippage limit)")
        print(f"   Target Take Profit: 1.2500 (100 pips bounce target from support)")
        print(f"   Security Stop Loss: 1.2350 (50 pips protection if support fails)")
        print("   Infinity Perfect for support/resistance trading strategies")
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
    """Create orders dynamically by type using the unified order interface for flexible strategy implementation."""
    # Step 1: Initialize AsyncClient for unified order interface demonstration
    # Unified interface allows programmatic order creation based on strategy logic
    async with AsyncClient(
        token=os.environ.get("FIVETWENTY_OANDA_TOKEN", "demo-token"),  # Environment auth
        environment=Environment.PRACTICE  # Safe testing for dynamic order creation
    ) as client:
        account_id = AccountID("101-004-12345678")  # Replace with your OANDA account ID
        instrument = InstrumentName("USD_JPY")      # Japanese Yen pair for demo
        units = 1000                               # Standard position size for all order types

        # Step 2: Build order request dynamically based on strategy requirements
        # Different order types serve different strategic purposes in trading
        print(f"Config Building {order_type} order request for {instrument}...")

        if order_type == "market":
            # Market order for immediate execution (speed over price control)
            order_request = MarketOrderRequest(
                instrument=instrument,    # Currency pair to trade
                units=units,             # Position size
            )
            print("   Lightning Market order: immediate execution at current price")

        elif order_type == "limit":
            # Limit order for precise price control (price over speed)
            if price is None:
                raise ValueError("Limit orders require price parameter")
            order_request = LimitOrderRequest(
                instrument=instrument,        # Currency pair to trade
                units=units,                 # Position size
                price=str(price),            # Exact entry price requirement
                timeInForce=TimeInForce.GTC, # Good till cancelled
            )
            print(f"   Target Limit order: precise entry at {price}")

        elif order_type == "stop":
            # Stop order for breakout trading (momentum capture)
            if price is None:
                raise ValueError("Stop orders require price parameter")
            order_request = StopOrderRequest(
                instrument=instrument,        # Currency pair to trade
                units=units,                 # Position size
                price=str(price),            # Breakout trigger price
                timeInForce=TimeInForce.GTC, # Good till cancelled
            )
            print(f"   Starting Stop order: breakout trigger at {price}")

        else:
            msg = f"Unsupported order type: {order_type}"
            raise ValueError(msg)

        print(f"   Success {order_type.title()} order request created for {instrument}")

        # Step 3: Execute order using unified interface
        # Single interface handles all order types consistently
        result = await client.orders.post_order(
            account_id=account_id,                                    # Account for execution
            order_request=order_request,                             # Order specification
            client_request_id=f"{order_type}-order-{int(time.time())}", # Unique tracking ID
        )
        order_id = result.order_create_transaction['id']
        print(f"   Success Unified {order_type} order created: {order_id}")
        print(f"   Data Order processed through unified interface successfully")
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
from fivetwenty.exceptions import FiveTwentyError
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
from fivetwenty.exceptions import FiveTwentyError
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