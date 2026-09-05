"""Unit tests for account configuration endpoints."""

from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock

import httpx
import pytest

from fivetwenty import AsyncClient
from fivetwenty.endpoints.accounts import AccountEndpoints
from fivetwenty.models import Account, AccountChanges, AccountProperties, AccountSummary, Instrument, OrderFillTransaction


class TestAccountConfigurationEndpoints:
    """Test suite for account configuration functionality."""

    @pytest.fixture
    def mock_client(self):
        """Create a mock async client."""
        client = MagicMock()

        # Create a side effect function that returns appropriate responses based on the request
        async def mock_request(method, path, **kwargs):
            mock_response = MagicMock()

            # For PATCH /accounts/{id}/configuration
            if method == "PATCH" and "/configuration" in path:
                mock_response.json.return_value = {
                    "clientConfigureTransaction": {
                        "id": "123",
                        "type": "CLIENT_CONFIGURE",
                        "time": "2024-01-01T00:00:00.000000000Z",
                        "userID": 1,
                        "accountID": "101-001-123456-001",
                        "batchID": "123",
                    },
                    "lastTransactionID": "123",
                }
            # For GET /accounts/{id}/changes
            elif method == "GET" and "/changes" in path:
                mock_response.json.return_value = {
                    "changes": {
                        "ordersCancelled": [],
                        "ordersCreated": [],
                        "ordersFilled": [],
                        "ordersTriggered": [],
                        "tradesOpened": [],
                        "tradesReduced": [],
                        "tradesClosed": [],
                        "positions": [],
                        "transactions": [],
                    },
                    "state": {
                        "unrealizedPL": "0.0000",
                        "NAV": "100000.0000",
                        "marginUsed": "0.0000",
                        "marginAvailable": "100000.0000",
                        "positionValue": "0.0000",
                        "marginCloseoutUnrealizedPL": "0.0000",
                        "marginCloseoutNAV": "100000.0000",
                        "marginCloseoutMarginUsed": "0.0000",
                        "marginCloseoutPositionValue": "0.0000",
                        "marginCloseoutPercent": "0.0000",
                        "withdrawalLimit": "100000.0000",
                        "orders": [],
                        "trades": [],
                        "positions": [],
                    },
                    "lastTransactionID": "123",
                }
            else:
                mock_response.json.return_value = {"mock": "data"}

            return mock_response

        client._request = AsyncMock(side_effect=mock_request)
        return client

    @pytest.fixture
    def accounts(self, mock_client):
        """Create AccountEndpoints instance with mock client."""
        return AccountEndpoints(mock_client)

    @pytest.mark.asyncio
    async def test_update_configuration_alias_only(self, accounts, mock_client):
        """Test updating account configuration with alias only."""
        await accounts.patch_account_configuration("101-001-123456-001", alias="My Trading Account")

        mock_client._request.assert_called_once_with(
            "PATCH",
            "/accounts/101-001-123456-001/configuration",
            json_data={"alias": "My Trading Account"},
        )

    @pytest.mark.asyncio
    async def test_update_configuration_margin_rate_only(self, accounts, mock_client):
        """Test updating account configuration with margin rate only."""
        await accounts.patch_account_configuration("101-001-123456-001", margin_rate="0.05")

        mock_client._request.assert_called_once_with(
            "PATCH",
            "/accounts/101-001-123456-001/configuration",
            json_data={"marginRate": "0.05"},
        )

    @pytest.mark.asyncio
    async def test_update_configuration_both_parameters(self, accounts, mock_client):
        """Test updating account configuration with both alias and margin rate."""
        await accounts.patch_account_configuration("101-001-123456-001", alias="Professional Account", margin_rate="0.02")

        mock_client._request.assert_called_once_with(
            "PATCH",
            "/accounts/101-001-123456-001/configuration",
            json_data={"alias": "Professional Account", "marginRate": "0.02"},
        )

    @pytest.mark.asyncio
    async def test_update_configuration_no_parameters_raises_error(self, accounts, mock_client):
        """Test that updating configuration with no parameters raises ValueError."""
        with pytest.raises(ValueError, match="Must provide at least one configuration parameter"):
            await accounts.patch_account_configuration("101-001-123456-001")

    @pytest.mark.asyncio
    async def test_get_changes_requires_transaction_id(self, accounts, mock_client):
        """Test that getting account changes requires transaction ID parameter."""
        with pytest.raises(TypeError, match="missing 1 required keyword-only argument: 'since_transaction_id'"):
            await accounts.get_account_changes("101-001-123456-001")

    @pytest.mark.asyncio
    async def test_get_changes_with_transaction_id(self, accounts, mock_client):
        """Test getting account changes since a specific transaction ID."""
        await accounts.get_account_changes("101-001-123456-001", since_transaction_id="12345")

        mock_client._request.assert_called_once_with(
            "GET",
            "/accounts/101-001-123456-001/changes",
            params={"sinceTransactionID": "12345"},
        )

    @pytest.mark.asyncio
    async def test_update_configuration_alias_validation(self, accounts, mock_client):
        """Test configuration update with various alias formats."""
        test_aliases = [
            "Simple Name",
            "Account-With-Hyphens",
            "Account_With_Underscores",
            "Account with 123 Numbers",
            "Very Long Account Name That Might Be Used",
            "",  # Empty string should be allowed
        ]

        for alias in test_aliases:
            mock_client._request.reset_mock()

            await accounts.patch_account_configuration("101-001-123456-001", alias=alias)

            mock_client._request.assert_called_once_with(
                "PATCH",
                "/accounts/101-001-123456-001/configuration",
                json_data={"alias": alias},
            )

    @pytest.mark.asyncio
    async def test_update_configuration_margin_rate_validation(self, accounts, mock_client):
        """Test configuration update with various margin rate formats."""
        test_margin_rates = [
            "0.01",  # 1%
            "0.05",  # 5%
            "0.10",  # 10%
            "0.20",  # 20%
            "0.50",  # 50%
            "1.00",  # 100%
            "0.001",  # 0.1%
            "0.0025",  # 0.25%
        ]

        for margin_rate in test_margin_rates:
            mock_client._request.reset_mock()

            await accounts.patch_account_configuration("101-001-123456-001", margin_rate=margin_rate)

            mock_client._request.assert_called_once_with(
                "PATCH",
                "/accounts/101-001-123456-001/configuration",
                json_data={"marginRate": margin_rate},
            )

    @pytest.mark.asyncio
    async def test_get_changes_transaction_id_formats(self, accounts, mock_client):
        """Test get changes with various transaction ID formats."""
        test_transaction_ids = [
            "12345",  # Simple numeric
            "98765432100",  # Large numeric
            "1",  # Single digit
            "0",  # Zero
        ]

        for transaction_id in test_transaction_ids:
            mock_client._request.reset_mock()

            await accounts.get_account_changes("101-001-123456-001", since_transaction_id=transaction_id)

            mock_client._request.assert_called_once_with(
                "GET",
                "/accounts/101-001-123456-001/changes",
                params={"sinceTransactionID": transaction_id},
            )

    @pytest.mark.asyncio
    async def test_configuration_update_idempotency(self, accounts, mock_client):
        """Test that configuration updates are made correctly."""
        await accounts.patch_account_configuration("101-001-123456-001", alias="Test Account")

        # Verify the request was made
        mock_client._request.assert_called_once()

    @pytest.mark.asyncio
    async def test_comprehensive_account_management_workflow(self, accounts, mock_client):
        """Test a comprehensive account management workflow."""
        account_id = "101-001-123456-001"

        # Step 1: Get changes since transaction ID (required)
        await accounts.get_account_changes(account_id, since_transaction_id="12345")

        # Step 2: Update account alias
        mock_client._request.reset_mock()
        await accounts.patch_account_configuration(account_id, alias="Updated Account Name")

        # Step 3: Update margin rate
        mock_client._request.reset_mock()
        await accounts.patch_account_configuration(account_id, margin_rate="0.03")

        # Step 4: Get changes since a transaction ID
        mock_client._request.reset_mock()
        await accounts.get_account_changes(account_id, since_transaction_id="54321")

        # Step 5: Update both alias and margin rate together
        mock_client._request.reset_mock()
        await accounts.patch_account_configuration(account_id, alias="Final Account Name", margin_rate="0.025")

        # Verify the final call
        mock_client._request.assert_called_once_with(
            "PATCH",
            "/accounts/101-001-123456-001/configuration",
            json_data={"alias": "Final Account Name", "marginRate": "0.025"},
        )

    @pytest.mark.asyncio
    async def test_account_changes_polling_pattern(self, accounts, mock_client):
        """Test the typical polling pattern for account changes."""
        account_id = "101-001-123456-001"

        # Simulate polling pattern: use returned transaction IDs for subsequent calls
        transaction_ids = ["1001", "1005", "1010", "1015"]

        for _i, since_id in enumerate(transaction_ids):
            mock_client._request.reset_mock()

            await accounts.get_account_changes(account_id, since_transaction_id=since_id)

            expected_params = {"sinceTransactionID": since_id}

            mock_client._request.assert_called_once_with(
                "GET",
                "/accounts/101-001-123456-001/changes",
                params=expected_params,
            )

    @pytest.mark.asyncio
    async def test_edge_cases_and_special_values(self, accounts, mock_client):
        """Test edge cases and special values for account configuration."""
        account_id = "101-001-123456-001"

        # Test with very small margin rate
        await accounts.patch_account_configuration(account_id, margin_rate="0.0001")

        # Test with zero margin rate (might be valid in some contexts)
        mock_client._request.reset_mock()
        await accounts.patch_account_configuration(account_id, margin_rate="0.0000")

        # Test with very long alias
        long_alias = "A" * 100  # Very long alias
        mock_client._request.reset_mock()
        await accounts.patch_account_configuration(account_id, alias=long_alias)

        mock_client._request.assert_called_once_with(
            "PATCH",
            "/accounts/101-001-123456-001/configuration",
            json_data={"alias": long_alias},
        )

    @pytest.mark.asyncio
    async def test_account_responses_support_compatibility_access(self, accounts):
        """Test account endpoint responses support attribute and snake_case access."""
        config_response = await accounts.patch_account_configuration("101-001-123456-001", alias="My Account")

        assert config_response.client_configure_transaction.id == "123"
        assert config_response["client_configure_transaction"].id == "123"
        assert config_response.last_transaction_id == "123"
        assert config_response["last_transaction_id"] == "123"

        changes_response = await accounts.get_account_changes("101-001-123456-001", since_transaction_id="123")

        assert changes_response.last_transaction_id == "123"
        assert changes_response.state.get("marginUsed") == "0.0000"


