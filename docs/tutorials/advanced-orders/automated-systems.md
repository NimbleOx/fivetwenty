# Automated Order Systems

Build rule-based order management systems with intelligent monitoring, error handling, and automated decision-making.

## Learning Objectives

By the end of this guide, you will:

- Design rule-based order management systems
- Implement automated monitoring and alerts
- Create intelligent error recovery mechanisms
- Build event-driven order systems
- Develop comprehensive logging and audit trails

## Rule-Based Order Management

Create systems that make order decisions based on predefined rules and market conditions.

### Basic Rule Engine Implementation

```python
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any

from fivetwenty import AsyncClient



class OrderRule(ABC):
    """Base class for order management rules."""

    def __init__(self, name: str, priority: int = 1) -> None:
        self.name = name
        self.priority = priority
        self.enabled = True

    @abstractmethod
    async def evaluate(self, context: dict[str, Any]) -> bool:
        """Evaluate if the rule condition is met."""
        pass

    @abstractmethod
    async def execute(self, context: dict[str, Any]) -> dict[str, Any]:
        """Execute the rule action."""
        pass

class RuleBasedOrderManager:
    def __init__(self, client: AsyncClient, account_id: str) -> None:
        self.client = client
        self.account_id = account_id
        self.rules: list[OrderRule] = []
        self.execution_log = []

    def add_rule(self, rule: OrderRule) -> Any:
        """Add a rule to the management system."""
        self.rules.append(rule)
        # Sort by priority (higher priority first)
        self.rules.sort(key=lambda r: r.priority, reverse=True)

    async def evaluate_and_execute_rules(self, context: dict[str, Any]) -> Any:
        """Evaluate all rules and execute applicable ones."""
        executed_rules = []

        for rule in self.rules:
            if not rule.enabled:
                continue

            try:
                if await rule.evaluate(context):
                    result = await rule.execute(context)
                    executed_rules.append({
                        "rule_name": rule.name,
                        "execution_time": datetime.utcnow(),
                        "result": result,
                    })

                    # Log execution
                    self.execution_log.append(executed_rules[-1])
                    print(f"Rule executed: {rule.name}")

            except Exception as e:
                print(f"Rule {rule.name} failed: {e}")

        return executed_rules
```

### Market Condition Rules

Implement rules based on market conditions:

```python
from datetime import datetime
from decimal import Decimal
from typing import Any



class SpreadThresholdRule(OrderRule):
    """Cancel orders when spread becomes too wide."""

    def __init__(self, max_spread_pips: Decimal, instruments: list[str]) -> None:
        super().__init__("SpreadThreshold", priority=10)
        self.max_spread_pips = max_spread_pips
        self.instruments = instruments

    async def evaluate(self, context: dict[str, Any]) -> bool:
        """Check if spread exceeds threshold."""
        client = context["client"]
        account_id = context["account_id"]

        for instrument in self.instruments:
            pricing = await client.pricing.get_pricing(
                account_id=account_id,
                instruments=[instrument]
            )

            current_spread = (
                Decimal(pricing.prices[0].asks[0].price) -
                Decimal(pricing.prices[0].bids[0].price)
            )

            pip_value = Decimal("0.0001")  # Adjust for instrument
            spread_pips = current_spread / pip_value

            if spread_pips > self.max_spread_pips:
                context["wide_spread_instrument"] = instrument
                context["current_spread"] = spread_pips
                return True

        return False

    async def execute(self, context: dict[str, Any]) -> dict[str, Any]:
        """Cancel pending orders for wide spread instrument."""
        client = context["client"]
        account_id = context["account_id"]
        instrument = context["wide_spread_instrument"]

        # Get all pending orders for this instrument
        orders = await client.orders.get_orders(account_id=account_id)
        cancelled_orders = []

        for order in orders.orders:
            if order.instrument == instrument and order.state == "PENDING":
                try:
                    await client.orders.cancel_order(
                        account_id=account_id,
                        order_id=order.id
                    )
                    cancelled_orders.append(order.id)
                except Exception as e:
                    print(f"Failed to cancel order {order.id}: {e}")

        return {
            "action": "cancel_orders",
            "instrument": instrument,
            "spread": context["current_spread"],
            "cancelled_orders": cancelled_orders
        }

class MarketSessionRule(OrderRule):
    """Adjust order parameters based on trading session."""

    def __init__(self) -> None:
        super().__init__("MarketSession", priority=5)

    async def evaluate(self, context: dict[str, Any]) -> bool:
        """Always evaluate - determines session-specific actions."""
        current_hour = datetime.utcnow().hour
        context["trading_session"] = self._determine_session(current_hour)
        return True

    def _determine_session(self, hour: int) -> str:
        """Determine current trading session."""
        if 8 <= hour <= 17:
            return "london"
        elif 13 <= hour <= 22:
            return "new_york"
        elif 23 <= hour <= 8:
            return "asia"
        else:
            return "overlap"

    async def execute(self, context: dict[str, Any]) -> dict[str, Any]:
        """Set session-specific parameters."""
        session = context["trading_session"]

        session_params = {
            "london": {
                "max_position_size": 20000,
                "stop_distance": Decimal("0.0025"),
                "active_strategies": ["breakout", "momentum"]
            },
            "new_york": {
                "max_position_size": 15000,
                "stop_distance": Decimal("0.0030"),
                "active_strategies": ["reversal", "range"]
            },
            "asia": {
                "max_position_size": 10000,
                "stop_distance": Decimal("0.0020"),
                "active_strategies": ["range", "carry"]
            },
            "overlap": {
                "max_position_size": 25000,
                "stop_distance": Decimal("0.0035"),
                "active_strategies": ["breakout", "momentum", "reversal"]
            }
        }

        context.update(session_params[session])

        return {
            "action": "update_session_params",
            "session": session,
            "parameters": session_params[session]
        }
```

### Position Management Rules

