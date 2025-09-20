# Orders Endpoint

📖 **OANDA Reference**: [Order Endpoints](https://developer.oanda.com/rest-live-v20/order-ep/)

Order creation, modification, and management.

---

## Native OANDA Endpoints

These methods directly correspond to OANDA v20 REST API endpoints with minimal abstraction.

### list_pending
```python
orders.list_pending(account_id: AccountID) -> list[Order]
```
Get all pending orders for account.

🔗 **OANDA Endpoint**: `GET /v3/accounts/{accountID}/pendingOrders`

📖 **OANDA Documentation**: [Get Orders](https://developer.oanda.com/rest-live-v20/order-ep/#get-orders)

**Parameters:**

- `account_id` (AccountID) - Target account

**Returns:** List of pending orders

**Raises:**

- `FiveTwentyError` - API errors

---

### get
```python
orders.get(account_id: AccountID, order_id: OrderID) -> Order
```
Get specific order details.

🔗 **OANDA Endpoint**: `GET /v3/accounts/{accountID}/orders/{orderSpecifier}`

📖 **OANDA Documentation**: [Get Orders](https://developer.oanda.com/rest-live-v20/order-ep/#get-orders)

**Parameters:**

- `account_id` (AccountID) - Target account
- `order_id` (OrderID) - Order identifier

**Returns:** Order details

**Raises:**

- `FiveTwentyError` - API errors or invalid order ID

---

### cancel
```python
orders.cancel(account_id: AccountID, order_id: OrderID) -> OrderResponse
```
Cancel pending order.

🔗 **OANDA Endpoint**: `PUT /v3/accounts/{accountID}/orders/{orderSpecifier}/cancel`

📖 **OANDA Documentation**: [Cancel Order](https://developer.oanda.com/rest-live-v20/order-ep/#cancel-order)

**Parameters:**

- `account_id` (AccountID) - Target account
- `order_id` (OrderID) - Order to cancel

**Returns:** Cancellation response

**Raises:**

- `FiveTwentyError` - API errors, order not found, or order not cancellable

---

### list
```python
orders.list(account_id: AccountID, **kwargs) -> list[Order]
```
Get list of all orders for account.

🔗 **OANDA Endpoint**: `GET /v3/accounts/{accountID}/orders`

📖 **OANDA Documentation**: [Get Orders](https://developer.oanda.com/rest-live-v20/order-ep/#get-orders)

**Parameters:**

- `account_id` (AccountID) - Target account

**Optional Parameters:**

- `ids` (list[OrderID]) - List of specific order IDs to retrieve
- `state` (OrderStateFilter) - Filter by order state ("PENDING", "FILLED", "CANCELLED", "ALL")
- `instrument` (InstrumentName) - Filter by instrument
- `count` (int) - Maximum number of orders to return
- `before_id` (OrderID) - Maximum order ID to return

**Returns:** List of orders matching criteria

**Raises:**

- `FiveTwentyError` - API errors or invalid parameters

---

### replace
```python
orders.replace(account_id: AccountID, order_id: OrderID, order: OrderRequest, **kwargs) -> OrderResponse
```
Replace existing order by cancelling and creating new order.

🔗 **OANDA Endpoint**: `PUT /v3/accounts/{accountID}/orders/{orderSpecifier}`

📖 **OANDA Documentation**: [Replace Order](https://developer.oanda.com/rest-live-v20/order-ep/#replace-order)

**Parameters:**

- `account_id` (AccountID) - Target account
- `order_id` (OrderID) - Order to replace
- `order` (OrderRequest) - New order specification

**Optional Parameters:**

- `client_request_id` (str) - Client request ID for tracking

**Returns:** Order replacement response with cancellation and creation details

**Raises:**

- `FiveTwentyError` - API errors, order not found, or replacement failed

---

### modify_client_extensions
```python
orders.modify_client_extensions(account_id: AccountID, order_id: OrderID, **kwargs) -> OrderResponse
```
Modify client extensions for existing order.

🔗 **OANDA Endpoint**: `PUT /v3/accounts/{accountID}/orders/{orderSpecifier}/clientExtensions`

📖 **OANDA Documentation**: [Update Order Client Extensions](https://developer.oanda.com/rest-live-v20/order-ep/#update-order-client-extensions)

**Parameters:**

- `account_id` (AccountID) - Target account
- `order_id` (OrderID) - Order to modify

**Optional Parameters:**

- `client_extensions` (ClientExtensions) - New client extensions
- `trade_client_extensions` (ClientExtensions) - New trade client extensions

**Returns:** Order modification response

**Raises:**

- `FiveTwentyError` - API errors, order not found, or modification failed

---

## Convenience Methods

These methods provide simplified interfaces for common order operations, wrapping the native OANDA endpoints with type-specific convenience.

### post_market_order
```python
orders.post_market_order(account_id: AccountID, instrument: InstrumentName, units: int, **kwargs) -> OrderResponse
```
🔗 **OANDA Endpoint**: `POST /v3/accounts/{accountID}/orders`

📖 **OANDA Documentation**: [Create Order](https://developer.oanda.com/rest-live-v20/order-ep/#create-order) (Convenience wrapper for MarketOrderRequest)

Create market order for immediate execution.

**Parameters:**

- `account_id` (AccountID) - Trading account
- `instrument` (InstrumentName) - Trading pair (e.g., "EUR_USD")
- `units` (int) - Order size (positive = buy, negative = sell)

**Optional Parameters:**

- `time_in_force` (TimeInForce) - "FOK", "IOC"
- `price_bound` (Decimal) - Maximum slippage price
- `position_fill` (OrderPositionFill) - Position handling strategy
- `client_extensions` (ClientExtensions) - Custom metadata
- `take_profit_on_fill` (TakeProfitDetails) - Auto TP order
- `stop_loss_on_fill` (StopLossDetails) - Auto SL order
- `trailing_stop_loss_on_fill` (TrailingStopLossDetails) - Auto TSL order

**Returns:** Order response with fill details

**Raises:**

- `FiveTwentyError` - API errors, insufficient margin, or invalid parameters

---

### post_limit_order
```python
orders.post_limit_order(account_id: AccountID, instrument: InstrumentName, units: int, price: Decimal, **kwargs) -> OrderResponse
```
🔗 **OANDA Endpoint**: `POST /v3/accounts/{accountID}/orders`

📖 **OANDA Documentation**: [Create Order](https://developer.oanda.com/rest-live-v20/order-ep/#create-order) (Convenience wrapper for LimitOrderRequest)

Create limit order for execution at specific price or better.

**Parameters:**

- `account_id` (AccountID) - Trading account
- `instrument` (InstrumentName) - Trading pair
- `units` (int) - Order size
- `price` (Decimal) - Limit price

**Optional Parameters:**

- `time_in_force` (TimeInForce) - "GTC", "GTD", "GFD", "FOK", "IOC"
- `gtd_time` (DateTime) - Expiration for GTD orders
- `position_fill` (OrderPositionFill) - Position handling
- `trigger_condition` (OrderTriggerCondition) - Trigger logic
- `client_extensions` (ClientExtensions) - Custom metadata
- `take_profit_on_fill` (TakeProfitDetails) - Auto TP order
- `stop_loss_on_fill` (StopLossDetails) - Auto SL order
- `trailing_stop_loss_on_fill` (TrailingStopLossDetails) - Auto TSL order

**Returns:** Order response with creation details

**Raises:**

- `FiveTwentyError` - API errors or invalid parameters

---

### post_stop_order
```python
orders.post_stop_order(account_id: AccountID, instrument: InstrumentName, units: int, price: Decimal, **kwargs) -> OrderResponse
```
🔗 **OANDA Endpoint**: `POST /v3/accounts/{accountID}/orders`

📖 **OANDA Documentation**: [Create Order](https://developer.oanda.com/rest-live-v20/order-ep/#create-order) (Convenience wrapper for StopOrderRequest)

Create stop order triggered at specific price level.

**Parameters:**

- `account_id` (AccountID) - Trading account
- `instrument` (InstrumentName) - Trading pair
- `units` (int) - Order size
- `price` (Decimal) - Stop trigger price

**Optional Parameters:**

- `price_bound` (Decimal) - Maximum slippage after trigger
- `time_in_force` (TimeInForce) - Order duration
- `gtd_time` (DateTime) - Expiration time
- `position_fill` (OrderPositionFill) - Position handling
- `trigger_condition` (OrderTriggerCondition) - Trigger logic
- Other fill-based parameters

**Returns:** Order response with creation details

**Raises:**

- `FiveTwentyError` - API errors or invalid parameters
