# Risk Management Tutorial

This tutorial teaches you how to implement comprehensive risk management strategies to protect your trading capital. Risk management is the most critical aspect of successful trading.

## Prerequisites

- Completed [Basic Trading Tutorial](basic-trading.md)
- Understanding of position sizing and leverage
- FiveTwenty setup with practice account

## Learning Objectives

By the end of this tutorial, you will:

- ✅ Master position sizing calculations
- ✅ Implement stop-loss and take-profit strategies
- ✅ Build portfolio risk monitoring systems
- ✅ Create automated risk controls
- ✅ Develop comprehensive risk frameworks

---

## 1. Risk Management Fundamentals

### The 3 Pillars of Risk Management

1. **Position Sizing**: How much to risk per trade
2. **Stop Losses**: Limiting downside on individual trades
3. **Portfolio Management**: Managing overall exposure

### Key Risk Metrics

- **Risk per Trade**: Percentage of account risked on single trade
- **Win Rate**: Percentage of profitable trades
- **Risk/Reward Ratio**: Average profit vs average loss
- **Maximum Drawdown**: Largest peak-to-trough decline
- **Sharpe Ratio**: Risk-adjusted returns

### The 1% Rule

**Never risk more than 1-2% of your account on a single trade.**

```python
from decimal import Decimal

# Example: $10,000 account with 1% risk
account_balance = 10000
risk_per_trade = account_balance * Decimal("0.01")  # $100 maximum risk
```

---

## 2. Position Sizing Strategies

### Fixed Dollar Amount

```python
import asyncio
from decimal import Decimal
from datetime import datetime

from fivetwenty import AsyncClient, Environment
from fivetwenty.exceptions import FiveTwentyError

# Configuration
TOKEN = "your-api-token-here"
ENVIRONMENT = Environment.PRACTICE

class PositionSizer:
    """Advanced position sizing calculator."""

    def __init__(self, account_balance: float, max_risk_percent: float = 1.0):
        self.account_balance = account_balance
        self.max_risk_percent = max_risk_percent
        self.max_risk_amount = account_balance * (max_risk_percent / 100)

    def calculate_position_size(self, entry_price: float, stop_loss: float,
                              instrument: str) -> int:
        """Calculate position size based on risk management rules."""

        # Calculate risk per unit
        risk_per_unit = abs(entry_price - stop_loss)

        if risk_per_unit == 0:
            print("⚠️ Warning: Entry price equals stop loss")
            return 0

        # Calculate position size
        position_size = int(self.max_risk_amount / risk_per_unit)

        # Get pip value for display
        pip_value = 0.01 if instrument.endswith('JPY') else 0.0001
        risk_pips = risk_per_unit / pip_value

        print(f"📊 Position Size Calculation:")
        print(f"   Max Risk: ${self.max_risk_amount:.2f} ({self.max_risk_percent}%)")
        print(f"   Entry Price: {entry_price:.5f}")
        print(f"   Stop Loss: {stop_loss:.5f}")
        print(f"   Risk per Unit: {risk_per_unit:.5f} ({risk_pips:.1f} pips)")
        print(f"   Position Size: {position_size:,} units")

        return position_size

    def validate_position_size(self, position_size: int, entry_price: float,
                             stop_loss: float) -> bool:
        """Validate that position size meets risk criteria."""

        risk_amount = abs(position_size) * abs(entry_price - stop_loss)
        risk_percent = (risk_amount / self.account_balance) * 100

        print(f"📋 Position Validation:")
        print(f"   Position Size: {abs(position_size):,} units")
        print(f"   Risk Amount: ${risk_amount:.2f}")
        print(f"   Risk Percentage: {risk_percent:.2f}%")

        if risk_percent > self.max_risk_percent:
            print(f"❌ Position size exceeds risk limit!")
            return False

        print(f"✅ Position size within risk limits")
        return True

# Example usage
async def demo_position_sizing(account_id: str):
    """Demonstrate position sizing calculations."""

    if not account_id:
        print("❌ No account ID")
        return

    async with AsyncClient(token=TOKEN, environment=ENVIRONMENT) as client:
        # Get account balance
        account = await client.accounts.get(account_id)
        balance = float(account.balance)

        # Create position sizer
        sizer = PositionSizer(balance, max_risk_percent=1.0)

        # Example trade setup
        instrument = "EUR_USD"
        entry_price=Decimal("1.1000")
        stop_loss=Decimal("1.0950")  # 50 pip stop

        # Calculate optimal position size
        position_size = sizer.calculate_position_size(entry_price, stop_loss, instrument)

        # Validate the calculation
        is_valid = sizer.validate_position_size(position_size, entry_price, stop_loss)

        return position_size if is_valid else 0
```

### Volatility-Based Position Sizing

