"""Tests for configuration management functionality."""

import json
import os
from unittest.mock import patch

import pytest
from pydantic import SecretStr, ValidationError

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

        config.token = SecretStr("")

        errors = ConfigValidator.validate_account_config(config)
        assert "Token is required" in errors

    def test_validate_missing_account_id(self):
        """Test validation properly checks account_id content."""
        # Create a valid config first
        config = AccountConfig(token="test-token", account_id="valid-account-id", environment=Environment.PRACTICE, alias="test_account")

        # Test validator logic by creating a config with empty secret value

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


class _RaisingSecret:
    """Truthy stand-in for SecretStr whose accessor always raises."""

    def get_secret_value(self) -> str:
        raise RuntimeError("secret unavailable")


class TestConfigValidatorAccountConfigExceptionPaths:
    """Test validate_account_config when secret accessors raise."""

    def _valid_config(self):
        return AccountConfig(token="valid-token", account_id="123-456-789", environment=Environment.PRACTICE, alias="valid_alias")

    def test_token_accessor_exception_reports_token_required(self):
        """Test that a raising token accessor is reported as a missing token."""
        config = self._valid_config()
        object.__setattr__(config, "token", _RaisingSecret())

        errors = ConfigValidator.validate_account_config(config)
        assert "Token is required" in errors
        assert "Account ID is required" not in errors

    def test_account_id_accessor_exception_reports_account_id_required(self):
        """Test that a raising account_id accessor is reported as missing."""
        config = self._valid_config()
        object.__setattr__(config, "account_id", _RaisingSecret())

        errors = ConfigValidator.validate_account_config(config)
        assert "Account ID is required" in errors
        assert "Token is required" not in errors


class TestConfigValidatorFieldValidators:
    """Test the static field-level validators on ConfigValidator."""

    def test_validate_token_valid(self):
        assert ConfigValidator.validate_token("a-token-of-reasonable-length") is True
        assert ConfigValidator.validate_token("12345678") is True  # Minimum length

    def test_validate_token_invalid(self):
        assert ConfigValidator.validate_token(None) is False
        assert ConfigValidator.validate_token("") is False
        assert ConfigValidator.validate_token("   ") is False
        assert ConfigValidator.validate_token("short") is False  # Below minimum length
        assert ConfigValidator.validate_token(12345678) is False  # type: ignore[arg-type]

    def test_validate_account_id_valid(self):
        assert ConfigValidator.validate_account_id("101-001-1234567-001") is True
        assert ConfigValidator.validate_account_id("  101-001-1234567-001  ") is True  # Whitespace stripped
        # The user segment varies in length on real accounts (6-9 digits observed live).
        assert ConfigValidator.validate_account_id("101-001-123456-001") is True
        assert ConfigValidator.validate_account_id("101-001-27189766-001") is True

    def test_validate_account_id_invalid(self):
        assert ConfigValidator.validate_account_id(None) is False
        assert ConfigValidator.validate_account_id("") is False
        assert ConfigValidator.validate_account_id("   ") is False
        assert ConfigValidator.validate_account_id("123-456-789") is False  # Wrong shape
        assert ConfigValidator.validate_account_id("abc-def-ghijklm-nop") is False
        assert ConfigValidator.validate_account_id(1010011234567001) is False  # type: ignore[arg-type]

    def test_validate_environment_valid(self):
        assert ConfigValidator.validate_environment("practice") is True
        assert ConfigValidator.validate_environment("live") is True
        assert ConfigValidator.validate_environment("LIVE") is True  # Case-insensitive
        assert ConfigValidator.validate_environment("Practice") is True

    def test_validate_environment_invalid(self):
        assert ConfigValidator.validate_environment(None) is False
        assert ConfigValidator.validate_environment("") is False
        assert ConfigValidator.validate_environment("staging") is False
        assert ConfigValidator.validate_environment(1) is False  # type: ignore[arg-type]

    def test_validate_config_all_valid(self):
        config_dict = {
            "token": "a-token-of-reasonable-length",
            "account_id": "101-001-1234567-001",
            "environment": "practice",
            "alias": "primary_account",
        }
        assert ConfigValidator.validate_config(config_dict) == {}

    def test_validate_config_all_invalid(self):
        errors = ConfigValidator.validate_config({})
        assert errors["token"] == "Invalid token format"
        assert errors["account_id"] == "Invalid account ID format"
        assert errors["environment"] == "Invalid environment (must be 'practice' or 'live')"
        assert errors["alias"] == "Alias is required"

    def test_validate_config_invalid_alias_identifier(self):
        config_dict = {
            "token": "a-token-of-reasonable-length",
            "account_id": "101-001-1234567-001",
            "environment": "live",
            "alias": "123-bad-alias",
        }
        errors = ConfigValidator.validate_config(config_dict)
        assert errors == {"alias": "Alias must be a valid identifier"}


