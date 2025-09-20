# Portfolio Analysis Tutorial

This tutorial teaches you how to analyze and optimize your trading portfolio using advanced statistical methods, correlation analysis, and performance metrics.

## Prerequisites

- Completed [Basic Trading](basic-trading.md) and [Risk Management](risk-management.md) tutorials
- Understanding of portfolio theory concepts
- FiveTwenty setup with historical data access

## Learning Objectives

By the end of this tutorial, you will:

- ✅ Analyze portfolio composition and diversification
- ✅ Calculate correlation matrices and risk metrics
- ✅ Optimize position allocation using modern portfolio theory
- ✅ Build performance attribution systems
- ✅ Create portfolio rebalancing strategies

---

## 1. Portfolio Theory Fundamentals

### Modern Portfolio Theory (MPT)

**Key Concepts:**

- **Diversification**: Reducing risk through uncorrelated assets
- **Efficient Frontier**: Optimal risk/return combinations
- **Correlation**: How instruments move together (-1 to +1)
- **Sharpe Ratio**: Risk-adjusted returns
- **Value at Risk (VaR)**: Maximum expected loss

### Portfolio Construction Principles

1. **Asset Selection**: Choose instruments with low correlation
2. **Position Sizing**: Weight positions based on risk contribution
3. **Risk Budgeting**: Allocate risk across different sources
4. **Rebalancing**: Maintain target allocations over time

---

## 2. Data Collection and Analysis Framework

```python
import asyncio
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
from typing import Dict, List, Tuple

from fivetwenty import AsyncClient, Environment
from fivetwenty.models import CandlestickGranularity
from fivetwenty.exceptions import FiveTwentyError

# Configuration
TOKEN = "your-api-token-here"
ENVIRONMENT = Environment.PRACTICE

class PortfolioAnalyzer:
    """Comprehensive portfolio analysis framework."""

    def __init__(self, client: AsyncClient, account_id: str):
        self.client = client
        self.account_id = account_id
        self.instruments = []
        self.price_data = {}
        self.returns_data = {}
        self.correlation_matrix = None
        self.portfolio_weights = {}

    async def collect_price_data(self, instruments: List[str],
                                periods: int = 500,
                                granularity: CandlestickGranularity = CandlestickGranularity.H4) -> Dict[str, pd.DataFrame]:
        """Collect historical price data for portfolio analysis."""

        print(f"📊 Collecting price data for {len(instruments)} instruments...")

        price_data = {}

        for instrument in instruments:
            try:
                print(f"   Fetching {instrument}...")

                candles = await self.client.instruments.candles(
                    instrument=instrument,
                    count=periods,
                    granularity=granularity
                )

                # Convert to DataFrame
                data = []
                for candle in candles.candles:
                    if candle.mid:
                        data.append({
                            'timestamp': pd.to_datetime(candle.time),
                            'open': float(candle.mid.o),
                            'high': float(candle.mid.h),
                            'low': float(candle.mid.l),
                            'close': float(candle.mid.c),
                            'volume': int(candle.volume)
                        })

                df = pd.DataFrame(data)
                df.set_index('timestamp', inplace=True)
                df.sort_index(inplace=True)

                price_data[instrument] = df
                print(f"   ✅ {instrument}: {len(df)} candles")

            except FiveTwentyError as e:
                print(f"   ❌ Error fetching {instrument}: {e.message}")

        self.instruments = list(price_data.keys())
        self.price_data = price_data

        print(f"✅ Data collection complete: {len(self.instruments)} instruments")
        return price_data

    def calculate_returns(self, price_column: str = 'close') -> Dict[str, pd.Series]:
        """Calculate returns for all instruments."""

        returns_data = {}

        for instrument, df in self.price_data.items():
            # Calculate percentage returns
            returns = df[price_column].pct_change().dropna()
            returns_data[instrument] = returns

        self.returns_data = returns_data
        print(f"📈 Returns calculated for {len(returns_data)} instruments")

        return returns_data

    def calculate_correlation_matrix(self) -> pd.DataFrame:
        """Calculate correlation matrix of returns."""

        if not self.returns_data:
            self.calculate_returns()

        # Align returns data
        returns_df = pd.DataFrame(self.returns_data)
        returns_df = returns_df.dropna()

        # Calculate correlation matrix
        correlation_matrix = returns_df.corr()
        self.correlation_matrix = correlation_matrix

        print(f"🔗 Correlation matrix calculated ({correlation_matrix.shape[0]}x{correlation_matrix.shape[1]})")
        return correlation_matrix

    def analyze_portfolio_statistics(self) -> Dict:
        """Calculate comprehensive portfolio statistics."""

        if not self.returns_data:
            self.calculate_returns()

        # Align returns data
        returns_df = pd.DataFrame(self.returns_data)
        returns_df = returns_df.dropna()

        statistics = {}

        for instrument in returns_df.columns:
            returns = returns_df[instrument]

            stats = {
                'mean_return': returns.mean() * 100,  # Percentage
                'volatility': returns.std() * 100,    # Percentage
                'sharpe_ratio': (returns.mean() / returns.std()) if returns.std() > 0 else 0,
                'max_return': returns.max() * 100,
                'min_return': returns.min() * 100,
                'skewness': returns.skew(),
                'kurtosis': returns.kurtosis(),
                'var_95': np.percentile(returns, 5) * 100,  # 95% VaR
                'var_99': np.percentile(returns, 1) * 100   # 99% VaR
            }

            statistics[instrument] = stats

        # Portfolio-level statistics if weights are defined
        if self.portfolio_weights:
            portfolio_returns = self._calculate_portfolio_returns(returns_df)

            statistics['PORTFOLIO'] = {
                'mean_return': portfolio_returns.mean() * 100,
                'volatility': portfolio_returns.std() * 100,
                'sharpe_ratio': (portfolio_returns.mean() / portfolio_returns.std()) if portfolio_returns.std() > 0 else 0,
                'max_return': portfolio_returns.max() * 100,
                'min_return': portfolio_returns.min() * 100,
                'skewness': portfolio_returns.skew(),
                'kurtosis': portfolio_returns.kurtosis(),
                'var_95': np.percentile(portfolio_returns, 5) * 100,
                'var_99': np.percentile(portfolio_returns, 1) * 100
            }

        return statistics

    def _calculate_portfolio_returns(self, returns_df: pd.DataFrame) -> pd.Series:
        """Calculate portfolio returns based on weights."""

        # Ensure weights sum to 1
        total_weight = sum(self.portfolio_weights.values())
        normalized_weights = {k: v/total_weight for k, v in self.portfolio_weights.items()}

        # Calculate weighted returns
        portfolio_returns = pd.Series(0, index=returns_df.index)

        for instrument, weight in normalized_weights.items():
            if instrument in returns_df.columns:
                portfolio_returns += returns_df[instrument] * weight

        return portfolio_returns

    def plot_correlation_heatmap(self, figsize: Tuple[int, int] = (12, 10)):
        """Plot correlation matrix heatmap."""

        if self.correlation_matrix is None:
            self.calculate_correlation_matrix()

        plt.figure(figsize=figsize)

        # Create heatmap
        sns.heatmap(
            self.correlation_matrix,
            annot=True,
            cmap='RdYlBu_r',
            center=0,
            square=True,
            fmt='.3f',
            cbar_kws={'label': 'Correlation Coefficient'}
        )

        plt.title('Portfolio Correlation Matrix', fontsize=16, fontweight='bold')
        plt.tight_layout()
        plt.show()

    def identify_correlation_clusters(self, threshold: float = 0.7) -> Dict[str, List[str]]:
        """Identify groups of highly correlated instruments."""

        if self.correlation_matrix is None:
            self.calculate_correlation_matrix()

        clusters = {}
        processed = set()

        for i, instrument1 in enumerate(self.correlation_matrix.columns):
            if instrument1 in processed:
                continue

            cluster = [instrument1]
            processed.add(instrument1)

            for j, instrument2 in enumerate(self.correlation_matrix.columns):
                if (i != j and
                    instrument2 not in processed and
                    abs(self.correlation_matrix.iloc[i, j]) >= threshold):

                    cluster.append(instrument2)
                    processed.add(instrument2)

            if len(cluster) > 1:
                clusters[f"Cluster_{len(clusters)+1}"] = cluster

        print(f"🔗 Found {len(clusters)} correlation clusters (threshold: {threshold}):")
        for cluster_name, instruments in clusters.items():
            print(f"   {cluster_name}: {', '.join(instruments)}")

        return clusters

# Example usage
async def demo_portfolio_analysis(account_id: str):
    """Demonstrate portfolio analysis capabilities."""

    if not account_id:
        print("❌ No account ID")
        return

    async with AsyncClient(token=TOKEN, environment=ENVIRONMENT) as client:
        analyzer = PortfolioAnalyzer(client, account_id)

        # Define instruments for analysis
        instruments = ["EUR_USD", "GBP_USD", "USD_JPY", "AUD_USD", "USD_CHF", "NZD_USD"]

        # Collect price data
        price_data = await analyzer.collect_price_data(instruments, periods=200)

        # Calculate returns and correlations
        returns_data = analyzer.calculate_returns()
        correlation_matrix = analyzer.calculate_correlation_matrix()

        # Analyze statistics
        stats = analyzer.analyze_portfolio_statistics()

        # Display results
        print(f"\n📊 Portfolio Statistics Summary:")
        print("-" * 60)

        for instrument, stat in stats.items():
            if instrument != 'PORTFOLIO':
                print(f"{instrument:10} | Return: {stat['mean_return']:+6.3f}% | "
                      f"Vol: {stat['volatility']:6.3f}% | Sharpe: {stat['sharpe_ratio']:6.3f}")

        # Find correlation clusters
        clusters = analyzer.identify_correlation_clusters(threshold=0.6)

        # Plot correlation heatmap
        if len(instruments) > 2:
            analyzer.plot_correlation_heatmap()

        return analyzer
```

