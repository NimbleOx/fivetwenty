"""Test exception handling."""

import pytest
from unittest.mock import Mock

from oanda.exceptions import OandaError, raise_for_oanda


def test_oanda_error_creation():
    """Test OandaError creation and attributes."""
    error = OandaError(
        status=400,
        code="INVALID_INSTRUMENT",
        message="Invalid instrument specified",
        request_id="req-123",
        retryable=False,
    )
    
    assert error.status == 400
    assert error.code == "INVALID_INSTRUMENT"
    assert error.message == "Invalid instrument specified"
    assert error.request_id == "req-123"
    assert error.retryable is False
    
    # Test string representation
    error_str = str(error)
    assert "HTTP 400" in error_str
    assert "INVALID_INSTRUMENT" in error_str
    assert "req-123" in error_str


def test_oanda_error_repr():
    """Test OandaError repr."""
    error = OandaError(
        status=500,
        code=None,
        message="Server error",
        request_id=None,
        retryable=True,
    )
    
    repr_str = repr(error)
    assert "OandaError" in repr_str
    assert "status=500" in repr_str
    assert "retryable=True" in repr_str


def test_raise_for_oanda_success():
    """Test that successful responses don't raise."""
    response = Mock()
    response.status_code = 200
    
    # Should not raise
    raise_for_oanda(response)
    
    response.status_code = 201
    raise_for_oanda(response)


def test_raise_for_oanda_json_error():
    """Test JSON error response parsing."""
    response = Mock()
    response.status_code = 400
    response.headers = {
        "content-type": "application/json",
        "X-Request-Id": "req-456"
    }
    response.json.return_value = {
        "errorCode": "INSUFFICIENT_MARGIN",
        "errorMessage": "Insufficient margin for trade"
    }
    response.text = ""
    
    with pytest.raises(OandaError) as exc_info:
        raise_for_oanda(response)
    
    error = exc_info.value
    assert error.status == 400
    assert error.code == "INSUFFICIENT_MARGIN"
    assert error.message == "Insufficient margin for trade"
    assert error.request_id == "req-456"
    assert error.retryable is False  # 400 is not retryable


def test_raise_for_oanda_html_error():
    """Test HTML error page handling."""
    response = Mock()
    response.status_code = 502
    response.headers = {"content-type": "text/html"}
    response.json.side_effect = ValueError("Not JSON")
    response.text = "<html><body>502 Bad Gateway</body></html>"
    
    with pytest.raises(OandaError) as exc_info:
        raise_for_oanda(response)
    
    error = exc_info.value
    assert error.status == 502
    assert error.code is None
    assert "502 Bad Gateway" in error.message
    assert error.retryable is True  # 502 is retryable


def test_raise_for_oanda_retryable_status():
    """Test retryable status code detection."""
    retryable_codes = [429, 502, 503, 504]
    
    for code in retryable_codes:
        response = Mock()
        response.status_code = code
        response.headers = {}
        response.json.return_value = {}
        response.text = f"Error {code}"
        
        with pytest.raises(OandaError) as exc_info:
            raise_for_oanda(response)
        
        assert exc_info.value.retryable is True


def test_raise_for_oanda_malformed_json():
    """Test malformed JSON handling."""
    response = Mock()
    response.status_code = 500
    response.headers = {"content-type": "application/json"}
    response.json.side_effect = ValueError("Invalid JSON")
    response.text = "Internal Server Error"
    
    with pytest.raises(OandaError) as exc_info:
        raise_for_oanda(response)
    
    error = exc_info.value
    assert error.status == 500
    assert error.code is None
    assert error.message == "Internal Server Error"