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


async def main():
    import os

    from fivetwenty import AccountConfig, AsyncClient, Environment

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

async def test_strategy(client: AsyncClient) -> None:
    """Test trading strategy on practice account."""
    accounts = await client.accounts.get_accounts()
    print(f"Strategy test completed with {len(accounts)} accounts")

    # Deploy to live after validation
    async with AsyncClient(config=live_config) as live_client:
        print(f"Executing live trades on account: {live_config.alias}")
        await execute_live_trades(live_client)

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

## Advanced HTTP Configuration

### Proxy Configuration

If you need to use a proxy:

```python
import asyncio


async def main():
    from fivetwenty import AsyncClient, Environment

    # Simple proxy
    async with AsyncClient(
        token="your-token",
        environment=Environment.PRACTICE,
        proxies="http://proxy.example.com:8080",
    ) as client:
        accounts = await client.accounts.get_accounts()
        print(f"Retrieved {len(accounts)} accounts via simple proxy")

    # Authenticated proxy
    proxy_url = "http://username:password@proxy.example.com:8080"
    async with AsyncClient(
        token="your-token",
        environment=Environment.PRACTICE,
        proxies=proxy_url,
    ) as client:
        accounts = await client.accounts.get_accounts()
        print(f"Retrieved {len(accounts)} accounts via authenticated proxy")

asyncio.run(main())
```

### Custom SSL Configuration

For corporate environments:

```python
from fivetwenty import AsyncClient, Environment

# Custom CA bundle
async with AsyncClient(
    token="your-token",
    environment=Environment.PRACTICE,
    verify="/path/to/ca-bundle.crt"
) as client:
    accounts = await client.accounts.get_accounts()
    print(f"Retrieved {len(accounts)} accounts with custom CA bundle")

# Client certificate authentication
async with AsyncClient(
    token="your-token",
    environment=Environment.PRACTICE,
    cert="/path/to/client-cert.pem"
) as client:
    accounts = await client.accounts.get_accounts()
    print(f"Retrieved {len(accounts)} accounts with client certificate")

# Disable SSL verification (not recommended)
async with AsyncClient(
    token="your-token",
    environment=Environment.PRACTICE,
    verify=False
) as client:
    accounts = await client.accounts.get_accounts()
    print(f"Retrieved {len(accounts)} accounts with SSL verification disabled")
```

### Custom HTTP Transport

For advanced HTTP configuration:

```python
import asyncio


async def main():
    import httpx

    from fivetwenty import AsyncClient, Environment

    # Create custom HTTP client
    transport = httpx.AsyncClient(
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
    print("Custom HTTP transport configured")

    # Use with FiveTwenty client
    async with AsyncClient(
        token="your-token",
        environment=Environment.PRACTICE,
        transport=transport,
    ) as client:
        accounts = await client.accounts.get_accounts()
        print(f"Retrieved {len(accounts)} accounts with custom transport")

asyncio.run(main())
```

## Production Deployment

### Docker Configuration

```dockerfile
FROM python:3.11-slim

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . /app
WORKDIR /app

# Set non-secret environment variables
ENV FIVETWENTY_OANDA_ENVIRONMENT=live
ENV FIVETWENTY_OANDA_ACCOUNT_ALIAS=docker_trading

# Never set secrets in Dockerfile
# ENV FIVETWENTY_OANDA_TOKEN=""  # NO!
# ENV FIVETWENTY_OANDA_ACCOUNT=""  # NO!

CMD ["python", "main.py"]
```

```bash
# Pass secrets at runtime
docker run -e FIVETWENTY_OANDA_TOKEN="$SECRET_TOKEN" \
           -e FIVETWENTY_OANDA_ACCOUNT="$SECRET_ACCOUNT" \
           my-trading-app
# This way secrets are never stored in the image
```

### CI/CD Configuration

For GitHub Actions:

```yaml
# .github/workflows/deploy.yml
name: Deploy Trading Bot

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Test Authentication
        env:
          FIVETWENTY_OANDA_TOKEN: ${{ secrets.FIVETWENTY_OANDA_TOKEN }}
          FIVETWENTY_OANDA_ACCOUNT: ${{ secrets.FIVETWENTY_OANDA_ACCOUNT }}
          FIVETWENTY_OANDA_ENVIRONMENT: practice
        run: |
          python test_auth.py

      - name: Deploy to Production
        env:
          FIVETWENTY_OANDA_TOKEN: ${{ secrets.FIVETWENTY_LIVE_TOKEN }}
          FIVETWENTY_OANDA_ACCOUNT: ${{ secrets.OANDA_LIVE_ACCOUNT }}
          FIVETWENTY_OANDA_ENVIRONMENT: live
        run: |
          echo "Deploying to production environment"
          python deploy.py
```

## Best Practices

### Security

1. **Never commit tokens** - Use environment variables or secret management
2. **Rotate tokens regularly** - Generate new tokens periodically
3. **Use separate tokens** - Different tokens for different environments
4. **Validate configurations** - Check settings before deployment
5. **Monitor token usage** - Track API usage and anomalies

### Organization

1. **Use descriptive aliases** - Make account purposes clear
2. **Document configurations** - Comment your setup
3. **Environment-specific settings** - Different configs per environment
4. **Test authentication** - Verify setup before deploying
5. **Log safely** - Never log tokens or secrets

### Performance

1. **Reuse clients** - Don't create new clients for each request
2. **Configure timeouts** - Set appropriate timeout values
3. **Use connection pooling** - Optimize for high-frequency trading
4. **Handle rate limits** - Implement proper backoff strategies
5. **Cache configurations** - Load once, use many times

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

## Migration from Previous Versions

If upgrading from an older version:

```python
# Old way (deprecated)
from fivetwenty import AsyncClient, Environment

client = AsyncClient("token", Environment.PRACTICE)
print("Old-style client created (deprecated)")

# New way - Direct parameters
from fivetwenty import AsyncClient, Environment

client = AsyncClient(token="token", environment=Environment.PRACTICE)
print("New-style client created with direct parameters")

# New way - Configuration object (recommended)
from fivetwenty import AccountConfig, AsyncClient, Environment

config = AccountConfig(
    token="token",
    account_id="account-id",
    environment=Environment.PRACTICE,
    alias="my_account",
)
client = AsyncClient(config=config)
print(f"New-style client created with config object: {config.summary()}")
```

## Next Steps

Now that authentication is configured:

- [Learn about environments](environments.md) to understand practice vs live trading
- [Make your first trade](first-trade.md) to test your setup
- [Review configuration options](../../explanation/configuration.md) for advanced use cases
- [Check error handling](../../explanation/error-handling.md) for production readiness
