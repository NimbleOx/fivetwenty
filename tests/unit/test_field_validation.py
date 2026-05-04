"""Tests for OANDA field validation tooling."""

from docs_validation.src.parity.field_validate import (
    LibraryCatalog,
    LibraryField,
    LibraryType,
    OfficialDefinition,
    OfficialField,
    _resolve_fields,
    _types_equivalent,
    validate,
)


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
