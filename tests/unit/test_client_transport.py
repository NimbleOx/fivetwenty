"""Client request contract tests using httpx.MockTransport."""

import json
from decimal import Decimal

import httpx
import pytest

from fivetwenty import AsyncClient
from fivetwenty.exceptions import FiveTwentyError


@pytest.mark.asyncio
async def test_request_adds_auth_headers_params_and_stringifies_decimal_body() -> None:
    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return httpx.Response(200, json={"ok": True})

    transport_client = httpx.AsyncClient(transport=httpx.MockTransport(handler), base_url="https://api.example.test")

    async with AsyncClient(token="secret-token", account_id="acct-1", transport=transport_client) as client:
        response = await client._request(
            "POST",
            "/v3/accounts/acct-1/orders",
            params={"instrument": "EUR_USD"},
            json_data={"order": {"price": Decimal("1.1000"), "units": Decimal("1000")}},
            headers={"ClientRequestID": "test-request-id"},
        )

    assert response.json() == {"ok": True}
    assert len(requests) == 1
    request = requests[0]
    assert str(request.url) == "https://api.example.test/v3/accounts/acct-1/orders?instrument=EUR_USD"
    assert request.headers["Authorization"] == "Bearer secret-token"
    assert request.headers["ClientRequestID"] == "test-request-id"
    assert json.loads(request.content) == {"order": {"price": "1.1000", "units": "1000"}}


@pytest.mark.asyncio
async def test_get_request_retries_retryable_status_codes() -> None:
    responses = [
        httpx.Response(503, json={"errorMessage": "temporarily unavailable"}, headers={"Retry-After": "0"}),
        httpx.Response(200, json={"ok": True}),
    ]
    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return responses.pop(0)

    transport_client = httpx.AsyncClient(transport=httpx.MockTransport(handler), base_url="https://api.example.test")

    async with AsyncClient(token="secret-token", account_id="acct-1", transport=transport_client, max_retries=2) as client:
        response = await client._request("GET", "/v3/accounts/acct-1")

    assert response.json() == {"ok": True}
    assert len(requests) == 2


@pytest.mark.asyncio
async def test_get_request_retries_transient_transport_errors() -> None:
    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        if len(requests) == 1:
            raise httpx.ConnectError("temporary connection failure", request=request)
        return httpx.Response(200, json={"ok": True})

    transport_client = httpx.AsyncClient(transport=httpx.MockTransport(handler), base_url="https://api.example.test")

    async with AsyncClient(token="secret-token", account_id="acct-1", transport=transport_client, max_retries=2) as client:
        response = await client._request("GET", "/v3/accounts/acct-1")

    assert response.json() == {"ok": True}
    assert len(requests) == 2


@pytest.mark.asyncio
async def test_write_requests_do_not_retry_retryable_status_codes() -> None:
    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return httpx.Response(
            503,
            json={"errorCode": "SERVICE_UNAVAILABLE", "errorMessage": "temporarily unavailable"},
            headers={"content-type": "application/json"},
        )

    transport_client = httpx.AsyncClient(transport=httpx.MockTransport(handler), base_url="https://api.example.test")

    async with AsyncClient(token="secret-token", account_id="acct-1", transport=transport_client, max_retries=3) as client:
        with pytest.raises(FiveTwentyError) as exc_info:
            await client._request("POST", "/v3/accounts/acct-1/orders", json_data={"order": {"type": "MARKET"}})

    assert len(requests) == 1
    assert exc_info.value.status == 503
    assert exc_info.value.retryable


@pytest.mark.asyncio
async def test_request_maps_json_error_payload_to_fivetwenty_error() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            401,
            json={"errorCode": "INVALID_TOKEN", "errorMessage": "Invalid authorization token"},
            headers={"content-type": "application/json", "X-Request-Id": "req-123"},
        )

    transport_client = httpx.AsyncClient(transport=httpx.MockTransport(handler), base_url="https://api.example.test")

    async with AsyncClient(token="bad-token", account_id="acct-1", transport=transport_client) as client:
        with pytest.raises(FiveTwentyError) as exc_info:
            await client._request("GET", "/v3/accounts/acct-1")

    error = exc_info.value
    assert error.status == 401
    assert error.code == "INVALID_TOKEN"
    assert error.message == "Invalid authorization token"
    assert error.request_id == "req-123"
    assert error.is_authentication_error


@pytest.mark.asyncio
async def test_write_requests_do_not_retry_transport_errors() -> None:
    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        raise httpx.ConnectError("temporary connection failure", request=request)

    transport_client = httpx.AsyncClient(transport=httpx.MockTransport(handler), base_url="https://api.example.test")

    async with AsyncClient(token="secret-token", account_id="acct-1", transport=transport_client, max_retries=3) as client:
        with pytest.raises(httpx.ConnectError):
            await client._request("POST", "/v3/accounts/acct-1/orders", json_data={"order": {"type": "MARKET"}})

    assert len(requests) == 1
