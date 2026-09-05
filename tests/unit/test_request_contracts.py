"""Regression tests at the OANDA request/response boundary."""

import json
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from typing import Any

import httpx
import pytest

from fivetwenty import AsyncClient
from fivetwenty.models import ClientExtensions, GuaranteedStopLossDetails, LimitOrderRequest, StopLossDetails, TakeProfitDetails, TimeInForce, TrailingStopLossDetails

ACCOUNT = "offline-account"
WHEN = datetime(2024, 1, 1, 12, 0, 0, 123456, tzinfo=timezone.utc)
DEPENDENT_ORDERS = [
    ("take_profit", "takeProfit", TakeProfitDetails, {"price": "1.2"}),
    ("stop_loss", "stopLoss", StopLossDetails, {"price": "1.0"}),
    ("trailing_stop_loss", "trailingStopLoss", TrailingStopLossDetails, {"distance": "0.01"}),
    ("guaranteed_stop_loss", "guaranteedStopLoss", GuaranteedStopLossDetails, {"price": "1.0"}),
]


def client_recording(requests: list[httpx.Request], payload: dict[str, Any] | None = None, **kwargs: Any) -> AsyncClient:
    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return httpx.Response(200, json=payload if payload is not None else {"lastTransactionID": "123"})

    transport = httpx.AsyncClient(transport=httpx.MockTransport(handler), base_url="https://offline.example.test/v3")
    return AsyncClient(token="offline-token", account_id=ACCOUNT, transport=transport, **kwargs)


@pytest.mark.asyncio
@pytest.mark.parametrize(("parameter", "wire", "model", "fields"), DEPENDENT_ORDERS)
async def test_dependent_orders_distinguish_omission_cancellation_and_partial_changes(parameter, wire, model, fields):
    requests: list[httpx.Request] = []
    async with client_recording(requests) as client:
        await client.trades.put_trade_orders(ACCOUNT, "123")
        await client.trades.put_trade_orders(ACCOUNT, "123", **{parameter: None})
        await client.trades.put_trade_orders(ACCOUNT, "123", **{parameter: {"clientExtensions": {"tag": "exit"}}})
        await client.trades.put_trade_orders(ACCOUNT, "123", **{parameter: {}})
        await client.trades.put_trade_orders(ACCOUNT, "123", **{parameter: model(**fields)})

    assert [json.loads(request.content) for request in requests] == [{}, {wire: None}, {wire: {"clientExtensions": {"tag": "exit"}}}, {wire: {}}, {wire: fields}]


@pytest.mark.asyncio
async def test_dependent_order_cancellation_can_be_combined_with_an_update():
    requests: list[httpx.Request] = []
    async with client_recording(requests) as client:
        await client.trades.put_trade_orders(ACCOUNT, "123", take_profit=None, stop_loss=StopLossDetails(price="1.0"))
    assert json.loads(requests[0].content) == {"takeProfit": None, "stopLoss": {"price": "1.0"}}


@pytest.mark.asyncio
@pytest.mark.parametrize(("datetime_format", "expected"), [("RFC3339", "2024-01-01T12:00:00.123456Z"), ("UNIX", "1704110400.123456000")])
@pytest.mark.parametrize("operation", ["create", "replace"])
async def test_order_datetimes_follow_client_format_without_changing_models(datetime_format, expected, operation):
    requests: list[httpx.Request] = []
    dependent = TakeProfitDetails(price="1.2", time_in_force=TimeInForce.GTD, gtd_time=WHEN)
    order = LimitOrderRequest(instrument="EUR_USD", units=Decimal("1.5"), price="1.1", time_in_force=TimeInForce.GTD, gtd_time=WHEN, take_profit_on_fill=dependent)
    async with client_recording(requests, datetime_format=datetime_format) as client:
        if operation == "create":
            await client.orders.post_order(ACCOUNT, order)
        else:
            await client.orders.put_order(ACCOUNT, "123", order)
    body = json.loads(requests[0].content)["order"]
    assert requests[0].headers["Accept-Datetime-Format"] == datetime_format
    assert body["gtdTime"] == expected
    assert body["takeProfitOnFill"]["gtdTime"] == expected
    assert order.gtd_time is WHEN
    assert dependent.gtd_time is WHEN
    assert order.model_dump(by_alias=True)["gtdTime"] == "2024-01-01T12:00:00.123456Z"


