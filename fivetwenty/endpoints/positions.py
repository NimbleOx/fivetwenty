"""Position management endpoints."""

from decimal import Decimal
from typing import TYPE_CHECKING, Any

from ..models import (
    AccountID,
    ClientExtensions,
    InstrumentName,
)

if TYPE_CHECKING:
    from ..client import AsyncClient


class PositionEndpoints:
    """Position management operations."""

    def __init__(self, client: "AsyncClient"):
        self._client = client

    async def get_positions(self, account_id: AccountID) -> dict[str, Any]:
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
        return response.json()  # type: ignore[no-any-return]

    async def get_open_positions(self, account_id: AccountID) -> dict[str, Any]:
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
        return response.json()  # type: ignore[no-any-return]

    async def get_position(self, account_id: AccountID, instrument: InstrumentName) -> dict[str, Any]:
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
        return response.json()  # type: ignore[no-any-return]

    async def close_position(
        self,
        account_id: AccountID,
        instrument: InstrumentName,
        *,
        long_units: str | Decimal | None = None,
        short_units: str | Decimal | None = None,
        long_client_extensions: ClientExtensions | dict[str, str] | None = None,
        short_client_extensions: ClientExtensions | dict[str, str] | None = None,
    ) -> dict[str, Any]:
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
            if isinstance(long_client_extensions, ClientExtensions):
                body["longClientExtensions"] = long_client_extensions.model_dump(by_alias=True, exclude_none=True)
            else:
                body["longClientExtensions"] = long_client_extensions
        if short_client_extensions is not None:
            if isinstance(short_client_extensions, ClientExtensions):
                body["shortClientExtensions"] = short_client_extensions.model_dump(by_alias=True, exclude_none=True)
            else:
                body["shortClientExtensions"] = short_client_extensions

        instrument_str = instrument.value if hasattr(instrument, "value") else str(instrument)
        response = await self._client._request(
            "PUT",
            f"/accounts/{account_id}/positions/{instrument_str}/close",
            json_data=body,
        )
        return response.json()  # type: ignore[no-any-return]
