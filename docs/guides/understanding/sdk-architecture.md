# SDK architecture

FiveTwenty translates between OANDA's JSON API and Python objects. The design has
three main layers: clients manage HTTP, endpoint groups build requests and parse
response envelopes, and Pydantic models validate individual data objects.

```mermaid
flowchart LR
    App[Application] --> Endpoints[Endpoint methods]
    Endpoints --> REST[REST request and retry handling]
    Endpoints --> Stream[Streaming HTTP reader]
    REST --> HTTP[HTTPX client]
    Stream --> HTTP
    HTTP --> OANDA[OANDA API]
    Endpoints --> Models[Pydantic models in response dictionaries]
```

## Async and sync clients

`AsyncClient` is the primary implementation. It uses HTTPX for requests, connection
pooling and streaming. Reuse one client for related work on the same event loop and
close it with `async with` or `await client.aclose()`.

`Client` runs an `AsyncClient` on a dedicated background event-loop thread. Ordinary
endpoint calls block until the corresponding coroutine finishes and return the
same response shape. Synchronous pricing uses `client.pricing.stream_iter()`;
other async-generator methods are not converted into blocking iterators.

The wrapper adds a thread and queue, not a trading scheduler. See
[async and sync clients](async-vs-sync.md) for examples and lifetime rules.

## Requests and response envelopes

Endpoint names follow the public API, for example `get_account_summary()`,
`post_order()`, `put_trade_orders()` and `cancel_order()`. Most account-scoped
methods take `account_id` first. Consult the endpoint reference for exact names;
there is no generic `list()` or `modify()` convention.

Most methods return a dictionary with OANDA keys and typed model values:

```python
from fivetwenty import AsyncClient
from fivetwenty.models import AccountSummary


async def read_account(client: AsyncClient) -> AccountSummary:
    response = await client.accounts.get_account_summary(client.account_id)
    account = response["account"]
    print(response["lastTransactionID"])
    return account
```

`get_accounts()` is an exception: it returns a list of account-property models.
Conditional transaction fields in write responses may be absent. Inspect the
returned keys rather than assuming every accepted request produced a fill.

## Model values and wire values

Model attributes use Python names such as `closeout_bid`; aliases such as
`closeoutBid` are used on the wire. Financial attributes declared as `Decimal`
remain decimals in Python. The public `PriceValue`, `AccountUnits` and
`DecimalNumber` aliases also represent `Decimal` values.

Timestamps become Python datetimes. `datetime_format="UNIX"` changes request and
response encoding, not the Python attribute type. Python datetimes retain
microseconds; a wire timestamp with finer precision cannot be represented exactly.

```python
from decimal import Decimal

from fivetwenty.models import LimitOrderRequest

order = LimitOrderRequest(instrument="EUR_USD", units=Decimal("1"), price=Decimal("1.05"))
order.units = Decimal("2")
wire = order.model_dump(mode="json", by_alias=True, exclude_none=True)
print(wire["units"])  # Serialized string: "2"
```

Models are mutable, with assignment validation enabled. Updating a local model
never updates the account; send an endpoint request to change server state.
Compatibility dictionary access on a model returns serialized values, so use
attributes when you need native decimals, datetimes or nested model objects.

## Retry and streaming behavior

REST retries apply to eligible read requests after selected status or transport
failures. `max_retries` counts attempts after the initial request. Writes are sent
once because a timeout does not establish whether the server processed them.

Basic pricing and transaction streams yield typed records from line-delimited
JSON. They report failures to the caller. `stream_pricing_with_retries()` adds a
reconnection policy and connection-state values. Reconnection does not replay
missed transactions or restore application state.

Close a partially consumed async stream with `contextlib.aclosing`. The sync pricing
iterator has a bounded queue of 1,024 records and drops the oldest queued record
when full. It is a current-price interface, not lossless storage.

## Configuration and credentials

The client resolves an `AccountConfig`, direct credentials or environment variables
as described in [configuration](configuration.md). It retains the token in memory
for Authorization headers. `SecretStr` masks configuration representations, and
SDK request logging redacts Authorization headers; application logs, dumps and
custom transports remain the application's responsibility.

The selected environment chooses practice or live hosts. Configuration is not a
permission boundary: verify the resolved environment before an application is
allowed to submit orders.

## Testing and extension

REST and streams both use the configured HTTPX client. Inject an HTTPX client with
`MockTransport` to test requests and responses without contacting OANDA. Mocking
only `_request()` does not cover streaming. See the
[testing guide](../../contributing/testing-guide.md).

Custom transports must supply the appropriate base URL and transport settings.
Closing the SDK also closes an injected HTTPX client, so give each SDK instance a
clear transport owner. The direct runtime dependencies are HTTPX and Pydantic;
plotting, strategy execution and account-state persistence belong to application
code.

The library is beta software. Compatibility changes are documented as they are
made; this documentation does not promise a particular deprecation schedule.
