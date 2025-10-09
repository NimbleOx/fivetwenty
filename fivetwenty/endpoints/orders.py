"""Order management endpoints.

OANDA Order Management Patterns:
-------------------------------
1. Primary Trading: Use convenience methods (post_market_order, post_limit_order) with
   takeProfitOnFill/stopLossOnFill for immediate risk management upon execution.

2. Post-Trade Risk Management: Use post_order() with TakeProfitOrderRequest,
   StopLossOrderRequest, etc. to add risk management to existing trades.

3. Advanced Orders: Use post_order() with specific order request types for full control.
"""

from decimal import Decimal
from typing import TYPE_CHECKING, Any, TypedDict

from .._internal.utils import quantize_price
from ..models import (
    AccountID,
    ClientExtensions,
    FixedPriceOrder,
    GuaranteedStopLossOrder,
    GuaranteedStopLossOrderRejectTransaction,
    GuaranteedStopLossOrderRequest,
    GuaranteedStopLossOrderTransaction,
    InstrumentName,
    LimitOrder,
    LimitOrderRejectTransaction,
    LimitOrderRequest,
    LimitOrderTransaction,
    MarketIfTouchedOrder,
    MarketIfTouchedOrderRejectTransaction,
    MarketIfTouchedOrderRequest,
    MarketIfTouchedOrderTransaction,
    MarketOrder,
    MarketOrderRejectTransaction,
    MarketOrderRequest,
    MarketOrderTransaction,
    OrderCancelTransaction,
    OrderClientExtensionsModifyTransaction,
    OrderFillTransaction,
    StopLossDetails,
    StopLossOrder,
    StopLossOrderRejectTransaction,
    StopLossOrderRequest,
    StopLossOrderTransaction,
    StopOrder,
    StopOrderRejectTransaction,
    StopOrderRequest,
    StopOrderTransaction,
    TakeProfitDetails,
    TakeProfitOrder,
    TakeProfitOrderRejectTransaction,
    TakeProfitOrderRequest,
    TakeProfitOrderTransaction,
    TimeInForce,
    TrailingStopLossOrder,
    TrailingStopLossOrderRejectTransaction,
    TrailingStopLossOrderRequest,
    TrailingStopLossOrderTransaction,
)

if TYPE_CHECKING:
    from ..client import AsyncClient

# Union type for all possible order types returned by the API
Order = MarketOrder | LimitOrder | StopOrder | MarketIfTouchedOrder | TakeProfitOrder | StopLossOrder | GuaranteedStopLossOrder | TrailingStopLossOrder | FixedPriceOrder

# Union type for order request objects (for order creation)
OrderRequest = MarketOrderRequest | LimitOrderRequest | StopOrderRequest | TakeProfitOrderRequest | StopLossOrderRequest | MarketIfTouchedOrderRequest | TrailingStopLossOrderRequest | GuaranteedStopLossOrderRequest

# Union type for order creation transactions
OrderCreateTransaction = MarketOrderTransaction | LimitOrderTransaction | StopOrderTransaction | MarketIfTouchedOrderTransaction | TakeProfitOrderTransaction | StopLossOrderTransaction | TrailingStopLossOrderTransaction | GuaranteedStopLossOrderTransaction

# Union type for order rejection transactions
OrderRejectTransaction = MarketOrderRejectTransaction | LimitOrderRejectTransaction | StopOrderRejectTransaction | MarketIfTouchedOrderRejectTransaction | TakeProfitOrderRejectTransaction | StopLossOrderRejectTransaction | TrailingStopLossOrderRejectTransaction | GuaranteedStopLossOrderRejectTransaction


class OrderResponse(TypedDict, total=False):
    """Response from order creation endpoints."""

    orderCreateTransaction: OrderCreateTransaction
    orderFillTransaction: OrderFillTransaction
    orderCancelTransaction: OrderCancelTransaction
    orderReissueTransaction: OrderCreateTransaction  # Re-issued order creation
    orderReissueRejectTransaction: OrderRejectTransaction  # Rejection of re-issue
    relatedTransactionIDs: list[str]
    lastTransactionID: str  # Required field