```python
from decimal import Decimal

from fivetwenty import AsyncClient, Environment

import numpy as np
from fivetwenty.models import CandlestickGranularity

class VolatilityPositionSizer(PositionSizer):
    """Position sizing based on market volatility (ATR)."""

    async def calculate_atr_position_size(self, client: AsyncClient, instrument: str,
                                        atr_multiplier: float = 2.0) -> int:
        """Calculate position size based on Average True Range."""

        try:
            # Get historical data for ATR calculation
            candles = await client.instruments.candles(
                instrument=instrument,
                count=50,
                granularity=CandlestickGranularity.H4
            )

            # Calculate ATR
            true_ranges = []
            for i in range(1, len(candles.candles)):
                curr = candles.candles[i]
                prev = candles.candles[i-1]

                if curr.mid and prev.mid:
                    high = float(curr.mid.h)
                    low = float(curr.mid.l)
                    prev_close = float(prev.mid.c)

                    tr1 = high - low
                    tr2 = abs(high - prev_close)
                    tr3 = abs(low - prev_close)

                    true_range = max(tr1, tr2, tr3)
                    true_ranges.append(true_range)

            # Calculate 14-period ATR
            atr = sum(true_ranges[-14:]) / 14 if len(true_ranges) >= 14 else 0

            if atr == 0:
                print("❌ Could not calculate ATR")
                return 0

            # Get current price
            current_price = float(candles.candles[-1].mid.c)

            # Calculate stop loss based on ATR
            stop_distance = atr * atr_multiplier

            # Calculate position size
            position_size = int(self.max_risk_amount / stop_distance)

            pip_value = 0.01 if instrument.endswith('JPY') else 0.0001
            stop_pips = stop_distance / pip_value

            print(f"📊 ATR-Based Position Sizing:")
            print(f"   Current Price: {current_price:.5f}")
            print(f"   ATR: {atr:.5f}")
            print(f"   Stop Distance: {stop_distance:.5f} ({stop_pips:.1f} pips)")
            print(f"   Position Size: {position_size:,} units")

            return position_size

        except Exception as e:
            print(f"❌ ATR calculation error: {e}")
            return 0

# Example ATR position sizing
async def demo_atr_position_sizing(account_id: str):
    """Demonstrate ATR-based position sizing."""

    if not account_id:
        return

    async with AsyncClient(token=TOKEN, environment=ENVIRONMENT) as client:
        account = await client.accounts.get(account_id)
        balance = float(account.balance)

        sizer = VolatilityPositionSizer(balance, max_risk_percent=1.5)

        # Calculate position size based on volatility
        position_size = await sizer.calculate_atr_position_size(
            client, "EUR_USD", atr_multiplier=Decimal("2.0000")
        )

        return position_size
```

---

## 3. Stop Loss Strategies

### Fixed Pip Stop Loss

```python
from fivetwenty import AsyncClient, Environment
from fivetwenty.exceptions import FiveTwentyError, FiveTwentyErrorCode

async def place_order_with_fixed_stop(account_id: str, instrument: str, units: int,
                                     stop_pips: float, take_profit_pips: float = None):
    """Place order with fixed pip-based stop loss."""

    async with AsyncClient(token=TOKEN, environment=ENVIRONMENT) as client:
        try:
            # Get current price
            prices = await client.pricing.get(account_id=account_id, instruments=[instrument])

            if units > 0:  # Buy order
                entry_price = float(prices[0].asks[0].price)
                pip_value = 0.01 if instrument.endswith('JPY') else 0.0001
                stop_loss_price = entry_price - (stop_pips * pip_value)
                take_profit_price = entry_price + (take_profit_pips * pip_value) if take_profit_pips else None
            else:  # Sell order
                entry_price = float(prices[0].bids[0].price)
                pip_value = 0.01 if instrument.endswith('JPY') else 0.0001
                stop_loss_price = entry_price + (stop_pips * pip_value)
                take_profit_price = entry_price - (take_profit_pips * pip_value) if take_profit_pips else None

            print(f"🎯 Fixed Stop Order:")
            print(f"   Entry: ~{entry_price:.5f}")
            print(f"   Stop: {stop_loss_price:.5f} ({stop_pips} pips)")
            if take_profit_price:
                print(f"   Target: {take_profit_price:.5f} ({take_profit_pips} pips)")

            # Place order with stops
            order_params = {
                'account_id': account_id,
                'instrument': instrument,
                'units': units,
                'stop_loss_on_fill': {'price': f"{stop_loss_price:.5f}"}
            }

            if take_profit_price:
                order_params['take_profit_on_fill'] = {'price': f"{take_profit_price:.5f}"}

            response = await client.orders.post_market_order(**order_params)

            if response.order_fill_transaction:
                fill = response.order_fill_transaction
                print(f"✅ Order executed with protective stops!")
                print(f"   Fill Price: {fill.price}")
                print(f"   Trade ID: {fill.trade_opened.trade_id if fill.trade_opened else 'N/A'}")

                return fill

        except FiveTwentyError as e:
            print(f"❌ Stop order error: {e.message}")
            return None
```

### Percentage-Based Stop Loss

```python
from fivetwenty import AsyncClient, Environment
from fivetwenty.exceptions import FiveTwentyError, FiveTwentyErrorCode

async def place_order_with_percentage_stop(account_id: str, instrument: str, units: int,
                                          stop_percentage: float = 1.0):
    """Place order with percentage-based stop loss."""

    async with AsyncClient(token=TOKEN, environment=ENVIRONMENT) as client:
        try:
            # Get current price
            prices = await client.pricing.get(account_id=account_id, instruments=[instrument])

            if units > 0:  # Buy order
                entry_price = float(prices[0].asks[0].price)
                stop_loss_price = entry_price * (1 - stop_percentage / 100)
            else:  # Sell order
                entry_price = float(prices[0].bids[0].price)
                stop_loss_price = entry_price * (1 + stop_percentage / 100)

            stop_distance = abs(entry_price - stop_loss_price)
            pip_value = 0.01 if instrument.endswith('JPY') else 0.0001
            stop_pips = stop_distance / pip_value

            print(f"📊 Percentage Stop Order:")
            print(f"   Entry: ~{entry_price:.5f}")
            print(f"   Stop: {stop_loss_price:.5f} ({stop_percentage}% / {stop_pips:.1f} pips)")

            response = await client.orders.post_market_order(
                account_id=account_id,
                instrument=instrument,
                units=units,
                stop_loss_on_fill={'price': f"{stop_loss_price:.5f}"}
            )

            if response.order_fill_transaction:
                fill = response.order_fill_transaction
                print(f"✅ Percentage stop order executed!")
                return fill

        except FiveTwentyError as e:
            print(f"❌ Percentage stop error: {e.message}")
            return None
```