---

## 3. Portfolio Optimization

### Modern Portfolio Theory Implementation

```python
from scipy.optimize import minimize
import warnings
warnings.filterwarnings('ignore')

class PortfolioOptimizer:
    """Portfolio optimization using Modern Portfolio Theory."""

    def __init__(self, returns_data: Dict[str, pd.Series]):
        self.returns_data = returns_data
        self.instruments = list(returns_data.keys())
        self.returns_df = pd.DataFrame(returns_data).dropna()
        self.mean_returns = self.returns_df.mean()
        self.cov_matrix = self.returns_df.cov()
        self.num_assets = len(self.instruments)

    def portfolio_performance(self, weights: np.ndarray) -> Tuple[float, float, float]:
        """Calculate portfolio performance metrics."""

        # Portfolio return
        portfolio_return = np.sum(self.mean_returns * weights)

        # Portfolio volatility
        portfolio_volatility = np.sqrt(np.dot(weights.T, np.dot(self.cov_matrix, weights)))

        # Sharpe ratio (assuming risk-free rate = 0)
        sharpe_ratio = portfolio_return / portfolio_volatility if portfolio_volatility > 0 else 0

        return portfolio_return, portfolio_volatility, sharpe_ratio

    def negative_sharpe(self, weights: np.ndarray) -> float:
        """Negative Sharpe ratio for optimization (minimize)."""
        return -self.portfolio_performance(weights)[2]

    def portfolio_volatility(self, weights: np.ndarray) -> float:
        """Portfolio volatility for minimum variance optimization."""
        return self.portfolio_performance(weights)[1]

    def optimize_sharpe_ratio(self) -> Dict:
        """Find portfolio with maximum Sharpe ratio."""

        # Constraints: weights sum to 1
        constraints = {'type': 'eq', 'fun': lambda x: np.sum(x) - 1}

        # Bounds: no short selling (0 <= weight <= 1)
        bounds = tuple((0, 1) for _ in range(self.num_assets))

        # Initial guess: equal weights
        initial_guess = np.array([1/self.num_assets] * self.num_assets)

        # Optimize
        result = minimize(
            self.negative_sharpe,
            initial_guess,
            method='SLSQP',
            bounds=bounds,
            constraints=constraints,
            options={'disp': False}
        )

        if result.success:
            optimal_weights = result.x
            perf = self.portfolio_performance(optimal_weights)

            portfolio = {
                'type': 'Maximum Sharpe Ratio',
                'weights': dict(zip(self.instruments, optimal_weights)),
                'expected_return': perf[0] * 100,  # Percentage
                'volatility': perf[1] * 100,       # Percentage
                'sharpe_ratio': perf[2],
                'optimization_success': True
            }
        else:
            portfolio = {'optimization_success': False, 'error': result.message}

        return portfolio

    def optimize_minimum_variance(self) -> Dict:
        """Find minimum variance portfolio."""

        constraints = {'type': 'eq', 'fun': lambda x: np.sum(x) - 1}
        bounds = tuple((0, 1) for _ in range(self.num_assets))
        initial_guess = np.array([1/self.num_assets] * self.num_assets)

        result = minimize(
            self.portfolio_volatility,
            initial_guess,
            method='SLSQP',
            bounds=bounds,
            constraints=constraints,
            options={'disp': False}
        )

        if result.success:
            optimal_weights = result.x
            perf = self.portfolio_performance(optimal_weights)

            portfolio = {
                'type': 'Minimum Variance',
                'weights': dict(zip(self.instruments, optimal_weights)),
                'expected_return': perf[0] * 100,
                'volatility': perf[1] * 100,
                'sharpe_ratio': perf[2],
                'optimization_success': True
            }
        else:
            portfolio = {'optimization_success': False, 'error': result.message}

        return portfolio

    def efficient_frontier(self, num_points: int = 100) -> pd.DataFrame:
        """Generate efficient frontier."""

        # Target returns range
        min_ret = self.mean_returns.min()
        max_ret = self.mean_returns.max()
        target_returns = np.linspace(min_ret, max_ret, num_points)

        efficient_portfolios = []

        for target_return in target_returns:
            # Constraints: weights sum to 1, target return
            constraints = [
                {'type': 'eq', 'fun': lambda x: np.sum(x) - 1},
                {'type': 'eq', 'fun': lambda x: np.sum(self.mean_returns * x) - target_return}
            ]

            bounds = tuple((0, 1) for _ in range(self.num_assets))
            initial_guess = np.array([1/self.num_assets] * self.num_assets)

            result = minimize(
                self.portfolio_volatility,
                initial_guess,
                method='SLSQP',
                bounds=bounds,
                constraints=constraints,
                options={'disp': False}
            )

            if result.success:
                weights = result.x
                perf = self.portfolio_performance(weights)

                efficient_portfolios.append({
                    'return': perf[0] * 100,
                    'volatility': perf[1] * 100,
                    'sharpe_ratio': perf[2],
                    'weights': weights
                })

        return pd.DataFrame(efficient_portfolios)

    def plot_efficient_frontier(self, show_optimal_portfolios: bool = True):
        """Plot the efficient frontier."""

        print("📊 Generating efficient frontier...")
        frontier = self.efficient_frontier(num_points=50)

        if frontier.empty:
            print("❌ Could not generate efficient frontier")
            return

        plt.figure(figsize=(12, 8))

        # Plot efficient frontier
        plt.scatter(frontier['volatility'], frontier['return'],
                   c=frontier['sharpe_ratio'], cmap='viridis',
                   alpha=0.7, s=50, label='Efficient Frontier')

        plt.colorbar(label='Sharpe Ratio')

        # Plot individual assets
        for i, instrument in enumerate(self.instruments):
            ret = self.mean_returns[instrument] * 100
            vol = np.sqrt(self.cov_matrix.iloc[i, i]) * 100
            plt.scatter(vol, ret, marker='o', s=100, label=instrument)
            plt.annotate(instrument, (vol, ret), xytext=(5, 5),
                        textcoords='offset points', fontsize=8)

        # Plot optimal portfolios
        if show_optimal_portfolios:
            max_sharpe = self.optimize_sharpe_ratio()
            min_var = self.optimize_minimum_variance()

            if max_sharpe['optimization_success']:
                plt.scatter(max_sharpe['volatility'], max_sharpe['expected_return'],
                           marker='*', s=200, color='red', label='Max Sharpe Ratio')

            if min_var['optimization_success']:
                plt.scatter(min_var['volatility'], min_var['expected_return'],
                           marker='*', s=200, color='green', label='Min Variance')

        plt.xlabel('Volatility (%)', fontsize=12)
        plt.ylabel('Expected Return (%)', fontsize=12)
        plt.title('Efficient Frontier', fontsize=14, fontweight='bold')
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.show()

# Demo portfolio optimization
async def demo_portfolio_optimization(analyzer: PortfolioAnalyzer):
    """Demonstrate portfolio optimization."""

    if not analyzer.returns_data:
        print("❌ No returns data available")
        return

    optimizer = PortfolioOptimizer(analyzer.returns_data)

    print("🎯 Portfolio Optimization Results:")
    print("=" * 50)

    # Optimize for maximum Sharpe ratio
    max_sharpe_portfolio = optimizer.optimize_sharpe_ratio()

    if max_sharpe_portfolio['optimization_success']:
        print(f"\n📈 Maximum Sharpe Ratio Portfolio:")
        print(f"   Expected Return: {max_sharpe_portfolio['expected_return']:.3f}%")
        print(f"   Volatility: {max_sharpe_portfolio['volatility']:.3f}%")
        print(f"   Sharpe Ratio: {max_sharpe_portfolio['sharpe_ratio']:.3f}")
        print(f"   Weights:")

        for instrument, weight in max_sharpe_portfolio['weights'].items():
            if weight > 0.01:  # Show weights > 1%
                print(f"     {instrument}: {weight*100:.1f}%")

    # Optimize for minimum variance
    min_var_portfolio = optimizer.optimize_minimum_variance()

    if min_var_portfolio['optimization_success']:
        print(f"\n📉 Minimum Variance Portfolio:")
        print(f"   Expected Return: {min_var_portfolio['expected_return']:.3f}%")
        print(f"   Volatility: {min_var_portfolio['volatility']:.3f}%")
        print(f"   Sharpe Ratio: {min_var_portfolio['sharpe_ratio']:.3f}")
        print(f"   Weights:")

        for instrument, weight in min_var_portfolio['weights'].items():
            if weight > 0.01:
                print(f"     {instrument}: {weight*100:.1f}%")

    # Plot efficient frontier
    optimizer.plot_efficient_frontier()

    return {
        'max_sharpe': max_sharpe_portfolio,
        'min_variance': min_var_portfolio,
        'optimizer': optimizer
    }
```

