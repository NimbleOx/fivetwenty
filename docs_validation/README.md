# Documentation Validation

This directory contains the validation tools for FiveTwenty documentation. The
system has two separate jobs:

1. Validate documentation files as authored: markdown structure, Python examples,
   links, security checks, financial precision, SDK method usage, and selected
   executable examples.
2. Validate API parity: compare the SDK and project docs against the official
   OANDA REST v20 documentation.

The official OANDA REST v20 documentation is the source of truth for parity
validation:

```text
https://developer.oanda.com/rest-live-v20/
```

## Quick Start

Run the default documentation validation from the repository root:

```bash
uv run poe docs-validate
```

That runs both validation tracks:

```bash
uv run poe docs-validate-files
uv run poe docs-validate-parity
```

Use the refresh task when you want to pull a fresh copy of the live OANDA docs
before running parity:

```bash
uv run poe docs-validate-parity-refresh
```

For a single documentation file, use the CLI directly:

```bash
uv run python -m docs_validation.src.cli validate \
  --config docs_validation/config/validation-complete.yml \
  --files docs/tutorials/getting-started/authentication.md
```

## Validation Tracks

### File-by-file docs validation

Command:

```bash
uv run python -m docs_validation.src.cli validate \
  --config docs_validation/config/validation-complete.yml
```

Configuration:

```text
docs_validation/config/validation-complete.yml
```

This track scans authored docs under `docs/**/*.md` plus the project `README.md`. It runs the configured
validators in `docs_validation/src/validators/`:

- `python_syntax`: syntax-check Python code blocks.
- `code_linting`: run Ruff against extracted Python examples.
- `code_typing`: run mypy checks against examples.
- `code_execution`: execute selected standalone examples with mocked API calls.
- `cross_references`: validate internal documentation references.
- `external_links`: check external links.
- `financial_precision`: catch unsafe numeric patterns in financial examples.
- `markdown_syntax`: validate markdown structure.
- `sdk_methods`: verify documented SDK method usage.
- `security`: detect exposed secrets and unsafe placeholder patterns.

Useful variants:

```bash
# Force sequential execution while debugging a validator.
uv run python -m docs_validation.src.cli validate \
  --config docs_validation/config/validation-complete.yml \
  --sequential

# Increase parallelism.
uv run python -m docs_validation.src.cli validate \
  --config docs_validation/config/validation-complete.yml \
  --parallel \
  --max-workers 8

# Validate only changed or targeted files.
uv run python -m docs_validation.src.cli validate \
  --config docs_validation/config/validation-complete.yml \
  --files docs/guides/understanding/best-practices.md
```

### OANDA parity validation

Command:

```bash
uv run python -m docs_validation.src.parity.run_all --no-fetch
```

Refresh command:

```bash
uv run python -m docs_validation.src.parity.run_all --refresh
```

The parity pipeline compares three surfaces:

- The SDK implementation in `fivetwenty/`.
- The project documentation in `docs/api-reference/`, guides, examples, and
  README content.
- The cached official OANDA REST v20 pages in `docs_validation/.cache/oanda/`.

`--no-fetch` uses the current local cache and fails if required cached pages are
missing. `--refresh` fetches live OANDA pages first, converts them into
parser-friendly markdown, and then runs the parity checks.

Use the strict mode when you want parity drift to fail the command:

```bash
uv run python -m docs_validation.src.parity.run_all --no-fetch --strict
```

### Field-level OANDA validation

The field validator checks model and response fields:

```bash
uv run python -m docs_validation.src.parity.field_validate
```

It validates official OANDA definitions against SDK models and response
TypedDicts. It checks:

- missing official models or SDK equivalents;
- missing fields;
- enum value drift;
- primitive aliases that are not represented in the SDK;
- requiredness drift;
- default drift;
- type drift;
- broad SDK types such as `dict[str, Any]` where OANDA documents a concrete
  object type.

Use `--refresh` to refresh only the official definition pages needed by the
field validator:

```bash
uv run python -m docs_validation.src.parity.field_validate --refresh
```

Use `--fail-on` for CI-style thresholds:

```bash
uv run python -m docs_validation.src.parity.field_validate --fail-on P0
```

Severity levels:

- `P0`: data-loss or deserialization risk, such as an official field missing
  from the SDK.
- `P1`: important enum or primitive representation drift.
- `P2`: type, requiredness, or default drift that needs review.
- `P3`: SDK extras or lower-risk drift.

Known parity drift can be waived in:

```text
docs_validation/config/parity-waivers.yml
```

Each waiver must name the generated issue code, exact target, reason, source
URL, expiry date, and optional severity. Active waivers are excluded from the
field-validation severity summary but are shown in the report. Expired waivers
do not suppress drift, and unused waivers are reported so stale exceptions get
cleaned up.

## Reports and Cache

Generated files are intentionally kept out of git:

```text
docs_validation/reports/
docs_validation/.cache/
```

The repository keeps `docs_validation/reports/.gitkeep` so the reports directory
exists after checkout.

Important generated reports:

- `docs_validation/reports/validation-report.md`: file-by-file validation
  output.
- `docs_validation/reports/<domain>-parity.md`: per-domain parity report for
  accounts, instruments, orders, positions, pricing, trades, and transactions.
- `docs_validation/reports/enums-parity.md`: enum value-set parity.
- `docs_validation/reports/tutorials-parity.md`,
  `guides-parity.md`, `examples-parity.md`, and `readme-parity.md`: docs-surface
  references against the SDK.
- `docs_validation/reports/field-validation.md`: strict field-level OANDA
  validation.

Important cache directories:

- `docs_validation/.cache/oanda/`: fetched official OANDA pages converted to
  markdown.
- `docs_validation/.cache/parity/`: extracted JSON surfaces and intermediate
  diff output.

Do not hand-edit generated reports or cache files. Fix the SDK, project docs, or
validation tooling, then regenerate the reports.

## Directory Layout

```text
docs_validation/
  README.md
  config/
    validation-complete.yml
  reports/
    .gitkeep
  src/
    cli.py
    engine.py
    config.py
    base.py
    models.py
    reporters/
    validators/
    parity/
  validation_plans/
```

Key parity modules:

- `live_oanda_fetch.py`: fetch live OANDA HTML and cache parser-friendly
  markdown.
- `extract_oanda_md.py`: extract OANDA definitions and endpoints from cached
  markdown.
- `extract_pydantic.py`: extract SDK model, enum, alias, and TypedDict surface.
- `extract_endpoints.py`: extract SDK endpoint methods and request paths.
- `extract_doc_tables.py`: extract API reference tables from project docs.
- `diff.py`: compare extracted surfaces and render markdown/JSON diffs.
- `run_domain.py`: run parity for one OANDA domain.
- `run_all.py`: run the full parity pipeline.
- `field_validate.py`: run strict field-by-field validation.

## Fragment Markers

Documentation examples can opt out of specific validators with HTML comments
placed in the three lines before a code block. Fragment markers are an escape
hatch for intentionally incomplete snippets, placeholder configuration, or
examples that are built up across multiple blocks. They should not be used to
hide stale SDK usage or code that should be corrected.

Example:

````markdown
<!-- validation: skip-typing -->
```python
client = make_client_from_context()
```
````

Supported markers:

- `<!-- validation: skip -->` and `<!-- validation: skip-all -->`: skip all
  code-block validators for the next block.
- `<!-- fragment: partial example -->`, `<!-- partial: configuration snippet -->`,
  and `<!-- example: incomplete code -->`: skip all code-block validators and
  record the human-readable reason in the validation report.
- `<!-- validation: skip-linting -->`, `<!-- skip-linting -->`,
  `<!-- no-linting -->`, `<!-- skip-lint -->`, and `<!-- no-lint -->`: skip
  Ruff linting only.
- `<!-- validation: skip-typing -->`, `<!-- skip-typing -->`,
  `<!-- no-typing -->`, `<!-- skip-type -->`, and `<!-- no-type -->`: skip
  type checking only.
- `<!-- validation: skip-syntax -->`, `<!-- skip-syntax -->`, and
  `<!-- no-syntax -->`: skip Python syntax validation only.
- `<!-- validation: skip-execution -->`, `<!-- skip-execution -->`, and
  `<!-- no-execution -->`: skip execution validation only.

