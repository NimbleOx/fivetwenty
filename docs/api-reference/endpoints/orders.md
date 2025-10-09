# Orders Endpoint

**OANDA Reference**: [Order Endpoints](https://developer.oanda.com/rest-live-v20/order-ep/)

Order creation, modification, and management.

---

## post_order

```python
import asyncio
from fivetwenty import AsyncClient
from fivetwenty.models import MarketOrderRequest
from fivetwenty.endpoints.orders import OrderResponse


async def main():
    async with AsyncClient() as client:
        order_response: OrderResponse = await client.orders.post_order(
            account_id=client.account_id,
            order_request=MarketOrderRequest(
                instrument="EUR_USD",
                units=1000,
            ),
            client_request_id="my-order-123",
        )
        print(f"Last Transaction ID: {order_response['lastTransactionID']}")

asyncio.run(main())
```
🔗 **OANDA Endpoint**: `POST /v3/accounts/{accountID}/orders`

**OANDA Documentation**: [Create Order](https://developer.oanda.com/rest-live-v20/order-ep/#create-order)

Create a new order using any order request type.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `account_id` | AccountID | ✅ | Target account identifier |
| `order_request` | MarketOrderRequest \| LimitOrderRequest \| StopOrderRequest \| TakeProfitOrderRequest \| StopLossOrderRequest \| MarketIfTouchedOrderRequest \| TrailingStopLossOrderRequest \| GuaranteedStopLossOrderRequest | ✅ | Order specification |
| `*` | | | **Keyword-only parameters below** |
| `timeout` | float \| None | ➖ | Request timeout override |
| `client_request_id` | str \| None | ➖ | Client-provided request ID for debugging and correlation |

**Returns:** `OrderResponse` - Order response with transaction details

**Raises:**

- `FiveTwentyError` - API errors or invalid order parameters

---

## post_market_order

```python
import asyncio
from decimal import Decimal
from fivetwenty import AsyncClient
from fivetwenty.endpoints.orders import OrderResponse


async def main():
    async with AsyncClient() as client:
        order: OrderResponse = await client.orders.post_market_order(
            account_id=client.account_id,
            instrument="EUR_USD",
            units=1000,
            take_profit=Decimal("1.1500"),
            stop_loss=Decimal("1.1200"),
        )
        print(f"Last Transaction ID: {order['lastTransactionID']}")

asyncio.run(main())
```
🔗 **OANDA Endpoint**: `POST /v3/accounts/{accountID}/orders`

**OANDA Documentation**: [Create Order](https://developer.oanda.com/rest-live-v20/order-ep/#create-order)

Create a market order (convenience method).

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `account_id` | AccountID | ✅ | Account to create order for |
| `instrument` | InstrumentName | ✅ | Instrument to trade |
| `units` | int \| Decimal \| str | ✅ | Number of units (positive = buy, negative = sell) |
| `*` | | | **Keyword-only parameters below** |
| `take_profit` | Decimal \| None | ➖ | Take profit price (creates takeProfitOnFill order) |
| `stop_loss` | Decimal \| None | ➖ | Stop loss price (creates stopLossOnFill order) |
| `timeout` | float \| None | ➖ | Request timeout override |
| `client_request_id` | str \| None | ➖ | Client-provided request ID for debugging and correlation |

**Returns:** `OrderResponse` - Order response with transaction details

**Raises:**

- `FiveTwentyError` - API errors, insufficient margin, or invalid parameters

---

## post_limit_order

```python
import asyncio
from decimal import Decimal
from fivetwenty import AsyncClient
from fivetwenty.endpoints.orders import OrderResponse


async def main():
    async with AsyncClient() as client:
        order: OrderResponse = await client.orders.post_limit_order(
            account_id=client.account_id,
            instrument="EUR_USD",
            units=1000,
            price=Decimal("1.1350"),
        )
        print(f"Last Transaction ID: {order['lastTransactionID']}")

asyncio.run(main())
```
🔗 **OANDA Endpoint**: `POST /v3/accounts/{accountID}/orders`

**OANDA Documentation**: [Create Order](https://developer.oanda.com/rest-live-v20/order-ep/#create-order)

Create a limit order (convenience method).

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `account_id` | AccountID | ✅ | Account to create order for |
| `instrument` | InstrumentName | ✅ | Instrument to trade |
| `units` | int \| Decimal \| str | ✅ | Number of units (positive = buy, negative = sell) |
| `price` | Decimal | ✅ | Limit price |
| `*` | | | **Keyword-only parameters below** |
| `time_in_force` | str | ➖ | Order time in force (GTC, GTD, GFD, FOK, IOC) - default: "GTC" |
| `take_profit` | Decimal \| None | ➖ | Take profit price (creates takeProfitOnFill order) |
| `stop_loss` | Decimal \| None | ➖ | Stop loss price (creates stopLossOnFill order) |
| `timeout` | float \| None | ➖ | Request timeout override |
| `client_request_id` | str \| None | ➖ | Client-provided request ID for debugging and correlation |

**Returns:** `OrderResponse` - Order response with transaction details

**Raises:**

- `FiveTwentyError` - API errors or invalid parameters

---

## post_stop_order

```python
import asyncio
from decimal import Decimal
from fivetwenty import AsyncClient
from fivetwenty.endpoints.orders import OrderResponse


async def main():
    async with AsyncClient() as client:
        order: OrderResponse = await client.orders.post_stop_order(
            account_id=client.account_id,
            instrument="EUR_USD",
            units=1000,
            price=Decimal("1.1200"),
        )
        print(f"Last Transaction ID: {order['lastTransactionID']}")

asyncio.run(main())
```
🔗 **OANDA Endpoint**: `POST /v3/accounts/{accountID}/orders`

**OANDA Documentation**: [Create Order](https://developer.oanda.com/rest-live-v20/order-ep/#create-order)

Create a stop order (convenience method).

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `account_id` | AccountID | ✅ | Account to create order for |
| `instrument` | InstrumentName | ✅ | Instrument to trade |
| `units` | int \| Decimal \| str | ✅ | Number of units (positive = buy, negative = sell) |
| `price` | Decimal | ✅ | Stop trigger price |
| `*` | | | **Keyword-only parameters below** |
| `price_bound` | Decimal \| None | ➖ | Maximum slippage price after trigger |
| `time_in_force` | str | ➖ | Order time in force (GTC, GTD, GFD, FOK, IOC) - default: "GTC" |
| `take_profit` | Decimal \| None | ➖ | Take profit price (creates takeProfitOnFill order) |
| `stop_loss` | Decimal \| None | ➖ | Stop loss price (creates stopLossOnFill order) |
| `timeout` | float \| None | ➖ | Request timeout override |
| `client_request_id` | str \| None | ➖ | Client-provided request ID for debugging and correlation |

**Returns:** `OrderResponse` - Order response with transaction details

**Raises:**

- `FiveTwentyError` - API errors or invalid parameters

---

## post_market_if_touched_order

```python
import asyncio
from decimal import Decimal
from fivetwenty import AsyncClient
from fivetwenty.endpoints.orders import OrderResponse


async def main():
    async with AsyncClient() as client:
        order: OrderResponse = await client.orders.post_market_if_touched_order(
            account_id=client.account_id,
            instrument="EUR_USD",
            units=1000,
            price=Decimal("1.1400"),
        )
        print(f"Last Transaction ID: {order['lastTransactionID']}")

asyncio.run(main())
```
🔗 **OANDA Endpoint**: `POST /v3/accounts/{accountID}/orders`

**OANDA Documentation**: [Create Order](https://developer.oanda.com/rest-live-v20/order-ep/#create-order)

Create a market-if-touched order (convenience method).

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `account_id` | AccountID | ✅ | Account to create order for |
| `instrument` | InstrumentName | ✅ | Instrument to trade |
| `units` | int \| Decimal \| str | ✅ | Number of units (positive = buy, negative = sell) |
| `price` | Decimal | ✅ | Trigger price |
| `*` | | | **Keyword-only parameters below** |
| `price_bound` | Decimal \| None | ➖ | Maximum slippage price after trigger |
| `time_in_force` | str | ➖ | Order time in force (GTC, GTD, GFD, FOK, IOC) - default: "GTC" |
| `take_profit` | Decimal \| None | ➖ | Take profit price (creates takeProfitOnFill order) |
| `stop_loss` | Decimal \| None | ➖ | Stop loss price (creates stopLossOnFill order) |
| `timeout` | float \| None | ➖ | Request timeout override |
| `client_request_id` | str \| None | ➖ | Client-provided request ID for debugging and correlation |

**Returns:** `OrderResponse` - Order response with transaction details

**Raises:**

- `FiveTwentyError` - API errors or invalid parameters

---

## get_orders

```python
import asyncio
from fivetwenty import AsyncClient


async def main() -> None:
    async with AsyncClient() as client:
        orders = await client.orders.get_orders(
            account_id=client.account_id,
            state="PENDING",
            count=50,
        )
        print(f"Found {len(orders)} orders")

asyncio.run(main())
```
🔗 **OANDA Endpoint**: `GET /v3/accounts/{accountID}/orders`

**OANDA Documentation**: [Get Orders](https://developer.oanda.com/rest-live-v20/order-ep/#get-orders)

Get list of orders for account.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `account_id` | AccountID | ✅ | Target account identifier |
| `*` | | | **Keyword-only parameters below** |
| `ids` | list[str] \| None | ➖ | List of specific order IDs to retrieve |
| `state` | str | ➖ | Filter by order state - default: "PENDING" |
| `instrument` | str \| None | ➖ | Filter by instrument |
| `count` | int | ➖ | Maximum number of orders to return - default: 50 |
| `before_id` | str \| None | ➖ | Maximum order ID to return |

**Returns:** `list[Order]` - List of Order models

**Raises:**

- `FiveTwentyError` - API errors or invalid parameters

---

## get_order

```python
import asyncio
from fivetwenty import AsyncClient
from fivetwenty.endpoints.orders import GetOrderResponse


async def main() -> None:
    async with AsyncClient() as client:
        result: GetOrderResponse = await client.orders.get_order(
            account_id=client.account_id,
            order_specifier="12345",
        )
        order = result["order"]
        print(f"Order type: {order.type}")
        print(f"Last Transaction ID: {result['lastTransactionID']}")

asyncio.run(main())
```
🔗 **OANDA Endpoint**: `GET /v3/accounts/{accountID}/orders/{orderSpecifier}`

**OANDA Documentation**: [Get Order](https://developer.oanda.com/rest-live-v20/order-ep/#get-order)

Get order details.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `account_id` | AccountID | ✅ | Target account identifier |
| `order_specifier` | str | ✅ | Order identifier or specifier |

**Returns:** `GetOrderResponse` - Dictionary containing order (`Order`) and lastTransactionID (`str`)

**Raises:**

- `FiveTwentyError` - API errors or order not found

---

## cancel_order

```python
import asyncio
from fivetwenty import AsyncClient
from fivetwenty.endpoints.orders import CancelOrderResponse


async def main() -> None:
    async with AsyncClient() as client:
        result: CancelOrderResponse = await client.orders.cancel_order(
            account_id=client.account_id,
            order_specifier="12345",
        )
        print(f"Last Transaction ID: {result['lastTransactionID']}")

asyncio.run(main())
```
🔗 **OANDA Endpoint**: `PUT /v3/accounts/{accountID}/orders/{orderSpecifier}/cancel`

**OANDA Documentation**: [Cancel Order](https://developer.oanda.com/rest-live-v20/order-ep/#cancel-order)

Cancel pending order.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `account_id` | AccountID | ✅ | Target account identifier |
| `order_specifier` | str | ✅ | Order identifier to cancel |
| `*` | | | **Keyword-only parameters below** |
| `timeout` | float \| None | ➖ | Request timeout override |
| `client_request_id` | str \| None | ➖ | Client-provided request ID for debugging and correlation |

**Returns:** `CancelOrderResponse` - Dictionary containing orderCancelTransaction, relatedTransactionIDs, and lastTransactionID

**Raises:**

- `FiveTwentyError` - API errors, order not found, or order not cancellable

---

## get_pending_orders

```python
import asyncio
from fivetwenty import AsyncClient
from fivetwenty.endpoints.orders import PendingOrdersResponse


async def main() -> None:
    async with AsyncClient() as client:
        result: PendingOrdersResponse = await client.orders.get_pending_orders(
            account_id=client.account_id
        )
        pending_orders = result["orders"]
        print(f"Found {len(pending_orders)} pending orders")
        print(f"Last Transaction ID: {result['lastTransactionID']}")

asyncio.run(main())
```
🔗 **OANDA Endpoint**: `GET /v3/accounts/{accountID}/pendingOrders`

**OANDA Documentation**: [Get Pending Orders](https://developer.oanda.com/rest-live-v20/order-ep/#get-pending-orders)

List all pending orders for an account.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `account_id` | AccountID | ✅ | Target account identifier |

**Returns:** `PendingOrdersResponse` - Dictionary containing orders (`list[Order]`) and lastTransactionID (`str`)

**Raises:**

- `FiveTwentyError` - API errors

---

## put_order

```python
import asyncio
from fivetwenty import AsyncClient
from fivetwenty.endpoints.orders import ReplaceOrderResponse


async def main() -> None:
    async with AsyncClient() as client:
        result: ReplaceOrderResponse = await client.orders.put_order(
            account_id=client.account_id,
            order_specifier="12345",
            order_request={"price": "1.1400"},
        )
        print(f"Last Transaction ID: {result['lastTransactionID']}")

asyncio.run(main())
```
🔗 **OANDA Endpoint**: `PUT /v3/accounts/{accountID}/orders/{orderSpecifier}`

**OANDA Documentation**: [Replace Order](https://developer.oanda.com/rest-live-v20/order-ep/#replace-order)

Replace existing order by cancelling and creating new order.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `account_id` | AccountID | ✅ | Target account identifier |
| `order_specifier` | str | ✅ | Order identifier to replace |
| `order_request` | dict[str, Any] | ✅ | New order specification |
| `*` | | | **Keyword-only parameters below** |
| `client_request_id` | str \| None | ➖ | Client-provided request ID for debugging and correlation |

**Returns:** `ReplaceOrderResponse` - Dictionary containing orderCancelTransaction, orderCreateTransaction, orderFillTransaction, relatedTransactionIDs, and lastTransactionID

**Raises:**

- `FiveTwentyError` - API errors, order not found, or replacement failed

---

## put_order_client_extensions

```python
import asyncio
from fivetwenty import AsyncClient
from fivetwenty.endpoints.orders import OrderClientExtensionsResponse


async def main() -> None:
    async with AsyncClient() as client:
        result: OrderClientExtensionsResponse = await client.orders.put_order_client_extensions(
            account_id=client.account_id,
            order_specifier="12345",
            client_extensions={"comment": "Updated order"},
        )
        print(f"Last Transaction ID: {result['lastTransactionID']}")

asyncio.run(main())
```
🔗 **OANDA Endpoint**: `PUT /v3/accounts/{accountID}/orders/{orderSpecifier}/clientExtensions`

**OANDA Documentation**: [Update Order Client Extensions](https://developer.oanda.com/rest-live-v20/order-ep/#update-order-client-extensions)

Modify client extensions for existing order.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `account_id` | AccountID | ✅ | Target account identifier |
| `order_specifier` | str | ✅ | Order identifier to modify |
| `*` | | | **Keyword-only parameters below** |
| `client_extensions` | dict[str, Any] \| None | ➖ | New order client extensions |
| `trade_client_extensions` | dict[str, Any] \| None | ➖ | New trade client extensions |

**Returns:** `OrderClientExtensionsResponse` - Dictionary containing orderClientExtensionsModifyTransaction, relatedTransactionIDs, and lastTransactionID

**Raises:**

- `FiveTwentyError` - API errors, order not found, or modification failed