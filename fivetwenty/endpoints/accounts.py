"""Account management endpoints."""

import builtins
from typing import TYPE_CHECKING, Any

from ..models import Account, AccountID, AccountProperties, AccountSummary, Instrument

if TYPE_CHECKING:
    from ..client import AsyncClient


class AccountEndpoints:
    """Account management operations."""

    def __init__(self, client: "AsyncClient"):
        self._client = client

    async def get_accounts(self) -> list[AccountProperties]:
        """
        Get list of accounts.

        Returns:
            List of account properties

        Raises:
            FiveTwentyError: On API errors
        """
        response = await self._client._request("GET", "/accounts")
        data = response.json()

        return [AccountProperties.model_validate(account_data) for account_data in data["accounts"]]

    async def get_account(self, account_id: AccountID) -> dict[str, Any]:
        """
        Get detailed account information.

        Args:
            account_id: Account ID to retrieve

        Returns:
            Dictionary containing account details and lastTransactionID

        Raises:
            FiveTwentyError: On API errors
        """
        response = await self._client._request("GET", f"/accounts/{account_id}")
        data = response.json()

        return {
            "account": Account.model_validate(data["account"]),
            "lastTransactionID": data["lastTransactionID"],
        }

    async def get_account_summary(self, account_id: AccountID) -> dict[str, Any]:
        """
        Get account summary (same as get but more efficient).

        Args:
            account_id: Account ID to retrieve

        Returns:
            Dictionary containing account summary and lastTransactionID

        Raises:
            FiveTwentyError: On API errors
        """
        response = await self._client._request("GET", f"/accounts/{account_id}/summary")
        data = response.json()

        return {
            "account": AccountSummary.model_validate(data["account"]),
            "lastTransactionID": data["lastTransactionID"],
        }

    async def get_account_instruments(
        self,
        account_id: AccountID,
        *,
        instruments: builtins.list[str] | None = None,
    ) -> dict[str, Any]:
        """
        Get tradeable instruments for an account.

        Args:
            account_id: Account ID
            instruments: Filter to specific instruments (optional)

        Returns:
            Dictionary containing instruments list and lastTransactionID

        Raises:
            FiveTwentyError: On API errors
        """
        params = {}
        if instruments:
            params["instruments"] = ",".join(instruments)

        response = await self._client._request(
            "GET",
            f"/accounts/{account_id}/instruments",
            params=params,
        )
        data = response.json()

        return {
            "instruments": [Instrument.model_validate(instrument_data) for instrument_data in data["instruments"]],
            "lastTransactionID": data["lastTransactionID"],
        }

    async def patch_account_configuration(
        self,
        account_id: AccountID,
        *,
        alias: str | None = None,
        margin_rate: str | None = None,
    ) -> dict[str, Any]:
        """
        Update account configuration settings.

        This allows updating account-level settings such as the account alias
        and margin rate. Changes affect how the account operates and appears.

        Args:
            account_id: Account identifier
            alias: New account alias (display name)
            margin_rate: New margin rate as decimal string (e.g., "0.05" for 5%)

        Returns:
            Dictionary containing configuration update results

        Raises:
            FiveTwentyError: On API errors
            ValueError: If no configuration parameters provided
        """
        if alias is None and margin_rate is None:
            raise ValueError("Must provide at least one configuration parameter")

        body: dict[str, Any] = {}
        if alias is not None:
            body["alias"] = alias
        if margin_rate is not None:
            body["marginRate"] = margin_rate

        response = await self._client._request(
            "PATCH",
            f"/accounts/{account_id}/configuration",
            json=body,
        )

        return response.json()  # type: ignore[no-any-return]

    async def get_account_changes(
        self,
        account_id: AccountID,
        *,
        since_transaction_id: str,
    ) -> dict[str, Any]:
        """
        Get account changes since a specific transaction ID.

        This endpoint provides efficient polling for account state changes
        including orders, trades, positions, and transactions that have
        occurred since the specified transaction ID.

        Args:
            account_id: Account identifier
            since_transaction_id: Get changes since this transaction ID (required)

        Returns:
            Dictionary containing account state changes and current state

        Raises:
            FiveTwentyError: On API errors
        """
        params = {"sinceTransactionID": since_transaction_id}

        response = await self._client._request(
            "GET",
            f"/accounts/{account_id}/changes",
            params=params,
        )

        return response.json()  # type: ignore[no-any-return]
