# Risk Management Fundamentals

!!! tip "🎯 Learning Goal"
    Master the essential concepts and principles that form the foundation of effective risk management in trading.

---

## The 3 Pillars of Risk Management

Every successful trading strategy is built on three fundamental pillars:

### 1. Position Sizing
**How much to risk per trade**
- Determines your exposure to any single trade
- Controls the impact of individual wins and losses
- Should be calculated systematically, not guessed

### 2. Stop Losses
**Limiting downside on individual trades**
- Your insurance policy against excessive losses
- Must be set before entering any trade
- Should be honored without exception

### 3. Portfolio Management
**Managing overall exposure**
- Controls risk across all positions
- Monitors correlation and concentration risk
- Ensures no single event can destroy your account

!!! warning "⚠️ All Three Pillars Required"
    Neglecting any one of these pillars substantially increases your risk of catastrophic loss. They work together as a comprehensive risk control system.

---

## Key Risk Metrics Every Trader Must Know

### Risk per Trade
**Percentage of account risked on single trade**
- Most important metric for capital preservation
- Should never exceed 1-2% for most traders
- Calculated as: (Position Size × Stop Distance) / Account Balance

### Win Rate
**Percentage of profitable trades**
- Important but not the only factor
- Can be profitable with 40% win rate if risk/reward is good
- Focus on overall expectancy, not just win rate

### Risk/Reward Ratio
**Average profit vs average loss**
- Minimum 1.5:1 recommended for most strategies
- 2:1 or higher preferred for long-term success
- Allows profitability even with lower win rates

### Maximum Drawdown
**Largest peak-to-trough decline**
- Measures your worst losing streak
- Critical for psychological resilience
- Should be limited to 15-20% maximum

### Sharpe Ratio
**Risk-adjusted returns**
- Measures return per unit of risk taken
- Higher values indicate better risk-adjusted performance
- Useful for comparing different strategies

---

## The 1% Rule: Your Safety Net

**The golden rule: Never risk more than 1-2% of your account on a single trade.**

### Why the 1% Rule Works

```python
from decimal import Decimal

# Example: $10,000 account with 1% risk
account_balance = Decimal("10000")  # Example account balance
risk_per_trade = account_balance * Decimal("0.01")  # $100 maximum risk

print(f"Account Balance: ${account_balance:,}")
print(f"Maximum Risk per Trade: ${risk_per_trade}")
print(f"Number of consecutive losses to lose 50%: {0.5 / 0.01:.0f} trades")
print(f"Number of consecutive losses to lose 90%: {0.9 / 0.01:.0f} trades")
```

**With 1% risk:**
- You can survive 69 consecutive losses before losing 50% of your account
- Takes 230 consecutive losses to lose 90% of your account
- Provides enormous cushion for learning and strategy development

### Risk Percentage Impact

| Risk % | Consecutive Losses to Lose 50% | Psychological Impact |
|--------|--------------------------------|---------------------|
| 1%     | 69 trades                      | Low stress           |
| 2%     | 35 trades                      | Moderate stress      |
| 5%     | 14 trades                      | High stress          |
| 10%    | 7 trades                       | Extreme stress       |

---

## Risk vs Reward Psychology

### The Trader's Dilemma

Most new traders face this psychological conflict:

- **Want high returns** → Take big risks
- **Fear of losses** → Avoid necessary risks
- **Emotional trading** → Inconsistent results

### The Professional Approach

**Professionals focus on:**
1. **Consistent execution** over big wins
2. **Process over outcomes** for individual trades
3. **Long-term expectancy** over short-term results
4. **Capital preservation** as the primary goal

!!! quote "💡 Professional Mindset"
    "My job is not to be right. My job is to make money. I make money by managing risk, not by predicting markets." - Professional Trader

---

## Building Your Risk Management Foundation

### Step 1: Define Your Risk Tolerance
```python
def calculate_risk_parameters(account_balance: Decimal, monthly_income: Decimal,
                            emergency_fund: Decimal) -> dict:
    """Calculate personalized risk parameters."""
    
    # Never risk money you need for living expenses
    tradeable_capital = min(account_balance, emergency_fund * 0.5)
    
    # Conservative risk parameters
    max_risk_per_trade = tradeable_capital * 0.01  # 1%
    max_daily_risk = tradeable_capital * 0.05      # 5%
    max_monthly_risk = tradeable_capital * 0.20    # 20%
    
    return {
        'tradeable_capital': tradeable_capital,
        'max_risk_per_trade': max_risk_per_trade,
        'max_daily_risk': max_daily_risk,
        'max_monthly_risk': max_monthly_risk
    }

# Example calculation with sample financial values
params = calculate_risk_parameters(
    account_balance=Decimal("10000"),  # Example: $10,000 trading account
    monthly_income=Decimal("5000"),   # Example: $5,000 monthly income
    emergency_fund=Decimal("15000")   # Example: $15,000 emergency fund
)

print("📊 Your Risk Parameters:")
for key, value in params.items():
    print(f"   {key.replace('_', ' ').title()}: ${value:,.2f}")
```

### Step 2: Establish Risk Rules

Create written rules before you start trading:

**Position Size Rules:**
- Never risk more than 1% per trade
- Reduce risk to 0.5% during losing streaks
- Increase to 1.5% only after proven profitability

**Stop Loss Rules:**
- Every trade must have a stop loss before entry
- Never move stop loss against you
- Honor stop losses without exception

