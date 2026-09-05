"""Notebook-specific behavior retained by the shared example HTTP fixtures."""

import json
from pathlib import Path

import httpx
import pytest

from scripts.notebook_mocks import ACCOUNT_ID, AUDIT_ENV, NotebookApi


def test_notebook_candle_pagination_retains_time_boundaries() -> None:
    api = NotebookApi()
    params = {"from": "2024-06-03T12:00:00Z", "to": "2024-06-03T18:00:00Z", "granularity": "H2", "includeFirst": "false"}
    with httpx.Client(transport=httpx.MockTransport(api.handle), base_url="https://api-fxpractice.oanda.com/v3") as client:
        instrument = client.get("/instruments/EUR_USD/candles", params=params).json()
        account = client.get(f"/accounts/{ACCOUNT_ID}/instruments/EUR_USD/candles", params=params).json()
    assert account == instrument
    assert [candle["time"] for candle in instrument["candles"]] == ["2024-06-03T14:00:00.000000000Z", "2024-06-03T16:00:00.000000000Z", "2024-06-03T18:00:00.000000000Z"]


def test_notebook_stream_keeps_market_series_and_heartbeats() -> None:
    api = NotebookApi()
    with httpx.Client(transport=httpx.MockTransport(api.handle), base_url="https://stream-fxpractice.oanda.com/v3") as client:
        first = client.get(f"/accounts/{ACCOUNT_ID}/pricing/stream", params={"instruments": "EUR_USD,USD_JPY"})
        repeated = client.get(f"/accounts/{ACCOUNT_ID}/pricing/stream", params={"instruments": "EUR_USD,USD_JPY"})
    assert first.content == repeated.content
    records = [json.loads(line) for line in first.iter_lines()]
    assert sum(record["type"] == "HEARTBEAT" for record in records) == 4
    prices = [record for record in records if record["type"] == "PRICE"]
    assert len(prices) == 90
    assert len({record["bids"][0]["price"] for record in prices if record["instrument"] == "EUR_USD"}) > 1


@pytest.mark.parametrize(("method", "path"), [("POST", "/accounts"), ("GET", "/accounts/unknown/unsupported")])
def test_unsupported_notebook_requests_leave_audit_evidence(monkeypatch: pytest.MonkeyPatch, tmp_path: Path, method: str, path: str) -> None:
    audit = tmp_path / "requests.log"
    monkeypatch.setenv(AUDIT_ENV, str(audit))
    api = NotebookApi()
    with httpx.Client(transport=httpx.MockTransport(api.handle), base_url="https://api-fxpractice.oanda.com/v3") as client, pytest.raises(AssertionError, match="Unexpected HTTP request"):
        client.request(method, path)
    assert audit.read_text().strip() == f"{method} api-fxpractice.oanda.com{path}"
    assert len(api.unmocked) == 1
