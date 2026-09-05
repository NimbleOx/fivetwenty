# Exceptions API reference

The SDK defines `FiveTwentyError` for non-success HTTP responses and `StreamStall`
for detected stream stalls. They both inherit directly from Python's `Exception`;
`StreamStall` is not a subclass of `FiveTwentyError`.

## FiveTwentyError

The constructor is keyword-only. `status` and `message` are required; the other
fields below are optional.

| Attribute | Type | Meaning |
| --- | --- | --- |
| `status` | `int` | HTTP status code |
| `message` | `str` | API message or response-text fallback |
| `code` | `str \| None` | Returned OANDA error code |
| `request_id` | `str \| None` | Request identifier from response headers |
| `retryable` | `bool` | Classification hint; defaults to `False` |
| `response` | `httpx.Response \| None` | Original response |
| `details` | `ErrorDetails \| None` | Parsed structured error details |

The HTTP error parser marks selected temporary statuses and rate-limit codes as
retryable. That hint does not establish that repeating a write is safe. The SDK
restricts automatic REST retries to eligible read methods.

### Classification properties

| Property | Result |
| --- | --- |
| `is_client_error` | Whether status is in 400–499 |
| `is_server_error` | Whether status is in 500–599 |
| `is_authentication_error` | Status 401/403 or a recognized authentication/authorization category |
| `is_validation_error` | Recognized validation category or structured violations |
| `is_rate_limited` | Status 429 or recognized rate-limit category |
| `is_not_found` | Status 404 or recognized not-found category |
| `error_category` | Mapped category, or `None` for an unrecognized code |
| `error_severity` | Mapped severity with the SDK's fallback |
| `retry_after` | Integer seconds from `Retry-After`, or `None` |

There is no `is_bad_request` property; compare `status == 400`. A 400 response does
not necessarily have a recognized validation category. `retry_after` parses integer
seconds only, not an HTTP-date header value.

### Detail methods

`get_validation_errors()` groups known violations by field and returns an empty
dictionary when none are available. `get_remediation_message()` returns a suggestion
for certain known codes, or `None`. These mappings are conveniences, not an exhaustive
list of all OANDA errors or instructions to change account exposure automatically.

## StreamStall

Raised when stream timeout handling detects a stall. Network failures can also
propagate as HTTPX exceptions, and API rejection at stream startup can raise
`FiveTwentyError`. The final error after retries depends on the failure encountered.

## Other exceptions

Local argument checks can raise `ValueError`; model parsing can raise Pydantic
`ValidationError`; transport failures can raise `httpx.HTTPError` subclasses.
Catching only `FiveTwentyError` does not cover these paths. See
[error handling](error-handling.md) for recovery boundaries and logging examples.

::: fivetwenty.exceptions
    options:
      show_source: false
      show_root_heading: false
      members_order: source
