"""Tests for account-related models."""

from decimal import Decimal
from typing import Any

from fivetwenty.models import (
    Account,
    AccountChanges,
    AccountChangesState,
    AccountProperties,
    AccountSummary,
    AccumulatedAccountState,
    CalculatedAccountState,
    Currency,
    DynamicOrderState,
    GuaranteedStopLossOrderMode,
    GuaranteedStopLossOrderMutability,
    GuaranteedStopLossOrderParameters,
    MarketOrder,
    Transaction,
    UserAttributes,
)


class TestAccountModels:
    """Test account-related models."""

    def test_account_properties(self) -> None:
        """Test AccountProperties model."""
        props = AccountProperties(id="001-001-123456-001", mt4_account_id=12345, tags=["demo", "test"])
        assert props.id == "001-001-123456-001"
        assert props.mt4_account_id == 12345
        assert props.tags == ["demo", "test"]

    def test_account_properties_defaults(self) -> None:
        """Test AccountProperties with default values."""
        props = AccountProperties(id="001-001-123456-001")
        assert props.id == "001-001-123456-001"
        assert props.mt4_account_id is None
        assert props.tags == []

    def test_account(self) -> None:
        """Test Account model."""
        account = Account(
            id="001-001-123456-001",
            currency=Currency.USD,
            balance="10000.00",  # Use string for AccountUnits
            created_by_user_id=123456,
            created_time="2024-01-01T12:00:00Z",
            # Required fields for complete Account model
            open_trade_count=0,
            open_position_count=0,
            pending_order_count=0,
            hedging_enabled=True,
            unrealized_pl="0.00",
            nav="10000.00",
            margin_used="0.00",
            margin_available="10000.00",
            position_value="0.00",
            margin_closeout_unrealized_pl="0.00",
            margin_closeout_nav="10000.00",
            margin_closeout_margin_used="0.00",
            margin_closeout_percent="0.10000",
            margin_closeout_position_value="0.00000",
            withdrawal_limit="10000.00",
            margin_call_margin_used="0.00",
            margin_call_percent="0.05000",
            pl="0.00",
            resettable_pl="0.00",
            financing="0.00",
            commission="0.00",
            dividend_adjustment="0.00",
            guaranteed_execution_fees="0.00",
            last_transaction_id="1",
        )
        assert account.id == "001-001-123456-001"
        assert account.currency == Currency.USD
        assert account.balance == Decimal("10000.00")
        assert account.created_by_user_id == 123456


def _calculated_state_payload() -> dict[str, Any]:
    """CamelCase payload for the price-dependent account state fields."""
    return {
        "unrealizedPL": "25.50",
        "NAV": "10025.50",
        "marginUsed": "219.00",
        "marginAvailable": "9806.50",
        "positionValue": "10950.00",
        "marginCloseoutUnrealizedPL": "24.00",
        "marginCloseoutNAV": "10024.00",
        "marginCloseoutMarginUsed": "219.00",
        "marginCloseoutPercent": "0.01092",
        "marginCloseoutPositionValue": "10950.00000",
        "withdrawalLimit": "9806.50",
        "marginCallMarginUsed": "219.00",
        "marginCallPercent": "0.02184",
    }


def _accumulated_state_payload() -> dict[str, Any]:
    """CamelCase payload for the accumulated account state fields."""
    return {
        "balance": "10000.00",
        "pl": "150.00",
        "resettablePL": "150.00",
        "financing": "-5.25",
        "commission": "2.50",
        "dividendAdjustment": "0.00",
        "guaranteedExecutionFees": "0.00",
    }


