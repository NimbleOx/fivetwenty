"""Systematic consistency check between model aliases and the compat converter.

Every OANDA-facing model field must carry an alias that `_snake_to_oanda` can
reproduce from the Python field name (or need no alias at all). This pins down
two invariants at once:

1. Hand-typed ``Field(alias=...)`` values follow OANDA's camelCase convention —
   an alias typo anywhere in the ~950 aliased fields fails this test.
2. ``ApiResponse``'s snake_case attribute compatibility (which derives the
   camelCase key via ``_snake_to_oanda``) actually finds those aliases.

Genuine irregulars are listed explicitly so new ones are a conscious decision.
"""

from fivetwenty._internal.response import _snake_to_oanda
from fivetwenty.models.base import ApiModel

# SDK-only configuration models: not OANDA payloads, snake_case by design.
EXCLUDED_CLASSES = {"ReconnectionPolicy", "StreamingConfiguration", "StreamState"}

# (class name, field name) -> alias that intentionally deviates from the converter.
KNOWN_IRREGULAR_ALIASES = {
    # Leading acronym: the converter only uppercases non-leading parts.
    ("Account", "nav"): "NAV",
    ("AccountSummary", "nav"): "NAV",
    ("AccountChangesState", "nav"): "NAV",
    ("CalculatedAccountState", "nav"): "NAV",
    # OANDA's query parameter is the reserved-ish word "type".
    ("TransactionQueryFilter", "type_filter"): "type",
}


def _all_api_models() -> list[type[ApiModel]]:
    out: set[type[ApiModel]] = set()

    def walk(cls: type[ApiModel]) -> None:
        for sub in cls.__subclasses__():
            out.add(sub)
            walk(sub)

    walk(ApiModel)
    return sorted(out, key=lambda c: c.__name__)


def test_every_alias_matches_the_snake_to_oanda_converter() -> None:
    failures: list[str] = []
    checked = 0
    for cls in _all_api_models():
        if cls.__name__ in EXCLUDED_CLASSES:
            continue
        for field_name, field_info in cls.model_fields.items():
            expected = _snake_to_oanda(field_name)
            irregular = KNOWN_IRREGULAR_ALIASES.get((cls.__name__, field_name))
            if field_info.alias is None:
                # No alias means the field name must already be its own OANDA key.
                if expected != field_name:
                    failures.append(f"{cls.__name__}.{field_name}: no alias, but OANDA key would be {expected!r}")
            elif irregular is not None:
                if field_info.alias != irregular:
                    failures.append(f"{cls.__name__}.{field_name}: alias {field_info.alias!r} != documented irregular {irregular!r}")
            elif field_info.alias != expected:
                failures.append(f"{cls.__name__}.{field_name}: alias {field_info.alias!r} != converter output {expected!r}")
            checked += 1

    assert not failures, "Alias/converter drift:\n" + "\n".join(failures)
    assert checked > 1000, f"sanity: expected to check >1000 fields, checked {checked}"


def test_known_irregulars_still_exist() -> None:
    """If an irregular is removed or renamed, drop it from the allowlist."""
    by_name = {cls.__name__: cls for cls in _all_api_models()}
    for (cls_name, field_name), alias in KNOWN_IRREGULAR_ALIASES.items():
        cls = by_name.get(cls_name)
        assert cls is not None, f"allowlisted class {cls_name} no longer exists"
        field = cls.model_fields.get(field_name)
        assert field is not None, f"allowlisted field {cls_name}.{field_name} no longer exists"
        assert field.alias == alias


def test_converter_handles_oanda_suffix_conventions() -> None:
    assert _snake_to_oanda("trade_id") == "tradeID"
    assert _snake_to_oanda("trade_ids") == "tradeIDs"
    assert _snake_to_oanda("closing_transaction_ids") == "closingTransactionIDs"
    assert _snake_to_oanda("full_vwap") == "fullVWAP"
    assert _snake_to_oanda("unrealized_pl") == "unrealizedPL"
    assert _snake_to_oanda("margin_closeout_nav") == "marginCloseoutNAV"
    assert _snake_to_oanda("time_in_force") == "timeInForce"
    assert _snake_to_oanda("simple") == "simple"
