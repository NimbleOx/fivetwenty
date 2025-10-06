"""Unit tests for account configuration endpoints."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from fivetwenty.endpoints.accounts import AccountEndpoints


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
            json={"alias": "My Trading Account"},
        )

    @pytest.mark.asyncio
    async def test_update_configuration_margin_rate_only(self, accounts, mock_client):
        """Test updating account configuration with margin rate only."""
        await accounts.patch_account_configuration("101-001-123456-001", margin_rate="0.05")

        mock_client._request.assert_called_once_with(
            "PATCH",
            "/accounts/101-001-123456-001/configuration",
            json={"marginRate": "0.05"},
        )

    @pytest.mark.asyncio
    async def test_update_configuration_both_parameters(self, accounts, mock_client):
        """Test updating account configuration with both alias and margin rate."""
        await accounts.patch_account_configuration("101-001-123456-001", alias="Professional Account", margin_rate="0.02")

        mock_client._request.assert_called_once_with(
            "PATCH",
            "/accounts/101-001-123456-001/configuration",
            json={"alias": "Professional Account", "marginRate": "0.02"},
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
                json={"alias": alias},
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
                json={"marginRate": margin_rate},
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
            json={"alias": "Final Account Name", "marginRate": "0.025"},
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
            json={"alias": long_alias},
        )
