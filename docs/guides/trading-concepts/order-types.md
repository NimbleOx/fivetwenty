# Order Types Reference

Complete reference for OANDA order types available through the FiveTwenty SDK.

## OANDA Order Types

OANDA supports four primary order types:

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

<!-- fragment: Demo market order execution with immediate fill analysis -->
```python
from fivetwenty import AsyncClient
from typing import Any


async def place_market_order() -> Any:
    """Place market order with comprehensive execution analysis."""
    # Step 1: Initialize client for immediate order execution
    # Market orders prioritize speed and execution certainty over price
    async with AsyncClient() as client:
        print(f"Starting Placing Market Order for Immediate Execution")

        # Step 2: Configure market order parameters
        # Market orders execute at best available price immediately
        instrument = "EUR_USD"
        position_size = 10000  # 10,000 units (1 mini lot)

        print(f"\nAnalysis Market Order Configuration:")
        print(f"   Instrument Instrument: {instrument}")
        print(f"   Position Position size: {position_size:,} units")
        print(f"   Lightning Execution: IMMEDIATE at market price")
        print(f"   Target Time-in-force: FOK (Fill or Kill)")

        try:
            # Step 3: Execute market order with FOK time-in-force
            # FOK ensures complete fill or complete cancellation
            response = await client.orders.post_market_order(
                account_id="your_account_id",
                instrument=instrument,
                units=position_size,
                time_in_force="FOK"  # Fill or Kill - all or nothing
            )

            # Step 4: Analyze order execution results
            order_id = response.order_create_transaction.id
            print(f"\nSuccess Market Order Execution Results:")
            print(f"   ID Order ID: {order_id}")
            print(f"   Time Submitted: {response.order_create_transaction.time}")

            # Step 5: Check for immediate fill (typical for market orders)
            if response.order_fill_transaction:
                fill_price = response.order_fill_transaction.price
                fill_time = response.order_fill_transaction.time
                trade_id = response.order_fill_transaction.trade_opened.trade_id if response.order_fill_transaction.trade_opened else "N/A"

                print(f"   Instrument Fill price: {fill_price}")
                print(f"   Lightning Fill time: {fill_time}")
                print(f"   Link Trade ID: {trade_id}")
                print(f"   Success Status: FILLED immediately (market order success)")

                # Step 6: Calculate execution costs
                # Market orders pay the spread immediately
                print(f"\nNote Market Order Characteristics:")
                print(f"   Lightning Speed: Immediate execution")
                print(f"   Instrument Cost: Bid-ask spread paid upfront")
                print(f"   Target Certainty: High probability of fill")
                print(f"   ⚠️ Price risk: No price guarantee")

            else:
                # Rare case: market order not filled (market conditions)
                print(f"   ⚠️ Order submitted but not immediately filled")
                print(f"   List Status: PENDING (unusual for market orders)")
                print(f"   Note Note: Check market hours and liquidity")

        except Exception as e:
            print(f"\nError Market order execution failed: {e}")
            print(f"Note Common issues: Insufficient margin, market closed, invalid parameters")
            print(f"Config Recovery: Check account balance, verify market hours, adjust size")
            raise

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

<!-- fragment: Demo limit order placement with price discipline strategy -->
```python
from decimal import Decimal
from fivetwenty import AsyncClient
from typing import Any


async def place_limit_order() -> Any:
    """Place limit order with comprehensive price discipline strategy."""
    # Step 1: Initialize client for price-controlled order execution
    # Limit orders prioritize price over timing - patience for better prices
    async with AsyncClient() as client:
        print(f"Target Placing Limit Order for Price Discipline")

        # Step 2: Analyze market context for limit order placement
        instrument = "EUR_USD"
        limit_price = Decimal("1.0850")  # Target entry price
        position_size = 10000           # Position size in base currency units

        print(f"\nPosition Limit Order Strategy Analysis:")
        print(f"   Instrument Instrument: {instrument}")
        print(f"   Target Limit price: {limit_price}")
        print(f"   Analysis Position size: {position_size:,} units")
        print(f"   Note Strategy: Buy only at {limit_price} or better (lower)")
        print(f"   Time Patience: Wait for favorable market pricing")

        # Step 3: Explain limit order execution conditions
        print(f"\nSearch Execution Conditions:")
        print(f"   Success WILL EXECUTE if market drops to {limit_price} or below")
        print(f"   Error WILL NOT EXECUTE if market stays above {limit_price}")
        print(f"   Target PRICE GUARANTEE: Never pay more than {limit_price}")
        print(f"   Time TIME RISK: May never fill if price doesn't reach level")

        try:
            # Step 4: Execute limit order with GTC time-in-force
            # GTC keeps order active until filled or manually cancelled
            response = await client.orders.post_limit_order(
                account_id="your_account_id",
                instrument=instrument,
                units=position_size,
                price=limit_price,
                time_in_force="GTC"  # Good Till Cancelled - persistent order
            )

            # Step 5: Analyze limit order creation results
            order_id = response.order_create_transaction.id
            order_time = response.order_create_transaction.time
            order_price = response.order_create_transaction.price

            print(f"\nSuccess Limit Order Creation Results:")
            print(f"   ID Order ID: {order_id}")
            print(f"   Instrument Limit price: {order_price}")
            print(f"   Time Created: {order_time}")
            print(f"   List Status: PENDING (waiting for market price)")
            print(f"   Processing Time-in-force: GTC (active until filled/cancelled)")

            # Step 6: Provide limit order monitoring guidance
            print(f"\nAnalysis Order Monitoring Strategy:")
            print(f"   Watch Watch market: Monitor price movement toward {limit_price}")
            print(f"   Processing Flexibility: Can modify or cancel if market conditions change")
            print(f"   Position Analysis: Review if limit level remains valid")
            print(f"   Time Patience: Allow time for market to reach your price")

            # Step 7: Market scenarios for limit order success
            print(f"\nFeature Favorable Market Scenarios:")
            print(f"   Down Bearish momentum: Price declining toward limit level")
            print(f"   Processing Range trading: Price oscillating around limit level")
            print(f"   News News impact: Economic events pushing price to limit")
            print(f"   Target Support level: Limit placed at technical support")

            # Step 8: Risk considerations for limit orders
            print(f"\n⚠️ Limit Order Risk Considerations:")
            print(f"   Down Opportunity cost: May miss move if price doesn't reach limit")
            print(f"   Position Market gaps: Price may gap past limit (get better fill)")
            print(f"   Processing Changing conditions: Market structure may invalidate level")
            print(f"   Time Time decay: Prolonged unfilled orders may become stale")

        except Exception as e:
            print(f"\nError Limit order placement failed: {e}")
            print(f"Note Common issues: Invalid price level, insufficient margin reservation")
            print(f"Config Recovery: Verify price format, check margin requirements")
            raise

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

