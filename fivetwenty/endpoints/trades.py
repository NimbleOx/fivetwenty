"""Trade management endpoints."""

from typing import TYPE_CHECKING, Any, TypedDict

from ..models import (
    AccountID,
    InstrumentName,
    Trade,
    TradeID,
    TradeStateFilter,
)

if TYPE_CHECKING:
    from ..client import AsyncClient


class TradesResponse(TypedDict):
    """Response from get_trades and get_open_trades endpoints."""

    trades: list[Trade]
    lastTransactionID: str


class TradeResponse(TypedDict):
    """Response from get_trade endpoint."""

    trade: Trade
    lastTransactionID: str


class CloseTradeResponse(TypedDict, total=False):
    """Response from close_trade endpoint."""

    orderCreateTransaction: Any
    orderFillTransaction: Any
    orderCancelTransaction: Any
    relatedTransactionIDs: list[str]
    lastTransactionID: str


class TradeClientExtensionsResponse(TypedDict, total=False):
    """Response from put_trade_client_extensions endpoint."""

    tradeClientExtensionsModifyTransaction: Any
    relatedTransactionIDs: list[str]
    lastTransactionID: str


class TradeOrdersResponse(TypedDict, total=False):
    """Response from put_trade_orders endpoint."""

    takeProfitOrderCancelTransaction: Any
    takeProfitOrderTransaction: Any
    takeProfitOrderFillTransaction: Any
    takeProfitOrderCreatedCancelTransaction: Any
    stopLossOrderCancelTransaction: Any
    stopLossOrderTransaction: Any
    stopLossOrderFillTransaction: Any
    stopLossOrderCreatedCancelTransaction: Any
    trailingStopLossOrderTransaction: Any
    trailingStopLossOrderCancelTransaction: Any
    guaranteedStopLossOrderTransaction: Any
    guaranteedStopLossOrderCancelTransaction: Any
    relatedTransactionIDs: list[str]
    lastTransactionID: str


