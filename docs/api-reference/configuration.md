# Configuration API Reference

!!! note "📚 Reference - Information-oriented content"
    **Use this reference when:** You need to look up specific configuration classes, methods, and parameters

    **Content type:** Complete technical specifications for FiveTwenty configuration system

    **Assumed knowledge:** Python type hints, Pydantic models, and environment variable concepts

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

### Class Definition

<!-- fragment: Demo AccountConfig class definition with import redefinition -->
```python
from pydantic import BaseModel, SecretStr
from fivetwenty import Environment, AccountConfig

class AccountConfig(BaseModel):
    """Configuration for a single OANDA trading account."""

    token: SecretStr
    account_id: SecretStr
    environment: Environment
    alias: str
```

### Constructor

<!-- fragment: Demo constructor with SecretStr type compatibility issues -->
```python
from pydantic import SecretStr
from fivetwenty import Environment, AccountConfig

def create_account_config(
    token: SecretStr | str,
    account_id: SecretStr | str,
    environment: Environment,
    alias: str,
) -> AccountConfig:
    """Create an AccountConfig instance."""
    return AccountConfig(
        token=token,
        account_id=account_id,
        environment=environment,
        alias=alias
    )
```

**Parameters:**

- `token` (SecretStr | str) - OANDA API token (automatically protected)
- `account_id` (SecretStr | str) - OANDA account ID (automatically protected)
- `environment` (Environment) - `Environment.PRACTICE` or `Environment.LIVE`
- `alias` (str) - User-friendly identifier (must be valid Python identifier)
- `description` (str, optional) - Human-readable description

**Raises:**

- `ValidationError` - Invalid parameters (empty token, invalid alias format, etc.)

**Examples:**

<!-- fragment: Demo AccountConfig examples with string to SecretStr type mismatches -->
```python
from fivetwenty import AccountConfig, Environment

# Basic configuration
import os

config = AccountConfig(
    token=os.environ["FIVETWENTY_API_TOKEN"],
    account_id=os.environ["FIVETWENTY_ACCOUNT_ID"],
    environment=Environment.PRACTICE,
    alias="my_trading_account"
)

# With description
config = AccountConfig(
    token=os.environ["FIVETWENTY_API_TOKEN"],
    account_id=os.environ["FIVETWENTY_ACCOUNT_ID"],
    environment=Environment.LIVE,
    alias="production_trading"
)
```

### Properties

#### `token: SecretStr`
Protected API token that never appears in logs or string representations.

<!-- fragment: Demo token SecretStr field usage with string environment variable -->
```python
import os
from fivetwenty import AccountConfig, Environment

config = AccountConfig(
    token=os.environ["FIVETWENTY_OANDA_TOKEN"],
    account_id=os.environ["FIVETWENTY_OANDA_ACCOUNT"],
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

<!-- fragment: Demo account_id SecretStr field usage with string environment variable -->
```python
import os
from fivetwenty import AccountConfig, Environment

