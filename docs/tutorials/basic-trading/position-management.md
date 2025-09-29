# Position Management

!!! tip "Target Learning Goal"
    Master advanced position management techniques including stop losses, take profits, and risk-to-reward optimization.

---

## Understanding Position Management

Position management is the art of maximizing profits while controlling risk after entering a trade.

<!-- fragment: Demo position management with trade attribute access and dict type issues -->
```python
import asyncio
from decimal import Decimal
from dotenv import load_dotenv
from fivetwenty import AsyncClient

# Load environment variables from .env file
load_dotenv()

async def demonstrate_position_management(trade_id: str) -> None:
    """Learn position management techniques."""

    if not trade_id:
        print("Error No trade for position management demo")
        return

    print("🎛️ POSITION MANAGEMENT TECHNIQUES")
    print("=" * 40)

    # Zero-config - automatically uses environment variables
    async with AsyncClient() as client:
        # Get current trade
        trade = await client.trades.get_trade(client.account_id, trade_id)

        print("Data Current Position:")
        print(f"   Trade ID: {trade.id}")
        print(f"   Instrument: {trade.instrument}")
        print(f"   Units: {trade.current_units}")
        print(f"   Entry Price: {trade.price}")
        print(f"   Current P&L: ${Decimal(str(trade.unrealized_pl)):+.2f}")

        # Demonstrate different exit strategies
        print("\nTarget Exit Strategy Options:")

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

        print("   Risk/Reward Ratio: 1:1.5 (risking 20 pips to make 30 pips)")

        # Step 7: Educational note about implementation
        # In practice, these levels would be set using FiveTwenty's order management
        print("\nNote In real trading, you would implement these levels using:")
        print("   • Stop Loss orders for automatic risk management")
        print("   • Take Profit orders to secure gains automatically")
        print("   • Position monitoring for dynamic adjustments")
        print("   • Trailing stops to lock in profits as price moves favorably")
        print("\nConfig FiveTwenty Implementation:")
        print("   • Use StopLossOrderRequest to set protective stops")
        print("   • Use TakeProfitOrderRequest to secure profit targets")
        print("   • Monitor positions via client.trades.get_trades()")
        print("   • Close positions with client.positions.close_position()")

# Demonstrate position management
if __name__ == "__main__":
    # Replace with actual trade_id from your trading activity
    trade_id = "your_trade_id_here"
    asyncio.run(demonstrate_position_management(trade_id))
```

---

## Advanced Stop Loss Strategies

Different types of stop losses for different market conditions:

<!-- fragment: Demo stop loss strategies with docstring format and unnecessary else patterns -->
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

print("\nSecurity Stop Loss Strategy Examples:")
print(f"Entry Price: {entry_price:.5f}")
print(f"Position Type: {'Long' if is_long_position else 'Short'}")

# Strategy 1: Fixed pip distance (simple and predictable)
fixed_stop = StopLossStrategy.fixed_pip_stop(entry_price, is_long_position, 20)
print(f"Fixed 20-pip stop: {fixed_stop:.5f} (Risk: 20 pips)")

# Strategy 2: Percentage-based (scales with price)
percent_stop = StopLossStrategy.percentage_stop(entry_price, is_long_position, Decimal("0.005"))
print(f"0.5% stop: {percent_stop:.5f} (Risk: {((entry_price - percent_stop) * 10000):.1f} pips)")

# Strategy 3: Volatility-adjusted using simulated ATR value
# ATR of 0.0015 means average daily range is 15 pips
atr_stop = StopLossStrategy.atr_stop(entry_price, is_long_position, Decimal("0.0015"), Decimal("2.0"))
print(f"2x ATR stop: {atr_stop:.5f} (Risk: {((entry_price - atr_stop) * 10000):.1f} pips)")

# Strategy 4: Technical level-based (example with support at 1.0950)
support_level = Decimal("1.0950")
tech_stop = StopLossStrategy.support_resistance_stop(entry_price, is_long_position, support_level, 5)
print(f"Support-based stop: {tech_stop:.5f} (5 pips below support level)")
```

---

## Take Profit Strategies

Maximize profits with intelligent take profit placement:

<!-- fragment: Demo take profit strategies with docstring format and ternary operator patterns -->
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

print("\nTarget Take Profit Strategy Examples:")

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
    """Advanced position sizing strategies for optimal risk management."""

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

print(f"Balance Position Sizing Example:")
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

print(f"\nData Volatility Adjustment:")
print(f"Base Position: {base_position} units")
print(f"Current Volatility: {current_vol:.4f}")
print(f"Average Volatility: {average_vol:.4f}")
print(f"Adjusted Position: {adjusted_size} units")
```

---


## Using FiveTwenty for Position Management

Use FiveTwenty's order management APIs to set stop losses and take profits when opening positions. Monitor positions using the trades endpoint and close them using the position close methods when needed.

---

## What You've Learned

Success **Advanced Stop Loss Strategies**: Multiple approaches for different market conditions

Success **Take Profit Optimization**: Maximizing profits with intelligent exit strategies

Success **Position Monitoring**: Tracking performance and adjusting positions dynamically

Success **Position Sizing Mastery**: Risk-based and volatility-adjusted position sizing

!!! success "Complete Position Management Mastery Complete!"
    Excellent! You now have advanced skills for managing trading positions effectively. You understand how to balance risk and reward while maximizing profit potential. Next, you'll learn to build complete trading strategies.

---

## Next Steps

Continue to [Strategy Building](strategy-building.md) to learn how to combine your skills into systematic trading approaches.

---

## Related Resources

- [Risk Management Fundamentals](../risk-management.md) - Comprehensive risk control
- [Advanced Stop-Loss Strategies](../../guides/practical-solutions/implement-stop-loss-strategies.md) - Detailed stop loss techniques
- [Trading Models](../../api-reference/models/trading-models.md) - Technical API documentation