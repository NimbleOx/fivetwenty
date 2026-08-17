"""Unit tests for AsyncClient._stream and AsyncClient._stream_with_retries."""

from collections.abc import AsyncIterator
from typing import Any
from unittest.mock import Mock

import httpx
import pytest

from fivetwenty import AsyncClient
from fivetwenty.exceptions import FiveTwentyError, StreamStall
from fivetwenty.models.streaming import ReconnectionPolicy, StreamingConfiguration, StreamState

# _stream opens a fresh httpx.AsyncClient internally, so tests monkeypatch the
# httpx.AsyncClient attribute. Keep a reference to the real class for factories.
REAL_HTTPX_ASYNC_CLIENT = httpx.AsyncClient


def build_client(**kwargs: Any) -> AsyncClient:
    """Build an AsyncClient with an inert REST transport (streaming does not use it)."""
    dummy_transport = REAL_HTTPX_ASYNC_CLIENT(transport=httpx.MockTransport(lambda request: httpx.Response(200)))
    return AsyncClient(token="secret-token", account_id="acct-1", transport=dummy_transport, **kwargs)


def install_stream_transport(
    monkeypatch: pytest.MonkeyPatch,
    handler: Any,
) -> list[httpx.Request]:
    """Route the internally-created streaming httpx.AsyncClient through a MockTransport."""
    requests: list[httpx.Request] = []

    def recording_handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        response = handler(request)
        assert isinstance(response, httpx.Response)
        return response

    def factory(*args: Any, **kwargs: Any) -> httpx.AsyncClient:
        kwargs["transport"] = httpx.MockTransport(recording_handler)
        return REAL_HTTPX_ASYNC_CLIENT(*args, **kwargs)

    monkeypatch.setattr(httpx, "AsyncClient", factory)
    return requests


async def drain(stream: AsyncIterator[Any], into: list[Any] | None = None) -> list[Any]:
    """Consume an async iterator, optionally collecting items into a caller-owned list."""
    collected = into if into is not None else []
    async for item in stream:
        collected.append(item)
    return collected


class ExplodingByteStream(httpx.AsyncByteStream):
    """Async byte stream that yields chunks and then raises."""

    def __init__(self, chunks: list[bytes], exc: Exception) -> None:
        self._chunks = chunks
        self._exc = exc

    async def __aiter__(self) -> AsyncIterator[bytes]:
        for chunk in self._chunks:
            yield chunk
        raise self._exc

    async def aclose(self) -> None:
        return None