<!-- fragment: Demo stop order placement with risk management strategy -->
```python
from decimal import Decimal
from fivetwenty import AsyncClient
from typing import Any


async def place_stop_order() -> Any:
    """Place stop order with comprehensive risk management strategy."""
    # Step 1: Initialize client for risk-based order execution
    # Stop orders provide automatic risk management and breakout capture
    async with AsyncClient() as client:
        print(f"Security Placing Stop Order for Risk Management")

        # Step 2: Define stop order parameters for risk protection
        instrument = "EUR_USD"
        stop_price = Decimal("1.0800")   # Stop trigger level
        position_size = -10000           # Negative = sell order

        print(f"\nPosition Stop Order Risk Management Setup:")
        print(f"   Instrument Instrument: {instrument}")
        print(f"   Security Stop price: {stop_price}")
        print(f"   Down Position: {abs(position_size):,} units (SELL)")
        print(f"   Note Purpose: Risk protection or breakout strategy")
        print(f"   Lightning Trigger: Becomes market order when price hits {stop_price}")

        # Step 3: Explain stop order trigger mechanics
        print(f"\nSearch Stop Order Trigger Mechanics:")
        if position_size < 0:  # Sell stop
            print(f"   Down SELL STOP: Triggers when market falls to {stop_price}")
            print(f"   Security Use case: Stop-loss protection for long positions")
            print(f"   Note Logic: Cut losses when market moves against you")
        else:  # Buy stop
            print(f"   Analysis BUY STOP: Triggers when market rises to {stop_price}")
            print(f"   Starting Use case: Breakout entry for momentum strategies")
            print(f"   Note Logic: Enter position when market breaks resistance")

        print(f"   Lightning Execution: Converts to MARKET ORDER when triggered")
        print(f"   ⚠️ No price guarantee: May fill away from stop price")

        try:
            # Step 4: Execute stop order with GTC persistence
            # GTC ensures stop protection remains active
            response = await client.orders.post_stop_order(
                account_id="your_account_id",
                instrument=instrument,
                units=position_size,
                price=stop_price,
                time_in_force="GTC"  # Good Till Cancelled - persistent protection
            )

            # Step 5: Analyze stop order creation results
            order_id = response.order_create_transaction.id
            order_time = response.order_create_transaction.time
            trigger_price = response.order_create_transaction.price

            print(f"\nSuccess Stop Order Creation Results:")
            print(f"   ID Order ID: {order_id}")
            print(f"   Security Trigger price: {trigger_price}")
            print(f"   Time Created: {order_time}")
            print(f"   List Status: PENDING (monitoring market for trigger)")
            print(f"   Processing Protection: Active until triggered or cancelled")

            # Step 6: Risk management implications
            print(f"\nSecurity Risk Management Benefits:")
            print(f"   Secure Automatic: No manual intervention required")
            print(f"   Time 24/7: Protection active during all market hours")
            print(f"   Down Discipline: Removes emotion from loss-cutting")
            print(f"   Instrument Capital preservation: Limits maximum loss exposure")

            # Step 7: Stop order execution scenarios
            print(f"\nLightning Execution Scenarios:")
            print(f"   Success TRIGGERS when: Market price reaches {stop_price}")
            print(f"   Starting BECOMES: Market order for immediate execution")
            print(f"   Instrument FILLS at: Best available price (may differ from stop)")
            print(f"   Position SLIPPAGE: Possible in fast/volatile markets")

            # Step 8: Stop order best practices
            print(f"\nNote Stop Order Best Practices:")
            print(f"   Angle Placement: Below support (sell stop) or above resistance (buy stop)")
            print(f"   Position Distance: Consider normal market volatility")
            print(f"   Processing Adjustment: Move stops to protect profits")
            print(f"   ⚠️ Slippage: Account for execution price differences")
            print(f"   Analysis Position size: Ensure stop loss fits risk budget")

            # Step 9: Market conditions affecting stops
            print(f"\nWave Market Conditions Impact:")
            print(f"   Position Normal markets: Stops execute near trigger price")
            print(f"   Lightning Volatile markets: Higher slippage risk")
            print(f"   News News events: Potential for large slippage")
            print(f"   Clock Market gaps: Weekend/holiday gap risk")

        except Exception as e:
            print(f"\nError Stop order placement failed: {e}")
            print(f"Note Common issues: Invalid trigger price, margin requirements")
            print(f"Config Recovery: Check price level validity, verify account capacity")
            raise

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

<!-- fragment: Demo MIT order placement with profit-taking strategy -->
```python
from decimal import Decimal
from fivetwenty import AsyncClient
from typing import Any


