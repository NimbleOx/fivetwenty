"""Exercise published helpers with real SDK models and independent HTTP responses."""

import ast
import json
import re
from decimal import Decimal
from pathlib import Path

import httpx
import pytest

from fivetwenty import AsyncClient, Environment
from tests.unit.test_documentation_safety import ACCOUNT_ID, TIMESTAMP, _fill

ROOT = Path(__file__).resolve().parents[2]


def definitions(relative_path):
    path = ROOT / relative_path
    if path.suffix == ".py":
        blocks = [path.read_text()]
    else:
        blocks = re.findall(r"```python\n(.*?)\n```", path.read_text(), re.S)
    namespace = {"__name__": "documentation_test"}
    for block in blocks:
        tree = ast.parse(block)
        tree.body = [node for node in tree.body if isinstance(node, (ast.Import, ast.ImportFrom, ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) or (isinstance(node, ast.Assign) and any(isinstance(target, ast.Name) and target.id == "T" for target in node.targets))]
        exec(compile(tree, str(path), "exec"), namespace)
    return namespace


def client_for(handler, environment=Environment.PRACTICE):
    transport = httpx.AsyncClient(transport=httpx.MockTransport(handler), base_url="https://offline.example.test/v3")
    return AsyncClient(token="offline-token", account_id=ACCOUNT_ID, environment=environment, transport=transport)


@pytest.mark.parametrize("filled", [True, False])
async def test_documented_trade_close_requires_a_fill(filled):
    def handler(request):
        assert request.method == "PUT"
        assert request.url.path.endswith("/trades/42/close")
        assert request.content == b""
        payload = {"lastTransactionID": "124"}
        if filled:
            payload["orderFillTransaction"] = _fill("-1")
        return httpx.Response(200, json=payload)

    close = definitions("docs/guides/practical-solutions/close-positions.md")["close_owned_trade"]
    async with client_for(handler) as client:
        if filled:
            assert await close(client, "42") == "124"
        else:
            with pytest.raises(RuntimeError, match="No close fill"):
                await close(client, "42")


async def test_documented_position_close_controls_only_long_side():
    def handler(request):
        assert request.method == "PUT"
        assert request.url.path.endswith("/positions/EUR_USD/close")
        assert json.loads(request.content) == {"longUnits": "ALL", "shortUnits": "NONE"}
        return httpx.Response(200, json={"longOrderFillTransaction": _fill("-1"), "lastTransactionID": "124"})

    close = definitions("docs/guides/practical-solutions/close-positions.md")["close_long_side"]
    async with client_for(handler) as client:
        await close(client, "EUR_USD")


@pytest.mark.parametrize(
    ("page", "name", "field", "value"),
    [
        ("docs/guides/practical-solutions/implement-stop-loss-strategies.md", "set_stop", "stopLoss", {"price": "1.09"}),
        ("docs/tutorials/advanced-orders/dynamic-management.md", "set_trailing_stop", "trailingStopLoss", {"distance": "1.09"}),
    ],
)
async def test_documented_dependent_update_preserves_other_orders(page, name, field, value):
    def handler(request):
        assert request.method == "PUT"
        assert request.url.path.endswith("/trades/42/orders")
        assert json.loads(request.content) == {field: value}
        return httpx.Response(200, json={"lastTransactionID": "124"})

    update = definitions(page)[name]
    async with client_for(handler) as client:
        await update(client, "42", Decimal("1.09"))


@pytest.mark.parametrize(
    ("page", "name", "args"),
    [
        ("docs/guides/practical-solutions/close-positions.md", "close_owned_trade", ("42",)),
        ("docs/guides/practical-solutions/close-positions.md", "close_long_side", ("EUR_USD",)),
        ("docs/guides/practical-solutions/implement-stop-loss-strategies.md", "set_stop", ("42", Decimal("1.09"))),
        ("docs/tutorials/advanced-orders/dynamic-management.md", "set_trailing_stop", ("42", Decimal("0.002"))),
        ("docs/tutorials/advanced-orders/stop-orders-mit.md", "submit_stop", ("EUR_USD", Decimal("1"), Decimal("1.12"))),
    ],
)
async def test_documented_write_helpers_reject_live_before_http(page, name, args):
    def handler(request):
        pytest.fail(f"Unexpected request: {request.method}")

    operation = definitions(page)[name]
    async with client_for(handler, Environment.LIVE) as client:
        with pytest.raises(ValueError, match="practice"):
            await operation(client, *args)


@pytest.mark.parametrize(("series", "expected"), [(list(range(1, 21)), "above"), (list(range(20, 0, -1)), "below"), ([1] * 20, "equal")])
def test_documented_signal_relationship(series, expected):
    signal = definitions("docs/tutorials/basic-trading/strategy-building.md")["moving_average_signal"]
    assert signal([Decimal(value) for value in series]) == expected


@pytest.mark.parametrize(("closes", "short", "long"), [([], 5, 20), ([Decimal("1")] * 20, 0, 20), ([Decimal("1")] * 20, 20, 20)])
def test_documented_signal_rejects_invalid_inputs(closes, short, long):
    signal = definitions("docs/tutorials/basic-trading/strategy-building.md")["moving_average_signal"]
    with pytest.raises(ValueError):
        signal(closes, short, long)


@pytest.mark.parametrize(("conversion", "precision", "expected"), [("1", 0, "66"), ("0.8", 0, "83"), ("0.8", 2, "83.33")])
def test_documented_sizing_converts_loss_and_rounds_down(conversion, precision, expected):
    size = definitions("docs/tutorials/risk-management.md")["units_for_budget"]
    assert size(Decimal("1"), Decimal("1.1"), Decimal("1.085"), Decimal(conversion), precision) == Decimal(expected)


@pytest.mark.parametrize("page", ["docs/tutorials/getting-started/first-trade.md", "docs/examples/scripts/basic_usage.py"])
@pytest.mark.parametrize("fail_read", [False, True])
async def test_practice_lifecycle_closes_its_opened_trade_even_after_read_failure(page, fail_read):
    closed = False
    methods = []

    def handler(request):
        nonlocal closed
        methods.append(request.method)
        path = request.url.path
        if path.endswith("/pendingOrders"):
            return httpx.Response(200, json={"orders": [], "lastTransactionID": "121"})
        if path.endswith("/openTrades"):
            return httpx.Response(200, json={"trades": [], "lastTransactionID": "121"})
        if path.endswith("/instruments"):
            instrument = {
                "name": "EUR_USD",
                "type": "CURRENCY",
                "displayName": "EUR/USD",
                "pipLocation": -4,
                "displayPrecision": 5,
                "tradeUnitsPrecision": 0,
                "minimumTradeSize": "1",
                "maximumTrailingStopDistance": "1",
                "minimumTrailingStopDistance": "0.0005",
                "maximumPositionSize": "0",
                "maximumOrderUnits": "100000",
                "marginRate": "0.02",
            }
            return httpx.Response(200, json={"instruments": [instrument], "lastTransactionID": "121"})
        if path.endswith("/orders"):
            assert json.loads(request.content)["order"] == {"instrument": "EUR_USD", "units": "1", "positionFill": "OPEN_ONLY", "type": "MARKET", "timeInForce": "FOK"}
            fill = _fill("1")
            fill["tradeOpened"] = {"tradeID": "42", "units": "1", "price": "1.1"}
            return httpx.Response(201, json={"orderFillTransaction": fill, "lastTransactionID": "123"})
        if path.endswith("/trades/42/close"):
            assert request.method == "PUT"
            assert request.content == b""
            closed = True
            return httpx.Response(200, json={"orderFillTransaction": _fill("-1"), "lastTransactionID": "124"})
        assert path.endswith("/trades/42")
        if fail_read and not closed:
            raise httpx.ReadError("offline read failure", request=request)
        trade = {"id": "42", "instrument": "EUR_USD", "price": "1.1", "openTime": TIMESTAMP, "state": "CLOSED" if closed else "OPEN", "initialUnits": "1", "currentUnits": "0" if closed else "1", "initialMarginRequired": "0.1", "realizedPL": "0"}
        return httpx.Response(200, json={"trade": trade, "lastTransactionID": "124"})

    namespace = definitions(page)
    namespace["AsyncClient"] = lambda **kwargs: client_for(handler)
    if fail_read:
        with pytest.raises(httpx.ReadError):
            await namespace["main"]()
    else:
        await namespace["main"]()
    assert closed
    assert methods.count("POST") == methods.count("PUT") == 1


async def test_documented_candle_helper_excludes_incomplete_and_missing_midpoints():
    def handler(request):
        assert request.url.params["price"] == "M"
        candle = {"time": TIMESTAMP, "volume": 3, "complete": True, "mid": {"o": "1", "h": "2", "l": "1", "c": "1.5"}}
        return httpx.Response(200, json={"instrument": "EUR_USD", "granularity": "M5", "candles": [candle, {**candle, "complete": False}, {"time": TIMESTAMP, "volume": 0, "complete": True}]})

    read = definitions("docs/tutorials/basic-trading/market-data.md")["completed_closes"]
    async with client_for(handler) as client:
        assert await read(client, "EUR_USD") == [Decimal("1.5")]
