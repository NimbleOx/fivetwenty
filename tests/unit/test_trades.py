"""Unit tests for trade endpoints."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from fivetwenty.endpoints.trades import TradeEndpoints
from fivetwenty.models import TradeStateFilter


class TestTradeEndpoints:
    """Test trade management endpoints."""

    @pytest.fixture
    def mock_client(self):
        """Create a mock async client."""
        client = MagicMock()
        client._request = AsyncMock()
        return client

    @pytest.fixture
    def trades(self, mock_client):
        """Create TradeEndpoints instance."""
        return TradeEndpoints(mock_client)

    @pytest.mark.asyncio
    async def test_list_trades_basic(self, trades, mock_client):
        """Test basic trade listing."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "trades": [
                {
                    "id": "12345",
                    "instrument": "EUR_USD",
                    "price": "1.1000",
                    "openTime": "2024-01-01T00:00:00.000000000Z",
                    "state": "OPEN",
                    "initialUnits": "1000",
                    "initialMarginRequired": "33.00",
                    "currentUnits": "1000",
                    "realizedPL": "0.00000",
                    "unrealizedPL": "5.00000",
                    "marginUsed": "33.00",
                }
            ],
            "lastTransactionID": "12346",
        }
        mock_client._request.return_value = mock_response

        result = await trades.get_trades("101-001-123456-001")

        mock_client._request.assert_called_once_with(
            "GET",
            "/accounts/101-001-123456-001/trades",
            params={
                "state": "OPEN",
                "count": 50,
            },
        )
        assert result["trades"][0].id == "12345"
        assert result["lastTransactionID"] == "12346"

    @pytest.mark.asyncio
    async def test_list_trades_with_filters(self, trades, mock_client):
        """Test trade listing with filters."""
        mock_response = MagicMock()
        mock_response.json.return_value = {"trades": [], "lastTransactionID": "12346"}
        mock_client._request.return_value = mock_response

        await trades.get_trades(
            "101-001-123456-001",
            ids=["12345", "12346"],
            state=TradeStateFilter.CLOSED,
            instrument="EUR_USD",
            count=100,
            before_id="12340",
        )

        mock_client._request.assert_called_once_with(
            "GET",
            "/accounts/101-001-123456-001/trades",
            params={
                "ids": "12345,12346",
                "state": "CLOSED",
                "instrument": "EUR_USD",
                "count": 100,
                "beforeID": "12340",
            },
        )

    @pytest.mark.asyncio
    async def test_list_trades_count_limit(self, trades, mock_client):
        """Test that trade count is limited to maximum of 500."""
        mock_response = MagicMock()
        mock_response.json.return_value = {"trades": [], "lastTransactionID": "12346"}
        mock_client._request.return_value = mock_response

        await trades.get_trades("101-001-123456-001", count=1000)  # Over limit

        mock_client._request.assert_called_once_with(
            "GET",
            "/accounts/101-001-123456-001/trades",
            params={
                "state": "OPEN",
                "count": 500,  # Should be capped at 500
            },
        )

    @pytest.mark.asyncio
    async def test_list_open_trades(self, trades, mock_client):
        """Test listing open trades."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "trades": [
                {
                    "id": "12345",
                    "instrument": "EUR_USD",
                    "price": "1.1000",
                    "openTime": "2024-01-01T00:00:00.000000000Z",
                    "state": "OPEN",
                    "initialUnits": "1000",
                    "initialMarginRequired": "33.00",
                    "currentUnits": "1000",
                    "realizedPL": "0.00000",
                    "unrealizedPL": "5.00000",
                    "marginUsed": "33.00",
                }
            ],
            "lastTransactionID": "12346",
        }
        mock_client._request.return_value = mock_response

        result = await trades.get_open_trades("101-001-123456-001")

        mock_client._request.assert_called_once_with(
            "GET",
            "/accounts/101-001-123456-001/openTrades",
        )
        assert result["trades"][0].id == "12345"

    @pytest.mark.asyncio
    async def test_get_trade_by_id(self, trades, mock_client):
        """Test getting trade by ID."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "trade": {
                "id": "12345",
                "instrument": "EUR_USD",
                "price": "1.1000",
                "openTime": "2024-01-01T00:00:00.000000000Z",
                "state": "OPEN",
                "initialUnits": "1000",
                "initialMarginRequired": "33.00",
                "currentUnits": "1000",
                "realizedPL": "0.00000",
                "unrealizedPL": "5.00000",
                "marginUsed": "33.00",
            },
            "lastTransactionID": "12346",
        }
        mock_client._request.return_value = mock_response

        result = await trades.get_trade("101-001-123456-001", "12345")

        mock_client._request.assert_called_once_with(
            "GET",
            "/accounts/101-001-123456-001/trades/12345",
        )
        assert result["trade"].id == "12345"

    @pytest.mark.asyncio
    async def test_get_trade_by_client_id(self, trades, mock_client):
        """Test getting trade by client ID."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "trade": {
                "id": "12345",
                "instrument": "EUR_USD",
                "price": "1.1000",
                "openTime": "2024-01-01T00:00:00.000000000Z",
                "state": "OPEN",
                "initialUnits": "1000",
                "initialMarginRequired": "33.00",
                "currentUnits": "1000",
                "realizedPL": "0.00000",
                "unrealizedPL": "5.00000",
                "marginUsed": "33.00",
            },
            "lastTransactionID": "12346",
        }
        mock_client._request.return_value = mock_response

        await trades.get_trade("101-001-123456-001", "@my_trade_id")

        mock_client._request.assert_called_once_with(
            "GET",
            "/accounts/101-001-123456-001/trades/@my_trade_id",
        )

    @pytest.mark.asyncio
    async def test_close_trade_full(self, trades, mock_client):
        """Test closing trade completely."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "orderCreateTransaction": {
                "id": "12346",
                "type": "MARKET_ORDER",
                "accountID": "101-001-123456-001",
                "time": "2024-01-01T00:00:00.000000000Z",
                "userID": 123456,
                "batchID": "12346",
                "requestID": "12346",
                "instrument": "EUR_USD",
                "units": "1000",
                "timeInForce": "FOK",
                "positionFill": "DEFAULT",
                "reason": "TRADE_CLOSE",
            },
            "orderFillTransaction": {
                "id": "12347",
                "type": "ORDER_FILL",
                "accountID": "101-001-123456-001",
                "time": "2024-01-01T00:00:00.000000000Z",
                "userID": 123456,
                "batchID": "12347",
                "requestID": "12347",
                "orderID": "12346",
                "instrument": "EUR_USD",
                "units": "1000",
                "price": "1.1000",
                "pl": "0.0000",
                "financing": "0.0000",
                "commission": "0.0000",
                "accountBalance": "10000.0000",
                "tradesClosed": [{"tradeID": "12345", "units": "1000", "price": "1.1000", "realizedPL": "5.0000"}],
                "reason": "MARKET_ORDER",
            },
            "relatedTransactionIDs": ["12346", "12347"],
            "lastTransactionID": "12347",
        }
        mock_client._request.return_value = mock_response

        result = await trades.close_trade("101-001-123456-001", "12345")

        mock_client._request.assert_called_once_with(
            "PUT",
            "/accounts/101-001-123456-001/trades/12345/close",
            json_data=None,
            headers={},
        )
        assert result["orderFillTransaction"].id == "12347"

    @pytest.mark.asyncio
    async def test_close_trade_partial(self, trades, mock_client):
        """Test partially closing trade."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "orderCreateTransaction": {
                "id": "12346",
                "type": "MARKET_ORDER",
                "accountID": "101-001-123456-001",
                "time": "2024-01-01T00:00:00.000000000Z",
                "userID": 123456,
                "batchID": "12346",
                "requestID": "12346",
                "instrument": "EUR_USD",
                "units": "500",
                "timeInForce": "FOK",
                "positionFill": "DEFAULT",
                "reason": "TRADE_CLOSE",
            },
            "orderFillTransaction": {
                "id": "12347",
                "type": "ORDER_FILL",
                "accountID": "101-001-123456-001",
                "time": "2024-01-01T00:00:00.000000000Z",
                "userID": 123456,
                "batchID": "12347",
                "requestID": "12347",
                "orderID": "12346",
                "instrument": "EUR_USD",
                "units": "500",
                "price": "1.1000",
                "pl": "0.0000",
                "financing": "0.0000",
                "commission": "0.0000",
                "accountBalance": "10000.0000",
                "tradeReduced": {"tradeID": "12345", "units": "500", "price": "1.1000", "realizedPL": "2.5000"},
                "reason": "MARKET_ORDER",
            },
            "relatedTransactionIDs": ["12346", "12347"],
            "lastTransactionID": "12347",
        }
        mock_client._request.return_value = mock_response

        await trades.close_trade("101-001-123456-001", "12345", units="500", idempotency_key="close-trade-12345")

        mock_client._request.assert_called_once_with(
            "PUT",
            "/accounts/101-001-123456-001/trades/12345/close",
            json_data={"units": "500"},
            headers={"ClientRequestID": "close-trade-12345"},
        )

    @pytest.mark.asyncio
    async def test_update_client_extensions(self, trades, mock_client):
        """Test updating trade client extensions."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "tradeClientExtensionsModifyTransaction": {
                "id": "12347",
                "type": "TRADE_CLIENT_EXTENSIONS_MODIFY",
                "accountID": "101-001-123456-001",
                "time": "2024-01-01T00:00:00.000000000Z",
                "userID": 123456,
                "batchID": "12347",
                "requestID": "12347",
                "tradeID": "12345",
                "clientTradeID": "my_trade",
                "tradeClientExtensionsModify": {"id": "my_trade", "tag": "long_eur_usd", "comment": "Monthly EUR/USD position"},
            },
            "lastTransactionID": "12347",
        }
        mock_client._request.return_value = mock_response

        extensions = {"id": "my_trade", "tag": "long_eur_usd", "comment": "Monthly EUR/USD position"}

        await trades.put_trade_client_extensions("101-001-123456-001", "12345", client_extensions=extensions, idempotency_key="update-ext-12345")

        mock_client._request.assert_called_once_with(
            "PUT",
            "/accounts/101-001-123456-001/trades/12345/clientExtensions",
            json_data={"clientExtensions": extensions},
            headers={"ClientRequestID": "update-ext-12345"},
        )

    @pytest.mark.asyncio
    async def test_update_client_extensions_empty(self, trades, mock_client):
        """Test updating trade client extensions with no extensions."""
        mock_response = MagicMock()
        mock_response.json.return_value = {"lastTransactionID": "12347"}
        mock_client._request.return_value = mock_response

        await trades.put_trade_client_extensions("101-001-123456-001", "12345")

        mock_client._request.assert_called_once_with(
            "PUT",
            "/accounts/101-001-123456-001/trades/12345/clientExtensions",
            json_data={},
            headers={},
        )

    @pytest.mark.asyncio
    async def test_update_orders_take_profit(self, trades, mock_client):
        """Test updating take profit order for trade."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "takeProfitOrderTransaction": {
                "id": "12347",
                "type": "TAKE_PROFIT_ORDER",
                "accountID": "101-001-123456-001",
                "time": "2024-01-01T00:00:00.000000000Z",
                "userID": 123456,
                "batchID": "12347",
                "requestID": "12347",
                "tradeID": "12345",
                "price": "1.1100",
                "timeInForce": "GTC",
                "triggerCondition": "DEFAULT",
                "reason": "CLIENT_ORDER",
            },
            "lastTransactionID": "12347",
        }
        mock_client._request.return_value = mock_response

        take_profit = {"price": "1.1100", "timeInForce": "GTC"}

        await trades.put_trade_orders("101-001-123456-001", "12345", take_profit=take_profit, idempotency_key="update-tp-12345")

        mock_client._request.assert_called_once_with(
            "PUT",
            "/accounts/101-001-123456-001/trades/12345/orders",
            json_data={"takeProfit": take_profit},
            headers={"ClientRequestID": "update-tp-12345"},
        )

    @pytest.mark.asyncio
    async def test_update_orders_stop_loss(self, trades, mock_client):
        """Test updating stop loss order for trade."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "stopLossOrderTransaction": {
                "id": "12347",
                "type": "STOP_LOSS_ORDER",
                "accountID": "101-001-123456-001",
                "time": "2024-01-01T00:00:00.000000000Z",
                "userID": 123456,
                "batchID": "12347",
                "requestID": "12347",
                "tradeID": "12345",
                "price": "1.0900",
                "timeInForce": "GTC",
                "triggerCondition": "DEFAULT",
                "reason": "CLIENT_ORDER",
            },
            "lastTransactionID": "12347",
        }
        mock_client._request.return_value = mock_response

        stop_loss = {"price": "1.0900", "timeInForce": "GTC"}

        await trades.put_trade_orders("101-001-123456-001", "12345", stop_loss=stop_loss)

        mock_client._request.assert_called_once_with(
            "PUT",
            "/accounts/101-001-123456-001/trades/12345/orders",
            json_data={"stopLoss": stop_loss},
            headers={},
        )

    @pytest.mark.asyncio
    async def test_update_orders_trailing_stop_loss(self, trades, mock_client):
        """Test updating trailing stop loss order for trade."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "trailingStopLossOrderTransaction": {
                "id": "12347",
                "type": "TRAILING_STOP_LOSS_ORDER",
                "accountID": "101-001-123456-001",
                "time": "2024-01-01T00:00:00.000000000Z",
                "userID": 123456,
                "batchID": "12347",
                "requestID": "12347",
                "tradeID": "12345",
                "distance": "0.0100",
                "timeInForce": "GTC",
                "triggerCondition": "DEFAULT",
                "reason": "CLIENT_ORDER",
            },
            "lastTransactionID": "12347",
        }
        mock_client._request.return_value = mock_response

        trailing_stop_loss = {"distance": "0.0100", "timeInForce": "GTC"}

        await trades.put_trade_orders("101-001-123456-001", "12345", trailing_stop_loss=trailing_stop_loss)

        mock_client._request.assert_called_once_with(
            "PUT",
            "/accounts/101-001-123456-001/trades/12345/orders",
            json_data={"trailingStopLoss": trailing_stop_loss},
            headers={},
        )

    @pytest.mark.asyncio
    async def test_update_orders_multiple(self, trades, mock_client):
        """Test updating multiple orders for trade."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "takeProfitOrderTransaction": {
                "id": "12347",
                "type": "TAKE_PROFIT_ORDER",
                "accountID": "101-001-123456-001",
                "time": "2024-01-01T00:00:00.000000000Z",
                "userID": 123456,
                "batchID": "12347",
                "requestID": "12347",
                "tradeID": "12345",
                "price": "1.1100",
                "timeInForce": "GTC",
                "triggerCondition": "DEFAULT",
                "reason": "CLIENT_ORDER",
            },
            "stopLossOrderTransaction": {
                "id": "12348",
                "type": "STOP_LOSS_ORDER",
                "accountID": "101-001-123456-001",
                "time": "2024-01-01T00:00:00.000000000Z",
                "userID": 123456,
                "batchID": "12348",
                "requestID": "12348",
                "tradeID": "12345",
                "price": "1.0900",
                "timeInForce": "GTC",
                "triggerCondition": "DEFAULT",
                "reason": "CLIENT_ORDER",
            },
            "lastTransactionID": "12348",
        }
        mock_client._request.return_value = mock_response

        take_profit = {"price": "1.1100", "timeInForce": "GTC"}
        stop_loss = {"price": "1.0900", "timeInForce": "GTC"}

        await trades.put_trade_orders("101-001-123456-001", "12345", take_profit=take_profit, stop_loss=stop_loss)

        mock_client._request.assert_called_once_with(
            "PUT",
            "/accounts/101-001-123456-001/trades/12345/orders",
            json_data={"takeProfit": take_profit, "stopLoss": stop_loss},
            headers={},
        )

    @pytest.mark.asyncio
    async def test_update_orders_cancel_orders(self, trades, mock_client):
        """Test canceling orders by passing None."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "takeProfitOrderCancelTransaction": {
                "id": "12347",
                "type": "ORDER_CANCEL",
                "accountID": "101-001-123456-001",
                "time": "2024-01-01T00:00:00.000000000Z",
                "userID": 123456,
                "batchID": "12347",
                "requestID": "12347",
                "orderID": "12346",
                "reason": "CLIENT_REQUEST",
            },
            "lastTransactionID": "12347",
        }
        mock_client._request.return_value = mock_response

        # Pass None to cancel take profit order
        await trades.put_trade_orders(
            "101-001-123456-001",
            "12345",
            take_profit=None,  # This should cancel the TP order
        )

        mock_client._request.assert_called_once_with(
            "PUT",
            "/accounts/101-001-123456-001/trades/12345/orders",
            json_data={"takeProfit": None},
            headers={},
        )

    @pytest.mark.asyncio
    async def test_update_orders_guaranteed_stop_loss(self, trades, mock_client):
        """Test updating guaranteed stop loss order for trade."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "guaranteedStopLossOrderTransaction": {
                "id": "12347",
                "type": "GUARANTEED_STOP_LOSS_ORDER",
                "accountID": "101-001-123456-001",
                "time": "2024-01-01T00:00:00.000000000Z",
                "userID": 123456,
                "batchID": "12347",
                "requestID": "12347",
                "tradeID": "12345",
                "price": "1.0850",
                "timeInForce": "GTC",
                "gtdTime": "2024-12-31T23:59:59.000000000Z",
                "triggerCondition": "DEFAULT",
                "guaranteedExecutionPremium": "5.0000",
                "reason": "CLIENT_ORDER",
            },
            "lastTransactionID": "12347",
        }
        mock_client._request.return_value = mock_response

        guaranteed_stop_loss = {"price": "1.0850", "timeInForce": "GTC", "gtdTime": "2024-12-31T23:59:59.000000000Z"}

        await trades.put_trade_orders("101-001-123456-001", "12345", guaranteed_stop_loss=guaranteed_stop_loss)

        mock_client._request.assert_called_once_with(
            "PUT",
            "/accounts/101-001-123456-001/trades/12345/orders",
            json_data={"guaranteedStopLoss": guaranteed_stop_loss},
            headers={},
        )
