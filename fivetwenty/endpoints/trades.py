"""Trade management endpoints."""

from typing import TYPE_CHECKING, Any

from ..models import (
    AccountID,
    InstrumentName,
    TradeID,
    TradeStateFilter,
)

if TYPE_CHECKING:
    from ..client import AsyncClient


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
    ) -> dict[str, Any]:
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

        return response.json()  # type: ignore[no-any-return]

    async def get_open_trades(
        self,
        account_id: AccountID,
    ) -> dict[str, Any]:
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

        return response.json()  # type: ignore[no-any-return]

    async def get_trade(
        self,
        account_id: AccountID,
        trade_specifier: str,
    ) -> dict[str, Any]:
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

        return response.json()  # type: ignore[no-any-return]

    async def close_trade(
        self,
        account_id: AccountID,
        trade_specifier: str,
        *,
        units: str | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
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

        headers = {}
        if idempotency_key:
            headers["ClientRequestID"] = idempotency_key

        response = await self._client._request(
            "PUT",
            f"/accounts/{account_id}/trades/{trade_specifier}/close",
            json_data=data if data else None,
            headers=headers if headers else None,
        )

        return response.json()  # type: ignore[no-any-return]

    async def put_trade_client_extensions(
        self,
        account_id: AccountID,
        trade_specifier: str,
        *,
        client_extensions: dict[str, Any] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
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

        headers = {}
        if idempotency_key:
            headers["ClientRequestID"] = idempotency_key

        response = await self._client._request(
            "PUT",
            f"/accounts/{account_id}/trades/{trade_specifier}/clientExtensions",
            json_data=data,
            headers=headers if headers else None,
        )

        return response.json()  # type: ignore[no-any-return]

    async def put_trade_orders(
        self,
        account_id: AccountID,
        trade_specifier: str,
        **kwargs: Any,
    ) -> dict[str, Any]:
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

        headers = {}
        if idempotency_key:
            headers["ClientRequestID"] = idempotency_key

        response = await self._client._request(
            "PUT",
            f"/accounts/{account_id}/trades/{trade_specifier}/orders",
            json_data=data,
            headers=headers if headers else None,
        )

        return response.json()  # type: ignore[no-any-return]
