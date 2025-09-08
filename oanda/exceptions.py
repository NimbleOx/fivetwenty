"""OANDA API exceptions."""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import httpx


class OandaError(Exception):
    """Base exception for all OANDA API errors."""
    
    def __init__(
        self,
        *,
        status: int,
        code: str | None = None,
        message: str,
        request_id: str | None = None,
        retryable: bool = False,
        response: "httpx.Response | None" = None,
    ):
        super().__init__(message)
        self.status = status
        self.code = code
        self.message = message
        self.request_id = request_id
        self.retryable = retryable
        self.response = response
    
    def __str__(self) -> str:
        parts = [f"HTTP {self.status}"]
        if self.code:
            parts.append(f"({self.code})")
        parts.append(f": {self.message}")
        if self.request_id:
            parts.append(f" [Request ID: {self.request_id}]")
        return " ".join(parts)
    
    def __repr__(self) -> str:
        return (
            f"OandaError(status={self.status}, code={self.code!r}, "
            f"message={self.message!r}, request_id={self.request_id!r}, "
            f"retryable={self.retryable})"
        )


class StreamStall(Exception):
    """Exception raised when a stream stalls (no data received)."""
    pass


def raise_for_oanda(response: "httpx.Response") -> None:
    """
    Raise an OandaError for HTTP error status codes.
    
    Args:
        response: The HTTP response to check
        
    Raises:
        OandaError: If the response indicates an error
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
    
    # Limit error text to prevent bloat
    error_text = response.text[:500] if response.text else "Unknown error"
    
    raise OandaError(
        status=response.status_code,
        code=payload.get("errorCode"),
        message=payload.get("errorMessage") or error_text,
        request_id=response.headers.get("X-Request-Id"),
        retryable=response.status_code in {429, 502, 503, 504},
        response=response,
    )