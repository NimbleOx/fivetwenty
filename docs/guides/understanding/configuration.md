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

<!-- fragment: basic client configuration example with placeholder credentials -->
```python
import asyncio
import os
from fivetwenty import AsyncClient, Environment


async def main() -> None:
    # Step 1: Initialize AsyncClient with direct parameter configuration
    # This is the simplest approach - perfect for getting started or basic scripts
    async with AsyncClient(
        token=os.environ.get("FIVETWENTY_OANDA_TOKEN", "your-api-token"),  # API authentication token
        environment=Environment.PRACTICE  # Safe practice environment with virtual money
    ) as client:
        # Step 2: Test connection by retrieving accounts associated with the token
        # This verifies authentication and provides basic account information
        accounts = await client.accounts.get_accounts()
        print(f"Found {len(accounts)} accounts")

        # At this point, the client is fully configured and ready for trading operations
        # The context manager ensures proper cleanup of HTTP connections

if __name__ == "__main__":
    # Step 3: Run the async main function using asyncio event loop
    # This is the standard pattern for async applications
    asyncio.run(main())
```

### Configuration Objects

For more structured configuration:

<!-- fragment: configuration object example with placeholder credentials -->
```python
import asyncio
import os
from fivetwenty import AccountConfig, AsyncClient, Environment


async def main() -> None:
    # Step 1: Create structured configuration object for reusable settings
    # AccountConfig provides validation, secret masking, and organized configuration
    config = AccountConfig(
        token=os.environ.get("FIVETWENTY_OANDA_TOKEN", "your-api-token"),  # API authentication
        account_id=os.environ.get("FIVETWENTY_OANDA_ACCOUNT", "your-account-id"),  # Specific account to use
        environment=Environment.PRACTICE,  # Trading environment selection
        alias="my_trading_account",  # Human-readable identifier for logging/debugging
    )

    # Step 2: Use structured configuration with AsyncClient
    # Configuration objects enable better organization for production applications
    async with AsyncClient(config=config) as client:
        # Step 3: Verify connection and configuration by retrieving accounts
        # The client automatically uses the account_id from the configuration
        accounts = await client.accounts.get_accounts()
        print(f"Found {len(accounts)} accounts")

        # Benefits of configuration objects:
        # - Automatic validation of all parameters
        # - Secret masking for security in logs
        # - Reusable across multiple client instances
        # - Type safety with Pydantic models

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

<!-- fragment: environment variable configuration example with placeholder tokens -->
```python
import asyncio
import os
from fivetwenty import AsyncClient, Environment


async def main() -> None:
    # Step 1: Initialize client using environment variables for deployment-friendly configuration
    # Environment variables are ideal for Docker, Kubernetes, CI/CD, and serverless deployments
    async with AsyncClient(
        token=os.environ.get("FIVETWENTY_OANDA_TOKEN", "demo-token"),  # Fallback for development
        environment=Environment.PRACTICE  # Environment can also be loaded from env vars
    ) as client:
        # Step 2: Verify environment variable configuration
        # The client automatically loads standard FIVETWENTY_* environment variables
        accounts = await client.accounts.get_accounts()
        print(f"Found {len(accounts)} accounts")

        # Environment variable benefits:
        # - Secure: No hardcoded secrets in source code
        # - Flexible: Different configs for different deployment environments
        # - Standard: Follows 12-factor app principles
        # - Zero-config: Minimal code changes between environments

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
    # Step 1: Minimal direct parameter configuration for basic usage
    # Perfect for simple scripts and getting started quickly
    async with AsyncClient(
        token=os.environ.get("FIVETWENTY_OANDA_TOKEN", "demo-token"),  # Required: API authentication
        environment=Environment.PRACTICE  # Required: Trading environment
    ) as client:
        print(f"Connected: {client.config.summary()}")
        # Output shows environment and masked credentials for security

    # Step 2: Include account ID for convenience and clearer intent
    # Account ID eliminates need to call get_accounts() to find the correct account
    async with AsyncClient(
        token=os.environ.get("FIVETWENTY_OANDA_TOKEN", "demo-token"),  # API authentication
        account_id=os.environ.get("FIVETWENTY_OANDA_ACCOUNT", "demo-account"),  # Specific account target
        environment=Environment.LIVE  # CAUTION: Live environment uses real money!
    ) as client:
        print(f"Connected: {client.config.summary()}")
        # Account ID is now available as client.account_id without additional API calls

    # Step 3: Advanced configuration with HTTP client customization
    # These options optimize performance and reliability for production applications
    async with AsyncClient(
        token=os.environ.get("FIVETWENTY_OANDA_TOKEN", "demo-token"),  # API authentication
        environment=Environment.PRACTICE,  # Safe practice environment
        timeout=60.0,  # Extended timeout for slow networks (default: 30s)
        max_retries=5,  # Retry failed requests up to 5 times (default: 3)
        user_agent="MyTradingBot/1.0"  # Custom user agent for request identification
    ) as client:
        print(f"Connected: {client.config.summary()}")
        # Enhanced reliability and monitoring through custom configuration

