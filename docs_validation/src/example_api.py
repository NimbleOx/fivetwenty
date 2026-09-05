"""Deterministic OANDA HTTP fixtures shared by documentation and script checks.

These payloads exercise the real SDK. They cover example scenarios, not every
server rule or account-specific trading restriction.
"""

import json
import re
from collections.abc import Callable
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from typing import Any

import httpx

ACCOUNT_ID = "101-001-1234567-001"
TOKEN = "example-script-test-token"
USER_ID = 1234567
ANCHOR = datetime(2024, 6, 3, 12, 0, 0, tzinfo=timezone.utc)
STREAM_TICKS = 40

BASE_PRICES = {
    "EUR_USD": Decimal("1.10000"),
    "GBP_USD": Decimal("1.27000"),
    "AUD_USD": Decimal("0.66000"),
    "NZD_USD": Decimal("0.61000"),
    "USD_CAD": Decimal("1.36000"),
    "USD_CHF": Decimal("0.89000"),
    "USD_JPY": Decimal("157.000"),
    "EUR_JPY": Decimal("170.000"),
    "GBP_JPY": Decimal("199.000"),
    "EUR_GBP": Decimal("0.86000"),
    "XAU_USD": Decimal("2320.00"),
}

GRANULARITY_DELTAS = {
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


def _is_jpy(instrument: str) -> bool:
    return instrument.endswith("JPY")


def pip_size(instrument: str) -> Decimal:
    return Decimal("0.010") if _is_jpy(instrument) else Decimal("0.00010")


def _base(instrument: str) -> Decimal:
    return BASE_PRICES.get(instrument, Decimal("1.10000"))


def format_price(instrument: str, value: Decimal) -> str:
    return str(value.quantize(pip_size(instrument) / 10))


def format_timestamp(moment: datetime) -> str:
    return moment.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.000000000Z")


def _enum_value(raw: str) -> str:
    """Require wire values; Python enum member names are not API parameters."""
    if "." in raw:
        raise ValueError(f"Expected an enum wire value, received {raw!r}")
    return raw


def _instruments_param(params: httpx.QueryParams) -> list[str]:
    return [_enum_value(name) for name in params.get("instruments", "EUR_USD").split(",") if name]


def _candle(instrument: str, moment: datetime, offset: int) -> dict[str, Any]:
    step = pip_size(instrument)
    open_price = _base(instrument) + step * (offset % 7)
    close_price = open_price + step * (1 if offset % 2 else -1)
    prices = {
        "o": format_price(instrument, open_price),
        "h": format_price(instrument, max(open_price, close_price) + step * 2),
        "l": format_price(instrument, min(open_price, close_price) - step * 2),
        "c": format_price(instrument, close_price),
    }
    return {"time": format_timestamp(moment), "volume": 100 + offset, "complete": True, "mid": prices, "bid": prices, "ask": prices}


def _candles_response(instrument: str, params: httpx.QueryParams) -> dict[str, Any]:
    instrument = _enum_value(instrument)
    granularity = _enum_value(params.get("granularity", "S5"))
    delta = GRANULARITY_DELTAS.get(granularity, timedelta(seconds=5))
    count = min(int(params.get("count", "60")), 500)
    candles = [_candle(instrument, ANCHOR - delta * offset, offset) for offset in range(count, 0, -1)]
    return {"instrument": instrument, "granularity": granularity, "candles": candles}


def _client_price(instrument: str, tick: int) -> dict[str, Any]:
    spread = pip_size(instrument) * 2
    mid = _base(instrument) + pip_size(instrument) * (tick % 9)
    return {
        "type": "PRICE",
        "instrument": instrument,
        "time": format_timestamp(ANCHOR + timedelta(seconds=tick)),
        "tradeable": True,
        "status": "tradeable",
        "bids": [{"price": format_price(instrument, mid - spread / 2), "liquidity": 10000000}],
        "asks": [{"price": format_price(instrument, mid + spread / 2), "liquidity": 10000000}],
        "closeoutBid": format_price(instrument, mid - spread),
        "closeoutAsk": format_price(instrument, mid + spread),
    }


def _account_summary() -> dict[str, Any]:
    return {
        "id": ACCOUNT_ID,
        "alias": "Example Practice",
        "currency": "USD",
        "balance": "100000.0000",
        "createdByUserID": USER_ID,
        "createdTime": format_timestamp(ANCHOR - timedelta(days=365)),
        "guaranteedStopLossOrderMode": "DISABLED",
        "marginRate": "0.02",
        "openTradeCount": 1,
        "openPositionCount": 1,
        "pendingOrderCount": 1,
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
            "averagePrice": format_price(instrument, _base(instrument)),
            "tradeIDs": ["6791"],
            "pl": "150.2500",
            "unrealizedPL": "12.3400",
            "resettablePL": "150.2500",
            "financing": "-3.5000",
            "dividendAdjustment": "0.0000",
            "guaranteedExecutionFees": "0.0000",
        },
        "short": {
            "units": "0",
            "pl": "0.0000",
            "unrealizedPL": "0.0000",
            "resettablePL": "0.0000",
            "financing": "0.0000",
            "dividendAdjustment": "0.0000",
            "guaranteedExecutionFees": "0.0000",
        },
    }


