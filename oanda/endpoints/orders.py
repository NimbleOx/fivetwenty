"""Order management endpoints."""

from decimal import Decimal
from typing import TYPE_CHECKING, Dict, List, Optional, Any

from .._internal.utils import quantize_price
from .._models import (
    AccountID,
    InstrumentName, 
    MarketOrderRequest,
    OrderResponse,
    OrderType,
)

if TYPE_CHECKING:
    from ..client import AsyncClient


class OrderEndpoints:
    """Order management operations."""
    
    def __init__(self, client: "AsyncClient"):
        self._client = client
        self._precision_cache: Dict[str, int] = {}  # Simple cache for demo
    
    async def create_market(
        self,
        account_id: AccountID,
        instrument: InstrumentName,
        units: int,
        *,
        take_profit: Optional[Decimal] = None,
        stop_loss: Optional[Decimal] = None,
        timeout: Optional[float] = None,
        idempotency_key: Optional[str] = None,
    ) -> OrderResponse:
        """
        Create a market order.
        
        Args:
            account_id: Account to create order for
            instrument: Instrument to trade
            units: Number of units (positive = buy, negative = sell)
            take_profit: Take profit price (optional)
            stop_loss: Stop loss price (optional)
            timeout: Request timeout override
            idempotency_key: Idempotency key for duplicate prevention
            
        Returns:
            Order response with transaction details
            
        Raises:
            OandaError: On API errors
            ValueError: On invalid parameters
        """
        # Build the order request
        request = MarketOrderRequest(
            instrument=instrument,
            units=units,
        )
        
        # Add take profit if specified
        if take_profit is not None:
            precision = await self._get_precision(account_id, instrument)
            quantized_tp = quantize_price(precision, take_profit)
            request.take_profit_on_fill = {
                "price": str(quantized_tp)
            }
        
        # Add stop loss if specified  
        if stop_loss is not None:
            precision = await self._get_precision(account_id, instrument)
            quantized_sl = quantize_price(precision, stop_loss)
            request.stop_loss_on_fill = {
                "price": str(quantized_sl)
            }
        
        # Convert to dict and make request
        body = request.model_dump(by_alias=True, exclude_none=True)
        
        response = await self._client._request(
            "POST",
            f"/accounts/{account_id}/orders",
            json_data=body,
            timeout=timeout,
            idempotency_key=idempotency_key,
        )
        
        return OrderResponse.model_validate(response.json())
    
    async def list(
        self,
        account_id: AccountID,
        *,
        state: str = "PENDING",
        instrument: Optional[str] = None,
        count: int = 50,
        before_id: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        List orders for an account.
        
        Args:
            account_id: Account ID
            state: Order state filter
            instrument: Instrument filter (optional)
            count: Maximum number of orders
            before_id: Get orders before this ID
            
        Returns:
            List of orders
            
        Raises:
            OandaError: On API errors
        """
        params = {
            "state": state,
            "count": count,
        }
        
        if instrument:
            params["instrument"] = instrument
        if before_id:
            params["beforeID"] = before_id
        
        response = await self._client._request(
            "GET",
            f"/accounts/{account_id}/orders",
            params=params,
        )
        data = response.json()
        
        return data.get("orders", [])  # type: ignore[no-any-return]
    
    async def get(self, account_id: AccountID, order_id: str) -> Dict[str, Any]:
        """
        Get order details.
        
        Args:
            account_id: Account ID
            order_id: Order ID
            
        Returns:
            Order details
            
        Raises:
            OandaError: On API errors
        """
        response = await self._client._request(
            "GET",
            f"/accounts/{account_id}/orders/{order_id}",
        )
        data = response.json()
        
        return data["order"]  # type: ignore[no-any-return]
    
    async def cancel(
        self,
        account_id: AccountID,
        order_id: str,
        *,
        timeout: Optional[float] = None,
    ) -> Dict[str, Any]:
        """
        Cancel an order.
        
        Args:
            account_id: Account ID
            order_id: Order ID to cancel
            timeout: Request timeout override
            
        Returns:
            Cancellation response
            
        Raises:
            OandaError: On API errors
        """
        response = await self._client._request(
            "PUT",
            f"/accounts/{account_id}/orders/{order_id}/cancel",
            timeout=timeout,
        )
        
        return response.json()  # type: ignore[no-any-return]
    
    async def _get_precision(self, account_id: AccountID, instrument: str) -> int:
        """
        Get display precision for an instrument.
        
        This is a simple cache for the demo. In production, this would
        be more sophisticated with TTL, etc.
        """
        if instrument in self._precision_cache:
            return self._precision_cache[instrument]
        
        # Get instruments for this account
        instruments_data = await self._client.accounts.instruments(
            account_id, 
            instruments=[instrument]
        )
        
        if not instruments_data:
            raise ValueError(f"Instrument {instrument} not found")
        
        precision = instruments_data[0].display_precision
        self._precision_cache[instrument] = precision
        return precision