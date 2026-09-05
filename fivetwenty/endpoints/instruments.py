"""Instrument pricing and candlestick data endpoints."""

from __future__ import annotations

from typing import TYPE_CHECKING, TypedDict, cast

from .._internal.response import ApiResponse
from .._internal.utils import format_datetime_for_oanda

if TYPE_CHECKING:
    from datetime import datetime

    from ..client import AsyncClient
    from ..models import Candlestick, CandlestickGranularity, InstrumentName, OrderBook, PositionBook, PricingComponent


class CandlesResponse(TypedDict):
    """Response from get_instrument_candles endpoint."""

    instrument: InstrumentName | str
    granularity: CandlestickGranularity
    candles: list[Candlestick]


class OrderBookResponse(TypedDict):
    """Response from get_instrument_order_book endpoint."""

    orderBook: OrderBook


class PositionBookResponse(TypedDict):
    """Response from get_instrument_position_book endpoint."""

    positionBook: PositionBook


class InstrumentEndpoints:
    """Instrument pricing and historical data operations."""

    def __init__(self, client: AsyncClient):
        self._client = client

    async def get_instrument_candles(
        self,
        instrument: InstrumentName | str,
        *,
        price: PricingComponent = "M",
        granularity: CandlestickGranularity | str = "S5",
        count: int | None = None,
        from_time: datetime | None = None,
        to_time: datetime | None = None,
        smooth: bool = False,
        include_first: bool = True,
        daily_alignment: int = 17,
        alignment_timezone: str = "America/New_York",
        weekly_alignment: str = "Friday",
    ) -> CandlesResponse:
        """
        Get candlestick data for a specified instrument.

        This method provides access to historical and recent candlestick data
        with configurable granularities, price components, and alignment options.

        Args:
            instrument: Instrument enum or string (e.g., InstrumentName.EUR_USD or "EUR_USD")
            price: Price component(s) - M, B, A, BA, BM, AM, or BAM (default: M)
            granularity: Candlestick granularity enum or string (default: S5, matching the API)
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
            Get 500 M1 midpoint candles using enums:
                candles = await client.instruments.get_candles(
                    InstrumentName.EUR_USD,
                    granularity=CandlestickGranularity.M1,
                    count=500
                )

            Get H1 bid/ask candles for specific time range:
                candles = await client.instruments.get_candles(
                    InstrumentName.GBP_JPY,
                    price="BA",
                    granularity=CandlestickGranularity.H1,
                    from_time=datetime(2024, 1, 1),
                    to_time=datetime(2024, 1, 2)
                )
        """
        if count is not None and (from_time is not None or to_time is not None):
            raise ValueError("Cannot specify both count and time range parameters")

        # Convert enums to strings if needed
        instrument_str = instrument.value if hasattr(instrument, "value") else instrument
        granularity_str = granularity.value if hasattr(granularity, "value") else granularity

        params: dict[str, str] = {
            "price": price,
            "granularity": granularity_str,
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
            params["from"] = format_datetime_for_oanda(from_time, getattr(self._client, "_datetime_format", "RFC3339"))
            params["includeFirst"] = str(include_first).lower()
        if to_time is not None:
            params["to"] = format_datetime_for_oanda(to_time, getattr(self._client, "_datetime_format", "RFC3339"))

        response = await self._client._request(
            "GET",
            f"/instruments/{instrument_str}/candles",
            params=params,
        )

        from ..models import Candlestick, CandlestickGranularity, InstrumentName

        data = response.json()

        # OANDA defines InstrumentName as an open string; tolerate names
        # outside the convenience enum (e.g. CFDs on other account divisions).
        try:
            instrument_name: InstrumentName | str = InstrumentName(data["instrument"])
        except ValueError:
            instrument_name = data["instrument"]

        return cast(
            "CandlesResponse",
            ApiResponse(
                {
                    "instrument": instrument_name,
                    "granularity": CandlestickGranularity(data["granularity"]),
                    "candles": [Candlestick.model_validate(c) for c in data["candles"]],
                }
            ),
        )

    async def get_instrument_order_book(
        self,
        instrument: InstrumentName | str,
        *,
        time: datetime | None = None,
    ) -> OrderBookResponse:
        """
        Get an order book snapshot for an instrument.

        The order book partitions open orders into price buckets, each with the
        percentage of long and short orders at that price.

        Args:
            instrument: Instrument enum or string (e.g., InstrumentName.EUR_USD or "EUR_USD")
            time: Snapshot time; the most recent snapshot is returned when omitted

        Returns:
            Dictionary containing the orderBook snapshot

        Raises:
            FiveTwentyError: On API errors
        """
        instrument_str = instrument.value if hasattr(instrument, "value") else instrument
        params: dict[str, str] = {}
        if time is not None:
            params["time"] = format_datetime_for_oanda(time, getattr(self._client, "_datetime_format", "RFC3339"))

        response = await self._client._request(
            "GET",
            f"/instruments/{instrument_str}/orderBook",
            params=params,
        )

        from ..models import OrderBook

        data = response.json()
        return cast(
            "OrderBookResponse",
            ApiResponse({"orderBook": OrderBook.model_validate(data["orderBook"])}),
        )

    async def get_instrument_position_book(
        self,
        instrument: InstrumentName | str,
        *,
        time: datetime | None = None,
    ) -> PositionBookResponse:
        """
        Get a position book snapshot for an instrument.

        The position book partitions open positions into price buckets, each with
        the percentage of long and short positions at that price.

        Args:
            instrument: Instrument enum or string (e.g., InstrumentName.EUR_USD or "EUR_USD")
            time: Snapshot time; the most recent snapshot is returned when omitted

        Returns:
            Dictionary containing the positionBook snapshot

        Raises:
            FiveTwentyError: On API errors
        """
        instrument_str = instrument.value if hasattr(instrument, "value") else instrument
        params: dict[str, str] = {}
        if time is not None:
            params["time"] = format_datetime_for_oanda(time, getattr(self._client, "_datetime_format", "RFC3339"))

        response = await self._client._request(
            "GET",
            f"/instruments/{instrument_str}/positionBook",
            params=params,
        )

        from ..models import PositionBook

        data = response.json()
        return cast(
            "PositionBookResponse",
            ApiResponse({"positionBook": PositionBook.model_validate(data["positionBook"])}),
        )
