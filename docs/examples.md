# Scripts and notebooks

Examples live in the repository under `docs/examples/`; they are not installed with
the SDK package. Read each example's configuration and account-changing operations
before running it. A practice default can be overridden by environment configuration,
and practice requests still change account state.

For a first read-only script, start with [authentication](tutorials/getting-started/authentication.md).
For one explicit create-and-close sequence, use the
[practice trade lifecycle](tutorials/getting-started/first-trade.md).

## Python scripts

The scripts cover the following topics. “Contains writes” means the file includes
account-changing calls; inspect the selected entry point and conditions before use.
These are demonstrations, not unattended trading services.

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

Run cells in order with the configured Python kernel. Notebook Markdown explains
which operations change account state and which results use local simulations.
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

```bash
git clone https://github.com/NimbleOx/fivetwenty.git
cd fivetwenty
uv sync --group dev
uv run python docs/examples/scripts/pricing_and_candles.py
```

Set `FIVETWENTY_OANDA_TOKEN` and `FIVETWENTY_OANDA_ACCOUNT` for a practice account,
and `FIVETWENTY_OANDA_ENVIRONMENT=practice`. Check whether the selected script loads
`.env` itself; the SDK does not. Scripts that stream may run until interrupted.

For notebooks, install the packages imported by the setup cell, including any
analysis or plotting dependencies, and select that environment as the kernel.
From this checkout, a Jupyter installation can be started with:

```bash
uv run --with jupyter jupyter notebook docs/examples/notebooks
```

The repository's offline notebook check installs its analysis dependencies in an
ephemeral environment and executes temporary copies using mocked HTTP:

```bash
uv run poe docs-validate-notebooks
```

A successful mocked run checks SDK usage against synthetic responses. It does not
establish live fills, strategy performance or eligibility for account-specific
features. Backtests and paper simulations need their timing, costs, currency and
execution assumptions reviewed before their metrics are meaningful.

See [contributing](contributing/index.md) to report a stale example with its SDK
version, sanitized inputs and observed result.