---

## 4. Risk Attribution and Decomposition

### Risk Factor Analysis

```python
from decimal import Decimal

class RiskAttributionAnalyzer:
    """Analyze portfolio risk attribution and factor exposure."""

    def __init__(self, returns_data: Dict[str, pd.Series], portfolio_weights: Dict[str, float]):
        self.returns_data = returns_data
        self.portfolio_weights = portfolio_weights
        self.returns_df = pd.DataFrame(returns_data).dropna()
        self.instruments = list(returns_data.keys())

    def calculate_risk_contribution(self) -> Dict[str, Dict[str, float]]:
        """Calculate risk contribution of each position."""

        # Normalize weights
        total_weight = sum(self.portfolio_weights.values())
        weights = np.array([self.portfolio_weights.get(inst, 0) / total_weight
                           for inst in self.instruments])

        # Covariance matrix
        cov_matrix = self.returns_df.cov().values

        # Portfolio variance
        portfolio_variance = np.dot(weights.T, np.dot(cov_matrix, weights))
        portfolio_volatility = np.sqrt(portfolio_variance)

        # Marginal risk contribution
        marginal_risk = np.dot(cov_matrix, weights) / portfolio_volatility

        # Component risk contribution
        component_risk = weights * marginal_risk

        # Percentage risk contribution
        risk_contribution_pct = component_risk / portfolio_volatility * 100

        risk_attribution = {}

        for i, instrument in enumerate(self.instruments):
            risk_attribution[instrument] = {
                'weight': weights[i] * 100,
                'marginal_risk': marginal_risk[i] * 100,
                'component_risk': component_risk[i] * 100,
                'risk_contribution_pct': risk_contribution_pct[i],
                'risk_per_unit_weight': (marginal_risk[i] / weights[i] * 100) if weights[i] > 0 else 0
            }

        return risk_attribution

    def calculate_diversification_ratio(self) -> float:
        """Calculate portfolio diversification ratio."""

        weights = np.array([self.portfolio_weights.get(inst, 0)
                           for inst in self.instruments])

        # Normalize weights
        weights = weights / np.sum(weights)

        # Individual volatilities
        individual_vols = self.returns_df.std().values

        # Weighted average volatility
        weighted_avg_vol = np.sum(weights * individual_vols)

        # Portfolio volatility
        cov_matrix = self.returns_df.cov().values
        portfolio_vol = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))

        # Diversification ratio
        diversification_ratio = weighted_avg_vol / portfolio_vol

        return diversification_ratio

    def analyze_concentration_risk(self) -> Dict:
        """Analyze portfolio concentration metrics."""

        weights = np.array([self.portfolio_weights.get(inst, 0)
                           for inst in self.instruments])
        weights = weights / np.sum(weights)  # Normalize

        # Herfindahl-Hirschman Index (HHI)
        hhi = np.sum(weights ** 2)

        # Effective number of positions
        effective_positions = 1 / hhi

        # Maximum weight
        max_weight = np.max(weights)

        # Weight distribution statistics
        weight_std = np.std(weights)
        weight_gini = self._calculate_gini_coefficient(weights)

        concentration_metrics = {
            'hhi': hhi,
            'effective_positions': effective_positions,
            'max_weight': max_weight * 100,
            'weight_std': weight_std * 100,
            'gini_coefficient': weight_gini,
            'concentration_level': self._assess_concentration_level(hhi)
        }

        return concentration_metrics

    def _calculate_gini_coefficient(self, weights: np.ndarray) -> float:
        """Calculate Gini coefficient for weight distribution."""

        # Sort weights
        sorted_weights = np.sort(weights)
        n = len(sorted_weights)

        # Calculate Gini coefficient
        cumsum = np.cumsum(sorted_weights)
        gini = (n + 1 - 2 * np.sum(cumsum) / cumsum[-1]) / n

        return gini

    def _assess_concentration_level(self, hhi: float) -> str:
        """Assess concentration level based on HHI."""

        if hhi < 0.15:
            return "Low Concentration"
        elif hhi < 0.25:
            return "Moderate Concentration"
        else:
            return "High Concentration"

    def generate_risk_report(self) -> None:
        """Generate comprehensive risk attribution report."""

        print("🎯 PORTFOLIO RISK ATTRIBUTION REPORT")
        print("=" * 60)

        # Risk contribution analysis
        risk_attribution = self.calculate_risk_contribution()

        print(f"\n📊 Risk Contribution by Position:")
        print(f"{'Instrument':<12} {'Weight':<8} {'Risk Contrib':<12} {'Marginal Risk':<14}")
        print("-" * 60)

        for instrument, metrics in risk_attribution.items():
            print(f"{instrument:<12} {metrics['weight']:>6.1f}% {metrics['risk_contribution_pct']:>10.1f}% "
                  f"{metrics['marginal_risk']:>12.3f}%")

        # Diversification analysis
        div_ratio = self.calculate_diversification_ratio()
        concentration_metrics = self.analyze_concentration_risk()

        print(f"\n🔗 Diversification Metrics:")
        print(f"   Diversification Ratio: {div_ratio:.3f}")
        print(f"   Effective Positions: {concentration_metrics['effective_positions']:.1f}")
        print(f"   HHI: {concentration_metrics['hhi']:.3f}")
        print(f"   Concentration Level: {concentration_metrics['concentration_level']}")
        print(f"   Max Position Weight: {concentration_metrics['max_weight']:.1f}%")
        print(f"   Gini Coefficient: {concentration_metrics['gini_coefficient']:.3f}")

        # Risk efficiency analysis
        total_risk_contribution = sum(attr['risk_contribution_pct'] for attr in risk_attribution.values())
        total_weight = sum(attr['weight'] for attr in risk_attribution.values())

        print(f"\n⚖️ Risk Efficiency:")
        print(f"   Total Weight: {total_weight:.1f}%")
        print(f"   Total Risk Contribution: {total_risk_contribution:.1f}%")

        # Identify risk outliers
        print(f"\n🚨 Risk Outliers:")
        for instrument, metrics in risk_attribution.items():
            weight_risk_ratio = metrics['risk_contribution_pct'] / metrics['weight'] if metrics['weight'] > 0 else 0

            if weight_risk_ratio > 1.5:
                print(f"   ⚠️ {instrument}: High risk per unit weight ({weight_risk_ratio:.2f}x)")
            elif weight_risk_ratio < 0.5:
                print(f"   ✅ {instrument}: Low risk per unit weight ({weight_risk_ratio:.2f}x)")

# Demo risk attribution
def demo_risk_attribution():
    """Demonstrate risk attribution analysis."""

    # Example portfolio weights
    portfolio_weights = {
        'EUR_USD': Decimal("0.3000"),
        'GBP_USD': Decimal("0.2500"),
        'USD_JPY': Decimal("0.2000"),
        'AUD_USD': Decimal("0.1500"),
        'USD_CHF': Decimal("0.1000")
    }

    print("💡 Risk attribution demo requires returns data from portfolio analyzer")
    print("Example portfolio weights:", portfolio_weights)

    return portfolio_weights
```

