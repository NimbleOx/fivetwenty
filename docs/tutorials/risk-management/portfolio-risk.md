# Portfolio Risk Management

!!! tip "🎯 Learning Goal"
    Learn to monitor and control risk across multiple positions and instruments to protect your entire trading capital.

---

## Why Portfolio Risk Management Matters

Managing individual trades is only half the battle. Portfolio-level risk management:

- **Prevents catastrophic loss** from correlated positions
- **Controls overall exposure** across all instruments
- **Identifies concentration risk** before it becomes dangerous
- **Manages correlation** between different currency pairs
- **Ensures diversification** across strategies and timeframes

!!! warning "⚠️ Hidden Correlations"
    Many currency pairs are highly correlated. Having 1% risk on EUR/USD and 1% risk on GBP/USD might actually represent 1.8% risk due to correlation.

---

## Risk Monitoring Dashboard

Build a comprehensive system to track portfolio-wide risk in real-time.

### Implementation

```python
from decimal import Decimal

from fivetwenty import AsyncClient, Environment

class RiskMonitor:
    """Comprehensive portfolio risk monitoring system."""

    def __init__(self, client: AsyncClient, account_id: str):
        self.client = client
        self.account_id = account_id

        # Risk limits
        self.max_portfolio_risk = 0.10      # 10% max portfolio risk
        self.max_single_instrument = 0.05   # 5% max per instrument
        self.max_correlation_risk = 0.15    # 15% max correlated risk
        self.max_daily_loss = Decimal("0.05")          # 5% max daily loss

    async def calculate_portfolio_risk(self) -> dict:
        """Calculate comprehensive portfolio risk metrics."""

        try:
            # Get account info
            account = await self.client.accounts.get(self.account_id)
            account_balance = float(account.balance)

            # Get open positions
            positions = await self.client.positions.list_open(self.account_id)

            risk_summary = {
                'account_balance': account_balance,
                'total_exposure': 0,
                'total_unrealized_pl': 0,
                'instrument_risks': {},
                'correlation_groups': {},
                'risk_percentage': 0,
                'within_limits': True,
                'warnings': []
            }

            total_risk = 0

            for position in positions:
                instrument = position.instrument

                # Calculate position risk
                long_units = int(position.long.units) if position.long.units != "0" else 0
                short_units = int(position.short.units) if position.short.units != "0" else 0

                long_pl = float(position.long.unrealized_pl) if position.long.unrealized_pl else 0
                short_pl = float(position.short.unrealized_pl) if position.short.unrealized_pl else 0

                total_unrealized_pl = long_pl + short_pl
                net_units = long_units + short_units

                # Estimate risk (simplified - based on current unrealized P/L)
                position_risk = abs(total_unrealized_pl) if total_unrealized_pl < 0 else 0
                risk_percentage = (position_risk / account_balance) * 100

                risk_summary['instrument_risks'][instrument] = {
                    'net_units': net_units,
                    'unrealized_pl': total_unrealized_pl,
                    'risk_amount': position_risk,
                    'risk_percentage': risk_percentage
                }

                total_risk += position_risk
                risk_summary['total_unrealized_pl'] += total_unrealized_pl
                risk_summary['total_exposure'] += abs(net_units)

            # Calculate total portfolio risk
            risk_summary['risk_percentage'] = (total_risk / account_balance) * 100

            # Check limits
            if risk_summary['risk_percentage'] > self.max_portfolio_risk * 100:
                risk_summary['within_limits'] = False
                risk_summary['warnings'].append(
                    f"Portfolio risk ({risk_summary['risk_percentage']:.1f}%) exceeds limit"
                )

            # Check individual instrument limits
            for instrument, risk_data in risk_summary['instrument_risks'].items():
                if risk_data['risk_percentage'] > self.max_single_instrument * 100:
                    risk_summary['warnings'].append(
                        f"{instrument} risk ({risk_data['risk_percentage']:.1f}%) exceeds instrument limit"
                    )

            return risk_summary

        except Exception as e:
            print(f"❌ Risk calculation error: {e}")
            return {'error': str(e)}

    async def check_correlation_risk(self) -> dict:
        """Check for excessive correlation risk."""

        # Simplified correlation groups (in practice, use historical correlation data)
        correlation_groups = {
            'EUR_BASKET': ['EUR_USD', 'EUR_GBP', 'EUR_JPY', 'EUR_CHF'],
            'USD_BASKET': ['EUR_USD', 'GBP_USD', 'USD_JPY', 'USD_CHF'],
            'COMMODITY_CURRENCIES': ['AUD_USD', 'NZD_USD', 'USD_CAD'],
            'SAFE_HAVENS': ['USD_JPY', 'USD_CHF', 'XAU_USD']
        }

        try:
            positions = await self.client.positions.list_open(self.account_id)
            account = await self.client.accounts.get(self.account_id)
            account_balance = float(account.balance)

            correlation_risks = {}

            for group_name, instruments in correlation_groups.items():
                group_risk = 0
                group_exposure = 0

                for position in positions:
                    if position.instrument in instruments:
                        # Calculate position exposure
                        long_units = int(position.long.units) if position.long.units != "0" else 0
                        short_units = int(position.short.units) if position.short.units != "0" else 0
                        net_units = long_units + short_units

                        # Estimate position value (simplified)
                        group_exposure += abs(net_units)

                        # Add unrealized loss as risk
                        unrealized_pl = float(position.long.unrealized_pl or 0) + float(position.short.unrealized_pl or 0)
                        if unrealized_pl < 0:
                            group_risk += abs(unrealized_pl)

                if group_risk > 0:
                    risk_percentage = (group_risk / account_balance) * 100
                    correlation_risks[group_name] = {
                        'risk_amount': group_risk,
                        'risk_percentage': risk_percentage,
                        'exposure': group_exposure,
                        'instruments': [pos.instrument for pos in positions if pos.instrument in instruments]
                    }

            return correlation_risks

        except Exception as e:
            print(f"❌ Correlation risk error: {e}")
            return {}

    async def generate_risk_report(self) -> None:
        """Generate comprehensive risk report."""

        print("🏦 PORTFOLIO RISK REPORT")
        print("=" * 50)

        # Portfolio risk
        portfolio_risk = await self.calculate_portfolio_risk()

        if 'error' in portfolio_risk:
            print(f"❌ Error generating report: {portfolio_risk['error']}")
            return

        print(f"\n💰 Account Overview:")
        print(f"   Balance: ${portfolio_risk['account_balance']:,.2f}")
        print(f"   Total Unrealized P/L: ${portfolio_risk['total_unrealized_pl']:+,.2f}")
        print(f"   Portfolio Risk: {portfolio_risk['risk_percentage']:.2f}%")
        print(f"   Risk Status: {'✅ OK' if portfolio_risk['within_limits'] else '🚨 EXCEEDED'}")

        # Individual instrument risks
        if portfolio_risk['instrument_risks']:
            print(f"\n📊 Instrument Risk Breakdown:")
            for instrument, risk_data in portfolio_risk['instrument_risks'].items():
                status = "🟫" if risk_data['unrealized_pl'] >= 0 else "🔴"
                print(f"   {instrument}: {risk_data['net_units']:+,} units, "
                      f"P/L: ${risk_data['unrealized_pl']:+.2f}, "
                      f"Risk: {risk_data['risk_percentage']:.2f}% {status}")

        # Correlation risks
        correlation_risks = await self.check_correlation_risk()
        if correlation_risks:
            print(f"\n🔗 Correlation Risk Analysis:")
            for group, risk_data in correlation_risks.items():
                print(f"   {group}: {risk_data['risk_percentage']:.2f}% risk")
                print(f"     Instruments: {', '.join(risk_data['instruments'])}")

        # Risk warnings
        if portfolio_risk['warnings']:
            print(f"\n⚠️ Risk Warnings:")
            for warning in portfolio_risk['warnings']:
                print(f"   - {warning}")

        # Risk limits summary
        print(f"\n📋 Risk Limits:")
        print(f"   Max Portfolio Risk: {self.max_portfolio_risk * 100:.1f}%")
        print(f"   Max Per Instrument: {self.max_single_instrument * 100:.1f}%")
        print(f"   Max Correlation Risk: {self.max_correlation_risk * 100:.1f}%")
        print(f"   Max Daily Loss: {self.max_daily_loss * 100:.1f}%")

# Demo risk monitoring
async def demo_risk_monitoring(account_id: str):
    """Demonstrate risk monitoring system."""

    if not account_id:
        return

    async with AsyncClient(token=TOKEN, environment=ENVIRONMENT) as client:
        monitor = RiskMonitor(client, account_id)

        # Generate risk report
        await monitor.generate_risk_report()

        return monitor
```

