"""Account management endpoints."""

from typing import TYPE_CHECKING, List, Optional

from .._models import Account, AccountID, AccountProperties, Instrument

if TYPE_CHECKING:
    from ..client import AsyncClient


class AccountEndpoints:
    """Account management operations."""
    
    def __init__(self, client: "AsyncClient"):
        self._client = client
    
    async def list(self) -> List[AccountProperties]:
        """
        Get list of accounts.
        
        Returns:
            List of account properties
            
        Raises:
            OandaError: On API errors
        """
        response = await self._client._request("GET", "/accounts")
        data = response.json()
        
        return [
            AccountProperties.model_validate(account_data)
            for account_data in data["accounts"]
        ]
    
    async def get(self, account_id: AccountID) -> Account:
        """
        Get detailed account information.
        
        Args:
            account_id: Account ID to retrieve
            
        Returns:
            Complete account details
            
        Raises:
            OandaError: On API errors
        """
        response = await self._client._request("GET", f"/accounts/{account_id}")
        data = response.json()
        
        return Account.model_validate(data["account"])
    
    async def summary(self, account_id: AccountID) -> Account:
        """
        Get account summary (same as get but more efficient).
        
        Args:
            account_id: Account ID to retrieve
            
        Returns:
            Account summary
            
        Raises:
            OandaError: On API errors
        """
        response = await self._client._request("GET", f"/accounts/{account_id}/summary")
        data = response.json()
        
        return Account.model_validate(data["account"])
    
    async def instruments(
        self, 
        account_id: AccountID,
        *,
        instruments: Optional[List[str]] = None,
    ) -> List[Instrument]:
        """
        Get tradeable instruments for an account.
        
        Args:
            account_id: Account ID
            instruments: Filter to specific instruments (optional)
            
        Returns:
            List of available instruments
            
        Raises:
            OandaError: On API errors
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
        
        return [
            Instrument.model_validate(instrument_data)
            for instrument_data in data["instruments"]
        ]