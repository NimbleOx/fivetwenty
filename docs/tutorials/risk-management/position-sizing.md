# Position Sizing Strategies

!!! tip "🎯 Learning Goal"
    Master advanced position sizing techniques to optimize risk management and maximize risk-adjusted returns.

---

## Why Position Sizing Matters

Position sizing is arguably the most important aspect of risk management. It determines:

- **How much you can lose** on any single trade
- **How much capital you can grow** over time
- **Your psychological comfort** while trading
- **Your ability to survive** losing streaks

!!! quote "💡 Professional Insight"
    "Position sizing is the only thing you have complete control over in trading. You can't control if you win or lose, but you can always control how much you risk." - Van Tharp

---

## Fixed Dollar Amount Strategy

The most straightforward approach to position sizing.

### Implementation

```python
import asyncio
from decimal import Decimal
from datetime import datetime

from fivetwenty import AsyncClient, Environment
from fivetwenty.exceptions import FiveTwentyError

# Configuration
TOKEN = "your-api-token-here"
ENVIRONMENT = Environment.PRACTICE

class PositionSizer:
    """Advanced position sizing calculator."""

    def __init__(self, account_balance: float, max_risk_percent: float = 1.0):
        self.account_balance = account_balance
        self.max_risk_percent = max_risk_percent
        self.max_risk_amount = account_balance * (max_risk_percent / 100)

    def calculate_position_size(self, entry_price: float, stop_loss: float,
                              instrument: str) -> int:
        """Calculate position size based on risk management rules."""

        # Calculate risk per unit
        risk_per_unit = abs(entry_price - stop_loss)

        if risk_per_unit == 0:
            print("⚠️ Warning: Entry price equals stop loss")
            return 0

        # Calculate position size
        position_size = int(self.max_risk_amount / risk_per_unit)

        # Get pip value for display
        pip_value = 0.01 if instrument.endswith('JPY') else 0.0001
        risk_pips = risk_per_unit / pip_value

        print(f"📊 Position Size Calculation:")
        print(f"   Max Risk: ${self.max_risk_amount:.2f} ({self.max_risk_percent}%)")
        print(f"   Entry Price: {entry_price:.5f}")
        print(f"   Stop Loss: {stop_loss:.5f}")
        print(f"   Risk per Unit: {risk_per_unit:.5f} ({risk_pips:.1f} pips)")
        print(f"   Position Size: {position_size:,} units")

        return position_size

    def validate_position_size(self, position_size: int, entry_price: float,
                             stop_loss: float) -> bool:
        """Validate that position size meets risk criteria."""

        risk_amount = abs(position_size) * abs(entry_price - stop_loss)
        risk_percent = (risk_amount / self.account_balance) * 100

        print(f"📋 Position Validation:")
        print(f"   Position Size: {abs(position_size):,} units")
        print(f"   Risk Amount: ${risk_amount:.2f}")
        print(f"   Risk Percentage: {risk_percent:.2f}%")

        if risk_percent > self.max_risk_percent:
            print(f"❌ Position size exceeds risk limit!")
            return False

        print(f"✅ Position size within risk limits")
        return True

# Example usage
async def demo_position_sizing(account_id: str):
    """Demonstrate position sizing calculations."""

    if not account_id:
        print("❌ No account ID")
        return

    async with AsyncClient(token=TOKEN, environment=ENVIRONMENT) as client:
        # Get account balance
        account = await client.accounts.get(account_id)
        balance = float(account.balance)

        # Create position sizer
        sizer = PositionSizer(balance, max_risk_percent=1.0)

        # Example trade setup
        instrument = "EUR_USD"
        entry_price = Decimal("1.1000")
        stop_loss = Decimal("1.0950")  # 50 pip stop

        # Calculate optimal position size
        position_size = sizer.calculate_position_size(entry_price, stop_loss, instrument)

        # Validate the calculation
        is_valid = sizer.validate_position_size(position_size, entry_price, stop_loss)

        return position_size if is_valid else 0
```

### Advantages
- **Straightforward to understand** and implement
- **Consistent risk** across all trades
- **Practical to track** and manage