---

## Currency Correlation Analysis

Understand how different currency pairs move together to avoid overexposure.

### Correlation Matrix Implementation

```python
from fivetwenty import AsyncClient
import numpy as np
from datetime import datetime, timedelta
from fivetwenty.models import CandlestickGranularity

class CorrelationAnalyzer:
    """Analyze correlations between currency pairs."""
    
    def __init__(self, client: AsyncClient):
        self.client = client
        self.correlation_cache = {}
    
    async def calculate_correlation_matrix(self, instruments: list, 
                                         days_back: int = 30) -> dict:
        """Calculate correlation matrix for given instruments."""
        
        try:
            # Get price data for all instruments
            price_data = {}
            
            end_time = datetime.utcnow()
            start_time = end_time - timedelta(days=days_back)
            
            for instrument in instruments:
                candles = await self.client.instruments.candles(
                    instrument=instrument,
                    granularity=CandlestickGranularity.H4,
                    from_time=start_time.strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
                    to_time=end_time.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
                )
                
                if candles.candles:
                    # Calculate returns (price changes)
                    closes = [float(c.mid.c) for c in candles.candles if c.mid]
                    returns = []
                    
                    for i in range(1, len(closes)):
                        ret = (closes[i] - closes[i-1]) / closes[i-1]
                        returns.append(ret)
                    
                    price_data[instrument] = returns
            
            # Calculate correlation matrix
            correlation_matrix = {}
            
            for i, inst1 in enumerate(instruments):
                correlation_matrix[inst1] = {}
                
                for j, inst2 in enumerate(instruments):
                    if inst1 in price_data and inst2 in price_data:
                        # Ensure both series have same length
                        min_length = min(len(price_data[inst1]), len(price_data[inst2]))
                        
                        if min_length > 10:  # Need sufficient data
                            returns1 = price_data[inst1][:min_length]
                            returns2 = price_data[inst2][:min_length]
                            
                            correlation = np.corrcoef(returns1, returns2)[0, 1]
                            correlation_matrix[inst1][inst2] = correlation
                        else:
                            correlation_matrix[inst1][inst2] = 0.0
                    else:
                        correlation_matrix[inst1][inst2] = 0.0
            
            print(f"🔗 Correlation Matrix ({days_back} days):")
            print("=" * 60)
            
            # Print header
            print(f"{'Instrument':<12}", end="")
            for inst in instruments:
                print(f"{inst[:7]:<8}", end="")
            print()
            
            # Print correlation matrix
            for inst1 in instruments:
                print(f"{inst1:<12}", end="")
                for inst2 in instruments:
                    corr = correlation_matrix[inst1][inst2]
                    print(f"{corr:+.2f}   ", end="")
                print()
            
            return correlation_matrix
            
        except Exception as e:
            print(f"❌ Correlation calculation error: {e}")
            return {}
    
    def identify_high_correlations(self, correlation_matrix: dict, 
                                 threshold: float = 0.7) -> list:
        """Identify highly correlated pairs."""
        
        high_correlations = []
        
        instruments = list(correlation_matrix.keys())
        
        for i, inst1 in enumerate(instruments):
            for j, inst2 in enumerate(instruments[i+1:], i+1):
                if inst1 in correlation_matrix and inst2 in correlation_matrix[inst1]:
                    corr = correlation_matrix[inst1][inst2]
                    
                    if abs(corr) >= threshold:
                        high_correlations.append({
                            'pair': (inst1, inst2),
                            'correlation': corr,
                            'type': 'positive' if corr > 0 else 'negative'
                        })
        
        # Sort by absolute correlation
        high_correlations.sort(key=lambda x: abs(x['correlation']), reverse=True)
        
        print(f"\n🔍 High Correlations (|r| >= {threshold}):")
        for item in high_correlations:
            inst1, inst2 = item['pair']
            corr = item['correlation']
            print(f"   {inst1} vs {inst2}: {corr:+.3f} ({item['type']})")
        
        return high_correlations
    
    def calculate_effective_risk(self, positions: dict, 
                               correlation_matrix: dict) -> float:
        """Calculate effective portfolio risk considering correlations."""
        
        # Simplified effective risk calculation
        # In practice, you'd use more sophisticated portfolio risk models
        
        instruments = list(positions.keys())
        total_risk = 0
        
        for i, inst1 in enumerate(instruments):
            for j, inst2 in enumerate(instruments):
                if inst1 in correlation_matrix and inst2 in correlation_matrix[inst1]:
                    risk1 = positions[inst1]['risk_amount']
                    risk2 = positions[inst2]['risk_amount']
                    correlation = correlation_matrix[inst1][inst2]
                    
                    # Portfolio risk formula component
                    risk_contribution = risk1 * risk2 * correlation
                    total_risk += risk_contribution
        
        effective_risk = np.sqrt(max(0, total_risk))
        
        print(f"\n📊 Effective Risk Calculation:")
        print(f"   Sum of Individual Risks: ${sum(pos['risk_amount'] for pos in positions.values()):.2f}")
        print(f"   Effective Portfolio Risk: ${effective_risk:.2f}")
        
        return effective_risk

# Example correlation analysis
async def demo_correlation_analysis(account_id: str):
    """Demonstrate correlation analysis."""
    
    if not account_id:
        return
    
    async with AsyncClient(token=TOKEN, environment=ENVIRONMENT) as client:
        analyzer = CorrelationAnalyzer(client)
        
        # Major currency pairs to analyze
        major_pairs = ['EUR_USD', 'GBP_USD', 'USD_JPY', 'USD_CHF', 'AUD_USD', 'USD_CAD']
        
        # Calculate correlation matrix
        correlation_matrix = await analyzer.calculate_correlation_matrix(major_pairs, days_back=30)
        
        if correlation_matrix:
            # Identify high correlations
            high_corrs = analyzer.identify_high_correlations(correlation_matrix, threshold=0.6)
            
            return {
                'correlation_matrix': correlation_matrix,
                'high_correlations': high_corrs
            }
        
        return None
```

