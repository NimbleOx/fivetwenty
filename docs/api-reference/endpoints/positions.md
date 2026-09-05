# Positions Endpoint

**OANDA Reference**: [Position Endpoints](https://developer.oanda.com/rest-live-v20/position-ep/)

Position monitoring and management.

The examples below illustrate calls and response access. Helpers run only when
called. Examples that create, update, cancel or close resources change account
state; use a dedicated practice account and inspect each response. Local validation
and HTTPX transport exceptions can occur in addition to the API errors listed.

---

## get_positions

Get a list of all positions (open and closed) for an account.

**OANDA Endpoint**: `GET /v3/accounts/{accountID}/positions`

<!-- code-block: positions__get_positions -->
```python
import asyncio
from typing import TYPE_CHECKING

from dotenv import load_dotenv

from fivetwenty import AsyncClient

if TYPE_CHECKING:
    from fivetwenty.endpoints.positions import PositionsResponse

load_dotenv()


async def main() -> None:
    async with AsyncClient() as client:
        # Retrieve all positions (open and closed) for the account
        result: PositionsResponse = await client.positions.get_positions(
            account_id=client.account_id
        )
        positions = result["positions"]
        print(f"Found {len(positions)} position(s)")
        print(f"Last Transaction ID: {result['lastTransactionID']}")


asyncio.run(main())
```

🔗 **OANDA Documentation**: [Get Positions](https://developer.oanda.com/rest-live-v20/position-ep/#get-positions)

🔗 **Source**: [positions.get_positions](https://github.com/NimbleOx/fivetwenty/blob/main/fivetwenty/endpoints/positions.py)

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `account_id` | AccountID | ✅ | Account identifier |

**Returns:** Dictionary containing list of positions (`list[Position]`) and last transaction ID (`str`)

**Raises:**

`FiveTwentyError` - API errors:

- 401/403: Authentication failed (check `e.is_authentication_error`)
- 404: Account not found (check `e.is_not_found`)
- 429: Rate limit exceeded (check `e.is_rate_limited`)

---

## get_open_positions

Get a list of all open positions for an account.

**OANDA Endpoint**: `GET /v3/accounts/{accountID}/openPositions`

<!-- code-block: positions__get_open_positions -->
```python
import asyncio
from typing import TYPE_CHECKING

from dotenv import load_dotenv

from fivetwenty import AsyncClient

if TYPE_CHECKING:
    from fivetwenty.endpoints.positions import PositionsResponse

load_dotenv()


async def main() -> None:
    async with AsyncClient() as client:
        # Retrieve only open positions for the account
        result: PositionsResponse = await client.positions.get_open_positions(
            account_id=client.account_id
        )
        open_positions = result["positions"]
        print(f"Found {len(open_positions)} open position(s)")
        print(f"Last Transaction ID: {result['lastTransactionID']}")


asyncio.run(main())
```

🔗 **OANDA Documentation**: [Get Open Positions](https://developer.oanda.com/rest-live-v20/position-ep/#get-open-positions)

🔗 **Source**: [positions.get_open_positions](https://github.com/NimbleOx/fivetwenty/blob/main/fivetwenty/endpoints/positions.py)

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `account_id` | AccountID | ✅ | Account identifier |

**Returns:** Dictionary containing list of open positions (`list[Position]`) and last transaction ID (`str`)

**Raises:**

`FiveTwentyError` - API errors:

- 401/403: Authentication failed (check `e.is_authentication_error`)
- 404: Account not found (check `e.is_not_found`)
- 429: Rate limit exceeded (check `e.is_rate_limited`)

---

## get_position

Get the position for a specific instrument in an account.

**OANDA Endpoint**: `GET /v3/accounts/{accountID}/positions/{instrument}`

<!-- code-block: positions__get_position -->
```python
import asyncio
from typing import TYPE_CHECKING

from dotenv import load_dotenv

from fivetwenty import AsyncClient
from fivetwenty.models import InstrumentName

if TYPE_CHECKING:
    from fivetwenty.endpoints.positions import PositionResponse

load_dotenv()


async def main() -> None:
    async with AsyncClient() as client:
        # Get position details for a specific instrument
        result: PositionResponse = await client.positions.get_position(
            account_id=client.account_id,
            instrument=InstrumentName.EUR_USD,  # Change to your instrument
        )
        position = result["position"]
        print(f"Instrument: {position.instrument}")
        print(f"Last Transaction ID: {result['lastTransactionID']}")


asyncio.run(main())
```

🔗 **OANDA Documentation**: [Get Position](https://developer.oanda.com/rest-live-v20/position-ep/#get-position)

🔗 **Source**: [positions.get_position](https://github.com/NimbleOx/fivetwenty/blob/main/fivetwenty/endpoints/positions.py)

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `account_id` | AccountID | ✅ | Account identifier |
| `instrument` | InstrumentName | ✅ | Name of the instrument |

**Returns:** Dictionary containing position details (`Position`) and last transaction ID (`str`)

**Raises:**

`FiveTwentyError` - API errors:

- 401/403: Authentication failed (check `e.is_authentication_error`)
- 404: Position not found (check `e.is_not_found`)
- 429: Rate limit exceeded (check `e.is_rate_limited`)

---

## close_position

Close selected sides of an instrument position. Specify `"ALL"`, `"NONE"`, or a
positive quantity for each side you intend to control; short-side closure also
uses a positive quantity. Omitting a side does not explicitly request its closure.
Inspect both requested sides' transaction results. Closing exposure does not cancel
unrelated pending entry orders.

**OANDA Endpoint**: `PUT /v3/accounts/{accountID}/positions/{instrument}/close`

<!-- code-block: positions__close_position -->
```python
import asyncio
from typing import TYPE_CHECKING

from dotenv import load_dotenv

from fivetwenty import AsyncClient
from fivetwenty.models import InstrumentName

if TYPE_CHECKING:
    from fivetwenty.endpoints.positions import ClosePositionResponse

load_dotenv()


async def main() -> None:
    async with AsyncClient() as client:
        # Close all long units for a specific instrument
        result: ClosePositionResponse = await client.positions.close_position(
            account_id=client.account_id,
            instrument=InstrumentName.EUR_USD,  # Change to your instrument
            long_units="ALL",  # Use "ALL" to close entire position, or specify units
        )
        print(f"Last Transaction ID: {result['lastTransactionID']}")
        if "longOrderFillTransaction" in result:
            print(f"Long position closed: {result['longOrderFillTransaction']}")


asyncio.run(main())
```

🔗 **OANDA Documentation**: [Close Position](https://developer.oanda.com/rest-live-v20/position-ep/#close-position)

🔗 **Source**: [positions.close_position](https://github.com/NimbleOx/fivetwenty/blob/main/fivetwenty/endpoints/positions.py)

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `account_id` | AccountID | ✅ | Account identifier |
| `instrument` | InstrumentName | ✅ | Name of the instrument |
| `*` | | | **Keyword-only parameters below** |
| `long_units` | str \| Decimal \| None | ➖ | Units of long position to close ("ALL", "NONE", or number) |
| `short_units` | str \| Decimal \| None | ➖ | Units of short position to close ("ALL", "NONE", or number) |
| `long_client_extensions` | ClientExtensions \| None | ➖ | Client extensions for long position closure order |
| `short_client_extensions` | ClientExtensions \| None | ➖ | Client extensions for short position closure order |

**Returns:** Dictionary containing closure transaction details and last transaction ID (`str`)

**Raises:**

`FiveTwentyError` - API errors:

- 400: Invalid request parameters (check `e.status == 400`)
- 401/403: Authentication failed (check `e.is_authentication_error`)
- 404: Position not found or already closed (check `e.is_not_found`)
- 429: Rate limit exceeded (check `e.is_rate_limited`)