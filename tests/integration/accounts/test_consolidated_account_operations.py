"""Consolidated integration tests for account operations.

This module combines account validation, configuration checking, and instrument
retrieval into efficient tests that validate multiple aspects with fewer API calls.
"""

from decimal import Decimal

import pytest

from fivetwenty import AsyncClient


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.core
class TestConsolidatedAccountOperations:
    """Consolidated tests for account operations with efficient API usage."""

    async def test_comprehensive_account_validation(self, sandbox_client: AsyncClient, test_account_id: str):
        """Test comprehensive account functionality in a single efficient test.

        Consolidates testing of:
        - Account details retrieval and validation
        - Account summary data accuracy
        - Configuration settings verification
        - Data type and precision validation
        - Cross-endpoint consistency checking
        """
        print("✓ Starting comprehensive account validation test...")

        # Single API call to get detailed account information
        account_response = await sandbox_client.accounts.get_account(test_account_id)

        assert account_response is not None, "Account response should not be None"
        assert "account" in account_response, "Response should contain 'account' field"
        assert "lastTransactionID" in account_response, "Response should contain 'lastTransactionID' field"

        account = account_response["account"]

        print(f"✓ Retrieved account details for {test_account_id}")

        # Core account validation
        assert account.id == test_account_id, f"Account ID mismatch: expected {test_account_id}, got {account.id}"
        assert account.currency is not None, "Account currency should be set"
        assert len(account.currency) == 3, f"Currency should be 3-character code, got '{account.currency}'"

        # Financial data type validation
        assert isinstance(account.balance, Decimal), f"Balance should be Decimal, got {type(account.balance)}"
        assert isinstance(account.margin_used, Decimal), f"Margin used should be Decimal, got {type(account.margin_used)}"
        assert isinstance(account.margin_available, Decimal), f"Margin available should be Decimal, got {type(account.margin_available)}"
        assert isinstance(account.nav, Decimal), f"NAV should be Decimal, got {type(account.nav)}"
        assert isinstance(account.unrealized_pl, Decimal), f"Unrealized P&L should be Decimal, got {type(account.unrealized_pl)}"

        # Margin and balance validation
        assert account.margin_used >= 0, f"Margin used should be non-negative, got {account.margin_used}"
        assert account.margin_available >= 0, f"Margin available should be non-negative, got {account.margin_available}"

        # Count fields validation
        assert isinstance(account.open_trade_count, int), f"Open trade count should be int, got {type(account.open_trade_count)}"
        assert isinstance(account.open_position_count, int), f"Open position count should be int, got {type(account.open_position_count)}"
        assert isinstance(account.pending_order_count, int), f"Pending order count should be int, got {type(account.pending_order_count)}"

        assert account.open_trade_count >= 0, f"Open trade count should be non-negative, got {account.open_trade_count}"
        assert account.open_position_count >= 0, f"Open position count should be non-negative, got {account.open_position_count}"
        assert account.pending_order_count >= 0, f"Pending order count should be non-negative, got {account.pending_order_count}"

        # Configuration validation
        assert isinstance(account.hedging_enabled, bool), f"Hedging enabled should be bool, got {type(account.hedging_enabled)}"
        assert isinstance(account.created_by_user_id, int), f"Created by user ID should be int, got {type(account.created_by_user_id)}"
        assert account.created_time is not None, "Created time should be set"

        # Margin rate validation
        if account.margin_rate is not None:
            assert isinstance(account.margin_rate, Decimal), f"Margin rate should be Decimal, got {type(account.margin_rate)}"
            assert 0.001 <= account.margin_rate <= 1.0, f"Margin rate should be reasonable (0.1%-100%), got {account.margin_rate}"

        print(f"  Core account data validated - Balance: {account.balance}, NAV: {account.nav}")

        # Single API call to get account summary for consistency check
        account_summary_response = await sandbox_client.accounts.get_account_summary(test_account_id)
        account_summary = account_summary_response["account"]

        # Cross-endpoint consistency validation
        assert account_summary.id == test_account_id, "Summary should return same account ID"
        assert account_summary.currency == account.currency, "Summary currency should match detailed account"
        assert account_summary.balance == account.balance, "Summary balance should match detailed account"

        # GSL configuration validation
        assert account_summary.guaranteed_stop_loss_order_mode is not None, "GSL order mode should be set"
        gsl_mode = account_summary.guaranteed_stop_loss_order_mode
        valid_gsl_modes = ["DISABLED", "ALLOWED", "REQUIRED"]
        assert gsl_mode in valid_gsl_modes, f"GSL mode should be valid, got {gsl_mode}"

        print(f"  Configuration validated - Currency: {account.currency}, GSL: {gsl_mode}, Hedging: {account.hedging_enabled}")

        # Single API call to get accounts list for existence validation
        accounts = await sandbox_client.accounts.get_accounts()
        assert len(accounts) > 0, "Should have at least one account"

        account_ids = [acc.id for acc in accounts]
        assert test_account_id in account_ids, f"Test account {test_account_id} should be in accounts list"

        # Find our account in the list and validate basic properties
        our_account = next((acc for acc in accounts if acc.id == test_account_id), None)
        assert our_account is not None, "Should find our account in the list"
        assert hasattr(our_account, "tags"), "Account should have tags attribute"

        print(f"  Account list validation passed - Found {len(accounts)} total accounts")

        print(f"✓ Comprehensive account validation completed for {test_account_id}")

    async def test_account_instruments_and_configuration(self, sandbox_client: AsyncClient, test_account_id: str):
        """Test account instruments and trading configuration.

        Consolidates testing of:
        - Available instruments retrieval
        - Instrument metadata validation
        - Trading limits and precision
        - Margin requirements
        - Filtering functionality
        """
        print("✓ Starting account instruments and configuration test...")

        # Single API call to get all available instruments
        instruments_response = await sandbox_client.accounts.get_account_instruments(test_account_id)

        assert "instruments" in instruments_response, "Response should contain 'instruments' field"
        assert "lastTransactionID" in instruments_response, "Response should contain 'lastTransactionID' field"

        instruments = instruments_response["instruments"]

        # Basic validation
        assert len(instruments) > 0, "Account should have available instruments"
        assert len(instruments) > 50, "Practice account should have many instruments available"

        print(f"  Retrieved {len(instruments)} available instruments")

        # Test major currency pairs availability
        instrument_names = {instr.name for instr in instruments}
        major_pairs = {"EUR_USD", "GBP_USD", "USD_JPY", "USD_CHF"}
        available_majors = major_pairs.intersection(instrument_names)
        assert len(available_majors) >= 3, f"Should have most major pairs available, got: {available_majors}"

        # Find EUR_USD for detailed validation
        eur_usd = next((instr for instr in instruments if instr.name == "EUR_USD"), None)
        assert eur_usd is not None, "EUR_USD should be available for testing"

        # Comprehensive instrument validation
        assert eur_usd.name == "EUR_USD"
        assert eur_usd.display_name is not None
        assert len(eur_usd.display_name) > 0
        assert eur_usd.type is not None

        # Precision and pip location validation
        assert isinstance(eur_usd.pip_location, int)
        assert -5 <= eur_usd.pip_location <= 1, f"EUR_USD pip location should be reasonable, got {eur_usd.pip_location}"
        assert isinstance(eur_usd.display_precision, int)
        assert 1 <= eur_usd.display_precision <= 10
        assert isinstance(eur_usd.trade_units_precision, int)
        assert 0 <= eur_usd.trade_units_precision <= 8

        # Trading limits validation
        assert float(eur_usd.minimum_trade_size) > 0, "Minimum trade size should be positive"
        assert float(eur_usd.maximum_position_size) >= 0, "Maximum position size should be non-negative"
        assert float(eur_usd.maximum_order_units) > 0, "Maximum order units should be positive"
        assert float(eur_usd.minimum_trade_size) <= float(eur_usd.maximum_order_units), "Min trade size should be <= max order units"

        # Margin requirements validation
        assert float(eur_usd.margin_rate) > 0, "Margin rate should be positive"
        assert float(eur_usd.margin_rate) <= 1.0, "Margin rate should be <= 100%"
        assert float(eur_usd.margin_rate) >= 0.001, "Margin rate should be reasonable (>= 0.1%)"

        # Trailing stop distances validation
        assert float(eur_usd.minimum_trailing_stop_distance) >= 0
        assert float(eur_usd.maximum_trailing_stop_distance) > float(eur_usd.minimum_trailing_stop_distance)

        print(f"  EUR_USD validation passed - Min trade: {eur_usd.minimum_trade_size}, Margin rate: {eur_usd.margin_rate}")

        # Single API call to test filtering functionality
        filtered_instruments_response = await sandbox_client.accounts.get_account_instruments(test_account_id, instruments=["EUR_USD", "GBP_USD"])

        filtered_instruments = filtered_instruments_response["instruments"]
        assert len(filtered_instruments) == 2, f"Expected 2 instruments, got {len(filtered_instruments)}"

        filtered_names = {instr.name for instr in filtered_instruments}
        assert filtered_names == {"EUR_USD", "GBP_USD"}, f"Got unexpected instruments: {filtered_names}"

        # Instrument types validation
        instrument_types = {instr.type for instr in instruments}
        assert len(instrument_types) >= 1, f"Should have at least one instrument type, got: {instrument_types}"
        assert "CURRENCY" in instrument_types, f"Should have CURRENCY instruments available, got: {instrument_types}"

        print(f"  Filtering validation passed - Got {filtered_names}")
        print(f"  Available instrument types: {sorted(instrument_types)}")

        print("✓ Account instruments and configuration test completed")