class TradeEndpoints:
    """Trade management operations."""

    def __init__(self, client: "AsyncClient"):
        self._client = client

    async def get_trades(
        self,
        account_id: AccountID,
        *,
        ids: list[TradeID] | None = None,
        state: TradeStateFilter = TradeStateFilter.OPEN,
        instrument: InstrumentName | None = None,
        count: int = 50,
        before_id: TradeID | None = None,
    ) -> TradesResponse:
        """
        Get a list of trades for an account.

        Args:
            account_id: Account identifier
            ids: List of trade IDs to retrieve (optional)
            state: Filter trades by state (default: OPEN)
            instrument: Filter trades by instrument (optional)
            count: Maximum number of trades to return (default: 50, max: 500)
            before_id: Maximum trade ID to return (optional)

        Returns:
            Dictionary containing list of trades and last transaction ID

        Raises:
            FiveTwentyError: On API errors
        """
        params: dict[str, Any] = {
            "state": state.value,
            "count": min(count, 500),  # Enforce maximum
        }

        if ids:
            params["ids"] = ",".join(ids)
        if instrument:
            params["instrument"] = instrument
        if before_id:
            params["beforeID"] = before_id

        response = await self._client._request(
            "GET",
            f"/accounts/{account_id}/trades",
            params=params,
        )

        data = response.json()
        return {
            "trades": [Trade.model_validate(t) for t in data["trades"]],
            "lastTransactionID": data["lastTransactionID"],
        }

    async def get_open_trades(
        self,
        account_id: AccountID,
    ) -> TradesResponse:
        """
        Get the list of open trades for an account.

        Args:
            account_id: Account identifier

        Returns:
            Dictionary containing list of open trades and last transaction ID

        Raises:
            FiveTwentyError: On API errors
        """
        response = await self._client._request(
            "GET",
            f"/accounts/{account_id}/openTrades",
        )

        data = response.json()
        return {
            "trades": [Trade.model_validate(t) for t in data["trades"]],
            "lastTransactionID": data["lastTransactionID"],
        }

    async def get_trade(
        self,
        account_id: AccountID,
        trade_specifier: str,
    ) -> TradeResponse:
        """
        Get details of a specific trade.

        Args:
            account_id: Account identifier
            trade_specifier: Trade ID or @clientID

        Returns:
            Dictionary containing trade details and last transaction ID

        Raises:
            FiveTwentyError: On API errors
        """
        response = await self._client._request(
            "GET",
            f"/accounts/{account_id}/trades/{trade_specifier}",
        )

        data = response.json()
        return {
            "trade": Trade.model_validate(data["trade"]),
            "lastTransactionID": data["lastTransactionID"],
        }

    async def close_trade(
        self,
        account_id: AccountID,
        trade_specifier: str,
        *,
        units: str | None = None,
        idempotency_key: str | None = None,
    ) -> CloseTradeResponse:
        """
        Close a trade (fully or partially).

        Args:
            account_id: Account identifier
            trade_specifier: Trade ID or @clientID
            units: Number of units to close (default: ALL for full closure)
            idempotency_key: Idempotency key for duplicate prevention

        Returns:
            Dictionary containing closure transaction details

        Raises:
            FiveTwentyError: On API errors
        """
        data: dict[str, Any] = {}
        if units is not None:
            data["units"] = units

        headers: dict[str, str] = {}
        if idempotency_key:
            headers["ClientRequestID"] = idempotency_key

        response = await self._client._request(
            "PUT",
            f"/accounts/{account_id}/trades/{trade_specifier}/close",
            json_data=data if data else None,
            headers=headers,
        )

        return response.json()  # type: ignore[no-any-return]

    async def put_trade_client_extensions(
        self,
        account_id: AccountID,
        trade_specifier: str,
        *,
        client_extensions: dict[str, Any] | None = None,
        idempotency_key: str | None = None,
    ) -> TradeClientExtensionsResponse:
        """
        Update client extensions for a trade.

        Args:
            account_id: Account identifier
            trade_specifier: Trade ID or @clientID
            client_extensions: Client extensions to update
            idempotency_key: Idempotency key for duplicate prevention

        Returns:
            Dictionary containing update transaction details

        Raises:
            FiveTwentyError: On API errors
        """
        data: dict[str, Any] = {}
        if client_extensions:
            data["clientExtensions"] = client_extensions

        headers: dict[str, str] = {}
        if idempotency_key:
            headers["ClientRequestID"] = idempotency_key

        response = await self._client._request(
            "PUT",
            f"/accounts/{account_id}/trades/{trade_specifier}/clientExtensions",
            json_data=data,
            headers=headers,
        )

        return response.json()  # type: ignore[no-any-return]

    async def put_trade_orders(
        self,
        account_id: AccountID,
        trade_specifier: str,
        **kwargs: Any,
    ) -> TradeOrdersResponse:
        """
        Create, replace, or cancel dependent orders (TP/SL) for a trade.

        Args:
            account_id: Account identifier
            trade_specifier: Trade ID or @clientID
            **kwargs: Order specifications and options
                take_profit: Take profit order specification (optional)
                stop_loss: Stop loss order specification (optional)
                trailing_stop_loss: Trailing stop loss order specification (optional)
                guaranteed_stop_loss: Guaranteed stop loss order specification (optional)
                idempotency_key: Idempotency key for duplicate prevention

        Returns:
            Dictionary containing order update transaction details

        Raises:
            FiveTwentyError: On API errors
        """
        # Extract idempotency key
        idempotency_key = kwargs.pop("idempotency_key", None)

        data: dict[str, Any] = {}

        # Handle order parameters - None means cancel, absence means leave unchanged
        if "take_profit" in kwargs:
            data["takeProfit"] = kwargs["take_profit"]
        if "stop_loss" in kwargs:
            data["stopLoss"] = kwargs["stop_loss"]
        if "trailing_stop_loss" in kwargs:
            data["trailingStopLoss"] = kwargs["trailing_stop_loss"]
        if "guaranteed_stop_loss" in kwargs:
            data["guaranteedStopLoss"] = kwargs["guaranteed_stop_loss"]

        headers: dict[str, str] = {}
        if idempotency_key:
            headers["ClientRequestID"] = idempotency_key

        response = await self._client._request(
            "PUT",
            f"/accounts/{account_id}/trades/{trade_specifier}/orders",
            json_data=data,
            headers=headers,
        )

        return response.json()  # type: ignore[no-any-return]
