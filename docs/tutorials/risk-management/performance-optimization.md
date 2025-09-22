# Performance Optimization

!!! tip "🎯 Learning Goal"
    Master advanced techniques for optimizing risk-adjusted returns, including Kelly Criterion, performance attribution, and sophisticated metrics.

---

## Beyond Basic Risk Management

Once you have solid risk controls in place, the next step is optimization:

- **Maximize risk-adjusted returns** rather than just returns
- **Optimize position sizing** using mathematical models
- **Measure performance** with sophisticated metrics
- **Attribute returns** to different risk factors
- **Optimize portfolio allocation** across strategies

!!! quote "💡 Professional Insight"
    "It's not about making the most money - it's about making the most money per unit of risk taken. Risk-adjusted returns separate professionals from gamblers."

---

## Kelly Criterion for Optimal Sizing

The mathematically optimal approach to position sizing based on your edge.

### Kelly Formula Implementation

```python
from decimal import Decimal

class KellyOptimizer:
    """Implement Kelly Criterion for optimal position sizing."""
    
    def __init__(self, win_rate: float, avg_win: float, avg_loss: float):
        self.win_rate = win_rate / 100 if win_rate > 1 else win_rate  # Handle percentage input
        self.lose_rate = 1 - self.win_rate
        self.avg_win = avg_win
        self.avg_loss = abs(avg_loss)  # Ensure positive
        
        # Safety parameters
        self.max_kelly_fraction = 0.25  # Never bet more than 25% even if Kelly suggests it
        self.min_trades_for_kelly = 30  # Need sufficient history
    
    def calculate_kelly_fraction(self) -> dict:
        """Calculate optimal Kelly fraction."""
        
        if self.avg_loss == 0:
            return {'kelly_fraction': 0, 'error': 'Average loss cannot be zero'}
        
        # Kelly formula: f = (bp - q) / b
        # where:
        # b = odds received on a win (avg_win / avg_loss)
        # p = probability of winning (win_rate)
        # q = probability of losing (1 - win_rate)
        
        b = self.avg_win / self.avg_loss  # Odds ratio
        p = self.win_rate
        q = self.lose_rate
        
        # Calculate Kelly fraction
        kelly_fraction = (b * p - q) / b
        
        # Apply safety caps
        capped_kelly = max(0, min(kelly_fraction, self.max_kelly_fraction))
        
        result = {
            'raw_kelly_fraction': kelly_fraction,
            'capped_kelly_fraction': capped_kelly,
            'kelly_percentage': capped_kelly * 100,
            'win_rate': self.win_rate,
            'avg_win': self.avg_win,
            'avg_loss': self.avg_loss,
            'odds_ratio': b,
            'expectancy': (self.win_rate * self.avg_win) - (self.lose_rate * self.avg_loss)
        }
        
        print(f"📊 Kelly Criterion Analysis:")
        print(f"   Win Rate: {self.win_rate:.1%}")
        print(f"   Average Win: ${self.avg_win:.2f}")
        print(f"   Average Loss: ${self.avg_loss:.2f}")
        print(f"   Odds Ratio: {b:.2f}")
        print(f"   Expectancy: ${result['expectancy']:+.2f}")
        print(f"   Raw Kelly: {kelly_fraction:.1%}")
        print(f"   Capped Kelly: {capped_kelly:.1%}")
        
        # Interpretation
        if kelly_fraction <= 0:
            print(f"   ⚠️ Negative edge - Kelly suggests no position")
        elif kelly_fraction > 0.5:
            print(f"   ⚠️ Very high Kelly fraction - high confidence but risky")
        else:
            print(f"   ✅ Positive edge with reasonable Kelly fraction")
        
        return result
    
    def calculate_fractional_kelly(self, fraction: float = 0.25) -> dict:
        """Calculate fractional Kelly (typically 25% of full Kelly)."""
        
        kelly_result = self.calculate_kelly_fraction()
        
        if kelly_result['capped_kelly_fraction'] <= 0:
            return kelly_result
        
        fractional_kelly = kelly_result['capped_kelly_fraction'] * fraction
        
        kelly_result.update({
            'fractional_kelly': fractional_kelly,
            'fractional_percentage': fractional_kelly * 100,
            'fraction_used': fraction,
            'recommended_use': fractional_kelly
        })
        
        print(f"\n🎯 Fractional Kelly ({fraction:.0%} of full):")
        print(f"   Recommended Position Size: {fractional_kelly:.1%}")
        
        return kelly_result
    
    def calculate_position_size(self, account_balance: float, 
                              entry_price: float, stop_loss: float,
                              use_fractional: bool = True) -> int:
        """Calculate optimal position size using Kelly."""
        
        kelly_data = self.calculate_fractional_kelly() if use_fractional else self.calculate_kelly_fraction()
        
        if kelly_data.get('recommended_use', 0) <= 0:
            print(f"   ❌ Kelly suggests no position")
            return 0
        
        # Calculate risk per unit
        risk_per_unit = abs(entry_price - stop_loss)
        
        if risk_per_unit == 0:
            print(f"   ❌ No stop loss defined")
            return 0
        
        # Calculate position size
        kelly_fraction = kelly_data.get('recommended_use', 0)
        risk_amount = account_balance * kelly_fraction
        position_size = int(risk_amount / risk_per_unit)
        
        print(f"\n💰 Position Size Calculation:")
        print(f"   Account Balance: ${account_balance:,.2f}")
        print(f"   Kelly Fraction: {kelly_fraction:.1%}")
        print(f"   Risk Amount: ${risk_amount:.2f}")
        print(f"   Risk per Unit: ${risk_per_unit:.5f}")
        print(f"   Position Size: {position_size:,} units")
        
        return position_size
    
    def simulate_kelly_performance(self, trials: int = 1000, 
                                 starting_balance: float = 10000) -> dict:
        """Simulate Kelly performance over many trials."""
        
        import random
        
        kelly_data = self.calculate_fractional_kelly()
        kelly_fraction = kelly_data.get('recommended_use', 0)
        
        if kelly_fraction <= 0:
            return {'error': 'Negative Kelly fraction'}
        
        balances = []
        current_balance = starting_balance
        
        for trial in range(trials):
            # Simulate win/loss
            if random.random() < self.win_rate:
                # Win
                gain = current_balance * kelly_fraction * (self.avg_win / self.avg_loss)
                current_balance += gain
            else:
                # Loss
                loss = current_balance * kelly_fraction
                current_balance -= loss
            
            balances.append(current_balance)
        
        # Calculate metrics
        final_balance = balances[-1]
        total_return = (final_balance - starting_balance) / starting_balance
        max_balance = max(balances)
        min_balance = min(balances)
        max_drawdown = (max_balance - min_balance) / max_balance
        
        result = {
            'starting_balance': starting_balance,
            'final_balance': final_balance,
            'total_return': total_return,
            'total_return_pct': total_return * 100,
            'max_drawdown': max_drawdown,
            'max_drawdown_pct': max_drawdown * 100,
            'trials': trials,
            'kelly_fraction': kelly_fraction
        }
        
        print(f"\n🎢 Kelly Simulation Results ({trials:,} trials):")
        print(f"   Starting Balance: ${starting_balance:,.2f}")
        print(f"   Final Balance: ${final_balance:,.2f}")
        print(f"   Total Return: {total_return:.1%}")
        print(f"   Max Drawdown: {max_drawdown:.1%}")
        
        return result

# Example Kelly optimization
def demo_kelly_optimization():
    """Demonstrate Kelly Criterion optimization."""
    
    # Example trading statistics
    strategies = [
        {'name': 'Conservative Strategy', 'win_rate': 55, 'avg_win': 100, 'avg_loss': 80},
        {'name': 'Aggressive Strategy', 'win_rate': 40, 'avg_win': 200, 'avg_loss': 100},
        {'name': 'Balanced Strategy', 'win_rate': 60, 'avg_win': 120, 'avg_loss': 100}
    ]
    
    results = {}
    
    for strategy in strategies:
        print(f"\n🗺 Analyzing: {strategy['name']}")
        print("=" * 50)
        
        optimizer = KellyOptimizer(strategy['win_rate'], strategy['avg_win'], strategy['avg_loss'])
        
        # Calculate optimal position size
        position_size = optimizer.calculate_position_size(
            account_balance=10000,
            entry_price=Decimal("1.1000"),
            stop_loss=Decimal("1.0950")
        )
        
        # Run simulation
        simulation = optimizer.simulate_kelly_performance(trials=1000)
        
        results[strategy['name']] = {
            'position_size': position_size,
            'simulation': simulation
        }
    
    return results
```

