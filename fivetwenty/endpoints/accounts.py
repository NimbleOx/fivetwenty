"""Account management endpoints."""

import builtins
from typing import TYPE_CHECKING, Any, TypedDict

from ..models import (
    Account,
    AccountChanges,
    AccountChangesState,
    AccountID,
    AccountProperties,
    AccountSummary,
    ClientConfigureTransaction,
    Instrument,
)

if TYPE_CHECKING:
    from ..client import AsyncClient


class AccountResponse(TypedDict):
    """Response from get_account endpoint."""

    account: Account
    lastTransactionID: str


class AccountSummaryResponse(TypedDict):
    """Response from get_account_summary endpoint."""

    account: AccountSummary
    lastTransactionID: str


class AccountInstrumentsResponse(TypedDict):
    """Response from get_account_instruments endpoint."""

    instruments: list[Instrument]
    lastTransactionID: str


class AccountConfigurationResponse(TypedDict):
    """Response from patch_account_configuration endpoint."""

    clientConfigureTransaction: ClientConfigureTransaction
    lastTransactionID: str


class AccountChangesResponse(TypedDict):
    """Response from get_account_changes endpoint."""

    changes: AccountChanges
    state: AccountChangesState
    lastTransactionID: str


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

    async def get_account(self, account_id: AccountID) -> AccountResponse:
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

    async def get_account_summary(self, account_id: AccountID) -> AccountSummaryResponse:
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
    ) -> AccountInstrumentsResponse:
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
    ) -> AccountConfigurationResponse:
        """
        Update account configuration settings.

        This allows updating account-level settings such as the account alias
        and margin rate. Changes affect how the account operates and appears.

        Args:
            account_id: Account identifier
            alias: New account alias (display name)
            margin_rate: New margin rate as decimal string (e.g., "0.05" for 5%)

        Returns:
            Dictionary containing configuration transaction and lastTransactionID

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
            json_data=body,
        )

        data = response.json()
        return {
            "clientConfigureTransaction": ClientConfigureTransaction.model_validate(data["clientConfigureTransaction"]),
            "lastTransactionID": data["lastTransactionID"],
        }

    async def get_account_changes(
        self,
        account_id: AccountID,
        *,
        since_transaction_id: str,
    ) -> AccountChangesResponse:
        """
        Get account changes since a specific transaction ID.

        This endpoint provides efficient polling for account state changes
        including orders, trades, positions, and transactions that have
        occurred since the specified transaction ID.

        Args:
            account_id: Account identifier
            since_transaction_id: Get changes since this transaction ID (required)

        Returns:
            Dictionary containing changes, state, and lastTransactionID

        Raises:
            FiveTwentyError: On API errors
        """
        params = {"sinceTransactionID": since_transaction_id}

        response = await self._client._request(
            "GET",
            f"/accounts/{account_id}/changes",
            params=params,
        )

        data = response.json()
        return {
            "changes": AccountChanges.model_validate(data["changes"]),
            "state": AccountChangesState.model_validate(data["state"]),
            "lastTransactionID": data["lastTransactionID"],
        }
