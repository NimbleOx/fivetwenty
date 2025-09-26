# Multi-Account Configuration

FiveTwenty supports connecting to multiple OANDA accounts simultaneously through custom environment variable prefixes and configuration objects. This guide shows you how to set up and manage multiple accounts in your applications.

## Overview

You can connect to multiple accounts using three different approaches:

1. **Custom Environment Variable Prefixes** - Use different prefixes for different accounts
2. **Direct Configuration Objects** - Create configurations programmatically
3. **Mixed Approach** - Combine environment variables with direct configuration

## Method 1: Custom Environment Variable Prefixes

Set up different prefixes for each account in your environment:

```bash
# Account 1 - Practice environment
export TRADING_BOT_FIVETWENTY_OANDA_TOKEN="practice-token-1"
export TRADING_BOT_FIVETWENTY_OANDA_ACCOUNT="account-id-1"
export TRADING_BOT_FIVETWENTY_OANDA_ENVIRONMENT="practice"

# Account 2 - Live environment
export LIVE_ACCOUNT_FIVETWENTY_OANDA_TOKEN="live-token-2"
export LIVE_ACCOUNT_FIVETWENTY_OANDA_ACCOUNT="account-id-2"
export LIVE_ACCOUNT_FIVETWENTY_OANDA_ENVIRONMENT="live"

# Default account (uses FIVETWENTY_ prefix)
export FIVETWENTY_OANDA_TOKEN="default-token"
export FIVETWENTY_OANDA_ACCOUNT="default-account"
export FIVETWENTY_OANDA_ENVIRONMENT="practice"
```

### Initialize Clients with Custom Prefixes

```python
from fivetwenty import AsyncClient
from fivetwenty.configuration import AccountConfigLoader


async def multi_account_example():
    # Load configurations with custom prefixes
    trading_bot_config = AccountConfigLoader.from_env_prefix("TRADING_BOT_")
    live_account_config = AccountConfigLoader.from_env_prefix("LIVE_ACCOUNT_")
    default_config = AccountConfigLoader.load_default()  # Uses FIVETWENTY_

    # Validate configurations were loaded
    if trading_bot_config is None:
        raise ValueError("TRADING_BOT_ environment variables not found or incomplete")
    if live_account_config is None:
        raise ValueError("LIVE_ACCOUNT_ environment variables not found or incomplete")
    if default_config is None:
        raise ValueError("FIVETWENTY_ environment variables not found or incomplete")

    # Create clients for each account
    async with AsyncClient(config=trading_bot_config) as trading_bot:
        async with AsyncClient(config=live_account_config) as live_client:
            async with AsyncClient(config=default_config) as default_client:

                print(f"Trading Bot: {trading_bot.config.summary()}")
                print(f"Live Account: {live_client.config.summary()}")
                print(f"Default: {default_client.config.summary()}")

                # Use each client for different strategies
                await trading_bot.accounts.get_account(trading_bot.account_id)
                await live_client.accounts.get_account(live_client.account_id)
                await default_client.accounts.get_account(default_client.account_id)
```

### Single Account with Custom Prefix

```python
from fivetwenty import AsyncClient
from fivetwenty.configuration import AccountConfigLoader


async def single_custom_account():
    # Load configuration from MOMENTUM_FIVETWENTY_OANDA_* variables
    momentum_config = AccountConfigLoader.from_env_prefix("MOMENTUM_")

    if momentum_config is None:
        raise ValueError("MOMENTUM_ environment variables not found or incomplete")

    # Initialize client with the loaded configuration
    async with AsyncClient(config=momentum_config) as client:
        print(f"Connected: {client.config.summary()}")

        # Use the client normally
        account = await client.accounts.get_account(client.account_id)
        print(f"Balance: {account.balance} {account.currency}")
```

### Synchronous Client Example

```python
from fivetwenty import Client
from fivetwenty.configuration import AccountConfigLoader


def sync_example():
    # Load configuration for synchronous client
    momentum_config = AccountConfigLoader.from_env_prefix("MOMENTUM_")

    if momentum_config is None:
        raise ValueError("MOMENTUM_ environment variables not found")

    with Client(config=momentum_config) as client:
        account = client.accounts.get_account(client.account_id)
        print(f"Balance: {account.balance} {account.currency}")
```

## Method 2: Direct Configuration Objects

Create configurations programmatically without environment variables:

```python
from pydantic import SecretStr

from fivetwenty import AsyncClient, Environment
from fivetwenty.configuration import AccountConfig


async def direct_config_example():
    # Define multiple account configurations
    configs = [
        AccountConfig(
            token=SecretStr("practice-token-1"),
            account_id=SecretStr("practice-account-1"),
            environment=Environment.PRACTICE,
            alias="strategy_a",
        ),
        AccountConfig(
            token=SecretStr("live-token-1"),
            account_id=SecretStr("live-account-1"),
            environment=Environment.LIVE,
            alias="live_trading",
        ),
    ]

    clients = []
    for config in configs:
        client = AsyncClient(config=config)
        clients.append(client)

    # Use context managers to ensure proper cleanup
    async with clients[0] as strategy_a:
        async with clients[1] as live_trading:
            # Execute different strategies on different accounts
            await strategy_a.accounts.get_account(strategy_a.account_id)
            await live_trading.accounts.get_account(live_trading.account_id)
```

## Method 3: Mixed Approach

Combine environment variables with direct configuration:

```python
from pydantic import SecretStr

from fivetwenty import AsyncClient, Environment
from fivetwenty.configuration import AccountConfig, AccountConfigLoader


async def mixed_approach():
    # Load primary account from default environment variables
    primary_config = AccountConfigLoader.load_default()

    # Load secondary account from custom prefix
    secondary_config = AccountConfigLoader.from_env_prefix("SECONDARY_")

    # Create a third account with direct parameters
    test_config = AccountConfig(
        token=SecretStr("test-token"),
        account_id=SecretStr("test-account"),
        environment=Environment.PRACTICE,
        alias="testing",
    )

    async with AsyncClient(config=primary_config) as primary:
        async with AsyncClient(config=secondary_config) as secondary:
            async with AsyncClient(config=test_config) as test_client:
                # Use different clients for different purposes
                await primary.accounts.get_account(primary.account_id)
                await secondary.accounts.get_account(secondary.account_id)
                await test_client.accounts.get_account(test_client.account_id)
```

## Environment Variable Pattern

The pattern for custom prefixes follows: `{PREFIX}_FIVETWENTY_OANDA_{VARIABLE}`

### Examples:
- **Default**: `FIVETWENTY_OANDA_TOKEN`, `FIVETWENTY_OANDA_ACCOUNT`, etc.
- **Custom**: `MYBOT_FIVETWENTY_OANDA_TOKEN`, `MYBOT_FIVETWENTY_OANDA_ACCOUNT`, etc.

### Required Variables for Each Prefix:

| Variable | Description | Example |
|----------|-------------|---------|
| `{PREFIX}_FIVETWENTY_OANDA_TOKEN` | Your OANDA API token | `MYBOT_FIVETWENTY_OANDA_TOKEN="abc123..."` |
| `{PREFIX}_FIVETWENTY_OANDA_ACCOUNT` | Your OANDA account ID | `MYBOT_FIVETWENTY_OANDA_ACCOUNT="123-456-789"` |
| `{PREFIX}_FIVETWENTY_OANDA_ENVIRONMENT` | Environment: "practice" or "live" | `MYBOT_FIVETWENTY_OANDA_ENVIRONMENT="practice"` |

**Note:** The account alias is automatically generated from your prefix (e.g., `MYBOT_` becomes alias `"mybot"`).

## Best Practices

### Security
- Keep tokens secure using environment variables or secure vaults
- Never hardcode credentials in source code
- Use practice environment for development and testing
- Validate environment before connecting to live accounts

### Organization
- Use descriptive prefixes that match your application structure
- Group related accounts with consistent naming patterns
- Document which accounts are used for which purposes

### Error Handling

Always validate that configurations were loaded successfully:

```python
from fivetwenty import AsyncClient
from fivetwenty.configuration import AccountConfigLoader


async def safe_config_loading():
    # Load configuration with validation
    config = AccountConfigLoader.from_env_prefix("MYBOT_")
    if config is None:
        raise ValueError("MYBOT_ environment variables not found or incomplete")

    # Use the validated configuration
    async with AsyncClient(config=config) as client:
        account = await client.accounts.get_account(client.account_id)
        return account

# Alternative: Handle missing configuration gracefully
async def graceful_config_loading():
    config = AccountConfigLoader.from_env_prefix("OPTIONAL_BOT_")

    if config is None:
        print("Optional bot configuration not found, using default")
        config = AccountConfigLoader.load_default()
        if config is None:
            raise ValueError("No valid configuration found")

    async with AsyncClient(config=config) as client:
        return await client.accounts.get_account(client.account_id)
```

### Resource Management
Always use context managers to ensure proper client cleanup:

```python
import asyncio


async def main():
    # ✅ Correct - ensures cleanup
    async with AsyncClient(config=config) as client:
        await client.accounts.get_account(client.account_id)

    # ❌ Incorrect - may leak resources
    client = AsyncClient(config=config)
    await client.accounts.get_account(client.account_id)

asyncio.run(main())
```

## Real-World Example

Here's a complete example showing how to manage multiple accounts for different trading strategies:

```python
import asyncio
from fivetwenty import AsyncClient
from fivetwenty.configuration import AccountConfigLoader

async def trading_system():
    """Multi-account trading system example."""

    # Load different account configurations
    scalp_config = AccountConfigLoader.from_env_prefix("SCALP_")
    swing_config = AccountConfigLoader.from_env_prefix("SWING_")
    hedge_config = AccountConfigLoader.from_env_prefix("HEDGE_")

    # Validate all configs loaded successfully
    configs = {
        'scalping': scalp_config,
        'swing': swing_config,
        'hedge': hedge_config
    }

    for name, config in configs.items():
        if config is None:
            raise ValueError(f"Configuration for {name} strategy not found. "
                           f"Please set {name.upper()}_FIVETWENTY_OANDA_* environment variables")

    print(f"Loaded configurations:")
    for name, config in configs.items():
        print(f"  {name}: {config.summary()}")

    # Initialize clients and run strategies
    async with AsyncClient(config=scalp_config) as scalp_client, \
               AsyncClient(config=swing_config) as swing_client, \
               AsyncClient(config=hedge_config) as hedge_client:

        print("Starting trading strategies...")

        # Run different strategies concurrently
        await asyncio.gather(
            scalping_strategy(scalp_client),
            swing_strategy(swing_client),
            hedging_strategy(hedge_client)
        )

async def scalping_strategy(client: AsyncClient):
    """High-frequency scalping strategy."""
    try:
        account = await client.accounts.get_account(client.account_id)
        print(f"Scalping on {client.config.alias}: Balance {account.balance} {account.currency}")

        # Your scalping logic here
        # Example: Check current positions, place quick trades, etc.

    except Exception as e:
        print(f"Error in scalping strategy: {e}")

async def swing_strategy(client: AsyncClient):
    """Medium-term swing strategy."""
    try:
        account = await client.accounts.get_account(client.account_id)
        print(f"Swing trading on {client.config.alias}: Balance {account.balance} {account.currency}")

        # Your swing trading logic here
        # Example: Analyze trends, place longer-term trades, etc.

    except Exception as e:
        print(f"Error in swing strategy: {e}")

async def hedging_strategy(client: AsyncClient):
    """Risk management hedging."""
    try:
        account = await client.accounts.get_account(client.account_id)
        print(f"Hedging on {client.config.alias}: Balance {account.balance} {account.currency}")

        # Your hedging logic here
        # Example: Monitor positions, place hedge trades, etc.

    except Exception as e:
        print(f"Error in hedging strategy: {e}")

# Entry point
async def main():
    try:
        await trading_system()
        print("Trading system completed successfully")
    except ValueError as e:
        print(f"Configuration error: {e}")
        print("Please check your environment variables")
    except Exception as e:
        print(f"Unexpected error: {e}")

# Run the trading system
if __name__ == "__main__":
    asyncio.run(main())
```

## Environment Setup Examples

### Shell Script Setup
```bash
#!/bin/bash
# setup-trading-env.sh

# Scalping account (practice)
export SCALP_FIVETWENTY_OANDA_TOKEN="your-scalp-practice-token"
export SCALP_FIVETWENTY_OANDA_ACCOUNT="your-scalp-account-id"
export SCALP_FIVETWENTY_OANDA_ENVIRONMENT="practice"

# Swing trading account (live)
export SWING_FIVETWENTY_OANDA_TOKEN="your-swing-live-token"
export SWING_FIVETWENTY_OANDA_ACCOUNT="your-swing-account-id"
export SWING_FIVETWENTY_OANDA_ENVIRONMENT="live"

# Hedging account (live)
export HEDGE_FIVETWENTY_OANDA_TOKEN="your-hedge-live-token"
export HEDGE_FIVETWENTY_OANDA_ACCOUNT="your-hedge-account-id"
export HEDGE_FIVETWENTY_OANDA_ENVIRONMENT="live"

echo "Trading environment configured"
```

### Docker Environment File
```bash
# .env file for Docker
SCALP_FIVETWENTY_OANDA_TOKEN=your-scalp-token
SCALP_FIVETWENTY_OANDA_ACCOUNT=scalp-account-id
SCALP_FIVETWENTY_OANDA_ENVIRONMENT=practice

SWING_FIVETWENTY_OANDA_TOKEN=your-swing-token
SWING_FIVETWENTY_OANDA_ACCOUNT=swing-account-id
SWING_FIVETWENTY_OANDA_ENVIRONMENT=live
```

This multi-account configuration approach gives you the flexibility to:

- Run different strategies on different accounts
- Separate practice and live trading
- Organize accounts by risk profile or strategy type
- Scale your trading operations across multiple OANDA accounts

Remember to always test your multi-account setup in the practice environment before deploying to live trading accounts.