async def place_mit_order() -> Any:
    """Place Market-If-Touched order with comprehensive profit-taking strategy."""
    # Step 1: Initialize client for profit-maximization order execution
    # MIT orders capture profits when market reaches favorable levels
    async with AsyncClient() as client:
        print(f"Target Placing MIT Order for Profit Taking")

        # Step 2: Configure MIT order for profit-taking strategy
        instrument = "EUR_USD"
        mit_price = Decimal("1.0950")    # Profit-taking trigger level
        position_size = -10000           # Negative = close long position

        print(f"\nAnalysis MIT Order Profit-Taking Setup:")
        print(f"   Instrument Instrument: {instrument}")
        print(f"   Target MIT trigger: {mit_price}")
        print(f"   Position Position: {abs(position_size):,} units (CLOSE LONG)")
        print(f"   Note Strategy: Take profits when market reaches target")
        print(f"   Lightning Execution: Market order when price touches {mit_price}")

        # Step 3: Explain MIT order logic vs Stop orders
        print(f"\nProcessing MIT vs Stop Order Logic:")
        print(f"   Target MIT Order: Triggers on FAVORABLE price movement")
        print(f"   Analysis Example: Take profit when price rises to target")
        print(f"   Security Stop Order: Triggers on UNFAVORABLE price movement")
        print(f"   Down Example: Cut losses when price falls below level")
        print(f"   Note Key difference: MIT = profit, Stop = protection")

        # Step 4: MIT trigger scenarios
        print(f"\nPosition MIT Trigger Scenarios:")
        if position_size < 0:  # Closing long position
            print(f"   Analysis PROFIT TARGET: Sell when price rises to {mit_price}")
            print(f"   Instrument Logic: Close long position at profitable level")
            print(f"   Target Use case: Automated profit-taking for long trades")
        else:  # Opening short position
            print(f"   Down MEAN REVERSION: Buy when price rises to {mit_price}")
            print(f"   Processing Logic: Enter counter-trend position at resistance")
            print(f"   Target Use case: Fade breakouts or sell high")

        try:
            # Step 5: Execute MIT order with profit-taking discipline
            response = await client.orders.post_market_if_touched_order(
                account_id="your_account_id",
                instrument=instrument,
                units=position_size,
                price=mit_price,
                time_in_force="GTC"  # Good Till Cancelled - persistent profit target
            )

            # Step 6: Analyze MIT order creation results
            order_id = response.order_create_transaction.id
            order_time = response.order_create_transaction.time
            trigger_price = response.order_create_transaction.price

            print(f"\nSuccess MIT Order Creation Results:")
            print(f"   ID Order ID: {order_id}")
            print(f"   Target Trigger price: {trigger_price}")
            print(f"   Time Created: {order_time}")
            print(f"   List Status: PENDING (waiting for profit opportunity)")
            print(f"   Instrument Target: Profit-taking at {trigger_price}")

            # Step 7: Profit-taking strategy benefits
            print(f"\nInstrument Profit-Taking Strategy Benefits:")
            print(f"   Target Discipline: Automatic profit capture at target")
            print(f"   Calm Emotion-free: Removes greed from profit-taking")
            print(f"   Analysis Optimization: Captures gains during favorable moves")
            print(f"   Time Availability: Works 24/7 without monitoring")

            # Step 8: MIT execution characteristics
            print(f"\nLightning MIT Execution Characteristics:")
            print(f"   Analysis TRIGGERS when: Price touches {mit_price} favorably")
            print(f"   Starting BECOMES: Market order for immediate execution")
            print(f"   Instrument FILLS at: Best available price near trigger")
            print(f"   Success ADVANTAGE: Captures profits on favorable moves")

            # Step 9: Risk considerations for MIT orders
            print(f"\n⚠️ MIT Order Risk Considerations:")
            print(f"   Position Brief touch: Price may touch and reverse quickly")
            print(f"   Starting Momentum: Strong moves may fill at worse prices")
            print(f"   Target Target level: May need adjustment as market evolves")
            print(f"   Analysis Opportunity cost: May miss larger moves beyond target")

            # Step 10: MIT order optimization strategies
            print(f"\nConfig MIT Order Optimization:")
            print(f"   Angle Level selection: Place at technical resistance/targets")
            print(f"   Position Multiple targets: Use partial profit-taking levels")
            print(f"   Processing Dynamic adjustment: Move targets as trade develops")
            print(f"   Analysis Risk-reward: Ensure adequate profit vs potential loss")
            print(f"   Time Time frame: Match target to strategy timeframe")

        except Exception as e:
            print(f"\nError MIT order placement failed: {e}")
            print(f"Note Common issues: Invalid trigger level, position conflicts")
            print(f"Config Recovery: Verify trigger price, check existing positions")
            raise

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

### Required parameters

All orders need these parameters:

<!-- fragment: Demo order parameters with comprehensive configuration options -->
```python
from decimal import Decimal

# Step 1: Essential order parameters for all order types
# These parameters form the foundation of every trading order
print(f"Analysis Essential Order Parameters Configuration")

# Step 2: Define comprehensive order parameter structure
order_params = {
    "instrument": "EUR_USD",           # Trading pair (BASE_QUOTE format)
    "units": 10000,                   # Position size (+ buy, - sell)
    "type": "LIMIT",                  # Order type (MARKET, LIMIT, STOP, MIT)
    "price": Decimal("1.0850"),      # Execution price (required for non-market)
    "time_in_force": "GTC",           # Time validity (GTC, GTD, FOK, IOC)
}

print(f"\nPosition Order Parameter Breakdown:")
for param, value in order_params.items():
    if param == "instrument":
        print(f"   Instrument {param}: {value} (Currency pair in BASE_QUOTE format)")
    elif param == "units":
        direction = "BUY" if value > 0 else "SELL"
        print(f"   Analysis {param}: {value:,} ({direction} {abs(value):,} units)")
    elif param == "type":
        print(f"   Target {param}: {value} (Execution behavior)")
    elif param == "price":
        print(f"   Money {param}: {value} (Target execution price)")
    elif param == "time_in_force":
        print(f"   Time {param}: {value} (Order duration policy)")

# Step 3: Parameter validation and requirements
print(f"\nSecurity Parameter Requirements by Order Type:")
print(f"   MARKET orders: instrument, units, time_in_force")
print(f"   LIMIT orders: instrument, units, price, time_in_force")
print(f"   STOP orders: instrument, units, price, time_in_force")
print(f"   MIT orders: instrument, units, price, time_in_force")

# Step 4: Units parameter direction logic
print(f"\nDown Units Parameter Logic:")
print(f"   Success Positive units: BUY order (go long)")
print(f"   Error Negative units: SELL order (go short or close long)")
print(f"   Position Magnitude: Position size in base currency units")
print(f"   Note Example: +10000 = buy 10k EUR, -10000 = sell 10k EUR")
```

### Time-In-Force Options

Control how long orders remain active:

- **GTC** (Good Till Cancelled): Remains active until filled or cancelled
- **GTD** (Good Till Date): Expires at specified date/time
- **FOK** (Fill or Kill): Must fill completely or cancel immediately
- **IOC** (Immediate or Cancel): Fill partial amount, cancel remainder

