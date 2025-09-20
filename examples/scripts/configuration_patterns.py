#!/usr/bin/env python3
"""
Configuration Patterns Example

This example demonstrates the three ways to configure the FiveTwenty client:
1. Direct parameters
2. Configuration objects
3. Environment variables

Run with: uv run python docs/examples/scripts/configuration_patterns.py
"""

import asyncio
import os

from fivetwenty import AccountConfig, AsyncClient, Environment


async def main():
    """Demonstrate all three configuration patterns."""

    print("🔧 fivetwenty Configuration Patterns")
    print("=" * 50)

    # Pattern 1: Direct Parameters
    print("\n1️⃣ Direct Parameters")
    print("   Simple and explicit - pass credentials directly")

    async with AsyncClient(token="your-api-token-here", account_id="your-account-id-here", environment=Environment.PRACTICE) as client:
        print(f"   ✅ Client initialized: {client.config.summary()}")
        print(f"   📝 Account ID: {client.account_id}")

    # Pattern 2: Configuration Object
    print("\n2️⃣ Configuration Object")
    print("   Structured and reusable - create config objects")

    # Create configuration for a practice account
    practice_config = AccountConfig(token="your-api-token-here", account_id="practice-account-123", environment=Environment.PRACTICE, alias="practice_trading")

    async with AsyncClient(config=practice_config) as client:
        print(f"   ✅ Client initialized: {client.config.summary()}")

    # Create configuration for a live account
    live_config = AccountConfig(token="live-token-xyz789", account_id="live-account-789", environment=Environment.LIVE, alias="live_trading")

    print(f"   🏭 Live config created: {live_config.summary()}")
    print(f"   🔒 Secrets are masked: {live_config!r}")

    # Pattern 3: Environment Variables
    print("\n3️⃣ Environment Variables")
    print("   Zero-config - automatically loads from environment")

    # Set environment variables (normally done by your deployment system)
    os.environ["FIVETWENTY_OANDA_TOKEN"] = "env-token-456"
    os.environ["FIVETWENTY_OANDA_ACCOUNT"] = "env-account-456"
    os.environ["FIVETWENTY_OANDA_ENVIRONMENT"] = "practice"
    os.environ["FIVETWENTY_OANDA_ACCOUNT_ALIAS"] = "env_trading"

    async with AsyncClient() as client:  # No parameters needed!
        print(f"   ✅ Client initialized: {client.config.summary()}")
        print("   🌍 Loaded from environment variables")

    # Multiple Accounts Pattern
    print("\n4️⃣ Multiple Accounts (User Managed)")
    print("   Use different prefixes for multiple accounts")

    # Set up two different accounts with different prefixes
    os.environ["FIVETWENTY_MOMENTUM_TOKEN"] = "momentum-token"
    os.environ["FIVETWENTY_MOMENTUM_ACCOUNT_ID"] = "momentum-account"
    os.environ["FIVETWENTY_MOMENTUM_OANDA_ENVIRONMENT"] = "practice"
    os.environ["FIVETWENTY_MOMENTUM_ACCOUNT_ALIAS"] = "momentum_strategy"

    os.environ["FIVETWENTY_GRID_TOKEN"] = "grid-token"
    os.environ["FIVETWENTY_GRID_ACCOUNT_ID"] = "grid-account"
    os.environ["FIVETWENTY_GRID_OANDA_ENVIRONMENT"] = "practice"
    os.environ["FIVETWENTY_GRID_ACCOUNT_ALIAS"] = "grid_strategy"

    # Load configurations with custom prefixes
    from fivetwenty import AccountConfigLoader

    momentum_config = AccountConfigLoader.from_env_prefix("FIVETWENTY_MOMENTUM_")
    grid_config = AccountConfigLoader.from_env_prefix("FIVETWENTY_GRID_")

    if momentum_config and grid_config:
        async with AsyncClient(config=momentum_config) as momentum_client, AsyncClient(config=grid_config) as grid_client:
            print(f"   📈 Momentum client: {momentum_client.config.summary()}")
            print(f"   📊 Grid client: {grid_client.config.summary()}")

    # Security Features
    print("\n🔒 Security Features")
    print("   All account data is automatically protected")

    secret_config = AccountConfig(token="your-api-token-here", account_id="secret-account-12345", environment=Environment.LIVE, alias="secret_account")

    print(f"   🔒 String representation masks secrets: {secret_config!r}")
    print(f"   ✅ Summary is safe for logs: {secret_config.summary()}")
    print("   💡 Secrets never appear in logs or string output")

    print("\n🎉 All configuration patterns demonstrated!")
    print("\n💡 Tips:")
    print("   • Use direct parameters for simple scripts")
    print("   • Use config objects for structured applications")
    print("   • Use environment variables for deployment")
    print("   • Always keep your tokens secure!")


if __name__ == "__main__":
    asyncio.run(main())
