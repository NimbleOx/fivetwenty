# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html)
(pre-1.0: minor versions may contain breaking changes, called out explicitly below).

## [0.4.1] — 2026-08-17

Deep documentation execution-validation follow-up to 0.4.0: live tutorial
execution against the practice API, real execution coverage for guides and
example scripts, and headless notebook execution. Found and fixed three
SDK bugs along the way.

### Fixed
- `pricing.get_account_instrument_candles()` didn't normalize enum
  arguments: `granularity=CandlestickGranularity.M5` (the documented
  idiom) could produce a broken request depending on Python version,
  since `(str, Enum)` formatting behavior changed in 3.11. Confirmed
  live pre/post fix.
- Sync `Client` hung forever if called after `close()` (a stopped event
  loop never resolves `run_coroutine_threadsafe`); it now raises
  `RuntimeError` immediately, and `close()` is idempotent.
- `AsyncClient`'s docstring said `account_id` was always optional; it's
  required alongside `token`.

### Added
- Real (non-mocked) execution coverage extended from 17 to 35
  documentation files (all guides now included); `tests/unit/test_example_scripts.py`
  covers the 11 standalone example scripts; `poe docs-validate-notebooks`
  headlessly executes the 6 example notebooks against a mocked transport.
- Along the way: fixed 20 duplicated closing code fences in
  `forex-trading-concepts.md` that had been rendering ~20 sections of
  the live docs site as raw code, a missing fence in
  `manage-orders-effectively.md` that hid 9 code blocks (14 bugs) from
  every validator, 12 sites in tutorials that crashed instead of
  handling a non-fill gracefully, and dead-on-first-cell bugs in all 6
  example notebooks.

## [0.4.0] — 2026-08-17

Accuracy and hardening release: the SDK was audited end-to-end against OANDA's live v20 API
and current developer documentation. Several fixes are breaking.

### Fixed
- **Breaking** — `transactions.get_recent_transactions()` previously always
  returned an empty list: it sent an unsupported `count` query parameter and
  expected inline transaction data from an endpoint that only returns page
  URLs. It now resolves the account's `lastTransactionID` and fetches the
  trailing ID range via `/transactions/idrange`. With a type filter, fewer
  than `count` transactions may be returned (the filter applies within the ID
  range); `count` is now validated to 1–500.
- Transaction parsing no longer raises `ValueError` for
  `ORDER_CLIENT_EXTENSIONS_MODIFY_REJECT` and
  `TRADE_CLIENT_EXTENSIONS_MODIFY_REJECT`; the dispatcher is now an
  exhaustive type→model map covering all 38 OANDA transaction types, and
  both models joined `TransactionUnion`.
- `MarketOrderRejectTransaction.instrument`/`.units` are now optional —
  OANDA omits them on trade-close and closeout-generated rejects (observed
  live), which previously made such histories unparseable.
- `pricing.get_pricing_stream(snapshot=False)` is honored: the parameter is
  now always sent explicitly instead of being omitted (the server default is
  true, so omission silently ignored the argument).
- `stream_pricing_with_retries` no longer sends the nonexistent
  `includeHeartbeats` query parameter;
  `StreamingConfiguration.include_heartbeats` now controls whether heartbeats
  are yielded to the caller, as documented.
- The version fallback in `fivetwenty.__version__` no longer hardcodes a
  stale release number.
- Timed-out POST/PUT/PATCH requests are no longer retried: a timed-out write
  may have reached the server, and re-sending a market order could
  double-submit it. Timeout retries now apply to safe methods only.
- `_stream_with_retries` yields the CONNECTING/RECONNECTING state with the
  first line after a (re)connection, so consumers can detect recoveries as
  documented; previously every event carried CONNECTED.
- The sync `Client.pricing.stream_iter` no longer discards the newest event
  when its queue overflows; it drops the oldest instead, so slow consumers
  keep receiving current prices.
- `ApiResponse` snake_case attribute access now resolves `*_ids` and
  `*_vwap` fields (`tradeIDs`, `fullVWAP`); the camelCase converter produced
  `IDS`/`Vwap` for these suffixes.
- `ConfigValidator.validate_account_id` accepts real OANDA account IDs; the
  user segment varies in length (6-9 digits observed), and the previous
  pattern hardcoded exactly 7.
- `CalculatedAccountState` and `AccumulatedAccountState` can be instantiated
  again; type-checking-only imports had made their annotations unresolvable
  at model build time.

### Changed
- **Breaking** — `DelayedTradeCloseTransaction` renamed to
  `DelayedTradeClosureTransaction`, matching OANDA's definition.
- `instruments.get_instrument_candles()` `granularity` now defaults to
  `"S5"` (the API default) instead of being required.
- Instrument parameters and model fields are typed `InstrumentName | str`:
  OANDA defines instrument names as open strings, and account divisions can
  expose instruments outside the convenience enum. Response parsing tolerates
  unknown instrument names instead of raising.
- `models.__all__` deduplicated (`AccountChanges`/`AccountChangesState` were
  listed twice).

### Added
- `instruments.get_instrument_order_book()` and
  `instruments.get_instrument_position_book()`
  (`GET /v3/instruments/{instrument}/{orderBook,positionBook}`), with
  `OrderBookBucket`, `PositionBook`, and `PositionBookBucket` models;
  `OrderBook.buckets` now uses the correct bucket shape
  (`price`/`longCountPercent`/`shortCountPercent`).
- `AsyncClient(datetime_format=...)` sends the `Accept-Datetime-Format`
  header (`"RFC3339"` default, `"UNIX"` supported) on every request and
  stream.
- Documentation: instruments endpoint reference page, all 41 enums
  documented, rendered example notebooks, corrected endpoint quick-reference
  table, and a full accuracy/completeness findings report
  (`docs_validation/reviews/2026-08-findings.md`).
- CI: quality gates (format, lint, mypy strict, unit tests) on push and PR;
  repaired documentation maintenance workflow.
- Tests: unit suite grew from 567 to 834 with 98% coverage; every model
  class now has named field/alias tests, and a systematic alias-consistency
  test pins all hand-typed camelCase aliases against the converter.
- Packaging: Development Status classifier moved to Production/Stable.

## [0.3.2] — 2026-05-06
- Hardened client and live-integration safety checks.
- Live integration validation stabilized (preflight/postflight account state
  guards); typecheck and release quality gates expanded.
- Generated model round-trip contract tests; auditable parity waivers; docs
  validation fails on fragment audit flags.
- Docs workflows updated for Node 24 actions.

## [0.3.1] — 2025-10-09
- Packaging metadata fix on top of 0.3.0; no functional changes.

## [0.3.0] — 2025-10-09
- TypedDict return types across endpoints, executable documentation
  examples, and release automation.
- Extensive documentation restructuring (client, configuration,
  contributing).

## [0.2.0] — 2025-09-30
- Initial public release: async-first OANDA v20 SDK with sync wrapper,
  comprehensive Pydantic models, streaming with reconnection support, and
  MkDocs documentation site.
