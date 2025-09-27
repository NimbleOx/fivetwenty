# How to Implement Stop-Loss Strategies

**Problem**: You need to implement automated stop-loss mechanisms to protect your trading capital from excessive losses.

**Solution**: Use the FiveTwenty's built-in stop-loss functionality with multiple strategic approaches for different trading scenarios.

---

## Prerequisites

- Active OANDA account with trading permissions
- FiveTwenty configured with valid credentials
- Understanding of basic order types and risk management
- Account with sufficient margin for testing

---

## Quick Stop-Loss Implementation

### Basic Stop-Loss with Market Order

Attach a stop-loss immediately when placing a trade:

```python
import asyncio
import os
from decimal import Decimal
from typing import Any

from dotenv import load_dotenv

from fivetwenty import AsyncClient, Environment
from fivetwenty.models import StopLossDetails

# Load environment variables from .env file
load_dotenv()

async def place_order_with_stop_loss(instrument: str, units: int, stop_loss_price: Decimal) -> Any:
    """Place market order with immediate stop-loss protection."""

    # Zero-config - automatically uses environment variables
    async with AsyncClient(
        token=os.environ.get("FIVETWENTY_OANDA_TOKEN", "demo-token"),
        environment=Environment.PRACTICE
    ) as client:
        try:
            # Create market order with stop-loss attached
            response = await client.orders.post_market_order(
                account_id=client.account_id,
                instrument=instrument,
                units=units,
                stop_loss_on_fill=StopLossDetails(
                    price=stop_loss_price,
                    time_in_force="GTC"  # Good till cancelled
                )
            )

            if response.order_fill_transaction:
                fill = response.order_fill_transaction
                print(f"✅ Order filled at {fill.price}")
                print(f"🛡️ Stop-loss set at {stop_loss_price}")
                return fill.trade_opened.trade_id if fill.trade_opened else None

            print("❌ Order not filled")
            return None

        except Exception as e:
            print(f"❌ Error placing order with stop-loss: {e}")
            return None

# Usage example
if __name__ == "__main__":
    trade_id = asyncio.run(place_order_with_stop_loss(
        instrument="EUR_USD",
        units=10000,  # Buy 10k EUR
        stop_loss_price=Decimal("1.0950")  # Stop at 1.0950
    ))
```

---

## Fixed Distance Stop-Loss

### Pip-Based Stop-Loss

Set stop-loss at fixed pip distance from entry:

```python
import os
from decimal import Decimal
from typing import Any

from fivetwenty import AsyncClient, Environment
from fivetwenty.models import StopLossDetails


def calculate_stop_loss_price(entry_price: Decimal, units: int, pip_distance: int,
                            instrument: str) -> Decimal:
    """Calculate stop-loss price based on pip distance."""

    # Determine pip size (most pairs = 0.0001, JPY pairs = 0.01)
    pip_size = Decimal("0.01") if "JPY" in instrument else Decimal("0.0001")

    # Calculate pip value in price terms
    pip_value = pip_distance * pip_size

    # Long position: stop below entry, Short position: stop above entry
    return entry_price - pip_value if units > 0 else entry_price + pip_value

async def implement_pip_based_stop_loss(account_id: str, instrument: str, units: int, pip_distance: int = 50) -> Any:
    """Implement stop-loss based on fixed pip distance."""

    # Zero-config - automatically uses environment variables
    async with AsyncClient(
        token=os.environ.get("FIVETWENTY_OANDA_TOKEN", "demo-token"),
        environment=Environment.PRACTICE
    ) as client:
        try:
            # Get current price to calculate entry point
            prices = await client.pricing.get_pricing(account_id, [instrument])
            current_price = prices[0]

            # Use appropriate price for order direction
            entry_price = current_price.asks[0].price if units > 0 else current_price.bids[0].price

            # Calculate stop-loss price
            stop_loss_price = calculate_stop_loss_price(entry_price, units, pip_distance, instrument)

            print(f"📊 Entry price: {entry_price}")
            print(f"🛡️ Stop-loss: {stop_loss_price} ({pip_distance} pips)")

            # Place order with calculated stop-loss
            response = await client.orders.post_market_order(
                account_id=client.account_id,
                instrument=instrument,
                units=units,
                stop_loss_on_fill=StopLossDetails(
                    price=stop_loss_price,
                    time_in_force="GTC"
                )
            )

            return response.order_fill_transaction
        except Exception as e:
            print(f"❌ Error implementing pip-based stop: {e}")
            return None

# Usage with 30-pip stop-loss
async def example_usage():
    fill = await implement_pip_based_stop_loss(
        account_id="101-001-1234567-001",
        instrument="GBP_USD",
        units=5000,
        pip_distance=30
    )
    return fill
```

