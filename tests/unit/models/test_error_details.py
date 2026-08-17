"""Tests for OANDA API error detail models."""

from fivetwenty.models import (
    ApiErrorResponse,
    ApiRateLimitInfo,
    ApiValidationSchema,
    ErrorContext,
    FieldValidation,
    ValidationRuleViolation,
)


class TestApiRateLimitInfo:
    """Test ApiRateLimitInfo model and helpers."""

    def test_rate_limit_info(self) -> None:
        """Test ApiRateLimitInfo fields and usage calculation."""
        info = ApiRateLimitInfo(limit=100, remaining=75, reset_time="2024-01-15T12:01:00Z", window_seconds=60)
        assert info.limit == 100
        assert info.remaining == 75
        assert info.reset_time == "2024-01-15T12:01:00Z"
        assert info.window_seconds == 60
        assert info.usage_percentage == 25.0
        assert info.is_near_limit is False

    def test_rate_limit_info_near_limit(self) -> None:
        """Test is_near_limit above the 80% threshold."""
        info = ApiRateLimitInfo(limit=100, remaining=10, reset_time="2024-01-15T12:01:00Z", window_seconds=60)
        assert info.usage_percentage == 90.0
        assert info.is_near_limit is True

    def test_rate_limit_info_zero_limit(self) -> None:
        """Test usage_percentage with a zero limit."""
        info = ApiRateLimitInfo(limit=0, remaining=0, reset_time="2024-01-15T12:01:00Z", window_seconds=60)
        assert info.usage_percentage == 0.0


class TestValidationRuleViolation:
    """Test ValidationRuleViolation model."""

    def test_validation_rule_violation(self) -> None:
        """Test ValidationRuleViolation fields and defaults."""
        violation = ValidationRuleViolation(
            rule_id="UNITS_PRECISION",
            field_path="order.units",
            expected_type="DecimalNumber",
            allowed_values=[],
            actual_value="1.23456789",
            suggested_value="1.23457",
            help_text="Reduce the precision of units.",
        )
        assert violation.rule_id == "UNITS_PRECISION"
        assert violation.field_path == "order.units"
        assert violation.expected_type == "DecimalNumber"
        assert violation.actual_value == "1.23456789"
        assert violation.suggested_value == "1.23457"
        assert violation.min_value is None
        assert violation.max_value is None
        assert violation.allowed_values == []


class TestErrorContext:
    """Test ErrorContext model."""

    def test_error_context(self) -> None:
        """Test ErrorContext fields and defaults."""
        context = ErrorContext(
            request_id="req-001",
            endpoint="/v3/accounts/101-001-123456-001/orders",
            method="POST",
            account_id="101-001-123456-001",
            instrument="EUR_USD",
        )
        assert context.request_id == "req-001"
        assert context.endpoint == "/v3/accounts/101-001-123456-001/orders"
        assert context.method == "POST"
        assert context.account_id == "101-001-123456-001"
        assert context.instrument == "EUR_USD"
        assert context.timestamp is None
        assert context.ip_address is None


class TestApiErrorResponse:
    """Test ApiErrorResponse model and helpers."""

    def test_api_error_response(self) -> None:
        """Test ApiErrorResponse with nested violations and context."""
        response = ApiErrorResponse(
            error_message="Invalid units precision",
            error_code="UNITS_PRECISION_EXCEEDED",
            category="VALIDATION",
            severity="ERROR",
            violations=[ValidationRuleViolation(rule_id="UNITS_PRECISION", field_path="order.units")],
            context=ErrorContext(request_id="req-001"),
        )
        assert response.error_message == "Invalid units precision"
        assert response.error_code == "UNITS_PRECISION_EXCEEDED"
        assert response.category == "VALIDATION"
        assert len(response.violations) == 1
        assert response.violations[0].rule_id == "UNITS_PRECISION"
        assert response.context is not None
        assert response.context.request_id == "req-001"
        assert response.is_client_error is True
        assert response.is_retryable is False
        assert response.get_retry_delay() == 0

    def test_api_error_response_retry_behaviour(self) -> None:
        """Test retryable categories and retry delays."""
        rate_limited = ApiErrorResponse(error_message="Rate limit exceeded", category="RATE_LIMITING")
        assert rate_limited.is_retryable is True
        assert rate_limited.get_retry_delay() == 60

        server_error = ApiErrorResponse(error_message="Internal error", category="SERVER_ERROR")
        assert server_error.is_retryable is True
        assert server_error.get_retry_delay() == 5

        explicit = ApiErrorResponse(error_message="Rate limit exceeded", category="RATE_LIMITING", retry_after=30)
        assert explicit.get_retry_delay() == 30


class TestFieldValidation:
    """Test FieldValidation model."""

    def test_field_validation(self) -> None:
        """Test FieldValidation fields and defaults."""
        validation = FieldValidation(
            field_name="units",
            required=True,
            data_type="DecimalNumber",
            min_value=1.0,
            enum_values=[],
            description="Order size in units of the base currency.",
            example="1000",
        )
        assert validation.field_name == "units"
        assert validation.required is True
        assert validation.data_type == "DecimalNumber"
        assert validation.min_value == 1.0
        assert validation.max_length is None
        assert validation.dependencies == []


class TestApiValidationSchema:
    """Test ApiValidationSchema model and helpers."""

    def test_api_validation_schema(self) -> None:
        """Test ApiValidationSchema field lookup helpers."""
        schema = ApiValidationSchema(
            endpoint="/v3/accounts/{accountID}/orders",
            method="POST",
            fields=[
                FieldValidation(field_name="instrument", required=True),
                FieldValidation(field_name="units", required=True),
                FieldValidation(field_name="priceBound", required=False),
            ],
            global_rules=["order must be wrapped in an 'order' key"],
        )
        assert schema.endpoint == "/v3/accounts/{accountID}/orders"
        assert schema.method == "POST"
        assert schema.get_required_fields() == ["instrument", "units"]

        units = schema.get_field_validation("units")
        assert units is not None
        assert units.required is True
        assert schema.get_field_validation("missing") is None