---

## Risk-Adjusted Performance Metrics

Measure performance using sophisticated metrics that account for risk.

### Advanced Metrics Implementation

```python
import numpy as np
from datetime import datetime, timedelta
from fivetwenty import AsyncClient, Environment

class PerformanceAnalyzer:
    """Calculate advanced risk-adjusted performance metrics."""
    
    def __init__(self, client: AsyncClient, account_id: str):
        self.client = client
        self.account_id = account_id
        self.risk_free_rate = 0.02  # 2% annual risk-free rate
    
    async def calculate_comprehensive_metrics(self, days_back: int = 90) -> dict:
        """Calculate comprehensive performance metrics."""
        
        try:
            # Get transaction history
            end_time = datetime.utcnow()
            start_time = end_time - timedelta(days=days_back)
            
            transactions = await self.client.transactions.list(
                account_id=self.account_id,
                from_time=start_time.strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
                to_time=end_time.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
            )
            
            # Extract trade results and account values
            trade_results = []
            account_values = []
            
            for transaction in transactions.transactions:
                if hasattr(transaction, 'pl') and transaction.pl:
                    trade_results.append(float(transaction.pl))
                
                if hasattr(transaction, 'account_balance'):
                    account_values.append(float(transaction.account_balance))
            
            if not trade_results:
                return {'error': 'No trade data available'}
            
            # Calculate basic metrics
            basic_metrics = self._calculate_basic_metrics(trade_results)
            
            # Calculate risk metrics
            risk_metrics = self._calculate_risk_metrics(trade_results, account_values)
            
            # Calculate advanced metrics
            advanced_metrics = self._calculate_advanced_metrics(trade_results, account_values)
            
            # Combine all metrics
            all_metrics = {
                **basic_metrics,
                **risk_metrics,
                **advanced_metrics,
                'analysis_period_days': days_back,
                'total_trades': len(trade_results)
            }
            
            # Print comprehensive report
            self._print_performance_report(all_metrics)
            
            return all_metrics
            
        except Exception as e:
            return {'error': str(e)}
    
    def _calculate_basic_metrics(self, trade_results: list) -> dict:
        """Calculate basic performance metrics."""
        
        total_trades = len(trade_results)
        winning_trades = len([r for r in trade_results if r > 0])
        losing_trades = len([r for r in trade_results if r < 0])
        
        total_profit = sum(r for r in trade_results if r > 0)
        total_loss = sum(r for r in trade_results if r < 0)
        net_profit = sum(trade_results)
        
        win_rate = (winning_trades / total_trades) * 100 if total_trades > 0 else 0
        avg_win = total_profit / winning_trades if winning_trades > 0 else 0
        avg_loss = total_loss / losing_trades if losing_trades > 0 else 0
        
        profit_factor = abs(total_profit / total_loss) if total_loss != 0 else float('inf')
        expectancy = (win_rate / 100 * avg_win) + ((100 - win_rate) / 100 * avg_loss)
        
        return {
            'total_trades': total_trades,
            'winning_trades': winning_trades,
            'losing_trades': losing_trades,
            'win_rate': win_rate,
            'total_profit': total_profit,
            'total_loss': total_loss,
            'net_profit': net_profit,
            'avg_win': avg_win,
            'avg_loss': avg_loss,
            'profit_factor': profit_factor,
            'expectancy': expectancy
        }
    
    def _calculate_risk_metrics(self, trade_results: list, account_values: list) -> dict:
        """Calculate risk-adjusted metrics."""
        
        if len(trade_results) < 2:
            return {}
        
        # Calculate returns
        returns = np.array(trade_results)
        
        # Sharpe Ratio
        mean_return = np.mean(returns)
        std_return = np.std(returns)
        
        # Annualize (assuming daily trading)
        annual_return = mean_return * 252  # Trading days per year
        annual_volatility = std_return * np.sqrt(252)
        
        sharpe_ratio = (annual_return - self.risk_free_rate) / annual_volatility if annual_volatility > 0 else 0
        
        # Sortino Ratio (downside deviation)
        downside_returns = returns[returns < 0]
        downside_deviation = np.std(downside_returns) * np.sqrt(252) if len(downside_returns) > 0 else 0
        sortino_ratio = (annual_return - self.risk_free_rate) / downside_deviation if downside_deviation > 0 else 0
        
        # Maximum Drawdown
        if account_values:
            cumulative_values = np.array(account_values)
            peak = np.maximum.accumulate(cumulative_values)
            drawdown = (cumulative_values - peak) / peak
            max_drawdown = abs(drawdown.min()) * 100
        else:
            # Estimate from trade results
            cumulative_pl = np.cumsum(returns)
            peak = np.maximum.accumulate(cumulative_pl)
            drawdown = cumulative_pl - peak
            max_drawdown = abs(drawdown.min())
        
        # Calmar Ratio
        calmar_ratio = annual_return / (max_drawdown / 100) if max_drawdown > 0 else 0
        
        return {
            'sharpe_ratio': sharpe_ratio,
            'sortino_ratio': sortino_ratio,
            'max_drawdown': max_drawdown,
            'calmar_ratio': calmar_ratio,
            'annual_return': annual_return,
            'annual_volatility': annual_volatility,
            'downside_deviation': downside_deviation
        }
    
    def _calculate_advanced_metrics(self, trade_results: list, account_values: list) -> dict:
        """Calculate advanced performance metrics."""
        
        returns = np.array(trade_results)
        
        # Value at Risk (VaR) - 95% confidence
        var_95 = np.percentile(returns, 5)
        
        # Conditional Value at Risk (CVaR)
        cvar_95 = np.mean(returns[returns <= var_95])
        
        # Skewness and Kurtosis
        skewness = self._calculate_skewness(returns)
        kurtosis = self._calculate_kurtosis(returns)
        
        # Longest winning/losing streaks
        win_streak, loss_streak = self._calculate_streaks(trade_results)
        
        # R-squared (consistency)
        r_squared = self._calculate_r_squared(trade_results)
        
        return {
            'var_95': var_95,
            'cvar_95': cvar_95,
            'skewness': skewness,
            'kurtosis': kurtosis,
            'longest_win_streak': win_streak,
            'longest_loss_streak': loss_streak,
            'r_squared': r_squared
        }
    
    def _calculate_skewness(self, returns: np.ndarray) -> float:
        """Calculate skewness of returns."""
        mean_return = np.mean(returns)
        std_return = np.std(returns)
        
        if std_return == 0:
            return 0
        
        skewness = np.mean(((returns - mean_return) / std_return) ** 3)
        return skewness
    
    def _calculate_kurtosis(self, returns: np.ndarray) -> float:
        """Calculate kurtosis of returns."""
        mean_return = np.mean(returns)
        std_return = np.std(returns)
        
        if std_return == 0:
            return 0
        
        kurtosis = np.mean(((returns - mean_return) / std_return) ** 4) - 3
        return kurtosis
    
    def _calculate_streaks(self, trade_results: list) -> tuple:
        """Calculate longest winning and losing streaks."""
        
        current_win_streak = 0
        current_loss_streak = 0
        max_win_streak = 0
        max_loss_streak = 0
        
        for result in trade_results:
            if result > 0:
                current_win_streak += 1
                current_loss_streak = 0
                max_win_streak = max(max_win_streak, current_win_streak)
            elif result < 0:
                current_loss_streak += 1
                current_win_streak = 0
                max_loss_streak = max(max_loss_streak, current_loss_streak)
        
        return max_win_streak, max_loss_streak
    
    def _calculate_r_squared(self, trade_results: list) -> float:
        """Calculate R-squared (measure of consistency)."""
        
        if len(trade_results) < 2:
            return 0
        
        x = np.arange(len(trade_results))
        y = np.cumsum(trade_results)
        
        # Linear regression
        correlation_matrix = np.corrcoef(x, y)
        correlation = correlation_matrix[0, 1]
        r_squared = correlation ** 2
        
        return r_squared
    
    def _print_performance_report(self, metrics: dict):
        """Print comprehensive performance report."""
        
        print(f"\n📊 COMPREHENSIVE PERFORMANCE ANALYSIS")
        print("=" * 60)
        
        # Basic Performance
        print(f"\n💹 Basic Performance ({metrics['analysis_period_days']} days):")
        print(f"   Total Trades: {metrics['total_trades']}")
        print(f"   Win Rate: {metrics['win_rate']:.1f}%")
        print(f"   Net Profit: ${metrics['net_profit']:+.2f}")
        print(f"   Profit Factor: {metrics['profit_factor']:.2f}")
        print(f"   Expectancy: ${metrics['expectancy']:+.2f}")
        
        # Risk Metrics
        if 'sharpe_ratio' in metrics:
            print(f"\n🔒 Risk-Adjusted Metrics:")
            print(f"   Sharpe Ratio: {metrics['sharpe_ratio']:.2f}")
            print(f"   Sortino Ratio: {metrics['sortino_ratio']:.2f}")
            print(f"   Calmar Ratio: {metrics['calmar_ratio']:.2f}")
            print(f"   Max Drawdown: {metrics['max_drawdown']:.2f}%")
            
            # Interpretation
            if metrics['sharpe_ratio'] > 2.0:
                print(f"   🌟 Excellent risk-adjusted returns")
            elif metrics['sharpe_ratio'] > 1.0:
                print(f"   ✅ Good risk-adjusted returns")
            elif metrics['sharpe_ratio'] > 0.5:
                print(f"   ⚠️ Acceptable risk-adjusted returns")
            else:
                print(f"   ❌ Poor risk-adjusted returns")
        
        # Advanced Metrics
        if 'var_95' in metrics:
            print(f"\n🔬 Advanced Metrics:")
            print(f"   VaR (95%): ${metrics['var_95']:+.2f}")
            print(f"   CVaR (95%): ${metrics['cvar_95']:+.2f}")
            print(f"   Skewness: {metrics['skewness']:+.2f}")
            print(f"   Kurtosis: {metrics['kurtosis']:+.2f}")
            print(f"   Longest Win Streak: {metrics['longest_win_streak']}")
            print(f"   Longest Loss Streak: {metrics['longest_loss_streak']}")
            print(f"   Consistency (R²): {metrics['r_squared']:.2f}")

# Example performance analysis
async def demo_performance_analysis(account_id: str):
    """Demonstrate comprehensive performance analysis."""
    
    if not account_id:
        return
    
    async with AsyncClient(token=TOKEN, environment=ENVIRONMENT) as client:
        analyzer = PerformanceAnalyzer(client, account_id)
        
        # Calculate metrics for last 90 days
        metrics = await analyzer.calculate_comprehensive_metrics(days_back=90)
        
        return metrics
```