if __name__ == "__main__":
    asyncio.run(main())
```

### 2. Configuration Objects Pattern

Best for: Production applications, multiple accounts, reusable configurations

<!-- fragment: multi-account configuration example with placeholder credentials -->
```python
import asyncio
import os
from fivetwenty import AccountConfig, AsyncClient, Environment


async def main() -> None:
    # Step 1: Create separate configurations for different trading environments
    # This pattern enables safe development workflow: test in practice, deploy to live
    practice_config = AccountConfig(
        token=os.environ.get("PRACTICE_OANDA_TOKEN", "practice-token"),  # Practice API token
        account_id=os.environ.get("PRACTICE_OANDA_ACCOUNT", "practice-account-123"),  # Practice account
        environment=Environment.PRACTICE,  # Virtual money environment
        alias="practice_trading",  # Descriptive identifier for logging
    )

    live_config = AccountConfig(
        token=os.environ.get("LIVE_OANDA_TOKEN", "live-token"),  # Live API token
        account_id=os.environ.get("LIVE_OANDA_ACCOUNT", "live-account-456"),  # Real money account
        environment=Environment.LIVE,  # CRITICAL: Real money environment!
        alias="live_trading",  # Clear identification for production monitoring
    )

    # Step 2: Use practice configuration for strategy development and testing
    # Always test thoroughly in practice before moving to live trading
    async with AsyncClient(config=practice_config) as practice_client:
        # Safe testing environment - no real money at risk
        accounts = await practice_client.accounts.get_accounts()
        print("Practice accounts:", len(accounts))

        # This is where you would:
        # - Develop and test trading strategies
        # - Validate order placement logic
        # - Test error handling and edge cases
        # - Measure performance and latency

    # Step 3: Use live configuration for real trading (CAUTION REQUIRED)
    # Only proceed after thorough testing and validation in practice environment
    async with AsyncClient(config=live_config) as live_client:
        # DANGER: Real money trading - all losses are permanent!
        accounts = await live_client.accounts.get_accounts()
        print("Live accounts:", len(accounts))

        # Production trading requirements:
        # - Comprehensive testing completed in practice
        # - Risk management systems in place
        # - Position sizing appropriate for account balance
        # - Stop losses and emergency procedures ready
        # - Monitoring and alerting systems active


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
    # Step 1: Leverage standard environment variable naming convention
    # The FiveTwenty library follows FIVETWENTY_* naming for automatic recognition
    async with AsyncClient(
        token=os.environ.get("FIVETWENTY_OANDA_TOKEN", "demo-token"),  # Standard token variable
        environment=Environment.PRACTICE  # Environment can also be from FIVETWENTY_OANDA_ENVIRONMENT
    ) as client:
        # Step 2: Verify configuration loaded from environment variables
        # This approach works seamlessly with Docker, Kubernetes, and CI/CD systems
        accounts = await client.accounts.get_accounts()
        print(f"Found {len(accounts)} accounts")

        # Standard environment variables automatically recognized:
        # - FIVETWENTY_OANDA_TOKEN: API authentication token
        # - FIVETWENTY_OANDA_ACCOUNT: Default account ID
        # - FIVETWENTY_OANDA_ENVIRONMENT: practice or live
        # - FIVETWENTY_OANDA_ACCOUNT_ALIAS: Human-readable account name

if __name__ == "__main__":
    asyncio.run(main())
```

#### Custom Environment Variable Prefixes

For multiple accounts or microservices:

<!-- fragment: custom environment prefix configuration example with nested context managers -->
```python
import asyncio
from fivetwenty import AccountConfigLoader, AsyncClient


