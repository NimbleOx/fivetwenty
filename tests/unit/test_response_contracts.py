"""Independently specified wire fixtures for conditional trading responses."""

import json
from decimal import Decimal

import httpx
import pytest
from pydantic import ValidationError

from fivetwenty import AsyncClient
from fivetwenty.models import AccountChanges, ClientExtensions
from fivetwenty.models import transactions as models

BASE = {"id": "42", "time": "2024-01-01T00:00:00Z", "userID": 1, "accountID": "offline", "batchID": "42"}
CANCEL = {**BASE, "type": "ORDER_CANCEL", "orderID": "40", "reason": "CLIENT_REQUEST", "replacedByOrderID": "43"}
FILL = {**BASE, "type": "ORDER_FILL", "orderID": "40", "instrument": "EUR_USD", "units": "-0.5", "price": "1.23456", "pl": "0.12345"}
CREATE = {**BASE, "type": "MARKET_ORDER", "instrument": "EUR_USD", "units": "-0.5", "timeInForce": "FOK"}
DEPENDENTS = [
    ("takeProfitOrderTransaction", models.TakeProfitOrderTransaction, {**BASE, "type": "TAKE_PROFIT_ORDER", "tradeID": "40", "price": "1.23456"}),
    ("stopLossOrderTransaction", models.StopLossOrderTransaction, {**BASE, "type": "STOP_LOSS_ORDER", "tradeID": "40", "price": "1.01234"}),
    ("trailingStopLossOrderTransaction", models.TrailingStopLossOrderTransaction, {**BASE, "type": "TRAILING_STOP_LOSS_ORDER", "tradeID": "40", "distance": "0.00123"}),
    ("guaranteedStopLossOrderTransaction", models.GuaranteedStopLossOrderTransaction, {**BASE, "type": "GUARANTEED_STOP_LOSS_ORDER", "tradeID": "40", "price": "1.01234", "guaranteedExecutionPremium": "0.00012"}),
    *[(f"{prefix}OrderCancelTransaction", models.OrderCancelTransaction, CANCEL) for prefix in ["takeProfit", "stopLoss", "trailingStopLoss", "guaranteedStopLoss"]],
    *[(f"{prefix}OrderCreatedCancelTransaction", models.OrderCancelTransaction, CANCEL) for prefix in ["takeProfit", "stopLoss"]],
    *[(f"{prefix}OrderFillTransaction", models.OrderFillTransaction, FILL) for prefix in ["takeProfit", "stopLoss"]],
]


def recording_client(payload, requests):
    def respond(request):
        requests.append(request)
        return httpx.Response(200, json=payload)

    http = httpx.AsyncClient(transport=httpx.MockTransport(respond), base_url="https://offline.test/v3")
    return AsyncClient(token="offline-token", account_id="offline", transport=http)


@pytest.mark.parametrize(("key", "model", "transaction"), DEPENDENTS, ids=[row[0] for row in DEPENDENTS])
async def test_each_dependent_order_response_variant_retains_its_fields(key, model, transaction):
    payload = {key: transaction, "lastTransactionID": "42", "relatedTransactionIDs": ["40", "42"]}
    requests = []
    async with recording_client(payload, requests) as client:
        result = await client.trades.put_trade_orders("offline", "40", take_profit=None)
    assert set(result) == set(payload)
    assert type(result[key]) is model
    dumped = result[key].model_dump(mode="json", by_alias=True, exclude_unset=True)
    assert dumped == transaction
    assert result["relatedTransactionIDs"] == ["40", "42"]
    assert requests[0].url.path == "/v3/accounts/offline/trades/40/orders"
    assert json.loads(requests[0].content) == {"takeProfit": None}


@pytest.mark.parametrize("side", ["long", "short"])
@pytest.mark.parametrize(("suffix", "model", "transaction"), [("Create", models.MarketOrderTransaction, CREATE), ("Fill", models.OrderFillTransaction, FILL), ("Cancel", models.OrderCancelTransaction, CANCEL)])
async def test_close_position_parses_each_side_and_transaction_variant(side, suffix, model, transaction):
    key = f"{side}Order{suffix}Transaction"
    requests = []
    async with recording_client({key: transaction, "lastTransactionID": "42"}, requests) as client:
        result = await client.positions.close_position("offline", "EUR_USD", **{f"{side}_units": Decimal("0.5")})
    assert set(result) == {key, "lastTransactionID"}
    assert type(result[key]) is model
    assert result[key].model_dump(by_alias=True, mode="json", exclude_unset=True) == transaction
    assert json.loads(requests[0].content) == {f"{side}Units": "0.5"}


@pytest.mark.parametrize("side", ["long", "short"])
@pytest.mark.parametrize("units", ["0.5", "invalid"])
async def test_position_numeric_strings_are_preserved_and_invalid_units_never_send(side, units):
    requests = []
    async with recording_client({"lastTransactionID": "42"}, requests) as client:
        if units == "invalid":
            with pytest.raises(ValueError, match=f"{side}_units string"):
                await client.positions.close_position("offline", "EUR_USD", **{f"{side}_units": units})
            assert requests == []
        else:
            await client.positions.close_position("offline", "EUR_USD", **{f"{side}_units": units})
            assert json.loads(requests[0].content) == {f"{side}Units": "0.5"}


async def test_trade_close_can_return_a_cancellation_without_a_fill():
    requests = []
    async with recording_client({"orderCancelTransaction": CANCEL, "lastTransactionID": "42"}, requests) as client:
        result = await client.trades.close_trade("offline", "40")
    assert set(result) == {"orderCancelTransaction", "lastTransactionID"}
    assert result["orderCancelTransaction"].order_id == "40"
    assert result["orderCancelTransaction"].reason == "CLIENT_REQUEST"


async def test_trade_extension_response_preserves_a_typed_modification():
    payload = {"tradeClientExtensionsModifyTransaction": {**BASE, "type": "TRADE_CLIENT_EXTENSIONS_MODIFY", "tradeID": "40", "tradeClientExtensionsModify": {"tag": "exit"}}, "lastTransactionID": "42", "relatedTransactionIDs": ["40", "42"]}
    requests = []
    async with recording_client(payload, requests) as client:
        result = await client.trades.put_trade_client_extensions("offline", "40")
    assert result["tradeClientExtensionsModifyTransaction"].trade_client_extensions_modify.tag == "exit"
    assert result["relatedTransactionIDs"] == ["40", "42"]
    assert set(result) == set(payload)


async def test_position_close_keeps_side_specific_client_extensions():
    requests = []
    async with recording_client({"lastTransactionID": "42"}, requests) as client:
        await client.positions.close_position("offline", "EUR_USD", long_units="ALL", short_units="ALL", long_client_extensions=ClientExtensions(tag="long-exit"), short_client_extensions=ClientExtensions(tag="short-exit"))
    assert json.loads(requests[0].content) == {"longUnits": "ALL", "shortUnits": "ALL", "longClientExtensions": {"tag": "long-exit"}, "shortClientExtensions": {"tag": "short-exit"}}


@pytest.mark.parametrize("collection", ["ordersCreated", "transactions"])
@pytest.mark.parametrize("invalid", [None, "invalid", {"id": "42"}])
def test_account_changes_reject_malformed_collections(collection, invalid):
    with pytest.raises(ValidationError):
        AccountChanges.model_validate({collection: invalid})