# Realistic OANDA-shaped account summary payload (camelCase keys, string decimals)
ACCOUNT_SUMMARY_PAYLOAD = {
    "id": "101-001-123456-001",
    "alias": "Primary",
    "currency": "USD",
    "balance": "100000.0000",
    "createdByUserID": 1234567,
    "createdTime": "2023-06-01T12:00:00.000000000Z",
    "guaranteedStopLossOrderMode": "DISABLED",
    "marginRate": "0.02",
    "openTradeCount": 1,
    "openPositionCount": 1,
    "pendingOrderCount": 0,
    "hedgingEnabled": False,
    "unrealizedPL": "12.3400",
    "NAV": "100012.3400",
    "marginUsed": "220.0000",
    "marginAvailable": "99792.3400",
    "positionValue": "11000.0000",
    "marginCloseoutUnrealizedPL": "11.9800",
    "marginCloseoutNAV": "100011.9800",
    "marginCloseoutMarginUsed": "220.0000",
    "marginCloseoutPercent": "0.00110",
    "marginCloseoutPositionValue": "11000.0000",
    "withdrawalLimit": "99792.3400",
    "marginCallMarginUsed": "220.0000",
    "marginCallPercent": "0.00110",
    "pl": "150.2500",
    "resettablePL": "150.2500",
    "financing": "-3.5000",
    "commission": "0.0000",
    "dividendAdjustment": "0.0000",
    "guaranteedExecutionFees": "0.0000",
    "lastTransactionID": "5678",
}

