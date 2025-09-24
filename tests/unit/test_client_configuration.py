"""Tests for client configuration integration."""

import os
from unittest.mock import patch

import pytest

from fivetwenty import AccountConfig, AsyncClient, Client, Environment


class TestAsyncClientConfiguration:
    """Test AsyncClient configuration handling."""

    def test_direct_parameters(self):
        """Test client initialization with direct parameters."""
        client = AsyncClient(token="test-token", account_id="test-account-id", environment=Environment.PRACTICE)

        assert client._token == "test-token"
        assert client.account_id == "test-account-id"
        assert client._environment == Environment.PRACTICE
        assert client.config is not None
        assert client.config.alias == "direct_params"

    def test_config_object(self):
        """Test client initialization with AccountConfig object."""
        config = AccountConfig(token="config-token", account_id="config-account-id", environment=Environment.LIVE, alias="config_account")

        client = AsyncClient(config=config)

        assert client._token == "config-token"
        assert client.account_id == "config-account-id"
        assert client._environment == Environment.LIVE
        assert client.config == config
        assert client.config.alias == "config_account"

    def test_environment_variables_success(self):
        """Test client initialization with environment variables."""
        with patch.dict(os.environ, {"FIVETWENTY_OANDA_TOKEN": "env-token", "FIVETWENTY_OANDA_ACCOUNT": "env-account-id", "FIVETWENTY_OANDA_ENVIRONMENT": "live"}, clear=True):
            client = AsyncClient()

            assert client._token == "env-token"
            assert client.account_id == "env-account-id"
            assert client._environment == Environment.LIVE
            assert client.config is not None
            assert client.config.alias == "default"

    def test_environment_variables_missing(self):
        """Test client initialization fails when env vars are missing."""
        with patch.dict(os.environ, {}, clear=True), pytest.raises(ValueError, match="No configuration provided"):
            AsyncClient()

    def test_config_object_priority_over_params(self):
        """Test that config object takes priority over direct parameters."""
        config = AccountConfig(token="config-token", account_id="config-account-id", environment=Environment.LIVE, alias="config_account")

        # Pass both config and direct params - config should win except for account_id override
        client = AsyncClient(
            token="direct-token",  # should be ignored
            environment=Environment.PRACTICE,  # should be ignored
            config=config,
        )

        assert client._token == "config-token"
        assert client.account_id == "config-account-id"  # From config since no account_id override
        assert client._environment == Environment.LIVE
        assert client.config.alias == "config_account"

    def test_direct_params_priority_over_env_vars(self):
        """Test that direct parameters take priority over env vars."""
        with patch.dict(os.environ, {"FIVETWENTY_OANDA_TOKEN": "env-token", "FIVETWENTY_OANDA_ACCOUNT": "env-account-id", "FIVETWENTY_OANDA_ENVIRONMENT": "live"}, clear=True):
            client = AsyncClient(token="direct-token", account_id="direct-account-id", environment=Environment.PRACTICE)

            assert client._token == "direct-token"
            assert client.account_id == "direct-account-id"
            assert client._environment == Environment.PRACTICE

    def test_optional_account_id(self):
        """Test that account_id is optional for direct parameters."""
        client = AsyncClient(token="test-token", environment=Environment.PRACTICE)

        assert client._token == "test-token"
        assert client.account_id == "unknown"  # default value
        assert client._environment == Environment.PRACTICE

    def test_account_id_override(self):
        """Test that direct account_id parameter can override config."""
        config = AccountConfig(token="config-token", account_id="config-account-id", environment=Environment.PRACTICE, alias="config_account")

        client = AsyncClient(config=config, account_id="override-account-id")

        assert client._token == "config-token"
        assert client.account_id == "override-account-id"  # overridden
        assert client._environment == Environment.PRACTICE

    def test_properties(self):
        """Test client properties expose configuration correctly."""
        config = AccountConfig(token="test-token", account_id="test-account-id", environment=Environment.PRACTICE, alias="test_account")

        client = AsyncClient(config=config)

        assert client.account_id == "test-account-id"
        assert client.config == config
        assert client.config.summary() == "test_account (practice)"


class TestClientConfiguration:
    """Test sync Client configuration handling."""

    def test_direct_parameters(self):
        """Test sync client initialization with direct parameters."""
        client = Client(token="test-token", account_id="test-account-id", environment=Environment.PRACTICE)

        assert client.account_id == "test-account-id"
        assert client.config is not None
        assert client.config.alias == "direct_params"

    def test_config_object(self):
        """Test sync client initialization with AccountConfig object."""
        config = AccountConfig(token="config-token", account_id="config-account-id", environment=Environment.LIVE, alias="sync_config_account")

        client = Client(config=config)

        assert client.account_id == "config-account-id"
        assert client.config == config
        assert client.config.alias == "sync_config_account"

    def test_environment_variables_success(self):
        """Test sync client initialization with environment variables."""
        with patch.dict(os.environ, {"FIVETWENTY_OANDA_TOKEN": "sync-env-token", "FIVETWENTY_OANDA_ACCOUNT": "sync-env-account-id", "FIVETWENTY_OANDA_ENVIRONMENT": "practice"}, clear=True):
            client = Client()

            assert client.account_id == "sync-env-account-id"
            assert client.config is not None
            assert client.config.alias == "default"

    def test_environment_variables_missing(self):
        """Test sync client initialization fails when env vars are missing."""
        with patch.dict(os.environ, {}, clear=True), pytest.raises(ValueError, match="No configuration provided"):
            Client()

    def test_properties_delegate_to_async_client(self):
        """Test that sync client properties delegate to async client."""
        config = AccountConfig(token="test-token", account_id="test-account-id", environment=Environment.PRACTICE, alias="test_sync_account")

        client = Client(config=config)

        # Properties should match async client
        assert client.account_id == client._async.account_id
        assert client.config == client._async.config
        assert client.config.alias == "test_sync_account"


class TestClientConfigurationEdgeCases:
    """Test edge cases and error conditions."""

    def test_invalid_environment_variable_value(self):
        """Test that invalid environment values are handled."""
        with (
            patch.dict(
                os.environ,
                {
                    "FIVETWENTY_OANDA_TOKEN": "test-token",
                    "FIVETWENTY_OANDA_ACCOUNT": "test-account-id",
                    "FIVETWENTY_OANDA_ENVIRONMENT": "invalid",  # Invalid environment
                },
                clear=True,
            ),
            pytest.raises(ValueError),
        ):
            AsyncClient()

    def test_empty_token_in_config(self):
        """Test that whitespace-only token fails validation."""
        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            AccountConfig(
                token="   ",  # Whitespace-only token should fail validation
                account_id="test-account-id",
                environment=Environment.PRACTICE,
                alias="test_account",
            )

    def test_none_values_handled_properly(self):
        """Test that None values are handled properly."""
        client = AsyncClient(
            token="test-token",
            account_id=None,  # Should use default
            environment=Environment.PRACTICE,
        )

        assert client._token == "test-token"
        assert client.account_id == "unknown"
        assert client._environment == Environment.PRACTICE

    def test_secret_values_not_logged(self):
        """Test that secret values don't appear in string representations."""
        config = AccountConfig(token="super-secret-token", account_id="secret-account-id", environment=Environment.PRACTICE, alias="test_account")

        client = AsyncClient(config=config)

        # Check that secrets don't appear in representations
        config_str = str(client.config)
        config_repr = repr(client.config)

        assert "super-secret-token" not in config_str
        assert "secret-account-id" not in config_str
        assert "super-secret-token" not in config_repr
        assert "secret-account-id" not in config_repr
        assert "***" in config_repr
