"""Simple tests for main client classes."""

from fivetwenty import AsyncClient, Client, Environment


class TestAsyncClientBasic:
    """Test AsyncClient basic functionality."""

    def test_async_client_initialization(self):
        """Test AsyncClient initialization."""
        client = AsyncClient(token="test-token")

        assert client._token == "test-token"
        assert client._environment == Environment.PRACTICE
        assert client.timeout == 30.0

    def test_async_client_with_custom_environment(self):
        """Test AsyncClient with custom environment."""
        client = AsyncClient(token="test-token", environment=Environment.LIVE)

        assert client._environment == Environment.LIVE

    def test_async_client_with_custom_timeout(self):
        """Test AsyncClient with custom timeout."""
        client = AsyncClient(token="test-token", timeout=60.0)

        assert client.timeout == 60.0

    def test_async_client_has_endpoints(self):
        """Test AsyncClient has expected endpoint attributes."""
        client = AsyncClient(token="test-token")

        # Check that endpoint attributes exist (they're created lazily)
        assert hasattr(client, "accounts")
        assert hasattr(client, "orders")
        assert hasattr(client, "trades")
        assert hasattr(client, "positions")
        assert hasattr(client, "pricing")
        assert hasattr(client, "instruments")
        assert hasattr(client, "transactions")


class TestSyncClientBasic:
    """Test sync Client basic functionality."""

    def test_sync_client_initialization(self):
        """Test sync Client initialization."""
        client = Client(token="test-token")

        assert hasattr(client, "_async")
        assert client._async._token == "test-token"

    def test_sync_client_with_custom_parameters(self):
        """Test sync Client with custom parameters."""
        client = Client(token="test-token", environment=Environment.LIVE, timeout=45.0)

        assert client._async._environment == Environment.LIVE
        assert client._async.timeout == 45.0

    def test_sync_client_has_endpoints(self):
        """Test sync Client has expected endpoint attributes."""
        client = Client(token="test-token")

        # Check that endpoint attributes exist
        assert hasattr(client, "accounts")
        assert hasattr(client, "orders")
        assert hasattr(client, "trades")
        assert hasattr(client, "positions")
        assert hasattr(client, "pricing")
        assert hasattr(client, "instruments")
        assert hasattr(client, "transactions")


class TestClientEnvironmentIntegration:
    """Test client integration with environment configuration."""

    def test_client_practice_environment(self):
        """Test client with practice environment."""
        client = AsyncClient(token="test-token", environment=Environment.PRACTICE)
        assert client._environment == Environment.PRACTICE

    def test_client_live_environment(self):
        """Test client with live environment."""
        client = AsyncClient(token="test-token", environment=Environment.LIVE)
        assert client._environment == Environment.LIVE

    def test_client_environment_switching(self):
        """Test creating clients with different environments."""
        practice_client = AsyncClient(token="test-token", environment=Environment.PRACTICE)
        live_client = AsyncClient(token="test-token", environment=Environment.LIVE)

        assert practice_client._environment != live_client._environment


class TestClientConfiguration:
    """Test client configuration options."""

    def test_client_max_retries_configuration(self):
        """Test client max retries configuration."""
        client = AsyncClient(token="test-token", max_retries=5)
        assert client.max_retries == 5

        # Test default
        client_default = AsyncClient(token="test-token")
        assert client_default.max_retries == 3

    def test_client_token_storage(self):
        """Test client stores token securely."""
        token = "secret-token-123"
        client = AsyncClient(token=token)
        assert client._token == token

    def test_client_attributes_exist(self):
        """Test client has expected attributes."""
        client = AsyncClient(token="test-token")

        assert hasattr(client, "_token")
        assert hasattr(client, "_environment")
        assert hasattr(client, "timeout")
        assert hasattr(client, "max_retries")
        assert hasattr(client, "_http")
