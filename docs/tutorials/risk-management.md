# Risk Management with FiveTwenty

Learn essential risk management techniques using FiveTwenty's stop loss orders, position monitoring, and account controls.

!!! success "🎯 Practical Guide - Problem-oriented solutions"
    **Use this guide when:** You need to protect trading capital and control position risk

    **Learning outcome:** Implement risk controls using FiveTwenty SDK features

    **Time commitment:** 30-40 minutes

## Prerequisites

- Completed [Basic Trading](basic-trading/index.md) tutorial
- Understanding of position management concepts
- FiveTwenty setup with live or practice account

## Essential Risk Controls

### Stop Loss Orders

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
    """Place market order with automatic stop loss."""

    # Place market order
    market_order = MarketOrderRequest(
        instrument=instrument,
        units=units,
        time_in_force=TimeInForce.FOK,
    )

    order_response = await client.orders.post_order(account_id, market_order)

    if order_response.order_fill_transaction:
        # Order filled, add stop loss
        fill_price = Decimal(order_response.order_fill_transaction.price)

        # Calculate stop loss price
        if units > 0:  # Long position
            stop_price = fill_price - stop_loss_distance
        else:  # Short position
            stop_price = fill_price + stop_loss_distance

        # Create stop loss order
        stop_loss = StopLossOrderRequest(
            tradeID=order_response.order_fill_transaction.tradeOpened.tradeID,
            price=str(stop_price),
            timeInForce="GTC"
        )

        stop_response = await client.orders.post_order(account_id, stop_loss)

        return {
            "trade_id": order_response.order_fill_transaction.tradeOpened.tradeID,
            "entry_price": fill_price,
            "stop_price": stop_price,
            "stop_order_id": stop_response.order_create_transaction.id
        }

    raise ValueError("Market order was not filled")

# Usage
async def main():
    # Zero-config - automatically uses environment variables
    async with AsyncClient() as client:
        result = await place_order_with_stop_loss(
            client=client,
            account_id=client.account_id,
        instrument="EUR_USD",
        units=Decimal("1000"),
        stop_loss_distance=Decimal("0.0020")  # 20 pips
    )

        print(f"Trade {result['trade_id']} opened with stop at {result['stop_price']}")

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    asyncio.run(main())
```

### Position Size Based on Risk

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
    """Calculate position size based on account risk percentage."""

    # Get account balance
    account = await client.accounts.get_account(account_id)
    balance = Decimal(account.balance)

    # Calculate risk amount
    risk_amount = balance * (risk_percentage / 100)

    # Get current price to calculate pip value
    pricing = await client.pricing.get_pricing(
        account_id=account_id,
        instruments=[instrument]
    )

    current_price = Decimal(pricing.prices[0].asks[0].price)

    # Calculate pip value (simplified for major pairs)
    if "JPY" in instrument:
        pip_value = Decimal("0.01") / current_price  # Yen pairs
    else:
        pip_value = Decimal("0.0001") / current_price  # Major pairs

    # Calculate position size
    position_size = risk_amount / (stop_loss_pips * pip_value)

    # Round to appropriate increment
    return position_size.quantize(Decimal("1"))
```

### Account Monitoring and Limits

```python
class RiskMonitor:
    """Monitor account risk in real-time."""

    def __init__(self, client: AsyncClient, account_id: str):
        self.client = client
        self.account_id = account_id
        self.max_daily_loss = Decimal("1000")  # Max $1000 daily loss
        self.max_drawdown = Decimal("0.10")    # Max 10% drawdown
        self.daily_start_balance = None

    async def check_risk_limits(self) -> dict:
        """Check current risk against limits."""
        account = await self.client.accounts.get_account(self.account_id)
        current_balance = Decimal(account.balance)

        # Set daily start balance if not set
        if self.daily_start_balance is None:
            self.daily_start_balance = current_balance

        # Calculate daily P&L
        daily_pnl = current_balance - self.daily_start_balance

        # Get all open positions for exposure calculation
        positions = await self.client.positions.get_positions(self.client.account_id)
        total_exposure = Decimal("0")

        for position in positions.positions:
            if position.long.units != "0" or position.short.units != "0":
                long_units = abs(Decimal(position.long.units)) if position.long.units != "0" else Decimal("0")
                short_units = abs(Decimal(position.short.units)) if position.short.units != "0" else Decimal("0")
                total_exposure += long_units + short_units

        return {
            "current_balance": current_balance,
            "daily_pnl": daily_pnl,
            "daily_loss_limit_breached": daily_pnl < -self.max_daily_loss,
            "drawdown_limit_breached": (self.daily_start_balance - current_balance) / self.daily_start_balance > self.max_drawdown,
            "total_exposure": total_exposure,
            "margin_used": Decimal(account.margin_used),
            "margin_available": Decimal(account.margin_available)
        }

    async def emergency_close_all(self) -> list:
        """Close all positions in emergency."""
        positions = await self.client.positions.get_positions(self.client.account_id)
        closed_positions = []

        for position in positions.positions:
            if position.long.units != "0" or position.short.units != "0":
                # Close the position
                close_response = await self.client.positions.close_position(
                    account_id=self.account_id,
                    instrument=position.instrument,
                    longUnits="ALL" if position.long.units != "0" else None,
                    shortUnits="ALL" if position.short.units != "0" else None
                )
                closed_positions.append({
                    "instrument": position.instrument,
                    "response": close_response
                })

        return closed_positions
```

### Daily Loss Circuit Breaker

```python
async def trading_circuit_breaker(
    client: AsyncClient,
    account_id: str,
    max_daily_loss: Decimal
) -> bool:
    """Check if daily loss limit is exceeded and halt trading if needed."""

    monitor = RiskMonitor(client, account_id)
    risk_status = await monitor.check_risk_limits()

    if risk_status["daily_loss_limit_breached"]:
        print(f"⚠️ Daily loss limit exceeded: ${risk_status['daily_pnl']}")

        # Close all positions
        closed = await monitor.emergency_close_all()
        print(f"Closed {len(closed)} positions")

        return False  # Halt trading

    return True  # Continue trading
```

## Next Steps

- Learn [Advanced Orders](advanced-orders/index.md) for sophisticated risk management
- Explore [Best Practices](../guides/understanding/best-practices.md) for production trading
- See [Account Management](account-management.md) for multi-position risk

For comprehensive risk management theory, consider specialized finance resources alongside FiveTwenty for implementation.
