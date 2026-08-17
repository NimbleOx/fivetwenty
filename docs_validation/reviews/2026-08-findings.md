# fivetwenty OANDA v20 Accuracy & Completeness Review — August 2026

## Methodology

- **Spec sources**: live scrape of developer.oanda.com/rest-live-v20 (fetched 2026-08-16 via `poe docs-validate-parity-refresh`), cross-checked against the vendored `oanda-api-reference/` snapshot. OANDA's site no longer serves the instrument endpoints page (`instrument-ep` returns 404 and is absent from their nav); for that domain the April 2026 cached snapshot, OANDA's release notes, and live API probes serve as the source of truth. Where scraped docs and live behavior conflict, live behavior wins.
- **Live verification**: read-only probes against the PRACTICE environment (2026-08-16, market closed) confirmed response shapes for the transactions list endpoint, `Accept-Datetime-Format` handling, candles defaults, orderBook/positionBook availability, and the account instrument list. The full live integration suite runs after market open (Sunday 17:00 ET); order-placement lanes are marked "pending market open" until then.
- **Harness note**: the repo's own parity pipeline reported "no drift" at baseline, but had blind spots that hid real findings (see F-TOOL-01…04). Those were fixed first (commit A) so every number below comes from a trustworthy pipeline.
- **Severity scheme** (same as `field_validate.py`): P0 wrong behavior/data loss · P1 spec violation or materially wrong claim · P2 drift/inconsistency · P3 cosmetic.
- **Categories**: SDK-ACC (SDK vs OANDA accuracy) · DOC-COMP (docs completeness) · DOC-ACC (docs accuracy) · TOOL (tooling/CI) · TEST (test coverage).

## Summary

| | P0 | P1 | P2 | P3 |
|---|---|---|---|---|
| SDK-ACC | 1 | 3 | 3 | 4 |
| DOC-COMP | – | 1 | 2 | 1 |
| DOC-ACC | – | 2 | 2 | 2 |
| TOOL | – | 6 | 3 | 3 |
| TEST | – | – | 2 | – |

## Findings

### SDK accuracy (SDK-ACC)