### Disadvantages
- **Doesn't account for volatility** differences
- **May be too conservative** in low volatility
- **May be too aggressive** in high volatility

---

## Volatility-Based Position Sizing

A more sophisticated approach that adjusts position size based on market volatility.

### ATR-Based Position Sizing

```python
from decimal import Decimal

from fivetwenty import AsyncClient, Environment

import numpy as np
from fivetwenty.models import CandlestickGranularity

class VolatilityPositionSizer(PositionSizer):
    """Position sizing based on market volatility (ATR)."""

    async def calculate_atr_position_size(self, client: AsyncClient, instrument: str,
                                        atr_multiplier: float = 2.0) -> int:
        """Calculate position size based on Average True Range."""

        try:
            # Get historical data for ATR calculation
            candles = await client.instruments.candles(
                instrument=instrument,
                count=50,
                granularity=CandlestickGranularity.H4
            )

            # Calculate ATR
            true_ranges = []
            for i in range(1, len(candles.candles)):
                curr = candles.candles[i]
                prev = candles.candles[i-1]

                if curr.mid and prev.mid:
                    high = float(curr.mid.h)
                    low = float(curr.mid.l)
                    prev_close = float(prev.mid.c)

                    tr1 = high - low
                    tr2 = abs(high - prev_close)
                    tr3 = abs(low - prev_close)

                    true_range = max(tr1, tr2, tr3)
                    true_ranges.append(true_range)

            # Calculate 14-period ATR
            atr = sum(true_ranges[-14:]) / 14 if len(true_ranges) >= 14 else 0

            if atr == 0:
                print("❌ Could not calculate ATR")
                return 0

            # Get current price
            current_price = float(candles.candles[-1].mid.c)

            # Calculate stop loss based on ATR
            stop_distance = atr * atr_multiplier

            # Calculate position size
            position_size = int(self.max_risk_amount / stop_distance)

            pip_value = 0.01 if instrument.endswith('JPY') else 0.0001
            stop_pips = stop_distance / pip_value

            print(f"📊 ATR-Based Position Sizing:")
            print(f"   Current Price: {current_price:.5f}")
            print(f"   ATR: {atr:.5f}")
            print(f"   Stop Distance: {stop_distance:.5f} ({stop_pips:.1f} pips)")
            print(f"   Position Size: {position_size:,} units")

            return position_size

        except Exception as e:
            print(f"❌ ATR calculation error: {e}")
            return 0

# Example ATR position sizing
async def demo_atr_position_sizing(account_id: str):
    """Demonstrate ATR-based position sizing."""

    if not account_id:
        return

    async with AsyncClient(token=TOKEN, environment=ENVIRONMENT) as client:
        account = await client.accounts.get(account_id)
        balance = float(account.balance)

        sizer = VolatilityPositionSizer(balance, max_risk_percent=1.5)

        # Calculate position size based on volatility
        position_size = await sizer.calculate_atr_position_size(
            client, "EUR_USD", atr_multiplier=Decimal("2.0000")
        )

        return position_size
```

### How ATR Position Sizing Works

1. **Calculate ATR**: Measures recent price volatility
2. **Set Stop Distance**: Multiply ATR by factor (typically 1.5-3.0)
3. **Calculate Position Size**: Risk Amount / Stop Distance
4. **Result**: Smaller positions in volatile markets, larger in stable markets

### ATR Multiplier Guidelines

| Market Condition | ATR Multiplier | Rationale |
|------------------|----------------|-----------|
| Trending         | 2.0-2.5        | Give trend room to breathe |
| Ranging          | 1.5-2.0        | Tighter stops in sideways markets |
| Breakout         | 2.5-3.0        | Accommodate volatility expansion |
| News Events      | 3.0+           | Extra cushion for volatility spikes |

---

## Kelly Criterion Position Sizing

The most mathematically sophisticated approach to position sizing.

### The Kelly Formula

