"""OANDA API client implementations."""

import asyncio
import contextlib
import queue
import threading
from collections.abc import AsyncIterator, Iterator
from typing import TYPE_CHECKING, Any, Optional

import httpx

from ._internal.environment import Environment
from ._internal.utils import (
    MonotonicTimeout,
    backoff_with_jitter,
    build_user_agent,
    stringify_decimals,
)
from .configuration import AccountConfig, AccountConfigLoader
from .endpoints.accounts import AccountEndpoints
from .endpoints.instruments import InstrumentEndpoints
from .endpoints.orders import OrderEndpoints
from .endpoints.positions import PositionEndpoints
from .endpoints.pricing import PricingEndpoints
from .endpoints.trades import TradeEndpoints
from .endpoints.transactions import TransactionEndpoints
from .exceptions import StreamStall, raise_for_fivetwenty
from .models import ClientPrice, PricingHeartbeat
from .models.streaming import StreamingConfiguration, StreamState

if TYPE_CHECKING:
    from logging import Logger


class AsyncClient:
    """
    Async FiveTwenty API client.

    This is the primary interface to the OANDA API. Use this for async code.
    """

    def __init__(
        self,
        token: str | None = None,
        *,
        account_id: str | None = None,
        environment: Environment = Environment.PRACTICE,
        config: AccountConfig | None = None,
        timeout: float = 30.0,
        max_retries: int = 3,
        transport: httpx.AsyncClient | None = None,
        user_agent: str | None = None,
        proxies: str | None = None,
        verify: bool | str = True,
        cert: str | None = None,
        logger: Optional["Logger"] = None,
    ):
        """
        Initialize the async client.

        Three initialization patterns are supported:

        1. Direct parameters:
           AsyncClient(token="...", account_id="...", environment=Environment.PRACTICE)

        2. Configuration object:
           config = AccountConfig(token="...", account_id="...", ...)
           AsyncClient(config=config)

        3. Environment variables (fallback):
           AsyncClient()  # Reads FIVETWENTY_* environment variables

        Args:
            token: OANDA API token (if not using config)
            account_id: OANDA account ID (optional, for client convenience)
            environment: API environment (practice or live)
            config: AccountConfig object with credentials
            timeout: Request timeout in seconds
            max_retries: Maximum retry attempts
            transport: Custom httpx client (optional)
            user_agent: Custom user agent (optional)
            proxies: Proxy URL (optional)
            verify: SSL verification (True, False, or path to CA bundle)
            cert: Client certificate path (optional)
            logger: Logger instance (optional)

        Raises:
            ValueError: If no valid configuration is provided
        """
        # Configuration resolution: config object > direct params > env vars
        final_config: AccountConfig | None = None

        if config is not None:
            # Use provided config object
            final_config = config
        elif token is not None:
            # Build config from direct parameters
            from pydantic import SecretStr

            final_config = AccountConfig(
                token=SecretStr(token),
                account_id=SecretStr(account_id or "unknown"),  # account_id is optional for client
                environment=environment,
                alias="direct_params",
            )
        else:
            # Try to load from environment variables
            final_config = AccountConfigLoader.load_default()
            if final_config is None:
                raise ValueError("No configuration provided. Either pass token parameter, config object, or set FIVETWENTY_OANDA_TOKEN/FIVETWENTY_OANDA_ACCOUNT environment variables.")

        # Extract values from final config
        self._token = final_config.token.get_secret_value()  # Never log this!
        self._account_id = final_config.account_id.get_secret_value() if account_id is None else account_id
        self._config = final_config
        self._logger = logger
        self._environment = final_config.environment
        self.timeout = timeout
        self.max_retries = max_retries

        # Setup HTTP client
        if transport:
            self._http = transport
        else:
            # Build httpx client with proper types
            client_kwargs = {
                "base_url": self._environment.base_url,
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
        self.instruments = InstrumentEndpoints(self)
        self.orders = OrderEndpoints(self)
        self.positions = PositionEndpoints(self)
        self.pricing = PricingEndpoints(self)
        self.trades = TradeEndpoints(self)
        self.transactions = TransactionEndpoints(self)

    @property
    def account_id(self) -> str | None:
        """Get the configured account ID (if available)."""
        return self._account_id

    @property
    def config(self) -> AccountConfig | None:
        """Get the account configuration."""
        return self._config

    async def __aenter__(self) -> "AsyncClient":
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        await self.aclose()

    async def aclose(self) -> None:
        """Close the HTTP client."""
        await self._http.aclose()

    async def close(self) -> None:
        """Compatibility alias for aclose()."""
        await self.aclose()

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
        timeout: float | None = None,
        retries: int | None = None,
        idempotency_key: str | None = None,
        params: dict[str, Any] | None = None,
        json_data: dict[str, Any] | None = None,
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
            FiveTwentyError: On API errors
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
                self._log(
                    "debug",
                    f"{method} {path}",
                    extra={
                        "method": method,
                        "path": path,
                        "attempt": attempt + 1,
                        "headers": headers,
                        "params": params,
                    },
                )

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
                if response.status_code in {429, 502, 503, 504} and allow_retry and attempt < max_tries - 1:  # Don't sleep on final attempt
                    retry_after = response.headers.get("Retry-After")
                    delay = float(retry_after) if retry_after else backoff_with_jitter(attempt)

                    self._log(
                        "warning",
                        f"Retrying after {delay:.2f}s",
                        extra={
                            "status": response.status_code,
                            "attempt": attempt + 1,
                            "delay": delay,
                        },
                    )
                    await asyncio.sleep(delay)
                    continue

                # Raise for any HTTP errors
                raise_for_fivetwenty(response)
                return response

            except httpx.TimeoutException:
                if attempt < max_tries - 1:
                    delay = backoff_with_jitter(attempt)
                    self._log(
                        "warning",
                        f"Timeout, retrying after {delay:.2f}s",
                        extra={
                            "attempt": attempt + 1,
                            "delay": delay,
                        },
                    )
                    await asyncio.sleep(delay)
                    continue
                self._log("error", "Request timeout", extra={"attempts": attempt + 1})
                raise

        # This should never be reached, but satisfies mypy
        raise RuntimeError("Request retries exhausted")

    async def _stream(
        self,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        timeout: float | None = None,
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
                raise_for_fivetwenty(response)

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

    async def _stream_with_retries(
        self,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        timeout: float | None = None,
        config: StreamingConfiguration | None = None,
    ) -> AsyncIterator[tuple[str, StreamState]]:
        """
        Stream data with automatic retry logic and connection state tracking.

        Args:
            path: Stream endpoint path
            params: Query parameters
            timeout: Request timeout
            config: Streaming configuration with retry settings

        Yields:
            Tuple of (raw_line, current_stream_state)

        Raises:
            StreamStall: If all retry attempts are exhausted
        """
        if config is None:
            config = StreamingConfiguration()

        attempt = 0
        max_attempts = config.reconnection_policy.max_attempts
        delay = config.reconnection_policy.delay_seconds

        while attempt <= max_attempts:
            try:
                if attempt == 0:
                    current_state = StreamState.CONNECTING
                else:
                    current_state = StreamState.RECONNECTING
                    if attempt > 1:
                        # Add delay before reconnection (except first retry)
                        await asyncio.sleep(delay)

                # Try to establish stream
                async for line in self._stream(
                    path,
                    params=params,
                    timeout=timeout,
                    stall_timeout=config.stall_timeout,
                ):
                    # First successful line means we're connected
                    if current_state in (StreamState.CONNECTING, StreamState.RECONNECTING):
                        current_state = StreamState.CONNECTED

                    yield line, current_state

                # If we get here, stream ended normally
                current_state = StreamState.DISCONNECTED
                return

            except StreamStall as e:  # noqa: PERF203
                attempt += 1
                current_state = StreamState.RECONNECTING

                if attempt > max_attempts:
                    # Final failure
                    current_state = StreamState.DISCONNECTED
                    raise StreamStall(f"Stream failed after {max_attempts} attempts: {e}")

                # Log retry attempt (optional logging)
                if hasattr(self, "_logger") and self._logger:
                    self._logger.warning(f"Stream stalled, retrying ({attempt}/{max_attempts}): {e}")

        # Should not reach here, but satisfy mypy
        raise StreamStall(f"Stream failed after {max_attempts} attempts")


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
        self.instruments = _SyncEndpointProxy(self, "instruments")
        self.orders = _SyncEndpointProxy(self, "orders")
        self.positions = _SyncEndpointProxy(self, "positions")
        self.pricing = _SyncPricingProxy(self)
        self.trades = _SyncEndpointProxy(self, "trades")
        self.transactions = _SyncEndpointProxy(self, "transactions")

    @property
    def account_id(self) -> str | None:
        """Get the configured account ID (if available)."""
        return self._async.account_id

    @property
    def config(self) -> AccountConfig | None:
        """Get the account configuration."""
        return self._async.config

    def __enter__(self) -> "Client":
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        self.close()

    def close(self) -> None:
        """Close the client and clean up resources."""
        # Close async client
        fut = asyncio.run_coroutine_threadsafe(self._async.aclose(), self._loop)
        with contextlib.suppress(asyncio.TimeoutError):
            fut.result(timeout=5.0)

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
            FiveTwentyError: On API errors
            StreamStall: On stream stall
        """
        q: queue.Queue[object] = queue.Queue(maxsize=1024)

        async def _pump() -> None:
            try:
                async for event in self._async_endpoint.get_pricing_stream(account_id, instruments):
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
        self._client._loop.call_soon_threadsafe(lambda: asyncio.create_task(_pump()))

        # Consume from thread-safe queue
        while True:
            item = q.get()
            if item is StopIteration:
                break
            if isinstance(item, Exception):
                raise item
            # Type narrowing: we know this is ClientPrice or PricingHeartbeat from async stream
            yield item  # type: ignore[misc]
