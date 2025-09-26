# Portfolio Optimization

Apply Modern Portfolio Theory optimization techniques to find optimal asset allocations that maximize return for given risk levels.

---

## Prerequisites

- Completed [Portfolio Theory](portfolio-theory.md) and [Data Collection](data-collection.md)
- Understanding of mathematical optimization
- Python with scipy, numpy, and optimization libraries

---

## Learning Objectives

- ✅ Implement mean-variance optimization
- ✅ Build efficient frontier calculations
- ✅ Apply portfolio constraints
- ✅ Create risk budgeting strategies

---

## Portfolio Optimization Framework

```python
from scipy.optimize import minimize
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from typing import Dict, List, Tuple, Optional
import warnings

"""Comprehensive module for trading operations."""
warnings.filterwarnings('ignore')

class PortfolioOptimizer:
    """Portfolio optimization using Modern Portfolio Theory."""

    def __init__(self, returns_data: Dict[str, pd.Series]: Any) -> None:
        self.returns_data = returns_data
        self.instruments = list(returns_data.keys())
        self.returns_df = pd.DataFrame(returns_data).dropna()
        self.mean_returns = self.returns_df.mean()
        self.cov_matrix = self.returns_df.cov()
        self.num_assets = len(self.instruments)

    def portfolio_performance(self, weights: np.ndarray) -> Tuple[float, float, float]:
        """Calculate portfolio performance metrics."""

        # Portfolio return
        portfolio_return = np.sum(self.mean_returns * weights) * 252  # Annualized

        # Portfolio volatility
        portfolio_variance = np.dot(weights.T, np.dot(self.cov_matrix, weights))
        portfolio_volatility = np.sqrt(portfolio_variance) * np.sqrt(252)  # Annualized

        # Sharpe ratio (assuming 0% risk-free rate)
        sharpe_ratio = portfolio_return / portfolio_volatility if portfolio_volatility > 0 else 0

        return portfolio_return, portfolio_volatility, sharpe_ratio

    def optimize_portfolio(self, target_return: Optional[float] = None,
                          target_risk: Optional[float] = None) -> Dict:
        """Optimize portfolio for maximum Sharpe ratio or target return/risk."""

        # Constraints: weights sum to 1
        constraints = ({'type': 'eq', 'fun': lambda x: np.sum(x) - 1})

        # Bounds: each weight between 0 and 1 (long-only)
        bounds = tuple((0, 1) for _ in range(self.num_assets))

        # Initial guess: equal weights
        initial_guess = np.array([1/self.num_assets] * self.num_assets)

        if target_return is not None:
            # Minimize risk for target return
            constraints = [
                {'type': 'eq', 'fun': lambda x: np.sum(x) - 1},
                {'type': 'eq', 'fun': lambda x: self.portfolio_performance(x)[0] - target_return}
            ]

            result = minimize(
                fun=lambda x: self.portfolio_performance(x)[1],  # Minimize volatility
                x0=initial_guess,
                method='SLSQP',
                bounds=bounds,
                constraints=constraints
            )

        elif target_risk is not None:
            # Maximize return for target risk
            constraints = [
                {'type': 'eq', 'fun': lambda x: np.sum(x) - 1},
                {'type': 'eq', 'fun': lambda x: self.portfolio_performance(x)[1] - target_risk}
            ]

            result = minimize(
                fun=lambda x: -self.portfolio_performance(x)[0],  # Maximize return (minimize negative)
                x0=initial_guess,
                method='SLSQP',
                bounds=bounds,
                constraints=constraints
            )

        else:
            # Maximize Sharpe ratio
            result = minimize(
                fun=lambda x: -self.portfolio_performance(x)[2],  # Maximize Sharpe (minimize negative)
                x0=initial_guess,
                method='SLSQP',
                bounds=bounds,
                constraints=constraints
            )

        if result.success:
            optimal_weights = result.x
            portfolio_return, portfolio_volatility, sharpe_ratio = self.portfolio_performance(optimal_weights)

            return {
                'weights': dict(zip(self.instruments, optimal_weights)),
                'expected_return': portfolio_return,
                'volatility': portfolio_volatility,
                'sharpe_ratio': sharpe_ratio,
                'optimization_success': True
            }
        else:
            return {'optimization_success': False, 'message': 'Optimization failed'}

    def efficient_frontier(self, num_portfolios: int = 100) -> pd.DataFrame:
        """Generate efficient frontier points."""

        # Define target returns range
        min_return = self.mean_returns.min() * 252
        max_return = self.mean_returns.max() * 252
        target_returns = np.linspace(min_return, max_return, num_portfolios)

        efficient_portfolios = []

        for target_return in target_returns:
            try:
                result = self.optimize_portfolio(target_return=target_return)
                if result['optimization_success']:
                    efficient_portfolios.append({
                        'return': result['expected_return'],
                        'volatility': result['volatility'],
                        'sharpe_ratio': result['sharpe_ratio'],
                        'weights': result['weights']
                    })
            except:
                continue

        return pd.DataFrame(efficient_portfolios)

    def plot_efficient_frontier(self, num_portfolios: int = 100) -> Any:
        """Plot the efficient frontier."""

        # Generate efficient frontier
        frontier_df = self.efficient_frontier(num_portfolios)

        if frontier_df.empty:
            print("Could not generate efficient frontier")
            return

        # Individual asset returns and volatilities
        individual_returns = self.mean_returns * 252
        individual_volatilities = np.sqrt(np.diag(self.cov_matrix)) * np.sqrt(252)

        # Plot
        plt.figure(figsize=(12, 8))

        # Plot efficient frontier
        plt.plot(frontier_df['volatility'], frontier_df['return'],
                'b-', linewidth=2, label='Efficient Frontier')

        # Plot individual assets
        plt.scatter(individual_volatilities, individual_returns,
                   marker='o', s=100, alpha=0.7, label='Individual Assets')

        # Add asset labels
        for i, instrument in enumerate(self.instruments):
            plt.annotate(instrument,
                        (individual_volatilities[i], individual_returns[i]),
                        xytext=(5, 5), textcoords='offset points', fontsize=9)

        # Highlight maximum Sharpe ratio portfolio
        max_sharpe_idx = frontier_df['sharpe_ratio'].idxmax()
        if not pd.isna(max_sharpe_idx):
            max_sharpe_portfolio = frontier_df.loc[max_sharpe_idx]
            plt.scatter(max_sharpe_portfolio['volatility'], max_sharpe_portfolio['return'],
                       marker='*', s=500, color='red', label='Max Sharpe Ratio')

        plt.xlabel('Volatility (Standard Deviation)')
        plt.ylabel('Expected Return')
        plt.title('Efficient Frontier')
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.show()

        return frontier_df

# Risk Budgeting Implementation
class RiskBudgetOptimizer:
    """Optimize portfolio using risk budgeting approach."""

    def __init__(self, returns_data: Dict[str, pd.Series]: Any) -> None:
        self.returns_data = returns_data
        self.returns_df = pd.DataFrame(returns_data).dropna()
        self.cov_matrix = self.returns_df.cov()
        self.instruments = list(returns_data.keys())

    def risk_contribution(self, weights: np.ndarray) -> np.ndarray:
        """Calculate risk contribution of each asset."""

        portfolio_variance = np.dot(weights.T, np.dot(self.cov_matrix, weights))
        marginal_contrib = np.dot(self.cov_matrix, weights)
        risk_contrib = weights * marginal_contrib / portfolio_variance

        return risk_contrib

    def optimize_risk_parity(self) -> Dict:
        """Optimize for equal risk contribution (risk parity)."""

        def risk_parity_objective(weights: Any) -> Any:
            """Objective function for risk parity optimization."""
            risk_contrib = self.risk_contribution(weights)
            target_contrib = 1 / len(weights)  # Equal contribution
            return np.sum((risk_contrib - target_contrib) ** 2)

        # Constraints and bounds
        constraints = {'type': 'eq', 'fun': lambda x: np.sum(x) - 1}
        bounds = tuple((0.01, 0.99) for _ in range(len(self.instruments)))
        initial_guess = np.array([1/len(self.instruments)] * len(self.instruments))

        result = minimize(
            fun=risk_parity_objective,
            x0=initial_guess,
            method='SLSQP',
            bounds=bounds,
            constraints=constraints
        )

        if result.success:
            optimal_weights = result.x
            risk_contrib = self.risk_contribution(optimal_weights)

            return {
                'weights': dict(zip(self.instruments, optimal_weights)),
                'risk_contributions': dict(zip(self.instruments, risk_contrib)),
                'optimization_success': True
            }
        else:
            return {'optimization_success': False}

# Example usage
async def portfolio_optimization_example():
    """Demonstrate portfolio optimization techniques."""

    # This would use the PortfolioAnalyzer from data-collection.md
    # analyzer = PortfolioAnalyzer(client, account_id)
    # returns_data = analyzer.returns_data

    # For demonstration, create sample data
    instruments = ["EUR_USD", "GBP_USD", "USD_JPY", "AUD_USD"]

    # Sample returns data would come from actual analysis
    # returns_data = {...}  # From PortfolioAnalyzer

    print("Portfolio optimization techniques:")
    print("1. Mean-variance optimization")
    print("2. Efficient frontier generation")
    print("3. Risk parity optimization")
    print("4. Constrained optimization")

    # optimizer = PortfolioOptimizer(returns_data)
    # frontier = optimizer.plot_efficient_frontier()
    # risk_parity = RiskBudgetOptimizer(returns_data).optimize_risk_parity()

    return "Optimization framework ready"

# Run example
# result = await portfolio_optimization_example()
```