### Trailing Stop Implementation

```python
from fivetwenty import AsyncClient, Environment

class TrailingStopManager:
    """Advanced trailing stop management system."""

    def __init__(self, client: AsyncClient, account_id: str):
        self.client = client
        self.account_id = account_id
        self.active_trails = {}

    async def set_trailing_stop(self, trade_id: str, trail_distance_pips: float,
                               breakeven_pips: float = None):
        """Set trailing stop with optional break-even protection."""

        try:
            trade = await self.client.trades.get(self.account_id, trade_id)

            if not trade:
                print(f"❌ Trade {trade_id} not found")
                return False

            entry_price = float(trade.price)
            current_units = int(trade.current_units)
            instrument = trade.instrument

            # Store trailing parameters
            self.active_trails[trade_id] = {
                'instrument': instrument,
                'entry_price': entry_price,
                'units': current_units,
                'trail_distance_pips': trail_distance_pips,
                'breakeven_pips': breakeven_pips,
                'best_price': entry_price,
                'in_breakeven': False
            }

            print(f"📈 Trailing Stop Activated:")
            print(f"   Trade ID: {trade_id}")
            print(f"   Trail Distance: {trail_distance_pips} pips")
            if breakeven_pips:
                print(f"   Break-even at: {breakeven_pips} pips profit")

            return True

        except Exception as e:
            print(f"❌ Trailing stop error: {e}")
            return False

    async def update_trailing_stops(self):
        """Update all active trailing stops."""

        for trade_id, trail_info in list(self.active_trails.items()):
            try:
                # Get current price
                instrument = trail_info['instrument']
                prices = await self.client.pricing.get(
                    account_id=self.account_id,
                    instruments=[instrument]
                )

                if trail_info['units'] > 0:  # Long position
                    current_price = float(prices[0].bids[0].price)
                else:  # Short position
                    current_price = float(prices[0].asks[0].price)

                # Update best price
                if trail_info['units'] > 0:
                    if current_price > trail_info['best_price']:
                        trail_info['best_price'] = current_price
                else:
                    if current_price < trail_info['best_price']:
                        trail_info['best_price'] = current_price

                # Calculate new stop level
                pip_value = 0.01 if instrument.endswith('JPY') else 0.0001
                trail_distance = trail_info['trail_distance_pips'] * pip_value

                if trail_info['units'] > 0:  # Long position
                    new_stop = trail_info['best_price'] - trail_distance

                    # Check break-even condition
                    if (trail_info['breakeven_pips'] and
                        not trail_info['in_breakeven'] and
                        current_price >= trail_info['entry_price'] + (trail_info['breakeven_pips'] * pip_value)):

                        new_stop = trail_info['entry_price'] + (5 * pip_value)  # 5 pip buffer
                        trail_info['in_breakeven'] = True
                        print(f"🛡️ Trade {trade_id} moved to break-even protection")

                else:  # Short position
                    new_stop = trail_info['best_price'] + trail_distance

                    if (trail_info['breakeven_pips'] and
                        not trail_info['in_breakeven'] and
                        current_price <= trail_info['entry_price'] - (trail_info['breakeven_pips'] * pip_value)):

                        new_stop = trail_info['entry_price'] - (5 * pip_value)
                        trail_info['in_breakeven'] = True
                        print(f"🛡️ Trade {trade_id} moved to break-even protection")

                # Update stop loss if beneficial
                trade = await self.client.trades.get(self.account_id, trade_id)

                if not trade:
                    # Trade closed - remove from tracking
                    del self.active_trails[trade_id]
                    continue

                if trade.stop_loss_order:
                    current_stop = float(trade.stop_loss_order.price)

                    # Only update if new stop is better
                    should_update = False
                    if trail_info['units'] > 0 and new_stop > current_stop:
                        should_update = True
                    elif trail_info['units'] < 0 and new_stop < current_stop:
                        should_update = True

                    if should_update:
                        await self.client.trades.update(
                            account_id=self.account_id,
                            trade_id=trade_id,
                            stop_loss={'price': f"{new_stop:.5f}"}
                        )

                        print(f"📈 Trail updated for {trade_id}: {current_stop:.5f} → {new_stop:.5f}")

            except Exception as e:
                print(f"❌ Error updating trail for {trade_id}: {e}")

    async def monitor_trailing_stops(self, update_interval: int = 30):
        """Continuously monitor and update trailing stops."""

        print(f"🔄 Starting trailing stop monitoring (interval: {update_interval}s)")

        while self.active_trails:
            await self.update_trailing_stops()
            await asyncio.sleep(update_interval)

        print(f"🛑 No more active trailing stops - monitoring stopped")

# Demo trailing stops
async def demo_trailing_stops(account_id: str):
    """Demonstrate trailing stop functionality."""

    if not account_id:
        return

    async with AsyncClient(token=TOKEN, environment=ENVIRONMENT) as client:
        manager = TrailingStopManager(client, account_id)

        # Note: This requires an existing trade
        # In practice, you'd get the trade_id from a previous order
        print("💡 Trailing stop manager created")
        print("Use manager.set_trailing_stop(trade_id, trail_pips) to activate")

        return manager
```

