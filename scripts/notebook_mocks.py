"""Offline OANDA v20 stand-in used by ``poe docs-validate-notebooks``.

``install()`` is called from a setup cell that the notebook runner injects at the
top of a throwaway copy of each notebook. Every ``httpx`` client built afterwards
(the REST client the SDK holds, plus the short-lived ones ``AsyncClient._stream``
creates per connection) is routed through an ``httpx.MockTransport``, so the
notebook cells drive the real endpoint, model, and streaming code paths without
reaching OANDA or placing orders.
"""

from __future__ import annotations

import json
import os
import random
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from typing import Any

import httpx

ACCOUNT_ID = "101-001-1234567-001"
TOKEN = "notebook-validation-token"
AUDIT_ENV = "FIVETWENTY_NOTEBOOK_AUDIT"

_ANCHOR = datetime(2024, 6, 3, 12, 0, 0, tzinfo=timezone.utc)
_MAX_CANDLES_PER_PAGE = 500
_STREAM_TICKS_PER_INSTRUMENT = 45

_GRANULARITY_DELTAS = {
    "S5": timedelta(seconds=5),
    "S10": timedelta(seconds=10),
    "S15": timedelta(seconds=15),
    "S30": timedelta(seconds=30),
    "M1": timedelta(minutes=1),
    "M2": timedelta(minutes=2),
    "M4": timedelta(minutes=4),
    "M5": timedelta(minutes=5),
    "M10": timedelta(minutes=10),
    "M15": timedelta(minutes=15),
    "M30": timedelta(minutes=30),
    "H1": timedelta(hours=1),
    "H2": timedelta(hours=2),
    "H3": timedelta(hours=3),
    "H4": timedelta(hours=4),
    "H6": timedelta(hours=6),
    "H8": timedelta(hours=8),
    "H12": timedelta(hours=12),
    "D": timedelta(days=1),
    "W": timedelta(weeks=1),
    "M": timedelta(days=30),
}

_BASE_PRICES = {
    "EUR_USD": Decimal("1.10000"),
    "GBP_USD": Decimal("1.27000"),
    "AUD_USD": Decimal("0.66000"),
    "USD_CAD": Decimal("1.36000"),
    "USD_CHF": Decimal("0.89000"),
    "USD_JPY": Decimal("157.000"),
    "EUR_JPY": Decimal("170.000"),
    "GBP_JPY": Decimal("199.000"),
}

_SERIES_CACHE: dict[tuple[str, int], list[Decimal]] = {}


def _is_jpy(instrument: str) -> bool:
    return instrument.endswith("JPY")


def _pip(instrument: str) -> Decimal:
    return Decimal("0.010") if _is_jpy(instrument) else Decimal("0.00010")


def _precision(instrument: str) -> int:
    return 3 if _is_jpy(instrument) else 5


def _series(instrument: str, length: int) -> list[Decimal]:
    """Deterministic Decimal random walk, seeded per instrument."""
    cached = _SERIES_CACHE.get((instrument, length))
    if cached is not None:
        return cached

    rng = random.Random(instrument)
    value = _BASE_PRICES.get(instrument, Decimal("1.10000"))
    step = _pip(instrument)
    floor = value / 2
    series: list[Decimal] = []
    for _ in range(length):
        value = max(floor, value + step * rng.randint(-4, 4))
        series.append(value)
    _SERIES_CACHE[(instrument, length)] = series
    return series


def _format(instrument: str, value: Decimal) -> str:
    return str(value.quantize(_pip(instrument) / 10))


def _rfc3339(moment: datetime) -> str:
    return moment.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.000000000Z")


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
    step = _pip(instrument)
    candles = []
    for index, moment in enumerate(times):
        open_price = prices[index]
        close_price = prices[index + 1]
        high = max(open_price, close_price) + step * 2
        low = min(open_price, close_price) - step * 2
        candles.append(
            {
                "time": _rfc3339(moment),
                "volume": 100 + index % 400,
                "complete": True,
                "mid": {
                    "o": _format(instrument, open_price),
                    "h": _format(instrument, high),
                    "l": _format(instrument, low),
                    "c": _format(instrument, close_price),
                },
            }
        )
    return candles


