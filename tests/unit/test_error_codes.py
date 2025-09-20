"""Tests for OANDA error codes and categories."""

import pytest

from fivetwenty.models.error_codes import ErrorCategory, ErrorSeverity, FiveTwentyErrorCode, get_error_category, get_error_severity


class TestFiveTwentyErrorCode:
    """Test OANDA error code enum."""

    def test_error_code_values(self):
        """Test that error codes have expected values."""
        assert FiveTwentyErrorCode.INVALID_TOKEN == "INVALID_TOKEN"
        assert FiveTwentyErrorCode.INSUFFICIENT_MARGIN == "INSUFFICIENT_MARGIN"
        assert FiveTwentyErrorCode.RATE_LIMIT_EXCEEDED == "RATE_LIMIT_EXCEEDED"

    def test_error_code_creation_from_string(self):
        """Test creating error codes from string values."""
        error_code = FiveTwentyErrorCode("INVALID_TOKEN")
        assert error_code == FiveTwentyErrorCode.INVALID_TOKEN

        # Test unknown error code
        with pytest.raises(ValueError, match="is not a valid"):
            FiveTwentyErrorCode("UNKNOWN_ERROR_CODE")


class TestErrorCategory:
    """Test error category enum."""

    def test_error_categories(self):
        """Test error category values."""
        assert ErrorCategory.AUTHENTICATION == "AUTHENTICATION"
        assert ErrorCategory.VALIDATION == "VALIDATION"
        assert ErrorCategory.BUSINESS_LOGIC == "BUSINESS_LOGIC"
        assert ErrorCategory.RATE_LIMITING == "RATE_LIMITING"


class TestErrorSeverity:
    """Test error severity enum."""

    def test_error_severities(self):
        """Test error severity values."""
        assert ErrorSeverity.INFO == "INFO"
        assert ErrorSeverity.WARNING == "WARNING"
        assert ErrorSeverity.ERROR == "ERROR"
        assert ErrorSeverity.CRITICAL == "CRITICAL"


class TestErrorCategoryMapping:
    """Test error code to category mapping."""

    def test_get_error_category_with_enum(self):
        """Test getting category from error code enum."""
        category = get_error_category(FiveTwentyErrorCode.INVALID_TOKEN)
        assert category == ErrorCategory.AUTHENTICATION

        category = get_error_category(FiveTwentyErrorCode.INSUFFICIENT_MARGIN)
        assert category == ErrorCategory.BUSINESS_LOGIC

        category = get_error_category(FiveTwentyErrorCode.VALIDATION_ERROR)
        assert category == ErrorCategory.VALIDATION

    def test_get_error_category_with_string(self):
        """Test getting category from error code string."""
        category = get_error_category("INVALID_TOKEN")
        assert category == ErrorCategory.AUTHENTICATION

        category = get_error_category("RATE_LIMIT_EXCEEDED")
        assert category == ErrorCategory.RATE_LIMITING

    def test_get_error_category_with_unknown_code(self):
        """Test getting category for unknown error code."""
        category = get_error_category("UNKNOWN_ERROR_CODE")
        assert category is None

        category = get_error_category(None)
        assert category is None

    def test_authentication_errors_categorized(self):
        """Test that authentication errors are properly categorized."""
        auth_errors = [
            FiveTwentyErrorCode.INVALID_TOKEN,
            FiveTwentyErrorCode.INSUFFICIENT_AUTHORIZATION,
        ]

        for error_code in auth_errors:
            category = get_error_category(error_code)
            assert category in {ErrorCategory.AUTHENTICATION, ErrorCategory.AUTHORIZATION}

    def test_validation_errors_categorized(self):
        """Test that validation errors are properly categorized."""
        validation_errors = [
            FiveTwentyErrorCode.INVALID_REQUEST,
            FiveTwentyErrorCode.PRECISION_EXCEEDED,
            FiveTwentyErrorCode.INVALID_VALUE,
            FiveTwentyErrorCode.PRICE_PRECISION_EXCEEDED,
        ]

        for error_code in validation_errors:
            category = get_error_category(error_code)
            assert category == ErrorCategory.VALIDATION

    def test_business_logic_errors_categorized(self):
        """Test that business logic errors are properly categorized."""
        business_errors = [
            FiveTwentyErrorCode.INSUFFICIENT_MARGIN,
            FiveTwentyErrorCode.MARKET_HALTED,
            FiveTwentyErrorCode.INSTRUMENT_NOT_TRADEABLE,
        ]

        for error_code in business_errors:
            category = get_error_category(error_code)
            assert category == ErrorCategory.BUSINESS_LOGIC


class TestErrorSeverityMapping:
    """Test error code to severity mapping."""

    def test_get_error_severity_with_enum(self):
        """Test getting severity from error code enum."""
        severity = get_error_severity(FiveTwentyErrorCode.INVALID_TOKEN)
        assert severity == ErrorSeverity.CRITICAL

        severity = get_error_severity(FiveTwentyErrorCode.RATE_LIMIT_EXCEEDED)
        assert severity == ErrorSeverity.WARNING

    def test_get_error_severity_with_string(self):
        """Test getting severity from error code string."""
        severity = get_error_severity("INVALID_TOKEN")
        assert severity == ErrorSeverity.CRITICAL

        severity = get_error_severity("TRADE_DOESNT_EXIST")
        assert severity == ErrorSeverity.WARNING

    def test_get_error_severity_with_unknown_code(self):
        """Test getting severity for unknown error code defaults to ERROR."""
        severity = get_error_severity("UNKNOWN_ERROR_CODE")
        assert severity == ErrorSeverity.ERROR

        severity = get_error_severity(None)
        assert severity == ErrorSeverity.ERROR

    def test_critical_errors_have_critical_severity(self):
        """Test that critical errors have CRITICAL severity."""
        critical_errors = [
            FiveTwentyErrorCode.INVALID_TOKEN,
            FiveTwentyErrorCode.INSUFFICIENT_AUTHORIZATION,
            FiveTwentyErrorCode.ACCOUNT_NOT_TRADEABLE,
        ]

        for error_code in critical_errors:
            severity = get_error_severity(error_code)
            assert severity == ErrorSeverity.CRITICAL

    def test_warning_errors_have_warning_severity(self):
        """Test that warning-level errors have WARNING severity."""
        warning_errors = [
            FiveTwentyErrorCode.TRADE_DOESNT_EXIST,
            FiveTwentyErrorCode.ORDER_DOESNT_EXIST,
            FiveTwentyErrorCode.RATE_LIMIT_EXCEEDED,
        ]

        for error_code in warning_errors:
            severity = get_error_severity(error_code)
            assert severity == ErrorSeverity.WARNING