async def main() -> None:
    # Step 1: Load configurations using custom environment variable prefixes
    # Custom prefixes enable multiple trading strategies with different configurations
    momentum_config = AccountConfigLoader.from_env_prefix("MOMENTUM_")  # MOMENTUM_OANDA_TOKEN, etc.
    grid_config = AccountConfigLoader.from_env_prefix("GRID_")  # GRID_OANDA_TOKEN, etc.

    # Step 2: Define async function for parallel strategy execution
    # Separate clients allow different strategies to use different accounts/environments
    async def run_strategies() -> None:
        # Step 3: Initialize multiple clients concurrently using nested context managers
        # Each client operates independently with its own configuration and connection pool
        async with AsyncClient(config=momentum_config) as momentum_client:
            async with AsyncClient(config=grid_config) as grid_client:
                # Step 4: Execute account verification for both strategies simultaneously
                # Parallel API calls reduce initialization time for multi-strategy systems
                accounts1 = await momentum_client.accounts.get_accounts()
                accounts2 = await grid_client.accounts.get_accounts()
                print(f"Momentum accounts: {len(accounts1)}, Grid accounts: {len(accounts2)}")

                # At this point, both clients are ready for their respective trading strategies:
                # - momentum_client: For trend-following or momentum-based strategies
                # - grid_client: For grid trading or range-bound strategies
                # Each can operate on different accounts, environments, or with different parameters

    # Step 5: Execute the multi-strategy setup
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
<!-- fragment: configuration priority example with placeholder tokens -->
```python
import asyncio
import os
from fivetwenty import AsyncClient, AccountConfig, Environment


async def main() -> None:
    # Step 1: Demonstrate configuration object priority (highest precedence)
    # When config object is provided, it overrides all direct parameters
    config = AccountConfig(
        token=os.environ.get("CONFIG_TOKEN", "config-token"),  # Token from config object
        account_id=os.environ.get("CONFIG_ACCOUNT", "account-id"),  # Account from config object
        environment=Environment.PRACTICE  # Environment from config object
    )
    async with AsyncClient(
        token="direct-token",  # IGNORED: Config object takes precedence
        config=config,  # USED: Configuration object has highest priority
    ) as client:
        print(f"Connected: {client.config.summary()}")
        # Output shows config object values, not direct parameter values

    # Step 2: Demonstrate direct parameter priority over environment variables
    # Direct parameters override environment variables when no config object is provided
    async with AsyncClient(
        token="direct-token",  # USED: Direct parameter overrides FIVETWENTY_OANDA_TOKEN
        environment=Environment.PRACTICE  # USED: Direct parameter specification
    ) as client:
        print(f"Connected: {client.config.summary()}")
        # Even if FIVETWENTY_OANDA_TOKEN is set, "direct-token" is used instead

    # Configuration priority hierarchy (highest to lowest):
    # 1. Configuration object (config=AccountConfig(...))
    # 2. Direct parameters (token="...", environment=...)
    # 3. Environment variables (FIVETWENTY_OANDA_TOKEN, etc.)

    # This hierarchy provides flexibility:
    # - Environment variables for default/deployment settings
    # - Direct parameters for script-specific overrides
    # - Configuration objects for structured, reusable settings

if __name__ == "__main__":
    asyncio.run(main())
```

## Security Features

### Automatic Secret Masking

The library automatically protects sensitive information:

<!-- fragment: secret masking example with placeholder credentials -->
```python
import asyncio
import os
from fivetwenty import AccountConfig, AsyncClient, Environment


async def main() -> None:
    # Step 1: Create configuration with sensitive credentials
    # FiveTwenty automatically protects sensitive information for security
    config = AccountConfig(
        token=os.environ.get("SECRET_TOKEN", "super-secret-token"),  # Sensitive API token
        account_id=os.environ.get("SECRET_ACCOUNT", "secret-account-123"),  # Sensitive account ID
        environment=Environment.PRACTICE,  # Environment selection
        alias="my_account",  # Non-sensitive alias for identification
    )

    # Step 2: Demonstrate automatic secret masking in string representations
    # Secrets are automatically masked to prevent accidental exposure in logs/debug output
    print(repr(config))
    # Output: AccountConfig(alias='my_account', environment=practice, token=SecretStr('***'), account_id=SecretStr('***'))
    # Notice: Token and account_id are masked with '***' for security

    # Step 3: Use safe summary for logging and monitoring
    # Summary method provides safe representation without exposing sensitive data
    print(config.summary())
    # Output: my_account (practice)
    # Safe for application logs, monitoring dashboards, and debug output

    # Step 4: Access actual configuration values when needed by the client
    # The client can access real values internally while keeping them masked externally
    async with AsyncClient(config=config) as client:
        print(f"Using account: {client.account_id}")
        # Output: Using account: secret-account-123
        # Real value is accessible to the client for API operations

    # Security benefits of automatic masking:
    # - Prevents accidental credential exposure in logs
    # - Safe debugging and development workflows
    # - Secure monitoring and alerting systems
    # - Compliance with security best practices

if __name__ == "__main__":
    asyncio.run(main())
```

### Validation

The library validates configuration values:

<!-- fragment: validation examples with placeholder credentials and error cases -->
```python
import os
from pydantic import ValidationError
from fivetwenty import AccountConfig, Environment

# Step 1: Demonstrate alias validation - invalid format
# AccountConfig validates that aliases follow Python identifier rules
try:
    config = AccountConfig(
        token=os.environ.get("TEST_TOKEN", "token"),  # Valid token for testing
        account_id=os.environ.get("TEST_ACCOUNT", "account"),  # Valid account for testing
        environment=Environment.PRACTICE,  # Safe environment for validation testing
        alias="123invalid",  # ERROR: Cannot start with number - violates identifier rules
    )
except ValidationError:
    print("Alias must be a valid identifier")
    # Fix: Use aliases like "account_123", "trading_bot_v1", or "strategy_momentum"

# Step 2: Demonstrate token validation - empty/whitespace tokens rejected
# Security requires non-empty tokens to prevent authentication bypasses
try:
    config = AccountConfig(
        token="   ",  # ERROR: Whitespace-only token is invalid
        account_id=os.environ.get("TEST_ACCOUNT", "account"),  # Valid account for testing
        environment=Environment.PRACTICE,  # Safe environment for validation testing
        alias="valid_alias",  # Valid identifier format
    )
except ValidationError:
    print("Token cannot be empty")
    # Security enforcement: Prevents accidental deployment with missing credentials
    # Fix: Provide actual OANDA API token from account settings

# Validation benefits:
# - Early error detection before API calls
# - Prevents common configuration mistakes
# - Enforces security best practices
# - Clear error messages for debugging
```

### Configuration Validation

Use the validator to check configuration:

```python
import os
from fivetwenty import ConfigValidator, AccountConfig, Environment

# Step 1: Create configuration to validate
# ConfigValidator provides comprehensive validation beyond basic Pydantic checks
config = AccountConfig(
    token=os.environ.get("YOUR_TOKEN", "your-token"),  # API authentication token
    account_id=os.environ.get("YOUR_ACCOUNT", "your-account-id"),  # Target account ID
    environment=Environment.PRACTICE  # Trading environment selection
)

# Step 2: Run comprehensive configuration validation
# Validates format, security requirements, and logical consistency
errors = ConfigValidator.validate_account_config(config)

# Step 3: Handle validation results appropriately
if errors:
    # Configuration has issues that need attention before deployment
    for error in errors:
        print(f"Configuration error: {error}")
    # Recommended: Fix errors before proceeding to prevent runtime failures
else:
    print("Configuration is valid")
    # Safe to proceed with client initialization and trading operations

# ConfigValidator checks include:
# - Token format and security requirements
# - Account ID format validation
# - Environment consistency
# - Alias identifier compliance
# - Cross-field logical validation
```

## Advanced Client Configuration

### HTTP Client Options

