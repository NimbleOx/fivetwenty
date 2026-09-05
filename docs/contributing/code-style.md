# Code style and implementation patterns

Follow the repository's Ruff and mypy configuration. Use explicit types for public
interfaces and keep each endpoint's request construction, response envelope and
model parsing easy to inspect.

## Numeric and datetime values

Use `Decimal` for financial values and construct literal decimal values from strings.
Multiplying an integer by a `Decimal` preserves decimal arithmetic; it does not
introduce floating-point loss. Avoid converting a value through `float` before
constructing its decimal representation.

```python
from decimal import Decimal


def quote_value(units: int, price: Decimal) -> Decimal:
    return units * price
```

This result is in the price's quote currency, not necessarily account currency.
Use ordinary floating-point seconds for timeouts and retry delays. Preserve native
datetimes in models and serialize request datetimes through the shared formatter.

## Models and response envelopes

Derive SDK API models from the shared `ApiModel` and use OANDA aliases for wire
fields. Follow existing Pydantic v2 configuration and validators. Do not introduce a
second model configuration pattern or replace decimal trade units with integers.

Keep endpoint metadata and parsed objects in the documented response dictionary.
Optional transaction fields must remain optional: a creation response does not
always contain a fill. Avoid manufacturing empty objects to hide missing data.

## Endpoints and errors

Use existing method names and resource groups as the naming model, such as
`get_account_summary()` and `post_market_order()`. Route HTTP through the shared
client so authentication, datetime headers, transport settings and retry behavior
remain consistent.

Preserve the distinction between local validation, HTTP API errors and transport
failures. Do not fabricate a status code for an exception that has no response, or
catch an error only to return a value that looks like success.

## Async and streaming lifecycle

Endpoint implementations are asynchronous. The synchronous client delegates ordinary
calls to one background event-loop thread; it does not call `asyncio.run()` for every
request. Async-generator streams need their dedicated adapter and cleanup path.

Close delegated generators when an outer generator closes. Keep buffers and task
counts bounded, propagate cancellation, and define whether a stream consumer may
drop records. Connection retry logic is not account-history recovery.

## Docstrings and examples

Document argument units, defaults, return keys and meaningful errors. Distinguish
API requirements from convenience validation and application policy. Show native
model attributes in calculations and avoid unsupported execution or security promises.

Examples should either be complete scripts or clearly identified helpers. A type
signature belongs in a signature block, not a pretend implementation that returns a
placeholder success. Use a read-only example when demonstrating configuration;
identify account-changing operations and check their resolved practice environment.

## Tests and checks

Use independent HTTP payloads with `httpx.MockTransport` and assert observable
requests and results. Follow the [testing guide](testing-guide.md) for edge cases,
stream cleanup and integration-test opt-in.

Before submitting a code change, run:

```bash
uv run poe check-fast
```

Documentation changes also need a site build, link checks and validation appropriate
to any executable examples they change. Formatting and coverage numbers supplement
review; they do not replace checking that the behavior matches OANDA's contract.