---

## Performance Attribution Analysis

Break down returns by different factors to understand what drives performance.

### Attribution Implementation

```python
class PerformanceAttribution:
    """Analyze what factors contribute to trading performance."""
    
    def __init__(self):
        self.attribution_factors = {
            'strategy': {},
            'instrument': {},
            'timeframe': {},
            'market_condition': {}
        }
    
    def add_trade_attribution(self, trade_data: dict):
        """Add trade with attribution factors."""
        
        pnl = trade_data['pnl']
        
        # Attribute to strategy
        strategy = trade_data.get('strategy', 'unknown')
        if strategy not in self.attribution_factors['strategy']:
            self.attribution_factors['strategy'][strategy] = []
        self.attribution_factors['strategy'][strategy].append(pnl)
        
        # Attribute to instrument
        instrument = trade_data.get('instrument', 'unknown')
        if instrument not in self.attribution_factors['instrument']:
            self.attribution_factors['instrument'][instrument] = []
        self.attribution_factors['instrument'][instrument].append(pnl)
        
        # Attribute to timeframe
        timeframe = trade_data.get('timeframe', 'unknown')
        if timeframe not in self.attribution_factors['timeframe']:
            self.attribution_factors['timeframe'][timeframe] = []
        self.attribution_factors['timeframe'][timeframe].append(pnl)
        
        # Attribute to market condition
        market_condition = trade_data.get('market_condition', 'unknown')
        if market_condition not in self.attribution_factors['market_condition']:
            self.attribution_factors['market_condition'][market_condition] = []
        self.attribution_factors['market_condition'][market_condition].append(pnl)
    
    def calculate_attribution_metrics(self) -> dict:
        """Calculate attribution metrics for each factor."""
        
        attribution_results = {}
        
        for factor_type, factor_data in self.attribution_factors.items():
            attribution_results[factor_type] = {}
            
            total_factor_pnl = 0
            
            for factor_name, pnl_list in factor_data.items():
                if pnl_list:
                    factor_pnl = sum(pnl_list)
                    factor_trades = len(pnl_list)
                    factor_win_rate = len([p for p in pnl_list if p > 0]) / factor_trades * 100
                    factor_avg_pnl = factor_pnl / factor_trades
                    
                    attribution_results[factor_type][factor_name] = {
                        'total_pnl': factor_pnl,
                        'trade_count': factor_trades,
                        'win_rate': factor_win_rate,
                        'avg_pnl': factor_avg_pnl
                    }
                    
                    total_factor_pnl += factor_pnl
            
            # Calculate percentage contribution
            for factor_name, metrics in attribution_results[factor_type].items():
                if total_factor_pnl != 0:
                    contribution_pct = (metrics['total_pnl'] / total_factor_pnl) * 100
                    metrics['contribution_pct'] = contribution_pct
                else:
                    metrics['contribution_pct'] = 0
        
        return attribution_results
    
    def print_attribution_report(self):
        """Print detailed attribution analysis."""
        
        attribution_results = self.calculate_attribution_metrics()
        
        print(f"\n🔍 PERFORMANCE ATTRIBUTION ANALYSIS")
        print("=" * 55)
        
        for factor_type, factor_results in attribution_results.items():
            print(f"\n📊 {factor_type.replace('_', ' ').title()} Attribution:")
            
            # Sort by contribution
            sorted_factors = sorted(
                factor_results.items(),
                key=lambda x: x[1]['total_pnl'],
                reverse=True
            )
            
            for factor_name, metrics in sorted_factors:
                status = "🟫" if metrics['total_pnl'] > 0 else "🔴"
                print(f"   {factor_name}: ${metrics['total_pnl']:+.2f} "
                      f"({metrics['contribution_pct']:+.1f}%) - "
                      f"{metrics['trade_count']} trades, "
                      f"{metrics['win_rate']:.1f}% win rate {status}")
        
        return attribution_results
    
    def identify_best_performers(self) -> dict:
        """Identify best performing factors."""
        
        attribution_results = self.calculate_attribution_metrics()
        best_performers = {}
        
        for factor_type, factor_results in attribution_results.items():
            if factor_results:
                best_factor = max(
                    factor_results.items(),
                    key=lambda x: x[1]['total_pnl']
                )
                
                best_performers[factor_type] = {
                    'name': best_factor[0],
                    'metrics': best_factor[1]
                }
        
        print(f"\n🏆 Best Performers by Category:")
        for factor_type, best in best_performers.items():
            print(f"   {factor_type.title()}: {best['name']} "
                  f"(${best['metrics']['total_pnl']:+.2f})")
        
        return best_performers

# Example attribution analysis
def demo_attribution_analysis():
    """Demonstrate performance attribution."""
    
    # Sample trade data with attribution factors
    sample_trades = [
        {'pnl': 150, 'strategy': 'trend_following', 'instrument': 'EUR_USD', 'timeframe': 'H4', 'market_condition': 'trending'},
        {'pnl': -80, 'strategy': 'mean_reversion', 'instrument': 'GBP_USD', 'timeframe': 'H1', 'market_condition': 'ranging'},
        {'pnl': 200, 'strategy': 'trend_following', 'instrument': 'USD_JPY', 'timeframe': 'H4', 'market_condition': 'trending'},
        {'pnl': -50, 'strategy': 'breakout', 'instrument': 'EUR_USD', 'timeframe': 'M15', 'market_condition': 'volatile'},
        {'pnl': 120, 'strategy': 'mean_reversion', 'instrument': 'AUD_USD', 'timeframe': 'H1', 'market_condition': 'ranging'},
        {'pnl': -30, 'strategy': 'trend_following', 'instrument': 'GBP_USD', 'timeframe': 'H4', 'market_condition': 'choppy'},
        {'pnl': 180, 'strategy': 'breakout', 'instrument': 'USD_CAD', 'timeframe': 'M15', 'market_condition': 'volatile'}
    ]
    
    attribution = PerformanceAttribution()
    
    # Add trades to attribution analysis
    for trade in sample_trades:
        attribution.add_trade_attribution(trade)
    
    # Generate reports
    results = attribution.print_attribution_report()
    best_performers = attribution.identify_best_performers()
    
    return {
        'attribution_results': results,
        'best_performers': best_performers
    }
```

