"""Pricing and streaming endpoints."""

import json
from collections.abc import AsyncIterator
from datetime import datetime
from typing import TYPE_CHECKING, Any

from ..models import AccountID, ClientPrice, PricingHeartbeat
from ..models.streaming import StreamingConfiguration, StreamState

if TYPE_CHECKING:
    from ..client import AsyncClient


class PricingEndpoints:
    """Pricing and real-time data operations."""

    def __init__(self, client: "AsyncClient"):
        self._client = client

    async def get_pricing(
        self,
        account_id: AccountID,
        instruments: list[str],
        *,
        since: str | None = None,
        include_units_available: bool = True,
        include_home_conversions: bool = False,
    ) -> dict[str, Any]:
        """
        Get current prices for instruments.

        Args:
            account_id: Account ID
            instruments: List of instruments to get prices for
            since: Only get prices changed since this time
            include_units_available: Include units available info
            include_home_conversions: Include home currency conversions

        Returns:
            Pricing information

        Raises:
            FiveTwentyError: On API errors
        """
        params = {
            "instruments": ",".join(instruments),
            "includeUnitsAvailable": str(include_units_available).lower(),
            "includeHomeConversions": str(include_home_conversions).lower(),
        }

        if since:
            params["since"] = since

        response = await self._client._request(
            "GET",
            f"/accounts/{account_id}/pricing",
            params=params,
        )

        return response.json()  # type: ignore[no-any-return]

    async def get_pricing_stream(
        self,
        account_id: AccountID,
        instruments: list[str],
        *,
        snapshot: bool = True,
        include_home_conversions: bool = False,
        stall_timeout: float = 30.0,
    ) -> AsyncIterator[ClientPrice | PricingHeartbeat]:
        """
        Stream real-time pricing data.

        Args:
            account_id: Account ID
            instruments: List of instruments to stream
            snapshot: Include initial snapshot
            include_home_conversions: Include home currency conversion factors
            stall_timeout: Timeout for detecting stream stalls

        Yields:
            ClientPrice or PricingHeartbeat objects

        Raises:
            FiveTwentyError: On API errors
            StreamStall: On stream timeout or connection issues
        """
        params = {
            "instruments": ",".join(instruments),
        }

        if snapshot:
            params["snapshot"] = "true"
        if include_home_conversions:
            params["includeHomeConversions"] = "true"

        async for line in self._client._stream(
            f"/accounts/{account_id}/pricing/stream",
            params=params,
            stall_timeout=stall_timeout,
        ):
            try:
                data = json.loads(line)

                if data.get("type") == "PRICE":
                    yield ClientPrice.model_validate(data)
                elif data.get("type") == "HEARTBEAT":
                    yield PricingHeartbeat.model_validate(data)

            except (json.JSONDecodeError, ValueError) as e:
                # Log malformed data but continue streaming
                self._client._log(
                    "warning",
                    f"Malformed stream data: {e}",
                    extra={
                        "line": line[:200],  # Truncate for logging
                    },
                )
                continue

    async def get_account_instrument_candles(
        self,
        account_id: AccountID,
        instrument: str,
        *,
        price: str = "M",
        granularity: str = "S5",
        count: int | None = None,
        from_time: datetime | None = None,
        to_time: datetime | None = None,
        smooth: bool = False,
        include_first: bool = True,
        daily_alignment: int = 17,
        alignment_timezone: str = "America/New_York",
        weekly_alignment: str = "Friday",
    ) -> dict[str, Any]:
        """
        Get account-specific candlestick data for a specified instrument.

        This method provides access to historical candlestick data through an
        account-specific endpoint, which may return different data based on
        account permissions and access levels.

        Args:
            account_id: Account identifier
            instrument: The instrument to get candlestick data for
            price: Price component(s) - M, B, A, BA, BM, AM, or BAM (default: M)
            granularity: Candlestick granularity (default: S5)
            count: Number of candlesticks to return (max 5000, conflicts with time range)
            from_time: Start of time range for candlesticks
            to_time: End of time range for candlesticks
            smooth: Use previous candle's close as open price (default: False)
            include_first: Include candlestick covered by from_time (default: True)
            daily_alignment: Hour of day for daily-aligned granularities (0-23, default: 17)
            alignment_timezone: Timezone for daily alignment (default: America/New_York)
            weekly_alignment: Day of week for weekly alignment (default: Friday)

        Returns:
            Dictionary containing instrument, granularity, and list of candlesticks

        Raises:
            FiveTwentyError: On API errors
            ValueError: If both count and time range are specified

        Examples:
            Get account-specific M1 candles:
                candles = await client.pricing.get_account_candles(
                    account_id,
                    "EUR_USD",
                    granularity="M1",
                    count=100
                )

            Get H4 bid/ask candles for time range:
                candles = await client.pricing.get_account_candles(
                    account_id,
                    "GBP_JPY",
                    price="BA",
                    granularity="H4",
                    from_time=datetime(2024, 1, 1),
                    to_time=datetime(2024, 1, 2)
                )
        """
        if count is not None and (from_time is not None or to_time is not None):
            raise ValueError("Cannot specify both count and time range parameters")

        params: dict[str, str] = {
            "price": price,
            "granularity": granularity,
            "smooth": str(smooth).lower(),
            "includeFirst": str(include_first).lower(),
            "dailyAlignment": str(daily_alignment),
            "alignmentTimezone": alignment_timezone,
            "weeklyAlignment": weekly_alignment,
        }

        if count is not None:
            if count > 5000:
                raise ValueError("Count cannot exceed 5000")
            params["count"] = str(count)

        if from_time is not None:
            params["from"] = from_time.isoformat()
        if to_time is not None:
            params["to"] = to_time.isoformat()

        response = await self._client._request(
            "GET",
            f"/accounts/{account_id}/instruments/{instrument}/candles",
            params=params,
        )

        return response.json()  # type: ignore[no-any-return]

    async def get_latest_candles(
        self,
        account_id: AccountID,
        candle_specifications: list[str],
        *,
        units: int = 1,
        smooth: bool = False,
        daily_alignment: int = 17,
        alignment_timezone: str = "America/New_York",
        weekly_alignment: str = "Friday",
    ) -> dict[str, Any]:
        """
        Get the latest candle for multiple instrument/granularity combinations.

        Args:
            account_id: Account identifier
            candle_specifications: List of "INSTRUMENT:GRANULARITY:PRICE" specs
            units: Number of units for each candle spec (1-5000)
            smooth: Apply smoothing to candles
            daily_alignment: Hour for daily candle alignment (0-23)
            alignment_timezone: Timezone for alignment
            weekly_alignment: Day for weekly candle alignment

        Returns:
            Dictionary containing latest candles for each specification

        Raises:
            FiveTwentyError: On API errors
            ValueError: On invalid parameters
        """
        if not candle_specifications:
            raise ValueError("Must specify at least one candle specification")

        if not (1 <= units <= 5000):
            raise ValueError("Units must be between 1 and 5000")

        params = {
            "candleSpecifications": ",".join(candle_specifications),
            "units": str(units),
            "smooth": str(smooth).lower(),
            "dailyAlignment": str(daily_alignment),
            "alignmentTimezone": alignment_timezone,
            "weeklyAlignment": weekly_alignment,
        }

        response = await self._client._request(
            "GET",
            f"/accounts/{account_id}/candles/latest",
            params=params,
        )

        return response.json()  # type: ignore[no-any-return]

    async def stream_pricing_with_retries(
        self,
        account_id: AccountID,
        instruments: list[str],
        *,
        snapshot: bool = True,
        include_home_conversions: bool = False,
        config: StreamingConfiguration | None = None,
    ) -> AsyncIterator[tuple[ClientPrice | PricingHeartbeat, StreamState]]:
        """
        Stream real-time pricing data with automatic retry and connection state tracking.

        This method provides enhanced streaming with automatic reconnection on failures
        and real-time connection state information.

        Args:
            account_id: Account ID
            instruments: List of instruments to stream
            snapshot: Include initial snapshot
            include_home_conversions: Include home currency conversion factors
            config: Streaming configuration (uses defaults if None)

        Yields:
            Tuple of (price_data, stream_state) where:
            - price_data: ClientPrice for actual pricing updates or PricingHeartbeat for heartbeats
            - stream_state: Current connection state (CONNECTING/CONNECTED/RECONNECTING/DISCONNECTED)

        Raises:
            StreamStall: If all retry attempts are exhausted

        Example:
            ```python
            config = StreamingConfiguration(
                reconnection_policy=ReconnectionPolicy(max_attempts=5, delay_seconds=2.0)
            )

            async for price_data, state in client.pricing.stream_pricing_with_retries(
                "123-456-789",
                ["EUR_USD", "GBP_USD"],
                config=config
            ):
                if state == StreamState.RECONNECTING:
                    print("Connection lost, retrying...")
                elif state == StreamState.CONNECTED and isinstance(price_data, ClientPrice):
                    print(f"{price_data.instrument}: {price_data.asks[0].price}")
            ```
        """
        if config is None:
            config = StreamingConfiguration()

        params = {
            "snapshot": str(snapshot).lower(),
            "instruments": ",".join(instruments),
        }

        if config.include_heartbeats:
            params["includeHeartbeats"] = "true"
        if include_home_conversions:
            params["includeHomeConversions"] = "true"

        async for line, state in self._client._stream_with_retries(
            f"/accounts/{account_id}/pricing/stream",
            params=params,
            config=config,
        ):
            try:
                data = json.loads(line)
            except json.JSONDecodeError as e:
                self._client._log(
                    "warning",
                    f"Malformed stream data: {e}",
                    extra={
                        "line": line[:200],  # Truncate for logging
                    },
                )
                continue

            # Parse the data based on type
            if data.get("type") == "HEARTBEAT":
                heartbeat = PricingHeartbeat.model_validate(data)
                yield heartbeat, state
            elif data.get("type") == "PRICE":
                price = ClientPrice.model_validate(data)
                yield price, state
            else:
                # Unknown message type - log and skip
                self._client._log(
                    "warning",
                    f"Unknown pricing stream message type: {data.get('type')}",
                    extra={"data": data},
                )
                continue
