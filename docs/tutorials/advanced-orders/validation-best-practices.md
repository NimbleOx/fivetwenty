# Validation & Best Practices

Master comprehensive risk management, error handling, and validation systems for robust order management in production trading environments.

## Learning Objectives

By the end of this guide, you will:

- Implement comprehensive order validation systems
- Build robust error handling and recovery mechanisms
- Design risk management frameworks
- Create testing and quality assurance processes
- Establish production-ready monitoring and alerting

## Comprehensive Order Validation

Build validation systems that prevent costly trading errors before they occur.

### Pre-Order Validation Framework

```python
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Any, Dict, List, Optional

from fivetwenty import AsyncClient


class ValidationSeverity(Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

@dataclass
class ValidationResult:
    is_valid: bool
    severity: ValidationSeverity
    rule_name: str
    message: str
    details: dict[str, Any] | None = None

class OrderValidator(ABC):
    """Base class for order validation rules."""

    def __init__(self, name: str, severity: ValidationSeverity = ValidationSeverity.ERROR):
        self.name = name
        self.severity = severity
        self.enabled = True

    @abstractmethod
    async def validate(self, order_params: dict[str, Any], context: dict[str, Any]) -> ValidationResult:
        """Validate order parameters and return result."""
        pass

class OrderValidationFramework:
    def __init__(self, client: AsyncClient, account_id: str):
        self.client = client
        self.account_id = account_id
        self.validators: list[OrderValidator] = []
        self.validation_history = []

    def add_validator(self, validator: OrderValidator):
        """Add a validator to the framework."""
        self.validators.append(validator)

    async def validate_order(
        self,
        order_params: dict[str, Any],
        strict_mode: bool = True,
    ) -> dict[str, Any]:
        """Validate order against all registered validators."""

        validation_session = {
            "timestamp": datetime.utcnow(),
            "order_params": order_params,
            "results": [],
            "passed": True,
            "errors": [],
            "warnings": [],
        }

        # Build context for validators
        context = await self._build_validation_context()

        # Run all validators
        for validator in self.validators:
            if not validator.enabled:
                continue

            try:
                result = await validator.validate(order_params, context)
                validation_session["results"].append(result)

                if not result.is_valid:
                    if result.severity in [ValidationSeverity.ERROR, ValidationSeverity.CRITICAL]:
                        validation_session["errors"].append(result)
                        validation_session["passed"] = False
                    elif result.severity == ValidationSeverity.WARNING:
                        validation_session["warnings"].append(result)
                        if strict_mode:
                            validation_session["passed"] = False

            except Exception as e:
                error_result = ValidationResult(
                    is_valid=False,
                    severity=ValidationSeverity.CRITICAL,
                    rule_name=validator.name,
                    message=f"Validator failed: {e}",
                    details={"exception": str(e)},
                )
                validation_session["results"].append(error_result)
                validation_session["errors"].append(error_result)
                validation_session["passed"] = False

        # Store validation history
        self.validation_history.append(validation_session)

        return validation_session

    async def _build_validation_context(self) -> dict[str, Any]:
        """Build context information for validators."""
        try:
            # Get account information
            account = await self.client.accounts.get_account(account_id=self.account_id)

            # Get current positions
            positions = await self.client.positions.get_positions(account_id=self.account_id)

            # Get pending orders
            orders = await self.client.orders.get_orders(account_id=self.account_id)

            context = {
                "account": account,
                "positions": positions.positions,
                "pending_orders": orders.orders,
                "current_time": datetime.utcnow(),
                "account_balance": Decimal(account.balance),
                "margin_available": Decimal(account.margin_available),
                "margin_used": Decimal(account.margin_used),
            }

            return context

        except Exception as e:
            print(f"Failed to build validation context: {e}")
            return {"error": str(e)}
```

### Specific Validation Rules

#### Risk-Based Validators

