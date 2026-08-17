# Multi-Account Configuration

FiveTwenty supports connecting to multiple OANDA accounts simultaneously through custom environment variable prefixes and configuration objects. This guide shows you how to set up and manage multiple accounts in your applications.

## Overview

You can connect to multiple accounts using three different approaches:

1. **Custom Environment Variable Prefixes** - Use different prefixes for different accounts
2. **Direct Configuration Objects** - Create configurations programmatically
3. **Mixed Approach** - Combine environment variables with direct configuration

## Method 1: Custom Environment Variable Prefixes

Set up different prefixes for each account in your environment:

```bash
# Account 1 - Practice environment
export TRADING_BOT_FIVETWENTY_OANDA_TOKEN="practice-token-1"
export TRADING_BOT_FIVETWENTY_OANDA_ACCOUNT="account-id-1"
export TRADING_BOT_FIVETWENTY_OANDA_ENVIRONMENT="practice"

# Account 2 - Live environment
export LIVE_ACCOUNT_FIVETWENTY_OANDA_TOKEN="live-token-2"
export LIVE_ACCOUNT_FIVETWENTY_OANDA_ACCOUNT="account-id-2"
export LIVE_ACCOUNT_FIVETWENTY_OANDA_ENVIRONMENT="live"

# Default account (uses FIVETWENTY_ prefix)
export FIVETWENTY_OANDA_TOKEN="default-token"
export FIVETWENTY_OANDA_ACCOUNT="default-account"
export FIVETWENTY_OANDA_ENVIRONMENT="practice"
```

### Initialize Clients with Custom Prefixes

<!-- fragment: partial multi-account configuration example -->
```python
import asyncio
from typing import Any
from fivetwenty import AsyncClient
from fivetwenty.configuration import AccountConfigLoader


async def multi_account_example() -> None:
    """Demonstrate multi-account configuration with comprehensive validation and secure setup."""

    print(f"Starting Multi-Account Configuration Example")
    print(f"List Loading configurations with custom environment variable prefixes...")

    # Step 1: Load configurations with custom prefixes for different account purposes
    # Each prefix allows for separate environment variables and isolated configurations
    print(f"\nConfig Step 1: Loading account configurations...")
    trading_bot_config = AccountConfigLoader.from_env_prefix("TRADING_BOT_")
    live_account_config = AccountConfigLoader.from_env_prefix("LIVE_ACCOUNT_")
    default_config = AccountConfigLoader.load_default()  # Uses standard FIVETWENTY_ prefix

    # Step 2: Comprehensive configuration validation with detailed feedback
    print(f"\nSuccess Step 2: Validating loaded configurations...")
    config_status = {
        "Trading Bot (TRADING_BOT_)": trading_bot_config,
        "Live Account (LIVE_ACCOUNT_)": live_account_config,
        "Default Account (FIVETWENTY_)": default_config
    }

    # Validate each configuration and provide detailed feedback
    for name, config in config_status.items():
        if config is None:
            print(f"   Error {name}: Configuration not found or incomplete")
            prefix = name.split("(")[1].rstrip(")")
            print(f"      Note Required environment variables:")
            print(f"         • {prefix}_FIVETWENTY_OANDA_TOKEN")
            print(f"         • {prefix}_FIVETWENTY_OANDA_ACCOUNT")
            print(f"         • {prefix}_FIVETWENTY_OANDA_ENVIRONMENT")
            raise ValueError(f"{name} environment variables not found or incomplete")
        else:
            print(f"   Success {name}: Configuration loaded successfully")
            print(f"      World Environment: {config.environment.value}")
            print(f"      Tag  Alias: {config.alias}")

    # Step 3: Initialize clients with proper error handling and context management
    print(f"\nLink Step 3: Initializing clients for multi-account operations...")
    try:
        # Nested async context managers ensure proper resource cleanup
        async with AsyncClient(config=trading_bot_config) as trading_bot:
            async with AsyncClient(config=live_account_config) as live_client:
                async with AsyncClient(config=default_config) as default_client:

                    print(f"\nData Active Client Summary:")
                    print(f"   🤖 Trading Bot: {trading_bot.config.summary()}")
                    print(f"   Balance Live Account: {live_client.config.summary()}")
                    print(f"   Target Default Account: {default_client.config.summary()}")

                    # Step 4: Validate each client connection with account verification
                    print(f"\nSearch Step 4: Validating client connections...")

                    # Trading bot account validation
                    print(f"   🤖 Testing Trading Bot connection...")
                    trading_account = await trading_bot.accounts.get_account(trading_bot.account_id)
                    print(f"      Success Connected: {trading_account.balance} {trading_account.currency}")
                    print(f"      Analysis Margin available: {trading_account.margin_available}")

                    # Live account validation (extra caution for live environment)
                    print(f"   Balance Testing Live Account connection...")
                    if live_client.environment.value == "live":
                        print(f"      ⚠️  LIVE ENVIRONMENT - Real money at risk")
                    live_account = await live_client.accounts.get_account(live_client.account_id)
                    print(f"      Success Connected: {live_account.balance} {live_account.currency}")
                    print(f"      Data Open positions: {live_account.open_position_count}")

                    # Default account validation
                    print(f"   Target Testing Default Account connection...")
                    default_account = await default_client.accounts.get_account(default_client.account_id)
                    print(f"      Success Connected: {default_account.balance} {default_account.currency}")
                    print(f"      List Open orders: {default_account.open_order_count}")

                    # Step 5: Demonstrate account-specific operations
                    print(f"\nTarget Step 5: Account-specific operations completed")
                    print(f"   Success All accounts validated and ready for trading operations")
                    print(f"   Note Each client can now be used for different strategies:")
                    print(f"      • Trading Bot: Automated trading algorithms")
                    print(f"      • Live Account: Real money trading operations")
                    print(f"      • Default Account: General trading activities")

    except Exception as e:
        print(f"Error Multi-account setup failed: {type(e).__name__}: {e}")
        print(f"Note Check all environment variables are set correctly")
        raise

    print(f"\nFlag Multi-account configuration example completed successfully")
```

### Single Account with Custom Prefix

