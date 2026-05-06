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

Stop loss orders are the foundation of effective risk management in trading. Without stop losses, a single adverse market move can wipe out weeks or months of profitable trades. By automatically closing positions at predetermined price levels, stop losses protect your capital from catastrophic losses while allowing profitable trades to run. Every professional trading strategy includes stop loss protection as a non-negotiable risk control.

The FiveTwenty SDK provides a streamlined approach to stop loss management using the `stop_loss` parameter on market orders. This creates a "stopLossOnFill" order that automatically activates when your market order executes, ensuring immediate risk protection without the complexity of managing separate stop loss orders. This example demonstrates how to calculate appropriate stop levels based on position direction and attach them to trades in a single, atomic operation.

<!-- filepath: docs/tutorials/risk-management/example_stop_loss.py -->
```python
"""Demonstrate stop loss order placement for automated risk protection.

This example shows how to:
- Calculate stop loss price based on position direction and risk tolerance
- Place a market order with automatic stop loss protection
- Use stopLossOnFill for immediate risk management
- Verify trade execution and stop loss attachment
"""

import asyncio
from decimal import Decimal
from typing import Any

from dotenv import load_dotenv

from fivetwenty import AsyncClient
from fivetwenty.models import InstrumentName

load_dotenv()


async def place_order_with_stop_loss(
    client: AsyncClient,
    account_id: str,
    instrument: InstrumentName,
    units: int,
    stop_loss_pips: int,
) -> dict[str, Any]:
    """Place market order with automatic stop loss protection."""

    # ==============================================================================
    # STEP 1: GET CURRENT PRICE FOR STOP LOSS CALCULATION
    # ==============================================================================

    # The SDK method: client.pricing.get_pricing()
    #
    # Parameters:
    #   - account_id: Your OANDA account ID
    #   - instruments: List of instruments to get pricing for
    #
    # Returns: PricingResponse TypedDict with structure:
    #   {
    #       "prices": list[ClientPrice],  # Current prices for requested instruments
    #       "time": str
    #   }

    pricing_response = await client.pricing.get_pricing(
        account_id=account_id,
        instruments=[instrument],
    )

    # Extract current market price
    current_price = pricing_response["prices"][0]
    # Use ask for buys (long), bid for sells (short)
    entry_price = (
        Decimal(current_price.asks[0].price)
        if units > 0
        else Decimal(current_price.bids[0].price)
    )

    # ==============================================================================
    # STEP 2: CALCULATE STOP LOSS PRICE
    # ==============================================================================

    # Calculate stop distance in price terms
    # EUR/USD uses 4 decimal places: 1 pip = 0.0001
    pip_size = Decimal("0.0001")
    stop_distance = pip_size * stop_loss_pips

    # Calculate stop price based on position direction
    # Long positions (units > 0): stop below entry to limit downside
    # Short positions (units < 0): stop above entry to limit upside
    if units > 0:
        stop_price = entry_price - stop_distance  # Long: stop below entry
    else:
        stop_price = entry_price + stop_distance  # Short: stop above entry

    # ==============================================================================
    # STEP 3: PLACE MARKET ORDER WITH STOP LOSS
    # ==============================================================================

    # The SDK method: client.orders.post_market_order()
    #
    # Parameters:
    #   - account_id: Your OANDA account ID
    #   - instrument: Currency pair to trade
    #   - units: Position size (positive=long, negative=short)
    #   - stop_loss: Stop loss price (creates stopLossOnFill order)
    #
    # Returns: OrderResponse TypedDict with structure:
    #   {
    #       "orderFillTransaction": OrderFillTransaction or None
    #       "orderCreateTransaction": OrderCreateTransaction or None
    #       "relatedTransactionIDs": list[str]
    #       "lastTransactionID": str
    #   }
    #
    # NOTE: RECOMMENDED PATTERN - Use stop_loss parameter for automatic risk
    #       management that activates when the order fills. This is preferred
    #       over creating separate stop loss orders after the trade.

    order_response = await client.orders.post_market_order(
        account_id=account_id,
        instrument=instrument,
        units=units,
        stop_loss=stop_price,  # Automatic stop loss on fill
    )

    # Verify order was filled before proceeding
    if not order_response.get("orderFillTransaction"):
        raise ValueError("Market order was not filled")

    fill_transaction = order_response["orderFillTransaction"]

    # ==============================================================================
    # STEP 4: VERIFY TRADE AND STOP LOSS ATTACHMENT
    # ==============================================================================

    # Extract trade details from fill transaction
    trade_opened = fill_transaction.trade_opened
    if not trade_opened:
        raise ValueError("No trade was opened by this order")

    # Actual fill price may differ slightly from estimated entry price
    actual_fill_price = fill_transaction.price

    return {
        "trade_id": trade_opened.trade_id,
        "entry_price": actual_fill_price,
        "stop_price": stop_price,
        "stop_distance_pips": stop_loss_pips,
        "fill_transaction_id": order_response["lastTransactionID"],
    }


async def main() -> None:
    """Execute protected trade with automatic stop loss."""

    # ==============================================================================
    # CONNECT TO OANDA
    # ==============================================================================

    # AsyncClient automatically reads FIVETWENTY_OANDA_* environment variables
    # Context manager ensures proper cleanup of HTTP connections
    async with AsyncClient() as client:
        # ==============================================================================
        # PLACE PROTECTED TRADE
        # ==============================================================================

        # Place trade with 20-pip stop loss protection
        result = await place_order_with_stop_loss(
            client=client,
            account_id=client.account_id,
            instrument=InstrumentName.EUR_USD,
            units=1000,  # Long position (buy)
            stop_loss_pips=20,  # 20 pips = $20 risk on 1000 units
        )

        # Display execution details
        print("Protected trade executed:")
        print(f"  Trade ID: {result['trade_id']}")
        print(f"  Entry Price: {result['entry_price']:.5f}")
        print(f"  Stop Loss: {result['stop_price']:.5f}")
        print(f"  Protection: {result['stop_distance_pips']} pips")


if __name__ == "__main__":
    asyncio.run(main())
```

### Position Size Based on Risk

<!-- fragment: partial position sizing example -->
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

<!-- fragment: partial risk monitoring example -->
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

<!-- fragment: partial circuit breaker example -->
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
