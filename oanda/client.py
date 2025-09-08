"""OANDA API client implementations."""

import asyncio
import json
import queue
import sys
import threading
from typing import TYPE_CHECKING, Any, Dict, Optional, AsyncIterator, Iterator
from time import monotonic

import httpx

from ._internal.environment import Environment
from ._internal.utils import (
    backoff_with_jitter, 
    build_user_agent, 
    stringify_decimals,
    MonotonicTimeout,
)
from .exceptions import raise_for_oanda, StreamStall
from .endpoints.accounts import AccountEndpoints
from .endpoints.orders import OrderEndpoints  
from .endpoints.pricing import PricingEndpoints
from ._models import ClientPrice, PricingHeartbeat

if TYPE_CHECKING:
    from logging import Logger


class AsyncClient:
    """
    Async OANDA API client.
    
    This is the primary interface to the OANDA API. Use this for async code.
    """
    
    def __init__(
        self,
        token: str,
        *,
        environment: Environment = Environment.PRACTICE,
        timeout: float = 30.0,
        max_retries: int = 3,
        transport: Optional[httpx.AsyncClient] = None,
        user_agent: Optional[str] = None,
        proxies: Optional[str] = None,
        verify: bool | str = True,
        cert: Optional[str] = None,
        logger: Optional["Logger"] = None,
    ):
        """
        Initialize the async client.
        
        Args:
            token: OANDA API token
            environment: API environment (practice or live)
            timeout: Request timeout in seconds
            max_retries: Maximum retry attempts
            transport: Custom httpx client (optional)
            user_agent: Custom user agent (optional)
            proxies: Proxy URL (optional)
            verify: SSL verification (True, False, or path to CA bundle)
            cert: Client certificate path (optional)
            logger: Logger instance (optional)
        """
        self._token = token  # Never log this!
        self._logger = logger
        self._environment = environment
        self.timeout = timeout
        self.max_retries = max_retries
        
        # Setup HTTP client
        if transport:
            self._http = transport
        else:
            # Build httpx client with proper types
            client_kwargs = {
                "base_url": environment.base_url,
                "headers": {
                    "Accept": "application/json",
                    "Accept-Encoding": "gzip",
                    "User-Agent": user_agent or build_user_agent(),
                },
                "timeout": httpx.Timeout(
                    connect=5.0,
                    read=timeout,
                    write=10.0,
                    pool=timeout,
                ),
                "http2": False,  # Optional, requires h2 package
                "trust_env": True,
                "verify": verify,
                "limits": httpx.Limits(
                    max_connections=100,
                    max_keepalive_connections=20,
                ),
            }
            
            # Add optional parameters if provided 
            if proxies is not None:
                client_kwargs["proxies"] = proxies
            if cert is not None:
                client_kwargs["cert"] = cert
                
            self._http = httpx.AsyncClient(**client_kwargs)  # type: ignore[arg-type]
        
        # Initialize endpoints
        self.accounts = AccountEndpoints(self)
        self.orders = OrderEndpoints(self)
        self.pricing = PricingEndpoints(self)
    
    async def __aenter__(self) -> "AsyncClient":
        return self
    
    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        await self.aclose()
    
    async def aclose(self) -> None:
        """Close the HTTP client."""
        await self._http.aclose()
    
    def _log(self, level: str, msg: str, **extra: Any) -> None:
        """Log with token redaction."""
        if self._logger:
            # Redact sensitive headers
            if "headers" in extra:
                headers = extra["headers"].copy()
                if "Authorization" in headers:
                    headers["Authorization"] = "Bearer ***"
                extra["headers"] = headers
            
            getattr(self._logger, level)(msg, **extra)
    
    async def _request(
        self,
        method: str,
        path: str,
        *,
        timeout: Optional[float] = None,
        retries: Optional[int] = None,
        idempotency_key: Optional[str] = None,
        params: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> httpx.Response:
        """
        Make an HTTP request with retries and error handling.
        
        Args:
            method: HTTP method
            path: Request path (relative to base URL)
            timeout: Request timeout override
            retries: Retry count override
            idempotency_key: Idempotency key for writes
            params: Query parameters
            json_data: JSON request body
            **kwargs: Additional httpx arguments
            
        Returns:
            HTTP response
            
        Raises:
            OandaError: On API errors
        """
        max_tries = retries if retries is not None else self.max_retries
        headers = kwargs.pop("headers", {})
        
        # Add standard headers (never log the token!)
        headers["Authorization"] = f"Bearer {self._token}"
        if idempotency_key:
            headers["Idempotency-Key"] = idempotency_key
        
        # Convert Decimals to strings in JSON data
        if json_data:
            json_data = stringify_decimals(json_data)
        
        # Only retry writes if idempotency key provided
        is_write = method in {"POST", "PUT", "PATCH", "DELETE"}
        allow_retry = not is_write or bool(idempotency_key)
        
        for attempt in range(max_tries):
            try:
                self._log("debug", f"{method} {path}", extra={
                    "method": method,
                    "path": path,
                    "attempt": attempt + 1,
                    "headers": headers,
                    "params": params,
                })
                
                response = await self._http.request(
                    method,
                    path,
                    timeout=timeout or self.timeout,
                    headers=headers,
                    params=params,
                    json=json_data,
                    **kwargs,
                )
                
                # Check for retryable errors
                if response.status_code in {429, 502, 503, 504} and allow_retry:
                    if attempt < max_tries - 1:  # Don't sleep on final attempt
                        retry_after = response.headers.get("Retry-After")
                        if retry_after:
                            delay = float(retry_after)
                        else:
                            delay = backoff_with_jitter(attempt)
                        
                        self._log("warning", f"Retrying after {delay:.2f}s", extra={
                            "status": response.status_code,
                            "attempt": attempt + 1,
                            "delay": delay,
                        })
                        await asyncio.sleep(delay)
                        continue
                
                # Raise for any HTTP errors
                raise_for_oanda(response)
                return response
                
            except httpx.TimeoutException as e:
                if attempt < max_tries - 1:
                    delay = backoff_with_jitter(attempt)
                    self._log("warning", f"Timeout, retrying after {delay:.2f}s", extra={
                        "attempt": attempt + 1,
                        "delay": delay,
                    })
                    await asyncio.sleep(delay)
                    continue
                else:
                    self._log("error", "Request timeout", extra={"attempts": attempt + 1})
                    raise
        
        # This should never be reached, but satisfies mypy
        raise RuntimeError("Request retries exhausted")
    
    async def _stream(
        self,
        path: str,
        *,
        params: Optional[Dict[str, Any]] = None,
        timeout: Optional[float] = None,
        stall_timeout: float = 30.0,
    ) -> AsyncIterator[str]:
        """
        Stream data from an endpoint.
        
        Args:
            path: Stream endpoint path
            params: Query parameters
            timeout: Request timeout
            stall_timeout: Maximum time without data before raising StreamStall
            
        Yields:
            Raw lines from the stream
            
        Raises:
            StreamStall: If no data received within stall_timeout
        """
        headers = {"Authorization": f"Bearer {self._token}"}
        stall_timer = MonotonicTimeout(stall_timeout)
        
        try:
            async with self._http.stream(
                "GET",
                path,
                params=params,
                headers=headers,
                timeout=timeout or self.timeout,
            ) as response:
                raise_for_oanda(response)
                
                async for line in response.aiter_lines():
                    if not line.strip():
                        # Empty line - check for stall
                        if stall_timer.expired:
                            raise StreamStall(f"No data for {stall_timeout}s")
                        continue
                    
                    # Reset stall timer on data
                    stall_timer = MonotonicTimeout(stall_timeout)
                    yield line
                    
        except httpx.TimeoutException:
            raise StreamStall("Stream timed out")
        except httpx.ConnectError as e:
            raise StreamStall(f"Stream connection failed: {e}")


class Client:
    """
    Sync OANDA API client.
    
    This is a thread-safe wrapper around AsyncClient. Not thread-safe itself - 
    use one instance per thread.
    """
    
    def __init__(self, **kwargs: Any) -> None:
        """
        Initialize sync client.
        
        Accepts same arguments as AsyncClient.
        """
        self._async = AsyncClient(**kwargs)
        self._loop = asyncio.new_event_loop()
        self._thread = threading.Thread(target=self._loop.run_forever, daemon=True)
        self._thread.start()
        
        # Create sync endpoint proxies
        self.accounts = _SyncEndpointProxy(self, "accounts")
        self.orders = _SyncEndpointProxy(self, "orders")
        self.pricing = _SyncPricingProxy(self)
    
    def __enter__(self) -> "Client":
        return self
    
    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        self.close()
    
    def close(self) -> None:
        """Close the client and clean up resources."""
        # Close async client
        fut = asyncio.run_coroutine_threadsafe(self._async.aclose(), self._loop)
        try:
            fut.result(timeout=5.0)
        except asyncio.TimeoutError:
            pass
        
        # Stop event loop
        self._loop.call_soon_threadsafe(self._loop.stop)
        
        # Wait for thread to finish
        if self._thread.is_alive():
            self._thread.join(timeout=5.0)
    
    def _run(self, coro: Any) -> Any:
        """Run async coroutine in background thread."""
        future = asyncio.run_coroutine_threadsafe(coro, self._loop)
        return future.result()


class _SyncEndpointProxy:
    """Proxy that converts async endpoint methods to sync."""
    
    def __init__(self, client: Client, endpoint_name: str) -> None:
        self._client = client
        self._async_endpoint = getattr(client._async, endpoint_name)
    
    def __getattr__(self, name: str) -> Any:
        async_method = getattr(self._async_endpoint, name)
        
        def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
            return self._client._run(async_method(*args, **kwargs))
        
        return sync_wrapper


class _SyncPricingProxy(_SyncEndpointProxy):
    """Special pricing proxy with sync streaming support."""
    
    def __init__(self, client: Client) -> None:
        super().__init__(client, "pricing")
    
    def stream_iter(self, account_id: str, instruments: list[str]) -> Iterator[ClientPrice | PricingHeartbeat]:
        """
        Stream prices (blocking iterator).
        
        Safe for slow consumers with bounded queue backpressure.
        
        Args:
            account_id: Account to stream for
            instruments: List of instruments to stream
            
        Yields:
            Price or heartbeat events
            
        Raises:
            OandaError: On API errors
            StreamStall: On stream stall
        """
        q: queue.Queue[object] = queue.Queue(maxsize=1024)
        
        async def _pump() -> None:
            try:
                async for event in self._async_endpoint.stream(account_id, instruments):
                    try:
                        q.put_nowait(event)
                    except queue.Full:
                        # Backpressure: drop old events or wait briefly
                        await asyncio.sleep(0.001)
            except Exception as e:
                q.put(e)  # Pass exceptions to consumer
            finally:
                q.put(StopIteration)
        
        # Start pump task in background loop
        self._client._loop.call_soon_threadsafe(
            lambda: asyncio.create_task(_pump())
        )
        
        # Consume from thread-safe queue
        while True:
            item = q.get()
            if item is StopIteration:
                break
            if isinstance(item, Exception):
                raise item
            # Type narrowing: we know this is ClientPrice or PricingHeartbeat from async stream
            yield item  # type: ignore[misc]