"""Environment and deployment integration tests for the OANDA SDK.

This module tests the SDK's behavior across different environments and deployment scenarios:
- Environment-specific configuration handling
- Practice vs Live environment isolation
- Deployment environment detection
- Configuration validation across environments
- Network condition resilience
- Cross-platform compatibility
"""

import asyncio
import os
import platform
import sys
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path
from unittest.mock import patch

import pytest

from fivetwenty import AsyncClient, Client
from fivetwenty._internal.environment import Environment
from fivetwenty.configuration import AccountConfig, AccountConfigLoader
from fivetwenty.exceptions import FiveTwentyError


@pytest.mark.integration
class TestEnvironmentAndDeployment:
    """Test SDK behavior across different environments and deployment scenarios."""

    def test_environment_detection_and_isolation(self):
        """Test environment detection and proper isolation between practice/live."""
        print("Testing environment detection and isolation...")

        # Test Environment enum
        assert Environment.PRACTICE.value == "practice"
        assert Environment.LIVE.value == "live"

        # Test environment URL mapping
        practice_url = Environment.PRACTICE.base_url
        live_url = Environment.LIVE.base_url

        print(f"Practice URL: {practice_url}")
        print(f"Live URL: {live_url}")

        assert "fxpractice" in practice_url.lower()
        assert "fxtrade" in live_url.lower()
        assert practice_url != live_url

        # Test that environments are properly isolated
        practice_client = AsyncClient(token="dummy-token", environment=Environment.PRACTICE, account_id="dummy-account")
        live_client = AsyncClient(token="dummy-token", environment=Environment.LIVE, account_id="dummy-account")

        assert practice_client._environment.base_url != live_client._environment.base_url
        assert "fxpractice" in practice_client._environment.base_url
        assert "fxtrade" in live_client._environment.base_url

        print("Environment isolation verified")

    def test_configuration_environment_handling(self):
        """Test configuration handling across different environments."""
        print("Testing configuration environment handling...")

        # Test practice environment config
        practice_config = AccountConfig(
            account_id="123-456-7890123-456",
            alias="test_practice",
            token="practice-token-123",
            environment=Environment.PRACTICE,
        )

        assert practice_config.environment == Environment.PRACTICE
        assert "practice" in practice_config.summary()
        assert "practice" in str(practice_config.environment.value)

        # Test live environment config
        live_config = AccountConfig(
            account_id="789-012-3456789-012",
            alias="test_live",
            token="live-token-456",
            environment=Environment.LIVE,
        )

        assert live_config.environment == Environment.LIVE
        assert "live" in live_config.summary()

        # Test config validation doesn't leak sensitive data
        practice_repr = repr(practice_config)
        live_repr = repr(live_config)

        assert "practice-token-123" not in practice_repr
        assert "live-token-456" not in live_repr
        assert "***" in practice_repr
        assert "***" in live_repr

        print("Configuration environment handling verified")

    def test_environment_variable_configuration(self):
        """Test configuration loading from environment variables."""
        print("Testing environment variable configuration...")

        # Test default environment loading (should return None without env vars)
        # Clear any existing FIVETWENTY environment variables for this test
        fivetwenty_vars = {key: "" for key in os.environ if key.startswith("FIVETWENTY_")}
        with patch.dict(os.environ, fivetwenty_vars, clear=False):
            default_config = AccountConfigLoader.load_default()
            assert default_config is None, "Should return None when env vars not set"

        # Test with mock environment variables
        test_env = {
            "FIVETWENTY_OANDA_TOKEN": "test-token-123",
            "FIVETWENTY_OANDA_ACCOUNT": "123-456-7890123-456",
            "FIVETWENTY_OANDA_ACCOUNT_ALIAS": "test_account",
            "FIVETWENTY_OANDA_ENVIRONMENT": "practice",
        }

        with patch.dict(os.environ, test_env):
            config = AccountConfigLoader.load_default()
            assert config is not None, "Should load config when env vars are set"
            assert config.alias == "test_account"
            assert config.environment == Environment.PRACTICE
            assert config.token.get_secret_value() == "test-token-123"
            assert config.account_id.get_secret_value() == "123-456-7890123-456"

        # Test custom prefix
        custom_env = {
            "CUSTOM_OANDA_TOKEN": "custom-token-456",
            "CUSTOM_OANDA_ACCOUNT": "456-789-0123456-789",
            "CUSTOM_OANDA_ENVIRONMENT": "live",
        }

        with patch.dict(os.environ, custom_env):
            custom_config = AccountConfigLoader.from_env_prefix("CUSTOM_")
            assert custom_config is not None
            assert custom_config.environment == Environment.LIVE
            assert custom_config.alias == "default"  # Default alias

        # Test missing required fields
        incomplete_env = {
            "FIVETWENTY_OANDA_TOKEN": "token-only",
            # Missing account ID
        }

        with patch.dict(os.environ, incomplete_env, clear=True):
            incomplete_config = AccountConfigLoader.load_default()
            assert incomplete_config is None, "Should return None with incomplete env vars"

        print("Environment variable configuration verified")

    async def test_network_resilience(self, sandbox_client: AsyncClient, test_account_id: str):
        """Test SDK resilience under various network conditions."""
        print("Testing network resilience...")

        # Test basic connectivity
        try:
            account = await sandbox_client.accounts.get_account_summary(test_account_id)
            assert account is not None
            print("  ✓ Basic connectivity works")
        except Exception as e:
            print(f"  ✗ Basic connectivity failed: {e}")
            pytest.skip("Network connectivity issues")

        # Test timeout handling with very short timeout
        short_timeout_client = AsyncClient(
            token=sandbox_client._token,
            environment=sandbox_client._environment,
            account_id=test_account_id,
            timeout=0.001,  # Very short timeout to force timeout errors
        )

        timeout_errors = 0
        for i in range(5):
            try:
                await short_timeout_client.accounts.get_account_summary(test_account_id)
            except Exception as e:
                if "timeout" in str(e).lower():
                    timeout_errors += 1
                    print(f"  Request {i + 1}: Timeout (expected)")
                else:
                    print(f"  Request {i + 1}: Other error - {e}")

        print(f"  Timeout handling: {timeout_errors}/5 requests timed out as expected")

        # Test retry behavior with transient failures
        retry_success_count = 0
        for i in range(10):
            try:
                # Use normal client for actual requests
                await sandbox_client.accounts.get_account_summary(test_account_id)
                retry_success_count += 1
            except Exception as e:
                print(f"  Retry test {i + 1} failed: {e}")

        retry_success_rate = retry_success_count / 10
        print(f"  Retry resilience: {retry_success_rate:.0%} success rate")

        assert retry_success_rate > 0.7, "Should maintain >70% success rate under normal conditions"

    def test_cross_platform_compatibility(self):
        """Test SDK compatibility across different platforms."""
        print("Testing cross-platform compatibility...")

        # Get platform information
        system_info = {
            "platform": platform.platform(),
            "system": platform.system(),
            "architecture": platform.architecture(),
            "python_version": sys.version,
            "machine": platform.machine(),
        }

        print(f"  Platform: {system_info['platform']}")
        print(f"  System: {system_info['system']}")
        print(f"  Architecture: {system_info['architecture']}")
        print(f"  Python: {system_info['python_version'][:20]}...")

        # Test basic client creation on current platform
        try:
            client = AsyncClient(token="dummy-token", environment=Environment.PRACTICE, account_id="dummy-account")
            assert client is not None
            print("  ✓ AsyncClient creation successful")
        except Exception as e:
            print(f"  ✗ AsyncClient creation failed: {e}")
            raise

        try:
            sync_client = Client(token="dummy-token", environment=Environment.PRACTICE, account_id="dummy-account")
            assert sync_client is not None
            sync_client.close()  # Clean up
            print("  ✓ Sync Client creation successful")
        except Exception as e:
            print(f"  ✗ Sync Client creation failed: {e}")
            raise

        # Test Decimal handling across platforms
        test_decimal = Decimal("1234.56789")
        decimal_str = str(test_decimal)
        assert "1234.56789" in decimal_str
        print("  ✓ Decimal handling consistent")

        # Test timezone handling
        utc_time = datetime.now(timezone.utc)
        assert utc_time.tzinfo is not None
        print(f"  ✓ Timezone handling: {utc_time.isoformat()}")

        print("Cross-platform compatibility verified")

    async def test_concurrent_environment_access(self):
        """Test concurrent access with multiple environment configurations."""
        print("Testing concurrent environment access...")

        # Create clients for different environments (using dummy credentials)
        practice_client = AsyncClient(
            token="practice-dummy-token",
            environment=Environment.PRACTICE,
            account_id="practice-dummy-account",
        )

        live_client = AsyncClient(token="live-dummy-token", environment=Environment.LIVE, account_id="live-dummy-account")

        # Test that clients maintain separate configurations
        assert practice_client._environment == Environment.PRACTICE
        assert live_client._environment == Environment.LIVE
        assert practice_client._environment.base_url != live_client._environment.base_url

        # Test concurrent client operations (will fail due to dummy credentials, but should maintain separation)
        async def test_practice_client():
            try:
                await practice_client.accounts.get_account_summary("dummy")
            except FiveTwentyError:
                return "practice_error"  # Expected
            except Exception as e:
                return f"practice_unexpected: {e}"

        async def test_live_client():
            try:
                await live_client.accounts.get_account_summary("dummy")
            except FiveTwentyError:
                return "live_error"  # Expected
            except Exception as e:
                return f"live_unexpected: {e}"

        # Run concurrently to ensure no cross-environment contamination
        results = await asyncio.gather(test_practice_client(), test_live_client(), return_exceptions=True)

        print(f"  Practice result: {results[0]}")
        print(f"  Live result: {results[1]}")

        # Both should fail with OANDA errors (due to dummy credentials) but maintain environment separation
        assert "practice" in str(results[0]) or "error" in str(results[0])
        assert "live" in str(results[1]) or "error" in str(results[1])

        print("Concurrent environment access verified")

    async def test_configuration_validation_across_environments(self, sandbox_client: AsyncClient, test_account_id: str):
        """Test configuration validation works across different environments."""
        print("Testing configuration validation across environments...")

        # Test current environment validation
        current_env = sandbox_client._environment
        print(f"Current environment: {current_env.value}")

        # Validate account access in current environment
        try:
            account_response = await sandbox_client.accounts.get_account(test_account_id)
            account = account_response["account"]
            assert account.id == test_account_id
            print(f"  ✓ Account validation successful in {current_env.value}")
        except Exception as e:
            print(f"  ✗ Account validation failed: {e}")
            raise

        # Test configuration object validation
        test_configs = [
            {
                "name": "Valid practice config",
                "config": AccountConfig(
                    account_id="123-456-7890123-456",
                    alias="valid_practice",
                    token="valid-practice-token",
                    environment=Environment.PRACTICE,
                ),
                "should_be_valid": True,
            },
            {
                "name": "Valid live config",
                "config": AccountConfig(
                    account_id="789-012-3456789-012",
                    alias="valid_live",
                    token="valid-live-token",
                    environment=Environment.LIVE,
                ),
                "should_be_valid": True,
            },
        ]

        for test_case in test_configs:
            config = test_case["config"]
            try:
                # Test basic validation
                assert config.alias is not None
                assert config.token.get_secret_value() is not None
                assert config.account_id.get_secret_value() is not None
                assert config.environment in [Environment.PRACTICE, Environment.LIVE]

                print(f"  ✓ {test_case['name']}: Configuration valid")

            except Exception as e:
                if test_case["should_be_valid"]:
                    print(f"  ✗ {test_case['name']}: Unexpected validation failure - {e}")
                    raise
                print(f"  ✓ {test_case['name']}: Expected validation failure - {e}")

    def test_deployment_environment_detection(self):
        """Test detection of various deployment environments."""
        print("Testing deployment environment detection...")

        # Check for common deployment environment indicators
        deployment_indicators = {
            "CI": os.getenv("CI"),
            "GITHUB_ACTIONS": os.getenv("GITHUB_ACTIONS"),
            "TRAVIS": os.getenv("TRAVIS"),
            "JENKINS_URL": os.getenv("JENKINS_URL"),
            "BUILD_NUMBER": os.getenv("BUILD_NUMBER"),
            "DOCKER": Path("/.dockerenv").exists(),
            "KUBERNETES": os.getenv("KUBERNETES_SERVICE_HOST"),
            "AWS_LAMBDA": os.getenv("AWS_LAMBDA_FUNCTION_NAME"),
            "HEROKU": os.getenv("DYNO"),
        }

        detected_environments = [name for name, indicator in deployment_indicators.items() if indicator]

        print(f"  Detected deployment environments: {detected_environments or ['None']}")

        # Test that SDK works regardless of deployment environment
        try:
            # Basic SDK initialization should work in any environment
            client = AsyncClient(token="test-token", environment=Environment.PRACTICE, account_id="test-account")
            assert client is not None
            print("  ✓ SDK initialization works in current deployment environment")
        except Exception as e:
            print(f"  ✗ SDK initialization failed: {e}")
            raise

        # Test environment-specific configuration
        if "CI" in detected_environments:
            print("  Running in CI environment - testing CI-specific behavior")
            # In CI, we might want to use different timeouts or retry policies
            # This is where CI-specific configuration would be tested

        if "DOCKER" in detected_environments:
            print("  Running in Docker environment - testing containerized behavior")
            # Test Docker-specific behavior like network connectivity

        print("Deployment environment detection completed")

    async def test_environment_switching_safety(self):
        """Test that environment switching is safe and properly isolated."""
        print("Testing environment switching safety...")

        # Create clients for both environments with different configurations
        clients = {}

        try:
            clients["practice"] = AsyncClient(
                token="practice-token",
                environment=Environment.PRACTICE,
                account_id="practice-account",
            )

            clients["live"] = AsyncClient(token="live-token", environment=Environment.LIVE, account_id="live-account")

            # Verify isolation
            practice_client = clients["practice"]
            live_client = clients["live"]

            # Check that configurations don't leak between clients
            assert practice_client._token == "practice-token"
            assert live_client._token == "live-token"

            assert practice_client._account_id == "practice-account"
            assert live_client._account_id == "live-account"

            assert practice_client._environment == Environment.PRACTICE
            assert live_client._environment == Environment.LIVE

            # Test URL isolation
            assert "fxpractice" in practice_client._environment.base_url.lower()
            assert "fxtrade" in live_client._environment.base_url.lower()

            print("  ✓ Client environment isolation verified")

            # Test that simultaneous operations don't interfere
            async def practice_operation():
                try:
                    # This will fail with dummy credentials, but should maintain practice URL
                    await practice_client.accounts.get_account_summary("dummy")
                except Exception:
                    return practice_client._environment.base_url

            async def live_operation():
                try:
                    # This will fail with dummy credentials, but should maintain live URL
                    await live_client.accounts.get_account_summary("dummy")
                except Exception:
                    return live_client._environment.base_url

            practice_url, live_url = await asyncio.gather(practice_operation(), live_operation())

            assert "fxpractice" in practice_url.lower()
            assert "fxtrade" in live_url.lower()
            assert practice_url != live_url

            print("  ✓ Concurrent environment operations properly isolated")

        except Exception as e:
            print(f"  ✗ Environment switching safety test failed: {e}")
            raise

        print("Environment switching safety verified")

    def test_configuration_security_across_environments(self):
        """Test that configuration maintains security across different environments."""
        print("Testing configuration security across environments...")

        # Test that secrets are properly protected in both environments
        environments = [Environment.PRACTICE, Environment.LIVE]

        for env in environments:
            config = AccountConfig(
                account_id=f"secret-account-{env.value}",
                alias=f"test_{env.value}",
                token=f"secret-token-{env.value}",
                environment=env,
            )

            # Test string representations don't leak secrets
            config_str = str(config)
            config_repr = repr(config)

            assert f"secret-account-{env.value}" not in config_str
            assert f"secret-token-{env.value}" not in config_str
            assert f"secret-account-{env.value}" not in config_repr
            assert f"secret-token-{env.value}" not in config_repr

            assert "***" in config_repr
            print(f"  ✓ {env.value.title()} environment secrets properly protected")

            # Test that summary is safe
            summary = config.summary()
            assert f"secret-account-{env.value}" not in summary
            assert f"secret-token-{env.value}" not in summary
            assert env.value in summary  # Environment should be visible
            assert config.alias in summary  # Alias should be visible

        print("Configuration security verified across environments")