def _candles_response(instrument: str, params: httpx.QueryParams) -> dict[str, Any]:
    granularity = params.get("granularity", "S5")
    delta = _GRANULARITY_DELTAS.get(granularity, timedelta(seconds=5))
    from_time = _parse_time(params.get("from"))
    to_time = _parse_time(params.get("to"))

    if from_time is not None:
        include_first = params.get("includeFirst", "true") == "true"
        start = from_time if include_first else from_time + delta
        limit = to_time or start + delta * _MAX_CANDLES_PER_PAGE
        times = []
        moment = start
        while moment <= limit and len(times) < _MAX_CANDLES_PER_PAGE:
            times.append(moment)
            moment += delta
    else:
        count = min(int(params.get("count", "500")), 5000)
        times = [_ANCHOR - delta * offset for offset in range(count, 0, -1)]

    return {
        "instrument": instrument,
        "granularity": granularity,
        "candles": _candles(instrument, times),
    }


def _client_price(instrument: str, tick: int) -> dict[str, Any]:
    prices = _series(instrument, _STREAM_TICKS_PER_INSTRUMENT + 1)
    mid = prices[tick % len(prices)]
    spread = _pip(instrument) * 2
    bid = mid - spread / 2
    ask = mid + spread / 2
    return {
        "type": "PRICE",
        "instrument": instrument,
        "time": _rfc3339(_ANCHOR + timedelta(seconds=tick)),
        "tradeable": True,
        "bids": [{"price": _format(instrument, bid), "liquidity": 10000000}],
        "asks": [{"price": _format(instrument, ask), "liquidity": 10000000}],
        "closeoutBid": _format(instrument, bid - spread),
        "closeoutAsk": _format(instrument, ask + spread),
    }


def _account_summary() -> dict[str, Any]:
    return {
        "id": ACCOUNT_ID,
        "alias": "Notebook Practice",
        "currency": "USD",
        "balance": "100000.0000",
        "createdByUserID": 1234567,
        "createdTime": _rfc3339(_ANCHOR - timedelta(days=365)),
        "guaranteedStopLossOrderMode": "DISABLED",
        "marginRate": "0.02",
        "openTradeCount": 1,
        "openPositionCount": 1,
        "pendingOrderCount": 0,
        "hedgingEnabled": False,
        "unrealizedPL": "12.3400",
        "NAV": "100012.3400",
        "marginUsed": "220.0000",
        "marginAvailable": "99792.3400",
        "positionValue": "11000.0000",
        "marginCloseoutUnrealizedPL": "11.9800",
        "marginCloseoutNAV": "100011.9800",
        "marginCloseoutMarginUsed": "220.0000",
        "marginCloseoutPercent": "0.00110",
        "marginCloseoutPositionValue": "11000.0000",
        "withdrawalLimit": "99792.3400",
        "marginCallMarginUsed": "220.0000",
        "marginCallPercent": "0.00110",
        "pl": "150.2500",
        "resettablePL": "150.2500",
        "financing": "-3.5000",
        "commission": "0.0000",
        "dividendAdjustment": "0.0000",
        "guaranteedExecutionFees": "0.0000",
        "lastTransactionID": "5678",
    }


def _position(instrument: str) -> dict[str, Any]:
    return {
        "instrument": instrument,
        "pl": "150.2500",
        "unrealizedPL": "12.3400",
        "marginUsed": "220.0000",
        "resettablePL": "150.2500",
        "financing": "-3.5000",
        "commission": "0.0000",
        "dividendAdjustment": "0.0000",
        "guaranteedExecutionFees": "0.0000",
        "long": {
            "units": "1000",
            "averagePrice": _format(instrument, _BASE_PRICES.get(instrument, Decimal("1.10000"))),
            "tradeIDs": ["101"],
            "pl": "150.2500",
            "unrealizedPL": "12.3400",
            "resettablePL": "150.2500",
        },
        "short": {
            "units": "0",
            "pl": "0.0000",
            "unrealizedPL": "0.0000",
            "resettablePL": "0.0000",
        },
    }


def _instrument(instrument: str) -> dict[str, Any]:
    return {
        "name": instrument,
        "type": "CURRENCY",
        "displayName": instrument.replace("_", "/"),
        "pipLocation": -2 if _is_jpy(instrument) else -4,
        "displayPrecision": _precision(instrument),
        "tradeUnitsPrecision": 0,
        "minimumTradeSize": "1",
        "maximumTrailingStopDistance": "1.00000",
        "minimumTrailingStopDistance": "0.00050",
        "maximumPositionSize": "0",
        "maximumOrderUnits": "100000000",
        "marginRate": "0.02",
    }


