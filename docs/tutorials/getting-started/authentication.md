# Authentication

This guide covers getting an OANDA API token and configuring the FiveTwenty client to use it without exposing your credentials.

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

The FiveTwenty library accepts credentials in three ways:

### 1. Direct Parameters

The most straightforward approach is to pass credentials directly to the client constructor. This example shows how to authenticate using environment variables for security:

```python
import asyncio
import os

from dotenv import load_dotenv
from fivetwenty import AsyncClient, Environment

# Load environment variables from .env file
load_dotenv()


async def main() -> None:
    """
    Tutorial: Basic OANDA API Authentication.

    This example demonstrates how to connect to the OANDA API using the fivetwenty library.
    You'll learn how to:
    - Create an authenticated API client
    - Retrieve account information
    - Verify your connection is working
    """

    # Step 1: Create the API client
    # The AsyncClient manages your connection to OANDA's servers
    # Using 'async with' ensures proper cleanup when done
    async with AsyncClient(
        # Your API token authenticates your requests (stored in .env file)
        token=os.environ["FIVETWENTY_OANDA_TOKEN"],

        # The account ID specifies which OANDA account to interact with
        account_id=os.environ["FIVETWENTY_OANDA_ACCOUNT"],

        # Use PRACTICE for learning/testing (never risk real money while learning!)
        environment=Environment.PRACTICE,
    ) as client:
        # Step 2: Test the connection by fetching your accounts
        # This API call returns a list of all accounts you have access to
        accounts = await client.accounts.get_accounts()
        account_count = len(accounts)

        # Step 3: Display the results
        # If you see this message, your API credentials are working correctly!
        print(f" Authentication successful - found {account_count} account(s)")
        print(f"📋 Configuration: {client.config.summary()}")


# Step 4: Run the tutorial when this script is executed
# asyncio.run() is needed because we're using async/await for API calls
if __name__ == "__main__":
    asyncio.run(main())
```

### 2. Configuration Objects

For reusable configurations and multi-account scenarios, use configuration objects. This approach works well when running multiple clients connected to different accounts:

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
    print(f"Using configuration: {client.config.summary()}")
    print(f"Successfully retrieved {account_count} account(s)")
    print(f"Token and account ID are automatically masked for security")
```

### 3. Environment Variables

The approach we recommend uses environment variables, so no credentials appear in your code at all. First, set up your environment:

<!-- fragment: shell commands with placeholder tokens -->
```bash
# Set environment variables (in your shell etc).
export FIVETWENTY_OANDA_TOKEN="your-api-token"
export FIVETWENTY_OANDA_ACCOUNT="your-account-id"
export FIVETWENTY_OANDA_ENVIRONMENT="practice"
# Configuration is loaded automatically when these are set
```

Then create clients without passing credentials at all. The library loads its configuration from the environment variables:

<!-- fragment: zero-config client example -->
```python
import asyncio  # Needed for async/await operations (API calls run asynchronously)

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


async def main() -> None:
    """
    Tutorial: Zero-Configuration Authentication

    This example shows the simplest way to connect to OANDA - just set your
    environment variables and the fivetwenty library handles the rest!
    """
    # Import AsyncClient inside the function (can also import at top of file)
    from fivetwenty import AsyncClient

    # Step 1: Create the API client with zero configuration
    # The AsyncClient automatically reads these environment variables:
    # - FIVETWENTY_OANDA_TOKEN: Your API token for authentication
    # - FIVETWENTY_OANDA_ACCOUNT: Your account ID
    # - FIVETWENTY_OANDA_ENVIRONMENT: "practice" or "live"
    # Using 'async with' ensures the connection is properly closed when done
    async with AsyncClient() as client:
        # Step 2: Test the connection by fetching your accounts
        # This API call retrieves a list of all accounts you can access
        # If this succeeds, your credentials are configured correctly!
        accounts = await client.accounts.get_accounts()
        account_count = len(accounts)

        # Step 3: Display the results
        # The config.summary() method shows your settings without exposing secrets
        print(f" Auto-loaded configuration: {client.config.summary()}")
        print(f" Authentication successful: {account_count} account(s) found")
        print(" Ready for trading operations!")


# Step 4: Run the tutorial
# This is the standard Python idiom for executable scripts
# asyncio.run() is required because our main() function uses async/await
if __name__ == "__main__":
    asyncio.run(main())
```

## Secure Token Management

### Environment Variables (Recommended)

Never hardcode tokens. Use environment variables:

**Bad - Never do this:**
<!-- fragment: bad example - intentionally wrong -->
```text
token = "abc123def456"  # NEVER hardcode tokens!
```

**Good - Use environment variables:**
```python
import os

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

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
print(f"Token loaded from environment: {masked_token}")
print(f"Environment-based authentication configured successfully")
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
    print("variables loaded from .env file")
    print(".env file should be added to .gitignore for security")

    # Step 2: Create client using automatically loaded environment variables
    # AsyncClient seamlessly uses the variables loaded by dotenv
    async with AsyncClient() as client:
        # Step 3: Validate that .env configuration works correctly
        # Account listing confirms successful authentication using .env credentials
        accounts = await client.accounts.get_accounts()
        account_count = len(accounts)

        # Step 4: Confirm successful .env-based authentication
        print(f"Authentication successful: {account_count} account(s) found")
        print(f"Local development environment configured properly")

