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

The most straightforward approach is to pass credentials directly to the client constructor. This example shows how to authenticate using environment variables for security:

```python
import asyncio
import os

from fivetwenty import AsyncClient, Environment

async def main() -> None:
    """Demonstrate explicit parameter authentication with environment variable security."""

    # Step 1: Create AsyncClient with explicit parameter configuration
    # This approach provides maximum control over authentication credentials
    async with AsyncClient(
        token=os.environ["FIVETWENTY_OANDA_TOKEN"],         # API token from secure environment storage
        account_id=os.environ["FIVETWENTY_OANDA_ACCOUNT"],  # Target account identifier
        environment=Environment.PRACTICE                    # Safe practice environment for testing
    ) as client:
        # Step 2: Validate authentication by requesting account information
        # Account listing confirms successful API authentication and authorization
        accounts = await client.accounts.get_accounts()
        account_count = len(accounts)

        # Step 3: Display authentication success confirmation
        print(f"Success Authentication successful - found {account_count} account(s)")
        print(f"Config Configuration: {client.config.summary()}")

# Step 4: Execute the authentication validation test
if __name__ == "__main__":
    asyncio.run(main())
```

### 2. Configuration Objects

For reusable configurations and multi-account scenarios, use configuration objects. This approach is ideal when running multiple clients connected to different accounts:

<!-- fragment: configuration with placeholder values -->
```python
from fivetwenty import AccountConfig, AsyncClient, Environment

# Step 1: Create reusable configuration object for structured credential management
# AccountConfig provides validation, security masking, and reusability across clients
config = AccountConfig(
    token="your-api-token",                # Replace with actual OANDA API token
    account_id="your-account-id",          # Replace with actual account identifier
    environment=Environment.PRACTICE,      # Practice environment for safe development
    alias="development_account"            # Optional alias for configuration identification
)

# Step 2: Initialize client using pre-configured settings
# Configuration objects enable consistent settings across multiple client instances
async with AsyncClient(config=config) as client:
    # Step 3: Verify authentication by retrieving account information
    # This confirms the configuration object contains valid credentials
    accounts = await client.accounts.get_accounts()
    account_count = len(accounts)

    # Step 4: Display configuration summary with automatic credential masking
    # Summary method protects sensitive information while showing configuration status
    print(f"List Using configuration: {client.config.summary()}")
    print(f"Success Successfully retrieved {account_count} account(s)")
    print(f"Lock Token and account ID are automatically masked for security")
```

### 3. Environment Variables

The most secure and convenient approach uses environment variables for zero-config authentication. First, set up your environment:

<!-- fragment: shell commands with placeholder tokens -->
```bash
# Set environment variables (in your shell etc).
export FIVETWENTY_OANDA_TOKEN="your-api-token"
export FIVETWENTY_OANDA_ACCOUNT="your-account-id"
export FIVETWENTY_OANDA_ENVIRONMENT="practice"
# Configuration is loaded automatically when these are set
```

Then create clients without explicitly passing credentials - the library automatically loads configuration from environment variables:

<!-- fragment: zero-config client example -->
```python
import asyncio


async def main() -> None:
    """Demonstrate zero-configuration authentication using environment variables."""
    from fivetwenty import AsyncClient

    # Step 1: Create AsyncClient with automatic environment-based configuration
    # Zero-config approach reads all settings from environment variables:
    # - FIVETWENTY_OANDA_TOKEN: Your OANDA API authentication token
    # - FIVETWENTY_OANDA_ACCOUNT: Target account ID for trading operations
    # - FIVETWENTY_OANDA_ENVIRONMENT: Environment setting (practice/live)
    async with AsyncClient() as client:
        # Step 2: Validate automatic configuration by requesting account data
        # This confirms environment variables were loaded correctly
        accounts = await client.accounts.get_accounts()
        account_count = len(accounts)

        # Step 3: Display configuration summary with security protection
        # Summary method shows configuration status without exposing credentials
        print(f"Config Auto-loaded configuration: {client.config.summary()}")
        print(f"Success Authentication successful: {account_count} account(s) found")
        print(f"Starting Zero-config setup complete - ready for trading operations")

# Step 4: Execute the zero-configuration authentication validation
if __name__ == "__main__":
    asyncio.run(main())
```

## Secure Token Management

### Environment Variables (Recommended)

Never hardcode tokens. Use environment variables:

**Error Bad - Never do this:**
<!-- fragment: bad example - intentionally wrong -->
```text
token = "abc123def456"  # NEVER hardcode tokens!
```

**Success Good - Use environment variables:**
```python
import os

# Step 1: Safely retrieve API token from environment variables
# Environment variables keep secrets out of source code and version control
token = os.environ.get("FIVETWENTY_OANDA_TOKEN")

# Step 2: Validate that required credentials are available
# Early validation prevents runtime failures during authentication
if not token:
    raise ValueError("FIVETWENTY_OANDA_TOKEN environment variable not set")

# Step 3: Confirm token loading with secure masking
# Display confirmation while protecting sensitive credential information
masked_token = '*' * min(8, len(token)) + '...' if len(token) > 8 else '*' * len(token)
print(f"Lock Token loaded from environment: {masked_token}")
print(f"Success Environment-based authentication configured successfully")
```

### Using .env Files

For local development, install python-dotenv and create a .env file:

```bash
uv add python-dotenv
```

<!-- fragment: .env file template with placeholders -->
```bash
# .env file (add to .gitignore!)
FIVETWENTY_OANDA_TOKEN=your-practice-token
FIVETWENTY_OANDA_ACCOUNT=your-account-id
FIVETWENTY_OANDA_ENVIRONMENT=practice
FIVETWENTY_OANDA_ACCOUNT_ALIAS=development_account
```

<!-- fragment: dotenv usage example -->
```python
import asyncio


async def main() -> None:
    """Demonstrate secure local development using .env file configuration."""
    from dotenv import load_dotenv

    from fivetwenty import AsyncClient

    # Step 1: Load environment variables from .env file
    # dotenv provides secure local development without hardcoding credentials
    load_dotenv()
    print("Config Environment variables loaded from .env file")
    print("Folder .env file should be added to .gitignore for security")

    # Step 2: Create client using automatically loaded environment variables
    # AsyncClient seamlessly uses the variables loaded by dotenv
    async with AsyncClient() as client:
        # Step 3: Validate that .env configuration works correctly
        # Account listing confirms successful authentication using .env credentials
        accounts = await client.accounts.get_accounts()
        account_count = len(accounts)

        # Step 4: Confirm successful .env-based authentication
        print(f"Success Authentication successful: {account_count} account(s) found")
        print(f"Starting Local development environment configured properly")

# Step 5: Execute the .env-based authentication test
if __name__ == "__main__":
    asyncio.run(main())
```

### Secret Management Systems

For production deployments, you can use AWS Secrets Manager, HashiCorp Vault, Kubernetes Secrets, etc. to set environment variables as appropriate.


## Multiple Account Configuration

You can create as many clients as you need to access different accounts with OANDA. Common scenarios include separating long and short positions to comply with US broker hedging rules, isolating different trading strategies to manage risk, or maintaining separate accounts for testing versus live trading.

For traders subject to US broker hedging rules, using separate long and short accounts provides a compliant way to maintain opposing positions in the same currency pair. This approach allows you to hedge positions without violating FIFO (First In, First Out) rules that prevent holding both long and short positions simultaneously in a single account. The next example shows how you might approach this.

