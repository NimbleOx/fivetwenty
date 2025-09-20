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

```python
class AccountConfig(BaseModel):
    """Configuration for a single OANDA trading account."""

    token: SecretStr
    account_id: SecretStr
    environment: Environment
    alias: str
```

### Constructor

```python
AccountConfig(
    token: SecretStr | str,
    account_id: SecretStr | str,
    environment: Environment,
    alias: str,
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

```python
from fivetwenty import AccountConfig, Environment

# Basic configuration
config = AccountConfig(
    token="your-api-token",
    account_id="your-account-id",
    environment=Environment.PRACTICE,
    alias="my_trading_account"
)

# With description
config = AccountConfig(
    token="your-api-token",
    account_id="your-account-id",
    environment=Environment.LIVE,
    alias="production_trading",

)
```

### Properties

#### `token: SecretStr`
Protected API token that never appears in logs or string representations.

```python
config = AccountConfig(...)
# Safe - returns SecretStr object
token_obj = config.token

# To access actual value (use with caution)
actual_token = config.token.get_secret_value()
```

#### `account_id: SecretStr`
Protected account ID that never appears in logs or string representations.

```python
config = AccountConfig(...)
# Safe - returns SecretStr object
account_obj = config.account_id

# To access actual value (use with caution)
actual_account = config.account_id.get_secret_value()
```

#### `environment: Environment`
Trading environment (practice or live).

```python
config = AccountConfig(...)
if config.environment == Environment.LIVE:
    print("⚠️ LIVE trading - real money at risk")
else:
    print("✅ Practice trading - virtual money")
```

#### `alias: str`
User-friendly identifier for the account configuration.

```python
config = AccountConfig(alias="my_bot", ...)
print(f"Bot name: {config.alias}")  # Safe to log
```


### Methods

#### `summary() -> str`
Returns safe summary string suitable for logging.

**Returns:** `str` - Format: "{alias} ({environment})"

**Usage:**
```python
config = AccountConfig(
    alias="my_trader",
    environment=Environment.PRACTICE,
    ...
)
print(config.summary())  # "my_trader (practice)"