# Step 5: Execute the .env-based authentication test
if __name__ == "__main__":
    asyncio.run(main())
```

### Secret Management Systems

For production deployments, you can use AWS Secrets Manager, HashiCorp Vault, Kubernetes Secrets, etc. to set environment variables as appropriate.


## Multiple Account Configuration

FiveTwenty can manage multiple OANDA accounts at once. The usual reasons are US broker hedging compliance and keeping separate strategies in separate accounts.

!!! tip "Multi-Account Management"
    For detailed examples of multi-account setups including US broker hedging compliance, separate strategy accounts, and aggregate account monitoring, see [Account Management Tutorial](../account-management.md#multi-account-management).

## Security Features

### Automatic Secret Masking

The library automatically protects sensitive information:

<!-- fragment: security masking example with placeholder tokens -->
```python
import os

from dotenv import load_dotenv
from fivetwenty import AccountConfig, Environment
from pydantic import SecretStr

# Load environment variables from .env file
load_dotenv()

# Step 1: Create configuration with automatic security masking
# AccountConfig automatically protects sensitive information from exposure
config = AccountConfig(
    token=SecretStr(
        os.environ["FIVETWENTY_OANDA_TOKEN"]
    ),  # API token (automatically masked)
    account_id=SecretStr(
        os.environ["FIVETWENTY_OANDA_ACCOUNT"]
    ),  # Account ID (automatically masked)
    environment=Environment.PRACTICE,  # Environment setting (visible)
    alias="my_account",  # Friendly alias (visible)
)

# Step 2: Demonstrate automatic secret masking in string representation
# repr() output masks sensitive credentials while showing configuration structure
config_repr = repr(config)
print(f"Configuration representation: {config_repr}")
print("   Note: Token and account ID are automatically masked with '***'")
# Output: AccountConfig(alias='my_account', environment=practice, token=SecretStr('***'), account_id=SecretStr('***'))

# Step 3: Generate safe summary for logging and monitoring
# Summary method provides configuration info without exposing sensitive data
summary = config.summary()
print(f"Safe configuration summary: {summary}")
print("   Safe for logs, monitoring, and display purposes")
# Output: my_account (practice)
```

### Configuration Validation

The library validates all configuration values:

<!-- fragment: validation example - designed to fail -->
```python
from fivetwenty import AccountConfig, Environment
from pydantic import SecretStr, ValidationError

# Step 1: Demonstrate token validation (empty/whitespace tokens rejected)
# Configuration validation prevents common credential errors before runtime
try:
    config = AccountConfig(
        token=SecretStr("   "),  # Empty/whitespace token - validation fails
        account_id=SecretStr("123-456-789"),  # Valid account ID format
        environment=Environment.PRACTICE,  # Valid environment
        alias="my_account",  # Valid alias
    )
    print(f"Error: Unexpected success: {config}")
except ValidationError as e:
    print("Empty token rejected (expected): Configuration validation working")
    print(f"   Error: details: {e}")

# Step 2: Demonstrate alias validation (must follow naming rules)
# Alias validation ensures configuration identifiers follow proper conventions
try:
    config = AccountConfig(
        token=SecretStr("valid-token"),  # Valid token format
        account_id=SecretStr("valid-account"),  # Valid account ID
        environment=Environment.PRACTICE,  # Valid environment
        alias="123invalid",  # Invalid alias - starts with number
    )
    print(f"Error: Unexpected success: {config}")
except ValidationError as e:
    print("Invalid alias rejected (expected): Alias validation working")
    print(f"   Error: details: {e}")
    print("   Note: Aliases must start with a letter, not a number")
```

## Testing Authentication

Before deploying your application, verify that your authentication setup works. You can test in two ways: validate the configuration structure without making API calls, or actually connect to OANDA's servers.

### Test Your Authentication Setup

This script does the real thing: it connects to OANDA, retrieves your account information, and prints balance, open trades, and margin usage for each account. If it runs cleanly, both your credentials and your network path to OANDA are good.

<!-- fragment: authentication test example with placeholder tokens -->
```python
import asyncio
import os

from dotenv import load_dotenv
from fivetwenty import AsyncClient, Environment