```python
from decimal import Decimal
from typing import Any




class MaxPositionRule(OrderRule):
    """Enforce maximum position size limits."""

    def __init__(self, max_total_exposure: Decimal) -> None:
        super().__init__("MaxPosition", priority=8)
        self.max_total_exposure = max_total_exposure

    async def evaluate(self, context: dict[str, Any]) -> bool:
        """Check if current exposure exceeds maximum."""
        client = context["client"]
        account_id = context["account_id"]

        # Get current positions
        positions = await client.positions.get_positions(account_id=account_id)

        total_exposure = Decimal("0")
        for position in positions.positions:
            if hasattr(position, "long") and position.long.units != "0":
                total_exposure += abs(Decimal(position.long.units))
            if hasattr(position, "short") and position.short.units != "0":
                total_exposure += abs(Decimal(position.short.units))

        context["current_exposure"] = total_exposure
        return total_exposure > self.max_total_exposure

    async def execute(self, context: dict[str, Any]) -> dict[str, Any]:
        """Cancel new orders or reduce positions."""
        client = context["client"]
        account_id = context["account_id"]

        # Cancel all pending orders
        orders = await client.orders.get_orders(account_id=account_id)
        cancelled_orders = []

        for order in orders.orders:
            if order.state == "PENDING":
                try:
                    await client.orders.cancel_order(
                        account_id=account_id,
                        order_id=order.id,
                    )
                    cancelled_orders.append(order.id)
                except Exception:
                    pass

        return {
            "action": "exposure_limit_exceeded",
            "current_exposure": context["current_exposure"],
            "max_exposure": self.max_total_exposure,
            "cancelled_orders": cancelled_orders,
        }

class StopLossProtectionRule(OrderRule):
    """Ensure all positions have stop-loss protection."""

    def __init__(self, max_stop_distance: Decimal) -> None:
        super().__init__("StopLossProtection", priority=9)
        self.max_stop_distance = max_stop_distance

    async def evaluate(self, context: dict[str, Any]) -> bool:
        """Check for unprotected positions."""
        client = context["client"]
        account_id = context["account_id"]

        # Get current positions and orders
        positions = await client.positions.get_positions(account_id=account_id)
        orders = await client.orders.get_orders(account_id=account_id)

        # Find positions without stop-loss protection
        unprotected_positions = []

        for position in positions.positions:
            if position.long.units != "0" or position.short.units != "0":
                # Check if position has stop-loss order
                has_stop = any(
                    order.type == "STOP" and order.instrument == position.instrument
                    for order in orders.orders
                    if order.state == "PENDING"
                )

                if not has_stop:
                    unprotected_positions.append(position)

        context["unprotected_positions"] = unprotected_positions
        return len(unprotected_positions) > 0

    async def execute(self, context: dict[str, Any]) -> dict[str, Any]:
        """Place stop-loss orders for unprotected positions."""
        client = context["client"]
        account_id = context["account_id"]
        unprotected = context["unprotected_positions"]

        placed_stops = []

        for position in unprotected:
            try:
                # Get current price for stop calculation
                pricing = await client.pricing.get_pricing(
                    account_id=account_id,
                    instruments=[position.instrument],
                )

                current_price = Decimal(pricing.prices[0].asks[0].price)

                # Determine position direction and calculate stop
                if position.long.units != "0":
                    # Long position - place sell stop below current price
                    units = -int(position.long.units)
                    stop_price = current_price - self.max_stop_distance
                elif position.short.units != "0":
                    # Short position - place buy stop above current price
                    units = -int(position.short.units)  # Make positive to close short
                    stop_price = current_price + self.max_stop_distance

                # Place stop-loss order
                stop_response = await client.orders.post_stop_order(
                    account_id=account_id,
                    instrument=position.instrument,
                    units=units,
                    price=stop_price,
                    time_in_force="GTC",
                )

                placed_stops.append({
                    "instrument": position.instrument,
                    "order_id": stop_response.order_create_transaction.id,
                    "stop_price": stop_price,
                })

            except Exception as e:
                print(f"Failed to place stop for {position.instrument}: {e}")

        return {
            "action": "place_protective_stops",
            "placed_stops": placed_stops,
        }
```

## Automated Monitoring System

Create comprehensive monitoring for order and position management.

### Real-Time Monitoring Engine

