# Configuration

The FiveTwenty library provides flexible configuration options to manage your OANDA API credentials and client settings securely. This guide covers all configuration patterns and advanced options.

## Overview

The library supports three main configuration approaches:

1. **Direct parameters** - Straightforward and explicit
2. **Configuration objects** - Structured and reusable
3. **Environment variables** - Zero-config deployment

All approaches prioritize security by automatically masking sensitive information in logs and output.

## Environment Concepts

OANDA provides two distinct environments for trading: **Practice** and **Live**. Understanding the differences is crucial for safe development and trading.

### Environment Overview

| Feature | Practice Environment | Live Environment |
|---------|---------------------|------------------|
| **Real Money** | No (virtual funds) | Yes (real funds) |
| **API Endpoint** | api-fxpractice.oanda.com | api-fxtrade.oanda.com |
| **Market Data** | Real-time | Real-time |
| **Execution** | Simulated | Real market |
| **Risk** | None | Real financial risk |
| **Use Case** | Testing & Learning | Production Trading |

### Practice Environment

The practice environment is designed for safe development and learning:

- **Virtual Funds**: Start with $100,000 in virtual money
- **Real Market Data**: Access to live market prices for realistic testing
- **Full API Access**: All OANDA API features available
- **No Risk**: No real money at stake
- **Reset Available**: Can reset account balance anytime
- **No KYC Required**: Instant setup with just email verification

**Ideal for:**
- Learning the OANDA platform and API
- Testing and developing trading strategies
- Code development and debugging
- Paper trading competitions
- Training new traders

### Live Environment

The live environment is for real money trading:

- **Real Money**: All transactions involve actual funds
- **Market Execution**: Orders executed in real market conditions
- **Full Trading Features**: Access to all OANDA trading capabilities
- **Permanent Results**: Profits and losses are real and permanent

**Requirements:**
- Funded OANDA account
- Completed KYC (Know Your Customer) verification
- Understanding of trading risks
- Production-ready, thoroughly tested code

**Critical Safety Considerations:**
- Always test thoroughly in practice before deploying to live
- Implement proper risk management and position sizing
- Use stop losses and take profits
- Monitor account balance and margin requirements
- Have emergency procedures for stopping trading

### Environment URLs

The SDK automatically routes requests to the correct endpoints:

```python
from fivetwenty import Environment

# Practice environment
print(Environment.PRACTICE.base_url)
# Output: https://api-fxpractice.oanda.com/v3

# Live environment
print(Environment.LIVE.base_url)
# Output: https://api-fxtrade.oanda.com/v3
```

### Development Workflow

**Recommended development flow:**

1. **Develop in Practice**: Write and test all code in practice environment
2. **Validate Strategy**: Thoroughly test trading strategy with virtual funds
3. **Code Review**: Review code for security, error handling, and risk management
4. **Gradual Deployment**: Start with small position sizes in live environment
5. **Monitor and Scale**: Monitor performance before increasing position sizes

## Quick Start

### Direct Parameters

The simplest way to configure the client:

```python
import asyncio
import os
from fivetwenty import AsyncClient, Environment


async def main() -> None:
    async with AsyncClient(
        token=os.environ.get("FIVETWENTY_OANDA_TOKEN", "your-api-token"),
        environment=Environment.PRACTICE
    ) as client:
        accounts = await client.accounts.get_accounts()
        print(f"Found {len(accounts)} accounts")

if __name__ == "__main__":
    asyncio.run(main())
```

### Configuration Objects

For more structured configuration:

```python
import asyncio
import os
from fivetwenty import AccountConfig, AsyncClient, Environment


async def main() -> None:
    # Create configuration
    config = AccountConfig(
        token=os.environ.get("FIVETWENTY_OANDA_TOKEN", "your-api-token"),
        account_id=os.environ.get("FIVETWENTY_OANDA_ACCOUNT", "your-account-id"),
        environment=Environment.PRACTICE,
        alias="my_trading_account",
    )

    # Use configuration
    async with AsyncClient(config=config) as client:
        accounts = await client.accounts.get_accounts()
        print(f"Found {len(accounts)} accounts")

if __name__ == "__main__":
    asyncio.run(main())
```

### Environment Variables

For deployment and CI/CD:

```bash
# Set environment variables
export FIVETWENTY_OANDA_TOKEN="your-api-token"
export FIVETWENTY_OANDA_ACCOUNT="your-account-id"
export FIVETWENTY_OANDA_ENVIRONMENT="practice"
export FIVETWENTY_OANDA_ACCOUNT_ALIAS="my_account"
```

