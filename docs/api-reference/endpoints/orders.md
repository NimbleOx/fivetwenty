# Orders Endpoint

**OANDA Reference**: [Order Endpoints](https://developer.oanda.com/rest-live-v20/order-ep/)

Order creation, modification, and management.

The examples below illustrate calls and response access. Helpers run only when
called. Examples that create, update, cancel or close resources change account
state; use a dedicated practice account and inspect each response. Local validation
and HTTPX transport exceptions can occur in addition to the API errors listed.

---

## post_order

Create a new order using any order request type.

**OANDA Endpoint**: `POST /v3/accounts/{accountID}/orders`

<!-- code-block: orders__post_order -->
```python
import asyncio
from decimal import Decimal

from dotenv import load_dotenv

from fivetwenty import AsyncClient
from fivetwenty.endpoints.orders import OrderResponse
from fivetwenty.models import InstrumentName, MarketOrderRequest

load_dotenv()


async def main() -> None:
    async with AsyncClient() as client:
        # Create a market order using the generic post_order method
        order_response: OrderResponse = await client.orders.post_order(
            account_id=client.account_id,
            order_request=MarketOrderRequest(
                instrument=InstrumentName.EUR_USD,
                units=Decimal(1000),
            ),
            client_request_id="my-order-123",
        )
        print(f"Last Transaction ID: {order_response['lastTransactionID']}")


if __name__ == "__main__":
    asyncio.run(main())
```

🔗 **OANDA Documentation**: [Create Order](https://developer.oanda.com/rest-live-v20/order-ep/#create-order)

🔗 **Source**: [orders.post_order](https://github.com/NimbleOx/fivetwenty/blob/main/fivetwenty/endpoints/orders.py#L140)

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `account_id` | AccountID | ✅ | Target account identifier |
| `order_request` | OrderRequest \| dict[str, Any] | ✅ | Order specification |
| `*` | | | **Keyword-only parameters below** |
| `timeout` | float \| None | ➖ | Request timeout override |
| `client_request_id` | str \| None | ➖ | Client-provided request ID for debugging and correlation |

**Returns:** `OrderResponse` TypedDict containing:

- `lastTransactionID`: Transaction ID string
- `orderCreateTransaction`: Transaction details for the created order
- `orderFillTransaction`: Transaction details if order was filled (optional)
- `relatedTransactionIDs`: List of related transaction IDs

**Raises:**

`FiveTwentyError` - API errors:

  - 401/403: Authentication failed (check `e.is_authentication_error`)
  - 404: Account not found (check `e.is_not_found`)
  - 429: Rate limit exceeded (check `e.is_rate_limited`, use `e.retry_after`)
  - 400: Invalid order parameters (inspect `e.code` and `e.details`)

- `ValueError` - If order_request is invalid or missing required fields

---

## post_market_order

Create a market order (convenience method for immediate execution at current market price).

**OANDA Endpoint**: `POST /v3/accounts/{accountID}/orders`

<!-- code-block: orders__post_market_order -->
```python
import asyncio
from decimal import Decimal

from dotenv import load_dotenv

from fivetwenty import AsyncClient
from fivetwenty.endpoints.orders import OrderResponse
from fivetwenty.models import InstrumentName

load_dotenv()


async def main() -> None:
    async with AsyncClient() as client:
        # Create a market order with take profit and stop loss
        order: OrderResponse = await client.orders.post_market_order(
            account_id=client.account_id,
            instrument=InstrumentName.EUR_USD,
            units=1000,
            take_profit=Decimal("1.1500"),
            stop_loss=Decimal("1.1200"),
        )
        print(f"Last Transaction ID: {order['lastTransactionID']}")


if __name__ == "__main__":
    asyncio.run(main())
```

🔗 **OANDA Documentation**: [Create Order](https://developer.oanda.com/rest-live-v20/order-ep/#create-order)

🔗 **Source**: [orders.post_market_order](https://github.com/NimbleOx/fivetwenty/blob/main/fivetwenty/endpoints/orders.py#L221)

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

**Returns:** `OrderResponse` TypedDict containing:

- `lastTransactionID`: Transaction ID string
- `orderCreateTransaction`: Transaction details for the created order
- `orderFillTransaction`: Transaction details if order was filled (optional)
- `relatedTransactionIDs`: List of related transaction IDs

**Raises:**

`FiveTwentyError` - API errors:

  - 401/403: Authentication failed (check `e.is_authentication_error`)
  - 404: Account not found (check `e.is_not_found`)
  - 429: Rate limit exceeded (check `e.is_rate_limited`, use `e.retry_after`)
  - 400: Invalid parameters or insufficient margin (inspect `e.code` and `e.details`)

---

## post_limit_order

Create a limit order (convenience method for order execution at specified price or better).

**OANDA Endpoint**: `POST /v3/accounts/{accountID}/orders`

<!-- code-block: orders__post_limit_order -->
```python
import asyncio
from decimal import Decimal

from dotenv import load_dotenv

from fivetwenty import AsyncClient
from fivetwenty.endpoints.orders import OrderResponse
from fivetwenty.models import InstrumentName

load_dotenv()


async def main() -> None:
    async with AsyncClient() as client:
        # Create a limit order to buy EUR/USD at 1.1350
        order: OrderResponse = await client.orders.post_limit_order(
            account_id=client.account_id,
            instrument=InstrumentName.EUR_USD,
            units=1000,
            price=Decimal("1.1350"),
        )
        print(f"Last Transaction ID: {order['lastTransactionID']}")


if __name__ == "__main__":
    asyncio.run(main())
```

🔗 **OANDA Documentation**: [Create Order](https://developer.oanda.com/rest-live-v20/order-ep/#create-order)

🔗 **Source**: [orders.post_limit_order](https://github.com/NimbleOx/fivetwenty/blob/main/fivetwenty/endpoints/orders.py#L281)

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

**Returns:** `OrderResponse` TypedDict containing:

- `lastTransactionID`: Transaction ID string
- `orderCreateTransaction`: Transaction details for the created order
- `relatedTransactionIDs`: List of related transaction IDs

**Raises:**

`FiveTwentyError` - API errors:

  - 401/403: Authentication failed (check `e.is_authentication_error`)
  - 404: Account not found (check `e.is_not_found`)
  - 429: Rate limit exceeded (check `e.is_rate_limited`, use `e.retry_after`)
  - 400: Invalid parameters (inspect `e.code` and `e.details`)

---

## post_stop_order

Create a stop order (convenience method for order execution when market reaches trigger price).

**OANDA Endpoint**: `POST /v3/accounts/{accountID}/orders`

<!-- code-block: orders__post_stop_order -->
```python
import asyncio
from decimal import Decimal

from dotenv import load_dotenv

from fivetwenty import AsyncClient
from fivetwenty.endpoints.orders import OrderResponse
from fivetwenty.models import InstrumentName

load_dotenv()


async def main() -> None:
    async with AsyncClient() as client:
        # Create a stop order triggered when EUR/USD reaches 1.1200
        order: OrderResponse = await client.orders.post_stop_order(
            account_id=client.account_id,
            instrument=InstrumentName.EUR_USD,
            units=1000,
            price=Decimal("1.1200"),
        )
        print(f"Last Transaction ID: {order['lastTransactionID']}")


if __name__ == "__main__":
    asyncio.run(main())
```

🔗 **OANDA Documentation**: [Create Order](https://developer.oanda.com/rest-live-v20/order-ep/#create-order)

🔗 **Source**: [orders.post_stop_order](https://github.com/NimbleOx/fivetwenty/blob/main/fivetwenty/endpoints/orders.py#L349)

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

**Returns:** `OrderResponse` TypedDict containing:

- `lastTransactionID`: Transaction ID string
- `orderCreateTransaction`: Transaction details for the created order
- `relatedTransactionIDs`: List of related transaction IDs

**Raises:**

`FiveTwentyError` - API errors:

  - 401/403: Authentication failed (check `e.is_authentication_error`)
  - 404: Account not found (check `e.is_not_found`)
  - 429: Rate limit exceeded (check `e.is_rate_limited`, use `e.retry_after`)
  - 400: Invalid parameters (inspect `e.code` and `e.details`)

---

## post_market_if_touched_order

Create a market-if-touched order (convenience method for market order execution when price reaches trigger level).

**OANDA Endpoint**: `POST /v3/accounts/{accountID}/orders`

<!-- code-block: orders__post_market_if_touched_order -->
```python
import asyncio
from decimal import Decimal

from dotenv import load_dotenv

from fivetwenty import AsyncClient
from fivetwenty.endpoints.orders import OrderResponse
from fivetwenty.models import InstrumentName

load_dotenv()


async def main() -> None:
    async with AsyncClient() as client:
        # Create market-if-touched order triggered at 1.1400
        order: OrderResponse = await client.orders.post_market_if_touched_order(
            account_id=client.account_id,
            instrument=InstrumentName.EUR_USD,
            units=1000,
            price=Decimal("1.1400"),
        )
        print(f"Last Transaction ID: {order['lastTransactionID']}")


if __name__ == "__main__":
    asyncio.run(main())
```

🔗 **OANDA Documentation**: [Create Order](https://developer.oanda.com/rest-live-v20/order-ep/#create-order)

🔗 **Source**: [orders.post_market_if_touched_order](https://github.com/NimbleOx/fivetwenty/blob/main/fivetwenty/endpoints/orders.py#L420)

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

**Returns:** `OrderResponse` TypedDict containing:

- `lastTransactionID`: Transaction ID string
- `orderCreateTransaction`: Transaction details for the created order
- `relatedTransactionIDs`: List of related transaction IDs

**Raises:**

`FiveTwentyError` - API errors:

  - 401/403: Authentication failed (check `e.is_authentication_error`)
  - 404: Account not found (check `e.is_not_found`)
  - 429: Rate limit exceeded (check `e.is_rate_limited`, use `e.retry_after`)
  - 400: Invalid parameters (inspect `e.code` and `e.details`)

---

## get_orders

Get a list of orders for an account with optional filtering.

**OANDA Endpoint**: `GET /v3/accounts/{accountID}/orders`

!!! note "Beta Compatibility"
    `get_orders()` returns OANDA's response envelope, not a bare list. Code written against older beta versions should change from `orders = await client.orders.get_orders(account_id)` to:

    ```text
    result = await client.orders.get_orders(account_id)
    orders = result["orders"]
    last_transaction_id = result["lastTransactionID"]
    ```

    The synchronous `Client` uses the same response shape.

<!-- code-block: orders__get_orders -->
```python
import asyncio

from dotenv import load_dotenv

from fivetwenty import AsyncClient

load_dotenv()


async def main() -> None:
    async with AsyncClient() as client:
        # Get pending orders for the account
        result = await client.orders.get_orders(
            account_id=client.account_id,
            state="PENDING",
            count=50,
        )
        orders = result["orders"]
        print(f"Found {len(orders)} orders")
        print(f"Last Transaction ID: {result['lastTransactionID']}")


if __name__ == "__main__":
    asyncio.run(main())
```

🔗 **OANDA Documentation**: [Get Orders](https://developer.oanda.com/rest-live-v20/order-ep/#get-orders)

🔗 **Source**: [orders.get_orders](https://github.com/NimbleOx/fivetwenty/blob/main/fivetwenty/endpoints/orders.py#L491)

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `account_id` | AccountID | ✅ | Target account identifier |
| `*` | | | **Keyword-only parameters below** |
| `ids` | list[str] \| None | ➖ | List of specific order IDs to retrieve |
| `state` | OrderStateFilter \| str | ➖ | Filter by order state - default: "PENDING" |
| `instrument` | str \| None | ➖ | Filter by instrument |
| `count` | int | ➖ | Maximum number of orders to return - default: 50, max: 500 |
| `before_id` | str \| None | ➖ | Maximum order ID to return |

**Returns:** `GetOrdersResponse` TypedDict containing:

- `orders`: List of Order models
- `lastTransactionID`: Transaction ID string

**Raises:**

`FiveTwentyError` - API errors:

  - 401/403: Authentication failed (check `e.is_authentication_error`)
  - 404: Account not found (check `e.is_not_found`)
  - 429: Rate limit exceeded (check `e.is_rate_limited`, use `e.retry_after`)
  - 400: Invalid filter parameters (inspect `e.code` and `e.details`)

`ValueError` - If count is outside 1-500

---

## get_order

Get details for a specific order by order ID or specifier.

**OANDA Endpoint**: `GET /v3/accounts/{accountID}/orders/{orderSpecifier}`

<!-- code-block: orders__get_order -->
```python
import asyncio

from dotenv import load_dotenv

from fivetwenty import AsyncClient
from fivetwenty.endpoints.orders import GetOrderResponse

load_dotenv()


async def main() -> None:
    async with AsyncClient() as client:
        # Get details for a specific order
        # Replace with your actual order ID
        result: GetOrderResponse = await client.orders.get_order(
            account_id=client.account_id,
            order_specifier="12345",
        )
        order = result["order"]
        print(f"Order type: {order.type}")
        print(f"Last Transaction ID: {result['lastTransactionID']}")


if __name__ == "__main__":
    asyncio.run(main())
```

🔗 **OANDA Documentation**: [Get Order](https://developer.oanda.com/rest-live-v20/order-ep/#get-order)

🔗 **Source**: [orders.get_order](https://github.com/NimbleOx/fivetwenty/blob/main/fivetwenty/endpoints/orders.py#L551)

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `account_id` | AccountID | ✅ | Target account identifier |
| `order_specifier` | str | ✅ | Order identifier or specifier |

**Returns:** `GetOrderResponse` TypedDict containing:

- `order`: Order model with full order details
- `lastTransactionID`: Transaction ID string

**Raises:**

`FiveTwentyError` - API errors:

  - 401/403: Authentication failed (check `e.is_authentication_error`)
  - 404: Order or account not found (check `e.is_not_found`)
  - 429: Rate limit exceeded (check `e.is_rate_limited`, use `e.retry_after`)

---

## cancel_order

Cancel a pending order by order ID or specifier.

**OANDA Endpoint**: `PUT /v3/accounts/{accountID}/orders/{orderSpecifier}/cancel`

<!-- code-block: orders__cancel_order -->
```python
import asyncio

from dotenv import load_dotenv

from fivetwenty import AsyncClient
from fivetwenty.endpoints.orders import CancelOrderResponse

load_dotenv()


async def main() -> None:
    async with AsyncClient() as client:
        # Cancel a pending order
        # Replace with your actual order ID
        result: CancelOrderResponse = await client.orders.cancel_order(
            account_id=client.account_id,
            order_specifier="12345",
        )
        print(f"Last Transaction ID: {result['lastTransactionID']}")


if __name__ == "__main__":
    asyncio.run(main())
```

🔗 **OANDA Documentation**: [Cancel Order](https://developer.oanda.com/rest-live-v20/order-ep/#cancel-order)

🔗 **Source**: [orders.cancel_order](https://github.com/NimbleOx/fivetwenty/blob/main/fivetwenty/endpoints/orders.py#L581)

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `account_id` | AccountID | ✅ | Target account identifier |
| `order_specifier` | str | ✅ | Order identifier to cancel |
| `*` | | | **Keyword-only parameters below** |
| `timeout` | float \| None | ➖ | Request timeout override |
| `client_request_id` | str \| None | ➖ | Client-provided request ID for debugging and correlation |

**Returns:** `CancelOrderResponse` TypedDict containing:

- `orderCancelTransaction`: Transaction details for the cancellation
- `relatedTransactionIDs`: List of related transaction IDs
- `lastTransactionID`: Transaction ID string

**Raises:**

`FiveTwentyError` - API errors:

  - 401/403: Authentication failed (check `e.is_authentication_error`)
  - 404: Order or account not found (check `e.is_not_found`)
  - 429: Rate limit exceeded (check `e.is_rate_limited`, use `e.retry_after`)
  - 400: Order not cancellable (already filled or cancelled) (inspect `e.code` and `e.details`)

---

## get_pending_orders

Get all pending orders for an account.

**OANDA Endpoint**: `GET /v3/accounts/{accountID}/pendingOrders`

<!-- code-block: orders__get_pending_orders -->
```python
import asyncio

from dotenv import load_dotenv

from fivetwenty import AsyncClient
from fivetwenty.endpoints.orders import PendingOrdersResponse

load_dotenv()


async def main() -> None:
    async with AsyncClient() as client:
        # Get all pending orders
        result: PendingOrdersResponse = await client.orders.get_pending_orders(
            account_id=client.account_id
        )
        pending_orders = result["orders"]
        print(f"Found {len(pending_orders)} pending orders")
        print(f"Last Transaction ID: {result['lastTransactionID']}")


if __name__ == "__main__":
    asyncio.run(main())
```

🔗 **OANDA Documentation**: [Get Pending Orders](https://developer.oanda.com/rest-live-v20/order-ep/#get-pending-orders)

🔗 **Source**: [orders.get_pending_orders](https://github.com/NimbleOx/fivetwenty/blob/main/fivetwenty/endpoints/orders.py#L629)

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `account_id` | AccountID | ✅ | Target account identifier |

**Returns:** `PendingOrdersResponse` TypedDict containing:

- `orders`: List of pending Order models
- `lastTransactionID`: Transaction ID string

**Raises:**

`FiveTwentyError` - API errors:

  - 401/403: Authentication failed (check `e.is_authentication_error`)
  - 404: Account not found (check `e.is_not_found`)
  - 429: Rate limit exceeded (check `e.is_rate_limited`, use `e.retry_after`)

---

## put_order

Replace an existing order by cancelling it and creating a new order with updated parameters.

**OANDA Endpoint**: `PUT /v3/accounts/{accountID}/orders/{orderSpecifier}`

<!-- code-block: orders__put_order -->
```python
import asyncio
from decimal import Decimal

from dotenv import load_dotenv

from fivetwenty import AsyncClient
from fivetwenty.endpoints.orders import ReplaceOrderResponse
from fivetwenty.models import InstrumentName, LimitOrderRequest

load_dotenv()


async def main() -> None:
    async with AsyncClient() as client:
        # Replace an existing limit order with new price
        # Replace with your actual order ID
        result: ReplaceOrderResponse = await client.orders.put_order(
            account_id=client.account_id,
            order_specifier="12345",
            order_request=LimitOrderRequest(
                instrument=InstrumentName.EUR_USD,
                units=Decimal("1000"),
                price=Decimal("1.1400"),
            ),
        )
        print(f"Last Transaction ID: {result['lastTransactionID']}")


if __name__ == "__main__":
    asyncio.run(main())
```

🔗 **OANDA Documentation**: [Replace Order](https://developer.oanda.com/rest-live-v20/order-ep/#replace-order)

🔗 **Source**: [orders.put_order](https://github.com/NimbleOx/fivetwenty/blob/main/fivetwenty/endpoints/orders.py#L665)

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `account_id` | AccountID | ✅ | Target account identifier |
| `order_specifier` | str | ✅ | Order identifier to replace |
| `order_request` | OrderRequest \| dict[str, Any] | ✅ | New order specification |
| `*` | | | **Keyword-only parameters below** |
| `client_request_id` | str \| None | ➖ | Client-provided request ID for debugging and correlation |

**Returns:** `ReplaceOrderResponse` TypedDict containing:

- `orderCancelTransaction`: Transaction details for cancelled order (optional)
- `orderCreateTransaction`: Transaction details for new order
- `orderFillTransaction`: Transaction details if new order filled (optional)
- `relatedTransactionIDs`: List of related transaction IDs
- `lastTransactionID`: Transaction ID string

**Raises:**

`FiveTwentyError` - API errors:

  - 401/403: Authentication failed (check `e.is_authentication_error`)
  - 404: Order or account not found (check `e.is_not_found`)
  - 429: Rate limit exceeded (check `e.is_rate_limited`, use `e.retry_after`)
  - 400: Invalid order specification or replacement failed (inspect `e.code` and `e.details`)

---

## put_order_client_extensions

Modify client extensions for an existing order without replacing the order.

**OANDA Endpoint**: `PUT /v3/accounts/{accountID}/orders/{orderSpecifier}/clientExtensions`

<!-- code-block: orders__put_order_client_extensions -->
```python
import asyncio

from dotenv import load_dotenv

from fivetwenty import AsyncClient
from fivetwenty.endpoints.orders import OrderClientExtensionsResponse
from fivetwenty.models import ClientExtensions

load_dotenv()


async def main() -> None:
    async with AsyncClient() as client:
        # Update client extensions for an order
        # Replace with your actual order ID
        result: OrderClientExtensionsResponse = (
            await client.orders.put_order_client_extensions(
                account_id=client.account_id,
                order_specifier="12345",
                client_extensions=ClientExtensions(comment="Updated order"),
            )
        )
        print(f"Last Transaction ID: {result['lastTransactionID']}")


if __name__ == "__main__":
    asyncio.run(main())
```

🔗 **OANDA Documentation**: [Update Order Client Extensions](https://developer.oanda.com/rest-live-v20/order-ep/#update-order-client-extensions)

🔗 **Source**: [orders.put_order_client_extensions](https://github.com/NimbleOx/fivetwenty/blob/main/fivetwenty/endpoints/orders.py#L731)

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `account_id` | AccountID | ✅ | Target account identifier |
| `order_specifier` | str | ✅ | Order identifier to modify |
| `*` | | | **Keyword-only parameters below** |
| `client_extensions` | ClientExtensions \| None | ➖ | New order client extensions |
| `trade_client_extensions` | ClientExtensions \| None | ➖ | New trade client extensions |

**Returns:** `OrderClientExtensionsResponse` TypedDict containing:

- `orderClientExtensionsModifyTransaction`: Transaction details for the modification
- `relatedTransactionIDs`: List of related transaction IDs
- `lastTransactionID`: Transaction ID string

**Raises:**

`FiveTwentyError` - API errors:

  - 401/403: Authentication failed (check `e.is_authentication_error`)
  - 404: Order or account not found (check `e.is_not_found`)
  - 429: Rate limit exceeded (check `e.is_rate_limited`, use `e.retry_after`)
  - 400: Invalid client extensions or modification failed (inspect `e.code` and `e.details`)
