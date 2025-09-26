# Performance Attribution

Analyze what drives portfolio performance through factor-based attribution and benchmark comparison.

---

## Prerequisites

- Completed risk attribution tutorial
- Understanding of performance metrics
- Access to benchmark and factor data

---

## Learning Objectives

- ✅ Implement factor-based performance attribution
- ✅ Calculate alpha and beta decomposition
- ✅ Analyze performance drivers
- ✅ Compare against benchmarks

---

## Performance Attribution Framework

```python
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple
import matplotlib.pyplot as plt


class PerformanceAttributionAnalyzer:
    """Advanced performance attribution analysis."""

    def __init__(self, portfolio_returns: pd.Series, benchmark_returns: pd.Series, factor_returns: Dict[str, pd.Series]: Any = None) -> None:
        self.portfolio_returns = portfolio_returns
        self.benchmark_returns = benchmark_returns
        self.factor_returns = pd.DataFrame(factor_returns) if factor_returns else None

        # Align all data
        self._align_data()

    def _align_data(self) -> Any:
        """Align all return series to common dates."""
        common_index = self.portfolio_returns.index.intersection(self.benchmark_returns.index)

        if self.factor_returns is not None:
            common_index = common_index.intersection(self.factor_returns.index)

        self.portfolio_returns = self.portfolio_returns.loc[common_index]
        self.benchmark_returns = self.benchmark_returns.loc[common_index]

        if self.factor_returns is not None:
            self.factor_returns = self.factor_returns.loc[common_index]

    def calculate_performance_metrics(self) -> Dict:
        """Calculate comprehensive performance metrics."""

        # Excess returns
        excess_returns = self.portfolio_returns - self.benchmark_returns

        # Performance metrics
        metrics = {
            'total_return': (1 + self.portfolio_returns).prod() - 1,
            'benchmark_return': (1 + self.benchmark_returns).prod() - 1,
            'excess_return': (1 + excess_returns).prod() - 1,
            'annualized_return': self.portfolio_returns.mean() * 252,
            'annualized_benchmark': self.benchmark_returns.mean() * 252,
            'annualized_excess': excess_returns.mean() * 252,
            'volatility': self.portfolio_returns.std() * np.sqrt(252),
            'benchmark_volatility': self.benchmark_returns.std() * np.sqrt(252),
            'tracking_error': excess_returns.std() * np.sqrt(252),
            'information_ratio': (excess_returns.mean() / excess_returns.std()) * np.sqrt(252) if excess_returns.std() > 0 else 0,
            'sharpe_ratio': (self.portfolio_returns.mean() / self.portfolio_returns.std()) * np.sqrt(252) if self.portfolio_returns.std() > 0 else 0,
            'max_drawdown': self._calculate_max_drawdown(),
            'hit_rate': (excess_returns > 0).mean(),
            'up_capture': self._calculate_capture_ratio(up=True),
            'down_capture': self._calculate_capture_ratio(up=False)
        }

        return metrics

    def factor_attribution(self) -> Dict:
        """Perform factor-based performance attribution."""

        if self.factor_returns is None:
            return {'error': 'No factor data available'}

        # Prepare data
        y = self.portfolio_returns.values
        X = np.column_stack([np.ones(len(self.factor_returns)), self.factor_returns.values])

        # Multiple regression
        coefficients, residuals, rank, s = np.linalg.lstsq(X, y, rcond=None)

        alpha = coefficients[0]
        betas = dict(zip(self.factor_returns.columns, coefficients[1:]))

        # Factor contributions to return
        factor_contributions = {}
        for i, factor in enumerate(self.factor_returns.columns):
            factor_return = self.factor_returns[factor].mean() * 252  # Annualized
            beta = betas[factor]
            factor_contributions[factor] = beta * factor_return

        # R-squared
        ss_res = np.sum(residuals) if len(residuals) > 0 else np.sum((y - X @ coefficients) ** 2)
        ss_tot = np.sum((y - np.mean(y)) ** 2)
        r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0

        return {
            'alpha': alpha * 252,  # Annualized
            'betas': betas,
            'factor_contributions': factor_contributions,
            'r_squared': r_squared,
            'explained_return': sum(factor_contributions.values()),
            'unexplained_return': alpha * 252
        }

    def rolling_attribution(self, window_days: int = 252) -> pd.DataFrame:
        """Calculate rolling performance attribution."""

        if len(self.portfolio_returns) < window_days:
            return pd.DataFrame()

        rolling_metrics = []

        for i in range(window_days, len(self.portfolio_returns)):
            # Window data
            window_portfolio = self.portfolio_returns.iloc[i-window_days:i]
            window_benchmark = self.benchmark_returns.iloc[i-window_days:i]

            # Calculate metrics for window
            excess_returns = window_portfolio - window_benchmark

            metrics = {
                'date': self.portfolio_returns.index[i],
                'return': window_portfolio.mean() * 252,
                'benchmark': window_benchmark.mean() * 252,
                'excess': excess_returns.mean() * 252,
                'volatility': window_portfolio.std() * np.sqrt(252),
                'tracking_error': excess_returns.std() * np.sqrt(252),
                'information_ratio': (excess_returns.mean() / excess_returns.std()) * np.sqrt(252) if excess_returns.std() > 0 else 0,
                'beta': self._calculate_beta(window_portfolio, window_benchmark)
            }

            rolling_metrics.append(metrics)

        return pd.DataFrame(rolling_metrics).set_index('date')

    def _calculate_max_drawdown(self) -> float:
        """Calculate maximum drawdown."""
        cumulative = (1 + self.portfolio_returns).cumprod()
        running_max = cumulative.expanding().max()
        drawdown = (cumulative / running_max) - 1
        return drawdown.min()

    def _calculate_capture_ratio(self, up: bool = True) -> float:
        """Calculate up/down capture ratio."""
        if up:
            mask = self.benchmark_returns > 0
        else:
            mask = self.benchmark_returns < 0

        if not mask.any():
            return 0

        portfolio_avg = self.portfolio_returns[mask].mean()
        benchmark_avg = self.benchmark_returns[mask].mean()

        return portfolio_avg / benchmark_avg if benchmark_avg != 0 else 0

    def _calculate_beta(self, portfolio_returns: pd.Series, benchmark_returns: pd.Series) -> float:
        """Calculate beta coefficient."""
        covariance = np.cov(portfolio_returns, benchmark_returns)[0, 1]
        benchmark_variance = np.var(benchmark_returns)
        return covariance / benchmark_variance if benchmark_variance > 0 else 0

    def plot_performance_attribution(self) -> Any:
        """Plot performance attribution analysis."""

        fig, axes = plt.subplots(2, 2, figsize=(15, 12))

        # Cumulative returns
        cumulative_portfolio = (1 + self.portfolio_returns).cumprod()
        cumulative_benchmark = (1 + self.benchmark_returns).cumprod()

        axes[0, 0].plot(cumulative_portfolio.index, cumulative_portfolio, label='Portfolio', linewidth=2)
        axes[0, 0].plot(cumulative_benchmark.index, cumulative_benchmark, label='Benchmark', linewidth=2)
        axes[0, 0].set_title('Cumulative Returns')
        axes[0, 0].legend()
        axes[0, 0].grid(True, alpha=0.3)

        # Excess returns
        excess_returns = self.portfolio_returns - self.benchmark_returns
        cumulative_excess = (1 + excess_returns).cumprod()

        axes[0, 1].plot(cumulative_excess.index, cumulative_excess, label='Excess Return', color='green', linewidth=2)
        axes[0, 1].axhline(y=1, color='black', linestyle='--', alpha=0.5)
        axes[0, 1].set_title('Cumulative Excess Returns')
        axes[0, 1].legend()
        axes[0, 1].grid(True, alpha=0.3)

        # Rolling Sharpe ratio
        rolling_sharpe = self.portfolio_returns.rolling(252).mean() / self.portfolio_returns.rolling(252).std() * np.sqrt(252)
        benchmark_sharpe = self.benchmark_returns.rolling(252).mean() / self.benchmark_returns.rolling(252).std() * np.sqrt(252)

        axes[1, 0].plot(rolling_sharpe.index, rolling_sharpe, label='Portfolio Sharpe', linewidth=2)
        axes[1, 0].plot(benchmark_sharpe.index, benchmark_sharpe, label='Benchmark Sharpe', linewidth=2)
        axes[1, 0].set_title('Rolling Sharpe Ratio (1Y)')
        axes[1, 0].legend()
        axes[1, 0].grid(True, alpha=0.3)

        # Drawdown
        cumulative = (1 + self.portfolio_returns).cumprod()
        running_max = cumulative.expanding().max()
        drawdown = (cumulative / running_max) - 1

        axes[1, 1].fill_between(drawdown.index, drawdown, 0, alpha=0.3, color='red')
        axes[1, 1].plot(drawdown.index, drawdown, color='red', linewidth=1)
        axes[1, 1].set_title('Portfolio Drawdown')
        axes[1, 1].grid(True, alpha=0.3)

        plt.tight_layout()
        plt.show()

# Benchmark Construction
class BenchmarkConstructor:
    """Construct custom benchmarks for attribution analysis."""

    def __init__(self, instrument_returns: Dict[str, pd.Series]: Any) -> None:
        self.instrument_returns = pd.DataFrame(instrument_returns).dropna()

    def equal_weight_benchmark(self) -> pd.Series:
        """Create equal-weighted benchmark."""
        weights = {inst: 1/len(self.instrument_returns.columns) for inst in self.instrument_returns.columns}
        return self._calculate_weighted_return(weights)

    def market_cap_benchmark(self, market_caps: Dict[str, float]) -> pd.Series:
        """Create market-cap weighted benchmark."""
        total_cap = sum(market_caps.values())
        weights = {inst: cap/total_cap for inst, cap in market_caps.items()}
        return self._calculate_weighted_return(weights)

    def _calculate_weighted_return(self, weights: Dict[str, float]) -> pd.Series:
        """Calculate weighted portfolio return."""
        benchmark_returns = pd.Series(0, index=self.instrument_returns.index)

        for instrument, weight in weights.items():
            if instrument in self.instrument_returns.columns:
                benchmark_returns += self.instrument_returns[instrument] * weight

        return benchmark_returns

# Example usage
def performance_attribution_example():
    """Demonstrate performance attribution analysis."""

    print("Performance Attribution Analysis:")
    print("1. Calculate performance metrics")
    print("2. Factor-based attribution")
    print("3. Rolling performance analysis")
    print("4. Benchmark comparison")
    print("5. Attribution visualization")

    # analyzer = PerformanceAttributionAnalyzer(portfolio_returns, benchmark_returns, factor_returns)
    # metrics = analyzer.calculate_performance_metrics()
    # attribution = analyzer.factor_attribution()

    return "Performance attribution framework ready"

# Run example
# result = performance_attribution_example()
```

## Key Attribution Methods

### 1. Factor-Based Attribution
- **Factor Exposures**: Portfolio sensitivity to systematic factors
- **Factor Contributions**: Return explained by each factor
- **Alpha Generation**: Unexplained return (skill)

### 2. Style Attribution
- **Value vs Growth**: Value and growth factor exposures
- **Size**: Large-cap vs small-cap bias
- **Momentum**: Trend-following characteristics

### 3. Sector Attribution
- **Sector Allocation**: Return from sector weights
- **Security Selection**: Return from instrument choice within sectors
- **Interaction Effect**: Combined allocation and selection effects

---

## Next Steps

Continue to [Portfolio Rebalancing](portfolio-rebalancing.md) to implement dynamic portfolio management.

---

## Related Tutorials

- [Risk Attribution](risk-attribution.md) - Risk analysis
- [Portfolio Rebalancing](portfolio-rebalancing.md) - Dynamic management
- [Best Practices](best-practices.md) - Implementation guidance