---

## Percentage-Based Stop-Loss

### Account Risk Percentage

Limit risk to fixed percentage of account balance:

```python
import os
from decimal import Decimal
from typing import Any

from fivetwenty import AsyncClient, Environment
from fivetwenty.models import StopLossDetails


async def percentage_based_stop_loss(account_id: str, instrument: str,
                                   units: int, risk_percentage: Decimal = Decimal("0.02")) -> Any:
    """Implement stop-loss based on account risk percentage."""

    # Zero-config - automatically uses environment variables
    async with AsyncClient(
        token=os.environ.get("FIVETWENTY_OANDA_TOKEN", "demo-token"),
        environment=Environment.PRACTICE
    ) as client:
        try:
            # Get account balance
            account = await client.accounts.get_account(account_id)
            account_balance = Decimal(str(account.balance))
            max_loss = account_balance * risk_percentage

            print(f"💰 Account balance: ${account_balance:,.2f}")
            print(f"⚠️ Maximum risk: ${max_loss:.2f} ({risk_percentage:.1%})")

            # Get current pricing
            prices = await client.pricing.get_pricing(account_id, [instrument])
            current_price = prices[0]

            # Calculate pip value for position size
            pip_size = Decimal("0.01") if "JPY" in instrument else Decimal("0.0001")

            # Estimate pip value in account currency (simplified)
            # For EUR_USD with 10k units: 1 pip = $1
            pip_value_per_unit = Decimal(str(pip_size))
            total_pip_value = abs(units) * pip_value_per_unit

            # Calculate maximum pips to risk
            max_pips_to_risk = int(max_loss / total_pip_value)

            # Minimum stop distance (prevent too-tight stops)
            min_stop_pips = 10
            stop_distance_pips = max(max_pips_to_risk, min_stop_pips)

            print(f"📏 Stop distance: {stop_distance_pips} pips")

            # Calculate stop-loss price
            entry_price = current_price.asks[0].price if units > 0 else current_price.bids[0].price

            # Use function defined earlier in this module
            pip_size = Decimal("0.01") if "JPY" in instrument else Decimal("0.0001")
            pip_value = stop_distance_pips * pip_size
            stop_loss_price = entry_price - pip_value if units > 0 else entry_price + pip_value

            # Place order
            response = await client.orders.post_market_order(
                account_id=client.account_id,
                instrument=instrument,
                units=units,
                stop_loss_on_fill=StopLossDetails(
                    price=stop_loss_price,
                    time_in_force="GTC"
                )
            )

            if response.order_fill_transaction:
                fill = response.order_fill_transaction
                actual_risk = abs(Decimal(str(fill.price)) - stop_loss_price) * abs(units)
                print(f"✅ Order placed - Actual risk: ${actual_risk:.2f}")

        return response.order_fill_transaction

        except Exception as e:
            print(f"❌ Error with percentage-based stop: {e}")
            return None

# Risk 1.5% of account on this trade
async def example_usage():
    fill = await percentage_based_stop_loss(
        account_id="101-001-1234567-001",
        instrument="EUR_USD",
        units=15000,
        risk_percentage=Decimal("0.015")  # 1.5%
    )
    return fill
```

---

## Dynamic Stop-Loss Strategies

### Trailing Stop-Loss

Stop-loss that follows favorable price movement:

