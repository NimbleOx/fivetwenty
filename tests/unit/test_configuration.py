"""Tests for configuration management functionality."""

import os
from unittest.mock import patch

import pytest
from pydantic import ValidationError

from fivetwenty import AccountConfig, AccountConfigLoader, ConfigValidator, Environment


class TestAccountConfig:
    """Test AccountConfig model functionality."""

    def test_create_account_config(self):
        """Test creating a valid AccountConfig."""
        config = AccountConfig(token="test-token-123", account_id="123-456-789", environment=Environment.PRACTICE, alias="test_account")

        assert config.token.get_secret_value() == "test-token-123"
        assert config.account_id.get_secret_value() == "123-456-789"
        assert config.environment == Environment.PRACTICE
        assert config.alias == "test_account"

    def test_account_config_repr_masks_secrets(self):
        """Test that __repr__ masks sensitive information."""
        config = AccountConfig(token="test-token-123", account_id="123-456-789", environment=Environment.PRACTICE, alias="test_account")

        repr_str = repr(config)
        assert "test-token-123" not in repr_str
        assert "123-456-789" not in repr_str
        assert "***" in repr_str
        assert "test_account" in repr_str
        assert "practice" in repr_str

    def test_account_config_summary(self):
        """Test safe summary method."""
        config = AccountConfig(token="test-token-123", account_id="123-456-789", environment=Environment.LIVE, alias="production_account")

        summary = config.summary()
        assert summary == "production_account (live)"
        assert "test-token-123" not in summary
        assert "123-456-789" not in summary

    def test_alias_validation_valid(self):
        """Test that valid aliases are accepted."""
        valid_aliases = ["test_account", "account123", "myAccount", "a", "A123_test"]

        for alias in valid_aliases:
            config = AccountConfig(token="test-token", account_id="123-456-789", environment=Environment.PRACTICE, alias=alias)
            assert config.alias == alias

    def test_alias_validation_invalid(self):
        """Test that invalid aliases are rejected."""
        invalid_aliases = [
            "123_invalid",  # starts with number
            "test-account",  # contains dash
            "test account",  # contains space
            "",  # empty
            "test@account",  # contains special chars
        ]

        for alias in invalid_aliases:
            with pytest.raises(ValidationError):
                AccountConfig(token="test-token", account_id="123-456-789", environment=Environment.PRACTICE, alias=alias)

    def test_required_fields(self):
        """Test that required fields are validated."""
        with pytest.raises(ValidationError):
            AccountConfig()  # No required fields

        with pytest.raises(ValidationError):
            AccountConfig(token="test-token")  # Missing account_id, environment, alias


class TestConfigValidator:
    """Test ConfigValidator functionality."""

    def test_validate_valid_config(self):
        """Test validation of valid config returns no errors."""
        config = AccountConfig(token="test-token-123", account_id="123-456-789", environment=Environment.PRACTICE, alias="test_account")

        errors = ConfigValidator.validate_account_config(config)
        assert errors == []

    def test_validate_missing_token(self):
        """Test validation properly checks token content."""
        # Create a valid config first
        config = AccountConfig(token="valid-token", account_id="123-456-789", environment=Environment.PRACTICE, alias="test_account")

        # Test validator logic by creating a config with empty secret value
        from pydantic import SecretStr

        config.token = SecretStr("")

        errors = ConfigValidator.validate_account_config(config)
        assert "Token is required" in errors

    def test_validate_missing_account_id(self):
        """Test validation properly checks account_id content."""
        # Create a valid config first
        config = AccountConfig(token="test-token", account_id="valid-account-id", environment=Environment.PRACTICE, alias="test_account")

        # Test validator logic by creating a config with empty secret value
        from pydantic import SecretStr

        config.account_id = SecretStr("")

        errors = ConfigValidator.validate_account_config(config)
        assert "Account ID is required" in errors

    def test_validate_missing_alias(self):
        """Test validation fails for missing alias."""
        config = AccountConfig(
            token="test-token",
            account_id="123-456-789",
            environment=Environment.PRACTICE,
            alias="a",  # Valid but minimal alias
        )

        # Manually set alias to whitespace to test validator
        config.alias = "   "
        errors = ConfigValidator.validate_account_config(config)
        assert "Account alias is required" in errors

    def test_validate_multiple_errors(self):
        """Test validation returns multiple errors."""
        # Create a valid config first
        config = AccountConfig(token="valid-token", account_id="valid-account-id", environment=Environment.PRACTICE, alias="valid_alias")

        # Test validator logic by setting fields to empty
        from pydantic import SecretStr

        config.token = SecretStr("")
        config.account_id = SecretStr("")
        config.alias = ""

        errors = ConfigValidator.validate_account_config(config)
        assert len(errors) == 3
        assert "Token is required" in errors
        assert "Account ID is required" in errors
        assert "Account alias is required" in errors


