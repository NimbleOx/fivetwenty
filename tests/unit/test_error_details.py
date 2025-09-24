"""Tests for error details and validation models."""

from fivetwenty.models.error_details import ErrorDetails, ValidationViolation


class TestValidationViolation:
    """Test ValidationViolation model."""

    def test_validation_violation_creation(self):
        """Test creating ValidationViolation."""
        violation = ValidationViolation(field="units", message="Units must be non-zero", code="INVALID_VALUE")

        assert violation.field == "units"
        assert violation.message == "Units must be non-zero"
        assert violation.code == "INVALID_VALUE"

    def test_validation_violation_without_code(self):
        """Test creating ValidationViolation without code."""
        violation = ValidationViolation(field="price", message="Price is required")

        assert violation.field == "price"
        assert violation.message == "Price is required"
        assert violation.code is None


class TestErrorDetails:
    """Test ErrorDetails model."""

    def test_error_details_creation(self):
        """Test creating ErrorDetails."""
        violations = [ValidationViolation(field="units", message="Invalid units"), ValidationViolation(field="price", message="Invalid price")]

        details = ErrorDetails(message="Validation failed", code="VALIDATION_ERROR", violations=violations, additional_fields={"context": "order_creation"})

        assert details.message == "Validation failed"
        assert details.code == "VALIDATION_ERROR"
        assert len(details.violations) == 2
        assert details.additional_fields["context"] == "order_creation"

    def test_from_api_response_simple_error(self):
        """Test parsing simple error from API response."""
        payload = {"errorMessage": "Invalid instrument", "errorCode": "INVALID_INSTRUMENT"}

        details = ErrorDetails.from_api_response(payload)

        assert details.message == "Invalid instrument"
        assert details.code == "INVALID_INSTRUMENT"
        assert len(details.violations) == 0
        assert len(details.additional_fields) == 0

    def test_from_api_response_validation_error(self):
        """Test parsing validation error with violations from API response."""
        payload = {"errorMessage": "Validation failed", "errorCode": "VALIDATION_ERROR", "violations": [{"field": "units", "message": "Units must be non-zero", "code": "INVALID_VALUE"}, {"field": "price", "message": "Price precision exceeded"}]}

        details = ErrorDetails.from_api_response(payload)

        assert details.message == "Validation failed"
        assert details.code == "VALIDATION_ERROR"
        assert len(details.violations) == 2

        assert details.violations[0].field == "units"
        assert details.violations[0].message == "Units must be non-zero"
        assert details.violations[0].code == "INVALID_VALUE"

        assert details.violations[1].field == "price"
        assert details.violations[1].message == "Price precision exceeded"
        assert details.violations[1].code is None

    def test_from_api_response_with_additional_fields(self):
        """Test parsing error with additional fields."""
        payload = {"errorMessage": "Order rejected", "errorCode": "INSUFFICIENT_MARGIN", "marginRequired": "1000.00", "marginAvailable": "500.00", "instrument": "EUR_USD"}

        details = ErrorDetails.from_api_response(payload)

        assert details.message == "Order rejected"
        assert details.code == "INSUFFICIENT_MARGIN"
        assert details.additional_fields["marginRequired"] == "1000.00"
        assert details.additional_fields["marginAvailable"] == "500.00"
        assert details.additional_fields["instrument"] == "EUR_USD"

    def test_from_api_response_malformed_violations(self):
        """Test parsing error with malformed violations data."""
        payload = {
            "errorMessage": "Validation failed",
            "violations": [
                "not_a_dict",
                {},  # Empty dict
                {"field": "units"},  # Missing message
            ],
        }

        details = ErrorDetails.from_api_response(payload)

        assert details.message == "Validation failed"
        # Should handle malformed violations gracefully
        assert len(details.violations) == 2  # Only valid ones
        assert details.violations[0].field == "unknown"
        assert details.violations[1].field == "units"

    def test_get_field_errors(self):
        """Test getting validation errors grouped by field."""
        violations = [
            ValidationViolation(field="units", message="Units must be positive"),
            ValidationViolation(field="units", message="Units exceed maximum"),
            ValidationViolation(field="price", message="Price is required"),
        ]

        details = ErrorDetails(message="Validation failed", violations=violations)

        field_errors = details.get_field_errors()

        assert "units" in field_errors
        assert "price" in field_errors
        assert len(field_errors["units"]) == 2
        assert len(field_errors["price"]) == 1
        assert "Units must be positive" in field_errors["units"]
        assert "Units exceed maximum" in field_errors["units"]
        assert "Price is required" in field_errors["price"]

    def test_has_validation_errors(self):
        """Test checking if error has validation violations."""
        # Error without violations
        details1 = ErrorDetails(message="Simple error")
        assert not details1.has_validation_errors()

        # Error with violations
        details2 = ErrorDetails(message="Validation failed", violations=[ValidationViolation(field="units", message="Invalid")])
        assert details2.has_validation_errors()

    def test_get_violation_by_field(self):
        """Test getting first violation for a specific field."""
        violations = [
            ValidationViolation(field="units", message="First units error"),
            ValidationViolation(field="price", message="Price error"),
            ValidationViolation(field="units", message="Second units error"),
        ]

        details = ErrorDetails(message="Validation failed", violations=violations)

        units_violation = details.get_violation_by_field("units")
        assert units_violation is not None
        assert units_violation.message == "First units error"

        price_violation = details.get_violation_by_field("price")
        assert price_violation is not None
        assert price_violation.message == "Price error"

        # Non-existent field
        invalid_violation = details.get_violation_by_field("invalid_field")
        assert invalid_violation is None

    def test_from_api_response_empty_payload(self):
        """Test parsing empty API response payload."""
        payload = {}

        details = ErrorDetails.from_api_response(payload)

        assert details.message == "Unknown error"
        assert details.code is None
        assert len(details.violations) == 0
        assert len(details.additional_fields) == 0
