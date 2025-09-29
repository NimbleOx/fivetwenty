# Strategy Building

!!! tip "Target Learning Goal"
    Develop your first complete trading strategy with systematic signal generation and risk management.

---

## Designing Your First Strategy

Let's build a simple but complete moving average crossover strategy:

```python
from decimal import Decimal
from typing import Any

from dotenv import load_dotenv

from fivetwenty import AsyncClient

# Load environment variables from .env file
load_dotenv()

class SimpleMovingAverageCrossover:
    """A complete trading strategy with risk management."""

    def __init__(self, instrument: str = "EUR_USD") -> None:
        self.instrument = instrument
        self.position_size = 1000  # Conservative size
        self.max_risk_per_trade = 0.02  # 2% risk per trade
        self.stop_loss_pips = 20
        self.take_profit_pips = 30
        self.fast_ma_period = 10
        self.slow_ma_period = 20

        # Strategy state
        self.prices = []
        self.current_position = None
        self.strategy_stats = {
            'total_trades': 0,
            'winning_trades': 0,
            'total_pnl': 0.0
        }

    def calculate_moving_average(self, prices: list, period: int) -> Decimal:
        """Calculate simple moving average."""
        if len(prices) < period:
            return None
        return sum(prices[-period:]) / period

    def should_buy(self) -> bool:
        """Check if we should enter a long position."""
        if len(self.prices) < self.slow_ma_period:
            return False

        fast_ma = self.calculate_moving_average(self.prices, self.fast_ma_period)
        slow_ma = self.calculate_moving_average(self.prices, self.slow_ma_period)

        # Previous MAs for crossover detection
        prev_fast_ma = self.calculate_moving_average(self.prices[:-1], self.fast_ma_period)
        prev_slow_ma = self.calculate_moving_average(self.prices[:-1], self.slow_ma_period)

        if not all([fast_ma, slow_ma, prev_fast_ma, prev_slow_ma]):
            return False

        # Buy signal: fast MA crosses above slow MA
        return (prev_fast_ma <= prev_slow_ma) and (fast_ma > slow_ma)

    def should_sell(self) -> bool:
        """Check if we should enter a short position."""
        if len(self.prices) < self.slow_ma_period:
            return False

        fast_ma = self.calculate_moving_average(self.prices, self.fast_ma_period)
        slow_ma = self.calculate_moving_average(self.prices, self.slow_ma_period)

        # Previous MAs for crossover detection
        prev_fast_ma = self.calculate_moving_average(self.prices[:-1], self.fast_ma_period)
        prev_slow_ma = self.calculate_moving_average(self.prices[:-1], self.slow_ma_period)

        if not all([fast_ma, slow_ma, prev_fast_ma, prev_slow_ma]):
            return False

        # Sell signal: fast MA crosses below slow MA
        return (prev_fast_ma >= prev_slow_ma) and (fast_ma < slow_ma)

    async def update_prices(self, client: AsyncClient) -> Any:
        """Update price history for strategy calculations."""
        try:
            # Get recent historical data
            candles = await client.instruments.get_instrument_candles(
                instrument=self.instrument,
                count=max(50, self.slow_ma_period + 10),
                granularity="M5"  # 5-minute candles for more signals
            )

            if candles.candles:
                self.prices = [Decimal(str(c.mid.c)) for c in candles.candles if c.mid]
                return True
        except Exception as e:
            print(f"⚠️ Error updating prices: {e}")
        return False

# Create your strategy instance
if __name__ == "__main__":
    strategy = SimpleMovingAverageCrossover("EUR_USD")
```

---

## Strategy Backtesting Framework

Test your strategy on historical data:

```python
from decimal import Decimal

import pandas as pd
from dotenv import load_dotenv

from fivetwenty import AsyncClient

# Load environment variables from .env file
load_dotenv()

class StrategyBacktester:
    """Backtest trading strategies on historical data."""

    def __init__(self, strategy, initial_balance: Decimal = Decimal("10000")):
        self.strategy = strategy
        self.initial_balance = initial_balance
        self.current_balance = initial_balance
        self.trades = []
        self.equity_curve = []

    async def run_backtest(self, client: AsyncClient, start_date: str, end_date: str):
        """Run strategy backtest on historical data."""

        print("Processing RUNNING STRATEGY BACKTEST")
        print("=" * 35)

        try:
            # Get historical data
            candles = await client.instruments.get_instrument_candles(
                instrument=self.strategy.instrument,
                granularity="H1",  # 1-hour candles
                from_time=start_date,
                to_time=end_date
            )

            if not candles.candles:
                print("Error No historical data available")
                return

            print(f"Data Testing on {len(candles.candles)} data points")

            # Process each candle
            for i, candle in enumerate(candles.candles):
                if not candle.mid:
                    continue

                price = Decimal(str(candle.mid.c))
                timestamp = candle.time

                # Update strategy with new price
                self.strategy.prices.append(price)

                # Check for signals
                if not self.current_position and len(self.strategy.prices) >= self.strategy.slow_ma_period:
                    if self.strategy.should_buy():
                        await self._execute_backtest_trade("BUY", price, timestamp)
                    elif self.strategy.should_sell():
                        await self._execute_backtest_trade("SELL", price, timestamp)

                # Check for exit conditions
                elif self.current_position:
                    await self._check_exit_conditions(price, timestamp)

                # Step 7: Record account equity for performance analysis
                # Track balance over time to calculate drawdowns and risk metrics
                self.equity_curve.append({
                    'timestamp': timestamp,           # Time point for this balance record
                    'balance': self.current_balance,   # Account balance at this time
                    'price': price                     # Market price at this time
                })

            # Step 8: Generate comprehensive performance report
            self._generate_backtest_report()

        except Exception as e:
            print(f"Error Backtest error: {e}")

    async def _execute_backtest_trade(self, direction: str, price: Decimal, timestamp):
        """Execute trade in backtest environment."""

        units = self.strategy.position_size if direction == "BUY" else -self.strategy.position_size

        # Calculate stop loss and take profit
        if direction == "BUY":
            stop_loss = price - (self.strategy.stop_loss_pips * 0.0001)
            take_profit = price + (self.strategy.take_profit_pips * 0.0001)
        else:
            stop_loss = price + (self.strategy.stop_loss_pips * 0.0001)
            take_profit = price - (self.strategy.take_profit_pips * 0.0001)

        self.current_position = {
            'direction': direction,
            'entry_price': price,
            'units': units,
            'stop_loss': stop_loss,
            'take_profit': take_profit,
            'entry_time': timestamp
        }

        print(f"Analysis Backtest {direction}: {price:.5f} at {timestamp}")

    async def _check_exit_conditions(self, current_price: Decimal, timestamp):
        """Check if position should be closed."""

        if not self.current_position:
            return

        position = self.current_position
        should_close = False
        exit_reason = ""

        # Check stop loss
        if position['direction'] == "BUY" and current_price <= position['stop_loss']:
            should_close = True
            exit_reason = "Stop Loss"
        elif position['direction'] == "SELL" and current_price >= position['stop_loss']:
            should_close = True
            exit_reason = "Stop Loss"

        # Check take profit
        elif position['direction'] == "BUY" and current_price >= position['take_profit']:
            should_close = True
            exit_reason = "Take Profit"
        elif position['direction'] == "SELL" and current_price <= position['take_profit']:
            should_close = True
            exit_reason = "Take Profit"

        if should_close:
            await self._close_backtest_position(current_price, timestamp, exit_reason)

    async def _close_backtest_position(self, exit_price: Decimal, timestamp, reason: str):
        """Close position in backtest."""

        position = self.current_position
        entry_price = position['entry_price']
        units = position['units']

        # Calculate P&L
        if units > 0:  # Long position
            pnl = (exit_price - entry_price) * abs(units)
        else:  # Short position
            pnl = (entry_price - exit_price) * abs(units)

        # Update balance
        self.current_balance += pnl

        # Record trade
        trade_record = {
            'entry_time': position['entry_time'],
            'exit_time': timestamp,
            'direction': position['direction'],
            'entry_price': entry_price,
            'exit_price': exit_price,
            'units': units,
            'pnl': pnl,
            'exit_reason': reason
        }

        self.trades.append(trade_record)
        self.strategy.strategy_stats['total_trades'] += 1

        if pnl > 0:
            self.strategy.strategy_stats['winning_trades'] += 1

        self.strategy.strategy_stats['total_pnl'] += pnl

        print(f"📉 Close {position['direction']}: {exit_price:.5f} | P&L: ${pnl:+.2f} | {reason}")

        self.current_position = None

    def _generate_backtest_report(self):
        """Generate comprehensive backtest report."""

        print(f"\nData BACKTEST RESULTS")
        print("=" * 25)

        if not self.trades:
            print("No trades executed during backtest period")
            return

        # Basic statistics
        total_trades = len(self.trades)
        winning_trades = sum(1 for trade in self.trades if trade['pnl'] > 0)
        losing_trades = total_trades - winning_trades

        win_rate = (winning_trades / total_trades) * 100 if total_trades > 0 else 0
        total_pnl = sum(trade['pnl'] for trade in self.trades)
        total_return = ((self.current_balance - self.initial_balance) / self.initial_balance) * 100

        print(f"Initial Balance: ${self.initial_balance:,.2f}")
        print(f"Final Balance: ${self.current_balance:,.2f}")
        print(f"Total Return: {total_return:+.2f}%")
        print(f"Total P&L: ${total_pnl:+.2f}")
        print(f"Total Trades: {total_trades}")
        print(f"Winning Trades: {winning_trades}")
        print(f"Losing Trades: {losing_trades}")
        print(f"Win Rate: {win_rate:.1f}%")

        if self.trades:
            winning_pnls = [trade['pnl'] for trade in self.trades if trade['pnl'] > 0]
            losing_pnls = [trade['pnl'] for trade in self.trades if trade['pnl'] < 0]

            avg_win = sum(winning_pnls) / len(winning_pnls) if winning_pnls else 0
            avg_loss = sum(losing_pnls) / len(losing_pnls) if losing_pnls else 0

            print(f"Average Win: ${avg_win:.2f}")
            print(f"Average Loss: ${avg_loss:.2f}")

            if avg_loss != 0:
                profit_factor = abs(avg_win / avg_loss)
                print(f"Profit Factor: {profit_factor:.2f}")

# Step 9: Example backtest execution
# Demonstrates how to test strategy on historical data
if __name__ == "__main__":
    # Create strategy and backtester instances
    strategy = SimpleMovingAverageCrossover("EUR_USD")
    backtester = StrategyBacktester(strategy, initial_balance=Decimal("10000"))

    print("Backtest Configuration:")
    print(f"Strategy: {strategy.__class__.__name__}")
    print(f"Instrument: {strategy.instrument}")
    print(f"Initial Balance: ${backtester.initial_balance:,}")
    print(f"Test Period: January 2024 (1 month)")

    # Run backtest (uncomment for actual use)
    # await backtester.run_backtest(client, "2024-01-01T00:00:00Z", "2024-02-01T00:00:00Z")
    # print(f"\nBacktest completed. Final balance: ${backtester.current_balance:,.2f}")
```

