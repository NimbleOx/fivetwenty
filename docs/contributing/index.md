# Contribute to FiveTwenty

Start with a focused bug report, API mismatch, test improvement or documentation
change. Include the observed behavior, the expected behavior and a reproducible
example that contains no credentials.

## Set up and check a change

```bash
git clone https://github.com/NimbleOx/fivetwenty.git
cd fivetwenty
uv sync --group dev
uv run poe check-fast
```

`check-fast` checks formatting, lint, types and deterministic unit tests. It does
not run authenticated OANDA integration tests. The task definitions in
`pyproject.toml` are the source of truth for available commands.

Use [development setup](development-setup.md) for individual commands,
[code style](code-style.md) for implementation conventions, and the
[testing guide](testing-guide.md) for HTTP mocks and live-test opt-in.

## Match the API contract

When changing an endpoint or model, compare the relevant OANDA documentation and
existing request/response types. Preserve wire field names, optional-field semantics
and numeric precision. Add focused regression evidence for behavior changes; do not
add duplicate tests merely to execute more lines.

Update the relevant [reference](../api-reference/index.md) and any affected
[tutorials](../tutorials/index.md) or [examples](../examples.md). Explain defaults,
return envelopes, conditional fields and account mutations where a reader needs them.

## Submit a pull request

Describe the concrete problem and resulting behavior, then state how the change was
verified. Keep the scope reviewable and identify any remaining limits, such as an
account-specific feature that was tested offline but not exercised against OANDA.
Review the staged diff before committing so local credentials and generated reports
are not included accidentally.

For API questions, include the SDK and Python versions, practice/live environment,
relevant error code and a sanitized example. Use
[issues](https://github.com/NimbleOx/fivetwenty/issues) for bugs and
[discussions](https://github.com/NimbleOx/fivetwenty/discussions) for usage questions.
Report security vulnerabilities privately through
[GitHub Security Advisories](https://github.com/NimbleOx/fivetwenty/security/advisories).