@pytest.mark.asyncio
@pytest.mark.parametrize(("parameter", "wire", "model", "fields"), DEPENDENT_ORDERS)
@pytest.mark.parametrize("as_dict", [False, True])
async def test_dependent_order_datetimes_follow_unix_format(parameter, wire, model, fields, as_dict):
    requests: list[httpx.Request] = []
    details = {"timeInForce": "GTD", "gtdTime": WHEN} if as_dict else model(**fields, time_in_force=TimeInForce.GTD, gtd_time=WHEN)
    async with client_recording(requests, datetime_format="UNIX") as client:
        await client.trades.put_trade_orders(ACCOUNT, "123", **{parameter: details})
    assert json.loads(requests[0].content)[wire]["gtdTime"] == "1704110400.123456000"
    assert requests[0].headers["Accept-Datetime-Format"] == "UNIX"


@pytest.mark.asyncio
@pytest.mark.parametrize("endpoint", ["instrument", "account"])
@pytest.mark.parametrize("boundary", ["from_time", "to_time"])
@pytest.mark.parametrize("datetime_format", ["RFC3339", "UNIX"])
async def test_candle_count_can_be_combined_with_one_time_boundary(endpoint, boundary, datetime_format):
    requests: list[httpx.Request] = []
    async with client_recording(requests, {"instrument": "EUR_USD", "granularity": "M1", "candles": []}, datetime_format=datetime_format) as client:
        kwargs = {"count": 100, boundary: WHEN, "granularity": "M1"}
        if endpoint == "instrument":
            await client.instruments.get_instrument_candles("EUR_USD", **kwargs)
        else:
            await client.pricing.get_account_instrument_candles(ACCOUNT, "EUR_USD", **kwargs)
    params = requests[0].url.params
    assert params["count"] == "100"
    assert params[boundary.removesuffix("_time")] == ("1704110400.123456000" if datetime_format == "UNIX" else WHEN.isoformat())


@pytest.mark.asyncio
@pytest.mark.parametrize("endpoint", ["instrument", "account"])
async def test_candle_full_range_omits_count_and_rejects_an_explicit_count(endpoint):
    requests: list[httpx.Request] = []
    async with client_recording(requests, {"instrument": "EUR_USD", "granularity": "M1", "candles": []}) as client:
        method = client.instruments.get_instrument_candles if endpoint == "instrument" else client.pricing.get_account_instrument_candles
        args = ("EUR_USD",) if endpoint == "instrument" else (ACCOUNT, "EUR_USD")
        await method(*args, from_time=WHEN, to_time=WHEN + timedelta(hours=1))
        with pytest.raises(ValueError, match="both from_time and to_time"):
            await method(*args, count=100, from_time=WHEN, to_time=WHEN + timedelta(hours=1))
    assert len(requests) == 1
    assert "count" not in requests[0].url.params


@pytest.mark.asyncio
@pytest.mark.parametrize(("units", "expected"), [(10000, "10000"), (Decimal("0.5"), "0.5"), ("100000000000000000000.125", "100000000000000000000.125"), (Decimal("1E-8"), "0.00000001")])
@pytest.mark.parametrize("latest", [False, True])
async def test_candles_accept_decimal_position_quantities(latest, units, expected):
    requests: list[httpx.Request] = []
    response = {"latestCandles": []} if latest else {"instrument": "EUR_USD", "granularity": "M1", "candles": []}
    async with client_recording(requests, response) as client:
        if latest:
            await client.pricing.get_latest_candles(ACCOUNT, ["EUR_USD:M1:BA"], units=units)
        else:
            await client.pricing.get_account_instrument_candles(ACCOUNT, "EUR_USD", units=units)
    assert requests[0].url.params["units"] == expected


@pytest.mark.asyncio
@pytest.mark.parametrize("field", ["clientExtensions", "tradeClientExtensions"])
async def test_order_extension_response_accepts_each_independent_modification(field):
    requests: list[httpx.Request] = []
    transaction = {"id": "124", "type": "ORDER_CLIENT_EXTENSIONS_MODIFY", "time": WHEN.isoformat(), "userID": 1, "accountID": ACCOUNT, "batchID": "124", "orderID": "123", f"{field}Modify": {"tag": "updated"}}
    payload = {"lastTransactionID": "124", "orderClientExtensionsModifyTransaction": transaction}
    async with client_recording(requests, payload) as client:
        argument = "client_extensions" if field == "clientExtensions" else "trade_client_extensions"
        result = await client.orders.put_order_client_extensions(ACCOUNT, "123", **{argument: ClientExtensions(tag="updated")})
    response = result["orderClientExtensionsModifyTransaction"]
    assert response.model_dump(by_alias=True, exclude_none=True)[f"{field}Modify"] == {"tag": "updated"}
    assert getattr(response, "trade_client_extensions_modify" if field == "clientExtensions" else "client_extensions_modify") is None
