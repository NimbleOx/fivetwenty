"""Small, isolated practice-account lifecycles with concrete server outcomes."""

from decimal import Decimal

import pytest

from fivetwenty import FiveTwentyError
from fivetwenty.models import ClientExtensions, LimitOrderRequest, MarketOrderRequest, OrderPositionFill, StopLossDetails, TakeProfitDetails
from tests.integration.helpers import skip_or_raise_environment_error

pytestmark = [pytest.mark.integration, pytest.mark.trading]


@pytest.fixture
async def instrument(trading_client, test_account_id):
    result = await trading_client.accounts.get_account_instruments(test_account_id, instruments=["EUR_USD"])
    assert len(result["instruments"]) == 1
    pricing = await trading_client.pricing.get_pricing(test_account_id, ["EUR_USD"])
    price = pricing["prices"][0]
    if price.status != "tradeable":
        pytest.skip("EUR_USD is not currently tradeable")
    return result["instruments"][0], price


async def open_trade(client, account_id, details, sign=1):
    order = MarketOrderRequest(instrument="EUR_USD", units=details.minimum_trade_size * sign, position_fill=OrderPositionFill.OPEN_ONLY)
    try:
        response = await client.orders.post_order(account_id, order)
    except FiveTwentyError as exc:
        skip_or_raise_environment_error(exc, "Opening the practice test trade")
    fill = response["orderFillTransaction"]
    assert fill.instrument == "EUR_USD"
    assert fill.trade_opened is not None
    return fill.trade_opened.trade_id


@pytest.mark.parametrize("kind", ["limit", "stop", "market_if_touched"])
async def test_pending_order_creation_lookup_and_cancellation(trading_client, test_account_id, instrument, kind):
    details, quote = instrument
    multiplier = Decimal("1.1") if kind == "stop" else Decimal("0.9")
    price = (quote.closeout_bid * multiplier).quantize(Decimal(10) ** -details.display_precision)
    create = getattr(trading_client.orders, f"post_{kind}_order")
    response = await create(test_account_id, "EUR_USD", details.minimum_trade_size, price)
    order_id = response["orderCreateTransaction"].id
    order = (await trading_client.orders.get_order(test_account_id, order_id))["order"]
    assert order.state == "PENDING"
    assert order.type == kind.upper()
    pending = await trading_client.orders.get_pending_orders(test_account_id)
    assert order_id in {item.id for item in pending["orders"]}
    cancelled = await trading_client.orders.cancel_order(test_account_id, order_id)
    assert cancelled["orderCancelTransaction"].order_id == order_id
    assert (await trading_client.orders.get_order(test_account_id, order_id))["order"].state == "CANCELLED"


async def test_order_replacement_and_extensions(trading_client, test_account_id, instrument):
    details, quote = instrument
    quantum = Decimal(10) ** -details.display_precision
    price = (quote.closeout_bid * Decimal("0.9")).quantize(quantum)
    initial = await trading_client.orders.post_limit_order(test_account_id, "EUR_USD", details.minimum_trade_size, price)
    order_id = initial["orderCreateTransaction"].id
    request = LimitOrderRequest(instrument="EUR_USD", units=details.minimum_trade_size, price=price - quantum)
    replaced = await trading_client.orders.put_order(test_account_id, order_id, request)
    replacement_id = replaced["orderCreateTransaction"].id
    assert replaced["orderCancelTransaction"].order_id == order_id
    assert replacement_id != order_id
    await trading_client.orders.put_order_client_extensions(test_account_id, replacement_id, client_extensions=ClientExtensions(tag="sdk-integration"))
    order = (await trading_client.orders.get_order(test_account_id, replacement_id))["order"]
    assert order.price == price - quantum
    assert order.client_extensions.tag == "sdk-integration"


async def test_trade_extensions_dependent_updates_and_close(trading_client, test_account_id, instrument):
    details, quote = instrument
    trade_id = await open_trade(trading_client, test_account_id, details)
    await trading_client.trades.put_trade_client_extensions(test_account_id, trade_id, client_extensions=ClientExtensions(tag="sdk-integration"))
    quantum = Decimal(10) ** -details.display_precision
    take_profit = (quote.closeout_ask * Decimal("1.1")).quantize(quantum)
    stop_loss = (quote.closeout_bid * Decimal("0.9")).quantize(quantum)
    await trading_client.trades.put_trade_orders(test_account_id, trade_id, take_profit=TakeProfitDetails(price=take_profit), stop_loss=StopLossDetails(price=stop_loss))
    trade = (await trading_client.trades.get_trade(test_account_id, trade_id))["trade"]
    assert trade.client_extensions.tag == "sdk-integration"
    assert trade.take_profit_order.price == take_profit
    assert trade.stop_loss_order.price == stop_loss
    stop_id = trade.stop_loss_order.id
    await trading_client.trades.put_trade_orders(test_account_id, trade_id, take_profit=None)
    updated = (await trading_client.trades.get_trade(test_account_id, trade_id))["trade"]
    assert updated.take_profit_order is None
    assert updated.stop_loss_order.id == stop_id
    closed = await trading_client.trades.close_trade(test_account_id, trade_id)
    assert trade_id in {trade.trade_id for trade in closed["orderFillTransaction"].trades_closed}
    assert (await trading_client.trades.get_trade(test_account_id, trade_id))["trade"].state == "CLOSED"


@pytest.mark.parametrize(("sign", "side"), [(1, "long"), (-1, "short")])
async def test_explicit_position_close_removes_owned_exposure(trading_client, test_account_id, instrument, sign, side):
    details, _ = instrument
    await open_trade(trading_client, test_account_id, details, sign)
    position = (await trading_client.positions.get_position(test_account_id, "EUR_USD"))["position"]
    assert getattr(position, side).units == details.minimum_trade_size * sign
    closed = await trading_client.positions.close_position(test_account_id, "EUR_USD", **{f"{side}_units": "ALL"})
    assert closed[f"{side}OrderFillTransaction"].units == -details.minimum_trade_size * sign
    assert (await trading_client.trades.get_open_trades(test_account_id))["trades"] == []
