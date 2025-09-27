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

### 2. Configuration Objects

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

### 3. Environment Variables

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

For local development, install python-dotenv and create a .env file:

```bash
uv add python-dotenv
```

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

You can create as many clients as you need to access different accounts with OANDA. Common scenarios include separating long and short positions to comply with US broker hedging rules, isolating different trading strategies to manage risk, or maintaining separate accounts for testing versus live trading.

For traders subject to US broker hedging rules, using separate long and short accounts provides a compliant way to maintain opposing positions in the same currency pair. This approach allows you to hedge positions without violating FIFO (First In, First Out) rules that prevent holding both long and short positions simultaneously in a single account. The next example shows how you might approach this.

```python
import asyncio
import os
from fivetwenty import AccountConfig, AsyncClient, Environment


async def main():
    # Long account for bullish positions
    long_config = AccountConfig(
        token=os.environ["LONG_ACCOUNT_TOKEN"],
        account_id=os.environ["LONG_ACCOUNT_ID"],
        environment=Environment.LIVE,
        alias="long_positions",
    )

    # Short account for bearish positions
    short_config = AccountConfig(
        token=os.environ["SHORT_ACCOUNT_TOKEN"],
        account_id=os.environ["SHORT_ACCOUNT_ID"],
        environment=Environment.LIVE,
        alias="short_positions",
    )

    # Execute hedged strategy across both accounts
    async with AsyncClient(config=long_config) as long_client:
        async with AsyncClient(config=short_config) as short_client:
            print("Executing hedged strategy across long and short accounts")

            # Open long position in one account
            await execute_long_strategy(long_client)

            # Open short position in separate account for hedging
            await execute_short_strategy(short_client)

async def execute_long_strategy(client: AsyncClient) -> None:
    """Execute bullish strategy on long account."""
    accounts = await client.accounts.get_accounts()
    print(f"Long strategy executed on account: {client.config.alias}")
    print(f"Account count: {len(accounts)}")

async def execute_short_strategy(client: AsyncClient) -> None:
    """Execute bearish strategy on short account."""
    accounts = await client.accounts.get_accounts()
    print(f"Short strategy executed on account: {client.config.alias}")
    print(f"Account count: {len(accounts)}")

asyncio.run(main())
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

Before deploying your application, it's important to verify that your authentication setup works correctly. You can test your configuration in two ways: validate the configuration structure without making API calls, or verify authentication by connecting to OANDA's servers.

### Test Your Authentication Setup

```python
import asyncio
import os

from fivetwenty import AsyncClient, Environment


async def test_authentication():
    """Test OANDA API authentication and configuration."""

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

If you encounter authentication issues, this section provides quick solutions for the most common problems.

### Quick Fixes

**Missing Environment Variables**
```bash
export FIVETWENTY_OANDA_TOKEN="your-api-token"
export FIVETWENTY_OANDA_ACCOUNT="your-account-id"
export FIVETWENTY_OANDA_ENVIRONMENT="practice"
```

**Invalid Token Format**
```python
# Check your token is properly formatted
import os
token = os.environ.get("FIVETWENTY_OANDA_TOKEN", "").strip()
if not token:
    print("❌ Token is empty or missing")
else:
    print(f"✅ Token loaded: {token[:8]}...")
```

**Environment Mismatch**
```python
# Ensure token matches environment
from fivetwenty import AsyncClient, Environment

# Practice token → Practice environment
client = AsyncClient(token=practice_token, environment=Environment.PRACTICE)

# Live token → Live environment
client = AsyncClient(token=live_token, environment=Environment.LIVE)
```

!!! info "Comprehensive Troubleshooting"
    For detailed authentication troubleshooting, debugging tools, network issues, SSL problems, and complete error diagnostics, see [Connection Failure Handling Guide](../../guides/practical-solutions/handle-connection-failures.md#authentication-troubleshooting).

## Summary

You now have a secure, flexible authentication setup for FiveTwenty. The SDK supports multiple authentication methods from direct parameters to environment variables, with automatic secret masking and comprehensive validation. Whether you're using a single account for development or multiple accounts for complex trading strategies, the configuration system scales to meet your needs while maintaining security best practices.

## Next Steps

Now that authentication is configured:

- [Learn about environments](../../guides/understanding/environments.md) to understand practice vs live trading
- [Make your first trade](first-trade.md) to test your setup
- [Review configuration options](../../guides/understanding/configuration.md) for advanced use cases
- [Check error handling](../../api-reference/error-handling.md) for production readiness
