"""Notebook market series and transport setup using the shared example API.

The runner injects ``install()`` before notebook cells build HTTP clients. Both
REST and streaming requests exercise the real SDK through a mock transport.
"""

from __future__ import annotations

import os
import random
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from pathlib import Path
from typing import Any

import httpx

from docs_validation.src.example_api import (
    ACCOUNT_ID,
    ANCHOR,
    BASE_PRICES,
    GRANULARITY_DELTAS,
    MockOandaApi,
    format_price,
    format_timestamp,
    pip_size,
)

TOKEN = "notebook-validation-token"
AUDIT_ENV = "FIVETWENTY_NOTEBOOK_AUDIT"
_MAX_CANDLES_PER_PAGE = 500
_STREAM_TICKS_PER_INSTRUMENT = 45
_SERIES_CACHE: dict[tuple[str, int], list[Decimal]] = {}


def _series(instrument: str, length: int) -> list[Decimal]:
    """Deterministic Decimal random walk, seeded per instrument."""
    cached = _SERIES_CACHE.get((instrument, length))
    if cached is not None:
        return cached

    rng = random.Random(instrument)
    value = BASE_PRICES.get(instrument, Decimal("1.10000"))
    step = pip_size(instrument)
    floor = value / 2
    series: list[Decimal] = []
    for _ in range(length):
        value = max(floor, value + step * rng.randint(-4, 4))
        series.append(value)
    _SERIES_CACHE[(instrument, length)] = series
    return series


def _parse_time(raw: str | None) -> datetime | None:
    if not raw:
        return None
    text = raw.replace("Z", "+00:00")
    try:
        parsed = datetime.fromisoformat(text)
    except ValueError:
        return None
    return parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)


def _candles(instrument: str, times: list[datetime]) -> list[dict[str, Any]]:
    prices = _series(instrument, len(times) + 1)
    step = pip_size(instrument)
    candles = []
    for index, moment in enumerate(times):
        open_price = prices[index]
        close_price = prices[index + 1]
        high = max(open_price, close_price) + step * 2
        low = min(open_price, close_price) - step * 2
        candles.append(
            {
                "time": format_timestamp(moment),
                "volume": 100 + index % 400,
                "complete": True,
                "mid": {
                    "o": format_price(instrument, open_price),
                    "h": format_price(instrument, high),
                    "l": format_price(instrument, low),
                    "c": format_price(instrument, close_price),
                },
            }
        )
    return candles


def _candles_response(instrument: str, params: httpx.QueryParams) -> dict[str, Any]:
    granularity = params.get("granularity", "S5")
    delta = GRANULARITY_DELTAS.get(granularity, timedelta(seconds=5))
    from_time = _parse_time(params.get("from"))
    to_time = _parse_time(params.get("to"))

    if from_time is not None:
        include_first = params.get("includeFirst", "true") == "true"
        start = from_time if include_first else from_time + delta
        limit = to_time or start + delta * _MAX_CANDLES_PER_PAGE
        times: list[datetime] = []
        moment = start
        while moment <= limit and len(times) < _MAX_CANDLES_PER_PAGE:
            times.append(moment)
            moment += delta
    else:
        count = min(int(params.get("count", "500")), 5000)
        times = [ANCHOR - delta * offset for offset in range(count, 0, -1)]

    return {
        "instrument": instrument,
        "granularity": granularity,
        "candles": _candles(instrument, times),
    }


def _client_price(instrument: str, tick: int) -> dict[str, Any]:
    prices = _series(instrument, _STREAM_TICKS_PER_INSTRUMENT + 1)
    mid = prices[tick % len(prices)]
    spread = pip_size(instrument) * 2
    bid = mid - spread / 2
    ask = mid + spread / 2
    return {
        "type": "PRICE",
        "instrument": instrument,
        "time": format_timestamp(ANCHOR + timedelta(seconds=tick)),
        "tradeable": True,
        "bids": [{"price": format_price(instrument, bid), "liquidity": 10000000}],
        "asks": [{"price": format_price(instrument, ask), "liquidity": 10000000}],
        "closeoutBid": format_price(instrument, bid - spread),
        "closeoutAsk": format_price(instrument, ask + spread),
    }


class NotebookApi(MockOandaApi):
    """Record unsupported requests even when a notebook catches the exception."""

    def __init__(self) -> None:
        super().__init__(candles_response=_candles_response, client_price=_client_price, stream_ticks=_STREAM_TICKS_PER_INSTRUMENT)

    def _unmocked(self, request: httpx.Request, path: str) -> httpx.Response:
        audit = os.environ.get(AUDIT_ENV)
        if audit:
            with Path(audit).open("a", encoding="utf-8") as handle:
                handle.write(f"{request.method} {request.url.host}{path}\n")
        return super()._unmocked(request, path)


def install() -> None:
    """Force every httpx client created from here on through the mock transport."""
    os.environ.setdefault("FIVETWENTY_OANDA_TOKEN", TOKEN)
    os.environ.setdefault("FIVETWENTY_OANDA_ACCOUNT", ACCOUNT_ID)

    api = NotebookApi()
    transport = httpx.MockTransport(api.handle)
    for client_class in (httpx.AsyncClient, httpx.Client):
        if getattr(client_class, "_fivetwenty_mocked", False):
            continue
        original_init = client_class.__init__

        def patched_init(self: Any, *args: Any, _original_init: Any = original_init, **kwargs: Any) -> None:
            kwargs["transport"] = transport
            _original_init(self, *args, **kwargs)

        client_class.__init__ = patched_init  # type: ignore[method-assign]
        client_class._fivetwenty_mocked = True  # type: ignore[union-attr]
