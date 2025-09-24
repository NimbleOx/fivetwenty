"""OANDA API exceptions."""

from typing import TYPE_CHECKING

from .models.error_codes import ErrorCategory, ErrorSeverity, FiveTwentyErrorCode, get_error_category, get_error_severity
from .models.error_details import ErrorDetails

if TYPE_CHECKING:
    import httpx


class FiveTwentyError(Exception):
    """Enhanced exception for all OANDA API errors.

    This exception provides comprehensive error information including:
    - HTTP status code and OANDA error code
    - Error categorization and severity
    - Structured validation errors
    - Rate limiting information
    - Retry guidance
    """

    def __init__(
        self,
        *,
        status: int,
        code: str | None = None,
        message: str,
        request_id: str | None = None,
        retryable: bool = False,
        response: "httpx.Response | None" = None,
        details: ErrorDetails | None = None,
    ):
        super().__init__(message)
        self.status = status
        self.code = code
        self.message = message
        self.request_id = request_id
        self.retryable = retryable
        self.response = response
        self.details = details

    @property
    def error_category(self) -> ErrorCategory | None:
        """Get the error category (AUTHENTICATION, VALIDATION, etc.)."""
        return get_error_category(self.code)

    @property
    def error_severity(self) -> ErrorSeverity:
        """Get the error severity (INFO, WARNING, ERROR, CRITICAL)."""
        return get_error_severity(self.code)

    @property
    def is_client_error(self) -> bool:
        """Check if this is a client error (4xx status code)."""
        return 400 <= self.status < 500

    @property
    def is_server_error(self) -> bool:
        """Check if this is a server error (5xx status code)."""
        return 500 <= self.status < 600

    @property
    def is_authentication_error(self) -> bool:
        """Check if this is an authentication/authorization error."""
        return self.status in {401, 403} or self.error_category in {ErrorCategory.AUTHENTICATION, ErrorCategory.AUTHORIZATION}

    @property
    def is_validation_error(self) -> bool:
        """Check if this is a validation error."""
        return self.error_category == ErrorCategory.VALIDATION or (self.details is not None and self.details.has_validation_errors())

    @property
    def is_rate_limited(self) -> bool:
        """Check if this is a rate limiting error."""
        return self.status == 429 or self.error_category == ErrorCategory.RATE_LIMITING

    @property
    def is_not_found(self) -> bool:
        """Check if this is a not found error."""
        return self.status == 404 or self.error_category == ErrorCategory.NOT_FOUND

    @property
    def retry_after(self) -> int | None:
        """Get the retry-after seconds from response headers (for rate limiting)."""
        if self.response:
            retry_after = self.response.headers.get("Retry-After")
            if retry_after:
                try:
                    return int(retry_after)
                except ValueError:
                    pass
        return None

    def get_validation_errors(self) -> dict[str, list[str]]:
        """Get validation errors grouped by field name."""
        if self.details:
            return self.details.get_field_errors()
        return {}

    def get_remediation_message(self) -> str | None:
        """Get suggested remediation message for common error codes."""
        if not self.code:
            return None

        remediation_messages = {
            FiveTwentyErrorCode.INVALID_TOKEN: "Check your authentication token and ensure it's valid and properly formatted.",
            FiveTwentyErrorCode.INSUFFICIENT_AUTHORIZATION: "Verify your account has the required permissions for this operation.",
            FiveTwentyErrorCode.ACCOUNT_NOT_TRADEABLE: "Ensure your account is approved for trading and not restricted.",
            FiveTwentyErrorCode.RATE_LIMIT_EXCEEDED: f"Rate limit exceeded. Wait {self.retry_after or 'a few'} seconds before retrying.",
            FiveTwentyErrorCode.INSUFFICIENT_MARGIN: "Reduce position size or add funds to your account.",
            FiveTwentyErrorCode.INSTRUMENT_NOT_TRADEABLE: "Check if the instrument is available for trading during current market hours.",
            FiveTwentyErrorCode.MARKET_HALTED: "Wait for market to resume trading before placing orders.",
            FiveTwentyErrorCode.INVALID_INSTRUMENT: "Check the instrument name format (e.g., 'EUR_USD').",
            FiveTwentyErrorCode.PRECISION_EXCEEDED: "Reduce the precision of price or unit values.",
            FiveTwentyErrorCode.TRADE_DOESNT_EXIST: "Verify the trade ID exists and belongs to this account.",
            FiveTwentyErrorCode.ORDER_DOESNT_EXIST: "Verify the order ID exists and belongs to this account.",
        }

        try:
            error_code_enum = FiveTwentyErrorCode(self.code)
            return remediation_messages.get(error_code_enum)
        except ValueError:
            return None

    def __str__(self) -> str:
        parts = [f"HTTP {self.status}"]
        if self.code:
            parts.append(f"({self.code})")
        parts.append(f": {self.message}")
        if self.request_id:
            parts.append(f" [Request ID: {self.request_id}]")

        # Add validation error summary if present
        if self.is_validation_error and self.details and self.details.violations:
            violation_count = len(self.details.violations)
            parts.append(f" [{violation_count} validation error{'s' if violation_count != 1 else ''}]")

        return " ".join(parts)

    def __repr__(self) -> str:
        return f"FiveTwentyError(status={self.status}, code={self.code!r}, message={self.message!r}, request_id={self.request_id!r}, retryable={self.retryable}, category={self.error_category!r}, severity={self.error_severity!r})"


class StreamStall(Exception):
    """Exception raised when a stream stalls (no data received)."""


def raise_for_fivetwenty(response: "httpx.Response") -> None:
    """
    Raise an enhanced FiveTwentyError for HTTP error status codes.

    Args:
        response: The HTTP response to check

    Raises:
        FiveTwentyError: If the response indicates an error
    """
    if 200 <= response.status_code < 300:
        return

    # Safely parse JSON errors
    payload = {}
    try:
        content_type = response.headers.get("content-type") or ""
        if "application/json" in content_type:
            payload = response.json()
    except Exception:
        # Malformed JSON or not JSON at all
        payload = {}

    # Parse structured error details
    details = None
    if payload:
        details = ErrorDetails.from_api_response(payload)

    # Limit error text to prevent bloat
    try:
        error_text = response.text[:500] if response.text else "Unknown error"
    except Exception:
        # Handle streaming responses or other edge cases
        error_text = f"HTTP {response.status_code} error"

    # Determine if the error is retryable
    retryable = (
        response.status_code in {429, 502, 503, 504}  # Standard retryable status codes
        or payload.get("errorCode") == "RATE_LIMIT_EXCEEDED"  # OANDA-specific rate limiting
    )

    raise FiveTwentyError(
        status=response.status_code,
        code=payload.get("errorCode"),
        message=payload.get("errorMessage") or error_text,
        request_id=response.headers.get("X-Request-Id"),
        retryable=retryable,
        response=response,
        details=details,
    )