```python
from decimal import Decimal

class MaxPositionSizeValidator(OrderValidator):
    """Validate order doesn't exceed maximum position size limits."""

    def __init__(self, max_units_per_instrument: int, max_total_exposure: Decimal):
        super().__init__("MaxPositionSize", ValidationSeverity.ERROR)
        self.max_units_per_instrument = max_units_per_instrument
        self.max_total_exposure = max_total_exposure

    async def validate(self, order_params: Dict[str, Any], context: Dict[str, Any]) -> ValidationResult:
        """Validate position size limits."""

        instrument = order_params.get("instrument")
        units = order_params.get("units", 0)

        # Check individual instrument limit
        current_position_size = 0
        for position in context.get("positions", []):
            if position.instrument == instrument:
                if position.long.units != "0":
                    current_position_size += int(position.long.units)
                if position.short.units != "0":
                    current_position_size += abs(int(position.short.units))

        new_position_size = current_position_size + abs(units)

        if new_position_size > self.max_units_per_instrument:
            return ValidationResult(
                is_valid=False,
                severity=self.severity,
                rule_name=self.name,
                message=f"Position size {new_position_size} exceeds limit {self.max_units_per_instrument}",
                details={
                    "current_size": current_position_size,
                    "order_size": abs(units),
                    "new_size": new_position_size,
                    "limit": self.max_units_per_instrument
                }
            )

        # Check total exposure limit
        total_exposure = sum(
            abs(int(pos.long.units)) + abs(int(pos.short.units))
            for pos in context.get("positions", [])
            if pos.long.units != "0" or pos.short.units != "0"
        )

        if total_exposure + abs(units) > self.max_total_exposure:
            return ValidationResult(
                is_valid=False,
                severity=self.severity,
                rule_name=self.name,
                message=f"Total exposure would exceed limit",
                details={
                    "current_exposure": total_exposure,
                    "order_size": abs(units),
                    "limit": self.max_total_exposure
                }
            )

        return ValidationResult(
            is_valid=True,
            severity=ValidationSeverity.INFO,
            rule_name=self.name,
            message="Position size validation passed"
        )

class MarginRequirementValidator(OrderValidator):
    """Validate sufficient margin for order."""

    def __init__(self, margin_buffer: Decimal = Decimal("0.1")):
        super().__init__("MarginRequirement", ValidationSeverity.ERROR)
        self.margin_buffer = margin_buffer  # 10% buffer

    async def validate(self, order_params: Dict[str, Any], context: Dict[str, Any]) -> ValidationResult:
        """Validate margin requirements."""

        units = abs(order_params.get("units", 0))
        instrument = order_params.get("instrument")

        # Estimate margin required (simplified calculation)
        # In practice, you'd use OANDA's margin calculation API
        leverage = Decimal("50")  # Assume 50:1 leverage for majors
        notional_value = Decimal(units)
        estimated_margin = notional_value / leverage

        margin_available = context.get("margin_available", Decimal("0"))
        required_margin = estimated_margin * (Decimal("1") + self.margin_buffer)

        if margin_available < required_margin:
            return ValidationResult(
                is_valid=False,
                severity=self.severity,
                rule_name=self.name,
                message=f"Insufficient margin: need {required_margin}, have {margin_available}",
                details={
                    "margin_available": margin_available,
                    "margin_required": required_margin,
                    "estimated_margin": estimated_margin,
                    "margin_buffer": self.margin_buffer
                }
            )

        return ValidationResult(
            is_valid=True,
            severity=ValidationSeverity.INFO,
            rule_name=self.name,
            message="Margin requirement validation passed"
        )

class RiskPerTradeValidator(OrderValidator):
    """Validate risk per trade doesn't exceed limits."""

    def __init__(self, max_risk_per_trade: Decimal):
        super().__init__("RiskPerTrade", ValidationSeverity.WARNING)
        self.max_risk_per_trade = max_risk_per_trade

    async def validate(self, order_params: Dict[str, Any], context: Dict[str, Any]) -> ValidationResult:
        """Validate risk per trade."""

        units = order_params.get("units", 0)
        entry_price = order_params.get("price")
        stop_price = order_params.get("stop_loss_price")

        if not entry_price or not stop_price:
            return ValidationResult(
                is_valid=True,
                severity=ValidationSeverity.INFO,
                rule_name=self.name,
                message="No stop loss specified - cannot validate risk"
            )

        # Calculate risk amount
        stop_distance = abs(Decimal(str(entry_price)) - Decimal(str(stop_price)))
        risk_amount = abs(units) * stop_distance

        account_balance = context.get("account_balance", Decimal("0"))
        risk_percentage = risk_amount / account_balance if account_balance > 0 else Decimal("1")

        if risk_percentage > self.max_risk_per_trade:
            return ValidationResult(
                is_valid=False,
                severity=self.severity,
                rule_name=self.name,
                message=f"Risk {risk_percentage:.2%} exceeds limit {self.max_risk_per_trade:.2%}",
                details={
                    "risk_amount": risk_amount,
                    "risk_percentage": risk_percentage,
                    "limit": self.max_risk_per_trade,
                    "account_balance": account_balance
                }
            )

        return ValidationResult(
            is_valid=True,
            severity=ValidationSeverity.INFO,
            rule_name=self.name,
            message=f"Risk validation passed: {risk_percentage:.2%}"
        )
```

#### Market Condition Validators

