"""Position management endpoints."""

from decimal import Decimal
from typing import TYPE_CHECKING, Any, TypedDict

from ..models import (
    AccountID,
    ClientExtensions,
    InstrumentName,
    MarketOrderTransaction,
    OrderCancelTransaction,
    OrderFillTransaction,
    Position,
)

if TYPE_CHECKING:
    from ..client import AsyncClient


class PositionsResponse(TypedDict):
    """Response from get_positions and get_open_positions endpoints."""

    positions: list[Position]
    lastTransactionID: str


class PositionResponse(TypedDict):
    """Response from get_position endpoint."""

    position: Position
    lastTransactionID: str


class ClosePositionResponse(TypedDict, total=False):
    """Response from close_position endpoint."""

    longOrderCreateTransaction: MarketOrderTransaction
    longOrderFillTransaction: OrderFillTransaction
    longOrderCancelTransaction: OrderCancelTransaction
    shortOrderCreateTransaction: MarketOrderTransaction
    shortOrderFillTransaction: OrderFillTransaction
    shortOrderCancelTransaction: OrderCancelTransaction
    relatedTransactionIDs: list[str]
    lastTransactionID: str


class PositionEndpoints:
    """Position management operations."""

    def __init__(self, client: "AsyncClient"):
        self._client = client

    async def get_positions(self, account_id: AccountID) -> PositionsResponse:
        """
        Get a list of all positions for an account.

        Returns positions for every instrument that has had a position
        during the lifetime of the account, including historical positions.

        Args:
            account_id: Account identifier

        Returns:
            Dictionary containing list of positions and last transaction ID

        Raises:
            FiveTwentyError: On API errors
        """
        response = await self._client._request("GET", f"/accounts/{account_id}/positions")
        data = response.json()
        return {
            "positions": [Position.model_validate(p) for p in data["positions"]],
            "lastTransactionID": data["lastTransactionID"],
        }

    async def get_open_positions(self, account_id: AccountID) -> PositionsResponse:
        """
        Get a list of all open positions for an account.

        An open position is a position that currently has active trades.

        Args:
            account_id: Account identifier

        Returns:
            Dictionary containing list of open positions and last transaction ID

        Raises:
            FiveTwentyError: On API errors
        """
        response = await self._client._request("GET", f"/accounts/{account_id}/openPositions")
        data = response.json()
        return {
            "positions": [Position.model_validate(p) for p in data["positions"]],
            "lastTransactionID": data["lastTransactionID"],
        }

    async def get_position(self, account_id: AccountID, instrument: InstrumentName) -> PositionResponse:
        """
        Get the position for a specific instrument in an account.

        Args:
            account_id: Account identifier
            instrument: Name of the instrument

        Returns:
            Dictionary containing position details and last transaction ID

        Raises:
            FiveTwentyError: On API errors (404 if no position exists)
        """
        instrument_str = instrument.value if hasattr(instrument, "value") else str(instrument)
        response = await self._client._request("GET", f"/accounts/{account_id}/positions/{instrument_str}")
        data = response.json()
        return {
            "position": Position.model_validate(data["position"]),
            "lastTransactionID": data["lastTransactionID"],
        }

    async def close_position(
        self,
        account_id: AccountID,
        instrument: InstrumentName,
        *,
        long_units: str | Decimal | None = None,
        short_units: str | Decimal | None = None,
        long_client_extensions: ClientExtensions | None = None,
        short_client_extensions: ClientExtensions | None = None,
    ) -> ClosePositionResponse:
        """
        Close the open position for a specific instrument.

        Allows partial or complete position closure by specifying units
        for long and/or short sides. Use "ALL" to close entire position side,
        "NONE" to leave unchanged, or a specific number of units.

        Args:
            account_id: Account identifier
            instrument: Name of the instrument
            long_units: Units of long position to close ("ALL", "NONE", or number)
            short_units: Units of short position to close ("ALL", "NONE", or number)
            long_client_extensions: Client extensions for long position closure order
            short_client_extensions: Client extensions for short position closure order

        Returns:
            Dictionary containing closure transaction details

        Raises:
            FiveTwentyError: On API errors
            ValueError: If neither long_units nor short_units specified
        """
        if long_units is None and short_units is None:
            raise ValueError("Must specify at least one of long_units or short_units")

        body: dict[str, Any] = {}

        if long_units is not None:
            if isinstance(long_units, str):
                # Allow "ALL", "NONE", or numeric strings
                if long_units in ("ALL", "NONE"):
                    body["longUnits"] = long_units
                else:
                    # Validate numeric strings by attempting conversion
                    try:
                        float(long_units)  # Basic validation for numeric string
                        body["longUnits"] = long_units
                    except ValueError:
                        raise ValueError("long_units string must be 'ALL', 'NONE', or a numeric value")
            else:
                # Convert Decimal to string
                body["longUnits"] = str(long_units)

        if short_units is not None:
            if isinstance(short_units, str):
                # Allow "ALL", "NONE", or numeric strings
                if short_units in ("ALL", "NONE"):
                    body["shortUnits"] = short_units
                else:
                    # Validate numeric strings by attempting conversion
                    try:
                        float(short_units)  # Basic validation for numeric string
                        body["shortUnits"] = short_units
                    except ValueError:
                        raise ValueError("short_units string must be 'ALL', 'NONE', or a numeric value")
            else:
                # Convert Decimal to string
                body["shortUnits"] = str(short_units)

        # Add client extensions to request body
        if long_client_extensions is not None:
            body["longClientExtensions"] = long_client_extensions.model_dump(by_alias=True, exclude_none=True, mode="json")
        if short_client_extensions is not None:
            body["shortClientExtensions"] = short_client_extensions.model_dump(by_alias=True, exclude_none=True, mode="json")

        instrument_str = instrument.value if hasattr(instrument, "value") else str(instrument)
        response = await self._client._request(
            "PUT",
            f"/accounts/{account_id}/positions/{instrument_str}/close",
            json_data=body,
        )
        data = response.json()

        # Parse transaction fields if present
        result: ClosePositionResponse = {
            "lastTransactionID": data["lastTransactionID"],
        }

        if "relatedTransactionIDs" in data:
            result["relatedTransactionIDs"] = data["relatedTransactionIDs"]

        # Parse long position transactions
        if "longOrderCreateTransaction" in data:
            result["longOrderCreateTransaction"] = MarketOrderTransaction.model_validate(data["longOrderCreateTransaction"])
        if "longOrderFillTransaction" in data:
            result["longOrderFillTransaction"] = OrderFillTransaction.model_validate(data["longOrderFillTransaction"])
        if "longOrderCancelTransaction" in data:
            result["longOrderCancelTransaction"] = OrderCancelTransaction.model_validate(data["longOrderCancelTransaction"])

        # Parse short position transactions
        if "shortOrderCreateTransaction" in data:
            result["shortOrderCreateTransaction"] = MarketOrderTransaction.model_validate(data["shortOrderCreateTransaction"])
        if "shortOrderFillTransaction" in data:
            result["shortOrderFillTransaction"] = OrderFillTransaction.model_validate(data["shortOrderFillTransaction"])
        if "shortOrderCancelTransaction" in data:
            result["shortOrderCancelTransaction"] = OrderCancelTransaction.model_validate(data["shortOrderCancelTransaction"])

        return result