<!-- fragment: multi-account configuration with placeholder tokens -->
```python
import asyncio
import os
from fivetwenty import AccountConfig, AsyncClient, Environment


async def main() -> None:
    """Demonstrate multi-account hedging strategy for US broker compliance."""

    # Step 1: Configure dedicated account for long positions
    # Separate long account enables compliance with US FIFO regulations
    long_config = AccountConfig(
        token=os.environ["LONG_ACCOUNT_TOKEN"],    # Dedicated token for long account
        account_id=os.environ["LONG_ACCOUNT_ID"],  # Long position account identifier
        environment=Environment.LIVE,              # Live trading environment
        alias="long_positions",                   # Descriptive alias for identification
    )

    # Step 2: Configure dedicated account for short positions
    # Separate short account allows hedging without violating broker rules
    short_config = AccountConfig(
        token=os.environ["SHORT_ACCOUNT_TOKEN"],   # Dedicated token for short account
        account_id=os.environ["SHORT_ACCOUNT_ID"], # Short position account identifier
        environment=Environment.LIVE,              # Live trading environment
        alias="short_positions",                  # Descriptive alias for identification
    )

    # Step 3: Execute hedged trading strategy across both accounts
    # Multiple clients enable simultaneous management of long and short positions
    async with AsyncClient(config=long_config) as long_client:
        async with AsyncClient(config=short_config) as short_client:
            print("Starting Executing multi-account hedging strategy")
            print("Analysis Long positions will be managed on dedicated account")
            print("📉 Short positions will be managed on separate account")

            # Step 4: Execute bullish strategy on long account
            # Long account handles all buy positions for the strategy
            await execute_long_strategy(long_client)

            # Step 5: Execute bearish strategy on short account for hedging
            # Short account provides hedge against long positions
            await execute_short_strategy(short_client)

async def execute_long_strategy(client: AsyncClient) -> None:
    """Execute bullish trading strategy with comprehensive account validation."""

    # Step 1: Validate long account accessibility and configuration
    # Account verification ensures the long strategy can execute properly
    accounts = await client.accounts.get_accounts()

    # Step 2: Confirm successful long account strategy execution
    print(f"Analysis Long strategy executed on account: {client.config.alias}")
    print(f"Success Account validation: {len(accounts)} account(s) accessible")
    print(f"Target Ready for bullish position management")

async def execute_short_strategy(client: AsyncClient) -> None:
    """Execute bearish trading strategy with comprehensive account validation."""

    # Step 1: Validate short account accessibility and configuration
    # Account verification ensures the short strategy can execute properly
    accounts = await client.accounts.get_accounts()

    # Step 2: Confirm successful short account strategy execution
    print(f"📉 Short strategy executed on account: {client.config.alias}")
    print(f"Success Account validation: {len(accounts)} account(s) accessible")
    print(f"Target Ready for bearish position management and hedging")

asyncio.run(main())
```

## Security Features

### Automatic Secret Masking

The library automatically protects sensitive information:

<!-- fragment: security masking example with placeholder tokens -->
```python
import os
from fivetwenty import AccountConfig, Environment

# Step 1: Create configuration with automatic security masking
# AccountConfig automatically protects sensitive information from exposure
config = AccountConfig(
    token=os.environ["FIVETWENTY_OANDA_TOKEN"],     # API token (automatically masked)
    account_id=os.environ["FIVETWENTY_OANDA_ACCOUNT"], # Account ID (automatically masked)
    environment=Environment.PRACTICE,                # Environment setting (visible)
    alias="my_account",                             # Friendly alias (visible)
)

# Step 2: Demonstrate automatic secret masking in string representation
# repr() output masks sensitive credentials while showing configuration structure
config_repr = repr(config)
print(f"Lock Configuration representation: {config_repr}")
print("   Note: Token and account ID are automatically masked with '***'")
# Output: AccountConfig(alias='my_account', environment=practice, token=SecretStr('***'), account_id=SecretStr('***'))

# Step 3: Generate safe summary for logging and monitoring
# Summary method provides configuration info without exposing sensitive data
summary = config.summary()
print(f"Data Safe configuration summary: {summary}")
print("   Safe for logs, monitoring, and display purposes")
# Output: my_account (practice)
```

### Configuration Validation

The library validates all configuration values:

<!-- fragment: validation example - designed to fail -->
```python
from pydantic import ValidationError

from fivetwenty import AccountConfig, Environment

# Step 1: Demonstrate token validation (empty/whitespace tokens rejected)
# Configuration validation prevents common credential errors before runtime
try:
    config = AccountConfig(
        token="   ",                          # Empty/whitespace token - validation fails
        account_id="123-456-789",            # Valid account ID format
        environment=Environment.PRACTICE,     # Valid environment
        alias="my_account",                  # Valid alias
    )
    print(f"Error Unexpected success: {config}")
except ValidationError as e:
    print(f"Success Empty token rejected (expected): Configuration validation working")
    print(f"   Error details: {e}")

# Step 2: Demonstrate alias validation (must follow naming rules)
# Alias validation ensures configuration identifiers follow proper conventions
try:
    config = AccountConfig(
        token="valid-token",                  # Valid token format
        account_id="valid-account",           # Valid account ID
        environment=Environment.PRACTICE,     # Valid environment
        alias="123invalid",                  # Invalid alias - starts with number
    )
    print(f"Error Unexpected success: {config}")
except ValidationError as e:
    print(f"Success Invalid alias rejected (expected): Alias validation working")
    print(f"   Error details: {e}")
    print(f"   Note: Aliases must start with a letter, not a number")
```

## Testing Authentication

