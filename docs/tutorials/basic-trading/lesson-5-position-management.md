# Lesson 5: Position Management Mastery

!!! tip "🎯 Learning Goal"
    Master advanced position management techniques including stop losses, take profits, and risk-to-reward optimization.

---

## Understanding Position Management

Position management is the art of maximizing profits while controlling risk after entering a trade.

```python
from decimal import Decimal
from fivetwenty import AsyncClient, Environment

async def demonstrate_position_management(account_id: str, trade_id: str):
    """Learn position management techniques."""

    if not trade_id:
        print("❌ No trade for position management demo")
        return

    print("🎛️ POSITION MANAGEMENT TECHNIQUES")
    print("=" * 40)

    async with AsyncClient(token=TOKEN, account_id="your-account-id", environment=ENVIRONMENT) as client:
        # Get current trade
        trade = await client.trades.get_trade(account_id, trade_id)

        print(f"📊 Current Position:")
        print(f"   Trade ID: {trade.id}")
        print(f"   Instrument: {trade.instrument}")
        print(f"   Units: {trade.current_units}")
        print(f"   Entry Price: {trade.price}")
        print(f"   Current P&L: ${Decimal(str(trade.unrealized_pl)):+.2f}")

        # Demonstrate different exit strategies
        print(f"\n🎯 Exit Strategy Options:")

        entry_price = Decimal(str(trade.price))
        is_long = int(trade.current_units) > 0

        if is_long:
            stop_loss_price = entry_price - Decimal("0.0020")  # 20 pips stop
            take_profit_price = entry_price + Decimal("0.0030")  # 30 pips profit
            print(f"   Stop Loss: {stop_loss_price:.5f} (20 pips below entry)")
            print(f"   Take Profit: {take_profit_price:.5f} (30 pips above entry)")
        else:
            stop_loss_price = entry_price + Decimal("0.0020")  # 20 pips stop
            take_profit_price = entry_price - Decimal("0.0030")  # 30 pips profit
            print(f"   Stop Loss: {stop_loss_price:.5f} (20 pips above entry)")
            print(f"   Take Profit: {take_profit_price:.5f} (30 pips below entry)")

        print(f"   Risk/Reward Ratio: 1:1.5 (risking 20 pips to make 30 pips)")

        # Don't actually set stop loss in tutorial - just demonstrate
        print(f"\n💡 In real trading, you would set these levels using:")
        print(f"   • Stop Loss orders for risk management")
        print(f"   • Take Profit orders to secure gains")
        print(f"   • Position monitoring for optimal exits")

# Demonstrate position management
if trade_id:
    await demonstrate_position_management(account_id, trade_id)
```

---

## Advanced Stop Loss Strategies

Different types of stop losses for different market conditions:

```python
from decimal import Decimal



class StopLossStrategy:
    """Advanced stop loss calculation strategies."""

    @staticmethod
    def fixed_pip_stop(entry_price: Decimal, is_long: bool, pip_distance: int) -> Decimal:
        """Fixed pip distance stop loss."""
        pip_value = Decimal("0.0001")
        if is_long:
            return entry_price - (pip_distance * pip_value)
        else:
            return entry_price + (pip_distance * pip_value)

    @staticmethod
    def percentage_stop(entry_price: Decimal, is_long: bool, percentage: Decimal) -> Decimal:
        """Percentage-based stop loss."""
        if is_long:
            return entry_price * (1 - percentage)
        else:
            return entry_price * (1 + percentage)

    @staticmethod
    def atr_stop(entry_price: Decimal, is_long: bool, atr_value: Decimal, multiplier: Decimal = Decimal("2.0")) -> Decimal:
        """ATR (Average True Range) based stop loss."""
        stop_distance = atr_value * multiplier
        if is_long:
            return entry_price - stop_distance
        else:
            return entry_price + stop_distance

    @staticmethod
    def support_resistance_stop(entry_price: Decimal, is_long: bool, level: Decimal, buffer_pips: int = 5) -> Decimal:
        """Stop loss based on support/resistance levels."""
        buffer = buffer_pips * Decimal("0.0001")
        if is_long:
            return level - buffer  # Below support
        else:
            return level + buffer  # Above resistance

# Example usage
entry_price = Decimal("1.1000")
is_long_position = True

# Expected output: "🛡️ Stop Loss Strategy Examples:"
print(f"Entry Price: {entry_price:.5f}")

fixed_stop = StopLossStrategy.fixed_pip_stop(entry_price, is_long_position, 20)
print(f"Fixed 20-pip stop: {fixed_stop:.5f}")

percent_stop = StopLossStrategy.percentage_stop(entry_price, is_long_position, 0.005)
print(f"0.5% stop: {percent_stop:.5f}")

# Simulated ATR value
atr_stop = StopLossStrategy.atr_stop(entry_price, is_long_position, 0.0015, 2.0)
print(f"2x ATR stop: {atr_stop:.5f}")
```