# The full account payload extends the summary with open trades/positions/orders
ACCOUNT_PAYLOAD = {
    **ACCOUNT_SUMMARY_PAYLOAD,
    "trades": [],
    "positions": [],
    "orders": [],
}


class TestAccountReadEndpoints:
    """Test suite for get_accounts, get_account, and get_account_summary."""

    @pytest.fixture
    def mock_client(self):
        """Create a mock async client returning realistic OANDA account payloads."""
        client = MagicMock()

        async def mock_request(method, path, **kwargs):
            mock_response = MagicMock()

            if path.endswith("/summary"):
                mock_response.json.return_value = {
                    "account": ACCOUNT_SUMMARY_PAYLOAD,
                    "lastTransactionID": "5678",
                }
            elif path == "/accounts":
                mock_response.json.return_value = {
                    "accounts": [
                        {"id": "101-001-123456-001", "tags": ["demo"]},
                        {"id": "101-001-123456-002", "mt4AccountID": 7654321, "tags": []},
                    ],
                    "lastTransactionID": "5678",
                }
            else:
                mock_response.json.return_value = {
                    "account": ACCOUNT_PAYLOAD,
                    "lastTransactionID": "5678",
                }

            return mock_response

        client._request = AsyncMock(side_effect=mock_request)
        return client

    @pytest.fixture
    def accounts(self, mock_client):
        """Create AccountEndpoints instance with mock client."""
        return AccountEndpoints(mock_client)

    @pytest.mark.asyncio
    async def test_get_accounts(self, accounts, mock_client):
        """Test that get_accounts hits /accounts and parses AccountProperties."""
        result = await accounts.get_accounts()

        mock_client._request.assert_called_once_with("GET", "/accounts")

        assert isinstance(result, list)
        assert len(result) == 2
        assert all(isinstance(item, AccountProperties) for item in result)
        assert result[0].id == "101-001-123456-001"
        assert result[0].tags == ["demo"]
        assert result[0].mt4_account_id is None
        assert result[1].id == "101-001-123456-002"
        assert result[1].mt4_account_id == 7654321

    @pytest.mark.asyncio
    async def test_get_accounts_drops_last_transaction_id(self, accounts, mock_client):
        """Test that get_accounts returns a bare list without the lastTransactionID wrapper."""
        result = await accounts.get_accounts()

        assert isinstance(result, list)
        assert not isinstance(result, dict)

    @pytest.mark.asyncio
    async def test_get_account(self, accounts, mock_client):
        """Test that get_account hits the account URL and parses the Account model."""
        result = await accounts.get_account("101-001-123456-001")

        mock_client._request.assert_called_once_with("GET", "/accounts/101-001-123456-001")

        account = result["account"]
        assert isinstance(account, Account)
        assert account.id == "101-001-123456-001"
        assert account.alias == "Primary"
        assert account.currency == "USD"
        assert account.balance == Decimal("100000.0000")
        assert account.margin_rate == Decimal("0.02")
        assert account.nav == Decimal("100012.3400")
        assert account.hedging_enabled is False
        assert account.open_trade_count == 1
        assert account.trades == []
        assert account.positions == []
        assert account.orders == []
        assert result["lastTransactionID"] == "5678"
        assert result.last_transaction_id == "5678"

    @pytest.mark.asyncio
    async def test_get_account_summary(self, accounts, mock_client):
        """Test that get_account_summary hits the summary URL and parses AccountSummary."""
        result = await accounts.get_account_summary("101-001-123456-001")

        mock_client._request.assert_called_once_with("GET", "/accounts/101-001-123456-001/summary")

        summary = result["account"]
        assert isinstance(summary, AccountSummary)
        assert summary.id == "101-001-123456-001"
        assert summary.currency == "USD"
        assert summary.balance == Decimal("100000.0000")
        assert summary.unrealized_pl == Decimal("12.3400")
        assert summary.margin_available == Decimal("99792.3400")
        assert summary.pl == Decimal("150.2500")
        assert summary.last_transaction_id == "5678"
        assert result["lastTransactionID"] == "5678"
        assert result.last_transaction_id == "5678"