---

## Portfolio Optimization Techniques

Optimize allocation across multiple strategies and instruments.

### Modern Portfolio Theory Implementation

```python
import numpy as np
from scipy.optimize import minimize

class PortfolioOptimizer:
    """Optimize portfolio allocation using Modern Portfolio Theory."""
    
    def __init__(self, strategy_returns: dict, risk_free_rate: float = 0.02):
        self.strategy_returns = strategy_returns
        self.risk_free_rate = risk_free_rate
        self.strategy_names = list(strategy_returns.keys())
        self.returns_matrix = np.array([strategy_returns[name] for name in self.strategy_names]).T
    
    def calculate_portfolio_metrics(self, weights: np.ndarray) -> dict:
        """Calculate portfolio return and risk for given weights."""
        
        # Portfolio return
        portfolio_return = np.sum(np.mean(self.returns_matrix, axis=0) * weights)
        
        # Portfolio variance
        cov_matrix = np.cov(self.returns_matrix.T)
        portfolio_variance = np.dot(weights.T, np.dot(cov_matrix, weights))
        portfolio_volatility = np.sqrt(portfolio_variance)
        
        # Sharpe ratio
        sharpe_ratio = (portfolio_return - self.risk_free_rate) / portfolio_volatility
        
        return {
            'return': portfolio_return,
            'volatility': portfolio_volatility,
            'sharpe_ratio': sharpe_ratio,
            'weights': weights
        }
    
    def optimize_sharpe_ratio(self) -> dict:
        """Find portfolio weights that maximize Sharpe ratio."""
        
        num_strategies = len(self.strategy_names)
        
        # Objective function (negative Sharpe ratio for minimization)
        def negative_sharpe(weights):
            metrics = self.calculate_portfolio_metrics(weights)
            return -metrics['sharpe_ratio']
        
        # Constraints
        constraints = (
            {'type': 'eq', 'fun': lambda x: np.sum(x) - 1},  # Weights sum to 1
        )
        
        # Bounds (0 to 1 for each weight)
        bounds = tuple((0, 1) for _ in range(num_strategies))
        
        # Initial guess (equal weights)
        initial_weights = np.array([1/num_strategies] * num_strategies)
        
        # Optimize
        result = minimize(
            negative_sharpe,
            initial_weights,
            method='SLSQP',
            bounds=bounds,
            constraints=constraints
        )
        
        if result.success:
            optimal_weights = result.x
            optimal_metrics = self.calculate_portfolio_metrics(optimal_weights)
            
            print(f"🎯 Optimal Sharpe Ratio Portfolio:")
            for i, strategy in enumerate(self.strategy_names):
                print(f"   {strategy}: {optimal_weights[i]:.1%}")
            
            print(f"   Expected Return: {optimal_metrics['return']:.2%}")
            print(f"   Volatility: {optimal_metrics['volatility']:.2%}")
            print(f"   Sharpe Ratio: {optimal_metrics['sharpe_ratio']:.2f}")
            
            return optimal_metrics
        else:
            return {'error': 'Optimization failed'}
    
    def optimize_minimum_variance(self) -> dict:
        """Find portfolio weights that minimize variance."""
        
        num_strategies = len(self.strategy_names)
        
        # Objective function (portfolio variance)
        def portfolio_variance(weights):
            cov_matrix = np.cov(self.returns_matrix.T)
            return np.dot(weights.T, np.dot(cov_matrix, weights))
        
        # Constraints
        constraints = (
            {'type': 'eq', 'fun': lambda x: np.sum(x) - 1},  # Weights sum to 1
        )
        
        # Bounds
        bounds = tuple((0, 1) for _ in range(num_strategies))
        
        # Initial guess
        initial_weights = np.array([1/num_strategies] * num_strategies)
        
        # Optimize
        result = minimize(
            portfolio_variance,
            initial_weights,
            method='SLSQP',
            bounds=bounds,
            constraints=constraints
        )
        
        if result.success:
            optimal_weights = result.x
            optimal_metrics = self.calculate_portfolio_metrics(optimal_weights)
            
            print(f"\n🛡️ Minimum Variance Portfolio:")
            for i, strategy in enumerate(self.strategy_names):
                print(f"   {strategy}: {optimal_weights[i]:.1%}")
            
            print(f"   Expected Return: {optimal_metrics['return']:.2%}")
            print(f"   Volatility: {optimal_metrics['volatility']:.2%}")
            print(f"   Sharpe Ratio: {optimal_metrics['sharpe_ratio']:.2f}")
            
            return optimal_metrics
        else:
            return {'error': 'Optimization failed'}
    
    def calculate_efficient_frontier(self, num_points: int = 50) -> dict:
        """Calculate efficient frontier points."""
        
        num_strategies = len(self.strategy_names)
        
        # Get min and max returns
        min_return = np.min(np.mean(self.returns_matrix, axis=0))
        max_return = np.max(np.mean(self.returns_matrix, axis=0))
        
        target_returns = np.linspace(min_return, max_return, num_points)
        
        efficient_portfolios = []
        
        for target_return in target_returns:
            # Objective function (minimize variance)
            def portfolio_variance(weights):
                cov_matrix = np.cov(self.returns_matrix.T)
                return np.dot(weights.T, np.dot(cov_matrix, weights))
            
            # Constraints
            constraints = (
                {'type': 'eq', 'fun': lambda x: np.sum(x) - 1},  # Weights sum to 1
                {'type': 'eq', 'fun': lambda x: np.sum(np.mean(self.returns_matrix, axis=0) * x) - target_return}  # Target return
            )
            
            # Bounds
            bounds = tuple((0, 1) for _ in range(num_strategies))
            
            # Initial guess
            initial_weights = np.array([1/num_strategies] * num_strategies)
            
            # Optimize
            result = minimize(
                portfolio_variance,
                initial_weights,
                method='SLSQP',
                bounds=bounds,
                constraints=constraints
            )
            
            if result.success:
                weights = result.x
                metrics = self.calculate_portfolio_metrics(weights)
                efficient_portfolios.append(metrics)
        
        print(f"\n📈 Efficient Frontier ({len(efficient_portfolios)} points):")
        print(f"   Return Range: {min_return:.2%} to {max_return:.2%}")
        print(f"   Risk Range: {min([p['volatility'] for p in efficient_portfolios]):.2%} to "
              f"{max([p['volatility'] for p in efficient_portfolios]):.2%}")
        
        return {
            'efficient_portfolios': efficient_portfolios,
            'target_returns': target_returns.tolist()
        }

# Example portfolio optimization
def demo_portfolio_optimization():
    """Demonstrate portfolio optimization."""
    
    # Sample strategy returns (daily)
    strategy_returns = {
        'trend_following': np.random.normal(0.001, 0.02, 252),  # 252 trading days
        'mean_reversion': np.random.normal(0.0008, 0.015, 252),
        'breakout': np.random.normal(0.0012, 0.025, 252),
        'carry_trade': np.random.normal(0.0005, 0.01, 252)
    }
    
    optimizer = PortfolioOptimizer(strategy_returns)
    
    # Optimize for maximum Sharpe ratio
    max_sharpe = optimizer.optimize_sharpe_ratio()
    
    # Optimize for minimum variance
    min_variance = optimizer.optimize_minimum_variance()
    
    # Calculate efficient frontier
    frontier = optimizer.calculate_efficient_frontier()
    
    return {
        'max_sharpe': max_sharpe,
        'min_variance': min_variance,
        'efficient_frontier': frontier
    }
```

