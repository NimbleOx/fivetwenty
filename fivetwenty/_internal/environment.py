"""Environment configuration."""

from enum import Enum


class Environment(Enum):
    """OANDA API environments."""

    PRACTICE = "practice"
    LIVE = "live"

    @property
    def base_url(self) -> str:
        """Get the REST API base URL for this environment."""
        if self == Environment.LIVE:
            return "https://api-fxtrade.oanda.com/v3"
        return "https://api-fxpractice.oanda.com/v3"

    @property
    def stream_url(self) -> str:
        """Get the streaming API base URL for this environment."""
        if self == Environment.LIVE:
            return "https://stream-fxtrade.oanda.com/v3"
        return "https://stream-fxpractice.oanda.com/v3"