```python
from datetime import datetime
from decimal import Decimal


class SpreadValidator(OrderValidator):
    """Validate spread isn't too wide for order execution."""

    def __init__(self, max_spread_pips: Decimal):
        super().__init__("SpreadValidation", ValidationSeverity.WARNING)
        self.max_spread_pips = max_spread_pips

    async def validate(self, order_params: Dict[str, Any], context: Dict[str, Any]) -> ValidationResult:
        """Validate current spread."""

        instrument = order_params.get("instrument")

        try:
            # Get current pricing
            pricing = await context["client"].pricing.get_pricing(
                account_id=context["account_id"],
                instruments=[instrument],
            )

            ask_price = Decimal(pricing.prices[0].asks[0].price)
            bid_price = Decimal(pricing.prices[0].bids[0].price)
            spread = ask_price - bid_price

            # Convert to pips (assume 4-decimal currency pair)
            pip_value = Decimal("0.0001")
            spread_pips = spread / pip_value

            if spread_pips > self.max_spread_pips:
                return ValidationResult(
                    is_valid=False,
                    severity=self.severity,
                    rule_name=self.name,
                    message=f"Spread {spread_pips:.1f} pips exceeds limit {self.max_spread_pips}",
                    details={
                        "current_spread": spread,
                        "spread_pips": spread_pips,
                        "limit": self.max_spread_pips,
                        "ask": ask_price,
                        "bid": bid_price,
                    },
                )

            return ValidationResult(
                is_valid=True,
                severity=ValidationSeverity.INFO,
                rule_name=self.name,
                message=f"Spread validation passed: {spread_pips:.1f} pips",
            )

        except Exception as e:
            return ValidationResult(
                is_valid=False,
                severity=ValidationSeverity.ERROR,
                rule_name=self.name,
                message=f"Failed to check spread: {e}",
            )

class MarketHoursValidator(OrderValidator):
    """Validate market is open for the instrument."""

    def __init__(self):
        super().__init__("MarketHours", ValidationSeverity.WARNING)

    async def validate(self, order_params: Dict[str, Any], context: Dict[str, Any]) -> ValidationResult:
        """Validate market hours."""

        instrument = order_params.get("instrument")
        current_time = datetime.now(timezone.utc)

        # Simplified market hours check
        # In practice, you'd check specific instrument trading hours
        weekend = current_time.weekday() >= 5  # Saturday = 5, Sunday = 6

        if weekend:
            return ValidationResult(
                is_valid=False,
                severity=self.severity,
                rule_name=self.name,
                message="Market closed - weekend trading not available",
                details={
                    "current_time": current_time.isoformat(),
                    "weekday": current_time.weekday(),
                },
            )

        # Check for major market holidays (simplified)
        # In practice, you'd have a comprehensive holiday calendar

        return ValidationResult(
            is_valid=True,
            severity=ValidationSeverity.INFO,
            rule_name=self.name,
            message="Market hours validation passed",
        )
```

#### Technical Validators

