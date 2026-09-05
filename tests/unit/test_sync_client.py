"""Unit tests for the sync Client wrapper and _SyncPricingProxy.stream_iter."""

import asyncio
import threading
from collections.abc import AsyncIterator, Callable

import httpx
import pytest

from fivetwenty import Client
from fivetwenty._internal.environment import Environment
from fivetwenty.models import ClientPrice, PricingHeartbeat


def build_client(handler: Callable[[httpx.Request], httpx.Response] | None = None) -> Client:
    """Build a sync Client whose AsyncClient routes REST calls through a MockTransport."""
    active_handler = handler or (lambda request: httpx.Response(200, json={"ok": True}))
    transport_client = httpx.AsyncClient(transport=httpx.MockTransport(active_handler), base_url="https://api.example.test")
    return Client(token="secret-token", account_id="acct-1", transport=transport_client)


def make_price(instrument: str) -> ClientPrice:
    return ClientPrice.model_validate(
        {
            "type": "PRICE",
            "instrument": instrument,
            "closeoutBid": "1.1000",
            "closeoutAsk": "1.1002",
        }
    )


def make_heartbeat() -> PricingHeartbeat:
    return PricingHeartbeat.model_validate({"type": "HEARTBEAT", "time": "2026-01-01T00:00:00Z"})


class TestSyncClientBridge:
    """Sync endpoint calls are bridged to the background event loop thread."""

    def test_sync_endpoint_call_returns_parsed_data(self) -> None:
        requests: list[httpx.Request] = []

        def handler(request: httpx.Request) -> httpx.Response:
            requests.append(request)
            return httpx.Response(200, json={"accounts": [{"id": "001-001-1234567-001", "tags": ["demo"]}]})

        with build_client(handler) as client:
            accounts = client.accounts.get_accounts()

        assert len(accounts) == 1
        assert accounts[0].id == "001-001-1234567-001"
        assert accounts[0].tags == ["demo"]
        assert len(requests) == 1
        assert requests[0].url.path == "/accounts"
        assert requests[0].headers["Authorization"] == "Bearer secret-token"

    def test_sync_endpoint_call_propagates_api_errors(self) -> None:
        from fivetwenty.exceptions import FiveTwentyError

        def handler(request: httpx.Request) -> httpx.Response:
            return httpx.Response(401, json={"errorCode": "INVALID_TOKEN", "errorMessage": "Invalid authorization token"})

        with build_client(handler) as client:
            with pytest.raises(FiveTwentyError) as exc_info:
                client.accounts.get_accounts()

        assert exc_info.value.status == 401

    def test_properties_delegate_to_async_client(self) -> None:
        with build_client() as client:
            assert client.account_id == "acct-1"
            assert client.config.environment is Environment.PRACTICE
            assert client._environment is Environment.PRACTICE


class TestSyncClientLifecycle:
    """Context manager and close() shut down the background thread."""

    def test_context_manager_stops_background_thread(self) -> None:
        client = build_client()
        with client:
            assert client._thread.is_alive()
        assert not client._thread.is_alive()

    def test_explicit_close_stops_background_thread(self) -> None:
        client = build_client()
        assert client._thread.is_alive()
        client.close()
        assert not client._thread.is_alive()

    def test_close_is_idempotent(self) -> None:
        client = build_client()
        client.close()
        client.close()  # must not hang or raise
        assert not client._thread.is_alive()

    def test_endpoint_call_after_close_raises_instead_of_hanging(self) -> None:
        """Regression: calling through a closed client used to hang forever
        (run_coroutine_threadsafe against a stopped-but-not-closed loop never
        resolves), instead of failing immediately as the fail-hard policy requires."""
        client = build_client()
        client.close()

        with pytest.raises(RuntimeError, match="Client is closed"):
            client.accounts.get_accounts()

    def test_stream_iter_after_close_raises_instead_of_hanging(self) -> None:
        client = build_client()
        client.close()

        with pytest.raises(RuntimeError, match="Client is closed"):
            next(client.pricing.stream_iter("acct-1", ["EUR_USD"]))