class GetOrderResponse(TypedDict):
    """Response from get_order endpoint."""

    order: Order
    lastTransactionID: str


class CancelOrderResponse(TypedDict, total=False):
    """Response from cancel_order endpoint."""

    orderCancelTransaction: OrderCancelTransaction
    relatedTransactionIDs: list[str]
    lastTransactionID: str


class PendingOrdersResponse(TypedDict):
    """Response from get_pending_orders endpoint."""

    orders: list[Order]
    lastTransactionID: str


class ReplaceOrderResponse(TypedDict, total=False):
    """Response from put_order endpoint."""

    orderCancelTransaction: OrderCancelTransaction
    orderCreateTransaction: OrderCreateTransaction
    orderFillTransaction: OrderFillTransaction
    relatedTransactionIDs: list[str]
    lastTransactionID: str


class OrderClientExtensionsResponse(TypedDict, total=False):
    """Response from put_order_client_extensions endpoint."""

    orderClientExtensionsModifyTransaction: OrderClientExtensionsModifyTransaction
    relatedTransactionIDs: list[str]
    lastTransactionID: str


class OrderEndpoints:
    """Order management operations."""

    def __init__(self, client: "AsyncClient"):
        self._client = client
        self._precision_cache: dict[str, int] = {}  # Simple cache for demo

    async def post_order(
        self,
        account_id: AccountID,
        order_request: OrderRequest,
        *,
        timeout: float | None = None,
        client_request_id: str | None = None,
    ) -> OrderResponse:
        """
        Create an order of any type.

        OANDA Order Pattern Guide:
        -------------------------
        1. **Primary Orders** (open new positions):
           - MarketOrderRequest, LimitOrderRequest, StopOrderRequest, MarketIfTouchedOrderRequest
           - Use takeProfitOnFill/stopLossOnFill for automatic risk management

        2. **Risk Management Orders** (manage existing trades):
           - TakeProfitOrderRequest, StopLossOrderRequest, TrailingStopLossOrderRequest
           - Require existing tradeID - used for post-trade risk management
           - GuaranteedStopLossOrderRequest - may be used standalone with special requirements

        3. **Administrative Orders** (internal use only):
           - FixedPriceOrder - Cannot be created via public API

        Args:
            account_id: Account to create order for
            order_request: Order request object (any supported order type)
            timeout: Request timeout override
            client_request_id: Optional client-provided request ID for debugging and
                correlation purposes. This appears in OANDA's internal logs but NOT
                in transaction responses. Useful for support tickets and request
                tracking in your application. Does NOT provide idempotency.
                Example: "trading-bot-v1-2025-01-15T10:30:00" or "support-issue-123"

        Returns:
            Order response with transaction details

        Raises:
            FiveTwentyError: On API errors
            ValueError: On invalid parameters
        """
        # Convert to dict and wrap in "order" parameter as required by OANDA API
        order_data = order_request.model_dump(by_alias=True, exclude_none=True, mode="json")
        body = {"order": order_data}

        # Add ClientRequestID header for request correlation and debugging
        # NOTE: This appears in OANDA's internal logs but NOT in transaction responses
        # OANDA will generate its own numeric requestID in transaction data
        headers = {"ClientRequestID": client_request_id} if client_request_id else {}

        response = await self._client._request(
            "POST",
            f"/accounts/{account_id}/orders",
            json_data=body,
            timeout=timeout,
            headers=headers,
        )

        data = response.json()
        result: OrderResponse = {
            "lastTransactionID": data["lastTransactionID"],
        }

        if "orderCreateTransaction" in data:
            result["orderCreateTransaction"] = self._parse_order_transaction(data["orderCreateTransaction"])
        if "orderFillTransaction" in data:
            result["orderFillTransaction"] = OrderFillTransaction.model_validate(data["orderFillTransaction"])
        if "orderCancelTransaction" in data:
            result["orderCancelTransaction"] = OrderCancelTransaction.model_validate(data["orderCancelTransaction"])
        if "orderReissueTransaction" in data:
            result["orderReissueTransaction"] = self._parse_order_transaction(data["orderReissueTransaction"])
        if "orderReissueRejectTransaction" in data:
            result["orderReissueRejectTransaction"] = self._parse_order_reject_transaction(data["orderReissueRejectTransaction"])
        if "relatedTransactionIDs" in data:
            result["relatedTransactionIDs"] = data["relatedTransactionIDs"]

        return result

    async def post_market_order(
        self,
        account_id: AccountID,
        instrument: InstrumentName,
        units: int | Decimal | str,
        *,
        take_profit: Decimal | None = None,
        stop_loss: Decimal | None = None,
        timeout: float | None = None,
        client_request_id: str | None = None,
    ) -> OrderResponse:
        """
        Create a market order (convenience method).

        RECOMMENDED PATTERN: Use take_profit and stop_loss parameters here for automatic
        risk management that activates when the order fills. This is preferred over
        creating separate TakeProfitOrderRequest/StopLossOrderRequest after the trade.

        Args:
            account_id: Account to create order for
            instrument: Instrument to trade
            units: Number of units (positive = buy, negative = sell)
            take_profit: Take profit price (optional) - creates takeProfitOnFill order
            stop_loss: Stop loss price (optional) - creates stopLossOnFill order
            timeout: Request timeout override
            client_request_id: Optional client-provided request ID for debugging and
                correlation purposes. See post_order() for detailed explanation.

        Returns:
            Order response with transaction details

        Raises:
            FiveTwentyError: On API errors
            ValueError: On invalid parameters
        """
        # Build the market order request
        request = MarketOrderRequest(
            instrument=instrument,
            units=units,  # type: ignore[arg-type]  # Pydantic handles conversion to Decimal  # type: ignore[arg-type]  # Pydantic handles conversion to Decimal
        )

        # Add take profit if specified
        if take_profit is not None:
            precision = await self._get_precision(account_id, instrument)
            quantized_tp = quantize_price(precision, take_profit)
            request.take_profit_on_fill = TakeProfitDetails(price=quantized_tp)

        # Add stop loss if specified
        if stop_loss is not None:
            precision = await self._get_precision(account_id, instrument)
            quantized_sl = quantize_price(precision, stop_loss)
            request.stop_loss_on_fill = StopLossDetails(price=quantized_sl)

        return await self.post_order(
            account_id=account_id,
            order_request=request,
            timeout=timeout,
            client_request_id=client_request_id,
        )

    async def post_limit_order(
        self,
        account_id: AccountID,
        instrument: InstrumentName,
        units: int | Decimal | str,
        price: Decimal,
        *,
        time_in_force: str = "GTC",
        take_profit: Decimal | None = None,
        stop_loss: Decimal | None = None,
        timeout: float | None = None,
        client_request_id: str | None = None,
    ) -> OrderResponse:
        """
        Create a limit order (convenience method).

        RECOMMENDED PATTERN: Use take_profit and stop_loss parameters here for automatic
        risk management that activates when the order fills. This is preferred over
        creating separate TakeProfitOrderRequest/StopLossOrderRequest after the trade.

        Args:
            account_id: Account to create order for
            instrument: Instrument to trade
            units: Number of units (positive = buy, negative = sell)
            price: Limit price for order execution
            time_in_force: Order time in force (GTC, GTD, GFD, FOK, IOC)
            take_profit: Take profit price (optional) - creates takeProfitOnFill order
            stop_loss: Stop loss price (optional) - creates stopLossOnFill order
            timeout: Request timeout override
            client_request_id: Optional client-provided request ID for debugging and
                correlation purposes. See post_order() for detailed explanation.

        Returns:
            Order response with transaction details

        Raises:
            FiveTwentyError: On API errors
            ValueError: On invalid parameters
        """
        # Get precision for price quantization
        precision = await self._get_precision(account_id, instrument)
        quantized_price = quantize_price(precision, price)

        # Build the limit order request
        request = LimitOrderRequest(
            instrument=instrument,
            units=units,  # type: ignore[arg-type]  # Pydantic handles conversion to Decimal
            price=quantized_price,
            timeInForce=TimeInForce(time_in_force),
        )

        # Add take profit if specified
        if take_profit is not None:
            quantized_tp = quantize_price(precision, take_profit)
            request.take_profit_on_fill = TakeProfitDetails(price=quantized_tp)

        # Add stop loss if specified
        if stop_loss is not None:
            quantized_sl = quantize_price(precision, stop_loss)
            request.stop_loss_on_fill = StopLossDetails(price=quantized_sl)

        return await self.post_order(
            account_id=account_id,
            order_request=request,
            timeout=timeout,
            client_request_id=client_request_id,
        )

    async def post_stop_order(
        self,
        account_id: AccountID,
        instrument: InstrumentName,
        units: int | Decimal | str,
        price: Decimal,
        *,
        price_bound: Decimal | None = None,
        time_in_force: str = "GTC",
        take_profit: Decimal | None = None,
        stop_loss: Decimal | None = None,
        timeout: float | None = None,
        client_request_id: str | None = None,
    ) -> OrderResponse:
        """
        Create a stop order (convenience method).

        Args:
            account_id: Account to create order for
            instrument: Instrument to trade
            units: Number of units (positive = buy, negative = sell)
            price: Stop price for order execution
            price_bound: Optional price bound for order execution
            time_in_force: Order time in force (GTC, GTD, GFD, FOK, IOC)
            take_profit: Take profit price (optional)
            stop_loss: Stop loss price (optional)
            timeout: Request timeout override
            client_request_id: Optional client-provided request ID for debugging and
                correlation purposes. See post_order() for detailed explanation.

        Returns:
            Order response with transaction details

        Raises:
            FiveTwentyError: On API errors
            ValueError: On invalid parameters
        """
        # Get precision for price quantization
        precision = await self._get_precision(account_id, instrument)
        quantized_price = quantize_price(precision, price)

        # Build the stop order request
        request = StopOrderRequest(
            instrument=instrument,
            units=units,  # type: ignore[arg-type]  # Pydantic handles conversion to Decimal
            price=quantized_price,
            timeInForce=TimeInForce(time_in_force),
        )

        # Add price bound if specified
        if price_bound is not None:
            quantized_bound = quantize_price(precision, price_bound)
            request.price_bound = quantized_bound

        # Add take profit if specified
        if take_profit is not None:
            quantized_tp = quantize_price(precision, take_profit)
            request.take_profit_on_fill = TakeProfitDetails(price=quantized_tp)

        # Add stop loss if specified
        if stop_loss is not None:
            quantized_sl = quantize_price(precision, stop_loss)
            request.stop_loss_on_fill = StopLossDetails(price=quantized_sl)

        return await self.post_order(
            account_id=account_id,
            order_request=request,
            timeout=timeout,
            client_request_id=client_request_id,
        )

    async def post_market_if_touched_order(
        self,
        account_id: AccountID,
        instrument: InstrumentName,
        units: int | Decimal | str,
        price: Decimal,
        *,
        price_bound: Decimal | None = None,
        time_in_force: str = "GTC",
        take_profit: Decimal | None = None,
        stop_loss: Decimal | None = None,
        timeout: float | None = None,
        client_request_id: str | None = None,
    ) -> OrderResponse:
        """
        Create a market-if-touched order (convenience method).

        Args:
            account_id: Account to create order for
            instrument: Instrument to trade
            units: Number of units (positive = buy, negative = sell)
            price: Trigger price for order execution
            price_bound: Optional price bound for order execution
            time_in_force: Order time in force (GTC, GTD, GFD, FOK, IOC)
            take_profit: Take profit price (optional)
            stop_loss: Stop loss price (optional)
            timeout: Request timeout override
            client_request_id: Optional client-provided request ID for debugging and
                correlation purposes. See post_order() for detailed explanation.

        Returns:
            Order response with transaction details

        Raises:
            FiveTwentyError: On API errors
            ValueError: On invalid parameters
        """
        # Get precision for price quantization
        precision = await self._get_precision(account_id, instrument)
        quantized_price = quantize_price(precision, price)

        # Build the market-if-touched order request
        request = MarketIfTouchedOrderRequest(
            instrument=instrument,
            units=units,  # type: ignore[arg-type]  # Pydantic handles conversion to Decimal
            price=quantized_price,
            timeInForce=TimeInForce(time_in_force),
        )

        # Add price bound if specified
        if price_bound is not None:
            quantized_bound = quantize_price(precision, price_bound)
            request.price_bound = quantized_bound

        # Add take profit if specified
        if take_profit is not None:
            quantized_tp = quantize_price(precision, take_profit)
            request.take_profit_on_fill = TakeProfitDetails(price=quantized_tp)

        # Add stop loss if specified
        if stop_loss is not None:
            quantized_sl = quantize_price(precision, stop_loss)
            request.stop_loss_on_fill = StopLossDetails(price=quantized_sl)

        return await self.post_order(
            account_id=account_id,
            order_request=request,
            timeout=timeout,
            client_request_id=client_request_id,
        )

    async def get_orders(
        self,
        account_id: AccountID,
        *,
        ids: list[str] | None = None,
        state: str = "PENDING",
        instrument: str | None = None,
        count: int = 50,
        before_id: str | None = None,
    ) -> list[Order]:
        """
        List orders for an account.

        Args:
            account_id: Account ID
            ids: List of specific order IDs to fetch (optional)
            state: Order state filter
            instrument: Instrument filter (optional)
            count: Maximum number of orders
            before_id: Get orders before this ID

        Returns:
            List of order models

        Raises:
            FiveTwentyError: On API errors
        """
        params = {
            "state": state,
            "count": count,
        }

        if ids:
            params["ids"] = ",".join(ids)
        if instrument:
            params["instrument"] = instrument.value if hasattr(instrument, "value") else str(instrument)
        if before_id:
            params["beforeID"] = before_id

        response = await self._client._request(
            "GET",
            f"/accounts/{account_id}/orders",
            params=params,
        )
        data = response.json()

        # Parse each order based on its type field
        return [self._parse_order(order_data) for order_data in data.get("orders", [])]

    async def get_order(self, account_id: AccountID, order_specifier: str) -> GetOrderResponse:
        """
        Get order details.

        Args:
            account_id: Account ID
            order_specifier: Order ID or @clientID format

        Returns:
            Dictionary containing order details and lastTransactionID

        Raises:
            FiveTwentyError: On API errors
        """
        response = await self._client._request(
            "GET",
            f"/accounts/{account_id}/orders/{order_specifier}",
        )
        data = response.json()

        return {
            "order": self._parse_order(data["order"]),
            "lastTransactionID": data["lastTransactionID"],
        }

    async def cancel_order(
        self,
        account_id: AccountID,
        order_specifier: str,
        *,
        timeout: float | None = None,
        client_request_id: str | None = None,
    ) -> CancelOrderResponse:
        """
        Cancel an order.

        Args:
            account_id: Account ID
            order_specifier: Order ID or @clientID format to cancel
            timeout: Request timeout override
            client_request_id: Client request ID for debugging and correlation

        Returns:
            Cancellation response

        Raises:
            FiveTwentyError: On API errors
        """
        headers = {}
        if client_request_id:
            headers["ClientRequestID"] = client_request_id

        response = await self._client._request(
            "PUT",
            f"/accounts/{account_id}/orders/{order_specifier}/cancel",
            timeout=timeout,
            headers=headers,
        )

        data = response.json()
        result: CancelOrderResponse = {
            "lastTransactionID": data["lastTransactionID"],
        }

        if "orderCancelTransaction" in data:
            result["orderCancelTransaction"] = OrderCancelTransaction.model_validate(data["orderCancelTransaction"])
        if "relatedTransactionIDs" in data:
            result["relatedTransactionIDs"] = data["relatedTransactionIDs"]

        return result

    async def get_pending_orders(
        self,
        account_id: AccountID,
    ) -> PendingOrdersResponse:
        """
        List all pending orders for an account.

        Pending orders are orders that have been created but not yet filled,
        cancelled or expired.

        Args:
            account_id: Account identifier

        Returns:
            Dictionary containing list of pending orders and last transaction ID

        Raises:
            FiveTwentyError: On API errors
        """
        response = await self._client._request(
            "GET",
            f"/accounts/{account_id}/pendingOrders",
        )

        data = response.json()

        return {
            "orders": [self._parse_order(order_data) for order_data in data.get("orders", [])],
            "lastTransactionID": data["lastTransactionID"],
        }

    async def put_order(
        self,
        account_id: AccountID,
        order_specifier: str,
        order_request: OrderRequest,
        *,
        client_request_id: str | None = None,
    ) -> ReplaceOrderResponse:
        """
        Replace an existing order with a new order.

        This operation atomically cancels the existing order and creates
        a replacement order. The OrderSpecifier can be either an Order ID
        or a client-provided identifier using @clientID format.

        Args:
            account_id: Account identifier
            order_specifier: Order ID or @clientID to replace
            order_request: New order specification (any OrderRequest type)
            client_request_id: Optional client-provided request ID for debugging and
                correlation purposes. See post_order() for detailed explanation.

        Returns:
            Dictionary containing replacement transaction details

        Raises:
            FiveTwentyError: On API errors (404 if order not found)
        """
        headers = {}
        if client_request_id:
            headers["ClientRequestID"] = client_request_id

        # Convert Pydantic model to dict with proper formatting
        order_data = order_request.model_dump(by_alias=True, exclude_none=True, mode="json")

        response = await self._client._request(
            "PUT",
            f"/accounts/{account_id}/orders/{order_specifier}",
            json_data={"order": order_data},
            headers=headers,
        )

        data = response.json()
        result: ReplaceOrderResponse = {
            "lastTransactionID": data["lastTransactionID"],
        }

        if "orderCancelTransaction" in data:
            result["orderCancelTransaction"] = OrderCancelTransaction.model_validate(data["orderCancelTransaction"])
        if "orderCreateTransaction" in data:
            result["orderCreateTransaction"] = self._parse_order_transaction(data["orderCreateTransaction"])
        if "orderFillTransaction" in data:
            result["orderFillTransaction"] = OrderFillTransaction.model_validate(data["orderFillTransaction"])
        if "relatedTransactionIDs" in data:
            result["relatedTransactionIDs"] = data["relatedTransactionIDs"]

        return result

    async def put_order_client_extensions(
        self,
        account_id: AccountID,
        order_specifier: str,
        *,
        client_extensions: ClientExtensions | None = None,
        trade_client_extensions: ClientExtensions | None = None,
    ) -> OrderClientExtensionsResponse:
        """
        Update the client extensions for an order.

        Client extensions are custom metadata that can be attached to orders
        and trades for tracking purposes. Do not use with MT4 accounts.

        Args:
            account_id: Account identifier
            order_specifier: Order ID or @clientID
            client_extensions: Extensions for the order itself
            trade_client_extensions: Extensions for trades created when order fills

        Returns:
            Dictionary containing modification transaction details

        Raises:
            FiveTwentyError: On API errors
            ValueError: If no extensions provided
        """
        if client_extensions is None and trade_client_extensions is None:
            raise ValueError("Must provide at least one set of client extensions")

        body: dict[str, Any] = {}
        if client_extensions is not None:
            body["clientExtensions"] = client_extensions.model_dump(by_alias=True, exclude_none=True, mode="json")
        if trade_client_extensions is not None:
            body["tradeClientExtensions"] = trade_client_extensions.model_dump(by_alias=True, exclude_none=True, mode="json")

        response = await self._client._request(
            "PUT",
            f"/accounts/{account_id}/orders/{order_specifier}/clientExtensions",
            json_data=body,
        )

        data = response.json()
        result: OrderClientExtensionsResponse = {
            "lastTransactionID": data["lastTransactionID"],
        }

        if "orderClientExtensionsModifyTransaction" in data:
            result["orderClientExtensionsModifyTransaction"] = OrderClientExtensionsModifyTransaction.model_validate(data["orderClientExtensionsModifyTransaction"])
        if "relatedTransactionIDs" in data:
            result["relatedTransactionIDs"] = data["relatedTransactionIDs"]

        return result

    async def _get_precision(self, account_id: AccountID, instrument: str) -> int:
        """
        Get display precision for an instrument.

        This is a simple cache for the demo. In production, this would
        be more sophisticated with TTL, etc.
        """
        if instrument in self._precision_cache:
            return self._precision_cache[instrument]

        # Get instruments for this account
        instruments_response = await self._client.accounts.get_account_instruments(account_id, instruments=[instrument])
        instruments_data = instruments_response["instruments"]

        if not instruments_data:
            raise ValueError(f"Instrument {instrument} not found")

        precision: int = instruments_data[0].display_precision
        self._precision_cache[instrument] = precision
        return precision

    def _parse_order(self, order_data: dict[str, Any]) -> Order:  # noqa: PLR0911
        """
        Parse order data into the appropriate Order model based on type discriminator.

        Args:
            order_data: Raw order data from API response

        Returns:
            Parsed Order model (MarketOrder, LimitOrder, StopOrder, etc.)

        Raises:
            ValueError: If order type is unknown
        """
        order_type = order_data.get("type")

        if order_type == "MARKET":
            return MarketOrder.model_validate(order_data)
        if order_type == "LIMIT":
            return LimitOrder.model_validate(order_data)
        if order_type == "STOP":
            return StopOrder.model_validate(order_data)
        if order_type == "MARKET_IF_TOUCHED":
            return MarketIfTouchedOrder.model_validate(order_data)
        if order_type == "TAKE_PROFIT":
            return TakeProfitOrder.model_validate(order_data)
        if order_type == "STOP_LOSS":
            return StopLossOrder.model_validate(order_data)
        if order_type == "GUARANTEED_STOP_LOSS":
            return GuaranteedStopLossOrder.model_validate(order_data)
        if order_type == "TRAILING_STOP_LOSS":
            return TrailingStopLossOrder.model_validate(order_data)
        if order_type == "FIXED_PRICE":
            return FixedPriceOrder.model_validate(order_data)

        raise ValueError(f"Unknown order type: {order_type}")

    def _parse_order_transaction(self, transaction_data: dict[str, Any]) -> OrderCreateTransaction:  # noqa: PLR0911
        """
        Parse transaction data into the appropriate order creation transaction model.

        Args:
            transaction_data: Raw transaction data from API response

        Returns:
            Parsed OrderCreateTransaction model

        Raises:
            ValueError: If transaction type is unknown
        """
        transaction_type = transaction_data.get("type")

        if transaction_type == "MARKET_ORDER":
            return MarketOrderTransaction.model_validate(transaction_data)
        if transaction_type == "LIMIT_ORDER":
            return LimitOrderTransaction.model_validate(transaction_data)
        if transaction_type == "STOP_ORDER":
            return StopOrderTransaction.model_validate(transaction_data)
        if transaction_type == "MARKET_IF_TOUCHED_ORDER":
            return MarketIfTouchedOrderTransaction.model_validate(transaction_data)
        if transaction_type == "TAKE_PROFIT_ORDER":
            return TakeProfitOrderTransaction.model_validate(transaction_data)
        if transaction_type == "STOP_LOSS_ORDER":
            return StopLossOrderTransaction.model_validate(transaction_data)
        if transaction_type == "GUARANTEED_STOP_LOSS_ORDER":
            return GuaranteedStopLossOrderTransaction.model_validate(transaction_data)
        if transaction_type == "TRAILING_STOP_LOSS_ORDER":
            return TrailingStopLossOrderTransaction.model_validate(transaction_data)

        raise ValueError(f"Unknown order transaction type: {transaction_type}")

    def _parse_order_reject_transaction(self, transaction_data: dict[str, Any]) -> OrderRejectTransaction:  # noqa: PLR0911
        """
        Parse transaction data into the appropriate order reject transaction model.

        Args:
            transaction_data: Raw transaction data from API response

        Returns:
            Parsed OrderRejectTransaction model

        Raises:
            ValueError: If transaction type is unknown
        """
        transaction_type = transaction_data.get("type")

        if transaction_type == "MARKET_ORDER_REJECT":
            return MarketOrderRejectTransaction.model_validate(transaction_data)
        if transaction_type == "LIMIT_ORDER_REJECT":
            return LimitOrderRejectTransaction.model_validate(transaction_data)
        if transaction_type == "STOP_ORDER_REJECT":
            return StopOrderRejectTransaction.model_validate(transaction_data)
        if transaction_type == "MARKET_IF_TOUCHED_ORDER_REJECT":
            return MarketIfTouchedOrderRejectTransaction.model_validate(transaction_data)
        if transaction_type == "TAKE_PROFIT_ORDER_REJECT":
            return TakeProfitOrderRejectTransaction.model_validate(transaction_data)
        if transaction_type == "STOP_LOSS_ORDER_REJECT":
            return StopLossOrderRejectTransaction.model_validate(transaction_data)
        if transaction_type == "GUARANTEED_STOP_LOSS_ORDER_REJECT":
            return GuaranteedStopLossOrderRejectTransaction.model_validate(transaction_data)
        if transaction_type == "TRAILING_STOP_LOSS_ORDER_REJECT":
            return TrailingStopLossOrderRejectTransaction.model_validate(transaction_data)

        raise ValueError(f"Unknown order reject transaction type: {transaction_type}")

    # =========================================================================
    # INTENTIONALLY OMITTED CONVENIENCE METHODS
    # =========================================================================
    #
    # The following convenience methods are NOT implemented by design:
    #
    # def post_take_profit_order(...) -> OrderResponse:
    #     """OMITTED: Use post_order(TakeProfitOrderRequest(...)) for post-trade risk management.
    #     PREFERRED: Use take_profit parameter in post_market_order/post_limit_order for OnFill pattern."""
    #
    # def post_stop_loss_order(...) -> OrderResponse:
    #     """OMITTED: Use post_order(StopLossOrderRequest(...)) for post-trade risk management.
    #     PREFERRED: Use stop_loss parameter in post_market_order/post_limit_order for OnFill pattern."""
    #
    # def post_trailing_stop_loss_order(...) -> OrderResponse:
    #     """OMITTED: Use post_order(TrailingStopLossOrderRequest(...)) for post-trade risk management.
    #     PREFERRED: Use trailing_stop_loss parameter in convenience methods for OnFill pattern."""
    #
    # def post_guaranteed_stop_loss_order(...) -> OrderResponse:
    #     """OMITTED: Use post_order(GuaranteedStopLossOrderRequest(...)) for specialized use cases.
    #     These orders require careful premium cost consideration and are not common enough for convenience method."""
    #
    # def post_fixed_price_order(...) -> OrderResponse:
    #     """OMITTED: FixedPriceOrders are administrative/internal only and cannot be created via public API."""
    #
    # DESIGN RATIONALE:
    # ----------------
    # 1. Risk management orders (TP/SL/TSL) are primarily used via OnFill patterns,
    #    not as standalone orders. The convenience methods already support this.
    #
    # 2. Post-trade risk management is an advanced use case requiring explicit
    #    trade IDs and careful parameter construction - users should use post_order().
    #
    # 3. Guaranteed Stop Loss orders have complex premium calculations and requirements
    #    that warrant explicit usage rather than convenience methods.
    #
    # 4. Administrative orders (FixedPrice) are not available for client creation.
    #
    # This design encourages best practices while keeping the API surface clean.
