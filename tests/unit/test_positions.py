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

        # Create a side effect function that returns appropriate responses based on the request
        async def mock_request(method, path, **kwargs):
            mock_response = MagicMock()

            # For GET /accounts/{id}/positions - list all positions
            if (method == "GET" and path.endswith("/positions")) or (method == "GET" and "/openPositions" in path):
                mock_response.json.return_value = {
                    "positions": [
                        {
                            "instrument": "EUR_USD",
                            "pl": "100.0000",
                            "unrealizedPL": "50.0000",
                            "marginUsed": "200.0000",
                            "resettablePL": "100.0000",
                            "financing": "1.0000",
                            "commission": "0.5000",
                            "dividendAdjustment": "0.0000",
                            "guaranteedExecutionFees": "0.0000",
                            "long": {
                                "units": "1000",
                                "averagePrice": "1.10000",
                                "tradeIDs": ["12345"],
                                "pl": "50.0000",
                                "unrealizedPL": "25.0000",
                                "resettablePL": "50.0000",
                                "financing": "0.5000",
                                "dividendAdjustment": "0.0000",
                                "guaranteedExecutionFees": "0.0000",
                            },
                            "short": {
                                "units": "0",
                                "averagePrice": None,
                                "tradeIDs": [],
                                "pl": "0.0000",
                                "unrealizedPL": "0.0000",
                                "resettablePL": "0.0000",
                                "financing": "0.0000",
                                "dividendAdjustment": "0.0000",
                                "guaranteedExecutionFees": "0.0000",
                            },
                        }
                    ],
                    "lastTransactionID": "12346",
                }
            # For GET /accounts/{id}/positions/{instrument} - get specific position
            elif method == "GET" and "/positions/" in path:
                mock_response.json.return_value = {
                    "position": {
                        "instrument": "EUR_USD",
                        "pl": "100.0000",
                        "unrealizedPL": "50.0000",
                        "marginUsed": "200.0000",
                        "resettablePL": "100.0000",
                        "financing": "1.0000",
                        "commission": "0.5000",
                        "dividendAdjustment": "0.0000",
                        "guaranteedExecutionFees": "0.0000",
                        "long": {
                            "units": "1000",
                            "averagePrice": "1.10000",
                            "tradeIDs": ["12345"],
                            "pl": "50.0000",
                            "unrealizedPL": "25.0000",
                            "resettablePL": "50.0000",
                            "financing": "0.5000",
                            "dividendAdjustment": "0.0000",
                            "guaranteedExecutionFees": "0.0000",
                        },
                        "short": {
                            "units": "0",
                            "averagePrice": None,
                            "tradeIDs": [],
                            "pl": "0.0000",
                            "unrealizedPL": "0.0000",
                            "resettablePL": "0.0000",
                            "financing": "0.0000",
                            "dividendAdjustment": "0.0000",
                            "guaranteedExecutionFees": "0.0000",
                        },
                    },
                    "lastTransactionID": "12346",
                }
            # For PUT /accounts/{id}/positions/{instrument}/close - close position
            elif method == "PUT" and "/close" in path:
                mock_response.json.return_value = {
                    "longOrderCreateTransaction": {
                        "id": "12346",
                        "type": "MARKET_ORDER",
                        "time": "2024-01-01T00:00:00.000000000Z",
                        "userID": 1,
                        "accountID": "101-001-123456-001",
                        "batchID": "12346",
                        "requestID": "12346",
                        "instrument": "EUR_USD",
                        "units": "-1000",
                        "timeInForce": "FOK",
                        "positionFill": "REDUCE_ONLY",
                        "reason": "POSITION_CLOSEOUT",
                    },
                    "longOrderFillTransaction": {
                        "id": "12347",
                        "type": "ORDER_FILL",
                        "time": "2024-01-01T00:00:00.000000000Z",
                        "userID": 1,
                        "accountID": "101-001-123456-001",
                        "batchID": "12347",
                        "requestID": "12347",
                        "orderID": "12346",
                        "instrument": "EUR_USD",
                        "units": "-1000",
                        "price": "1.10000",
                        "pl": "100.0000",
                        "financing": "0.0000",
                        "commission": "0.0000",
                        "accountBalance": "100100.0000",
                        "reason": "MARKET_ORDER_POSITION_CLOSEOUT",
                    },
                    "relatedTransactionIDs": ["12346", "12347"],
                    "lastTransactionID": "12347",
                }
            else:
                mock_response.json.return_value = {"mock": "data"}

            return mock_response

        client._request = AsyncMock(side_effect=mock_request)
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

    @pytest.mark.asyncio
    async def test_position_responses_support_compatibility_access(self, positions):
        """Test position endpoint responses support attribute and nested model access."""
        position_response = await positions.get_position("101-001-123456-001", "EUR_USD")

        assert position_response.last_transaction_id == "12346"
        assert position_response["last_transaction_id"] == "12346"
        assert position_response["instrument"] == "EUR_USD"
        assert position_response.position.get("marginUsed") == "200.0000"

        close_response = await positions.close_position("101-001-123456-001", "EUR_USD", long_units="ALL")

        assert close_response.long_order_fill_transaction.id == "12347"
        assert close_response["long_order_fill_transaction"].id == "12347"
