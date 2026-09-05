# Scripts and notebooks

Explore runnable scripts and notebooks in the repository's `docs/examples/`
directory. To use them, [run from a checkout](#run-from-a-checkout); they are provided
separately from the installed SDK.

For a first read-only script, start with [authentication](tutorials/getting-started/authentication.md).
To place and close a single practice trade, follow
[Your first trade](tutorials/getting-started/first-trade.md).

Use practice credentials and check the client's resolved environment before
running an example. Environment variables can override a practice default, and
write requests change account state even on a practice account.

## Python scripts

Choose a script by topic. **Contains writes** identifies files with calls that
change account state. Read the script to see which calls run and under what
conditions before executing it.

| Script | Topic | Contains writes |
| --- | --- | --- |
| [basic_usage.py](https://github.com/NimbleOx/fivetwenty/blob/main/docs/examples/scripts/basic_usage.py) | Getting started with FiveTwenty | Yes |
| [account_management.py](https://github.com/NimbleOx/fivetwenty/blob/main/docs/examples/scripts/account_management.py) | Account operations and configuration | No |
| [configuration_patterns.py](https://github.com/NimbleOx/fivetwenty/blob/main/docs/examples/scripts/configuration_patterns.py) | Different ways to configure the client | No |
| [sync_usage.py](https://github.com/NimbleOx/fivetwenty/blob/main/docs/examples/scripts/sync_usage.py) | Using the synchronous client wrapper | Yes |
| [pricing_and_candles.py](https://github.com/NimbleOx/fivetwenty/blob/main/docs/examples/scripts/pricing_and_candles.py) | Market data and candlestick analysis | No |
| [advanced_order_management.py](https://github.com/NimbleOx/fivetwenty/blob/main/docs/examples/scripts/advanced_order_management.py) | Complex order types and management | Yes |
| [position_management.py](https://github.com/NimbleOx/fivetwenty/blob/main/docs/examples/scripts/position_management.py) | Position tracking and management | Yes |
| [trade_management.py](https://github.com/NimbleOx/fivetwenty/blob/main/docs/examples/scripts/trade_management.py) | Trade lifecycle management | Yes |
| [transaction_analysis.py](https://github.com/NimbleOx/fivetwenty/blob/main/docs/examples/scripts/transaction_analysis.py) | Transaction history and analysis | No |
| [enhanced_error_handling.py](https://github.com/NimbleOx/fivetwenty/blob/main/docs/examples/scripts/enhanced_error_handling.py) | Error handling patterns | Yes |
| [advanced_features_demo.py](https://github.com/NimbleOx/fivetwenty/blob/main/docs/examples/scripts/advanced_features_demo.py) | Tour of advanced SDK features | Yes |

## Jupyter notebooks

Run cells in order using the Python environment where you installed the notebook's
dependencies. Each notebook explains which operations change account state and
which results use local simulations.
The quick-start notebook places an order, and its position-close cell can affect
trades that predate the notebook.

| Notebook | Exercise |
| --- | --- |
| [quick-start.ipynb](https://github.com/NimbleOx/fivetwenty/blob/main/docs/examples/notebooks/quick-start.ipynb) | Quick start guide and basic operations |
| [trading-strategies.ipynb](https://github.com/NimbleOx/fivetwenty/blob/main/docs/examples/notebooks/trading-strategies.ipynb) | Strategy development and implementation |
| [streaming-data.ipynb](https://github.com/NimbleOx/fivetwenty/blob/main/docs/examples/notebooks/streaming-data.ipynb) | Real-time data processing and streaming |
| [risk-management.ipynb](https://github.com/NimbleOx/fivetwenty/blob/main/docs/examples/notebooks/risk-management.ipynb) | Risk management techniques and tools |
| [data-analysis.ipynb](https://github.com/NimbleOx/fivetwenty/blob/main/docs/examples/notebooks/data-analysis.ipynb) | Market data analysis and visualization |
| [backtesting.ipynb](https://github.com/NimbleOx/fivetwenty/blob/main/docs/examples/notebooks/backtesting.ipynb) | Simplified historical simulation and parameter comparisons |

## Run from a checkout

Set `FIVETWENTY_OANDA_TOKEN` and `FIVETWENTY_OANDA_ACCOUNT` for a practice account,
and `FIVETWENTY_OANDA_ENVIRONMENT=practice`, as described in
[authentication](tutorials/getting-started/authentication.md). Check whether your
chosen script loads `.env` itself; the SDK reads environment variables directly.

Clone the repository, install development dependencies and run a script:

```bash
git clone https://github.com/NimbleOx/fivetwenty.git
cd fivetwenty
uv sync --group dev
uv run python docs/examples/scripts/pricing_and_candles.py
```

Scripts that stream may run until interrupted.

For notebooks, install the packages imported by the setup cell, including any
analysis or plotting dependencies, and select that environment as the kernel.
From this checkout, a Jupyter installation can be started with:

```bash
uv run --with jupyter jupyter notebook docs/examples/notebooks
```

To check the notebooks offline, run the repository's validation command. It
installs analysis dependencies in a temporary environment and executes copies of
the notebooks with simulated API responses:

```bash
uv run poe docs-validate-notebooks
```

This check verifies that the examples work with the SDK and its test data. Use a
practice account to check behavior with OANDA. When interpreting backtest or
simulation results, review the assumptions about timing, costs, currency conversion
and execution.

To report an example that needs updating, see [contributing](contributing/index.md).
Include the SDK version, inputs with private details removed, and what happened.