INSTRUMENT_PAYLOAD = {
    "name": "EUR_USD",
    "type": "CURRENCY",
    "displayName": "EUR/USD",
    "pipLocation": -4,
    "displayPrecision": 5,
    "tradeUnitsPrecision": 0,
    "minimumTradeSize": "1",
    "maximumTrailingStopDistance": "1.00000",
    "minimumTrailingStopDistance": "0.00050",
    "maximumPositionSize": "0",
    "maximumOrderUnits": "100000000",
    "marginRate": "0.02",
}


class TestAccountInstrumentEndpoints:
    """Test suite for get_account_instruments."""

    @pytest.fixture
    def mock_client(self):
        """Create a mock async client returning an instrument payload."""
        client = MagicMock()

        async def mock_request(method, path, **kwargs):
            mock_response = MagicMock()
            mock_response.json.return_value = {
                "instruments": [INSTRUMENT_PAYLOAD],
                "lastTransactionID": "4321",
            }
            return mock_response

        client._request = AsyncMock(side_effect=mock_request)
        return client

    @pytest.fixture
    def accounts(self, mock_client):
        """Create AccountEndpoints instance with mock client."""
        return AccountEndpoints(mock_client)

    @pytest.mark.asyncio
    async def test_get_account_instruments_without_filter(self, accounts, mock_client):
        """Test that get_account_instruments sends no params when unfiltered."""
        result = await accounts.get_account_instruments("101-001-123456-001")

        mock_client._request.assert_called_once_with("GET", "/accounts/101-001-123456-001/instruments", params={})

        instruments = result["instruments"]
        assert len(instruments) == 1
        assert isinstance(instruments[0], Instrument)
        assert str(instruments[0].name) == "EUR_USD"
        assert instruments[0].display_precision == 5
        assert instruments[0].margin_rate == Decimal("0.02")
        assert result["lastTransactionID"] == "4321"

    @pytest.mark.asyncio
    async def test_get_account_instruments_with_filter(self, accounts, mock_client):
        """Test that the instruments filter is comma-joined into params."""
        await accounts.get_account_instruments("101-001-123456-001", instruments=["EUR_USD", "GBP_USD"])

        mock_client._request.assert_called_once_with("GET", "/accounts/101-001-123456-001/instruments", params={"instruments": "EUR_USD,GBP_USD"})