```python
class KellyPositionSizer:
    """Position sizing using Kelly Criterion."""

    def __init__(self, win_rate: float, avg_win: float, avg_loss: float):
        self.win_rate = win_rate / 100  # Convert percentage to decimal
        self.lose_rate = 1 - self.win_rate
        self.avg_win = avg_win
        self.avg_loss = abs(avg_loss)  # Ensure positive

    def calculate_kelly_percentage(self) -> float:
        """Calculate optimal bet size using Kelly formula."""

        if self.avg_loss == 0:
            return 0

        # Kelly formula: f = (bp - q) / b
        # where:
        # b = odds received (avg_win / avg_loss)
        # p = probability of winning (win_rate)
        # q = probability of losing (1 - win_rate)

        b = self.avg_win / self.avg_loss
        p = self.win_rate
        q = self.lose_rate

        kelly_fraction = (b * p - q) / b

        # Cap at reasonable maximum (25%)
        kelly_percentage = max(0, min(kelly_fraction * 100, 25))

        print(f"📊 Kelly Criterion Analysis:")
        print(f"   Win Rate: {self.win_rate * 100:.1f}%")
        print(f"   Average Win: ${self.avg_win:.2f}")
        print(f"   Average Loss: ${self.avg_loss:.2f}")
        print(f"   Win/Loss Ratio: {b:.2f}")
        print(f"   Kelly Percentage: {kelly_percentage:.2f}%")

        return kelly_percentage

    def calculate_position_size(self, account_balance: float, risk_per_unit: float) -> int:
        """Calculate position size using Kelly criterion."""

        kelly_percent = self.calculate_kelly_percentage()

        if kelly_percent <= 0:
            print("⚠️ Kelly criterion suggests no position")
            return 0

        # Use fraction of Kelly for safety (typically 25-50% of full Kelly)
        safety_factor = 0.25  # Use 25% of Kelly recommendation
        adjusted_kelly = kelly_percent * safety_factor

        risk_amount = account_balance * (adjusted_kelly / 100)
        position_size = int(risk_amount / risk_per_unit) if risk_per_unit > 0 else 0

        print(f"   Adjusted Kelly (25%): {adjusted_kelly:.2f}%")
        print(f"   Risk Amount: ${risk_amount:.2f}")
        print(f"   Position Size: {position_size:,} units")

        return position_size

# Demo Kelly sizing
def demo_kelly_sizing():
    """Demonstrate Kelly criterion position sizing."""

    # Example trading statistics
    win_rate = 60  # 60% win rate
    avg_win = 150  # Average win $150
    avg_loss = 100  # Average loss $100

    kelly_sizer = KellyPositionSizer(win_rate, avg_win, avg_loss)

    # Calculate for example account
    account_balance = 10000
    risk_per_unit = 0.50  # $0.50 risk per unit

    optimal_size = kelly_sizer.calculate_position_size(account_balance, risk_per_unit)

    return optimal_size
```

### Kelly Criterion Guidelines

**When to Use Kelly:**
- Have at least 30-50 trades of statistical data
- Trading strategy is well-defined and consistent
- Win rate and average win/loss are stable

**When NOT to Use Kelly:**
- New trading strategy without track record
- Highly variable win rates or profit/loss amounts
- Emotional or discretionary trading

**Safety Modifications:**
- **Fractional Kelly**: Use 25-50% of full Kelly recommendation
- **Maximum Cap**: Never exceed 5% of account on single trade
- **Minimum Floor**: Always maintain at least 0.5% minimum risk

---

## Adaptive Position Sizing

Adjust position sizes based on recent performance and market conditions.

### Performance-Based Adjustments