---

## 4. Portfolio Risk Management

### Risk Monitoring Dashboard

```python
from decimal import Decimal

from fivetwenty import AsyncClient, Environment

class RiskMonitor:
    """Comprehensive portfolio risk monitoring system."""

    def __init__(self, client: AsyncClient, account_id: str):
        self.client = client
        self.account_id = account_id

        # Risk limits
        self.max_portfolio_risk = 0.10      # 10% max portfolio risk
        self.max_single_instrument = 0.05   # 5% max per instrument
        self.max_correlation_risk = 0.15    # 15% max correlated risk
        self.max_daily_loss = Decimal("0.05")          # 5% max daily loss

    async def calculate_portfolio_risk(self) -> dict:
        """Calculate comprehensive portfolio risk metrics."""

        try:
            # Get account info
            account = await self.client.accounts.get(self.account_id)
            account_balance = float(account.balance)

            # Get open positions
            positions = await self.client.positions.list_open(self.account_id)

            risk_summary = {
                'account_balance': account_balance,
                'total_exposure': 0,
                'total_unrealized_pl': 0,
                'instrument_risks': {},
                'correlation_groups': {},
                'risk_percentage': 0,
                'within_limits': True,
                'warnings': []
            }

            total_risk = 0

            for position in positions:
                instrument = position.instrument

                # Calculate position risk
                long_units = int(position.long.units) if position.long.units != "0" else 0
                short_units = int(position.short.units) if position.short.units != "0" else 0

                long_pl = float(position.long.unrealized_pl) if position.long.unrealized_pl else 0
                short_pl = float(position.short.unrealized_pl) if position.short.unrealized_pl else 0

                total_unrealized_pl = long_pl + short_pl
                net_units = long_units + short_units

                # Estimate risk (simplified - based on current unrealized P/L)
                position_risk = abs(total_unrealized_pl) if total_unrealized_pl < 0 else 0
                risk_percentage = (position_risk / account_balance) * 100

                risk_summary['instrument_risks'][instrument] = {
                    'net_units': net_units,
                    'unrealized_pl': total_unrealized_pl,
                    'risk_amount': position_risk,
                    'risk_percentage': risk_percentage
                }

                total_risk += position_risk
                risk_summary['total_unrealized_pl'] += total_unrealized_pl
                risk_summary['total_exposure'] += abs(net_units)

            # Calculate total portfolio risk
            risk_summary['risk_percentage'] = (total_risk / account_balance) * 100

            # Check limits
            if risk_summary['risk_percentage'] > self.max_portfolio_risk * 100:
                risk_summary['within_limits'] = False
                risk_summary['warnings'].append(
                    f"Portfolio risk ({risk_summary['risk_percentage']:.1f}%) exceeds limit"
                )

            # Check individual instrument limits
            for instrument, risk_data in risk_summary['instrument_risks'].items():
                if risk_data['risk_percentage'] > self.max_single_instrument * 100:
                    risk_summary['warnings'].append(
                        f"{instrument} risk ({risk_data['risk_percentage']:.1f}%) exceeds instrument limit"
                    )

            return risk_summary

        except Exception as e:
            print(f"❌ Risk calculation error: {e}")
            return {'error': str(e)}

    async def check_correlation_risk(self) -> dict:
        """Check for excessive correlation risk."""

        # Simplified correlation groups (in practice, use historical correlation data)
        correlation_groups = {
            'EUR_BASKET': ['EUR_USD', 'EUR_GBP', 'EUR_JPY', 'EUR_CHF'],
            'USD_BASKET': ['EUR_USD', 'GBP_USD', 'USD_JPY', 'USD_CHF'],
            'COMMODITY_CURRENCIES': ['AUD_USD', 'NZD_USD', 'USD_CAD'],
            'SAFE_HAVENS': ['USD_JPY', 'USD_CHF', 'XAU_USD']
        }

        try:
            positions = await self.client.positions.list_open(self.account_id)
            account = await self.client.accounts.get(self.account_id)
            account_balance = float(account.balance)

            correlation_risks = {}

            for group_name, instruments in correlation_groups.items():
                group_risk = 0
                group_exposure = 0

                for position in positions:
                    if position.instrument in instruments:
                        # Calculate position exposure
                        long_units = int(position.long.units) if position.long.units != "0" else 0
                        short_units = int(position.short.units) if position.short.units != "0" else 0
                        net_units = long_units + short_units

                        # Estimate position value (simplified)
                        group_exposure += abs(net_units)

                        # Add unrealized loss as risk
                        unrealized_pl = float(position.long.unrealized_pl or 0) + float(position.short.unrealized_pl or 0)
                        if unrealized_pl < 0:
                            group_risk += abs(unrealized_pl)

                if group_risk > 0:
                    risk_percentage = (group_risk / account_balance) * 100
                    correlation_risks[group_name] = {
                        'risk_amount': group_risk,
                        'risk_percentage': risk_percentage,
                        'exposure': group_exposure,
                        'instruments': [pos.instrument for pos in positions if pos.instrument in instruments]
                    }

            return correlation_risks

        except Exception as e:
            print(f"❌ Correlation risk error: {e}")
            return {}

    async def generate_risk_report(self) -> None:
        """Generate comprehensive risk report."""

        print("🏛️ PORTFOLIO RISK REPORT")
        print("=" * 50)

        # Portfolio risk
        portfolio_risk = await self.calculate_portfolio_risk()

        if 'error' in portfolio_risk:
            print(f"❌ Error generating report: {portfolio_risk['error']}")
            return

        print(f"\n💰 Account Overview:")
        print(f"   Balance: ${portfolio_risk['account_balance']:,.2f}")
        print(f"   Total Unrealized P/L: ${portfolio_risk['total_unrealized_pl']:+,.2f}")
        print(f"   Portfolio Risk: {portfolio_risk['risk_percentage']:.2f}%")
        print(f"   Risk Status: {'✅ OK' if portfolio_risk['within_limits'] else '🚨 EXCEEDED'}")

        # Individual instrument risks
        if portfolio_risk['instrument_risks']:
            print(f"\n📊 Instrument Risk Breakdown:")
            for instrument, risk_data in portfolio_risk['instrument_risks'].items():
                status = "🟢" if risk_data['unrealized_pl'] >= 0 else "🔴"
                print(f"   {instrument}: {risk_data['net_units']:+,} units, "
                      f"P/L: ${risk_data['unrealized_pl']:+.2f}, "
                      f"Risk: {risk_data['risk_percentage']:.2f}% {status}")

        # Correlation risks
        correlation_risks = await self.check_correlation_risk()
        if correlation_risks:
            print(f"\n🔗 Correlation Risk Analysis:")
            for group, risk_data in correlation_risks.items():
                print(f"   {group}: {risk_data['risk_percentage']:.2f}% risk")
                print(f"     Instruments: {', '.join(risk_data['instruments'])}")

        # Risk warnings
        if portfolio_risk['warnings']:
            print(f"\n⚠️ Risk Warnings:")
            for warning in portfolio_risk['warnings']:
                print(f"   - {warning}")

        # Risk limits summary
        print(f"\n📋 Risk Limits:")
        print(f"   Max Portfolio Risk: {self.max_portfolio_risk * 100:.1f}%")
        print(f"   Max Per Instrument: {self.max_single_instrument * 100:.1f}%")
        print(f"   Max Correlation Risk: {self.max_correlation_risk * 100:.1f}%")
        print(f"   Max Daily Loss: {self.max_daily_loss * 100:.1f}%")

# Demo risk monitoring
async def demo_risk_monitoring(account_id: str):
    """Demonstrate risk monitoring system."""

    if not account_id:
        return

    async with AsyncClient(token=TOKEN, environment=ENVIRONMENT) as client:
        monitor = RiskMonitor(client, account_id)

        # Generate risk report
        await monitor.generate_risk_report()

        return monitor
```

