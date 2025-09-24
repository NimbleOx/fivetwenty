# Risk Attribution & Decomposition

Understand and decompose portfolio risk sources using advanced statistical techniques and factor analysis.

---

## Prerequisites

- Completed previous portfolio tutorials
- Understanding of risk metrics and factor models
- Python with statistical libraries

---

## Learning Objectives

- ✅ Decompose portfolio risk by instrument and factor
- ✅ Calculate Value at Risk (VaR) and Component VaR
- ✅ Implement risk factor analysis
- ✅ Build risk monitoring systems

---

## Risk Attribution Framework

```python
import numpy as np
import pandas as pd
from scipy import stats
from typing import Dict, List, Tuple
import matplotlib.pyplot as plt

class RiskAttributionAnalyzer:
    """Advanced risk attribution and decomposition analysis."""

    def __init__(self, returns_data: Dict[str, pd.Series], portfolio_weights: Dict[str, float]):
        self.returns_data = returns_data
        self.returns_df = pd.DataFrame(returns_data).dropna()
        self.portfolio_weights = portfolio_weights
        self.instruments = list(returns_data.keys())

    def calculate_component_var(self, confidence_level: float = 0.05) -> Dict:
        """Calculate Component Value at Risk for each instrument."""

        # Portfolio returns
        portfolio_returns = self._calculate_portfolio_returns()

        # Portfolio VaR
        portfolio_var = np.percentile(portfolio_returns, confidence_level * 100)

        # Component VaR calculation
        component_vars = {}

        for instrument in self.instruments:
            if instrument in self.portfolio_weights:
                weight = self.portfolio_weights[instrument]

                # Calculate marginal VaR using finite differences
                perturbed_weights = self.portfolio_weights.copy()
                perturbed_weights[instrument] += 0.001  # Small perturbation

                # Normalize weights
                total_weight = sum(perturbed_weights.values())
                perturbed_weights = {k: v/total_weight for k, v in perturbed_weights.items()}

                # Calculate perturbed portfolio returns
                perturbed_returns = self._calculate_portfolio_returns(perturbed_weights)
                perturbed_var = np.percentile(perturbed_returns, confidence_level * 100)

                # Marginal VaR
                marginal_var = (perturbed_var - portfolio_var) / 0.001

                # Component VaR
                component_var = weight * marginal_var
                component_vars[instrument] = component_var

        return {
            'portfolio_var': portfolio_var,
            'component_vars': component_vars,
            'confidence_level': confidence_level
        }

    def risk_factor_analysis(self, factor_returns: Dict[str, pd.Series]) -> Dict:
        """Perform risk factor analysis using multiple regression."""

        factor_df = pd.DataFrame(factor_returns).dropna()
        results = {}

        for instrument in self.instruments:
            if instrument in self.returns_df.columns:
                # Run regression: instrument_returns = alpha + beta * factors + epsilon
                y = self.returns_df[instrument].dropna()

                # Align data
                common_dates = y.index.intersection(factor_df.index)
                y_aligned = y.loc[common_dates]
                x_aligned = factor_df.loc[common_dates]

                if len(y_aligned) > len(factor_df.columns) + 10:  # Ensure sufficient data
                    # Add constant for alpha
                    x_with_const = np.column_stack([np.ones(len(x_aligned)), x_aligned.values])

                    # Perform regression
                    beta_coeffs, residuals, rank, s = np.linalg.lstsq(x_with_const, y_aligned, rcond=None)

                    # Calculate R-squared
                    ss_res = np.sum(residuals) if len(residuals) > 0 else np.sum((y_aligned - x_with_const @ beta_coeffs) ** 2)
                    ss_tot = np.sum((y_aligned - np.mean(y_aligned)) ** 2)
                    r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0

                    # Factor exposures (betas)
                    alpha = beta_coeffs[0]
                    betas = dict(zip(factor_df.columns, beta_coeffs[1:]))

                    # Risk decomposition
                    factor_variance = np.dot(beta_coeffs[1:], np.dot(x_aligned.cov().values, beta_coeffs[1:]))
                    specific_variance = np.var(y_aligned - x_with_const @ beta_coeffs)
                    total_variance = np.var(y_aligned)

                    results[instrument] = {
                        'alpha': alpha,
                        'betas': betas,
                        'r_squared': r_squared,
                        'factor_variance': factor_variance,
                        'specific_variance': specific_variance,
                        'total_variance': total_variance,
                        'factor_contribution': factor_variance / total_variance if total_variance > 0 else 0
                    }

        return results

    def correlation_risk_decomposition(self) -> Dict:
        """Decompose portfolio risk using correlation structure."""

        # Calculate correlation matrix
        correlation_matrix = self.returns_df.corr()

        # Portfolio variance decomposition
        weights_array = np.array([self.portfolio_weights.get(inst, 0) for inst in self.instruments])

        # Individual variance contributions
        individual_vars = {}
        correlation_contributions = {}

        for i, instrument in enumerate(self.instruments):
            if instrument in self.portfolio_weights:
                weight = self.portfolio_weights[instrument]
                individual_variance = self.returns_df[instrument].var()

                # Individual contribution (own variance)
                individual_contribution = (weight ** 2) * individual_variance
                individual_vars[instrument] = individual_contribution

                # Correlation contributions with other instruments
                correlation_contrib = 0
                for j, other_instrument in enumerate(self.instruments):
                    if i != j and other_instrument in self.portfolio_weights:
                        other_weight = self.portfolio_weights[other_instrument]
                        correlation = correlation_matrix.loc[instrument, other_instrument]
                        covariance = (correlation *
                                    np.sqrt(individual_variance) *
                                    np.sqrt(self.returns_df[other_instrument].var()))

                        correlation_contrib += weight * other_weight * covariance

                correlation_contributions[instrument] = correlation_contrib

        return {
            'individual_variance_contributions': individual_vars,
            'correlation_contributions': correlation_contributions,
            'total_portfolio_variance': sum(individual_vars.values()) + sum(correlation_contributions.values()) / 2
        }

    def _calculate_portfolio_returns(self, weights: Dict[str, float] = None) -> pd.Series:
        """Calculate portfolio returns using specified or default weights."""

        if weights is None:
            weights = self.portfolio_weights

        # Normalize weights
        total_weight = sum(weights.values())
        normalized_weights = {k: v/total_weight for k, v in weights.items()}

        # Calculate weighted returns
        portfolio_returns = pd.Series(0, index=self.returns_df.index)

        for instrument, weight in normalized_weights.items():
            if instrument in self.returns_df.columns:
                portfolio_returns += self.returns_df[instrument] * weight

        return portfolio_returns

# Risk Monitoring System
class RiskMonitor:
    """Real-time risk monitoring and alerting system."""

    def __init__(self, risk_analyzer: RiskAttributionAnalyzer):
        self.risk_analyzer = risk_analyzer
        self.risk_limits = {}
        self.alerts = []

    def set_risk_limits(self, limits: Dict[str, Dict]):
        """Set risk limits for monitoring."""
        self.risk_limits = limits

    def check_risk_limits(self) -> List[Dict]:
        """Check current risk against limits and generate alerts."""

        alerts = []

        # Check VaR limits
        var_analysis = self.risk_analyzer.calculate_component_var()

        if 'portfolio_var_limit' in self.risk_limits:
            limit = self.risk_limits['portfolio_var_limit']
            if abs(var_analysis['portfolio_var']) > limit:
                alerts.append({
                    'type': 'VaR_BREACH',
                    'message': f"Portfolio VaR ({var_analysis['portfolio_var']:.4f}) exceeds limit ({limit:.4f})",
                    'severity': 'HIGH'
                })

        # Check concentration limits
        for instrument, component_var in var_analysis['component_vars'].items():
            if f'{instrument}_var_limit' in self.risk_limits:
                limit = self.risk_limits[f'{instrument}_var_limit']
                if abs(component_var) > limit:
                    alerts.append({
                        'type': 'CONCENTRATION_BREACH',
                        'message': f"{instrument} Component VaR ({component_var:.4f}) exceeds limit ({limit:.4f})",
                        'severity': 'MEDIUM'
                    })

        self.alerts.extend(alerts)
        return alerts

# Example usage
def risk_attribution_example():
    """Demonstrate risk attribution analysis."""

    # Sample data (would come from actual portfolio analysis)
    instruments = ["EUR_USD", "GBP_USD", "USD_JPY", "AUD_USD"]
    weights = {"EUR_USD": 0.4, "GBP_USD": 0.3, "USD_JPY": 0.2, "AUD_USD": 0.1}

    print("Risk Attribution Analysis:")
    print("1. Component VaR calculation")
    print("2. Risk factor analysis")
    print("3. Correlation risk decomposition")
    print("4. Risk monitoring and limits")

    # analyzer = RiskAttributionAnalyzer(returns_data, weights)
    # var_analysis = analyzer.calculate_component_var()
    # risk_decomposition = analyzer.correlation_risk_decomposition()

    return "Risk attribution framework ready"

# Run example
# result = risk_attribution_example()
```

## Key Risk Metrics

### 1. Value at Risk (VaR)
- **Portfolio VaR**: Maximum expected loss at confidence level
- **Component VaR**: Each instrument's contribution to portfolio VaR
- **Marginal VaR**: Risk change from small position increase

### 2. Risk Factor Analysis
- **Factor Exposures**: Sensitivity to market factors
- **Factor Variance**: Risk explained by factors
- **Specific Risk**: Idiosyncratic risk component

### 3. Correlation Risk
- **Diversification Benefit**: Risk reduction from correlation
- **Concentration Risk**: Risk from similar exposures
- **Correlation Breakdown**: Risk during market stress

---

## Next Steps

Continue to [Performance Attribution](performance-attribution.md) to analyze what drives portfolio returns.

---

## Related Tutorials

- [Portfolio Optimization](portfolio-optimization.md) - Optimization methods
- [Performance Attribution](performance-attribution.md) - Return analysis
- [Best Practices](best-practices.md) - Implementation guidance