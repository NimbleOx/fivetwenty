"""Unit tests for instrument endpoints."""

import typing
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock

import pytest

from fivetwenty.endpoints.instruments import InstrumentEndpoints


class TestInstrumentEndpoints:
    """Test suite for instrument functionality."""

    @pytest.fixture
    def mock_client(self):
        """Create a mock async client."""
        client = MagicMock()
        mock_response = MagicMock()
        # Mock response matching OANDA API structure
        mock_response.json.return_value = {
            "instrument": "EUR_USD",
            "granularity": "S5",
            "candles": [
                {
                    "time": "2024-01-01T12:00:00.000000000Z",
                    "volume": 100,
                    "complete": True,
                    "mid": {"o": "1.10000", "h": "1.10010", "l": "1.09990", "c": "1.10005"},
                }
            ],
        }
        client._request = AsyncMock(return_value=mock_response)
        return client

    @pytest.fixture
    def instruments(self, mock_client):
        """Create InstrumentEndpoints instance with mock client."""
        return InstrumentEndpoints(mock_client)

    @pytest.mark.asyncio
    async def test_get_candles_basic(self, instruments, mock_client):
        """Test basic candle data retrieval."""
        from fivetwenty.models import CandlestickGranularity

        await instruments.get_instrument_candles("EUR_USD", granularity=CandlestickGranularity.S5)

        mock_client._request.assert_called_once_with(
            "GET",
            "/instruments/EUR_USD/candles",
            params={
                "price": "M",
                "granularity": "S5",
                "smooth": "false",
                "dailyAlignment": "17",
                "alignmentTimezone": "America/New_York",
                "weeklyAlignment": "Friday",
            },
        )

    @pytest.mark.asyncio
    async def test_get_candles_with_count(self, instruments, mock_client):
        """Test candle retrieval with count parameter."""
        await instruments.get_instrument_candles("GBP_USD", count=100, granularity="H1", price="BA")

        mock_client._request.assert_called_once_with(
            "GET",
            "/instruments/GBP_USD/candles",
            params={
                "price": "BA",
                "granularity": "H1",
                "count": "100",
                "smooth": "false",
                "dailyAlignment": "17",
                "alignmentTimezone": "America/New_York",
                "weeklyAlignment": "Friday",
            },
        )

    @pytest.mark.asyncio
    async def test_get_candles_with_time_range(self, instruments, mock_client):
        """Test candle retrieval with time range."""
        from_time = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        to_time = datetime(2024, 1, 2, 12, 0, 0, tzinfo=timezone.utc)

        await instruments.get_instrument_candles("USD_JPY", from_time=from_time, to_time=to_time, granularity="M15", smooth=True)

        mock_client._request.assert_called_once_with(
            "GET",
            "/instruments/USD_JPY/candles",
            params={
                "price": "M",
                "granularity": "M15",
                "from": from_time.isoformat(),
                "to": to_time.isoformat(),
                "smooth": "true",
                "includeFirst": "true",
                "dailyAlignment": "17",
                "alignmentTimezone": "America/New_York",
                "weeklyAlignment": "Friday",
            },
        )

    @pytest.mark.asyncio
    async def test_get_candles_custom_alignment(self, instruments, mock_client):
        """Test candle retrieval with custom alignment settings."""
        await instruments.get_instrument_candles("AUD_USD", granularity="D", daily_alignment=22, alignment_timezone="Europe/London", weekly_alignment="Monday")

        mock_client._request.assert_called_once_with(
            "GET",
            "/instruments/AUD_USD/candles",
            params={
                "price": "M",
                "granularity": "D",
                "smooth": "false",
                "dailyAlignment": "22",
                "alignmentTimezone": "Europe/London",
                "weeklyAlignment": "Monday",
            },
        )

    @pytest.mark.asyncio
    async def test_get_candles_count_too_high_raises_error(self, instruments, mock_client):
        """Test that count > 5000 raises ValueError."""
        from fivetwenty.models import CandlestickGranularity

        with pytest.raises(ValueError, match="Count cannot exceed 5000"):
            await instruments.get_instrument_candles("EUR_USD", granularity=CandlestickGranularity.H1, count=5001)

    @pytest.mark.asyncio
    async def test_get_candles_count_and_time_raises_error(self, instruments, mock_client):
        """Test that specifying both count and time range raises ValueError."""
        from fivetwenty.models import CandlestickGranularity

        from_time = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        with pytest.raises(ValueError, match="Cannot specify both count and time range"):
            await instruments.get_instrument_candles("EUR_USD", granularity=CandlestickGranularity.H1, count=100, from_time=from_time)

    @pytest.mark.asyncio
    async def test_get_candles_all_price_types(self, instruments, mock_client):
        """Test candle retrieval with all price types."""
        from fivetwenty.models import CandlestickGranularity

        price_types = ["M", "B", "A", "BA", "BM", "AM", "BAM"]

        for price_type in price_types:
            mock_client._request.reset_mock()

            await instruments.get_instrument_candles("EUR_USD", granularity=CandlestickGranularity.S5, price=price_type)

            mock_client._request.assert_called_once_with(
                "GET",
                "/instruments/EUR_USD/candles",
                params={
                    "price": price_type,
                    "granularity": "S5",
                    "smooth": "false",
                    "dailyAlignment": "17",
                    "alignmentTimezone": "America/New_York",
                    "weeklyAlignment": "Friday",
                },
            )

    @pytest.mark.asyncio
    async def test_get_candles_all_granularities(self, instruments, mock_client):
        """Test candle retrieval with all supported granularities."""
        granularities = ["S5", "S10", "S15", "S30", "M1", "M2", "M4", "M5", "M10", "M15", "M30", "H1", "H2", "H3", "H4", "H6", "H8", "H12", "D", "W", "M"]

        for granularity in granularities:
            mock_client._request.reset_mock()

            await instruments.get_instrument_candles("EUR_USD", granularity=granularity)

            mock_client._request.assert_called_once_with(
                "GET",
                "/instruments/EUR_USD/candles",
                params={
                    "price": "M",
                    "granularity": granularity,
                    "smooth": "false",
                    "dailyAlignment": "17",
                    "alignmentTimezone": "America/New_York",
                    "weeklyAlignment": "Friday",
                },
            )

    @pytest.mark.asyncio
    async def test_get_candles_comprehensive_parameters(self, instruments, mock_client):
        """Test candle retrieval with comprehensive parameter set."""
        from_time = datetime(2024, 6, 1, 9, 0, 0, tzinfo=timezone.utc)
        to_time = datetime(2024, 6, 1, 17, 0, 0, tzinfo=timezone.utc)

        await instruments.get_instrument_candles("EUR_GBP", price="BAM", granularity="H4", from_time=from_time, to_time=to_time, smooth=True, include_first=False, daily_alignment=8, alignment_timezone="Asia/Tokyo", weekly_alignment="Sunday")

        mock_client._request.assert_called_once_with(
            "GET",
            "/instruments/EUR_GBP/candles",
            params={
                "price": "BAM",
                "granularity": "H4",
                "from": from_time.isoformat(),
                "to": to_time.isoformat(),
                "smooth": "true",
                "includeFirst": "false",
                "dailyAlignment": "8",
                "alignmentTimezone": "Asia/Tokyo",
                "weeklyAlignment": "Sunday",
            },
        )

    @pytest.mark.asyncio
    async def test_get_candles_edge_case_values(self, instruments, mock_client):
        """Test candle retrieval with edge case parameter values."""
        from fivetwenty.models import CandlestickGranularity

        # Test with maximum count
        await instruments.get_instrument_candles("USD_CHF", granularity=CandlestickGranularity.H1, count=5000)

        # Test with minimum daily alignment
        mock_client._request.reset_mock()
        await instruments.get_instrument_candles("NZD_USD", granularity=CandlestickGranularity.S5, daily_alignment=0)

        # Test with maximum daily alignment
        mock_client._request.reset_mock()
        await instruments.get_instrument_candles("CAD_JPY", granularity=CandlestickGranularity.S5, daily_alignment=23)

        mock_client._request.assert_called_with(
            "GET",
            "/instruments/CAD_JPY/candles",
            params={
                "price": "M",
                "granularity": "S5",
                "smooth": "false",
                "dailyAlignment": "23",
                "alignmentTimezone": "America/New_York",
                "weeklyAlignment": "Friday",
            },
        )

    @pytest.mark.asyncio
    async def test_candle_response_supports_compatibility_access(self, instruments):
        """Test instrument candle responses support attribute access."""
        from fivetwenty.models import CandlestickGranularity, InstrumentName

        response = await instruments.get_instrument_candles("EUR_USD", granularity=CandlestickGranularity.S5)

        assert response.instrument == InstrumentName.EUR_USD
        assert response.granularity == CandlestickGranularity.S5
        assert len(response.candles) == 1