---

## ✅ Skill Checkpoint: Performance Optimization

Test your understanding of performance optimization:

!!! question "🧠 Test Your Understanding"
    1. **Why is Sharpe ratio better than basic returns for evaluating performance?**
       <details>
       <summary>Click to reveal answer</summary>
       **Sharpe ratio adjusts for risk taken**. A 20% return with 30% volatility (Sharpe 0.6) is worse than 15% return with 10% volatility (Sharpe 1.5). It measures return per unit of risk.
       </details>

    2. **When should you use fractional Kelly rather than full Kelly?**
       <details>
       <summary>Click to reveal answer</summary>
       **Almost always**. Full Kelly can recommend very large position sizes that create excessive volatility. Fractional Kelly (25-50% of full) provides most of the benefit with much lower volatility.
       </details>

    3. **What does performance attribution tell you that overall metrics don't?**
       <details>
       <summary>Click to reveal answer</summary>
       **Which specific factors drive your returns**. Overall metrics show you made money, but attribution shows whether it came from strategy choice, instrument selection, market timing, or luck.
       </details>

---

## Optimization Best Practices

### Implementation Guidelines

1. **Start with Solid Foundation**
   - Ensure basic risk management is working
   - Have sufficient trade history (30+ trades minimum)
   - Validate metrics on out-of-sample data