```python
from decimal import Decimal


class PriceValidityValidator(OrderValidator):
    """Validate order price is reasonable relative to current market."""

    def __init__(self, max_price_deviation: Decimal = Decimal("0.05")):
        super().__init__("PriceValidity", ValidationSeverity.ERROR)
        self.max_price_deviation = max_price_deviation  # 5% max deviation

    async def validate(self, order_params: Dict[str, Any], context: Dict[str, Any]) -> ValidationResult:
        """Validate order price."""

        order_type = order_params.get("type")
        if order_type == "MARKET":
            return ValidationResult(
                is_valid=True,
                severity=ValidationSeverity.INFO,
                rule_name=self.name,
                message="Market order - no price validation needed",
            )

        order_price = order_params.get("price")
        instrument = order_params.get("instrument")

        if not order_price:
            return ValidationResult(
                is_valid=False,
                severity=self.severity,
                rule_name=self.name,
                message="No price specified for non-market order",
            )

        try:
            # Get current market price
            pricing = await context["client"].pricing.get_pricing(
                account_id=context["account_id"],
                instruments=[instrument],
            )

            mid_price = (
                Decimal(pricing.prices[0].asks[0].price) +
                Decimal(pricing.prices[0].bids[0].price)
            ) / Decimal("2")

            price_diff = abs(Decimal(str(order_price)) - mid_price)
            price_deviation = price_diff / mid_price

            if price_deviation > self.max_price_deviation:
                return ValidationResult(
                    is_valid=False,
                    severity=self.severity,
                    rule_name=self.name,
                    message=f"Order price deviates {price_deviation:.2%} from market",
                    details={
                        "order_price": order_price,
                        "market_price": mid_price,
                        "deviation": price_deviation,
                        "limit": self.max_price_deviation,
                    },
                )

            return ValidationResult(
                is_valid=True,
                severity=ValidationSeverity.INFO,
                rule_name=self.name,
                message="Price validity validation passed",
            )

        except Exception as e:
            return ValidationResult(
                is_valid=False,
                severity=ValidationSeverity.ERROR,
                rule_name=self.name,
                message=f"Failed to validate price: {e}",
            )

class OrderParametersValidator(OrderValidator):
    """Validate order parameters are properly formatted."""

    def __init__(self):
        super().__init__("OrderParameters", ValidationSeverity.ERROR)

    async def validate(self, order_params: Dict[str, Any], context: Dict[str, Any]) -> ValidationResult:
        """Validate order parameters."""

        required_params = ["instrument", "units", "type"]
        missing_params = [param for param in required_params if param not in order_params]

        if missing_params:
            return ValidationResult(
                is_valid=False,
                severity=self.severity,
                rule_name=self.name,
                message=f"Missing required parameters: {missing_params}",
                details={"missing_params": missing_params},
            )

        # Validate instrument format
        instrument = order_params.get("instrument")
        if "_" not in instrument:
            return ValidationResult(
                is_valid=False,
                severity=self.severity,
                rule_name=self.name,
                message=f"Invalid instrument format: {instrument}",
            )

        # Validate units
        units = order_params.get("units")
        if not isinstance(units, int) or units == 0:
            return ValidationResult(
                is_valid=False,
                severity=self.severity,
                rule_name=self.name,
                message=f"Invalid units: {units}",
            )

        # Validate order type
        valid_types = ["MARKET", "LIMIT", "STOP", "MARKET_IF_TOUCHED"]
        order_type = order_params.get("type")
        if order_type not in valid_types:
            return ValidationResult(
                is_valid=False,
                severity=self.severity,
                rule_name=self.name,
                message=f"Invalid order type: {order_type}",
            )

        return ValidationResult(
            is_valid=True,
            severity=ValidationSeverity.INFO,
            rule_name=self.name,
            message="Parameter validation passed",
        )
```

## Error Handling and Recovery

Build robust error handling systems for production trading.

### Comprehensive Error Handler