<!-- fragment: partial single account setup example -->
```python
import asyncio
from typing import Any
from fivetwenty import AsyncClient
from fivetwenty.configuration import AccountConfigLoader


async def single_custom_account() -> None:
    """Demonstrate single account setup with custom environment variable prefix and comprehensive validation."""

    print(f"Lightning Single Custom Account Configuration")
    print(f"Target Target: MOMENTUM_ environment variable prefix")

    # Step 1: Load configuration from MOMENTUM_FIVETWENTY_OANDA_* variables
    print(f"\nList Step 1: Loading MOMENTUM account configuration...")
    print(f"   Search Searching for environment variables:")
    print(f"      • MOMENTUM_FIVETWENTY_OANDA_TOKEN")
    print(f"      • MOMENTUM_FIVETWENTY_OANDA_ACCOUNT")
    print(f"      • MOMENTUM_FIVETWENTY_OANDA_ENVIRONMENT")

    momentum_config = AccountConfigLoader.from_env_prefix("MOMENTUM_")

    # Step 2: Validate configuration loading with detailed error reporting
    if momentum_config is None:
        print(f"Error MOMENTUM configuration not found")
        print(f"Note Setup instructions:")
        print(f"   export MOMENTUM_FIVETWENTY_OANDA_TOKEN='your-momentum-token'")
        print(f"   export MOMENTUM_FIVETWENTY_OANDA_ACCOUNT='your-momentum-account-id'")
        print(f"   export MOMENTUM_FIVETWENTY_OANDA_ENVIRONMENT='practice'  # or 'live'")
        raise ValueError("MOMENTUM_ environment variables not found or incomplete")

    print(f"Success MOMENTUM configuration loaded successfully")
    print(f"   World Environment: {momentum_config.environment.value}")
    print(f"   Tag  Alias: {momentum_config.alias}")
    print(f"   Config Configuration: {momentum_config.summary()}")

    # Step 3: Initialize client with comprehensive connection validation
    print(f"\nLink Step 2: Initializing MOMENTUM client...")
    try:
        async with AsyncClient(config=momentum_config) as client:
            print(f"Success Client initialized: {client.config.summary()}")

            # Step 4: Validate connection with account details retrieval
            print(f"\nSearch Step 3: Validating account connection...")
            account = await client.accounts.get_account(client.account_id)

            print(f"Success Account connection validated")
            print(f"Data Account Details:")
            print(f"   Balance Balance: {account.balance} {account.currency}")
            print(f"   Analysis Margin Available: {account.margin_available} {account.currency}")
            print(f"   Data Margin Rate: {account.margin_rate}")
            print(f"   Numbers Open Positions: {account.open_position_count}")
            print(f"   List Open Orders: {account.open_order_count}")
            print(f"   Notes Account ID: {account.id}")

            # Step 5: Environment-specific guidance
            if client.environment.value == "live":
                print(f"\n⚠️  LIVE ENVIRONMENT DETECTED:")
                print(f"   ⚠️ Real money at risk - ensure proper risk management")
                print(f"   Note Verify all trading strategies before deployment")
            else:
                print(f"\nSuccess Practice environment - safe for development and testing")
                print(f"   Note Perfect for testing momentum trading strategies")

            # Step 6: Usage guidance for momentum trading
            print(f"\nTarget MOMENTUM Trading Configuration Ready:")
            print(f"   Success Client configured for momentum-based strategies")
            print(f"   Note Suitable for:")
            print(f"      • Trend-following algorithms")
            print(f"      • Breakout trading systems")
            print(f"      • Moving average strategies")
            print(f"      • Price momentum indicators")

    except Exception as e:
        print(f"Error MOMENTUM client initialization failed: {type(e).__name__}")
        print(f"Search Error details: {e}")
        print(f"Note Troubleshooting steps:")
        print(f"   1. Verify all MOMENTUM_ environment variables are set")
        print(f"   2. Check token validity in OANDA dashboard")
        print(f"   3. Ensure account ID matches your OANDA account")
        print(f"   4. Confirm network connectivity")
        raise

    print(f"\nFlag Single custom account setup completed successfully")
```

### Synchronous Client Example

<!-- fragment: Demo sync client configuration -->
```python
from typing import Any
from fivetwenty import Client
from fivetwenty.configuration import AccountConfigLoader


def sync_example() -> None:
    """Demonstrate synchronous client configuration with comprehensive setup and validation."""

    print(f"Processing Synchronous Client Configuration Example")
    print(f"Lightning Using blocking/synchronous API for simplified integration")

    # Step 1: Load configuration for synchronous client operations
    print(f"\nList Step 1: Loading MOMENTUM configuration for sync client...")
    print(f"   Search Target environment variables: MOMENTUM_FIVETWENTY_OANDA_*")

    momentum_config = AccountConfigLoader.from_env_prefix("MOMENTUM_")

    # Step 2: Validate configuration with detailed error handling
    if momentum_config is None:
        print(f"Error Configuration loading failed")
        print(f"Note Required environment variables:")
        print(f"   • MOMENTUM_FIVETWENTY_OANDA_TOKEN")
        print(f"   • MOMENTUM_FIVETWENTY_OANDA_ACCOUNT")
        print(f"   • MOMENTUM_FIVETWENTY_OANDA_ENVIRONMENT")
        print(f"\nConfig Setup example:")
        print(f"   export MOMENTUM_FIVETWENTY_OANDA_TOKEN='your-token'")
        print(f"   export MOMENTUM_FIVETWENTY_OANDA_ACCOUNT='123-456-789'")
        print(f"   export MOMENTUM_FIVETWENTY_OANDA_ENVIRONMENT='practice'")
        raise ValueError("MOMENTUM_ environment variables not found")

    print(f"Success Configuration loaded successfully")
    print(f"   World Environment: {momentum_config.environment.value}")
    print(f"   Tag  Alias: {momentum_config.alias}")

    # Step 3: Initialize synchronous client with proper resource management
    print(f"\nLink Step 2: Initializing synchronous client...")
    print(f"   Info  Synchronous client uses background thread for async operations")
    print(f"   Lightning Provides blocking API for easier integration")

    try:
        with Client(config=momentum_config) as client:
            print(f"Success Synchronous client initialized")
            print(f"   Config Configuration: {client.config.summary()}")
            print(f"   🧵 Background thread: Active")

            # Step 4: Test synchronous account operations
            print(f"\nSearch Step 3: Testing synchronous operations...")
            account = client.accounts.get_account(client.account_id)

            print(f"Success Account data retrieved successfully")
            print(f"Data Account Information:")
            print(f"   Balance Balance: {account.balance} {account.currency}")
            print(f"   Analysis Margin Available: {account.margin_available}")
            print(f"   Numbers Open Positions: {account.open_position_count}")
            print(f"   List Open Orders: {account.open_order_count}")

            # Step 5: Demonstrate additional synchronous operations
            print(f"\nLightning Additional synchronous operations:")
            print(f"   Success Account validation: Complete")
            print(f"   Success Connection status: Healthy")
            print(f"   Success API responsiveness: Normal")

            # Step 6: Usage guidance for synchronous operations
            print(f"\nNote Synchronous Client Benefits:")
            print(f"   • Simpler code structure (no async/await)")
            print(f"   • Easy integration with existing sync codebases")
            print(f"   • Automatic thread management")
            print(f"   • Compatible with standard Python patterns")

            print(f"\n⚠️  Synchronous Client Considerations:")
            print(f"   • May block execution thread during API calls")
            print(f"   • Less efficient for high-frequency operations")
            print(f"   • Consider AsyncClient for performance-critical applications")

    except Exception as e:
        print(f"Error Synchronous client error: {type(e).__name__}")
        print(f"Search Error details: {e}")
        print(f"Note Troubleshooting:")
        print(f"   1. Verify environment variables are correct")
        print(f"   2. Check network connectivity")
        print(f"   3. Validate OANDA account credentials")
        raise

    print(f"\nFlag Synchronous client example completed")
```

