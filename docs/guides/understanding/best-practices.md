# Application patterns

The most useful habits are to keep client ownership clear, preserve numeric types
and distinguish a failed request from an unknown trading outcome.

## Reuse clients and close resources

Create one client for related operations on an account. Reusing it allows HTTPX to
reuse connections. Close clients with context managers; close a partially consumed
stream with `aclosing` or the sync pricing iterator with `closing`.

Do not create an unbounded task for every price update. Keep a bounded queue or a
latest-price cache, and decide whether dropping old prices is acceptable. Transaction
processing needs reconciliation rather than silent loss.

## Preserve financial values

Build decimal inputs from strings, for example `Decimal("0.001")`, instead of
converting a binary float. Inspect instrument metadata before choosing quantities
or prices: `minimum_trade_size`, `trade_units_precision`, `display_precision` and
order-distance restrictions serve different purposes.

Rounding a value to display precision does not establish that an order is valid.
Account rules, available margin, price bounds and current market state can still
cause rejection or cancellation.

## Read the response before changing local state

Most endpoint results are dictionaries containing models. Read
`response["account"].balance` or `response["orders"]`; do not assume the enclosing
response is itself the model. A write may return creation, fill, cancellation or
reissue transactions. Inspect the actual keys and retain relevant transaction IDs.

Updating a Pydantic object changes local state only. To keep an account view current,
use the API's account changes or transaction history instead of treating local
objects as live references to server state.

## Retry only when the operation permits it

The SDK already retries eligible reads. Adding another retry loop can multiply
attempts and delay failure reporting. Set a total retry budget and account for the
client's configured retries.

Do not put order creation, replacement or trade closure inside a generic retry
decorator. A timeout can occur after a write has succeeded. Reconcile account and
transaction state before deciding whether another write is necessary.

## Token security

Use environment variables or a secret store and avoid printing extracted tokens.
`SecretStr` protects routine display of configuration values; it does not secure
application logs, exception attachments or stored files automatically.

Rotate credentials through the deployment's secret-management process and recreate
clients when credentials change. Avoid logging full request headers or raw config.

## Test the application boundary

Use HTTP mocks for error sequences and exact request assertions. Keep practice
integration tests separate and opt-in. A successful practice run establishes only
the scenarios actually exercised; it does not establish strategy performance or
complete live-market equivalence.

See [testing](../../contributing/testing-guide.md), [connection failures](../practical-solutions/handle-connection-failures.md)
and [performance measurement](../optimization/index.md) for concrete patterns.
