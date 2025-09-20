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
from typing import TYPE_CHECKING, Any

from .._internal.utils import quantize_price
from ..models import (
    AccountID,
    GuaranteedStopLossOrderRequest,
    InstrumentName,
    LimitOrderRequest,
    MarketIfTouchedOrderRequest,
    MarketOrderRequest,
    OrderResponse,
    StopLossDetails,
    StopLossOrderRequest,
    StopOrderRequest,
    TakeProfitDetails,
    TakeProfitOrderRequest,
    TimeInForce,
    TrailingStopLossOrderRequest,
)

if TYPE_CHECKING:
    from ..client import AsyncClient


class OrderEndpoints:
    """Order management operations."""

    def __init__(self, client: "AsyncClient"):
        self._client = client
        self._precision_cache: dict[str, int] = {}  # Simple cache for demo

    async def post_order(
        self,
        account_id: AccountID,
        order_request: (MarketOrderRequest | LimitOrderRequest | StopOrderRequest | TakeProfitOrderRequest | StopLossOrderRequest | MarketIfTouchedOrderRequest | TrailingStopLossOrderRequest | GuaranteedStopLossOrderRequest),
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

        return OrderResponse.model_validate(response.json())

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
            request.take_profit_on_fill = TakeProfitDetails(price=str(quantized_tp))

        # Add stop loss if specified
        if stop_loss is not None:
            precision = await self._get_precision(account_id, instrument)
            quantized_sl = quantize_price(precision, stop_loss)
            request.stop_loss_on_fill = StopLossDetails(price=str(quantized_sl))

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
            price=str(quantized_price),
            timeInForce=TimeInForce(time_in_force),
        )

        # Add take profit if specified
        if take_profit is not None:
            quantized_tp = quantize_price(precision, take_profit)
            request.take_profit_on_fill = TakeProfitDetails(price=str(quantized_tp))

        # Add stop loss if specified
        if stop_loss is not None:
            quantized_sl = quantize_price(precision, stop_loss)
            request.stop_loss_on_fill = StopLossDetails(price=str(quantized_sl))

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
            price=str(quantized_price),
            timeInForce=TimeInForce(time_in_force),
        )

        # Add price bound if specified
        if price_bound is not None:
            quantized_bound = quantize_price(precision, price_bound)
            request.price_bound = str(quantized_bound)

        # Add take profit if specified
        if take_profit is not None:
            quantized_tp = quantize_price(precision, take_profit)
            request.take_profit_on_fill = TakeProfitDetails(price=str(quantized_tp))

        # Add stop loss if specified
        if stop_loss is not None:
            quantized_sl = quantize_price(precision, stop_loss)
            request.stop_loss_on_fill = StopLossDetails(price=str(quantized_sl))

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
            price=str(quantized_price),
            timeInForce=TimeInForce(time_in_force),
        )

        # Add price bound if specified
        if price_bound is not None:
            quantized_bound = quantize_price(precision, price_bound)
            request.price_bound = str(quantized_bound)

        # Add take profit if specified
        if take_profit is not None:
            quantized_tp = quantize_price(precision, take_profit)
            request.take_profit_on_fill = TakeProfitDetails(price=str(quantized_tp))

        # Add stop loss if specified
        if stop_loss is not None:
            quantized_sl = quantize_price(precision, stop_loss)
            request.stop_loss_on_fill = StopLossDetails(price=str(quantized_sl))

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
    ) -> list[dict[str, Any]]:
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
            List of orders

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
            params["instrument"] = instrument
        if before_id:
            params["beforeID"] = before_id

        response = await self._client._request(
            "GET",
            f"/accounts/{account_id}/orders",
            params=params,
        )
        data = response.json()

        return data.get("orders", [])  # type: ignore[no-any-return]

    async def get_order(self, account_id: AccountID, order_specifier: str) -> dict[str, Any]:
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
            "order": data["order"],
            "lastTransactionID": data["lastTransactionID"],
        }

    async def cancel_order(
        self,
        account_id: AccountID,
        order_specifier: str,
        *,
        timeout: float | None = None,
        client_request_id: str | None = None,
    ) -> dict[str, Any]:
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

        return response.json()  # type: ignore[no-any-return]

    async def get_pending_orders(
        self,
        account_id: AccountID,
    ) -> dict[str, Any]:
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

        return response.json()  # type: ignore[no-any-return]

    async def put_order(
        self,
        account_id: AccountID,
        order_specifier: str,
        order_request: dict[str, Any],
        *,
        client_request_id: str | None = None,
    ) -> dict[str, Any]:
        """
        Replace an existing order with a new order.

        This operation atomically cancels the existing order and creates
        a replacement order. The OrderSpecifier can be either an Order ID
        or a client-provided identifier using @clientID format.

        Args:
            account_id: Account identifier
            order_specifier: Order ID or @clientID to replace
            order_request: New order specification (OrderRequest object as dict)
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

        response = await self._client._request(
            "PUT",
            f"/accounts/{account_id}/orders/{order_specifier}",
            json_data={"order": order_request},
            headers=headers,
        )

        return response.json()  # type: ignore[no-any-return]

    async def put_order_client_extensions(
        self,
        account_id: AccountID,
        order_specifier: str,
        *,
        client_extensions: dict[str, Any] | None = None,
        trade_client_extensions: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
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
            body["clientExtensions"] = client_extensions
        if trade_client_extensions is not None:
            body["tradeClientExtensions"] = trade_client_extensions

        response = await self._client._request(
            "PUT",
            f"/accounts/{account_id}/orders/{order_specifier}/clientExtensions",
            json_data=body,
        )

        return response.json()  # type: ignore[no-any-return]

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