### Understanding Correlation Impact

| Correlation | Relationship | Portfolio Impact |
|-------------|--------------|------------------|
| +0.8 to +1.0 | Extremely Strong Positive | Positions move together - increases risk |
| +0.5 to +0.8 | Strong Positive | Significant co-movement |
| +0.2 to +0.5 | Moderate Positive | Some co-movement |
| -0.2 to +0.2 | Weak/No Correlation | Independent movement |
| -0.5 to -0.2 | Moderate Negative | Opposite movement |
| -0.8 to -0.5 | Strong Negative | Strong opposite movement |
| -1.0 to -0.8 | Extremely Strong Negative | Perfect hedge potential |

---

## Portfolio Diversification Strategies

Spread risk across different instruments, timeframes, and strategies.

### Diversification Implementation

```python
class PortfolioDiversifier:
    """Manage portfolio diversification across multiple dimensions."""
    
    def __init__(self, max_positions: int = 10):
        self.max_positions = max_positions
        self.diversification_rules = {
            'max_currency_exposure': 0.30,  # 30% max in any single currency
            'max_correlation_group': 0.25,  # 25% max in correlated group
            'max_strategy_allocation': 0.40, # 40% max in any single strategy
            'min_instruments': 3            # Minimum 3 different instruments
        }
    
    def analyze_currency_exposure(self, positions: dict) -> dict:
        """Analyze exposure to individual currencies."""
        
        currency_exposure = {}
        total_risk = sum(pos['risk_amount'] for pos in positions.values())
        
        for instrument, position in positions.items():
            # Extract currencies from instrument (e.g., EUR_USD -> EUR, USD)
            currencies = instrument.split('_')
            
            for currency in currencies:
                if currency not in currency_exposure:
                    currency_exposure[currency] = 0
                
                # Add risk amount (simplified - actual calculation more complex)
                currency_exposure[currency] += position['risk_amount'] / 2  # Split between base/quote
        
        # Calculate percentages
        currency_percentages = {}
        for currency, exposure in currency_exposure.items():
            percentage = (exposure / total_risk) * 100 if total_risk > 0 else 0
            currency_percentages[currency] = {
                'exposure_amount': exposure,
                'percentage': percentage,
                'within_limit': percentage <= self.diversification_rules['max_currency_exposure'] * 100
            }
        
        print(f"🌍 Currency Exposure Analysis:")
        for currency, data in currency_percentages.items():
            status = "✅" if data['within_limit'] else "❌"
            print(f"   {currency}: {data['percentage']:.1f}% ({status})")
        
        return currency_percentages
    
    def check_diversification_rules(self, positions: dict, 
                                  correlation_data: dict = None) -> dict:
        """Check all diversification rules."""
        
        violations = []
        recommendations = []
        
        # Check number of instruments
        num_instruments = len(positions)
        if num_instruments < self.diversification_rules['min_instruments']:
            violations.append(f"Only {num_instruments} instruments (min: {self.diversification_rules['min_instruments']})")
            recommendations.append("Add more instruments to improve diversification")
        
        # Check currency exposure
        currency_exposure = self.analyze_currency_exposure(positions)
        for currency, data in currency_exposure.items():
            if not data['within_limit']:
                violations.append(f"{currency} exposure ({data['percentage']:.1f}%) exceeds limit")
                recommendations.append(f"Reduce {currency} exposure or hedge positions")
        
        # Check correlation groups (if data available)
        if correlation_data:
            for group_name, group_data in correlation_data.items():
                if group_data['risk_percentage'] > self.diversification_rules['max_correlation_group'] * 100:
                    violations.append(f"{group_name} correlation risk ({group_data['risk_percentage']:.1f}%) too high")
                    recommendations.append(f"Reduce positions in {group_name} instruments")
        
        result = {
            'compliant': len(violations) == 0,
            'violations': violations,
            'recommendations': recommendations,
            'diversification_score': self._calculate_diversification_score(positions)
        }
        
        print(f"\n📋 Diversification Analysis:")
        print(f"   Compliant: {'✅ Yes' if result['compliant'] else '❌ No'}")
        print(f"   Diversification Score: {result['diversification_score']:.1f}/100")
        
        if violations:
            print(f"   Violations:")
            for violation in violations:
                print(f"     - {violation}")
        
        if recommendations:
            print(f"   Recommendations:")
            for rec in recommendations:
                print(f"     • {rec}")
        
        return result
    
    def _calculate_diversification_score(self, positions: dict) -> float:
        """Calculate overall diversification score (0-100)."""
        
        score = 100.0
        
        # Penalize for too few instruments
        num_instruments = len(positions)
        if num_instruments < 5:
            score -= (5 - num_instruments) * 10
        
        # Penalize for concentration
        total_risk = sum(pos['risk_amount'] for pos in positions.values())
        if total_risk > 0:
            for instrument, position in positions.items():
                concentration = (position['risk_amount'] / total_risk) * 100
                if concentration > 25:  # More than 25% in single instrument
                    score -= (concentration - 25) * 2
        
        return max(0, min(100, score))
    
    def suggest_optimal_allocation(self, available_instruments: list,
                                 total_risk_budget: float) -> dict:
        """Suggest optimal portfolio allocation."""
        
        # Simplified allocation suggestion
        num_positions = min(len(available_instruments), self.max_positions)
        
        if num_positions == 0:
            return {}
        
        # Equal weight allocation with adjustments
        base_allocation = total_risk_budget / num_positions
        
        allocations = {}
        for i, instrument in enumerate(available_instruments[:num_positions]):
            # Adjust based on instrument characteristics
            allocation = base_allocation
            
            # Reduce allocation for highly correlated instruments
            # Increase allocation for diversifying instruments
            # (This would be more sophisticated in practice)
            
            allocations[instrument] = {
                'suggested_risk': allocation,
                'percentage': (allocation / total_risk_budget) * 100,
                'rationale': "Equal weight with diversification adjustments"
            }
        
        print(f"🎯 Suggested Portfolio Allocation:")
        for instrument, data in allocations.items():
            print(f"   {instrument}: ${data['suggested_risk']:.2f} ({data['percentage']:.1f}%)")
        
        return allocations

# Example diversification analysis
def demo_diversification_analysis():
    """Demonstrate diversification analysis."""
    
    # Example current positions
    current_positions = {
        'EUR_USD': {'risk_amount': 200, 'direction': 'long'},
        'GBP_USD': {'risk_amount': 150, 'direction': 'long'},
        'USD_JPY': {'risk_amount': 100, 'direction': 'short'},
        'EUR_GBP': {'risk_amount': 175, 'direction': 'short'}
    }
    
    diversifier = PortfolioDiversifier(max_positions=8)
    
    # Analyze current diversification
    analysis = diversifier.check_diversification_rules(current_positions)
    
    # Suggest improvements
    available_instruments = ['AUD_USD', 'USD_CAD', 'USD_CHF', 'NZD_USD']
    suggestions = diversifier.suggest_optimal_allocation(
        available_instruments, 
        total_risk_budget=1000
    )
    
    return {
        'current_analysis': analysis,
        'suggestions': suggestions
    }
```