**Portfolio Rules:**
- Maximum 10 open positions simultaneously
- Maximum 20% total portfolio risk
- Maximum 5% risk in any single currency

### Step 3: Implement Tracking Systems

```python
class RiskTracker:
    """Track risk metrics in real-time."""
    
    def __init__(self, account_balance: Decimal):
        self.account_balance = account_balance
        self.daily_trades = []
        self.open_risks = {}
    
    def add_trade_risk(self, trade_id: str, risk_amount: Decimal):
        """Add new trade risk to tracking."""
        self.open_risks[trade_id] = risk_amount
        self.daily_trades.append(risk_amount)
    
    def get_current_risk_exposure(self) -> dict:
        """Calculate current risk exposure."""
        total_risk = sum(self.open_risks.values())
        risk_percentage = (total_risk / self.account_balance) * 100
        
        return {
            'total_risk_amount': total_risk,
            'risk_percentage': risk_percentage,
            'open_positions': len(self.open_risks),
            'within_limits': risk_percentage <= 20  # 20% max portfolio risk
        }

# Example usage with sample account balance
tracker = RiskTracker(Decimal("10000"))  # Example: $10,000 account balance
tracker.add_trade_risk("trade_1", 100)  # $100 risk
tracker.add_trade_risk("trade_2", 75)   # $75 risk

exposure = tracker.get_current_risk_exposure()
print(f"Current Risk: ${exposure['total_risk_amount']} ({exposure['risk_percentage']:.1f}%)")
print(f"Within Limits: {'Yes' if exposure['within_limits'] else 'No'}")
```

---

## ✅ Skill Checkpoint: Risk Fundamentals

Test your understanding of risk management fundamentals:

!!! question "🧠 Test Your Understanding"
    1. **Why is the 1% rule so important for new traders?**
       <details>
       <summary>Click to reveal answer</summary>
       **Provides enormous room for error while learning**. New traders make mistakes, and 1% risk ensures these mistakes don't destroy the account before skills develop.
       </details>

    2. **What's more important: win rate or risk/reward ratio?**
       <details>
       <summary>Click to reveal answer</summary>
       **Risk/reward ratio is generally more important**. You can be profitable with 40% win rate if your average win is 2x your average loss, but you can't overcome poor R/R with high win rate alone.
       </details>

    3. **How do the three pillars of risk management work together?**
       <details>
       <summary>Click to reveal answer</summary>
       **Position sizing limits individual trade impact, stop losses prevent catastrophic losses, and portfolio management ensures diversification**. Together they create multiple layers of protection.
       </details>

---

## Risk Management Philosophy

### Core Principles

1. **Capital Preservation First**
   - Your first goal is not to lose money
   - Growth comes second to survival
   - Small consistent gains compound powerfully

2. **Risk Management is Profit Management**
   - Controlling losses indirectly controls profits
   - Better risk management = more consistent returns
   - Reduced stress = better decision making

3. **Plan Your Risk Before You Trade**
   - Never enter a trade without knowing your risk
   - Risk planning prevents emotional decisions
   - Clear rules enable systematic execution

### The Compound Effect

Small improvements in risk management compound dramatically:

```python
def compare_risk_strategies(initial_balance: Decimal, months: int):
    """Compare different risk management approaches."""
    
    strategies = {
        'Conservative (1% risk)': {'risk': 0.01, 'win_rate': 0.55, 'rr': 1.8},
        'Moderate (2% risk)': {'risk': 0.02, 'win_rate': 0.55, 'rr': 1.8},
        'Aggressive (5% risk)': {'risk': 0.05, 'win_rate': 0.55, 'rr': 1.8}
    }
    
    for name, params in strategies.items():
        balance = initial_balance
        trades_per_month = 20
        
        for month in range(months):
            for trade in range(trades_per_month):
                risk_amount = balance * params['risk']
                
                if random.random() < params['win_rate']:
                    # Win
                    balance += risk_amount * params['rr']
                else:
                    # Loss
                    balance -= risk_amount
                    
                # Prevent balance from going negative
                balance = max(balance, 0)
        
        print(f"{name}: ${balance:,.2f} (Return: {(balance/initial_balance-1)*100:+.1f}%)")

# Demonstrate the power of conservative risk management
compare_risk_strategies(Decimal("10000"), 12)  # Example: $10,000 starting balance, 1 year simulation
```

---

## What You've Learned

✅ **Three Pillars**: Position sizing, stop losses, and portfolio management

✅ **Key Metrics**: Risk per trade, win rate, risk/reward, drawdown, and Sharpe ratio

✅ **1% Rule**: The foundation of capital preservation

✅ **Risk Psychology**: Professional mindset vs emotional trading

✅ **Foundation Building**: Personal risk parameters and tracking systems

!!! success "🎉 Foundation Complete!"
    You now understand the fundamental principles that separate professional traders from gamblers. These concepts will guide every trading decision you make. Next, learn to calculate optimal position sizes.

---

## Next Steps

Continue to [Position Sizing Strategies](position-sizing.md) to learn how to calculate optimal position sizes for your trades.

---

## Related Resources

- **[Basic Trading Tutorial](../basic-trading/index.md)** - Foundation trading skills
- **[Position Management](../basic-trading/lesson-5-position-management.md)** - Individual position management
- **[Portfolio Analysis](../portfolio-analysis/index.md)** - Advanced risk analysis
- **[Performance Attribution](../portfolio-analysis/performance-attribution.md)** - Measuring risk-adjusted returns