def _instrument(instrument: str) -> dict[str, Any]:
    return {
        "name": instrument,
        "type": "CURRENCY",
        "displayName": instrument.replace("_", "/"),
        "pipLocation": -2 if _is_jpy(instrument) else -4,
        "displayPrecision": 3 if _is_jpy(instrument) else 5,
        "tradeUnitsPrecision": 0,
        "minimumTradeSize": "1",
        "maximumTrailingStopDistance": "1.00000",
        "minimumTrailingStopDistance": "0.00050",
        "maximumPositionSize": "0",
        "maximumOrderUnits": "100000000",
        "marginRate": "0.02",
    }


def _trade(trade_id: str, instrument: str = "EUR_USD") -> dict[str, Any]:
    return {
        "id": trade_id,
        "instrument": instrument,
        "price": format_price(instrument, _base(instrument)),
        "openTime": format_timestamp(ANCHOR - timedelta(hours=2)),
        "state": "OPEN",
        "initialUnits": "1000",
        "currentUnits": "1000",
        "realizedPL": "0.0000",
        "unrealizedPL": "12.3400",
        "marginUsed": "220.0000",
        "financing": "0.0000",
        "dividendAdjustment": "0.0000",
        "initialMarginRequired": "220.0000",
    }


def _order(order_id: str, instrument: str = "EUR_USD") -> dict[str, Any]:
    return {
        "id": order_id,
        "createTime": format_timestamp(ANCHOR - timedelta(hours=1)),
        "state": "PENDING",
        "type": "LIMIT",
        "instrument": instrument,
        "units": "1000",
        "price": format_price(instrument, _base(instrument) - pip_size(instrument) * 50),
        "timeInForce": "GTC",
        "triggerCondition": "DEFAULT",
        "partialFill": "DEFAULT_FILL",
        "positionFill": "DEFAULT",
    }


def _transaction_base(transaction_id: str, transaction_type: str) -> dict[str, Any]:
    return {
        "id": transaction_id,
        "time": format_timestamp(ANCHOR),
        "userID": USER_ID,
        "accountID": ACCOUNT_ID,
        "batchID": transaction_id,
        "type": transaction_type,
    }


def _order_fill_transaction(transaction_id: str, instrument: str, units: str, price: str) -> dict[str, Any]:
    return _transaction_base(transaction_id, "ORDER_FILL") | {
        "orderID": "6789",
        "instrument": instrument,
        "units": units,
        "requestedUnits": units,
        "price": price,
        "fullVWAP": price,
        "reason": "MARKET_ORDER",
        "pl": "1.2500",
        "quotePL": "1.2500",
        "financing": "0.0000",
        "baseFinancing": "0.0000",
        "commission": "0.0000",
        "guaranteedExecutionFee": "0.0000",
        "quoteGuaranteedExecutionFee": "0.0000",
        "accountBalance": "100000.0000",
        "halfSpreadCost": "0.0500",
        "tradeOpened": {"tradeID": "6791", "units": units, "price": price, "initialMarginRequired": "220.0000", "halfSpreadCost": "0.0500"},
        "tradesClosed": [{"tradeID": "6790", "units": units, "price": price, "realizedPL": "1.2500", "financing": "0.0000", "halfSpreadCost": "0.0500"}],
    }


def _order_cancel_transaction(transaction_id: str) -> dict[str, Any]:
    return _transaction_base(transaction_id, "ORDER_CANCEL") | {"orderID": "6789", "reason": "CLIENT_REQUEST"}