---

## Risk Budgeting and Allocation

Systematically allocate risk across different strategies and instruments.

### Risk Budget Implementation

```python
class RiskBudgetManager:
    """Manage risk allocation across different categories."""
    
    def __init__(self, total_risk_budget: float):
        self.total_risk_budget = total_risk_budget
        self.risk_allocations = {
            'trend_following': 0.40,    # 40% to trend strategies
            'mean_reversion': 0.25,     # 25% to mean reversion
            'breakout': 0.20,           # 20% to breakout strategies
            'hedge': 0.15               # 15% to hedging positions
        }
        self.allocated_risk = {category: 0 for category in self.risk_allocations}
    
    def allocate_risk(self, strategy_category: str, risk_amount: float) -> bool:
        """Allocate risk to a strategy category."""
        
        if strategy_category not in self.risk_allocations:
            print(f"❌ Unknown strategy category: {strategy_category}")
            return False
        
        # Check if allocation would exceed budget
        max_allocation = self.total_risk_budget * self.risk_allocations[strategy_category]
        
        if self.allocated_risk[strategy_category] + risk_amount > max_allocation:
            available = max_allocation - self.allocated_risk[strategy_category]
            print(f"⚠️ {strategy_category} budget exceeded. Available: ${available:.2f}")
            return False
        
        # Allocate the risk
        self.allocated_risk[strategy_category] += risk_amount
        
        print(f"✅ Allocated ${risk_amount:.2f} to {strategy_category}")
        print(f"   Used: ${self.allocated_risk[strategy_category]:.2f} / ${max_allocation:.2f}")
        
        return True
    
    def get_risk_utilization(self) -> dict:
        """Get current risk utilization by category."""
        
        utilization = {}
        total_used = 0
        
        for category, allocation_pct in self.risk_allocations.items():
            max_budget = self.total_risk_budget * allocation_pct
            used = self.allocated_risk[category]
            utilization_pct = (used / max_budget) * 100 if max_budget > 0 else 0
            
            utilization[category] = {
                'max_budget': max_budget,
                'used': used,
                'available': max_budget - used,
                'utilization_pct': utilization_pct
            }
            
            total_used += used
        
        print(f"📊 Risk Budget Utilization:")
        print(f"   Total Budget: ${self.total_risk_budget:.2f}")
        print(f"   Total Used: ${total_used:.2f} ({(total_used/self.total_risk_budget)*100:.1f}%)")
        print(f"   Available: ${self.total_risk_budget - total_used:.2f}")
        print()
        
        for category, data in utilization.items():
            print(f"   {category.replace('_', ' ').title()}:")
            print(f"     Budget: ${data['max_budget']:.2f}")
            print(f"     Used: ${data['used']:.2f} ({data['utilization_pct']:.1f}%)")
            print(f"     Available: ${data['available']:.2f}")
        
        return utilization
    
    def rebalance_suggestions(self) -> list:
        """Suggest rebalancing actions."""
        
        suggestions = []
        utilization = self.get_risk_utilization()
        
        # Find over/under utilized categories
        for category, data in utilization.items():
            if data['utilization_pct'] > 90:
                suggestions.append(f"Reduce {category} positions - near budget limit")
            elif data['utilization_pct'] < 20:
                suggestions.append(f"Consider adding {category} positions - underutilized")
        
        # Check overall utilization
        total_used = sum(data['used'] for data in utilization.values())
        overall_utilization = (total_used / self.total_risk_budget) * 100
        
        if overall_utilization < 50:
            suggestions.append("Overall risk utilization low - consider increasing position sizes")
        elif overall_utilization > 85:
            suggestions.append("High risk utilization - be cautious about new positions")
        
        if suggestions:
            print(f"\n📝 Rebalancing Suggestions:")
            for suggestion in suggestions:
                print(f"   • {suggestion}")
        
        return suggestions

# Example risk budgeting
def demo_risk_budgeting():
    """Demonstrate risk budgeting system."""
    
    # Create risk budget manager with $1000 total budget
    risk_manager = RiskBudgetManager(total_risk_budget=1000)
    
    # Simulate some risk allocations
    allocations = [
        ('trend_following', 150),
        ('trend_following', 100),
        ('mean_reversion', 80),
        ('breakout', 120),
        ('hedge', 60)
    ]
    
    for category, amount in allocations:
        risk_manager.allocate_risk(category, amount)
    
    # Check utilization
    utilization = risk_manager.get_risk_utilization()
    
    # Get rebalancing suggestions
    suggestions = risk_manager.rebalance_suggestions()
    
    return {
        'utilization': utilization,
        'suggestions': suggestions
    }
```