ORDER_RESPONSE_CASES = [
    ("MARKET", "MarketOrder", {"instrument": "EUR_USD", "units": "100"}),
    ("LIMIT", "LimitOrder", {"instrument": "EUR_USD", "units": "100", "price": "1.20000"}),
    ("STOP", "StopOrder", {"instrument": "EUR_USD", "units": "100", "price": "1.20000"}),
    ("MARKET_IF_TOUCHED", "MarketIfTouchedOrder", {"instrument": "EUR_USD", "units": "100", "price": "1.20000"}),
    ("TAKE_PROFIT", "TakeProfitOrder", {"tradeID": "2", "price": "1.20000"}),
    ("STOP_LOSS", "StopLossOrder", {"tradeID": "2", "price": "1.10000"}),
    ("GUARANTEED_STOP_LOSS", "GuaranteedStopLossOrder", {"tradeID": "2", "price": "1.10000", "guaranteedExecutionPremium": "0.00020"}),
    ("TRAILING_STOP_LOSS", "TrailingStopLossOrder", {"tradeID": "2", "distance": "0.01000", "trailingStopValue": "1.10000"}),
    ("FIXED_PRICE", "FixedPriceOrder", {"instrument": "EUR_USD", "units": "100", "price": "1.20000", "tradeState": "OPEN"}),
]