class TestStream:
    """Tests for AsyncClient._stream."""

    @pytest.mark.asyncio
    async def test_stream_yields_lines_and_sends_auth_headers(self, monkeypatch: pytest.MonkeyPatch) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            return httpx.Response(200, content=b'{"type":"PRICE"}\n{"type":"HEARTBEAT"}\n')

        requests = install_stream_transport(monkeypatch, handler)

        async with build_client() as client:
            lines = [line async for line in client._stream("/accounts/acct-1/pricing/stream", params={"instruments": "EUR_USD"})]

        assert lines == ['{"type":"PRICE"}', '{"type":"HEARTBEAT"}']
        assert len(requests) == 1
        request = requests[0]
        # Absolute URL is built from Environment.stream_url, not the REST base_url
        assert str(request.url) == "https://stream-fxpractice.oanda.com/v3/accounts/acct-1/pricing/stream?instruments=EUR_USD"
        assert request.headers["Authorization"] == "Bearer secret-token"
        assert request.headers["Accept-Datetime-Format"] == "RFC3339"
        assert request.headers["Accept"] == "application/json"

    @pytest.mark.asyncio
    async def test_stream_skips_blank_lines_without_stalling(self, monkeypatch: pytest.MonkeyPatch) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            return httpx.Response(200, content=b"\nline1\n\nline2\n")

        install_stream_transport(monkeypatch, handler)

        async with build_client() as client:
            lines = [line async for line in client._stream("/accounts/acct-1/pricing/stream", stall_timeout=30.0)]

        assert lines == ["line1", "line2"]

    @pytest.mark.asyncio
    async def test_stream_non_200_raises_fivetwenty_error(self, monkeypatch: pytest.MonkeyPatch) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            return httpx.Response(401, json={"errorCode": "INVALID_TOKEN", "errorMessage": "Invalid authorization token"})

        install_stream_transport(monkeypatch, handler)

        async with build_client() as client:
            with pytest.raises(FiveTwentyError) as exc_info:
                await drain(client._stream("/accounts/acct-1/pricing/stream"))

        assert exc_info.value.status == 401
        assert exc_info.value.code == "INVALID_TOKEN"

    @pytest.mark.asyncio
    async def test_stream_timeout_during_iteration_raises_stream_stall(self, monkeypatch: pytest.MonkeyPatch) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            return httpx.Response(200, stream=ExplodingByteStream([b"line1\n"], httpx.ReadTimeout("read timed out")))

        install_stream_transport(monkeypatch, handler)

        lines: list[str] = []
        async with build_client() as client:
            with pytest.raises(StreamStall, match="Stream timed out"):
                await drain(client._stream("/accounts/acct-1/pricing/stream"), lines)

        assert lines == ["line1"]

    @pytest.mark.asyncio
    async def test_stream_connect_error_raises_stream_stall(self, monkeypatch: pytest.MonkeyPatch) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            raise httpx.ConnectError("connection refused", request=request)

        install_stream_transport(monkeypatch, handler)

        async with build_client() as client:
            with pytest.raises(StreamStall, match="Stream connection failed"):
                await drain(client._stream("/accounts/acct-1/pricing/stream"))

    @pytest.mark.asyncio
    async def test_stream_stall_detected_on_empty_line_after_timeout(self, monkeypatch: pytest.MonkeyPatch) -> None:
        # stall_timeout=0.0 makes the MonotonicTimeout expired immediately, so the
        # first empty line triggers stall detection without any real waiting.
        def handler(request: httpx.Request) -> httpx.Response:
            return httpx.Response(200, content=b"line1\n\n")

        install_stream_transport(monkeypatch, handler)

        lines: list[str] = []
        async with build_client() as client:
            with pytest.raises(StreamStall, match="No data for"):
                await drain(client._stream("/accounts/acct-1/pricing/stream", stall_timeout=0.0), lines)

        assert lines == ["line1"]


# Sentinel-free scripting for _stream_with_retries: each script is one _stream
# call; strings are yielded, exceptions are raised after prior items.
StreamScript = list[str | Exception]


def install_stream_stub(monkeypatch: pytest.MonkeyPatch, client: AsyncClient, scripts: list[StreamScript]) -> list[dict[str, Any]]:
    calls: list[dict[str, Any]] = []

    async def fake_stream(path: str, **kwargs: Any) -> AsyncIterator[str]:
        script = scripts[len(calls)]
        calls.append({"path": path, **kwargs})
        for item in script:
            if isinstance(item, Exception):
                raise item
            yield item

    monkeypatch.setattr(client, "_stream", fake_stream)
    return calls


def fast_config(max_attempts: int = 2) -> StreamingConfiguration:
    return StreamingConfiguration(reconnection_policy=ReconnectionPolicy(max_attempts=max_attempts, delay_seconds=0.0))


