"""Exercise financial examples through the real SDK with an offline HTTP transport."""

import ast
import asyncio
import json
import re
from collections.abc import Callable
from decimal import Decimal
from pathlib import Path
from typing import Any

import httpx
import pytest

from fivetwenty import AsyncClient, Environment
from fivetwenty.exceptions import FiveTwentyError
from fivetwenty.models import LimitOrderRequest, OrderPositionFill, StopOrderRequest, TimeInForce

ROOT = Path(__file__).resolve().parents[2]
RISK_NOTEBOOK = "docs/examples/notebooks/risk-management.ipynb"
CLOSE_EXAMPLES = ["docs/guides/practical-solutions/close-positions.md", "docs/examples/notebooks/quick-start.ipynb"]
ACCOUNT_ID = "offline-account"
TIMESTAMP = "2026-09-01T12:00:00Z"


def _definition(relative_path: str, name: str, **overrides: Any) -> Any:
    """Compile only the selected definition, never notebook setup or example calls."""
    path = ROOT / relative_path
    if path.suffix == ".ipynb":
        blocks = ["".join(cell["source"]) for cell in json.loads(path.read_text())["cells"] if cell["cell_type"] == "code"]
    else:
        blocks = re.findall(r"```python\n(.*?)\n```", path.read_text(), re.S)
    node = next(node for block in blocks for node in ast.parse(block).body if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == name)
    namespace = {
        "AsyncClient": AsyncClient,
        "Environment": Environment,
        "FiveTwentyError": FiveTwentyError,
        "Decimal": Decimal,
        "asyncio": asyncio,
        "LimitOrderRequest": LimitOrderRequest,
        "StopOrderRequest": StopOrderRequest,
        "OrderPositionFill": OrderPositionFill,
        "TimeInForce": TimeInForce,
        "TOKEN": "offline-token",
        "ACCOUNT_ID": ACCOUNT_ID,
        "ENVIRONMENT": Environment.PRACTICE,
        **overrides,
    }
    module = ast.Module(body=[ast.ImportFrom(module="__future__", names=[ast.alias(name="annotations")], level=0), node], type_ignores=[])
    exec(compile(ast.fix_missing_locations(module), str(path), "exec"), namespace)
    return namespace[name]


def _client_factory(handler: Callable[[httpx.Request], httpx.Response]) -> Callable[..., AsyncClient]:
    def create(**kwargs: Any) -> AsyncClient:
        kwargs.setdefault("token", "offline-token")
        transport = httpx.AsyncClient(transport=httpx.MockTransport(handler), base_url="https://offline.example.test/v3")
        return AsyncClient(**kwargs, transport=transport)

    return create


def _account(currency: str) -> dict[str, Any]:
    return {
        **dict.fromkeys(
            (
                "unrealizedPL",
                "marginUsed",
                "positionValue",
                "marginCloseoutUnrealizedPL",
                "marginCloseoutMarginUsed",
                "marginCloseoutPercent",
                "marginCloseoutPositionValue",
                "marginCallMarginUsed",
                "marginCallPercent",
                "pl",
                "resettablePL",
                "financing",
                "commission",
                "dividendAdjustment",
                "guaranteedExecutionFees",
            ),
            "0",
        ),
        "id": ACCOUNT_ID,
        "currency": currency,
        "balance": "10000",
        "NAV": "10000",
        "marginAvailable": "10000",
        "marginCloseoutNAV": "10000",
        "withdrawalLimit": "10000",
        "createdByUserID": 1,
        "createdTime": TIMESTAMP,
        "openTradeCount": 0,
        "openPositionCount": 0,
        "pendingOrderCount": 0,
        "hedgingEnabled": True,
        "lastTransactionID": "123",
    }


def _position(long_units: str, short_units: str) -> dict[str, Any]:
    return {
        "instrument": "EUR_USD",
        "pl": "0",
        "resettablePL": "0",
        "long": {"units": long_units, "pl": "0", "resettablePL": "0"},
        "short": {"units": short_units, "pl": "0", "resettablePL": "0"},
    }


def _transaction(**fields: Any) -> dict[str, Any]:
    return {"id": "123", "time": TIMESTAMP, "userID": 1, "accountID": ACCOUNT_ID, "batchID": "122", **fields}


def _fill(units: str) -> dict[str, Any]:
    return _transaction(type="ORDER_FILL", orderID="122", instrument="EUR_USD", units=units, price="1.1", pl="0")


