"""Tests for transaction-related models."""

from decimal import Decimal
from typing import Any

import pytest

from fivetwenty.models import (
    AcceptDatetimeFormat,
    ClientConfigureRejectTransaction,
    ClientConfigureTransaction,
    CloseTransaction,
    CreateTransaction,
    Currency,
    DailyFinancingTransaction,
    DividendAdjustmentTransaction,
    FixedPriceOrderTransaction,
    FundingReason,
    GuaranteedStopLossOrderRejectTransaction,
    GuaranteedStopLossOrderTransaction,
    InstrumentName,
    LimitOrderRejectTransaction,
    LimitOrderTransaction,
    LiquidityRegenerationSchedule,
    LiquidityRegenerationScheduleStep,
    MarginCallEnterTransaction,
    MarginCallExitTransaction,
    MarginCallExtendTransaction,
    MarketIfTouchedOrderRejectTransaction,
    MarketIfTouchedOrderTransaction,
    MarketOrderRejectTransaction,
    MarketOrderTransaction,
    OpenTradeDividendAdjustment,
    OpenTradeFinancing,
    OrderCancelRejectTransaction,
    OrderCancelTransaction,
    OrderClientExtensionsModifyTransaction,
    OrderFillTransaction,
    OrderPositionFill,
    PositionFinancing,
    ReopenTransaction,
    ResetResettablePLTransaction,
    StopLossOrderRejectTransaction,
    StopLossOrderTransaction,
    StopOrderRejectTransaction,
    StopOrderTransaction,
    TakeProfitOrderRejectTransaction,
    TakeProfitOrderTransaction,
    TimeInForce,
    TradeClientExtensionsModifyTransaction,
    TradeOpen,
    TradeReduce,
    TrailingStopLossOrderRejectTransaction,
    TrailingStopLossOrderTransaction,
    Transaction,
    TransactionFilter,
    TransactionHeartbeat,
    TransactionIDRange,
    TransactionQueryFilter,
    TransactionRejectReason,
    TransactionType,
    TransferFundsRejectTransaction,
    TransferFundsTransaction,
)
from fivetwenty.models.transactions import FullPrice


def _txn_base(txn_id: str, txn_type: str) -> dict[str, Any]:
    """Build the common OANDA transaction envelope fields."""
    return {
        "id": txn_id,
        "time": "2024-01-15T12:00:00.000000000Z",
        "userID": 123456,
        "accountID": "101-001-123456-001",
        "batchID": txn_id,
        "type": txn_type,
    }


