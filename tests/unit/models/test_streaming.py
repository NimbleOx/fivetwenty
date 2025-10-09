"""Tests for streaming utilities."""

from fivetwenty.models import (
    ReconnectionPolicy,
    StreamingConfiguration,
    StreamState,
)


class TestStreamingUtilities:
    """Test streaming utilities and configuration."""

    def test_stream_state_enum(self) -> None:
        """Test StreamState enum values."""
        assert StreamState.CONNECTING == "connecting"
        assert StreamState.CONNECTED == "connected"
        assert StreamState.RECONNECTING == "reconnecting"
        assert StreamState.DISCONNECTED == "disconnected"

    def test_reconnection_policy(self) -> None:
        """Test ReconnectionPolicy model."""
        policy_data = {
            "max_attempts": 5,
            "delay_seconds": 2.0,
        }

        policy = ReconnectionPolicy(**policy_data)
        assert policy.max_attempts == 5
        assert policy.delay_seconds == 2.0

    def test_reconnection_policy_defaults(self) -> None:
        """Test ReconnectionPolicy default values."""
        policy = ReconnectionPolicy()
        assert policy.max_attempts == 3  # Default value
        assert policy.delay_seconds == 1.0  # Default value

    def test_streaming_configuration(self) -> None:
        """Test StreamingConfiguration model."""
        config_data = {
            "include_heartbeats": False,
            "stall_timeout": 60.0,
            "reconnection_policy": {
                "max_attempts": 5,
                "delay_seconds": 2.0,
            },
        }

        config = StreamingConfiguration(**config_data)
        assert config.include_heartbeats is False
        assert config.stall_timeout == 60.0
        assert config.reconnection_policy.max_attempts == 5
        assert config.reconnection_policy.delay_seconds == 2.0

    def test_streaming_configuration_defaults(self) -> None:
        """Test StreamingConfiguration default values."""
        config = StreamingConfiguration()
        assert config.include_heartbeats is True  # Default
        assert config.stall_timeout == 30.0  # Default
        assert isinstance(config.reconnection_policy, ReconnectionPolicy)
        assert config.reconnection_policy.max_attempts == 3  # Default