class TestInstrumentCandlesSpecCompliance:
    """Spec-compliance behaviors added in the 0.4.0 accuracy review."""

    @pytest.fixture
    def mock_client(self):
        client = MagicMock()
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "instrument": "EUR_USD",
            "granularity": "S5",
            "candles": [],
        }
        client._request = AsyncMock(return_value=mock_response)
        return client

    @pytest.fixture
    def instruments(self, mock_client):
        return InstrumentEndpoints(mock_client)

    @pytest.mark.asyncio
    async def test_granularity_defaults_to_s5(self, instruments, mock_client):
        """The API default granularity is S5; the SDK matches it."""
        await instruments.get_instrument_candles("EUR_USD")

        params = mock_client._request.call_args.kwargs["params"]
        assert params["granularity"] == "S5"

    @pytest.mark.asyncio
    async def test_unknown_instrument_name_tolerated(self, instruments, mock_client):
        """OANDA defines InstrumentName as an open string; unknown names must not fail."""
        mock_client._request.return_value.json.return_value = {
            "instrument": "XAG_SGD_MINI",
            "granularity": "S5",
            "candles": [],
        }

        result = await instruments.get_instrument_candles("XAG_SGD_MINI")

        assert result["instrument"] == "XAG_SGD_MINI"


class TestOrderBookEndpoints:
    """Order book and position book snapshots (GET /v3/instruments/{instrument}/{order,position}Book)."""

    BOOK_PAYLOAD: typing.ClassVar[dict] = {
        "instrument": "EUR_USD",
        "time": "2026-08-17T04:40:00Z",
        "unixTime": "1786941600",
        "price": "1.15865",
        "bucketWidth": "0.00050",
        "buckets": [
            {"price": "1.15850", "longCountPercent": "0.6708", "shortCountPercent": "0.5361"},
            {"price": "1.15900", "longCountPercent": "1.2000", "shortCountPercent": "0.1000"},
        ],
    }

    @pytest.fixture
    def mock_client(self):
        client = MagicMock()
        client._request = AsyncMock(return_value=MagicMock())
        return client

    @pytest.fixture
    def instruments(self, mock_client):
        return InstrumentEndpoints(mock_client)

    @pytest.mark.asyncio
    async def test_get_order_book(self, instruments, mock_client):
        from decimal import Decimal

        from fivetwenty.models import OrderBook, OrderBookBucket

        mock_client._request.return_value.json.return_value = {"orderBook": self.BOOK_PAYLOAD}

        result = await instruments.get_instrument_order_book("EUR_USD")

        mock_client._request.assert_called_once_with("GET", "/instruments/EUR_USD/orderBook", params={})
        book = result["orderBook"]
        assert isinstance(book, OrderBook)
        assert isinstance(book.buckets[0], OrderBookBucket)
        assert book.buckets[0].long_count_percent == Decimal("0.6708")
        assert book.bucket_width == Decimal("0.00050")

    @pytest.mark.asyncio
    async def test_get_position_book_with_time(self, instruments, mock_client):
        from fivetwenty.models import PositionBook

        mock_client._request.return_value.json.return_value = {"positionBook": self.BOOK_PAYLOAD}
        snapshot_time = datetime(2026, 8, 17, 4, 40, tzinfo=timezone.utc)

        result = await instruments.get_instrument_position_book("EUR_USD", time=snapshot_time)

        mock_client._request.assert_called_once_with(
            "GET",
            "/instruments/EUR_USD/positionBook",
            params={"time": snapshot_time.isoformat()},
        )
        assert isinstance(result["positionBook"], PositionBook)
        assert len(result["positionBook"].buckets) == 2