```python
from datetime import datetime
from fivetwenty import AsyncClient
from enum import Enum
from typing import Callable, Optional
import traceback

class ErrorCategory(Enum):
    NETWORK = "network"
    AUTHENTICATION = "authentication"
    VALIDATION = "validation"
    MARKET_DATA = "market_data"
    ORDER_EXECUTION = "order_execution"
    INSUFFICIENT_FUNDS = "insufficient_funds"
    RATE_LIMITING = "rate_limiting"
    SYSTEM = "system"

class TradingErrorHandler:
    def __init__(self, client: AsyncClient, account_id: str):
        self.client = client
        self.account_id = account_id
        self.error_handlers = {}
        self.error_history = []
        self.circuit_breaker_states = {}

    def register_error_handler(
        self,
        error_category: ErrorCategory,
        handler: Callable,
        max_retries: int = 3,
        retry_delay: int = 1
    ):
        """Register error handler for specific error category."""
        self.error_handlers[error_category] = {
            "handler": handler,
            "max_retries": max_retries,
            "retry_delay": retry_delay
        }

    async def handle_error(
        self,
        error: Exception,
        operation_context: Dict[str, Any],
        error_category: Optional[ErrorCategory] = None
    ) -> Dict[str, Any]:
        """Handle error with appropriate recovery strategy."""

        # Categorize error if not provided
        if not error_category:
            error_category = self._categorize_error(error)

        # Record error
        error_record = {
            "timestamp": datetime.utcnow(),
            "error_type": type(error).__name__,
            "error_message": str(error),
            "error_category": error_category,
            "operation_context": operation_context,
            "stack_trace": traceback.format_exc(),
            "recovery_attempted": False,
            "recovery_successful": False
        }

        self.error_history.append(error_record)

        # Check circuit breaker
        if self._should_circuit_break(error_category):
            error_record["circuit_breaker_triggered"] = True
            return error_record

        # Attempt recovery
        if error_category in self.error_handlers:
            handler_config = self.error_handlers[error_category]

            for attempt in range(handler_config["max_retries"]):
                try:
                    error_record["recovery_attempted"] = True
                    recovery_result = await handler_config["handler"](
                        error, operation_context, attempt
                    )

                    if recovery_result.get("success", False):
                        error_record["recovery_successful"] = True
                        error_record["recovery_result"] = recovery_result
                        break

                    await asyncio.sleep(handler_config["retry_delay"] * (2 ** attempt))

                except Exception as recovery_error:
                    error_record["recovery_error"] = str(recovery_error)

        return error_record

    def _categorize_error(self, error: Exception) -> ErrorCategory:
        """Categorize error based on type and message."""

        error_message = str(error).lower()
        error_type = type(error).__name__

        if "network" in error_message or "connection" in error_message:
            return ErrorCategory.NETWORK

        if "authentication" in error_message or "unauthorized" in error_message:
            return ErrorCategory.AUTHENTICATION

        if "insufficient" in error_message and "margin" in error_message:
            return ErrorCategory.INSUFFICIENT_FUNDS

        if "rate limit" in error_message or "too many requests" in error_message:
            return ErrorCategory.RATE_LIMITING

        if "validation" in error_message or "invalid" in error_message:
            return ErrorCategory.VALIDATION

        if isinstance(error, VeeTwentyError):
            return ErrorCategory.ORDER_EXECUTION

        return ErrorCategory.SYSTEM

    def _should_circuit_break(self, error_category: ErrorCategory) -> bool:
        """Determine if circuit breaker should trigger."""

        # Simple circuit breaker logic
        recent_errors = [
            err for err in self.error_history[-10:]  # Last 10 errors
            if err["error_category"] == error_category
            and (datetime.utcnow() - err["timestamp"]).seconds < 300  # Last 5 minutes
        ]

        # Break circuit if too many errors of same category
        return len(recent_errors) >= 5

# Error handler implementations
async def network_error_handler(
    error: Exception,
    context: Dict[str, Any],
    attempt: int
) -> Dict[str, Any]:
    """Handle network-related errors."""

    print(f"Network error attempt {attempt + 1}: {error}")

    # Wait longer on each retry
    await asyncio.sleep(2 ** attempt)

    # Test connection
    try:
        client = context["client"]
        await client.accounts.get_account(account_id=context["account_id"])
        return {"success": True, "action": "connection_restored"}
    except Exception:
        return {"success": False, "action": "connection_still_failed"}

async def insufficient_funds_handler(
    error: Exception,
    context: Dict[str, Any],
    attempt: int
) -> Dict[str, Any]:
    """Handle insufficient funds errors."""

    print(f"Insufficient funds - reducing position size")

    # Reduce order size
    original_units = context.get("units", 0)
    reduced_units = int(original_units * (0.8 ** (attempt + 1)))  # Reduce by 20% each attempt

    if reduced_units < 1000:  # Minimum viable position
        return {"success": False, "action": "position_too_small"}

    context["units"] = reduced_units

    return {
        "success": True,
        "action": "position_size_reduced",
        "original_units": original_units,
        "new_units": reduced_units
    }

async def rate_limit_handler(
    error: Exception,
    context: Dict[str, Any],
    attempt: int
) -> Dict[str, Any]:
    """Handle rate limiting errors."""

    # Exponential backoff for rate limits
    wait_time = 5 * (2 ** attempt)
    print(f"Rate limited - waiting {wait_time} seconds")

    await asyncio.sleep(wait_time)

    return {"success": True, "action": "rate_limit_wait_completed"}
```

## Risk Management Framework

Implement comprehensive risk controls for trading operations.

### Real-Time Risk Monitor

