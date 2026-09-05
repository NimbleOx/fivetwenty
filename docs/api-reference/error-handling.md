# Error handling and recovery

Classify a failure before choosing a recovery action. An invalid local argument,
a server rejection and a lost response are different situations, even when they
occur during the same endpoint call.

## Exception classes

| Failure | Exception | Response |
| --- | --- | --- |
| Invalid local argument | `ValueError` | Correct the input |
| Invalid model data | Pydantic `ValidationError` | Inspect the request or returned schema |
| Non-success HTTP response | `FiveTwentyError` | Inspect status, code and transaction details |
| Network or HTTP transport failure | HTTPX exception | Determine whether the request could have reached OANDA |
| Stream stall | `StreamStall` | Reconnect under a bounded policy and reconcile gaps |

See [exception attributes](exceptions.md) for classification helpers. Known error
codes are mapped by the SDK, but unfamiliar codes must still be handled.

## Inspect an API error

```python
from fivetwenty import AsyncClient, FiveTwentyError


async def read_account(client: AsyncClient) -> None:
    try:
        response = await client.accounts.get_account_summary(client.account_id)
        print(response["account"].currency)
    except FiveTwentyError as error:
        print(f"HTTP {error.status}; code={error.code}; request={error.request_id}")
        if error.is_authentication_error:
            print("Verify token, account access and resolved environment")
        elif error.is_rate_limited:
            print(f"Retry-After seconds: {error.retry_after}")
        raise
```

This example reports context and propagates the failure. It does not turn a failed
read into an empty account or a successful operation. Avoid logging raw response
bodies or HTTP headers when they may contain sensitive information.

## Retry strategies

`max_retries` counts attempts after the initial REST request. The SDK automatically
retries selected temporary failures only for `GET`, `HEAD` and `OPTIONS`. A value
of zero disables those retries. Streaming reconnection has a separate policy.

If an application adds retries around an SDK call that already retries, the attempt
counts multiply. Choose one layer to own the budget. The following helper is for
**read-only operations**, with the client configured using `max_retries=0`:

```python
import asyncio
import random
from collections.abc import Awaitable, Callable
from typing import TypeVar

from fivetwenty import FiveTwentyError

T = TypeVar("T")


async def retry_with_backoff(
    operation: Callable[[], Awaitable[T]],
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
) -> T:
    if max_retries < 0 or base_delay < 0 or max_delay < 0:
        message = "Retry count and delays must be nonnegative"
        raise ValueError(message)
    for attempt in range(max_retries + 1):
        try:
            return await operation()
        except FiveTwentyError as error:  # noqa: PERF203 - each attempt needs its own handler
            if attempt == max_retries or not (error.retryable or error.is_rate_limited):
                raise
            retry_after = error.retry_after
            delay = float(retry_after) if retry_after is not None else base_delay * 2**attempt
            delay = max(0.0, delay)
            if delay > max_delay:
                raise
            delay = min(max_delay, delay + random.uniform(0.0, delay * 0.1))  # noqa: S311 - timing jitter is not a secret
            await asyncio.sleep(delay)
    message = "Unreachable retry state"
    raise RuntimeError(message)
```

The helper accepts integer `Retry-After` seconds and adds bounded jitter. If the
server requests more than the configured maximum wait, it propagates the error
rather than retrying before that interval. It does not retry transport exceptions
or parse HTTP-date headers. Callers should also bound the overall workflow duration.

## Unknown write outcomes

After a write timeout, OANDA may have processed the request even though the client
did not receive its response. Repeating it can create another order or apply another
change. Preserve request context, query orders/trades and related transactions, and
resolve the previous outcome before deciding on another write.

`client_request_id` supports tracing; it is not a write-deduplication guarantee.
A successful HTTP response is also not proof of a fill: inspect conditional
creation, cancellation, fill and rejection details as applicable.

## Stream recovery

The basic pricing and transaction stream methods do not reconnect automatically.
Pricing's retry iterator can reconnect and report state, but it cannot replay
missed prices. A transaction consumer needs a persisted processing cursor and a
history-retrieval path to cover a disconnect. See
[streaming concepts](../guides/trading-concepts/streaming.md).

## Application circuit breakers

A circuit breaker is application policy, not a built-in SDK account control. Define
which failures count, what pauses, when recovery is attempted, and whether other
processes can still submit orders. Pausing new entries, cancelling pending orders
and closing exposure are separate operations.

## Test recovery behavior

Use a controlled HTTP transport to simulate rejection, timeout, repeated temporary
failures and stream interruption. Assert the actual number of requests, final error
and released resources. Test ambiguous writes without automatically resubmitting
them. See the [testing guide](../contributing/testing-guide.md).
