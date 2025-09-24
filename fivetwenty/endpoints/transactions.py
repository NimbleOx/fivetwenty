"""Transaction history and audit endpoints."""

from __future__ import annotations

import builtins  # noqa: TC003
import json
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from collections.abc import AsyncIterator
    from datetime import datetime

    from ..client import AsyncClient
    from ..models import AccountID
else:
    from datetime import datetime  # noqa: TC003

    from ..models import AccountID  # noqa: TC001


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
    ) -> dict[str, Any]:
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
    ) -> dict[str, Any]:
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

        return response.json()  # type: ignore[no-any-return]

    async def get_transactions_since_id(
        self,
        account_id: AccountID,
        transaction_id: str,
        *,
        transaction_type: builtins.list[str] | None = None,
    ) -> dict[str, Any]:
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

        return response.json()  # type: ignore[no-any-return]

    async def get_transactions_stream(
        self,
        account_id: AccountID,
        *,
        stall_timeout: float = 30.0,
    ) -> AsyncIterator[dict[str, Any]]:
        """
        Stream live transaction events for an account.

        This provides real-time updates about transactions as they occur,
        including order fills, account changes, and other transaction events.

        Args:
            account_id: Account identifier
            stall_timeout: Timeout for detecting stream stalls

        Yields:
            Transaction objects as they occur

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
                transaction = json.loads(line)
                yield transaction
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
    ) -> dict[str, Any]:
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

        return response.json()  # type: ignore[no-any-return]

    async def get_recent_transactions(
        self,
        account_id: AccountID,
        *,
        count: int = 50,
        transaction_type: builtins.list[str] | None = None,
    ) -> dict[str, Any]:
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

        return response.json()  # type: ignore[no-any-return]