```python
from datetime import datetime
from decimal import Decimal

from fivetwenty import AsyncClient


class RealTimeRiskMonitor:
    def __init__(self, client: AsyncClient, account_id: str):
        self.client = client
        self.account_id = account_id
        self.risk_limits = {}
        self.monitoring_active = False
        self.risk_violations = []

    def set_risk_limits(self, limits: Dict[str, Any]):
        """Set risk limits for monitoring."""
        self.risk_limits.update(limits)

    async def start_monitoring(self, check_interval: int = 30):
        """Start real-time risk monitoring."""
        self.monitoring_active = True

        while self.monitoring_active:
            try:
                await self._check_all_risk_limits()
                await asyncio.sleep(check_interval)
            except Exception as e:
                print(f"Risk monitoring error: {e}")
                await asyncio.sleep(check_interval)

    async def _check_all_risk_limits(self):
        """Check all risk limits against current positions."""

        # Get current account state
        account = await self.client.accounts.get_account(account_id=self.account_id)
        positions = await self.client.positions.get_positions(account_id=self.account_id)

        risk_metrics = await self._calculate_risk_metrics(account, positions.positions)

        # Check each limit
        for limit_name, limit_value in self.risk_limits.items():
            current_value = risk_metrics.get(limit_name)

            if current_value is not None and current_value > limit_value:
                violation = {
                    "timestamp": datetime.utcnow(),
                    "limit_name": limit_name,
                    "limit_value": limit_value,
                    "current_value": current_value,
                    "severity": "HIGH" if current_value > limit_value * 1.2 else "MEDIUM",
                }

                self.risk_violations.append(violation)
                await self._handle_risk_violation(violation)

    async def _calculate_risk_metrics(
        self,
        account,
        positions: List[Any],
    ) -> Dict[str, Decimal]:
        """Calculate current risk metrics."""

        metrics = {}

        # Calculate total exposure
        total_exposure = Decimal("0")
        total_unrealized_pl = Decimal("0")

        for position in positions:
            if position.long.units != "0":
                total_exposure += abs(Decimal(position.long.units))
                total_unrealized_pl += Decimal(position.long.unrealized_pl or "0")

            if position.short.units != "0":
                total_exposure += abs(Decimal(position.short.units))
                total_unrealized_pl += Decimal(position.short.unrealized_pl or "0")

        account_balance = Decimal(account.balance)

        metrics.update({
            "total_exposure": total_exposure,
            "account_balance": account_balance,
            "unrealized_pl": total_unrealized_pl,
            "drawdown_percent": abs(total_unrealized_pl) / account_balance * 100 if total_unrealized_pl < 0 else Decimal("0"),
            "margin_used_percent": Decimal(account.margin_used) / account_balance * 100,
            "exposure_to_balance_ratio": total_exposure / account_balance,
        })

        return metrics

    async def _handle_risk_violation(self, violation: Dict[str, Any]):
        """Handle risk limit violation."""

        print(f"RISK VIOLATION: {violation['limit_name']} = {violation['current_value']} "
              f"(limit: {violation['limit_value']})")

        # Implement emergency procedures based on violation type
        if violation["limit_name"] == "drawdown_percent" and violation["severity"] == "HIGH":
            await self._emergency_position_reduction()

        elif violation["limit_name"] == "total_exposure" and violation["severity"] == "HIGH":
            await self._halt_new_orders()

    async def _emergency_position_reduction(self):
        """Emergency position reduction procedure."""

        print("EMERGENCY: Reducing all positions by 50%")

        positions = await self.client.positions.get_positions(account_id=self.account_id)

        for position in positions.positions:
            try:
                if position.long.units != "0":
                    # Reduce long position by 50%
                    units_to_close = int(Decimal(position.long.units) * Decimal("0.5"))
                    await self.client.orders.post_market_order(
                        account_id=self.account_id,
                        instrument=position.instrument,
                        units=-units_to_close,
                        time_in_force="FOK",
                    )

                if position.short.units != "0":
                    # Reduce short position by 50%
                    units_to_close = int(abs(Decimal(position.short.units)) * Decimal("0.5"))
                    await self.client.orders.post_market_order(
                        account_id=self.account_id,
                        instrument=position.instrument,
                        units=units_to_close,
                        time_in_force="FOK",
                    )

            except Exception as e:
                print(f"Failed to reduce position {position.instrument}: {e}")

    async def _halt_new_orders(self):
        """Halt all new order placement."""

        print("EMERGENCY: Halting all new orders")

        # Cancel all pending orders
        orders = await self.client.orders.get_orders(account_id=self.account_id)

        for order in orders.orders:
            if order.state == "PENDING":
                try:
                    await self.client.orders.cancel_order(
                        account_id=self.account_id,
                        order_id=order.id,
                    )
                except Exception as e:
                    print(f"Failed to cancel order {order.id}: {e}")
```

## Testing and Quality Assurance

Implement comprehensive testing for order management systems.

### Order Testing Framework

