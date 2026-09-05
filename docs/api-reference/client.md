# Client API reference

`AsyncClient` owns the HTTP connection and exposes endpoint groups. `Client` offers
blocking calls through a background event-loop thread. Choose the interface that
fits the application; both use the same endpoint implementation.

## AsyncClient

The constructor accepts an optional positional `token` and the keyword arguments
below. Create it inside an `async with` block, or call `await client.aclose()` when
finished.

| Argument | Type | Default and meaning |
| --- | --- | --- |
| `token` | `str \| None` | `None`; direct API token |
| `account_id` | `str \| None` | `None`; required with a direct token |
| `environment` | `Environment` | `PRACTICE`; used with direct credentials |
| `config` | `AccountConfig \| None` | `None`; explicit configuration object |
| `timeout` | `float` | `30.0`; default read timeout in seconds |
| `max_retries` | `int` | `3`; retries after the initial eligible REST request |
| `transport` | `httpx.AsyncClient \| None` | `None`; an existing HTTP client |
| `user_agent` | `str \| None` | `None`; use the SDK's user agent |
| `proxies` | `str \| None` | `None`; proxy URL for an SDK-created HTTP client |
| `verify` | `bool \| str` | `True`; TLS verification or CA path |
| `cert` | `str \| None` | `None`; client certificate path |
| `logger` | `logging.Logger \| None` | `None`; SDK logger |
| `datetime_format` | `AcceptDatetimeFormat \| str` | `RFC3339`; also accepts `UNIX` |

### Configuration priority

With `config`, that object's token and environment are used; a direct `account_id`
can override its account ID. Otherwise, providing `token` selects direct credentials
and requires `account_id`. Without either `config` or `token`, the client loads the
standard environment variables.

In the environment-loading branch, passing only `environment` or `account_id` does
not override the loaded values. Inspect `client.config.environment` when the
resolved environment matters. See [configuration](configuration.md).

### Read-only example

This function uses credentials already present in the process environment. It does
not load a `.env` file itself.

<!-- code-block: async_client_usage_examples -->
```python
from fivetwenty import AsyncClient


async def list_account_ids() -> list[str]:
    async with AsyncClient() as client:
        accounts = await client.accounts.get_accounts()
        return [account.id for account in accounts]
```

### HTTP ownership and timeouts

REST and streaming use the same HTTP client. Streaming selects the streaming host
and supplies a separate timeout. For an SDK-created HTTP client, connect timeout is
5 seconds, write timeout is 10 seconds, and `timeout` supplies the default
read and pool timeouts. An endpoint's explicit timeout override applies to that request.

Despite its name, `transport` expects an `httpx.AsyncClient`, not an HTTPX transport
object. Configure its base URL, headers, TLS, proxy and connection limits yourself;
SDK constructor options do not rebuild it. Closing the SDK also closes the injected
HTTP client, so give it a compatible ownership lifetime.

### Datetime serialization

`datetime_format` controls the `Accept-Datetime-Format` header and serialization of
native datetimes in query parameters and request bodies, including nested orders.
Datetime model attributes remain Python `datetime` objects. Standalone model dumps
use RFC3339 unless a serialization context requests UNIX formatting. Python's
microsecond precision does not preserve sub-microsecond timestamps.

Some envelope fields, including pricing's top-level `time`, remain wire strings;
check the endpoint return type. A pricing `since` string is passed through as a wire
value and must match the selected format.

## Client

`Client(**kwargs)` forwards constructor arguments to `AsyncClient`. Use a `with`
block or `client.close()` to release its HTTP resources and background thread.
Ordinary endpoint methods return their result synchronously.

<!-- code-block: client_usage_examples -->
```python
from fivetwenty import Client


def list_account_ids() -> list[str]:
    with Client() as client:
        accounts = client.accounts.get_accounts()
        return [account.id for account in accounts]
```

The special `pricing.stream_iter()` adapter provides blocking stream iteration.
The ordinary proxy does not convert every async-generator endpoint into a blocking
iterator. Its pricing queue holds 1,024 records and drops the oldest record when
full; explicitly close the iterator when stopping early. See
[async versus sync](../guides/understanding/async-vs-sync.md).

## Properties and endpoint groups

Both clients expose `account_id` as a string and `config` as an `AccountConfig`.
Endpoint groups are available as attributes:

| Attribute | Operations |
| --- | --- |
| [accounts](endpoints/accounts.md) | Account reads, configuration and account instruments |
| [instruments](endpoints/instruments.md) | Instrument candles and order/position books |
| [pricing](endpoints/pricing.md) | Account prices, candles and price streams |
| [orders](endpoints/orders.md) | Create, query, replace and cancel orders |
| [trades](endpoints/trades.md) | Trade reads, closure and dependent orders |
| [positions](endpoints/positions.md) | Instrument exposure and side-specific closure |
| [transactions](endpoints/transactions.md) | Transaction queries and streams |

## Error handling

Non-success HTTP responses raise `FiveTwentyError`. Transport errors can propagate
as HTTPX exceptions; local validation can raise `ValueError` or Pydantic
`ValidationError`. These failures require different recovery decisions.

<!-- code-block: fivetwenty_error_handling -->
```python
from fivetwenty import AsyncClient, FiveTwentyError


async def show_trade(client: AsyncClient, trade_id: str) -> None:
    try:
        response = await client.trades.get_trade(client.account_id, trade_id)
        print(response["trade"].state)
    except FiveTwentyError as error:
        print(f"HTTP {error.status}; code={error.code}; request={error.request_id}")
        raise
```

See [exceptions](exceptions.md) for fields and [error handling](error-handling.md)
for retry and unknown-outcome behavior.

## Rate limits

Reuse established connections and bound concurrency. OANDA's published
[best practices](https://developer.oanda.com/rest-live-v20/best-practices/) recommend
at most two new connections per second and 100 requests per second on established
connections. These are service recommendations, not a throughput guarantee.
Inspect rate-limit responses and allow backoff; the SDK does not reserve capacity
across separate processes.

## Environment considerations

Practice and live use separate API hosts and credentials. Both can impose account
and instrument restrictions. Practice execution does not establish expected live
fills, liquidity or profitability. See [environments](../guides/understanding/environments.md)
for host names and explicit environment checks.