@pytest.mark.asyncio
@pytest.mark.parametrize(("currency", "conversion", "expected"), [("USD", None, 40000), ("GBP", "0.8", 50000)])
async def test_notebook_sizes_using_loss_in_account_currency(currency: str, conversion: str | None, expected: int) -> None:
    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        if request.url.path.endswith(f"/accounts/{ACCOUNT_ID}"):
            return httpx.Response(200, json={"account": _account(currency), "lastTransactionID": "123"})
        assert request.method == "GET"
        assert request.url.path.endswith("/pricing")
        assert request.url.params["includeHomeConversions"] == "true"
        return httpx.Response(200, json={"prices": [], "time": TIMESTAMP, "homeConversions": [{"currency": "USD", "accountGain": "1.1", "accountLoss": conversion, "positionValue": "0.9"}]})

    async with _client_factory(handler)(account_id=ACCOUNT_ID) as client:
        manager = _definition(RISK_NOTEBOOK, "RiskManager")(client, ACCOUNT_ID)
        units = await manager.calculate_position_size("EUR_USD", Decimal("1.10000"), Decimal("1.09500"))

    assert units == expected
    assert len(requests) == (1 if currency == "USD" else 2)


@pytest.mark.asyncio
@pytest.mark.parametrize("conversion", [None, "0", "-1"])
async def test_notebook_rejects_unavailable_or_invalid_home_conversion(conversion: str | None) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path.endswith(f"/accounts/{ACCOUNT_ID}"):
            return httpx.Response(200, json={"account": _account("GBP"), "lastTransactionID": "123"})
        assert request.method == "GET"
        assert request.url.path.endswith("/pricing")
        conversions = [] if conversion is None else [{"currency": "USD", "accountGain": "0.8", "accountLoss": conversion, "positionValue": "0.8"}]
        return httpx.Response(200, json={"prices": [], "time": TIMESTAMP, "homeConversions": conversions})

    async with _client_factory(handler)(account_id=ACCOUNT_ID) as client:
        manager = _definition(RISK_NOTEBOOK, "RiskManager")(client, ACCOUNT_ID)
        with pytest.raises(ValueError, match="No valid loss conversion"):
            await manager.calculate_position_size("EUR_USD", Decimal("1.1"), Decimal("1.095"))


@pytest.mark.asyncio
@pytest.mark.parametrize("example", CLOSE_EXAMPLES)
@pytest.mark.parametrize(("long_units", "short_units"), [("1000", "0"), ("0", "-1000"), ("1000", "-1000"), ("0.5", "-0.25")])
async def test_close_examples_use_explicit_sides_without_opening_hedges(example: str, long_units: str, short_units: str) -> None:
    requests: list[httpx.Request] = []
    expected = {"longUnits": "ALL" if Decimal(long_units) else "NONE", "shortUnits": "ALL" if Decimal(short_units) else "NONE"}

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        if request.method == "GET":
            assert request.url.path.endswith("/openPositions")
            return httpx.Response(200, json={"positions": [_position(long_units, short_units)], "lastTransactionID": "123"})
        assert request.method == "PUT"
        assert request.url.path.endswith("/positions/EUR_USD/close")
        assert json.loads(request.content) == expected
        payload: dict[str, Any] = {"lastTransactionID": "124"}
        for side, units in (("long", long_units), ("short", short_units)):
            if Decimal(units):
                payload[f"{side}OrderFillTransaction"] = _fill(str(-Decimal(units)))
        return httpx.Response(200, json=payload)

    close_position = _definition(example, "close_position", AsyncClient=_client_factory(handler))
    result = await close_position(ACCOUNT_ID, "EUR_USD")

    assert result is not None
    assert [request.method for request in requests] == ["GET", "PUT"]


@pytest.mark.asyncio
@pytest.mark.parametrize("example", CLOSE_EXAMPLES)
async def test_close_examples_do_not_report_success_without_requested_fill(example: str) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        if request.method == "GET":
            return httpx.Response(200, json={"positions": [_position("1000", "-1000")], "lastTransactionID": "123"})
        assert request.method == "PUT"
        assert request.url.path.endswith("/close")
        # One side filled, the other was cancelled; the instrument is not closed.
        return httpx.Response(200, json={"lastTransactionID": "124", "longOrderFillTransaction": _fill("-1000"), "shortOrderCancelTransaction": _transaction(type="ORDER_CANCEL", orderID="122")})

    close_position = _definition(example, "close_position", AsyncClient=_client_factory(handler))
    assert await close_position(ACCOUNT_ID, "EUR_USD") is None


@pytest.mark.asyncio
@pytest.mark.parametrize("example", CLOSE_EXAMPLES)
async def test_close_examples_handle_empty_position_envelope(example: str) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.method == "GET"
        assert request.url.path.endswith("/openPositions")
        return httpx.Response(200, json={"positions": [], "lastTransactionID": "123"})

    close_position = _definition(example, "close_position", AsyncClient=_client_factory(handler))
    assert await close_position(ACCOUNT_ID, "EUR_USD") is None