```python
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock


class OrderSystemTestFramework:
    """Framework for testing order management systems."""

    def __init__(self):
        self.mock_client = None
        self.test_results = []

    def setup_mock_client(self):
        """Set up mock client for testing."""
        self.mock_client = AsyncMock()

        # Mock account data
        mock_account = MagicMock()
        mock_account.balance = "10000.0"
        mock_account.margin_available = "8000.0"
        mock_account.margin_used = "2000.0"

        self.mock_client.accounts.get_account.return_value = mock_account

        # Mock pricing data
        mock_pricing = MagicMock()
        mock_pricing.prices = [MagicMock()]
        mock_pricing.prices[0].asks = [MagicMock()]
        mock_pricing.prices[0].bids = [MagicMock()]
        mock_pricing.prices[0].asks[0].price = "1.0850"
        mock_pricing.prices[0].bids[0].price = "1.0848"

        self.mock_client.pricing.get_pricing.return_value = mock_pricing

        # Mock order responses
        mock_order_response = MagicMock()
        mock_order_response.order_create_transaction.id = "test_order_123"

        self.mock_client.orders.post_market_order.return_value = mock_order_response
        self.mock_client.orders.post_limit_order.return_value = mock_order_response

        return self.mock_client

    async def test_validation_framework(self):
        """Test order validation framework."""

        client = self.setup_mock_client()
        validator_framework = OrderValidationFramework(client, "test_account")

        # Add test validators
        validator_framework.add_validator(
            MaxPositionSizeValidator(50000, Decimal("100000")),
        )
        validator_framework.add_validator(PriceValidityValidator())

        # Test valid order
        valid_order = {
            "instrument": "EUR_USD",
            "units": 10000,
            "type": "LIMIT",
            "price": Decimal("1.0850"),
        }

        result = await validator_framework.validate_order(valid_order)

        assert result["passed"] == True
        assert len(result["errors"]) == 0

        # Test invalid order (too large)
        invalid_order = {
            "instrument": "EUR_USD",
            "units": 200000,  # Exceeds limit
            "type": "LIMIT",
            "price": Decimal("1.0850"),
        }

        result = await validator_framework.validate_order(invalid_order)

        assert result["passed"] == False
        assert len(result["errors"]) > 0

        print("Validation framework tests passed")

    async def test_error_handling(self):
        """Test error handling system."""

        client = self.setup_mock_client()
        error_handler = TradingErrorHandler(client, "test_account")

        # Register test handlers
        error_handler.register_error_handler(
            ErrorCategory.INSUFFICIENT_FUNDS,
            insufficient_funds_handler,
        )

        # Test error handling
        test_error = Exception("Insufficient margin")
        context = {"units": 50000, "client": client, "account_id": "test_account"}

        result = await error_handler.handle_error(
            test_error,
            context,
            ErrorCategory.INSUFFICIENT_FUNDS,
        )

        assert result["recovery_attempted"] == True
        print("Error handling tests passed")

    async def test_risk_monitoring(self):
        """Test risk monitoring system."""

        client = self.setup_mock_client()
        risk_monitor = RealTimeRiskMonitor(client, "test_account")

        # Set test limits
        risk_monitor.set_risk_limits({
            "drawdown_percent": Decimal("5.0"),
            "total_exposure": Decimal("50000"),
        })

        # Test risk calculation
        account = await client.accounts.get_account(account_id="test_account")

        # Mock positions with high risk
        mock_positions = MagicMock()
        mock_positions.positions = []

        risk_metrics = await risk_monitor._calculate_risk_metrics(
            account,
            mock_positions.positions,
        )

        assert "total_exposure" in risk_metrics
        assert "drawdown_percent" in risk_metrics

        print("Risk monitoring tests passed")

    async def run_all_tests(self):
        """Run all test suites."""

        test_suites = [
            self.test_validation_framework,
            self.test_error_handling,
            self.test_risk_monitoring,
        ]

        for test_suite in test_suites:
            try:
                await test_suite()
                self.test_results.append({
                    "test": test_suite.__name__,
                    "status": "PASSED",
                })
            except Exception as e:
                self.test_results.append({
                    "test": test_suite.__name__,
                    "status": "FAILED",
                    "error": str(e),
                })

        # Print results
        print("\nTest Results:")
        for result in self.test_results:
            status = result["status"]
            test_name = result["test"]
            print(f"{test_name}: {status}")

            if status == "FAILED":
                print(f"  Error: {result['error']}")

# Usage
async def run_tests():
    test_framework = OrderSystemTestFramework()
    await test_framework.run_all_tests()
```

## Production Monitoring and Alerting

Establish comprehensive monitoring for production trading systems.

### Production Monitoring System

