# Complete Trading System

!!! tip "Learning Goal"
    Build a production-ready automated trading system with full automation, risk management, and performance tracking.

---

## Complete Trading Strategy Implementation

Let's build a comprehensive automated trading system:

<!-- fragment: Demo complete trading strategy with magic numbers and attribute access patterns -->
```python
import asyncio
from datetime import datetime
from decimal import Decimal

from dotenv import load_dotenv

from fivetwenty import AsyncClient

# Load environment variables from .env file
load_dotenv()

# SimpleMovingAverageCrossover would be defined elsewhere
# (see previous lessons for implementation)

async def run_complete_trading_strategy(strategy, duration_minutes: int = 10):
    """Run a complete trading strategy with full automation."""

    print("LAUNCHING AUTOMATED TRADING STRATEGY")
    print("=" * 45)
    print(f"Strategy: Moving Average Crossover")
    print(f"Instrument: {strategy.instrument}")
    print(f"Duration: {duration_minutes} minutes")
    print(f"Fast MA: {strategy.fast_ma_period} periods")
    print(f"Slow MA: {strategy.slow_ma_period} periods")

    # Zero-config - automatically uses environment variables
    async with AsyncClient() as client:
        start_time = datetime.now()

        while (datetime.now() - start_time).seconds < duration_minutes * 60:
            try:
                print(f"\n{datetime.now().strftime('%H:%M:%S')} - Strategy Check")

                # Step 1: Update market data
                if not await strategy.update_prices(client):
                    print("   WARNING: Could not update prices, skipping this cycle")
                    await asyncio.sleep(60)  # Wait 1 minute before retry
                    continue

                current_price = strategy.prices[-1]
                print(f"   Current Price: {current_price:.5f}")

                # Step 2: Calculate indicators
                if len(strategy.prices) >= strategy.slow_ma_period:
                    fast_ma = strategy.calculate_moving_average(
                        strategy.prices, strategy.fast_ma_period
                    )
                    slow_ma = strategy.calculate_moving_average(
                        strategy.prices, strategy.slow_ma_period
                    )
                    print(f"   Fast MA: {fast_ma:.5f}")
                    print(f"   Slow MA: {slow_ma:.5f}")

                # Step 3: Check current position
                open_trades = await client.trades.get_trades(
                    client.account_id,
                    state="OPEN",
                    instrument=strategy.instrument
                )

                has_position = len(open_trades) > 0
                print(f"   Current Position: {'YES' if has_position else 'NONE'}")

                # Step 4: Strategy logic
                if not has_position:
                    # Look for entry signals
                    if strategy.should_buy():
                        print("   BUY SIGNAL DETECTED!")
                        await execute_strategy_trade(
                            client, strategy, "BUY", current_price
                        )
                    elif strategy.should_sell():
                        print("   SELL SIGNAL DETECTED!")
                        await execute_strategy_trade(
                            client, strategy, "SELL", current_price
                        )
                    else:
                        print("   No signal - waiting")
                else:
                    print("   Managing existing position...")
                    # In a real strategy, you might implement trailing stops,
                    # position sizing adjustments, or other management rules here

                # Step 5: Display strategy statistics
                print(f"   Strategy Stats: {strategy.strategy_stats['total_trades']} trades, "
                      f"${strategy.strategy_stats['total_pnl']:+.2f} total P&L")

                await asyncio.sleep(60)  # Check every minute

            except Exception as e:
                print(f"   Error ERROR: Strategy error: {e}")
                print(f"   Processing Continuing strategy loop after error recovery")
                # In production: implement proper error logging and alerting
                await asyncio.sleep(60)  # Wait before retrying to avoid error loops

        # Step 11: Strategy completion and final analysis
        print(f"\nFlag Strategy completed after {duration_minutes} minutes")
        print(f"Session ended at: {datetime.now().strftime('%H:%M:%S')}")

        # Generate comprehensive final performance report
        print_strategy_performance(strategy)

async def execute_strategy_trade(client: AsyncClient, strategy,
                               direction: str, current_price: Decimal):
    """Execute a trade based on strategy signal."""

    try:
        units = strategy.position_size if direction == "BUY" else -strategy.position_size

        # Calculate stop loss and take profit levels
        if direction == "BUY":
            stop_loss_price = current_price - (strategy.stop_loss_pips * Decimal("0.0001"))
            take_profit_price = current_price + (strategy.take_profit_pips * Decimal("0.0001"))
        else:
            stop_loss_price = current_price + (strategy.stop_loss_pips * Decimal("0.0001"))
            take_profit_price = current_price - (strategy.take_profit_pips * Decimal("0.0001"))

        # Place the trade with risk management
        response = await client.orders.post_market_order(
            account_id=client.account_id,
            instrument=strategy.instrument,
            units=units,
            stop_loss=Decimal(str(stop_loss_price)),
            take_profit=Decimal(str(take_profit_price))
        )

        if response.order_fill_transaction:
            fill = response.order_fill_transaction
            strategy.strategy_stats['total_trades'] += 1

            print(f"   {direction} ORDER EXECUTED!")
            print(f"      Trade ID: {fill.id}")
            print(f"      Fill Price: {fill.price}")
            print(f"      Stop Loss: {stop_loss_price:.5f}")
            print(f"      Take Profit: {take_profit_price:.5f}")

    except Exception as e:
        print(f"   ERROR: Trade execution failed: {e}")

def print_strategy_performance(strategy):
    """Display comprehensive strategy performance."""

    print(f"\nFINAL STRATEGY PERFORMANCE")
    print("=" * 35)

    stats = strategy.strategy_stats
    print(f"Total Trades: {stats['total_trades']}")

    if stats['total_trades'] > 0:
        win_rate = (stats['winning_trades'] / stats['total_trades']) * 100
        print(f"Winning Trades: {stats['winning_trades']}")
        print(f"Win Rate: {win_rate:.1f}%")
        print(f"Total P&L: ${stats['total_pnl']:+.2f}")

        if stats['total_pnl'] > 0:
            print("Profitable strategy performance!")
        elif stats['total_pnl'] < 0:
            print("Learning opportunity - analyze what happened")
        else:
            print("Breakeven performance")
    else:
        print("No trades executed during this period")

    print(f"\nStrategy Parameters:")
    print(f"   Instrument: {strategy.instrument}")
    print(f"   Position Size: {strategy.position_size} units")
    print(f"   Stop Loss: {strategy.stop_loss_pips} pips")
    print(f"   Take Profit: {strategy.take_profit_pips} pips")
    print(f"   Fast MA: {strategy.fast_ma_period} periods")
    print(f"   Slow MA: {strategy.slow_ma_period} periods")

# Run your complete strategy (uncomment to run)
# if __name__ == "__main__":
#     # strategy would be initialized elsewhere
#     asyncio.run(run_complete_trading_strategy(strategy, duration_minutes=5))
```