class TestPhase4TransactionModels:
    """Test Phase 4: Transaction & audit trail models."""

    def test_transaction_type_enum(self) -> None:
        """Test TransactionType enum values."""
        # Account Management
        assert TransactionType.CREATE == "CREATE"
        assert TransactionType.CLOSE == "CLOSE"
        assert TransactionType.CLIENT_CONFIGURE == "CLIENT_CONFIGURE"

        # Order Creation
        assert TransactionType.MARKET_ORDER == "MARKET_ORDER"
        assert TransactionType.LIMIT_ORDER == "LIMIT_ORDER"
        assert TransactionType.STOP_ORDER == "STOP_ORDER"

        # Order Management
        assert TransactionType.ORDER_FILL == "ORDER_FILL"
        assert TransactionType.ORDER_CANCEL == "ORDER_CANCEL"

        # Financial Operations
        assert TransactionType.DAILY_FINANCING == "DAILY_FINANCING"
        assert TransactionType.DIVIDEND_ADJUSTMENT == "DIVIDEND_ADJUSTMENT"

    def test_accept_datetime_format_enum(self) -> None:
        """Test AcceptDatetimeFormat enum values."""
        assert AcceptDatetimeFormat.UNIX == "UNIX"
        assert AcceptDatetimeFormat.RFC3339 == "RFC3339"

    def test_transaction_filter_enum(self) -> None:
        """Test official TransactionFilter enum values."""
        assert TransactionFilter.ORDER == "ORDER"
        assert TransactionFilter.FUNDING == "FUNDING"
        assert TransactionFilter.ORDER_FILL == "ORDER_FILL"
        assert TransactionFilter.ONE_CANCELS_ALL_ORDER == "ONE_CANCELS_ALL_ORDER"

    def test_transaction_reject_reason_enum(self) -> None:
        """Test TransactionRejectReason enum values."""
        assert TransactionRejectReason.INTERNAL_SERVER_ERROR == "INTERNAL_SERVER_ERROR"
        assert TransactionRejectReason.INSUFFICIENT_MARGIN == "INSUFFICIENT_MARGIN"
        assert TransactionRejectReason.ACCOUNT_NOT_ACTIVE == "ACCOUNT_NOT_ACTIVE"

    def test_funding_reason_enum(self) -> None:
        """Test FundingReason enum values."""
        assert FundingReason.CLIENT_FUNDING == "CLIENT_FUNDING"
        assert FundingReason.ACCOUNT_TRANSFER == "ACCOUNT_TRANSFER"
        assert FundingReason.ADJUSTMENT == "ADJUSTMENT"

    def test_transaction_base_model(self) -> None:
        """Test base Transaction model."""
        transaction_data = {
            "id": "12345",
            "time": "2024-01-15T12:00:00.000000000Z",
            "userID": 123456,
            "accountID": "101-001-123456-001",
            "batchID": "12345",
            "requestID": "req-001",
            "type": "MARKET_ORDER",
        }

        transaction = Transaction(**transaction_data)
        assert transaction.id == "12345"
        assert transaction.user_id == 123456
        assert transaction.account_id == "101-001-123456-001"
        assert transaction.batch_id == "12345"
        assert transaction.request_id == "req-001"
        assert transaction.type == TransactionType.MARKET_ORDER

    def test_transaction_aliases(self) -> None:
        """Test Transaction model camelCase aliases."""
        api_data = {
            "id": "12345",
            "time": "2024-01-15T12:00:00.000000000Z",
            "userID": 123456,
            "accountID": "101-001-123456-001",
            "batchID": "12345",
            "requestID": "req-001",
            "type": "ORDER_FILL",
        }

        transaction = Transaction(**api_data)
        transaction_back_to_api = transaction.model_dump(by_alias=True, exclude_none=True)
        assert transaction_back_to_api["userID"] == 123456
        assert transaction_back_to_api["accountID"] == "101-001-123456-001"
        assert transaction_back_to_api["batchID"] == "12345"
        assert transaction_back_to_api["requestID"] == "req-001"

    def test_order_fill_transaction(self) -> None:
        """Test OrderFillTransaction model."""
        fill_data = {
            "id": "12346",
            "time": "2024-01-15T12:00:01.000000000Z",
            "userID": 123456,
            "accountID": "101-001-123456-001",
            "batchID": "12346",
            "type": "ORDER_FILL",
            "orderID": "order-123",
            "clientOrderID": "client-order-123",
            "instrument": "EUR_USD",
            "units": "10000",
            "price": "1.0950",
            "pl": "15.25",
            "financing": "0.50",
            "commission": "2.50",
            "accountBalance": "10000.00",
        }

        fill = OrderFillTransaction(**fill_data)
        assert fill.order_id == "order-123"
        assert fill.client_order_id == "client-order-123"
        assert fill.instrument == InstrumentName.EUR_USD
        assert fill.units == Decimal("10000")  # Field is now Decimal
        assert fill.price == Decimal("1.0950")  # PriceValue is now Decimal
        assert fill.pl == Decimal("15.25")  # Field is now Decimal
        assert fill.commission == Decimal("2.50")  # Field is now Decimal

    def test_order_fill_transaction_aliases(self) -> None:
        """Test OrderFillTransaction camelCase aliases."""
        api_data = {
            "id": "12346",
            "time": "2024-01-15T12:00:01.000000000Z",
            "userID": 123456,
            "accountID": "101-001-123456-001",
            "batchID": "12346",
            "type": "ORDER_FILL",
            "orderID": "order-123",
            "clientOrderID": "client-order-123",
            "instrument": "EUR_USD",
            "units": "10000",
            "fullVWAP": "1.0950",
            "fullPrice": {
                "instrument": "EUR_USD",
                "time": "2024-01-15T12:00:01.000000000Z",
                "tradeable": True,
                "closeoutBid": "1.0945",
                "closeoutAsk": "1.0955",
                "liquidity": 10000000,
            },
            "gainQuoteHomeConversionFactor": "1.0",
            "lossQuoteHomeConversionFactor": "1.0",
            "accountBalance": "10000.00",
            "halfSpreadCost": "0.25",
        }

        fill = OrderFillTransaction(**api_data)
        fill_back_to_api = fill.model_dump(by_alias=True, exclude_none=True)
        assert fill_back_to_api["orderID"] == "order-123"
        assert fill_back_to_api["clientOrderID"] == "client-order-123"
        assert fill_back_to_api["fullVWAP"] == "1.0950"
        assert fill_back_to_api["fullPrice"]["closeoutBid"] == "1.0945"
        assert fill_back_to_api["fullPrice"]["closeoutAsk"] == "1.0955"
        assert fill_back_to_api["accountBalance"] == "10000.00"

    def test_order_fill_transaction_partial_full_price(self) -> None:
        """Test transaction-embedded fullPrice payloads without ClientPrice identity fields."""
        api_data = {
            "id": "12346",
            "time": "2024-01-15T12:00:01.000000000Z",
            "userID": 123456,
            "accountID": "101-001-123456-001",
            "batchID": "12346",
            "type": "ORDER_FILL",
            "orderID": "order-123",
            "instrument": "EUR_USD",
            "units": "10000",
            "fullPrice": {
                "closeoutBid": "1.0945",
                "closeoutAsk": "1.0955",
                "bids": [{"price": "1.0945", "liquidity": "10000000"}],
                "asks": [{"price": "1.0955", "liquidity": "10000000"}],
            },
        }

        fill = OrderFillTransaction(**api_data)

        assert fill.full_price is not None
        assert fill.full_price.instrument is None
        assert fill.full_price.time is None
        assert fill.full_price.tradeable is None
        assert fill.full_price.closeout_bid == Decimal("1.0945")
        assert fill.full_price.bids[0].liquidity == Decimal("10000000")

    def test_order_cancel_transaction(self) -> None:
        """Test OrderCancelTransaction model."""
        cancel_data = {
            "id": "12347",
            "time": "2024-01-15T12:00:02.000000000Z",
            "userID": 123456,
            "accountID": "101-001-123456-001",
            "batchID": "12347",
            "type": "ORDER_CANCEL",
            "orderID": "order-124",
            "clientOrderID": "client-order-124",
            "reason": "CLIENT_REQUEST",
            "replacedByOrderID": "order-125",
        }

        cancel = OrderCancelTransaction(**cancel_data)
        assert cancel.order_id == "order-124"
        assert cancel.client_order_id == "client-order-124"
        assert cancel.reason == "CLIENT_REQUEST"
        assert cancel.replaced_by_order_id == "order-125"

    def test_market_order_transaction(self) -> None:
        """Test MarketOrderTransaction model."""
        market_data = {
            "id": "12348",
            "time": "2024-01-15T12:00:03.000000000Z",
            "userID": 123456,
            "accountID": "101-001-123456-001",
            "batchID": "12348",
            "type": "MARKET_ORDER",
            "instrument": "GBP_USD",
            "units": "5000",
            "timeInForce": "FOK",
            "positionFill": "DEFAULT",
            "priceBound": "1.2500",
            "reason": "CLIENT_ORDER",
        }

        market = MarketOrderTransaction(**market_data)
        assert market.instrument == InstrumentName.GBP_USD
        assert market.units == Decimal("5000")  # Field is now Decimal
        assert market.time_in_force == TimeInForce.FOK
        assert market.position_fill == OrderPositionFill.DEFAULT
        assert market.price_bound == Decimal("1.2500")

    def test_market_order_transaction_aliases(self) -> None:
        """Test MarketOrderTransaction camelCase aliases."""
        api_data = {
            "id": "12348",
            "time": "2024-01-15T12:00:03.000000000Z",
            "userID": 123456,
            "accountID": "101-001-123456-001",
            "batchID": "12348",
            "type": "MARKET_ORDER",
            "instrument": "GBP_USD",
            "units": "5000",
            "timeInForce": "FOK",
            "positionFill": "DEFAULT",
            "priceBound": "1.2500",
            "clientExtensions": {"id": "client-123", "comment": "Test order"},
            "takeProfitOnFill": {"price": "1.2600"},
            "stopLossOnFill": {"price": "1.2400"},
            "trailingStopLossOnFill": {"distance": "0.0050"},
            "tradeClientExtensions": {"id": "trade-123"},
        }

        market = MarketOrderTransaction(**api_data)
        market_back_to_api = market.model_dump(by_alias=True, exclude_none=True)
        assert market_back_to_api["timeInForce"] == "FOK"
        assert market_back_to_api["positionFill"] == "DEFAULT"
        assert market_back_to_api["priceBound"] == "1.2500"
        assert market_back_to_api["clientExtensions"]["id"] == "client-123"
        assert market_back_to_api["takeProfitOnFill"]["price"] == "1.2600"

    def test_transaction_query_filter(self) -> None:
        """Test TransactionQueryFilter model."""
        filter_data = {
            "from": "12340",
            "to": "12350",
            "pageSize": 100,
            "type": ["ORDER_FILL", "ORDER_CANCEL"],
        }

        filter_obj = TransactionQueryFilter(**filter_data)
        assert filter_obj.from_ == "12340"
        assert filter_obj.to == "12350"
        assert filter_obj.page_size == 100
        assert filter_obj.type_filter == [TransactionType.ORDER_FILL, TransactionType.ORDER_CANCEL]

    def test_transaction_query_filter_aliases(self) -> None:
        """Test TransactionQueryFilter camelCase aliases."""
        api_data = {
            "from": "12340",
            "to": "12350",
            "pageSize": 100,
            "type": ["MARKET_ORDER", "LIMIT_ORDER"],
        }

        filter_obj = TransactionQueryFilter(**api_data)
        filter_back_to_api = filter_obj.model_dump(by_alias=True, exclude_none=True)
        assert filter_back_to_api["from"] == "12340"
        assert filter_back_to_api["pageSize"] == 100
        assert filter_back_to_api["type"] == ["MARKET_ORDER", "LIMIT_ORDER"]

    def test_transaction_id_range(self) -> None:
        """Test TransactionIDRange model."""
        range_data = {"from": "12340", "to": "12350"}

        range_obj = TransactionIDRange(**range_data)
        assert range_obj.from_ == "12340"
        assert range_obj.to == "12350"

    def test_transaction_id_range_aliases(self) -> None:
        """Test TransactionIDRange camelCase aliases."""
        api_data = {"from": "12340", "to": "12350"}

        range_obj = TransactionIDRange(**api_data)
        range_back_to_api = range_obj.model_dump(by_alias=True, exclude_none=True)
        assert range_back_to_api["from"] == "12340"
        assert range_back_to_api["to"] == "12350"