```python
import asyncio
import os
from fivetwenty import AsyncClient, Environment


async def main() -> None:
    # No configuration needed - loads automatically
    async with AsyncClient(
        token=os.environ.get("FIVETWENTY_OANDA_TOKEN", "demo-token"),
        environment=Environment.PRACTICE
    ) as client:
        accounts = await client.accounts.get_accounts()
        print(f"Found {len(accounts)} accounts")

if __name__ == "__main__":
    asyncio.run(main())
```

## Configuration Patterns

### 1. Direct Parameters Pattern

Best for: Basic scripts, getting started, testing

```python
import asyncio
import os
from fivetwenty import AsyncClient, Environment


async def main() -> None:
    # Minimal configuration
    async with AsyncClient(
        token=os.environ.get("FIVETWENTY_OANDA_TOKEN", "demo-token"),
        environment=Environment.PRACTICE
    ) as client:
        print(f"Connected: {client.config.summary()}")

    # With optional account ID for convenience
    async with AsyncClient(
        token=os.environ.get("FIVETWENTY_OANDA_TOKEN", "demo-token"),
        account_id=os.environ.get("FIVETWENTY_OANDA_ACCOUNT", "demo-account"),
        environment=Environment.LIVE
    ) as client:
        print(f"Connected: {client.config.summary()}")

    # With additional client options
    async with AsyncClient(
        token=os.environ.get("FIVETWENTY_OANDA_TOKEN", "demo-token"),
        environment=Environment.PRACTICE,
        timeout=60.0,
        max_retries=5,
        user_agent="MyTradingBot/1.0"
    ) as client:
        print(f"Connected: {client.config.summary()}")

if __name__ == "__main__":
    asyncio.run(main())
```

### 2. Configuration Objects Pattern

Best for: Production applications, multiple accounts, reusable configurations

```python
import asyncio
import os
from fivetwenty import AccountConfig, AsyncClient, Environment


async def main() -> None:
    # Create reusable configurations
    practice_config = AccountConfig(
        token=os.environ.get("PRACTICE_OANDA_TOKEN", "practice-token"),
        account_id=os.environ.get("PRACTICE_OANDA_ACCOUNT", "practice-account-123"),
        environment=Environment.PRACTICE,
        alias="practice_trading",
    )

    live_config = AccountConfig(
        token=os.environ.get("LIVE_OANDA_TOKEN", "live-token"),
        account_id=os.environ.get("LIVE_OANDA_ACCOUNT", "live-account-456"),
        environment=Environment.LIVE,
        alias="live_trading",
    )

    # Use configurations
    async with AsyncClient(config=practice_config) as practice_client:
        # Test strategies safely
        accounts = await practice_client.accounts.get_accounts()
        print("Practice accounts:", len(accounts))

    async with AsyncClient(config=live_config) as live_client:
        # Execute live trades
        accounts = await live_client.accounts.get_accounts()
        print("Live accounts:", len(accounts))


if __name__ == "__main__":
    asyncio.run(main())
```

### 3. Environment Variables Pattern

Best for: Docker deployments, Kubernetes, CI/CD, serverless

#### Standard Environment Variables

The library automatically loads these environment variables:

| Variable | Description | Example |
|----------|-------------|---------|
| `FIVETWENTY_OANDA_TOKEN` | OANDA API token | `your-api-token` |
| `FIVETWENTY_OANDA_ACCOUNT` | OANDA account ID | `123-456-789` |
| `FIVETWENTY_OANDA_ENVIRONMENT` | Environment (practice/live) | `practice` |
| `FIVETWENTY_OANDA_ACCOUNT_ALIAS` | Account alias | `my_trading_account` |
```python
import asyncio
import os
from fivetwenty import AsyncClient, Environment


async def main() -> None:
    # Automatically loads FIVETWENTY_* variables
    async with AsyncClient(
        token=os.environ.get("FIVETWENTY_OANDA_TOKEN", "demo-token"),
        environment=Environment.PRACTICE
    ) as client:
        accounts = await client.accounts.get_accounts()
        print(f"Found {len(accounts)} accounts")

if __name__ == "__main__":
    asyncio.run(main())
```

#### Custom Environment Variable Prefixes

For multiple accounts or microservices:

```python
import asyncio
from fivetwenty import AccountConfigLoader, AsyncClient


async def main() -> None:
    # Load with custom prefix
    momentum_config = AccountConfigLoader.from_env_prefix("MOMENTUM_")
    grid_config = AccountConfigLoader.from_env_prefix("GRID_")

    # Use different clients for different strategies
    async def run_strategies() -> None:
        async with AsyncClient(config=momentum_config) as momentum_client:
            async with AsyncClient(config=grid_config) as grid_client:
                # Example parallel strategy execution
                accounts1 = await momentum_client.accounts.get_accounts()
                accounts2 = await grid_client.accounts.get_accounts()
                print(f"Momentum accounts: {len(accounts1)}, Grid accounts: {len(accounts2)}")

    # Run the strategies
    await run_strategies()

if __name__ == "__main__":
    asyncio.run(main())
```

Environment variables for custom prefixes:
```bash
# Momentum strategy
export MOMENTUM_OANDA_TOKEN="momentum-token"
export MOMENTUM_OANDA_ACCOUNT="momentum-account"
export MOMENTUM_OANDA_ENVIRONMENT="practice"
export MOMENTUM_OANDA_ACCOUNT_ALIAS="momentum_strategy"

# Grid strategy
export GRID_OANDA_TOKEN="grid-token"
export GRID_OANDA_ACCOUNT="grid-account"
export GRID_OANDA_ENVIRONMENT="practice"
export GRID_OANDA_ACCOUNT_ALIAS="grid_strategy"
```

## Configuration Priority

When multiple configuration methods are used, the priority is:

1. **Configuration object** (highest priority)
2. **Direct parameters**
3. **Environment variables** (lowest priority)
```python
import asyncio
import os
from fivetwenty import AsyncClient, AccountConfig, Environment


async def main() -> None:
    # Config object takes priority over direct parameters
    config = AccountConfig(
        token=os.environ.get("CONFIG_TOKEN", "config-token"),
        account_id=os.environ.get("CONFIG_ACCOUNT", "account-id"),
        environment=Environment.PRACTICE
    )
    async with AsyncClient(
        token="direct-token",  # Ignored
        config=config,  # Used
    ) as client:
        print(f"Connected: {client.config.summary()}")

    # Direct parameters take priority over environment variables
    # (assuming FIVETWENTY_OANDA_TOKEN is set)
    async with AsyncClient(
        token="direct-token",  # Used instead of FIVETWENTY_OANDA_TOKEN
        environment=Environment.PRACTICE
    ) as client:
        print(f"Connected: {client.config.summary()}")

if __name__ == "__main__":
    asyncio.run(main())
```

## Security Features

### Automatic Secret Masking

The library automatically protects sensitive information:

```python
import asyncio
import os
from fivetwenty import AccountConfig, AsyncClient, Environment


async def main() -> None:
    config = AccountConfig(
        token=os.environ.get("SECRET_TOKEN", "super-secret-token"),
        account_id=os.environ.get("SECRET_ACCOUNT", "secret-account-123"),
        environment=Environment.PRACTICE,
        alias="my_account",
    )

    # Secrets are automatically masked
    print(repr(config))
    # AccountConfig(alias='my_account', environment=practice, token=SecretStr('***'), account_id=SecretStr('***'))

    # Safe for logs
    print(config.summary())
    # my_account (practice)

    # Access configuration safely
    async with AsyncClient(config=config) as client:
        print(f"Using account: {client.account_id}")
        # Using account: secret-account-123

if __name__ == "__main__":
    asyncio.run(main())
```

### Validation

The library validates configuration values:

```python
import os
from pydantic import ValidationError
from fivetwenty import AccountConfig, Environment

# Invalid alias (starts with number)
try:
    config = AccountConfig(
        token=os.environ.get("TEST_TOKEN", "token"),
        account_id=os.environ.get("TEST_ACCOUNT", "account"),
        environment=Environment.PRACTICE,
        alias="123invalid",  # Error!
    )
except ValidationError:
    print("Alias must be a valid identifier")

# Empty tokens are rejected
try:
    config = AccountConfig(
        token="   ",  # Whitespace-only token
        account_id=os.environ.get("TEST_ACCOUNT", "account"),
        environment=Environment.PRACTICE,
        alias="valid_alias",
    )
except ValidationError:
    print("Token cannot be empty")
```

### Configuration Validation

Use the validator to check configuration:

```python
import os
from fivetwenty import ConfigValidator, AccountConfig, Environment

config = AccountConfig(
    token=os.environ.get("YOUR_TOKEN", "your-token"),
    account_id=os.environ.get("YOUR_ACCOUNT", "your-account-id"),
    environment=Environment.PRACTICE
)
errors = ConfigValidator.validate_account_config(config)

if errors:
    for error in errors:
        print(f"Configuration error: {error}")
else:
    print("Configuration is valid")
```