class TestAccountConfigLoaderFile:
    """Test AccountConfigLoader file-based loading."""

    def _write_config(self, tmp_path, data):
        config_file = tmp_path / "accounts.json"
        config_file.write_text(json.dumps(data) if isinstance(data, dict) else data)
        return str(config_file)

    def _valid_data(self):
        return {
            "accounts": [
                {"alias": "primary", "token": "token-one", "account_id": "101-001-1234567-001", "environment": "practice"},
                {"alias": "live_acct", "token": "token-two", "account_id": "101-001-7654321-002", "environment": "live"},
            ]
        }

    def test_load_from_file_valid(self, tmp_path):
        """Test loading multiple accounts from a valid JSON file."""
        config_file = self._write_config(tmp_path, self._valid_data())

        accounts = AccountConfigLoader.load_from_file(config_file)

        assert len(accounts) == 2
        assert accounts[0].alias == "primary"
        assert accounts[0].token.get_secret_value() == "token-one"
        assert accounts[0].account_id.get_secret_value() == "101-001-1234567-001"
        assert accounts[0].environment == Environment.PRACTICE
        assert accounts[1].alias == "live_acct"
        assert accounts[1].environment == Environment.LIVE

    def test_load_from_file_missing_file(self, tmp_path):
        """Test that a missing config file raises FileNotFoundError."""
        missing = str(tmp_path / "does_not_exist.json")
        with pytest.raises(FileNotFoundError, match="Configuration file not found"):
            AccountConfigLoader.load_from_file(missing)

    def test_load_from_file_malformed_json(self, tmp_path):
        """Test that malformed JSON raises a decode error."""
        config_file = self._write_config(tmp_path, "{not valid json")
        with pytest.raises(json.JSONDecodeError):
            AccountConfigLoader.load_from_file(config_file)

    def test_load_from_file_missing_accounts_key(self, tmp_path):
        """Test that a file without 'accounts' raises ValueError."""
        config_file = self._write_config(tmp_path, {"users": []})
        with pytest.raises(ValueError, match="must contain 'accounts' key"):
            AccountConfigLoader.load_from_file(config_file)

    def test_load_from_file_missing_required_account_field(self, tmp_path):
        """Test that an account entry missing a required key raises KeyError."""
        data = {"accounts": [{"alias": "primary", "account_id": "101-001-1234567-001", "environment": "practice"}]}
        config_file = self._write_config(tmp_path, data)
        with pytest.raises(KeyError):
            AccountConfigLoader.load_from_file(config_file)

    def test_load_from_file_invalid_environment_value(self, tmp_path):
        """Test that an unknown environment value raises ValueError."""
        data = {"accounts": [{"alias": "primary", "token": "token-one", "account_id": "101-001-1234567-001", "environment": "staging"}]}
        config_file = self._write_config(tmp_path, data)
        with pytest.raises(ValueError, match="is not a valid"):
            AccountConfigLoader.load_from_file(config_file)

    def test_load_by_alias_found(self, tmp_path):
        """Test loading a specific account by alias."""
        config_file = self._write_config(tmp_path, self._valid_data())

        config = AccountConfigLoader.load_by_alias(config_file, "live_acct")

        assert config is not None
        assert config.alias == "live_acct"
        assert config.environment == Environment.LIVE
        assert config.token.get_secret_value() == "token-two"

    def test_load_by_alias_missing(self, tmp_path):
        """Test that a missing alias returns None."""
        config_file = self._write_config(tmp_path, self._valid_data())
        assert AccountConfigLoader.load_by_alias(config_file, "nonexistent") is None

    def test_load_by_alias_missing_file(self, tmp_path):
        """Test that load_by_alias propagates missing-file errors."""
        with pytest.raises(FileNotFoundError):
            AccountConfigLoader.load_by_alias(str(tmp_path / "nope.json"), "primary")


class TestAccountConfigLoaderEnvPrefix:
    """Additional from_env_prefix behavior."""

    def test_from_env_prefix_missing_vars_returns_none(self):
        """Test that from_env_prefix returns None when variables are absent."""
        with patch.dict(os.environ, {}, clear=True):
            assert AccountConfigLoader.from_env_prefix("MOMENTUM_") is None

    def test_from_env_prefix_does_not_read_default_vars(self):
        """Test that a prefixed lookup ignores the unprefixed default variables."""
        with patch.dict(os.environ, {"FIVETWENTY_OANDA_TOKEN": "default-token", "FIVETWENTY_OANDA_ACCOUNT": "default-account"}, clear=True):
            assert AccountConfigLoader.from_env_prefix("MOMENTUM_") is None


class TestAccountConfigSecretHandling:
    """Test that secrets never leak through string conversions."""

    def test_secrets_masked_in_str_and_repr(self):
        config = AccountConfig(token="super-secret-token", account_id="101-001-1234567-001", environment=Environment.PRACTICE, alias="masked")

        for rendered in (str(config), repr(config)):
            assert "super-secret-token" not in rendered
            assert "101-001-1234567-001" not in rendered

    def test_secret_values_stripped(self):
        """Test that whitespace around secret values is stripped by the validator."""
        config = AccountConfig(token=SecretStr("  padded-token  "), account_id=SecretStr("  padded-id  "), environment=Environment.LIVE, alias="stripped")

        assert config.token.get_secret_value() == "padded-token"
        assert config.account_id.get_secret_value() == "padded-id"