<!-- fragment: Demo time-in-force controls with comprehensive expiration management -->
```python
from decimal import Decimal
from fivetwenty import AsyncClient
from datetime import datetime, timedelta
from typing import Any


async def order_with_time_controls() -> Any:
    """Demonstrate comprehensive time-in-force order management."""
    # Step 1: Initialize client for time-controlled order placement
    # Time-in-force controls determine order lifetime and behavior
    async with AsyncClient() as client:
        print(f"Time Time-In-Force Order Controls Demo")

        # Step 2: Calculate strategic expiration time
        # GTD orders expire at specific date/time for tactical control
        current_time = datetime.utcnow()
        expiry_time = current_time + timedelta(hours=24)  # 24-hour tactical window

        print(f"\nPosition GTD (Good Till Date) Configuration:")
        print(f"   Time Current time: {current_time.strftime('%Y-%m-%d %H:%M UTC')}")
        print(f"   Clock Expiry time: {expiry_time.strftime('%Y-%m-%d %H:%M UTC')}")
        print(f"   Analysis Duration: 24 hours tactical window")
        print(f"   Target Strategy: Time-limited opportunity capture")

        # Step 3: Configure limit order with time control
        instrument = "EUR_USD"
        limit_price = Decimal("1.0850")
        position_size = 10000

        print(f"\nAnalysis Order Configuration:")
        print(f"   Instrument Instrument: {instrument}")
        print(f"   Target Limit price: {limit_price}")
        print(f"   Position Position: {position_size:,} units")
        print(f"   Time Time-in-force: GTD (expires automatically)")

        try:
            # Step 4: Execute GTD limit order with expiration
            response = await client.orders.post_limit_order(
                account_id="your_account_id",
                instrument=instrument,
                units=position_size,
                price=limit_price,
                time_in_force="GTD",
                gtd_time=expiry_time  # Automatic expiration
            )

            # Step 5: Analyze time-controlled order creation
            order_id = response.order_create_transaction.id
            order_time = response.order_create_transaction.time

            print(f"\nSuccess GTD Order Creation Results:")
            print(f"   ID Order ID: {order_id}")
            print(f"   Time Created: {order_time}")
            print(f"   Clock Expires: {expiry_time}")
            print(f"   List Status: PENDING (time-limited)")

            # Step 6: Time-in-force strategy implications
            print(f"\nNote GTD Strategy Benefits:")
            print(f"   Time Auto-cleanup: Order expires without manual intervention")
            print(f"   Target Tactical: Perfect for event-driven trading")
            print(f"   Security Risk control: Prevents stale orders")
            print(f"   Analysis Discipline: Forces strategy re-evaluation")

            # Step 7: Alternative time-in-force demonstrations
            print(f"\nMap Time-In-Force Options Comparison:")

            tif_options = [
                ("GTC", "Good Till Cancelled", "Permanent until manual cancel", "Infinity"),
                ("GTD", "Good Till Date", "Expires at specific time", "Time"),
                ("FOK", "Fill or Kill", "Complete fill or immediate cancel", "Lightning"),
                ("IOC", "Immediate or Cancel", "Partial fill, cancel remainder", "Starting")
            ]

            for tif_code, tif_name, description, emoji in tif_options:
                print(f"   {emoji} {tif_code}: {tif_name}")
                print(f"     Note {description}")

            # Step 8: Use case scenarios for each TIF
            print(f"\nTarget Time-In-Force Use Cases:")
            print(f"   Processing GTC: Long-term support/resistance levels")
            print(f"   Time GTD: Pre-earnings, pre-news event orders")
            print(f"   Lightning FOK: Large orders requiring complete fill")
            print(f"   Starting IOC: Scalping, immediate partial execution")

            # Step 9: Time management best practices
            print(f"\nSecurity Time Management Best Practices:")
            print(f"   Position Regular review: Check pending orders daily")
            print(f"   Time Strategic expiry: Match duration to strategy")
            print(f"   Processing Renewal decision: Evaluate before expiration")
            print(f"   Target Context awareness: Consider changing market conditions")

        except Exception as e:
            print(f"\nError GTD order placement failed: {e}")
            print(f"Note Common issues: Invalid expiry time, timezone problems")
            print(f"Config Recovery: Check time format, verify future timestamp")
            raise

        return response
```

## Order State Management

### Order Lifecycle

Orders progress through predictable states:

1. **PENDING** - Waiting for trigger conditions
2. **FILLED** - Executed
3. **CANCELLED** - Manually cancelled or expired
4. **REJECTED** - Failed validation or execution

### Monitoring Order Status