## Advanced Client Configuration

### HTTP Client Options

```python
import asyncio
import os
from fivetwenty import AsyncClient, Environment


async def main() -> None:
    # Custom HTTP client configuration
    async with AsyncClient(
        token=os.environ.get("YOUR_TOKEN", "your-token"),
        environment=Environment.PRACTICE,
        timeout=60.0,
        max_retries=5,
        user_agent="MyTradingApp/1.0",
        proxies="http://proxy.example.com:8080",
        verify=True,  # or "/path/to/ca-bundle.crt"
        cert="/path/to/client-cert.pem"
    ) as client:
        print(f"Connected: {client.config.summary()}")

if __name__ == "__main__":
    asyncio.run(main())
```

### Custom HTTP Transport

For advanced HTTP configuration:

```python
import asyncio
import os

import httpx

from fivetwenty import AsyncClient, Environment


async def main() -> None:

    # Create custom transport
    transport = httpx.AsyncClient(
        base_url=Environment.PRACTICE.base_url,
        timeout=httpx.Timeout(
            connect=5.0,
            read=60.0,
            write=10.0,
            pool=60.0,
        ),
        limits=httpx.Limits(
            max_connections=100,
            max_keepalive_connections=20,
        ),
        http2=False,
        trust_env=True,
    )

    # Use with client
    async with AsyncClient(
        token=os.environ.get("YOUR_TOKEN", "your-token"),
        environment=Environment.PRACTICE,
        transport=transport,
    ) as client:
        print(f"Client configured: {client.config.environment}")

asyncio.run(main())
```

### Logging Configuration

```python
import asyncio
import logging
import os
from fivetwenty import AsyncClient, Environment


async def main() -> None:
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("my_trading_app")

    # Pass logger to client
    async with AsyncClient(
        token=os.environ.get("YOUR_TOKEN", "your-token"),
        environment=Environment.PRACTICE,
        logger=logger
    ) as client:
        # Client operations will be logged
        accounts = await client.accounts.get_accounts()
        print(f"Found {len(accounts)} accounts")

if __name__ == "__main__":
    asyncio.run(main())
```

## Sync Client Configuration

The sync `Client` supports the same configuration patterns:

```python
import os
from fivetwenty import Client, AccountConfig, Environment

# Direct parameters
with Client(
    token=os.environ.get("YOUR_TOKEN", "your-token"),
    environment=Environment.PRACTICE
) as client:
    accounts = client.accounts.get_accounts()
    print(f"Found {len(accounts)} accounts")

# Configuration object
config = AccountConfig(
    token=os.environ.get("YOUR_TOKEN", "your-token"),
    account_id=os.environ.get("YOUR_ACCOUNT", "your-account"),
    environment=Environment.PRACTICE,
    alias="example_config"
)
with Client(config=config) as client:
    accounts = client.accounts.get_accounts()
    print(f"Found {len(accounts)} accounts")

# Environment variables
with Client(
    token=os.environ.get("FIVETWENTY_OANDA_TOKEN", "demo-token"),
    environment=Environment.PRACTICE
) as client:  # Loads from FIVETWENTY_* variables
    accounts = client.accounts.get_accounts()
    print(f"Found {len(accounts)} accounts")
```

## Configuration Management Utilities

### Configuration Builder

```python
import json
import os
from fivetwenty import AccountConfig, Environment


class ConfigBuilder:
    """Helper to build configurations from various sources."""

    @staticmethod
    def from_vault(vault_client: Any, secret_path: str, environment: str) -> AccountConfig:
        """Load configuration from HashiCorp Vault."""
        secret = vault_client.secrets.kv.v2.read_secret_version(
            path=secret_path,
            mount_point="secret",
        )

        data = secret["data"]["data"]

        return AccountConfig(
            token=data["token"],
            account_id=data["account_id"],
            environment=Environment.PRACTICE if environment == "practice" else Environment.LIVE,
            alias=data.get("alias", "vault_account"),
            description=data.get("description"),
        )

    @staticmethod
    def from_json_file(file_path: str) -> AccountConfig:
        """Load configuration from JSON file (non-secret data only)."""
        with open(file_path, 'r') as f:
            data = json.load(f)

        return AccountConfig(
            token=os.environ["FIVETWENTY_OANDA_TOKEN"],  # From environment
            account_id=os.environ["FIVETWENTY_OANDA_ACCOUNT"],  # From environment
            environment=Environment(data["environment"]),
            alias=data["alias"],
            description=data.get("description"),
        )
```

