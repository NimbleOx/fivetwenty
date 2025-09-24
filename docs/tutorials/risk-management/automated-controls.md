# Automated Risk Controls

!!! tip "🎯 Learning Goal"
    Build automated systems that enforce risk management rules without human intervention, protecting your capital even when you're not watching.

---

## Why Automation is Critical

Automated risk controls are essential because:

- **Human emotions** can override good risk management
- **Markets move** faster than manual responses
- **Consistency** is impossible with manual oversight
- **Sleep and breaks** are necessary but markets don't stop
- **Black swan events** require immediate response

!!! warning "⚠️ Automation as Insurance"
    Think of automated risk controls as insurance policies. You hope you never need them, but when you do, they can save your entire trading career.

---

## Circuit Breaker System

Automatically halt trading when predefined risk thresholds are exceeded.

### Implementation

```python
from datetime import datetime
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
        self.max_drawdown_percent = Decimal("15.0")
        self.max_open_positions = 10

        # Tracking
        self.daily_start_balance = None
        self.consecutive_losses = 0
        self.peak_balance = None

    async def initialize_daily_tracking(self):
        """Initialize daily tracking parameters."""

        try:
            account = await self.client.accounts.get(self.account_id)
            current_balance = Decimal(str(account.nav))

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
            current_balance = Decimal(str(account.nav))

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
            current_balance = Decimal(str(account.nav))

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

### Circuit Breaker Configuration

| Trigger Type | Conservative | Moderate | Aggressive |
|--------------|--------------|----------|------------|
| Daily Loss | 3% | 5% | 8% |
| Max Drawdown | 10% | 15% | 20% |
| Consecutive Losses | 3 | 5 | 7 |
| Max Positions | 5 | 10 | 15 |

---

## Position Size Enforcer

Automatically verify and adjust position sizes before order execution.

### Implementation

```python
from decimal import Decimal
from fivetwenty import AsyncClient

