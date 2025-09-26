# Portfolio Management with FiveTwenty

Learn how to manage multiple positions and track portfolio performance using FiveTwenty's position and account APIs.

!!! success "🎯 Practical Guide - Problem-oriented solutions"
    **Use this guide when:** You need to manage multiple currency positions as a portfolio

    **Learning outcome:** Track and analyze portfolio performance using FiveTwenty

    **Time commitment:** 20-30 minutes

## Prerequisites

- Completed [Basic Trading](../basic-trading/index.md) tutorial
- Understanding of position management concepts
- FiveTwenty setup with live or practice account

## Essential Portfolio Operations

### Getting Portfolio Overview

```python
import asyncio
from decimal import Decimal
from fivetwenty import AsyncClient

async def get_portfolio_summary(client: AsyncClient, account_id: str) -> dict:
    """Get current portfolio status."""
    # Get account summary
    account = await client.accounts.get_account(account_id)

    # Get all positions
    positions = await client.positions.get_positions(account_id)

    # Calculate portfolio metrics
    total_exposure = Decimal("0")
    open_positions = []

    for position in positions.positions:
        if position.long.units != "0" or position.short.units != "0":
            long_units = Decimal(position.long.units) if position.long.units != "0" else Decimal("0")
            short_units = Decimal(position.short.units) if position.short.units != "0" else Decimal("0")
            net_units = long_units + short_units

            if net_units != 0:
                open_positions.append({
                    "instrument": position.instrument,
                    "net_units": net_units,
                    "unrealized_pl": Decimal(position.unrealized_pl)
                })
                total_exposure += abs(net_units)

    return {
        "account_balance": Decimal(account.balance),
        "total_exposure": total_exposure,
        "open_positions": len(open_positions),
        "positions": open_positions,
        "margin_used": Decimal(account.margin_used),
        "margin_available": Decimal(account.margin_available)
    }

# Usage
async def main():
    client = AsyncClient(token="your-token", account_id="your-account")
    account_id = "your-account-id"

    portfolio = await get_portfolio_summary(client, account_id)
    print(f"Portfolio balance: ${portfolio['account_balance']}")
    print(f"Total exposure: {portfolio['total_exposure']} units")
    print(f"Open positions: {portfolio['open_positions']}")

asyncio.run(main())
```

### Position Sizing and Allocation

```python
async def calculate_position_sizes(
    client: AsyncClient,
    account_id: str,
    target_allocations: dict[str, Decimal],  # {"EUR_USD": Decimal("0.3"), ...}
    total_risk_capital: Decimal
) -> dict[str, Decimal]:
    """Calculate position sizes based on target allocations."""

    position_sizes = {}

    for instrument, allocation in target_allocations.items():
        # Get current pricing
        pricing = await client.pricing.get_pricing(
            account_id=account_id,
            instruments=[instrument]
        )

        current_price = Decimal(pricing.prices[0].asks[0].price)

        # Calculate target capital for this instrument
        target_capital = total_risk_capital * allocation

        # Calculate units needed
        units = (target_capital / current_price).quantize(Decimal("1"))
        position_sizes[instrument] = units

    return position_sizes
```

### Simple Rebalancing

```python
async def rebalance_portfolio(
    client: AsyncClient,
    account_id: str,
    target_allocations: dict[str, Decimal],
    rebalance_threshold: Decimal = Decimal("0.05")  # 5% threshold
) -> list[dict]:
    """Rebalance portfolio when allocations drift beyond threshold."""

    # Get current portfolio state
    account = await client.accounts.get_account(account_id)
    positions = await client.positions.get_positions(account_id)
    total_capital = Decimal(account.balance)

    # Calculate current allocations
    current_values = {}
    total_value = Decimal("0")

    for position in positions.positions:
        if position.long.units != "0" or position.short.units != "0":
            # Get current pricing
            pricing = await client.pricing.get_pricing(
                account_id=account_id,
                instruments=[position.instrument]
            )
            current_price = Decimal(pricing.prices[0].asks[0].price)

            long_units = Decimal(position.long.units) if position.long.units != "0" else Decimal("0")
            short_units = Decimal(position.short.units) if position.short.units != "0" else Decimal("0")
            net_units = long_units + short_units

            position_value = abs(net_units) * current_price
            current_values[position.instrument] = position_value
            total_value += position_value

    # Check if rebalancing is needed
    rebalance_trades = []

    for instrument, target_allocation in target_allocations.items():
        current_value = current_values.get(instrument, Decimal("0"))
        current_allocation = current_value / total_value if total_value > 0 else Decimal("0")

        allocation_drift = abs(current_allocation - target_allocation)

        if allocation_drift > rebalance_threshold:
            target_value = total_capital * target_allocation
            value_adjustment = target_value - current_value

            # Get pricing for unit calculation
            pricing = await client.pricing.get_pricing(
                account_id=account_id,
                instruments=[instrument]
            )
            current_price = Decimal(pricing.prices[0].asks[0].price)

            units_to_trade = (value_adjustment / current_price).quantize(Decimal("1"))

            if abs(units_to_trade) >= 1:  # Minimum trade size
                rebalance_trades.append({
                    "instrument": instrument,
                    "units": units_to_trade,
                    "reason": f"Drift: {allocation_drift:.1%} > {rebalance_threshold:.1%}"
                })

    return rebalance_trades
```

## Key Portfolio Concepts

### Position Correlation
When managing multiple positions, consider correlation between currency pairs to avoid excessive risk concentration.

### Risk Limits
Set portfolio-level limits:
- Maximum total exposure
- Maximum positions per currency
- Daily loss limits
- Drawdown thresholds

### Performance Tracking
Monitor these metrics:
- Total portfolio P&L
- Individual position performance
- Win/loss ratios
- Risk-adjusted returns

## Best Practices

1. **Keep it Simple**: Focus on basic allocation and risk management rather than complex optimization
2. **Use FiveTwenty's Position API**: Leverage built-in position tracking rather than building your own
3. **Monitor Margin**: Always check margin requirements when sizing positions
4. **Regular Rebalancing**: Set clear thresholds for when to rebalance
5. **Risk First**: Set maximum loss limits before optimizing for returns

## Next Steps

- Learn [Risk Management](../risk-management/index.md) for portfolio-level risk controls
- Explore [Advanced Orders](../advanced-orders/index.md) for complex position management
- See [Best Practices](../../explanation/best-practices.md) for production considerations

For comprehensive portfolio theory and optimization techniques, consider specialized financial libraries like `scipy.optimize` or `cvxpy` alongside FiveTwenty for execution.