```python
from decimal import Decimal

from fivetwenty import AsyncClient


async def implement_trailing_stop_loss(account_id: str, instrument: str, units: int, trail_distance_pips: int = 50) -> Any:
    """Implement trailing stop-loss that moves with favorable price action."""

    # Zero-config - automatically uses environment variables
    async with AsyncClient() as client:
        try:
            # Calculate trailing distance in price terms
            pip_size = Decimal("0.01") if "JPY" in instrument else Decimal("0.0001")
            trail_distance = Decimal(str(trail_distance_pips)) * pip_size

            print(f"📈 Implementing trailing stop: {trail_distance_pips} pips")

            # Place initial market order with trailing stop
            response = await client.orders.post_market_order(
                account_id=client.account_id,
                instrument=instrument,
                units=units,
                trailing_stop_loss_on_fill={
                    "distance": str(trail_distance),
                    "time_in_force": "GTC"
                }
            )

            if response.order_fill_transaction:
                fill = response.order_fill_transaction
                print(f"✅ Order filled at {fill.price}")
                print(f"🔄 Trailing stop active: {trail_distance_pips} pips")

                # Get the created trade ID for monitoring
                trade_id = fill.trade_opened.trade_id if fill.trade_opened else None

                if trade_id:
                    # Check trade details to see trailing stop
                    trade = await client.trades.get_trade(account_id, trade_id)
                    if trade.trailing_stop_loss_order:
                        tsl_order = trade.trailing_stop_loss_order
                        print(f"🎯 Trailing stop order ID: {tsl_order.id}")
                        print(f"📏 Trail distance: {tsl_order.distance}")

                return trade_id

        print("❌ Order not filled")
        return None

        except Exception as e:
            print(f"❌ Error implementing trailing stop: {e}")
            return None

# Usage
async def main() -> None:
    trade_id = await implement_trailing_stop_loss(
        account_id="101-001-1234567-001",
        instrument="GBP_JPY",
        units=8000,
        trail_distance_pips=75
    )

# Run the example
# asyncio.run(main())
```

### ATR-Based Dynamic Stop-Loss

Stop-loss based on market volatility using Average True Range:

```python
import os
from decimal import Decimal
from typing import Any

import pandas as pd

from fivetwenty import AsyncClient, Environment
from fivetwenty.models import StopLossDetails


async def calculate_atr_stop_loss(account_id: str, instrument: str, units: int,
                                atr_multiplier: Decimal = Decimal("2.0"), atr_period: int = 14) -> Any:
    """Calculate stop-loss based on Average True Range volatility."""

    # Zero-config - automatically uses environment variables
    async with AsyncClient() as client:
        try:
            # Get historical data for ATR calculation
            candles_response = await client.instruments.get_instrument_candles(
                instrument=instrument,
                count=atr_period + 10,  # Extra candles for calculation
                granularity="H1"  # 1-hour candles
            )

            # Convert to DataFrame for ATR calculation
            data = []
            for candle in candles_response.candles:
                if candle.mid:
                    data.append({
                        'high': float(Decimal(str(candle.mid.h))),
                        'low': float(Decimal(str(candle.mid.l))),
                        'close': float(Decimal(str(candle.mid.c)))
                    })

            df = pd.DataFrame(data)

            # Calculate True Range
            df['prev_close'] = df['close'].shift(1)
            df['tr1'] = df['high'] - df['low']
            df['tr2'] = abs(df['high'] - df['prev_close'])
            df['tr3'] = abs(df['low'] - df['prev_close'])
            df['tr'] = df[['tr1', 'tr2', 'tr3']].max(axis=1)

            # Calculate ATR (Simple Moving Average of TR)
            current_atr = df['tr'].rolling(window=atr_period).mean().iloc[-1]
            current_price = df['close'].iloc[-1]

            print(f"📊 Current ATR: {current_atr:.5f}")
            print(f"💹 Current price: {current_price:.5f}")

            # Calculate stop-loss distance
            stop_distance = current_atr * atr_multiplier

            # Set stop-loss based on position direction
            if units > 0:  # Long position
                stop_loss_price = Decimal(str(current_price - stop_distance))
            else:  # Short position
                stop_loss_price = Decimal(str(current_price + stop_distance))

            print(f"🛡️ ATR-based stop: {stop_loss_price} ({stop_distance:.5f} distance)")

            # Place order with ATR-based stop
            response = await client.orders.post_market_order(
                account_id=client.account_id,
                instrument=instrument,
                units=units,
                stop_loss_on_fill=StopLossDetails(
                    price=stop_loss_price,
                    time_in_force="GTC"
                )
            )

            return response.order_fill_transaction

        except Exception as e:
            print(f"❌ Error calculating ATR stop-loss: {e}")
            return None

# Usage with 2x ATR stop-loss
async def main() -> None:
    _fill = await calculate_atr_stop_loss(
        account_id="101-001-1234567-001",
        instrument="USD_JPY",
        units=-12000,  # Short position
        atr_multiplier=2.5,
        atr_period=20
    )

# Run the example
# asyncio.run(main())
```