<!-- fragment: Demo comprehensive order status monitoring with lifecycle tracking -->
```python
from fivetwenty import AsyncClient
from typing import Any


async def monitor_order_status(order_id: str) -> Any:
    """Monitor order status with comprehensive lifecycle tracking."""
    # Step 1: Initialize client for order status monitoring
    # Order monitoring is essential for trade management
    async with AsyncClient() as client:
        print(f"Watch Comprehensive Order Status Monitoring")
        print(f"   ID Order ID: {order_id}")

        try:
            # Step 2: Retrieve detailed order information
            order = await client.orders.get_order(
                account_id="your_account_id",
                order_id=order_id
            )

            # Step 3: Analyze order state and provide detailed status
            order_state = order.state
            print(f"\nAnalysis Order Status Analysis:")
            print(f"   List Current state: {order_state}")
            print(f"   Business Instrument: {order.instrument}")
            print(f"   Position Units: {order.units}")
            print(f"   Time Created: {order.create_time}")

            # Step 4: State-specific detailed analysis
            if order_state == "PENDING":
                # Order waiting for execution conditions
                print(f"\nTime PENDING Order Details:")
                print(f"   Target Target price: {order.price}")
                print(f"   Clock Time-in-force: {order.time_in_force}")
                print(f"   Analysis Order type: {order.type}")

                if hasattr(order, 'gtd_time') and order.gtd_time:
                    print(f"   Time Expires: {order.gtd_time}")

                print(f"   Position Status: Monitoring market for trigger conditions")
                print(f"   Note Action: Wait for price {order.price} or manual intervention")

            elif order_state == "FILLED":
                # Order successfully executed
                print(f"\nSuccess FILLED Order Details:")
                if hasattr(order, 'filling_transaction') and order.filling_transaction:
                    fill_price = order.filling_transaction.price
                    fill_time = order.filling_transaction.time
                    print(f"   Instrument Fill price: {fill_price}")
                    print(f"   Time Fill time: {fill_time}")

                    # Calculate execution quality
                    if hasattr(order, 'price') and order.price:
                        requested_price = Decimal(str(order.price))
                        actual_price = Decimal(str(fill_price))
                        slippage = actual_price - requested_price

                        if abs(slippage) < 0.0001:  # Less than 1 pip
                            execution_quality = "Success EXCELLENT"
                        elif abs(slippage) < 0.0005:  # Less than 5 pips
                            execution_quality = "Green GOOD"
                        else:
                            execution_quality = "Yellow ACCEPTABLE"

                        print(f"   Down Slippage: {slippage:+.5f}")
                        print(f"   Target Execution quality: {execution_quality}")

                print(f"   Success Status: Successfully executed")
                print(f"   Note Next: Monitor resulting position")

            elif order_state == "CANCELLED":
                # Order cancelled before execution
                print(f"\nError CANCELLED Order Details:")
                if hasattr(order, 'cancelling_transaction') and order.cancelling_transaction:
                    cancel_reason = order.cancelling_transaction.reason
                    cancel_time = order.cancelling_transaction.time
                    print(f"   Notes Cancel reason: {cancel_reason}")
                    print(f"   Time Cancel time: {cancel_time}")

                    # Analyze cancellation reasons
                    if "CLIENT_REQUEST" in cancel_reason:
                        print(f"   User Manual cancellation by user")
                    elif "TIME_IN_FORCE_EXPIRED" in cancel_reason:
                        print(f"   Time Expired due to GTD time limit")
                    elif "MARKET_HALTED" in cancel_reason:
                        print(f"   Pause Market conditions prevented execution")
                    else:
                        print(f"   ⚠️ System cancellation: {cancel_reason}")

                print(f"   Position Status: Order no longer active")
                print(f"   Note Action: Place new order if still desired")

            elif order_state == "REJECTED":
                # Order failed validation
                print(f"\nError REJECTED Order Details:")
                if hasattr(order, 'reject_reason'):
                    print(f"   Notes Reject reason: {order.reject_reason}")

                print(f"   ⚠️ Status: Failed validation or execution")
                print(f"   Note Action: Review parameters and resubmit")

            else:
                # Unknown or new order state
                print(f"\n⚠️ UNKNOWN State: {order_state}")
                print(f"   Note Check API documentation for new states")

            # Step 5: Order monitoring recommendations
            print(f"\nNote Order Monitoring Recommendations:")
            if order_state == "PENDING":
                print(f"   Watch Monitor: Check market movement toward target")
                print(f"   Processing Review: Validate order still aligns with strategy")
                print(f"   Time Timeline: Consider time remaining for execution")
            elif order_state == "FILLED":
                print(f"   Analysis Position: Monitor resulting position performance")
                print(f"   Security Risk: Ensure stop losses are in place")
                print(f"   Position Management: Consider profit-taking levels")
            elif order_state in ["CANCELLED", "REJECTED"]:
                print(f"   Search Analysis: Review why order didn't execute")
                print(f"   Processing Strategy: Adjust approach if needed")
                print(f"   Target Reentry: Place new order with updated parameters")

        except Exception as e:
            print(f"\nError Order status retrieval failed: {e}")
            print(f"Note Common issues: Invalid order ID, network problems")
            print(f"Config Recovery: Verify order ID, check connection")
            raise

        return order
```

### Modifying Pending Orders

<!-- fragment: Demo order modification with dynamic strategy adjustment -->
```python
from decimal import Decimal
from fivetwenty import AsyncClient
from fivetwenty.models import LimitOrderRequest, InstrumentName
from typing import Any


async def modify_pending_order(order_id: str, new_price: Decimal) -> Any:
    """Modify pending order with dynamic strategy adjustment capabilities."""
    # Step 1: Initialize client for order modification
    # Order modification allows strategy adaptation without cancelling/replacing
    async with AsyncClient() as client:
        print(f"Config Dynamic Order Modification System")
        print(f"   ID Order ID: {order_id}")
        print(f"   Target New price: {new_price}")

        try:
            # Step 2: Retrieve current order details for comparison
            current_order = await client.orders.get_order(
                account_id="your_account_id",
                order_specifier=order_id
            )

            print(f"\nAnalysis Current Order Analysis:")
            print(f"   Instrument Current price: {current_order.price}")
            print(f"   List State: {current_order.state}")
            print(f"   Business Instrument: {current_order.instrument}")
            print(f"   Position Units: {current_order.units}")

            # Step 3: Validate modification eligibility
            if current_order.state != "PENDING":
                print(f"\n⚠️ Modification Not Possible:")
                print(f"   List Order state: {current_order.state}")
                print(f"   Note Only PENDING orders can be modified")
                return None

            # Step 4: Calculate modification impact
            current_price = Decimal(str(current_order.price))
            price_change = new_price - current_price
            price_change_pips = price_change * 10000

            print(f"\nProcessing Modification Impact Analysis:")
            print(f"   Down Price change: {price_change:+.5f}")
            print(f"   Position Change in pips: {price_change_pips:+.1f} pips")

            # Determine modification direction and strategy
            if price_change > 0:
                direction = "Analysis HIGHER"
                strategy_impact = "More aggressive (worse entry price)"
            elif price_change < 0:
                direction = "Down LOWER"
                strategy_impact = "More conservative (better entry price)"
            else:
                direction = "Minus SAME"
                strategy_impact = "No price change"

            print(f"   Target Direction: {direction}")
            print(f"   Note Strategy impact: {strategy_impact}")

            # Step 5: Execute order modification
            print(f"\nStarting Executing Order Modification...")
            response = await client.orders.put_order(
                account_id="your_account_id",
                order_specifier=order_id,
                order_request=LimitOrderRequest(
                    instrument=current_order.instrument,
                    units=current_order.units,
                    price=new_price,
                ),
            )

            # Step 6: Analyze modification results
            if response.order_create_transaction:
                # Modification creates new order transaction
                new_order_id = response.order_create_transaction.id
                modification_time = response.order_create_transaction.time

                print(f"\nSuccess Order Modification Results:")
                print(f"   ID New order ID: {new_order_id}")
                print(f"   Instrument Updated price: {new_price}")
                print(f"   Time Modified: {modification_time}")
                print(f"   List Status: PENDING (with new parameters)")

            # Step 7: Strategic modification guidance
            print(f"\nNote Order Modification Best Practices:")
            print(f"   Analysis Market adaptation: Adjust to changing conditions")
            print(f"   Time Timing: Modify before market moves away")
            print(f"   Target Strategy alignment: Ensure modification fits plan")
            print(f"   Processing Frequency: Avoid excessive modifications")

            # Step 8: Common modification scenarios
            print(f"\nMap Common Modification Scenarios:")
            print(f"   Down Better entry: Lower limit price for better value")
            print(f"   Analysis Market pursuit: Raise price to catch moving market")
            print(f"   Map Technical update: Adjust to new support/resistance")
            print(f"   Time Time pressure: Modify before GTD expiration")

            # Step 9: Risk considerations for modifications
            print(f"\n⚠️ Modification Risk Considerations:")
            print(f"   Position Slippage: Market may move while modifying")
            print(f"   Time Timing: Brief window where order is inactive")
            print(f"   Processing Strategy drift: Too many changes may blur plan")
            print(f"   Analysis Execution risk: Modified order may fill immediately")

            # Step 10: Alternative to modification
            print(f"\nProcessing Alternatives to Modification:")
            print(f"   Error Cancel + Replace: More control but takes longer")
            print(f"   Position Scale in: Multiple orders at different levels")
            print(f"   Time Wait: Sometimes best to stick with original plan")

        except Exception as e:
            print(f"\nError Order modification failed: {e}")
            print(f"Note Common issues: Order already filled/cancelled, invalid price")
            print(f"Config Recovery: Check order status, validate new parameters")
            raise

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

<!-- fragment: Demo robust order placement with comprehensive error handling -->
```python
from decimal import Decimal
from fivetwenty import AsyncClient
from fivetwenty.exceptions import FiveTwentyError
from typing import Any, Optional


