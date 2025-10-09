"""Trade management endpoints."""

from typing import TYPE_CHECKING, Any, TypedDict

from ..models import (
    AccountID,
    ClientExtensions,
    GuaranteedStopLossDetails,
    GuaranteedStopLossOrderTransaction,
    InstrumentName,
    MarketOrderTransaction,
    OrderCancelTransaction,
    OrderFillTransaction,
    StopLossDetails,
    StopLossOrderTransaction,
    TakeProfitDetails,
    TakeProfitOrderTransaction,
    Trade,
    TradeClientExtensionsModifyTransaction,
    TradeID,
    TradeStateFilter,
    TrailingStopLossDetails,
    TrailingStopLossOrderTransaction,
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

    orderCreateTransaction: MarketOrderTransaction
    orderFillTransaction: OrderFillTransaction
    orderCancelTransaction: OrderCancelTransaction
    relatedTransactionIDs: list[str]
    lastTransactionID: str


class TradeClientExtensionsResponse(TypedDict, total=False):
    """Response from put_trade_client_extensions endpoint."""

    tradeClientExtensionsModifyTransaction: TradeClientExtensionsModifyTransaction
    relatedTransactionIDs: list[str]
    lastTransactionID: str


class TradeOrdersResponse(TypedDict, total=False):
    """Response from put_trade_orders endpoint."""

    takeProfitOrderCancelTransaction: OrderCancelTransaction
    takeProfitOrderTransaction: TakeProfitOrderTransaction
    takeProfitOrderFillTransaction: OrderFillTransaction
    takeProfitOrderCreatedCancelTransaction: OrderCancelTransaction
    stopLossOrderCancelTransaction: OrderCancelTransaction
    stopLossOrderTransaction: StopLossOrderTransaction
    stopLossOrderFillTransaction: OrderFillTransaction
    stopLossOrderCreatedCancelTransaction: OrderCancelTransaction
    trailingStopLossOrderTransaction: TrailingStopLossOrderTransaction
    trailingStopLossOrderCancelTransaction: OrderCancelTransaction
    guaranteedStopLossOrderTransaction: GuaranteedStopLossOrderTransaction
    guaranteedStopLossOrderCancelTransaction: OrderCancelTransaction
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
            params["instrument"] = instrument.value if hasattr(instrument, "value") else str(instrument)
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
    ) -> CloseTradeResponse:
        """
        Close a trade (fully or partially).

        Args:
            account_id: Account identifier
            trade_specifier: Trade ID or @clientID
            units: Number of units to close (default: ALL for full closure)

        Returns:
            Dictionary containing closure transaction details

        Raises:
            FiveTwentyError: On API errors
        """
        data: dict[str, Any] = {}
        if units is not None:
            data["units"] = units

        response = await self._client._request(
            "PUT",
            f"/accounts/{account_id}/trades/{trade_specifier}/close",
            json_data=data if data else None,
        )

        response_data = response.json()
        result: CloseTradeResponse = {
            "lastTransactionID": response_data["lastTransactionID"],
        }

        if "orderCreateTransaction" in response_data:
            result["orderCreateTransaction"] = MarketOrderTransaction.model_validate(response_data["orderCreateTransaction"])
        if "orderFillTransaction" in response_data:
            result["orderFillTransaction"] = OrderFillTransaction.model_validate(response_data["orderFillTransaction"])
        if "orderCancelTransaction" in response_data:
            result["orderCancelTransaction"] = OrderCancelTransaction.model_validate(response_data["orderCancelTransaction"])
        if "relatedTransactionIDs" in response_data:
            result["relatedTransactionIDs"] = response_data["relatedTransactionIDs"]

        return result

    async def put_trade_client_extensions(
        self,
        account_id: AccountID,
        trade_specifier: str,
        *,
        client_extensions: ClientExtensions | None = None,
    ) -> TradeClientExtensionsResponse:
        """
        Update client extensions for a trade.

        Args:
            account_id: Account identifier
            trade_specifier: Trade ID or @clientID
            client_extensions: Client extensions to update

        Returns:
            Dictionary containing update transaction details

        Raises:
            FiveTwentyError: On API errors
        """
        data: dict[str, Any] = {}
        if client_extensions:
            data["clientExtensions"] = client_extensions.model_dump(by_alias=True, exclude_none=True, mode="json")

        response = await self._client._request(
            "PUT",
            f"/accounts/{account_id}/trades/{trade_specifier}/clientExtensions",
            json_data=data,
        )

        response_data = response.json()
        result: TradeClientExtensionsResponse = {
            "lastTransactionID": response_data["lastTransactionID"],
        }

        if "tradeClientExtensionsModifyTransaction" in response_data:
            result["tradeClientExtensionsModifyTransaction"] = TradeClientExtensionsModifyTransaction.model_validate(response_data["tradeClientExtensionsModifyTransaction"])
        if "relatedTransactionIDs" in response_data:
            result["relatedTransactionIDs"] = response_data["relatedTransactionIDs"]

        return result

    async def put_trade_orders(
        self,
        account_id: AccountID,
        trade_specifier: str,
        *,
        take_profit: TakeProfitDetails | None = None,
        stop_loss: StopLossDetails | None = None,
        trailing_stop_loss: TrailingStopLossDetails | None = None,
        guaranteed_stop_loss: GuaranteedStopLossDetails | None = None,
    ) -> TradeOrdersResponse:
        """
        Create, replace, or cancel dependent orders (TP/SL) for a trade.

        Args:
            account_id: Account identifier
            trade_specifier: Trade ID or @clientID
            take_profit: Take profit order specification
            stop_loss: Stop loss order specification
            trailing_stop_loss: Trailing stop loss order specification
            guaranteed_stop_loss: Guaranteed stop loss order specification

        Returns:
            Dictionary containing order update transaction details

        Raises:
            FiveTwentyError: On API errors
        """
        data: dict[str, Any] = {}

        # Handle order parameters - convert Pydantic models to dicts
        if take_profit is not None:
            data["takeProfit"] = take_profit.model_dump(by_alias=True, exclude_none=True, mode="json")
        if stop_loss is not None:
            data["stopLoss"] = stop_loss.model_dump(by_alias=True, exclude_none=True, mode="json")
        if trailing_stop_loss is not None:
            data["trailingStopLoss"] = trailing_stop_loss.model_dump(by_alias=True, exclude_none=True, mode="json")
        if guaranteed_stop_loss is not None:
            data["guaranteedStopLoss"] = guaranteed_stop_loss.model_dump(by_alias=True, exclude_none=True, mode="json")

        response = await self._client._request(
            "PUT",
            f"/accounts/{account_id}/trades/{trade_specifier}/orders",
            json_data=data,
        )

        response_data = response.json()
        result: TradeOrdersResponse = {
            "lastTransactionID": response_data["lastTransactionID"],
        }

        # Parse all possible transaction fields
        if "takeProfitOrderCancelTransaction" in response_data:
            result["takeProfitOrderCancelTransaction"] = OrderCancelTransaction.model_validate(response_data["takeProfitOrderCancelTransaction"])
        if "takeProfitOrderTransaction" in response_data:
            result["takeProfitOrderTransaction"] = TakeProfitOrderTransaction.model_validate(response_data["takeProfitOrderTransaction"])
        if "takeProfitOrderFillTransaction" in response_data:
            result["takeProfitOrderFillTransaction"] = OrderFillTransaction.model_validate(response_data["takeProfitOrderFillTransaction"])
        if "takeProfitOrderCreatedCancelTransaction" in response_data:
            result["takeProfitOrderCreatedCancelTransaction"] = OrderCancelTransaction.model_validate(response_data["takeProfitOrderCreatedCancelTransaction"])

        if "stopLossOrderCancelTransaction" in response_data:
            result["stopLossOrderCancelTransaction"] = OrderCancelTransaction.model_validate(response_data["stopLossOrderCancelTransaction"])
        if "stopLossOrderTransaction" in response_data:
            result["stopLossOrderTransaction"] = StopLossOrderTransaction.model_validate(response_data["stopLossOrderTransaction"])
        if "stopLossOrderFillTransaction" in response_data:
            result["stopLossOrderFillTransaction"] = OrderFillTransaction.model_validate(response_data["stopLossOrderFillTransaction"])
        if "stopLossOrderCreatedCancelTransaction" in response_data:
            result["stopLossOrderCreatedCancelTransaction"] = OrderCancelTransaction.model_validate(response_data["stopLossOrderCreatedCancelTransaction"])

        if "trailingStopLossOrderTransaction" in response_data:
            result["trailingStopLossOrderTransaction"] = TrailingStopLossOrderTransaction.model_validate(response_data["trailingStopLossOrderTransaction"])
        if "trailingStopLossOrderCancelTransaction" in response_data:
            result["trailingStopLossOrderCancelTransaction"] = OrderCancelTransaction.model_validate(response_data["trailingStopLossOrderCancelTransaction"])

        if "guaranteedStopLossOrderTransaction" in response_data:
            result["guaranteedStopLossOrderTransaction"] = GuaranteedStopLossOrderTransaction.model_validate(response_data["guaranteedStopLossOrderTransaction"])
        if "guaranteedStopLossOrderCancelTransaction" in response_data:
            result["guaranteedStopLossOrderCancelTransaction"] = OrderCancelTransaction.model_validate(response_data["guaranteedStopLossOrderCancelTransaction"])

        if "relatedTransactionIDs" in response_data:
            result["relatedTransactionIDs"] = response_data["relatedTransactionIDs"]

        return result