## Method 2: Direct Configuration Objects

Create configurations programmatically without environment variables:

<!-- fragment: partial direct configuration example -->
```python
import asyncio
from typing import List, Any
from pydantic import SecretStr

from fivetwenty import AsyncClient, Environment
from fivetwenty.configuration import AccountConfig


async def direct_config_example() -> None:
    """Demonstrate direct configuration creation without environment variables for maximum control."""

    print(f"Config Direct Configuration Example")
    print(f"Note Creating configurations programmatically without environment variables")

    # Step 1: Define multiple account configurations with different purposes
    print(f"\nList Step 1: Creating account configurations...")

    configs = [
        # Practice account for strategy development and testing
        AccountConfig(
            token=SecretStr("practice-token-1"),      # Replace with actual practice token
            account_id=SecretStr("practice-account-1"), # Replace with actual practice account ID
            environment=Environment.PRACTICE,           # Safe testing environment
            alias="strategy_a",                        # Descriptive alias for identification
        ),
        # Live account for real trading operations
        AccountConfig(
            token=SecretStr("live-token-1"),          # Replace with actual live token
            account_id=SecretStr("live-account-1"),     # Replace with actual live account ID
            environment=Environment.LIVE,               # Real money environment
            alias="live_trading",                      # Descriptive alias for identification
        ),
    ]

    # Step 2: Display configuration summary with security considerations
    print(f"Success Configurations created:")
    for i, config in enumerate(configs, 1):
        print(f"   {i}. {config.alias}:")
        print(f"      World Environment: {config.environment.value}")
        print(f"      Lock Token: {str(config.token)[:12]}... (masked for security)")
        print(f"      Tag  Alias: {config.alias}")

        if config.environment == Environment.LIVE:
            print(f"      ⚠️  LIVE environment - real money at risk")
        else:
            print(f"      Success Practice environment - safe for testing")

    # Step 3: Initialize clients with proper error handling
    print(f"\nLink Step 2: Initializing clients from direct configurations...")
    clients: List[AsyncClient] = []

    try:
        # Create client instances from configurations
        for config in configs:
            client = AsyncClient(config=config)
            clients.append(client)
            print(f"   Success Client created for {config.alias}")

        # Step 4: Use context managers to ensure proper resource cleanup
        print(f"\nLightning Step 3: Activating clients with proper resource management...")

        # Nested context managers ensure all resources are properly cleaned up
        async with clients[0] as strategy_a:
            async with clients[1] as live_trading:
                print(f"Success Both clients activated successfully")

                # Step 5: Validate each client connection
                print(f"\nSearch Step 4: Validating client connections...")

                # Strategy A (Practice) validation
                print(f"   Test Testing Strategy A (Practice) connection...")
                strategy_account = await strategy_a.accounts.get_account(strategy_a.account_id)
                print(f"      Success Connected: {strategy_account.balance} {strategy_account.currency}")
                print(f"      Data Margin: {strategy_account.margin_available}")
                print(f"      Target Environment: {strategy_a.environment.value}")

                # Live Trading validation (with extra caution)
                print(f"   Balance Testing Live Trading connection...")
                print(f"      ⚠️  LIVE ENVIRONMENT - Proceeding with caution")
                live_account = await live_trading.accounts.get_account(live_trading.account_id)
                print(f"      Success Connected: {live_account.balance} {live_account.currency}")
                print(f"      Data Positions: {live_account.open_position_count}")
                print(f"      List Orders: {live_account.open_order_count}")
                print(f"      ⚠️ Environment: {live_trading.environment.value} (REAL MONEY)")

                # Step 6: Demonstrate account-specific operations
                print(f"\nTarget Step 5: Executing account-specific operations...")

                # Strategy operations (safe testing)
                print(f"   Test Strategy A Operations:")
                print(f"      • Algorithm development and testing")
                print(f"      • Risk-free strategy validation")
                print(f"      • Performance backtesting")
                print(f"      • Parameter optimization")

                # Live operations (real money - extra caution)
                print(f"   Balance Live Trading Operations:")
                print(f"      • Real money position management")
                print(f"      • Risk-controlled order execution")
                print(f"      • Portfolio monitoring")
                print(f"      • Profit/loss realization")

                # Step 7: Configuration benefits summary
                print(f"\nNote Direct Configuration Benefits:")
                print(f"   Success No dependency on environment variables")
                print(f"   Success Programmatic configuration management")
                print(f"   Success Runtime configuration flexibility")
                print(f"   Success Easy integration with external config systems")
                print(f"   Success Precise control over each account setup")

    except Exception as e:
        print(f"Error Direct configuration failed: {type(e).__name__}")
        print(f"Search Error details: {e}")
        print(f"Note Troubleshooting:")
        print(f"   1. Verify all tokens and account IDs are correct")
        print(f"   2. Check token permissions in OANDA dashboard")
        print(f"   3. Ensure account IDs match OANDA accounts exactly")
        print(f"   4. Validate network connectivity")
        raise
    finally:
        # Cleanup any remaining resources
        print(f"\n🧹 Cleaning up resources...")
        for client in clients:
            try:
                if hasattr(client, '_session') and client._session:
                    print(f"   Processing Cleaning up client resources")
            except:
                pass

    print(f"\nFlag Direct configuration example completed successfully")
```

## Method 3: Mixed Approach

Combine environment variables with direct configuration:

<!-- fragment: partial mixed approach configuration example -->
```python
import asyncio
from typing import Dict, Any, Optional
from pydantic import SecretStr

from fivetwenty import AsyncClient, Environment
from fivetwenty.configuration import AccountConfig, AccountConfigLoader


async def mixed_approach() -> None:
    """Demonstrate mixed configuration approach combining environment variables and direct configuration."""

    print(f"Processing Mixed Configuration Approach Example")
    print(f"Note Combining environment variables, custom prefixes, and direct configuration")

    # Step 1: Load primary account from default environment variables
    print(f"\nList Step 1: Loading configurations from multiple sources...")

    print(f"   Search Loading primary config from default FIVETWENTY_ variables...")
    primary_config = AccountConfigLoader.load_default()

    print(f"   Search Loading secondary config from SECONDARY_ prefix...")
    secondary_config = AccountConfigLoader.from_env_prefix("SECONDARY_")

    print(f"   Config Creating test config with direct parameters...")
    test_config = AccountConfig(
        token=SecretStr("test-token"),           # Replace with actual test token
        account_id=SecretStr("test-account"),     # Replace with actual test account
        environment=Environment.PRACTICE,        # Safe testing environment
        alias="testing",                        # Descriptive alias
    )

    # Step 2: Validate all configurations with detailed feedback
    print(f"\nSuccess Step 2: Validating mixed configurations...")

    config_sources: Dict[str, Optional[Any]] = {
        "Primary (FIVETWENTY_)": primary_config,
        "Secondary (SECONDARY_)": secondary_config,
        "Test (Direct)": test_config
    }

    valid_configs = {}

    for name, config in config_sources.items():
        if config is None:
            print(f"   ⚠️  {name}: Configuration not found")
            if "FIVETWENTY_" in name:
                print(f"      Note Set FIVETWENTY_OANDA_* environment variables")
            elif "SECONDARY_" in name:
                print(f"      Note Set SECONDARY_FIVETWENTY_OANDA_* environment variables")
            print(f"      Processing Skipping this configuration")
        else:
            print(f"   Success {name}: Configuration loaded")
            print(f"      World Environment: {config.environment.value}")
            print(f"      Tag  Alias: {config.alias}")
            valid_configs[name] = config

    if len(valid_configs) == 0:
        print(f"Error No valid configurations found")
        print(f"Note Setup at least one configuration source:")
        print(f"   1. FIVETWENTY_OANDA_* environment variables")
        print(f"   2. SECONDARY_FIVETWENTY_OANDA_* environment variables")
        print(f"   3. Direct configuration will be created automatically")
        raise ValueError("No valid configurations available")

    print(f"\nData Configuration Summary:")
    print(f"   Success Valid configurations: {len(valid_configs)}")
    print(f"   Config Mixed approach successfully demonstrated")

    # Step 3: Initialize clients based on available configurations
    print(f"\nLink Step 3: Initializing clients from mixed sources...")

    active_clients = []

    try:
        # Handle multiple configurations with flexible context management
        if "Primary (FIVETWENTY_)" in valid_configs:
            print(f"   Target Initializing primary client...")
            primary = AsyncClient(config=valid_configs["Primary (FIVETWENTY_)"])
            active_clients.append(("primary", primary))

        if "Secondary (SECONDARY_)" in valid_configs:
            print(f"   Analysis Initializing secondary client...")
            secondary = AsyncClient(config=valid_configs["Secondary (SECONDARY_)"])
            active_clients.append(("secondary", secondary))

        if "Test (Direct)" in valid_configs:
            print(f"   Test Initializing test client...")
            test_client = AsyncClient(config=valid_configs["Test (Direct)"])
            active_clients.append(("test", test_client))

        # Step 4: Activate all available clients
        print(f"\nLightning Step 4: Activating {len(active_clients)} clients...")

        # Dynamic context management for available clients
        if len(active_clients) == 3:
            # All three clients available
            async with active_clients[0][1] as primary:
                async with active_clients[1][1] as secondary:
                    async with active_clients[2][1] as test_client:
                        await _execute_mixed_operations(primary, secondary, test_client)

        elif len(active_clients) == 2:
            # Two clients available
            async with active_clients[0][1] as client1:
                async with active_clients[1][1] as client2:
                    await _execute_mixed_operations(client1, client2)

        elif len(active_clients) == 1:
            # Single client available
            async with active_clients[0][1] as client:
                await _execute_mixed_operations(client)

        print(f"\nFlag Mixed approach example completed successfully")

    except Exception as e:
        print(f"Error Mixed approach failed: {type(e).__name__}")
        print(f"Search Error details: {e}")
        print(f"Note Check all valid configurations and network connectivity")
        raise


async def _execute_mixed_operations(*clients: AsyncClient) -> None:
    """Execute operations on available clients from mixed configuration sources."""

    print(f"\nTarget Step 5: Executing operations on {len(clients)} active clients...")

    for i, client in enumerate(clients, 1):
        try:
            print(f"\n   Search Client {i}: {client.config.alias}")
            account = await client.accounts.get_account(client.account_id)

            print(f"      Success Connection validated")
            print(f"      Balance Balance: {account.balance} {account.currency}")
            print(f"      World Environment: {client.environment.value}")
            print(f"      Data Positions: {account.open_position_count}")
            print(f"      List Orders: {account.open_order_count}")

            # Environment-specific guidance
            if client.environment.value == "live":
                print(f"      ⚠️  LIVE environment - real money operations")
            else:
                print(f"      Success Practice environment - safe for testing")

        except Exception as client_error:
            print(f"      Error Client {i} error: {client_error}")

    # Step 6: Demonstrate mixed approach benefits
    print(f"\nNote Mixed Approach Benefits Demonstrated:")
    print(f"   Success Flexibility: Environment variables + direct config")
    print(f"   Success Scalability: Multiple configuration sources")
    print(f"   Success Reliability: Fallback configuration options")
    print(f"   Success Security: Environment variables for sensitive data")
    print(f"   Success Control: Direct configuration for specific needs")
    print(f"   Success Maintainability: Clear separation of concerns")
```

## Environment Variable Pattern

The pattern for custom prefixes follows: `{PREFIX}_FIVETWENTY_OANDA_{VARIABLE}`

### Examples:
- **Default**: `FIVETWENTY_OANDA_TOKEN`, `FIVETWENTY_OANDA_ACCOUNT`, etc.
- **Custom**: `MYBOT_FIVETWENTY_OANDA_TOKEN`, `MYBOT_FIVETWENTY_OANDA_ACCOUNT`, etc.

### Required Variables for Each Prefix:

| Variable | Description | Example |
|----------|-------------|---------|
| `{PREFIX}_FIVETWENTY_OANDA_TOKEN` | Your OANDA API token | `MYBOT_FIVETWENTY_OANDA_TOKEN="abc123..."` |
| `{PREFIX}_FIVETWENTY_OANDA_ACCOUNT` | Your OANDA account ID | `MYBOT_FIVETWENTY_OANDA_ACCOUNT="123-456-789"` |
| `{PREFIX}_FIVETWENTY_OANDA_ENVIRONMENT` | Environment: "practice" or "live" | `MYBOT_FIVETWENTY_OANDA_ENVIRONMENT="practice"` |