---

## ✅ Skill Checkpoint: Portfolio Risk Management

Test your understanding of portfolio-level risk management:

!!! question "🧠 Test Your Understanding"
    1. **Why might 1% risk on EUR/USD and 1% risk on GBP/USD not equal 2% total risk?**
       <details>
       <summary>Click to reveal answer</summary>
       **Due to correlation between the pairs**. EUR/USD and GBP/USD are often positively correlated (both involve USD and European currencies), so they may move together. The effective risk might be closer to 1.7-1.8% rather than 2%.
       </details>

    2. **What's the maximum percentage of your portfolio you should allocate to correlated instruments?**
       <details>
       <summary>Click to reveal answer</summary>
       **Generally 15-25% maximum to highly correlated instruments**. This prevents your entire portfolio from moving in the same direction due to a single market event affecting all correlated positions.
       </details>

    3. **How does currency exposure differ from instrument exposure?**
       <details>
       <summary>Click to reveal answer</summary>
       **Currency exposure considers your total exposure to individual currencies across all pairs**. For example, trading EUR/USD long and EUR/GBP short gives you net EUR exposure, even though they're different instruments.
       </details>

---

## Portfolio Risk Best Practices

### Daily Risk Management Routine

1. **Morning Risk Check**
   - Review overnight position changes
   - Check correlation exposure
   - Verify risk limits compliance
   - Plan day's trading within budget