Before deploying your application, it's important to verify that your authentication setup works correctly. You can test your configuration in two ways: validate the configuration structure without making API calls, or verify authentication by connecting to OANDA's servers.

### Test Your Authentication Setup

<!-- fragment: authentication test example with placeholder tokens -->
```python
import asyncio
import os

from fivetwenty import AsyncClient, Environment


async def test_authentication() -> None:
    """Comprehensive authentication test with detailed account information and error handling."""

    try:
        # Step 1: Initialize client for authentication testing
        # Practice environment provides safe testing without affecting live trading
        async with AsyncClient(
            token=os.environ["FIVETWENTY_OANDA_TOKEN"],  # API token from environment
            environment=Environment.PRACTICE,             # Safe practice environment
        ) as client:
            # Step 2: Validate authentication by requesting account data
            # Account listing confirms successful API authentication and authorization
            accounts = await client.accounts.get_accounts()
            account_count = len(accounts)

            # Step 3: Display authentication success with configuration summary
            print("Success Authentication successful!")
            print(f"Config Configuration: {client.config.summary()}")
            print(f"Data Found {account_count} account(s):")

            # Step 4: Display detailed account information for verification
            # Account details help verify correct account access and trading capacity
            for account in accounts:
                account_info = f"{account.id}: {account.alias or 'No alias set'}"
                balance_info = f"{account.balance} {account.currency}"
                print(f"  Business Account: {account_info}")
                print(f"     Balance Balance: {balance_info}")
                print(f"     Analysis Open Trades: {account.open_trade_count}")
                print(f"     Secure Margin Used: {account.margin_used} {account.currency}")

            print(f"\nStarting Authentication test completed successfully")

    except Exception as e:
        # Step 5: Handle authentication failures with diagnostic information
        # Detailed error handling helps identify configuration issues quickly
        print(f"Error Authentication failed: {e}")
        print(f"Search Troubleshooting steps:")
        print(f"   • Verify FIVETWENTY_OANDA_TOKEN environment variable is set")
        print(f"   • Check token validity in OANDA account management")
        print(f"   • Ensure network connectivity to OANDA servers")
        print(f"   • Confirm token matches selected environment (practice vs live)")

# Step 6: Execute the comprehensive authentication test
if __name__ == "__main__":
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
<!-- fragment: troubleshooting commands with placeholders -->
```bash
export FIVETWENTY_OANDA_TOKEN="your-api-token"
export FIVETWENTY_OANDA_ACCOUNT="your-account-id"
export FIVETWENTY_OANDA_ENVIRONMENT="practice"
```

**Invalid Token Format**
```python
# Step 1: Validate token format and availability
# Token validation prevents authentication failures before API calls
import os

# Step 2: Safely retrieve and clean token from environment
# Strip whitespace to handle common configuration errors
token = os.environ.get("FIVETWENTY_OANDA_TOKEN", "").strip()

# Step 3: Validate token presence and basic format
# Early validation catches configuration issues before runtime
if not token:
    print("Error Token is empty or missing")
    print("   Set FIVETWENTY_OANDA_TOKEN environment variable")
else:
    # Step 4: Display token confirmation with security masking
    # Show partial token for verification while protecting sensitive data
    masked_token = token[:8] + '...' if len(token) > 8 else '*' * len(token)
    print(f"Success Token loaded: {masked_token}")
    print(f"Ruler Token length: {len(token)} characters")
    print(f"Lock Token format appears valid")
```

**Environment Mismatch**
```python
# Step 1: Ensure token-environment compatibility for successful authentication
# Token type must match environment: practice tokens for practice, live tokens for live
import os
from fivetwenty import AsyncClient, Environment

# Step 2: Configure practice environment with practice token
# Practice tokens only work with practice environment for safety
practice_client = AsyncClient(
    token=os.environ["FIVETWENTY_PRACTICE_TOKEN"],  # Practice-specific API token
    environment=Environment.PRACTICE                # Practice environment setting
)
print("Test Practice environment configured with practice token")

# Step 3: Configure live environment with live token
# Live tokens only work with live environment for real trading
live_client = AsyncClient(
    token=os.environ["FIVETWENTY_LIVE_TOKEN"],      # Live trading API token
    environment=Environment.LIVE                    # Live environment setting
)
print("Starting Live environment configured with live token")
print("⚠️  Note: Live tokens access real money - use with caution")
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