class TestStreamIter:
    """Tests for _SyncPricingProxy.stream_iter."""

    def test_stream_iter_yields_events_in_order_and_terminates(self, monkeypatch: pytest.MonkeyPatch) -> None:
        heartbeat = make_heartbeat()
        price_one = make_price("EUR_USD")
        price_two = make_price("GBP_USD")
        received: list[tuple[str, list[str]]] = []

        async def fake_stream(account_id: str, instruments: list[str]) -> AsyncIterator[ClientPrice | PricingHeartbeat]:
            received.append((account_id, instruments))
            for event in (heartbeat, price_one, price_two):
                yield event

        client = build_client()
        try:
            monkeypatch.setattr(client._async.pricing, "get_pricing_stream", fake_stream)

            events = list(client.pricing.stream_iter("acct-1", ["EUR_USD", "GBP_USD"]))
        finally:
            client.close()

        assert events == [heartbeat, price_one, price_two]
        assert received == [("acct-1", ["EUR_USD", "GBP_USD"])]

    def test_stream_iter_consumer_can_break_early_and_close_cleanly(self, monkeypatch: pytest.MonkeyPatch) -> None:
        async def fake_stream(account_id: str, instruments: list[str]) -> AsyncIterator[ClientPrice | PricingHeartbeat]:
            for _ in range(5):
                yield make_heartbeat()

        client = build_client()
        try:
            monkeypatch.setattr(client._async.pricing, "get_pricing_stream", fake_stream)

            first_events = []
            for event in client.pricing.stream_iter("acct-1", ["EUR_USD"]):
                first_events.append(event)
                break
        finally:
            client.close()

        assert len(first_events) == 1
        assert isinstance(first_events[0], PricingHeartbeat)
        assert not client._thread.is_alive()

    def test_stream_iter_propagates_exception_from_async_generator(self, monkeypatch: pytest.MonkeyPatch) -> None:
        heartbeat = make_heartbeat()

        async def fake_stream(account_id: str, instruments: list[str]) -> AsyncIterator[ClientPrice | PricingHeartbeat]:
            yield heartbeat
            raise ValueError("stream exploded")

        client = build_client()
        try:
            monkeypatch.setattr(client._async.pricing, "get_pricing_stream", fake_stream)

            iterator = client.pricing.stream_iter("acct-1", ["EUR_USD"])
            assert next(iterator) == heartbeat
            with pytest.raises(ValueError, match="stream exploded"):
                next(iterator)
        finally:
            client.close()

    def test_stream_iter_backpressure_drops_oldest_events(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Under backpressure, delivered events stay in produced order and the newest
        data is never the one dropped -- regardless of exactly how the background
        pump and the consumer happen to interleave.

        A fixed sleep to "let the pump race ahead" before consuming was flaky
        (stream_iter is a generator: nothing, not even queue construction, runs
        until first iterated, so the sleep raced nothing) and pinning an exact
        surviving set assumes a specific winner of a genuine two-thread race,
        which isn't guaranteed across Python versions/runners -- empirically the
        pump (a zero-await async generator) usually finishes producing before the
        consumer's first blocking get() succeeds, but that's a scheduling detail,
        not a contract. These two invariants hold no matter who wins.
        """
        import queue as queue_module

        class TinyQueue(queue_module.Queue):  # type: ignore[type-arg]
            def __init__(self, maxsize: int = 0) -> None:
                super().__init__(maxsize=2)

        prices = [make_price(f"PAIR_{i}") for i in range(5)]

        async def fake_stream(account_id: str, instruments: list[str]) -> AsyncIterator[ClientPrice | PricingHeartbeat]:
            for price in prices:
                yield price

        client = build_client()
        try:
            monkeypatch.setattr(client._async.pricing, "get_pricing_stream", fake_stream)
            monkeypatch.setattr("fivetwenty.client.queue.Queue", TinyQueue)
            events = list(client.pricing.stream_iter("acct-1", ["EUR_USD"]))
        finally:
            client.close()

        indices = [prices.index(e) for e in events]
        assert indices == sorted(indices), f"events delivered out of order: {indices}"
        assert len(set(indices)) == len(indices), f"duplicate events delivered: {indices}"
        assert events[-1] == prices[-1], "the most recent event must never be the one evicted"
        assert 1 <= len(events) <= len(prices)


@pytest.mark.parametrize("close_client", [False, True])
def test_closing_active_sync_stream_releases_the_http_response(close_client):
    closed = threading.Event()

    class LiveBody(httpx.AsyncByteStream):
        async def __aiter__(self):
            yield b'{"type":"HEARTBEAT","time":"2024-01-01T00:00:00Z"}\n'
            await asyncio.Event().wait()

        async def aclose(self):
            closed.set()

    client = build_client(lambda request: httpx.Response(200, stream=LiveBody()))
    stream = client.pricing.stream_iter("acct-1", ["EUR_USD"])
    try:
        assert isinstance(next(stream), PricingHeartbeat)
        if close_client:
            client.close()
        else:
            stream.close()
        assert closed.wait(timeout=1), "Closing a sync stream must close its active HTTP response"
    finally:
        if not client._closed:

            def cancel_tasks():
                for task in asyncio.all_tasks(client._loop):
                    task.cancel()

            client._loop.call_soon_threadsafe(cancel_tasks)
            closed.wait(timeout=1)
        stream.close()
        client.close()
    assert not client._thread.is_alive()
    assert client._loop.is_closed()


@pytest.mark.parametrize("stream_error", [False, True])
def test_sync_shutdown_does_not_block_on_a_full_unconsumed_queue(monkeypatch, stream_error):
    import queue as queue_module

    class TinyQueue(queue_module.Queue):
        def __init__(self, maxsize=0):
            super().__init__(maxsize=2)

    release = asyncio.Event()
    produced = threading.Event()

    async def fake_stream(account_id, instruments):
        yield make_heartbeat()
        await release.wait()
        for _ in range(3):
            yield make_heartbeat()
        produced.set()
        if stream_error:
            raise ValueError("full-queue failure")

    with build_client() as client:
        monkeypatch.setattr(client._async.pricing, "get_pricing_stream", fake_stream)
        monkeypatch.setattr("fivetwenty.client.queue.Queue", TinyQueue)
        stream = client.pricing.stream_iter("acct-1", ["EUR_USD"])
        try:
            next(stream)
            client._loop.call_soon_threadsafe(release.set)
            assert produced.wait(timeout=1)
            # The worker must remain responsive even without a queue consumer.
            asyncio.run_coroutine_threadsafe(asyncio.sleep(0), client._loop).result(timeout=1)
            client.close()
            assert not client._thread.is_alive()
            if stream_error:
                with pytest.raises(ValueError, match="full-queue failure"):
                    list(stream)
            else:
                assert len(list(stream)) == 2
        finally:
            stream.close()