---

## Enhanced Strategy with Advanced Features

Here's an enhanced version with additional capabilities:

<!-- fragment: Demo enhanced strategy with magic numbers and decimal precision patterns -->
```python
from decimal import Decimal

from dotenv import load_dotenv

from fivetwenty import AsyncClient

# Load environment variables from .env file
load_dotenv()

# Enhanced strategy concepts (for further learning)
# Note: SimpleMovingAverageCrossover would be imported from previous lesson

class EnhancedTradingStrategy:  # SimpleMovingAverageCrossover
    """Enhanced strategy with additional features."""

    def __init__(self, instrument: str = "EUR_USD") -> None:
        # super().__init__(instrument)  # Uncomment if inheriting from SimpleMovingAverageCrossover

        # Basic strategy attributes (from parent class)
        self.instrument = instrument
        self.position_size = 1000
        self.max_risk_per_trade = 0.02
        self.stop_loss_pips = 20
        self.take_profit_pips = 30

        # Enhanced features
        self.max_daily_trades = 5
        self.daily_trade_count = 0
        self.trend_filter_enabled = True
        self.volatility_filter_enabled = True

    async def check_market_conditions(self, client: AsyncClient) -> dict:
        """Advanced market condition analysis."""

        conditions = {
            "trend": "neutral",
            "volatility": "normal",
            "spread": "normal",
            "tradeable": True,
        }

        try:
            # Check spread conditions
            pricing = await client.pricing.get_pricing(
                client.account_id,
                [self.instrument],
            )

            if pricing.prices:
                price = pricing.prices[0]
                bid = Decimal(str(price.bids[0].price))
                ask = Decimal(str(price.asks[0].price))
                spread = ask - bid

                if spread > 0.0005:  # 5 pips
                    conditions["spread"] = "wide"
                    conditions["tradeable"] = False

                # Add more sophisticated analysis here:
                # - Volatility measurement
                # - Trend strength calculation
                # - Economic calendar awareness
                # - Multi-timeframe analysis

        except Exception:
            conditions["tradeable"] = False

        return conditions

    def calculate_dynamic_position_size(self, account_balance: Decimal,
                                      volatility: Decimal) -> int:
        """Calculate position size based on account and market conditions."""

        # Base position size
        base_size = self.position_size

        # Adjust for volatility (reduce size in high volatility)
        if volatility > Decimal("0.002"):  # High volatility threshold
            base_size = int(base_size * Decimal("0.5"))
        elif volatility < Decimal("0.001"):  # Low volatility
            base_size = int(base_size * Decimal("1.2"))

        # Ensure we don't exceed risk limits
        max_size_by_risk = int(account_balance * self.max_risk_per_trade / 20)

        return min(base_size, max_size_by_risk, 2000)  # Cap at 2000 units

print("Strategy Enhancement Ideas:")
print("- Add volatility filters to avoid trading in choppy markets")
print("- Implement dynamic position sizing based on market conditions")
print("- Add time-of-day filters (avoid trading during low liquidity)")
print("- Include economic calendar integration")
print("- Implement portfolio-level risk management")
print("- Add machine learning for signal optimization")
```