---

## 5. Performance Attribution

### Factor-Based Performance Analysis

```python
class PerformanceAttributor:
    """Analyze portfolio performance attribution."""

    def __init__(self, portfolio_returns: pd.Series, benchmark_returns: pd.Series = None):
        self.portfolio_returns = portfolio_returns
        self.benchmark_returns = benchmark_returns

    def calculate_performance_metrics(self) -> Dict:
        """Calculate comprehensive performance metrics."""

        returns = self.portfolio_returns.dropna()

        if len(returns) == 0:
            return {'error': 'No valid returns data'}

        # Basic metrics
        total_return = (1 + returns).prod() - 1
        annualized_return = (1 + returns.mean()) ** 252 - 1  # Assuming daily returns
        volatility = returns.std() * np.sqrt(252)  # Annualized

        # Risk metrics
        sharpe_ratio = annualized_return / volatility if volatility > 0 else 0

        # Drawdown analysis
        cumulative_returns = (1 + returns).cumprod()
        rolling_max = cumulative_returns.expanding().max()
        drawdown = (cumulative_returns - rolling_max) / rolling_max
        max_drawdown = drawdown.min()

        # VaR calculations
        var_95 = np.percentile(returns, 5)
        var_99 = np.percentile(returns, 1)

        # Tail statistics
        skewness = returns.skew()
        kurtosis = returns.kurtosis()

        # Win/Loss statistics
        positive_returns = returns[returns > 0]
        negative_returns = returns[returns < 0]

        win_rate = len(positive_returns) / len(returns) * 100
        avg_win = positive_returns.mean() if len(positive_returns) > 0 else 0
        avg_loss = negative_returns.mean() if len(negative_returns) > 0 else 0

        profit_factor = abs(avg_win * len(positive_returns) /
                           (avg_loss * len(negative_returns))) if len(negative_returns) > 0 else float('inf')

        metrics = {
            'total_return': total_return * 100,
            'annualized_return': annualized_return * 100,
            'volatility': volatility * 100,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': max_drawdown * 100,
            'var_95': var_95 * 100,
            'var_99': var_99 * 100,
            'skewness': skewness,
            'kurtosis': kurtosis,
            'win_rate': win_rate,
            'avg_win': avg_win * 100,
            'avg_loss': avg_loss * 100,
            'profit_factor': profit_factor,
            'num_observations': len(returns)
        }

        # Benchmark comparison if available
        if self.benchmark_returns is not None:
            benchmark_metrics = self._calculate_benchmark_metrics()
            metrics.update(benchmark_metrics)

        return metrics

    def _calculate_benchmark_metrics(self) -> Dict:
        """Calculate benchmark-relative metrics."""

        # Align returns
        aligned_data = pd.DataFrame({
            'portfolio': self.portfolio_returns,
            'benchmark': self.benchmark_returns
        }).dropna()

        if len(aligned_data) == 0:
            return {}

        portfolio_ret = aligned_data['portfolio']
        benchmark_ret = aligned_data['benchmark']

        # Tracking error
        active_returns = portfolio_ret - benchmark_ret
        tracking_error = active_returns.std() * np.sqrt(252)

        # Information ratio
        active_return = active_returns.mean() * 252
        information_ratio = active_return / tracking_error if tracking_error > 0 else 0

        # Beta calculation
        covariance = np.cov(portfolio_ret, benchmark_ret)[0, 1]
        benchmark_variance = np.var(benchmark_ret)
        beta = covariance / benchmark_variance if benchmark_variance > 0 else 0

        # Alpha (Jensen's alpha)
        portfolio_mean = portfolio_ret.mean() * 252
        benchmark_mean = benchmark_ret.mean() * 252
        alpha = portfolio_mean - beta * benchmark_mean

        # Up/Down capture ratios
        up_periods = benchmark_ret > 0
        down_periods = benchmark_ret < 0

        up_capture = (portfolio_ret[up_periods].mean() /
                     benchmark_ret[up_periods].mean()) if up_periods.sum() > 0 else 0

        down_capture = (portfolio_ret[down_periods].mean() /
                       benchmark_ret[down_periods].mean()) if down_periods.sum() > 0 else 0

        return {
            'tracking_error': tracking_error * 100,
            'information_ratio': information_ratio,
            'beta': beta,
            'alpha': alpha * 100,
            'up_capture': up_capture * 100,
            'down_capture': down_capture * 100,
            'correlation': np.corrcoef(portfolio_ret, benchmark_ret)[0, 1]
        }

    def plot_performance_analysis(self, figsize: Tuple[int, int] = (15, 10)):
        """Create comprehensive performance visualization."""

        returns = self.portfolio_returns.dropna()

        if len(returns) == 0:
            print("❌ No returns data for plotting")
            return

        fig, axes = plt.subplots(2, 2, figsize=figsize)

        # 1. Cumulative returns
        cumulative_returns = (1 + returns).cumprod()
        axes[0, 0].plot(cumulative_returns.index, cumulative_returns.values,
                       linewidth=2, label='Portfolio')

        if self.benchmark_returns is not None:
            benchmark_cum = (1 + self.benchmark_returns).cumprod()
            axes[0, 0].plot(benchmark_cum.index, benchmark_cum.values,
                           linewidth=2, alpha=0.7, label='Benchmark')

        axes[0, 0].set_title('Cumulative Returns', fontweight='bold')
        axes[0, 0].set_ylabel('Cumulative Return')
        axes[0, 0].legend()
        axes[0, 0].grid(True, alpha=0.3)

        # 2. Drawdown
        rolling_max = cumulative_returns.expanding().max()
        drawdown = (cumulative_returns - rolling_max) / rolling_max

        axes[0, 1].fill_between(drawdown.index, drawdown.values, 0,
                               alpha=0.7, color='red', label='Drawdown')
        axes[0, 1].set_title('Drawdown', fontweight='bold')
        axes[0, 1].set_ylabel('Drawdown (%)')
        axes[0, 1].grid(True, alpha=0.3)

        # 3. Returns distribution
        axes[1, 0].hist(returns * 100, bins=30, alpha=0.7, edgecolor='black')
        axes[1, 0].axvline(returns.mean() * 100, color='red', linestyle='--',
                          label=f'Mean: {returns.mean()*100:.3f}%')
        axes[1, 0].set_title('Returns Distribution', fontweight='bold')
        axes[1, 0].set_xlabel('Return (%)')
        axes[1, 0].set_ylabel('Frequency')
        axes[1, 0].legend()
        axes[1, 0].grid(True, alpha=0.3)

        # 4. Rolling Sharpe ratio
        rolling_sharpe = returns.rolling(window=60).mean() / returns.rolling(window=60).std()
        rolling_sharpe = rolling_sharpe * np.sqrt(252)  # Annualized

        axes[1, 1].plot(rolling_sharpe.index, rolling_sharpe.values, linewidth=2)
        axes[1, 1].axhline(y=1, color='red', linestyle='--', alpha=0.7, label='Sharpe = 1')
        axes[1, 1].set_title('Rolling Sharpe Ratio (60-period)', fontweight='bold')
        axes[1, 1].set_xlabel('Date')
        axes[1, 1].set_ylabel('Sharpe Ratio')
        axes[1, 1].legend()
        axes[1, 1].grid(True, alpha=0.3)

        plt.tight_layout()
        plt.show()

    def generate_performance_report(self) -> None:
        """Generate comprehensive performance report."""

        metrics = self.calculate_performance_metrics()

        if 'error' in metrics:
            print(f"❌ {metrics['error']}")
            return

        print("📈 PORTFOLIO PERFORMANCE REPORT")
        print("=" * 50)

        print(f"\n💰 Return Metrics:")
        print(f"   Total Return: {metrics['total_return']:+.2f}%")
        print(f"   Annualized Return: {metrics['annualized_return']:+.2f}%")
        print(f"   Volatility: {metrics['volatility']:.2f}%")
        print(f"   Sharpe Ratio: {metrics['sharpe_ratio']:.3f}")

        print(f"\n🛡️ Risk Metrics:")
        print(f"   Maximum Drawdown: {metrics['max_drawdown']:.2f}%")
        print(f"   95% VaR: {metrics['var_95']:.2f}%")
        print(f"   99% VaR: {metrics['var_99']:.2f}%")

        print(f"\n📊 Distribution Metrics:")
        print(f"   Skewness: {metrics['skewness']:.3f}")
        print(f"   Kurtosis: {metrics['kurtosis']:.3f}")

        print(f"\n🎯 Trading Metrics:")
        print(f"   Win Rate: {metrics['win_rate']:.1f}%")
        print(f"   Average Win: {metrics['avg_win']:.3f}%")
        print(f"   Average Loss: {metrics['avg_loss']:.3f}%")
        print(f"   Profit Factor: {metrics['profit_factor']:.2f}")

        # Benchmark metrics if available
        if 'tracking_error' in metrics:
            print(f"\n🎯 Benchmark Comparison:")
            print(f"   Alpha: {metrics['alpha']:+.2f}%")
            print(f"   Beta: {metrics['beta']:.3f}")
            print(f"   Tracking Error: {metrics['tracking_error']:.2f}%")
            print(f"   Information Ratio: {metrics['information_ratio']:.3f}")
            print(f"   Correlation: {metrics['correlation']:.3f}")
            print(f"   Up Capture: {metrics['up_capture']:.1f}%")
            print(f"   Down Capture: {metrics['down_capture']:.1f}%")

        print(f"\n📋 Data Quality:")
        print(f"   Observations: {metrics['num_observations']:,}")

# Demo performance attribution
def demo_performance_attribution():
    """Demonstrate performance attribution analysis."""

    # Generate sample portfolio returns
    np.random.seed(42)
    dates = pd.date_range('2023-01-01', periods=100, freq='D')
    portfolio_returns = pd.Series(np.random.normal(0.001, 0.02, 100), index=dates)
    benchmark_returns = pd.Series(np.random.normal(0.0005, 0.015, 100), index=dates)

    attributor = PerformanceAttributor(portfolio_returns, benchmark_returns)
    attributor.generate_performance_report()
    attributor.plot_performance_analysis()

    return attributor
```