class TestAccountStateModels:
    """Named coverage for account summary and state models."""

    def test_account_summary(self) -> None:
        """Test AccountSummary with an OANDA-shaped payload."""
        payload = {
            "id": "101-001-123456-001",
            "alias": "primary",
            "currency": "USD",
            "createdByUserID": 123456,
            "createdTime": "2024-01-01T12:00:00.000000000Z",
            "guaranteedStopLossOrderMode": "DISABLED",
            "marginRate": "0.02",
            "openTradeCount": 1,
            "openPositionCount": 1,
            "pendingOrderCount": 2,
            "hedgingEnabled": False,
            "lastTransactionID": "1234",
            **_calculated_state_payload(),
            **_accumulated_state_payload(),
        }

        summary = AccountSummary(**payload)
        assert summary.created_by_user_id == payload["createdByUserID"]
        assert summary.guaranteed_stop_loss_order_mode == GuaranteedStopLossOrderMode.DISABLED
        assert summary.open_trade_count == payload["openTradeCount"]
        assert summary.pending_order_count == payload["pendingOrderCount"]
        assert summary.last_transaction_id == payload["lastTransactionID"]
        assert summary.margin_rate == Decimal("0.02")
        assert summary.nav == Decimal("10025.50")
        assert summary.margin_closeout_percent == Decimal("0.01092")
        assert isinstance(summary.balance, Decimal)
        assert isinstance(summary.unrealized_pl, Decimal)

        dumped = summary.model_dump(by_alias=True, exclude_none=True)
        assert dumped["NAV"] == "10025.50"
        assert dumped["createdByUserID"] == 123456
        assert AccountSummary(**dumped) == summary

    def test_calculated_account_state(self) -> None:
        """Test CalculatedAccountState aliases and Decimal typing."""
        payload = _calculated_state_payload()
        state = CalculatedAccountState(**payload)
        assert state.unrealized_pl == Decimal(payload["unrealizedPL"])
        assert state.nav == Decimal(payload["NAV"])
        assert state.margin_used == Decimal(payload["marginUsed"])
        assert state.margin_call_percent == Decimal(payload["marginCallPercent"])
        assert isinstance(state.margin_available, Decimal)
        assert CalculatedAccountState(**state.model_dump(by_alias=True, exclude_none=True)) == state

    def test_accumulated_account_state(self) -> None:
        """Test AccumulatedAccountState aliases and Decimal typing."""
        payload = {**_accumulated_state_payload(), "marginCallExtensionCount": 0}
        state = AccumulatedAccountState(**payload)
        assert state.resettable_pl == Decimal(payload["resettablePL"])
        assert state.dividend_adjustment == Decimal(payload["dividendAdjustment"])
        assert state.guaranteed_execution_fees == Decimal(payload["guaranteedExecutionFees"])
        assert state.margin_call_extension_count == 0
        assert isinstance(state.financing, Decimal)
        assert AccumulatedAccountState(**state.model_dump(by_alias=True, exclude_none=True)) == state

    def test_user_attributes(self) -> None:
        """Test UserAttributes aliases."""
        payload = {
            "userID": 123456,
            "username": "trader1",
            "title": "Mr",
            "name": "Test Trader",
            "email": "trader@example.com",
            "divisionAbbreviation": "OAP",
            "languageAbbreviation": "en",
            "homeCurrency": "USD",
        }

        attributes = UserAttributes(**payload)
        assert attributes.user_id == payload["userID"]
        assert attributes.division_abbreviation == payload["divisionAbbreviation"]
        assert attributes.language_abbreviation == payload["languageAbbreviation"]
        assert attributes.home_currency == Currency.USD
        assert UserAttributes(**attributes.model_dump(by_alias=True, exclude_none=True)) == attributes

    def test_guaranteed_stop_loss_order_parameters(self) -> None:
        """Test GuaranteedStopLossOrderParameters aliases."""
        payload = {"mutabilityMarketOpen": "REPLACEABLE", "mutabilityMarketHalted": "FIXED"}
        parameters = GuaranteedStopLossOrderParameters(**payload)
        assert parameters.mutability_market_open == GuaranteedStopLossOrderMutability.REPLACEABLE
        assert parameters.mutability_market_halted == GuaranteedStopLossOrderMutability.FIXED
        assert GuaranteedStopLossOrderParameters(**parameters.model_dump(by_alias=True, exclude_none=True)) == parameters


class TestAccountChangesModels:
    """Named coverage for account changes polling models."""

    def test_account_changes(self) -> None:
        """Test AccountChanges aliases with nested orders and transactions."""
        payload = {
            "ordersCreated": [
                {
                    "id": "10",
                    "createTime": "2024-01-15T12:00:00.000000000Z",
                    "state": "FILLED",
                    "type": "MARKET",
                    "instrument": "EUR_USD",
                    "units": "100",
                }
            ],
            "ordersCancelled": [],
            "ordersFilled": [],
            "ordersTriggered": [],
            "tradesOpened": [],
            "tradesReduced": [],
            "tradesClosed": [],
            "positions": [],
            "transactions": [
                {
                    "id": "10",
                    "time": "2024-01-15T12:00:00.000000000Z",
                    "userID": 123456,
                    "accountID": "101-001-123456-001",
                    "batchID": "10",
                    "type": "MARKET_ORDER",
                    "instrument": "EUR_USD",
                    "units": "100",
                }
            ],
        }

        changes = AccountChanges(**payload)
        assert len(changes.orders_created) == 1
        assert isinstance(changes.orders_created[0], MarketOrder)
        assert changes.orders_created[0].units == Decimal("100")
        assert changes.orders_cancelled == []
        assert changes.trades_opened == []
        assert len(changes.transactions) == 1
        assert isinstance(changes.transactions[0], Transaction)
        assert changes.transactions[0].account_id == "101-001-123456-001"

    def test_account_changes_state(self) -> None:
        """Test AccountChangesState aliases, Decimal typing, and dynamic order states."""
        payload = {
            **_calculated_state_payload(),
            "balance": "10000.00",
            "resettablePL": "150.00",
            "dividendAdjustment": "0.00",
            "orders": [{"id": "7", "trailingStopValue": "1.1000", "triggerDistance": "0.0050", "isTriggerDistanceExact": True}],
            "trades": [],
            "positions": [],
        }

        state = AccountChangesState(**payload)
        assert state.unrealized_pl == Decimal("25.50")
        assert state.nav == Decimal("10025.50")
        assert state.margin_used == Decimal("219.00")
        assert isinstance(state.balance, Decimal)
        assert len(state.orders) == 1
        assert isinstance(state.orders[0], DynamicOrderState)
        assert state.orders[0].trailing_stop_value == Decimal("1.1000")
        assert AccountChangesState(**state.model_dump(by_alias=True, exclude_none=True)) == state