```python
from datetime import datetime
from decimal import Decimal

from fivetwenty import AsyncClient
from typing import Any




class OrderMonitoringEngine:
    def __init__(self, client: AsyncClient, account_id: str) -> None:
        self.client = client
        self.account_id = account_id
        self.active_monitors = {}
        self.alert_handlers = []
        self.monitoring_active = False

    async def start_monitoring(self, check_interval: int = 30) -> Any:
        """Start continuous monitoring of orders and positions."""
        self.monitoring_active = True

        while self.monitoring_active:
            try:
                await self._check_all_monitors()
                await asyncio.sleep(check_interval)
            except Exception as e:
                print(f"Monitoring error: {e}")
                await asyncio.sleep(check_interval)

    async def _check_all_monitors(self) -> Any:
        """Check all active monitors and trigger alerts."""
        current_time = datetime.utcnow()

        # Get current market data
        context = {
            "client": self.client,
            "account_id": self.account_id,
            "current_time": current_time,
        }

        # Check order timeouts
        await self._check_order_timeouts(context)

        # Check position risks
        await self._check_position_risks(context)

        # Check market conditions
        await self._check_market_conditions(context)

    async def _check_order_timeouts(self, context: dict[str, Any]) -> Any:
        """Check for orders that have been pending too long."""
        orders = await self.client.orders.get_orders(
            account_id=self.account_id,
        )

        timeout_threshold = timedelta(hours=2)  # 2-hour timeout

        for order in orders.orders:
            if order.state == "PENDING":
                order_age = context["current_time"] - datetime.fromisoformat(
                    order.create_time.replace("Z", "+00:00"),
                )

                if order_age > timeout_threshold:
                    await self._trigger_alert({
                        "type": "order_timeout",
                        "order_id": order.id,
                        "instrument": order.instrument,
                        "age_hours": order_age.total_seconds() / 3600,
                    })

    async def _check_position_risks(self, context: dict[str, Any]) -> Any:
        """Check for high-risk position situations."""
        positions = await self.client.positions.get_positions(
            account_id=self.account_id,
        )

        for position in positions.positions:
            if position.long.units != "0" or position.short.units != "0":
                # Calculate unrealized P&L risk
                unrealized_pl = Decimal(position.unrealized_pl or "0")

                # Get position size
                if position.long.units != "0":
                    position_size = abs(Decimal(position.long.units))
                else:
                    position_size = abs(Decimal(position.short.units))

                # Risk threshold: 2% of position value
                risk_threshold = position_size * Decimal("0.02")

                if abs(unrealized_pl) > risk_threshold:
                    await self._trigger_alert({
                        "type": "high_risk_position",
                        "instrument": position.instrument,
                        "unrealized_pl": unrealized_pl,
                        "risk_threshold": risk_threshold,
                        "position_size": position_size,
                    })

    async def _check_market_conditions(self, context: dict[str, Any]) -> Any:
        """Check for unusual market conditions."""
        instruments = ["EUR_USD", "GBP_USD", "USD_JPY"]  # Monitor major pairs

        for instrument in instruments:
            pricing = await self.client.pricing.get_pricing(
                account_id=self.account_id,
                instruments=[instrument],
            )

            spread = (
                Decimal(pricing.prices[0].asks[0].price) -
                Decimal(pricing.prices[0].bids[0].price)
            )

            # Alert on unusually wide spreads
            normal_spread_threshold = Decimal("0.0005")  # 0.5 pips

            if spread > normal_spread_threshold:
                await self._trigger_alert({
                    "type": "wide_spread",
                    "instrument": instrument,
                    "current_spread": spread,
                    "threshold": normal_spread_threshold,
                })

    async def _trigger_alert(self, alert_data: dict[str, Any]) -> Any:
        """Trigger alert through all registered handlers."""
        for handler in self.alert_handlers:
            try:
                await handler.handle_alert(alert_data)
            except Exception as e:
                # Expected output: f"Alert handler failed: {e}"

    def add_alert_handler(self, handler: Any) -> Any:
        """Add an alert handler to the monitoring system."""
        self.alert_handlers.append(handler)

    def stop_monitoring(self) -> Any:
        """Stop the monitoring engine."""
        self.monitoring_active = False
```

### Alert System Implementation

```python
from datetime import datetime
from typing import Any




class BaseAlertHandler(ABC):
    """Base class for alert handlers."""

    @abstractmethod
    async def handle_alert(self, alert_data: dict[str, Any]) -> Any:
        """Handle an alert."""
        pass

class ConsoleAlertHandler(BaseAlertHandler):
    """Simple console-based alert handler."""

    async def handle_alert(self, alert_data: dict[str, Any]) -> Any:
        """Print alert to console."""
        alert_type = alert_data["type"]
        timestamp = datetime.utcnow().isoformat()

        print(f"[ALERT {timestamp}] {alert_type.upper()}")

        if alert_type == "order_timeout":
            print(f"  Order {alert_data['order_id']} ({alert_data['instrument']}) "
                  f"pending for {alert_data['age_hours']:.1f} hours")

        elif alert_type == "high_risk_position":
            print(f"  Position {alert_data['instrument']} P&L: {alert_data['unrealized_pl']} "
                  f"(threshold: {alert_data['risk_threshold']})")

        elif alert_type == "wide_spread":
            print(f"  Wide spread {alert_data['instrument']}: {alert_data['current_spread']} "
                  f"(threshold: {alert_data['threshold']})")

class EmailAlertHandler(BaseAlertHandler):
    """Email-based alert handler (implementation depends on email service)."""

    def __init__(self, email_config: dict[str, str]) -> None:
        self.email_config = email_config

    async def handle_alert(self, alert_data: dict[str, Any]) -> Any:
        """Send alert via email."""
        # Implementation would integrate with your email service
        print(f"Email alert sent: {alert_data['type']}")

class DatabaseAlertHandler(BaseAlertHandler):
    """Database logging alert handler."""

    def __init__(self, db_connection: Any) -> None:
        self.db_connection = db_connection

    async def handle_alert(self, alert_data: dict[str, Any]) -> Any:
        """Log alert to database."""
        # Implementation would log to your database
        print(f"Database alert logged: {alert_data['type']}")
```