def _transaction(transaction_id: int, instrument: str = "EUR_USD") -> dict[str, Any]:
    return {
        "id": str(transaction_id),
        "time": _rfc3339(_ANCHOR - timedelta(minutes=transaction_id)),
        "userID": 1234567,
        "accountID": ACCOUNT_ID,
        "batchID": str(transaction_id),
        "type": "ORDER_FILL",
        "orderID": str(transaction_id),
        "instrument": instrument,
        "units": "1000",
        "price": _format(instrument, _BASE_PRICES[instrument]),
        "reason": "MARKET_ORDER",
        "pl": "1.2500",
        "financing": "0.0000",
        "commission": "0.0000",
        "accountBalance": "100000.0000",
    }


def _trade(trade_id: str, instrument: str = "EUR_USD") -> dict[str, Any]:
    return {
        "id": trade_id,
        "instrument": instrument,
        "price": _format(instrument, _BASE_PRICES[instrument]),
        "openTime": _rfc3339(_ANCHOR - timedelta(hours=2)),
        "state": "OPEN",
        "initialUnits": "1000",
        "currentUnits": "1000",
        "realizedPL": "0.0000",
        "unrealizedPL": "12.3400",
        "marginUsed": "220.0000",
        "financing": "0.0000",
        "dividendAdjustment": "0.0000",
    }


def _order_fill(body: dict[str, Any]) -> dict[str, Any]:
    order = body.get("order", {})
    instrument = order.get("instrument", "EUR_USD")
    units = order.get("units", "1000")
    fill_price = order.get("price") or _format(instrument, _BASE_PRICES.get(instrument, Decimal("1.10000")))
    return {
        "orderCreateTransaction": {
            "id": "6789",
            "time": _rfc3339(_ANCHOR),
            "userID": 1234567,
            "accountID": ACCOUNT_ID,
            "batchID": "6789",
            "type": "MARKET_ORDER" if order.get("type") != "LIMIT" else "LIMIT_ORDER",
            "instrument": instrument,
            "units": units,
            "timeInForce": order.get("timeInForce", "FOK"),
            "reason": "CLIENT_ORDER",
        },
        "orderFillTransaction": {
            "id": "6790",
            "time": _rfc3339(_ANCHOR),
            "userID": 1234567,
            "accountID": ACCOUNT_ID,
            "batchID": "6789",
            "type": "ORDER_FILL",
            "orderID": "6789",
            "instrument": instrument,
            "units": units,
            "price": fill_price,
            "reason": "MARKET_ORDER",
            "pl": "0.0000",
            "financing": "0.0000",
            "commission": "0.0000",
            "accountBalance": "100000.0000",
            "tradeOpened": {
                "tradeID": "6791",
                "units": units,
                "price": fill_price,
                "initialMarginRequired": "220.0000",
            },
        },
        "relatedTransactionIDs": ["6789", "6790"],
        "lastTransactionID": "6790",
    }


def _stream_body(params: httpx.QueryParams) -> bytes:
    instruments = [name for name in params.get("instruments", "EUR_USD").split(",") if name]
    lines: list[str] = []
    for tick in range(_STREAM_TICKS_PER_INSTRUMENT):
        lines.extend(json.dumps(_client_price(instrument, tick)) for instrument in instruments)
        if tick % 10 == 9:
            lines.append(json.dumps({"type": "HEARTBEAT", "time": _rfc3339(_ANCHOR + timedelta(seconds=tick))}))
    return ("\n".join(lines) + "\n").encode()


def _unmocked(method: str, path: str) -> httpx.Response:
    """Record the gap so the runner fails loudly instead of the notebook swallowing a 404."""
    audit = os.environ.get(AUDIT_ENV)
    if audit:
        with open(audit, "a", encoding="utf-8") as handle:  # noqa: PTH123
            handle.write(f"{method} {path}\n")
    return httpx.Response(404, json={"errorMessage": f"unmocked path: {method} {path}"})


