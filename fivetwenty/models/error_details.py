"""OANDA API error detail models."""

from typing import Any

from pydantic import BaseModel

__all__ = [
    "ApiErrorResponse",
    "ApiRateLimitInfo",
    "ApiValidationSchema",
    "ErrorContext",
    "ErrorDetails",
    "FieldValidation",
    "ValidationRuleViolation",
    "ValidationViolation",
]


class ValidationViolation(BaseModel):
    """A single validation violation from OANDA API error responses."""

    field: str
    """The field that failed validation."""

    message: str
    """Human-readable validation error message."""

    code: str | None = None
    """Machine-readable error code for the violation."""


class ErrorDetails(BaseModel):
    """Structured error details from OANDA API responses."""

    message: str
    """Primary error message."""

    code: str | None = None
    """Primary error code."""

    violations: list[ValidationViolation] = []
    """List of validation violations (for validation errors)."""

    additional_fields: dict[str, Any] = {}
    """Any additional error context from the API response."""

    @classmethod
    def from_api_response(cls, payload: dict[str, Any]) -> "ErrorDetails":
        """Parse error details from OANDA API error response."""
        message = payload.get("errorMessage", "Unknown error")
        code = payload.get("errorCode")

        # Parse validation violations if present
        violation_data = payload.get("violations", [])
        violations = [ValidationViolation(field=violation.get("field", "unknown"), message=violation.get("message", "Validation failed"), code=violation.get("code")) for violation in violation_data if isinstance(violation, dict)]

        # Collect any additional fields for context
        additional_fields = {key: value for key, value in payload.items() if key not in {"errorMessage", "errorCode", "violations"}}

        return cls(message=message, code=code, violations=violations, additional_fields=additional_fields)

    def get_field_errors(self) -> dict[str, list[str]]:
        """Get validation errors grouped by field name."""
        field_errors: dict[str, list[str]] = {}
        for violation in self.violations:
            if violation.field not in field_errors:
                field_errors[violation.field] = []
            field_errors[violation.field].append(violation.message)
        return field_errors

    def has_validation_errors(self) -> bool:
        """Check if this error contains validation violations."""
        return len(self.violations) > 0

    def get_violation_by_field(self, field: str) -> ValidationViolation | None:
        """Get the first validation violation for a specific field."""
        for violation in self.violations:
            if violation.field == field:
                return violation
        return None


class ApiRateLimitInfo(BaseModel):
    """Information about API rate limiting."""

    limit: int
    """Maximum requests allowed in the time window."""

    remaining: int
    """Requests remaining in current time window."""

    reset_time: str
    """When the rate limit window resets (ISO 8601 timestamp)."""

    window_seconds: int
    """Duration of the rate limit window in seconds."""

    @property
    def usage_percentage(self) -> float:
        """Calculate percentage of rate limit used."""
        if self.limit == 0:
            return 0.0
        return ((self.limit - self.remaining) / self.limit) * 100.0

    @property
    def is_near_limit(self) -> bool:
        """Check if close to rate limit (>80% usage)."""
        return self.usage_percentage > 80.0


class ValidationRuleViolation(BaseModel):
    """Detailed validation rule violation with context."""

    rule_id: str
    """Unique identifier for the validation rule."""

    field_path: str
    """JSON path to the field that failed validation."""

    expected_type: str | None = None
    """Expected data type for the field."""

    expected_format: str | None = None
    """Expected format pattern for the field."""

    min_value: float | None = None
    """Minimum allowed value (for numeric fields)."""

    max_value: float | None = None
    """Maximum allowed value (for numeric fields)."""

    allowed_values: list[str] = []
    """List of allowed values (for enum fields)."""

    actual_value: str | None = None
    """The actual value that failed validation."""

    suggested_value: str | None = None
    """A suggested correct value."""

    help_text: str | None = None
    """Additional help text for resolving the error."""


class ErrorContext(BaseModel):
    """Additional context information for errors."""

    request_id: str | None = None
    """Unique identifier for the request that caused the error."""

    endpoint: str | None = None
    """API endpoint that was called."""

    method: str | None = None
    """HTTP method used."""

    account_id: str | None = None
    """Account ID associated with the request."""

    instrument: str | None = None
    """Instrument involved in the error (if applicable)."""

    timestamp: str | None = None
    """When the error occurred."""

    user_agent: str | None = None
    """User agent of the client."""

    ip_address: str | None = None
    """IP address of the client (if available)."""


class ApiErrorResponse(BaseModel):
    """Complete API error response with enhanced details."""

    error_message: str
    """Primary error message."""

    error_code: str | None = None
    """Primary error code."""

    category: str | None = None
    """Error category (VALIDATION, BUSINESS_LOGIC, etc.)."""

    severity: str | None = None
    """Error severity (INFO, WARNING, ERROR, CRITICAL)."""

    violations: list[ValidationRuleViolation] = []
    """Detailed validation violations."""

    context: ErrorContext | None = None
    """Additional error context."""

    rate_limit_info: ApiRateLimitInfo | None = None
    """Rate limiting information (if applicable)."""

    retry_after: int | None = None
    """Seconds to wait before retrying (for rate limits)."""

    documentation_url: str | None = None
    """URL to relevant documentation."""

    @property
    def is_retryable(self) -> bool:
        """Check if this error indicates a retryable condition."""
        retryable_categories = ["RATE_LIMITING", "SERVER_ERROR"]
        return self.category in retryable_categories

    @property
    def is_client_error(self) -> bool:
        """Check if this is a client-side error (4xx)."""
        client_categories = ["VALIDATION", "AUTHENTICATION", "AUTHORIZATION", "NOT_FOUND"]
        return self.category in client_categories

    def get_retry_delay(self) -> int:
        """Get recommended retry delay in seconds."""
        if self.retry_after:
            return self.retry_after
        if self.category == "RATE_LIMITING":
            return 60  # Default 1 minute for rate limits
        if self.category == "SERVER_ERROR":
            return 5  # Default 5 seconds for server errors
        return 0  # No retry for client errors


class FieldValidation(BaseModel):
    """Field-level validation information."""

    field_name: str
    """Name of the field being validated."""

    required: bool = False
    """Whether the field is required."""

    data_type: str | None = None
    """Expected data type."""

    min_length: int | None = None
    """Minimum string length."""

    max_length: int | None = None
    """Maximum string length."""

    pattern: str | None = None
    """Regex pattern for validation."""

    min_value: float | None = None
    """Minimum numeric value."""

    max_value: float | None = None
    """Maximum numeric value."""

    enum_values: list[str] = []
    """Allowed enumeration values."""

    dependencies: list[str] = []
    """Other fields this field depends on."""

    description: str | None = None
    """Human-readable field description."""

    example: str | None = None
    """Example valid value."""


class ApiValidationSchema(BaseModel):
    """Complete validation schema for API requests."""

    endpoint: str
    """API endpoint this schema applies to."""

    method: str
    """HTTP method."""

    fields: list[FieldValidation] = []
    """Field validation rules."""

    global_rules: list[str] = []
    """Global validation rules that apply to the entire request."""

    def get_field_validation(self, field_name: str) -> FieldValidation | None:
        """Get validation rules for a specific field."""
        for field in self.fields:
            if field.field_name == field_name:
                return field
        return None

    def get_required_fields(self) -> list[str]:
        """Get list of required field names."""
        return [field.field_name for field in self.fields if field.required]