## Optimization Strategies

### 1. Mean-Variance Optimization
- **Maximum Sharpe Ratio**: Best risk-adjusted returns
- **Target Return**: Minimize risk for desired return
- **Target Risk**: Maximize return for acceptable risk

### 2. Risk Budgeting
- **Equal Risk Contribution**: Each asset contributes equally to portfolio risk
- **Custom Risk Budgets**: Allocate specific risk amounts to each asset
- **Factor-Based Budgeting**: Budget risk by risk factors

### 3. Constraint Optimization
- **Long-only constraints**: No short selling
- **Position limits**: Maximum/minimum allocations
- **Sector constraints**: Diversification requirements

## Advanced Optimization

### Black-Litterman Model
```python

"""Module docstring."""

from typing import Any
def black_litterman_optimization(returns_data, market_caps, tau=0.05) -> Any:
    """Implement Black-Litterman portfolio optimization."""

    # Prior (market equilibrium) expected returns
    # Investor views and confidence
    # Posterior expected returns
    # Optimization with Bayesian updating

    pass  # Implementation details
```

### Dynamic Optimization
```python

"""Module docstring."""

from typing import Any
def dynamic_portfolio_optimization(returns_data, rebalance_frequency="monthly") -> Any:
    """Implement dynamic portfolio optimization with rebalancing."""

    # Time-varying optimization
    # Rolling window estimation
    # Transaction cost consideration
    # Performance monitoring

    pass  # Implementation details
```

---

## Next Steps

Proceed to [Risk Attribution](risk-attribution.md) to analyze the sources of portfolio risk in your optimized portfolios.

---

## Related Tutorials

- [Data Collection](data-collection.md) - Data infrastructure
- [Risk Attribution](risk-attribution.md) - Risk analysis
- [Portfolio Rebalancing](portfolio-rebalancing.md) - Dynamic management