---

## 5. Automated Risk Controls

### Circuit Breaker System

```python
from decimal import Decimal

from fivetwenty import AsyncClient, Environment

class CircuitBreaker:
    """Automated trading halt system for risk protection."""

    def __init__(self, client: AsyncClient, account_id: str):
        self.client = client
        self.account_id = account_id
        self.trading_halted = False
        self.halt_reasons = []

        # Circuit breaker thresholds
        self.max_daily_loss_percent = Decimal("5.0")
        self.max_consecutive_losses = 5
        self.max_drawdown_percent = 15.0
        self.max_open_positions = 10

        # Tracking
        self.daily_start_balance = None
        self.consecutive_losses = 0
        self.peak_balance = None

    async def initialize_daily_tracking(self):
        """Initialize daily tracking parameters."""

        try:
            account = await self.client.accounts.get(self.account_id)
            current_balance = float(account.nav)

            if self.daily_start_balance is None:
                self.daily_start_balance = current_balance

            if self.peak_balance is None or current_balance > self.peak_balance:
                self.peak_balance = current_balance

            print(f"📊 Risk Tracking Initialized:")
            print(f"   Daily Start: ${self.daily_start_balance:,.2f}")
            print(f"   Peak Balance: ${self.peak_balance:,.2f}")
            print(f"   Current: ${current_balance:,.2f}")

        except Exception as e:
            print(f"❌ Tracking initialization error: {e}")

    async def check_circuit_breakers(self) -> bool:
        """Check all circuit breaker conditions."""

        try:
            account = await self.client.accounts.get(self.account_id)
            current_balance = float(account.nav)

            # Check daily loss limit
            if self.daily_start_balance:
                daily_loss_percent = ((self.daily_start_balance - current_balance) /
                                    self.daily_start_balance) * 100

                if daily_loss_percent > self.max_daily_loss_percent:
                    self.halt_trading(f"Daily loss limit exceeded: {daily_loss_percent:.2f}%")
                    return True

            # Check maximum drawdown
            if self.peak_balance:
                drawdown_percent = ((self.peak_balance - current_balance) /
                                  self.peak_balance) * 100

                if drawdown_percent > self.max_drawdown_percent:
                    self.halt_trading(f"Maximum drawdown exceeded: {drawdown_percent:.2f}%")
                    return True

            # Check open positions limit
            positions = await self.client.positions.list_open(self.account_id)
            if len(positions) > self.max_open_positions:
                self.halt_trading(f"Too many open positions: {len(positions)}")
                return True

            # Check consecutive losses (would need trade history analysis)
            # This is a simplified check - in practice, analyze recent trade history

            return self.trading_halted

        except Exception as e:
            print(f"❌ Circuit breaker check error: {e}")
            return False

    def halt_trading(self, reason: str):
        """Halt all trading activity."""

        if not self.trading_halted:
            self.trading_halted = True
            self.halt_reasons.append(reason)

            print(f"🚨 TRADING HALTED!")
            print(f"   Reason: {reason}")
            print(f"   Time: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}")

    async def emergency_close_all_positions(self):
        """Emergency close all open positions."""

        if not self.trading_halted:
            print("⚠️ Trading not halted - use halt_trading() first")
            return

        try:
            print("🚨 EMERGENCY: Closing all positions...")

            positions = await self.client.positions.list_open(self.account_id)

            for position in positions:
                instrument = position.instrument

                # Calculate net position
                long_units = int(position.long.units) if position.long.units != "0" else 0
                short_units = int(position.short.units) if position.short.units != "0" else 0
                net_units = long_units + short_units

                if net_units != 0:
                    # Close position with market order
                    close_units = -net_units

                    response = await self.client.orders.post_market_order(
                        account_id=self.account_id,
                        instrument=instrument,
                        units=close_units
                    )

                    if response.order_fill_transaction:
                        print(f"   ✅ Closed {instrument}: {net_units} → 0")
                    else:
                        print(f"   ❌ Failed to close {instrument}")

            print("🛑 Emergency closure complete")

        except Exception as e:
            print(f"❌ Emergency closure error: {e}")

    def reset_circuit_breaker(self):
        """Reset circuit breaker (use with caution)."""

        print("🔄 Resetting circuit breaker...")
        self.trading_halted = False
        self.halt_reasons = []
        print("✅ Circuit breaker reset - trading enabled")

    async def get_status_report(self) -> dict:
        """Get current circuit breaker status."""

        try:
            account = await self.client.accounts.get(self.account_id)
            current_balance = float(account.nav)

            status = {
                'trading_halted': self.trading_halted,
                'halt_reasons': self.halt_reasons,
                'current_balance': current_balance,
                'daily_start_balance': self.daily_start_balance,
                'peak_balance': self.peak_balance
            }

            if self.daily_start_balance:
                status['daily_pl'] = current_balance - self.daily_start_balance
                status['daily_pl_percent'] = ((current_balance - self.daily_start_balance) /
                                            self.daily_start_balance) * 100

            if self.peak_balance:
                status['drawdown'] = self.peak_balance - current_balance
                status['drawdown_percent'] = ((self.peak_balance - current_balance) /
                                            self.peak_balance) * 100

            return status

        except Exception as e:
            return {'error': str(e)}

# Demo circuit breaker
async def demo_circuit_breaker(account_id: str):
    """Demonstrate circuit breaker system."""

    if not account_id:
        return

    async with AsyncClient(token=TOKEN, environment=ENVIRONMENT) as client:
        breaker = CircuitBreaker(client, account_id)

        # Initialize tracking
        await breaker.initialize_daily_tracking()

        # Check current status
        is_halted = await breaker.check_circuit_breakers()

        print(f"\n🔒 Circuit Breaker Status:")
        print(f"   Trading Halted: {'Yes' if is_halted else 'No'}")
        if breaker.halt_reasons:
            print(f"   Halt Reasons: {', '.join(breaker.halt_reasons)}")

        # Get detailed status
        status = await breaker.get_status_report()
        if 'error' not in status:
            print(f"\n📊 Risk Status:")
            if 'daily_pl_percent' in status:
                print(f"   Daily P/L: {status['daily_pl_percent']:+.2f}%")
            if 'drawdown_percent' in status:
                print(f"   Drawdown: {status['drawdown_percent']:.2f}%")

        return breaker
```

