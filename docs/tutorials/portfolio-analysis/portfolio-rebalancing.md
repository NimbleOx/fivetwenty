# Portfolio Rebalancing

Implement dynamic portfolio rebalancing strategies that maintain target allocations and optimize transaction costs.

---

## Prerequisites

- Understanding of portfolio optimization and attribution
- Transaction cost concepts
- FiveTwenty trading capabilities

---

## Learning Objectives

- ✅ Implement rebalancing triggers and methods
- ✅ Optimize transaction costs
- ✅ Build automated rebalancing systems
- ✅ Monitor rebalancing effectiveness

---

## Dynamic Rebalancing Framework

```python
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
import asyncio
from decimal import Decimal

from fivetwenty import AsyncClient, Environment


"""Comprehensive module for trading operations."""
class PortfolioRebalancer:
    """Dynamic portfolio rebalancing with transaction cost optimization."""

    def __init__(self, client: AsyncClient, account_id: str, target_weights: Dict[str, float]: Any) -> None:
        self.client = client
        self.account_id = account_id
        self.target_weights = target_weights
        self.instruments = list(target_weights.keys())
        self.transaction_costs = {}
        self.rebalancing_history = []

    async def get_current_positions(self) -> Dict[str, float]:
        """Get current portfolio positions."""

        try:
            # Get account summary
            account = await self.client.accounts.get_account(self.account_id)

            # Get current positions
            positions = {}
            total_value = float(account.nav)

            if hasattr(account, 'positions') and account.positions:
                for position in account.positions:
                    if position.instrument in self.instruments:
                        # Calculate position value
                        units = float(Decimal(str(position.long.units)) - Decimal(str(position.short.units)))

                        # Get current price to calculate market value
                        pricing = await self.client.pricing.get_pricing(
                            self.account_id, [position.instrument]
                        )

                        if pricing:
                            current_price = Decimal(str(pricing[0].closeout_ask))
                            position_value = abs(units) * current_price
                            weight = position_value / total_value if total_value > 0 else 0
                            positions[position.instrument] = weight

            # Fill missing instruments with zero weights
            for instrument in self.instruments:
                if instrument not in positions:
                    positions[instrument] = 0.0

            return positions

        except Exception as e:
            print(f"Error getting positions: {e}")
            return {inst: 0.0 for inst in self.instruments}

    def calculate_rebalancing_trades(self, current_weights: Dict[str, float],
                                   total_portfolio_value: Decimal,
                                   tolerance: Decimal = Decimal("0.05")) -> Dict[str, float]:
        """Calculate required trades for rebalancing."""

        trades = {}

        for instrument in self.instruments:
            current_weight = current_weights.get(instrument, 0.0)
            target_weight = self.target_weights.get(instrument, 0.0)

            weight_difference = target_weight - current_weight

            # Only trade if difference exceeds tolerance
            if abs(weight_difference) > float(tolerance):
                # Calculate trade size in base currency
                trade_value = weight_difference * float(total_portfolio_value)

                # Convert to units (simplified - would need actual price conversion)
                trades[instrument] = trade_value

        return trades

    async def execute_rebalancing_trades(self, trades: Dict[str, float],
                                       max_trade_size: Decimal = Decimal("10000")) -> List[Dict]:
        """Execute rebalancing trades with size limits."""

        executed_trades = []

        for instrument, trade_value in trades.items():
            if abs(trade_value) < 100:  # Skip minimal trades
                continue

            try:
                # Split large trades
                remaining_value = trade_value
                while abs(remaining_value) > 100:
                    # Determine trade size
                    trade_size = min(abs(remaining_value), float(max_trade_size))
                    if remaining_value < 0:
                        trade_size = -trade_size

                    # Convert to units (simplified)
                    units = int(trade_size)  # Would need proper conversion

                    # Execute trade
                    response = await self.client.orders.post_market_order(
                        account_id=self.account_id,
                        instrument=instrument,
                        units=units
                    )

                    if response.order_fill_transaction:
                        executed_trades.append({
                            'instrument': instrument,
                            'units': units,
                            'price': Decimal(str(response.order_fill_transaction.price)),
                            'timestamp': datetime.now(),
                            'trade_id': response.order_fill_transaction.id
                        })

                        remaining_value -= trade_size

                    else:
                        print(f"Failed to execute trade for {instrument}")
                        break

            except Exception as e:
                print(f"Error executing trade for {instrument}: {e}")

        return executed_trades

    def should_rebalance(self, current_weights: Dict[str, float],
                        rebalancing_method: str = 'threshold') -> bool:
        """Determine if rebalancing is needed."""

        if rebalancing_method == 'threshold':
            # Threshold-based rebalancing
            threshold = 0.05  # 5% deviation threshold

            for instrument in self.instruments:
                current_weight = current_weights.get(instrument, 0.0)
                target_weight = self.target_weights.get(instrument, 0.0)

                if abs(current_weight - target_weight) > threshold:
                    return True

            return False

        elif rebalancing_method == 'time':
            # Time-based rebalancing (monthly)
            if not self.rebalancing_history:
                return True

            last_rebalance = self.rebalancing_history[-1]['timestamp']
            return (datetime.now() - last_rebalance).days >= 30

        elif rebalancing_method == 'volatility':
            # Volatility-based rebalancing
            # Would implement based on market volatility conditions
            return False

        else:
            return False

    async def monitor_and_rebalance(self, check_interval_hours: int = 24) -> Any:
        """Continuous monitoring and rebalancing."""

        print("Starting portfolio monitoring and rebalancing...")

        while True:
            try:
                # Get current positions
                current_weights = await self.get_current_positions()

                # Check if rebalancing is needed
                if self.should_rebalance(current_weights):
                    print("Rebalancing triggered...")

                    # Get portfolio value
                    account = await self.client.accounts.get_account(self.account_id)
                    portfolio_value = float(account.nav)

                    # Calculate required trades
                    trades = self.calculate_rebalancing_trades(
                        current_weights, portfolio_value
                    )

                    if trades:
                        # Execute trades
                        executed_trades = await self.execute_rebalancing_trades(trades)

                        # Record rebalancing
                        self.rebalancing_history.append({
                            'timestamp': datetime.now(),
                            'trades': executed_trades,
                            'pre_rebalance_weights': current_weights.copy(),
                            'target_weights': self.target_weights.copy()
                        })

                        print(f"Rebalancing completed: {len(executed_trades)} trades executed")

                    else:
                        print("No trades required for rebalancing")

                else:
                    print("No rebalancing needed")

                # Wait before next check
                await asyncio.sleep(check_interval_hours * 3600)

            except Exception as e:
                print(f"Error in monitoring loop: {e}")
                await asyncio.sleep(3600)  # Wait 1 hour before retry

class TransactionCostOptimizer:
    """Optimize rebalancing considering transaction costs."""

    def __init__(self, spread_costs: Dict[str, float]: Any, commission_rates: Dict[str, float]: Any) -> None:
        self.spread_costs = spread_costs  # Spread cost per unit
        self.commission_rates = commission_rates  # Commission as % of trade value

    def calculate_transaction_costs(self, trades: Dict[str, float]) -> Dict[str, float]:
        """Calculate transaction costs for proposed trades."""

        costs = {}

        for instrument, trade_size in trades.items():
            # Spread cost
            spread_cost = abs(trade_size) * self.spread_costs.get(instrument, 0.0001)

            # Commission
            commission = abs(trade_size) * self.commission_rates.get(instrument, 0.0001)

            # Total transaction cost
            total_cost = spread_cost + commission
            costs[instrument] = total_cost

        return costs

    def optimize_rebalancing_schedule(self, weight_deviations: Dict[str, float],
                                    rebalancing_benefit: Decimal) -> Dict[str, bool]:
        """Determine which instruments to rebalance based on cost-benefit."""

        rebalance_decisions = {}

        for instrument, deviation in weight_deviations.items():
            # Estimate benefit from rebalancing (risk reduction)
            estimated_benefit = abs(deviation) * float(rebalancing_benefit)

            # Calculate transaction cost
            trade_size = deviation * 10000  # Assume $10k portfolio
            transaction_cost = self.calculate_transaction_costs({instrument: trade_size})

            # Rebalance if benefit exceeds cost
            rebalance_decisions[instrument] = estimated_benefit > transaction_cost.get(instrument, 0)

        return rebalance_decisions

# Advanced Rebalancing Strategies
class AdaptiveRebalancer:
    """Adaptive rebalancing based on market conditions."""

    def __init__(self, base_rebalancer: PortfolioRebalancer) -> None:
        self.base_rebalancer = base_rebalancer
        self.market_conditions = {}

    def calculate_adaptive_thresholds(self, market_volatility: Decimal) -> Dict[str, float]:
        """Calculate dynamic rebalancing thresholds based on market conditions."""

        base_threshold = 0.05  # 5% base threshold

        # Increase threshold during high volatility
        volatility_adjustment = min(float(market_volatility * 2), 0.03)  # Max 3% additional
        adaptive_threshold = base_threshold + volatility_adjustment

        return {inst: adaptive_threshold for inst in self.base_rebalancer.instruments}

    def market_timing_rebalance(self, market_signals: Dict[str, float]) -> Dict[str, float]:
        """Adjust target weights based on market timing signals."""

        adjusted_weights = self.base_rebalancer.target_weights.copy()

        for instrument, signal in market_signals.items():
            if instrument in adjusted_weights:
                # Adjust weight based on signal strength (-1 to +1)
                adjustment = signal * 0.1  # Max 10% adjustment
                adjusted_weights[instrument] *= (1 + adjustment)

        # Normalize weights to sum to 1
        total_weight = sum(adjusted_weights.values())
        adjusted_weights = {k: v/total_weight for k, v in adjusted_weights.items()}

        return adjusted_weights

# Example usage
async def portfolio_rebalancing_example():
    """Demonstrate portfolio rebalancing capabilities."""

    # Configuration
    TOKEN = "your-api-token"
    ACCOUNT_ID = "your-account-id"
    target_weights = {
        "EUR_USD": 0.4,
        "GBP_USD": 0.3,
        "USD_JPY": 0.2,
        "AUD_USD": 0.1
    }

    print("Portfolio Rebalancing System:")
    print("1. Monitor current positions")
    print("2. Calculate rebalancing needs")
    print("3. Optimize transaction costs")
    print("4. Execute rebalancing trades")
    print("5. Track rebalancing history")

    async with AsyncClient(token=TOKEN, environment=Environment.PRACTICE) as client:
        # Initialize rebalancer
        rebalancer = PortfolioRebalancer(client, ACCOUNT_ID, target_weights)

        # Get current positions
        current_weights = await rebalancer.get_current_positions()
        print(f"Current weights: {current_weights}")

        # Check if rebalancing needed
        needs_rebalance = rebalancer.should_rebalance(current_weights)
        print(f"Needs rebalancing: {needs_rebalance}")

        return rebalancer

# Run example
# rebalancer = await portfolio_rebalancing_example()
```