class TestPhase4AliasTests:
    """Test Phase 4 model alias functionality for OANDA API compatibility."""

    def test_transaction_roundtrip_validation(self) -> None:
        """Test Transaction model roundtrip with API data."""
        api_data = {
            "id": "12345",
            "time": "2024-01-15T12:00:00.000000000Z",
            "userID": 123456,
            "accountID": "101-001-123456-001",
            "batchID": "12345",
            "requestID": "req-001",
            "type": "ORDER_FILL",
        }

        transaction = Transaction(**api_data)
        transaction_back_to_api = transaction.model_dump(by_alias=True, exclude_none=True)

        # Perfect round-trip
        transaction_roundtrip = Transaction(**transaction_back_to_api)
        assert transaction_roundtrip.user_id == transaction.user_id
        assert transaction_roundtrip.account_id == transaction.account_id
        assert transaction_roundtrip.batch_id == transaction.batch_id
        assert transaction_roundtrip.request_id == transaction.request_id

    def test_order_fill_transaction_roundtrip_validation(self) -> None:
        """Test OrderFillTransaction model roundtrip with API data."""
        api_data = {
            "id": "12346",
            "time": "2024-01-15T12:00:01.000000000Z",
            "userID": 123456,
            "accountID": "101-001-123456-001",
            "batchID": "12346",
            "type": "ORDER_FILL",
            "orderID": "order-123",
            "clientOrderID": "client-order-123",
            "instrument": "EUR_USD",
            "units": "10000",
            "gainQuoteHomeConversionFactor": "1.0",
            "lossQuoteHomeConversionFactor": "1.0",
            "fullVWAP": "1.0950",
            "fullPrice": {
                "instrument": "EUR_USD",
                "time": "2024-01-15T12:00:01.000000000Z",
                "tradeable": True,
                "closeoutBid": "1.0945",
                "closeoutAsk": "1.0955",
                "liquidity": 10000000,
            },
            "accountBalance": "10000.00",
            "halfSpreadCost": "0.25",
        }

        fill = OrderFillTransaction(**api_data)
        fill_back_to_api = fill.model_dump(by_alias=True, exclude_none=True)

        # Perfect round-trip
        fill_roundtrip = OrderFillTransaction(**fill_back_to_api)
        assert fill_roundtrip.order_id == fill.order_id
        assert fill_roundtrip.client_order_id == fill.client_order_id
        assert fill_roundtrip.gain_quote_home_conversion_factor == fill.gain_quote_home_conversion_factor
        assert fill_roundtrip.full_vwap == fill.full_vwap

    def test_market_order_transaction_roundtrip_validation(self) -> None:
        """Test MarketOrderTransaction model roundtrip with API data."""
        api_data = {
            "id": "12348",
            "time": "2024-01-15T12:00:03.000000000Z",
            "userID": 123456,
            "accountID": "101-001-123456-001",
            "batchID": "12348",
            "type": "MARKET_ORDER",
            "instrument": "GBP_USD",
            "units": "5000",
            "timeInForce": "FOK",
            "positionFill": "DEFAULT",
            "priceBound": "1.2500",
            "tradeClose": {"tradeID": "trade-123", "units": "5000"},
            "longPositionCloseout": {"instrument": "GBP_USD", "units": "ALL"},
            "shortPositionCloseout": {"instrument": "GBP_USD", "units": "ALL"},
            "marginCloseout": {"reason": "MARGIN_CHECK_VIOLATION"},
            "delayedTradeClose": {"tradeID": "trade-124", "sourceTransactionID": "12347"},
            "clientExtensions": {"id": "client-123", "tag": "test", "comment": "Test order"},
            "tradeClientExtensions": {"id": "trade-client-123"},
        }

        market = MarketOrderTransaction(**api_data)
        market_back_to_api = market.model_dump(by_alias=True, exclude_none=True)

        # Perfect round-trip
        market_roundtrip = MarketOrderTransaction(**market_back_to_api)
        assert market_roundtrip.time_in_force == market.time_in_force
        assert market_roundtrip.position_fill == market.position_fill
        assert market_roundtrip.price_bound == market.price_bound
        assert market_roundtrip.trade_close == market.trade_close
        assert market_roundtrip.client_extensions == market.client_extensions


