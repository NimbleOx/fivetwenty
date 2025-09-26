# Orders Endpoint

📖 **OANDA Reference**: [Order Endpoints](https://developer.oanda.com/rest-live-v20/order-ep/)

Order creation, modification, and management.

---

## post_order
```python
import asyncio
from fivetwenty import AsyncClient
from fivetwenty.models import MarketOrderRequest


async def main():
    # orders.create(account_id: AccountID, order_request: OrderRequest,
    #              timeout: float | None = None, client_request_id: str | None = None) -> OrderResponse

    # Example usage:
    async with AsyncClient() as client:
        order_response = await client.orders.post_order(
            account_id="123-456-789",
            order_request=MarketOrderRequest(
                instrument="EUR_USD",
                units=1000,
            ),
            client_request_id="my-order-123",
        )

asyncio.run(main())
```
🔗 **OANDA Endpoint**: `POST /v3/accounts/{accountID}/orders`

📖 **OANDA Documentation**: [Create Order](https://developer.oanda.com/rest-live-v20/order-ep/#create-order)

Create a new order using any order request type.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `account_id` | AccountID | ✅ | Target account identifier |
| `order_request` | MarketOrderRequest \| LimitOrderRequest \| StopOrderRequest \| TakeProfitOrderRequest \| StopLossOrderRequest \| MarketIfTouchedOrderRequest \| TrailingStopLossOrderRequest \| GuaranteedStopLossOrderRequest | ✅ | Order specification |
| `timeout` | float | ➖ | Request timeout override |
| `client_request_id` | str | ➖ | Client-provided request ID for debugging and correlation |

**Returns:** Order response with transaction details

**Raises:**

- `FiveTwentyError` - API errors or invalid order parameters

---

## post_market_order
```python
import asyncio
from decimal import Decimal
from fivetwenty import AsyncClient


async def main():
    # orders.post_market_order(account_id: AccountID, instrument: InstrumentName,
    #                         units: int | Decimal | str, take_profit: Decimal | None = None,
    #                         stop_loss: Decimal | None = None, timeout: float | None = None,
    #                         client_request_id: str | None = None) -> OrderResponse

    # Example usage:
    async with AsyncClient() as client:
        order = await client.orders.post_market_order(
            account_id="123-456-789",
            instrument="EUR_USD",
            units=1000,
            take_profit=Decimal("1.1500"),
            stop_loss=Decimal("1.1200"),
        )

asyncio.run(main())
```
🔗 **OANDA Endpoint**: `POST /v3/accounts/{accountID}/orders`

📖 **OANDA Documentation**: [Create Order](https://developer.oanda.com/rest-live-v20/order-ep/#create-order)

Create a market order (convenience method).

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `account_id` | AccountID | ✅ | Account to create order for |
| `instrument` | InstrumentName | ✅ | Instrument to trade |
| `units` | int \| Decimal \| str | ✅ | Number of units (positive = buy, negative = sell) |
| `take_profit` | Decimal | ➖ | Take profit price (creates takeProfitOnFill order) |
| `stop_loss` | Decimal | ➖ | Stop loss price (creates stopLossOnFill order) |
| `timeout` | float | ➖ | Request timeout override |
| `client_request_id` | str | ➖ | Client-provided request ID for debugging and correlation |

**Returns:** Order response with transaction details

**Raises:**

- `FiveTwentyError` - API errors, insufficient margin, or invalid parameters

---

## post_limit_order
```python
import asyncio
from decimal import Decimal
from fivetwenty import AsyncClient

# orders.post_limit_order(account_id: AccountID, instrument: InstrumentName,
#                        units: int | Decimal | str, price: Decimal,
#                        take_profit: Decimal | None = None, stop_loss: Decimal | None = None,
#                        timeout: float | None = None, client_request_id: str | None = None) -> OrderResponse


async def main():
    # Example usage:
    async with AsyncClient() as client:
        order = await client.orders.post_limit_order(
            account_id="123-456-789",
            instrument="EUR_USD",
            units=1000,
            price=Decimal("1.1350")
        )

asyncio.run(main())
```
🔗 **OANDA Endpoint**: `POST /v3/accounts/{accountID}/orders`

📖 **OANDA Documentation**: [Create Order](https://developer.oanda.com/rest-live-v20/order-ep/#create-order)

Create a limit order (convenience method).

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `account_id` | AccountID | ✅ | Account to create order for |
| `instrument` | InstrumentName | ✅ | Instrument to trade |
| `units` | int \| Decimal \| str | ✅ | Number of units (positive = buy, negative = sell) |
| `price` | Decimal | ✅ | Limit price |
| `time_in_force` | str | ➖ | Order time in force (GTC, GTD, GFD, FOK, IOC) |
| `take_profit` | Decimal | ➖ | Take profit price (creates takeProfitOnFill order) |
| `stop_loss` | Decimal | ➖ | Stop loss price (creates stopLossOnFill order) |
| `timeout` | float | ➖ | Request timeout override |
| `client_request_id` | str | ➖ | Client-provided request ID for debugging and correlation |

**Returns:** Order response with transaction details

**Raises:**

- `FiveTwentyError` - API errors or invalid parameters

---

## post_stop_order
```python
import asyncio
from decimal import Decimal
from fivetwenty import AsyncClient

# orders.post_stop_order(account_id: AccountID, instrument: InstrumentName,
#                       units: int | Decimal | str, price: Decimal,
#                       take_profit: Decimal | None = None, stop_loss: Decimal | None = None,
#                       timeout: float | None = None, client_request_id: str | None = None) -> OrderResponse


async def main():
    # Example usage:
    async with AsyncClient() as client:
        order = await client.orders.post_stop_order(
            account_id="123-456-789",
            instrument="EUR_USD",
            units=1000,
            price=Decimal("1.1200")
        )

asyncio.run(main())
```
🔗 **OANDA Endpoint**: `POST /v3/accounts/{accountID}/orders`

📖 **OANDA Documentation**: [Create Order](https://developer.oanda.com/rest-live-v20/order-ep/#create-order)

Create a stop order (convenience method).

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `account_id` | AccountID | ✅ | Account to create order for |
| `instrument` | InstrumentName | ✅ | Instrument to trade |
| `units` | int \| Decimal \| str | ✅ | Number of units (positive = buy, negative = sell) |
| `price` | Decimal | ✅ | Stop trigger price |
| `price_bound` | Decimal | ➖ | Maximum slippage price after trigger |
| `time_in_force` | str | ➖ | Order time in force (GTC, GTD, GFD, FOK, IOC) |
| `take_profit` | Decimal | ➖ | Take profit price (creates takeProfitOnFill order) |
| `stop_loss` | Decimal | ➖ | Stop loss price (creates stopLossOnFill order) |
| `timeout` | float | ➖ | Request timeout override |
| `client_request_id` | str | ➖ | Client-provided request ID for debugging and correlation |

**Returns:** Order response with transaction details

**Raises:**

- `FiveTwentyError` - API errors or invalid parameters

---

## post_market_if_touched_order
```python
import asyncio
from decimal import Decimal
from fivetwenty import AsyncClient

# orders.post_market_if_touched_order(account_id: AccountID, instrument: InstrumentName,
#                                    units: int | Decimal | str, price: Decimal,
#                                    take_profit: Decimal | None = None, stop_loss: Decimal | None = None,
#                                    timeout: float | None = None, client_request_id: str | None = None) -> OrderResponse


async def main():
    # Example usage:
    async with AsyncClient() as client:
        order = await client.orders.post_market_if_touched_order(
            account_id="123-456-789",
            instrument="EUR_USD",
            units=1000,
            price=Decimal("1.1400")
        )

asyncio.run(main())
```
🔗 **OANDA Endpoint**: `POST /v3/accounts/{accountID}/orders`

📖 **OANDA Documentation**: [Create Order](https://developer.oanda.com/rest-live-v20/order-ep/#create-order)

Create a market-if-touched order (convenience method).

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `account_id` | AccountID | ✅ | Account to create order for |
| `instrument` | InstrumentName | ✅ | Instrument to trade |
| `units` | int \| Decimal \| str | ✅ | Number of units (positive = buy, negative = sell) |
| `price` | Decimal | ✅ | Trigger price |
| `price_bound` | Decimal | ➖ | Maximum slippage price after trigger |
| `time_in_force` | str | ➖ | Order time in force (GTC, GTD, GFD, FOK, IOC) |
| `take_profit` | Decimal | ➖ | Take profit price (creates takeProfitOnFill order) |
| `stop_loss` | Decimal | ➖ | Stop loss price (creates stopLossOnFill order) |
| `timeout` | float | ➖ | Request timeout override |
| `client_request_id` | str | ➖ | Client-provided request ID for debugging and correlation |

**Returns:** Order response with transaction details

**Raises:**

- `FiveTwentyError` - API errors or invalid parameters

---

## get_orders
```python
import asyncio
from fivetwenty import AsyncClient

# orders.get_orders(account_id: AccountID, ids: list[str] | None = None,
#            state: str = "PENDING", instrument: str | None = None,
#            count: int | None = None, before_id: str | None = None) -> dict[str, Any]


async def main():
    # Example usage:
    async with AsyncClient() as client:
        orders = await client.orders.get_orders(
            account_id="123-456-789",
            state="PENDING",
            count=50
        )

asyncio.run(main())
```
🔗 **OANDA Endpoint**: `GET /v3/accounts/{accountID}/orders`

📖 **OANDA Documentation**: [Get Orders](https://developer.oanda.com/rest-live-v20/order-ep/#get-orders)

Get list of orders for account.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `account_id` | AccountID | ✅ | Target account identifier |
| `ids` | list[str] | ➖ | List of specific order IDs to retrieve |
| `state` | str | ➖ | Filter by order state (default: "PENDING") |
| `instrument` | str | ➖ | Filter by instrument |
| `count` | int | ➖ | Maximum number of orders to return |
| `before_id` | str | ➖ | Maximum order ID to return |

**Returns:** Dictionary containing orders list and lastTransactionID

**Raises:**

- `FiveTwentyError` - API errors or invalid parameters

---

## get_order
```python
import asyncio
from fivetwenty import AsyncClient

# orders.get_order(account_id: AccountID, order_specifier: str) -> dict[str, Any]


async def main():
    # Example usage:
    async with AsyncClient() as client:
        order = await client.orders.get_order(
            account_id="123-456-789",
            order_specifier="12345"
        )

asyncio.run(main())
```
🔗 **OANDA Endpoint**: `GET /v3/accounts/{accountID}/orders/{orderSpecifier}`

📖 **OANDA Documentation**: [Get Order](https://developer.oanda.com/rest-live-v20/order-ep/#get-order)

Get order details.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `account_id` | AccountID | ✅ | Target account identifier |
| `order_specifier` | str | ✅ | Order identifier or specifier |

**Returns:** Dictionary containing order details and lastTransactionID

**Raises:**

- `FiveTwentyError` - API errors or order not found

---

## cancel_order
```python
import asyncio
from fivetwenty import AsyncClient

# orders.cancel_order(account_id: AccountID, order_specifier: str,
#             timeout: float | None = None, client_request_id: str | None = None) -> dict[str, Any]


async def main():
    # Example usage:
    async with AsyncClient() as client:
        result = await client.orders.cancel_order(
            account_id="123-456-789",
            order_specifier="12345"
        )

asyncio.run(main())
```
🔗 **OANDA Endpoint**: `PUT /v3/accounts/{accountID}/orders/{orderSpecifier}/cancel`

📖 **OANDA Documentation**: [Cancel Order](https://developer.oanda.com/rest-live-v20/order-ep/#cancel-order)

Cancel pending order.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `account_id` | AccountID | ✅ | Target account identifier |
| `order_specifier` | str | ✅ | Order identifier to cancel |
| `timeout` | float | ➖ | Request timeout override |
| `client_request_id` | str | ➖ | Client-provided request ID for debugging and correlation |

**Returns:** Dictionary containing cancellation transaction details

**Raises:**

- `FiveTwentyError` - API errors, order not found, or order not cancellable

---

## get_pending_orders
```python
import asyncio
from fivetwenty import AsyncClient

# orders.get_pending_orders(account_id: AccountID) -> dict[str, Any]


async def main():
    # Example usage:
    async with AsyncClient() as client:
        open_orders = await client.orders.get_pending_orders(account_id="123-456-789")

asyncio.run(main())
```
🔗 **OANDA Endpoint**: `GET /v3/accounts/{accountID}/pendingOrders`

📖 **OANDA Documentation**: [Get Pending Orders](https://developer.oanda.com/rest-live-v20/order-ep/#get-pending-orders)

List all pending orders for an account.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `account_id` | AccountID | ✅ | Target account identifier |

**Returns:** Dictionary containing pending orders list and lastTransactionID

**Raises:**

- `FiveTwentyError` - API errors

---

## put_order
```python
import asyncio
from fivetwenty import AsyncClient

# orders.put_order(account_id: AccountID, order_specifier: str,
#              order_request: dict[str, Any], client_request_id: str | None = None) -> dict[str, Any]


async def main():
    # Example usage:
    async with AsyncClient() as client:
        result = await client.orders.put_order(
            account_id="123-456-789",
            order_specifier="12345",
            order_request={"price": "1.1400"}
        )

asyncio.run(main())
```
🔗 **OANDA Endpoint**: `PUT /v3/accounts/{accountID}/orders/{orderSpecifier}`

📖 **OANDA Documentation**: [Replace Order](https://developer.oanda.com/rest-live-v20/order-ep/#replace-order)

Replace existing order by cancelling and creating new order.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `account_id` | AccountID | ✅ | Target account identifier |
| `order_specifier` | str | ✅ | Order identifier to replace |
| `order_request` | dict[str, Any] | ✅ | New order specification |
| `client_request_id` | str | ➖ | Client-provided request ID for debugging and correlation |

**Returns:** Dictionary containing replacement transaction details

**Raises:**

- `FiveTwentyError` - API errors, order not found, or replacement failed

---

## put_order_client_extensions
```python
import asyncio
from fivetwenty import AsyncClient

# orders.put_order_client_extensions(account_id: AccountID, order_specifier: str,
#                                client_extensions: dict[str, Any] | None = None,
#                                trade_client_extensions: dict[str, Any] | None = None) -> dict[str, Any]


async def main():
    # Example usage:
    async with AsyncClient() as client:
        result = await client.orders.put_order_client_extensions(
            account_id="123-456-789",
            order_specifier="12345",
            client_extensions={"comment": "Updated order"}
        )

asyncio.run(main())
```
🔗 **OANDA Endpoint**: `PUT /v3/accounts/{accountID}/orders/{orderSpecifier}/clientExtensions`

📖 **OANDA Documentation**: [Update Order Client Extensions](https://developer.oanda.com/rest-live-v20/order-ep/#update-order-client-extensions)

Modify client extensions for existing order.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `account_id` | AccountID | ✅ | Target account identifier |
| `order_specifier` | str | ✅ | Order identifier to modify |
| `client_extensions` | dict[str, Any] | ➖ | New order client extensions |
| `trade_client_extensions` | dict[str, Any] | ➖ | New trade client extensions |

**Returns:** Dictionary containing modification transaction details

**Raises:**

- `FiveTwentyError` - API errors, order not found, or modification failed