# Safe for all logging contexts
logger.info(f"Starting trading session: {config.summary()}")
```

### Security Features

#### Automatic Secret Masking
All secret values are automatically masked in string representations:

```python
config = AccountConfig(
    token="super-secret-token",
    account_id="secret-account-123",
    alias="demo_account",
    environment=Environment.PRACTICE
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
from pydantic import ValidationError

# Invalid alias (starts with number)
try:
    AccountConfig(
        alias="123invalid",  # Must be valid identifier
        token="token",
        account_id="account",
        environment=Environment.PRACTICE
    )
except ValidationError as e:
    print("Alias must be valid Python identifier")

# Empty token
try:
    AccountConfig(
        token="   ",  # Whitespace-only
        account_id="account",
        environment=Environment.PRACTICE,
        alias="valid_alias"
    )
except ValidationError as e:
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
from fivetwenty import AccountConfigLoader

# Set environment variables first
import os
os.environ['FIVETWENTY_OANDA_TOKEN'] = 'your-token'
os.environ['FIVETWENTY_OANDA_ACCOUNT'] = 'your-account'
os.environ['FIVETWENTY_OANDA_ENVIRONMENT'] = 'practice'
os.environ['FIVETWENTY_OANDA_ACCOUNT_ALIAS'] = 'my_account'

# Load configuration
config = AccountConfigLoader.load_default()
if config:
    print(f"Loaded: {config.summary()}")
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
os.environ['STRATEGY_A_OANDA_TOKEN'] = 'token-a'
os.environ['STRATEGY_A_OANDA_ACCOUNT'] = 'account-a'
os.environ['STRATEGY_A_OANDA_ENVIRONMENT'] = 'practice'
os.environ['STRATEGY_A_OANDA_ACCOUNT_ALIAS'] = 'momentum_strategy'

# Load with custom prefix
config = AccountConfigLoader.from_env_prefix("STRATEGY_A_")
if config:
    print(f"Strategy config: {config.summary()}")
```

**Multi-Strategy Example:**
```python
# Load configurations for different strategies
momentum_config = AccountConfigLoader.from_env_prefix("MOMENTUM_")
grid_config = AccountConfigLoader.from_env_prefix("GRID_")
scalping_config = AccountConfigLoader.from_env_prefix("SCALPING_")

configs = [c for c in [momentum_config, grid_config, scalping_config] if c]
print(f"Loaded {len(configs)} strategy configurations")
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
```python
from fivetwenty import AccountConfig, ConfigValidator, Environment

config = AccountConfig(
    token="valid-token",
    account_id="valid-account",
    environment=Environment.PRACTICE,
    alias="valid_alias"
)

errors = ConfigValidator.validate_account_config(config)
if errors:
    print("Configuration errors:")
    for error in errors:
        print(f"  - {error}")
else:
    print("✅ Configuration is valid")
```

**Error Handling Example:**
```python
# Create config with potential issues
config = AccountConfig(
    token="valid-token",
    account_id="",  # Empty account ID
    environment=Environment.PRACTICE,
    alias="123invalid"  # Invalid alias
)

errors = ConfigValidator.validate_account_config(config)
# errors might contain:
# - "Account ID cannot be empty"
# - "Alias must be a valid Python identifier"

# Fix errors before using
if errors:
    raise ValueError(f"Configuration errors: {', '.join(errors)}")
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

```python
from fivetwenty import Environment

# Create configurations for different environments
practice_config = AccountConfig(
    environment=Environment.PRACTICE,
    ...
)

live_config = AccountConfig(
    environment=Environment.LIVE,
    ...
)

# Check environment in code
if config.environment == Environment.LIVE:
    print("⚠️ Using live environment - real money at risk")

# Get base URL
print(f"API URL: {config.environment.base_url}")
```

---

## Usage Patterns

### Basic Configuration

```python
from fivetwenty import AccountConfig, Environment

config = AccountConfig(
    token="your-api-token",
    account_id="your-account-id",
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
    "scalping": AccountConfigLoader.from_env_prefix("SCALPING_")
}

# Filter out None values
active_accounts = {name: config for name, config in accounts.items() if config}
print(f"Active strategies: {list(active_accounts.keys())}")
```

### Configuration Validation

```python
from fivetwenty import ConfigValidator

def create_safe_config(**kwargs) -> AccountConfig:
    """Create configuration with validation."""
    config = AccountConfig(**kwargs)

    errors = ConfigValidator.validate_account_config(config)
    if errors:
        raise ValueError(f"Invalid configuration: {', '.join(errors)}")

    return config
```

### Production Deployment

```python
import os
from fivetwenty import AccountConfigLoader, Environment

def load_production_config() -> AccountConfig:
    """Load production configuration with safety checks."""
    config = AccountConfigLoader.load_default()

    if not config:
        raise RuntimeError("No configuration found - check environment variables")

    # Ensure we're in the expected environment
    expected_env = os.environ.get("EXPECTED_OANDA_ENVIRONMENT", "practice")
    if config.environment.value != expected_env:
        raise RuntimeError(
            f"Environment mismatch: expected {expected_env}, "
            f"got {config.environment.value}"
        )

    # Extra validation for live
    if config.environment == Environment.LIVE:
        if "practice" in config.token.get_secret_value().lower():
            raise RuntimeError("Practice token detected in live environment")

    return config
```

---

## Security Best Practices

### 1. Never Log Secrets

```python
# ✅ Safe - uses automatic masking
logger.info(f"Config: {repr(config)}")
logger.info(f"Trading on: {config.summary()}")

# ❌ Dangerous - exposes secrets
logger.info(f"Token: {config.token.get_secret_value()}")  # DON'T DO THIS
```

### 2. Validate Before Use

```python
from fivetwenty import AsyncClient, Environment

from fivetwenty import ConfigValidator

def safe_client_creation(config: AccountConfig) -> AsyncClient:
    """Create client with validation."""
    errors = ConfigValidator.validate_account_config(config)
    if errors:
        raise ValueError(f"Invalid config: {', '.join(errors)}")

    return AsyncClient(config=config)
```

### 3. Environment Separation

```python
# Separate environment variables
# Practice: PRACTICE_FIVETWENTY_*
# Live: LIVE_FIVETWENTY_*

def load_env_specific_config(env: str) -> AccountConfig:
    """Load configuration for specific environment."""
    prefix = f"{env.upper()}_FIVETWENTY_"
    config = AccountConfigLoader.from_env_prefix(prefix)

    if not config:
        raise ValueError(f"No {env} configuration found")

    return config
```

### 4. Runtime Verification

```python
from fivetwenty import AsyncClient, Environment

async def verify_config_connection(config: AccountConfig) -> bool:
    """Test configuration by connecting to API."""
    try:
        async with AsyncClient(config=config) as client:
            accounts = await client.accounts.list()
            return len(accounts) > 0
    except Exception as e:
        logger.error(f"Config verification failed: {e}")
        return False
```

---

## Common Patterns

### Configuration Factory

```python
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

```python
class ConfigManager:
    """Manage multiple configurations."""

    def __init__(self):
        self.configs: dict[str, AccountConfig] = {}
        self._load_configs()

    def _load_configs(self):
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
```python
from pydantic import ValidationError

try:
    config = AccountConfig(
        token="",
        account_id="123",
        environment=Environment.PRACTICE,
        alias="123invalid"
    )
except ValidationError as e:
    # Handle validation errors
    for error in e.errors():
        print(f"Field: {error['loc']}, Error: {error['msg']}")
```

### ValueError
Raised by loader methods when required environment variables are missing.

**Example:**
```python
config = AccountConfigLoader.load_default()
if not config:
    raise ValueError("Required environment variables not set")
```

---

## Migration Guide

### From Direct Parameters

```python
from fivetwenty import AsyncClient, Environment

# Old way
client = AsyncClient(token="token", environment=Environment.PRACTICE)

# New way - Direct parameters (still supported)
client = AsyncClient(token="token", environment=Environment.PRACTICE)

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
from fivetwenty import AsyncClient, Environment

# Old way
token = os.environ["FIVETWENTY_OANDA_TOKEN"]
client = AsyncClient(token=token, environment=Environment.PRACTICE)

# New way
config = AccountConfigLoader.load_default()  # Loads FIVETWENTY_* variables
client = AsyncClient(config=config)
```

### Adding Configuration Validation

```python
# Add validation to existing configurations
from fivetwenty import ConfigValidator

errors = ConfigValidator.validate_account_config(config)
if errors:
    raise ValueError(f"Configuration issues: {', '.join(errors)}")
```