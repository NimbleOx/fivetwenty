"""Streaming utilities and connection state for OANDA API streaming endpoints."""

from enum import Enum

from pydantic import Field

from .base import ApiModel


class StreamState(str, Enum):
    """Current state of a streaming connection."""

    CONNECTING = "connecting"
    CONNECTED = "connected"
    RECONNECTING = "reconnecting"
    DISCONNECTED = "disconnected"


class ReconnectionPolicy(ApiModel):
    """Policy for handling stream reconnections."""

    max_attempts: int = Field(alias="maxAttempts", default=3, description="Maximum reconnection attempts")
    delay_seconds: float = Field(alias="delaySeconds", default=1.0, description="Delay between reconnection attempts")


class StreamingConfiguration(ApiModel):
    """Configuration for streaming connections."""

    include_heartbeats: bool = Field(alias="includeHeartbeats", default=True, description="Include heartbeat messages")
    stall_timeout: float = Field(alias="stallTimeout", default=30.0, description="Seconds before considering stream stalled")
    reconnection_policy: ReconnectionPolicy = Field(alias="reconnectionPolicy", default_factory=ReconnectionPolicy, description="Reconnection settings")


# Removed extra streaming models that are not part of official OANDA v20 API:
# These were custom wrapper models, but OANDA streaming endpoints return
# actual data models (ClientPrice, PricingHeartbeat, etc.) not wrapper models

__all__ = [
    "ReconnectionPolicy",
    "StreamState",
    "StreamingConfiguration",
]