```python
import asyncio
import os
from fivetwenty import AsyncClient, Environment


async def main() -> None:
    # Step 1: Configure AsyncClient with advanced HTTP options for production use
    # These settings optimize performance, reliability, and monitoring for trading applications
    async with AsyncClient(
        token=os.environ.get("YOUR_TOKEN", "your-token"),  # API authentication
        environment=Environment.PRACTICE,  # Safe environment for testing
        timeout=60.0,  # Extended timeout for slow networks or complex operations
        max_retries=5,  # Increased retry attempts for reliable order execution
        user_agent="MyTradingApp/1.0",  # Custom identification for monitoring and support
        # proxies="http://proxy.example.com:8080",  # Corporate proxy configuration
        # verify=True,  # SSL certificate verification (True = default CA bundle)
        # verify="/path/to/ca-bundle.crt",  # Custom CA bundle for private networks
        # cert="/path/to/client-cert.pem"  # Client certificate for mutual TLS authentication
    ) as client:
        print(f"Connected: {client.config.summary()}")

        # Advanced HTTP configuration benefits:
        # - Timeout: Prevents hanging connections in volatile markets
        # - Max retries: Improves reliability during network issues
        # - User agent: Enables support team to identify your application
        # - Proxy support: Works with corporate network infrastructure
        # - SSL verification: Ensures secure communication with OANDA servers
        # - Client certificates: Supports enterprise security requirements

if __name__ == "__main__":
    asyncio.run(main())
```

### Custom HTTP Transport

For advanced HTTP configuration:

<!-- fragment: partial custom HTTP transport configuration example -->
```python
import asyncio
import os

import httpx

from fivetwenty import AsyncClient, Environment


async def main() -> None:
    # Step 1: Create custom httpx transport for advanced HTTP configuration
    # This demonstrates the underlying HTTP client configuration options
    transport = httpx.AsyncClient(
        base_url=Environment.PRACTICE.base_url,  # OANDA practice API base URL
        timeout=httpx.Timeout(
            connect=5.0,  # Connection establishment timeout
            read=60.0,    # Response reading timeout (important for streaming)
            write=10.0,   # Request writing timeout
            pool=60.0,    # Connection pool timeout
        ),
        limits=httpx.Limits(
            max_connections=100,         # Total connection pool size
            max_keepalive_connections=20, # Persistent connections for performance
        ),
        http2=False,      # Disable HTTP/2 for compatibility (OANDA uses HTTP/1.1)
        trust_env=True,   # Honor proxy environment variables (HTTP_PROXY, etc.)
    )

    # Step 2: Use AsyncClient with standard configuration
    # Custom transport configuration shown for educational purposes
    async with AsyncClient(
        token=os.environ.get("YOUR_TOKEN", "your-token"),  # API authentication
        environment=Environment.PRACTICE,  # Safe practice environment
        # transport=transport,  # Custom transport not exposed in current FiveTwenty API
    ) as client:
        print(f"Client configured: {client.config.environment}")

        # Note: FiveTwenty manages httpx configuration internally for optimal OANDA API performance
        # This example shows the underlying concepts for educational purposes
        # The AsyncClient automatically configures appropriate timeouts, limits, and HTTP settings

    # Custom transport benefits (handled internally by FiveTwenty):
    # - Optimized connection pooling for trading workloads
    # - Appropriate timeouts for financial market APIs
    # - HTTP/1.1 compatibility with OANDA infrastructure
    # - Environment variable support for proxy configuration

asyncio.run(main())
```

### Logging Configuration

<!-- fragment: partial logging configuration example -->
```python
import asyncio
import logging
import os
from fivetwenty import AsyncClient, Environment


async def main() -> None:
    # Step 1: Configure application logging for trading operations monitoring
    # Proper logging is critical for debugging, monitoring, and compliance
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("my_trading_app")

    # Step 2: Configure httpx logging to monitor HTTP requests/responses
    # This reveals actual API communication for debugging and performance analysis
    logging.getLogger("httpx").setLevel(logging.DEBUG)
    # DEBUG level shows: request URLs, headers, response codes, timing
    # Useful for troubleshooting connectivity and API issues

    # Step 3: Initialize client with logging monitoring active
    async with AsyncClient(
        token=os.environ.get("YOUR_TOKEN", "your-token"),  # API authentication
        environment=Environment.PRACTICE  # Safe environment for logging testing
    ) as client:
        # Step 4: Execute operations with comprehensive logging
        # All HTTP requests/responses are now logged for analysis
        accounts = await client.accounts.get_accounts()
        print(f"Found {len(accounts)} accounts")

        # Logging benefits for trading applications:
        # - Request/response debugging for API issues
        # - Performance monitoring and latency analysis
        # - Audit trail for compliance requirements
        # - Error diagnosis for failed operations
        # - Network troubleshooting capabilities

        # Security note: Be careful with DEBUG logging in production
        # - May expose sensitive data in request headers
        # - Can generate large log volumes affecting performance
        # - Consider INFO or WARNING levels for production systems

if __name__ == "__main__":
    asyncio.run(main())
```