# (class, OANDA-shaped payload, expected attribute values) for every
# order create/reject transaction pair not otherwise covered by name.
ORDER_TRANSACTION_CASES = [
    pytest.param(
        LimitOrderTransaction,
        {
            **_txn_base("21", "LIMIT_ORDER"),
            "instrument": "EUR_USD",
            "units": "100",
            "price": "1.1000",
            "timeInForce": "GTC",
            "positionFill": "DEFAULT",
            "triggerCondition": "DEFAULT",
            "reason": "CLIENT_ORDER",
            "replacesOrderID": "20",
        },
        {"instrument": "EUR_USD", "units": Decimal("100"), "price": Decimal("1.1000"), "reason": "CLIENT_ORDER", "replaces_order_id": "20"},
        id="limit-order",
    ),
    pytest.param(
        LimitOrderRejectTransaction,
        {
            **_txn_base("22", "LIMIT_ORDER_REJECT"),
            "instrument": "EUR_USD",
            "units": "100",
            "price": "1.1000",
            "timeInForce": "GTC",
            "intendedReplacesOrderID": "20",
            "rejectReason": "PRICE_INVALID",
        },
        {"instrument": "EUR_USD", "price": Decimal("1.1000"), "intended_replaces_order_id": "20", "reject_reason": "PRICE_INVALID"},
        id="limit-order-reject",
    ),
    pytest.param(
        StopOrderTransaction,
        {
            **_txn_base("23", "STOP_ORDER"),
            "instrument": "GBP_USD",
            "units": "-500",
            "price": "1.2400",
            "priceBound": "1.2390",
            "timeInForce": "GTC",
            "reason": "CLIENT_ORDER",
        },
        {"instrument": "GBP_USD", "units": Decimal("-500"), "price": Decimal("1.2400"), "price_bound": Decimal("1.2390"), "reason": "CLIENT_ORDER"},
        id="stop-order",
    ),
    pytest.param(
        StopOrderRejectTransaction,
        {
            **_txn_base("24", "STOP_ORDER_REJECT"),
            "instrument": "GBP_USD",
            "units": "-500",
            "price": "1.2400",
            "rejectReason": "PRICE_PRECISION_EXCEEDED",
        },
        {"instrument": "GBP_USD", "price": Decimal("1.2400"), "reject_reason": "PRICE_PRECISION_EXCEEDED"},
        id="stop-order-reject",
    ),
    pytest.param(
        MarketIfTouchedOrderTransaction,
        {
            **_txn_base("25", "MARKET_IF_TOUCHED_ORDER"),
            "instrument": "USD_JPY",
            "units": "1000",
            "price": "145.500",
            "priceBound": "145.600",
            "reason": "CLIENT_ORDER",
        },
        {"instrument": "USD_JPY", "units": Decimal("1000"), "price": Decimal("145.500"), "price_bound": Decimal("145.600"), "reason": "CLIENT_ORDER"},
        id="market-if-touched-order",
    ),
    pytest.param(
        MarketIfTouchedOrderRejectTransaction,
        {
            **_txn_base("26", "MARKET_IF_TOUCHED_ORDER_REJECT"),
            "instrument": "USD_JPY",
            "units": "1000",
            "price": "145.500",
            "rejectReason": "PRICE_BOUND_INVALID",
        },
        {"instrument": "USD_JPY", "price": Decimal("145.500"), "reject_reason": "PRICE_BOUND_INVALID"},
        id="market-if-touched-order-reject",
    ),
    pytest.param(
        TakeProfitOrderTransaction,
        {
            **_txn_base("27", "TAKE_PROFIT_ORDER"),
            "tradeID": "18",
            "clientTradeID": "my-trade-18",
            "price": "1.1500",
            "reason": "ON_FILL",
            "orderFillTransactionID": "19",
        },
        {"trade_id": "18", "client_trade_id": "my-trade-18", "price": Decimal("1.1500"), "reason": "ON_FILL", "order_fill_transaction_id": "19"},
        id="take-profit-order",
    ),
    pytest.param(
        TakeProfitOrderRejectTransaction,
        {
            **_txn_base("28", "TAKE_PROFIT_ORDER_REJECT"),
            "tradeID": "18",
            "price": "1.1500",
            "rejectReason": "TRADE_DOESNT_EXIST",
        },
        {"trade_id": "18", "price": Decimal("1.1500"), "reject_reason": "TRADE_DOESNT_EXIST"},
        id="take-profit-order-reject",
    ),
    pytest.param(
        StopLossOrderTransaction,
        {
            **_txn_base("29", "STOP_LOSS_ORDER"),
            "tradeID": "18",
            "price": "1.0500",
            "guaranteed": False,
            "reason": "ON_FILL",
        },
        {"trade_id": "18", "price": Decimal("1.0500"), "guaranteed": False, "reason": "ON_FILL"},
        id="stop-loss-order",
    ),
    pytest.param(
        StopLossOrderRejectTransaction,
        {
            **_txn_base("30", "STOP_LOSS_ORDER_REJECT"),
            "tradeID": "18",
            "price": "1.0500",
            "rejectReason": "PRICE_DISTANCE_INVALID",
        },
        {"trade_id": "18", "price": Decimal("1.0500"), "reject_reason": "PRICE_DISTANCE_INVALID"},
        id="stop-loss-order-reject",
    ),
    pytest.param(
        TrailingStopLossOrderTransaction,
        {
            **_txn_base("31", "TRAILING_STOP_LOSS_ORDER"),
            "tradeID": "18",
            "distance": "0.0050",
            "reason": "CLIENT_ORDER",
        },
        {"trade_id": "18", "distance": Decimal("0.0050"), "reason": "CLIENT_ORDER"},
        id="trailing-stop-loss-order",
    ),
    pytest.param(
        TrailingStopLossOrderRejectTransaction,
        {
            **_txn_base("32", "TRAILING_STOP_LOSS_ORDER_REJECT"),
            "tradeID": "18",
            "distance": "0.0050",
            "rejectReason": "PRICE_DISTANCE_MAXIMUM_EXCEEDED",
        },
        {"trade_id": "18", "distance": Decimal("0.0050"), "reject_reason": "PRICE_DISTANCE_MAXIMUM_EXCEEDED"},
        id="trailing-stop-loss-order-reject",
    ),
    pytest.param(
        GuaranteedStopLossOrderTransaction,
        {
            **_txn_base("33", "GUARANTEED_STOP_LOSS_ORDER"),
            "tradeID": "18",
            "price": "1.0400",
            "guaranteedExecutionPremium": "0.50",
            "reason": "ON_FILL",
        },
        {"trade_id": "18", "price": Decimal("1.0400"), "guaranteed_execution_premium": Decimal("0.50"), "reason": "ON_FILL"},
        id="guaranteed-stop-loss-order",
    ),
    pytest.param(
        GuaranteedStopLossOrderRejectTransaction,
        {
            **_txn_base("34", "GUARANTEED_STOP_LOSS_ORDER_REJECT"),
            "tradeID": "18",
            "price": "1.0400",
            "rejectReason": "INSUFFICIENT_MARGIN",
        },
        {"trade_id": "18", "price": Decimal("1.0400"), "reject_reason": "INSUFFICIENT_MARGIN"},
        id="guaranteed-stop-loss-order-reject",
    ),
]


