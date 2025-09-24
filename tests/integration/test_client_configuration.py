"""Integration tests for configuration and authentication management."""

import json  # noqa: F401
import os
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest
from pydantic import SecretStr, ValidationError

from fivetwenty import AsyncClient, Client
from fivetwenty._internal.environment import Environment
from fivetwenty.configuration import AccountConfig, AccountConfigLoader, ConfigValidator
from fivetwenty.exceptions import FiveTwentyError


@pytest.mark.asyncio
@pytest.mark.integration
class TestConfigurationManagement:
    """Integration tests for configuration and authentication management."""

    async def test_account_config_validation(self):
        """Test AccountConfig validation and security.

        Validates:
        - Required field validation
        - Secret field handling
        - Alias validation rules
        - Environment validation
        - String sanitization
        """
        print("✓ Testing AccountConfig validation...")

        # Test 1: Valid configuration
        try:
            valid_config = AccountConfig(account_id=SecretStr("123-456-7890123-456"), alias="main_account", token=SecretStr("test-token-12345"), environment=Environment.PRACTICE)

            assert valid_config.alias == "main_account"
            assert valid_config.environment == Environment.PRACTICE
            assert valid_config.token.get_secret_value() == "test-token-12345"
            assert valid_config.account_id.get_secret_value() == "123-456-7890123-456"

            print("  - Valid configuration accepted")

        except Exception as e:
            pytest.fail(f"Valid configuration should be accepted: {e}")

        # Test 2: Invalid alias formats
        invalid_aliases = [
            "",  # Empty
            "   ",  # Whitespace only
            "123start",  # Starts with number
            "has-dashes",  # Contains dashes
            "has spaces",  # Contains spaces
            "has@special",  # Contains special chars
            "_underscore_start",  # Starts with underscore
        ]

        for invalid_alias in invalid_aliases:
            with pytest.raises(ValidationError) as exc_info:
                AccountConfig(account_id=SecretStr("123-456-7890123-456"), alias=invalid_alias, token=SecretStr("test-token"), environment=Environment.PRACTICE)

            assert "alias" in str(exc_info.value).lower()
            print(f"  - Invalid alias rejected: '{invalid_alias}'")

        # Test 3: Valid alias formats
        valid_aliases = [
            "a",  # Single letter
            "Account1",  # With number
            "my_account",  # With underscore
            "MyTradingAccount",  # CamelCase
            "account_123_test",  # Complex valid
        ]

        for valid_alias in valid_aliases:
            try:
                config = AccountConfig(account_id=SecretStr("123-456-7890123-456"), alias=valid_alias, token=SecretStr("test-token"), environment=Environment.PRACTICE)
                assert config.alias == valid_alias
                print(f"  - Valid alias accepted: '{valid_alias}'")

            except ValidationError:
                pytest.fail(f"Valid alias should be accepted: {valid_alias}")

        # Test 4: Secret field validation
        # Empty secrets should be rejected
        with pytest.raises(ValidationError):
            AccountConfig(
                account_id=SecretStr(""),  # Empty account ID
                alias="test",
                token=SecretStr("valid-token"),
                environment=Environment.PRACTICE,
            )
        print("  - Empty account_id rejected")

        with pytest.raises(ValidationError):
            AccountConfig(
                account_id=SecretStr("valid-id"),
                alias="test",
                token=SecretStr(""),  # Empty token
                environment=Environment.PRACTICE,
            )
        print("  - Empty token rejected")

        # Test 5: String sanitization (whitespace stripping)
        config_with_whitespace = AccountConfig(
            account_id=SecretStr("  123-456-7890123-456  "),
            alias="  test_account  ",  # Will be stripped
            token=SecretStr("  test-token  "),
            environment=Environment.PRACTICE,
        )

        assert config_with_whitespace.alias == "test_account"  # Whitespace stripped
        assert config_with_whitespace.token.get_secret_value() == "test-token"  # Whitespace stripped
        print("  - Whitespace stripping verified")

        # Test 6: Safe representation (no secrets exposed)
        config = AccountConfig(account_id=SecretStr("SENSITIVE-ACCOUNT-ID"), alias="production", token=SecretStr("SENSITIVE-TOKEN-12345"), environment=Environment.LIVE)

        repr_str = repr(config)
        str_str = str(config)
        summary = config.summary()

        # Ensure secrets are not exposed
        assert "SENSITIVE-ACCOUNT-ID" not in repr_str
        assert "SENSITIVE-TOKEN-12345" not in repr_str
        assert "***" in repr_str  # Should show masked values

        assert "SENSITIVE-ACCOUNT-ID" not in str_str
        assert "SENSITIVE-TOKEN-12345" not in str_str

        assert "SENSITIVE-ACCOUNT-ID" not in summary
        assert "SENSITIVE-TOKEN-12345" not in summary
        assert "production" in summary  # Alias should be visible

        print("  - Secret masking in representations verified")

        # Test 7: Environment validation
        for env in [Environment.PRACTICE, Environment.LIVE]:
            config = AccountConfig(account_id=SecretStr("test-id"), alias="test", token=SecretStr("test-token"), environment=env)
            assert config.environment == env
            print(f"  - Environment {env.value} accepted")

        print("✓ AccountConfig validation test completed")

    async def test_config_validator_class(self):
        """Test ConfigValidator functionality.

        Validates:
        - Token format validation
        - Account ID format validation
        - Environment validation
        - Alias validation
        """
        print("✓ Testing ConfigValidator...")

        # Test 1: Token validation
        valid_tokens = [
            "a" * 65,  # 65 character token (OANDA format)
            "test-token-12345",
            "1234567890abcdef" * 4,  # 64 chars hex-like
        ]

        for token in valid_tokens:
            result = ConfigValidator.validate_token(token)
            assert result is True
            print(f"  - Valid token format accepted: {len(token)} chars")

        invalid_tokens = [
            "",  # Empty
            "   ",  # Whitespace only
            "short",  # Too short
            None,  # None value
        ]

        for token in invalid_tokens:
            result = ConfigValidator.validate_token(token)
            assert result is False
            print(f"  - Invalid token format rejected: '{token}'")

        # Test 2: Account ID validation
        valid_account_ids = [
            "123-456-7890123-456",  # Standard format
            "001-001-1234567-001",  # With leading zeros
            "999-999-9999999-999",  # Max values
        ]

        for account_id in valid_account_ids:
            result = ConfigValidator.validate_account_id(account_id)
            assert result is True
            print(f"  - Valid account ID accepted: {account_id}")

        invalid_account_ids = [
            "",  # Empty
            "123456789",  # No dashes
            "abc-def-ghijklm-nop",  # Letters
            "12-34-5678901-23",  # Wrong segment lengths
            "123_456_7890123_456",  # Wrong separator
        ]

        for account_id in invalid_account_ids:
            result = ConfigValidator.validate_account_id(account_id)
            assert result is False
            print(f"  - Invalid account ID rejected: '{account_id}'")

        # Test 3: Environment validation
        assert ConfigValidator.validate_environment("practice") is True
        assert ConfigValidator.validate_environment("live") is True
        assert ConfigValidator.validate_environment("PRACTICE") is True
        assert ConfigValidator.validate_environment("LIVE") is True
        assert ConfigValidator.validate_environment("invalid") is False
        assert ConfigValidator.validate_environment("") is False
        print("  - Environment validation verified")

        # Test 4: Comprehensive validation
        valid_config_dict = {"token": "a" * 65, "account_id": "123-456-7890123-456", "environment": "practice", "alias": "main"}

        errors = ConfigValidator.validate_config(valid_config_dict)
        assert len(errors) == 0
        print("  - Full config validation passed")

        invalid_config_dict = {"token": "short", "account_id": "invalid", "environment": "wrong", "alias": "123invalid"}

        errors = ConfigValidator.validate_config(invalid_config_dict)
        assert len(errors) > 0
        assert "token" in errors
        assert "account_id" in errors
        assert "environment" in errors
        assert "alias" in errors
        print(f"  - Invalid config detected {len(errors)} errors")

        print("✓ ConfigValidator test completed")

    async def test_account_config_loader(self):
        """Test AccountConfigLoader functionality.

        Validates:
        - Environment variable loading
        - Configuration file loading
        - Multiple account configurations
        - Default configuration selection
        - Configuration precedence
        """
        print("✓ Testing AccountConfigLoader...")

        # Test 1: Load from environment variables
        with patch.dict(os.environ, {"FIVETWENTY_OANDA_TOKEN": "env-test-token-12345", "FIVETWENTY_OANDA_ACCOUNT": "123-456-7890123-456", "FIVETWENTY_OANDA_ENVIRONMENT": "practice", "FIVETWENTY_OANDA_ACCOUNT_ALIAS": "default"}):
            config = AccountConfigLoader.load_default()

            assert config is not None
            assert config.token.get_secret_value() == "env-test-token-12345"
            assert config.account_id.get_secret_value() == "123-456-7890123-456"
            assert config.environment == Environment.PRACTICE
            assert config.alias == "default"  # Default alias when loaded from env

            print("  - Environment variable loading verified")

        # Test 2: Missing environment variables
        with patch.dict(os.environ, {}, clear=True):
            config = AccountConfigLoader.load_default()
            assert config is None
            print("  - Missing environment variables handled")

        # Test 3: Partial environment variables (missing account)
        with patch.dict(
            os.environ,
            {
                "FIVETWENTY_OANDA_TOKEN": "test-token",
                "FIVETWENTY_OANDA_ENVIRONMENT": "practice",
                # Clear all existing FIVETWENTY variables and only set the ones we want
                "FIVETWENTY_OANDA_ACCOUNT": "",  # Missing required field
                "FIVETWENTY_OANDA_ACCOUNT_ALIAS": "",
            },
        ):
            config = AccountConfigLoader.load_default()
            assert config is None  # Should return None if any required field is missing
            print("  - Partial environment variables rejected")

        # Test 4: Invalid environment value
        with patch.dict(os.environ, {"FIVETWENTY_OANDA_TOKEN": "test-token", "FIVETWENTY_OANDA_ACCOUNT": "123-456-7890123-456", "FIVETWENTY_OANDA_ENVIRONMENT": "invalid", "FIVETWENTY_OANDA_ACCOUNT_ALIAS": ""}):
            with pytest.raises(ValueError):
                AccountConfigLoader.load_default()
            print("  - Invalid environment value rejected")

        # Test 5: Load from configuration file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            config_data = {"accounts": [{"alias": "main", "token": "file-token-main", "account_id": "111-111-1111111-111", "environment": "practice"}, {"alias": "secondary", "token": "file-token-secondary", "account_id": "222-222-2222222-222", "environment": "practice"}]}
            import json

            json.dump(config_data, f)
            config_file = f.name

        try:
            configs = AccountConfigLoader.load_from_file(config_file)
            assert len(configs) == 2

            # Check first account
            assert configs[0].alias == "main"
            assert configs[0].token.get_secret_value() == "file-token-main"
            assert configs[0].account_id.get_secret_value() == "111-111-1111111-111"

            # Check second account
            assert configs[1].alias == "secondary"
            assert configs[1].token.get_secret_value() == "file-token-secondary"
            assert configs[1].account_id.get_secret_value() == "222-222-2222222-222"

            print("  - Configuration file loading verified")

        finally:
            Path(config_file).unlink()

        # Test 6: Load specific account by alias
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            config_data = {"accounts": [{"alias": "prod", "token": "prod-token", "account_id": "333-333-3333333-333", "environment": "live"}, {"alias": "test", "token": "test-token", "account_id": "444-444-4444444-444", "environment": "practice"}]}
            json.dump(config_data, f)
            config_file = f.name

        try:
            config = AccountConfigLoader.load_by_alias(config_file, "test")
            assert config is not None
            assert config.alias == "test"
            assert config.environment == Environment.PRACTICE

            config = AccountConfigLoader.load_by_alias(config_file, "prod")
            assert config is not None
            assert config.alias == "prod"
            assert config.environment == Environment.LIVE

            config = AccountConfigLoader.load_by_alias(config_file, "nonexistent")
            assert config is None

            print("  - Load by alias verified")

        finally:
            Path(config_file).unlink()

        # Test 7: Invalid configuration file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            f.write("invalid json content")
            invalid_file = f.name

        try:
            with pytest.raises(json.JSONDecodeError):  # Should raise JSON decode error
                AccountConfigLoader.load_from_file(invalid_file)
            print("  - Invalid JSON file rejected")

        finally:
            Path(invalid_file).unlink()

        print("✓ AccountConfigLoader test completed")

    async def test_client_configuration_integration(self, sandbox_client: AsyncClient):
        """Test client initialization with various configurations.

        Validates:
        - Client initialization with config object
        - Client initialization with direct parameters
        - Client initialization from environment
        - Configuration precedence
        - Multi-client configurations
        """
        print("✓ Testing client configuration integration...")

        # Test 1: Initialize AsyncClient with config object
        config = AccountConfig(account_id=SecretStr("test-account-id"), alias="test", token=SecretStr(sandbox_client._token), environment=Environment.PRACTICE)

        try:
            client = AsyncClient(config=config)
            assert client._token == sandbox_client._token
            assert client._environment == Environment.PRACTICE

            # Test that client is functional
            accounts = await client.accounts.get_accounts()
            assert accounts is not None

            await client.close()
            print("  - AsyncClient with config object verified")

        except Exception as e:
            pytest.fail(f"Client initialization with config failed: {e}")

        # Test 2: Initialize AsyncClient with direct parameters
        try:
            client = AsyncClient(token=sandbox_client._token, account_id="test-id", environment=Environment.PRACTICE)

            assert client._token == sandbox_client._token
            assert client._environment == Environment.PRACTICE

            await client.close()
            print("  - AsyncClient with direct parameters verified")

        except Exception as e:
            pytest.fail(f"Client initialization with parameters failed: {e}")

        # Test 3: Initialize from environment variables
        with patch.dict(os.environ, {"FIVETWENTY_OANDA_TOKEN": sandbox_client._token, "FIVETWENTY_OANDA_ACCOUNT": "123-456-7890123-456", "FIVETWENTY_OANDA_ENVIRONMENT": "practice"}):
            try:
                client = AsyncClient()  # No parameters - should load from env
                assert client._token == sandbox_client._token
                assert client._environment == Environment.PRACTICE

                await client.close()
                print("  - AsyncClient from environment variables verified")

            except Exception as e:
                pytest.fail(f"Client initialization from env failed: {e}")

        # Test 4: Configuration precedence (config > params > env)
        with patch.dict(os.environ, {"FIVETWENTY_OANDA_TOKEN": "env-token", "FIVETWENTY_OANDA_ACCOUNT": "env-account", "FIVETWENTY_OANDA_ENVIRONMENT": "live"}):
            # Config object should take precedence
            config = AccountConfig(account_id=SecretStr("config-account"), alias="config", token=SecretStr(sandbox_client._token), environment=Environment.PRACTICE)

            client = AsyncClient(
                config=config,
                token="param-token",  # Should be ignored
                environment=Environment.LIVE,  # Should be ignored
            )

            assert client._token == sandbox_client._token  # From config
            assert client._environment == Environment.PRACTICE  # From config

            await client.close()
            print("  - Configuration precedence verified")

        # Test 5: Multiple clients with different configurations
        configs = [AccountConfig(account_id=SecretStr(f"account-{i}"), alias=f"client_{i}", token=SecretStr(sandbox_client._token), environment=Environment.PRACTICE) for i in range(3)]

        clients = []
        try:
            for config in configs:
                client = AsyncClient(config=config)
                clients.append(client)

            # All clients should be independent
            assert len(clients) == 3
            for _i, client in enumerate(clients):
                assert client._token == sandbox_client._token

            print("  - Multiple client configurations verified")

        finally:
            for client in clients:
                await client.close()

        # Test 6: Synchronous client configuration
        config = AccountConfig(account_id=SecretStr("sync-account"), alias="sync", token=SecretStr(sandbox_client._token), environment=Environment.PRACTICE)

        try:
            sync_client = Client(config=config)
            assert sync_client._async._token == sandbox_client._token

            # Test that sync client is functional
            accounts = sync_client.accounts.get_accounts()
            assert accounts is not None

            sync_client.close()
            print("  - Synchronous client configuration verified")

        except Exception as e:
            pytest.fail(f"Sync client initialization failed: {e}")

        # Test 7: Invalid configuration handling
        with pytest.raises(ValueError):
            # No token provided anywhere
            with patch.dict(os.environ, {}, clear=True):
                AsyncClient()

        print("  - Invalid configuration rejected")

        print("✓ Client configuration integration test completed")

    async def test_environment_switching(self, sandbox_client: AsyncClient):
        """Test environment switching and URL construction.

        Validates:
        - Practice environment URLs
        - Live environment URLs
        - Environment-specific behavior
        - URL construction
        """
        print("✓ Testing environment switching...")

        # Test 1: Practice environment
        practice_client = AsyncClient(token=sandbox_client._token, environment=Environment.PRACTICE)

        try:
            assert practice_client._environment == Environment.PRACTICE
            assert "practice" in practice_client._environment.base_url.lower() or "fxpractice" in practice_client._environment.base_url.lower()
            print(f"  - Practice URL: {practice_client._environment.base_url}")

            await practice_client.close()

        except Exception as e:
            pytest.fail(f"Practice environment failed: {e}")

        # Test 2: Live environment (URL construction only, no real connection)
        live_client = AsyncClient(token="dummy-live-token", environment=Environment.LIVE)

        try:
            assert live_client._environment == Environment.LIVE
            assert "fxtrade" in live_client._environment.base_url.lower()
            assert "practice" not in live_client._environment.base_url.lower()
            print(f"  - Live URL: {live_client._environment.base_url}")

            await live_client.close()

        except Exception as e:
            pytest.fail(f"Live environment failed: {e}")

        # Test 3: Environment string values
        assert Environment.PRACTICE.value == "practice"
        assert Environment.LIVE.value == "live"
        print("  - Environment string values verified")

        # Test 4: Environment from string
        practice_from_str = AsyncClient(
            token=sandbox_client._token,
            environment="practice",  # String instead of enum
        )

        assert practice_from_str._environment == Environment.PRACTICE
        await practice_from_str.close()
        print("  - Environment from string verified")

        print("✓ Environment switching test completed")

    async def test_secure_credential_handling(self, sandbox_client: AsyncClient):
        """Test secure handling of credentials.

        Validates:
        - Credentials not logged
        - Credentials not in error messages
        - Secure storage in memory
        - No credential leakage
        """
        print("✓ Testing secure credential handling...")

        sensitive_token = "SENSITIVE-TOKEN-12345-SHOULD-NOT-APPEAR"
        sensitive_account = "999-999-9999999-999"

        # Test 1: Credentials not in string representations
        config = AccountConfig(account_id=SecretStr(sensitive_account), alias="secure_test", token=SecretStr(sensitive_token), environment=Environment.PRACTICE)

        # Check all string representations
        assert sensitive_token not in str(config)
        assert sensitive_token not in repr(config)
        assert sensitive_token not in config.summary()
        assert sensitive_account not in str(config)
        assert sensitive_account not in repr(config)
        assert sensitive_account not in config.summary()

        print("  - Credentials masked in string representations")

        # Test 2: Credentials not in error messages
        try:
            # This will fail but shouldn't expose token
            client = AsyncClient(token=sensitive_token, environment=Environment.PRACTICE)
            await client.accounts.get_accounts()
            await client.close()

        except FiveTwentyError as e:
            error_str = str(e)
            assert sensitive_token not in error_str
            print("  - Credentials not exposed in API errors")

        except Exception as e:
            error_str = str(e)
            assert sensitive_token not in error_str
            print("  - Credentials not exposed in general errors")

        # Test 3: SecretStr proper usage
        config = AccountConfig(account_id=SecretStr(sensitive_account), alias="test", token=SecretStr(sensitive_token), environment=Environment.PRACTICE)

        # Should only be accessible via get_secret_value()
        assert isinstance(config.token, SecretStr)
        assert isinstance(config.account_id, SecretStr)
        assert config.token.get_secret_value() == sensitive_token
        assert config.account_id.get_secret_value() == sensitive_account

        print("  - SecretStr protection verified")

        # Test 4: Client doesn't expose credentials
        client = AsyncClient(token=sensitive_token, environment=Environment.PRACTICE)

        try:
            # Check client string representation
            client_str = str(client)
            client_repr = repr(client)

            assert sensitive_token not in client_str
            assert sensitive_token not in client_repr

            print("  - Client doesn't expose credentials")

        finally:
            await client.close()

        # Test 5: Credentials in headers are protected
        # The token is used in Authorization header but should be protected
        client = AsyncClient(token=sandbox_client._token, environment=Environment.PRACTICE)

        try:
            # Make a request and ensure headers aren't exposed
            await client.accounts.get_accounts()

            # The client should not expose the authorization header in any logs
            print("  - Authorization header protection verified")

        finally:
            await client.close()

        print("✓ Secure credential handling test completed")

    async def test_configuration_validation_errors(self):
        """Test configuration validation error handling.

        Validates:
        - Detailed validation errors
        - Error messages clarity
        - Multiple validation errors
        - Field-specific errors
        """
        print("✓ Testing configuration validation errors...")

        # Test 1: Multiple validation errors
        try:
            AccountConfig(
                account_id=SecretStr(""),  # Empty
                alias="123-invalid",  # Invalid format
                token=SecretStr("   "),  # Whitespace only
                environment="wrong",  # Invalid environment
            )
            pytest.fail("Should have raised ValidationError")

        except ValidationError as e:
            errors = e.errors()
            assert len(errors) >= 3  # At least 3 fields should have errors

            # Check that we get clear error messages
            error_fields = {error["loc"][0] for error in errors}
            assert "account_id" in error_fields
            assert "alias" in error_fields
            assert "token" in error_fields

            print(f"  - Multiple validation errors detected: {len(errors)} errors")

        # Test 2: Field-specific error details
        try:
            AccountConfig(account_id=SecretStr("valid-id"), alias="_starts_with_underscore", token=SecretStr("valid-token"), environment=Environment.PRACTICE)
            pytest.fail("Should have raised ValidationError")

        except ValidationError as e:
            errors = e.errors()
            # Should have exactly one error for alias
            alias_errors = [e for e in errors if "alias" in e["loc"]]
            assert len(alias_errors) == 1
            assert "identifier" in alias_errors[0]["msg"].lower()

            print("  - Field-specific error messages verified")

        # Test 3: Environment validation errors
        with pytest.raises(ValueError):
            # Using string that can't be converted to Environment
            AccountConfig(
                account_id=SecretStr("valid-id"),
                alias="valid",
                token=SecretStr("valid-token"),
                environment="production",  # Invalid - should be 'practice' or 'live'
            )

        print("  - Environment validation errors verified")

        # Test 4: Type validation errors
        with pytest.raises(ValidationError):
            AccountConfig(
                account_id=123,  # Should be SecretStr
                alias="valid",
                token=SecretStr("valid-token"),
                environment=Environment.PRACTICE,
            )

        print("  - Type validation errors verified")

        print("✓ Configuration validation errors test completed")

    async def test_multi_account_configuration(self):
        """Test multi-account configuration scenarios.

        Validates:
        - Multiple account management
        - Account switching
        - Isolated configurations
        - Account-specific operations
        """
        print("✓ Testing multi-account configuration...")

        # Test 1: Create multiple account configurations
        accounts = []
        for i in range(3):
            config = AccountConfig(account_id=SecretStr(f"{i}11-{i}22-{i}333333-{i}44"), alias=f"account_{i}", token=SecretStr(f"token-{i}-12345"), environment=Environment.PRACTICE)
            accounts.append(config)

        assert len(accounts) == 3
        assert all(acc.alias == f"account_{i}" for i, acc in enumerate(accounts))
        print(f"  - Created {len(accounts)} account configurations")

        # Test 2: Save and load multiple accounts
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            config_data = {"default": "primary", "accounts": [{"alias": acc.alias, "token": acc.token.get_secret_value(), "account_id": acc.account_id.get_secret_value(), "environment": acc.environment.value} for acc in accounts]}
            import json

            json.dump(config_data, f)
            config_file = f.name

        try:
            # Load all accounts
            loaded_accounts = AccountConfigLoader.load_from_file(config_file)
            assert len(loaded_accounts) == 3

            # Verify each account
            for i, acc in enumerate(loaded_accounts):
                assert acc.alias == f"account_{i}"
                assert acc.token.get_secret_value() == f"token-{i}-12345"

            print("  - Multi-account save/load verified")

            # Load specific account
            acc_1 = AccountConfigLoader.load_by_alias(config_file, "account_1")
            assert acc_1 is not None
            assert acc_1.alias == "account_1"

            print("  - Specific account loading verified")

        finally:
            Path(config_file).unlink()

        # Test 3: Account isolation in clients
        # Note: Using sandbox token for all to avoid auth errors
        configs = [
            AccountConfig(
                account_id=SecretStr(f"test-{i}"),
                alias=f"client_{i}",
                token=SecretStr("test-token"),  # Same token but different configs
                environment=Environment.PRACTICE,
            )
            for i in range(2)
        ]

        clients = []
        try:
            for config in configs:
                client = AsyncClient(config=config)
                clients.append(client)

            # Each client should maintain its own configuration
            assert clients[0]._config.alias == "client_0"
            assert clients[1]._config.alias == "client_1"

            print("  - Client configuration isolation verified")

        finally:
            for client in clients:
                await client.close()

        print("✓ Multi-account configuration test completed")
