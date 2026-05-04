"""Tests for live integration safety helpers."""

from tests.integration.conftest import CLIENT_REQUEST_ID_PREFIX, _client_request_id_factory
from tests.integration.helpers import cleanup_error_message, is_tolerated_cleanup_error


class _MissingResourceError(Exception):
    status = 404


def test_client_request_id_factory_prefixes_and_bounds_values() -> None:
    make_client_request_id = _client_request_id_factory("tests/integration/test_file.py::test_name")

    first_id = make_client_request_id("custom request with spaces")
    second_id = make_client_request_id()

    assert first_id.startswith(f"{CLIENT_REQUEST_ID_PREFIX}-")
    assert second_id.startswith(f"{CLIENT_REQUEST_ID_PREFIX}-")
    assert first_id != second_id
    assert len(first_id) <= 128
    assert " " not in first_id


def test_cleanup_error_classification_and_message() -> None:
    exc = _MissingResourceError("missing")

    assert is_tolerated_cleanup_error(exc)
    assert cleanup_error_message("order", "123", exc) == "order 123: _MissingResourceError: missing"