class TestOrderTransactionFamilies:
    """Named coverage for the order create/reject transaction pairs."""

    @pytest.mark.parametrize(("model_cls", "payload", "expected"), ORDER_TRANSACTION_CASES)
    def test_order_transaction(self, model_cls: type[Transaction], payload: dict[str, Any], expected: dict[str, Any]) -> None:
        """Validate an OANDA-shaped payload, alias mapping, Decimal typing and round-trip."""
        txn = model_cls(**payload)

        # Envelope aliases map field-by-field
        assert txn.user_id == payload["userID"]
        assert txn.account_id == payload["accountID"]
        assert txn.batch_id == payload["batchID"]
        assert txn.type == payload["type"]

        # Class-specific fields
        for attr, value in expected.items():
            assert getattr(txn, attr) == value, f"{model_cls.__name__}.{attr}"

        # Monetary fields must be Decimal, never float
        for attr in ("units", "price", "distance", "price_bound", "guaranteed_execution_premium"):
            value = getattr(txn, attr, None)
            if value is not None:
                assert isinstance(value, Decimal), f"{model_cls.__name__}.{attr} should be Decimal"

        # Round-trip through camelCase JSON
        dumped = txn.model_dump(by_alias=True, exclude_none=True)
        assert dumped["type"] == payload["type"]
        assert model_cls(**dumped) == txn


class TestMarketOrderRejectTransaction:
    """Named coverage for MarketOrderRejectTransaction."""

    def test_trade_close_shaped_reject_without_instrument_or_units(self) -> None:
        """A trade-close reject observed live has no top-level instrument/units (fixed bug)."""
        payload = {
            "id": "24046",
            "accountID": "101-001-27189766-001",
            "userID": 27189766,
            "batchID": "24046",
            "time": "2026-05-05T05:13:28.963445047Z",
            "type": "MARKET_ORDER_REJECT",
            "rejectReason": "TRADE_DOESNT_EXIST",
            "timeInForce": "FOK",
            "positionFill": "REDUCE_ONLY",
            "reason": "TRADE_CLOSE",
            "tradeClose": {"units": "ALL", "tradeID": "24043"},
        }

        reject = MarketOrderRejectTransaction(**payload)
        assert reject.instrument is None
        assert reject.units is None
        assert reject.type == TransactionType.MARKET_ORDER_REJECT
        assert reject.reject_reason == TransactionRejectReason.TRADE_DOESNT_EXIST
        assert reject.time_in_force == TimeInForce.FOK
        assert reject.position_fill == OrderPositionFill.REDUCE_ONLY
        assert reject.reason == "TRADE_CLOSE"
        assert reject.trade_close is not None
        assert reject.trade_close.trade_id == payload["tradeClose"]["tradeID"]
        assert reject.trade_close.units == "ALL"

        dumped = reject.model_dump(by_alias=True, exclude_none=True)
        assert "instrument" not in dumped
        assert "units" not in dumped
        assert dumped["rejectReason"] == "TRADE_DOESNT_EXIST"
        assert MarketOrderRejectTransaction(**dumped) == reject

    def test_client_order_shaped_reject(self) -> None:
        """A client-order reject carries top-level instrument/units as Decimal."""
        payload = {
            **_txn_base("40", "MARKET_ORDER_REJECT"),
            "instrument": "EUR_USD",
            "units": "10000",
            "timeInForce": "FOK",
            "positionFill": "DEFAULT",
            "reason": "CLIENT_ORDER",
            "rejectReason": "INSUFFICIENT_MARGIN",
        }

        reject = MarketOrderRejectTransaction(**payload)
        assert reject.instrument == InstrumentName.EUR_USD
        assert reject.units == Decimal("10000")
        assert isinstance(reject.units, Decimal)
        assert reject.reject_reason == "INSUFFICIENT_MARGIN"
        assert MarketOrderRejectTransaction(**reject.model_dump(by_alias=True, exclude_none=True)) == reject


