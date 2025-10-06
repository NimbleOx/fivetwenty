"""Transaction history and audit endpoints."""

from __future__ import annotations

import builtins  # noqa: TC003
import json
from typing import TYPE_CHECKING, Any, TypedDict

from ..models import (
    ClientConfigureRejectTransaction,
    ClientConfigureTransaction,
    CloseTransaction,
    CreateTransaction,
    DailyFinancingTransaction,
    DelayedTradeCloseTransaction,
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
    TradeClientExtensionsModifyTransaction,
    TrailingStopLossOrderRejectTransaction,
    TrailingStopLossOrderTransaction,
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
    | TradeClientExtensionsModifyTransaction
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
    | DelayedTradeCloseTransaction
)


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
        transaction_type: builtins.list[str] | None = None,
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
        if page_size > 1000:
            raise ValueError("Page size cannot exceed 1000")

        params: dict[str, str] = {"pageSize": str(page_size)}

        if from_time:
            params["from"] = from_time.isoformat()
        if to_time:
            params["to"] = to_time.isoformat()
        if transaction_type:
            params["type"] = ",".join(transaction_type)

        response = await self._client._request(
            "GET",
            f"/accounts/{account_id}/transactions",
            params=params,
        )

        return response.json()  # type: ignore[no-any-return]

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
        return {
            "transaction": self._parse_transaction(data["transaction"]),
            "lastTransactionID": data["lastTransactionID"],
        }

    async def get_transactions_since_id(
        self,
        account_id: AccountID,
        transaction_id: str,
        *,
        transaction_type: builtins.list[str] | None = None,
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
            params["type"] = ",".join(transaction_type)

        response = await self._client._request(
            "GET",
            f"/accounts/{account_id}/transactions/sinceid",
            params=params,
        )

        data = response.json()
        return {
            "transactions": [self._parse_transaction(t) for t in data.get("transactions", [])],
            "lastTransactionID": data["lastTransactionID"],
        }

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
        transaction_type: builtins.list[str] | None = None,
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
            params["type"] = ",".join(transaction_type)

        response = await self._client._request(
            "GET",
            f"/accounts/{account_id}/transactions/idrange",
            params=params,
        )

        data = response.json()
        return {
            "transactions": [self._parse_transaction(t) for t in data.get("transactions", [])],
            "lastTransactionID": data["lastTransactionID"],
        }

    async def get_recent_transactions(
        self,
        account_id: AccountID,
        *,
        count: int = 50,
        transaction_type: builtins.list[str] | None = None,
    ) -> TransactionsRangeResponse:
        """
        Get the most recent transactions for an account.

        This is a convenience method for getting recent transaction history
        without specifying time ranges or transaction IDs.

        Args:
            account_id: Account identifier
            count: Number of recent transactions to retrieve (max 500)
            transaction_type: Filter by transaction types

        Returns:
            Dictionary containing recent transactions

        Raises:
            FiveTwentyError: On API errors
            ValueError: If count exceeds limits
        """
        if count > 500:
            raise ValueError("Count cannot exceed 500")

        params: dict[str, str] = {"count": str(count)}

        if transaction_type:
            params["type"] = ",".join(transaction_type)

        response = await self._client._request(
            "GET",
            f"/accounts/{account_id}/transactions",
            params=params,
        )

        data = response.json()
        return {
            "transactions": [self._parse_transaction(t) for t in data.get("transactions", [])],
            "lastTransactionID": data["lastTransactionID"],
        }

    def _parse_transaction(self, transaction_data: dict[str, Any]) -> TransactionUnion:  # noqa: PLR0911
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

        if transaction_type == "ORDER_FILL":
            return OrderFillTransaction.model_validate(transaction_data)
        if transaction_type == "ORDER_CANCEL":
            return OrderCancelTransaction.model_validate(transaction_data)
        if transaction_type == "MARKET_ORDER":
            return MarketOrderTransaction.model_validate(transaction_data)
        if transaction_type == "CREATE":
            return CreateTransaction.model_validate(transaction_data)
        if transaction_type == "CLIENT_CONFIGURE":
            return ClientConfigureTransaction.model_validate(transaction_data)
        if transaction_type == "CLIENT_CONFIGURE_REJECT":
            return ClientConfigureRejectTransaction.model_validate(transaction_data)
        if transaction_type == "LIMIT_ORDER":
            return LimitOrderTransaction.model_validate(transaction_data)
        if transaction_type == "LIMIT_ORDER_REJECT":
            return LimitOrderRejectTransaction.model_validate(transaction_data)
        if transaction_type == "MARKET_ORDER_REJECT":
            return MarketOrderRejectTransaction.model_validate(transaction_data)
        if transaction_type == "STOP_ORDER":
            return StopOrderTransaction.model_validate(transaction_data)
        if transaction_type == "STOP_ORDER_REJECT":
            return StopOrderRejectTransaction.model_validate(transaction_data)
        if transaction_type == "TAKE_PROFIT_ORDER":
            return TakeProfitOrderTransaction.model_validate(transaction_data)
        if transaction_type == "TAKE_PROFIT_ORDER_REJECT":
            return TakeProfitOrderRejectTransaction.model_validate(transaction_data)
        if transaction_type == "STOP_LOSS_ORDER":
            return StopLossOrderTransaction.model_validate(transaction_data)
        if transaction_type == "STOP_LOSS_ORDER_REJECT":
            return StopLossOrderRejectTransaction.model_validate(transaction_data)
        if transaction_type == "TRAILING_STOP_LOSS_ORDER":
            return TrailingStopLossOrderTransaction.model_validate(transaction_data)
        if transaction_type == "TRAILING_STOP_LOSS_ORDER_REJECT":
            return TrailingStopLossOrderRejectTransaction.model_validate(transaction_data)
        if transaction_type == "GUARANTEED_STOP_LOSS_ORDER":
            return GuaranteedStopLossOrderTransaction.model_validate(transaction_data)
        if transaction_type == "GUARANTEED_STOP_LOSS_ORDER_REJECT":
            return GuaranteedStopLossOrderRejectTransaction.model_validate(transaction_data)
        if transaction_type == "MARKET_IF_TOUCHED_ORDER":
            return MarketIfTouchedOrderTransaction.model_validate(transaction_data)
        if transaction_type == "MARKET_IF_TOUCHED_ORDER_REJECT":
            return MarketIfTouchedOrderRejectTransaction.model_validate(transaction_data)
        if transaction_type == "ORDER_CANCEL_REJECT":
            return OrderCancelRejectTransaction.model_validate(transaction_data)
        if transaction_type == "ORDER_CLIENT_EXTENSIONS_MODIFY":
            return OrderClientExtensionsModifyTransaction.model_validate(transaction_data)
        if transaction_type == "TRADE_CLIENT_EXTENSIONS_MODIFY":
            return TradeClientExtensionsModifyTransaction.model_validate(transaction_data)
        if transaction_type == "MARGIN_CALL_ENTER":
            return MarginCallEnterTransaction.model_validate(transaction_data)
        if transaction_type == "MARGIN_CALL_EXIT":
            return MarginCallExitTransaction.model_validate(transaction_data)
        if transaction_type == "DAILY_FINANCING":
            return DailyFinancingTransaction.model_validate(transaction_data)
        if transaction_type == "DIVIDEND_ADJUSTMENT":
            return DividendAdjustmentTransaction.model_validate(transaction_data)
        if transaction_type == "RESET_RESETTABLE_PL":
            return ResetResettablePLTransaction.model_validate(transaction_data)
        if transaction_type == "CLOSE":
            return CloseTransaction.model_validate(transaction_data)
        if transaction_type == "REOPEN":
            return ReopenTransaction.model_validate(transaction_data)
        if transaction_type == "TRANSFER_FUNDS":
            return TransferFundsTransaction.model_validate(transaction_data)
        if transaction_type == "TRANSFER_FUNDS_REJECT":
            return TransferFundsRejectTransaction.model_validate(transaction_data)
        if transaction_type == "MARGIN_CALL_EXTEND":
            return MarginCallExtendTransaction.model_validate(transaction_data)
        if transaction_type == "FIXED_PRICE_ORDER":
            return FixedPriceOrderTransaction.model_validate(transaction_data)
        if transaction_type == "DELAYED_TRADE_CLOSURE":
            return DelayedTradeCloseTransaction.model_validate(transaction_data)

        raise ValueError(f"Unknown transaction type: {transaction_type}")