```python
from decimal import Decimal

class AdaptivePositionSizer:
    """Position sizer that adapts based on recent performance."""

    def __init__(self, base_risk_percent: float = 1.0):
        self.base_risk_percent = base_risk_percent
        self.recent_trades = []  # Track last 20 trades
        self.max_trades_tracked = 20

    def add_trade_result(self, profit_loss: float):
        """Add trade result to performance tracking."""
        self.recent_trades.append(profit_loss)
        
        # Keep only recent trades
        if len(self.recent_trades) > self.max_trades_tracked:
            self.recent_trades = self.recent_trades[-self.max_trades_tracked:]

    def calculate_adaptive_risk(self) -> float:
        """Calculate risk percentage based on recent performance."""
        
        if len(self.recent_trades) < 5:
            return self.base_risk_percent
        
        # Calculate recent performance metrics
        recent_pnl = sum(self.recent_trades)
        winning_trades = len([t for t in self.recent_trades if t > 0])
        win_rate = winning_trades / len(self.recent_trades)
        
        # Adjust risk based on performance
        risk_multiplier = 1.0
        
        # Reduce risk after losses
        if recent_pnl < 0:
            risk_multiplier *= 0.75  # Reduce by 25%
        elif recent_pnl > 0:
            risk_multiplier *= 1.1   # Increase by 10%
        
        # Adjust based on win rate
        if win_rate < 0.4:
            risk_multiplier *= 0.8   # Reduce for low win rate
        elif win_rate > 0.6:
            risk_multiplier *= 1.05  # Small increase for high win rate
        
        # Calculate adjusted risk
        adjusted_risk = self.base_risk_percent * risk_multiplier
        
        # Apply safety limits
        adjusted_risk = max(0.25, min(adjusted_risk, 2.0))  # 0.25% - 2% range
        
        print(f"🎯 Adaptive Risk Calculation:")
        print(f"   Base Risk: {self.base_risk_percent:.2f}%")
        print(f"   Recent P/L: ${recent_pnl:+.2f}")
        print(f"   Win Rate: {win_rate:.1%}")
        print(f"   Risk Multiplier: {risk_multiplier:.2f}")
        print(f"   Adjusted Risk: {adjusted_risk:.2f}%")
        
        return adjusted_risk

    def get_position_size(self, account_balance: float, entry_price: float, 
                         stop_loss: float) -> int:
        """Get adaptive position size."""
        
        risk_percent = self.calculate_adaptive_risk()
        risk_amount = account_balance * (risk_percent / 100)
        risk_per_unit = abs(entry_price - stop_loss)
        
        position_size = int(risk_amount / risk_per_unit) if risk_per_unit > 0 else 0
        
        return position_size

# Example adaptive sizing
def demo_adaptive_sizing():
    """Demonstrate adaptive position sizing."""
    
    sizer = AdaptivePositionSizer(base_risk_percent=1.0)
    
    # Simulate some trade results
    trade_results = [-50, 100, -75, 150, -25, 200, -100, 80]
    
    for result in trade_results:
        sizer.add_trade_result(result)
    
    # Calculate position size
    position_size = sizer.get_position_size(
        account_balance=10000,
        entry_price=Decimal("1.1000"),
        stop_loss=Decimal("1.0950")
    )
    
    print(f"   Recommended Position Size: {position_size:,} units")
    
    return sizer
```

---

## Position Sizing Comparison

### Strategy Comparison Table

| Strategy | Complexity | Adaptability | Data Required | Best For |
|----------|------------|--------------|---------------|----------|
| Fixed Dollar | Low | None | Account balance | Beginners |
| Fixed Percentage | Low | None | Account balance | Consistent markets |
| ATR-Based | Medium | Market volatility | Historical prices | Varying volatility |
| Kelly Criterion | High | Performance stats | 30+ trade history | Systematic strategies |
| Adaptive | High | Recent performance | Ongoing trade results | Experienced traders |

### Choosing Your Approach

**For Beginners:**
Start with fixed percentage (1% rule) until you develop consistency.

**For Intermediate Traders:**
Combine fixed percentage with volatility adjustments (ATR-based).

**For Advanced Traders:**
Use Kelly Criterion with safety modifications and adaptive adjustments.

---

## ✅ Skill Checkpoint: Position Sizing

Test your understanding of position sizing strategies:

!!! question "🧠 Test Your Understanding"
    1. **Why does ATR-based sizing reduce risk in volatile markets?**
       <details>
       <summary>Click to reveal answer</summary>
       **Larger stop distances mean smaller position sizes for the same dollar risk**. When volatility increases, ATR increases, requiring wider stops, which automatically reduces position size to maintain consistent dollar risk.
       </details>

    2. **What's the main risk of using full Kelly Criterion sizing?**
       <details>
       <summary>Click to reveal answer</summary>
       **Overbetting and increased volatility**. Full Kelly can recommend very large position sizes that create excessive portfolio volatility and psychological stress. Most professionals use 25-50% of Kelly recommendation.
       </details>

    3. **When should you increase your position size above normal?**
       <details>
       <summary>Click to reveal answer</summary>
       **Only after proven consistent profitability with your base size**. Increase gradually (not more than 50% above base) and only when you have statistical evidence your strategy works.
       </details>