class TestAccountLifecycleTransactions:
    """Named coverage for account management transactions."""

    def test_create_transaction(self) -> None:
        """Test CreateTransaction aliases and fields."""
        payload = {
            **_txn_base("1", "CREATE"),
            "divisionID": 4,
            "siteID": 1,
            "accountUserID": 123456,
            "accountNumber": 1,
            "homeCurrency": "USD",
        }

        create = CreateTransaction(**payload)
        assert create.division_id == payload["divisionID"]
        assert create.site_id == payload["siteID"]
        assert create.account_user_id == payload["accountUserID"]
        assert create.account_number == payload["accountNumber"]
        assert create.home_currency == Currency.USD
        assert CreateTransaction(**create.model_dump(by_alias=True, exclude_none=True)) == create

    @pytest.mark.parametrize(
        ("model_cls", "txn_type"),
        [
            pytest.param(CloseTransaction, "CLOSE", id="close"),
            pytest.param(ReopenTransaction, "REOPEN", id="reopen"),
            pytest.param(ResetResettablePLTransaction, "RESET_RESETTABLE_PL", id="reset-resettable-pl"),
            pytest.param(MarginCallEnterTransaction, "MARGIN_CALL_ENTER", id="margin-call-enter"),
            pytest.param(MarginCallExitTransaction, "MARGIN_CALL_EXIT", id="margin-call-exit"),
        ],
    )
    def test_marker_transactions(self, model_cls: type[Transaction], txn_type: str) -> None:
        """Envelope-only transactions validate and round-trip."""
        payload = _txn_base("50", txn_type)
        txn = model_cls(**payload)
        assert txn.type == txn_type
        assert txn.account_id == payload["accountID"]
        assert txn.batch_id == payload["batchID"]
        assert model_cls(**txn.model_dump(by_alias=True, exclude_none=True)) == txn

    def test_margin_call_extend_transaction(self) -> None:
        """Test MarginCallExtendTransaction extensionNumber alias."""
        payload = {**_txn_base("51", "MARGIN_CALL_EXTEND"), "extensionNumber": 2}
        extend = MarginCallExtendTransaction(**payload)
        assert extend.extension_number == payload["extensionNumber"]
        assert extend.type == TransactionType.MARGIN_CALL_EXTEND
        assert MarginCallExtendTransaction(**extend.model_dump(by_alias=True, exclude_none=True)) == extend

    def test_client_configure_transaction(self) -> None:
        """Test ClientConfigureTransaction fields and Decimal margin rate."""
        payload = {**_txn_base("52", "CLIENT_CONFIGURE"), "alias": "primary", "marginRate": "0.02"}
        configure = ClientConfigureTransaction(**payload)
        assert configure.alias == "primary"
        assert configure.margin_rate == Decimal("0.02")
        assert isinstance(configure.margin_rate, Decimal)
        assert ClientConfigureTransaction(**configure.model_dump(by_alias=True, exclude_none=True)) == configure

    def test_client_configure_reject_transaction(self) -> None:
        """Test ClientConfigureRejectTransaction rejectReason alias."""
        payload = {**_txn_base("53", "CLIENT_CONFIGURE_REJECT"), "alias": "primary", "marginRate": "0.02", "rejectReason": "INTERNAL_SERVER_ERROR"}
        reject = ClientConfigureRejectTransaction(**payload)
        assert reject.margin_rate == Decimal("0.02")
        assert reject.reject_reason == TransactionRejectReason.INTERNAL_SERVER_ERROR
        assert ClientConfigureRejectTransaction(**reject.model_dump(by_alias=True, exclude_none=True)) == reject


class TestFundingTransactions:
    """Named coverage for funding transactions."""

    def test_transfer_funds_transaction(self) -> None:
        """Test TransferFundsTransaction aliases and Decimal amounts."""
        payload = {
            **_txn_base("60", "TRANSFER_FUNDS"),
            "amount": "1000.00",
            "fundingReason": "CLIENT_FUNDING",
            "comment": "Initial deposit",
            "accountBalance": "11000.00",
        }

        transfer = TransferFundsTransaction(**payload)
        assert transfer.amount == Decimal("1000.00")
        assert isinstance(transfer.amount, Decimal)
        assert transfer.funding_reason == FundingReason.CLIENT_FUNDING
        assert transfer.account_balance == Decimal("11000.00")
        assert transfer.comment == "Initial deposit"
        assert TransferFundsTransaction(**transfer.model_dump(by_alias=True, exclude_none=True)) == transfer

    def test_transfer_funds_reject_transaction(self) -> None:
        """Test TransferFundsRejectTransaction rejectReason alias."""
        payload = {
            **_txn_base("61", "TRANSFER_FUNDS_REJECT"),
            "amount": "-500.00",
            "fundingReason": "ADJUSTMENT",
            "rejectReason": "ACCOUNT_DEPOSIT_LOCKED",
        }

        reject = TransferFundsRejectTransaction(**payload)
        assert reject.amount == Decimal("-500.00")
        assert isinstance(reject.amount, Decimal)
        assert reject.funding_reason == FundingReason.ADJUSTMENT
        assert reject.reject_reason == "ACCOUNT_DEPOSIT_LOCKED"
        assert TransferFundsRejectTransaction(**reject.model_dump(by_alias=True, exclude_none=True)) == reject