**Note:** The account alias is automatically generated from your prefix (e.g., `MYBOT_` becomes alias `"mybot"`).

## Best Practices

### Security
- Keep tokens secure using environment variables or secure vaults
- Never hardcode credentials in source code
- Use practice environment for development and testing
- Validate environment before connecting to live accounts

### Organization
- Use descriptive prefixes that match your application structure
- Group related accounts with consistent naming patterns
- Document which accounts are used for which purposes

### Error Handling

Always validate that configurations were loaded successfully:
<!-- fragment: Demo safe configuration loading with ValueError patterns -->
```python
import asyncio
from typing import Any, Optional
from fivetwenty import AsyncClient
from fivetwenty.configuration import AccountConfigLoader, AccountConfig


async def safe_config_loading() -> Any:
    """Demonstrate safe configuration loading with comprehensive validation and error handling."""

    print(f"Secure Safe Configuration Loading Example")
    print(f"Security  Implementing robust validation and error handling")

    # Step 1: Load configuration with comprehensive validation
    print(f"\nList Step 1: Loading MYBOT configuration with validation...")
    print(f"   Search Searching for MYBOT_FIVETWENTY_OANDA_* environment variables")

    config = AccountConfigLoader.from_env_prefix("MYBOT_")

    # Step 2: Validate configuration loading with detailed feedback
    if config is None:
        print(f"Error Configuration validation failed")
        print(f"Note Required environment variables missing:")
        print(f"   • MYBOT_FIVETWENTY_OANDA_TOKEN (your OANDA API token)")
        print(f"   • MYBOT_FIVETWENTY_OANDA_ACCOUNT (your OANDA account ID)")
        print(f"   • MYBOT_FIVETWENTY_OANDA_ENVIRONMENT ('practice' or 'live')")
        print(f"\nConfig Setup instructions:")
        print(f"   export MYBOT_FIVETWENTY_OANDA_TOKEN='your-api-token'")
        print(f"   export MYBOT_FIVETWENTY_OANDA_ACCOUNT='your-account-id'")
        print(f"   export MYBOT_FIVETWENTY_OANDA_ENVIRONMENT='practice'")
        raise ValueError("MYBOT_ environment variables not found or incomplete")

    print(f"Success Configuration loaded and validated")
    print(f"   World Environment: {config.environment.value}")
    print(f"   Tag  Alias: {config.alias}")
    print(f"   Lock Security: Credentials properly masked")

    # Step 3: Use the validated configuration with comprehensive error handling
    print(f"\nLink Step 2: Initializing client with validated configuration...")
    try:
        async with AsyncClient(config=config) as client:
            print(f"Success Client initialized successfully")

            # Step 4: Validate account access
            print(f"\nSearch Step 3: Validating account access...")
            account = await client.accounts.get_account(client.account_id)

            print(f"Success Account access validated")
            print(f"Data Account Details:")
            print(f"   Balance Balance: {account.balance} {account.currency}")
            print(f"   Analysis Margin: {account.margin_available}")
            print(f"   Numbers Positions: {account.open_position_count}")

            return account

    except Exception as e:
        print(f"Error Client operation failed: {type(e).__name__}")
        print(f"Search Error details: {e}")
        print(f"Note Troubleshooting steps:")
        print(f"   1. Verify token is valid and not expired")
        print(f"   2. Check account ID matches OANDA account")
        print(f"   3. Ensure network connectivity")
        print(f"   4. Validate environment setting")
        raise


# Alternative: Handle missing configuration gracefully with fallback options
async def graceful_config_loading() -> Any:
    """Demonstrate graceful configuration loading with fallback mechanisms and user-friendly error handling."""

    print(f"🤝 Graceful Configuration Loading Example")
    print(f"Processing Implementing fallback mechanisms for robust configuration")

    # Step 1: Attempt to load optional configuration
    print(f"\nList Step 1: Attempting to load OPTIONAL_BOT configuration...")
    config = AccountConfigLoader.from_env_prefix("OPTIONAL_BOT_")

    # Step 2: Graceful fallback to default configuration
    if config is None:
        print(f"⚠️  OPTIONAL_BOT configuration not found")
        print(f"Processing Falling back to default FIVETWENTY configuration...")

        config = AccountConfigLoader.load_default()

        if config is None:
            print(f"Error No valid configuration found")
            print(f"Note Setup at least one configuration:")
            print(f"\nTarget Option 1 - Optional Bot Configuration:")
            print(f"   export OPTIONAL_BOT_FIVETWENTY_OANDA_TOKEN='bot-token'")
            print(f"   export OPTIONAL_BOT_FIVETWENTY_OANDA_ACCOUNT='bot-account'")
            print(f"   export OPTIONAL_BOT_FIVETWENTY_OANDA_ENVIRONMENT='practice'")
            print(f"\nTarget Option 2 - Default Configuration:")
            print(f"   export FIVETWENTY_OANDA_TOKEN='default-token'")
            print(f"   export FIVETWENTY_OANDA_ACCOUNT='default-account'")
            print(f"   export FIVETWENTY_OANDA_ENVIRONMENT='practice'")
            raise ValueError("No valid configuration found")
        else:
            print(f"Success Default configuration loaded as fallback")
            print(f"   World Environment: {config.environment.value}")
            print(f"   Tag  Alias: {config.alias}")
    else:
        print(f"Success OPTIONAL_BOT configuration loaded successfully")
        print(f"   World Environment: {config.environment.value}")
        print(f"   Tag  Alias: {config.alias}")

    # Step 3: Use the configuration with comprehensive validation
    print(f"\nLink Step 2: Initializing client with selected configuration...")
    try:
        async with AsyncClient(config=config) as client:
            print(f"Success Client initialized with {config.alias} configuration")

            # Step 4: Validate functionality
            print(f"\nSearch Step 3: Testing client functionality...")
            account = await client.accounts.get_account(client.account_id)

            print(f"Success Graceful configuration loading successful")
            print(f"Data Final Account Status:")
            print(f"   Balance Balance: {account.balance} {account.currency}")
            print(f"   Config Configuration: {config.alias}")
            print(f"   World Environment: {config.environment.value}")

            # Step 5: Usage recommendations
            print(f"\nNote Graceful Loading Benefits:")
            print(f"   Success Fallback mechanisms prevent total failure")
            print(f"   Success User-friendly error messages")
            print(f"   Success Multiple configuration options supported")
            print(f"   Success Robust error handling")

            return account

    except Exception as e:
        print(f"Error Graceful loading failed: {type(e).__name__}")
        print(f"Search Error details: {e}")
        print(f"Note Even with fallback, configuration issues exist")
        print(f"Config Verify at least one valid configuration source")
        raise
```