---

## Stop-Loss Management

### Modifying Existing Stop-Loss

Update stop-loss on existing positions:

```python
import os
from decimal import Decimal
from typing import Any

from fivetwenty import AsyncClient, Environment
from fivetwenty.models import StopLossDetails


async def modify_stop_loss(account_id: str, trade_id: str, new_stop_price: Decimal) -> Any:
    """Modify stop-loss on existing trade."""

    # Zero-config - automatically uses environment variables
    async with AsyncClient() as client:
        try:
            # Modify trade's stop-loss order
            response = await client.trades.put_trade_orders(
                account_id=client.account_id,
                trade_id=trade_id,
                stop_loss=StopLossDetails(
                    price=new_stop_price,
                    time_in_force="GTC"
                )
            )

            if response:
                print(f"✅ Stop-loss updated to {new_stop_price}")
                return True
            else:
                print("❌ Failed to update stop-loss")
                return False

        except Exception as e:
            print(f"❌ Error modifying stop-loss: {e}")
            return False

# Move stop-loss to break-even
async def main() -> None:
    await modify_stop_loss("101-001-1234567-001", "12345", Decimal("1.1000"))

# Run the example
# asyncio.run(main())
```

### Break-Even Stop-Loss

Move stop-loss to entry price after favorable movement:

```python
from decimal import Decimal

from fivetwenty import AsyncClient


async def move_to_breakeven(account_id: str, trade_id: str, trigger_pips: int = 20) -> Any:
    """Move stop-loss to break-even after price moves favorably."""

    # Zero-config - automatically uses environment variables
    async with AsyncClient() as client:
        try:
            # Get current trade details
            trade = await client.trades.get_trade(account_id, trade_id)
            entry_price = trade.price
            current_units = trade.current_units
            instrument = trade.instrument

            # Get current market price
            prices = await client.pricing.get_pricing(account_id, [instrument])
            current_price = prices[0]

            # Determine current market price for position
            if current_units > 0:  # Long position
                market_price = current_price.bid
            else:  # Short position
                market_price = current_price.ask

            # Calculate pip movement
            pip_size = Decimal("0.01") if "JPY" in instrument else Decimal("0.0001")

            if current_units > 0:  # Long position
                pip_movement = (Decimal(str(market_price)) - Decimal(str(entry_price))) / pip_size
            else:  # Short position
                pip_movement = (Decimal(str(entry_price)) - Decimal(str(market_price))) / pip_size

            print(f"📊 Current P/L: {pip_movement:.1f} pips")

            # Check if profitable enough to move to break-even
            if pip_movement >= trigger_pips:
                print(f"🎯 Moving stop-loss to break-even (entry: {entry_price})")

                # Move stop to break-even (entry price)
                success = await modify_stop_loss(account_id, trade_id, entry_price)

                if success:
                    print("✅ Stop-loss moved to break-even - Risk eliminated!")
                    return True
            else:
                print(f"⏳ Need {trigger_pips - pip_movement:.1f} more pips for break-even")
                return False

        except Exception as e:
            print(f"❌ Error moving to break-even: {e}")
            return False

# Move to break-even after 25 pips profit
async def main() -> None:
    await move_to_breakeven("101-001-1234567-001", "67890", trigger_pips=25)

# Run the example
# asyncio.run(main())
```