class PositionSizeEnforcer:
    """Automatically enforce position sizing rules."""
    
    def __init__(self, client: AsyncClient, account_id: str):
        self.client = client
        self.account_id = account_id
        
        # Enforcement rules
        self.max_risk_per_trade = Decimal("0.02")  # 2% max per trade
        self.max_position_size = 10000   # 10,000 units max
        self.min_position_size = 100     # 100 units min
        self.risk_enforcement_enabled = True
    
    async def validate_and_adjust_order(self, instrument: str, requested_units: int,
                                      entry_price: Decimal, stop_loss: Decimal) -> dict:
        """Validate order and suggest adjustments if needed."""
        
        try:
            # Get current account balance
            account = await self.client.accounts.get(self.account_id)
            account_balance = Decimal(str(account.balance))
            
            # Calculate risk metrics
            risk_per_unit = abs(entry_price - stop_loss)
            requested_risk = abs(requested_units) * risk_per_unit
            risk_percentage = (requested_risk / account_balance) * 100
            
            result = {
                'original_units': requested_units,
                'approved_units': requested_units,
                'risk_amount': requested_risk,
                'risk_percentage': risk_percentage,
                'adjustments_made': [],
                'approved': True,
                'warnings': []
            }
            
            # Check risk percentage limit
            if risk_percentage > self.max_risk_per_trade * Decimal("100"):
                # Calculate maximum allowed units
                max_risk_amount = account_balance * self.max_risk_per_trade
                max_units = int(max_risk_amount / risk_per_unit)
                
                result['approved_units'] = max_units if requested_units > 0 else -max_units
                result['adjustments_made'].append(
                    f"Reduced from {abs(requested_units):,} to {abs(max_units):,} units (risk limit)"
                )
                
                # Recalculate metrics
                result['risk_amount'] = abs(max_units) * risk_per_unit
                result['risk_percentage'] = (result['risk_amount'] / account_balance) * 100
            
            # Check absolute position size limits
            if abs(result['approved_units']) > self.max_position_size:
                result['approved_units'] = self.max_position_size if requested_units > 0 else -self.max_position_size
                result['adjustments_made'].append(
                    f"Capped at maximum position size: {self.max_position_size:,} units"
                )
            
            if abs(result['approved_units']) < self.min_position_size:
                if self.risk_enforcement_enabled:
                    result['approved'] = False
                    result['adjustments_made'].append(
                        f"Position too small: {abs(result['approved_units']):,} < {self.min_position_size:,} units"
                    )
                else:
                    result['warnings'].append(
                        f"Position size below minimum: {abs(result['approved_units']):,} units"
                    )
            
            # Additional validations
            if stop_loss == entry_price:
                result['approved'] = False
                result['adjustments_made'].append("No stop loss defined")
            
            # Check current portfolio exposure
            current_exposure = await self._check_portfolio_exposure(instrument)
            if current_exposure and current_exposure['risk_percentage'] > 10:  # 10% max per instrument
                result['warnings'].append(
                    f"High exposure to {instrument}: {current_exposure['risk_percentage']:.1f}%"
                )
            
            return result
            
        except Exception as e:
            return {
                'error': str(e),
                'approved': False,
                'original_units': requested_units
            }
    
    async def _check_portfolio_exposure(self, instrument: str) -> dict:
        """Check current exposure to specific instrument."""
        
        try:
            positions = await self.client.positions.list_open(self.account_id)
            account = await self.client.accounts.get(self.account_id)
            account_balance = Decimal(str(account.balance))

            for position in positions:
                if position.instrument == instrument:
                    total_pl = (Decimal(str(position.long.unrealized_pl or 0)) +
                              Decimal(str(position.short.unrealized_pl or 0)))
                    
                    # Simplified risk calculation
                    risk_amount = abs(total_pl) if total_pl < 0 else 0
                    risk_percentage = (risk_amount / account_balance) * 100
                    
                    return {
                        'instrument': instrument,
                        'risk_amount': risk_amount,
                        'risk_percentage': risk_percentage,
                        'unrealized_pl': total_pl
                    }
            
            return None
            
        except Exception:
            return None
    
    async def execute_validated_order(self, instrument: str, requested_units: int,
                                    entry_price: Decimal, stop_loss: Decimal,
                                    take_profit: Decimal = None) -> dict:
        """Execute order after validation and adjustment."""
        
        # Validate the order
        validation = await self.validate_and_adjust_order(
            instrument, requested_units, entry_price, stop_loss
        )
        
        print(f"📋 Order Validation Results:")
        print(f"   Original Units: {validation['original_units']:,}")
        print(f"   Approved Units: {validation.get('approved_units', 0):,}")
        print(f"   Risk: ${validation.get('risk_amount', 0):.2f} ({validation.get('risk_percentage', 0):.2f}%)")
        
        if validation.get('adjustments_made'):
            print(f"   Adjustments:")
            for adjustment in validation['adjustments_made']:
                print(f"     • {adjustment}")
        
        if validation.get('warnings'):
            print(f"   Warnings:")
            for warning in validation['warnings']:
                print(f"     ⚠️ {warning}")
        
        if not validation.get('approved', False):
            print(f"   ❌ Order rejected")
            return {'status': 'rejected', 'validation': validation}
        
        # Execute the approved order
        try:
            approved_units = validation['approved_units']
            
            order_params = {
                'account_id': self.account_id,
                'instrument': instrument,
                'units': approved_units,
                'stop_loss_on_fill': {'price': f"{stop_loss:.5f}"}
            }
            
            if take_profit:
                order_params['take_profit_on_fill'] = {'price': f"{take_profit:.5f}"}
            
            response = await self.client.orders.post_market_order(**order_params)
            
            if response.order_fill_transaction:
                fill = response.order_fill_transaction
                print(f"   ✅ Order executed: {fill.units} units at {fill.price}")
                
                return {
                    'status': 'executed',
                    'fill': fill,
                    'validation': validation
                }
            else:
                print(f"   ⚠️ Order placed but not immediately filled")
                return {
                    'status': 'pending',
                    'response': response,
                    'validation': validation
                }
                
        except Exception as e:
            print(f"   ❌ Order execution failed: {e}")
            return {
                'status': 'failed',
                'error': str(e),
                'validation': validation
            }

# Example usage
async def demo_position_enforcer(account_id: str):
    """Demonstrate position size enforcement."""
    
    if not account_id:
        return
    
    async with AsyncClient(token=TOKEN, environment=ENVIRONMENT) as client:
        enforcer = PositionSizeEnforcer(client, account_id)
        
        # Test with oversized position
        print("🧪 Testing oversized position:")
        result = await enforcer.execute_validated_order(
            instrument="EUR_USD",
            requested_units=50000,  # Very large position
            entry_price=Decimal("1.1000"),
            stop_loss=Decimal("1.0950"),
            take_profit=Decimal("1.1050")
        )
        
        return enforcer
```

---

## Real-Time Risk Monitor

Continuously monitor risk metrics and take action when thresholds are exceeded.

### Implementation

```python
from fivetwenty import AsyncClient
import asyncio
from datetime import datetime, timedelta

