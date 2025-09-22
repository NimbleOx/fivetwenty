# Client API Reference

!!! note "📚 Reference - Information-oriented content"
    **Use this reference when:** You need to look up specific method signatures, parameters, or return values

    **Content type:** Comprehensive technical specifications for quick lookup

    **Assumed knowledge:** Familiarity with FiveTwenty concepts and Python async programming

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
| [accounts](endpoints/accounts.md) | Account management | `list()`, `get()`, `summary()`, `instruments()`, `configure()`, `changes()` |
| [orders](endpoints/orders.md) | Order operations | `post_market_order()`, `post_limit_order()`, `cancel()`, `list_pending()`, `list()`, `replace()` |
| [trades](endpoints/trades.md) | Trade management | `list_open()`, `get()`, `close()`, `modify()`, `list()` |
| [positions](endpoints/positions.md) | Position tracking | `list_open()`, `get()`, `close()`, `list()` |
| [pricing](endpoints/pricing.md) | Market data | `get()`, `stream()`, `candles()`, `latest_candles()` |
| [instruments](endpoints/instruments.md) | Instrument data | `get_all()`, `candles()`, `order_book()` |
| [transactions](endpoints/transactions.md) | Transaction history | `list()`, `get()`, `get_range()`, `stream()`, `list_since()` |

---

## Client Classes

### AsyncClient
Primary async client for OANDA API operations. Recommended for production use.

**Constructor:**
```python
from fivetwenty import AsyncClient, Environment

# Constructor signature:
client = AsyncClient(
    token=str | None,
    account_id=str | None,
    environment=Environment.PRACTICE,
    config=AccountConfig | None,
    timeout=30.0,
    max_retries=3,
    transport=httpx.AsyncClient | None,
    user_agent=str | None,
    proxies=str | None,
    verify=True,
    cert=str | None,
    logger=Optional[Logger] | None
)
```

**Configuration Parameters (choose one approach):**

1. **Configuration Object** (recommended for applications):
   - `config` (AccountConfig) - Pre-configured account settings

2. **Direct Parameters** (basic scripts):
   - `token` (str) - OANDA API token
   - `account_id` (str, optional) - OANDA account ID for convenience
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

```python
from fivetwenty import AsyncClient, Environment

# Environment variables (recommended for deployment)
async with AsyncClient() as client:
    accounts = await client.accounts.list()

# Direct parameters (basic scripts)
async with AsyncClient(
    token="your-token",
    environment=Environment.PRACTICE
) as client:
    accounts = await client.accounts.list()

# Configuration object (structured applications)
from fivetwenty import AccountConfig

config = AccountConfig(
    token="your-token",
    account_id="your-account-id",
    environment=Environment.PRACTICE,
    alias="production_trading"
)

async with AsyncClient(config=config) as client:
    print(f"Trading on: {client.config.summary()}")
    accounts = await client.accounts.list()
```

**Configuration Priority:**
When multiple configuration sources are provided:
1. `config` parameter (highest priority)
2. Direct parameters (`token`, `account_id`, etc.)
3. Environment variables (lowest priority)

**Properties:**

- `account_id` (str | None) - Configured account ID
- `config` (AccountConfig | None) - Account configuration object
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
Client(**kwargs)
```

**Parameters:**

- Accepts all the same parameters as async client

**Usage Examples:**

```python
# Environment variables
with Client() as client:
    accounts = client.accounts.list()

# Direct parameters
with Client(
    token="your-token",
    environment=Environment.PRACTICE
) as client:
    accounts = client.accounts.list()

# Configuration object
config = AccountConfig(...)
with Client(config=config) as client:
    print(f"Using: {client.config.summary()}")
    accounts = client.accounts.list()
```

**Properties:**

- `account_id` (str | None) - Configured account ID
- `config` (AccountConfig | None) - Account configuration object
- Same endpoint structure as async client, but with synchronous methods

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
```python
config = AccountConfig(
    token="your_token",
    account_id="your_account_id",
    environment=Environment.PRACTICE,
    alias="my_config",
)
```

**Parameters:**

- `token` - OANDA API token (automatically protected)
- `account_id` - OANDA account ID (automatically protected)
- `environment` - Environment.PRACTICE or Environment.LIVE
- `alias` - User-friendly identifier (valid Python identifier)
- `description` - Optional human-readable description

**Security Features:**

- Automatically masks `token` and `account_id` in string representations
- Validates alias format (must be valid identifier)
- Prevents logging of sensitive credentials

**Methods:**

- `summary()` → str - Safe summary for logs ("alias (environment)")

**Example:**
```python
config = AccountConfig(
    token="your-api-token",
    account_id="your-account-id",
    environment=Environment.PRACTICE,
    alias="demo_trading",

)

print(config.summary())  # "demo_trading (practice)"
print(repr(config))      # Secrets are masked as '***'
```

### Environment Variable Loading

**Standard Variables:**

- `FIVETWENTY_OANDA_TOKEN` - API token
- `FIVETWENTY_OANDA_ACCOUNT` - Account ID
- `FIVETWENTY_OANDA_ENVIRONMENT` - "practice" or "live"
- `FIVETWENTY_OANDA_ACCOUNT_ALIAS` - Account alias

**Custom Prefixes:**
```python
from fivetwenty import AccountConfigLoader

# Load with custom prefix
config = AccountConfigLoader.from_env_prefix("TRADING_")
# Loads from TRADING_OANDA_TOKEN, TRADING_OANDA_ACCOUNT, etc.
```

## Error Handling

### Configuration Errors

**ValueError**: Raised when no valid configuration is provided:
```python
from fivetwenty import AsyncClient, Environment

try:
    client = AsyncClient()  # No config provided
except ValueError as e:
    print("Set FIVETWENTY_OANDA_TOKEN environment variable or pass token parameter")
```

**ValidationError**: Raised for invalid configuration values:
```python
from pydantic import ValidationError

try:
    config = AccountConfig(
        token="",  # Empty token
        account_id="account",
        environment=Environment.PRACTICE,
        alias="123invalid"  # Invalid alias
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
```python
from fivetwenty.exceptions import FiveTwentyError

try:
    trade = await client.trades.get(client.account_id, "invalid_id")
except FiveTwentyError as e:
    print(f"Error {e.status_code}: {e.message}")
    if e.error_code == "TRADE_NOT_FOUND":
        # Handle specific error
        pass
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
- URL: `https://api-fxpractice.oanda.com/v3`
- Virtual money only
- Same API functionality as live
- Reset account balances available
- No trading restrictions

### Live Environment
- URL: `https://api-fxtrade.oanda.com/v3`
- Real money trading
- Risk management essential
- Requires live trading account
- Subject to margin requirements

**Security Best Practices:**

1. **Credential Protection:**
   - Never commit tokens to version control
   - Use environment variables or secure vaults for credentials
   - Rotate tokens regularly
   - Use separate tokens for practice and live environments

2. **Configuration Validation:**
   - Always validate configuration before deployment
   - Use structured `AccountConfig` objects in applications
   - Test authentication before starting trading operations

3. **Environment Separation:**
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

```python
# Load configurations
momentum_config = AccountConfigLoader.from_env_prefix("STRATEGY_A_")
grid_config = AccountConfigLoader.from_env_prefix("STRATEGY_B_")
```