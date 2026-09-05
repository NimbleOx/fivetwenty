# System Models

**OANDA Reference**: [Primitives Data Definitions](https://developer.oanda.com/rest-live-v20/primitives-df/)

SDK streaming configuration, parsed error details and primitive aliases. Streaming
policies are local SDK settings, not request objects sent to OANDA.

Field names are Python attributes. Required means required at model construction;
`None` in the type indicates a nullable value. Defaults and local validation do not
establish server eligibility. See [reading model tables](index.md#reading-model-tables).

---

## Streaming Models

### StreamingConfiguration
Configuration for streaming connections.

🔗 **Source**: [StreamingConfiguration](https://github.com/NimbleOx/fivetwenty/blob/main/fivetwenty/models/streaming.py)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `include_heartbeats` | bool | ➖ | Yield heartbeat messages to the caller (default: True). OANDA always sends heartbeats; when False they are filtered out client-side |
| `stall_timeout` | float | ➖ | Seconds before considering stream stalled (default: 30.0) |
| `reconnection_policy` | [ReconnectionPolicy](#reconnectionpolicy) | ➖ | Reconnection settings (default: ReconnectionPolicy()) |

### ReconnectionPolicy
Policy for automatic reconnection.

🔗 **Source**: [ReconnectionPolicy](https://github.com/NimbleOx/fivetwenty/blob/main/fivetwenty/models/streaming.py)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `max_attempts` | int | ➖ | Maximum reconnection attempts (default: 3) |
| `delay_seconds` | float | ➖ | Delay between reconnection attempts in seconds (default: 1.0) |

---

## Error Models

### ErrorDetails
Structured error information from API responses.

🔗 **Source**: [ErrorDetails](https://github.com/NimbleOx/fivetwenty/blob/main/fivetwenty/models/error_details.py)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `message` | str | ✅ | Primary error message |
| `code` | str \| None | ➖ | Primary error code |
| `violations` | list[[ValidationViolation](#validationviolation)] | ➖ | Field validation errors (default: empty list) |
| `additional_fields` | dict[str, Any] | ➖ | Additional error context from API response (default: empty dict) |

### ValidationViolation
Specific field validation error.

🔗 **Source**: [ValidationViolation](https://github.com/NimbleOx/fivetwenty/blob/main/fivetwenty/models/error_details.py)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `field` | str | ✅ | Field name with validation error |
| `message` | str | ✅ | Validation error message |
| `code` | str \| None | ➖ | Machine-readable error code for the violation |

---

## Type Aliases
- `AccountID` - str: Account identifier using format "{siteID}-{divisionID}-{userID}-{accountNumber}"
- `TradeID` - str: Trade identifier (OANDA-assigned positive integer as string)
- `OrderID` - str: Order identifier (unique within account)
- `TransactionID` - str: Transaction identifier (positive integer assigned sequentially by OANDA)
- `RequestID` - str: OANDA-generated request identifier returned in response headers and transaction payloads
- `ClientRequestID` - str: Client-provided request identifier sent with write requests for support correlation
- `PriceValue` - `Decimal`: native price value; encoded as a string on the wire
- `AccountUnits` - `Decimal`: native account-currency amount; encoded as a string on the wire
- `DecimalNumber` - `Decimal`: general decimal quantity

OANDA's DateTime primitive is an RFC3339 or UNIX wire value. Datetime model fields
use Python `datetime`, with microsecond precision. `DateTime` is an alias for `datetime`.
