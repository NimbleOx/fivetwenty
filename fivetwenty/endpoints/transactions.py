"""Transaction history and audit endpoints."""

from __future__ import annotations

import builtins  # noqa: TC003
import json
from typing import TYPE_CHECKING, Any, TypedDict, cast

from .._internal.response import ApiResponse
from .._internal.utils import format_datetime_for_oanda
from ..models import (
    ClientConfigureRejectTransaction,
    ClientConfigureTransaction,
    CloseTransaction,
    CreateTransaction,
    DailyFinancingTransaction,
    DelayedTradeClosureTransaction,
    DividendAdjustmentTransaction,
    FixedPriceOrderTransaction,
    GuaranteedStopLossOrderRejectTransaction,
    GuaranteedStopLossOrderTransaction,
    LimitOrderRejectTransaction,
    LimitOrderTransaction,
    MarginCallEnterTransaction,
    MarginCallExitTransaction,
    MarginCallExtendTransaction,
    MarketIfTouchedOrderRejectTransaction,
    MarketIfTouchedOrderTransaction,
    MarketOrderRejectTransaction,
    MarketOrderTransaction,
    OrderCancelRejectTransaction,
    OrderCancelTransaction,
    OrderClientExtensionsModifyRejectTransaction,
    OrderClientExtensionsModifyTransaction,
    OrderFillTransaction,
    ReopenTransaction,
    ResetResettablePLTransaction,
    StopLossOrderRejectTransaction,
    StopLossOrderTransaction,
    StopOrderRejectTransaction,
    StopOrderTransaction,
    TakeProfitOrderRejectTransaction,
    TakeProfitOrderTransaction,
    TradeClientExtensionsModifyRejectTransaction,
    TradeClientExtensionsModifyTransaction,
    TrailingStopLossOrderRejectTransaction,
    TrailingStopLossOrderTransaction,
    TransactionFilter,
    TransactionHeartbeat,
    TransferFundsRejectTransaction,
    TransferFundsTransaction,
)

if TYPE_CHECKING:
    from collections.abc import AsyncIterator
    from datetime import datetime

    from ..client import AsyncClient
    from ..models import AccountID
else:
    from datetime import datetime  # noqa: TC003

    from ..models import AccountID

# Union type for all possible transaction types
TransactionUnion = (
    OrderFillTransaction
    | OrderCancelTransaction
    | MarketOrderTransaction
    | CreateTransaction
    | ClientConfigureTransaction
    | ClientConfigureRejectTransaction
    | LimitOrderTransaction
    | LimitOrderRejectTransaction
    | MarketOrderRejectTransaction
    | StopOrderTransaction
    | StopOrderRejectTransaction
    | TakeProfitOrderTransaction
    | TakeProfitOrderRejectTransaction
    | StopLossOrderTransaction
    | StopLossOrderRejectTransaction
    | TrailingStopLossOrderTransaction
    | TrailingStopLossOrderRejectTransaction
    | GuaranteedStopLossOrderTransaction
    | GuaranteedStopLossOrderRejectTransaction
    | MarketIfTouchedOrderTransaction
    | MarketIfTouchedOrderRejectTransaction
    | OrderCancelRejectTransaction
    | OrderClientExtensionsModifyTransaction
    | OrderClientExtensionsModifyRejectTransaction
    | TradeClientExtensionsModifyTransaction
    | TradeClientExtensionsModifyRejectTransaction
    | MarginCallEnterTransaction
    | MarginCallExitTransaction
    | DailyFinancingTransaction
    | DividendAdjustmentTransaction
    | ResetResettablePLTransaction
    | CloseTransaction
    | ReopenTransaction
    | TransferFundsTransaction
    | TransferFundsRejectTransaction
    | MarginCallExtendTransaction
    | FixedPriceOrderTransaction
    | DelayedTradeClosureTransaction
)


def _format_transaction_filters(transaction_type: builtins.list[TransactionFilter | str]) -> str:
    return ",".join(item.value if isinstance(item, TransactionFilter) else item for item in transaction_type)