---

## Position Sizing Best Practices

### Implementation Guidelines

1. **Start Conservative**
   - Begin with 0.5-1% risk per trade
   - Only increase after consistent profitability
   - Never jump from 1% to 5% - increase gradually

2. **Use Multiple Methods**
   - Calculate position size using 2-3 methods
   - Take the most conservative result
   - Cross-validate your calculations

3. **Account for Correlation**
   - Reduce position sizes for correlated trades
   - Don't risk 1% on EUR/USD and 1% on GBP/USD simultaneously
   - Consider currency exposure across all positions

4. **Monitor and Adjust**
   - Track actual vs intended risk
   - Review position sizing monthly
   - Adjust based on account growth

### Position Sizing Checklist

```python
from decimal import Decimal

def validate_position_size_decision(account_balance: float, position_size: int,
                                   entry_price: float, stop_loss: float,
                                   instrument: str) -> dict:
    """Comprehensive position size validation."""
    
    validation = {
        'checks': [],
        'warnings': [],
        'errors': [],
        'approved': True
    }
    
    # Calculate risk metrics
    risk_amount = abs(position_size) * abs(entry_price - stop_loss)
    risk_percent = (risk_amount / account_balance) * 100
    
    # Risk percentage check
    if risk_percent <= 1.0:
        validation['checks'].append(f"✅ Risk {risk_percent:.2f}% within 1% limit")
    elif risk_percent <= 2.0:
        validation['warnings'].append(f"⚠️ Risk {risk_percent:.2f}% above 1% but acceptable")
    else:
        validation['errors'].append(f"❌ Risk {risk_percent:.2f}% exceeds safe limits")
        validation['approved'] = False
    
    # Position size reasonableness
    if abs(position_size) <= 10000:
        validation['checks'].append("✅ Position size reasonable")
    elif abs(position_size) <= 50000:
        validation['warnings'].append("⚠️ Large position size")
    else:
        validation['errors'].append("❌ Excessive position size")
        validation['approved'] = False
    
    # Stop loss presence
    if stop_loss != entry_price:
        validation['checks'].append("✅ Stop loss defined")
    else:
        validation['errors'].append("❌ No stop loss defined")
        validation['approved'] = False
    
    return validation

# Example validation
result = validate_position_size_decision(
    account_balance=10000,
    position_size=2000,
    entry_price=Decimal("1.1000"),
    stop_loss=Decimal("1.0950"),
    instrument="EUR_USD"
)

print("📋 Position Size Validation:")
for check in result['checks']:
    print(f"   {check}")
for warning in result['warnings']:
    print(f"   {warning}")
for error in result['errors']:
    print(f"   {error}")
print(f"   Approved: {'Yes' if result['approved'] else 'No'}")
```

---

## What You've Learned

✅ **Fixed Dollar Strategy**: Basic, consistent approach for beginners

✅ **Volatility-Based Sizing**: ATR-based adjustments for market conditions

✅ **Kelly Criterion**: Mathematical optimization for experienced traders

✅ **Adaptive Sizing**: Performance-based adjustments for dynamic risk management

✅ **Validation Systems**: Comprehensive checks to prevent costly mistakes

!!! success "🎉 Position Sizing Mastery Complete!"
    You now have a complete toolkit for calculating optimal position sizes in any market condition. These techniques will help you balance risk and reward while maintaining capital preservation. Next, learn advanced stop loss strategies.

---

## Next Steps

Continue to [Stop Loss Strategies](stop-loss-strategies.md) to learn how to protect your positions with sophisticated stop loss techniques.

---

## Related Resources

- **[Risk Management Fundamentals](fundamentals.md)** - Core risk management principles
- **[Portfolio Risk Management](portfolio-risk.md)** - Managing risk across multiple positions
- **[Performance Optimization](performance-optimization.md)** - Advanced risk-adjusted metrics
- **[Position Management](../basic-trading/lesson-5-position-management.md)** - Individual position management techniques