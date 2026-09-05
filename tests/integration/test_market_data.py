"""Live price/candle contracts without hardcoded market-price expectations."""

import asyncio
from datetime import datetime, timezone
from decimal import Decimal

import pytest

from fivetwenty import AsyncClient
from fivetwenty.models import ClientPrice, PricingHeartbeat, TransactionHeartbeat

pytestmark = pytest.mark.integration


async def test_pricing_and_home_conversions(sandbox_client, test_account_id):
    result = await sandbox_client.pricing.get_pricing(test_account_id, ["EUR_USD"], include_home_conversions=True)
    assert [price.instrument for price in result["prices"]] == ["EUR_USD"]
    price = result["prices"][0]
    assert isinstance(price.closeout_bid, Decimal)
    assert price.closeout_ask >= price.closeout_bid > 0
    assert result["homeConversions"]
    assert all(conversion.account_loss > 0 for conversion in result["homeConversions"])


@pytest.mark.parametrize("datetime_format", ["RFC3339", "UNIX"])
@pytest.mark.parametrize("endpoint", ["account", "instrument"])
async def test_candle_pagination_returns_native_datetimes(integration_config, test_account_id, datetime_format, endpoint):
    async with AsyncClient(**integration_config, datetime_format=datetime_format) as client:
        kwargs = {"count": 3, "to_time": datetime.now(timezone.utc), "granularity": "M1"}
        if endpoint == "account":
            result = await client.pricing.get_account_instrument_candles(test_account_id, "EUR_USD", units=Decimal("0.5"), **kwargs)
        else:
            result = await client.instruments.get_instrument_candles("EUR_USD", **kwargs)
    candles = result["candles"]
    assert len(candles) == 3
    assert result["instrument"] == "EUR_USD"
    assert all(isinstance(candle.time, datetime) for candle in candles)
    assert [candle.time for candle in candles] == sorted({candle.time for candle in candles})


async def test_latest_candles_preserve_specifications(sandbox_client, test_account_id):
    result = await sandbox_client.pricing.get_latest_candles(test_account_id, ["EUR_USD:M1:M"], units=Decimal("0.5"))
    assert len(result["latestCandles"]) == 1
    assert result["latestCandles"][0]["instrument"] == "EUR_USD"
    assert result["latestCandles"][0]["granularity"] == "M1"
    assert result["latestCandles"][0]["candles"]


@pytest.mark.parametrize("endpoint", ["pricing", "transactions"])
async def test_stream_delivers_a_typed_record_within_a_bounded_wait(sandbox_client, test_account_id, endpoint):
    if endpoint == "pricing":
        stream = sandbox_client.pricing.get_pricing_stream(test_account_id, ["EUR_USD"])
    else:
        stream = sandbox_client.transactions.get_transactions_stream(test_account_id)
    try:
        event = await asyncio.wait_for(anext(stream), timeout=30)
        assert isinstance(event, (ClientPrice, PricingHeartbeat)) if endpoint == "pricing" else isinstance(event, TransactionHeartbeat) or hasattr(event, "id")
        assert isinstance(event.time, datetime)
    finally:
        await stream.aclose()
