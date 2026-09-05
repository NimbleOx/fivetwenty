# Testing Guide

Run the deterministic suite before committing. It blocks real HTTP transports and
checks requests, response models, retries, streaming cleanup and documentation tools.

```bash
# Unit tests
uv run poe test

# SDK line and branch coverage, with the same 99% gate used by CI
uv run poe test-cov

# A specific contract suite
uv run pytest tests/unit/test_client_transport.py

# Quality checks
uv run poe check-fast

# Execute Markdown Python examples with the real SDK and offline HTTP fixtures
uv run poe docs-validate-examples

# Execute all six notebooks through HTTP mocks
uv run poe docs-validate-notebooks
```

An ordinary `uv run pytest` includes unit tests and skips the live integration
suite. CI runs unit tests on Python 3.10, 3.11, 3.12 and 3.13. A separate job checks
the minimum supported HTTPX and Pydantic versions on Python 3.10.

## Test structure

```text
tests/
├── conftest.py                   # Live-test opt-in
├── unit/
│   ├── conftest.py               # Reject unmocked HTTP
│   ├── test_client_transport.py  # HTTP, retries and logging
│   ├── test_sync_client.py       # Background loop and stream lifecycle
│   ├── test_request_contracts.py
│   ├── test_response_contracts.py
│   └── models/                  # Model fields and wire serialization
└── integration/
    ├── conftest.py               # Practice fixtures and verified cleanup
    ├── test_account_reads.py
    ├── test_api_errors.py
    ├── test_market_data.py
    ├── test_transaction_reads.py
    └── test_trading_lifecycle.py
```

## Write tests at the HTTP boundary

Use `httpx.MockTransport` with an independent wire payload. Assert the outgoing
request and observable response values, and close every client explicitly.

```python
import httpx

from fivetwenty import AsyncClient


async def test_account_discovery() -> None:
    def respond(request: httpx.Request) -> httpx.Response:
        assert request.method == "GET"  # noqa: S101
        assert request.url.path == "/v3/accounts"  # noqa: S101
        return httpx.Response(200, json={"accounts": [{"id": "123", "tags": []}]})

    transport = httpx.AsyncClient(
        transport=httpx.MockTransport(respond),
        base_url="https://offline.example.test/v3",
    )
    async with AsyncClient(token="offline-token", account_id="123", transport=transport) as client:
        accounts = await client.accounts.get_accounts()
    assert [account.id for account in accounts] == ["123"]  # noqa: S101
```

Pytest's configured asyncio mode runs asynchronous test functions automatically.
Use `Decimal` and Python datetimes for value assertions. Control clocks, jitter and
transport failures so that tests do not depend on random delays or network speed.
Consume streaming generators and verify response cleanup when closing or cancelling.

Keep enum wire-value assertions and independent model examples. Generated model
round trips provide broad regression coverage, but cannot establish API fidelity by
themselves. Avoid duplicate presence checks, always-true assertions, or exception
handlers that merely print a failure.

## Live integration

Live tests require explicit opt-in and OANDA practice credentials:

```bash
export FIVETWENTY_OANDA_TOKEN="your-practice-token"
export FIVETWENTY_OANDA_ACCOUNT="your-practice-account"

# Read-only server checks
uv run pytest tests/integration --run-integration-live -m 'not trading'

# Includes order and trade operations
uv run poe test-integration
```

Use a dedicated practice account with no other process trading on it. Trading tests
require no pending orders or open trades before starting, use the instrument's
minimum trade size, and verify cleanup after success or failure. Failed cleanup
fails the test. Known market-state restrictions can skip a case; unexpected errors
must propagate. `SKIP_INTEGRATION=1` forces all live cases to skip.

The live suite checks focused server outcomes. Regional order restrictions and
transport failure matrices also need deterministic offline tests; a passing live
run does not verify every account-specific API feature.

## Coverage interpretation

The SDK gate measures `fivetwenty` with branch coverage. Model and enum declarations
contribute to the percentage, so review assertion quality alongside that number.
Do not add source exclusions or weak tests to increase coverage.

Documentation tooling is a separate measurement:

```bash
uv run pytest tests/unit --cov=docs_validation.src --cov-branch --cov-report=term-missing --cov-fail-under=0
```

Actual documentation diagnostics are tracked separately from tests of the validators.
The Markdown execution worker runs in a subprocess, so its execution is not included
in this in-process coverage measurement. Runner regressions exercise valid examples,
broken SDK calls, invalid responses, environment isolation and worker failures.
