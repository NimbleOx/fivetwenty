"""Streaming configuration defaults, nested parsing, and public state values."""

import pytest

from fivetwenty.models import ReconnectionPolicy, StreamingConfiguration, StreamState


def test_stream_states_are_strings_with_stable_values() -> None:
    assert {state.name: state.value for state in StreamState} == {
        "CONNECTING": "connecting",
        "CONNECTED": "connected",
        "RECONNECTING": "reconnecting",
        "DISCONNECTED": "disconnected",
    }
    assert all(isinstance(state, str) and state == state.value for state in StreamState)


def test_streaming_configuration_defaults() -> None:
    config = StreamingConfiguration()
    assert isinstance(config.reconnection_policy, ReconnectionPolicy)
    assert config.model_dump() == {
        "include_heartbeats": True,
        "stall_timeout": 30.0,
        "reconnection_policy": {"max_attempts": 3, "delay_seconds": 1.0},
    }


@pytest.mark.parametrize("policy", [{"max_attempts": 5, "delay_seconds": 2.0}, ReconnectionPolicy(max_attempts=5, delay_seconds=2.0)], ids=["dictionary", "model"])
def test_nested_configuration_survives_json_roundtrip(policy: dict[str, int | float] | ReconnectionPolicy) -> None:
    config = StreamingConfiguration.model_validate({"include_heartbeats": False, "stall_timeout": 60.0, "reconnection_policy": policy})
    assert isinstance(config.reconnection_policy, ReconnectionPolicy)
    assert config.model_dump() == {
        "include_heartbeats": False,
        "stall_timeout": 60.0,
        "reconnection_policy": {"max_attempts": 5, "delay_seconds": 2.0},
    }
    assert StreamingConfiguration.model_validate_json(config.model_dump_json()) == config


def test_default_policies_are_independent() -> None:
    first = StreamingConfiguration()
    second = StreamingConfiguration()
    first.reconnection_policy.max_attempts = 9
    assert second.reconnection_policy.max_attempts == 3
