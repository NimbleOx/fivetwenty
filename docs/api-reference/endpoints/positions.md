# Positions Endpoint

📖 **OANDA Reference**: [Position Endpoints](https://developer.oanda.com/rest-live-v20/position-ep/)

Position monitoring and management.

---

## get_positions
```python
import asyncio
from fivetwenty import AsyncClient


async def main() -> None:
    async with AsyncClient() as client:
        # positions.get_positions(account_id: AccountID) -> dict[str, Any]

        # Example usage:
        _positions = await client.positions.get_positions(account_id="123-456-789")

asyncio.run(main())
```
🔗 **OANDA Endpoint**: `GET /v3/accounts/{accountID}/positions`

📖 **OANDA Documentation**: [Get Positions](https://developer.oanda.com/rest-live-v20/position-ep/#get-positions)

Get a list of all positions for an account.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `account_id` | AccountID | ✅ | Account identifier |

**Returns:** Dictionary containing list of positions and last transaction ID

**Raises:**

- `FiveTwentyError` - API errors

---

## get_open_positions
```python
import asyncio
from fivetwenty import AsyncClient

async def main() -> None:
    async with AsyncClient() as client:
        # positions.get_open_positions(account_id: AccountID) -> dict[str, Any]

        # Example usage:
        _open_positions = await client.positions.get_open_positions(account_id="123-456-789")

asyncio.run(main())
```
🔗 **OANDA Endpoint**: `GET /v3/accounts/{accountID}/openPositions`

📖 **OANDA Documentation**: [Get Open Positions](https://developer.oanda.com/rest-live-v20/position-ep/#get-open-positions)

Get a list of all open positions for an account.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `account_id` | AccountID | ✅ | Account identifier |

**Returns:** Dictionary containing list of open positions and last transaction ID

**Raises:**

- `FiveTwentyError` - API errors

---

## get_position
<!-- fragment: Demo get_position with argument type patterns -->
```python
import asyncio
from fivetwenty import AsyncClient

async def main() -> None:
    async with AsyncClient() as client:
        # positions.get_position(account_id: AccountID, instrument: InstrumentName) -> dict[str, Any]

        # Example usage:
        _position = await client.positions.get_position(
            account_id="123-456-789",
            instrument="EUR_USD"
        )

asyncio.run(main())
```
🔗 **OANDA Endpoint**: `GET /v3/accounts/{accountID}/positions/{instrument}`

📖 **OANDA Documentation**: [Get Position](https://developer.oanda.com/rest-live-v20/position-ep/#get-position)

Get the position for a specific instrument in an account.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `account_id` | AccountID | ✅ | Account identifier |
| `instrument` | InstrumentName | ✅ | Name of the instrument |

**Returns:** Dictionary containing position details and last transaction ID

**Raises:**

- `FiveTwentyError` - API errors (404 if no position exists)

---

## close_position
<!-- fragment: Demo close_position with argument type patterns -->
```python
import asyncio
from fivetwenty import AsyncClient


async def main() -> None:
    async with AsyncClient() as client:
        # positions.close_position(account_id: AccountID, instrument: InstrumentName,
        #                long_units: str | Decimal | None = None,
        #                short_units: str | Decimal | None = None,
        #                long_client_extensions: ClientExtensions | dict[str, str] | None = None,
        #                short_client_extensions: ClientExtensions | dict[str, str] | None = None) -> dict[str, Any]

        # Example usage:
        _result = await client.positions.close_position(
            account_id="123-456-789",
            instrument="EUR_USD",
            long_units="ALL",
        )

asyncio.run(main())
```
🔗 **OANDA Endpoint**: `PUT /v3/accounts/{accountID}/positions/{instrument}/close`

📖 **OANDA Documentation**: [Close Position](https://developer.oanda.com/rest-live-v20/position-ep/#close-position)

Close the open position for a specific instrument.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `account_id` | AccountID | ✅ | Account identifier |
| `instrument` | InstrumentName | ✅ | Name of the instrument |
| `long_units` | str &#124; Decimal | ➖ | Units of long position to close ("ALL", "NONE", or number) |
| `short_units` | str &#124; Decimal | ➖ | Units of short position to close ("ALL", "NONE", or number) |
| `long_client_extensions` | ClientExtensions &#124; dict[str, str] | ➖ | Client extensions for long position closure order |
| `short_client_extensions` | ClientExtensions &#124; dict[str, str] | ➖ | Client extensions for short position closure order |

**Returns:** Dictionary containing closure transaction details

**Raises:**

- `FiveTwentyError` - API errors