---

## 6. Portfolio Rebalancing Strategies

### Dynamic Rebalancing Framework

```python
from decimal import Decimal

from fivetwenty import AsyncClient, Environment

class PortfolioRebalancer:
    """Dynamic portfolio rebalancing system."""

    def __init__(self, client: AsyncClient, account_id: str, target_weights: Dict[str, float]):
        self.client = client
        self.account_id = account_id
        self.target_weights = target_weights
        self.rebalance_threshold = Decimal("0.05")  # 5% deviation threshold
        self.min_trade_size = 100  # Minimum trade size

    async def get_current_positions(self) -> Dict[str, Dict]:
        """Get current portfolio positions."""

        try:
            positions = await self.client.positions.list_open(self.account_id)
            account = await self.client.accounts.get(self.account_id)

            current_positions = {}
            total_value = float(account.nav)

            for position in positions:
                instrument = position.instrument

                # Calculate net position
                long_units = int(position.long.units) if position.long.units != "0" else 0
                short_units = int(position.short.units) if position.short.units != "0" else 0
                net_units = long_units + short_units

                # Get current price for position value
                prices = await self.client.pricing.get(
                    account_id=self.account_id,
                    instruments=[instrument]
                )

                if prices and prices[0].asks and prices[0].bids:
                    if net_units >= 0:
                        current_price = float(prices[0].bids[0].price)
                    else:
                        current_price = float(prices[0].asks[0].price)

                    position_value = abs(net_units) * current_price
                    weight = position_value / total_value if total_value > 0 else 0

                    current_positions[instrument] = {
                        'units': net_units,
                        'value': position_value,
                        'weight': weight,
                        'current_price': current_price
                    }

            return current_positions

        except Exception as e:
            print(f"❌ Error getting positions: {e}")
            return {}

    async def calculate_rebalancing_trades(self) -> List[Dict]:
        """Calculate required trades for rebalancing."""

        current_positions = await self.get_current_positions()

        if not current_positions:
            print("❌ No current positions found")
            return []

        # Calculate total portfolio value
        total_value = sum(pos['value'] for pos in current_positions.values())

        rebalancing_trades = []

        for instrument, target_weight in self.target_weights.items():
            current_weight = current_positions.get(instrument, {}).get('weight', 0)
            weight_difference = target_weight - current_weight

            # Check if rebalancing is needed
            if abs(weight_difference) > self.rebalance_threshold:
                target_value = total_value * target_weight
                current_value = current_positions.get(instrument, {}).get('value', 0)

                value_difference = target_value - current_value

                # Get current price
                if instrument in current_positions:
                    current_price = current_positions[instrument]['current_price']
                else:
                    # Get price for new position
                    prices = await self.client.pricing.get(
                        account_id=self.account_id,
                        instruments=[instrument]
                    )
                    current_price = float(prices[0].asks[0].price) if prices else 0

                if current_price > 0:
                    units_to_trade = int(value_difference / current_price)

                    # Check minimum trade size
                    if abs(units_to_trade) >= self.min_trade_size:
                        rebalancing_trades.append({
                            'instrument': instrument,
                            'current_weight': current_weight,
                            'target_weight': target_weight,
                            'weight_difference': weight_difference,
                            'units_to_trade': units_to_trade,
                            'current_price': current_price,
                            'trade_value': abs(units_to_trade * current_price)
                        })

        return rebalancing_trades

    async def execute_rebalancing(self, dry_run: bool = True) -> List[Dict]:
        """Execute rebalancing trades."""

        trades = await self.calculate_rebalancing_trades()

        if not trades:
            print("✅ Portfolio is already balanced")
            return []

        print(f"🔄 Rebalancing Analysis ({'DRY RUN' if dry_run else 'LIVE EXECUTION'}):")
        print("=" * 60)

        executed_trades = []

        for trade in trades:
            print(f"\n📊 {trade['instrument']}:")
            print(f"   Current Weight: {trade['current_weight']*100:.1f}%")
            print(f"   Target Weight: {trade['target_weight']*100:.1f}%")
            print(f"   Deviation: {trade['weight_difference']*100:+.1f}%")
            print(f"   Required Trade: {trade['units_to_trade']:+,} units")
            print(f"   Trade Value: ${trade['trade_value']:,.2f}")

            if not dry_run:
                try:
                    # Execute the trade
                    response = await self.client.orders.post_market_order(
                        account_id=self.account_id,
                        instrument=trade['instrument'],
                        units=trade['units_to_trade']
                    )

                    if response.order_fill_transaction:
                        fill = response.order_fill_transaction
                        executed_trades.append({
                            'instrument': trade['instrument'],
                            'units': trade['units_to_trade'],
                            'fill_price': float(fill.price),
                            'trade_id': fill.trade_opened.trade_id if fill.trade_opened else None,
                            'status': 'FILLED'
                        })
                        print(f"   ✅ Executed at {fill.price}")
                    else:
                        executed_trades.append({
                            'instrument': trade['instrument'],
                            'units': trade['units_to_trade'],
                            'status': 'FAILED'
                        })
                        print(f"   ❌ Execution failed")

                except Exception as e:
                    print(f"   ❌ Error: {e}")
                    executed_trades.append({
                        'instrument': trade['instrument'],
                        'units': trade['units_to_trade'],
                        'status': 'ERROR',
                        'error': str(e)
                    })

        if dry_run:
            print(f"\n💡 This was a dry run. Set dry_run=False to execute trades.")
        else:
            successful_trades = len([t for t in executed_trades if t['status'] == 'FILLED'])
            print(f"\n📊 Rebalancing Summary:")
            print(f"   Total Trades: {len(executed_trades)}")
            print(f"   Successful: {successful_trades}")
            print(f"   Failed: {len(executed_trades) - successful_trades}")

        return executed_trades

    def set_rebalancing_parameters(self, threshold: float = None, min_trade_size: int = None):
        """Update rebalancing parameters."""

        if threshold is not None:
            self.rebalance_threshold = threshold
            print(f"📊 Rebalance threshold set to {threshold*100:.1f}%")

        if min_trade_size is not None:
            self.min_trade_size = min_trade_size
            print(f"📊 Minimum trade size set to {min_trade_size:,} units")

# Demo rebalancing
async def demo_portfolio_rebalancing(account_id: str):
    """Demonstrate portfolio rebalancing."""

    if not account_id:
        print("❌ No account ID")
        return

    # Example target allocation
    target_weights = {
        'EUR_USD': Decimal("0.4000"),
        'GBP_USD': Decimal("0.3000"),
        'USD_JPY': Decimal("0.2000"),
        'AUD_USD': Decimal("0.1000")
    }

    async with AsyncClient(token=TOKEN, environment=ENVIRONMENT) as client:
        rebalancer = PortfolioRebalancer(client, account_id, target_weights)

        print("🎯 Target Portfolio Allocation:")
        for instrument, weight in target_weights.items():
            print(f"   {instrument}: {weight*100:.1f}%")

        # Analyze current positions
        current_positions = await rebalancer.get_current_positions()

        if current_positions:
            print(f"\n📊 Current Portfolio:")
            for instrument, position in current_positions.items():
                print(f"   {instrument}: {position['weight']*100:.1f}% "
                      f"({position['units']:,} units)")

        # Calculate rebalancing needs (dry run)
        executed_trades = await rebalancer.execute_rebalancing(dry_run=True)

        return rebalancer
```