---

## Take Profit Strategies

Maximize profits with intelligent take profit placement:

```python
from decimal import Decimal


class TakeProfitStrategy:
    """Advanced take profit strategies."""

    @staticmethod
    def fixed_target(entry_price: Decimal, is_long: bool, target_pips: int) -> Decimal:
        """Fixed pip target."""
        pip_value = Decimal("0.0001")
        if is_long:
            return entry_price + (target_pips * pip_value)
        else:
            return entry_price - (target_pips * pip_value)

    @staticmethod
    def risk_reward_ratio(entry_price: Decimal, stop_loss: Decimal, is_long: bool, ratio: Decimal = Decimal("2.0")) -> Decimal:
        """Take profit based on risk-reward ratio."""
        risk = abs(entry_price - stop_loss)
        reward = risk * ratio

        if is_long:
            return entry_price + reward
        else:
            return entry_price - reward

    @staticmethod
    def multiple_targets(entry_price: Decimal, is_long: bool, targets: list) -> list:
        """Multiple take profit levels for scaling out."""
        pip_value = Decimal("0.0001")
        take_profits = []

        for target_pips in targets:
            if is_long:
                tp = entry_price + (Decimal(str(target_pips)) * pip_value)
            else:
                tp = entry_price - (Decimal(str(target_pips)) * pip_value)
            take_profits.append(tp)

        return take_profits

# Example usage
entry_price = Decimal("1.1000")
stop_loss = Decimal("1.0980")
is_long_position = True

print("\n🎯 Take Profit Strategy Examples:")

fixed_tp = TakeProfitStrategy.fixed_target(entry_price, is_long_position, 30)
print(f"Fixed 30-pip target: {fixed_tp:.5f}")

rr_tp = TakeProfitStrategy.risk_reward_ratio(entry_price, stop_loss, is_long_position, Decimal("2.0"))
print(f"2:1 Risk-Reward target: {rr_tp:.5f}")

multiple_tps = TakeProfitStrategy.multiple_targets(entry_price, is_long_position, [15, 30, 50])
print(f"Multiple targets: {[f'{tp:.5f}' for tp in multiple_tps]}")
```

---


## Position Sizing and Risk Management

Advanced position sizing based on volatility and risk:

```python
from decimal import Decimal

class AdvancedPositionSizing:
    """Advanced position sizing strategies."""

    @staticmethod
    def fixed_risk_sizing(account_balance: Decimal, risk_percent: Decimal,
                         entry_price: Decimal, stop_loss: Decimal) -> int:
        """Calculate position size based on fixed risk percentage."""

        risk_amount = account_balance * (risk_percent / 100)
        price_risk = abs(entry_price - stop_loss)

        if price_risk <= 0:
            return 0

        # For forex, 1 pip = $1 per 10,000 units for most pairs
        pip_risk = price_risk / Decimal("0.0001")
        risk_per_pip = risk_amount / pip_risk
        position_size = int(risk_per_pip * Decimal("10000"))

        return position_size

    @staticmethod
    def volatility_adjusted_sizing(base_position: int, current_volatility: Decimal,
                                 average_volatility: Decimal) -> int:
        """Adjust position size based on current volatility."""

        volatility_ratio = average_volatility / current_volatility
        adjusted_size = int(base_position * volatility_ratio)

        # Cap adjustments to reasonable ranges
        return max(int(base_position * Decimal("0.5")), min(adjusted_size, int(base_position * Decimal("1.5"))))

# Example position sizing
account_balance = Decimal("10000")
risk_percent = Decimal("1.0")  # 1% risk
entry_price = Decimal("1.1000")
stop_loss = Decimal("1.0980")

position_size = AdvancedPositionSizing.fixed_risk_sizing(
    account_balance, risk_percent, entry_price, stop_loss
)

print(f"💰 Position Sizing Example:")
print(f"Account Balance: ${account_balance}")
print(f"Risk Percentage: {risk_percent}%")
print(f"Entry Price: {entry_price:.5f}")
print(f"Stop Loss: {stop_loss:.5f}")
print(f"Calculated Position Size: {position_size} units")

# Volatility adjustment
base_position = 5000
current_vol = Decimal("0.0015")  # Current volatility
average_vol = Decimal("0.0012")  # Average volatility

adjusted_size = AdvancedPositionSizing.volatility_adjusted_sizing(
    base_position, current_vol, average_vol
)

print(f"\n📊 Volatility Adjustment:")
print(f"Base Position: {base_position} units")
print(f"Current Volatility: {current_vol:.4f}")
print(f"Average Volatility: {average_vol:.4f}")
print(f"Adjusted Position: {adjusted_size} units")
```

---

## Skill Checkpoint: Advanced Position Management

Test your understanding of position management:

!!! question "🧠 Test Your Understanding"
    1. **What's the benefit of using a 2:1 risk-reward ratio?**
       <details>
       <summary>Click to reveal answer</summary>
       **Profitable even with 50% win rate**. If you risk $100 to make $200, you can be wrong half the time and still be profitable overall.
       </details>

    2. **How do you optimize take profit levels?**
       <details>
       <summary>Click to reveal answer</summary>
       **Use technical analysis and risk-reward ratios**. Target key resistance levels and maintain at least 1:2 risk-reward ratios for profitable trading.
       </details>

    3. **Why adjust position size based on volatility?**
       <details>
       <summary>Click to reveal answer</summary>
       **Maintain consistent risk levels**. High volatility = smaller positions, low volatility = larger positions, keeping your dollar risk constant regardless of market conditions.
       </details>

---

## Position Management Best Practices

### Before Entering
- ✅ Plan your exit strategy before entering
- ✅ Calculate position size based on risk
- ✅ Set stop loss and take profit levels
- ✅ Consider market volatility

### While In Position
- ✅ Monitor price action and your levels
- ✅ Monitor position performance continuously
- ✅ Be prepared to exit if analysis changes
- ✅ Don't move stops against you

### After Exiting
- ✅ Analyze what worked and what didn't
- ✅ Document lessons learned
- ✅ Plan improvements for next trade
- ✅ Maintain trading journal

---

## What You've Learned

✅ **Advanced Stop Loss Strategies**: Multiple approaches for different market conditions

✅ **Take Profit Optimization**: Maximizing profits with intelligent exit strategies

✅ **Position Monitoring**: Tracking performance and adjusting positions dynamically

✅ **Position Sizing Mastery**: Risk-based and volatility-adjusted position sizing

!!! success "🎉 Position Management Mastery Complete!"
    Excellent! You now have advanced skills for managing trading positions effectively. You understand how to balance risk and reward while maximizing profit potential. Next, you'll learn to build complete trading strategies.

---

## Next Steps

Continue to [Lesson 6: Building Trading Strategies](lesson-6-strategy-building.md) to learn how to combine your skills into systematic trading approaches.

---

## Related Resources

- [Risk Management Fundamentals](../risk-management/index.md) - Comprehensive risk control
- [Advanced Stop-Loss Strategies](../../how-to-guides/implement-stop-loss-strategies.md) - Detailed stop loss techniques
- [Trading Models](../../api-reference/models/trading-models.md) - Technical API documentation