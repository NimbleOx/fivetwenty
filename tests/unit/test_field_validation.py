"""Tests for OANDA field validation tooling."""

from pathlib import Path

from docs_validation.src.parity.field_validate import (
    LibraryCatalog,
    LibraryField,
    LibraryType,
    OfficialDefinition,
    OfficialField,
    _resolve_fields,
    _types_equivalent,
    apply_waivers,
    validate,
)
from docs_validation.src.parity.waivers import load_waivers, split_waived_issues


def _field(name: str, annotation: str = "str", *, wire_name: str | None = None) -> LibraryField:
    return LibraryField(
        name=name,
        wire_name=wire_name or name,
        annotation=annotation,
        optional=True,
        default=None,
        has_default=False,
        source_file="sdk.py",
        source_line=1,
    )


def _official_field(name: str, type_: str = "string") -> OfficialField:
    return OfficialField(
        name=name,
        type=type_,
        required=False,
        default=None,
        source_file="oanda.md",
        source_line=1,
        source_url="https://developer.oanda.com/rest-live-v20/test/",
    )


def test_resolve_fields_includes_inherited_base_fields():
    catalog = LibraryCatalog(
        types={
            "BaseTransaction": LibraryType(
                name="BaseTransaction",
                kind="model",
                fields={"id": _field("id")},
                bases=[],
                source_file="base.py",
            ),
            "ChildTransaction": LibraryType(
                name="ChildTransaction",
                kind="model",
                fields={"reason": _field("reason")},
                bases=["BaseTransaction"],
                source_file="child.py",
            ),
        },
    )

    resolved = _resolve_fields("ChildTransaction", catalog)

    assert set(resolved) == {"id", "reason"}
    assert resolved["id"].inherited_from == "BaseTransaction"


def test_validate_does_not_report_missing_inherited_official_field():
    official = {
        "ChildTransaction": OfficialDefinition(
            name="ChildTransaction",
            fields={
                "id": _official_field("id"),
                "reason": _official_field("reason"),
            },
        ),
    }
    catalog = LibraryCatalog(
        types={
            "Transaction": LibraryType(
                name="Transaction",
                kind="model",
                fields={"id": _field("id")},
                bases=[],
                source_file="base.py",
            ),
            "ChildTransaction": LibraryType(
                name="ChildTransaction",
                kind="model",
                fields={"reason": _field("reason")},
                bases=["Transaction"],
                source_file="child.py",
            ),
        },
    )

    issues = validate(official, catalog)

    assert not [issue for issue in issues if issue.code == "missing_field"]


def test_validate_compares_configured_model_name_alias():
    official = {
        "CandlestickResponse": OfficialDefinition(
            name="CandlestickResponse",
            fields={"candles": _official_field("candles", "Array[Candlestick]")},
        ),
    }
    catalog = LibraryCatalog(
        types={
            "CandlesResponse": LibraryType(
                name="CandlesResponse",
                kind="typeddict",
                fields={"candles": _field("candles", "list[Candlestick]")},
                bases=[],
                source_file="endpoints.py",
            ),
        },
    )

    issues = validate(official, catalog)

    assert not [issue for issue in issues if issue.code in {"missing_model", "type_drift"}]


def test_type_equivalence_normalizes_python_and_oanda_collections():
    assert _types_equivalent("Array[TradeID]", "list[TradeID]")
    assert _types_equivalent("DecimalNumber", "Decimal")
    assert _types_equivalent("OrderID", "str")


def test_load_waivers_requires_explicit_audit_fields(tmp_path: Path) -> None:
    waiver_path = tmp_path / "waivers.yml"
    waiver_path.write_text(
        """
waivers:
  - code: missing_field
    target: Trade.marginUsed
    severity: P0
    reason: Reviewed upstream drift while model migration is pending.
    source_url: https://developer.oanda.com/rest-live-v20/trade-df/
    expires: "2099-01-01"
""",
        encoding="utf-8",
    )

    waivers = load_waivers(waiver_path)

    assert len(waivers) == 1
    assert waivers[0].target == "Trade.marginUsed"
    assert waivers[0].severity == "P0"


def test_split_waived_issues_keeps_waivers_exact_and_auditable(tmp_path: Path) -> None:
    waiver_path = tmp_path / "waivers.yml"
    waiver_path.write_text(
        """
waivers:
  - code: missing_field
    target: Trade.marginUsed
    severity: P0
    reason: Reviewed upstream drift while model migration is pending.
    source_url: https://developer.oanda.com/rest-live-v20/trade-df/
    expires: "2099-01-01"
  - code: type_drift
    target: Trade.price
    severity: P2
    reason: Stale waiver that should be reported.
    source_url: https://developer.oanda.com/rest-live-v20/trade-df/
    expires: "2099-01-01"
""",
        encoding="utf-8",
    )
    issue = validate(
        {
            "Trade": OfficialDefinition(
                name="Trade",
                fields={"marginUsed": _official_field("marginUsed", "AccountUnits")},
            ),
        },
        LibraryCatalog(
            types={
                "Trade": LibraryType(
                    name="Trade",
                    kind="model",
                    fields={},
                    bases=[],
                    source_file="trade.py",
                ),
            },
        ),
    )

    result = split_waived_issues(issue, load_waivers(waiver_path))

    assert result.active_issues == []
    assert result.waived_issues[0].issue.code == "missing_field"
    assert result.unused_waivers[0].target == "Trade.price"


def test_apply_waivers_reports_expired_and_unused_waivers(tmp_path: Path) -> None:
    waiver_path = tmp_path / "waivers.yml"
    waiver_path.write_text(
        """
waivers:
  - code: missing_field
    target: Trade.marginUsed
    severity: P0
    reason: Expired waiver must not hide drift.
    source_url: https://developer.oanda.com/rest-live-v20/trade-df/
    expires: "2000-01-01"
  - code: type_drift
    target: Trade.price
    severity: P2
    reason: Stale waiver should be cleaned up.
    source_url: https://developer.oanda.com/rest-live-v20/trade-df/
    expires: "2099-01-01"
""",
        encoding="utf-8",
    )
    raw_issues = validate(
        {
            "Trade": OfficialDefinition(
                name="Trade",
                fields={"marginUsed": _official_field("marginUsed", "AccountUnits")},
            ),
        },
        LibraryCatalog(
            types={
                "Trade": LibraryType(
                    name="Trade",
                    kind="model",
                    fields={},
                    bases=[],
                    source_file="trade.py",
                ),
            },
        ),
    )

    issues, waived = apply_waivers(raw_issues, waiver_path)

    assert waived == []
    assert [issue.code for issue in issues] == ["missing_field", "expired_waiver", "unused_waiver"]