---

## Advanced Stop-Loss Patterns

### Tiered Stop-Loss Strategy

Partial position closure at multiple levels:

```python
from decimal import Decimal

from fivetwenty import AsyncClient


async def implement_tiered_stop_loss(account_id: str, instrument: str, units: int) -> Any:
    """Implement tiered stop-loss with multiple exit levels."""

    # Zero-config - automatically uses environment variables
    async with AsyncClient() as client:
        try:
            # Get current price
            prices = await client.pricing.get_pricing(account_id, [instrument])
            entry_price = prices[0].asks[0].price if units > 0 else prices[0].bids[0].price

            # Calculate multiple stop levels
            pip_size = Decimal("0.01") if "JPY" in instrument else Decimal("0.0001")

            if units > 0:  # Long position stops
                stop1 = entry_price - (20 * pip_size)  # Tight stop - 25% of position
                stop2 = entry_price - (40 * pip_size)  # Medium stop - 50% of position
                stop3 = entry_price - (80 * pip_size)  # Wide stop - remaining 25%
            else:  # Short position stops
                stop1 = entry_price + (20 * pip_size)
                stop2 = entry_price + (40 * pip_size)
                stop3 = entry_price + (80 * pip_size)

            print(f"🎯 Tiered stops: {stop1} | {stop2} | {stop3}")

            # Place main position
            main_response = await client.orders.post_market_order(
                account_id=client.account_id,
                instrument=instrument,
                units=units
            )

            if main_response.order_fill_transaction:
                print(f"✅ Main position filled at {main_response.order_fill_transaction.price}")

                # Place tiered stop-loss orders as separate stop orders
                position_size = abs(units)

                # First tier stop (25% of position)
                await client.orders.post_stop_order(
                    account_id=client.account_id,
                    instrument=instrument,
                    units=int(-0.25 * position_size) if units > 0 else int(0.25 * position_size),
                    price=stop1
                )

                # Second tier stop (50% of position)
                await client.orders.post_stop_order(
                    account_id=client.account_id,
                    instrument=instrument,
                    units=int(-0.50 * position_size) if units > 0 else int(0.50 * position_size),
                    price=stop2
                )

                # Third tier stop (remaining 25%)
                await client.orders.post_stop_order(
                    account_id=client.account_id,
                    instrument=instrument,
                    units=int(-0.25 * position_size) if units > 0 else int(0.25 * position_size),
                    price=stop3
                )

                print("✅ Tiered stop-loss orders placed")
                return True
            else:
                print("❌ Main position not filled")
                return False

        except Exception as e:
            print(f"❌ Error implementing tiered stops: {e}")
            return False

# Implement 3-tier stop strategy
async def main() -> None:
    await implement_tiered_stop_loss(
        account_id="101-001-1234567-001",
        instrument="EUR_GBP",
        units=20000
    )

# Run the example
# asyncio.run(main())
```

---

## Stop-Loss Monitoring and Alerts

### Real-Time Stop-Loss Monitoring

Monitor positions and stop-loss orders:

```python
import asyncio
from decimal import Decimal

from fivetwenty import AsyncClient, Environment

async def monitor_stop_loss_positions(account_id: str, check_interval: int = 30) -> None:
    """Monitor all positions with stop-loss orders."""

    async with AsyncClient(token="your-token", environment=Environment.PRACTICE) as client:
        print("🔍 Starting stop-loss monitoring...")

        try:
            while True:
                # Get all open trades
                trades = await client.trades.get_open_trades(account_id)

                print(f"\n📊 Monitoring {len(trades)} open positions:")

                for trade in trades:
                    print(f"\n🔹 Trade {trade.id} ({trade.instrument}):")
                    print(f"   Units: {trade.current_units}")
                    print(f"   Entry: {trade.price}")
                    print(f"   Unrealized P/L: {trade.unrealized_pl}")

                    # Check stop-loss order
                    if trade.stop_loss_order:
                        sl_order = trade.stop_loss_order
                        print(f"   🛡️ Stop-Loss: {sl_order.price} (ID: {sl_order.id})")

                        # Calculate distance to stop
                        current_price = Decimal(str(trade.price))  # Simplified - should get current market
                        stop_price = Decimal(str(sl_order.price))
                        distance = abs(current_price - stop_price)

                        if distance < 0.0050:  # Within 50 pips (adjust for pair)
                            print(f"   ⚠️ CLOSE TO STOP: {distance:.5f} away")
                    else:
                        print(f"   ⚠️ NO STOP-LOSS PROTECTION!")

                    # Check trailing stop
                    if trade.trailing_stop_loss_order:
                        tsl_order = trade.trailing_stop_loss_order
                        print(f"   🔄 Trailing Stop: {tsl_order.distance} distance")

                # Wait before next check
                await asyncio.sleep(check_interval)

        except KeyboardInterrupt:
            print("\n✅ Monitoring stopped")
        except Exception as e:
            print(f"❌ Monitoring error: {e}")

# Start monitoring (run in background)
# await monitor_stop_loss_positions("101-001-1234567-001", check_interval=60)
```

---

## Best Practices and Guidelines

### Stop-Loss Rules

```python
from decimal import Decimal

class StopLossRules:
    """Best practices for stop-loss implementation."""

    @staticmethod
    def validate_stop_loss_setup(entry_price: Decimal, stop_price: Decimal,
                               units: int, instrument: str) -> dict:
        """Validate stop-loss configuration."""

        results = {
            'valid': True,
            'warnings': [],
            'errors': []
        }

        # Calculate risk
        pip_size = Decimal("0.01") if "JPY" in instrument else Decimal("0.0001")
        risk_distance = abs(Decimal(str(entry_price)) - Decimal(str(stop_price)))
        risk_pips = risk_distance / pip_size

        # Rule 1: Minimum stop distance
        if risk_pips < 10:
            results['errors'].append(f"Stop too tight: {risk_pips:.1f} pips (min 10)")
            results['valid'] = False

        # Rule 2: Maximum stop distance
        if risk_pips > 200:
            results['warnings'].append(f"Stop very wide: {risk_pips:.1f} pips")

        # Rule 3: Stop direction validation
        if units > 0 and stop_price >= entry_price:
            results['errors'].append("Long position stop must be below entry")
            results['valid'] = False

        if units < 0 and stop_price <= entry_price:
            results['errors'].append("Short position stop must be above entry")
            results['valid'] = False

        # Rule 4: Reasonable risk amount
        position_value = abs(units) * Decimal(str(entry_price))
        risk_amount = abs(units) * risk_distance
        risk_percentage = (risk_amount / position_value) * 100

        if risk_percentage > 10:
            results['warnings'].append(f"High risk: {risk_percentage:.1f}% of position")

        results['risk_pips'] = risk_pips
        results['risk_amount'] = risk_amount
        results['risk_percentage'] = risk_percentage

        return results

    @staticmethod
    def print_validation_results(results: dict):
        """Print validation results."""

        print(f"\n🔍 Stop-Loss Validation:")
        print(f"   Risk: {results['risk_pips']:.1f} pips (${results['risk_amount']:.2f})")
        print(f"   Risk %: {results['risk_percentage']:.2f}% of position value")

        if results['errors']:
            print(f"   ❌ Errors:")
            for error in results['errors']:
                print(f"      • {error}")

        if results['warnings']:
            print(f"   ⚠️ Warnings:")
            for warning in results['warnings']:
                print(f"      • {warning}")

        if results['valid']:
            print(f"   ✅ Configuration valid")
        else:
            print(f"   ❌ Configuration invalid")

# Usage
validation = StopLossRules.validate_stop_loss_setup(
    entry_price=Decimal("1.1000"),
    stop_price=Decimal("1.0950"),
    units=10000,
    instrument="EUR_USD"
)
StopLossRules.print_validation_results(validation)
```

