"""Unit tests for enhanced pricing endpoints."""

from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock

import pytest

from fivetwenty.endpoints.pricing import PricingEndpoints


class TestEnhancedPricingEndpoints:
    """Test suite for enhanced pricing functionality."""

    @pytest.fixture
    def mock_client(self):
        """Create a mock async client."""
        client = MagicMock()

        def side_effect(method, path, **kwargs):
            """Return different responses based on endpoint."""
            mock_response = MagicMock()

            # Latest candles endpoint
            if "/candles/latest" in path:
                mock_response.json.return_value = {
                    "latestCandles": [
                        {
                            "instrument": "EUR_USD",
                            "granularity": "H1",
                            "candles": [
                                {
                                    "time": "2024-01-15T14:00:00.000000000Z",
                                    "complete": True,
                                    "volume": 100,
                                    "mid": {"o": "1.1000", "h": "1.1050", "l": "1.0950", "c": "1.1025"},
                                }
                            ],
                        }
                    ]
                }
            # Account instrument candles endpoint
            elif "/instruments/" in path and "/candles" in path:
                mock_response.json.return_value = {
                    "instrument": "EUR_USD",
                    "granularity": "S5",
                    "candles": [
                        {
                            "time": "2024-01-15T14:00:00.000000000Z",
                            "complete": True,
                            "volume": 50,
                            "mid": {"o": "1.1000", "h": "1.1010", "l": "1.0995", "c": "1.1005"},
                        }
                    ],
                }
            # Pricing endpoint
            elif "/pricing" in path:
                mock_response.json.return_value = {
                    "prices": [],
                    "time": "2024-01-15T14:30:00.000000000Z",
                    "homeConversions": [],
                }
            else:
                mock_response.json.return_value = {"mock": "data"}

            return mock_response

        client._request = AsyncMock(side_effect=side_effect)
        return client

    @pytest.fixture
    def pricing(self, mock_client):
        """Create PricingEndpoints instance with mock client."""
        return PricingEndpoints(mock_client)

    @pytest.mark.asyncio
    async def test_get_latest_candles_basic(self, pricing, mock_client):
        """Test basic latest candles retrieval."""
        candle_specs = ["EUR_USD:H1:M", "GBP_USD:M15:BA"]

        await pricing.get_latest_candles("101-001-123456-001", candle_specs)

        mock_client._request.assert_called_once_with(
            "GET",
            "/accounts/101-001-123456-001/candles/latest",
            params={
                "candleSpecifications": "EUR_USD:H1:M,GBP_USD:M15:BA",
                "units": "1",
                "smooth": "false",
                "dailyAlignment": "17",
                "alignmentTimezone": "America/New_York",
                "weeklyAlignment": "Friday",
            },
        )

    @pytest.mark.asyncio
    async def test_get_latest_candles_with_units(self, pricing, mock_client):
        """Test latest candles with multiple units."""
        candle_specs = ["USD_JPY:D:M"]

        await pricing.get_latest_candles("101-001-123456-001", candle_specs, units=50, smooth=True)

        mock_client._request.assert_called_once_with(
            "GET",
            "/accounts/101-001-123456-001/candles/latest",
            params={
                "candleSpecifications": "USD_JPY:D:M",
                "units": "50",
                "smooth": "true",
                "dailyAlignment": "17",
                "alignmentTimezone": "America/New_York",
                "weeklyAlignment": "Friday",
            },
        )

    @pytest.mark.asyncio
    async def test_get_latest_candles_custom_alignment(self, pricing, mock_client):
        """Test latest candles with custom alignment."""
        candle_specs = ["AUD_CAD:W:BM"]

        await pricing.get_latest_candles("101-001-123456-001", candle_specs, daily_alignment=0, alignment_timezone="Asia/Tokyo", weekly_alignment="Sunday")

        mock_client._request.assert_called_once_with(
            "GET",
            "/accounts/101-001-123456-001/candles/latest",
            params={
                "candleSpecifications": "AUD_CAD:W:BM",
                "units": "1",
                "smooth": "false",
                "dailyAlignment": "0",
                "alignmentTimezone": "Asia/Tokyo",
                "weeklyAlignment": "Sunday",
            },
        )

    @pytest.mark.asyncio
    async def test_get_latest_candles_empty_specs_raises_error(self, pricing, mock_client):
        """Test that empty candle specifications raises ValueError."""
        with pytest.raises(ValueError, match="Must specify at least one candle specification"):
            await pricing.get_latest_candles("101-001-123456-001", [])

    @pytest.mark.asyncio
    async def test_get_latest_candles_units_out_of_range_raises_error(self, pricing, mock_client):
        """Test that units out of valid range raises ValueError."""
        candle_specs = ["EUR_USD:H1:M"]

        with pytest.raises(ValueError, match="Units must be between 1 and 5000"):
            await pricing.get_latest_candles("101-001-123456-001", candle_specs, units=0)

        with pytest.raises(ValueError, match="Units must be between 1 and 5000"):
            await pricing.get_latest_candles("101-001-123456-001", candle_specs, units=5001)

    @pytest.mark.asyncio
    async def test_get_pricing_with_datetime_since(self, pricing, mock_client):
        """Test pricing retrieval with datetime since parameter."""
        since_time = datetime(2024, 1, 15, 14, 30, 0, tzinfo=timezone.utc)

        # Mock response with required fields
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "prices": [],
            "time": "2024-01-15T14:30:00.000000000Z",
            "homeConversions": [],
        }
        mock_client._request = AsyncMock(return_value=mock_response)

        await pricing.get_pricing("101-001-123456-001", ["EUR_USD", "GBP_USD"], since=since_time.isoformat(), include_home_conversions=True)

        mock_client._request.assert_called_once_with(
            "GET",
            "/accounts/101-001-123456-001/pricing",
            params={
                "instruments": "EUR_USD,GBP_USD",
                "includeUnitsAvailable": "true",
                "includeHomeConversions": "true",
                "since": since_time.isoformat(),
            },
        )

    @pytest.mark.asyncio
    async def test_comprehensive_candle_specifications(self, pricing, mock_client):
        """Test comprehensive candle specifications with all price types."""
        candle_specs = [
            "EUR_USD:H1:M",  # Mid prices
            "GBP_USD:M30:B",  # Bid prices
            "USD_JPY:M15:A",  # Ask prices
            "AUD_USD:H4:BA",  # Bid and Ask
            "USD_CAD:D:BM",  # Bid and Mid
            "EUR_GBP:W:AM",  # Ask and Mid
            "NZD_USD:M:BAM",  # All prices
        ]

        await pricing.get_latest_candles("101-001-123456-001", candle_specs, units=10)

        expected_specs = ",".join(candle_specs)
        mock_client._request.assert_called_once_with(
            "GET",
            "/accounts/101-001-123456-001/candles/latest",
            params={
                "candleSpecifications": expected_specs,
                "units": "10",
                "smooth": "false",
                "dailyAlignment": "17",
                "alignmentTimezone": "America/New_York",
                "weeklyAlignment": "Friday",
            },
        )

    @pytest.mark.asyncio
    async def test_get_account_candles_basic(self, pricing, mock_client):
        """Test basic account-specific candle data retrieval."""
        await pricing.get_account_instrument_candles("101-001-123456-001", "EUR_USD")

        mock_client._request.assert_called_once_with(
            "GET",
            "/accounts/101-001-123456-001/instruments/EUR_USD/candles",
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
    async def test_get_account_candles_with_count(self, pricing, mock_client):
        """Test account-specific candle retrieval with count parameter."""
        await pricing.get_account_instrument_candles("101-001-123456-001", "GBP_USD", count=200, granularity="H1", price="BA")

        mock_client._request.assert_called_once_with(
            "GET",
            "/accounts/101-001-123456-001/instruments/GBP_USD/candles",
            params={
                "price": "BA",
                "granularity": "H1",
                "count": "200",
                "smooth": "false",
                "dailyAlignment": "17",
                "alignmentTimezone": "America/New_York",
                "weeklyAlignment": "Friday",
            },
        )

    @pytest.mark.asyncio
    async def test_get_account_candles_with_time_range(self, pricing, mock_client):
        """Test account-specific candle retrieval with time range."""
        from_time = datetime(2024, 2, 1, 10, 0, 0, tzinfo=timezone.utc)
        to_time = datetime(2024, 2, 1, 18, 0, 0, tzinfo=timezone.utc)

        await pricing.get_account_instrument_candles("101-001-123456-001", "USD_JPY", from_time=from_time, to_time=to_time, granularity="M30", smooth=True)

        mock_client._request.assert_called_once_with(
            "GET",
            "/accounts/101-001-123456-001/instruments/USD_JPY/candles",
            params={
                "price": "M",
                "granularity": "M30",
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
    async def test_get_account_candles_count_too_high_raises_error(self, pricing, mock_client):
        """Test that count > 5000 raises ValueError for account candles."""
        with pytest.raises(ValueError, match="Count cannot exceed 5000"):
            await pricing.get_account_instrument_candles("101-001-123456-001", "EUR_USD", count=5001)

    @pytest.mark.asyncio
    async def test_get_account_candles_count_and_time_raises_error(self, pricing, mock_client):
        """Test that specifying both count and time range raises ValueError for account candles."""
        from_time = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        with pytest.raises(ValueError, match="Cannot specify both count and time range"):
            await pricing.get_account_instrument_candles("101-001-123456-001", "EUR_USD", count=100, from_time=from_time)

    @pytest.mark.asyncio
    async def test_pricing_responses_support_compatibility_access(self, pricing):
        """Test pricing endpoint responses support attribute and snake_case access."""
        pricing_response = await pricing.get_pricing("101-001-123456-001", ["EUR_USD"], include_home_conversions=True)

        assert pricing_response.time == "2024-01-15T14:30:00.000000000Z"
        assert pricing_response.home_conversions == []
        assert pricing_response["home_conversions"] == []

        candles_response = await pricing.get_account_instrument_candles("101-001-123456-001", "EUR_USD")

        assert candles_response.instrument == "EUR_USD"
        assert candles_response.granularity == "S5"

        latest_response = await pricing.get_latest_candles("101-001-123456-001", ["EUR_USD:H1:M"])

        assert latest_response.latest_candles[0].instrument == "EUR_USD"


class TestPricingStreamParams:
    """Stream request parameter contract."""

    @pytest.mark.asyncio
    async def test_snapshot_false_sent_explicitly(self):
        """snapshot=False must be sent — omitting it would fall back to the server default (true)."""
        captured: dict = {}

        async def fake_stream(path, *, params=None, stall_timeout=30.0):
            captured["path"] = path
            captured["params"] = params
            if False:  # pragma: no cover - makes this an async generator
                yield ""

        client = MagicMock()
        client._stream = fake_stream
        pricing = PricingEndpoints(client)

        async for _ in pricing.get_pricing_stream("101-001-123456-001", ["EUR_USD"], snapshot=False):
            pass

        assert captured["params"]["snapshot"] == "false"
        assert captured["params"]["instruments"] == "EUR_USD"

    @pytest.mark.asyncio
    async def test_unknown_instrument_in_candles_response_tolerated(self):
        """Open InstrumentName: candle responses for instruments outside the enum must parse."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "instrument": "XPT_USD_EXOTIC",
            "granularity": "S5",
            "candles": [],
        }
        client = MagicMock()
        client._request = AsyncMock(return_value=mock_response)
        pricing = PricingEndpoints(client)

        result = await pricing.get_account_instrument_candles("101-001-123456-001", "XPT_USD_EXOTIC")

        assert result["instrument"] == "XPT_USD_EXOTIC"