## Event-Driven Order System

Build systems that respond to market events and order state changes.

### Event-Driven Architecture

```python
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

from fivetwenty import AsyncClient
from typing import Any




class EventType(Enum):
    ORDER_FILLED = "order_filled"
    ORDER_CANCELLED = "order_cancelled"
    POSITION_OPENED = "position_opened"
    POSITION_CLOSED = "position_closed"
    PRICE_ALERT = "price_alert"
    SPREAD_WARNING = "spread_warning"

@dataclass
class TradingEvent:
    event_type: EventType
    timestamp: datetime
    data: dict[str, Any]
    instrument: str = None

class EventDrivenOrderSystem:
    def __init__(self, client: AsyncClient, account_id: str) -> None:
        self.client = client
        self.account_id = account_id
        self.event_handlers: dict[EventType, list[Callable]] = {}
        self.event_queue = asyncio.Queue()
        self.processing_events = False

    def register_handler(self, event_type: EventType, handler: Callable) -> Any:
        """Register an event handler."""
        if event_type not in self.event_handlers:
            self.event_handlers[event_type] = []
        self.event_handlers[event_type].append(handler)

    async def emit_event(self, event: TradingEvent) -> Any:
        """Emit an event to the system."""
        await self.event_queue.put(event)

    async def start_event_processing(self) -> Any:
        """Start processing events from the queue."""
        self.processing_events = True

        while self.processing_events:
            try:
                # Wait for events with timeout
                event = await asyncio.wait_for(
                    self.event_queue.get(),
                    timeout=1.0,
                )

                await self._process_event(event)

            except asyncio.TimeoutError:
                continue  # No events in queue
            except Exception as e:
                print(f"Event processing error: {e}")

    async def _process_event(self, event: TradingEvent) -> Any:
        """Process a single event through all registered handlers."""
        if event.event_type in self.event_handlers:
            for handler in self.event_handlers[event.event_type]:
                try:
                    await handler(event)
                except Exception as e:
                    print(f"Event handler failed: {e}")

    def stop_event_processing(self) -> Any:
        """Stop event processing."""
        self.processing_events = False
```

### Event Handler Implementations

```python
async def order_filled_handler(event: TradingEvent) -> Any:
    """Handle order filled events."""
    order_data = event.data
    print(f"Order filled: {order_data['order_id']} at {order_data['fill_price']}")

    # Automatically place protective stop if not exists
    if "auto_stop" in order_data and order_data["auto_stop"]:
        # Implementation would place protective stop
        pass

async def position_opened_handler(event: TradingEvent) -> Any:
    """Handle new position events."""
    position_data = event.data
    print(f"Position opened: {position_data['instrument']} {position_data['units']} units")

    # Set up position monitoring
    # Implementation would start position-specific monitoring

async def spread_warning_handler(event: TradingEvent) -> Any:
    """Handle spread warning events."""
    spread_data = event.data
    print(f"Spread warning: {spread_data['instrument']} spread: {spread_data['spread']}")

    # Cancel pending orders for affected instrument
    # Implementation would cancel orders with wide spreads

# Register event handlers
event_system = EventDrivenOrderSystem(client, "your_account_id")
event_system.register_handler(EventType.ORDER_FILLED, order_filled_handler)
event_system.register_handler(EventType.POSITION_OPENED, position_opened_handler)
event_system.register_handler(EventType.SPREAD_WARNING, spread_warning_handler)
```

## Intelligent Error Recovery