---

## 7. Summary and Best Practices

### Portfolio Management Checklist

```python
class PortfolioManagementFramework:
    """Comprehensive portfolio management framework."""

    @staticmethod
    def evaluate_portfolio_health(analyzer: PortfolioAnalyzer,
                                 portfolio_weights: Dict[str, float]) -> Dict:
        """Evaluate overall portfolio health."""

        health_score = 0
        max_score = 100
        recommendations = []

        # 1. Diversification (25 points)
        if analyzer.correlation_matrix is not None:
            avg_correlation = analyzer.correlation_matrix.values[
                np.triu_indices_from(analyzer.correlation_matrix.values, k=1)
            ].mean()

            if avg_correlation < 0.3:
                health_score += 25
            elif avg_correlation < 0.5:
                health_score += 15
                recommendations.append("Consider reducing correlation between positions")
            elif avg_correlation < 0.7:
                health_score += 10
                recommendations.append("High correlation - diversification needed")
            else:
                recommendations.append("CRITICAL: Very high correlation - major diversification issues")

        # 2. Risk concentration (25 points)
        max_weight = max(portfolio_weights.values()) if portfolio_weights else 1.0

        if max_weight < 0.25:
            health_score += 25
        elif max_weight < 0.40:
            health_score += 15
            recommendations.append("Consider reducing largest position size")
        elif max_weight < 0.60:
            health_score += 10
            recommendations.append("High concentration risk in largest position")
        else:
            recommendations.append("CRITICAL: Excessive concentration in single position")

        # 3. Number of positions (20 points)
        num_positions = len([w for w in portfolio_weights.values() if w > 0.01]) if portfolio_weights else 0

        if 5 <= num_positions <= 15:
            health_score += 20
        elif 3 <= num_positions <= 20:
            health_score += 15
        elif num_positions > 0:
            health_score += 10
            if num_positions < 3:
                recommendations.append("Consider adding more positions for diversification")
            else:
                recommendations.append("Consider reducing number of positions for better management")

        # 4. Risk-adjusted returns (15 points)
        stats = analyzer.analyze_portfolio_statistics()
        if 'PORTFOLIO' in stats:
            sharpe = stats['PORTFOLIO']['sharpe_ratio']
            if sharpe > 1.5:
                health_score += 15
            elif sharpe > 1.0:
                health_score += 10
            elif sharpe > 0.5:
                health_score += 5
                recommendations.append("Work on improving risk-adjusted returns")
            else:
                recommendations.append("Poor risk-adjusted returns - review strategy")

        # 5. Volatility management (15 points)
        if 'PORTFOLIO' in stats:
            volatility = stats['PORTFOLIO']['volatility']
            if volatility < 15:
                health_score += 15
            elif volatility < 25:
                health_score += 10
            elif volatility < 35:
                health_score += 5
                recommendations.append("Consider reducing portfolio volatility")
            else:
                recommendations.append("High volatility - implement better risk controls")

        # Health assessment
        if health_score >= 80:
            health_level = "EXCELLENT"
        elif health_score >= 60:
            health_level = "GOOD"
        elif health_score >= 40:
            health_level = "FAIR"
        elif health_score >= 20:
            health_level = "POOR"
        else:
            health_level = "CRITICAL"

        return {
            'health_score': health_score,
            'max_score': max_score,
            'health_level': health_level,
            'recommendations': recommendations
        }

    @staticmethod
    def print_portfolio_health_report(health_assessment: Dict):
        """Print formatted portfolio health report."""

        print("🏥 PORTFOLIO HEALTH ASSESSMENT")
        print("=" * 50)

        score = health_assessment['health_score']
        max_score = health_assessment['max_score']
        level = health_assessment['health_level']

        print(f"\n🎯 Overall Health Score: {score}/{max_score} ({score/max_score*100:.1f}%)")
        print(f"📊 Health Level: {level}")

        # Health level emoji
        emoji_map = {
            'EXCELLENT': '🟢',
            'GOOD': '🟡',
            'FAIR': '🟠',
            'POOR': '🔴',
            'CRITICAL': '🚨'
        }

        print(f"{emoji_map.get(level, '❓')} Status: {level}")

        if health_assessment['recommendations']:
            print(f"\n💡 Recommendations:")
            for i, rec in enumerate(health_assessment['recommendations'], 1):
                print(f"   {i}. {rec}")
        else:
            print(f"\n✅ No specific recommendations - portfolio looks healthy!")

# Portfolio management best practices
def print_portfolio_best_practices():
    """Print portfolio management best practices."""

    print("📚 PORTFOLIO MANAGEMENT BEST PRACTICES")
    print("=" * 50)

    practices = [
        "🎯 Define clear investment objectives and risk tolerance",
        "📊 Maintain diversification across uncorrelated instruments",
        "⚖️ Use position sizing based on risk contribution",
        "🔄 Rebalance regularly to maintain target allocations",
        "📈 Monitor correlation changes over time",
        "🛡️ Implement stop-losses and risk controls",
        "📋 Track performance attribution and risk metrics",
        "🔍 Review and adjust strategy based on market conditions",
        "💰 Never risk more than you can afford to lose",
        "📚 Continuously educate yourself on market dynamics"
    ]

    for practice in practices:
        print(f"   {practice}")

    print(f"\n🎓 Key Metrics to Monitor:")
    print(f"   • Sharpe Ratio (target: > 1.0)")
    print(f"   • Maximum Drawdown (target: < 15%)")
    print(f"   • Portfolio Correlation (target: < 0.5)")
    print(f"   • Position Concentration (max position: < 25%)")
    print(f"   • Risk-Adjusted Returns (alpha > 0)")
```

