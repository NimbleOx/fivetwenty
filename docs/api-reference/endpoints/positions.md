# Positions Endpoint

**OANDA Reference**: [Position Endpoints](https://developer.oanda.com/rest-live-v20/position-ep/)

Position monitoring and management.

---

## get_positions
```python
import asyncio
from typing import TYPE_CHECKING

from fivetwenty import AsyncClient

if TYPE_CHECKING:
    from fivetwenty.endpoints.positions import PositionsResponse


async def main() -> None:
    async with AsyncClient() as client:
        # positions.get_positions(account_id: AccountID) -> PositionsResponse
        # Returns: {"positions": list[Position], "lastTransactionID": str}

        result: PositionsResponse = await client.positions.get_positions(
            account_id=client.account_id
        )
        positions = result["positions"]
        print(f"Found {len(positions)} position(s)")
        print(f"Last Transaction ID: {result['lastTransactionID']}")


asyncio.run(main())
```
🔗 **OANDA Endpoint**: `GET /v3/accounts/{accountID}/positions`

**OANDA Documentation**: [Get Positions](https://developer.oanda.com/rest-live-v20/position-ep/#get-positions)

Get a list of all positions for an account.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `account_id` | AccountID | ✅ | Account identifier |

**Returns:** Dictionary containing list of positions (`list[Position]`) and last transaction ID (`str`)

**Raises:**

- `FiveTwentyError` - API errors

---

## get_open_positions
```python
import asyncio
from typing import TYPE_CHECKING

from fivetwenty import AsyncClient

if TYPE_CHECKING:
    from fivetwenty.endpoints.positions import PositionsResponse


async def main() -> None:
    async with AsyncClient() as client:
        # positions.get_open_positions(account_id: AccountID) -> PositionsResponse
        # Returns: {"positions": list[Position], "lastTransactionID": str}

        result: PositionsResponse = await client.positions.get_open_positions(
            account_id=client.account_id
        )
        open_positions = result["positions"]
        print(f"Found {len(open_positions)} open position(s)")
        print(f"Last Transaction ID: {result['lastTransactionID']}")


asyncio.run(main())
```
🔗 **OANDA Endpoint**: `GET /v3/accounts/{accountID}/openPositions`

**OANDA Documentation**: [Get Open Positions](https://developer.oanda.com/rest-live-v20/position-ep/#get-open-positions)

Get a list of all open positions for an account.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `account_id` | AccountID | ✅ | Account identifier |

**Returns:** Dictionary containing list of open positions (`list[Position]`) and last transaction ID (`str`)

**Raises:**

- `FiveTwentyError` - API errors

---

## get_position
```python
import asyncio
from typing import TYPE_CHECKING

from fivetwenty import AsyncClient

if TYPE_CHECKING:
    from fivetwenty.endpoints.positions import PositionResponse


async def main() -> None:
    async with AsyncClient() as client:
        # positions.get_position(account_id: AccountID, instrument: InstrumentName) -> PositionResponse
        # Returns: {"position": Position, "lastTransactionID": str}

        result: PositionResponse = await client.positions.get_position(
            account_id=client.account_id,
            instrument="EUR_USD"
        )
        position = result["position"]
        print(f"Instrument: {position.instrument}")
        print(f"Last Transaction ID: {result['lastTransactionID']}")


asyncio.run(main())
```
🔗 **OANDA Endpoint**: `GET /v3/accounts/{accountID}/positions/{instrument}`

**OANDA Documentation**: [Get Position](https://developer.oanda.com/rest-live-v20/position-ep/#get-position)

Get the position for a specific instrument in an account.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `account_id` | AccountID | ✅ | Account identifier |
| `instrument` | InstrumentName | ✅ | Name of the instrument |

**Returns:** Dictionary containing position details (`Position`) and last transaction ID (`str`)

**Raises:**

- `FiveTwentyError` - API errors (404 if no position exists)

---

## close_position
```python
import asyncio
from typing import TYPE_CHECKING

from fivetwenty import AsyncClient

if TYPE_CHECKING:
    from fivetwenty.endpoints.positions import ClosePositionResponse


async def main() -> None:
    async with AsyncClient() as client:
        # positions.close_position(account_id: AccountID, instrument: InstrumentName, *,
        #                          long_units: str | Decimal | None = None,
        #                          short_units: str | Decimal | None = None,
        #                          long_client_extensions: ClientExtensions | dict[str, str] | None = None,
        #                          short_client_extensions: ClientExtensions | dict[str, str] | None = None) -> ClosePositionResponse

        result: ClosePositionResponse = await client.positions.close_position(
            account_id=client.account_id,
            instrument="EUR_USD",
            long_units="ALL",
        )
        print(f"Last Transaction ID: {result['lastTransactionID']}")
        if "longOrderFillTransaction" in result:
            print(f"Long position closed: {result['longOrderFillTransaction']}")


asyncio.run(main())
```
🔗 **OANDA Endpoint**: `PUT /v3/accounts/{accountID}/positions/{instrument}/close`

**OANDA Documentation**: [Close Position](https://developer.oanda.com/rest-live-v20/position-ep/#close-position)

Close the open position for a specific instrument.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `account_id` | AccountID | ✅ | Account identifier |
| `instrument` | InstrumentName | ✅ | Name of the instrument |
| `*` | | | **Keyword-only parameters below** |
| `long_units` | str \| Decimal \| None | ➖ | Units of long position to close ("ALL", "NONE", or number) |
| `short_units` | str \| Decimal \| None | ➖ | Units of short position to close ("ALL", "NONE", or number) |
| `long_client_extensions` | ClientExtensions \| dict[str, str] \| None | ➖ | Client extensions for long position closure order |
| `short_client_extensions` | ClientExtensions \| dict[str, str] \| None | ➖ | Client extensions for short position closure order |

**Returns:** Dictionary containing closure transaction details and last transaction ID (`str`)

**Raises:**

- `FiveTwentyError` - API errors