def _handle(request: httpx.Request) -> httpx.Response:  # noqa: PLR0911
    path = request.url.path.removeprefix("/v3")
    params = request.url.params
    segments = [segment for segment in path.split("/") if segment]

    if segments[:1] == ["instruments"] and segments[-1:] == ["candles"]:
        return httpx.Response(200, json=_candles_response(segments[1], params))

    if path == "/accounts":
        return httpx.Response(200, json={"accounts": [{"id": ACCOUNT_ID, "tags": ["demo"]}]})

    if segments[:1] != ["accounts"] or len(segments) < 2:
        return _unmocked(request.method, path)

    tail = segments[2:]

    if not tail or tail == ["summary"]:
        return httpx.Response(200, json={"account": _account_summary() | {"trades": [], "positions": [_position("EUR_USD")], "orders": []}, "lastTransactionID": "5678"})

    if tail == ["instruments"]:
        requested = [name for name in params.get("instruments", "EUR_USD").split(",") if name]
        return httpx.Response(200, json={"instruments": [_instrument(name) for name in requested], "lastTransactionID": "5678"})

    if tail == ["pricing"]:
        requested = [name for name in params.get("instruments", "EUR_USD").split(",") if name]
        return httpx.Response(200, json={"prices": [_client_price(name, 0) for name in requested], "time": _rfc3339(_ANCHOR)})

    if tail == ["pricing", "stream"]:
        return httpx.Response(200, content=_stream_body(params), headers={"Content-Type": "application/x-ndjson"})

    if tail[:1] == ["instruments"] and tail[-1:] == ["candles"]:
        return httpx.Response(200, json=_candles_response(tail[1], params))

    if tail[:1] in (["positions"], ["openPositions"]):
        if tail[-1:] == ["close"]:
            return httpx.Response(200, json={"lastTransactionID": "5678"})
        if len(tail) == 2 and tail[0] == "positions":
            return httpx.Response(200, json={"position": _position(tail[1]), "lastTransactionID": "5678"})
        return httpx.Response(200, json={"positions": [_position("EUR_USD")], "lastTransactionID": "5678"})

    if tail[:1] in (["orders"], ["pendingOrders"]):
        if request.method == "POST" and tail == ["orders"]:
            return httpx.Response(201, json=_order_fill(json.loads(request.content or b"{}")))
        return httpx.Response(200, json={"orders": [], "lastTransactionID": "5678"})

    if tail[:1] in (["trades"], ["openTrades"]):
        if tail[-1:] in (["orders"], ["clientExtensions"], ["close"]):
            return httpx.Response(200, json={"lastTransactionID": "5678"})
        if len(tail) == 1:
            return httpx.Response(200, json={"trades": [_trade("6791")], "lastTransactionID": "5678"})
        return httpx.Response(200, json={"trade": _trade(tail[1]), "lastTransactionID": "5678"})

    if tail[:1] == ["transactions"]:
        if tail[1:] in (["idrange"], ["sinceid"]):
            return httpx.Response(200, json={"transactions": [_transaction(index) for index in range(1, 6)], "lastTransactionID": "5678"})
        if len(tail) == 2:
            return httpx.Response(200, json={"transaction": _transaction(int(tail[1]) if tail[1].isdigit() else 1), "lastTransactionID": "5678"})
        return httpx.Response(
            200,
            json={
                "from": params.get("from", _rfc3339(_ANCHOR - timedelta(days=1))),
                "to": params.get("to", _rfc3339(_ANCHOR)),
                "pageSize": int(params.get("pageSize", "100")),
                "count": 5,
                "pages": [f"https://api-fxpractice.oanda.com/v3/accounts/{ACCOUNT_ID}/transactions/idrange?from=1&to=5"],
                "lastTransactionID": "5678",
            },
        )

    return _unmocked(request.method, path)


def install() -> None:
    """Force every httpx client created from here on through the mock transport."""
    os.environ.setdefault("FIVETWENTY_OANDA_TOKEN", TOKEN)
    os.environ.setdefault("FIVETWENTY_OANDA_ACCOUNT", ACCOUNT_ID)

    transport = httpx.MockTransport(_handle)
    for client_class in (httpx.AsyncClient, httpx.Client):
        if getattr(client_class, "_fivetwenty_mocked", False):
            continue
        original_init = client_class.__init__

        def patched_init(self: Any, *args: Any, _original_init: Any = original_init, **kwargs: Any) -> None:
            kwargs["transport"] = transport
            _original_init(self, *args, **kwargs)

        client_class.__init__ = patched_init  # type: ignore[method-assign]
        client_class._fivetwenty_mocked = True  # type: ignore[attr-defined]
