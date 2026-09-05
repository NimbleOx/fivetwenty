# Handle connection failures

First identify where the failure occurred: local configuration, transport, an HTTP
error response, or response parsing. Recovery depends on that distinction and on
whether the operation could have changed the account.

## Diagnose the failure

| Symptom | Check next |
|---|---|
| `ValueError` during client construction | Required credentials, environment value and configuration precedence |
| `httpx.TimeoutException` or another transport error | Network, proxy/TLS settings, timeout and whether a write may have reached OANDA |
| `FiveTwentyError` with 401/403 | Token, resolved environment and access to the selected account |
| `FiveTwentyError` with 429 | Request pacing, retry budget and any `Retry-After` information |
| Pydantic `ValidationError` while parsing | Returned payload, SDK version and a possible response-contract mismatch |
| `StreamStall` | Stream timeout or interrupted connection; decide whether to reconnect and reconcile |

## Authentication troubleshooting

Verify the resolved environment and account rather than inferring them from the
shape of a token. Local validation cannot prove that credentials are valid. A
read-only account request is the useful next check:

```python
import httpx

from fivetwenty import AsyncClient, FiveTwentyError


async def check_access(client: AsyncClient) -> None:
    try:
        response = await client.accounts.get_account_summary(client.account_id)
    except FiveTwentyError as error:
        print(f"API status={error.status}, code={error.code}, request={error.request_id}")
        raise
    except httpx.TransportError:
        print("The account request did not complete over HTTP")
        raise
    print(response["account"].currency)
```

Log a sanitized error code and request ID. Never attach tokens or complete
Authorization headers to diagnostic reports. Consult OANDA's
[authentication guidance](https://developer.oanda.com/rest-live-v20/authentication/)
when replacing or revoking credentials.

## Read retries

The client already retries eligible reads after selected server or transport
failures. With `max_retries=3`, the initial request plus three retries can be sent.
Setting zero disables retries while still making the initial request.

An outer retry loop adds another budget on top of the SDK's budget. Account for
both before adding one. For throttling, pace requests and reuse connections;
[OANDA's best practices](https://developer.oanda.com/rest-live-v20/best-practices/)
provide current guidance. There is no SDK-wide fixed 20-requests-per-second rule.

## Unknown write outcomes

Order creation, replacement, cancellation and trade/position closure are not
automatically retried. If their response is lost, the server may have processed the
request. A client-side timeout is not evidence that nothing happened.

Retain the intended action, account, known order/trade IDs, client identifiers and
last observed transaction ID. Query the relevant order, trade or transaction history
to determine the current state before deciding whether to submit another action.
A client request ID is useful for tracing; it is not a general idempotency guarantee.

## Streaming recovery

`get_pricing_stream()` and `get_transactions_stream()` expose connection failures
to the caller. For automatic pricing reconnection, use
`stream_pricing_with_retries()` with a `StreamingConfiguration`. Its reconnection
budget is separate from REST `max_retries`.

A reconnect starts a new stream; it does not supply a durable transaction cursor.
Persist the last processed transaction ID and recover missing records through
transaction history. Apply records once, then resume live consumption using a
reconciliation policy suitable for the application.

## TLS, proxies and diagnostics

Check DNS resolution, outbound HTTPS access, proxy configuration, trust roots and
system time. Do not disable certificate verification as a routine fix for a TLS
error. Configure the required trust roots or proxy in HTTPX instead.

Keep a reproducible record of the SDK version, sanitized method/path, exception
class, status/code, retry settings and timing. If a response fails model validation,
preserve a redacted payload for a regression test rather than replacing it with an
empty success result.
