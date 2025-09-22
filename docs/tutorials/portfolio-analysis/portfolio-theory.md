# Portfolio Theory Fundamentals

Learn the mathematical foundations of modern portfolio theory and portfolio construction principles.

---

## Prerequisites

- Basic understanding of statistics and probability
- Familiarity with risk and return concepts
- Python environment with scientific libraries

---

## Learning Objectives

By the end of this tutorial, you will understand:

- ✅ Modern Portfolio Theory (MPT) concepts
- ✅ Portfolio construction principles
- ✅ Risk and return relationships
- ✅ Diversification benefits

---

## Modern Portfolio Theory (MPT)

**Key Concepts:**

- **Diversification**: Reducing risk through uncorrelated assets
- **Efficient Frontier**: Optimal risk/return combinations
- **Correlation**: How instruments move together (-1 to +1)
- **Sharpe Ratio**: Risk-adjusted returns
- **Value at Risk (VaR)**: Maximum expected loss

### Mathematical Foundation

Modern Portfolio Theory, developed by Harry Markowitz, is based on the principle that investors can construct portfolios to optimize expected return for a given level of risk.

**Expected Portfolio Return:**
```
E(Rp) = Σ(wi × E(Ri))
```

**Portfolio Variance:**
```
σ²p = Σ(wi² × σi²) + Σ Σ(wi × wj × σij)
```

Where:
- `wi` = weight of asset i
- `E(Ri)` = expected return of asset i
- `σi²` = variance of asset i
- `σij` = covariance between assets i and j

### Portfolio Construction Principles

1. **Asset Selection**: Choose instruments with low correlation
2. **Position Sizing**: Weight positions based on risk contribution
3. **Risk Budgeting**: Allocate risk across different sources
4. **Rebalancing**: Maintain target allocations over time

### Risk-Return Trade-off

The fundamental principle of MPT is that higher expected returns come with higher risk. The efficient frontier represents the set of optimal portfolios offering the highest expected return for each level of risk.

### Diversification Benefits

Diversification reduces portfolio risk through:
- **Correlation reduction**: Combining assets that don't move together
- **Risk spreading**: Distributing risk across multiple sources
- **Volatility smoothing**: Reducing overall portfolio volatility

### Correlation Analysis

Correlation coefficients range from -1 to +1:
- **+1**: Perfect positive correlation (move together)
- **0**: No correlation (independent movements)
- **-1**: Perfect negative correlation (move opposite)

**Optimal diversification** occurs when combining assets with correlation < 0.7.

---

## Next Steps

Now that you understand the theoretical foundation, proceed to [Data Collection & Analysis](data-collection.md) to build the infrastructure for implementing these concepts.

---

## Related Tutorials

- [Data Collection & Analysis](data-collection.md) - Build analysis infrastructure
- [Portfolio Optimization](portfolio-optimization.md) - Apply MPT optimization
- [Risk Attribution](risk-attribution.md) - Analyze risk sources