@pytest.mark.asyncio
@pytest.mark.parametrize("collection", ["account", "ordersCreated", "ordersCancelled", "ordersFilled", "ordersTriggered"])
@pytest.mark.parametrize(("order_type", "expected_class", "fields"), ORDER_RESPONSE_CASES, ids=[case[0] for case in ORDER_RESPONSE_CASES])
async def test_account_endpoints_preserve_concrete_order_types(collection, order_type, expected_class, fields):
    """Wire discriminators select the same concrete model in every account collection."""
    order = {"id": "10", "createTime": "2024-01-15T12:00:00Z", "state": "PENDING", "type": order_type, **fields}
    if order_type in {"MARKET", "FIXED_PRICE"}:
        order["state"] = "FILLED"
    if collection == "account":
        response_body = {"account": {**ACCOUNT_PAYLOAD, "orders": [order]}, "lastTransactionID": "10"}
    else:
        response_body = {"changes": {collection: [order]}, "state": {}, "lastTransactionID": "10"}

    def handler(request):
        expected_path = "/accounts/101-001-123456-001" + ("" if collection == "account" else "/changes")
        assert request.method == "GET"
        assert request.url.path == expected_path
        if collection != "account":
            assert request.url.params["sinceTransactionID"] == "9"
        return httpx.Response(200, json=response_body)

    transport = httpx.AsyncClient(transport=httpx.MockTransport(handler), base_url="https://api.example.test")
    async with AsyncClient(token="synthetic-token", account_id="101-001-123456-001", transport=transport) as client:
        if collection == "account":
            response = await client.accounts.get_account("101-001-123456-001")
            container = response["account"]
            parsed_order = container.orders[0]
            wire_collection = "orders"
        else:
            response = await client.accounts.get_account_changes("101-001-123456-001", since_transaction_id="9")
            container = response["changes"]
            parsed_order = getattr(container, collection)[0]
            wire_collection = collection

    assert type(parsed_order).__name__ == expected_class
    assert parsed_order.type == order_type
    if order_type == "GUARANTEED_STOP_LOSS":
        assert not hasattr(parsed_order, "guaranteed")
    dumped = container.model_dump(by_alias=True, exclude_unset=True)
    assert dumped[wire_collection] == [order]
    reparsed = type(container).model_validate_json(container.model_dump_json(by_alias=True))
    assert type(getattr(reparsed, wire_collection)[0]).__name__ == expected_class
    assert getattr(reparsed, wire_collection)[0] == parsed_order


@pytest.mark.asyncio
async def test_get_account_changes_preserves_fill_details_and_nested_serialization():
    """A fill retains monetary amounts and nested trade details through the public HTTP path."""
    transaction = {
        "id": "6360",
        "type": "ORDER_FILL",
        "time": "2024-01-15T12:00:00Z",
        "userID": 1,
        "accountID": "101-001-123456-001",
        "batchID": "6359",
        "orderID": "6359",
        "instrument": "USD_CAD",
        "units": "-100",
        "price": "1.28324",
        "reason": "MARKET_ORDER",
        "pl": "0.00000",
        "financing": "0.00000",
        "accountBalance": "43650.78835",
        "tradeOpened": {"tradeID": "6360", "units": "-100", "price": "1.28324", "initialMarginRequired": "2.50"},
    }
    response_body = {"changes": {"transactions": [transaction]}, "state": {}, "lastTransactionID": "6360"}
    transport = httpx.AsyncClient(transport=httpx.MockTransport(lambda request: httpx.Response(200, json=response_body)), base_url="https://api.example.test")
    async with AsyncClient(token="synthetic-token", account_id="101-001-123456-001", transport=transport) as client:
        response = await client.accounts.get_account_changes("101-001-123456-001", since_transaction_id="6359")

    changes = response["changes"]
    fill = changes.transactions[0]
    assert isinstance(fill, OrderFillTransaction)
    assert fill.units == Decimal("-100")
    assert fill.account_balance == Decimal("43650.78835")
    assert fill.trade_opened.initial_margin_required == Decimal("2.50")
    assert changes.model_dump(by_alias=True, exclude_unset=True) == {"transactions": [transaction]}
    assert changes["transactions"][0]["tradeOpened"]["price"] == "1.28324"
    reparsed = AccountChanges.model_validate_json(changes.model_dump_json(by_alias=True))
    assert isinstance(reparsed.transactions[0], OrderFillTransaction)
    assert reparsed.transactions[0] == fill


@pytest.mark.parametrize(("collection", "invalid_type"), [("ordersCreated", "NOT_AN_ORDER"), ("transactions", "NOT_A_TRANSACTION")])
def test_account_changes_reject_unknown_discriminators(collection, invalid_type):
    """Unknown variants fail explicitly instead of masquerading as a known base model."""
    with pytest.raises(ValueError, match=r"Unknown (order|transaction) type"):
        AccountChanges.model_validate({collection: [{"type": invalid_type}]})
