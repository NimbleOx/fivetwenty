# Risk Management with FiveTwenty

Learn essential risk management techniques using FiveTwenty's stop loss orders, position monitoring, and account controls.

!!! success "Target Practical Guide - Problem-oriented solutions"
    **Use this guide when:** You need to protect trading capital and control position risk

    **Learning outcome:** Implement risk controls using FiveTwenty SDK features

    **Time commitment:** 30-40 minutes

## Prerequisites

- Completed [Basic Trading](basic-trading/index.md) tutorial
- Understanding of position management concepts
- FiveTwenty setup with live or practice account

## Essential Risk Controls

### Stop Loss Orders

<!-- fragment: Demo stop loss implementation with ternary operators and type annotation issues -->
```python
import asyncio
from decimal import Decimal
from fivetwenty import AsyncClient
from fivetwenty.models import (
    MarketOrderRequest,
    StopLossOrderRequest,
    TimeInForce
)

async def place_order_with_stop_loss(
    client: AsyncClient,
    account_id: str,
    instrument: str,
    units: Decimal,
    stop_loss_distance: Decimal
) -> dict:
    """Place market order with automatic stop loss protection for capital preservation."""

    # Step 1: Create market order with specific execution requirements
    # FOK (Fill or Kill) ensures order executes completely or not at all
    market_order = MarketOrderRequest(
        instrument=instrument,           # Currency pair to trade
        units=units,                    # Position size (positive=long, negative=short)
        time_in_force=TimeInForce.FOK,  # Fill completely or cancel immediately
    )

    # Step 2: Execute market order and await immediate fill response
    # This creates the primary trading position that needs protection
    order_response = await client.orders.post_order(account_id, market_order)

    # Step 3: Verify order execution and proceed with stop loss placement
    # Only add stop loss protection if the market order was successfully filled
    if order_response.order_fill_transaction:
        # Step 4: Extract actual fill price for precise stop loss calculation
        # Use the exact price we traded at, not the requested price
        fill_price = Decimal(order_response.order_fill_transaction.price)

        # Step 5: Calculate stop loss price based on position direction
        # Long positions need stops below entry, short positions need stops above
        if units > 0:  # Long position - protect against downward moves
            stop_price = fill_price - stop_loss_distance  # Stop below entry price
        else:  # Short position - protect against upward moves
            stop_price = fill_price + stop_loss_distance  # Stop above entry price

        # Step 6: Create stop loss order linked to the opened trade
        # GTC (Good Till Cancelled) keeps stop active until manually removed
        stop_loss = StopLossOrderRequest(
            tradeID=order_response.order_fill_transaction.tradeOpened.tradeID,  # Link to specific trade
            price=str(stop_price),    # Price level that triggers stop loss
            timeInForce="GTC"         # Remains active indefinitely
        )

        # Step 7: Submit stop loss order to provide automatic risk protection
        # This creates a safety net that executes without human intervention
        stop_response = await client.orders.post_order(account_id, stop_loss)

        # Step 8: Return comprehensive trade details for monitoring and management
        # This information enables position tracking and risk assessment
        return {
            "trade_id": order_response.order_fill_transaction.tradeOpened.tradeID,  # Primary trade identifier
            "entry_price": fill_price,              # Actual execution price achieved
            "stop_price": stop_price,               # Stop loss trigger level
            "stop_order_id": stop_response.order_create_transaction.id  # Stop order identifier
        }

    raise ValueError("Market order was not filled")

# Usage Example - Protected Trade Execution
async def main():
    """Demonstrate risk-managed trading with automatic stop loss protection."""

    # Step 1: Initialize client using environment-based authentication
    # Zero-config approach reads OANDA credentials from environment variables
    async with AsyncClient() as client:
        # Step 2: Execute trade with integrated stop loss protection
        # This combines position opening with immediate risk protection
        result = await place_order_with_stop_loss(
            client=client,                           # Authenticated FiveTwenty client
            account_id=client.account_id,           # Account from environment config
            instrument="EUR_USD",                   # Major currency pair with tight spreads
            units=Decimal("1000"),                  # Conservative position size (1,000 units)
            stop_loss_distance=Decimal("0.0020")   # 20 pips stop loss (2% protection)
        )

        # Step 3: Confirm successful execution with stop loss protection active
        print(f"Success Protected trade executed: ID {result['trade_id']}")
        print(f"   Entry Price: {result['entry_price']:.5f}")
        print(f"   Stop Loss: {result['stop_price']:.5f} (automatic protection active)")

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    asyncio.run(main())
```