## Sync Client Configuration

The sync `Client` supports the same configuration patterns:

<!-- fragment: partial sync client configuration example -->
```python
import os
from fivetwenty import Client, AccountConfig, Environment

# Step 1: Direct parameter configuration for sync client
# Sync Client provides the same configuration options as AsyncClient
with Client(
    token=os.environ.get("YOUR_TOKEN", "your-token"),  # API authentication token
    environment=Environment.PRACTICE  # Safe practice environment
) as client:
    # Synchronous API call - blocks until response received
    accounts = client.accounts.get_accounts()
    print(f"Found {len(accounts)} accounts")
    # Sync client automatically manages async/sync conversion internally

# Step 2: Configuration object approach for structured settings
# Same AccountConfig works with both AsyncClient and sync Client
config = AccountConfig(
    token=os.environ.get("YOUR_TOKEN", "your-token"),  # API authentication
    account_id=os.environ.get("YOUR_ACCOUNT", "your-account"),  # Target account
    environment=Environment.PRACTICE,  # Environment selection
    alias="example_config"  # Human-readable identifier
)
with Client(config=config) as client:
    # Configuration object provides same benefits in sync context
    accounts = client.accounts.get_accounts()
    print(f"Found {len(accounts)} accounts")
    # Automatic validation, secret masking, and type safety

# Step 3: Environment variable configuration for deployment
# Standard FIVETWENTY_* environment variables work with sync client
with Client(
    token=os.environ.get("FIVETWENTY_OANDA_TOKEN", "demo-token"),  # Standard env var
    environment=Environment.PRACTICE  # Environment specification
) as client:  # Automatically loads from FIVETWENTY_* variables
    accounts = client.accounts.get_accounts()
    print(f"Found {len(accounts)} accounts")

    # Sync Client benefits:
    # - Simpler programming model for blocking operations
    # - No async/await syntax required
    # - Same configuration flexibility as AsyncClient
    # - Automatic async/sync conversion handled internally
    # - Perfect for scripts, batch jobs, and synchronous workflows
```

## Configuration Management Utilities

### Configuration Builder

<!-- fragment: configuration builder utility class with file operations -->
```python
import json
import os
from typing import Any
from fivetwenty import AccountConfig, Environment


class ConfigBuilder:
    """Helper utility to build configurations from various enterprise sources."""

    @staticmethod
    def from_vault(vault_client: Any, secret_path: str, environment: str) -> AccountConfig:
        """Load configuration from HashiCorp Vault for enterprise secret management."""
        # Step 1: Retrieve secrets from HashiCorp Vault
        # Vault provides centralized, secure secret management for production systems
        secret = vault_client.secrets.kv.v2.read_secret_version(
            path=secret_path,        # Vault path like "trading/oanda/credentials"
            mount_point="secret",    # Vault mount point for KV store
        )

        # Step 2: Extract secret data from Vault response format
        # Vault wraps secret data in nested structure for versioning
        data = secret["data"]["data"]

        # Step 3: Build AccountConfig from Vault secrets with environment logic
        # Environment parameter controls practice vs live environment selection
        return AccountConfig(
            token=data["token"],                    # OANDA API token from Vault
            account_id=data["account_id"],          # Account ID from Vault
            environment=Environment.PRACTICE if environment == "practice" else Environment.LIVE,
            alias=data.get("alias", "vault_account")  # Optional alias with fallback
        )
        # Benefits: Centralized secret rotation, audit trails, access control

    @staticmethod
    def from_json_file(file_path: str) -> AccountConfig:
        """Load configuration from JSON file with secrets from environment variables."""
        # Step 1: Load non-sensitive configuration from JSON file
        # JSON file contains only non-secret configuration like environment and alias
        with open(file_path, 'r') as f:
            data = json.load(f)
        # Example JSON: {"environment": "practice", "alias": "trading_bot_v1"}

        # Step 2: Build configuration combining JSON config with environment secrets
        # Secrets come from environment variables for security - never store in files
        return AccountConfig(
            token=os.environ["FIVETWENTY_OANDA_TOKEN"],    # Secure: from environment
            account_id=os.environ["FIVETWENTY_OANDA_ACCOUNT"],  # Secure: from environment
            environment=Environment(data["environment"]),   # From JSON file
            alias=data["alias"]                             # From JSON file
        )
        # Security pattern: Secrets in env vars, config in version-controlled files
```