2. **Mid-Day Reassessment**
   - Update unrealized P/L
   - Check for correlation changes
   - Adjust position sizes if needed
   - Monitor market stress indicators

3. **End-of-Day Review**
   - Calculate daily risk metrics
   - Document any limit breaches
   - Plan next day's risk budget
   - Update correlation analysis

### Risk Limit Framework

```python
class RiskLimitFramework:
    """Comprehensive risk limit management system."""
    
    def __init__(self, account_balance: float):
        self.account_balance = account_balance
        
        # Multi-level risk limits
        self.limits = {
            'per_trade': {
                'max_risk_pct': 1.0,        # 1% max per trade
                'alert_threshold': 0.8      # Alert at 0.8%
            },
            'daily': {
                'max_loss_pct': 3.0,        # 3% max daily loss
                'alert_threshold': 2.0      # Alert at 2%
            },
            'portfolio': {
                'max_risk_pct': 15.0,       # 15% max portfolio risk
                'alert_threshold': 12.0     # Alert at 12%
            },
            'correlation': {
                'max_group_pct': 25.0,      # 25% max correlated group
                'alert_threshold': 20.0     # Alert at 20%
            },
            'currency': {
                'max_exposure_pct': 40.0,   # 40% max single currency
                'alert_threshold': 30.0     # Alert at 30%
            }
        }
    
    def check_all_limits(self, current_positions: dict) -> dict:
        """Check all risk limits and return status."""
        
        results = {
            'overall_status': 'OK',
            'violations': [],
            'warnings': [],
            'limit_checks': {}
        }
        
        # This would integrate with actual position data
        # Simplified example showing the framework
        
        for limit_type, limits in self.limits.items():
            # Calculate current value for this limit type
            current_value = self._calculate_current_value(limit_type, current_positions)
            
            status = 'OK'
            if current_value > limits['max_risk_pct']:
                status = 'VIOLATION'
                results['violations'].append(f"{limit_type} limit exceeded: {current_value:.1f}%")
                results['overall_status'] = 'VIOLATION'
            elif current_value > limits['alert_threshold']:
                status = 'WARNING'
                results['warnings'].append(f"{limit_type} approaching limit: {current_value:.1f}%")
                if results['overall_status'] == 'OK':
                    results['overall_status'] = 'WARNING'
            
            results['limit_checks'][limit_type] = {
                'current': current_value,
                'limit': limits['max_risk_pct'],
                'threshold': limits['alert_threshold'],
                'status': status
            }
        
        return results
    
    def _calculate_current_value(self, limit_type: str, positions: dict) -> float:
        """Calculate current value for specific limit type."""
        # Simplified calculation - would be more complex in practice
        if limit_type == 'portfolio':
            total_risk = sum(pos.get('risk_amount', 0) for pos in positions.values())
            return (total_risk / self.account_balance) * 100
        
        # Add other limit type calculations
        return 0.0
```

---

## What You've Learned

✅ **Risk Monitoring**: Real-time portfolio risk tracking and reporting

✅ **Correlation Analysis**: Understanding and managing currency correlations

✅ **Diversification**: Spreading risk across instruments, currencies, and strategies

✅ **Risk Budgeting**: Systematic allocation of risk across different categories

✅ **Limit Framework**: Multi-level risk controls with alerts and violations

!!! success "🎉 Portfolio Risk Management Complete!"
    You now have the tools to manage risk across your entire portfolio, not just individual trades. These techniques will help you avoid the correlation traps that catch many traders and ensure your portfolio is properly diversified. Next, learn about automated risk controls.

---

## Next Steps

Continue to [Automated Risk Controls](automated-controls.md) to learn how to build systems that automatically enforce your risk management rules.

---

## Related Resources

- **[Risk Management Fundamentals](fundamentals.md)** - Core risk management principles
- **[Position Sizing Strategies](position-sizing.md)** - Calculate optimal position sizes
- **[Portfolio Analysis](../portfolio-analysis/index.md)** - Advanced portfolio analysis techniques
- **[Performance Attribution](../portfolio-analysis/performance-attribution.md)** - Analyze portfolio performance sources