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

### 1. Direct Parameters (Simple)

For quick scripts and testing:

```python
from fivetwenty import AsyncClient, Environment

async with AsyncClient(
    token="your-api-token",
    environment=Environment.PRACTICE
) as client:
    accounts = await client.accounts.list()
    print(f"Found {len(accounts)} accounts")
```

### 2. Configuration Objects (Recommended)

For production applications with multiple accounts:

```python
from fivetwenty import AsyncClient, Environment

from fivetwenty import AccountConfig, AsyncClient, Environment

# Create secure configuration
config = AccountConfig(
    token="your-api-token",
    account_id="your-account-id",
    environment=Environment.PRACTICE,
    alias="my_trading_account",

)

# Use configuration
async with AsyncClient(config=config) as client:
    accounts = await client.accounts.list()
    print(f"Using account: {client.config.summary()}")
```

### 3. Environment Variables (Deployment)

For Docker, Kubernetes, and CI/CD:

```bash
# Set environment variables
export FIVETWENTY_OANDA_TOKEN="your-api-token"
export FIVETWENTY_OANDA_ACCOUNT="your-account-id"
export FIVETWENTY_OANDA_ENVIRONMENT="practice"
export FIVETWENTY_OANDA_ACCOUNT_ALIAS="my_trading_account"
```

```python
from fivetwenty import AsyncClient, Environment

# Zero-config - automatically loads environment variables
async with AsyncClient() as client:
    accounts = await client.accounts.list()
    print(f"Loaded config: {client.config.summary()}")
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
from dotenv import load_dotenv
from fivetwenty import AsyncClient

# Load .env file
load_dotenv()

# Automatically uses environment variables
async with AsyncClient() as client:
    accounts = await client.accounts.list()
```

### Secret Management Systems

For production deployments:

#### AWS Secrets Manager

```python
from fivetwenty import AsyncClient, Environment

import boto3
from fivetwenty import AccountConfig, AsyncClient, Environment

def get_fivetwenty_config():
    """Load OANDA configuration from AWS Secrets Manager."""

    client = boto3.client('secretsmanager')
    response = client.get_secret_value(SecretId='OANDA/api-credentials')

    import json
    secrets = json.loads(response['SecretString'])

    return AccountConfig(
        token=secrets['token'],
        account_id=secrets['account_id'],
        environment=Environment.LIVE,
        alias="production_trading"
    )

# Use in application
config = get_fivetwenty_config()
async with AsyncClient(config=config) as client:
    accounts = await client.accounts.list()
```

#### HashiCorp Vault

```python
from fivetwenty import Client
import os
import hvac
from fivetwenty import AccountConfig, Environment

def get_vault_config():
    """Load configuration from HashiCorp Vault."""

    client = hvac.Client(url='https://vault.example.com')
    client.token = os.environ['VAULT_TOKEN']

    secret = client.secrets.kv.v2.read_secret_version(
        path='OANDA/credentials',
        mount_point='secret'
    )

    data = secret['data']['data']

    return AccountConfig(
        token=data['api_token'],
        account_id=data['account_id'],
        environment=Environment.LIVE,
        alias="vault_trading_account"
    )
```

#### Kubernetes Secrets

```yaml
# secret.yaml
apiVersion: v1
kind: Secret
metadata:
  name: OANDA-credentials
type: Opaque
data:
  FIVETWENTY_OANDA_TOKEN: <base64-encoded-token>
  FIVETWENTY_OANDA_ACCOUNT: <base64-encoded-account-id>
stringData:
  FIVETWENTY_OANDA_ENVIRONMENT: "live"
  FIVETWENTY_OANDA_ACCOUNT_ALIAS: "kubernetes_trading"

---
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
spec:
  template:
    spec:
      containers:
      - name: trading-app
        envFrom:
        - secretRef:
            name: OANDA-credentials
```

## Multiple Account Configuration

### Different Environments

```python
import os
from fivetwenty import AsyncClient, Environment

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
    await test_strategy(practice_client)

# Deploy to live after validation
async with AsyncClient(config=live_config) as live_client:
    await execute_live_trades(live_client)
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
from fivetwenty import AsyncClient, Environment

from fivetwenty import AccountConfigLoader, AsyncClient

# Load configurations with custom prefixes
momentum_config = AccountConfigLoader.from_env_prefix("MOMENTUM_")
grid_config = AccountConfigLoader.from_env_prefix("GRID_")

# Run strategies in parallel
async with AsyncClient(config=momentum_config) as momentum_client:
    async with AsyncClient(config=grid_config) as grid_client:
        await asyncio.gather(
            run_momentum_strategy(momentum_client),
            run_grid_strategy(grid_client)
        )
```

## Security Features

### Automatic Secret Masking

The library automatically protects sensitive information:

```python
from fivetwenty import AccountConfig
from fivetwenty import Environment

config = AccountConfig(
    token = 'your-api-token-here',
    account_id="secret-account-123",
    environment=Environment.PRACTICE,
    alias="my_account"
)

# Secrets are automatically masked in logs
print(repr(config))
# AccountConfig(alias='my_account', environment=practice, token=SecretStr('***'), account_id=SecretStr('***'))

# Safe summary for monitoring
print(config.summary())
# my_account (practice)
```

### Configuration Validation

The library validates all configuration values:

```python
from fivetwenty import AccountConfig
from fivetwenty import Environment
from pydantic import ValidationError

try:
    config = AccountConfig(
        token="   ",  # Empty token - rejected
        account_id="123-456-789",
        environment=Environment.PRACTICE,
        alias="my_account"
    )
except ValidationError as e:
    print("Invalid configuration:", e)

try:
    config = AccountConfig(
        token="valid-token",
        account_id="valid-account",
        environment=Environment.PRACTICE,
        alias="123invalid"  # Invalid alias - starts with number
    )
except ValidationError as e:
    print("Invalid alias:", e)
```