- **F-SDK-01 · P0 · `get_recent_transactions` always returns an empty list.** `fivetwenty/endpoints/transactions.py:384` sends a `count` query param (not accepted by `GET /v3/accounts/{id}/transactions`; spec accepts `from`/`to`/`pageSize`/`type`) and parses `data.get("transactions", [])` — but the endpoint returns `{from, to, pageSize, count, pages[], lastTransactionID}` with page **URLs**, never an inline `transactions` array. **Confirmed live 2026-08-16**: HTTP 200, no `transactions` key. Every caller silently receives `[]`. *Resolution: rewritten in commit B via `lastTransactionID` + `/transactions/idrange`; breaking (0.4.0).*
- **F-SDK-02 · P1 · `_parse_transaction` crashes on two real transaction types.** The dispatcher (`transactions.py:434`) has no branch for `ORDER_CLIENT_EXTENSIONS_MODIFY_REJECT` or `TRADE_CLIENT_EXTENSIONS_MODIFY_REJECT` and raises `ValueError`, so any history/stream containing one breaks parsing entirely. The models exist (`models/transactions.py:577,597`) but are also missing from `TransactionUnion` (`transactions.py:63`, 36 members vs OANDA's 38 types). *Resolution: commit B — dispatch replaced with an exhaustive type→class map + completeness test.*
- **F-SDK-03 · P1 · `DelayedTradeCloseTransaction` misnames OANDA's `DelayedTradeClosureTransaction`.** Confirmed against the refreshed `transaction-df` spec. *Resolution: commit B — hard rename (0.4.0), no alias.*
- **F-SDK-04 · P1 · No `Accept-Datetime-Format` support.** The `AcceptDatetimeFormat` enum exists (`models/enums.py:286`) but no request ever sends the header. **Confirmed live**: the server honors `UNIX` and returns epoch-format timestamps. *Resolution: commit B — client-level option sent on `_request` and `_stream`, default RFC3339 (preserves current behavior).*
- **F-SDK-05 · P2 · orderBook/positionBook endpoints missing.** `GET /v3/instruments/{instrument}/orderBook` and `/positionBook` are live (**confirmed 2026-08-16**: HTTP 200, 6701/596 buckets) and in OANDA's release notes, though the current doc site no longer renders the instrument endpoints page. The `OrderBook` model exists with no endpoint — and its `buckets` field is typed as `list[PriceBucket]` (`{price, liquidity}`) while the real bucket shape is `{price, longCountPercent, shortCountPercent}`, so it would mis-parse if ever used. `PositionBook` was deliberately removed (`models/pricing.py:129` comment calls it "not part of official OANDA v20 API" — incorrect). *Resolution: commit B — implement both endpoints, add `OrderBookBucket`/`PositionBookBucket`/`PositionBook`, fix `OrderBook.buckets`.*
- **F-SDK-06 · P2 · `get_instrument_candles` requires `granularity`; the API defaults it.** Spec and live server default to `S5` (**confirmed live**: omitting granularity returns S5 candles). `fivetwenty/endpoints/instruments.py:30` makes it keyword-required. *Resolution: commit B — default `"S5"`.*
- **F-SDK-07 · P2 · `InstrumentName` is a closed 68-member enum; OANDA defines an open string.** `primitives-df`: "A string containing the base currency and quote currency delimited by a '_'". The enum exactly covers this practice account's 68 instruments (**confirmed live**) but other account divisions (CFDs, metals-only, region-specific) can expose names outside it, which would fail model validation. *Resolution: commit B — parameters and model fields accept `InstrumentName | str`; enum kept for autocomplete.*
- **F-SDK-08 · P3 · `stream_pricing_with_retries` sends `includeHeartbeats`, which is not a pricing-stream parameter.** Spec params are `instruments`/`snapshot`/`includeHomeConversions` only; heartbeats are always sent. *Resolution: commit B — parameter dropped from the request.*
- **F-SDK-09 · P3 · `get_pricing` sends deprecated `includeUnitsAvailable`.** Spec: "Deprecated: Will be removed in a future API update." *Resolution: commit B — kept (still functional) but docstring and docs note the deprecation.*
- **F-SDK-10 · P3 · `models/__init__.py` `__all__` lists `AccountChanges` and `AccountChangesState` twice** (155 entries, 153 unique). *Resolution: commit B.*
- **F-SDK-11 · P3 · `__init__.py` hardcodes version fallback `"0.3.0"`** while pyproject is 0.3.2 — guaranteed to drift. *Resolution: commit B — fallback removed/single-sourced.*

### Documentation completeness (DOC-COMP)

- **F-DCOMP-01 · P1 · `docs/api-reference/endpoints/instruments.md` does not exist.** The instruments endpoint group (wired at `client.py:172`) has no reference page; it is also absent from `endpoints/index.md`. This crashed the parity lane for months (masked — see F-TOOL-02). *Resolution: commit C — page written; instruments added to the index.*
- **F-DCOMP-02 · P2 · 19 of 41 enums undocumented** in `models/enum-models.md` (all `*Reason` enums, `TransactionFilter`, `TransactionRejectReason`, `AcceptDatetimeFormat`, `DailyAlignment`, `GuaranteedStopLossOrderMutability`, `TradePL`, …). *Resolution: commit C.*
- **F-DCOMP-03 · P2 · No CHANGELOG anywhere.** *Resolution: commit E — `CHANGELOG.md` backfilled from git history for 0.3.x, 0.4.0 section for this review's breaking changes.*
- **F-DCOMP-04 · P3 · `transaction-models.md` has zero 🔗 Source links** while every other model page links each section to source. *Resolution: commit C.*

### Documentation accuracy (DOC-ACC)

- **F-DACC-01 · P1 · The endpoint quick-reference table is fictional.** `endpoints/index.md:13-19` lists method names that do not exist anywhere in the SDK (`list()`, `get()`, `summary()`, `cancel()`, `stream()`, `candles()`, `replace()`, …) instead of the real `get_accounts()`, `cancel_order()`, `get_pricing_stream()`, `put_order()`, etc. Every row is wrong. *Resolution: commit C — rewritten from the real surface.*
- **F-DACC-02 · P1 · CLAUDE.md is materially wrong about the project.** It claims VCR.py-recorded integration tests (they are live-network-only), documents nonexistent poe tasks (`test-unit`, `test-verbose`, `test-cov`, `quality`, `check`, `dev-install-all`, `docs-validate-fast`, `docs-validate-complete`), says `poe test` runs all tests (unit only), describes `models.py` as a single file (it is a 12-module package), counts "75+ models" (168 classes), and names the error class "VeeTwentyError" (actual: `FiveTwentyError`). `docs/contributing/testing-guide.md:172` (`poe check`) and `docs/guides/understanding/sdk-architecture.md` (VCR claims) repeat the drift. *Resolution: commit E.*
- **F-DACC-03 · P2 · Model counts inconsistent and wrong**: "80+" (`models/index.md:9`) vs "75+" (`docs/index.md`) vs 168 actual classes / 78 documented sections. README claims "100% endpoint coverage (all 7 endpoint groups)" above a list of 6. *Resolution: commits C/E — one number, one counting rule.*
- **F-DACC-04 · P2 · `post_order` documented with an 8-way union**; the signature is `OrderRequest | dict[str, Any]` (`orders.py:142`) — the docs omit the dict branch and hand-expand the alias. Five default-value prose claims also drifted (caught by the new checker; now 0). *Resolution: commit C.*
- **F-DACC-05 · P3 · 11 stale `#L` source anchors in `orders.md`** — every anchored link is 8–33 lines off (e.g. `post_order` anchored L134, defined at L142). Now machine-checked (`docs-meta-parity.md`). *Resolution: commit C, verified by the checker.*
- **F-DACC-06 · P3 · `docs/examples.md` tells users to find examples inside the installed package**, but the wheel packages only `fivetwenty*` and `docs_validation*` — the instruction cannot work. *Resolution: commit C — points at the repository instead.*

### Tooling / CI (TOOL)

- **F-TOOL-01 · P1 · The parity pipeline violated its own exit-code contract.** `run_all.py` documented "exits non-zero on P0 drift" but returned 0 unless `--strict`; blocked lanes were swallowed entirely (summary printed "No drift detected" while the instruments lane was failing). *Resolution: commit A — P0 → exit 1 unconditionally; blocked lanes → exit 2.*
- **F-TOOL-02 · P1 · The instruments parity lane was configured out of existence.** `run_domain.py` had `doc_endpoint: None, has_oanda_endpoint: False` — factually wrong (OANDA had an instrument endpoints page; the API serves three instrument endpoints) — so missing endpoints and the missing doc page never surfaced. A stale `BLOCKED-instruments.md` from May was never cleaned up. *Resolution: commit A — lane restored; missing doc pages now report as P1 findings; stale BLOCKED files auto-cleaned.*
- **F-TOOL-03 · P1 · Streaming endpoints were parity false-negatives.** `extract_endpoints.py` only matched `_request()` calls, so `/pricing/stream` and `/transactions/stream` showed ❌ despite being implemented. *Resolution: commit A — `_stream`/`_stream_with_retries` extraction.*
- **F-TOOL-04 · P1 · Failed OANDA fetches silently reused stale cache.** `live_oanda_fetch.py` printed `FAILED` to stderr and returned 0; a 404 (as `instrument-ep` currently is) left months-old cache masquerading as fresh spec. *Resolution: commit A — stale pages warn loudly, are recorded in `fetch-status.json`, and surface in the pipeline summary; missing-with-no-cache is fatal.*
- **F-TOOL-05 · P1 · `docs-maintenance.yml` weekly cron is broken.** It invokes `scripts/validate-docs.py` and `docs/requirements.txt` — neither exists — masked by `continue-on-error`. *Resolution: commit D.*
- **F-TOOL-06 · P1 · No CI runs tests, lint, or typecheck at all.** Both workflows are docs-only; `docs.yml`'s path filter watches `docs-tooling/validation/**`, a directory that doesn't exist (real: `docs_validation/`), and never runs `docs-validate`. *Resolution: commit D — new `ci.yml`; `docs.yml` filter and validation step fixed.*
- **F-TOOL-07 · P2 · `check-fast`/`check-full` mutate the tree** (they run `ruff format`, not `--check`), so "checks" can dirty a clean working copy. *Resolution: commit D — `format-check` task.*
- **F-TOOL-08 · P2 · No coverage configuration** despite `pytest-cov` being a dependency and `testing-guide.md` documenting targets (80%+ overall). *Resolution: commit D — `[tool.coverage.*]` added.*
- **F-TOOL-09 · P2 · Orphaned/dead test infrastructure**: `pytest-vcr` dependency and `vcr_config` fixture never used; markers `unit`/`slow`/`compliance` declared but unused; `tests/integration/` subpackages missing `__init__.py` (only `orders/` has one); duplicate `test-integration`/`test-integration-live` poe tasks. *Resolution: commit D.*
- **F-TOOL-10 · P3 · mkdocs issues**: `models/index.md` in nav twice; `mkdocs-jupyter` installed but not enabled so the 6 notebooks never render; `docs/examples/scripts/__pycache__/*.pyc` copied into the built site. *Resolution: commit C.*
- **F-TOOL-11 · P3 · Root `520logo.svg` untracked and differs from `docs/assets/520logo.svg`.** Disposition needs an owner decision — it may be a newer logo awaiting placement. *Left untracked; flagged only.*
- **F-TOOL-12 · P3 · Stale generated reports committed to history** (`BLOCKED-instruments.md`, May-era `readme-parity.md` flagging already-fixed version drift). *Resolution: commit A regeneration.*

### Test coverage (TEST)

- **F-TEST-01 · P2 · Zero-coverage public surface**: `stream_pricing_with_retries` (no test anywhere), accounts `get_accounts`/`get_account`/`get_account_summary` (no unit tests), `get_transactions_stream` (no integration test). *Resolution: commit F.*
- **F-TEST-02 · P2 · 93 of 168 model classes have no named tests** — only the generic roundtrip contract exercises them; no field/alias-level assertions for any `*RejectTransaction`, order-state models, instrument models, `AccountSummary`/`AccountChanges`, or `*Reason` enums. *Resolution: commit F — named field/alias tests per module.*

## Deferred items

- OANDA's missing `instrument-ep` documentation page is an upstream regression; the harness now tracks it as a stale-cache warning. Re-check on future refreshes.
- `pages`-following variant of `get_recent_transactions` (chasing page URLs) rejected in favor of the `idrange` design — fewer requests, no URL parsing, same result.

## Verification results

_To be filled in Phase 7 (final gates)._
