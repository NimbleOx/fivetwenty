# Trades Endpoint

**OANDA Reference**: [Trade Endpoints](https://developer.oanda.com/rest-live-v20/trade-ep/)

Trade monitoring and management.

---

## get_trades

```python
import asyncio
from fivetwenty import AsyncClient
from fivetwenty.models import TradeStateFilter
from fivetwenty.endpoints.trades import TradesResponse


async def main() -> None:
    async with AsyncClient() as client:
        # trades.get_trades(account_id: AccountID, *, ids: list[TradeID] | None = None,
        #                   state: TradeStateFilter = TradeStateFilter.OPEN,
        #                   instrument: InstrumentName | None = None, count: int = 50,
        #                   before_id: TradeID | None = None) -> TradesResponse
        # Returns: {"trades": list[Trade], "lastTransactionID": str}

        result: TradesResponse = await client.trades.get_trades(
            client.account_id,
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
| `*` | | | **Keyword-only parameters below** |
| `ids` | list[TradeID] \| None | ➖ | List of trade IDs to retrieve |
| `state` | TradeStateFilter | ➖ | Filter trades by state (default: OPEN) |
| `instrument` | InstrumentName \| None | ➖ | Filter trades by instrument |
| `count` | int | ➖ | Maximum number of trades to return (default: 50, max: 500) |
| `before_id` | TradeID \| None | ➖ | Maximum trade ID to return |

**Returns:** Dictionary containing list of trades (`list[Trade]`) and last transaction ID (`str`)

**Raises:**

- `FiveTwentyError` - API errors

---

## get_open_trades

```python
import asyncio
from fivetwenty import AsyncClient
from fivetwenty.endpoints.trades import TradesResponse


async def main() -> None:
    async with AsyncClient() as client:
        # trades.get_open_trades(account_id: AccountID) -> TradesResponse
        # Returns: {"trades": list[Trade], "lastTransactionID": str}

        result: TradesResponse = await client.trades.get_open_trades(client.account_id)
        trades = result["trades"]
        print(f"Open trades: {len(trades)}")
        print(f"Last Transaction ID: {result['lastTransactionID']}")


if __name__ == "__main__":
    asyncio.run(main())
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

```python
import asyncio
from fivetwenty import AsyncClient
from fivetwenty.endpoints.trades import TradeResponse


async def main() -> None:
    async with AsyncClient() as client:
        # trades.get_trade(account_id: AccountID, trade_specifier: str) -> TradeResponse
        # Returns: {"trade": Trade, "lastTransactionID": str}

        result: TradeResponse = await client.trades.get_trade(
            client.account_id,
            trade_specifier="12345"
        )
        trade = result["trade"]
        print(f"Trade ID: {trade.id}")
        print(f"Last Transaction ID: {result['lastTransactionID']}")


if __name__ == "__main__":
    asyncio.run(main())
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

```python
import asyncio
from fivetwenty import AsyncClient
from fivetwenty.endpoints.trades import CloseTradeResponse


async def main() -> None:
    async with AsyncClient() as client:
        # trades.close_trade(account_id: AccountID, trade_specifier: str, *,
        #                    units: str | None = None, idempotency_key: str | None = None) -> CloseTradeResponse
        # Returns: {"orderCreateTransaction": MarketOrderTransaction, "orderFillTransaction": OrderFillTransaction,
        #           "orderCancelTransaction": OrderCancelTransaction, "relatedTransactionIDs": list[str],
        #           "lastTransactionID": str} (fields are optional)

        result: CloseTradeResponse = await client.trades.close_trade(
            client.account_id,
            trade_specifier="12345",
            units="1000"
        )
        print(f"Last Transaction ID: {result['lastTransactionID']}")


if __name__ == "__main__":
    asyncio.run(main())
```
🔗 **OANDA Endpoint**: `PUT /v3/accounts/{accountID}/trades/{tradeSpecifier}/close`

**OANDA Documentation**: [Close Trade](https://developer.oanda.com/rest-live-v20/trade-ep/#close-trade)

Close a trade (fully or partially).

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `account_id` | AccountID | ✅ | Account identifier |
| `trade_specifier` | str | ✅ | Trade ID or @clientID |
| `*` | | | **Keyword-only parameters below** |
| `units` | str \| None | ➖ | Number of units to close (default: ALL for full closure) |
| `idempotency_key` | str \| None | ➖ | Idempotency key for duplicate prevention |

**Returns:** Dictionary containing closure transaction details and last transaction ID (`str`)

**Raises:**

- `FiveTwentyError` - API errors

---

## put_trade_client_extensions

```python
import asyncio
from fivetwenty import AsyncClient
from fivetwenty.endpoints.trades import TradeClientExtensionsResponse
from fivetwenty.models import ClientExtensions


async def main() -> None:
    async with AsyncClient() as client:
        # trades.put_trade_client_extensions(account_id: AccountID, trade_specifier: str, *,
        #                                    client_extensions: ClientExtensions | None = None,
        #                                    idempotency_key: str | None = None) -> TradeClientExtensionsResponse
        # Returns: {"tradeClientExtensionsModifyTransaction": TradeClientExtensionsModifyTransaction,
        #           "relatedTransactionIDs": list[str], "lastTransactionID": str} (fields may be optional)

        result: TradeClientExtensionsResponse = await client.trades.put_trade_client_extensions(
            client.account_id,
            trade_specifier="12345",
            client_extensions=ClientExtensions(comment="Updated comment"),
        )
        print(f"Last Transaction ID: {result['lastTransactionID']}")


if __name__ == "__main__":
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
| `*` | | | **Keyword-only parameters below** |
| `client_extensions` | ClientExtensions \| None | ➖ | New trade client extensions |
| `idempotency_key` | str \| None | ➖ | Idempotency key for safe retries |

**Returns:** Dictionary containing modification transaction details and last transaction ID (`str`)

**Raises:**

- `FiveTwentyError` - API errors, trade not found, or modification failed

---

## put_trade_orders

```python
import asyncio
from fivetwenty import AsyncClient
from fivetwenty.endpoints.trades import TradeOrdersResponse


async def main() -> None:
    async with AsyncClient() as client:
        # trades.put_trade_orders(account_id: AccountID, trade_specifier: str,
        #                         **kwargs: Any) -> TradeOrdersResponse
        # kwargs: take_profit, stop_loss, trailing_stop_loss, guaranteed_stop_loss, idempotency_key
        # Returns: {"takeProfitOrderCancelTransaction": OrderCancelTransaction,
        #           "takeProfitOrderTransaction": TakeProfitOrderTransaction,
        #           "stopLossOrderTransaction": StopLossOrderTransaction, ...
        #           "relatedTransactionIDs": list[str], "lastTransactionID": str} (fields may be optional)

        result: TradeOrdersResponse = await client.trades.put_trade_orders(
            client.account_id,
            trade_specifier="12345",
            take_profit={"price": "1.1500"},
            stop_loss={"price": "1.1200"}
        )
        print(f"Last Transaction ID: {result['lastTransactionID']}")


if __name__ == "__main__":
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
| `**kwargs` | Any | ➖ | **Keyword arguments below** |
| `take_profit` | Any | ➖ | Take profit order specification |
| `stop_loss` | Any | ➖ | Stop loss order specification |
| `trailing_stop_loss` | Any | ➖ | Trailing stop loss order specification |
| `guaranteed_stop_loss` | Any | ➖ | Guaranteed stop loss order specification |
| `idempotency_key` | Any | ➖ | Idempotency key for safe retries |

**Returns:** Dictionary containing order update transaction details and last transaction ID (`str`)

**Raises:**

- `FiveTwentyError` - API errors, trade not found, or update failed