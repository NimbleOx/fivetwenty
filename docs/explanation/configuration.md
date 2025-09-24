# Configuration

The FiveTwenty library provides flexible configuration options to manage your OANDA API credentials and client settings securely. This guide covers all configuration patterns and advanced options.

## Overview

The library supports three main configuration approaches:

1. **Direct parameters** - Straightforward and explicit
2. **Configuration objects** - Structured and reusable
3. **Environment variables** - Zero-config deployment

All approaches prioritize security by automatically masking sensitive information in logs and output.

## Quick Start

### Direct Parameters

The simplest way to configure the client:

```python
from fivetwenty import AsyncClient, Environment

async with AsyncClient(
    token="your-api-token",
    environment=Environment.PRACTICE
) as client:
    accounts = await client.accounts.list()
```

### Configuration Objects

For more structured configuration:

```python
from fivetwenty import AsyncClient, Environment

from fivetwenty import AccountConfig, AsyncClient, Environment

# Create configuration
config = AccountConfig(
    token="your-api-token",
    account_id="your-account-id",
    environment=Environment.PRACTICE,
    alias="my_trading_account",

)

# Use configuration
async with AsyncClient(config=config) as client:
    accounts = await client.accounts.list()
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
from fivetwenty import AsyncClient, Environment

# No configuration needed - loads automatically
async with AsyncClient() as client:
    accounts = await client.accounts.list()
```

## Configuration Patterns

### 1. Direct Parameters Pattern

Best for: Basic scripts, getting started, testing

```python
from fivetwenty import AsyncClient, Environment

# Minimal configuration
client = AsyncClient(
    token="your-token",
    environment=Environment.PRACTICE
)

# With optional account ID for convenience
client = AsyncClient(
    token="your-token",
    account_id="your-account-id",
    environment=Environment.LIVE
)

# With additional client options
client = AsyncClient(
    token="your-token",
    environment=Environment.PRACTICE,
    timeout=60.0,
    max_retries=5,
    user_agent="MyTradingBot/1.0"
)
```

### 2. Configuration Objects Pattern

Best for: Production applications, multiple accounts, reusable configurations

```python
from fivetwenty import AsyncClient, Environment

from fivetwenty import AccountConfig, AsyncClient, Environment

# Create reusable configurations
practice_config = AccountConfig(
    token="practice-token",
    account_id="practice-account-123",
    environment=Environment.PRACTICE,
    alias="practice_trading",

)

live_config = AccountConfig(
    token="live-token",
    account_id="live-account-456",
    environment=Environment.LIVE,
    alias="live_trading",

)

# Use configurations
async with AsyncClient(config=practice_config) as practice_client:
    # Test strategies safely
    await test_strategy(practice_client)

async with AsyncClient(config=live_config) as live_client:
    # Execute live trades
    await execute_trades(live_client)
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
from fivetwenty import AsyncClient, Environment

# Automatically loads FIVETWENTY_* variables
async with AsyncClient() as client:
    accounts = await client.accounts.list()
```

#### Custom Environment Variable Prefixes

For multiple accounts or microservices:

```python
from fivetwenty import AsyncClient, Environment

from fivetwenty import AccountConfigLoader, AsyncClient

# Load with custom prefix
momentum_config = AccountConfigLoader.from_env_prefix("MOMENTUM_")
grid_config = AccountConfigLoader.from_env_prefix("GRID_")

# Use different clients for different strategies
async with AsyncClient(config=momentum_config) as momentum_client:
    async with AsyncClient(config=grid_config) as grid_client:
        await run_parallel_strategies(momentum_client, grid_client)
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
from fivetwenty import AsyncClient, Environment

# Config object takes priority over direct parameters
config = AccountConfig(token="config-token", account_id="account-id")
client = AsyncClient(
    token="direct-token",  # Ignored
    config=config  # Used
)

# Direct parameters take priority over environment variables
# (assuming FIVETWENTY_OANDA_TOKEN is set)
client = AsyncClient(
    token="direct-token"  # Used instead of FIVETWENTY_OANDA_TOKEN
)
```

## Security Features

### Automatic Secret Masking

The library automatically protects sensitive information:

```python
from fivetwenty import AsyncClient, Environment

config = AccountConfig(
    token="super-secret-token",
    account_id="secret-account-123",
    environment=Environment.PRACTICE,
    alias="my_account"
)

# Secrets are automatically masked
print(repr(config))
# AccountConfig(alias='my_account', environment=practice, token=SecretStr('***'), account_id=SecretStr('***'))

# Safe for logs
print(config.summary())
# my_account (practice)

# Access configuration safely
client = AsyncClient(config=config)
print(f"Using account: {client.account_id}")
# Using account: secret-account-123
```

### Validation

The library validates configuration values:

```python
from pydantic import ValidationError

# Invalid alias (starts with number)
try:
    config = AccountConfig(
        token="token",
        account_id="account",
        environment=Environment.PRACTICE,
        alias="123invalid"  # Error!
    )
except ValidationError as e:
    print("Alias must be a valid identifier")

# Empty tokens are rejected
try:
    config = AccountConfig(
        token="   ",  # Whitespace-only token
        account_id="account",
        environment=Environment.PRACTICE,
        alias="valid_alias"
    )
except ValidationError as e:
    print("Token cannot be empty")
```

