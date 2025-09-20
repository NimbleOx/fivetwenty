# Trades Endpoint

📖 **OANDA Reference**: [Trade Endpoints](https://developer.oanda.com/rest-live-v20/trade-ep/)

Trade monitoring and management.

---

## list_open
```python
trades.list_open(account_id: AccountID) -> list[Trade]
```
🔗 **OANDA Endpoint**: `GET /v3/accounts/{accountID}/openTrades`

📖 **OANDA Documentation**: [Get Open Trades](https://developer.oanda.com/rest-live-v20/trade-ep/#get-open-trades)

Get all open trades for account.

**Parameters:**

- `account_id` (AccountID) - Target account

**Returns:** List of open trades

**Raises:**

- `FiveTwentyError` - API errors

---

## get
```python
trades.get(account_id: AccountID, trade_id: TradeID) -> Trade
```
🔗 **OANDA Endpoint**: `GET /v3/accounts/{accountID}/trades/{tradeSpecifier}`

📖 **OANDA Documentation**: [Get Trade Details](https://developer.oanda.com/rest-live-v20/trade-ep/#get-trade-details)

Get specific trade details.

**Parameters:**

- `account_id` (AccountID) - Target account
- `trade_id` (TradeID) - Trade identifier

**Returns:** Trade details

**Raises:**

- `FiveTwentyError` - API errors or invalid trade ID

---

## close
```python
trades.close(account_id: AccountID, trade_id: TradeID, units: int = None) -> OrderResponse
```
🔗 **OANDA Endpoint**: `PUT /v3/accounts/{accountID}/trades/{tradeSpecifier}/close`

📖 **OANDA Documentation**: [Close Trade](https://developer.oanda.com/rest-live-v20/trade-ep/#close-trade)

Close trade completely or partially.

**Parameters:**

- `account_id` (AccountID) - Target account
- `trade_id` (TradeID) - Trade to close
- `units` (int, optional) - Units to close (default: close all)

**Returns:** Close response with fill details

**Raises:**

- `FiveTwentyError` - API errors, trade not found, or insufficient units

---

## modify
```python
trades.modify(account_id: AccountID, trade_id: TradeID, **kwargs) -> OrderResponse
```
🔗 **OANDA Endpoint**: `PUT /v3/accounts/{accountID}/trades/{tradeSpecifier}/orders`

📖 **OANDA Documentation**: [Modify Trade Orders](https://developer.oanda.com/rest-live-v20/trade-ep/#modify-trade-orders)

Modify trade stop loss or take profit orders.

**Parameters:**

- `account_id` (AccountID) - Target account
- `trade_id` (TradeID) - Trade to modify

**Optional Parameters:**

- `take_profit` (TakeProfitDetails) - New take profit order
- `stop_loss` (StopLossDetails) - New stop loss order
- `trailing_stop_loss` (TrailingStopLossDetails) - New trailing stop order

**Returns:** Modification response

**Raises:**

- `FiveTwentyError` - API errors or invalid parameters

---

## list
```python
trades.list(account_id: AccountID, **kwargs) -> list[Trade]
```
🔗 **OANDA Endpoint**: `GET /v3/accounts/{accountID}/trades`

📖 **OANDA Documentation**: [Get All Trades](https://developer.oanda.com/rest-live-v20/trade-ep/#get-all-trades)

Get list of all trades for account.

**Parameters:**

- `account_id` (AccountID) - Target account

**Optional Parameters:**

- `ids` (list[TradeID]) - List of specific trade IDs to retrieve
- `state` (TradeStateFilter) - Filter by trade state ("OPEN", "CLOSED", "ALL")
- `instrument` (InstrumentName) - Filter by instrument
- `count` (int) - Maximum number of trades to return (max 500)
- `before_id` (TradeID) - Maximum trade ID to return

**Returns:** List of trades matching criteria

**Raises:**

- `FiveTwentyError` - API errors or invalid parameters

---

## modify_client_extensions
```python
trades.modify_client_extensions(account_id: AccountID, trade_id: TradeID, client_extensions: ClientExtensions) -> TradeResponse
```
🔗 **OANDA Endpoint**: `PUT /v3/accounts/{accountID}/trades/{tradeSpecifier}/clientExtensions`

📖 **OANDA Documentation**: [Modify Trade Client Extensions](https://developer.oanda.com/rest-live-v20/trade-ep/#modify-trade-client-extensions)

Update client extensions for existing trade.

**Parameters:**

- `account_id` (AccountID) - Target account
- `trade_id` (TradeID) - Trade to modify
- `client_extensions` (ClientExtensions) - New client extensions

**Returns:** Trade modification response

**Raises:**

- `FiveTwentyError` - API errors, trade not found, or modification failed