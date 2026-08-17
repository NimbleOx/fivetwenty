# Examples & Code Samples

This page provides access to comprehensive examples and code samples for FiveTwenty. All examples are included with your FiveTwenty installation in the `docs/examples/` directory and are maintained to stay up-to-date with the latest SDK features.

## Browse Examples Locally

All examples are organized into two categories in your FiveTwenty installation:

### Python Scripts

**[`docs/examples/scripts/`](https://github.com/NimbleOx/fivetwenty/tree/main/docs/examples/scripts)**

Complete, runnable Python scripts demonstrating specific functionality:

- **[`basic_usage.py`](https://github.com/NimbleOx/fivetwenty/blob/main/docs/examples/scripts/basic_usage.py)** - Getting started with FiveTwenty
- **[`account_management.py`](https://github.com/NimbleOx/fivetwenty/blob/main/docs/examples/scripts/account_management.py)** - Account operations and configuration
- **[`configuration_patterns.py`](https://github.com/NimbleOx/fivetwenty/blob/main/docs/examples/scripts/configuration_patterns.py)** - Different ways to configure the client
- **[`sync_usage.py`](https://github.com/NimbleOx/fivetwenty/blob/main/docs/examples/scripts/sync_usage.py)** - Using the synchronous client wrapper
- **[`pricing_and_candles.py`](https://github.com/NimbleOx/fivetwenty/blob/main/docs/examples/scripts/pricing_and_candles.py)** - Market data and candlestick analysis
- **[`advanced_order_management.py`](https://github.com/NimbleOx/fivetwenty/blob/main/docs/examples/scripts/advanced_order_management.py)** - Complex order types and management
- **[`position_management.py`](https://github.com/NimbleOx/fivetwenty/blob/main/docs/examples/scripts/position_management.py)** - Position tracking and management
- **[`trade_management.py`](https://github.com/NimbleOx/fivetwenty/blob/main/docs/examples/scripts/trade_management.py)** - Trade lifecycle management
- **[`transaction_analysis.py`](https://github.com/NimbleOx/fivetwenty/blob/main/docs/examples/scripts/transaction_analysis.py)** - Transaction history and analysis
- **[`enhanced_error_handling.py`](https://github.com/NimbleOx/fivetwenty/blob/main/docs/examples/scripts/enhanced_error_handling.py)** - Robust error handling patterns
- **[`advanced_features_demo.py`](https://github.com/NimbleOx/fivetwenty/blob/main/docs/examples/scripts/advanced_features_demo.py)** - Advanced SDK features showcase

### Jupyter Notebooks

**[`docs/examples/notebooks/`](https://github.com/NimbleOx/fivetwenty/tree/main/docs/examples/notebooks)**

Interactive Jupyter notebooks for learning and experimentation:

- **[`quick-start.ipynb`](https://github.com/NimbleOx/fivetwenty/blob/main/docs/examples/notebooks/quick-start.ipynb)** - Quick start guide and basic operations
- **[`trading-strategies.ipynb`](https://github.com/NimbleOx/fivetwenty/blob/main/docs/examples/notebooks/trading-strategies.ipynb)** - Strategy development and implementation
- **[`streaming-data.ipynb`](https://github.com/NimbleOx/fivetwenty/blob/main/docs/examples/notebooks/streaming-data.ipynb)** - Real-time data processing and streaming
- **[`risk-management.ipynb`](https://github.com/NimbleOx/fivetwenty/blob/main/docs/examples/notebooks/risk-management.ipynb)** - Risk management techniques and tools
- **[`data-analysis.ipynb`](https://github.com/NimbleOx/fivetwenty/blob/main/docs/examples/notebooks/data-analysis.ipynb)** - Market data analysis and visualization
- **[`backtesting.ipynb`](https://github.com/NimbleOx/fivetwenty/blob/main/docs/examples/notebooks/backtesting.ipynb)** - Strategy backtesting framework

## Getting Started

### Prerequisites

Before running any examples, make sure you have:

1. **FiveTwenty installed**: `uv add fivetwenty`
2. **OANDA API credentials**: [Get your API token](tutorials/getting-started/authentication.md)
3. **Environment configured**: Set your `FIVETWENTY_OANDA_TOKEN` and account details

### Running Python Scripts

1. **Install FiveTwenty** (if not already installed):
   ```bash
   uv add fivetwenty
   ```

2. **Get the examples** (they live in the repository, not the installed package):
   ```bash
   git clone https://github.com/NimbleOx/fivetwenty.git
   cd fivetwenty/docs/examples/scripts
   ```

3. **Set up your environment**:
   ```bash
   export FIVETWENTY_OANDA_TOKEN="your-practice-token"
   export FIVETWENTY_OANDA_ACCOUNT="your-account-id"
   export FIVETWENTY_OANDA_ENVIRONMENT="practice"
   ```

4. **Run any script**:
   ```bash
   python path/to/examples/scripts/basic_usage.py
   ```

### Running Jupyter Notebooks

1. **Install Jupyter**:
   ```bash
   uv add jupyter
   ```

2. **Navigate to notebooks directory**:
   ```bash
   # Find and navigate to the notebooks directory
   cd path/to/docs/examples/notebooks/
   ```

3. **Start Jupyter**:
   ```bash
   jupyter notebook
   ```

4. **Open any notebook** and follow the interactive instructions

## Documentation Integration

Examples complement our structured documentation:

- **[Tutorials](tutorials/index.md)** - Step-by-step learning paths
- **[Guides](guides/index.md)** - Comprehensive guidance and solutions
- **[API Reference](api-reference/index.md)** - Complete API documentation

## Contributing Examples

Found a bug or want to add an example?

1. **Report issues**: See [Contributing Guide](contributing/index.md) for reporting guidelines
2. **Contribute examples**: [Contributing Guide](contributing/index.md)
3. **Suggest improvements**: [Contributing Guide](contributing/index.md)

## Example Categories

### By Skill Level

- **Beginner**: [`basic_usage.py`](https://github.com/NimbleOx/fivetwenty/blob/main/docs/examples/scripts/basic_usage.py), [`quick-start.ipynb`](https://github.com/NimbleOx/fivetwenty/blob/main/docs/examples/notebooks/quick-start.ipynb)
- **Intermediate**: [`account_management.py`](https://github.com/NimbleOx/fivetwenty/blob/main/docs/examples/scripts/account_management.py), [`pricing_and_candles.py`](https://github.com/NimbleOx/fivetwenty/blob/main/docs/examples/scripts/pricing_and_candles.py), [`trading-strategies.ipynb`](https://github.com/NimbleOx/fivetwenty/blob/main/docs/examples/notebooks/trading-strategies.ipynb)
- **Advanced**: [`advanced_features_demo.py`](https://github.com/NimbleOx/fivetwenty/blob/main/docs/examples/scripts/advanced_features_demo.py), [`enhanced_error_handling.py`](https://github.com/NimbleOx/fivetwenty/blob/main/docs/examples/scripts/enhanced_error_handling.py), [`backtesting.ipynb`](https://github.com/NimbleOx/fivetwenty/blob/main/docs/examples/notebooks/backtesting.ipynb)

### By Use Case

- **Account Management**: [`account_management.py`](https://github.com/NimbleOx/fivetwenty/blob/main/docs/examples/scripts/account_management.py), [`configuration_patterns.py`](https://github.com/NimbleOx/fivetwenty/blob/main/docs/examples/scripts/configuration_patterns.py)
- **Market Data**: [`pricing_and_candles.py`](https://github.com/NimbleOx/fivetwenty/blob/main/docs/examples/scripts/pricing_and_candles.py), [`data-analysis.ipynb`](https://github.com/NimbleOx/fivetwenty/blob/main/docs/examples/notebooks/data-analysis.ipynb), [`streaming-data.ipynb`](https://github.com/NimbleOx/fivetwenty/blob/main/docs/examples/notebooks/streaming-data.ipynb)
- **Trading**: [`advanced_order_management.py`](https://github.com/NimbleOx/fivetwenty/blob/main/docs/examples/scripts/advanced_order_management.py), [`position_management.py`](https://github.com/NimbleOx/fivetwenty/blob/main/docs/examples/scripts/position_management.py), [`trade_management.py`](https://github.com/NimbleOx/fivetwenty/blob/main/docs/examples/scripts/trade_management.py)
- **Analysis**: [`transaction_analysis.py`](https://github.com/NimbleOx/fivetwenty/blob/main/docs/examples/scripts/transaction_analysis.py), [`backtesting.ipynb`](https://github.com/NimbleOx/fivetwenty/blob/main/docs/examples/notebooks/backtesting.ipynb), [`risk-management.ipynb`](https://github.com/NimbleOx/fivetwenty/blob/main/docs/examples/notebooks/risk-management.ipynb)
- **Integration**: [`sync_usage.py`](https://github.com/NimbleOx/fivetwenty/blob/main/docs/examples/scripts/sync_usage.py), [`enhanced_error_handling.py`](https://github.com/NimbleOx/fivetwenty/blob/main/docs/examples/scripts/enhanced_error_handling.py)

---

**Remember**: All examples use the practice environment by default for safe learning and testing!