## Testing Authentication

### Verify Configuration

```python
import os
import asyncio
from fivetwenty import AsyncClient, Environment

async def test_authentication():
    """Test OANDA API authentication."""

    try:
        async with AsyncClient(
            token=os.environ["FIVETWENTY_OANDA_TOKEN"],
            environment=Environment.PRACTICE
        ) as client:
            # Test authentication by listing accounts
            accounts = await client.accounts.list()

            print("✅ Authentication successful!")
            print(f"Configuration: {client.config.summary()}")
            print(f"Found {len(accounts)} account(s):")

            for account in accounts:
                print(f"  • {account.id}: {account.alias}")
                print(f"    Balance: {account.balance} {account.currency}")

    except Exception as e:
        print(f"❌ Authentication failed: {e}")
        print("Check your token and environment configuration")

# Run test
asyncio.run(test_authentication())
```

### Validate Configuration

```python
import os
from fivetwenty import ConfigValidator, AccountConfig, Environment

# Create configuration
config = AccountConfig(
    token=os.environ["FIVETWENTY_OANDA_TOKEN"],
    account_id=os.environ["FIVETWENTY_OANDA_ACCOUNT"],
    environment=Environment.PRACTICE,
    alias="test_account"
)

# Validate configuration
errors = ConfigValidator.validate_account_config(config)

if errors:
    print("Configuration errors:")
    for error in errors:
        print(f"  • {error}")
else:
    print("✅ Configuration is valid")
```

## Advanced HTTP Configuration

### Proxy Configuration

If you need to use a proxy:

```python
from fivetwenty import AsyncClient, Environment

# Simple proxy
async with AsyncClient(
    token="your-token",
    environment=Environment.PRACTICE,
    proxies="http://proxy.example.com:8080"
) as client:
    accounts = await client.accounts.list()

# Authenticated proxy
proxy_url = "http://username:password@proxy.example.com:8080"
async with AsyncClient(
    token="your-token",
    environment=Environment.PRACTICE,
    proxies=proxy_url
) as client:
    accounts = await client.accounts.list()
```

### Custom SSL Configuration

For corporate environments:

```python
from fivetwenty import Client
from fivetwenty import AsyncClient, Environment

# Custom CA bundle
async with AsyncClient(
    token="your-token",
    environment=Environment.PRACTICE,
    verify="/path/to/ca-bundle.crt"
) as client:
    accounts = await client.accounts.list()

# Client certificate authentication
async with AsyncClient(
    token="your-token",
    environment=Environment.PRACTICE,
    cert="/path/to/client-cert.pem"
) as client:
    accounts = await client.accounts.list()

# Disable SSL verification (not recommended)
async with AsyncClient(
    token="your-token",
    environment=Environment.PRACTICE,
    verify=False
) as client:
    accounts = await client.accounts.list()
```

### Custom HTTP Transport

For advanced HTTP configuration:

```python
from fivetwenty import AsyncClient, Environment

import httpx

# Create custom HTTP client
transport = httpx.AsyncClient(
    timeout=httpx.Timeout(
        connect=5.0,
        read=60.0,
        write=10.0,
        pool=60.0
    ),
    limits=httpx.Limits(
        max_connections=100,
        max_keepalive_connections=20
    ),
    http2=False,
    trust_env=True
)

# Use with FiveTwenty client
async with AsyncClient(
    token="your-token",
    environment=Environment.PRACTICE,
    transport=transport
) as client:
    accounts = await client.accounts.list()
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
except ValueError as e:
    print(f"Configuration error: {e}")
    # Fix: Set FIVETWENTY_OANDA_TOKEN environment variable

# Error: Invalid token format
try:
    client = AsyncClient(token="invalid-token")
    await client.accounts.list()
except Exception as e:
    print(f"Authentication error: {e}")
    # Fix: Get valid token from OANDA account settings

# Error: Wrong environment
try:
    client = AsyncClient(
        token="practice-token",
        environment=Environment.LIVE  # Wrong environment
    )
    await client.accounts.list()
except Exception as e:
    print(f"Environment error: {e}")
    # Fix: Use correct environment for your token
```

### Debug Authentication Issues

```python
from fivetwenty import AsyncClient, Environment

# Check configuration
client = AsyncClient(token="your-token", environment=Environment.PRACTICE)

print(f"Environment: {client.config.environment.value}")
print(f"Account ID: {client.account_id}")
print(f"Config summary: {client.config.summary()}")

# Validate manually
from fivetwenty import ConfigValidator
errors = ConfigValidator.validate_account_config(client.config)
if errors:
    print("Configuration issues:", errors)
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
    accounts = await client.accounts.list()
```

## Migration from Previous Versions

If upgrading from an older version:

```python
# Old way (deprecated)
from fivetwenty import AsyncClient, Environment
client = AsyncClient("token", Environment.PRACTICE)

# New way - Direct parameters
from fivetwenty import AsyncClient, Environment
client = AsyncClient(token="token", environment=Environment.PRACTICE)

# New way - Configuration object (recommended)
from fivetwenty import AccountConfig, AsyncClient, Environment
config = AccountConfig(
    token="token",
    account_id="account-id",
    environment=Environment.PRACTICE,
    alias="my_account"
)
client = AsyncClient(config=config)
```

## Next Steps

Now that authentication is configured:

- [Learn about environments](environments.md) to understand practice vs live trading
- [Make your first trade](first-trade.md) to test your setup
- [Review configuration options](../../explanation/configuration.md) for advanced use cases
- [Check error handling](../../explanation/error-handling.md) for production readiness
