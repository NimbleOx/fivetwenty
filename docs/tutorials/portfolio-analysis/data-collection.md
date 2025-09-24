# Data Collection & Analysis Framework

Build the data infrastructure needed for comprehensive portfolio analysis using FiveTwenty.

---

## Prerequisites

- Completed [Portfolio Theory Fundamentals](portfolio-theory.md)
- FiveTwenty SDK configured with OANDA account
- Python with pandas, numpy, matplotlib, and seaborn

---

## Learning Objectives

By the end of this tutorial, you will:

- ✅ Collect historical price data for multiple instruments
- ✅ Calculate returns and statistical measures
- ✅ Build correlation matrices and analysis
- ✅ Create visualization and analysis framework

---

## Portfolio Data Framework

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

        print(f"Collecting price data for {len(instruments)} instruments...")

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
        print(f"Returns calculated for {len(returns_data)} instruments")

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

        print(f"Correlation matrix calculated ({correlation_matrix.shape[0]}x{correlation_matrix.shape[1]})")
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

        print(f"Found {len(clusters)} correlation clusters (threshold: {threshold}):")
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
        print(f"\nPortfolio Statistics Summary:")
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

## Key Analysis Components

### 1. Price Data Collection
- **Multi-instrument**: Fetch data for entire portfolio
- **Configurable periods**: Adjust historical depth
- **Error handling**: Graceful handling of API issues
- **Data validation**: Ensure data quality and completeness

### 2. Returns Calculation
- **Percentage returns**: Standard return calculation
- **Multiple price types**: Open, close, high, low options
- **Data alignment**: Handle different data availability

### 3. Statistical Analysis
- **Risk metrics**: Volatility, VaR, skewness, kurtosis
- **Performance metrics**: Returns, Sharpe ratio
- **Portfolio aggregation**: Combined portfolio statistics

### 4. Correlation Analysis
- **Correlation matrix**: Pairwise correlations
- **Cluster identification**: Group similar instruments
- **Visualization**: Heatmap representation

## Data Quality Considerations

### Missing Data Handling
```python
# Check for missing data
def validate_data_quality(price_data: Dict[str, pd.DataFrame]) -> Dict[str, Dict]:
    quality_report = {}

    for instrument, df in price_data.items():
        quality_report[instrument] = {
            'total_periods': len(df),
            'missing_periods': df.isnull().sum().sum(),
            'date_range': (df.index.min(), df.index.max()),
            'completeness': 1 - (df.isnull().sum().sum() / (len(df) * len(df.columns)))
        }

    return quality_report
```

### Data Alignment
```python
# Align data across instruments
def align_portfolio_data(returns_data: Dict[str, pd.Series]) -> pd.DataFrame:
    """Align returns data across all instruments."""

    returns_df = pd.DataFrame(returns_data)

    # Report alignment statistics
    print(f"Original data points: {sum(len(series) for series in returns_data.values())}")
    print(f"Aligned data points: {len(returns_df.dropna()) * len(returns_df.columns)}")
    print(f"Data utilization: {len(returns_df.dropna()) / len(returns_df):.2%}")

    return returns_df.dropna()
```

---

## Next Steps

With your data collection framework in place, proceed to [Portfolio Optimization](portfolio-optimization.md) to apply mathematical optimization techniques.

---

## Related Tutorials

- [Portfolio Theory Fundamentals](portfolio-theory.md) - Theoretical foundation
- [Portfolio Optimization](portfolio-optimization.md) - Apply optimization methods
- [Risk Attribution](risk-attribution.md) - Analyze risk sources