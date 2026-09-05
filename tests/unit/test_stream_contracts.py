"""Stream framing, malformed records and cancellation through real SDK methods."""

import asyncio
import json
from unittest.mock import Mock

import httpx
import pytest

from fivetwenty import AsyncClient
from fivetwenty.models import ClientPrice, PricingHeartbeat, TransactionHeartbeat


@pytest.mark.parametrize("endpoint", ["pricing", "transactions"])
async def test_stream_decodes_split_records_and_recovers_after_invalid_data(endpoint):
    heartbeat = {"type": "HEARTBEAT", "time": "2024-01-01T00:00:00Z"}
    if endpoint == "transactions":
        heartbeat["lastTransactionID"] = "42"
    records = ["not json", json.dumps({"type": "HEARTBEAT", "time": "bad"}), json.dumps({"type": "FUTURE_MESSAGE"}), json.dumps(heartbeat)]
    if endpoint == "pricing":
        records.append(json.dumps({"type": "PRICE", "instrument": "EUR_USD", "bids": [], "asks": [], "closeoutBid": "1.2345", "closeoutAsk": "1.2347"}))
    raw = ("\r\n".join(records) + "\r\n").encode()

    class Chunks(httpx.AsyncByteStream):
        closed = False

        async def __aiter__(self):
            for offset in range(0, len(raw), 7):
                yield raw[offset : offset + 7]

        async def aclose(self):
            self.closed = True

    body = Chunks()
    requests = []

    def handler(request):
        requests.append(request)
        return httpx.Response(200, stream=body)

    logger = Mock()
    transport = httpx.AsyncClient(transport=httpx.MockTransport(handler))
    async with AsyncClient(token="offline-token", account_id="offline", transport=transport, logger=logger) as client:
        if endpoint == "pricing":
            stream = client.pricing.get_pricing_stream("offline", ["EUR_USD"], include_home_conversions=True, stall_timeout=17)
        else:
            stream = client.transactions.get_transactions_stream("offline", stall_timeout=17)
        events = [event async for event in stream]
    assert isinstance(events[0], PricingHeartbeat if endpoint == "pricing" else TransactionHeartbeat)
    assert len(events) == (2 if endpoint == "pricing" else 1)
    if endpoint == "pricing":
        assert isinstance(events[1], ClientPrice)
        assert requests[0].url.params["includeHomeConversions"] == "true"
    assert logger.warning.call_count >= 2
    assert requests[0].url.path == f"/v3/accounts/offline/{endpoint}/stream"
    assert body.closed


async def test_async_stream_cancellation_closes_the_response_without_reconnecting():
    started = asyncio.Event()
    closed = asyncio.Event()
    requests = []

    class WaitingBody(httpx.AsyncByteStream):
        async def __aiter__(self):
            started.set()
            await asyncio.Event().wait()
            yield b""

        async def aclose(self):
            closed.set()

    def handler(request):
        requests.append(request)
        return httpx.Response(200, stream=WaitingBody())

    transport = httpx.AsyncClient(transport=httpx.MockTransport(handler))
    async with AsyncClient(token="offline-token", account_id="offline", transport=transport) as client:
        stream = client.pricing.stream_pricing_with_retries("offline", ["EUR_USD"])
        task = asyncio.create_task(anext(stream))
        await asyncio.wait_for(started.wait(), timeout=1)
        task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await task
        assert closed.is_set()
        assert len(requests) == 1


@pytest.mark.parametrize("endpoint", ["pricing", "transactions", "retrying_pricing"])
async def test_closing_a_partially_consumed_stream_closes_its_body(endpoint):
    closed = asyncio.Event()

    class Body(httpx.AsyncByteStream):
        async def __aiter__(self):
            yield b'{"type":"HEARTBEAT","time":"2024-01-01T00:00:00Z","lastTransactionID":"42"}\n'
            await asyncio.Event().wait()

        async def aclose(self):
            closed.set()

    transport = httpx.AsyncClient(transport=httpx.MockTransport(lambda request: httpx.Response(200, stream=Body())))
    async with AsyncClient(token="offline-token", account_id="offline", transport=transport) as client:
        if endpoint == "transactions":
            stream = client.transactions.get_transactions_stream("offline")
        elif endpoint == "pricing":
            stream = client.pricing.get_pricing_stream("offline", ["EUR_USD"])
        else:
            stream = client.pricing.stream_pricing_with_retries("offline", ["EUR_USD"])
        await anext(stream)
        await stream.aclose()
        assert closed.is_set(), "aclose() must complete response cleanup before returning"