# Maps every OANDA transaction type discriminator to its model. Must stay
# exhaustive over the official TransactionType set — verified by unit test.
_TRANSACTION_TYPE_MAP: dict[str, type[TransactionUnion]] = {
    "CREATE": CreateTransaction,
    "CLOSE": CloseTransaction,
    "REOPEN": ReopenTransaction,
    "CLIENT_CONFIGURE": ClientConfigureTransaction,
    "CLIENT_CONFIGURE_REJECT": ClientConfigureRejectTransaction,
    "TRANSFER_FUNDS": TransferFundsTransaction,
    "TRANSFER_FUNDS_REJECT": TransferFundsRejectTransaction,
    "MARKET_ORDER": MarketOrderTransaction,
    "MARKET_ORDER_REJECT": MarketOrderRejectTransaction,
    "FIXED_PRICE_ORDER": FixedPriceOrderTransaction,
    "LIMIT_ORDER": LimitOrderTransaction,
    "LIMIT_ORDER_REJECT": LimitOrderRejectTransaction,
    "STOP_ORDER": StopOrderTransaction,
    "STOP_ORDER_REJECT": StopOrderRejectTransaction,
    "MARKET_IF_TOUCHED_ORDER": MarketIfTouchedOrderTransaction,
    "MARKET_IF_TOUCHED_ORDER_REJECT": MarketIfTouchedOrderRejectTransaction,
    "TAKE_PROFIT_ORDER": TakeProfitOrderTransaction,
    "TAKE_PROFIT_ORDER_REJECT": TakeProfitOrderRejectTransaction,
    "STOP_LOSS_ORDER": StopLossOrderTransaction,
    "STOP_LOSS_ORDER_REJECT": StopLossOrderRejectTransaction,
    "GUARANTEED_STOP_LOSS_ORDER": GuaranteedStopLossOrderTransaction,
    "GUARANTEED_STOP_LOSS_ORDER_REJECT": GuaranteedStopLossOrderRejectTransaction,
    "TRAILING_STOP_LOSS_ORDER": TrailingStopLossOrderTransaction,
    "TRAILING_STOP_LOSS_ORDER_REJECT": TrailingStopLossOrderRejectTransaction,
    "ORDER_FILL": OrderFillTransaction,
    "ORDER_CANCEL": OrderCancelTransaction,
    "ORDER_CANCEL_REJECT": OrderCancelRejectTransaction,
    "ORDER_CLIENT_EXTENSIONS_MODIFY": OrderClientExtensionsModifyTransaction,
    "ORDER_CLIENT_EXTENSIONS_MODIFY_REJECT": OrderClientExtensionsModifyRejectTransaction,
    "TRADE_CLIENT_EXTENSIONS_MODIFY": TradeClientExtensionsModifyTransaction,
    "TRADE_CLIENT_EXTENSIONS_MODIFY_REJECT": TradeClientExtensionsModifyRejectTransaction,
    "MARGIN_CALL_ENTER": MarginCallEnterTransaction,
    "MARGIN_CALL_EXTEND": MarginCallExtendTransaction,
    "MARGIN_CALL_EXIT": MarginCallExitTransaction,
    "DELAYED_TRADE_CLOSURE": DelayedTradeClosureTransaction,
    "DAILY_FINANCING": DailyFinancingTransaction,
    "DIVIDEND_ADJUSTMENT": DividendAdjustmentTransaction,
    "RESET_RESETTABLE_PL": ResetResettablePLTransaction,
}


class TransactionsResponse(TypedDict, total=False):
    """Response from get_transactions endpoint."""

    from_: str  # Note: 'from' is a reserved keyword
    to: str
    pageSize: int
    type: list[str]  # Array of transaction type filters
    count: int
    pages: list[str]
    lastTransactionID: str


class TransactionResponse(TypedDict):
    """Response from get_transaction endpoint."""

    transaction: TransactionUnion
    lastTransactionID: str


class TransactionsSinceIdResponse(TypedDict):
    """Response from get_transactions_since_id endpoint."""

    transactions: list[TransactionUnion]
    lastTransactionID: str


class TransactionsRangeResponse(TypedDict):
    """Response from get_transactions_range and get_recent_transactions endpoints."""

    transactions: list[TransactionUnion]
    lastTransactionID: str