async def robust_order_placement() -> Optional[Any]:
    """Demonstrate robust order placement with comprehensive error handling."""
    # Step 1: Initialize client for fault-tolerant order placement
    # Robust error handling is essential for production trading systems
    async with AsyncClient() as client:
        print(f"Security Robust Order Placement with Error Handling")

        # Step 2: Configure order parameters with validation
        order_config = {
            "account_id": "your_account_id",
            "instrument": "EUR_USD",
            "units": 10000,
            "price": Decimal("1.0850"),
            "time_in_force": "GTC"
        }

        print(f"\nAnalysis Order Configuration:")
        for param, value in order_config.items():
            print(f"   Position {param}: {value}")

        # Step 3: Attempt order placement with comprehensive error handling
        max_retries = 3
        retry_count = 0

        while retry_count < max_retries:
            try:
                print(f"\nStarting Order Placement Attempt #{retry_count + 1}")

                # Execute limit order with full error handling
                response = await client.orders.post_limit_order(
                    account_id=order_config["account_id"],
                    instrument=order_config["instrument"],
                    units=order_config["units"],
                    price=order_config["price"],
                    time_in_force=order_config["time_in_force"]
                )

                # Step 4: Success path - order placed successfully
                order_id = response.order_create_transaction.id
                print(f"\nSuccess Order Placement Successful:")
                print(f"   ID Order ID: {order_id}")
                print(f"   Instrument Price: {order_config['price']}")
                print(f"   List Status: PENDING")
                print(f"   Success Recovery attempts: {retry_count}")

                return response

            except FiveTwentyError as e:
                retry_count += 1
                error_message = str(e)
                print(f"\nError Order Placement Failed (Attempt #{retry_count}):")
                print(f"   Notes Error: {error_message}")

                # Step 5: Error-specific handling and recovery strategies
                if "INSUFFICIENT_MARGIN" in error_message:
                    print(f"\nInstrument INSUFFICIENT_MARGIN Error Handling:")
                    print(f"   ⚠️ Issue: Not enough margin for position size")
                    print(f"   Config Recovery: Reducing position size by 50%")

                    # Reduce position size for retry
                    order_config["units"] = int(order_config["units"] * 0.5)
                    print(f"   Down New position size: {order_config['units']:,} units")

                    if order_config["units"] < 1000:  # Minimum viable size
                        print(f"   Error Position too small - insufficient account funds")
                        break

                elif "INVALID_PRICE" in error_message:
                    print(f"\nInstrument INVALID_PRICE Error Handling:")
                    print(f"   ⚠️ Issue: Price outside allowed bounds")
                    print(f"   Config Recovery: Adjusting price toward market")

                    # Adjust price toward market (example: 10 pips closer)
                    price_adjustment = Decimal("0.0010")  # 10 pips
                    if order_config["units"] > 0:  # Buy order
                        order_config["price"] += price_adjustment
                    else:  # Sell order
                        order_config["price"] -= price_adjustment

                    print(f"   Analysis Adjusted price: {order_config['price']}")

                elif "MARKET_CLOSED" in error_message:
                    print(f"\nPause MARKET_CLOSED Error Handling:")
                    print(f"   ⚠️ Issue: Trading session not active")
                    print(f"   Time Recovery: Market closed - cannot retry immediately")
                    print(f"   Note Recommendation: Schedule order for next session")
                    break  # Cannot recover from market closure

                elif "ACCOUNT_NOT_ACTIVE" in error_message:
                    print(f"\nBusiness ACCOUNT_NOT_ACTIVE Error Handling:")
                    print(f"   ⚠️ Issue: Account status prevents trading")
                    print(f"   Note Recovery: Contact broker - cannot auto-recover")
                    break  # Cannot recover from account issues

                elif "INVALID_INSTRUMENT" in error_message:
                    print(f"\nBusiness INVALID_INSTRUMENT Error Handling:")
                    print(f"   ⚠️ Issue: Instrument not available for trading")
                    print(f"   Note Recovery: Verify instrument name and availability")
                    break  # Cannot recover from invalid instrument

                elif "PRICE_PRECISION_EXCEEDED" in error_message:
                    print(f"\nPosition PRICE_PRECISION_EXCEEDED Error Handling:")
                    print(f"   ⚠️ Issue: Too many decimal places in price")
                    print(f"   Config Recovery: Rounding to valid precision")

                    # Round to 4 decimal places for most pairs
                    order_config["price"] = order_config["price"].quantize(Decimal("0.0001"))
                    print(f"   Analysis Rounded price: {order_config['price']}")

                else:
                    # Step 6: Handle unexpected errors
                    print(f"\n⚠️ UNEXPECTED Error Handling:")
                    print(f"   Notes Unknown error: {error_message}")
                    print(f"   Note Recovery: Generic retry with backoff")

                # Step 7: Retry delay with exponential backoff
                if retry_count < max_retries:
                    import asyncio
                    delay = 2 ** retry_count  # 2s, 4s, 8s delay
                    print(f"   Time Waiting {delay}s before retry...")
                    await asyncio.sleep(delay)
                else:
                    print(f"   Error Max retries ({max_retries}) exceeded")

        # Step 8: All retry attempts failed
        print(f"\nError Order Placement Failed After All Retries:")
        print(f"   Numbers Total attempts: {retry_count}")
        print(f"   ⚠️ Final status: FAILED")
        print(f"   Note Recommendation: Review account status and market conditions")

        # Step 9: Error handling best practices summary
        print(f"\nNote Error Handling Best Practices:")
        print(f"   Processing Retry logic: Implement intelligent retry strategies")
        print(f"   Down Parameter adjustment: Adapt to error conditions")
        print(f"   Time Exponential backoff: Avoid overwhelming API")
        print(f"   Position Logging: Record all errors for analysis")
        print(f"   Security Graceful degradation: Fail safely when unrecoverable")
        print(f"   Analysis Monitoring: Alert on persistent failures")

        return None  # Indicate failure