---

## 6. Risk-Reward Optimization

### Kelly Criterion Position Sizing

```python
class KellyPositionSizer:
    """Position sizing using Kelly Criterion."""

    def __init__(self, win_rate: float, avg_win: float, avg_loss: float):
        self.win_rate = win_rate / 100  # Convert percentage to decimal
        self.lose_rate = 1 - self.win_rate
        self.avg_win = avg_win
        self.avg_loss = abs(avg_loss)  # Ensure positive

    def calculate_kelly_percentage(self) -> float:
        """Calculate optimal bet size using Kelly formula."""

        if self.avg_loss == 0:
            return 0

        # Kelly formula: f = (bp - q) / b
        # where:
        # b = odds received (avg_win / avg_loss)
        # p = probability of winning (win_rate)
        # q = probability of losing (1 - win_rate)

        b = self.avg_win / self.avg_loss
        p = self.win_rate
        q = self.lose_rate

        kelly_fraction = (b * p - q) / b

        # Cap at reasonable maximum (25%)
        kelly_percentage = max(0, min(kelly_fraction * 100, 25))

        print(f"📊 Kelly Criterion Analysis:")
        print(f"   Win Rate: {self.win_rate * 100:.1f}%")
        print(f"   Average Win: ${self.avg_win:.2f}")
        print(f"   Average Loss: ${self.avg_loss:.2f}")
        print(f"   Win/Loss Ratio: {b:.2f}")
        print(f"   Kelly Percentage: {kelly_percentage:.2f}%")

        return kelly_percentage

    def calculate_position_size(self, account_balance: float, risk_per_unit: float) -> int:
        """Calculate position size using Kelly criterion."""

        kelly_percent = self.calculate_kelly_percentage()

        if kelly_percent <= 0:
            print("⚠️ Kelly criterion suggests no position")
            return 0

        # Use fraction of Kelly for safety (typically 25-50% of full Kelly)
        safety_factor = 0.25  # Use 25% of Kelly recommendation
        adjusted_kelly = kelly_percent * safety_factor

        risk_amount = account_balance * (adjusted_kelly / 100)
        position_size = int(risk_amount / risk_per_unit) if risk_per_unit > 0 else 0

        print(f"   Adjusted Kelly (25%): {adjusted_kelly:.2f}%")
        print(f"   Risk Amount: ${risk_amount:.2f}")
        print(f"   Position Size: {position_size:,} units")

        return position_size

# Demo Kelly sizing
def demo_kelly_sizing():
    """Demonstrate Kelly criterion position sizing."""

    # Example trading statistics
    win_rate = 60  # 60% win rate
    avg_win = 150  # Average win $150
    avg_loss = 100  # Average loss $100

    kelly_sizer = KellyPositionSizer(win_rate, avg_win, avg_loss)

    # Calculate for example account
    account_balance = 10000
    risk_per_unit = 0.50  # $0.50 risk per unit

    optimal_size = kelly_sizer.calculate_position_size(account_balance, risk_per_unit)

    return optimal_size
```

