#!/usr/bin/env python3
"""
Configuration Patterns Example

Demonstrates different ways to configure the client:
- Environment variables (default)
- Direct configuration
- AccountConfig usage
- Multi-account setup
- Custom environment prefixes
"""

import asyncio
import os

from pydantic import SecretStr

from fivetwenty import AccountConfig, AsyncClient, Environment


async def main() -> None:
    """Configuration patterns example."""

    # Section 1: Default environment variable configuration
    print("\n=== 1. Environment Variable Configuration ===")

    print("\nDefault configuration reads from environment variables:")
    print("  FIVETWENTY_OANDA_TOKEN")
    print("  FIVETWENTY_OANDA_ACCOUNT")
    print("  FIVETWENTY_OANDA_ENVIRONMENT")

    async with AsyncClient() as client:
        print("\n✅ Connected using environment variables")
        print(f"Account: {client.account_id}")
        print(f"Environment: {client._environment.value}")

    # Section 2: Direct parameter configuration
    print("\n=== 2. Direct Parameter Configuration ===")

    print("\nYou can pass configuration directly to the client:")

    # Get values from environment for this example
    token = os.getenv("FIVETWENTY_OANDA_TOKEN")
    account_id = os.getenv("FIVETWENTY_OANDA_ACCOUNT")

    async with AsyncClient(token=token, account_id=account_id, environment=Environment.PRACTICE) as client:
        print("✅ Connected with direct parameters")
        print(f"Account: {client.account_id}")
        print(f"Environment: {client._environment}")

    # Section 3: Using AccountConfig
    print("\n=== 3. AccountConfig Usage ===")

    print("\nAccountConfig provides structured configuration:")

    config = AccountConfig(alias="example", token=SecretStr(token) if token else SecretStr(""), account_id=SecretStr(account_id) if account_id else SecretStr(""), environment=Environment.PRACTICE)

    print("\nAccountConfig created:")
    print(f"  Account ID: {config.account_id.get_secret_value()}")
    print(f"  Environment: {config.environment}")
    print(f"  Token: {config.token.get_secret_value()[:10]}... (masked)")

    async with AsyncClient(config=config) as client:
        print("\n✅ Connected with AccountConfig")
        summary = await client.accounts.get_account_summary(client.account_id)
        print(f"Balance: {summary['account'].balance}")

    # Section 4: Multi-account configuration
    print("\n=== 4. Multi-Account Configuration ===")

    print("\nManage multiple accounts using custom prefixes:")
    print("\nExample environment variables:")
    print("  ACCOUNT_A_OANDA_TOKEN=token-1")
    print("  ACCOUNT_A_OANDA_ACCOUNT=account-1")
    print("  ACCOUNT_A_OANDA_ENVIRONMENT=practice")
    print()
    print("  ACCOUNT_B_OANDA_TOKEN=token-2")
    print("  ACCOUNT_B_OANDA_ACCOUNT=account-2")
    print("  ACCOUNT_B_OANDA_ENVIRONMENT=practice")

    print("\n💡 Usage:")
    print("""
# Account A
async with AsyncClient(env_prefix="ACCOUNT_A_") as client_a:
    print(f"Account A: {client_a.account_id}")

# Account B
async with AsyncClient(env_prefix="ACCOUNT_B_") as client_b:
    print(f"Account B: {client_b.account_id}")
    """)

    # Section 5: Custom environment prefixes
    print("\n=== 5. Custom Environment Prefixes ===")

    print("\nUse custom prefixes for different strategies:")
    print("  STRATEGY_1_OANDA_TOKEN")
    print("  STRATEGY_1_OANDA_ACCOUNT")
    print("  STRATEGY_1_OANDA_ENVIRONMENT")

    print("\n  STRATEGY_2_OANDA_TOKEN")
    print("  STRATEGY_2_OANDA_ACCOUNT")
    print("  STRATEGY_2_OANDA_ENVIRONMENT")

    print("\n💡 This allows:")
    print("  - Multiple strategies on same account")
    print("  - Different accounts per strategy")
    print("  - Easy environment switching")

    # Section 6: Configuration from files
    print("\n=== 6. Configuration from Files ===")

    print("\n1. Using python-dotenv:")
    print("""
from dotenv import load_dotenv

# Load from .env file
load_dotenv()

# Now environment variables are available
async with AsyncClient() as client:
    print(f"Connected: {client.account_id}")
    """)

    print("\n2. Using JSON configuration:")
    print("""
import json

with open('config.json') as f:
    config = json.load(f)

async with AsyncClient(
    token=config['token'],
    account_id=config['account_id'],
    environment=Environment.PRACTICE
) as client:
    print(f"Connected from JSON config")
    """)

    print("\n3. Using YAML configuration:")
    print("""
import yaml

with open('config.yaml') as f:
    config = yaml.safe_load(f)

async with AsyncClient(
    token=config['oanda']['token'],
    account_id=config['oanda']['account_id'],
    environment=Environment.PRACTICE
) as client:
    print(f"Connected from YAML config")
    """)

    # Section 7: Practice vs Live environment
    print("\n=== 7. Practice vs Live Environment ===")

    print("\nEnvironment Selection:")
    print("  Environment.PRACTICE - Practice trading (sandbox)")
    print("    URL: api-fxpractice.oanda.com")
    print("    Use for: Testing, development, learning")
    print("    Risk: None (virtual money)")

    print("\n  Environment.LIVE - Live trading (real money)")
    print("    URL: api-fxtrade.oanda.com")
    print("    Use for: Production trading")
    print("    Risk: Real capital at stake")

    print("\n⚠️  SAFETY:")
    print("  - ALWAYS test in PRACTICE first")
    print("  - Use separate tokens for practice/live")
    print("  - Double-check environment before trading")
    print("  - Start with small positions in live")

    # Section 8: Configuration validation
    print("\n=== 8. Configuration Validation ===")

    print("\nFiveTwenty validates configuration at runtime:")

    print("\nCommon Configuration Errors:")
    print("  ❌ Missing token")
    print("     Error: 'OANDA API token is required'")

    print("\n  ❌ Missing account_id")
    print("     Error: 'OANDA account ID is required'")

    print("\n  ❌ Invalid environment")
    print("     Error: 'Invalid environment value'")

    print("\n  ❌ Invalid token format")
    print("     Error: 401 Unauthorized")

    print("\n✅ Validation occurs when creating AsyncClient")
    print("   Errors are raised before any API calls")

    # Section 9: Secure configuration practices
    print("\n=== 9. Secure Configuration ===")

    print("\nBest Practices:")
    print("  ✅ Use environment variables or secure vaults")
    print("  ✅ Never commit credentials to version control")
    print("  ✅ Add .env to .gitignore")
    print("  ✅ Use different tokens for different environments")
    print("  ✅ Rotate tokens periodically")
    print("  ✅ Use restrictive file permissions (chmod 600 .env)")

    print("\n.gitignore patterns:")
    print("  .env")
    print("  .env.*")
    print("  config.json")
    print("  *credentials*")

    print("\nAccountConfig automatically masks sensitive data:")
    masked_config = AccountConfig(alias="demo", token=SecretStr("super-secret-token-12345"), account_id=SecretStr("123-456-7890123-001"), environment=Environment.PRACTICE)
    print(f"  Token in repr: {masked_config!r}")
    print("  (Token is masked, not exposed in logs)")

    # Section 10: Runtime configuration updates
    print("\n=== 10. Runtime Configuration Updates ===")

    print("\nSwitching configuration at runtime:")

    print("\n1. Close existing client:")
    print("""
async with AsyncClient() as client1:
    # Use first configuration
    print(f"Client 1: {client1.account_id}")

# Client 1 automatically closed

async with AsyncClient(account_id="different-account") as client2:
    # Use second configuration
    print(f"Client 2: {client2.account_id}")
    """)

    print("\n2. Multiple simultaneous clients:")
    print("""
async with AsyncClient(account_id="account-1") as client1, \\
           AsyncClient(account_id="account-2") as client2:
    # Both clients active
    balance1 = await client1.accounts.get_account_summary(client1.account_id)
    balance2 = await client2.accounts.get_account_summary(client2.account_id)
    """)

    print("\n💡 Use Cases:")
    print("  - Trading across multiple accounts")
    print("  - Separate live and practice monitoring")
    print("  - Different strategies with different configs")

    print("\n✅ Configuration patterns example completed!")


if __name__ == "__main__":
    asyncio.run(main())