```

## Best Practices

### Order Validation

Always validate parameters before submission:

<!-- fragment: Demo comprehensive parameter validation with trading-specific checks -->
```python
from typing import Any
from decimal import Decimal


def validate_order_params(instrument: str, units: int, price: Decimal) -> Any:
    """Comprehensive order parameter validation for trading safety."""
    print(f"Security Order Parameter Validation")

    # Step 1: Units validation - ensure minimum viable trade size
    print(f"\nPosition Units Validation:")
    print(f"   Analysis Provided units: {units:,}")

    if abs(units) < 1:
        print(f"   Error Error: Units too small ({abs(units)})")
        raise ValueError("Units must be at least 1")
    elif abs(units) > 10000000:  # 10M unit safety limit
        print(f"   ⚠️ Warning: Very large position ({abs(units):,} units)")
        print(f"   Note Consider risk management implications")

    direction = "BUY" if units > 0 else "SELL"
    print(f"   Success Valid: {abs(units):,} units ({direction} order)")

    # Step 2: Price precision validation - forex-specific requirements
    print(f"\nInstrument Price Precision Validation:")
    print(f"   Analysis Provided price: {price}")

    # Check decimal places (forex pairs have specific precision requirements)
    price_tuple = price.as_tuple()
    decimal_places = abs(price_tuple.exponent) if price_tuple.exponent < 0 else 0

    print(f"   Position Decimal places: {decimal_places}")

    # Validate precision based on instrument type
    if "JPY" in instrument:
        max_precision = 3  # JPY pairs: 3 decimal places
        expected_precision = "3 decimal places (JPY pairs)"
    else:
        max_precision = 5  # Major pairs: 5 decimal places
        expected_precision = "5 decimal places (major pairs)"

    if decimal_places > max_precision:
        print(f"   Error Error: Price precision too high ({decimal_places} > {max_precision})")
        print(f"   Note Expected: {expected_precision}")
        raise ValueError(f"Price precision too high for {instrument}")

    print(f"   Success Valid: {decimal_places} decimal places (within {max_precision} limit)")

    # Step 3: Instrument format validation
    print(f"\nBusiness Instrument Format Validation:")
    print(f"   Analysis Provided instrument: {instrument}")

    # Check basic format (BASE_QUOTE)
    if "_" not in instrument:
        print(f"   Error Error: Missing underscore separator")
        print(f"   Note Expected format: BASE_QUOTE (e.g., EUR_USD)")
        raise ValueError("Invalid instrument format - must be BASE_QUOTE")

    # Split and validate currency codes
    parts = instrument.split("_")
    if len(parts) != 2:
        print(f"   Error Error: Incorrect number of parts ({len(parts)})")
        raise ValueError("Instrument must have exactly one underscore")

    base_currency, quote_currency = parts

    # Validate currency code lengths
    if len(base_currency) != 3 or len(quote_currency) != 3:
        print(f"   Error Error: Invalid currency code lengths")
        print(f"   Note Base: {base_currency} ({len(base_currency)} chars), Quote: {quote_currency} ({len(quote_currency)} chars)")
        raise ValueError("Currency codes must be 3 characters each")

    # Check for valid alphabetic characters
    if not base_currency.isalpha() or not quote_currency.isalpha():
        print(f"   Error Error: Non-alphabetic characters in currency codes")
        raise ValueError("Currency codes must contain only letters")

    print(f"   Success Valid: {base_currency}/{quote_currency} format")

    # Step 4: Price reasonableness checks
    print(f"\nPosition Price Reasonableness Validation:")

    # Check for obviously invalid prices
    if price <= 0:
        print(f"   Error Error: Price must be positive ({price})")
        raise ValueError("Price must be greater than zero")
    elif price > 1000000:  # Extremely high price
        print(f"   ⚠️ Warning: Unusually high price ({price})")
        print(f"   Note Verify this is intended")
    elif price < Decimal("0.00001"):  # Extremely low price
        print(f"   ⚠️ Warning: Unusually low price ({price})")
        print(f"   Note Verify this is intended")

    print(f"   Success Valid: Price {price} within reasonable range")

    # Step 5: Combined validation summary
    print(f"\nSuccess Validation Summary:")
    print(f"   Business Instrument: {instrument} (valid format)")
    print(f"   Position Units: {units:,} (valid size and direction)")
    print(f"   Instrument Price: {price} (valid precision and range)")
    print(f"   Success All parameters pass validation")

    return True  # All validations passed
