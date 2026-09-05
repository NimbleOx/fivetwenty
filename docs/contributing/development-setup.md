# Development setup

Use Python 3.10 or later, Git and uv. From a repository checkout:

```bash
uv sync --group dev
uv run python -c "import fivetwenty; print(fivetwenty.__file__)"
uv run poe check-fast
```

The import path should point into this checkout. `uv sync --group dev` installs the
project and development dependencies from the lock file; it does not itself run tests.

## Common commands

| Command | Purpose |
| --- | --- |
| `uv run poe format` | Apply Ruff formatting |
| `uv run poe format-check` | Check formatting without edits |
| `uv run poe lint` | Run Ruff lint checks |
| `uv run poe typecheck` | Check SDK, examples, validators and tests with mypy |
| `uv run poe test` | Run deterministic unit tests |
| `uv run poe test-cov` | Measure SDK statement and branch coverage |
| `uv run poe check-fast` | Run format check, lint, types and unit tests |
| `uv run poe docs-serve` | Preview documentation locally |
| `uv run python -m mkdocs build --clean --strict` | Build documentation and fail on warnings |
| `uv run poe docs-validate` | Run document validators and cached parity checks |
| `uv run poe docs-validate-notebooks` | Execute notebooks with mocked HTTP |

To work on one behavior, run the relevant test file before the full check:

```bash
uv run pytest tests/unit/test_client_transport.py
```

## Credentials and live tests

Unit tests and mocked notebook execution do not need OANDA credentials. The live
suite requires explicit opt-in and a dedicated practice account; some cases create
and close trades. Follow the [testing guide](testing-guide.md#live-integration)
before running it. Do not use live account credentials for development checks.

A `.env` file is not automatically loaded by every command. Use the environment
loading behavior of the particular script or test, and keep credentials out of Git.

## Repository layout

| Path | Contents |
| --- | --- |
| `fivetwenty/client.py` | Async transport and synchronous wrapper |
| `fivetwenty/configuration.py` | Account configuration and environment loading |
| `fivetwenty/endpoints/` | Resource-specific API methods and response envelopes |
| `fivetwenty/models/` | Request/response models, enums and aliases |
| `tests/unit/` | Deterministic contract and tooling tests |
| `tests/integration/` | Opt-in practice API tests |
| `docs/examples/` | Scripts and notebooks |
| `docs_validation/` | Documentation and API-parity tools |

When adding a method to an existing endpoint group, follow that group's patterns.
A new group also needs client attachment and public API documentation. Put new
models in the relevant module under `fivetwenty/models/`, and update exports where
public access is intended.

## Editor and troubleshooting

Select this checkout's `.venv` interpreter in your editor. Configure Ruff and pytest
against the same environment used by the commands above. If an import resolves to
another installation, inspect the interpreter and import path before reinstalling.

Run a failing check directly to see its diagnostics. A documentation validation
failure can indicate a content issue or a failed validation dependency; a successful
site build alone does not establish that embedded Python examples run correctly.