## Rebalancing Strategies

### 1. Threshold-Based Rebalancing
- **Fixed Thresholds**: Rebalance when weights deviate by fixed percentage
- **Adaptive Thresholds**: Adjust thresholds based on market conditions
- **Asymmetric Thresholds**: Different thresholds for different instruments

### 2. Time-Based Rebalancing
- **Calendar Rebalancing**: Monthly, quarterly schedules
- **Business Cycle**: Align with economic cycles
- **Seasonal Patterns**: Account for seasonal market effects

### 3. Volatility-Based Rebalancing
- **High Volatility**: More frequent rebalancing
- **Low Volatility**: Less frequent rebalancing
- **Regime Detection**: Adjust strategy based on market regime

## Cost Optimization

### Transaction Cost Components
- **Spread Costs**: Bid-ask spread impact
- **Commission Costs**: Broker fees
- **Market Impact**: Price movement from large trades
- **Opportunity Costs**: Timing delays

### Cost Minimization Strategies
- **Trade Sizing**: Optimal trade size determination
- **Trade Timing**: Execute during high liquidity periods
- **Netting**: Offset opposing trades
- **Gradual Execution**: Spread large trades over time

---

## Next Steps

Complete the series with [Best Practices](best-practices.md) for production implementation.

---

## Related Tutorials

- [Portfolio Optimization](portfolio-optimization.md) - Optimization methods
- [Performance Attribution](performance-attribution.md) - Performance analysis
- [Best Practices](best-practices.md) - Implementation guidance