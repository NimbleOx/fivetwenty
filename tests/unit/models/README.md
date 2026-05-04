# Model Tests

This directory contains model-focused unit tests for `fivetwenty.models`.

Most files follow the source module they exercise:

| Model module | Primary test file |
|---|---|
| `accounts.py` | `test_accounts.py` |
| `base.py` | `test_base.py` |
| `instruments.py` | `test_instruments.py` |
| `orders.py` | `test_orders.py` |
| `positions.py` | `test_positions.py` |
| `pricing.py` | `test_pricing.py` |
| `streaming.py` | `test_streaming.py` |
| `trades.py` | `test_trades.py` |
| `transactions.py` | `test_transactions.py` |

Cross-cutting model behavior lives in separate contract tests. In particular,
`test_roundtrip_contracts.py` discovers every public Pydantic model in
`fivetwenty.models`, builds representative API-style payloads, dumps by OANDA
aliases, and reparses the dumped JSON shape. That catches broad serialization,
alias, enum, decimal, datetime, and forward-reference regressions without
duplicating every domain-specific assertion.

## Working With Model Tests

Run all model tests:

```bash
uv run pytest tests/unit/models/
```

Run one module while editing its model file:

```bash
uv run pytest tests/unit/models/test_orders.py
```

Run the generated round-trip contract suite:

```bash
uv run pytest tests/unit/models/test_roundtrip_contracts.py
```

## Test Expectations

When changing a model:

1. Keep domain-specific behavior in the matching `test_<module>.py` file.
2. Add targeted tests for new defaults, aliases, validation rules, or helper
   methods.
3. Let `test_roundtrip_contracts.py` cover generic API payload round-tripping.
4. If a new model needs unusual generated sample data, update the helper in
   `test_roundtrip_contracts.py` instead of weakening the contract.