def _order_response(body: dict[str, Any]) -> dict[str, Any]:
    order = body.get("order", {})
    instrument = order.get("instrument", "EUR_USD")
    units = str(order.get("units", "1000"))
    price = str(order.get("price") or format_price(instrument, _base(instrument)))
    order_type = order.get("type", "MARKET")
    create = _transaction_base("6789", f"{order_type}_ORDER") | {
        "instrument": instrument,
        "units": units,
        "timeInForce": order.get("timeInForce", "FOK"),
        "reason": "CLIENT_ORDER",
        "triggerCondition": "DEFAULT",
        "partialFill": "DEFAULT_FILL",
        "positionFill": "DEFAULT",
    }
    if order_type != "MARKET":
        create["price"] = price
    if "tradeID" in order:
        create["tradeID"] = order["tradeID"]
    response: dict[str, Any] = {"orderCreateTransaction": create, "relatedTransactionIDs": ["6789"], "lastTransactionID": "6790"}
    if order_type == "MARKET":
        response["orderFillTransaction"] = _order_fill_transaction("6790", instrument, units, price)
        response["relatedTransactionIDs"] = ["6789", "6790"]
    return response


def _close_response(instrument: str, units: str) -> dict[str, Any]:
    price = format_price(instrument, _base(instrument))
    return {
        "longOrderCreateTransaction": _transaction_base("6800", "MARKET_ORDER") | {"instrument": instrument, "units": units, "timeInForce": "FOK", "reason": "POSITION_CLOSEOUT", "positionFill": "REDUCE_ONLY"},
        "longOrderFillTransaction": _order_fill_transaction("6801", instrument, units, price),
        "relatedTransactionIDs": ["6800", "6801"],
        "lastTransactionID": "6801",
    }


def _account_changes() -> dict[str, Any]:
    return {
        "changes": {
            "ordersCreated": [],
            "ordersCancelled": [],
            "ordersFilled": [],
            "ordersTriggered": [],
            "tradesOpened": [],
            "tradesReduced": [],
            "tradesClosed": [],
            "positions": [_position("EUR_USD")],
            "transactions": [_order_fill_transaction("5678", "EUR_USD", "1000", format_price("EUR_USD", _base("EUR_USD")))],
        },
        "state": {
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
            "balance": "100000.0000",
            "orders": [],
            "trades": [],
            "positions": [],
        },
        "lastTransactionID": "5678",
    }