### Resource Management
Always use context managers to ensure proper client cleanup:

<!-- fragment: Demo resource management with asyncio -->
```python
import asyncio
from typing import Any

from fivetwenty import AsyncClient
from fivetwenty.configuration import AccountConfigLoader


async def main() -> None:
    """Demonstrate proper resource management patterns with comprehensive examples and best practices."""

    print(f"🧹 Resource Management Best Practices")
    print(f"Config Demonstrating correct and incorrect patterns for client lifecycle management")

    # Step 1: Load configuration with validation
    print(f"\nList Step 1: Loading configuration...")
    config = AccountConfigLoader.load_default()

    if config is None:
        print(f"Error No configuration found")
        print(f"Note Setup required environment variables:")
        print(f"   export FIVETWENTY_OANDA_TOKEN='your-token'")
        print(f"   export FIVETWENTY_OANDA_ACCOUNT='your-account'")
        print(f"   export FIVETWENTY_OANDA_ENVIRONMENT='practice'")
        raise ValueError("No configuration found")

    print(f"Success Configuration loaded: {config.alias}")

    # Step 2: Demonstrate CORRECT resource management
    print(f"\nSuccess CORRECT Pattern: Using async context manager")
    print(f"   Note Ensures automatic resource cleanup")
    print(f"   Config Handles connection closing, session cleanup, etc.")

    try:
        # CORRECT: async context manager ensures proper cleanup
        async with AsyncClient(config=config) as client:
            print(f"   Link Client initialized with context manager")
            print(f"   Data Client status: ACTIVE")

            # Perform operations
            account = await client.accounts.get_account(client.account_id)
            print(f"   Success Account operation successful: {account.balance} {account.currency}")
            print(f"   Analysis Margin available: {account.margin_available}")

            # Context manager automatically handles cleanup here
            print(f"   🧹 Context manager will handle cleanup automatically")

        print(f"   Success Client properly closed by context manager")
        print(f"   Secure All resources cleaned up")

    except Exception as e:
        print(f"   Error Error with correct pattern: {e}")
        print(f"   Note Even with errors, context manager ensures cleanup")

    # Step 3: Demonstrate INCORRECT resource management (for educational purposes)
    print(f"\nError INCORRECT Pattern: Manual client management")
    print(f"   ⚠️  Potential resource leaks")
    print(f"   ⚠️ Connections may not be properly closed")
    print(f"   Note Educational example - DO NOT use in production")

    try:
        # INCORRECT: Manual management without context manager
        client = AsyncClient(config=config)
        print(f"   Link Client created manually (no context manager)")
        print(f"   ⚠️  Client status: CREATED but not properly managed")

        # Client is created but __aenter__ was never called
        # This means the session is not initialized
        print(f"   Error Client session not initialized - operations will fail")
        print(f"   Note Missing: await client.__aenter__() or async with pattern")

        # This will likely fail because session isn't initialized
        try:
            account = await client.accounts.get_account(client.account_id)
            print(f"   ⚠️  Operation somehow succeeded: {account.balance}")
        except Exception as op_error:
            print(f"   Error Operation failed as expected: {type(op_error).__name__}")
            print(f"   Note Session not initialized - context manager required")

        # Manual cleanup attempt (not recommended)
        try:
            print(f"   🧹 Attempting manual cleanup...")
            if hasattr(client, '_session') and client._session:
                await client._session.aclose()
            print(f"   ⚠️  Manual cleanup attempted (unreliable)")
        except Exception as cleanup_error:
            print(f"   Error Manual cleanup failed: {cleanup_error}")
            print(f"   Note This demonstrates why context managers are essential")

    except Exception as e:
        print(f"   Error Incorrect pattern failed: {type(e).__name__}: {e}")
        print(f"   Note This demonstrates the problems with manual management")

    # Step 4: Advanced resource management patterns
    print(f"\nTarget Advanced Resource Management Patterns:")

    # Multiple clients with proper resource management
    print(f"\n   Link Multiple Clients Pattern:")
    try:
        # Multiple clients using nested context managers
        config1 = config  # Use same config for demo
        config2 = config  # In practice, these would be different

        async with AsyncClient(config=config1) as client1:
            async with AsyncClient(config=config2) as client2:
                print(f"      Success Multiple clients properly managed")
                print(f"      Config Each client has isolated resources")
                print(f"      🧹 Cleanup guaranteed for all clients")

                # Quick validation
                acc1 = await client1.accounts.get_account(client1.account_id)
                acc2 = await client2.accounts.get_account(client2.account_id)
                print(f"      Data Both clients operational")

        print(f"      Success All clients properly cleaned up")

    except Exception as e:
        print(f"      Error Multiple client pattern error: {e}")

    # Step 5: Resource management best practices summary
    print(f"\n📚 Resource Management Best Practices:")
    print(f"   Success ALWAYS use 'async with AsyncClient(config) as client:'")
    print(f"   Success Let context managers handle initialization and cleanup")
    print(f"   Success Multiple clients: use nested context managers")
    print(f"   Success Error handling: context managers clean up even on exceptions")
    print(f"   Error NEVER create clients without context managers")
    print(f"   Error NEVER rely on manual cleanup")
    print(f"   Error NEVER ignore resource lifecycle management")

    print(f"\nNote Why Context Managers Are Essential:")
    print(f"   Secure Automatic resource cleanup")
    print(f"   Security  Exception safety")
    print(f"   🧹 Memory leak prevention")
    print(f"   Link Proper connection management")
    print(f"   Lightning Optimal performance")

    print(f"\nFlag Resource management demonstration completed")


# Step 6: Provide correct usage example
if __name__ == "__main__":
    print(f"Starting Starting resource management demonstration...")
    try:
        asyncio.run(main())
        print(f"\nSuccess Demonstration completed successfully")
    except KeyboardInterrupt:
        print(f"\nStop  Demonstration interrupted by user")
    except Exception as e:
        print(f"\nError Demonstration failed: {type(e).__name__}: {e}")
        print(f"Note Check your environment configuration")
```

## Real-World Example

Here's a complete example showing how to manage multiple accounts for different trading strategies:

<!-- fragment: Demo complete trading system with nested async context managers -->
```python
import asyncio
from typing import Dict, Any, Optional

from fivetwenty import AsyncClient
from fivetwenty.configuration import AccountConfigLoader, AccountConfig


async def trading_system() -> None:
    """Complete multi-account trading system with comprehensive error handling and monitoring."""

    print(f"Starting Multi-Account Trading System")
    print(f"Target Initializing scalping, swing, and hedging strategies across multiple accounts")

    # Step 1: Load different account configurations for specialized strategies
    print(f"\nList Step 1: Loading strategy-specific configurations...")
    print(f"   Search Scalp Strategy: SCALP_FIVETWENTY_OANDA_*")
    print(f"   Search Swing Strategy: SWING_FIVETWENTY_OANDA_*")
    print(f"   Search Hedge Strategy: HEDGE_FIVETWENTY_OANDA_*")

    scalp_config = AccountConfigLoader.from_env_prefix("SCALP_")
    swing_config = AccountConfigLoader.from_env_prefix("SWING_")
    hedge_config = AccountConfigLoader.from_env_prefix("HEDGE_")

    # Step 2: Validate all configurations with detailed feedback
    configs: Dict[str, Optional[AccountConfig]] = {
        'scalping': scalp_config,
        'swing': swing_config,
        'hedge': hedge_config
    }

    print(f"\nSuccess Step 2: Validating strategy configurations...")
    valid_configs = {}

    for name, config in configs.items():
        if config is None:
            print(f"   Error {name.capitalize()} strategy: Configuration not found")
            prefix = name.upper()
            print(f"      Note Required variables:")
            print(f"         export {prefix}_FIVETWENTY_OANDA_TOKEN='strategy-token'")
            print(f"         export {prefix}_FIVETWENTY_OANDA_ACCOUNT='strategy-account'")
            print(f"         export {prefix}_FIVETWENTY_OANDA_ENVIRONMENT='practice'")
            raise ValueError(f"Configuration for {name} strategy not found. "
                           f"Please set {prefix}_FIVETWENTY_OANDA_* environment variables")
        else:
            print(f"   Success {name.capitalize()} strategy: Configuration loaded")
            print(f"      World Environment: {config.environment.value}")
            print(f"      Tag  Alias: {config.alias}")
            if config.environment.value == "live":
                print(f"      ⚠️  LIVE environment - real money strategy")
            valid_configs[name] = config

    print(f"\nData Configuration Summary:")
    for name, config in valid_configs.items():
        print(f"   Target {name.capitalize()}: {config.summary()}")

    # Step 3: Initialize clients with proper resource management
    print(f"\nLink Step 3: Initializing multi-client trading environment...")
    try:
        # Nested async context managers ensure all clients are properly managed
        async with AsyncClient(config=scalp_config) as scalp_client, \
                   AsyncClient(config=swing_config) as swing_client, \
                   AsyncClient(config=hedge_config) as hedge_client:

            print(f"Success All trading clients initialized successfully")
            print(f"Data Active Clients:")
            print(f"   Lightning Scalping: {scalp_client.config.alias} ({scalp_client.environment.value})")
            print(f"   Analysis Swing: {swing_client.config.alias} ({swing_client.environment.value})")
            print(f"   Security  Hedging: {hedge_client.config.alias} ({hedge_client.environment.value})")

            # Step 4: Validate all client connections before starting strategies
            print(f"\nSearch Step 4: Validating client connections...")

            # Validate each client connection
            clients_info = [
                ("Scalping", scalp_client),
                ("Swing", swing_client),
                ("Hedging", hedge_client)
            ]

            for strategy_name, client in clients_info:
                try:
                    account = await client.accounts.get_account(client.account_id)
                    print(f"   Success {strategy_name}: Connected - {account.balance} {account.currency}")
                except Exception as validation_error:
                    print(f"   Error {strategy_name}: Validation failed - {validation_error}")
                    raise

            # Step 5: Launch concurrent trading strategies
            print(f"\nStarting Step 5: Starting concurrent trading strategies...")
            print(f"   Lightning Launching high-frequency scalping operations")
            print(f"   Analysis Launching medium-term swing operations")
            print(f"   Security  Launching risk management hedging operations")

            # Execute all strategies concurrently with proper error isolation
            strategy_tasks = await asyncio.gather(
                scalping_strategy(scalp_client),
                swing_strategy(swing_client),
                hedging_strategy(hedge_client),
                return_exceptions=True  # Prevent one strategy failure from stopping others
            )

            # Step 6: Analyze strategy execution results
            print(f"\nData Step 6: Strategy execution summary...")
            strategy_names = ["Scalping", "Swing", "Hedging"]

            for i, (name, result) in enumerate(zip(strategy_names, strategy_tasks)):
                if isinstance(result, Exception):
                    print(f"   Error {name} strategy failed: {result}")
                else:
                    print(f"   Success {name} strategy completed successfully")

            print(f"\nTarget All trading strategies execution completed")

    except Exception as system_error:
        print(f"Error Trading system error: {type(system_error).__name__}")
        print(f"Search Error details: {system_error}")
        print(f"Note System-level failure - check configurations and connectivity")
        raise


async def scalping_strategy(client: AsyncClient) -> None:
    """High-frequency scalping strategy with comprehensive implementation."""

    print(f"\nLightning SCALPING STRATEGY INITIATED")
    print(f"   Target Account: {client.account_id}")
    print(f"   World Environment: {client.environment.value}")

    try:
        # Step 1: Initialize scalping environment
        account = await client.accounts.get_account(client.account_id)
        print(f"   Balance Starting balance: {account.balance} {account.currency}")
        print(f"   Data Available margin: {account.margin_available}")

        # Step 2: Scalping strategy implementation
        print(f"   Processing Implementing high-frequency scalping logic...")
        print(f"   Analysis Strategy focus: Quick profits from small price movements")
        print(f"   Time  Target timeframe: Seconds to minutes")
        print(f"   Target Risk management: Tight stop-losses")

        # Example scalping operations (customize based on your strategy)
        print(f"   Success Scalping operations:")
        print(f"      • Price tick analysis: Monitoring micro-movements")
        print(f"      • Order book depth: Analyzing liquidity")
        print(f"      • Spread optimization: Finding best entry/exit points")
        print(f"      • Position sizing: Risk-controlled unit allocation")

        # Simulate strategy execution time
        await asyncio.sleep(2)

        print(f"   Flag Scalping strategy cycle completed")

    except Exception as e:
        print(f"   Error Error in scalping strategy: {type(e).__name__}: {e}")
        print(f"   Note Scalping requires stable connectivity and low latency")
        raise


async def swing_strategy(client: AsyncClient) -> None:
    """Medium-term swing strategy with trend analysis and position management."""

    print(f"\nAnalysis SWING STRATEGY INITIATED")
    print(f"   Target Account: {client.account_id}")
    print(f"   World Environment: {client.environment.value}")

    try:
        # Step 1: Initialize swing trading environment
        account = await client.accounts.get_account(client.account_id)
        print(f"   Balance Starting balance: {account.balance} {account.currency}")
        print(f"   Data Portfolio positions: {account.open_position_count}")

        # Step 2: Swing strategy implementation
        print(f"   Processing Implementing swing trading logic...")
        print(f"   Data Strategy focus: Capturing medium-term price swings")
        print(f"   Time  Target timeframe: Hours to days")
        print(f"   Analysis Analysis: Technical indicators and trend patterns")

        # Example swing trading operations
        print(f"   Success Swing trading operations:")
        print(f"      • Trend analysis: Identifying market direction")
        print(f"      • Support/resistance: Finding key price levels")
        print(f"      • Moving averages: Confirming trend strength")
        print(f"      • Volume analysis: Validating price movements")
        print(f"      • Risk/reward: Calculating optimal position sizes")

        # Simulate strategy execution time
        await asyncio.sleep(2)

        print(f"   Flag Swing strategy analysis completed")

    except Exception as e:
        print(f"   Error Error in swing strategy: {type(e).__name__}: {e}")
        print(f"   Note Swing trading requires market analysis and patience")
        raise


async def hedging_strategy(client: AsyncClient) -> None:
    """Risk management hedging strategy with portfolio protection focus."""

    print(f"\nSecurity  HEDGING STRATEGY INITIATED")
    print(f"   Target Account: {client.account_id}")
    print(f"   World Environment: {client.environment.value}")

    try:
        # Step 1: Initialize hedging environment
        account = await client.accounts.get_account(client.account_id)
        print(f"   Balance Portfolio value: {account.balance} {account.currency}")
        print(f"   Data Exposure analysis: {account.open_position_count} positions")
        print(f"   Analysis Margin utilization: {account.margin_used} / {account.margin_available}")

        # Step 2: Hedging strategy implementation
        print(f"   Processing Implementing risk management hedging...")
        print(f"   Security  Strategy focus: Portfolio protection and risk mitigation")
        print(f"   Scale  Risk assessment: Analyzing exposure and correlation")
        print(f"   Secure Capital preservation: Protecting against adverse moves")

        # Example hedging operations
        print(f"   Success Hedging operations:")
        print(f"      • Position correlation: Analyzing inter-position risks")
        print(f"      • Exposure calculation: Measuring net currency exposure")
        print(f"      • Hedge ratio optimization: Determining optimal hedge sizes")
        print(f"      • Dynamic rebalancing: Adjusting hedges based on market conditions")
        print(f"      • Stress testing: Modeling portfolio under adverse scenarios")

        # Simulate strategy execution time
        await asyncio.sleep(2)

        print(f"   Flag Hedging strategy risk assessment completed")

    except Exception as e:
        print(f"   Error Error in hedging strategy: {type(e).__name__}: {e}")
        print(f"   Note Hedging requires comprehensive risk analysis")
        raise


# Step 7: Entry point with comprehensive error handling
async def main() -> None:
    """Main entry point for the trading system with comprehensive error handling."""

    print(f"Target FiveTwenty Multi-Account Trading System")
    print(f"Lightning Initializing professional trading environment...")

    try:
        await trading_system()
        print(f"\nAchievement Trading system completed successfully")
        print(f"Data All strategies executed without critical errors")
        print(f"Success System shutdown: Clean resource cleanup")

    except ValueError as config_error:
        print(f"\nError Configuration Error: {config_error}")
        print(f"Note Resolution steps:")
        print(f"   1. Check all required environment variables are set")
        print(f"   2. Verify OANDA account credentials")
        print(f"   3. Ensure proper environment configuration (practice/live)")
        print(f"   4. Review the setup instructions above")

    except Exception as system_error:
        print(f"\nError Unexpected system error: {type(system_error).__name__}")
        print(f"Search Error details: {system_error}")
        print(f"Note Troubleshooting:")
        print(f"   1. Check network connectivity")
        print(f"   2. Verify OANDA API service status")
        print(f"   3. Review system logs for additional details")
        print(f"   4. Contact support if issues persist")


# Run the trading system with proper execution handling
if __name__ == "__main__":
    print(f"Starting Starting FiveTwenty Multi-Account Trading System...")
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(f"\nStop  Trading system interrupted by user")
        print(f"🧹 Performing emergency shutdown...")
        print(f"Success System stopped safely")
    except Exception as e:
        print(f"\n💥 Critical system failure: {type(e).__name__}: {e}")
        print(f"⚠️ Emergency protocols activated")
        print(f"Call Contact system administrator immediately")
```

