"""Tests for position endpoints."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from fivetwenty.endpoints.positions import PositionEndpoints
from fivetwenty.models import AccountID, InstrumentName


class TestPositionEndpoints:
    """Test suite for PositionEndpoints."""

    @pytest.fixture
    def mock_client(self):
        """Create a mock async client."""
        client = MagicMock()
        mock_response = MagicMock()
        mock_response.json.return_value = {"mock": "data"}
        client._request = AsyncMock(return_value=mock_response)
        return client

    @pytest.fixture
    def positions(self, mock_client):
        """Create PositionEndpoints instance with mock client."""
        return PositionEndpoints(mock_client)

    @pytest.mark.asyncio
    async def test_list_all_positions(self, positions, mock_client):
        """Test listing all positions for an account."""
        await positions.get_positions("101-001-123456-001")
        mock_client._request.assert_called_once_with("GET", "/accounts/101-001-123456-001/positions")

    @pytest.mark.asyncio
    async def test_list_open_positions(self, positions, mock_client):
        """Test listing only open positions."""
        await positions.get_open_positions("101-001-123456-001")
        mock_client._request.assert_called_once_with("GET", "/accounts/101-001-123456-001/openPositions")

    @pytest.mark.asyncio
    async def test_get_position_for_instrument(self, positions, mock_client):
        """Test getting position for specific instrument."""
        await positions.get_position("101-001-123456-001", "EUR_USD")
        mock_client._request.assert_called_once_with("GET", "/accounts/101-001-123456-001/positions/EUR_USD")

    @pytest.mark.asyncio
    async def test_get_position_with_instrument_name_enum(self, positions, mock_client):
        """Test getting position using InstrumentName enum."""
        await positions.get_position("101-001-123456-001", InstrumentName.EUR_USD)
        mock_client._request.assert_called_once_with("GET", "/accounts/101-001-123456-001/positions/EUR_USD")

    @pytest.mark.asyncio
    async def test_close_position_all_long(self, positions, mock_client):
        """Test closing entire long position."""
        await positions.close_position("101-001-123456-001", "EUR_USD", long_units="ALL")
        mock_client._request.assert_called_once_with("PUT", "/accounts/101-001-123456-001/positions/EUR_USD/close", json_data={"longUnits": "ALL"})

    @pytest.mark.asyncio
    async def test_close_position_all_short(self, positions, mock_client):
        """Test closing entire short position."""
        await positions.close_position("101-001-123456-001", "EUR_USD", short_units="ALL")
        mock_client._request.assert_called_once_with("PUT", "/accounts/101-001-123456-001/positions/EUR_USD/close", json_data={"shortUnits": "ALL"})

    @pytest.mark.asyncio
    async def test_close_position_partial_long(self, positions, mock_client):
        """Test closing partial long position with specific units."""
        await positions.close_position("101-001-123456-001", "EUR_USD", long_units="1000")
        mock_client._request.assert_called_once_with("PUT", "/accounts/101-001-123456-001/positions/EUR_USD/close", json_data={"longUnits": "1000"})

    @pytest.mark.asyncio
    async def test_close_position_partial_short(self, positions, mock_client):
        """Test closing partial short position with specific units."""
        await positions.close_position("101-001-123456-001", "EUR_USD", short_units="500")
        mock_client._request.assert_called_once_with("PUT", "/accounts/101-001-123456-001/positions/EUR_USD/close", json_data={"shortUnits": "500"})

    @pytest.mark.asyncio
    async def test_close_position_both_sides(self, positions, mock_client):
        """Test closing both long and short positions simultaneously."""
        await positions.close_position("101-001-123456-001", "EUR_USD", long_units="ALL", short_units="500")
        mock_client._request.assert_called_once_with("PUT", "/accounts/101-001-123456-001/positions/EUR_USD/close", json_data={"longUnits": "ALL", "shortUnits": "500"})

    @pytest.mark.asyncio
    async def test_close_position_with_none_directive(self, positions, mock_client):
        """Test closing position with NONE directive (leave unchanged)."""
        await positions.close_position("101-001-123456-001", "EUR_USD", long_units="NONE", short_units="ALL")
        mock_client._request.assert_called_once_with("PUT", "/accounts/101-001-123456-001/positions/EUR_USD/close", json_data={"longUnits": "NONE", "shortUnits": "ALL"})

    @pytest.mark.asyncio
    async def test_close_position_with_decimal_number(self, positions, mock_client):
        """Test closing position with Decimal object."""
        from decimal import Decimal

        decimal_units = Decimal("1250.50")
        await positions.close_position("101-001-123456-001", "EUR_USD", long_units=decimal_units)
        mock_client._request.assert_called_once_with("PUT", "/accounts/101-001-123456-001/positions/EUR_USD/close", json_data={"longUnits": "1250.50"})

    @pytest.mark.asyncio
    async def test_close_position_no_units_specified_raises_error(self, positions, mock_client):
        """Test that ValueError is raised when no units specified."""
        with pytest.raises(ValueError, match="Must specify at least one of long_units or short_units"):
            await positions.close_position("101-001-123456-001", "EUR_USD")

    @pytest.mark.asyncio
    async def test_close_position_invalid_string_long_units_raises_error(self, positions, mock_client):
        """Test that ValueError is raised for invalid string units."""
        with pytest.raises(ValueError, match="long_units string must be 'ALL', 'NONE', or a numeric value"):
            await positions.close_position("101-001-123456-001", "EUR_USD", long_units="INVALID")

    @pytest.mark.asyncio
    async def test_close_position_invalid_string_short_units_raises_error(self, positions, mock_client):
        """Test that ValueError is raised for invalid string units."""
        with pytest.raises(ValueError, match="short_units string must be 'ALL', 'NONE', or a numeric value"):
            await positions.close_position("101-001-123456-001", "EUR_USD", short_units="PARTIAL")

    @pytest.mark.asyncio
    async def test_list_with_account_id_type(self, positions, mock_client):
        """Test list with AccountID type."""
        account_id = AccountID("101-001-123456-001")
        await positions.get_positions(account_id)
        mock_client._request.assert_called_once_with("GET", "/accounts/101-001-123456-001/positions")

    @pytest.mark.asyncio
    async def test_list_open_with_account_id_type(self, positions, mock_client):
        """Test list_open with AccountID type."""
        account_id = AccountID("101-001-123456-001")
        await positions.get_open_positions(account_id)
        mock_client._request.assert_called_once_with("GET", "/accounts/101-001-123456-001/openPositions")

    @pytest.mark.asyncio
    async def test_get_with_account_id_and_instrument_types(self, positions, mock_client):
        """Test get with proper type objects."""
        account_id = AccountID("101-001-123456-001")
        instrument = InstrumentName.GBP_USD
        await positions.get_position(account_id, instrument)
        mock_client._request.assert_called_once_with("GET", "/accounts/101-001-123456-001/positions/GBP_USD")

    @pytest.mark.asyncio
    async def test_close_with_type_objects(self, positions, mock_client):
        """Test close with proper type objects."""
        account_id = AccountID("101-001-123456-001")
        instrument = InstrumentName.USD_JPY
        await positions.close_position(account_id, instrument, long_units="ALL")
        mock_client._request.assert_called_once_with("PUT", "/accounts/101-001-123456-001/positions/USD_JPY/close", json_data={"longUnits": "ALL"})
