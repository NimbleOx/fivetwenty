"""Pricing and streaming endpoints."""

import json
from typing import TYPE_CHECKING, List, Dict, Any, AsyncIterator, Union

from .._models import AccountID, ClientPrice, PricingHeartbeat

if TYPE_CHECKING:
    from ..client import AsyncClient


class PricingEndpoints:
    """Pricing and real-time data operations."""
    
    def __init__(self, client: "AsyncClient"):
        self._client = client
    
    async def get(
        self,
        account_id: AccountID,
        instruments: List[str],
        *,
        since: str | None = None,
        include_units_available: bool = True,
        include_home_conversions: bool = False,
    ) -> Dict[str, Any]:
        """
        Get current prices for instruments.
        
        Args:
            account_id: Account ID
            instruments: List of instruments to get prices for
            since: Only get prices changed since this time
            include_units_available: Include units available info
            include_home_conversions: Include home currency conversions
            
        Returns:
            Pricing information
            
        Raises:
            OandaError: On API errors
        """
        params = {
            "instruments": ",".join(instruments),
            "includeUnitsAvailable": str(include_units_available).lower(),
            "includeHomeConversions": str(include_home_conversions).lower(),
        }
        
        if since:
            params["since"] = since
        
        response = await self._client._request(
            "GET",
            f"/accounts/{account_id}/pricing",
            params=params,
        )
        
        return response.json()  # type: ignore[no-any-return]
    
    async def stream(
        self,
        account_id: AccountID,
        instruments: List[str],
        *,
        snapshot: bool = True,
        stall_timeout: float = 30.0,
    ) -> AsyncIterator[Union[ClientPrice, PricingHeartbeat]]:
        """
        Stream real-time pricing data.
        
        Args:
            account_id: Account ID
            instruments: List of instruments to stream
            snapshot: Include initial snapshot
            stall_timeout: Timeout for detecting stream stalls
            
        Yields:
            ClientPrice or PricingHeartbeat objects
            
        Raises:
            OandaError: On API errors
            StreamStall: On stream timeout or connection issues
        """
        params = {
            "instruments": ",".join(instruments),
        }
        
        if snapshot:
            params["snapshot"] = "true"
        
        async for line in self._client._stream(
            f"/accounts/{account_id}/pricing/stream",
            params=params,
            stall_timeout=stall_timeout,
        ):
            try:
                data = json.loads(line)
                
                if data.get("type") == "PRICE":
                    yield ClientPrice.model_validate(data)
                elif data.get("type") == "HEARTBEAT":
                    yield PricingHeartbeat.model_validate(data)
                
            except (json.JSONDecodeError, ValueError) as e:
                # Log malformed data but continue streaming
                self._client._log("warning", f"Malformed stream data: {e}", extra={
                    "line": line[:200],  # Truncate for logging
                })
                continue