### Configuration Validation

Use the validator to check configuration:

```python
from fivetwenty import ConfigValidator

config = AccountConfig(...)
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
from fivetwenty import AsyncClient, Environment

import httpx

# Custom HTTP client configuration
async with AsyncClient(
    token="your-token",
    environment=Environment.PRACTICE,
    timeout=60.0,
    max_retries=5,
    user_agent="MyTradingApp/1.0",
    proxies="http://proxy.example.com:8080",
    verify=True,  # or "/path/to/ca-bundle.crt"
    cert="/path/to/client-cert.pem"
) as client:
    pass
```

### Custom HTTP Transport

For advanced HTTP configuration:

```python
from fivetwenty import AsyncClient, Environment

import httpx

# Create custom transport
transport = httpx.AsyncClient(
    base_url=Environment.PRACTICE.base_url,
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

# Use with client
async with AsyncClient(
    token="your-token",
    environment=Environment.PRACTICE,
    transport=transport
) as client:
    pass
```

### Logging Configuration

```python
from fivetwenty import AsyncClient, Environment

import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("my_trading_app")

# Pass logger to client
async with AsyncClient(
    token="your-token",
    environment=Environment.PRACTICE,
    logger=logger
) as client:
    # Client operations will be logged
    accounts = await client.accounts.list()
```

## Sync Client Configuration

The sync `Client` supports the same configuration patterns:

```python
from fivetwenty import Client, AccountConfig, Environment

# Direct parameters
with Client(token="your-token", environment=Environment.PRACTICE) as client:
    accounts = client.accounts.list()

# Configuration object
config = AccountConfig(...)
with Client(config=config) as client:
    accounts = client.accounts.list()

# Environment variables
with Client() as client:  # Loads from FIVETWENTY_* variables
    accounts = client.accounts.list()
```

## Production Deployment Patterns

### Docker Configuration

```dockerfile
FROM python:3.11-slim

# Install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy application
COPY . /app
WORKDIR /app

# Set environment variables
ENV FIVETWENTY_OANDA_ENVIRONMENT=live
ENV FIVETWENTY_OANDA_ACCOUNT_ALIAS=production_trading

# Secrets should be passed at runtime
# ENV FIVETWENTY_OANDA_TOKEN=""  # Don't set in Dockerfile
# ENV FIVETWENTY_OANDA_ACCOUNT=""  # Don't set in Dockerfile

CMD ["python", "main.py"]
```

```bash
# Run with secrets from environment/vault
docker run -e FIVETWENTY_OANDA_TOKEN="$SECRET_TOKEN" \
           -e FIVETWENTY_OANDA_ACCOUNT="$SECRET_ACCOUNT" \
           my-trading-app
```

### Kubernetes Configuration

```yaml
# configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: trading-config
data:
  FIVETWENTY_OANDA_ENVIRONMENT: "live"
  FIVETWENTY_OANDA_ACCOUNT_ALIAS: "k8s_trading"

---
# secret.yaml
apiVersion: v1
kind: Secret
metadata:
  name: trading-secrets
type: Opaque
data:
  FIVETWENTY_OANDA_TOKEN: <base64-encoded-token>
  FIVETWENTY_OANDA_ACCOUNT: <base64-encoded-account-id>

---
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: trading-app
spec:
  template:
    spec:
      containers:
      - name: trading-app
        image: my-trading-app:latest
        envFrom:
        - configMapRef:
            name: trading-config
        - secretRef:
            name: trading-secrets
```

### AWS Lambda Configuration

```python
import os
import boto3
from fivetwenty import AsyncClient

def get_secret(secret_name):
    """Get secret from AWS Secrets Manager."""

    session = boto3.Session()
    client = session.client('secretsmanager')

    response = client.get_secret_value(SecretId=secret_name)
    return response['SecretString']

def lambda_handler(event, context):
    """Lambda handler with secure configuration."""

    # Load secrets from AWS Secrets Manager
    token = get_secret('OANDA/api-token')
    account_id = get_secret('OANDA/account-id')

    # Environment from Lambda environment variables
    environment = os.environ.get('FIVETWENTY_OANDA_ENVIRONMENT', 'practice')

    async with AsyncClient(
        token=token,
        account_id=account_id,
        environment=Environment.PRACTICE if environment == 'practice' else Environment.LIVE
    ) as client:
        # Your trading logic here
        accounts = await client.accounts.list()
        return {'accounts': len(accounts)}
```

## Configuration Management Utilities

### Configuration Builder

