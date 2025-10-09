# Configuration API Reference

Complete API reference for FiveTwenty's secure configuration system.

---

## Overview

FiveTwenty provides a secure, flexible configuration system with three main components:

| Component | Purpose | Key Features |
|-----------|---------|--------------|
| [AccountConfig](#accountconfig) | Account credentials & settings | Automatic secret masking, validation |
| [AccountConfigLoader](#accountconfigloader) | Load configs from environment | Custom prefixes, validation |
| [ConfigValidator](#configvalidator) | Configuration validation | Runtime validation, helpful errors |

---

## AccountConfig

Secure configuration object for OANDA account credentials and settings.

### Constructor

```python
from pydantic import SecretStr

from fivetwenty import AccountConfig, Environment

# Constructor signature:
def AccountConfig(
    account_id: SecretStr,
    alias: str,
    token: SecretStr,
    environment: Environment,
) -> AccountConfig:
    ...
```

**Parameters:**

- `account_id` (SecretStr) - OANDA account ID (protected credential)
- `alias` (str) - User-friendly identifier (must be valid Python identifier)
- `token` (SecretStr) - OANDA API token (protected credential)
- `environment` (Environment) - `Environment.PRACTICE` or `Environment.LIVE`

**Raises:**

- `ValidationError` - Invalid parameters (empty token/account_id, invalid alias format, etc.)

**Examples:**

```python
import os

from pydantic import SecretStr

from fivetwenty import AccountConfig, Environment

# Basic configuration
config = AccountConfig(
    account_id=SecretStr(os.environ["FIVETWENTY_OANDA_ACCOUNT"]),
    alias="my_trading_account",
    token=SecretStr(os.environ["FIVETWENTY_OANDA_TOKEN"]),
    environment=Environment.PRACTICE,
)

# Live trading configuration
live_config = AccountConfig(
    account_id=SecretStr(os.environ["FIVETWENTY_OANDA_ACCOUNT"]),
    alias="production_trading",
    token=SecretStr(os.environ["FIVETWENTY_OANDA_TOKEN"]),
    environment=Environment.LIVE,
)
```

### Properties

#### `token: SecretStr`
Protected API token that never appears in logs or string representations.

```python
import os

from pydantic import SecretStr

from fivetwenty import AccountConfig, Environment

config = AccountConfig(
    token=SecretStr(os.environ["FIVETWENTY_OANDA_TOKEN"]),
    account_id=SecretStr(os.environ["FIVETWENTY_OANDA_ACCOUNT"]),
    environment=Environment.PRACTICE,
    alias="example"
)
# Safe - returns SecretStr object
token_obj = config.token

# To access actual value (use with caution)
actual_token = config.token.get_secret_value()
```

#### `account_id: SecretStr`
Protected account ID that never appears in logs or string representations.

```python
import os

from pydantic import SecretStr

from fivetwenty import AccountConfig, Environment

config = AccountConfig(
    token=SecretStr(os.environ["FIVETWENTY_OANDA_TOKEN"]),
    account_id=SecretStr(os.environ["FIVETWENTY_OANDA_ACCOUNT"]),
    environment=Environment.PRACTICE,
    alias="example"
)
# Safe - returns SecretStr object
account_obj = config.account_id

# To access actual value (use with caution)
actual_account = config.account_id.get_secret_value()
```

#### `environment: Environment`
Trading environment (practice or live).

```python
import os

from pydantic import SecretStr

from fivetwenty import AccountConfig, Environment

config = AccountConfig(
    token=SecretStr(os.environ["FIVETWENTY_OANDA_TOKEN"]),
    account_id=SecretStr(os.environ["FIVETWENTY_OANDA_ACCOUNT"]),
    environment=Environment.PRACTICE,
    alias="example"
)
if config.environment == Environment.LIVE:
    print("LIVE trading - real money at risk")
else:
    print("Practice trading - virtual money")
```

#### `alias: str`
User-friendly identifier for the account configuration.

```python
import os

from pydantic import SecretStr

from fivetwenty import AccountConfig, Environment

config = AccountConfig(
    alias="my_bot",
    token=SecretStr(os.environ["FIVETWENTY_OANDA_TOKEN"]),
    account_id=SecretStr(os.environ["FIVETWENTY_OANDA_ACCOUNT"]),
    environment=Environment.PRACTICE
)
print("Bot name:", config.alias)  # Safe to log
```


### Methods

#### `summary() -> str`
Returns safe summary string suitable for logging.

**Returns:** `str` - Format: "{alias} ({environment})"

**Usage:**
```python
import logging

from pydantic import SecretStr

from fivetwenty import AccountConfig, Environment

logger = logging.getLogger(__name__)

config = AccountConfig(
    alias="my_trader",
    environment=Environment.PRACTICE,
    token=SecretStr("token"),
    account_id=SecretStr("account_id"),
)
print(config.summary())
logger.info("Starting trading session: %s", config.summary())
```

Expected output:
```text
my_trader (practice)
```

### Security Features

#### Automatic Secret Masking
All secret values are automatically masked in string representations:

```python
import os

from pydantic import SecretStr

from fivetwenty import AccountConfig, Environment

config = AccountConfig(
    token=SecretStr(os.environ["FIVETWENTY_OANDA_TOKEN"]),
    account_id=SecretStr(os.environ["FIVETWENTY_OANDA_ACCOUNT"]),
    alias="demo_account",
    environment=Environment.PRACTICE,
)

# Secrets are masked in all representations
print(repr(config))
# AccountConfig(alias='demo_account', environment=practice, token=SecretStr('***'), account_id=SecretStr('***'))

print(str(config))
# Secrets never appear

# Safe summary for logs
print(config.summary())
# demo_account (practice)
```

#### Validation

The configuration validates all inputs:

```python
from pydantic import SecretStr, ValidationError

from fivetwenty import AccountConfig, Environment

# Invalid alias (starts with number)
try:
    AccountConfig(
        alias="123invalid",  # Must be valid identifier
        token=SecretStr("token"),
        account_id=SecretStr("account"),
        environment=Environment.PRACTICE,
    )
except ValidationError:
    print("Alias must be valid Python identifier")

# Empty token
try:
    AccountConfig(
        token=SecretStr("   "),  # Whitespace-only
        account_id=SecretStr("account"),
        environment=Environment.PRACTICE,
        alias="valid_alias",
    )
except ValidationError:
    print("Token cannot be empty or whitespace")
```

---

## AccountConfigLoader

Utility class for loading account configurations from environment variables.

### Static Methods

#### `load_default() -> AccountConfig | None`
Load configuration from standard `FIVETWENTY_*` environment variables.

**Environment Variables:**

- `FIVETWENTY_OANDA_TOKEN` - API token (required)
- `FIVETWENTY_OANDA_ACCOUNT` - Account ID (required)
- `FIVETWENTY_OANDA_ENVIRONMENT` - "practice" or "live" (defaults to "practice")

**Returns:** `AccountConfig | None` - Configuration object or None if required variables missing

**Note:** The alias is automatically set to "default" when using `load_default()`.

**Usage:**
```python
# Set environment variables first
import os
from fivetwenty import AccountConfigLoader

# Load from environment (set these in your shell/deployment)
# os.environ["FIVETWENTY_OANDA_TOKEN"] = "your-actual-token"
os.environ["FIVETWENTY_OANDA_ACCOUNT"] = "your-account"
os.environ["FIVETWENTY_OANDA_ENVIRONMENT"] = "practice"

# Load configuration
config = AccountConfigLoader.load_default()
if config:
    print("Configuration loaded:", config.summary())  # "default (practice)"
else:
    print("Required environment variables not found")
```

#### `from_env_prefix(prefix: str) -> AccountConfig | None`
Load configuration using custom environment variable prefix.

**Parameters:**

- `prefix` (str) - Environment variable prefix (e.g., "STRATEGY_A_")

**Environment Variables Pattern:**

- `{prefix}FIVETWENTY_OANDA_TOKEN` - API token
- `{prefix}FIVETWENTY_OANDA_ACCOUNT` - Account ID
- `{prefix}FIVETWENTY_OANDA_ENVIRONMENT` - Environment (defaults to "practice")

**Note:** The alias is automatically generated from the prefix (lowercased, trailing underscore removed).

**Returns:** `AccountConfig | None` - Configuration object or None if required variables missing

**Usage:**
```python
# Set custom prefixed variables
import os

from fivetwenty import AccountConfigLoader

# Load from environment (set these in your shell/deployment)
# os.environ["STRATEGY_A_FIVETWENTY_OANDA_TOKEN"] = "your-actual-token"
os.environ["STRATEGY_A_FIVETWENTY_OANDA_ACCOUNT"] = "account-a"
os.environ["STRATEGY_A_FIVETWENTY_OANDA_ENVIRONMENT"] = "practice"

# Load with custom prefix
config = AccountConfigLoader.from_env_prefix("STRATEGY_A_")
if config:
    # Alias is automatically generated as "strategy_a"
    print("Strategy config:", config.summary())  # "strategy_a (practice)"
```

**Multi-Strategy Example:**
```python
# Load configurations for different strategies
from fivetwenty import AccountConfigLoader

momentum_config = AccountConfigLoader.from_env_prefix("MOMENTUM_")
grid_config = AccountConfigLoader.from_env_prefix("GRID_")
scalping_config = AccountConfigLoader.from_env_prefix("SCALPING_")

configs = [c for c in [momentum_config, grid_config, scalping_config] if c]
print("Loaded", len(configs), "strategy configurations")
```

---

## ConfigValidator

Validation utility for account configurations.

### Static Methods

#### `validate_account_config(config: AccountConfig) -> list[str]`
Validate an account configuration and return any errors found.

**Parameters:**

- `config` (AccountConfig) - Configuration to validate

**Returns:** `list[str]` - List of error messages (empty if valid)

**Validation Checks:**

- Token is not empty or whitespace-only
- Account ID is not empty or whitespace-only
- Alias is not empty or whitespace-only

**Usage:**
```python
from pydantic import SecretStr

from fivetwenty import AccountConfig, ConfigValidator, Environment

config = AccountConfig(
    token=SecretStr("valid-token"),
    account_id=SecretStr("valid-account"),
    environment=Environment.PRACTICE,
    alias="valid_alias",
)

errors = ConfigValidator.validate_account_config(config)
if errors:
    print("Configuration errors:")
    for error in errors:
        print("  - Error:", str(error))
else:
    print("Configuration is valid")
```

**Note:** AccountConfig validation happens automatically via Pydantic validators. The ConfigValidator provides additional runtime checks after construction.

---

## Environment Enum

Enumeration for OANDA trading environments.

### Definition

```python
from enum import Enum

class Environment(Enum):
    """OANDA trading environments."""
    PRACTICE = "practice"
    LIVE = "live"
```

### Values

#### `Environment.PRACTICE`
Practice trading environment with virtual money.

**Properties:**

- `value: "practice"`
- `base_url` (`https\://api-fxpractice.oanda.com/v3`)

#### `Environment.LIVE`
Live trading environment with real money.

**Properties:**

- `value: "live"`
- `base_url` (`https\://api-fxtrade.oanda.com/v3`)

### Usage

```python
from pydantic import SecretStr

from fivetwenty import AccountConfig, Environment

# Create configurations for different environments
practice_config = AccountConfig(
    environment=Environment.PRACTICE,
    token=SecretStr("practice_token"),
    account_id=SecretStr("practice_account_id"),
    alias="practice",
)

live_config = AccountConfig(
    environment=Environment.LIVE,
    token=SecretStr("live_token"),
    account_id=SecretStr("live_account_id"),
    alias="live",
)

# Check environment in code
config = practice_config  # Use one of the configs above
if config.environment == Environment.LIVE:
    print("Using live environment - real money at risk")

# Get base URL
print("API URL:", config.environment.base_url)
```

---

## Usage Patterns

### Basic Configuration

```python
import os

from pydantic import SecretStr

from fivetwenty import AccountConfig, Environment

config = AccountConfig(
    token=SecretStr(os.environ["FIVETWENTY_OANDA_TOKEN"]),
    account_id=SecretStr(os.environ["FIVETWENTY_OANDA_ACCOUNT"]),
    environment=Environment.PRACTICE,
    alias="basic_trading"
)
```

### Environment Variable Configuration

```python
from fivetwenty import AccountConfigLoader

# Load from standard variables
config = AccountConfigLoader.load_default()

# Load from custom prefix
strategy_config = AccountConfigLoader.from_env_prefix("STRATEGY_")
```

### Multi-Account Management

```python
from fivetwenty import AccountConfigLoader

# Load multiple account configurations

accounts = {
    "momentum": AccountConfigLoader.from_env_prefix("MOMENTUM_"),
    "grid": AccountConfigLoader.from_env_prefix("GRID_"),
    "scalping": AccountConfigLoader.from_env_prefix("SCALPING_"),
}

# Filter out None values
active_accounts = {name: config for name, config in accounts.items() if config}
print("Active strategies:", list(active_accounts.keys()))
```

### Configuration Validation

```python
from typing import Any
from fivetwenty import AccountConfig, ConfigValidator

def create_safe_config(**kwargs: Any) -> AccountConfig:
    """Create configuration with validation."""
    config = AccountConfig(**kwargs)

    errors = ConfigValidator.validate_account_config(config)
    if errors:
        error_message = f"Invalid configuration: {', '.join(errors)}"
        raise ValueError(error_message)

    return config
```

### Production Deployment

```python
import os
from fivetwenty import AccountConfig, AccountConfigLoader, Environment

def load_production_config() -> AccountConfig:
    """Load production configuration with safety checks."""
    config = AccountConfigLoader.load_default()

    if not config:
        config_error_msg = "No configuration found - check environment variables"
        raise RuntimeError(config_error_msg)

    # Ensure we're in the expected environment
    expected_env = os.environ.get("EXPECTED_OANDA_ENVIRONMENT", "practice")
    if config.environment.value != expected_env:
        env_error_msg = (
            f"Environment mismatch: expected {expected_env}, "
            f"got {config.environment.value}"
        )
        raise RuntimeError(env_error_msg)

    # Extra validation for live
    if config.environment == Environment.LIVE and "practice" in config.token.get_secret_value().lower():
        practice_error_msg = "Practice token detected in live environment"
        raise RuntimeError(practice_error_msg)

    return config
```

---

## Security Best Practices

### 1. Never Log Secrets

```python
import logging

from pydantic import SecretStr

from fivetwenty import AccountConfig, Environment

logger = logging.getLogger(__name__)
# Define config for demonstration
config = AccountConfig(
    token=SecretStr("demo-token"),
    account_id=SecretStr("demo-account"),
    environment=Environment.PRACTICE,
    alias="demo"
)

# Safe - uses automatic masking
logger.info("Config: %s", repr(config))
logger.info("Trading on: %s", config.summary())

# Dangerous - exposes secrets
# logger.info("Token: %s", config.token.get_secret_value())  # DON'T DO THIS - Security risk
```

### 2. Validate Before Use

```python
from fivetwenty import AccountConfig, AsyncClient, ConfigValidator

def safe_client_creation(config: AccountConfig) -> AsyncClient:
    """Create client with validation."""
    errors = ConfigValidator.validate_account_config(config)
    if errors:
        error_message = f"Invalid config: {', '.join(errors)}"
        raise ValueError(error_message)

    return AsyncClient(config=config)
```

### 3. Environment Separation

```python
# Separate environment variables
# Practice: PRACTICE_FIVETWENTY_*
# Live: LIVE_FIVETWENTY_*
from fivetwenty import AccountConfig, AccountConfigLoader

def load_env_specific_config(env: str) -> AccountConfig:
    """Load configuration for specific environment."""
    prefix = f"{env.upper()}_FIVETWENTY_"
    config = AccountConfigLoader.from_env_prefix(prefix)

    if not config:
        error_message = f"No {env} configuration found"
        raise ValueError(error_message)

    return config
```

### 4. Runtime Verification

```python
import logging
from fivetwenty import AccountConfig, AsyncClient

logger = logging.getLogger(__name__)

async def verify_config_connection(config: AccountConfig) -> bool:
    """Test configuration by connecting to API."""
    try:
        async with AsyncClient(config=config) as client:
            accounts = await client.accounts.get_accounts()
            return len(accounts) > 0
    except Exception as e:
        error_msg = f"Config verification failed: {e}"
        logger.exception(error_msg)
        return False
```

---

## Error Reference

### ValidationError
Raised by Pydantic when configuration parameters are invalid.

**Common Causes:**

- Empty or whitespace-only token/account_id
- Invalid alias format (not a valid Python identifier)
- Invalid environment value

**Example:**
```python
from pydantic import ValidationError
from pydantic import SecretStr

from fivetwenty import AccountConfig, Environment

try:
    config = AccountConfig(
        token=SecretStr(""),
        account_id=SecretStr("123"),
        environment=Environment.PRACTICE,
        alias="123invalid",
    )
except ValidationError as e:
    # Handle validation errors
    for error in e.errors():
        print("Validation error - Field:", error['loc'], "Error:", error['msg'])
```

### ValueError
Raised by loader methods when required environment variables are missing.

**Example:**
```python
from fivetwenty import AccountConfigLoader

config = AccountConfigLoader.load_default()
if not config:
    error_msg = "Required environment variables not set"
    raise ValueError(error_msg)
```

---