@pytest.mark.asyncio
@pytest.mark.parametrize(("units", "side"), [(500, "long"), (-500, "short")])
async def test_partial_close_leaves_other_side_unchanged(units: int, side: str) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        if request.method == "GET":
            return httpx.Response(200, json={"positions": [_position("1000", "-1000")], "lastTransactionID": "123"})
        assert request.method == "PUT"
        assert request.url.path.endswith("/positions/EUR_USD/close")
        assert json.loads(request.content) == {"longUnits": "500" if side == "long" else "NONE", "shortUnits": "500" if side == "short" else "NONE"}
        return httpx.Response(200, json={"lastTransactionID": "124", f"{side}OrderFillTransaction": _fill(str(-units))})

    close_partial = _definition(CLOSE_EXAMPLES[0], "close_partial_position", AsyncClient=_client_factory(handler))
    assert await close_partial(ACCOUNT_ID, "EUR_USD", units) is not None


@pytest.mark.asyncio
async def test_verification_detects_fractional_hedged_position() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.method == "GET"
        return httpx.Response(200, json={"positions": [_position("0.5", "-0.5")], "lastTransactionID": "123"})

    verify = _definition(CLOSE_EXAMPLES[0], "verify_position_closed", AsyncClient=_client_factory(handler))
    assert await verify(ACCOUNT_ID, "EUR_USD") is False


@pytest.mark.asyncio
@pytest.mark.parametrize("units", [1000, -1000])
async def test_scale_out_limits_keep_price_trigger_and_cannot_open_exposure(units: int) -> None:
    orders: list[dict[str, Any]] = []

    def handler(request: httpx.Request) -> httpx.Response:
        if request.method == "GET":
            assert request.url.path.endswith("/trades/42")
            trade = {"id": "42", "instrument": "EUR_USD", "price": "1.1", "openTime": TIMESTAMP, "state": "OPEN", "initialUnits": str(units), "currentUnits": str(units), "initialMarginRequired": "50", "realizedPL": "0"}
            return httpx.Response(200, json={"trade": trade, "lastTransactionID": "123"})
        assert request.method == "POST"
        assert request.url.path.endswith("/orders")
        order = json.loads(request.content)["order"]
        orders.append(order)
        transaction = _transaction(**{**order, "type": "LIMIT_ORDER"})
        return httpx.Response(201, json={"orderCreateTransaction": transaction, "lastTransactionID": "123"})

    async with _client_factory(handler)(account_id=ACCOUNT_ID) as client:
        advanced = _definition(RISK_NOTEBOOK, "AdvancedOrders")(client, ACCOUNT_ID)
        result = await advanced.scale_out_position("42", [25, 75], [1.2, 1.3])

    assert len(result) == 2
    assert [order["price"] for order in orders] == ["1.20000", "1.30000"]
    assert all(order["type"] == "LIMIT" and order["positionFill"] == "REDUCE_ONLY" for order in orders)
    assert sum(Decimal(order["units"]) for order in orders) == -units


@pytest.mark.asyncio
@pytest.mark.parametrize("units", [1001, -1001])
async def test_tiered_stop_orders_cannot_open_exposure(units: int) -> None:
    orders: list[dict[str, Any]] = []

    def handler(request: httpx.Request) -> httpx.Response:
        if request.method == "GET":
            assert request.url.path.endswith("/pricing")
            price = {"instrument": "EUR_USD", "time": TIMESTAMP, "closeoutBid": "1.1", "closeoutAsk": "1.1002", "bids": [{"price": "1.1", "liquidity": "10000"}], "asks": [{"price": "1.1002", "liquidity": "10000"}]}
            return httpx.Response(200, json={"prices": [price], "time": TIMESTAMP})
        assert request.method == "POST"
        assert request.url.path.endswith("/orders")
        order = json.loads(request.content)["order"]
        orders.append(order)
        if order["type"] == "MARKET":
            return httpx.Response(201, json={"orderFillTransaction": _fill(str(units)), "lastTransactionID": "123"})
        return httpx.Response(201, json={"lastTransactionID": "124"})

    tiered_stops = _definition("docs/guides/practical-solutions/implement-stop-loss-strategies.md", "implement_tiered_stop_loss", AsyncClient=_client_factory(handler))
    assert await tiered_stops(ACCOUNT_ID, "EUR_USD", units) is True
    assert len(orders) == 4
    assert all(order["type"] == "STOP" and order["positionFill"] == "REDUCE_ONLY" for order in orders[1:])
    assert sum(Decimal(order["units"]) for order in orders[1:]) == -units
