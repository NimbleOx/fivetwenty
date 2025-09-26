# Environments

OANDA provides two distinct environments for trading: **Practice** and **Live**. Understanding the differences is crucial for safe development and trading.

## Environment Overview

| Feature | Practice Environment | Live Environment |
|---------|---------------------|------------------|
| **Real Money** | No (virtual funds) | Yes (real funds) |
| **API Endpoint** | api-fxpractice.oanda.com | api-fxtrade.oanda.com |
| **Market Data** | Real-time | Real-time |
| **Execution** | Simulated | Real market |
| **Risk** | None | Real financial risk |
| **Use Case** | Testing & Learning | Production Trading |

## Using Environments

### Setting the Environment

The SDK provides an `Environment` enum for easy configuration:

```python
from fivetwenty import AsyncClient, Environment

# For testing and development

"""Comprehensive module for trading operations."""
practice_client = AsyncClient(
    token="your-practice-token",
    environment=Environment.PRACTICE
)

# For real trading (use with caution!)
live_client = AsyncClient(
    token="your-live-token",
    environment=Environment.LIVE
)
```

### Environment URLs

The environments use different base URLs:

```python
from fivetwenty import Environment

# Check environment URLs
print(Environment.PRACTICE.base_url)
# Output: https://api-fxpractice.oanda.com/v3

print(Environment.LIVE.base_url)
# Output: https://api-fxtrade.oanda.com/v3
```

## Practice Environment

### Purpose

The practice environment is perfect for:

- ✅ Learning the OANDA platform
- ✅ Testing trading strategies
- ✅ Developing and debugging code
- ✅ Paper trading competitions
- ✅ Training new traders

### Features

- **Virtual Funds**: Start with $100,000 in virtual money
- **Real Market Data**: Access to live market prices
- **Full API Access**: All API features available
- **No Risk**: No real money at stake
- **Reset Available**: Can reset account balance

### Getting a Practice Account

