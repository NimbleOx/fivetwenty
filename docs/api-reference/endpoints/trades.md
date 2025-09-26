# Trades Endpoint

📖 **OANDA Reference**: [Trade Endpoints](https://developer.oanda.com/rest-live-v20/trade-ep/)

Trade monitoring and management.

---

## get_trades
```python
import asyncio


async def main():
    # trades.get_trades(account_id: AccountID, ids: list[TradeID] | None = None,
    #            state: TradeStateFilter = TradeStateFilter.OPEN,
    #            instrument: InstrumentName | None = None, count: int = 50,
    #            before_id: TradeID | None = None) -> dict[str, Any]

    # Example usage:
    trades = await client.trades.get_trades(
        account_id="123-456-789",
        state=TradeStateFilter.OPEN,
        count=20,
    )

asyncio.run(main())
```
🔗 **OANDA Endpoint**: `GET /v3/accounts/{accountID}/trades`

📖 **OANDA Documentation**: [Get Trades](https://developer.oanda.com/rest-live-v20/trade-ep/#get-trades)

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

**Returns:** Dictionary containing list of trades and last transaction ID

**Raises:**

- `FiveTwentyError` - API errors

---

## get_open_trades
```python
# trades.get_open_trades(account_id: AccountID) -> dict[str, Any]

# Example usage:
open_trades = await client.trades.get_open_trades(account_id="123-456-789")
```
🔗 **OANDA Endpoint**: `GET /v3/accounts/{accountID}/openTrades`

📖 **OANDA Documentation**: [Get Open Trades](https://developer.oanda.com/rest-live-v20/trade-ep/#get-open-trades)

Get all open trades for account.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `account_id` | AccountID | ✅ | Target account identifier |

**Returns:** Dictionary containing list of open trades and last transaction ID

**Raises:**

- `FiveTwentyError` - API errors

---

## get_trade
```python
# trades.get_trade(account_id: AccountID, trade_specifier: str) -> dict[str, Any]

# Example usage:
trade = await client.trades.get_trade(
    account_id="123-456-789",
    trade_specifier="12345"
)
```
🔗 **OANDA Endpoint**: `GET /v3/accounts/{accountID}/trades/{tradeSpecifier}`

📖 **OANDA Documentation**: [Get Trade Details](https://developer.oanda.com/rest-live-v20/trade-ep/#get-trade-details)

Get specific trade details.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `account_id` | AccountID | ✅ | Target account identifier |
| `trade_specifier` | str | ✅ | Trade ID or @clientID |

**Returns:** Dictionary containing trade details and last transaction ID

**Raises:**

- `FiveTwentyError` - API errors or invalid trade ID

---

## close_trade
```python
# trades.close_trade(account_id: AccountID, trade_specifier: str,
#             units: str | None = None, idempotency_key: str | None = None) -> dict[str, Any]

# Example usage:
result = await client.trades.close_trade(
    account_id="123-456-789",
    trade_specifier="12345",
    units="1000"
)
```
🔗 **OANDA Endpoint**: `PUT /v3/accounts/{accountID}/trades/{tradeSpecifier}/close`

📖 **OANDA Documentation**: [Close Trade](https://developer.oanda.com/rest-live-v20/trade-ep/#close-trade)

Close a trade (fully or partially).

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `account_id` | AccountID | ✅ | Account identifier |
| `trade_specifier` | str | ✅ | Trade ID or @clientID |
| `units` | str | ➖ | Number of units to close (default: ALL for full closure) |
| `idempotency_key` | str | ➖ | Idempotency key for duplicate prevention |

**Returns:** Dictionary containing closure transaction details

**Raises:**

- `FiveTwentyError` - API errors

---

## put_trade_client_extensions
```python
import asyncio


async def main():
    # trades.put_trade_client_extensions(account_id: AccountID, trade_specifier: str,
    #                                client_extensions: dict[str, Any] | None = None,
    #                                idempotency_key: str | None = None) -> dict[str, Any]

    # Example usage:
    result = await client.trades.put_trade_client_extensions(
        account_id="123-456-789",
        trade_specifier="12345",
        client_extensions={"comment": "Updated comment"},
    )

asyncio.run(main())
```
🔗 **OANDA Endpoint**: `PUT /v3/accounts/{accountID}/trades/{tradeSpecifier}/clientExtensions`

📖 **OANDA Documentation**: [Update Trade Client Extensions](https://developer.oanda.com/rest-live-v20/trade-ep/#update-trade-client-extensions)

Modify client extensions for existing trade.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `account_id` | AccountID | ✅ | Target account identifier |
| `trade_specifier` | str | ✅ | Trade identifier to modify |
| `client_extensions` | dict[str, Any] | ➖ | New trade client extensions |
| `idempotency_key` | str | ➖ | Idempotency key for safe retries |

**Returns:** Dictionary containing modification transaction details

**Raises:**

- `FiveTwentyError` - API errors, trade not found, or modification failed

---

## put_trade_orders
```python
# trades.put_trade_orders(account_id: AccountID, trade_specifier: str,
#              take_profit: dict[str, Any] | None = None,
#              stop_loss: dict[str, Any] | None = None,
#              trailing_stop_loss: dict[str, Any] | None = None,
#              guaranteed_stop_loss: dict[str, Any] | None = None,
#              idempotency_key: str | None = None) -> dict[str, Any]

# Example usage:
result = await client.trades.put_trade_orders(
    account_id="123-456-789",
    trade_specifier="12345",
    take_profit={"price": "1.1500"},
    stop_loss={"price": "1.1200"}
)
```
🔗 **OANDA Endpoint**: `PUT /v3/accounts/{accountID}/trades/{tradeSpecifier}/orders`

📖 **OANDA Documentation**: [Update Trade Dependent Orders](https://developer.oanda.com/rest-live-v20/trade-ep/#update-trade-dependent-orders)

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

**Returns:** Dictionary containing order update transaction details

**Raises:**

- `FiveTwentyError` - API errors, trade not found, or update failed