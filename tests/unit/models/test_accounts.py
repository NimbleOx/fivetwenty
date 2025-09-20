"""Tests for account-related models."""

from decimal import Decimal

from fivetwenty.models import (
    Account,
    AccountProperties,
    Currency,
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