## Environment Setup Examples

### Shell Script Setup
```bash
#!/bin/bash
# setup-trading-env.sh

# Scalping account (practice)
export SCALP_FIVETWENTY_OANDA_TOKEN="your-scalp-practice-token"
export SCALP_FIVETWENTY_OANDA_ACCOUNT="your-scalp-account-id"
export SCALP_FIVETWENTY_OANDA_ENVIRONMENT="practice"

# Swing trading account (live)
export SWING_FIVETWENTY_OANDA_TOKEN="your-swing-live-token"
export SWING_FIVETWENTY_OANDA_ACCOUNT="your-swing-account-id"
export SWING_FIVETWENTY_OANDA_ENVIRONMENT="live"

# Hedging account (live)
export HEDGE_FIVETWENTY_OANDA_TOKEN="your-hedge-live-token"
export HEDGE_FIVETWENTY_OANDA_ACCOUNT="your-hedge-account-id"
export HEDGE_FIVETWENTY_OANDA_ENVIRONMENT="live"

echo "Trading environment configured"
```

### Docker Environment File
```bash
# .env file for Docker
SCALP_FIVETWENTY_OANDA_TOKEN=your-scalp-token
SCALP_FIVETWENTY_OANDA_ACCOUNT=scalp-account-id
SCALP_FIVETWENTY_OANDA_ENVIRONMENT=practice

SWING_FIVETWENTY_OANDA_TOKEN=your-swing-token
SWING_FIVETWENTY_OANDA_ACCOUNT=swing-account-id
SWING_FIVETWENTY_OANDA_ENVIRONMENT=live
```

This multi-account configuration approach lets you:

- Run different strategies on different accounts
- Separate practice and live trading
- Organize accounts by risk profile or strategy type
- Scale your trading operations across multiple OANDA accounts

Remember to always test your multi-account setup in the practice environment before deploying to live trading accounts.