1. Sign up at [OANDA](https://www.oanda.com) and create a practice account
2. No credit card required
3. Instant access to API token
4. Multiple practice accounts allowed

### Example: Practice Trading

```python
import asyncio
import os

from fivetwenty import AsyncClient, Environment



"""Comprehensive module for trading operations."""
async def practice_trading() -> Any:
    """Safe trading in practice environment."""

    async with AsyncClient(
        token=os.environ["OANDA_PRACTICE_TOKEN"],
        environment=Environment.PRACTICE,  # Always practice for testing!
    ) as client:
        # Get practice account
        accounts = await client.accounts.get_accounts()
        account = accounts[0]

        print(f"Practice Account: {account.id}")
        print(f"Virtual Balance: {account.balance}")

        # Place a test trade (no real money!)
        order = await client.orders.post_market_order(
            account_id=account.id,
            instrument="EUR_USD",
            units=10000,  # Large position - it's just practice!
        )

        print("Practice trade executed!")

asyncio.run(practice_trading())
```

## Live Environment

### Purpose

The live environment is for:

- 💰 Real money trading
- 📊 Production trading systems
- 🏦 Advanced trading operations
- 📈 Actual profit and loss

### Requirements

- Funded OANDA account
- Completed KYC verification
- Understanding of trading risks
- Production-ready code

### Safety Measures

!!! danger "Real Money Warning"
    The live environment uses real money. Losses are real and permanent. Always test thoroughly in practice before going live.

### Example: Safe Live Trading

```python
import os

from fivetwenty import AsyncClient, Environment
from fivetwenty.exceptions import FiveTwentyError



"""Comprehensive module for trading operations."""
async def live_trading_with_safeguards() -> Any:
    """Production trading with safety checks."""

    # Multiple confirmation checks
    if not confirm_live_trading():
        print("Live trading cancelled")
        return

    async with AsyncClient(
        token=os.environ["FIVETWENTY_LIVE_TOKEN"],
        environment=Environment.LIVE,  # ⚠️ REAL MONEY
    ) as client:
        try:
            # Get account info
            accounts = await client.accounts.get_accounts()
            account = accounts[0]

            # Safety check: Verify sufficient margin
            if float(account.margin_available) < 1000:
                print("❌ Insufficient margin for safe trading")
                return

            # Safety check: Position size limits
            max_units = min(1000, float(account.margin_available) * 0.01)

            # Place conservative trade with stop loss
            order = await client.orders.post_market_order(
                account_id=account.id,
                instrument="EUR_USD",
                units=int(max_units),
                stop_loss_on_fill={
                    "price": "1.0850",  # Always use stop loss!
                    "time_in_force": "GTC",
                },
            )

            print(f"Live trade executed: {order.order_fill_transaction.id}")

        except FiveTwentyError as e:
            print(f"Trading error: {e}")
            # Log error for monitoring
            log_error(e)

def confirm_live_trading() -> Any:
    """Require explicit confirmation for live trading."""
    response = input("⚠️  LIVE TRADING - Real money at risk. Continue? (yes/no): ")
    return response.lower() == "yes"

def log_error(error: Any) -> Any:
    """Log errors for monitoring."""
    import logging
    logging.error(f"Live trading error: {error}")
```

## Environment-Specific Configuration

### Development Setup

Use environment variables to manage different configurations:

```bash
# .env.practice
FIVETWENTY_OANDA_ENVIRONMENT=practice
FIVETWENTY_OANDA_TOKEN=your-practice-token
FIVETWENTY_OANDA_ACCOUNT=101-001-1234567-001

# .env.live
FIVETWENTY_OANDA_ENVIRONMENT=live
FIVETWENTY_OANDA_TOKEN=your-live-token
FIVETWENTY_OANDA_ACCOUNT=001-001-1234567-001
```

### Dynamic Environment Selection

```python
import os

from fivetwenty import AsyncClient, Environment


def create_client():
    """Create client based on environment variable."""
    env = os.environ.get("FIVETWENTY_OANDA_ENVIRONMENT", "practice").lower()

    if env == "live":
        print("⚠️  WARNING: Using LIVE environment")
        return AsyncClient(
            token=os.environ["FIVETWENTY_LIVE_TOKEN"],
            environment=Environment.LIVE,
        )
    else:
        print("✅ Using PRACTICE environment")
        return AsyncClient(
            token=os.environ["OANDA_PRACTICE_TOKEN"],
            environment=Environment.PRACTICE,
        )

# Automatically selects based on FIVETWENTY_OANDA_ENVIRONMENT
client = create_client()
```

## Testing Strategy

### Recommended Workflow

from fivetwenty import Environment


"""Comprehensive module for trading operations."""
1. **Develop in Practice** - Write and debug all code
2. **Test in Practice** - Run comprehensive tests
3. **Paper Trade** - Run strategy for weeks/months
4. **Small Live Test** - Start with minimal position sizes
5. **Scale Up** - Gradually increase position sizes

### Environment-Specific Tests
```python
import os

import pytest

from fivetwenty import AsyncClient, Environment


@pytest.mark.parametrize("environment", [Environment.PRACTICE])
async def test_practice_only(environment):
    """Tests that should only run in practice."""
    client = AsyncClient(
        token=test_token,
        environment=environment,
    )
    # Test risky operations

@pytest.mark.skipif(
    os.environ.get("FIVETWENTY_OANDA_ENVIRONMENT") != "live",
    reason="Live environment tests disabled",
)
async def test_live_systems():
    """Tests for live trading systems."""
    # Only runs when explicitly enabled
    pass
```

## Monitoring and Alerts

### Environment-Aware Monitoring

```python
from fivetwenty import Environment


class TradingMonitor:
    def __init__(self, environment: Environment):
        self.environment = environment
        self.alert_threshold = 100 if environment == Environment.PRACTICE else 10

    def check_position_size(self, units: int):
        """Different thresholds for different environments."""
        if units > self.alert_threshold:
            if self.environment == Environment.LIVE:
                self.send_alert(f"⚠️ Large LIVE position: {units}")
            else:
                print(f"Practice position: {units}")

    def send_alert(self, message: str):
        """Send alerts for live trading only."""
        # Send email, SMS, or Slack notification
        pass
```

## Best Practices

### 1. Always Start with Practice

Never test new code directly in live:

```python
from fivetwenty import Environment


def validate_strategy(strategy):
    """Always validate in practice first."""
    # Run in practice for minimum period
    practice_results = run_backtest(strategy, Environment.PRACTICE)

    if practice_results.sharpe_ratio < 1.0:
        raise ValueError("Strategy not profitable in practice")

    return practice_results
```

### 2. Use Feature Flags

Control features per environment:

```python
from fivetwenty import Environment


class FeatureFlags:
    def __init__(self, environment: Environment):
        self.is_live = environment == Environment.LIVE

        # Disable risky features in live
        self.allow_martingale = not self.is_live
        self.max_position_size = 1000 if not self.is_live else 100
        self.enable_experimental = not self.is_live
```

### 3. Separate Credentials

FiveTwenty's configuration system makes credential separation straightforward and secure:

```python
# config.py - Secure credential management
import os

from fivetwenty import AccountConfig, AccountConfigLoader, Environment


class SecureCredentialManager:
    """Manage separate credentials for different environments."""

    @staticmethod
    def get_practice_config() -> AccountConfig:
        """Get practice environment configuration."""
        return AccountConfig(
            token=os.environ["FIVETWENTY_PRACTICE_TOKEN"],
            account_id=os.environ["FIVETWENTY_PRACTICE_ACCOUNT"],
            environment=Environment.PRACTICE,
            alias="safe_practice",

        )

    @staticmethod
    def get_live_config() -> AccountConfig:
        """Get live environment configuration with extra validation."""
        # Extra validation for live credentials
        token = os.environ.get("FIVETWENTY_LIVE_TOKEN")
        account_id = os.environ.get("FIVETWENTY_LIVE_ACCOUNT")

        if not token or not account_id:
            raise ValueError("Live credentials not found - check environment variables")

        # Ensure we're not accidentally using practice tokens in live
        if "practice" in token.lower() or "demo" in token.lower():
            raise ValueError("Practice token detected for live environment!")

        return AccountConfig(
            token=token,
            account_id=account_id,
            environment=Environment.LIVE,
            alias="production_live",

        )

    @staticmethod
    def get_config_for_environment(env: str) -> AccountConfig:
        """Get configuration for specified environment with safety checks."""
        if env.lower() == "live":
            print("🚨 Loading LIVE credentials - real money at risk")
            return SecureCredentialManager.get_live_config()
        else:
            print("✅ Loading PRACTICE credentials - safe virtual money")
            return SecureCredentialManager.get_practice_config()

# Alternative: Using environment variable prefixes
class MultiEnvironmentConfig:
    """Manage multiple environment configurations."""

    ENVIRONMENT_PREFIXES = {
        "practice": "PRACTICE_FIVETWENTY_",
        "staging": "STAGING_FIVETWENTY_",
        "live": "LIVE_FIVETWENTY_"
    }

    @classmethod
    def load_config(cls, env_name: str) -> AccountConfig:
        """Load configuration for specific environment."""
        prefix = cls.ENVIRONMENT_PREFIXES.get(env_name.lower())
        if not prefix:
            raise ValueError(f"Unknown environment: {env_name}")

        config = AccountConfigLoader.from_env_prefix(prefix)
        if not config:
            raise ValueError(f"No configuration found for {env_name} (prefix: {prefix})")

        # Validate environment matches expectation
        expected_env = Environment.LIVE if env_name.lower() == "live" else Environment.PRACTICE
        if config.environment != expected_env:
            raise ValueError(f"Environment mismatch: expected {expected_env}, got {config.environment}")

        return config
```

## Migration Checklist

from fivetwenty import Environment


"""Comprehensive module for trading operations."""
Before moving from Practice to Live:

- [ ] ✅ Strategy profitable for 3+ months in practice
- [ ] ✅ All error handling tested
- [ ] ✅ Stop losses on every trade
- [ ] ✅ Position sizing calculated correctly
- [ ] ✅ Monitoring and alerts configured
- [ ] ✅ Backup plans for system failures
- [ ] ✅ Understanding of all risks
- [ ] ✅ Capital you can afford to lose

## Troubleshooting

### Wrong Environment Errors

If you get unexpected behavior:
```python

# Always log the environment
print(f"Environment: {client._environment}")
print(f"Base URL: {client._environment.base_url}")
```

### Token Mismatch

Practice and live tokens are different:

```python
from fivetwenty import Environment


def validate_token_environment(token: str, environment: Environment):
    """Ensure token matches environment."""
    # Practice tokens often start with different prefixes
    if environment == Environment.LIVE and "practice" in token.lower():
        raise ValueError("Practice token used for live environment!")
```

## Next Steps

Now that you understand environments:

- Practice extensively in the [practice environment](first-trade.md)
- Learn about [error handling](../../explanation/error-handling.md) for production
- Understand [async vs sync](../../explanation/async-vs-sync.md) patterns
- Review [best practices](../../explanation/best-practices.md) before going live

Remember: **Always practice extensively before risking real money!**