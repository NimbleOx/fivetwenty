# Client API Reference

Complete reference for FiveTwenty client interfaces and configuration.

---

## Quick Reference

### Client Creation
| Method | Purpose | Parameters |
|--------|---------|------------|
| [AsyncClient](#asyncclient) | Async client | `token?`, `config?`, `account_id?`, `environment?`, `timeout?` |
| [Client](#client) | Sync client | Same as async client |

### Endpoint Groups
| Endpoint | Purpose | Key Methods |
|----------|---------|-------------|
| [accounts](endpoints/accounts.md) | Account management | `get_accounts()`, `get_account()`, `get_account_summary()`, `get_account_instruments()`, `patch_account_configuration()`, `get_account_changes()` |
| [orders](endpoints/orders.md) | Order operations | `post_market_order()`, `post_limit_order()`, `cancel_order()`, `get_pending_orders()`, `get_orders()`, `put_order()` |
| [trades](endpoints/trades.md) | Trade management | `get_open_trades()`, `get_trade()`, `close_trade()`, `put_trade_orders()`, `get_trades()` |
| [positions](endpoints/positions.md) | Position tracking | `get_open_positions()`, `get_position()`, `close_position()`, `get_positions()` |
| [pricing](endpoints/pricing.md) | Market data | `get_pricing()`, `get_pricing_stream()`, `get_instrument_candles()`, `get_latest_candles()` |
| [instruments](endpoints/instruments.md) | Instrument data | `get_account_instruments()`, `get_instrument_candles()` |
| [transactions](endpoints/transactions.md) | Transaction history | `get_transactions()`, `get_transaction()`, `get_transactions_range()`, `get_transactions_stream()`, `get_transactions_since_id()` |

---

## Client Classes

### AsyncClient
Primary async client for OANDA API operations. Recommended for production use.

**Constructor:**
```python
from logging import Logger

import httpx

from fivetwenty import AsyncClient, AccountConfig, Environment

# Constructor signature:
def AsyncClient(
    token: str | None = None,
    *,
    account_id: str | None = None,
    environment: Environment = Environment.PRACTICE,
    config: AccountConfig | None = None,
    timeout: float = 30.0,
    max_retries: int = 3,
    transport: httpx.AsyncClient | None = None,
    user_agent: str | None = None,
    proxies: str | None = None,
    verify: bool | str = True,
    cert: str | None = None,
    logger: Logger | None = None,
) -> AsyncClient:
    ...
```

**Configuration Parameters (choose one approach):**

1. **Configuration Object** (recommended for applications):
   - `config` (AccountConfig) - Pre-configured account settings

2. **Direct Parameters** (basic scripts):
   - `token` (str) - OANDA API token
   - `account_id` (str) - OANDA account ID (required when token is provided)
   - `environment` (Environment) - `Environment.PRACTICE` or `Environment.LIVE`

3. **Environment Variables** (deployment):
   - No parameters needed - loads from `FIVETWENTY_*` environment variables

**HTTP Configuration:**

- `timeout` (float) - Request timeout in seconds (default: 30.0)
- `max_retries` (int) - Maximum retry attempts (default: 3)
- `transport` (httpx.AsyncClient, optional) - Custom HTTP client
- `user_agent` (str, optional) - Custom user agent string
- `proxies` (str, optional) - Proxy URL
- `verify` (bool | str) - SSL verification (default: True)
- `cert` (str, optional) - Client certificate path
- `logger` (Logger, optional) - Logger instance for request logging

**Usage Examples:**

<!-- code-block: async_client_usage_examples -->
```python
from fivetwenty import AsyncClient, Environment

# Environment variables (recommended for deployment)

async with AsyncClient() as client:
    accounts = await client.accounts.get_accounts()

# Direct parameters (basic scripts)
async with AsyncClient(
    token="your-token",
    account_id="your-account-id",
    environment=Environment.PRACTICE
) as client:
    accounts = await client.accounts.get_accounts()

# Configuration object (structured applications)
from pydantic import SecretStr

from fivetwenty import AccountConfig

config = AccountConfig(
    token=SecretStr("your-token"),
    account_id=SecretStr("your-account-id"),
    environment=Environment.PRACTICE,
    alias="production_trading"
)

async with AsyncClient(config=config) as client:
    print(f"Trading on: {client.config.summary()}")
    accounts = await client.accounts.get_accounts()
```

**Configuration Priority:**
When multiple configuration sources are provided:

1. `config` parameter (highest priority)
2. Direct parameters (`token`, `account_id`, etc.)
3. Environment variables (lowest priority)

**Properties:**

- `account_id` (str) - Configured account ID
- `config` (AccountConfig) - Account configuration object
- `accounts` - [AccountEndpoints](endpoints/accounts.md)
- `orders` - [OrderEndpoints](endpoints/orders.md)
- `trades` - [TradeEndpoints](endpoints/trades.md)
- `positions` - [PositionEndpoints](endpoints/positions.md)
- `pricing` - [PricingEndpoints](endpoints/pricing.md)
- `instruments` - [InstrumentEndpoints](endpoints/instruments.md)
- `transactions` - [TransactionEndpoints](endpoints/transactions.md)

### Client
Synchronous wrapper around AsyncClient. Use for scripts and basic applications.

**Constructor:**
```python
from typing import Any

from fivetwenty import Client

# Constructor signature:
def Client(**kwargs: Any) -> Client:
    ...
```

**Parameters:**

Accepts the same parameters as [AsyncClient](#asyncclient). See AsyncClient documentation for complete parameter list.

**Usage Examples:**

<!-- code-block: client_usage_examples -->
```python
# Environment variables
from fivetwenty import Client

with Client() as client:
    accounts = client.accounts.get_accounts()

# Direct parameters
from fivetwenty import Client, Environment

with Client(
    token="your-token",
    account_id="your-account-id",
    environment=Environment.PRACTICE
) as client:
    accounts = client.accounts.get_accounts()

# Configuration object
from pydantic import SecretStr

from fivetwenty import AccountConfig

config = AccountConfig(
    token=SecretStr("your-token"),
    account_id=SecretStr("your-account-id"),
    environment=Environment.PRACTICE,
    alias="my_account"
)
with Client(config=config) as client:
    print(f"Using: {client.config.summary()}")
    accounts = client.accounts.get_accounts()
```

**Properties:**

- `account_id` (str) - Configured account ID
- `config` (AccountConfig) - Account configuration object
- Same endpoint structure as AsyncClient, but with synchronous methods

---

## API Endpoints Documentation

For detailed information about specific API endpoints and their methods, please refer to the individual endpoint documentation:

- **[Account Management](endpoints/accounts.md)** - Account information, configuration, and instruments
- **[Order Management](endpoints/orders.md)** - Creating, modifying, and canceling orders
- **[Trade Management](endpoints/trades.md)** - Managing open trades and positions
- **[Position Tracking](endpoints/positions.md)** - Position monitoring and closure
- **[Market Data](endpoints/pricing.md)** - Real-time pricing and streaming data
- **[Instrument Data](endpoints/instruments.md)** - Instrument specifications and historical data
- **[Transaction History](endpoints/transactions.md)** - Transaction records and streaming

Each endpoint page contains complete method signatures, parameters, return types, and usage examples.

---

## Configuration Management

### AccountConfig Class

Structured configuration for account credentials and settings.

**Constructor:**
<!-- code-block: account_config_constructor -->
```python
from pydantic import SecretStr

from fivetwenty import AccountConfig, Environment

config = AccountConfig(
    token=SecretStr("your_token"),
    account_id=SecretStr("your_account_id"),
    environment=Environment.PRACTICE,
    alias="my_config",
)
```

**Parameters:**

- `token` - OANDA API token (automatically protected)
- `account_id` - OANDA account ID (automatically protected)
- `environment` - Environment.PRACTICE or Environment.LIVE
- `alias` - User-friendly identifier (valid Python identifier)

**Security Features:**

- Automatically masks `token` and `account_id` in string representations
- Validates alias format (must be valid identifier)
- Prevents logging of sensitive credentials

**Methods:**

- `summary()` → str - Safe summary for logs ("alias (environment)")

**Example:**
<!-- code-block: account_config_example -->
```python
from pydantic import SecretStr

from fivetwenty import AccountConfig, Environment

config = AccountConfig(
    token=SecretStr("your-api-token"),
    account_id=SecretStr("your-account-id"),
    environment=Environment.PRACTICE,
    alias="demo_trading",
)

print(config.summary())  # "demo_trading (practice)"
print(repr(config))  # Secrets are masked as '***'
```

### Environment Variable Loading

**Standard Variables:**

- `FIVETWENTY_OANDA_TOKEN` - API token
- `FIVETWENTY_OANDA_ACCOUNT` - Account ID
- `FIVETWENTY_OANDA_ENVIRONMENT` - "practice" or "live"
- `FIVETWENTY_OANDA_ACCOUNT_ALIAS` - Account alias

**Custom Prefixes:**
<!-- code-block: account_config_loader -->
```python
from fivetwenty import AccountConfigLoader

# Load with custom prefix
config = AccountConfigLoader.from_env_prefix("TRADING_")
# Loads from TRADING_FIVETWENTY_OANDA_TOKEN, TRADING_FIVETWENTY_OANDA_ACCOUNT, etc.
```

## Error Handling

### Configuration Errors

**ValueError**: Raised when no valid configuration is provided:
<!-- code-block: value_error_example -->
```python
from fivetwenty import AsyncClient

try:
    client = AsyncClient()  # No config provided, no env vars
except ValueError as e:
    print(f"Configuration error: {e}")
    print("Set FIVETWENTY_OANDA_TOKEN/FIVETWENTY_OANDA_ACCOUNT or pass parameters")
```

**ValidationError**: Raised for invalid configuration values:
<!-- code-block: validation_error_example -->
```python
from pydantic import SecretStr, ValidationError

from fivetwenty import AccountConfig, Environment

try:
    config = AccountConfig(
        token=SecretStr(""),  # Empty token - will fail validation
        account_id=SecretStr("account"),
        environment=Environment.PRACTICE,
        alias="123invalid",  # Invalid alias - must start with letter
    )
except ValidationError as e:
    print(f"Configuration error: {e}")
```

### API Errors

All endpoint methods raise `FiveTwentyError` for API errors. The exception contains:

- `status_code` (int) - HTTP status code
- `error_code` (str) - OANDA error code
- `message` (str) - Error description
- `details` (dict) - Additional error information

**Example:**
<!-- code-block: fivetwenty_error_handling -->
```python
import asyncio

from fivetwenty import AsyncClient, FiveTwentyError


async def main() -> None:
    async with AsyncClient() as client:
        try:
            trade = await client.trades.get_trade(client.account_id, "invalid_id")
            print(f"Trade: {trade}")
        except FiveTwentyError as e:
            print(f"Error {e.status}: {e.message}")
            if e.code:
                print(f"Error code: {e.code}")
            # Handle specific errors
            if e.status == 404:
                print("Trade not found")


asyncio.run(main())
```

---

## Rate Limits

OANDA API enforces rate limits:

- **REST Requests**: 120 requests per minute
- **Streaming**: 20 concurrent connections
- **Burst**: Short bursts allowed up to double rate

**Best Practices:**

- Add delays between requests (500ms minimum recommended)
- Use streaming for real-time data instead of polling
- Implement exponential backoff on rate limit errors (429 status)
- Monitor `X-RateLimit-*` headers in responses

---

## Environment Considerations

### Practice Environment
- URL: `Environment.PRACTICE.base_url` (`https\://api-fxpractice.oanda.com/v3`)
- Virtual money only
- Same API functionality as live
- Reset account balances available
- No trading restrictions

### Live Environment
- URL: `Environment.LIVE.base_url` (`https\://api-fxtrade.oanda.com/v3`)
- Real money trading
- Risk management essential
- Requires live trading account
- Subject to margin requirements

## Security Best Practices

### Credential Protection

- Never commit tokens to version control
- Use environment variables or secure vaults for credentials
- Rotate tokens regularly
- Use separate tokens for practice and live environments

### Configuration Validation

- Always validate configuration before deployment
- Use structured `AccountConfig` objects in applications
- Test authentication before starting trading operations

### Environment Separation

- Keep practice and live configurations fully separate
- Use different aliases to explicitly identify environments
- Never use live tokens in development or testing

**Configuration Examples:**

```bash
# Production deployment with environment variables
export FIVETWENTY_OANDA_TOKEN="live-token"
export FIVETWENTY_OANDA_ACCOUNT="live-account"
export FIVETWENTY_OANDA_ENVIRONMENT="live"
export FIVETWENTY_OANDA_ACCOUNT_ALIAS="production_trading"

# Development with separate practice credentials
export FIVETWENTY_OANDA_TOKEN="practice-token"
export FIVETWENTY_OANDA_ACCOUNT="practice-account"
export FIVETWENTY_OANDA_ENVIRONMENT="practice"
export FIVETWENTY_OANDA_ACCOUNT_ALIAS="development"
```

**Multi-Account Configuration:**

```bash
# Multiple strategies with prefixes
export STRATEGY_A_OANDA_TOKEN="token-a"
export STRATEGY_A_OANDA_ACCOUNT="account-a"
export STRATEGY_A_OANDA_ENVIRONMENT="practice"
export STRATEGY_A_OANDA_ACCOUNT_ALIAS="momentum_strategy"

export STRATEGY_B_OANDA_TOKEN="token-b"
export STRATEGY_B_OANDA_ACCOUNT="account-b"
export STRATEGY_B_OANDA_ENVIRONMENT="practice"
export STRATEGY_B_OANDA_ACCOUNT_ALIAS="grid_strategy"
```

<!-- code-block: multi_account_configuration -->
```python
import asyncio

from fivetwenty import AccountConfigLoader, AsyncClient


async def main() -> None:
    # Load configurations with custom prefixes
    momentum_config = AccountConfigLoader.from_env_prefix("STRATEGY_A_")
    grid_config = AccountConfigLoader.from_env_prefix("STRATEGY_B_")

    # Use in clients
    async with AsyncClient(config=momentum_config) as momentum_client:
        print(f"Momentum: {momentum_client.config.summary()}")

    async with AsyncClient(config=grid_config) as grid_client:
        print(f"Grid: {grid_client.config.summary()}")


asyncio.run(main())
```

---

## Next Steps

Now that you understand client configuration, explore the API endpoints:

- **[Accounts](endpoints/accounts.md)** - Get account details and configuration
- **[Pricing](endpoints/pricing.md)** - Stream real-time prices and get historical candles
- **[Orders](endpoints/orders.md)** - Place and manage trading orders
- **[Trades](endpoints/trades.md)** - Monitor and close open trades
- **[Positions](endpoints/positions.md)** - Track instrument positions
- **[Transactions](endpoints/transactions.md)** - View transaction history

For hands-on examples, see the [Getting Started Guide](../guides/getting-started.md).