---

## Strategy Optimization

Improve your strategy through parameter optimization:

```python
from dotenv import load_dotenv

from fivetwenty import AsyncClient

# Load environment variables from .env file
load_dotenv()

class StrategyOptimizer:
    """Optimize strategy parameters through systematic testing."""

    def __init__(self, strategy_class, instrument: str):
        self.strategy_class = strategy_class
        self.instrument = instrument
        self.optimization_results = []

    async def optimize_parameters(self, client: AsyncClient, parameter_ranges: dict):
        """Optimize strategy parameters across given ranges."""

        print("Config STRATEGY OPTIMIZATION")
        print("=" * 30)

        import itertools

        # Generate all parameter combinations
        param_names = list(parameter_ranges.keys())
        param_values = list(parameter_ranges.values())
        combinations = list(itertools.product(*param_values))

        print(f"Testing {len(combinations)} parameter combinations...")

        best_return = float('-inf')
        best_params = None

        for i, params in enumerate(combinations):
            param_dict = dict(zip(param_names, params))

            # Create strategy with these parameters
            strategy = self.strategy_class(self.instrument)

            # Apply parameters
            for param_name, param_value in param_dict.items():
                setattr(strategy, param_name, param_value)

            # Run backtest
            backtester = StrategyBacktester(strategy)
            # await backtester.run_backtest(client, "2024-01-01T00:00:00Z", "2024-02-01T00:00:00Z")

            # Calculate return
            total_return = ((backtester.current_balance - backtester.initial_balance) / backtester.initial_balance) * 100

            result = {
                'parameters': param_dict.copy(),
                'return': total_return,
                'total_trades': len(backtester.trades),
                'win_rate': (sum(1 for t in backtester.trades if t['pnl'] > 0) / len(backtester.trades) * 100) if backtester.trades else 0
            }

            self.optimization_results.append(result)

            if total_return > best_return:
                best_return = total_return
                best_params = param_dict.copy()

            print(f"Combination {i+1}/{len(combinations)}: Return {total_return:.2f}%")

        print(f"\nAchievement OPTIMIZATION COMPLETE")
        print(f"Best Parameters: {best_params}")
        print(f"Best Return: {best_return:.2f}%")

        return best_params, best_return

# Example optimization
# if __name__ == "__main__":
#     optimizer = StrategyOptimizer(SimpleMovingAverageCrossover, "EUR_USD")
# parameter_ranges = {
#     'fast_ma_period': [5, 10, 15],
#     'slow_ma_period': [20, 25, 30],
#     'stop_loss_pips': [15, 20, 25],
#     'take_profit_pips': [25, 30, 35]
# }
# best_params, best_return = await optimizer.optimize_parameters(client, parameter_ranges)
```

---


## What You've Learned

Success **Strategy Design**: How to build systematic trading strategies with clear rules

Success **Backtesting**: Testing strategies on historical data for validation

Success **Parameter Optimization**: Systematically improving strategy performance

Success **Performance Analysis**: Evaluating strategy effectiveness and robustness

!!! success "Complete Strategy Building Complete!"
    Outstanding! You can now design, test, and optimize complete trading strategies. You understand the full development cycle from concept to implementation. Next, you'll learn to build production-ready automated systems.

---

## Next Steps

Continue to [Complete Trading System](complete-system.md) to build a production-ready automated trading system.

---

## Related Resources

- [Advanced Orders](../advanced-orders/index.md) - Complex order strategies
- [Risk Management](../risk-management.md) - Comprehensive risk frameworks
- [Performance Optimization](../../guides/optimization/index.md) - Performance optimization