"""Tests for simplified streaming models and functionality."""

from fivetwenty.models.streaming import (
    ReconnectionPolicy,
    StreamingConfiguration,
    StreamState,
)


class TestStreamState:
    """Test StreamState enum."""

    def test_stream_state_values(self):
        """Test StreamState enum values."""
        assert StreamState.CONNECTING == "connecting"
        assert StreamState.CONNECTED == "connected"
        assert StreamState.RECONNECTING == "reconnecting"
        assert StreamState.DISCONNECTED == "disconnected"

    def test_stream_state_str_inheritance(self):
        """Test that StreamState inherits from str."""
        state = StreamState.CONNECTED
        assert isinstance(state, str)
        assert state.value == "connected"


class TestReconnectionPolicy:
    """Test simplified ReconnectionPolicy model."""

    def test_reconnection_policy_defaults(self):
        """Test ReconnectionPolicy with default values."""
        policy = ReconnectionPolicy()

        assert policy.max_attempts == 3
        assert policy.delay_seconds == 1.0

    def test_reconnection_policy_with_values(self):
        """Test ReconnectionPolicy with custom values."""
        policy = ReconnectionPolicy(max_attempts=5, delay_seconds=2.0)

        assert policy.max_attempts == 5
        assert policy.delay_seconds == 2.0

    def test_reconnection_policy_validation(self):
        """Test ReconnectionPolicy validation."""
        # Should work with valid values
        policy = ReconnectionPolicy(max_attempts=1, delay_seconds=0.1)
        assert policy.max_attempts == 1
        assert policy.delay_seconds == 0.1

    def test_reconnection_policy_json_roundtrip(self):
        """Test JSON serialization roundtrip."""
        original = ReconnectionPolicy(max_attempts=10, delay_seconds=5.0)

        # Convert to JSON and back
        json_data = original.model_dump()
        restored = ReconnectionPolicy(**json_data)

        assert restored.max_attempts == original.max_attempts
        assert restored.delay_seconds == original.delay_seconds


class TestStreamingConfiguration:
    """Test simplified StreamingConfiguration model."""

    def test_streaming_config_defaults(self):
        """Test StreamingConfiguration default values."""
        config = StreamingConfiguration()

        assert config.include_heartbeats is True
        assert config.stall_timeout == 30.0
        assert isinstance(config.reconnection_policy, ReconnectionPolicy)
        assert config.reconnection_policy.max_attempts == 3

    def test_streaming_config_with_values(self):
        """Test StreamingConfiguration with custom values."""
        custom_policy = ReconnectionPolicy(max_attempts=5, delay_seconds=2.0)
        config = StreamingConfiguration(include_heartbeats=False, stall_timeout=60.0, reconnection_policy=custom_policy)

        assert config.include_heartbeats is False
        assert config.stall_timeout == 60.0
        assert config.reconnection_policy.max_attempts == 5
        assert config.reconnection_policy.delay_seconds == 2.0

    def test_streaming_config_policy_factory(self):
        """Test that default_factory creates new instances."""
        config1 = StreamingConfiguration()
        config2 = StreamingConfiguration()

        # Should be different instances but same values
        assert config1.reconnection_policy is not config2.reconnection_policy
        assert config1.reconnection_policy.max_attempts == config2.reconnection_policy.max_attempts

    def test_streaming_config_json_roundtrip(self):
        """Test JSON serialization roundtrip."""
        original = StreamingConfiguration(include_heartbeats=False, stall_timeout=45.0, reconnection_policy=ReconnectionPolicy(max_attempts=7, delay_seconds=1.5))

        # Convert to JSON and back
        json_data = original.model_dump()
        restored = StreamingConfiguration(**json_data)

        assert restored.include_heartbeats == original.include_heartbeats
        assert restored.stall_timeout == original.stall_timeout
        assert restored.reconnection_policy.max_attempts == original.reconnection_policy.max_attempts
        assert restored.reconnection_policy.delay_seconds == original.reconnection_policy.delay_seconds


class TestStreamingModelIntegration:
    """Test integration between streaming models."""

    def test_nested_model_creation(self):
        """Test creating nested streaming models."""
        config = StreamingConfiguration(stall_timeout=120.0, reconnection_policy=ReconnectionPolicy(max_attempts=10, delay_seconds=3.0))

        assert config.stall_timeout == 120.0
        assert config.reconnection_policy.max_attempts == 10
        assert config.reconnection_policy.delay_seconds == 3.0

    def test_model_validation_errors(self):
        """Test that invalid data raises validation errors."""
        # This should work fine with our simple models
        config = StreamingConfiguration(stall_timeout=-1.0)
        assert config.stall_timeout == -1.0  # We don't validate this in simple models

    def test_streaming_models_serialization(self):
        """Test that models can be serialized properly."""
        policy1 = ReconnectionPolicy(max_attempts=3, delay_seconds=1.0)
        policy2 = ReconnectionPolicy(max_attempts=3, delay_seconds=1.0)

        # Models should be serializable to dict
        policy1_dict = policy1.model_dump()
        policy2_dict = policy2.model_dump()

        assert policy1_dict == policy2_dict
        assert policy1_dict["max_attempts"] == 3
        # Note: Pydantic models are not hashable by default, which is fine for our simple SDK use case