2. **Use Multiple Metrics**
   - Don't optimize for single metric
   - Balance return, risk, and consistency
   - Consider drawdown and volatility

3. **Regular Reoptimization**
   - Review allocations monthly
   - Adjust for changing market conditions
   - Account for strategy performance drift

4. **Avoid Overfitting**
   - Use basic, robust metrics
   - Test on multiple time periods
   - Prefer consistent performance over peak performance

---

## What You've Learned

✅ **Kelly Criterion**: Mathematical optimization for position sizing

✅ **Advanced Metrics**: Sharpe, Sortino, Calmar ratios and sophisticated risk measures

✅ **Performance Attribution**: Understanding what drives your returns

✅ **Portfolio Optimization**: Modern Portfolio Theory for strategy allocation

✅ **Best Practices**: Implementation guidelines for sustainable optimization

!!! success "🎉 Performance Optimization Complete!"
    You now have the advanced tools to optimize your trading performance systematically. These techniques will help you squeeze maximum risk-adjusted returns from your strategies while maintaining robust risk controls. Next, learn how to validate and implement these concepts in practice.

---

## Next Steps

Continue to [Best Practices & Validation](best-practices.md) to learn how to implement and validate these advanced concepts in your trading practice.

---

## Related Resources

- **[Risk Management Fundamentals](fundamentals.md)** - Core risk management principles
- **[Portfolio Risk Management](portfolio-risk.md)** - Managing risk across multiple positions
- **[Portfolio Analysis](../portfolio-analysis/index.md)** - Advanced portfolio analysis techniques
- **[Performance Attribution](../portfolio-analysis/performance-attribution.md)** - Detailed performance analysis methods