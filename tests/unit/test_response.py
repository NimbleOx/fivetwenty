"""Tests for endpoint response compatibility containers."""

from fivetwenty._internal.response import ApiResponse
from fivetwenty.models import Trade


def test_api_response_resolves_snake_case_aliases() -> None:
    """Endpoint responses support OANDA keys and snake_case compatibility access."""
    response = ApiResponse(
        {
            "orderFillTransaction": {"id": "123"},
            "from": "2024-01-01T00:00:00Z",
            "lastTransactionID": "456",
        }
    )

    assert response.order_fill_transaction == {"id": "123"}
    assert response["order_fill_transaction"] == {"id": "123"}
    assert response.from_ == "2024-01-01T00:00:00Z"
    assert response.get("last_transaction_id") == "456"
    assert "order_fill_transaction" in response


def test_api_response_delegates_to_single_nested_model() -> None:
    """Single-object endpoint responses support direct access to nested model fields."""
    trade = Trade(
        id="123",
        instrument="EUR_USD",
        price="1.1000",
        openTime="2024-01-01T12:00:00Z",
        state="OPEN",
        initialUnits="1000",
        initialMarginRequired="50.00",
        currentUnits="1000",
        realizedPL="5.00",
    )
    response = ApiResponse({"trade": trade, "lastTransactionID": "456"})

    assert response["state"] == "OPEN"
    assert response.get("realizedPL") == "5.00"
    assert "openTime" in response
