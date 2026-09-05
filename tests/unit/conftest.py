"""Unit tests never use real HTTP transports, even when credentials are present."""

import httpx
import pytest


@pytest.fixture(autouse=True)
def block_unmocked_http(monkeypatch):
    def blocked(*args, **kwargs):
        raise AssertionError("Unit tests must supply an HTTP mock transport")

    monkeypatch.setattr(httpx.HTTPTransport, "handle_request", blocked)
    monkeypatch.setattr(httpx.AsyncHTTPTransport, "handle_async_request", blocked)
