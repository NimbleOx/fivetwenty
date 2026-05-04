"""Tests for transaction-related models."""

from decimal import Decimal

from fivetwenty.models import (
    AcceptDatetimeFormat,
    FundingReason,
    InstrumentName,
    MarketOrderTransaction,
    OrderCancelTransaction,
    OrderFillTransaction,
    OrderPositionFill,
    TimeInForce,
    Transaction,
    TransactionFilter,
    TransactionIDRange,
    TransactionQueryFilter,
    TransactionRejectReason,
    TransactionType,
)


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
        assert TransactionRejectReason.MARKET_HALTED == "MARKET_HALTED"
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
                "closeoutBid": "1.0945",
                "closeoutAsk": "1.0955",
                "liquidity": 10000000,
            },
            "accountBalance": "10000.00",
            "halfSpreadCost": "0.25",
            "guaranteeExecutionFee": "0.10",
        }

        fill = OrderFillTransaction(**api_data)
        fill_back_to_api = fill.model_dump(by_alias=True, exclude_none=True)

        # Perfect round-trip
        fill_roundtrip = OrderFillTransaction(**fill_back_to_api)
        assert fill_roundtrip.order_id == fill.order_id
        assert fill_roundtrip.client_order_id == fill.client_order_id
        assert fill_roundtrip.gain_quote_home_conversion_factor == fill.gain_quote_home_conversion_factor
        assert fill_roundtrip.full_vwap == fill.full_vwap
        assert fill_roundtrip.guarantee_execution_fee == fill.guarantee_execution_fee

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