### Risk-Adjusted Performance Metrics

```python
from fivetwenty import AsyncClient, Environment

async def calculate_risk_metrics(account_id: str, days_back: int = 30) -> dict:
    """Calculate comprehensive risk-adjusted performance metrics."""

    async with AsyncClient(token=TOKEN, environment=ENVIRONMENT) as client:
        try:
            from datetime import timedelta

            # Get transaction history
            end_time = datetime.utcnow()
            start_time = end_time - timedelta(days=days_back)

            transactions = await client.transactions.list(
                account_id=account_id,
                from_time=start_time.strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
                to_time=end_time.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
            )

            # Extract trade results
            trade_results = []
            for transaction in transactions.transactions:
                if hasattr(transaction, 'pl') and transaction.pl:
                    trade_results.append(float(transaction.pl))

            if not trade_results:
                print(f"📊 No trades found in the last {days_back} days")
                return {}

            # Calculate metrics
            total_trades = len(trade_results)
            winning_trades = len([r for r in trade_results if r > 0])
            losing_trades = len([r for r in trade_results if r < 0])

            total_profit = sum(r for r in trade_results if r > 0)
            total_loss = sum(r for r in trade_results if r < 0)
            net_profit = sum(trade_results)

            win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
            avg_win = total_profit / winning_trades if winning_trades > 0 else 0
            avg_loss = total_loss / losing_trades if losing_trades > 0 else 0

            # Risk metrics
            profit_factor = abs(total_profit / total_loss) if total_loss != 0 else float('inf')

            # Calculate Sharpe ratio (simplified)
            if len(trade_results) > 1:
                returns_std = np.std(trade_results)
                sharpe_ratio = (np.mean(trade_results) / returns_std) if returns_std > 0 else 0
            else:
                sharpe_ratio = 0

            # Maximum drawdown (simplified - based on cumulative P/L)
            cumulative_pl = np.cumsum(trade_results)
            peak = np.maximum.accumulate(cumulative_pl)
            drawdown = cumulative_pl - peak
            max_drawdown = abs(drawdown.min()) if len(drawdown) > 0 else 0

            # Expectancy
            expectancy = (win_rate / 100 * avg_win) + ((100 - win_rate) / 100 * avg_loss)

            metrics = {
                'period_days': days_back,
                'total_trades': total_trades,
                'winning_trades': winning_trades,
                'losing_trades': losing_trades,
                'win_rate': win_rate,
                'net_profit': net_profit,
                'avg_win': avg_win,
                'avg_loss': avg_loss,
                'profit_factor': profit_factor,
                'sharpe_ratio': sharpe_ratio,
                'max_drawdown': max_drawdown,
                'expectancy': expectancy
            }

            print(f"📊 Risk-Adjusted Performance ({days_back} days):")
            print(f"   Total Trades: {total_trades}")
            print(f"   Win Rate: {win_rate:.1f}%")
            print(f"   Net Profit: ${net_profit:+.2f}")
            print(f"   Profit Factor: {profit_factor:.2f}")
            print(f"   Sharpe Ratio: {sharpe_ratio:.2f}")
            print(f"   Max Drawdown: ${max_drawdown:.2f}")
            print(f"   Expectancy: ${expectancy:+.2f}")

            return metrics

        except Exception as e:
            print(f"❌ Risk metrics error: {e}")
            return {}
```

---

## 7. Best Practices and Summary

### Risk Management Checklist