class TransactionEndpoints:
    """Transaction history and audit operations."""

    def __init__(self, client: AsyncClient):
        self._client = client

    async def get_transactions(
        self,
        account_id: AccountID,
        *,
        from_time: datetime | None = None,
        to_time: datetime | None = None,
        page_size: int = 100,
        transaction_type: builtins.list[TransactionFilter | str] | None = None,
    ) -> TransactionsResponse:
        """
        List transactions for an account within a time range.

        Args:
            account_id: Account identifier
            from_time: Start time for transaction query
            to_time: End time for transaction query
            page_size: Number of transactions per page (max 1000)
            transaction_type: Filter by transaction types (e.g., ["ORDER_FILL", "MARKET_ORDER"])

        Returns:
            Dictionary containing transactions and pagination info

        Raises:
            FiveTwentyError: On API errors
            ValueError: If page_size exceeds limits
        """
        if not 1 <= page_size <= 1000:
            raise ValueError("Page size must be between 1 and 1000")

        params: dict[str, str] = {"pageSize": str(page_size)}

        if from_time:
            params["from"] = format_datetime_for_oanda(from_time, getattr(self._client, "_datetime_format", "RFC3339"))
        if to_time:
            params["to"] = format_datetime_for_oanda(to_time, getattr(self._client, "_datetime_format", "RFC3339"))
        if transaction_type:
            params["type"] = _format_transaction_filters(transaction_type)

        response = await self._client._request(
            "GET",
            f"/accounts/{account_id}/transactions",
            params=params,
        )

        return cast("TransactionsResponse", ApiResponse(response.json()))

    async def get_transaction(
        self,
        account_id: AccountID,
        transaction_id: str,
    ) -> TransactionResponse:
        """
        Get details for a specific transaction.

        Args:
            account_id: Account identifier
            transaction_id: Transaction ID to retrieve

        Returns:
            Dictionary containing transaction details

        Raises:
            FiveTwentyError: On API errors (404 if transaction not found)
        """
        response = await self._client._request(
            "GET",
            f"/accounts/{account_id}/transactions/{transaction_id}",
        )

        data = response.json()
        return cast(
            "TransactionResponse",
            ApiResponse(
                {
                    "transaction": self._parse_transaction(data["transaction"]),
                    "lastTransactionID": data["lastTransactionID"],
                }
            ),
        )

    async def get_transactions_since_id(
        self,
        account_id: AccountID,
        transaction_id: str,
        *,
        transaction_type: builtins.list[TransactionFilter | str] | None = None,
    ) -> TransactionsSinceIdResponse:
        """
        Get transactions that occurred after a specific transaction ID.

        This is useful for incremental updates where you want to fetch
        only new transactions since your last query.

        Args:
            account_id: Account identifier
            transaction_id: Get transactions after this ID
            transaction_type: Filter by transaction types

        Returns:
            Dictionary containing transactions since the specified ID

        Raises:
            FiveTwentyError: On API errors
        """
        params = {"id": transaction_id}

        if transaction_type:
            params["type"] = _format_transaction_filters(transaction_type)

        response = await self._client._request(
            "GET",
            f"/accounts/{account_id}/transactions/sinceid",
            params=params,
        )

        data = response.json()
        return cast(
            "TransactionsSinceIdResponse",
            ApiResponse(
                {
                    "transactions": [self._parse_transaction(t) for t in data.get("transactions", [])],
                    "lastTransactionID": data["lastTransactionID"],
                }
            ),
        )

    async def get_transactions_stream(
        self,
        account_id: AccountID,
        *,
        stall_timeout: float = 30.0,
    ) -> AsyncIterator[TransactionUnion | TransactionHeartbeat]:
        """
        Stream live transaction events for an account.

        This provides real-time updates about transactions as they occur,
        including order fills, account changes, and other transaction events.
        Heartbeat messages are sent every 5 seconds to keep the connection alive.

        Args:
            account_id: Account identifier
            stall_timeout: Timeout for detecting stream stalls

        Yields:
            Transaction objects or TransactionHeartbeat messages as they occur

        Raises:
            FiveTwentyError: On API errors
            StreamStall: On stream timeout or connection issues
        """
        async for line in self._client._stream(
            f"/accounts/{account_id}/transactions/stream",
            params={},
            stall_timeout=stall_timeout,
        ):
            try:
                transaction_data = json.loads(line)

                # Check if this is a heartbeat message
                if transaction_data.get("type") == "HEARTBEAT":
                    yield TransactionHeartbeat.model_validate(transaction_data)
                else:
                    yield self._parse_transaction(transaction_data)
            except (json.JSONDecodeError, ValueError) as e:
                # Log malformed data but continue streaming
                self._client._log(
                    "warning",
                    f"Malformed transaction stream data: {e}",
                    extra={
                        "line": line[:200],  # Truncate for logging
                        "account_id": str(account_id),
                    },
                )
                continue

    async def get_transactions_range(
        self,
        account_id: AccountID,
        from_transaction_id: str,
        to_transaction_id: str,
        *,
        transaction_type: builtins.list[TransactionFilter | str] | None = None,
    ) -> TransactionsRangeResponse:
        """
        Get transactions within a specific ID range.

        This is useful when you know the specific transaction ID boundaries
        and want to fetch all transactions in that range.

        Args:
            account_id: Account identifier
            from_transaction_id: Starting transaction ID (inclusive)
            to_transaction_id: Ending transaction ID (inclusive)
            transaction_type: Filter by transaction types

        Returns:
            Dictionary containing transactions in the specified ID range

        Raises:
            FiveTwentyError: On API errors
            ValueError: If from_transaction_id > to_transaction_id
        """
        # Basic validation - transaction IDs should be numeric
        try:
            from_id = int(from_transaction_id)
            to_id = int(to_transaction_id)
            if from_id > to_id:
                raise ValueError("from_transaction_id must be <= to_transaction_id")
        except ValueError as e:
            if "from_transaction_id must be" in str(e):
                raise
            raise ValueError("Transaction IDs must be numeric") from e

        params = {
            "from": from_transaction_id,
            "to": to_transaction_id,
        }

        if transaction_type:
            params["type"] = _format_transaction_filters(transaction_type)

        response = await self._client._request(
            "GET",
            f"/accounts/{account_id}/transactions/idrange",
            params=params,
        )

        data = response.json()
        return cast(
            "TransactionsRangeResponse",
            ApiResponse(
                {
                    "transactions": [self._parse_transaction(t) for t in data.get("transactions", [])],
                    "lastTransactionID": data["lastTransactionID"],
                }
            ),
        )

    async def get_recent_transactions(
        self,
        account_id: AccountID,
        *,
        count: int = 50,
        transaction_type: builtins.list[TransactionFilter | str] | None = None,
    ) -> TransactionsRangeResponse:
        """
        Get the most recent transactions for an account.

        This is a convenience method for getting recent transaction history
        without specifying time ranges or transaction IDs. It resolves the
        account's last transaction ID and fetches the trailing ID range, since
        the transactions list endpoint itself returns page URLs rather than
        transaction data.

        Args:
            account_id: Account identifier
            count: Number of most recent transaction IDs to cover (1-500).
                When transaction_type is set, fewer than count transactions
                may be returned: the filter applies within the ID range.
            transaction_type: Filter by transaction types

        Returns:
            Dictionary containing recent transactions

        Raises:
            FiveTwentyError: On API errors
            ValueError: If count is outside 1-500
        """
        if not 1 <= count <= 500:
            raise ValueError("Count must be between 1 and 500")

        response = await self._client._request(
            "GET",
            f"/accounts/{account_id}/transactions",
            params={"pageSize": "1"},
        )
        last_id = int(response.json()["lastTransactionID"])
        if last_id < 1:
            return cast(
                "TransactionsRangeResponse",
                ApiResponse({"transactions": [], "lastTransactionID": str(last_id)}),
            )

        return await self.get_transactions_range(
            account_id,
            str(max(1, last_id - count + 1)),
            str(last_id),
            transaction_type=transaction_type,
        )

    def _parse_transaction(self, transaction_data: dict[str, Any]) -> TransactionUnion:
        """
        Parse transaction data into the appropriate Transaction model based on type discriminator.

        Args:
            transaction_data: Raw transaction data from API response

        Returns:
            Parsed Transaction model

        Raises:
            ValueError: If transaction type is unknown
        """
        transaction_type = transaction_data.get("type")
        model = _TRANSACTION_TYPE_MAP.get(transaction_type or "")
        if model is None:
            raise ValueError(f"Unknown transaction type: {transaction_type}")
        return model.model_validate(transaction_data)