Build systems that handle errors gracefully and recover automatically.

### Error Recovery Manager

```python
from datetime import datetime
from decimal import Decimal
from fivetwenty import AsyncClient
from typing import Any



class ErrorRecoveryManager:
    def __init__(self, client: AsyncClient, account_id: str) -> None:
        self.client = client
        self.account_id = account_id
        self.recovery_strategies = {}
        self.error_history = []

    def register_recovery_strategy(self, error_type: str, strategy: Callable) -> Any:
        """Register a recovery strategy for specific error types."""
        self.recovery_strategies[error_type] = strategy

    async def handle_order_error(self, error: Exception, order_context: dict[str, Any]) -> Any:
        """Handle order-related errors with appropriate recovery."""
        error_type = type(error).__name__
        error_message = str(error)

        # Log error
        error_record = {
            "timestamp": datetime.utcnow(),
            "error_type": error_type,
            "error_message": error_message,
            "order_context": order_context,
            "recovery_attempted": False
        }

        self.error_history.append(error_record)

        # Attempt recovery
        if error_type in self.recovery_strategies:
            try:
                recovery_result = await self.recovery_strategies[error_type](
                    error, order_context
                )
                error_record["recovery_attempted"] = True
                error_record["recovery_result"] = recovery_result

                print(f"Recovery attempted for {error_type}: {recovery_result}")

            except Exception as recovery_error:
                print(f"Recovery failed: {recovery_error}")

        return error_record

# Recovery strategy implementations
async def insufficient_margin_recovery(error: Exception, context: dict[str, Any]) -> Any:
    """Recover from insufficient margin errors."""
    # Reduce position size and retry
    original_units = context.get("units", 0)
    reduced_units = int(original_units * Decimal("0.7"))  # Reduce by 30%

    context["units"] = reduced_units

    return {
        "action": "reduce_position_size",
        "original_units": original_units,
        "reduced_units": reduced_units
    }

async def invalid_price_recovery(error: Exception, context: dict[str, Any]) -> Any:
    """Recover from invalid price errors."""
    # Get current market price and adjust
    client = context["client"]
    account_id = context["account_id"]
    instrument = context["instrument"]

    pricing = await client.pricing.get_pricing(
        account_id=account_id,
        instruments=[instrument]
    )

    current_price = Decimal(pricing.prices[0].asks[0].price)

    # Adjust price to current market level
    context["price"] = current_price

    return {
        "action": "adjust_to_market_price",
        "new_price": current_price
    }

async def market_closed_recovery(error: Exception, context: dict[str, Any]) -> Any:
    """Recover from market closed errors."""
    # Queue order for next market open
    return {
        "action": "queue_for_market_open",
        "retry_time": "next_market_open"
    }

# Register recovery strategies
recovery_manager = ErrorRecoveryManager(client, "your_account_id")
recovery_manager.register_recovery_strategy("InsufficientMarginError", insufficient_margin_recovery)
recovery_manager.register_recovery_strategy("InvalidPriceError", invalid_price_recovery)
recovery_manager.register_recovery_strategy("MarketClosedError", market_closed_recovery)
```

## Comprehensive Logging and Audit

Implement detailed logging for compliance and analysis.

### Advanced Logging System