```python
from datetime import datetime
from decimal import Decimal

from fivetwenty import AsyncClient


class ProductionMonitoringSystem:
    """Comprehensive monitoring system for production trading."""

    def __init__(self, client: AsyncClient, account_id: str):
        self.client = client
        self.account_id = account_id
        self.monitoring_active = False
        self.alert_channels = []
        self.metrics_history = []

    def add_alert_channel(self, channel):
        """Add alert delivery channel."""
        self.alert_channels.append(channel)

    async def start_monitoring(self):
        """Start comprehensive production monitoring."""
        self.monitoring_active = True

        # Start monitoring tasks
        tasks = [
            asyncio.create_task(self._monitor_system_health()),
            asyncio.create_task(self._monitor_trading_performance()),
            asyncio.create_task(self._monitor_risk_metrics()),
            asyncio.create_task(self._monitor_order_execution()),
        ]

        await asyncio.gather(*tasks)

    async def _monitor_system_health(self):
        """Monitor system health metrics."""

        while self.monitoring_active:
            try:
                # Test API connectivity
                start_time = datetime.utcnow()
                await self.client.accounts.get_account(account_id=self.account_id)
                response_time = (datetime.utcnow() - start_time).total_seconds()

                if response_time > 5.0:  # 5-second threshold
                    await self._send_alert({
                        "type": "SLOW_API_RESPONSE",
                        "response_time": response_time,
                        "threshold": 5.0,
                    })

                # Monitor memory usage, CPU, etc.
                # Implementation would include system resource monitoring

            except Exception as e:
                await self._send_alert({
                    "type": "API_CONNECTION_FAILED",
                    "error": str(e),
                })

            await asyncio.sleep(60)  # Check every minute

    async def _monitor_trading_performance(self):
        """Monitor trading performance metrics."""

        while self.monitoring_active:
            try:
                # Calculate performance metrics
                account = await self.client.accounts.get_account(account_id=self.account_id)

                performance_metrics = {
                    "timestamp": datetime.utcnow(),
                    "account_balance": Decimal(account.balance),
                    "unrealized_pl": Decimal(account.unrealized_pl or "0"),
                    "margin_used": Decimal(account.margin_used),
                    "margin_available": Decimal(account.margin_available),
                }

                self.metrics_history.append(performance_metrics)

                # Check for significant changes
                if len(self.metrics_history) > 1:
                    prev_metrics = self.metrics_history[-2]
                    balance_change = (
                        performance_metrics["account_balance"] -
                        prev_metrics["account_balance"]
                    )

                    # Alert on large losses
                    if balance_change < -Decimal("500"):  # $500 loss threshold
                        await self._send_alert({
                            "type": "LARGE_LOSS",
                            "balance_change": balance_change,
                            "current_balance": performance_metrics["account_balance"],
                        })

            except Exception as e:
                print(f"Performance monitoring error: {e}")

            await asyncio.sleep(300)  # Check every 5 minutes

    async def _send_alert(self, alert_data: Dict[str, Any]):
        """Send alert through all configured channels."""

        for channel in self.alert_channels:
            try:
                await channel.send_alert(alert_data)
            except Exception as e:
                print(f"Failed to send alert via {channel}: {e}")

# Alert channel implementations
class EmailAlertChannel:
    def __init__(self, email_config: Dict[str, str]):
        self.email_config = email_config

    async def send_alert(self, alert_data: Dict[str, Any]):
        """Send alert via email."""
        # Implementation would integrate with email service
        print(f"EMAIL ALERT: {alert_data}")

class SlackAlertChannel:
    def __init__(self, webhook_url: str):
        self.webhook_url = webhook_url

    async def send_alert(self, alert_data: Dict[str, Any]):
        """Send alert via Slack."""
        # Implementation would integrate with Slack API
        print(f"SLACK ALERT: {alert_data}")
```

## Best Practices Summary

### Validation Systems
- Implement comprehensive pre-order validation
- Use multiple validation layers (technical, risk, market)
- Maintain validation history for analysis
- Enable strict mode for production environments

### Error Handling
- Categorize errors for appropriate handling
- Implement circuit breakers for critical errors
- Use exponential backoff for retries
- Maintain detailed error logs and recovery attempts

### Risk Management
- Monitor risk metrics in real-time
- Implement automatic risk controls and limits
- Use emergency procedures for critical violations
- Maintain audit trails for all risk actions

### Testing and QA
- Test all validation rules thoroughly
- Mock external dependencies for unit testing
- Implement integration tests with recorded data
- Maintain comprehensive test coverage

### Production Monitoring
- Monitor system health continuously
- Track trading performance metrics
- Implement multiple alert channels
- Maintain historical monitoring data

## Key Takeaways

1. **Comprehensive validation** prevents costly trading errors before they occur
2. **Robust error handling** ensures system reliability and automatic recovery
3. **Real-time risk monitoring** protects against catastrophic losses
4. **Thorough testing** validates system behavior under all conditions
5. **Production monitoring** provides visibility into system performance and health
6. **Defense in depth** using multiple validation and control layers ensures robust operation

Master these validation and best practices to build production-ready trading systems that operate reliably under all market conditions with comprehensive risk controls and monitoring capabilities.

## Course Completion

Congratulations! You have completed the Advanced Order Types tutorial series. You now have the knowledge and tools to build sophisticated, professional-grade order management systems with:

- **Complete order type mastery** for all market conditions
- **Advanced execution strategies** including trailing stops and scaling
- **Automated systems** with rule-based management
- **Sophisticated combinations** like bracket orders and hedging strategies
- **Production-ready validation** and risk management frameworks

Continue your trading system development by exploring other tutorial series focusing on streaming data, portfolio analysis, and production deployment strategies.