class TestStreamWithRetries:
    """Tests for AsyncClient._stream_with_retries."""

    @pytest.mark.asyncio
    async def test_happy_path_yields_lines_with_connected_state(self, monkeypatch: pytest.MonkeyPatch) -> None:
        async with build_client() as client:
            calls = install_stream_stub(monkeypatch, client, [["line1", "line2"]])
            config = StreamingConfiguration(stall_timeout=12.5)

            results = [item async for item in client._stream_with_retries("/stream", params={"a": "b"}, config=config)]

        # The first line after the initial connection carries CONNECTING so
        # consumers can observe the transition; subsequent lines are CONNECTED.
        assert results == [("line1", StreamState.CONNECTING), ("line2", StreamState.CONNECTED)]
        assert len(calls) == 1
        assert calls[0]["path"] == "/stream"
        assert calls[0]["params"] == {"a": "b"}
        assert calls[0]["stall_timeout"] == 12.5

    @pytest.mark.asyncio
    async def test_default_configuration_used_when_config_is_none(self, monkeypatch: pytest.MonkeyPatch) -> None:
        async with build_client() as client:
            calls = install_stream_stub(monkeypatch, client, [["only"]])

            results = [item async for item in client._stream_with_retries("/stream")]

        assert results == [("only", StreamState.CONNECTING)]
        assert calls[0]["stall_timeout"] == StreamingConfiguration().stall_timeout

    @pytest.mark.asyncio
    async def test_stream_stall_triggers_reconnect_and_continues(self, monkeypatch: pytest.MonkeyPatch) -> None:
        logger = Mock()
        async with build_client(logger=logger) as client:
            calls = install_stream_stub(
                monkeypatch,
                client,
                [
                    ["first", StreamStall("stalled")],
                    ["second", "third"],
                ],
            )

            results = [item async for item in client._stream_with_retries("/stream", config=fast_config())]

        # The first line after a recovery is yielded with RECONNECTING — this is
        # how consumers detect that the stream resumed after an interruption.
        assert results == [
            ("first", StreamState.CONNECTING),
            ("second", StreamState.RECONNECTING),
            ("third", StreamState.CONNECTED),
        ]
        assert len(calls) == 2
        assert logger.warning.called

    @pytest.mark.asyncio
    async def test_stream_stall_exhausts_retries_and_raises(self, monkeypatch: pytest.MonkeyPatch) -> None:
        async with build_client() as client:
            calls = install_stream_stub(
                monkeypatch,
                client,
                [[StreamStall("stalled")], [StreamStall("stalled")], [StreamStall("stalled")]],
            )

            with pytest.raises(StreamStall, match="Stream failed after 2 attempts"):
                await drain(client._stream_with_retries("/stream", config=fast_config(max_attempts=2)))

        # Initial connection plus two reconnection attempts
        assert len(calls) == 3

    @pytest.mark.asyncio
    async def test_retryable_http_errors_reconnect(self, monkeypatch: pytest.MonkeyPatch) -> None:
        for status in (500, 502, 503, 408):
            async with build_client() as client:
                calls = install_stream_stub(
                    monkeypatch,
                    client,
                    [
                        [FiveTwentyError(status=status, message="server issue")],
                        ["recovered"],
                    ],
                )

                results = [item async for item in client._stream_with_retries("/stream", config=fast_config())]

            assert results == [("recovered", StreamState.RECONNECTING)], f"status {status} should be retried"
            assert len(calls) == 2, f"status {status} should be retried"

    @pytest.mark.asyncio
    async def test_non_retryable_http_error_raises_immediately(self, monkeypatch: pytest.MonkeyPatch) -> None:
        async with build_client() as client:
            calls = install_stream_stub(
                monkeypatch,
                client,
                [[FiveTwentyError(status=401, code="INVALID_TOKEN", message="bad token")], ["never"]],
            )

            with pytest.raises(FiveTwentyError) as exc_info:
                await drain(client._stream_with_retries("/stream", config=fast_config()))

        assert exc_info.value.status == 401
        assert len(calls) == 1

    @pytest.mark.asyncio
    async def test_unexpected_exception_raises_immediately(self, monkeypatch: pytest.MonkeyPatch) -> None:
        async with build_client() as client:
            calls = install_stream_stub(monkeypatch, client, [[ValueError("boom")], ["never"]])

            with pytest.raises(ValueError, match="boom"):
                await drain(client._stream_with_retries("/stream", config=fast_config()))

        assert len(calls) == 1

    @pytest.mark.asyncio
    async def test_retryable_http_errors_exhaust_into_stream_stall(self, monkeypatch: pytest.MonkeyPatch) -> None:
        logger = Mock()
        async with build_client(logger=logger) as client:
            error_script: StreamScript = [FiveTwentyError(status=503, message="unavailable")]
            calls = install_stream_stub(monkeypatch, client, [error_script, error_script, error_script])

            with pytest.raises(StreamStall, match="Stream failed after 2 attempts"):
                await drain(client._stream_with_retries("/stream", config=fast_config(max_attempts=2)))

        assert len(calls) == 3
        assert logger.warning.called
