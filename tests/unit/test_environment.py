"""Tests for environment configuration."""

import pytest

from fivetwenty._internal.environment import Environment


class TestEnvironment:
    """Test Environment enum functionality."""

    def test_environment_values(self):
        """Test Environment enum values."""
        assert Environment.PRACTICE.value == "practice"
        assert Environment.LIVE.value == "live"

    def test_environment_base_url_practice(self):
        """Test base URL for practice environment."""
        env = Environment.PRACTICE
        expected_url = "https://api-fxpractice.oanda.com/v3"
        assert env.base_url == expected_url

    def test_environment_base_url_live(self):
        """Test base URL for live environment."""
        env = Environment.LIVE
        expected_url = "https://api-fxtrade.oanda.com/v3"
        assert env.base_url == expected_url

    def test_environment_base_url_property(self):
        """Test that base_url is a property."""
        env = Environment.PRACTICE
        # Should be able to access multiple times
        url1 = env.base_url
        url2 = env.base_url
        assert url1 == url2
        assert isinstance(url1, str)

    def test_environment_enum_members(self):
        """Test that all expected enum members exist."""
        members = list(Environment)
        assert len(members) == 2
        assert Environment.PRACTICE in members
        assert Environment.LIVE in members

    def test_environment_from_value(self):
        """Test creating Environment from string values."""
        practice_env = Environment("practice")
        live_env = Environment("live")

        assert practice_env == Environment.PRACTICE
        assert live_env == Environment.LIVE

    def test_environment_invalid_value(self):
        """Test that invalid values raise ValueError."""
        with pytest.raises(ValueError, match="is not a valid"):
            Environment("invalid")

        with pytest.raises(ValueError, match="is not a valid"):
            Environment("staging")

    def test_environment_string_representation(self):
        """Test string representation of Environment."""
        practice_str = str(Environment.PRACTICE)
        live_str = str(Environment.LIVE)

        assert "Environment.PRACTICE" in practice_str
        assert "Environment.LIVE" in live_str

    def test_environment_comparison(self):
        """Test Environment comparison operations."""
        practice1 = Environment.PRACTICE
        practice2 = Environment.PRACTICE
        live = Environment.LIVE

        # Test equality
        assert practice1 == practice2
        assert practice1 != live

        # Test identity
        assert practice1 is practice2  # Enum members are singletons

    def test_environment_url_format(self):
        """Test that base URLs follow expected format."""
        for env in Environment:
            url = env.base_url
            assert url.startswith("https://")
            assert url.endswith("/v3")
            assert "oanda.com" in url

    def test_environment_consistency(self):
        """Test consistency between environment values and URLs."""
        # Practice environment should point to practice domain
        assert "fxpractice" in Environment.PRACTICE.base_url

        # Live environment should point to trade domain
        assert "fxtrade" in Environment.LIVE.base_url

    def test_environment_immutable(self):
        """Test that Environment enum values are immutable."""
        env = Environment.PRACTICE
        original_value = env.value

        # Enum values should be immutable
        with pytest.raises(AttributeError):
            env.value = "modified"  # type: ignore[misc]

        assert env.value == original_value

    def test_environment_hashable(self):
        """Test that Environment instances are hashable."""
        env_set = {Environment.PRACTICE, Environment.LIVE}
        assert len(env_set) == 2

        env_dict = {Environment.PRACTICE: "practice_data", Environment.LIVE: "live_data"}
        assert env_dict[Environment.PRACTICE] == "practice_data"
        assert env_dict[Environment.LIVE] == "live_data"