### Position Size Based on Risk

<!-- fragment: Demo position sizing with attribute access and ternary operator patterns -->
```python
import asyncio
from decimal import Decimal

from fivetwenty import AsyncClient

async def calculate_risk_based_position_size(
    client: AsyncClient,
    account_id: str,
    instrument: str,
    risk_percentage: Decimal,  # e.g., Decimal("2") for 2%
    stop_loss_pips: int
) -> Decimal:
    """Calculate optimal position size based on account risk percentage and stop distance."""

    # Step 1: Retrieve current account balance for risk calculation base
    # Account balance represents total available capital for risk assessment
    account = await client.accounts.get_account(account_id)
    balance = Decimal(account.balance)  # Convert to Decimal for precise calculations

    # Step 2: Calculate maximum risk amount based on percentage of total capital
    # This ensures we never risk more than our predetermined risk tolerance
    risk_amount = balance * (risk_percentage / 100)  # Convert percentage to decimal

    # Step 3: Get current market price for accurate pip value calculation
    # Real-time pricing ensures position sizing reflects current market conditions
    pricing = await client.pricing.get_pricing(
        account_id=account_id,     # Account context for pricing
        instruments=[instrument]    # Single instrument for focused calculation
    )

    # Step 4: Extract ask price for long position calculations
    # Use ask price as it represents the cost to enter a long position
    current_price = Decimal(pricing.prices[0].asks[0].price)

    # Step 5: Calculate pip value based on currency pair characteristics
    # Different currency pairs have different pip values affecting risk calculations
    if "JPY" in instrument:
        pip_value = Decimal("0.01") / current_price    # Yen pairs use 0.01 as pip increment
    else:
        pip_value = Decimal("0.0001") / current_price  # Major pairs use 0.0001 as pip increment

    # Step 6: Calculate optimal position size using risk amount and stop distance
    # Position size = Risk Amount ÷ (Stop Distance × Pip Value)
    position_size = risk_amount / (stop_loss_pips * pip_value)

    # Step 7: Round to whole units for practical order execution
    # OANDA accepts whole unit increments for most currency pairs
    return position_size.quantize(Decimal("1"))
```

### Account Monitoring and Limits