class MockOandaApi:
    """Routes OANDA v20 REST and streaming requests to canned, schema-valid payloads."""

    def __init__(
        self,
        *,
        candles_response: Callable[[str, httpx.QueryParams], dict[str, Any]] = _candles_response,
        client_price: Callable[[str, int], dict[str, Any]] = _client_price,
        stream_ticks: int = STREAM_TICKS,
    ) -> None:
        self.candles_response = candles_response
        self.client_price = client_price
        self.stream_ticks = stream_ticks
        self.unmocked: list[str] = []
        self.empty_account = False
        self.closed_trades: set[str] = set()
        self.request_count = 0

    def _stream_body(self, params: httpx.QueryParams) -> bytes:
        instruments = _instruments_param(params)
        lines: list[str] = []
        for tick in range(self.stream_ticks):
            lines.extend(json.dumps(self.client_price(instrument, tick)) for instrument in instruments)
            if tick % 10 == 9:
                lines.append(json.dumps({"type": "HEARTBEAT", "time": format_timestamp(ANCHOR + timedelta(seconds=tick))}))
        return ("\n".join(lines) + "\n").encode()

    def _known_route(self, request: httpx.Request) -> bool:
        """Match methods and complete paths before choosing a fixture."""
        if request.url.host not in {"api-fxpractice.oanda.com", "api-fxtrade.oanda.com", "stream-fxpractice.oanda.com", "stream-fxtrade.oanda.com"}:
            return False
        routes = {
            "GET": [
                r"/v3/accounts",
                r"/v3/accounts/[^/]+",
                r"/v3/accounts/[^/]+/(summary|changes|instruments|pricing|candles/latest|positions|openPositions|orders|pendingOrders|trades|openTrades|transactions)",
                r"/v3/accounts/[^/]+/(pricing|transactions)/stream",
                r"/v3/accounts/[^/]+/(orders|trades|positions|transactions)/[^/]+",
                r"/v3/accounts/[^/]+/instruments/[^/]+/candles",
                r"/v3/instruments/[^/]+/(candles|orderBook|positionBook)",
            ],
            "POST": [r"/v3/accounts/[^/]+/orders"],
            "PUT": [r"/v3/accounts/[^/]+/orders/[^/]+", r"/v3/accounts/[^/]+/orders/[^/]+/(cancel|clientExtensions)", r"/v3/accounts/[^/]+/trades/[^/]+/(close|clientExtensions|orders)", r"/v3/accounts/[^/]+/positions/[^/]+/close"],
            "PATCH": [r"/v3/accounts/[^/]+/configuration"],
        }
        return any(re.fullmatch(pattern, request.url.path) for pattern in routes.get(request.method, []))

    def handle(self, request: httpx.Request) -> httpx.Response:  # noqa: PLR0911
        self.request_count += 1
        path = request.url.path.removeprefix("/v3")
        if not self._known_route(request):
            return self._unmocked(request, path)
        params = request.url.params
        segments = [segment for segment in path.split("/") if segment]
        body = json.loads(request.content) if request.content else {}

        if segments[:1] == ["instruments"]:
            if segments[-1:] == ["candles"]:
                return httpx.Response(200, json=self.candles_response(segments[1], params))
            if segments[-1] in {"orderBook", "positionBook"}:
                return httpx.Response(200, json={segments[-1]: {"instrument": segments[1], "time": format_timestamp(ANCHOR), "price": "1.1", "bucketWidth": "0.0005", "buckets": []}})
            return self._unmocked(request, path)

        if path == "/accounts":
            return httpx.Response(200, json={"accounts": [{"id": ACCOUNT_ID, "tags": ["demo"]}]})

        if segments[:1] != ["accounts"] or len(segments) < 2:
            return self._unmocked(request, path)

        tail = segments[2:]
        summary = _account_summary()

        if not tail:
            return httpx.Response(200, json={"account": summary | {"trades": [_trade("6791")], "positions": [_position("EUR_USD")], "orders": [_order("6788")]}, "lastTransactionID": "5678"})
        if tail == ["summary"]:
            return httpx.Response(200, json={"account": summary, "lastTransactionID": "5678"})
        if tail == ["changes"]:
            return httpx.Response(200, json=_account_changes())
        if tail == ["configuration"]:
            return httpx.Response(200, json={"clientConfigureTransaction": _transaction_base("5679", "CLIENT_CONFIGURE") | {"marginRate": "0.02"}, "lastTransactionID": "5679"})
        if tail == ["instruments"]:
            return httpx.Response(200, json={"instruments": [_instrument(name) for name in _instruments_param(params)], "lastTransactionID": "5678"})
        if tail == ["pricing"]:
            return httpx.Response(200, json={"prices": [self.client_price(name, 0) for name in _instruments_param(params)], "time": format_timestamp(ANCHOR)})
        if tail == ["pricing", "stream"]:
            return httpx.Response(200, content=self._stream_body(params), headers={"Content-Type": "application/octet-stream"})
        if tail == ["transactions", "stream"]:
            records = [_transaction_base("5678", "RESET_RESETTABLE_PL"), {"type": "HEARTBEAT", "time": format_timestamp(ANCHOR), "lastTransactionID": "5678"}]
            return httpx.Response(200, content=("\n".join(json.dumps(record) for record in records) + "\n").encode(), headers={"Content-Type": "application/octet-stream"})
        if tail == ["candles", "latest"]:
            specifications = [spec for spec in params.get("candleSpecifications", "EUR_USD:S5:M").split(",") if spec]
            latest = [self.candles_response(spec.split(":")[0], httpx.QueryParams({"granularity": spec.split(":")[1], "count": "10"})) for spec in specifications]
            return httpx.Response(200, json={"latestCandles": latest})
        if tail[:1] == ["instruments"] and tail[-1:] == ["candles"]:
            return httpx.Response(200, json=self.candles_response(tail[1], params))

        if tail[:1] in (["positions"], ["openPositions"]):
            if tail[-1:] == ["close"]:
                return httpx.Response(200, json=_close_response(_enum_value(tail[1]), "-1000"))
            if len(tail) == 2:
                return httpx.Response(200, json={"position": _position(_enum_value(tail[1])), "lastTransactionID": "5678"})
            return httpx.Response(200, json={"positions": [_position("EUR_USD")], "lastTransactionID": "5678"})

        if tail[:1] in (["orders"], ["pendingOrders"]):
            if request.method == "POST" and tail == ["orders"]:
                if str(body.get("order", {}).get("units", "1000")) in {"0", "0.0"}:
                    return httpx.Response(400, json={"errorCode": "UNITS_INVALID", "errorMessage": "The units specified are invalid"})
                return httpx.Response(201, json=_order_response(body))
            if tail[-1:] == ["cancel"]:
                return httpx.Response(200, json={"orderCancelTransaction": _order_cancel_transaction("6795"), "relatedTransactionIDs": ["6795"], "lastTransactionID": "6795"})
            if tail[-1:] == ["clientExtensions"]:
                return httpx.Response(200, json={"orderClientExtensionsModifyTransaction": _transaction_base("6796", "ORDER_CLIENT_EXTENSIONS_MODIFY") | {"orderID": tail[1], "clientExtensionsModify": {"id": "example-order", "tag": "example", "comment": "mocked"}}, "lastTransactionID": "6796"})
            if request.method == "PUT":
                return httpx.Response(201, json={"orderCancelTransaction": _order_cancel_transaction("6797")} | _order_response(body))
            if len(tail) == 2 and tail[0] == "orders":
                return httpx.Response(200, json={"order": _order(tail[1]), "lastTransactionID": "5678"})
            return httpx.Response(200, json={"orders": [] if self.empty_account else [_order("6788")], "lastTransactionID": "5678"})

        if tail[:1] in (["trades"], ["openTrades"]):
            if tail[-1:] == ["close"]:
                self.closed_trades.add(tail[1])
                return httpx.Response(
                    200,
                    json={
                        "orderCreateTransaction": _transaction_base("6810", "MARKET_ORDER") | {"instrument": "EUR_USD", "units": "-1000", "timeInForce": "FOK", "reason": "TRADE_CLOSE", "positionFill": "REDUCE_ONLY"},
                        "orderFillTransaction": _order_fill_transaction("6811", "EUR_USD", "-1000", format_price("EUR_USD", _base("EUR_USD"))),
                        "lastTransactionID": "6811",
                    },
                )
            if tail[-1:] == ["clientExtensions"]:
                return httpx.Response(200, json={"tradeClientExtensionsModifyTransaction": _transaction_base("6812", "TRADE_CLIENT_EXTENSIONS_MODIFY") | {"tradeID": tail[1], "tradeClientExtensionsModify": {"id": "example-trade", "tag": "example", "comment": "mocked"}}, "lastTransactionID": "6812"})
            if tail[-1:] == ["orders"]:
                return httpx.Response(200, json={"lastTransactionID": "6813"})
            if len(tail) == 2 and tail[0] == "trades":
                trade = _trade(tail[1])
                if tail[1] in self.closed_trades:
                    trade.update(state="CLOSED", currentUnits="0")
                return httpx.Response(200, json={"trade": trade, "lastTransactionID": "5678"})
            return httpx.Response(200, json={"trades": [] if self.empty_account else [_trade("6791")], "lastTransactionID": "5678"})

        if tail[:1] == ["transactions"]:
            transactions = [_order_fill_transaction(str(index), "EUR_USD", "1000", format_price("EUR_USD", _base("EUR_USD"))) for index in range(1, 6)]
            if tail[1:] in (["idrange"], ["sinceid"]):
                return httpx.Response(200, json={"transactions": transactions, "lastTransactionID": "5678"})
            if len(tail) == 2:
                return httpx.Response(200, json={"transaction": transactions[0], "lastTransactionID": "5678"})
            return httpx.Response(
                200,
                json={
                    "from": params.get("from", format_timestamp(ANCHOR - timedelta(days=1))),
                    "to": params.get("to", format_timestamp(ANCHOR)),
                    "pageSize": int(params.get("pageSize", "100")),
                    "count": len(transactions),
                    "pages": [f"https://api-fxpractice.oanda.com/v3/accounts/{ACCOUNT_ID}/transactions/idrange?from=1&to=5"],
                    "lastTransactionID": "5678",
                },
            )

        return self._unmocked(request, path)

    def _unmocked(self, request: httpx.Request, path: str) -> httpx.Response:
        message = f"Unexpected HTTP request: {request.method} {request.url.host}{path}"
        self.unmocked.append(message)
        raise AssertionError(message)