```

### Position Size Management

<!-- fragment: Demo comprehensive position size calculation with risk management -->
```python
from decimal import Decimal
from typing import Dict, Any


async def calculate_position_size(risk_amount: Decimal, stop_distance: Decimal, instrument: str = "EUR_USD") -> Dict[str, Any]:
    """Calculate position size based on comprehensive risk management rules."""
    print(f"Analysis Position Size Calculation System")
    print(f"   Instrument Risk amount: ${risk_amount}")
    print(f"   Security Stop distance: {stop_distance} price units")
    print(f"   Business Instrument: {instrument}")

    # Step 1: Determine pip value based on instrument type
    print(f"\nPosition Pip Value Calculation:")

    if "JPY" in instrument:
        # JPY pairs: pip is 0.01 (2nd decimal place)
        pip_size = Decimal("0.01")
        pip_value_per_10k = Decimal("1.0")  # Approximate for USD account
        print(f"   Japan JPY pair detected")
        print(f"   Position Pip size: {pip_size} (2nd decimal place)")
    else:
        # Major pairs: pip is 0.0001 (4th decimal place)
        pip_size = Decimal("0.0001")
        pip_value_per_10k = Decimal("1.0")  # $1 per pip for 10k units (EUR_USD)
        print(f"   World Major pair detected")
        print(f"   Position Pip size: {pip_size} (4th decimal place)")

    print(f"   Instrument Pip value: ${pip_value_per_10k} per 10k units")

    # Step 2: Convert stop distance to pips
    stop_distance_pips = stop_distance / pip_size
    print(f"\nSecurity Stop Distance Analysis:")
    print(f"   Pin Stop in price units: {stop_distance}")
    print(f"   Position Stop in pips: {stop_distance_pips:.1f} pips")

    # Step 3: Calculate base position size
    print(f"\nAnalysis Position Size Calculation:")

    # Risk per pip for 10k units
    risk_per_pip_10k = stop_distance_pips * pip_value_per_10k
    print(f"   Instrument Risk per 10k units: ${risk_per_pip_10k:.2f}")

    # Position size to match risk amount
    if risk_per_pip_10k > 0:
        position_size_10k_lots = risk_amount / risk_per_pip_10k
        position_size_units = position_size_10k_lots * 10000
    else:
        position_size_units = 0

    print(f"   Position Calculated size: {position_size_units:.0f} units")
    print(f"   Ruler In lots: {position_size_units / 10000:.2f} mini lots")

    # Step 4: Apply risk management constraints
    print(f"\nSecurity Risk Management Constraints:")

    # Maximum position size limits
    max_position_absolute = 1000000  # 1M units absolute maximum
    max_position_conservative = 100000  # 100k units conservative maximum

    # Apply constraints
    constrained_size = min(int(position_size_units), max_position_absolute)
    conservative_size = min(constrained_size, max_position_conservative)

    print(f"   Analysis Calculated: {position_size_units:.0f} units")
    print(f"   ⚠️ Absolute max: {max_position_absolute:,} units")
    print(f"   Success Conservative max: {max_position_conservative:,} units")
    print(f"   Target Final size: {constrained_size:,} units")

    # Step 5: Validate minimum position size
    minimum_position = 1000  # 1k units minimum
    if constrained_size < minimum_position:
        print(f"\n⚠️ Position Size Warning:")
        print(f"   Down Calculated size too small: {constrained_size} units")
        print(f"   Pin Minimum viable: {minimum_position} units")
        print(f"   Note Consider: Increase risk amount or reduce stop distance")

    # Step 6: Calculate actual risk with final position size
    actual_risk = (constrained_size / 10000) * risk_per_pip_10k
    risk_utilization = (actual_risk / risk_amount) * 100 if risk_amount > 0 else 0

    print(f"\nPosition Actual Risk Analysis:")
    print(f"   Instrument Target risk: ${risk_amount}")
    print(f"   Analysis Actual risk: ${actual_risk:.2f}")
    print(f"   Ruler Risk utilization: {risk_utilization:.1f}%")

    # Step 7: Position sizing recommendations
    print(f"\nNote Position Sizing Recommendations:")

    if risk_utilization > 100:
        print(f"   ⚠️ Over-leveraged: Reduce position size")
    elif risk_utilization > 90:
        print(f"   Yellow Near maximum: Consider slight reduction")
    elif risk_utilization > 70:
        print(f"   Success Well-utilized: Good risk management")
    else:
        print(f"   Green Conservative: Could increase if desired")

    # Calculate alternative sizing options
    sizing_options = {
        "conservative": conservative_size,
        "calculated": constrained_size,
        "aggressive": min(int(constrained_size * 1.5), max_position_absolute)
    }

    print(f"\nAnalysis Sizing Options:")
    for approach, size in sizing_options.items():
        option_risk = (size / 10000) * risk_per_pip_10k
        option_utilization = (option_risk / risk_amount) * 100 if risk_amount > 0 else 0
        print(f"   {approach.title()}: {size:,} units (${option_risk:.2f} risk, {option_utilization:.1f}% utilization)")

    # Step 8: Return comprehensive results
    return {
        "recommended_size": constrained_size,
        "conservative_size": conservative_size,
        "actual_risk": actual_risk,
        "risk_utilization": risk_utilization,
        "stop_distance_pips": stop_distance_pips,
        "pip_value": pip_value_per_10k,
        "sizing_options": sizing_options
    }
```

## Next Steps

The advanced-order tutorials build on these types:

- **[Stop Orders & Market-If-Touched](../../tutorials/advanced-orders/stop-orders-mit.md)** - Breakout and mean reversion strategies
- **[Dynamic Order Management](../../tutorials/advanced-orders/dynamic-management.md)** - Trailing stops and adaptive sizing
- **[Order Strategies & Combinations](../../tutorials/advanced-orders/order-strategies.md)** - Bracket orders and advanced techniques

## Key Takeaways

1. **Market orders** provide speed, **limit orders** provide price control
2. **Stop orders** trigger on unfavorable moves, **MIT orders** trigger on favorable moves
3. Choose **time-in-force** settings based on your strategy timeframe
4. Always validate order parameters before submission
5. Monitor order states and handle errors gracefully
6. Select order types based on market conditions and strategy goals