config = AccountConfig(
    token=os.environ["FIVETWENTY_OANDA_TOKEN"],
    account_id=os.environ["FIVETWENTY_OANDA_ACCOUNT"],
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

<!-- fragment: Demo environment field usage with SecretStr type mismatches -->
```python
import os
from fivetwenty import AccountConfig, Environment

config = AccountConfig(
    token=os.environ["FIVETWENTY_OANDA_TOKEN"],
    account_id=os.environ["FIVETWENTY_OANDA_ACCOUNT"],
    environment=Environment.PRACTICE,
    alias="example"
)
if config.environment == Environment.LIVE:
    print("⚠️ LIVE trading - real money at risk")
else:
    print("✅ Practice trading - virtual money")
```

#### `alias: str`
User-friendly identifier for the account configuration.

<!-- fragment: Demo alias field usage with SecretStr type mismatches for token and account_id -->
```python
import os
from fivetwenty import AccountConfig, Environment

config = AccountConfig(
    alias="my_bot",
    token=os.environ["FIVETWENTY_API_TOKEN"],
    account_id=os.environ["FIVETWENTY_ACCOUNT_ID"],
    environment=Environment.PRACTICE
)
print("Bot name:", config.alias)  # Safe to log
```


### Methods

#### `summary() -> str`
Returns safe summary string suitable for logging.

**Returns:** `str` - Format: "{alias} ({environment})"

**Usage:**
<!-- fragment: Demo summary method with string literals for SecretStr fields -->
```python
from fivetwenty import AccountConfig, Environment
import logging

logger = logging.getLogger(__name__)

config = AccountConfig(
    alias="my_trader",
    environment=Environment.PRACTICE,
    token="token",
    account_id="account_id",
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

<!-- fragment: Demo secret masking with SecretStr type compatibility issues -->
```python
import os
from fivetwenty import AccountConfig, Environment

config = AccountConfig(
    token=os.environ["FIVETWENTY_OANDA_TOKEN"],
    account_id=os.environ["FIVETWENTY_OANDA_ACCOUNT"],
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

<!-- fragment: Demo validation error examples with SecretStr type mismatches -->
```python
from pydantic import ValidationError
from fivetwenty import AccountConfig, Environment

# Invalid alias (starts with number)
try:
    AccountConfig(
        alias="123invalid",  # Must be valid identifier
        token="token",
        account_id="account",
        environment=Environment.PRACTICE,
    )
except ValidationError:
    print("Alias must be valid Python identifier")

# Empty token
try:
    AccountConfig(
        token="   ",  # Whitespace-only
        account_id="account",
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
- `FIVETWENTY_OANDA_ENVIRONMENT` - "practice" or "live" (required)
- `FIVETWENTY_OANDA_ACCOUNT_ALIAS` - Account alias (required)

**Returns:** `AccountConfig | None` - Configuration object or None if required variables missing

**Usage:**
```python
# Set environment variables first
import os
from fivetwenty import AccountConfigLoader

# Load from environment (set these in your shell/deployment)
# os.environ["FIVETWENTY_OANDA_TOKEN"] = "your-actual-token"
os.environ["FIVETWENTY_OANDA_ACCOUNT"] = "your-account"
os.environ["FIVETWENTY_OANDA_ENVIRONMENT"] = "practice"
os.environ["FIVETWENTY_OANDA_ACCOUNT_ALIAS"] = "my_account"

# Load configuration
config = AccountConfigLoader.load_default()
if config:
    print("Configuration loaded:", config.summary())
else:
    print("Required environment variables not found")
```

#### `from_env_prefix(prefix: str) -> AccountConfig | None`
Load configuration using custom environment variable prefix.

**Parameters:**

- `prefix` (str) - Environment variable prefix (e.g., "TRADING_")

**Environment Variables Pattern:**

- `{prefix}OANDA_TOKEN` - API token
- `{prefix}OANDA_ACCOUNT` - Account ID
- `{prefix}OANDA_ENVIRONMENT` - Environment
- `{prefix}OANDA_ACCOUNT_ALIAS` - Account alias

**Returns:** `AccountConfig | None` - Configuration object or None if required variables missing

**Usage:**
```python
# Set custom prefixed variables
import os
from fivetwenty import AccountConfigLoader

# Load from environment (set these in your shell/deployment)
# os.environ["STRATEGY_A_OANDA_TOKEN"] = "your-actual-token"
os.environ["STRATEGY_A_OANDA_ACCOUNT"] = "account-a"
os.environ["STRATEGY_A_OANDA_ENVIRONMENT"] = "practice"
os.environ["STRATEGY_A_OANDA_ACCOUNT_ALIAS"] = "momentum_strategy"

# Load with custom prefix
config = AccountConfigLoader.from_env_prefix("STRATEGY_A_")
if config:
    print("Strategy config:", config.summary())
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
- Alias is a valid Python identifier
- Environment is valid enum value
- Description (if provided) is not empty

**Usage:**
<!-- fragment: Demo ConfigValidator with SecretStr type issues -->
```python
from fivetwenty import AccountConfig, ConfigValidator, Environment

config = AccountConfig(
    token="valid-token",
    account_id="valid-account",
    environment=Environment.PRACTICE,
    alias="valid_alias",
)

errors = ConfigValidator.validate_account_config(config)
if errors:
    print("Configuration errors:")
    for error in errors:
        print("  - Error:", str(error))
else:
    print("✅ Configuration is valid")
```

**Error Handling Example:**
<!-- fragment: Demo validation example with SecretStr type mismatches -->
```python
# Create config with potential issues
from fivetwenty import AccountConfig, Environment

# For this example, we define a simple validator
class ConfigValidator:
    @staticmethod
    def validate_account_config(config: AccountConfig) -> list[str]:
        errors = []
        if not config.account_id:
            errors.append("Account ID cannot be empty")
        if config.alias and not config.alias.isidentifier():
            errors.append("Alias must be a valid Python identifier")
        return errors

config = AccountConfig(
    token="valid-token",
    account_id="",  # Empty account ID
    environment=Environment.PRACTICE,
    alias="123invalid",  # Invalid alias
)

errors = ConfigValidator.validate_account_config(config)
# errors might contain:
# - "Account ID cannot be empty"
# - "Alias must be a valid Python identifier"

# Fix errors before using
if errors:
    error_message = f"Configuration errors: {', '.join(errors)}"
    raise ValueError(error_message)
```

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

- `value`: `"practice"`
- `base_url`: `"https://api-fxpractice.oanda.com/v3"`

#### `Environment.LIVE`
Live trading environment with real money.

**Properties:**

- `value`: `"live"`
- `base_url`: `"https://api-fxtrade.oanda.com/v3"`

### Usage

<!-- fragment: Demo environment usage examples with SecretStr type compatibility issues -->
```python
from fivetwenty import AccountConfig, Environment

# Create configurations for different environments
practice_config = AccountConfig(
    environment=Environment.PRACTICE,
    token="practice_token",
    account_id="practice_account_id",
    alias="practice",
)

live_config = AccountConfig(
    environment=Environment.LIVE,
    token="live_token",
    account_id="live_account_id",
    alias="live",
)

# Check environment in code
config = practice_config  # Use one of the configs above
if config.environment == Environment.LIVE:
    print("⚠️ Using live environment - real money at risk")

# Get base URL
print("API URL:", config.environment.base_url)
```

---

## Usage Patterns

### Basic Configuration

<!-- fragment: Demo basic configuration with SecretStr type mismatches -->
```python
import os
from fivetwenty import AccountConfig, Environment

config = AccountConfig(
    token=os.environ["FIVETWENTY_OANDA_TOKEN"],
    account_id=os.environ["FIVETWENTY_OANDA_ACCOUNT"],
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

<!-- fragment: Demo production deployment with nested if statements and RuntimeError patterns -->
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
    if config.environment == Environment.LIVE:
        if "practice" in config.token.get_secret_value().lower():
            practice_error_msg = "Practice token detected in live environment"
            raise RuntimeError(practice_error_msg)

    return config
```

---

## Security Best Practices

### 1. Never Log Secrets

<!-- fragment: Demo security best practices with SecretStr type issues -->
```python
import logging
from fivetwenty import AccountConfig, Environment

logger = logging.getLogger(__name__)
# Define config for demonstration
config = AccountConfig(
    token="demo-token",
    environment=Environment.PRACTICE
)

# ✅ Safe - uses automatic masking
logger.info("Config: %s", repr(config))
logger.info("Trading on: %s", config.summary())

# ❌ Dangerous - exposes secrets
# logger.info("Token: %s", config.token.get_secret_value())  # DON'T DO THIS - Security risk
```

### 2. Validate Before Use

<!-- fragment: Demo config validation with ValueError f-string literals -->
```python
from fivetwenty import AccountConfig, AsyncClient, ConfigValidator

def safe_client_creation(config: AccountConfig) -> AsyncClient:
    """Create client with validation."""
    errors = ConfigValidator.validate_account_config(config)
    if errors:
        raise ValueError(f"Invalid config: {', '.join(errors)}")

    return AsyncClient(config=config)
```

### 3. Environment Separation

<!-- fragment: Demo environment-specific config loading with exception handling issues -->
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
        raise ValueError(f"No {env} configuration found")

    return config
```

### 4. Runtime Verification

<!-- fragment: Demo runtime verification with exception handling patterns -->
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
        logger.error(f"Config verification failed: {e}")
        return False
```

---

## Common Patterns

### Configuration Factory

<!-- fragment: Demo configuration factory with ValueError string literals -->
```python
import os
from fivetwenty import AccountConfig, Environment

class ConfigFactory:
    """Factory for creating configurations."""

    @staticmethod
    def create_practice_config(alias: str) -> AccountConfig:
        """Create practice configuration from environment."""
        return AccountConfig(
            token=os.environ["FIVETWENTY_PRACTICE_TOKEN"],
            account_id=os.environ["FIVETWENTY_PRACTICE_ACCOUNT"],
            environment=Environment.PRACTICE,
            alias=alias,
        )

    @staticmethod
    def create_live_config(alias: str) -> AccountConfig:
        """Create live configuration with extra validation."""
        token = os.environ.get("FIVETWENTY_LIVE_TOKEN")
        if not token:
            raise ValueError("Live token not found")

        if "practice" in token.lower():
            raise ValueError("Practice token used for live config")

        return AccountConfig(
            token=token,
            account_id=os.environ["FIVETWENTY_LIVE_ACCOUNT"],
            environment=Environment.LIVE,
            alias=alias,
        )
```

### Configuration Manager

<!-- fragment: Demo configuration manager with f-string exceptions and type issues -->
```python
from typing import Any
from fivetwenty import AccountConfig, AccountConfigLoader

class ConfigManager:
    """Manage multiple configurations."""

    def __init__(self) -> None:
        self.configs: dict[str, AccountConfig] = {}
        self._load_configs()

    def _load_configs(self) -> Any:
        """Load all available configurations."""
        # Standard config
        default_config = AccountConfigLoader.load_default()
        if default_config:
            self.configs["default"] = default_config

        # Strategy-specific configs
        strategies = ["MOMENTUM", "GRID", "SCALPING"]
        for strategy in strategies:
            config = AccountConfigLoader.from_env_prefix(f"{strategy}_")
            if config:
                self.configs[strategy.lower()] = config

    def get_config(self, name: str) -> AccountConfig:
        """Get configuration by name."""
        config = self.configs.get(name)
        if not config:
            raise ValueError(f"Configuration '{name}' not found")
        return config

    def list_configs(self) -> dict[str, str]:
        """List available configurations."""
        return {name: config.summary() for name, config in self.configs.items()}
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
<!-- fragment: Demo ValidationError handling with SecretStr type mismatches -->
```python
from pydantic import ValidationError
from fivetwenty import AccountConfig, Environment

try:
    config = AccountConfig(
        token="",
        account_id="123",
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
<!-- fragment: Demo ValueError example with string literal exception -->
```python
from fivetwenty import AccountConfigLoader

config = AccountConfigLoader.load_default()
if not config:
    raise ValueError("Required environment variables not set")
```

---

## Migration Guide

### From Direct Parameters

<!-- fragment: Demo migration guide with SecretStr type compatibility issues -->
```python
import os
from fivetwenty import AccountConfig, AsyncClient, Environment

# Old way
client = AsyncClient(
    token=os.environ["FIVETWENTY_API_TOKEN"],
    account_id=os.environ["FIVETWENTY_ACCOUNT_ID"],
    environment=Environment.PRACTICE
)

# New way - Direct parameters (still supported)
client = AsyncClient(
    token=os.environ["FIVETWENTY_API_TOKEN"],
    environment=Environment.PRACTICE
)

# New way - Configuration object (recommended)
config = AccountConfig(
    token="token",
    account_id="account",
    environment=Environment.PRACTICE,
    alias="my_account"
)
client = AsyncClient(config=config)
```

### From Environment Variables

```python
import os
from fivetwenty import AccountConfigLoader, AsyncClient, Environment

# Old way
token = os.environ["FIVETWENTY_OANDA_TOKEN"]
client = AsyncClient(token=token, account_id="your-account-id", environment=Environment.PRACTICE)

# New way
config = AccountConfigLoader.load_default()  # Loads FIVETWENTY_* variables
client = AsyncClient(config=config)
```

### Adding Configuration Validation

<!-- fragment: Demo configuration validation with type ignore and f-string exceptions -->
```python
# Add validation to existing configurations
from fivetwenty import AccountConfig, ConfigValidator

# Sample config for validation
config = AccountConfig(
    token="demo-token",
    account_id="demo-account",
    environment=Environment.PRACTICE
)
errors = ConfigValidator.validate_account_config(config)
if errors:
    error_msg = f"Configuration issues: {', '.join(errors)}"
    raise ValueError(error_msg)
```