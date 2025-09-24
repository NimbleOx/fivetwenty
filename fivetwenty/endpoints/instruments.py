"""Instrument pricing and candlestick data endpoints."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from datetime import datetime

    from ..client import AsyncClient


class InstrumentEndpoints:
    """Instrument pricing and historical data operations."""

    def __init__(self, client: AsyncClient):
        self._client = client

    async def get_instrument_candles(
        self,
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
        Get candlestick data for a specified instrument.

        This method provides access to historical and recent candlestick data
        with configurable granularities, price components, and alignment options.

        Args:
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
            Get 500 M1 midpoint candles:
                candles = await client.instruments.get_candles(
                    "EUR_USD",
                    granularity="M1",
                    count=500
                )

            Get H1 bid/ask candles for specific time range:
                candles = await client.instruments.get_candles(
                    "GBP_JPY",
                    price="BA",
                    granularity="H1",
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
            params["includeFirst"] = str(include_first).lower()
        if to_time is not None:
            params["to"] = to_time.isoformat()

        response = await self._client._request(
            "GET",
            f"/instruments/{instrument}/candles",
            params=params,
        )

        return response.json()  # type: ignore[no-any-return]
