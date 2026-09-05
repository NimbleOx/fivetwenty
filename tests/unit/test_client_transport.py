"""Client request contract tests using httpx.MockTransport."""

import json
import logging
from decimal import Decimal

import httpx
import pytest

from fivetwenty import AsyncClient
from fivetwenty.exceptions import FiveTwentyError


@pytest.mark.parametrize("read_timeout", [30.0, 7.5])
async def test_rest_requests_preserve_sdk_phase_timeouts(monkeypatch, read_timeout):
    observed = []
    original = httpx.AsyncClient

    def handle(request):
        observed.append(request.extensions["timeout"])
        return httpx.Response(200, json={"accounts": []})

    def offline_client(**kwargs):
        return original(**kwargs, transport=httpx.MockTransport(handle))

    monkeypatch.setattr("fivetwenty.client.httpx.AsyncClient", offline_client)
    async with AsyncClient(token="offline-token", account_id="offline", timeout=read_timeout) as client:
        await client.accounts.get_accounts()
    assert observed == [{"connect": 5.0, "read": read_timeout, "write": 10.0, "pool": read_timeout}]


@pytest.mark.parametrize("request_timeout", [None, 2.5, 0.0])
async def test_rest_timeout_override_preserves_or_replaces_injected_settings(request_timeout):
    observed = []
    defaults = {"connect": 1.0, "read": 2.0, "write": 3.0, "pool": 4.0}

    def handle(request):
        observed.append(request.extensions["timeout"])
        return httpx.Response(201, json={"lastTransactionID": "42"})

    transport = httpx.AsyncClient(base_url="https://offline.test/v3", transport=httpx.MockTransport(handle), timeout=httpx.Timeout(**defaults))
    async with AsyncClient(token="offline-token", account_id="offline", transport=transport, timeout=99.0) as client:
        await client.orders.post_order("offline", {"type": "MARKET", "instrument": "EUR_USD", "units": "1"}, timeout=request_timeout)
        await client.orders.post_order("offline", {"type": "MARKET", "instrument": "EUR_USD", "units": "1"})
    expected = defaults if request_timeout is None else dict.fromkeys(defaults, request_timeout)
    assert observed == [expected, defaults]


@pytest.mark.asyncio
@pytest.mark.parametrize("retry_count", [0, 1, 3])
@pytest.mark.parametrize("failure", ["status", "timeout", "connection"])
async def test_retry_budget_counts_retries_after_the_initial_request(monkeypatch, retry_count, failure):
    monkeypatch.setattr("fivetwenty.client.backoff_with_jitter", lambda attempt: 0.0)
    requests: list[httpx.Request] = []

    def handler(request):
        requests.append(request)
        if failure == "timeout":
            raise httpx.ReadTimeout("offline timeout", request=request)
        if failure == "connection":
            raise httpx.ConnectError("offline failure", request=request)
        return httpx.Response(503, headers={"Retry-After": "0"}, json={"errorMessage": "offline"})

    transport = httpx.AsyncClient(transport=httpx.MockTransport(handler), base_url="https://offline.example.test")
    async with AsyncClient(token="offline-token", account_id="offline-account", transport=transport, max_retries=retry_count) as client:
        with pytest.raises((FiveTwentyError, httpx.TransportError)):
            await client.accounts.get_accounts()
    assert len(requests) == retry_count + 1


@pytest.mark.asyncio
@pytest.mark.parametrize("method", ["GET", "POST", "PUT", "PATCH", "DELETE", "post"])
async def test_zero_retry_override_still_sends_one_request(method):
    requests = []

    def handler(request):
        requests.append(request)
        return httpx.Response(503, json={"errorMessage": "offline"})

    transport = httpx.AsyncClient(transport=httpx.MockTransport(handler), base_url="https://offline.example.test")
    async with AsyncClient(token="offline-token", account_id="offline-account", transport=transport, max_retries=3) as client:
        with pytest.raises(FiveTwentyError):
            await client._request(method, "/test", retries=0)
    assert len(requests) == 1


@pytest.mark.parametrize("value", [-1, 1.5, True])
async def test_invalid_retry_budgets_are_rejected(value):
    with pytest.raises(ValueError, match="non-negative integer"):
        AsyncClient(token="offline-token", account_id="offline-account", max_retries=value)
    requests = []

    def handler(request):
        requests.append(request)
        return httpx.Response(200)

    transport = httpx.AsyncClient(transport=httpx.MockTransport(handler), base_url="https://offline.example.test")
    async with AsyncClient(token="offline-token", account_id="offline-account", transport=transport) as client:
        with pytest.raises(ValueError, match="non-negative integer"):
            await client._request("GET", "/test", retries=value)
    assert not requests


@pytest.mark.asyncio
async def test_proxy_option_constructs_a_real_httpx_client():
    async with AsyncClient(token="offline-token", account_id="offline-account", proxies="http://127.0.0.1:8080") as client:
        assert isinstance(client._http, httpx.AsyncClient)