class RealTimeRiskMonitor:
    """Continuous risk monitoring with automated responses."""
    
    def __init__(self, client: AsyncClient, account_id: str):
        self.client = client
        self.account_id = account_id
        self.monitoring_active = False
        self.monitor_interval = 30  # seconds
        
        # Risk thresholds
        self.thresholds = {
            'portfolio_risk': {'warning': 10.0, 'critical': 15.0},  # %
            'daily_loss': {'warning': 3.0, 'critical': 5.0},        # %
            'position_count': {'warning': 8, 'critical': 12},       # count
            'margin_usage': {'warning': 80.0, 'critical': 95.0}     # %
        }
        
        # Automated responses
        self.auto_responses = {
            'reduce_positions': True,
            'halt_new_trades': True,
            'send_alerts': True,
            'emergency_close': False  # Require manual activation
        }
        
        self.alert_history = []
    
    async def start_monitoring(self):
        """Start continuous risk monitoring."""
        
        if self.monitoring_active:
            print("⚠️ Monitoring already active")
            return
        
        self.monitoring_active = True
        print(f"🔄 Starting real-time risk monitoring (interval: {self.monitor_interval}s)")
        
        try:
            while self.monitoring_active:
                await self._perform_risk_check()
                await asyncio.sleep(self.monitor_interval)
        except Exception as e:
            print(f"❌ Monitoring error: {e}")
            self.monitoring_active = False
    
    async def stop_monitoring(self):
        """Stop risk monitoring."""
        
        self.monitoring_active = False
        print("🛑 Risk monitoring stopped")
    
    async def _perform_risk_check(self):
        """Perform comprehensive risk check."""
        
        try:
            current_time = datetime.utcnow()
            
            # Get account and position data
            account = await self.client.accounts.get(self.account_id)
            positions = await self.client.positions.list_open(self.account_id)
            
            # Calculate risk metrics
            risk_metrics = await self._calculate_risk_metrics(account, positions)
            
            # Check thresholds
            alerts = self._check_thresholds(risk_metrics)
            
            if alerts:
                await self._handle_alerts(alerts, risk_metrics)
            
            # Log status (could save to file/database)
            self._log_risk_status(current_time, risk_metrics, alerts)
            
        except Exception as e:
            print(f"⚠️ Risk check error: {e}")
    
    async def _calculate_risk_metrics(self, account, positions) -> dict:
        """Calculate current risk metrics."""
        
        account_balance = Decimal(str(account.balance))
        account_nav = Decimal(str(account.nav))
        margin_used = Decimal(str(account.margin_used))
        margin_available = Decimal(str(account.margin_available))
        
        # Portfolio risk calculation
        total_unrealized_pl = 0
        position_risk = 0
        
        for position in positions:
            long_pl = Decimal(str(position.long.unrealized_pl or 0))
            short_pl = Decimal(str(position.short.unrealized_pl or 0))
            total_pl = long_pl + short_pl
            total_unrealized_pl += total_pl
            
            if total_pl < 0:
                position_risk += abs(total_pl)
        
        # Calculate metrics
        portfolio_risk_pct = (position_risk / account_balance) * Decimal("100")
        margin_usage_pct = (margin_used / (margin_used + margin_available)) * Decimal("100")
        
        # Daily P/L (simplified - would track from start of day)
        daily_pl_pct = Decimal("0")  # Would calculate from daily start balance
        
        return {
            'account_balance': account_balance,
            'account_nav': account_nav,
            'total_unrealized_pl': total_unrealized_pl,
            'portfolio_risk_pct': portfolio_risk_pct,
            'daily_pl_pct': daily_pl_pct,
            'position_count': len(positions),
            'margin_usage_pct': margin_usage_pct,
            'timestamp': datetime.utcnow()
        }
    
    def _check_thresholds(self, risk_metrics: dict) -> list:
        """Check if any thresholds are exceeded."""
        
        alerts = []
        
        for metric_name, thresholds in self.thresholds.items():
            current_value = risk_metrics.get(metric_name.replace('_', '_'), 0)
            
            if current_value >= thresholds['critical']:
                alerts.append({
                    'level': 'CRITICAL',
                    'metric': metric_name,
                    'current': current_value,
                    'threshold': thresholds['critical'],
                    'message': f"{metric_name} critical: {current_value:.1f} >= {thresholds['critical']:.1f}"
                })
            elif current_value >= thresholds['warning']:
                alerts.append({
                    'level': 'WARNING',
                    'metric': metric_name,
                    'current': current_value,
                    'threshold': thresholds['warning'],
                    'message': f"{metric_name} warning: {current_value:.1f} >= {thresholds['warning']:.1f}"
                })
        
        return alerts
    
    async def _handle_alerts(self, alerts: list, risk_metrics: dict):
        """Handle risk alerts with automated responses."""
        
        for alert in alerts:
            # Record alert
            self.alert_history.append({
                'timestamp': datetime.utcnow(),
                'alert': alert,
                'risk_metrics': risk_metrics.copy()
            })
            
            # Print alert
            level_emoji = "🚨" if alert['level'] == 'CRITICAL' else "⚠️"
            print(f"{level_emoji} {alert['level']}: {alert['message']}")
            
            # Take automated action
            if alert['level'] == 'CRITICAL':
                await self._take_critical_action(alert, risk_metrics)
            elif alert['level'] == 'WARNING':
                await self._take_warning_action(alert, risk_metrics)
    
    async def _take_critical_action(self, alert: dict, risk_metrics: dict):
        """Handle critical alerts."""
        
        print(f"🚨 CRITICAL ACTION REQUIRED: {alert['metric']}")
        
        if self.auto_responses['halt_new_trades']:
            print("   🛑 Halting new trades")
            # Would set a flag to prevent new order execution
        
        if self.auto_responses['reduce_positions'] and alert['metric'] == 'portfolio_risk':
            print("   📉 Reducing position sizes")
            await self._reduce_position_sizes()
        
        if self.auto_responses['emergency_close'] and alert['metric'] == 'daily_loss':
            print("   🚨 EMERGENCY: Closing all positions")
            await self._emergency_close_positions()
    
    async def _take_warning_action(self, alert: dict, risk_metrics: dict):
        """Handle warning alerts."""
        
        print(f"⚠️ WARNING ACTION: {alert['metric']}")
        
        if self.auto_responses['send_alerts']:
            # Would send email/SMS/notification
            print("   📧 Alert notification sent")
    
    async def _reduce_position_sizes(self):
        """Reduce position sizes by closing partial positions."""
        
        try:
            positions = await self.client.positions.list_open(self.account_id)
            
            for position in positions:
                # Close 50% of each position
                long_units = int(position.long.units) if position.long.units != "0" else 0
                short_units = int(position.short.units) if position.short.units != "0" else 0
                
                if long_units > 0:
                    close_units = -(long_units // 2)
                    await self._close_partial_position(position.instrument, close_units)
                
                if short_units < 0:
                    close_units = -(short_units // 2)
                    await self._close_partial_position(position.instrument, close_units)
                    
        except Exception as e:
            print(f"❌ Position reduction error: {e}")
    
    async def _close_partial_position(self, instrument: str, units: int):
        """Close partial position."""
        
        try:
            response = await self.client.orders.post_market_order(
                account_id=self.account_id,
                instrument=instrument,
                units=units
            )
            
            if response.order_fill_transaction:
                print(f"   ✅ Reduced {instrument}: {units} units")
            
        except Exception as e:
            print(f"   ❌ Failed to reduce {instrument}: {e}")
    
    async def _emergency_close_positions(self):
        """Emergency close all positions."""
        
        try:
            positions = await self.client.positions.list_open(self.account_id)
            
            for position in positions:
                instrument = position.instrument
                long_units = int(position.long.units) if position.long.units != "0" else 0
                short_units = int(position.short.units) if position.short.units != "0" else 0
                net_units = long_units + short_units
                
                if net_units != 0:
                    close_units = -net_units
                    
                    response = await self.client.orders.post_market_order(
                        account_id=self.account_id,
                        instrument=instrument,
                        units=close_units
                    )
                    
                    if response.order_fill_transaction:
                        print(f"   🚨 Emergency closed {instrument}")
                        
        except Exception as e:
            print(f"❌ Emergency close error: {e}")
    
    def _log_risk_status(self, timestamp: datetime, risk_metrics: dict, alerts: list):
        """Log current risk status."""
        
        # In production, save to file or database
        if alerts or risk_metrics['portfolio_risk_pct'] > 5:
            print(f"📊 {timestamp.strftime('%H:%M:%S')} - Portfolio Risk: {risk_metrics['portfolio_risk_pct']:.1f}%")
    
    def get_alert_summary(self) -> dict:
        """Get summary of recent alerts."""
        
        recent_alerts = [alert for alert in self.alert_history 
                        if alert['timestamp'] > datetime.utcnow() - timedelta(hours=24)]
        
        critical_count = len([a for a in recent_alerts if a['alert']['level'] == 'CRITICAL'])
        warning_count = len([a for a in recent_alerts if a['alert']['level'] == 'WARNING'])
        
        print(f"📋 24-Hour Alert Summary:")
        print(f"   Critical: {critical_count}")
        print(f"   Warnings: {warning_count}")
        print(f"   Total: {len(recent_alerts)}")
        
        return {
            'total_alerts': len(recent_alerts),
            'critical_alerts': critical_count,
            'warning_alerts': warning_count,
            'recent_alerts': recent_alerts
        }

# Example monitoring
async def demo_risk_monitoring(account_id: str):
    """Demonstrate real-time risk monitoring."""
    
    if not account_id:
        return
    
    async with AsyncClient(token=TOKEN, environment=ENVIRONMENT) as client:
        monitor = RealTimeRiskMonitor(client, account_id)
        
        print("🔄 Starting demo monitoring (will run for 2 minutes)")
        
        # Start monitoring in background
        monitor_task = asyncio.create_task(monitor.start_monitoring())
        
        # Let it run for 2 minutes
        await asyncio.sleep(120)
        
        # Stop monitoring
        await monitor.stop_monitoring()
        monitor_task.cancel()
        
        # Get summary
        summary = monitor.get_alert_summary()
        
        return monitor
```

---

## ✅ Skill Checkpoint: Automated Risk Controls

Test your understanding of automated risk management:

!!! question "🧠 Test Your Understanding"
    1. **Why is a circuit breaker system essential for automated trading?**
       <details>
       <summary>Click to reveal answer</summary>
       **Prevents catastrophic losses when systems malfunction or market conditions change rapidly**. Without circuit breakers, a bug or unexpected event could wipe out an account before human intervention is possible.
       </details>

    2. **What's the difference between position size enforcement and portfolio risk monitoring?**
       <details>
       <summary>Click to reveal answer</summary>
       **Position size enforcement validates individual trades before execution, while portfolio monitoring tracks aggregate risk across all positions**. Both are needed - enforcement prevents individual oversized trades, monitoring catches cumulative risk buildup.
       </details>

    3. **When should automated systems take action vs. sending alerts?**
       <details>
       <summary>Click to reveal answer</summary>
       **Warnings should send alerts for human review, critical violations should take immediate action**. For example, send alert at 3% daily loss, auto-halt trading at 5% loss. Balance automation with human oversight.
       </details>

---

## Automated Control Best Practices

### Implementation Guidelines

1. **Start Conservative**
   - Set tight initial thresholds
   - Begin with alerts before automation
   - Test thoroughly in simulation
   - Gradually increase automation

2. **Multiple Layers of Defense**
   - Position size validation
   - Real-time monitoring
   - Circuit breakers
   - Emergency controls

3. **Human Override Capability**
   - Always allow manual intervention
   - Provide emergency stop mechanisms
   - Log all automated actions
   - Enable system reset procedures

4. **Testing and Validation**
   - Test all scenarios in simulation
   - Verify alert mechanisms work
   - Practice emergency procedures
   - Regular system health checks

### Common Implementation Mistakes

#### ❌ **Over-Automation**
```python
# WRONG: Automating everything without human oversight
auto_responses = {
    'close_all_positions': True,     # Too aggressive
    'halt_trading': True,
    'reduce_sizes': True,
    'send_alerts': False             # No human notification
}

# RIGHT: Balanced automation with human oversight
auto_responses = {
    'close_all_positions': False,    # Manual decision
    'halt_trading': True,            # Automated safety
    'reduce_sizes': True,            # Automated risk reduction
    'send_alerts': True              # Always notify humans
}
```

#### ❌ **Insufficient Testing**
```python
# WRONG: Using untested thresholds
thresholds = {
    'daily_loss': 10.0  # Never tested what happens at this level
}

# RIGHT: Well-tested thresholds
thresholds = {
    'daily_loss': 5.0   # Tested in simulation, known to be appropriate
}
```

#### ❌ **No Failsafe Mechanisms**
```python
# WRONG: No way to stop automated system
class RiskSystem:
    def __init__(self):
        self.can_be_stopped = False  # Dangerous!

# RIGHT: Always include emergency stops
class RiskSystem:
    def __init__(self):
        self.emergency_stop_enabled = True
        self.manual_override = True
```

---

## Advanced Automation Features

### Machine Learning Integration

```python
class MLRiskPredictor:
    """Use machine learning to predict risk scenarios."""
    
    def __init__(self):
        self.model_loaded = False
        # In practice, load trained model
    
    def predict_risk_scenario(self, market_data: dict, portfolio_state: dict) -> dict:
        """Predict potential risk scenarios."""
        
        # Simplified example - in practice use trained ML model
        risk_factors = {
            'volatility_spike': self._assess_volatility_risk(market_data),
            'correlation_breakdown': self._assess_correlation_risk(portfolio_state),
            'liquidity_crisis': self._assess_liquidity_risk(market_data)
        }
        
        # Calculate overall risk score
        risk_score = sum(risk_factors.values()) / len(risk_factors)
        
        return {
            'overall_risk_score': risk_score,
            'risk_factors': risk_factors,
            'recommended_action': self._recommend_action(risk_score)
        }
    
    def _assess_volatility_risk(self, market_data: dict) -> float:
        """Assess volatility spike risk (0-1)."""
        # Simplified - real implementation would use sophisticated models
        return 0.3  # Example score
    
    def _assess_correlation_risk(self, portfolio_state: dict) -> float:
        """Assess correlation breakdown risk (0-1)."""
        return 0.2  # Example score
    
    def _assess_liquidity_risk(self, market_data: dict) -> float:
        """Assess liquidity crisis risk (0-1)."""
        return 0.1  # Example score
    
    def _recommend_action(self, risk_score: float) -> str:
        """Recommend action based on risk score."""
        if risk_score > 0.8:
            return "EMERGENCY_STOP"
        elif risk_score > 0.6:
            return "REDUCE_EXPOSURE"
        elif risk_score > 0.4:
            return "INCREASE_MONITORING"
        else:
            return "NORMAL_OPERATIONS"
```

### Dynamic Threshold Adjustment

```python
class AdaptiveThresholds:
    """Automatically adjust risk thresholds based on market conditions."""
    
    def __init__(self):
        self.base_thresholds = {
            'daily_loss': 5.0,
            'portfolio_risk': 15.0
        }
        self.current_thresholds = self.base_thresholds.copy()
    
    def adjust_for_market_conditions(self, volatility_index: float, 
                                   market_stress: float) -> dict:
        """Adjust thresholds based on market conditions."""
        
        # Tighten thresholds in high volatility/stress
        volatility_adjustment = 1.0 - (volatility_index * 0.3)
        stress_adjustment = 1.0 - (market_stress * 0.2)
        
        combined_adjustment = volatility_adjustment * stress_adjustment
        
        for threshold_name, base_value in self.base_thresholds.items():
            adjusted_value = base_value * combined_adjustment
            self.current_thresholds[threshold_name] = max(adjusted_value, base_value * 0.5)
        
        print(f"📊 Dynamic Threshold Adjustment:")
        print(f"   Volatility Index: {volatility_index:.2f}")
        print(f"   Market Stress: {market_stress:.2f}")
        print(f"   Adjustment Factor: {combined_adjustment:.2f}")
        
        for name, value in self.current_thresholds.items():
            print(f"   {name}: {self.base_thresholds[name]:.1f}% → {value:.1f}%")
        
        return self.current_thresholds
```

---

## What You've Learned

✅ **Circuit Breaker Systems**: Automated trading halts for emergency protection

✅ **Position Size Enforcement**: Automatic validation and adjustment of trade sizes

✅ **Real-Time Monitoring**: Continuous risk tracking with automated responses

✅ **Alert Management**: Graduated response system from warnings to critical actions

✅ **Advanced Features**: ML integration and adaptive thresholds

!!! success "🎉 Automated Risk Controls Complete!"
    You now have the tools to build sophisticated automated risk management systems that protect your capital 24/7. These systems provide the discipline and consistency that human traders often struggle to maintain. Next, learn advanced performance optimization techniques.

---

## Next Steps

Continue to [Performance Optimization](performance-optimization.md) to learn advanced techniques for optimizing risk-adjusted returns.

---

## Related Resources

- **[Risk Management Fundamentals](fundamentals.md)** - Core risk management principles
- **[Portfolio Risk Management](portfolio-risk.md)** - Managing risk across multiple positions
- **[Circuit Breaker Implementation](../../how-to-guides/implement-stop-loss-strategies.md)** - Detailed stop loss techniques
- **[API Reference: Orders](../../api-reference/endpoints/orders.md)** - Technical order management documentation