```python

from typing import Any
import json
import logging
from datetime import datetime
from pathlib import Path





class TradingLogger:
    """Class docstring."""
    def __init__(self, log_directory: str = "trading_logs") -> None:
        self.log_directory = Path(log_directory)
        self.log_directory.mkdir(exist_ok=True)

        # Set up different loggers for different purposes
        self.setup_loggers()

    def setup_loggers(self) -> Any:
        """Set up specialized loggers for different trading activities."""

        # Order activity logger
        self.order_logger = logging.getLogger("orders")
        order_handler = logging.FileHandler(
            self.log_directory / "orders.log",
        )
        order_handler.setFormatter(logging.Formatter(
            "%(asctime)s - %(levelname)s - %(message)s",
        ))
        self.order_logger.addHandler(order_handler)
        self.order_logger.setLevel(logging.INFO)

        # Error logger
        self.error_logger = logging.getLogger("errors")
        error_handler = logging.FileHandler(
            self.log_directory / "errors.log",
        )
        error_handler.setFormatter(logging.Formatter(
            "%(asctime)s - %(levelname)s - %(message)s",
        ))
        self.error_logger.addHandler(error_handler)
        self.error_logger.setLevel(logging.ERROR)

        # Performance logger
        self.performance_logger = logging.getLogger("performance")
        perf_handler = logging.FileHandler(
            self.log_directory / "performance.log",
        )
        perf_handler.setFormatter(logging.Formatter(
            "%(asctime)s - %(message)s",
        ))
        self.performance_logger.addHandler(perf_handler)
        self.performance_logger.setLevel(logging.INFO)

    def log_order_action(self, action: str, order_data: dict[str, Any]) -> Any:
        """Log order-related actions."""
        log_entry = {
            "action": action,
            "timestamp": datetime.utcnow().isoformat(),
            "order_data": order_data,
        }

        self.order_logger.info(json.dumps(log_entry))

    def log_error(self, error: Exception, context: dict[str, Any]) -> Any:
        """Log errors with context."""
        log_entry = {
            "error_type": type(error).__name__,
            "error_message": str(error),
            "timestamp": datetime.utcnow().isoformat(),
            "context": context,
        }

        self.error_logger.error(json.dumps(log_entry))

    def log_performance_metric(self, metric_name: str, value: Any, metadata: dict[str, Any] = None) -> Any:
        """Log performance metrics."""
        log_entry = {
            "metric": metric_name,
            "value": value,
            "timestamp": datetime.utcnow().isoformat(),
            "metadata": metadata or {},
        }

        self.performance_logger.info(json.dumps(log_entry))

# Usage example
logger = TradingLogger()

# Log order placement
logger.log_order_action("order_placed", {
    "order_id": "12345",
    "instrument": "EUR_USD",
    "units": 10000,
    "price": "1.0850",
})

# Log error
logger.log_error(Exception("Insufficient margin"), {
    "operation": "place_order",
    "instrument": "EUR_USD",
    "requested_units": 50000,
})

# Log performance metric
logger.log_performance_metric("order_fill_time", 1.2, {
    "instrument": "EUR_USD",
    "order_type": "LIMIT",
})
```

## Best Practices Summary

### Rule-Based Systems
- Design modular, reusable rules
- Implement proper priority ordering
- Include comprehensive error handling
- Maintain detailed execution logs

### Monitoring and Alerts
- Monitor key risk metrics continuously
- Implement multiple alert channels
- Use appropriate alert thresholds
- Test alert systems regularly

### Event-Driven Architecture
- Design loosely coupled event handlers
- Implement proper error isolation
- Use asynchronous processing for performance
- Maintain event history for analysis

### Error Recovery
- Anticipate common error scenarios
- Implement graceful degradation strategies
- Log all recovery attempts
- Test recovery mechanisms thoroughly

### Logging and Audit
- Log all trading activities
- Separate logs by activity type
- Include sufficient context in logs
- Implement log rotation and archival

## Next Steps

Complete your advanced order management education:

- **[Order Strategies & Combinations](order-strategies.md)** - Bracket orders and advanced techniques
- **[Validation & Best Practices](validation-best-practices.md)** - Risk management and error handling

## Key Takeaways

1. **Rule-based systems** enable consistent, disciplined order management
2. **Automated monitoring** provides real-time oversight and risk control
3. **Event-driven architecture** creates responsive, scalable trading systems
4. **Intelligent error recovery** maintains system reliability and uptime
5. **Comprehensive logging** supports compliance, debugging, and analysis
6. **Modular design** enables flexible and maintainable automation systems

Master these automated system techniques to build professional-grade trading infrastructure that operates reliably with minimal manual intervention while maintaining strict risk controls and comprehensive audit trails.