### Multi-Environment Manager

```python
import os
from typing import Any, Optional
from fivetwenty import AccountConfig, AccountConfigLoader, AsyncClient


class ConfigManager:
    """Manage configurations for multiple environments."""

    def __init__(self) -> None:
        self.configs: dict[str, AccountConfig] = {}
        self._load_configs()

    def _load_configs(self) -> None:
        """Load configurations for all environments."""
        environments = ["development", "staging", "production"]

        for env in environments:
            prefix = f"{env.upper()}_FIVETWENTY_"
            config = AccountConfigLoader.from_env_prefix(prefix)
            if config:
                self.configs[env] = config

    def get_config(self, environment: str) -> AccountConfig | None:
        """Get configuration for environment."""
        return self.configs.get(environment)

    def get_client(self, environment: str) -> AsyncClient:
        """Get client for environment."""
        config = self.get_config(environment)
        if not config:
            raise ValueError(f"No configuration found for environment: {environment}")

        return AsyncClient(config=config)


# Usage
manager = ConfigManager()
dev_client = manager.get_client("development")
prod_client = manager.get_client("production")
print(f"Created {len(manager.configs)} configurations")
```

## Troubleshooting

### Common Configuration Errors
```python
import os
from pydantic import ValidationError
from fivetwenty import AccountConfig, AsyncClient, Environment

# Error: Missing configuration
try:
    async with AsyncClient(
        token=os.environ.get("MISSING_TOKEN", ""),  # No env vars set
        environment=Environment.PRACTICE
    ) as client:
        print(f"Connected: {client.config.summary()}")
except ValueError as e:
    print(f"Configuration error: {e}")
    # Fix: Set FIVETWENTY_OANDA_TOKEN and FIVETWENTY_OANDA_ACCOUNT

# Error: Invalid alias format
try:
    config = AccountConfig(
        token=os.environ.get("TEST_TOKEN", "token"),
        account_id=os.environ.get("TEST_ACCOUNT", "account"),
        environment=Environment.PRACTICE,
        alias="123-invalid",  # Starts with number
    )
except ValidationError as e:
    print(f"Validation error: {e}")
    # Fix: Use valid identifier like "account_123"

# Error: Empty token
try:
    config = AccountConfig(
        token="",  # Empty token
        account_id=os.environ.get("TEST_ACCOUNT", "account"),
        environment=Environment.PRACTICE,
        alias="my_account",
    )
except ValidationError as e:
    print(f"Token error: {e}")
    # Fix: Provide valid token
```

### Debug Configuration

```python
import asyncio
import os
from fivetwenty import AsyncClient, Environment, ConfigValidator


async def main() -> None:
    # Check what configuration is being used
    async with AsyncClient(
        token=os.environ.get("YOUR_TOKEN", "your-token"),
        environment=Environment.PRACTICE
    ) as client:
        print(f"Account ID: {client.account_id}")
        print(f"Environment: {client.config.environment.value}")
        print(f"Alias: {client.config.alias}")
        print(f"Configuration summary: {client.config.summary()}")

        # Validate configuration manually
        errors = ConfigValidator.validate_account_config(client.config)
        if errors:
            print("Configuration issues:", errors)
        else:
            print("Configuration is valid")

if __name__ == "__main__":
    asyncio.run(main())
```

## Migration Guide

### From Old Configuration

If you were using the previous configuration format:

```python
import asyncio
import os
from fivetwenty import AsyncClient, Environment, AccountConfig


async def main() -> None:
    # Old way (no longer supported)
    # client = AsyncClient("your-token", Environment.PRACTICE)

    # New way - Direct parameters
    async with AsyncClient(
        token=os.environ.get("YOUR_TOKEN", "your-token"),
        environment=Environment.PRACTICE
    ) as client:
        print(f"Connected: {client.config.summary()}")

    # Or configuration object (recommended)
    config = AccountConfig(
        token=os.environ.get("YOUR_TOKEN", "your-token"),
        account_id=os.environ.get("YOUR_ACCOUNT", "your-account-id"),
        environment=Environment.PRACTICE,
        alias="my_account"
    )
    async with AsyncClient(config=config) as client:
        print(f"Connected: {client.config.summary()}")

if __name__ == "__main__":
    asyncio.run(main())
```

## Next Steps

- Learn about [environments](../tutorials/getting-started/environments.md) and their differences
- See [authentication](../tutorials/getting-started/authentication.md) for getting API tokens
- Review [best practices](best-practices.md) for production deployment
- Check [error handling](../api-reference/error-handling.md) for configuration-related errors