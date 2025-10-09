# Trades Endpoint

**OANDA Reference**: [Trade Endpoints](https://developer.oanda.com/rest-live-v20/trade-ep/)

Trade monitoring and management.

---

## get_trades

Get a list of trades for an account.

**OANDA Endpoint**: `GET /v3/accounts/{accountID}/trades`

<!-- code-block: trades__get_trades -->
```python
import asyncio

from dotenv import load_dotenv

from fivetwenty import AsyncClient
from fivetwenty.endpoints.trades import TradesResponse
from fivetwenty.models import TradeStateFilter

load_dotenv()


async def main() -> None:
    async with AsyncClient() as client:
        # Get list of trades filtered by state
        result: TradesResponse = await client.trades.get_trades(
            account_id=client.account_id,
            state=TradeStateFilter.CLOSED,
            count=20,
        )
        print(f"Found {len(result['trades'])} trades")
        print(f"Last Transaction ID: {result['lastTransactionID']}")


asyncio.run(main())
```

🔗 **OANDA Documentation**: [Get Trades](https://developer.oanda.com/rest-live-v20/trade-ep/#get-trades)

🔗 **Source**: [trades.get_trades](https://github.com/NimbleOx/fivetwenty/blob/main/fivetwenty/endpoints/trades.py)

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `account_id` | AccountID | ✅ | Account identifier |
| `*` | | | **Keyword-only parameters below** |
| `ids` | list[TradeID] \| None | ➖ | List of trade IDs to retrieve |
| `state` | TradeStateFilter | ➖ | Filter trades by state (default: OPEN) |
| `instrument` | InstrumentName \| None | ➖ | Filter trades by instrument |
| `count` | int | ➖ | Maximum number of trades to return (default: 50, max: 500) |
| `before_id` | TradeID \| None | ➖ | Maximum trade ID to return |

**Returns:** `TradesResponse` - Dictionary containing trades (`list[Trade]`) and lastTransactionID (`str`)

**Raises:**

`FiveTwentyError` - API errors:

- 400: Invalid request parameters (check `e.is_bad_request`)
- 401/403: Authentication failed (check `e.is_authentication_error`)
- 404: Account not found (check `e.is_not_found`)
- 429: Rate limit exceeded (check `e.is_rate_limited`)

---

## get_open_trades

Get all open trades for account.

**OANDA Endpoint**: `GET /v3/accounts/{accountID}/openTrades`

<!-- code-block: trades__get_open_trades -->
```python
import asyncio

from dotenv import load_dotenv

from fivetwenty import AsyncClient
from fivetwenty.endpoints.trades import TradesResponse

load_dotenv()


async def main() -> None:
    async with AsyncClient() as client:
        # Get all currently open trades
        result: TradesResponse = await client.trades.get_open_trades(
            account_id=client.account_id
        )
        print(f"Open trades: {len(result['trades'])}")
        print(f"Last Transaction ID: {result['lastTransactionID']}")


asyncio.run(main())
```

🔗 **OANDA Documentation**: [Get Open Trades](https://developer.oanda.com/rest-live-v20/trade-ep/#get-open-trades)

🔗 **Source**: [trades.get_open_trades](https://github.com/NimbleOx/fivetwenty/blob/main/fivetwenty/endpoints/trades.py)

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `account_id` | AccountID | ✅ | Target account identifier |

**Returns:** `TradesResponse` - Dictionary containing trades (`list[Trade]`) and lastTransactionID (`str`)

**Raises:**

`FiveTwentyError` - API errors:

- 400: Invalid request parameters (check `e.is_bad_request`)
- 401/403: Authentication failed (check `e.is_authentication_error`)
- 404: Account not found (check `e.is_not_found`)
- 429: Rate limit exceeded (check `e.is_rate_limited`)

---

## get_trade

Get specific trade details.

**OANDA Endpoint**: `GET /v3/accounts/{accountID}/trades/{tradeSpecifier}`

<!-- code-block: trades__get_trade -->
```python
import asyncio

from dotenv import load_dotenv

from fivetwenty import AsyncClient
from fivetwenty.endpoints.trades import TradeResponse

load_dotenv()


async def main() -> None:
    async with AsyncClient() as client:
        # Get details for a specific trade by ID
        result: TradeResponse = await client.trades.get_trade(
            account_id=client.account_id,
            trade_specifier="20984",  # Change to your trade ID
        )
        trade = result["trade"]
        print(f"Trade ID: {trade.id}")
        print(f"Last Transaction ID: {result['lastTransactionID']}")


asyncio.run(main())
```

🔗 **OANDA Documentation**: [Get Trade Details](https://developer.oanda.com/rest-live-v20/trade-ep/#get-trade-details)

🔗 **Source**: [trades.get_trade](https://github.com/NimbleOx/fivetwenty/blob/main/fivetwenty/endpoints/trades.py)

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `account_id` | AccountID | ✅ | Target account identifier |
| `trade_specifier` | str | ✅ | Trade ID or @clientID |

**Returns:** `TradeResponse` - Dictionary containing trade (`Trade`) and lastTransactionID (`str`)

**Raises:**

`FiveTwentyError` - API errors:

- 400: Invalid request parameters (check `e.is_bad_request`)
- 401/403: Authentication failed (check `e.is_authentication_error`)
- 404: Trade not found (check `e.is_not_found`)
- 429: Rate limit exceeded (check `e.is_rate_limited`)

---

## close_trade

Close a trade (fully or partially).

**OANDA Endpoint**: `PUT /v3/accounts/{accountID}/trades/{tradeSpecifier}/close`

<!-- code-block: trades__close_trade -->
```python
import asyncio

from dotenv import load_dotenv

from fivetwenty import AsyncClient
from fivetwenty.endpoints.trades import CloseTradeResponse

load_dotenv()


async def main() -> None:
    async with AsyncClient() as client:
        # Close a trade partially or fully
        result: CloseTradeResponse = await client.trades.close_trade(
            account_id=client.account_id,
            trade_specifier="20984",  # Change to your trade ID
            units="1000",  # Omit to close entire trade
        )
        print(f"Last Transaction ID: {result['lastTransactionID']}")


asyncio.run(main())
```

🔗 **OANDA Documentation**: [Close Trade](https://developer.oanda.com/rest-live-v20/trade-ep/#close-trade)

🔗 **Source**: [trades.close_trade](https://github.com/NimbleOx/fivetwenty/blob/main/fivetwenty/endpoints/trades.py)

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `account_id` | AccountID | ✅ | Account identifier |
| `trade_specifier` | str | ✅ | Trade ID or @clientID |
| `*` | | | **Keyword-only parameters below** |
| `units` | str \| None | ➖ | Number of units to close (default: ALL for full closure) |

**Returns:** `CloseTradeResponse` - Dictionary containing orderCreateTransaction, orderFillTransaction, orderCancelTransaction, relatedTransactionIDs, and lastTransactionID

**Raises:**

`FiveTwentyError` - API errors:

- 400: Invalid request parameters (check `e.is_bad_request`)
- 401/403: Authentication failed (check `e.is_authentication_error`)
- 404: Trade not found (check `e.is_not_found`)
- 429: Rate limit exceeded (check `e.is_rate_limited`)

---

## put_trade_client_extensions

Modify client extensions for existing trade.

**OANDA Endpoint**: `PUT /v3/accounts/{accountID}/trades/{tradeSpecifier}/clientExtensions`

<!-- code-block: trades__put_trade_client_extensions -->
```python
import asyncio

from dotenv import load_dotenv

from fivetwenty import AsyncClient
from fivetwenty.endpoints.trades import TradeClientExtensionsResponse
from fivetwenty.models import ClientExtensions

load_dotenv()


async def main() -> None:
    async with AsyncClient() as client:
        # Update client extensions (comment, tag, id) for a trade
        result: TradeClientExtensionsResponse = (
            await client.trades.put_trade_client_extensions(
                account_id=client.account_id,
                trade_specifier="20984",  # Change to your trade ID
                client_extensions=ClientExtensions(comment="Updated comment"),
            )
        )
        print(f"Last Transaction ID: {result['lastTransactionID']}")


asyncio.run(main())
```

🔗 **OANDA Documentation**: [Update Trade Client Extensions](https://developer.oanda.com/rest-live-v20/trade-ep/#update-trade-client-extensions)

🔗 **Source**: [trades.put_trade_client_extensions](https://github.com/NimbleOx/fivetwenty/blob/main/fivetwenty/endpoints/trades.py)

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `account_id` | AccountID | ✅ | Target account identifier |
| `trade_specifier` | str | ✅ | Trade identifier to modify |
| `*` | | | **Keyword-only parameters below** |
| `client_extensions` | ClientExtensions \| None | ➖ | New trade client extensions |

**Returns:** `TradeClientExtensionsResponse` - Dictionary containing tradeClientExtensionsModifyTransaction, relatedTransactionIDs, and lastTransactionID

**Raises:**

`FiveTwentyError` - API errors:

- 400: Invalid request parameters (check `e.is_bad_request`)
- 401/403: Authentication failed (check `e.is_authentication_error`)
- 404: Trade not found (check `e.is_not_found`)
- 429: Rate limit exceeded (check `e.is_rate_limited`)

---

## put_trade_orders

Update trade-dependent orders (take profit, stop loss, etc.).

**OANDA Endpoint**: `PUT /v3/accounts/{accountID}/trades/{tradeSpecifier}/orders`

<!-- code-block: trades__put_trade_orders -->
```python
import asyncio
from decimal import Decimal

from dotenv import load_dotenv

from fivetwenty import AsyncClient
from fivetwenty.endpoints.trades import TradeOrdersResponse
from fivetwenty.models import StopLossDetails, TakeProfitDetails

load_dotenv()


async def main() -> None:
    async with AsyncClient() as client:
        # Set or update take profit and stop loss orders for a trade
        result: TradeOrdersResponse = await client.trades.put_trade_orders(
            account_id=client.account_id,
            trade_specifier="21001",  # Change to your trade ID
            take_profit=TakeProfitDetails(price=Decimal("1.1500")),
            stop_loss=StopLossDetails(price=Decimal("1.1200")),
        )
        print(f"Last Transaction ID: {result['lastTransactionID']}")


asyncio.run(main())
```

🔗 **OANDA Documentation**: [Update Trade Dependent Orders](https://developer.oanda.com/rest-live-v20/trade-ep/#update-trade-dependent-orders)

🔗 **Source**: [trades.put_trade_orders](https://github.com/NimbleOx/fivetwenty/blob/main/fivetwenty/endpoints/trades.py)

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `account_id` | AccountID | ✅ | Target account identifier |
| `trade_specifier` | str | ✅ | Trade identifier to modify |
| `*` | | | **Keyword-only parameters below** |
| `take_profit` | TakeProfitDetails \| None | ➖ | Take profit order specification |
| `stop_loss` | StopLossDetails \| None | ➖ | Stop loss order specification |
| `trailing_stop_loss` | TrailingStopLossDetails \| None | ➖ | Trailing stop loss order specification |
| `guaranteed_stop_loss` | GuaranteedStopLossDetails \| None | ➖ | Guaranteed stop loss order specification |

**Returns:** `TradeOrdersResponse` - Dictionary containing order transaction details (takeProfitOrderCancelTransaction, takeProfitOrderTransaction, stopLossOrderTransaction, etc.), relatedTransactionIDs, and lastTransactionID

**Raises:**

`FiveTwentyError` - API errors:

- 400: Invalid request parameters (check `e.is_bad_request`)
- 401/403: Authentication failed (check `e.is_authentication_error`)
- 404: Trade not found (check `e.is_not_found`)
- 429: Rate limit exceeded (check `e.is_rate_limited`)