Marker matching is case-insensitive and only applies to HTML comments. Specific
markers are not treated as broader skips, so `validation: skip-linting` does not
also skip typing or execution.

The generated `docs_validation/reports/validation-report.md` includes a
fragment-marker usage section with skipped-block counts, the validators skipped,
and audit flags for marker reasons that look like validation debt rather than an
intentionally incomplete or placeholder snippet. `docs-validate-files` fails
when those audit flags are present.

Good uses:

- Tutorial steps that rely on state introduced in surrounding prose.
- Configuration examples with placeholder credentials.
- Intentionally failing examples that demonstrate validation or error handling.
- Small fragments that illustrate one pattern rather than a complete runnable
  program.

Avoid using markers for:

- Stale SDK method names or response shapes.
- Type errors caused by incorrect examples.
- Lint violations that are easy to fix without hurting readability.
- Complete examples that should be valid under the normal validators.

When in doubt, fix the snippet instead of marking it.

## Development Workflow

Before changing validators or parity tools, run focused checks first:

```bash
uv run ruff check docs_validation/src
uv run mypy docs_validation/src/parity/field_validate.py \
  docs_validation/src/parity/extract_pydantic.py \
  docs_validation/src/parity/extract_endpoints.py \
  docs_validation/src/parity/extract_oanda_md.py \
  docs_validation/src/parity/extract_doc_tables.py
uv run pytest tests/unit/test_field_validation.py
```

Then run broader checks:

```bash
uv run pytest tests/unit
uv run python -m docs_validation.src.parity.run_all --no-fetch
```

Run the refresh command before final parity review when the task depends on the
current official OANDA docs:

```bash
uv run python -m docs_validation.src.parity.run_all --refresh
```

## Adding or Changing Validators

File-by-file validators live in `docs_validation/src/validators/`.

When adding a validator:

1. Implement the validator class using the existing validator interfaces.
2. Register or expose it consistently with the existing validators.
3. Add configuration in `docs_validation/config/validation-complete.yml`.
4. Add focused tests.
5. Run the CLI against at least one representative documentation file.

When changing parity behavior:

1. Prefer shared extractor helpers over one-off parsing.
2. Keep cached official OANDA pages as inputs, not committed source.
3. Preserve source references in reports whenever possible.
4. Re-run `field_validate` and `run_all --no-fetch`.
5. If the behavior depends on current OANDA docs, also run the refresh command.

## Troubleshooting

If the parity cache is missing:

```bash
uv run python -m docs_validation.src.parity.run_all --refresh
```

If live OANDA fetches fail, retry with cached pages while working locally:

```bash
uv run python -m docs_validation.src.parity.run_all --no-fetch
```

If a documentation code block is intentionally incomplete, add a fragment marker
instead of weakening the validator globally.

If a parity report shows a field missing from the SDK, treat the official OANDA
definition page as source of truth and either update the SDK model or document
why a configured alias/exception is appropriate.

### Code-check outcomes

Missing mypy or Ruff executables, tool failures, and timeouts fail validation.
The command exits with status 1 when validation errors or fragment-audit failures are reported.
Install the development dependencies and include their executable directory in
PATH. All Python blocks are checked, including single-line examples and strings
containing `...`. A standalone ellipsis statement indicates an incomplete example
and is reported as a skip. HTML fragment markers remain the explicit way to mark
context-dependent snippets. Reports count both marker skips and implicit skips,
including files outside the execution include list.

## Interpreting validation evidence

A passing build checks site generation, not every Python example or API behavior.
Parity checks cover what their extractors recognize in the selected source cache;
review waivers, cache age and source differences alongside the result. Passing a
mocked example does not establish account eligibility or live execution behavior.

The file execution validator uses a restricted namespace and SDK test doubles.
Defining a helper does not execute its body, and a failure can come from an
incomplete double rather than the real SDK. Use HTTP-boundary example tests and the
mocked notebook runner to exercise actual serialization, parsing and lifecycle
behavior. Report those checks separately from file-validator diagnostics.

Generated reports are diagnostics, not independent reviews of prose or financial
claims. Inspect the rule and affected content before treating a lint issue, a broken
public link and a runtime failure as the same kind of problem.