class TestFinancingTransactions:
    """Named coverage for financing and dividend adjustment transactions."""

    def test_daily_financing_transaction(self) -> None:
        """Test DailyFinancingTransaction with nested PositionFinancing and OpenTradeFinancing."""
        payload = {
            **_txn_base("70", "DAILY_FINANCING"),
            "financing": "-1.25",
            "accountBalance": "9998.75",
            "accountFinancingMode": "DAILY",
            "positionFinancings": [
                {
                    "instrument": "EUR_USD",
                    "financing": "-1.25",
                    "baseFinancing": "-1.50",
                    "accountFinancingMode": "DAILY",
                    "homeConversionFactors": {"gainQuoteHome": {"factor": "1.0"}, "lossQuoteHome": {"factor": "1.0"}},
                    "openTradeFinancings": [{"tradeID": "100", "financing": "-0.75", "financingRate": "-0.0075"}],
                }
            ],
        }

        financing = DailyFinancingTransaction(**payload)
        assert financing.financing == Decimal("-1.25")
        assert isinstance(financing.financing, Decimal)
        assert financing.account_balance == Decimal("9998.75")
        assert financing.account_financing_mode == "DAILY"

        position = financing.position_financings[0]
        assert isinstance(position, PositionFinancing)
        assert position.instrument == InstrumentName.EUR_USD
        assert position.base_financing == Decimal("-1.50")
        assert position.home_conversion_factors is not None
        assert position.home_conversion_factors.gain_quote_home is not None
        assert position.home_conversion_factors.gain_quote_home.factor == Decimal("1.0")

        open_trade = position.open_trade_financings[0]
        assert isinstance(open_trade, OpenTradeFinancing)
        assert open_trade.trade_id == "100"
        assert open_trade.financing == Decimal("-0.75")
        assert open_trade.financing_rate == Decimal("-0.0075")

        assert DailyFinancingTransaction(**financing.model_dump(by_alias=True, exclude_none=True)) == financing

    def test_dividend_adjustment_transaction(self) -> None:
        """Test DividendAdjustmentTransaction with nested OpenTradeDividendAdjustment."""
        payload = {
            **_txn_base("71", "DIVIDEND_ADJUSTMENT"),
            "instrument": "SPX500_USD",
            "dividendAdjustment": "2.35",
            "quoteDividendAdjustment": "2.35",
            "accountBalance": "10002.35",
            "openTradeDividendAdjustments": [
                {"tradeID": "200", "dividendAdjustment": "2.35", "quoteDividendAdjustment": "2.35"},
            ],
        }

        dividend = DividendAdjustmentTransaction(**payload)
        assert dividend.instrument == payload["instrument"]
        assert dividend.dividend_adjustment == Decimal("2.35")
        assert isinstance(dividend.dividend_adjustment, Decimal)
        assert dividend.account_balance == Decimal("10002.35")

        open_trade = dividend.open_trade_dividend_adjustments[0]
        assert isinstance(open_trade, OpenTradeDividendAdjustment)
        assert open_trade.trade_id == "200"
        assert open_trade.dividend_adjustment == Decimal("2.35")

        assert DividendAdjustmentTransaction(**dividend.model_dump(by_alias=True, exclude_none=True)) == dividend

    def test_fixed_price_order_transaction(self) -> None:
        """Test FixedPriceOrderTransaction aliases and reason."""
        payload = {
            **_txn_base("72", "FIXED_PRICE_ORDER"),
            "instrument": "SPX500_USD",
            "units": "10",
            "price": "5250.0",
            "positionFill": "DEFAULT",
            "tradeState": "OPEN",
            "reason": "PLATFORM_ACCOUNT_MIGRATION",
        }

        fixed = FixedPriceOrderTransaction(**payload)
        assert fixed.units == Decimal("10")
        assert fixed.price == Decimal("5250.0")
        assert isinstance(fixed.price, Decimal)
        assert fixed.trade_state == payload["tradeState"]
        assert fixed.reason == "PLATFORM_ACCOUNT_MIGRATION"
        assert FixedPriceOrderTransaction(**fixed.model_dump(by_alias=True, exclude_none=True)) == fixed


class TestClientExtensionsTransactions:
    """Named coverage for client-extensions modify and cancel-reject transactions."""

    def test_order_cancel_reject_transaction(self) -> None:
        """Test OrderCancelRejectTransaction aliases."""
        payload = {
            **_txn_base("80", "ORDER_CANCEL_REJECT"),
            "orderID": "79",
            "clientOrderID": "client-79",
            "rejectReason": "ORDER_DOESNT_EXIST",
        }

        reject = OrderCancelRejectTransaction(**payload)
        assert reject.order_id == payload["orderID"]
        assert reject.client_order_id == payload["clientOrderID"]
        assert reject.reject_reason == TransactionRejectReason.ORDER_DOESNT_EXIST
        assert OrderCancelRejectTransaction(**reject.model_dump(by_alias=True, exclude_none=True)) == reject

    def test_order_client_extensions_modify_transaction(self) -> None:
        """Test OrderClientExtensionsModifyTransaction aliases."""
        payload = {
            **_txn_base("81", "ORDER_CLIENT_EXTENSIONS_MODIFY"),
            "orderID": "79",
            "clientOrderID": "client-79",
            "clientExtensionsModify": {"id": "new-id", "tag": "new-tag"},
            "tradeClientExtensionsModify": {"comment": "updated"},
        }

        modify = OrderClientExtensionsModifyTransaction(**payload)
        assert modify.order_id == payload["orderID"]
        assert modify.client_extensions_modify.id == "new-id"
        assert modify.client_extensions_modify.tag == "new-tag"
        assert modify.trade_client_extensions_modify is not None
        assert modify.trade_client_extensions_modify.comment == "updated"
        assert OrderClientExtensionsModifyTransaction(**modify.model_dump(by_alias=True, exclude_none=True)) == modify

    def test_trade_client_extensions_modify_transaction(self) -> None:
        """Test TradeClientExtensionsModifyTransaction aliases."""
        payload = {
            **_txn_base("82", "TRADE_CLIENT_EXTENSIONS_MODIFY"),
            "tradeID": "42",
            "clientTradeID": "client-42",
            "tradeClientExtensionsModify": {"id": "new-trade-id"},
        }

        modify = TradeClientExtensionsModifyTransaction(**payload)
        assert modify.trade_id == payload["tradeID"]
        assert modify.client_trade_id == payload["clientTradeID"]
        assert modify.trade_client_extensions_modify.id == "new-trade-id"
        assert TradeClientExtensionsModifyTransaction(**modify.model_dump(by_alias=True, exclude_none=True)) == modify


