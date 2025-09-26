# Authentication

The FiveTwenty library provides secure, flexible authentication for OANDA's API. This guide covers obtaining API tokens and configuring authentication securely.

## Getting Your API Token

To use the FiveTwenty library, you need an OANDA API access token:

1. **Practice Account**: Sign up at [OANDA](https://www.oanda.com) (free practice accounts available)
2. **Live Account**: Available to funded accounts at [OANDA](https://www.oanda.com)

### Finding Your Token

1. Log into your OANDA account
2. Navigate to **Manage API Access** in your account settings
3. Generate a new token or use an existing one
4. Copy the token securely

!!! warning "Security"
    Never commit your API token to version control! The library provides secure configuration options to protect your credentials.

## Authentication Methods

The FiveTwenty library supports three secure authentication approaches:

### 1. Direct Parameters

```python
import asyncio

from fivetwenty import AsyncClient, Environment

async def main():
    async with AsyncClient(
        token="your-api-token",
        account_id="your-account-id",  # Required parameter
        environment=Environment.PRACTICE
    ) as client:
        accounts = await client.accounts.get_accounts()
        account_count = len(accounts)
        print(f"Found {account_count} accounts")

# Run the async function
asyncio.run(main())
```

### 2. Configuration Objects (Recommended)

Apporpriate for running multiple clients connected to multiple accounts within the same logic (for example a short account and a long account):

```python
from fivetwenty import AccountConfig, AsyncClient, Environment

# Create secure configuration

config = AccountConfig(
    token="your-api-token",
    account_id="your-account-id",
    environment=Environment.PRACTICE,
)

# Use configuration
async with AsyncClient(config=config) as client:
    accounts = await client.accounts.get_accounts()
    account_count = len(accounts)
    print(f"Using account: {client.config.summary()}")
    print(f"Retrieved {account_count} accounts")
```

### 3. Environment Variables (Deployment)

For Docker, Kubernetes, and CI/CD:

```bash
# Set environment variables (in your shell etc).
export FIVETWENTY_OANDA_TOKEN="your-api-token"
export FIVETWENTY_OANDA_ACCOUNT="your-account-id"
export FIVETWENTY_OANDA_ENVIRONMENT="practice"
# Configuration is loaded automatically when these are set
```

```python
import asyncio


async def main():
    from fivetwenty import AsyncClient

    # Zero-config - automatically loads environment variables
    async with AsyncClient() as client:
        accounts = await client.accounts.get_accounts()
        account_count = len(accounts)
        print(f"Loaded config: {client.config.summary()}")
        print(f"Retrieved {account_count} accounts")

asyncio.run(main())
```

## Secure Token Management

### Environment Variables (Recommended)

Never hardcode tokens. Use environment variables:

**❌ Bad - Never do this:**
```python
token = "abc123def456"  # NEVER hardcode tokens!
```

**✅ Good - Use environment variables:**
```python
import os

token = os.environ.get("FIVETWENTY_OANDA_TOKEN")
if not token:
    raise ValueError("FIVETWENTY_OANDA_TOKEN not set")
print(f"Token loaded from environment: {'*' * min(8, len(token))}...")
```

### Using .env Files

For local development:

```bash
# .env file (add to .gitignore!)
FIVETWENTY_OANDA_TOKEN=your-practice-token
FIVETWENTY_OANDA_ACCOUNT=your-account-id
FIVETWENTY_OANDA_ENVIRONMENT=practice
FIVETWENTY_OANDA_ACCOUNT_ALIAS=development_account
```

```python
import asyncio


async def main():
    from dotenv import load_dotenv

    from fivetwenty import AsyncClient

    # Load .env file
    load_dotenv()
    print("Environment variables loaded from .env file")

    # Automatically uses environment variables
    async with AsyncClient() as client:
        accounts = await client.accounts.get_accounts()
        print(f"Environment variables loaded: {len(accounts)} accounts found")

asyncio.run(main())
```

### Secret Management Systems

For production deployments, you can use AWS Secrets Manager, HashiCorp Vault, Kubernetes Secrets, etc. to set environment variables as appropriate.


## Multiple Account Configuration

### Different Environments

```python
import asyncio
import os
from fivetwenty import AccountConfig, AsyncClient, Environment


async def main():

    # Practice account for testing
    practice_config = AccountConfig(
        token=os.environ["PRACTICE_TOKEN"],
        account_id=os.environ["PRACTICE_ACCOUNT"],
        environment=Environment.PRACTICE,
        alias="practice_testing",
    )

    # Live account for production
    live_config = AccountConfig(
        token=os.environ["LIVE_TOKEN"],
        account_id=os.environ["LIVE_ACCOUNT"],
        environment=Environment.LIVE,
        alias="live_trading",
    )

    # Test strategy on practice first
    async with AsyncClient(config=practice_config) as practice_client:
        print(f"Testing strategy on practice account: {practice_config.alias}")
        await test_strategy(practice_client)

    # Deploy to live after validation
    async with AsyncClient(config=live_config) as live_client:
        print(f"Executing live trades on account: {live_config.alias}")
        await execute_live_trades(live_client)

async def test_strategy(client: AsyncClient) -> None:
    """Test trading strategy on practice account."""
    accounts = await client.accounts.get_accounts()
    print(f"Strategy test completed with {len(accounts)} accounts")

async def execute_live_trades(client: AsyncClient) -> None:
    """Execute live trading operations."""
    accounts = await client.accounts.get_accounts()
    print(f"Live trading executed with {len(accounts)} accounts")

asyncio.run(main())
```

### Multiple Strategies

Use environment variable prefixes for different strategies:

```bash
# Momentum strategy
export MOMENTUM_OANDA_TOKEN="momentum-strategy-token"
export MOMENTUM_OANDA_ACCOUNT="momentum-account"
export MOMENTUM_OANDA_ENVIRONMENT="practice"
export MOMENTUM_OANDA_ACCOUNT_ALIAS="momentum_strategy"

# Grid strategy
export GRID_OANDA_TOKEN="grid-strategy-token"
export GRID_OANDA_ACCOUNT="grid-account"
export GRID_OANDA_ENVIRONMENT="practice"
export GRID_OANDA_ACCOUNT_ALIAS="grid_strategy"
```

```python
import asyncio
from fivetwenty import AccountConfigLoader, AsyncClient

# Load configurations with custom prefixes
momentum_config = AccountConfigLoader.from_env_prefix("MOMENTUM_")
grid_config = AccountConfigLoader.from_env_prefix("GRID_")
print(f"Loaded momentum config: {momentum_config.summary()}")
print(f"Loaded grid config: {grid_config.summary()}")

# Run strategies in parallel
async with AsyncClient(config=momentum_config) as momentum_client:
    async with AsyncClient(config=grid_config) as grid_client:
        print("Starting parallel strategies...")
        results = await asyncio.gather(
            run_momentum_strategy(momentum_client),
            run_grid_strategy(grid_client)
        )
        print(f"Parallel strategies completed: {len(results)} results")

async def run_momentum_strategy(client: AsyncClient) -> str:
    """Run momentum trading strategy."""
    accounts = await client.accounts.get_accounts()
    print(f"Momentum strategy running with {len(accounts)} accounts")
    return "momentum_complete"

async def run_grid_strategy(client: AsyncClient) -> str:
    """Run grid trading strategy."""
    accounts = await client.accounts.get_accounts()
    print(f"Grid strategy running with {len(accounts)} accounts")
    return "grid_complete"
```

## Security Features

### Automatic Secret Masking

The library automatically protects sensitive information:

```python
from fivetwenty import AccountConfig, Environment

config = AccountConfig(
    token="your-api-token-here",
    account_id="secret-account-123",
    environment=Environment.PRACTICE,
    alias="my_account",
)

# Secrets are automatically masked in logs
config_repr = repr(config)
print(config_repr)
# AccountConfig(alias='my_account', environment=practice, token=SecretStr('***'), account_id=SecretStr('***'))

# Safe summary for monitoring
summary = config.summary()
print(summary)
# my_account (practice)
```

### Configuration Validation

The library validates all configuration values:

```python
from pydantic import ValidationError

from fivetwenty import AccountConfig, Environment

try:
    config = AccountConfig(
        token="   ",  # Empty token - rejected
        account_id="123-456-789",
        environment=Environment.PRACTICE,
        alias="my_account",
    )
    print(f"Unexpected success: {config}")
except ValidationError as e:
    print(f"Invalid configuration (expected): {e}")

try:
    config = AccountConfig(
        token="valid-token",
        account_id="valid-account",
        environment=Environment.PRACTICE,
        alias="123invalid",  # Invalid alias - starts with number
    )
    print(f"Unexpected success: {config}")
except ValidationError as e:
    print(f"Invalid alias (expected): {e}")
```

## Testing Authentication

### Verify Configuration

```python
import asyncio
import os

from fivetwenty import AsyncClient, Environment


async def test_authentication():
    """Test OANDA API authentication."""

    try:
        async with AsyncClient(
            token=os.environ["FIVETWENTY_OANDA_TOKEN"],
            environment=Environment.PRACTICE,
        ) as client:
            # Test authentication by listing accounts
            accounts = await client.accounts.get_accounts()
            account_count = len(accounts)

            print("✅ Authentication successful!")
            print(f"Configuration: {client.config.summary()}")
            print(f"Found {account_count} account(s):")

            for account in accounts:
                account_info = f"{account.id}: {account.alias}"
                balance_info = f"{account.balance} {account.currency}"
                print(f"  • {account_info}")
                print(f"    Balance: {balance_info}")

    except Exception as e:
        print(f"❌ Authentication failed: {e}")
        print("Check your token and environment configuration")

# Run test
asyncio.run(test_authentication())
```

### Validate Configuration

```python
import os

from fivetwenty import AccountConfig, ConfigValidator, Environment

# Create configuration
config = AccountConfig(
    token=os.environ["FIVETWENTY_OANDA_TOKEN"],
    account_id=os.environ["FIVETWENTY_OANDA_ACCOUNT"],
    environment=Environment.PRACTICE,
    alias="test_account",
)

# Validate configuration
errors = ConfigValidator.validate_account_config(config)
error_count = len(errors) if errors else 0

if errors:
    print(f"Configuration errors ({error_count}):")
    for error in errors:
        print(f"  • {error}")
else:
    print("✅ Configuration is valid")
```

## Security Considerations

Always follow these critical security guidelines:

- **Never commit tokens to version control** - Use environment variables
- **Use separate tokens for different environments** - Practice vs live
- **Validate configurations before deployment** - Catch issues early

!!! tip "Comprehensive Security Guide"
    For complete security best practices, token rotation strategies, and production deployment patterns, see [Best Practices Guide](../../guides/understanding/best-practices.md).

!!! info "Advanced Configuration"
    For environment-specific settings, organizational patterns, and performance optimization, see [Configuration Guide](../../guides/understanding/configuration.md).

## Troubleshooting

### Common Authentication Errors
```python
from fivetwenty import AsyncClient, Environment

# Error: Missing token
try:
    client = AsyncClient()  # No token or env vars
    print(f"Unexpected success: {client}")
except ValueError as e:
    print(f"Configuration error (expected): {e}")
    # Fix: Set FIVETWENTY_OANDA_TOKEN environment variable

# Error: Invalid token format
try:
    client = AsyncClient(token="invalid-token")
    accounts = await client.accounts.get_accounts()
    print(f"Unexpected success: {len(accounts)} accounts")
except Exception as e:
    print(f"Authentication error (expected): {e}")
    # Fix: Get valid token from OANDA account settings

# Error: Wrong environment
try:
    client = AsyncClient(
        token="practice-token",
        environment=Environment.LIVE  # Wrong environment
    )
    accounts = await client.accounts.get_accounts()
    print(f"Unexpected success: {len(accounts)} accounts")
except Exception as e:
    print(f"Environment error (expected): {e}")
    # Fix: Use correct environment for your token
```

### Debug Authentication Issues

```python
from fivetwenty import AsyncClient, Environment

# Check configuration
client = AsyncClient(token="your-token", environment=Environment.PRACTICE)
config = client.config

print(f"Environment: {config.environment.value}")
print(f"Account ID: {client.account_id}")
print(f"Config summary: {config.summary()}")

# Validate manually
from fivetwenty import ConfigValidator

errors = ConfigValidator.validate_account_config(config)
if errors:
    print(f"Configuration issues ({len(errors)}): {errors}")
else:
    print("Configuration is valid")
```

### Rate Limiting

If you encounter rate limits:

- Use the SDK's built-in retry mechanism
- Implement exponential backoff
- Cache frequently accessed data
- Monitor your request patterns

```python
from fivetwenty import AsyncClient, Environment

# Configure retries for rate limiting
async with AsyncClient(
    token="your-token",
    environment=Environment.PRACTICE,
    max_retries=5,  # Increase retries
    timeout=60.0    # Increase timeout
) as client:
    accounts = await client.accounts.get_accounts()
    print(f"Retrieved {len(accounts)} accounts with retry configuration")
```

## Next Steps

Now that authentication is configured:

- [Learn about environments](environments.md) to understand practice vs live trading
- [Make your first trade](first-trade.md) to test your setup
- [Review configuration options](../../guides/understanding/configuration.md) for advanced use cases
- [Check error handling](../../api-reference/error-handling.md) for production readiness
