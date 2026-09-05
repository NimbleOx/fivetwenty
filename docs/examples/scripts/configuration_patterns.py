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
    # =====================================================
    # Environment variables are the RECOMMENDED way to configure FiveTwenty
    # because they:
    # - Keep credentials out of your source code
    # - Work well with containers and cloud platforms
    # - Are easy to manage in development and production
    # - Support the 12-factor app methodology
    #
    # The client looks for these specific variable names by default:
    # - FIVETWENTY_OANDA_TOKEN: Your OANDA API access token
    # - FIVETWENTY_OANDA_ACCOUNT: Your OANDA account ID
    # - FIVETWENTY_OANDA_ENVIRONMENT: Either "practice" or "live"
    #
    # These can be set in your shell, in a .env file, or via your deployment system
    print("\n=== 1. Environment Variable Configuration ===")

    print("\nDefault configuration reads from environment variables:")
    print("  FIVETWENTY_OANDA_TOKEN - Your API access token")
    print("  FIVETWENTY_OANDA_ACCOUNT - Your account ID")
    print("  FIVETWENTY_OANDA_ENVIRONMENT - 'practice' or 'live'")
    print("\nThese should be set in your environment before running")

    # When you call AsyncClient() with no arguments, it automatically:
    # 1. Reads the above environment variables
    # 2. Validates that required values are present
    # 3. Raises clear errors if anything is missing
    async with AsyncClient() as client:
        print("\n✅ Connected using environment variables")
        print(f"Account: {client.account_id}")
        print(f"Environment: {client._environment.value}")

    # Section 2: Direct parameter configuration
    # =========================================
    # Sometimes you need to pass configuration directly to the client
    # This is useful when:
    # - Testing with different accounts
    # - Loading config from a file or database
    # - Overriding specific values while keeping others from environment
    # - Building tools that manage multiple configurations
    print("\n=== 2. Direct Parameter Configuration ===")

    print("\nYou can pass configuration directly to the client:")
    print("  - Overrides environment variables")
    print("  - Useful for testing and dynamic configuration")
    print("  - Can mix direct parameters with environment variables")

    # For this example, we'll read from environment to avoid hardcoding credentials
    # In production, you might load these from a secure vault or config file
    token = os.getenv("FIVETWENTY_OANDA_TOKEN")
    account_id = os.getenv("FIVETWENTY_OANDA_ACCOUNT")

    # Direct parameter approach: pass values explicitly
    # This takes precedence over environment variables
    # Environment.PRACTICE is an enum - type-safe and validated
    async with AsyncClient(token=token, account_id=account_id, environment=Environment.PRACTICE) as client:
        print("✅ Connected with direct parameters")
        print(f"Account: {client.account_id}")
        print(f"Environment: {client._environment}")
        print("\n💡 Direct parameters override environment variables")

    # Section 3: Using AccountConfig
    # ==============================
    # AccountConfig is a Pydantic model that provides:
    # - Structured, validated configuration
    # - Automatic masking of sensitive data (token, account_id)
    # - Support for multiple account configurations
    # - Type safety and IDE autocomplete
    # - Safe serialization (secrets aren't accidentally exposed)
    #
    # This is the most secure way to handle configuration programmatically
    print("\n=== 3. AccountConfig Usage ===")

    print("\nAccountConfig provides structured configuration:")
    print("  - Type-safe configuration object")
    print("  - Automatic secret masking (using Pydantic SecretStr)")
    print("  - Safe for logging (secrets not exposed)")
    print("  - Supports multiple account configs")

    # AccountConfig requires:
    # - alias: A friendly name for this configuration (e.g., "production", "test")
    # - token: Wrapped in SecretStr for automatic masking
    # - account_id: Also wrapped in SecretStr
    # - environment: The Environment enum
    config = AccountConfig(
        alias="example",  # Friendly name for this config
        token=SecretStr(token) if token else SecretStr(""),  # SecretStr masks the value
        account_id=SecretStr(account_id) if account_id else SecretStr(""),  # Also masked
        environment=Environment.PRACTICE,
    )

    print("\nAccountConfig created:")
    print(f"  Alias: {config.alias}")
    print(f"  Account ID: {config.account_id.get_secret_value()}")  # Explicit .get_secret_value() to access
    print(f"  Environment: {config.environment}")
    print(f"  Token: {config.token.get_secret_value()[:10]}... (masked)")  # Show first 10 chars only

    # When you print or log an AccountConfig, sensitive values are automatically masked
    print(f"\n  repr() output: {config!r}")
    print("  Notice: token and account_id show as SecretStr('**********')")

    # Pass the AccountConfig to the client
    # This is cleaner than passing individual parameters
    async with AsyncClient(config=config) as client:
        print("\n✅ Connected with AccountConfig")
        summary = await client.accounts.get_account_summary(client.account_id)
        print(f"Balance: {summary['account'].balance}")

    # Section 4: Multi-account configuration
    # ======================================
    # Many traders manage multiple accounts:
    # - Different strategies on different accounts
    # - Separate practice and live accounts
    # - Multiple clients or sub-accounts
    #
    # FiveTwenty supports this via custom environment prefixes
    # Instead of FIVETWENTY_OANDA_*, you can use YOUR_PREFIX_FIVETWENTY_OANDA_*
    print("\n=== 4. Multi-Account Configuration ===")

    print("\nManage multiple accounts using custom prefixes:")
    print("  - Each account gets its own prefix")
    print("  - Set different environment variables for each")
    print("  - Load each prefix with AccountConfigLoader.from_env_prefix")

    print("\nExample environment variables:")
    print("  # Account A configuration")
    print("  ACCOUNT_A_FIVETWENTY_OANDA_TOKEN=token-1")
    print("  ACCOUNT_A_FIVETWENTY_OANDA_ACCOUNT=account-1")
    print("  ACCOUNT_A_FIVETWENTY_OANDA_ENVIRONMENT=practice")
    print()
    print("  # Account B configuration")
    print("  ACCOUNT_B_FIVETWENTY_OANDA_TOKEN=token-2")
    print("  ACCOUNT_B_FIVETWENTY_OANDA_ACCOUNT=account-2")
    print("  ACCOUNT_B_FIVETWENTY_OANDA_ENVIRONMENT=practice")

    print("\n💡 Usage:")
    print("  Load a config, require a non-None result, then pass it to AsyncClient:")
    print("  - AccountConfigLoader.from_env_prefix('ACCOUNT_A_') for Account A")
    print("  - AccountConfigLoader.from_env_prefix('ACCOUNT_B_') for Account B")
    print("  - Both can be active simultaneously")

    print("\n⚠️  Important:")
    print("  - Token and account are required; environment defaults to practice")
    print("  - Prefix must include trailing underscore")
    print("  - You can have clients for multiple accounts open at once")

    # Section 5: Custom environment prefixes
    # ======================================
    # Beyond just multiple accounts, prefixes support advanced use cases:
    # - Different strategies with their own configuration
    # - Separating dev/staging/prod configurations
    # - Running multiple instances with different configs
    print("\n=== 5. Custom Environment Prefixes ===")

    print("\nUse custom prefixes for different strategies:")
    print("  # Strategy-based configuration")
    print("  STRATEGY_1_FIVETWENTY_OANDA_TOKEN")
    print("  STRATEGY_1_FIVETWENTY_OANDA_ACCOUNT")
    print("  STRATEGY_1_FIVETWENTY_OANDA_ENVIRONMENT")

    print("\n  STRATEGY_2_FIVETWENTY_OANDA_TOKEN")
    print("  STRATEGY_2_FIVETWENTY_OANDA_ACCOUNT")
    print("  STRATEGY_2_FIVETWENTY_OANDA_ENVIRONMENT")

    print("\n💡 This allows:")
    print("  - Multiple strategies on same account")
    print("    (same account ID, different configurations)")
    print("  - Different accounts per strategy")
    print("    (strategy 1 on account A, strategy 2 on account B)")
    print("  - Easy environment switching")
    print("    (PROD_*, DEV_*, TEST_* prefixes)")

    print("\n  # Environment-based prefixes")
    print("  PROD_FIVETWENTY_OANDA_TOKEN     → Production trading")
    print("  STAGING_FIVETWENTY_OANDA_TOKEN  → Staging/testing")
    print("  DEV_FIVETWENTY_OANDA_TOKEN      → Development")

    # Section 6: Configuration from files
    # ===================================
    # While environment variables are recommended, you might need to load
    # configuration from files in some scenarios:
    # - Local development with .env files
    # - Legacy systems with JSON/YAML configs
    # - Configuration management tools
    print("\n=== 6. Configuration from Files ===")

    print("\n1. Using python-dotenv:")
    print("  - Most popular approach for local development")
    print("  - Loads .env file into environment variables")
    print("  - Works seamlessly with FiveTwenty's env var support")
    print("  - .env file contains: FIVETWENTY_OANDA_TOKEN, FIVETWENTY_OANDA_ACCOUNT, etc.")
    print("  - Call load_dotenv() before creating AsyncClient")

    print("\n2. Using JSON configuration:")
    print("  - Good for structured config files")
    print("  - Easy to read/write programmatically")
    print("  - Load JSON with json.load() and pass values to AsyncClient")
    print("  - ⚠️  Be careful: JSON files might be committed to git!")
    print("  - Remember to add config.json to .gitignore")

    print("\n3. Using YAML configuration:")
    print("  - More readable than JSON")
    print("  - Supports comments")
    print("  - Popular in DevOps/infrastructure tools")
    print("  - Load YAML with yaml.safe_load() and pass values to AsyncClient")

    print("\n⚠️  Security Warning for File-Based Configs:")
    print("  - NEVER commit credentials to version control")
    print("  - Add config files to .gitignore")
    print("  - Use restrictive file permissions (chmod 600)")
    print("  - Consider encrypting config files at rest")
    print("  - Environment variables are generally more secure")

    # Section 7: Practice vs Live environment
    # =======================================
    # This is CRITICAL to understand - choosing the wrong environment
    # can result in real money being traded when you meant to test!
    print("\n=== 7. Practice vs Live Environment ===")

    print("\nEnvironment Selection:")
    print("  Environment.PRACTICE - Practice trading (sandbox)")
    print("    URL: api-fxpractice.oanda.com")
    print("    Use for: Testing, development, learning, strategy backtesting")
    print("    Risk: None (virtual money, unlimited resets)")
    print("    Data: Real market prices, but trades don't affect real markets")
    print("    Perfect for: New developers, testing new strategies")

    print("\n  Environment.LIVE - Live trading (real money)")
    print("    URL: api-fxtrade.oanda.com")
    print("    Use for: Production trading with real capital")
    print("    Risk: Real capital at stake - you can lose money!")
    print("    Data: Real market prices, real execution")
    print("    Use only when: You've thoroughly tested in PRACTICE")

    print("\n⚠️  CRITICAL SAFETY RULES:")
    print("  - ALWAYS test in PRACTICE first")
    print("    (Test every strategy, every code change, every deployment)")
    print("  - Use separate tokens for practice/live")
    print("    (Different tokens = can't accidentally use wrong environment)")
    print("  - Double-check environment before trading")
    print("    (Add assertions: check client.config.environment == Environment.PRACTICE)")
    print("  - Start with small positions in live")
    print("    (Even after thorough testing, start with minimal risk)")
    print("  - Monitor closely when switching to live")
    print("    (Watch first few trades carefully)")

    print("\n💡 Pro Tip:")
    print("  Set a different env prefix for live:")
    print("    LIVE_FIVETWENTY_OANDA_* for production")
    print("    DEV_FIVETWENTY_OANDA_* for development")
    print("  This makes it harder to accidentally trade live")

    # Section 8: Configuration validation
    # ===================================
    # FiveTwenty validates configuration at startup to catch errors early
    # Better to fail fast with a clear error than to fail mid-trading
    print("\n=== 8. Configuration Validation ===")

    print("\nFiveTwenty validates configuration at runtime:")
    print("  - Happens when you create AsyncClient()")
    print("  - Fails fast with clear error messages")
    print("  - Prevents runtime errors during trading")
    print("  - Type-safe with Pydantic models")

    print("\nCommon Configuration Errors:")
    print("  ❌ Missing token")
    print("     Error: 'OANDA API token is required'")
    print("     Fix: Set FIVETWENTY_OANDA_TOKEN environment variable")

    print("\n  ❌ Missing account_id")
    print("     Error: 'OANDA account ID is required'")
    print("     Fix: Set FIVETWENTY_OANDA_ACCOUNT environment variable")

    print("\n  ❌ Invalid environment")
    print("     Error: 'Invalid environment value'")
    print("     Fix: Must be 'practice' or 'live' (case-insensitive)")

    print("\n  ❌ Invalid token format")
    print("     Error: 401 Unauthorized (from OANDA API)")
    print("     Fix: Check your token, regenerate if needed")

    print("\n✅ Validation occurs when creating AsyncClient")
    print("   - Errors are raised before any API calls")
    print("   - This is intentional - fail fast, not during trading")
    print("   - Much better than discovering issues mid-trade")

    # Section 9: Secure configuration practices
    # =========================================
    # Security is paramount when dealing with trading credentials
    # A compromised token means someone can trade with your account!
    print("\n=== 9. Secure Configuration ===")

    print("\nBest Practices:")
    print("  ✅ Use environment variables or secure vaults")
    print("     - Separates config from code")
    print("     - Easier to rotate credentials")
    print("     - Works well with CI/CD")

    print("  ✅ Never commit credentials to version control")
    print("     - Not even in private repos")
    print("     - Git history is permanent")
    print("     - Easy to accidentally leak")

    print("  ✅ Add .env to .gitignore")
    print("     - Prevents accidental commits")
    print("     - Add this FIRST, before adding .env file")

    print("  ✅ Use different tokens for different environments")
    print("     - Practice token ≠ Live token")
    print("     - Limits blast radius if compromised")
    print("     - Can revoke individually")

    print("  ✅ Rotate tokens periodically")
    print("     - Generate new token every 90 days")
    print("     - Revoke old token")
    print("     - Good security hygiene")

    print("  ✅ Use restrictive file permissions (chmod 600 .env)")
    print("     - Only your user can read the file")
    print("     - Prevents other users on system from reading")

    print("\n.gitignore patterns (add these!):")
    print("  .env              # Main environment file")
    print("  .env.*            # Any .env variants (.env.local, etc)")
    print("  config.json       # JSON config files")
    print("  config.yaml       # YAML config files")
    print("  *credentials*     # Anything with 'credentials' in name")
    print("  secrets/          # Directory containing secrets")

    print("\nAccountConfig automatically masks sensitive data:")
    # Demonstrate the masking behavior
    masked_config = AccountConfig(
        alias="demo",
        token=SecretStr("super-secret-token-12345"),
        account_id=SecretStr("123-456-7890123-001"),
        environment=Environment.PRACTICE,
    )
    print(f"  Token in repr: {masked_config!r}")
    print("  (Token is masked as '**********', not exposed in logs)")
    print("  This prevents accidental credential exposure in logs or error messages")

    # Section 10: Runtime configuration updates
    # =========================================
    # Sometimes you need to switch configuration while your application is running
    # This section shows safe patterns for doing so
    print("\n=== 10. Runtime Configuration Updates ===")

    print("\nSwitching configuration at runtime:")
    print("  - Close old client before opening new one")
    print("  - Or use multiple clients simultaneously")
    print("  - Each client is independent")

    print("\n1. Sequential: Close existing client before opening new:")
    print("  - Use separate 'async with' blocks")
    print("  - First client closes before second opens")
    print("  - All connections automatically cleaned up")

    print("\n2. Concurrent: Multiple simultaneous clients:")
    print("  - Both clients can be active at the same time")
    print("  - Each has its own connection pool")
    print("  - Useful for monitoring multiple accounts")
    print("  - Use multiple 'async with' contexts together")
    print("  - Use asyncio.gather() for concurrent operations")

    print("\n💡 Demo: Fetch account info with concurrent clients...")
    # Both clients active simultaneously
    async with AsyncClient() as client1, AsyncClient() as client2:
        # Can use both at the same time
        # These happen concurrently (not sequentially)
        balance1, balance2 = await asyncio.gather(client1.accounts.get_account_summary(client1.account_id), client2.accounts.get_account_summary(client2.account_id))

        print(f"✅ Client 1 balance: {balance1['account'].balance}")
        print(f"✅ Client 2 balance: {balance2['account'].balance}")

    print("\n💡 Use Cases for Multiple Clients:")
    print("  - Trading across multiple accounts")
    print("    (Portfolio diversification, different strategies)")
    print("  - Separate live and practice monitoring")
    print("    (Monitor production while testing in practice)")
    print("  - Different strategies with different configs")
    print("    (Strategy A on account 1, Strategy B on account 2)")
    print("  - Master/sub-account management")
    print("    (If you have multiple OANDA accounts)")

    print("\n⚠️  Resource Considerations:")
    print("  - Each client has its own HTTP connection pool")
    print("  - Multiple clients = more memory and connections")
    print("  - Typically not an issue for reasonable numbers (<10)")
    print("  - If monitoring many accounts, consider connection limits")

    print("\n✅ Configuration patterns example completed!")


if __name__ == "__main__":
    asyncio.run(main())
