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
        mock_response = MagicMock()
        mock_response.json.return_value = {"mock": "data"}
        client._request = AsyncMock(return_value=mock_response)
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
                "includeFirst": "true",
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
                "includeFirst": "true",
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