@pytest.mark.asyncio
async def test_request_redacts_credentials_in_log_records_without_changing_authentication(caplog: pytest.LogCaptureFixture) -> None:
    """Structured logging must not expose the token on any request attempt."""
    logger = logging.getLogger("fivetwenty.tests.request_redaction")
    caplog.set_level(logging.DEBUG, logger=logger.name)
    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        if len(requests) == 1:
            return httpx.Response(503, headers={"Retry-After": "0"}, json={"errorMessage": "Retry"})
        return httpx.Response(200, json={"accounts": []})

    transport_client = httpx.AsyncClient(transport=httpx.MockTransport(handler), base_url="https://api.example.test")
    async with AsyncClient(token="synthetic-redaction-token", account_id="acct-1", transport=transport_client, logger=logger, max_retries=2) as client:
        await client.accounts.get_accounts()

    records = [record for record in caplog.records if record.name == logger.name]
    request_records = [record for record in records if "headers" in record.__dict__]
    assert len(request_records) == 2
    assert all(record.__dict__["headers"]["Authorization"] == "Bearer ***" for record in request_records)
    assert all(record.__dict__["headers"]["Accept-Datetime-Format"] == "RFC3339" for record in request_records)
    assert all("synthetic-redaction-token" not in repr(record.__dict__) for record in records)
    assert len(requests) == 2
    assert all(request.headers["Authorization"] == "Bearer synthetic-redaction-token" for request in requests)


@pytest.mark.asyncio
@pytest.mark.parametrize("header_name", ["authorization", "Authorization", "AUTHORIZATION"])
async def test_logging_redacts_case_insensitive_headers_without_mutating_input(header_name: str, caplog: pytest.LogCaptureFixture) -> None:
    logger = logging.getLogger("fivetwenty.tests.header_redaction")
    caplog.set_level(logging.DEBUG, logger=logger.name)
    transport_client = httpx.AsyncClient(transport=httpx.MockTransport(lambda request: httpx.Response(200)))
    headers = {header_name: "Bearer synthetic-header-token", "RequestID": "request-1"}
    payload = {"headers": headers}

    async with AsyncClient(token="synthetic-header-token", account_id="acct-1", transport=transport_client, logger=logger) as client:
        client._log("debug", "Request", extra=payload)

    record = next(record for record in caplog.records if record.name == logger.name)
    assert record.__dict__["headers"] == {header_name: "Bearer ***", "RequestID": "request-1"}
    assert "synthetic-header-token" not in repr(record.__dict__)
    assert headers[header_name] == "Bearer synthetic-header-token"
    assert payload["headers"] is headers


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
            headers={"content-type": "application/json", "RequestID": "req-123"},
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


@pytest.mark.asyncio
async def test_get_request_retries_timeout_then_succeeds(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("fivetwenty.client.backoff_with_jitter", lambda attempt: 0.0)
    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        if len(requests) == 1:
            raise httpx.ReadTimeout("timed out", request=request)
        return httpx.Response(200, json={"ok": True})

    transport_client = httpx.AsyncClient(transport=httpx.MockTransport(handler), base_url="https://api.example.test")

    async with AsyncClient(token="secret-token", account_id="acct-1", transport=transport_client, max_retries=2) as client:
        response = await client._request("GET", "/v3/accounts/acct-1")

    assert response.json() == {"ok": True}
    assert len(requests) == 2


@pytest.mark.asyncio
async def test_get_request_timeout_exhausts_retries_and_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("fivetwenty.client.backoff_with_jitter", lambda attempt: 0.0)
    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        raise httpx.ReadTimeout("timed out", request=request)

    transport_client = httpx.AsyncClient(transport=httpx.MockTransport(handler), base_url="https://api.example.test")

    async with AsyncClient(token="secret-token", account_id="acct-1", transport=transport_client, max_retries=2) as client:
        with pytest.raises(httpx.ReadTimeout):
            await client._request("GET", "/v3/accounts/acct-1")

    assert len(requests) == 3


@pytest.mark.asyncio
async def test_request_sends_accept_datetime_format_header_default_rfc3339() -> None:
    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return httpx.Response(200, json={"ok": True})

    transport_client = httpx.AsyncClient(transport=httpx.MockTransport(handler), base_url="https://api.example.test")

    async with AsyncClient(token="secret-token", account_id="acct-1", transport=transport_client) as client:
        await client._request("GET", "/v3/accounts/acct-1/summary")

    assert requests[0].headers["Accept-Datetime-Format"] == "RFC3339"


@pytest.mark.asyncio
async def test_request_sends_unix_datetime_format_when_configured() -> None:
    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return httpx.Response(200, json={"ok": True})

    transport_client = httpx.AsyncClient(transport=httpx.MockTransport(handler), base_url="https://api.example.test")

    async with AsyncClient(token="secret-token", account_id="acct-1", transport=transport_client, datetime_format="UNIX") as client:
        await client._request("GET", "/v3/accounts/acct-1/summary")

    assert requests[0].headers["Accept-Datetime-Format"] == "UNIX"


@pytest.mark.asyncio
async def test_invalid_datetime_format_raises() -> None:
    with pytest.raises(ValueError):
        AsyncClient(token="secret-token", account_id="acct-1", datetime_format="ISO9000")


@pytest.mark.asyncio
async def test_write_request_not_retried_on_timeout() -> None:
    """A timed-out POST may have reached the server; retrying could double-submit."""
    attempts = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal attempts
        attempts += 1
        raise httpx.ReadTimeout("timed out", request=request)

    transport_client = httpx.AsyncClient(transport=httpx.MockTransport(handler), base_url="https://api.example.test")

    async with AsyncClient(token="secret-token", account_id="acct-1", transport=transport_client, max_retries=3) as client:
        with pytest.raises(httpx.TimeoutException):
            await client._request("POST", "/v3/accounts/acct-1/orders", json_data={"order": {}})

    assert attempts == 1
