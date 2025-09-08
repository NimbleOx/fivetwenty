"""
OANDA REST API v20 Python SDK

A simple, elegant Python client for OANDA's REST API v20.

Usage:
    from oanda import Client, AsyncClient, Environment

    # Async (recommended)
    async with AsyncClient(token="your-token") as client:
        accounts = await client.accounts.list()
        
    # Sync wrapper
    with Client(token="your-token") as client:
        accounts = client.accounts.list()
"""

__version__ = "20.1.0"

from .client import AsyncClient, Client
from .exceptions import OandaError, StreamStall
from ._internal.environment import Environment

__all__ = [
    # Main clients
    "AsyncClient",
    "Client", 
    
    # Exceptions
    "OandaError",
    "StreamStall",
    
    # Enums
    "Environment",
    
    # Version
    "__version__",
]