# Load environment variables from .env file
load_dotenv()


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
            print("Authentication successful!")
            print(f"Configuration: {client.config.summary()}")
            print(f"Found {account_count} account(s):")

            # Step 4: Display detailed account information for verification
            # Account details help verify correct account access and trading capacity
            for account in accounts:
                account_info = f"{account.id}: {account.alias or 'No alias set'}"
                balance_info = f"{account.balance} {account.currency}"
                print(f"  Account: {account_info}")
                print(f"     Balance: {balance_info}")
                print(f"     Open Trades: {account.open_trade_count}")
                print(f"     Margin Used: {account.margin_used} {account.currency}")

            print(f"\nAuthentication test completed successfully")

    except Exception as e:
        # Step 5: Handle authentication failures with diagnostic information
        # Detailed error handling helps identify configuration issues quickly
        print(f"Error: Authentication failed: {e}")
        print(f"Troubleshooting steps:")
        print(f"   • Verify FIVETWENTY_OANDA_TOKEN environment variable is set")
        print(f"   • Check token validity in OANDA account management")
        print(f"   • Ensure network connectivity to OANDA servers")
        print(f"   • Confirm token matches selected environment (practice vs live)")

# Step 6: Execute the comprehensive authentication test
if __name__ == "__main__":
    asyncio.run(test_authentication())
```

## Security Considerations

Three rules are worth repeating:

- Never commit tokens to version control; use environment variables
- Use separate tokens for practice and live environments
- Validate configurations before deployment to catch issues early

!!! tip "Security Guide"
    For token rotation strategies and production deployment patterns, see the [Best Practices Guide](../../guides/understanding/best-practices.md).

!!! info "Advanced Configuration"
    For environment-specific settings and other configuration options, see the [Configuration Guide](../../guides/understanding/configuration.md).

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
import os

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Step 1: Validate token format and availability
# Token validation prevents authentication failures before API calls

# Step 2: Safely retrieve and clean token from environment
# Strip whitespace to handle common configuration errors
token = os.environ.get("FIVETWENTY_OANDA_TOKEN", "").strip()

# Step 3: Validate token presence and basic format
# Early validation catches configuration issues before runtime
if not token:
    print("Error: Token is empty or missing")
    print("   Set FIVETWENTY_OANDA_TOKEN environment variable")
else:
    # Step 4: Display token confirmation with security masking
    # Show partial token for verification while protecting sensitive data
    masked_token = token[:8] + "..." if len(token) > 8 else "*" * len(token)
    print(f"Token loaded: {masked_token}")
    print(f"Token length: {len(token)} characters")
    print("Token format appears valid")
```

**Environment Mismatch**
```python
import os

from dotenv import load_dotenv
from fivetwenty import AsyncClient, Environment

# Load environment variables from .env file
load_dotenv()

# PROBLEM: Environment Mismatch Troubleshooting
# This example shows how to avoid a common mistake - using the wrong token
# with the wrong environment, which causes authentication failures.

# Step 1: Identify which token type you have
# OANDA tokens are environment-specific: practice tokens only work with practice,
# and live tokens only work with live environments
token = os.environ["FIVETWENTY_OANDA_TOKEN"]
account_id = os.environ.get("FIVETWENTY_OANDA_ACCOUNT")

# Step 2: Match your token to the correct environment
#  CORRECT: Using practice token with practice environment
correct_client = AsyncClient(
    token=token,
    account_id=account_id,
    environment=Environment.PRACTICE,  # Matches practice token
)
print(" CORRECT: Practice token paired with PRACTICE environment")
print(f"  Configuration: {correct_client.config.summary()}")

#  WRONG: Don't mix token types with environments
# This would fail authentication:
# wrong_client = AsyncClient(
#     token=token,  # Practice token
#     environment=Environment.LIVE,  # Wrong! This expects a live token
# )
# Result: Authentication error - token doesn't match environment

# Step 3: Solution for multiple environments
# Keep separate environment variables for practice vs live tokens:
# .env file should have:
#   FIVETWENTY_PRACTICE_TOKEN=your-practice-token
#   FIVETWENTY_LIVE_TOKEN=your-live-token
# Then use them explicitly:
#   practice_client = AsyncClient(
#       token=os.environ["FIVETWENTY_PRACTICE_TOKEN"],
#       environment=Environment.PRACTICE
#   )
#   live_client = AsyncClient(
#       token=os.environ["FIVETWENTY_LIVE_TOKEN"],
#       environment=Environment.LIVE
#   )

print("\n Always match token type to environment:")
print("   • Practice tokens  Environment.PRACTICE")
print("   • Live tokens  Environment.LIVE")

```

!!! info "More Troubleshooting"
    For network issues, SSL problems, and deeper authentication debugging, see the [Connection Failure Handling Guide](../../guides/practical-solutions/handle-connection-failures.md#authentication-troubleshooting).

## Summary

The SDK accepts credentials as direct parameters, configuration objects, or environment variables, and masks secrets in logs and reprs in every case. Environment variables are the right default; reach for `AccountConfig` once you manage more than one account.

## Next Steps

Now that authentication is configured:

- [Learn about environments](../../guides/understanding/environments.md) to understand practice vs live trading
- [Make your first trade](first-trade.md) to test your setup
- [Review configuration options](../../guides/understanding/configuration.md) for advanced use cases
- [Check error handling](../../api-reference/error-handling.md) for production readiness
