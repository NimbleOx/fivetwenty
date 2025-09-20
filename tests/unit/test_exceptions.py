"""Test enhanced exception handling."""

from unittest.mock import Mock

import pytest

from fivetwenty.exceptions import FiveTwentyError, raise_for_fivetwenty
from fivetwenty.models.error_codes import ErrorCategory, ErrorSeverity
from fivetwenty.models.error_details import ErrorDetails, ValidationViolation


def test_oanda_error_creation() -> None:
    """Test FiveTwentyError creation and attributes."""
    error = FiveTwentyError(
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


def test_oanda_error_repr() -> None:
    """Test FiveTwentyError repr."""
    error = FiveTwentyError(
        status=500,
        code=None,
        message="Server error",
        request_id=None,
        retryable=True,
    )

    repr_str = repr(error)
    assert "FiveTwentyError" in repr_str
    assert "status=500" in repr_str
    assert "retryable=True" in repr_str


def test_raise_for_fivetwenty_success() -> None:
    """Test that successful responses don't raise."""
    response = Mock()
    response.status_code = 200

    # Should not raise
    raise_for_fivetwenty(response)

    response.status_code = 201
    raise_for_fivetwenty(response)


def test_raise_for_fivetwenty_json_error() -> None:
    """Test JSON error response parsing."""
    response = Mock()
    response.status_code = 400
    response.headers = {"content-type": "application/json", "X-Request-Id": "req-456"}
    response.json.return_value = {
        "errorCode": "INSUFFICIENT_MARGIN",
        "errorMessage": "Insufficient margin for trade",
    }
    response.text = ""

    with pytest.raises(FiveTwentyError) as exc_info:
        raise_for_fivetwenty(response)

    error = exc_info.value
    assert error.status == 400
    assert error.code == "INSUFFICIENT_MARGIN"
    assert error.message == "Insufficient margin for trade"
    assert error.request_id == "req-456"
    assert error.retryable is False  # 400 is not retryable


def test_raise_for_fivetwenty_html_error() -> None:
    """Test HTML error page handling."""
    response = Mock()
    response.status_code = 502
    response.headers = {"content-type": "text/html"}
    response.json.side_effect = ValueError("Not JSON")
    response.text = "<html><body>502 Bad Gateway</body></html>"

    with pytest.raises(FiveTwentyError) as exc_info:
        raise_for_fivetwenty(response)

    error = exc_info.value
    assert error.status == 502
    assert error.code is None
    assert "502 Bad Gateway" in error.message
    assert error.retryable is True  # 502 is retryable


def test_raise_for_fivetwenty_retryable_status() -> None:
    """Test retryable status code detection."""
    retryable_codes = [429, 502, 503, 504]

    for code in retryable_codes:
        response = Mock()
        response.status_code = code
        response.headers = {}
        response.json.return_value = {}
        response.text = f"Error {code}"

        with pytest.raises(FiveTwentyError) as exc_info:
            raise_for_fivetwenty(response)

        assert exc_info.value.retryable is True


def test_raise_for_fivetwenty_malformed_json() -> None:
    """Test malformed JSON handling."""
    response = Mock()
    response.status_code = 500
    response.headers = {"content-type": "application/json"}
    response.json.side_effect = ValueError("Invalid JSON")
    response.text = "Internal Server Error"

    with pytest.raises(FiveTwentyError) as exc_info:
        raise_for_fivetwenty(response)

    error = exc_info.value
    assert error.status == 500
    assert error.code is None
    assert error.message == "Internal Server Error"


class TestEnhancedFiveTwentyError:
    """Test enhanced FiveTwentyError functionality."""

    def test_error_category_property(self):
        """Test error category property."""
        error = FiveTwentyError(status=401, code="INVALID_TOKEN", message="Invalid token")

        assert error.error_category == ErrorCategory.AUTHENTICATION

    def test_error_severity_property(self):
        """Test error severity property."""
        error = FiveTwentyError(status=401, code="INVALID_TOKEN", message="Invalid token")

        assert error.error_severity == ErrorSeverity.CRITICAL

    def test_is_client_error(self):
        """Test client error detection."""
        client_error = FiveTwentyError(status=400, message="Bad request")
        assert client_error.is_client_error
        assert not client_error.is_server_error

        server_error = FiveTwentyError(status=500, message="Server error")
        assert not server_error.is_client_error
        assert server_error.is_server_error

    def test_is_authentication_error(self):
        """Test authentication error detection."""
        auth_error = FiveTwentyError(status=401, code="INVALID_TOKEN", message="Invalid token")
        assert auth_error.is_authentication_error

        validation_error = FiveTwentyError(status=400, code="VALIDATION_ERROR", message="Validation failed")
        assert not validation_error.is_authentication_error

    def test_is_validation_error(self):
        """Test validation error detection."""
        # Error with validation category
        validation_error = FiveTwentyError(status=400, code="PRECISION_EXCEEDED", message="Price precision exceeded")
        assert validation_error.is_validation_error

        # Error with validation details
        details = ErrorDetails(message="Validation failed", violations=[ValidationViolation(field="units", message="Invalid units")])
        validation_error_with_details = FiveTwentyError(status=400, message="Validation failed", details=details)
        assert validation_error_with_details.is_validation_error

    def test_is_rate_limited(self):
        """Test rate limiting error detection."""
        # Status code based
        rate_limited = FiveTwentyError(status=429, message="Too many requests")
        assert rate_limited.is_rate_limited

        # Error code based
        rate_limited_code = FiveTwentyError(status=400, code="RATE_LIMIT_EXCEEDED", message="Rate limit exceeded")
        assert rate_limited_code.is_rate_limited

    def test_is_not_found(self):
        """Test not found error detection."""
        # Status code based
        not_found = FiveTwentyError(status=404, message="Not found")
        assert not_found.is_not_found

        # Error code based
        trade_not_found = FiveTwentyError(status=400, code="TRADE_DOESNT_EXIST", message="Trade doesn't exist")
        assert trade_not_found.is_not_found

    def test_retry_after_property(self):
        """Test retry-after header parsing."""
        # Mock response with Retry-After header
        response = Mock()
        response.headers = {"Retry-After": "30"}

        error = FiveTwentyError(status=429, message="Rate limited", response=response)

        assert error.retry_after == 30

        # Error without response
        error_no_response = FiveTwentyError(status=429, message="Rate limited")
        assert error_no_response.retry_after is None

        # Invalid retry-after value
        response_invalid = Mock()
        response_invalid.headers = {"Retry-After": "not-a-number"}
        error_invalid = FiveTwentyError(status=429, message="Rate limited", response=response_invalid)
        assert error_invalid.retry_after is None

    def test_get_validation_errors(self):
        """Test getting validation errors."""
        violations = [
            ValidationViolation(field="units", message="Units must be positive"),
            ValidationViolation(field="price", message="Price required"),
        ]
        details = ErrorDetails(message="Validation failed", violations=violations)

        error = FiveTwentyError(status=400, message="Validation failed", details=details)

        field_errors = error.get_validation_errors()
        assert "units" in field_errors
        assert "price" in field_errors
        assert field_errors["units"] == ["Units must be positive"]
        assert field_errors["price"] == ["Price required"]

        # Error without details
        error_no_details = FiveTwentyError(status=400, message="Error")
        assert error_no_details.get_validation_errors() == {}

    def test_get_remediation_message(self):
        """Test getting remediation messages."""
        error = FiveTwentyError(status=401, code="INVALID_TOKEN", message="Invalid token")

        remediation = error.get_remediation_message()
        assert remediation is not None
        assert "token" in remediation.lower()

        # Error without code
        error_no_code = FiveTwentyError(status=400, message="Error")
        assert error_no_code.get_remediation_message() is None

        # Unknown error code
        error_unknown = FiveTwentyError(status=400, code="UNKNOWN_ERROR_CODE", message="Unknown error")
        assert error_unknown.get_remediation_message() is None

    def test_string_representation_with_validation_errors(self):
        """Test string representation includes validation error count."""
        violations = [
            ValidationViolation(field="units", message="Invalid units"),
            ValidationViolation(field="price", message="Invalid price"),
        ]
        details = ErrorDetails(message="Validation failed", violations=violations)

        error = FiveTwentyError(status=400, code="VALIDATION_ERROR", message="Validation failed", request_id="req-123", details=details)

        error_str = str(error)
        assert "HTTP 400" in error_str
        assert "VALIDATION_ERROR" in error_str
        assert "2 validation errors" in error_str

    def test_enhanced_repr(self):
        """Test enhanced repr includes category and severity."""
        error = FiveTwentyError(status=401, code="INVALID_TOKEN", message="Invalid token")

        repr_str = repr(error)
        assert "FiveTwentyError" in repr_str
        assert "category=" in repr_str
        assert "AUTHENTICATION" in repr_str
        assert "severity=" in repr_str
        assert "CRITICAL" in repr_str

    def test_rate_limit_specific_remediation(self):
        """Test rate limit remediation includes retry-after."""
        response = Mock()
        response.headers = {"Retry-After": "60"}

        error = FiveTwentyError(status=429, code="RATE_LIMIT_EXCEEDED", message="Rate limit exceeded", response=response)

        remediation = error.get_remediation_message()
        assert "60 seconds" in remediation


class TestRaiseForOandaEnhanced:
    """Test enhanced raise_for_fivetwenty functionality."""

    def test_raise_with_validation_errors(self):
        """Test raising error with validation violations."""
        response = Mock()
        response.status_code = 400
        response.headers = {"content-type": "application/json"}
        response.json.return_value = {"errorCode": "VALIDATION_ERROR", "errorMessage": "Validation failed", "violations": [{"field": "units", "message": "Units must be positive", "code": "INVALID_VALUE"}]}
        response.text = ""

        with pytest.raises(FiveTwentyError) as exc_info:
            raise_for_fivetwenty(response)

        error = exc_info.value
        assert error.details is not None
        assert error.details.has_validation_errors()
        assert len(error.details.violations) == 1
        assert error.details.violations[0].field == "units"

    def test_raise_with_rate_limit_code(self):
        """Test that RATE_LIMIT_EXCEEDED error code makes error retryable."""
        response = Mock()
        response.status_code = 400  # Not normally retryable
        response.headers = {"content-type": "application/json"}
        response.json.return_value = {"errorCode": "RATE_LIMIT_EXCEEDED", "errorMessage": "Rate limit exceeded"}
        response.text = ""

        with pytest.raises(FiveTwentyError) as exc_info:
            raise_for_fivetwenty(response)

        error = exc_info.value
        assert error.retryable is True  # Should be retryable due to error code

    def test_raise_with_additional_error_fields(self):
        """Test parsing additional error context."""
        response = Mock()
        response.status_code = 400
        response.headers = {"content-type": "application/json"}
        response.json.return_value = {"errorCode": "INSUFFICIENT_MARGIN", "errorMessage": "Insufficient margin", "marginRequired": "1000.00", "marginAvailable": "500.00"}
        response.text = ""

        with pytest.raises(FiveTwentyError) as exc_info:
            raise_for_fivetwenty(response)

        error = exc_info.value
        assert error.details is not None
        assert error.details.additional_fields["marginRequired"] == "1000.00"
        assert error.details.additional_fields["marginAvailable"] == "500.00"