---

## Troubleshooting

### Common Stop-Loss Issues

```python
from decimal import Decimal
from typing import Any
from fivetwenty import AsyncClient, Environment

async def troubleshoot_stop_loss_issues(account_id: str) -> dict[str, Any] | None:
    """Diagnose common stop-loss problems."""

    async with AsyncClient(token="your-token", environment=Environment.PRACTICE) as client:
        print("🔧 Diagnosing stop-loss issues...\n")

        try:
            # Check account margin
            account = await client.accounts.get_account(account_id)
            margin_utilization = Decimal(str(account.margin_used)) / Decimal(str(account.balance))

            if margin_utilization > 0.8:
                print("⚠️ High margin usage - stops may trigger early")

            # Check open trades
            trades = await client.trades.get_open_trades(account_id)

            for trade in trades:
                print(f"🔍 Trade {trade.id}:")

                # Check for missing stops
                if not trade.stop_loss_order:
                    print("   ❌ Missing stop-loss protection")

                # Check for wide stops
                if trade.stop_loss_order:
                    entry = Decimal(str(trade.price))
                    stop = Decimal(str(trade.stop_loss_order.price))
                    risk = abs(entry - stop) / 0.0001  # Assuming non-JPY pair

                    if risk > 100:
                        print(f"   ⚠️ Very wide stop: {risk:.0f} pips")

                # Check unrealized P/L vs stop distance
                if float(trade.unrealized_pl) < -100:  # Significant loss
                    print(f"   📉 Large unrealized loss: {trade.unrealized_pl}")

            # Check pending stop orders
            orders = await client.orders.get_pending_orders(account_id)
            stop_orders = [o for o in orders if o.type == "STOP"]

            print(f"\n📋 Found {len(stop_orders)} pending stop orders")

            return {
                'margin_utilization': margin_utilization,
                'trades_without_stops': len([t for t in trades if not t.stop_loss_order]),
                'pending_stops': len(stop_orders)
            }

        except Exception as e:
            print(f"❌ Diagnostic error: {e}")
            return None

# Run diagnostics
async def main() -> None:
    diagnostics = await troubleshoot_stop_loss_issues("101-001-1234567-001")

# Run the example
# asyncio.run(main())
```

---

## Emergency Stop-Loss Procedures

### Emergency Position Exit

```python
from typing import Any
from fivetwenty import AsyncClient

async def emergency_stop_all_positions(account_id: str, reason: str = "Emergency stop") -> list[dict[str, Any]]:
    """Emergency closure of all positions regardless of stop-loss orders."""

    # Zero-config - automatically uses environment variables
    async with AsyncClient() as client:
        print(f"🚨 EMERGENCY STOP: {reason}")

        try:
            # Get all open positions
            positions = await client.positions.get_open_positions(account_id)

            if not positions:
                print("✅ No positions to close")
                return []

            results = []

            for position in positions:
                try:
                    # Close entire position for this instrument
                    response = await client.positions.close_position(
                        account_id=client.account_id,
                        instrument=position.instrument,
                        long_units="ALL",
                        short_units="ALL"
                    )

                    if response:
                        print(f"✅ Emergency closed: {position.instrument}")
                        results.append({'instrument': position.instrument, 'success': True})
                    else:
                        print(f"❌ Failed to close: {position.instrument}")
                        results.append({'instrument': position.instrument, 'success': False})

                except Exception as e:
                    print(f"❌ Error closing {position.instrument}: {e}")
                    results.append({'instrument': position.instrument, 'success': False, 'error': str(e)})

            successful_closes = sum(1 for r in results if r['success'])
            print(f"\n🚨 Emergency stop complete: {successful_closes}/{len(results)} positions closed")

            return results

        except Exception as e:
            print(f"❌ Emergency stop failed: {e}")
            return []

# Emergency stop all trading
# results = await emergency_stop_all_positions("101-001-1234567-001", "Market crash detected")
```

**Task Complete**: Stop-loss strategies implementation guide provides comprehensive risk management tools for all trading scenarios with FiveTwenty.