<!-- fragment: Demo risk monitoring with attribute access and union type issues -->
```python
class RiskMonitor:
    """Monitor account risk metrics in real-time for automated risk management."""

    def __init__(self, client: AsyncClient, account_id: str):
        """Initialize risk monitoring with configurable safety thresholds."""
        self.client = client                        # Authenticated FiveTwenty client
        self.account_id = account_id               # Target account for monitoring
        self.max_daily_loss = Decimal("1000")     # Maximum acceptable daily loss ($1000)
        self.max_drawdown = Decimal("0.10")       # Maximum drawdown percentage (10%)
        self.daily_start_balance = None           # Baseline for daily P&L calculation

    async def check_risk_limits(self) -> dict:
        """Comprehensive risk assessment against predefined safety thresholds."""

        # Step 1: Retrieve current account state for risk evaluation
        # Account object contains balance, margin, and position information
        account = await self.client.accounts.get_account(self.account_id)
        current_balance = Decimal(account.balance)  # Current account equity

        # Step 2: Initialize daily baseline if this is the first check
        # Daily start balance serves as reference point for daily P&L calculation
        if self.daily_start_balance is None:
            self.daily_start_balance = current_balance

        # Step 3: Calculate daily profit and loss for performance tracking
        # Daily P&L = Current Balance - Starting Balance (positive = profit, negative = loss)
        daily_pnl = current_balance - self.daily_start_balance

        # Step 4: Calculate total market exposure across all open positions
        # Exposure measurement helps assess overall portfolio risk concentration
        positions = await self.client.positions.get_positions(self.client.account_id)
        total_exposure = Decimal("0")  # Initialize exposure counter

        # Step 5: Sum absolute position sizes for total market exposure
        # Both long and short positions contribute to overall market risk
        for position in positions.positions:
            if position.long.units != "0" or position.short.units != "0":
                # Calculate absolute position sizes (direction doesn't matter for exposure)
                long_units = abs(Decimal(position.long.units)) if position.long.units != "0" else Decimal("0")
                short_units = abs(Decimal(position.short.units)) if position.short.units != "0" else Decimal("0")
                total_exposure += long_units + short_units  # Accumulate total exposure

        # Step 6: Return comprehensive risk assessment with actionable flags
        # This dictionary provides all necessary information for risk-based decision making
        return {
            "current_balance": current_balance,                                    # Current account equity
            "daily_pnl": daily_pnl,                                              # Today's profit/loss
            "daily_loss_limit_breached": daily_pnl < -self.max_daily_loss,      # Emergency stop flag
            "drawdown_limit_breached": (self.daily_start_balance - current_balance) / self.daily_start_balance > self.max_drawdown,  # Drawdown warning
            "total_exposure": total_exposure,                                     # Total market exposure
            "margin_used": Decimal(account.margin_used),                         # Capital committed to positions
            "margin_available": Decimal(account.margin_available)                # Remaining trading capacity
        }

    async def emergency_close_all(self) -> list:
        """Emergency closure of all open positions to preserve capital."""

        # Step 1: Retrieve all current positions for emergency closure
        # This ensures we close every open position without exception
        positions = await self.client.positions.get_positions(self.client.account_id)
        closed_positions = []  # Track successful closures for reporting

        # Step 2: Iterate through each position and force immediate closure
        # Emergency closure prioritizes capital preservation over profit optimization
        for position in positions.positions:
            if position.long.units != "0" or position.short.units != "0":
                # Step 3: Execute immediate market closure for each active position
                # "ALL" parameter closes entire position regardless of size
                close_response = await self.client.positions.close_position(
                    account_id=self.account_id,                              # Target account
                    instrument=position.instrument,                          # Currency pair to close
                    longUnits="ALL" if position.long.units != "0" else None, # Close all long units
                    shortUnits="ALL" if position.short.units != "0" else None # Close all short units
                )

                # Step 4: Record closure details for audit trail and reporting
                closed_positions.append({
                    "instrument": position.instrument,  # Which pair was closed
                    "response": close_response          # OANDA response details
                })

        return closed_positions
```

### Daily Loss Circuit Breaker

<!-- fragment: Demo circuit breaker with function type annotations and argument issues -->
```python
async def trading_circuit_breaker(
    client: AsyncClient,
    account_id: str,
    max_daily_loss: Decimal
) -> bool:
    """Automated circuit breaker to halt trading when risk limits are exceeded."""

    # Step 1: Initialize risk monitoring system for automated safety checks
    # Circuit breaker provides fail-safe mechanism against catastrophic losses
    monitor = RiskMonitor(client, account_id)

    # Step 2: Perform comprehensive risk assessment against safety thresholds
    # Risk status provides all necessary metrics for circuit breaker decision
    risk_status = await monitor.check_risk_limits()

    # Step 3: Evaluate daily loss threshold and trigger emergency procedures
    # Circuit breaker activates when daily losses exceed acceptable limits
    if risk_status["daily_loss_limit_breached"]:
        print(f"⚠️ CIRCUIT BREAKER ACTIVATED - Daily loss limit exceeded: ${risk_status['daily_pnl']}")

        # Step 4: Execute emergency closure of all positions to prevent further losses
        # Immediate position closure stops additional loss accumulation
        closed = await monitor.emergency_close_all()
        print(f"Emergency closure completed: {len(closed)} positions closed")

        return False  # Signal trading halt - no new positions allowed

    # Step 5: Return normal operation signal when risk levels are acceptable
    return True  # Continue trading - risk levels within acceptable bounds
```

## Next Steps

- Learn [Advanced Orders](advanced-orders/index.md) for sophisticated risk management
- Explore [Best Practices](../guides/understanding/best-practices.md) for production trading
- See [Account Management](account-management.md) for multi-position risk

For comprehensive risk management theory, consider specialized finance resources alongside FiveTwenty for implementation.
