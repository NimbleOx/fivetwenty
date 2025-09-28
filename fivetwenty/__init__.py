"""
OANDA REST API v20 Python SDK

A simple, elegant Python client for OANDA's REST API v20.

Usage:
    import asyncio
    from fivetwenty import Client, AsyncClient, Environment, AccountConfig

    # Method 1: Direct parameters
    async def main():
        async with AsyncClient(token="your-token", account_id="your-account-id", environment=Environment.PRACTICE) as client:
            accounts = await client.accounts.list()

    asyncio.run(main())

    # Method 2: Configuration object
    config = AccountConfig(
        token="your-token",
        account_id="your-account-id",
        environment=Environment.PRACTICE,
        alias="my_account"
    )

    async def main():
        async with AsyncClient(config=config) as client:
            accounts = await client.accounts.list()

    asyncio.run(main())

    # Method 3: Environment variables (fallback)
    # Set FIVETWENTY_OANDA_TOKEN, FIVETWENTY_OANDA_ACCOUNT, etc.
    async def main():
        async with AsyncClient() as client:
            accounts = await client.accounts.list()

    asyncio.run(main())

    # Sync wrapper (same patterns)
    with Client(token="your-token", account_id="your-account-id") as client:
        accounts = client.accounts.list()
"""

try:
    from importlib.metadata import version

    __version__ = version("fivetwenty")
except ImportError:
    # Fallback for development installs
    __version__ = "0.1.1"

from ._internal.environment import Environment
from .client import AsyncClient, Client
from .configuration import AccountConfig, AccountConfigLoader, ConfigValidator
from .exceptions import FiveTwentyError, StreamStall
from .models import ErrorCategory, ErrorDetails, ErrorSeverity, FiveTwentyErrorCode, ValidationViolation

__all__ = [
    # Configuration
    "AccountConfig",
    "AccountConfigLoader",
    # Main clients
    "AsyncClient",
    "Client",
    "ConfigValidator",
    # Enums
    "Environment",
    # Error handling
    "ErrorCategory",
    "ErrorDetails",
    "ErrorSeverity",
    # Exceptions
    "FiveTwentyError",
    "FiveTwentyErrorCode",
    "StreamStall",
    "ValidationViolation",
    # Version
    "__version__",
]