class TestAccountConfigLoader:
    """Test AccountConfigLoader functionality."""

    def test_load_from_env_success(self):
        """Test successful loading from environment variables."""
        with patch.dict(os.environ, {"TEST_FIVETWENTY_OANDA_TOKEN": "test-token-123", "TEST_FIVETWENTY_OANDA_ACCOUNT": "123-456-789", "TEST_FIVETWENTY_OANDA_ENVIRONMENT": "practice"}):
            config = AccountConfigLoader.load_from_env("TEST_")

            assert config is not None
            assert config.token.get_secret_value() == "test-token-123"
            assert config.account_id.get_secret_value() == "123-456-789"
            assert config.environment == Environment.PRACTICE
            assert config.alias == "test"

    def test_load_from_env_missing_token(self):
        """Test loading fails when token is missing."""
        with patch.dict(os.environ, {"TEST_FIVETWENTY_OANDA_ACCOUNT": "123-456-789", "TEST_FIVETWENTY_OANDA_ENVIRONMENT": "practice"}, clear=True):
            config = AccountConfigLoader.load_from_env("TEST_")
            assert config is None

    def test_load_from_env_missing_account_id(self):
        """Test loading fails when account_id is missing."""
        with patch.dict(os.environ, {"TEST_FIVETWENTY_OANDA_TOKEN": "test-token-123", "TEST_FIVETWENTY_OANDA_ENVIRONMENT": "practice"}, clear=True):
            config = AccountConfigLoader.load_from_env("TEST_")
            assert config is None

    def test_load_from_env_defaults(self):
        """Test loading with default values for optional fields."""
        with patch.dict(os.environ, {"TEST_FIVETWENTY_OANDA_TOKEN": "test-token-123", "TEST_FIVETWENTY_OANDA_ACCOUNT": "123-456-789"}, clear=True):
            config = AccountConfigLoader.load_from_env("TEST_")

            assert config is not None
            assert config.token.get_secret_value() == "test-token-123"
            assert config.account_id.get_secret_value() == "123-456-789"
            assert config.environment == Environment.PRACTICE  # default
            assert config.alias == "test"  # generated from TEST_ prefix

    def test_load_from_env_live_environment(self):
        """Test loading with live environment."""
        with patch.dict(os.environ, {"TEST_FIVETWENTY_OANDA_TOKEN": "test-token-123", "TEST_FIVETWENTY_OANDA_ACCOUNT": "123-456-789", "TEST_FIVETWENTY_OANDA_ENVIRONMENT": "live"}, clear=True):
            config = AccountConfigLoader.load_from_env("TEST_")

            assert config is not None
            assert config.environment == Environment.LIVE
            assert config.alias == "test"

    def test_load_default(self):
        """Test loading default configuration."""
        with patch.dict(os.environ, {"FIVETWENTY_OANDA_TOKEN": "default-token", "FIVETWENTY_OANDA_ACCOUNT": "default-account-id", "FIVETWENTY_OANDA_ENVIRONMENT": "practice"}, clear=True):
            config = AccountConfigLoader.load_default()

            assert config is not None
            assert config.token.get_secret_value() == "default-token"
            assert config.account_id.get_secret_value() == "default-account-id"
            assert config.alias == "default"

    def test_load_default_missing(self):
        """Test loading default configuration when env vars are missing."""
        with patch.dict(os.environ, {}, clear=True):
            config = AccountConfigLoader.load_default()
            assert config is None

    def test_from_env_prefix(self):
        """Test loading with custom prefix."""
        with patch.dict(os.environ, {"CUSTOM_PREFIX_FIVETWENTY_OANDA_TOKEN": "custom-token", "CUSTOM_PREFIX_FIVETWENTY_OANDA_ACCOUNT": "custom-account-id", "CUSTOM_PREFIX_FIVETWENTY_OANDA_ENVIRONMENT": "live"}, clear=True):
            config = AccountConfigLoader.from_env_prefix("CUSTOM_PREFIX_")

            assert config is not None
            assert config.token.get_secret_value() == "custom-token"
            assert config.account_id.get_secret_value() == "custom-account-id"
            assert config.environment == Environment.LIVE
            assert config.alias == "custom_prefix"

    def test_empty_environment_vars(self):
        """Test that empty environment variables are treated as missing."""
        with patch.dict(
            os.environ,
            {
                "TEST_FIVETWENTY_OANDA_TOKEN": "",  # empty
                "TEST_FIVETWENTY_OANDA_ACCOUNT": "123-456-789",
                "TEST_FIVETWENTY_OANDA_ENVIRONMENT": "practice",
            },
            clear=True,
        ):
            config = AccountConfigLoader.load_from_env("TEST_")
            assert config is None

    def test_whitespace_environment_vars(self):
        """Test that whitespace-only environment variables are treated as missing."""
        with patch.dict(
            os.environ,
            {
                "TEST_FIVETWENTY_OANDA_TOKEN": "   ",  # whitespace only
                "TEST_FIVETWENTY_OANDA_ACCOUNT": "123-456-789",
                "TEST_FIVETWENTY_OANDA_ENVIRONMENT": "practice",
            },
            clear=True,
        ):
            config = AccountConfigLoader.load_from_env("TEST_")
            # Should return None since whitespace-only token is invalid
            assert config is None