### Multi-Environment Manager

<!-- fragment: partial configuration manager class -->
```python
from fivetwenty import AccountConfig, AccountConfigLoader, AsyncClient


class ConfigManager:
    """Centralized configuration management for multi-environment deployments."""

    def __init__(self) -> None:
        # Step 1: Initialize configuration storage for multiple environments
        # Each environment gets its own configuration with appropriate settings
        self.configs: dict[str, AccountConfig] = {}
        self._load_configs()

    def _load_configs(self) -> None:
        """Load configurations for all deployment environments."""
        # Step 2: Define environments for systematic configuration loading
        # Standard deployment pipeline: development -> staging -> production
        environments = ["development", "staging", "production"]

        for env in environments:
            # Step 3: Create environment-specific variable prefixes
            # This enables different credentials and settings per environment
            prefix = f"{env.upper()}_FIVETWENTY_"  # DEV_FIVETWENTY_, STAGING_FIVETWENTY_, etc.

            # Step 4: Load configuration using environment prefix pattern
            # config = AccountConfigLoader.from_env_prefix(prefix)  # Conceptual example
            # if config:
            #     self.configs[env] = config
            pass  # Implementation depends on AccountConfigLoader availability

            # Environment variable examples:
            # DEV_FIVETWENTY_OANDA_TOKEN, DEV_FIVETWENTY_OANDA_ACCOUNT
            # STAGING_FIVETWENTY_OANDA_TOKEN, STAGING_FIVETWENTY_OANDA_ACCOUNT
            # PRODUCTION_FIVETWENTY_OANDA_TOKEN, PRODUCTION_FIVETWENTY_OANDA_ACCOUNT

    def get_config(self, environment: str) -> AccountConfig | None:
        """Retrieve configuration for specific environment with validation."""
        # Step 5: Safe configuration retrieval with None return for missing environments
        return self.configs.get(environment)

    def get_client(self, environment: str) -> AsyncClient:
        """Get configured client for specific environment with error handling."""
        # Step 6: Retrieve configuration with validation
        config = self.get_config(environment)
        if not config:
            # Clear error message for missing environment configuration
            raise ValueError(f"No configuration found for environment: {environment}")

        # Step 7: Return fully configured client for the environment
        return AsyncClient(config=config)
        # Client automatically inherits all environment-specific settings


# Step 8: Usage example for multi-environment configuration management
manager = ConfigManager()

# Get environment-specific clients with isolated configurations
dev_client = manager.get_client("development")      # Development environment settings
prod_client = manager.get_client("production")      # Production environment settings
print(f"Created {len(manager.configs)} configurations")

# Benefits of centralized configuration management:
# - Consistent configuration patterns across environments
# - Easy environment switching for deployments
# - Centralized validation and error handling
# - Type-safe configuration with compile-time checking
```

## Troubleshooting

### Common Configuration Errors
<!-- fragment: configuration error handling examples with await in non-async context -->
```python
import os
from pydantic import ValidationError
from fivetwenty import AccountConfig, AsyncClient, Environment

# Step 1: Handle missing configuration error
# This demonstrates validation of required configuration parameters
try:
    # Simulate missing environment variable scenario
    async with AsyncClient(
        token=os.environ.get("MISSING_TOKEN", ""),  # Empty string when env var not set
        environment=Environment.PRACTICE
    ) as client:
        print(f"Connected: {client.config.summary()}")
except ValueError as e:
    print(f"Configuration error: {e}")
    # Fix: Set required environment variables before running application
    # export FIVETWENTY_OANDA_TOKEN="your-api-token"
    # export FIVETWENTY_OANDA_ACCOUNT="your-account-id"

# Step 2: Handle invalid alias format validation error
# AccountConfig enforces Python identifier rules for aliases
try:
    config = AccountConfig(
        token=os.environ.get("TEST_TOKEN", "token"),     # Valid token for testing
        account_id=os.environ.get("TEST_ACCOUNT", "account"),  # Valid account for testing
        environment=Environment.PRACTICE,                # Safe environment
        alias="123-invalid",  # ERROR: Starts with number, contains hyphen
    )
except ValidationError as e:
    print(f"Validation error: {e}")
    # Fix: Use valid Python identifier format
    # Valid examples: "account_123", "trading_bot", "strategy_v1"
    # Invalid examples: "123invalid", "account-name", "my strategy"

# Step 3: Handle empty token security validation
# Security validation prevents deployment with missing credentials
try:
    config = AccountConfig(
        token="",  # ERROR: Empty token fails security validation
        account_id=os.environ.get("TEST_ACCOUNT", "account"),  # Valid account
        environment=Environment.PRACTICE,  # Safe environment
        alias="my_account",                # Valid alias
    )
except ValidationError as e:
    print(f"Token error: {e}")
    # Fix: Provide valid OANDA API token from account settings
    # Token format: Usually starts with hex characters, e.g., "abc123def456..."

# Error handling best practices:
# - Validate configuration early in application startup
# - Provide clear error messages with specific fix instructions
# - Use environment variables for secrets, never hardcode
# - Test configuration validation in CI/CD pipeline
```