---

## Summary

You've mastered comprehensive portfolio analysis and optimization:

- ✅ **Data Collection**: Historical price and returns analysis
- ✅ **Correlation Analysis**: Identifying relationships and clusters
- ✅ **Portfolio Optimization**: Modern Portfolio Theory implementation
- ✅ **Risk Attribution**: Understanding risk sources and concentration
- ✅ **Performance Analysis**: Comprehensive return and risk metrics
- ✅ **Rebalancing**: Dynamic portfolio management strategies
- ✅ **Health Assessment**: Portfolio evaluation framework

### Next Steps

Continue your learning:

- **[Streaming Data](streaming-data.md)** - Real-time portfolio monitoring
- **[Data Analysis](examples/notebooks/data-analysis.ipynb)** - Historical strategy validation
- **[Advanced Orders](advanced-orders.md)** - Sophisticated execution
- **[Risk Management](risk-management.md)** - Advanced risk controls

### Key Takeaways

1. **Diversification is your best friend** - Reduce risk through uncorrelated assets
2. **Correlation changes over time** - Monitor relationships continuously
3. **Risk contribution ≠ position weight** - Understand true risk sources
4. **Rebalancing is essential** - Maintain target allocations
5. **Performance attribution reveals insights** - Understand return sources

**Remember: Portfolio management is an ongoing process, not a one-time event.** 📊