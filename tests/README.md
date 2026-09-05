# Testing FiveTwenty

Run the deterministic suite with `uv run poe test`, or use `uv run poe test-cov`
for line and branch coverage. Unit tests block real HTTP transports, use synthetic
credentials, and run in CI across supported Python versions. The minimum runtime
dependency job runs the same suite on Python 3.10.

## What belongs in each suite

| Surface | Evidence |
|---|---|
| Endpoint contracts | Mock HTTP at the transport boundary; assert method, path, parameters, body, response envelope and parsed values. |
| Models | Independent wire examples and expected decimal/datetime values; round-trip and subtype checks supplement those examples. |
| Retry and streaming | Controlled transport failures, split chunks, cancellation, cleanup and observable retry counts. Avoid random network timeouts. |
| Sync client | Real background loop and HTTP mocks; close clients and iterators explicitly and verify resources are released. |
| Documentation tooling | Small valid/invalid documents, extractor fixtures and failed-tool cases. The real documentation backlog is tracked separately. |
| Published Markdown examples | `uv run poe docs-validate-examples` executes every Python block with the real SDK and shared HTTP fixtures; focused tests call important helper functions. |
| Live integration | Focused server outcomes on a dedicated OANDA practice account, explicitly requested. |

Do not add tests merely to execute declarations or repeat assertions made by
stronger contract tests. Tests should fail when the behavior they protect breaks.
Avoid `assert ... or True`, unconsumed stream generators, arbitrary import-time
limits, and catching an exception only to print it. Use a controlled clock or
random source for boundary checks. Retain enum wire-value tests and independent
API fixtures: generated round trips alone cannot establish API correctness.

## Live integration

`uv run poe test-integration` opts into the live suite. Set
`FIVETWENTY_OANDA_TOKEN` and `FIVETWENTY_OANDA_ACCOUNT` for a **practice** account.
The suite always selects the practice environment. Ordinary pytest runs skip it.
`SKIP_INTEGRATION=1` overrides the opt-in flag.

Use a dedicated account with no other trader or process operating on it. Trading
cases require no pending orders or open trades before starting, use the
instrument's minimum trade size, and verify cleanup after success or failure.
Cleanup failures fail the test. These cases create, replace, cancel and close
orders/trades; they are not read-only.

For read-only checks:

```sh
uv run python -m pytest tests/integration --run-integration-live -m 'not trading'
```

Live tests verify account and collection envelopes, transaction cursors and
filters, candle formats, typed stream records, read-only server errors, pending
order lifecycles, replacement/extensions, dependent-order cancellation and
explicit position closure. Market/account restrictions may produce a clearly
reported skip. Unexpected failures propagate.

The former omnibus live scenarios repeated configuration/model checks, accepted
any exception, relied on volatile prices/latencies, or demonstrated trading
strategies unrelated to SDK correctness. They were replaced by the focused suite.
Transport retry/failure matrices, enum variants, regional order types and model
edge cases remain deterministic offline tests. The live suite is not evidence
that every account-specific feature has been exercised against OANDA.

## Coverage

Coverage includes branches and measures the SDK (`fivetwenty`) by default. The
99% gate preserves a high baseline; it is not a substitute for asserting correct
outcomes. Model and enum declarations contribute to that percentage. Packaging
fallbacks checked in fresh subprocesses are not included in in-process coverage.

Measure the documentation tools separately:

```sh
uv run python -m pytest tests/unit --cov=docs_validation.src --cov-branch --cov-report=term-missing --cov-fail-under=0
```

That separate report includes developer tooling and must not be described using
the SDK's percentage. The documentation worker runs in a separate interpreter;
its executions are not included in this in-process measurement. No additional
source exclusions were added to improve the coverage result.