```python
from fivetwenty import AccountConfig, Environment
from typing import Optional

class ConfigBuilder:
    """Helper to build configurations from various sources."""

    @staticmethod
    def from_vault(vault_client, secret_path: str, environment: str) -> AccountConfig:
        """Load configuration from HashiCorp Vault."""

        secret = vault_client.secrets.kv.v2.read_secret_version(
            path=secret_path,
            mount_point='secret'
        )

        data = secret['data']['data']

        return AccountConfig(
            token=data['token'],
            account_id=data['account_id'],
            environment=Environment.PRACTICE if environment == 'practice' else Environment.LIVE,
            alias=data.get('alias', 'vault_account'),
            description=data.get('description')
        )

    @staticmethod
    def from_json_file(file_path: str) -> AccountConfig:
        """Load configuration from JSON file (non-secret data only)."""

        import json

        with open(file_path) as f:
            data = json.load(f)

        return AccountConfig(
            token=os.environ['FIVETWENTY_OANDA_TOKEN'],  # From environment
            account_id=os.environ['FIVETWENTY_OANDA_ACCOUNT'],  # From environment
            environment=Environment(data['environment']),
            alias=data['alias'],
            description=data.get('description')
        )
```

### Multi-Environment Manager

```python
from fivetwenty import AsyncClient, Environment

from typing import Dict
import os

class ConfigManager:
    """Manage configurations for multiple environments."""

    def __init__(self):
        self.configs: Dict[str, AccountConfig] = {}
        self._load_configs()

    def _load_configs(self):
        """Load configurations for all environments."""

        environments = ['development', 'staging', 'production']

        for env in environments:
            prefix = f"{env.upper()}_FIVETWENTY_"

            config = AccountConfigLoader.from_env_prefix(prefix)
            if config:
                self.configs[env] = config

    def get_config(self, environment: str) -> Optional[AccountConfig]:
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
dev_client = manager.get_client('development')
prod_client = manager.get_client('production')
```

## Best Practices

### Security

1. **Never hardcode secrets** - Use environment variables, vaults, or secure storage
2. **Use configuration objects** - Better type safety and validation
3. **Validate configurations** - Check values before creating clients
4. **Rotate tokens regularly** - Update API tokens periodically
5. **Use separate accounts** - Different accounts for different environments

### Organization

1. **Use descriptive aliases** - Make account purposes clear
2. **Document configurations** - Comment your configuration logic
3. **Environment-specific settings** - Different timeouts/retries per environment
4. **Version configurations** - Track configuration changes
5. **Test configurations** - Validate before deployment

### Performance

1. **Reuse configurations** - Create once, use multiple times
2. **Appropriate timeouts** - Balance speed vs reliability
3. **Configure retries** - More retries in production
4. **Connection pooling** - Use custom HTTP transport for high throughput
5. **Monitor configuration** - Log configuration on startup

### Deployment

1. **Use environment variables** - Best for containerized deployments
2. **Separate secrets** - Keep secrets separate from configuration
3. **Validate on startup** - Fail fast with invalid configuration
4. **Log safely** - Configuration summaries, never secrets
5. **Health checks** - Verify configuration and connectivity

## Troubleshooting

### Common Configuration Errors

```python
from fivetwenty import AsyncClient, AccountConfig
from pydantic import ValidationError

# Error: Missing configuration
try:
    client = AsyncClient()  # No env vars set
except ValueError as e:
    print(f"Configuration error: {e}")
    # Fix: Set FIVETWENTY_OANDA_TOKEN and FIVETWENTY_OANDA_ACCOUNT

# Error: Invalid alias format
try:
    config = AccountConfig(
        token="token",
        account_id="account",
        environment=Environment.PRACTICE,
        alias="123-invalid"  # Starts with number
    )
except ValidationError as e:
    print(f"Validation error: {e}")
    # Fix: Use valid identifier like "account_123"

# Error: Empty token
try:
    config = AccountConfig(
        token="",  # Empty token
        account_id="account",
        environment=Environment.PRACTICE,
        alias="my_account"
    )
except ValidationError as e:
    print(f"Token error: {e}")
    # Fix: Provide valid token
```

### Debug Configuration

```python
from fivetwenty import AsyncClient, Environment

# Check what configuration is being used
client = AsyncClient(token="your-token", environment=Environment.PRACTICE)

print(f"Account ID: {client.account_id}")
print(f"Environment: {client.config.environment.value}")
print(f"Alias: {client.config.alias}")
print(f"Configuration summary: {client.config.summary()}")

# Validate configuration manually
from fivetwenty import ConfigValidator
errors = ConfigValidator.validate_account_config(client.config)
if errors:
    print("Configuration issues:", errors)
else:
    print("Configuration is valid")
```

## Migration Guide

### From Old Configuration

If you were using the previous configuration format:

```python
from fivetwenty import AsyncClient, Environment

# Old way (no longer supported)
client = AsyncClient("your-token", Environment.PRACTICE)

# New way - Direct parameters
client = AsyncClient(token="your-token", environment=Environment.PRACTICE)

# Or configuration object (recommended)
config = AccountConfig(
    token="your-token",
    account_id="your-account-id",
    environment=Environment.PRACTICE,
    alias="my_account"
)
client = AsyncClient(config=config)
```

## Next Steps

- Learn about [environments](../tutorials/getting-started/environments.md) and their differences
- See [authentication](../tutorials/getting-started/authentication.md) for getting API tokens
- Review [best practices](best-practices.md) for production deployment
- Check [error handling](error-handling.md) for configuration-related errors