```python
class RiskManagementChecklist:
    """Comprehensive risk management validation checklist."""

    @staticmethod
    def validate_trade_setup(account_balance: float, position_size: int,
                           entry_price: float, stop_loss: float,
                           take_profit: float = None) -> dict:
        """Validate trade setup against risk management principles."""

        checklist = {
            'passed': [],
            'warnings': [],
            'failures': [],
            'overall_grade': 'F'
        }

        # 1. Position size validation
        risk_amount = abs(position_size) * abs(entry_price - stop_loss)
        risk_percentage = (risk_amount / account_balance) * 100

        if risk_percentage <= 1.0:
            checklist['passed'].append("✅ Position size within 1% risk limit")
        elif risk_percentage <= 2.0:
            checklist['warnings'].append("⚠️ Position size 1-2% risk (acceptable)")
        else:
            checklist['failures'].append("❌ Position size exceeds 2% risk limit")

        # 2. Stop loss validation
        if stop_loss:
            checklist['passed'].append("✅ Stop loss defined")
        else:
            checklist['failures'].append("❌ No stop loss defined")

        # 3. Risk/reward ratio
        if take_profit and stop_loss:
            risk = abs(entry_price - stop_loss)
            reward = abs(take_profit - entry_price)
            rr_ratio = reward / risk if risk > 0 else 0

            if rr_ratio >= 2.0:
                checklist['passed'].append(f"✅ Excellent R:R ratio ({rr_ratio:.2f}:1)")
            elif rr_ratio >= 1.5:
                checklist['passed'].append(f"✅ Good R:R ratio ({rr_ratio:.2f}:1)")
            elif rr_ratio >= 1.0:
                checklist['warnings'].append(f"⚠️ Marginal R:R ratio ({rr_ratio:.2f}:1)")
            else:
                checklist['failures'].append(f"❌ Poor R:R ratio ({rr_ratio:.2f}:1)")

        # 4. Position size reasonableness
        if abs(position_size) <= 10000:
            checklist['passed'].append("✅ Reasonable position size")
        elif abs(position_size) <= 50000:
            checklist['warnings'].append("⚠️ Large position size")
        else:
            checklist['failures'].append("❌ Excessive position size")

        # Calculate overall grade
        total_checks = len(checklist['passed']) + len(checklist['warnings']) + len(checklist['failures'])
        passed_checks = len(checklist['passed'])
        warning_checks = len(checklist['warnings'])

        if len(checklist['failures']) == 0:
            if passed_checks / total_checks >= 0.8:
                checklist['overall_grade'] = 'A'
            elif (passed_checks + warning_checks) / total_checks >= 0.8:
                checklist['overall_grade'] = 'B'
            else:
                checklist['overall_grade'] = 'C'
        elif len(checklist['failures']) <= 1:
            checklist['overall_grade'] = 'D'
        else:
            checklist['overall_grade'] = 'F'

        return checklist

    @staticmethod
    def print_checklist_result(checklist: dict):
        """Print formatted checklist results."""

        print(f"📋 Risk Management Checklist - Grade: {checklist['overall_grade']}")
        print("=" * 50)

        if checklist['passed']:
            print("✅ PASSED:")
            for item in checklist['passed']:
                print(f"   {item}")

        if checklist['warnings']:
            print("\n⚠️ WARNINGS:")
            for item in checklist['warnings']:
                print(f"   {item}")

        if checklist['failures']:
            print("\n❌ FAILURES:")
            for item in checklist['failures']:
                print(f"   {item}")

        print(f"\n🎯 Overall Assessment: {checklist['overall_grade']}")
        if checklist['overall_grade'] in ['A', 'B']:
            print("✅ Trade meets risk management standards")
        elif checklist['overall_grade'] == 'C':
            print("⚠️ Trade has room for improvement")
        else:
            print("🚨 Trade fails risk management standards - DO NOT EXECUTE")

# Demo checklist
def demo_risk_checklist():
    """Demonstrate risk management checklist."""

    # Example trade setups
    trade_setups = [
        {
            'name': 'Conservative Trade',
            'account_balance': 10000,
            'position_size': 1000,
            'entry_price': 1.1000,
            'stop_loss': 1.0950,
            'take_profit': 1.1100
        },
        {
            'name': 'Aggressive Trade',
            'account_balance': 10000,
            'position_size': 5000,
            'entry_price': 1.1000,
            'stop_loss': 1.0900,
            'take_profit': 1.1050
        }
    ]

    for setup in trade_setups:
        print(f"\n🔍 Analyzing: {setup['name']}")
        checklist = RiskManagementChecklist.validate_trade_setup(
            setup['account_balance'], setup['position_size'],
            setup['entry_price'], setup['stop_loss'], setup['take_profit']
        )
        RiskManagementChecklist.print_checklist_result(checklist)
```

### Essential Risk Management Rules

1. **Never risk more than 1-2% per trade**
2. **Always use stop losses**
3. **Maintain minimum 1.5:1 risk/reward ratios**
4. **Limit total portfolio risk to 10-15%**
5. **Monitor correlation risk**
6. **Use position sizing formulas**
7. **Implement circuit breakers**
8. **Track performance metrics**
9. **Review and adjust regularly**
10. **Practice emotional discipline**

---

## Summary

You've now mastered comprehensive risk management:

- ✅ **Position Sizing**: Fixed dollar, percentage, and volatility-based methods
- ✅ **Stop Loss Strategies**: Fixed pip, percentage, and trailing stops
- ✅ **Portfolio Risk**: Monitoring, correlation analysis, and limits
- ✅ **Automated Controls**: Circuit breakers and emergency procedures
- ✅ **Performance Metrics**: Risk-adjusted returns and expectancy
- ✅ **Validation Systems**: Trade checklists and approval processes

### Next Steps

Continue your education:

- **[Portfolio Analysis](portfolio-analysis.md)** - Multi-instrument optimization
- **[Streaming Data](streaming-data.md)** - Real-time risk monitoring
- **[Data Analysis](examples/notebooks/data-analysis.ipynb)** - Historical risk analysis
- **[Advanced Orders](advanced-orders.md)** - Sophisticated order management

### Remember

**Risk management is not about avoiding risk - it's about managing risk intelligently to preserve capital and enable long-term success.**

**Your #1 job as a trader is to protect your capital. Profits will follow.** 🛡️