---

## Performance Monitoring Dashboard

Monitor your strategy's real-time performance:

<!-- fragment: Demo performance monitoring with magic numbers and calculation patterns -->
```python
from datetime import datetime


class StrategyMonitor:
    """Monitor strategy performance in real-time."""

    def __init__(self, strategy):
        self.strategy = strategy
        self.start_time = datetime.now()
        self.daily_stats = {}

    def update_performance_metrics(self):
        """Calculate and update performance metrics."""

        current_time = datetime.now()
        runtime = (current_time - self.start_time).total_seconds() / 3600  # hours

        stats = self.strategy.strategy_stats

        metrics = {
            "runtime_hours": runtime,
            "total_trades": stats["total_trades"],
            "winning_trades": stats["winning_trades"],
            "total_pnl": stats["total_pnl"],
            "win_rate": (stats["winning_trades"] / max(stats["total_trades"], 1)) * 100,
            "trades_per_hour": stats["total_trades"] / max(runtime, 1),
            "pnl_per_hour": stats["total_pnl"] / max(runtime, 1),
        }

        return metrics

    def print_performance_dashboard(self):
        """Display real-time performance dashboard."""

        metrics = self.update_performance_metrics()

        print(f"\nSTRATEGY PERFORMANCE DASHBOARD")
        print("=" * 40)
        print(f"Runtime: {metrics['runtime_hours']:.1f} hours")
        print(f"Total Trades: {metrics['total_trades']}")
        print(f"Win Rate: {metrics['win_rate']:.1f}%")
        print(f"Total P&L: ${metrics['total_pnl']:+.2f}")
        print(f"Trades/Hour: {metrics['trades_per_hour']:.1f}")
        print(f"P&L/Hour: ${metrics['pnl_per_hour']:+.2f}")

        # Performance indicators
        if metrics["total_pnl"] > 0:
            print(f"Status: PROFITABLE")
        elif metrics["total_pnl"] < -100:
            print(f"Status: REVIEW NEEDED")
        else:
            print(f"Status: MONITORING")

# Example monitoring (strategy would be defined elsewhere)
# monitor = StrategyMonitor(strategy)
# monitor.print_performance_dashboard()
```

---


## What You've Learned

Success **Complete System Development**: Building production-ready automated trading systems

Success **Advanced Strategy Features**: Enhanced capabilities for real-world trading

Success **Production Deployment**: Checklist and best practices for live trading

Success **Performance Monitoring**: Real-time tracking and analysis of strategy performance

!!! success "Trading System Mastery Complete!"
    Incredible achievement! You've built a complete automated trading system from concept to production deployment. You understand the full development lifecycle, risk management, and operational requirements for successful algorithmic trading.

---

## Your Trading Journey Continues

### What You've Accomplished

Congratulations! You've successfully completed the comprehensive FiveTwenty trading tutorial series. You now possess:

Success **Level 1 - Foundation Knowledge**
- Deep understanding of forex concepts, pips, spreads, and order types
- Ability to analyze currency pair pricing and market dynamics

Success **Level 2 - Technical Proficiency**
- Skill connecting to OANDA API safely and securely
- Understanding of account management and margin concepts

Success **Level 3 - Trading Execution**
- Practical experience placing, monitoring, and closing trades
- Knowledge of position management and risk assessment

Success **Level 4 - System Development**
- Ability to build complete automated trading strategies
- Understanding of strategy design, backtesting, and optimization

### Ready for Advanced Learning?

**For Strategy Development:**
- Explore [Risk Management Fundamentals](../risk-management.md)
- Study [Advanced Order Types](../advanced-orders/index.md)
- Learn [Performance Optimization](../../guides/optimization/index.md)

**For Production Trading:**
- Set up [Live Trading Safely](../../guides/practical-solutions/setup-live-trading.md)

### Safety Reminders

!!! warning "Before Live Trading"
    1. **Practice extensively** with paper trading first
    2. **Start small** - use minimum position sizes initially
    3. **Never risk** more than you can afford to lose
    4. **Always use stop losses** and proper risk management
    5. **Keep learning** - markets constantly evolve

---

**Congratulations on completing your trading education foundation!**

Remember: **Successful trading requires practice, discipline, and continuous learning.** You've built the technical skills - now focus on developing the psychological discipline and market knowledge needed for long-term success.

**Happy Trading!**

---

## Related Resources

- [Account Management](../account-management.md) - Advanced analysis techniques
- [Streaming Data](../streaming-data.md) - Real-time data processing
- [API Reference](../../api-reference/index.md) - Complete technical documentation
