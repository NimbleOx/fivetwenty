# Trades Endpoint

**OANDA Reference**: [Trade Endpoints](https://developer.oanda.com/rest-live-v20/trade-ep/)

Trade monitoring and management.

---

## get_trades
<!-- fragment: Demo get_trades with return type annotations and unused import patterns -->
```python
import asyncio
from fivetwenty import AsyncClient
from fivetwenty.models import TradeStateFilter
from fivetwenty.endpoints.trades import TradesResponse


async def main() -> None:
    async with AsyncClient(token="demo-token", account_id="your-account-id") as client:
        # trades.get_trades(account_id: AccountID, ids: list[TradeID] | None = None,
        #            state: TradeStateFilter = TradeStateFilter.OPEN,
        #            instrument: InstrumentName | None = None, count: int = 50,
        #            before_id: TradeID | None = None) -> TradesResponse
        # Returns: {"trades": list[Trade], "lastTransactionID": str}

        # Example usage:
        result: TradesResponse = await client.trades.get_trades(
            account_id="123-456-789",
            state=TradeStateFilter.OPEN,
            count=20,
        )
        trades = result["trades"]
        print(f"Found {len(trades)} trades")
        print(f"Last Transaction ID: {result['lastTransactionID']}")


if __name__ == "__main__":
    asyncio.run(main())
```
🔗 **OANDA Endpoint**: `GET /v3/accounts/{accountID}/trades`

**OANDA Documentation**: [Get Trades](https://developer.oanda.com/rest-live-v20/trade-ep/#get-trades)

Get a list of trades for an account.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `account_id` | AccountID | ✅ | Account identifier |
| `ids` | list[TradeID] | ➖ | List of trade IDs to retrieve |
| `state` | TradeStateFilter | ➖ | Filter trades by state (default: OPEN) |
| `instrument` | InstrumentName | ➖ | Filter trades by instrument |
| `count` | int | ➖ | Maximum number of trades to return (default: 50, max: 500) |
| `before_id` | TradeID | ➖ | Maximum trade ID to return |

**Returns:** Dictionary containing list of trades (`list[Trade]`) and last transaction ID (`str`)

**Raises:**

- `FiveTwentyError` - API errors

---

## get_open_trades
<!-- fragment: Demo get_open_trades with missing return type annotation patterns -->
```python
import asyncio
from fivetwenty import AsyncClient
from fivetwenty.endpoints.trades import TradesResponse


async def get_open_trades_example() -> None:
    async with AsyncClient(token="demo-token") as client:
        # trades.get_open_trades(account_id: AccountID) -> TradesResponse
        # Returns: {"trades": list[Trade], "lastTransactionID": str}

        # Example usage:
        result: TradesResponse = await client.trades.get_open_trades(account_id="123-456-789")
        trades = result["trades"]
        print(f"Open trades: {len(trades)}")
        print(f"Last Transaction ID: {result['lastTransactionID']}")
```
🔗 **OANDA Endpoint**: `GET /v3/accounts/{accountID}/openTrades`

**OANDA Documentation**: [Get Open Trades](https://developer.oanda.com/rest-live-v20/trade-ep/#get-open-trades)

Get all open trades for account.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `account_id` | AccountID | ✅ | Target account identifier |

**Returns:** Dictionary containing list of open trades (`list[Trade]`) and last transaction ID (`str`)

**Raises:**

- `FiveTwentyError` - API errors

---

## get_trade
<!-- fragment: Demo get_trade with missing return type annotation patterns -->
```python
import asyncio
from fivetwenty import AsyncClient
from fivetwenty.endpoints.trades import TradeResponse


async def get_trade_example() -> None:
    async with AsyncClient(token="demo-token") as client:
        # trades.get_trade(account_id: AccountID, trade_specifier: str) -> TradeResponse
        # Returns: {"trade": Trade, "lastTransactionID": str}

        # Example usage:
        result: TradeResponse = await client.trades.get_trade(
            account_id="123-456-789",
            trade_specifier="12345"
        )
        trade = result["trade"]
        print(f"Trade ID: {trade.id}")
        print(f"Last Transaction ID: {result['lastTransactionID']}")
```
🔗 **OANDA Endpoint**: `GET /v3/accounts/{accountID}/trades/{tradeSpecifier}`

**OANDA Documentation**: [Get Trade Details](https://developer.oanda.com/rest-live-v20/trade-ep/#get-trade-details)

Get specific trade details.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `account_id` | AccountID | ✅ | Target account identifier |
| `trade_specifier` | str | ✅ | Trade ID or @clientID |

**Returns:** Dictionary containing trade details (`Trade`) and last transaction ID (`str`)

**Raises:**

- `FiveTwentyError` - API errors or invalid trade ID

---

## close_trade
<!-- fragment: Demo close_trade with missing return type annotation patterns -->
```python
import asyncio
from fivetwenty import AsyncClient
from fivetwenty.endpoints.trades import CloseTradeResponse


async def close_trade_example() -> None:
    async with AsyncClient(token="demo-token") as client:
        # trades.close_trade(account_id: AccountID, trade_specifier: str,
        #             units: str | None = None, idempotency_key: str | None = None) -> CloseTradeResponse
        # Returns: {"orderCreateTransaction": Any, "orderFillTransaction": Any,
        #           "orderCancelTransaction": Any, "relatedTransactionIDs": list[str],
        #           "lastTransactionID": str} (fields are optional)

        # Example usage:
        result: CloseTradeResponse = await client.trades.close_trade(
            account_id="123-456-789",
            trade_specifier="12345",
            units="1000"
        )
        print(f"Last Transaction ID: {result['lastTransactionID']}")
```
🔗 **OANDA Endpoint**: `PUT /v3/accounts/{accountID}/trades/{tradeSpecifier}/close`

**OANDA Documentation**: [Close Trade](https://developer.oanda.com/rest-live-v20/trade-ep/#close-trade)

Close a trade (fully or partially).

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `account_id` | AccountID | ✅ | Account identifier |
| `trade_specifier` | str | ✅ | Trade ID or @clientID |
| `units` | str | ➖ | Number of units to close (default: ALL for full closure) |
| `idempotency_key` | str | ➖ | Idempotency key for duplicate prevention |

**Returns:** Dictionary containing closure transaction details and last transaction ID (`str`)

**Raises:**

- `FiveTwentyError` - API errors

---

## put_trade_client_extensions
<!-- fragment: Demo put_trade_client_extensions with unused variables and return type patterns -->
```python
import asyncio
from fivetwenty import AsyncClient
from fivetwenty.endpoints.trades import TradeClientExtensionsResponse


async def main() -> None:
    async with AsyncClient() as client:
        # trades.put_trade_client_extensions(account_id: AccountID, trade_specifier: str,
        #                                client_extensions: dict[str, Any] | None = None,
        #                                idempotency_key: str | None = None) -> TradeClientExtensionsResponse
        # Returns: {"tradeClientExtensionsModifyTransaction": Any, "relatedTransactionIDs": list[str],
        #           "lastTransactionID": str} (fields may be optional)

        # Example usage:
        result: TradeClientExtensionsResponse = await client.trades.put_trade_client_extensions(
            account_id="123-456-789",
            trade_specifier="12345",
            client_extensions={"comment": "Updated comment"},
        )
        print(f"Last Transaction ID: {result['lastTransactionID']}")

asyncio.run(main())
```
🔗 **OANDA Endpoint**: `PUT /v3/accounts/{accountID}/trades/{tradeSpecifier}/clientExtensions`

**OANDA Documentation**: [Update Trade Client Extensions](https://developer.oanda.com/rest-live-v20/trade-ep/#update-trade-client-extensions)

Modify client extensions for existing trade.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `account_id` | AccountID | ✅ | Target account identifier |
| `trade_specifier` | str | ✅ | Trade identifier to modify |
| `client_extensions` | dict[str, Any] | ➖ | New trade client extensions |
| `idempotency_key` | str | ➖ | Idempotency key for safe retries |

**Returns:** Dictionary containing modification transaction details and last transaction ID (`str`)

**Raises:**

- `FiveTwentyError` - API errors, trade not found, or modification failed

---

## put_trade_orders
<!-- fragment: Demo put_trade_orders with unused variables and return type patterns -->
```python
import asyncio
from fivetwenty import AsyncClient
from fivetwenty.endpoints.trades import TradeOrdersResponse


async def main() -> None:
    async with AsyncClient() as client:
        # trades.put_trade_orders(account_id: AccountID, trade_specifier: str,
        #              take_profit: dict[str, Any] | None = None,
        #              stop_loss: dict[str, Any] | None = None,
        #              trailing_stop_loss: dict[str, Any] | None = None,
        #              guaranteed_stop_loss: dict[str, Any] | None = None,
        #              idempotency_key: str | None = None) -> TradeOrdersResponse
        # Returns: {"takeProfitOrderCancelTransaction": Any, "stopLossOrderTransaction": Any, ...
        #           "relatedTransactionIDs": list[str], "lastTransactionID": str} (fields may be optional)

        # Example usage:
        result: TradeOrdersResponse = await client.trades.put_trade_orders(
            account_id="123-456-789",
            trade_specifier="12345",
            take_profit={"price": "1.1500"},
            stop_loss={"price": "1.1200"}
        )
        print(f"Last Transaction ID: {result['lastTransactionID']}")

asyncio.run(main())
```
🔗 **OANDA Endpoint**: `PUT /v3/accounts/{accountID}/trades/{tradeSpecifier}/orders`

**OANDA Documentation**: [Update Trade Dependent Orders](https://developer.oanda.com/rest-live-v20/trade-ep/#update-trade-dependent-orders)

Update trade-dependent orders (take profit, stop loss, etc.).

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `account_id` | AccountID | ✅ | Target account identifier |
| `trade_specifier` | str | ✅ | Trade identifier to modify |
| `take_profit` | dict[str, Any] | ➖ | Take profit order specification |
| `stop_loss` | dict[str, Any] | ➖ | Stop loss order specification |
| `trailing_stop_loss` | dict[str, Any] | ➖ | Trailing stop loss order specification |
| `guaranteed_stop_loss` | dict[str, Any] | ➖ | Guaranteed stop loss order specification |
| `idempotency_key` | str | ➖ | Idempotency key for safe retries |

**Returns:** Dictionary containing order update transaction details and last transaction ID (`str`)

**Raises:**

- `FiveTwentyError` - API errors, trade not found, or update failed