### Debug Configuration

```python
import asyncio
import os
from fivetwenty import AsyncClient, Environment, ConfigValidator


async def main() -> None:
    # Step 1: Initialize client and inspect active configuration
    # This debug approach helps troubleshoot configuration issues
    async with AsyncClient(
        token=os.environ.get("YOUR_TOKEN", "your-token"),  # API authentication
        environment=Environment.PRACTICE  # Safe environment for debugging
    ) as client:
        # Step 2: Display detailed configuration information for debugging
        # These properties help verify what configuration is actually being used
        print(f"Account ID: {client.account_id}")                        # Configured account
        print(f"Environment: {client.config.environment.value}")        # practice or live
        print(f"Alias: {client.config.alias}")                         # Human-readable name
        print(f"Configuration summary: {client.config.summary()}")      # Safe summary

        # Step 3: Run comprehensive configuration validation
        # Manual validation provides detailed analysis of potential issues
        errors = ConfigValidator.validate_account_config(client.config)
        if errors:
            print("Configuration issues:", errors)
            # Each error provides specific guidance for resolution
            # Common issues: token format, alias validation, environment consistency
        else:
            print("Configuration is valid")
            # Safe to proceed with trading operations

        # Debug output helps with:
        # - Verifying environment variable loading
        # - Confirming configuration object usage
        # - Identifying validation failures
        # - Understanding configuration priority resolution
        # - Troubleshooting authentication issues

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
    # Step 1: Migration from deprecated API pattern
    # Old way (no longer supported in current versions)
    # client = AsyncClient("your-token", Environment.PRACTICE)  # Deprecated positional args

    # Step 2: Modern approach using named parameters
    # New way provides explicit, readable configuration
    async with AsyncClient(
        token=os.environ.get("YOUR_TOKEN", "your-token"),  # Named parameter for clarity
        environment=Environment.PRACTICE  # Explicit environment specification
    ) as client:
        print(f"Connected: {client.config.summary()}")
        # Benefits: Clear parameter names, IDE support, type safety

    # Step 3: Recommended configuration object approach for production
    # Configuration objects provide enhanced features and better organization
    config = AccountConfig(
        token=os.environ.get("YOUR_TOKEN", "your-token"),      # API authentication
        account_id=os.environ.get("YOUR_ACCOUNT", "your-account-id"),  # Target account
        environment=Environment.PRACTICE,                      # Environment selection
        alias="my_account"                                     # Human-readable identifier
    )
    async with AsyncClient(config=config) as client:
        print(f"Connected: {client.config.summary()}")

        # Configuration object advantages over direct parameters:
        # - Automatic validation of all configuration values
        # - Secret masking for security in logs and debug output
        # - Reusable configuration across multiple client instances
        # - Type safety with Pydantic models and IDE completion
        # - Structured organization for complex applications
        # - Support for advanced features like custom aliases

if __name__ == "__main__":
    asyncio.run(main())
```

## Next Steps

- Learn about [environments](environments.md) and their differences
- See [authentication](../../tutorials/getting-started/authentication.md) for getting API tokens
- Review [best practices](best-practices.md) for production deployment
- Check [error handling](../../api-reference/error-handling.md) for configuration-related errors