class TestOrderFillSupportModels:
    """Named coverage for order-fill support models."""

    def test_trade_open(self) -> None:
        """Test TradeOpen aliases and Decimal typing."""
        payload = {
            "tradeID": "100",
            "units": "10000",
            "price": "1.0950",
            "guaranteedExecutionFee": "0.00",
            "halfSpreadCost": "0.25",
            "initialMarginRequired": "219.00",
            "clientExtensions": {"id": "trade-100"},
        }

        opened = TradeOpen(**payload)
        assert opened.trade_id == payload["tradeID"]
        assert opened.half_spread_cost == Decimal("0.25")
        assert opened.initial_margin_required == Decimal("219.00")
        assert opened.units == Decimal("10000")
        assert isinstance(opened.price, Decimal)
        assert opened.client_extensions is not None
        assert opened.client_extensions.id == "trade-100"
        assert TradeOpen(**opened.model_dump(by_alias=True, exclude_none=True)) == opened

    def test_trade_reduce(self) -> None:
        """Test TradeReduce aliases and Decimal typing."""
        payload = {
            "tradeID": "100",
            "units": "-5000",
            "price": "1.0980",
            "realizedPL": "15.00",
            "financing": "-0.10",
            "guaranteedExecutionFee": "0.00",
            "halfSpreadCost": "0.13",
        }

        reduced = TradeReduce(**payload)
        assert reduced.trade_id == payload["tradeID"]
        assert reduced.realized_pl == Decimal("15.00")
        assert reduced.half_spread_cost == Decimal("0.13")
        assert reduced.units == Decimal("-5000")
        assert isinstance(reduced.realized_pl, Decimal)
        assert TradeReduce(**reduced.model_dump(by_alias=True, exclude_none=True)) == reduced

    def test_full_price(self) -> None:
        """Test FullPrice aliases and Decimal typing."""
        payload = {"closeoutBid": "1.0945", "closeoutAsk": "1.0955", "liquidity": 10000000}

        full_price = FullPrice(**payload)
        assert full_price.closeout_bid == Decimal("1.0945")
        assert full_price.closeout_ask == Decimal("1.0955")
        assert isinstance(full_price.closeout_bid, Decimal)
        assert full_price.liquidity == payload["liquidity"]
        assert FullPrice(**full_price.model_dump(by_alias=True, exclude_none=True)) == full_price

    def test_liquidity_regeneration_schedule(self) -> None:
        """Test LiquidityRegenerationSchedule and its steps."""
        payload = {
            "steps": [
                {"timestamp": "2024-01-15T12:00:05.000000000Z", "bidLiquidityUsed": "1000000", "askLiquidityUsed": "0"},
                {"timestamp": "2024-01-15T12:00:10.000000000Z", "bidLiquidityUsed": "0", "askLiquidityUsed": "0"},
            ]
        }

        schedule = LiquidityRegenerationSchedule(**payload)
        assert len(schedule.steps) == 2
        step = schedule.steps[0]
        assert isinstance(step, LiquidityRegenerationScheduleStep)
        assert step.bid_liquidity_used == Decimal("1000000")
        assert step.ask_liquidity_used == Decimal("0")
        assert isinstance(step.bid_liquidity_used, Decimal)
        assert LiquidityRegenerationSchedule(**schedule.model_dump(by_alias=True, exclude_none=True)) == schedule

    def test_transaction_heartbeat(self) -> None:
        """Test TransactionHeartbeat aliases."""
        payload = {"type": "HEARTBEAT", "time": "2024-01-15T12:00:00.000000000Z", "lastTransactionID": "12345"}

        heartbeat = TransactionHeartbeat(**payload)
        assert heartbeat.type == "HEARTBEAT"
        assert heartbeat.last_transaction_id == payload["lastTransactionID"]
        assert TransactionHeartbeat(**heartbeat.model_dump(by_alias=True, exclude_none=True)) == heartbeat


class TestTransactionEnumCompleteness:
    """Exact member counts for the large transaction enums."""

    def test_transaction_reject_reason_members(self) -> None:
        """TransactionRejectReason has the full official member set."""
        values = [member.value for member in TransactionRejectReason]
        assert len(values) == 198
        assert len(set(values)) == 198
        assert TransactionRejectReason("INSTRUMENT_MISSING") is TransactionRejectReason.INSTRUMENT_MISSING
        assert TransactionRejectReason("TRADE_DOESNT_EXIST") is TransactionRejectReason.TRADE_DOESNT_EXIST
        assert TransactionRejectReason("PRICE_DISTANCE_MINIMUM_NOT_MET") is TransactionRejectReason.PRICE_DISTANCE_MINIMUM_NOT_MET

    def test_transaction_filter_members(self) -> None:
        """TransactionFilter has the full official member set."""
        values = [member.value for member in TransactionFilter]
        assert len(values) == 42
        assert len(set(values)) == 42
        assert TransactionFilter("DAILY_FINANCING") is TransactionFilter.DAILY_FINANCING
        assert TransactionFilter("ONE_CANCELS_ALL_ORDER_TRIGGERED") is TransactionFilter.ONE_CANCELS_ALL_ORDER_TRIGGERED
