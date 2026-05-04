"""Strict field-by-field validation against official OANDA REST v20 docs.

This validator is intentionally stricter than the older parity reports:

* OANDA definitions are treated as the source of truth.
* Pydantic inheritance is resolved before comparing fields, so transaction
  subclasses do not repeatedly appear to be missing base Transaction fields.
* Concrete OANDA object fields typed as `dict[str, Any]` in the SDK are flagged.
* Enum values, primitive aliases, defaults, and requiredness are checked
  separately from field presence.

Usage:
    uv run python -m docs_validation.src.parity.field_validate
    uv run python -m docs_validation.src.parity.field_validate --refresh
    uv run python -m docs_validation.src.parity.field_validate --fail-on P0
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from .extract_endpoints import extract_module as extract_endpoints_module
from .extract_oanda_md import extract_definition_with_source
from .extract_pydantic import extract_module as extract_pydantic_module
from .waivers import DEFAULT_WAIVERS_PATH, ParityWaiver, WaivedIssue, load_waivers, split_waived_issues

REPO_ROOT = Path(__file__).resolve().parents[3]
OANDA_CACHE = REPO_ROOT / "docs_validation" / ".cache" / "oanda"
CACHE_DIR = REPO_ROOT / "docs_validation" / ".cache" / "parity"
REPORTS_DIR = REPO_ROOT / "docs_validation" / "reports"
MODELS_DIR = REPO_ROOT / "fivetwenty" / "models"
ENDPOINTS_DIR = REPO_ROOT / "fivetwenty" / "endpoints"

OFFICIAL_DEFINITION_PAGES = [
    "account-df.md",
    "instrument-df.md",
    "order-df.md",
    "position-df.md",
    "pricing-df.md",
    "pricing-common-df.md",
    "trade-df.md",
    "transaction-df.md",
    "primitives-df.md",
]

SEVERITY_ORDER = {"P0": 0, "P1": 1, "P2": 2, "P3": 3}

# Official types that are abstract/interface containers in OANDA docs and are
# intentionally represented as unions or concrete subclasses in the SDK.
ABSTRACT_OFFICIAL_MODELS = {
    "Order",
    "OrderRequest",
}

# Equivalent SDK names where the public library chose a different name from the
# official REST object. The validator still compares field shape through these
# aliases instead of silently suppressing the official model.
MODEL_NAME_ALIASES = {
    "CandlestickResponse": ("CandlesResponse",),
    "DelayedTradeClosureTransaction": ("DelayedTradeCloseTransaction",),
}

UPPERCASE_SUFFIXES = {"id", "ids", "url", "uri", "ip", "api", "pl", "nav"}
ID_ALIASES = {"AccountID", "TradeID", "OrderID", "TransactionID", "RequestID", "ClientID", "ClientOrderID", "ClientTradeID", "OrderSpecifier", "TradeSpecifier", "ClientRequestID", "ClientTag", "ClientComment"}
DECIMAL_ALIASES = {"DecimalNumber", "PriceValue", "AccountUnits", "Decimal"}
PY_PRIMITIVE_MAP = {
    "str": "string",
    "builtins.str": "string",
    "int": "integer",
    "builtins.int": "integer",
    "bool": "boolean",
    "builtins.bool": "boolean",
    "float": "DecimalNumber",
    "Decimal": "Decimal",
    "datetime": "DateTime",
}


@dataclass
class OfficialField:
    name: str
    type: str
    required: bool
    default: str | None
    source_file: str
    source_line: int | None
    source_url: str | None


@dataclass
class OfficialDefinition:
    name: str
    fields: dict[str, OfficialField] = field(default_factory=dict)
    enum_values: list[str] = field(default_factory=list)
    primitive: dict[str, str] = field(default_factory=dict)
    source_file: str = ""
    source_line: int | None = None
    source_url: str | None = None


@dataclass
class LibraryField:
    name: str
    wire_name: str
    annotation: str
    optional: bool
    default: str | None
    has_default: bool
    source_file: str
    source_line: int | None
    inherited_from: str | None = None


@dataclass
class LibraryType:
    name: str
    kind: str
    fields: dict[str, LibraryField]
    bases: list[str]
    source_file: str


@dataclass
class LibraryCatalog:
    types: dict[str, LibraryType] = field(default_factory=dict)
    enums: dict[str, dict[str, Any]] = field(default_factory=dict)
    aliases: dict[str, dict[str, str]] = field(default_factory=dict)


@dataclass
class ValidationIssue:
    severity: str
    code: str
    message: str
    official: str | None = None
    library: str | None = None
    model: str | None = None
    field: str | None = None
    expected: str | None = None
    actual: str | None = None


def _camel_to_snake(name: str) -> str:
    s1 = re.sub(r"(.)([A-Z][a-z]+)", r"\1_\2", name)
    return re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", s1).lower()


def _snake_to_oanda(name: str) -> str:
    if name.endswith("_"):
        name = name[:-1]
    parts = name.split("_")
    if not parts:
        return name
    out = [parts[0]]
    for part in parts[1:]:
        out.append(part.upper() if part in UPPERCASE_SUFFIXES else part.title())
    return "".join(out)


def _source_ref(path: str | None, line: int | None, url: str | None = None) -> str | None:
    if path is None:
        return None
    ref = f"{path}:{line}" if line else path
    if url:
        ref = f"{ref} ({url})"
    return ref


def _extract_official_definition(path: Path) -> dict[str, OfficialDefinition]:
    data = extract_definition_with_source(path)
    definitions: dict[str, OfficialDefinition] = {}

    for type_name, body in data.get("definitions", {}).items():
        definition = definitions.setdefault(
            type_name,
            OfficialDefinition(
                name=type_name,
                source_file=body.get("source_file", data["source_file"]),
                source_line=body.get("source_line"),
                source_url=body.get("source_url", data.get("source_url")),
            ),
        )
        for field_data in body.get("fields", []):
            field_name = field_data["name"]
            definition.fields[field_name] = OfficialField(
                name=field_name,
                type=field_data.get("type", ""),
                required=bool(field_data.get("required")),
                default=field_data.get("default"),
                source_file=field_data.get("source_file", definition.source_file),
                source_line=field_data.get("source_line"),
                source_url=field_data.get("source_url", definition.source_url),
            )
        definition.enum_values = body.get("enum_values", [])
        definition.primitive = body.get("primitive", {})

    return definitions


def build_official_catalog(paths: list[Path] | None = None) -> dict[str, OfficialDefinition]:
    """Extract all official OANDA definitions from cached markdown pages."""
    if paths is None:
        paths = [OANDA_CACHE / name for name in OFFICIAL_DEFINITION_PAGES if (OANDA_CACHE / name).exists()]
    out: dict[str, OfficialDefinition] = {}
    for path in paths:
        for name, definition in _extract_official_definition(path).items():
            existing = out.get(name)
            if existing is None or (not existing.fields and definition.fields):
                out[name] = definition
            else:
                if definition.enum_values and not existing.enum_values:
                    existing.enum_values = definition.enum_values
                if definition.primitive and not existing.primitive:
                    existing.primitive = definition.primitive
    return out


def _library_field(field_name: str, meta: dict[str, Any], source_file: str, inherited_from: str | None = None, *, force_optional: bool | None = None) -> LibraryField:
    alias = meta.get("alias")
    optional = bool(meta.get("optional")) if force_optional is None else force_optional
    return LibraryField(
        name=field_name,
        wire_name=alias or _snake_to_oanda(field_name),
        annotation=meta.get("annotation", ""),
        optional=optional,
        default=meta.get("default"),
        has_default=bool(meta.get("has_default")),
        source_file=source_file,
        source_line=meta.get("line"),
        inherited_from=inherited_from,
    )


def _add_library_data(catalog: LibraryCatalog, data: dict[str, Any], *, include_models: bool) -> None:
    source_file = data["source_file"]
    if include_models:
        for name, fields in data.get("models", {}).items():
            catalog.types[name] = LibraryType(
                name=name,
                kind="model",
                fields={field_name: _library_field(field_name, meta, source_file) for field_name, meta in fields.items()},
                bases=list(data.get("model_bases", {}).get(name, [])),
                source_file=source_file,
            )
    for name, fields in data.get("typeddicts", {}).items():
        field_map = fields.get("fields", fields)
        force_optional = str(fields.get("total", "True")) == "False"
        # Keep the first same-named TypedDict. Existing duplicates are response
        # shapes with matching field names.
        catalog.types.setdefault(
            name,
            LibraryType(
                name=name,
                kind="typeddict",
                fields={field_name: _library_field(field_name, meta, source_file, force_optional=force_optional) for field_name, meta in field_map.items()},
                bases=list(data.get("typeddict_bases", {}).get(name, [])),
                source_file=source_file,
            ),
        )
    for name, enum in data.get("enums", {}).items():
        catalog.enums[name] = {"values": {member: _strip_quotes(value) for member, value in enum.get("values", {}).items()}, "source_file": source_file, "line": enum.get("line")}
    for name, value in data.get("type_aliases", {}).items():
        catalog.aliases[name] = {"value": value, "source_file": source_file}


def build_library_catalog() -> LibraryCatalog:
    catalog = LibraryCatalog()
    for path in sorted(MODELS_DIR.glob("*.py")):
        if path.name != "__init__.py":
            _add_library_data(catalog, extract_pydantic_module(path), include_models=True)
    for path in sorted(ENDPOINTS_DIR.glob("*.py")):
        if path.name != "__init__.py":
            _add_library_data(catalog, extract_endpoints_module(path), include_models=False)
    return catalog


def _resolve_fields(type_name: str, catalog: LibraryCatalog, seen: set[str] | None = None) -> dict[str, LibraryField]:
    seen = seen or set()
    if type_name in seen:
        return {}
    seen.add(type_name)
    lib_type = catalog.types.get(type_name)
    if lib_type is None:
        return {}
    merged: dict[str, LibraryField] = {}
    for base in lib_type.bases:
        if base in catalog.types:
            for key, field_meta in _resolve_fields(base, catalog, seen).items():
                merged[key] = LibraryField(**{**asdict(field_meta), "inherited_from": field_meta.inherited_from or base})
    for field_meta in lib_type.fields.values():
        merged[field_meta.wire_name] = field_meta
    return merged


def _candidate_library_names(official_name: str) -> list[str]:
    return [official_name, *MODEL_NAME_ALIASES.get(official_name, ())]


def _find_library_type(official_name: str, catalog: LibraryCatalog) -> LibraryType | None:
    for candidate in _candidate_library_names(official_name):
        if candidate in catalog.types:
            return catalog.types[candidate]
    return None


def _strip_quotes(value: str | None) -> str | None:
    if value is None:
        return None
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
        return value[1:-1]
    return value


def _strip_optional(type_text: str) -> str:
    t = type_text.strip()
    t = re.sub(r"^Optional\[(.*)]$", r"\1", t)
    t = re.sub(r"^Required\[(.*)]$", r"\1", t)
    t = re.sub(r"^NotRequired\[(.*)]$", r"\1", t)
    t = t.replace(" | None", "").replace("None | ", "")
    if t.startswith("'") and t.endswith("'"):
        t = t[1:-1]
    if t.startswith('"') and t.endswith('"'):
        t = t[1:-1]
    return t


def _normalize_type(type_text: str) -> str:
    t = _strip_optional(type_text)
    if t.strip().lower() == "integer or decimal if available":
        return "Decimal"
    t = t.replace(" ", "")
    t = t.replace("typing.", "")
    if t in PY_PRIMITIVE_MAP:
        return PY_PRIMITIVE_MAP[t]
    list_match = re.match(r"^(?:builtins\.)?list\[(.*)]$", t)
    if list_match:
        return f"Array[{_normalize_type(list_match.group(1))}]"
    if t.startswith("dict[") or t in {"dict", "Any"}:
        return t
    if t in PY_PRIMITIVE_MAP:
        return PY_PRIMITIVE_MAP[t]
    return t


def _array_inner(type_text: str) -> str | None:
    match = re.match(r"^Array\[(.*)]$", _normalize_type(type_text))
    return match.group(1) if match else None


def _types_equivalent(expected: str, actual: str) -> bool:
    exp = _normalize_type(expected)
    act = _normalize_type(actual)
    if exp == act:
        return True
    exp_inner = _array_inner(exp)
    act_inner = _array_inner(act)
    if exp_inner is not None and act_inner is not None:
        return _types_equivalent(exp_inner, act_inner)
    if exp in DECIMAL_ALIASES and act in DECIMAL_ALIASES:
        return True
    if exp in ID_ALIASES and act == "string":
        return True
    return bool(exp == "string" and act in ID_ALIASES)


def _is_broad_type(expected: str, actual: str) -> bool:
    exp = _normalize_type(expected)
    act = _normalize_type(actual)
    if act in {"Any", "dict", "dict[str,Any]"}:
        return exp not in {"Any", "dict", "dict[str,Any]", "string", "integer", "boolean"}
    return False


def _normalize_default(value: str | None) -> str | None:
    value = _strip_quotes(value)
    if value is None:
        return None
    if value.startswith("factory:"):
        return None
    if "." in value:
        value = value.rsplit(".", 1)[-1]
    return value


def validate(official: dict[str, OfficialDefinition], library: LibraryCatalog) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []

    for name, definition in sorted(official.items()):
        if definition.fields:
            lib_type = _find_library_type(name, library)
            if lib_type is None:
                if name in ABSTRACT_OFFICIAL_MODELS or name in library.aliases:
                    continue
                issues.append(
                    ValidationIssue(
                        severity="P0",
                        code="missing_model",
                        model=name,
                        message=f"Official OANDA object `{name}` has no SDK model, TypedDict, or configured equivalent.",
                        official=_source_ref(definition.source_file, definition.source_line, definition.source_url),
                    ),
                )
                continue
            issues.extend(_validate_fields(definition, lib_type, library))

        if definition.enum_values:
            issues.extend(_validate_enum(definition, library))

        if definition.primitive:
            issues.extend(_validate_primitive(definition, library))

    return sorted(issues, key=lambda issue: (SEVERITY_ORDER[issue.severity], issue.model or "", issue.field or "", issue.code))


def _validate_fields(definition: OfficialDefinition, lib_type: LibraryType, library: LibraryCatalog) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    lib_fields = _resolve_fields(lib_type.name, library)
    official_field_names = set(definition.fields)
    library_field_names = set(lib_fields)

    for field_name, official_field in sorted(definition.fields.items()):
        library_field = lib_fields.get(field_name)
        if library_field is None:
            issues.append(
                ValidationIssue(
                    severity="P0",
                    code="missing_field",
                    model=definition.name,
                    field=field_name,
                    expected=official_field.type,
                    message=f"`{definition.name}.{field_name}` is documented by OANDA but missing from SDK `{lib_type.name}`.",
                    official=_source_ref(official_field.source_file, official_field.source_line, official_field.source_url),
                    library=_source_ref(lib_type.source_file, None),
                ),
            )
            continue

        if _is_broad_type(official_field.type, library_field.annotation):
            issues.append(
                ValidationIssue(
                    severity="P2",
                    code="broad_type",
                    model=definition.name,
                    field=field_name,
                    expected=official_field.type,
                    actual=library_field.annotation,
                    message=f"`{definition.name}.{field_name}` is typed as `{library_field.annotation}` but OANDA defines concrete type `{official_field.type}`.",
                    official=_source_ref(official_field.source_file, official_field.source_line, official_field.source_url),
                    library=_source_ref(library_field.source_file, library_field.source_line),
                ),
            )
        elif not _types_equivalent(official_field.type, library_field.annotation):
            issues.append(
                ValidationIssue(
                    severity="P2",
                    code="type_drift",
                    model=definition.name,
                    field=field_name,
                    expected=official_field.type,
                    actual=library_field.annotation,
                    message=f"`{definition.name}.{field_name}` type drift: OANDA `{official_field.type}`, SDK `{library_field.annotation}`.",
                    official=_source_ref(official_field.source_file, official_field.source_line, official_field.source_url),
                    library=_source_ref(library_field.source_file, library_field.source_line),
                ),
            )

        issues.extend(_validate_requiredness(definition, official_field, library_field))
        issues.extend(_validate_default(definition, official_field, library_field))

    for extra_name in sorted(library_field_names - official_field_names):
        extra_field = lib_fields[extra_name]
        if definition.name == "Transaction" and extra_name == "type":
            # The official base Transaction omits `type`, but every concrete
            # transaction includes a documented discriminator default.
            continue
        if extra_field.inherited_from and extra_name in {"id", "time", "userID", "accountID", "batchID", "requestID", "type"}:
            continue
        issues.append(
            ValidationIssue(
                severity="P3",
                code="extra_field",
                model=definition.name,
                field=extra_name,
                actual=extra_field.annotation,
                message=f"`{lib_type.name}.{extra_name}` exists in the SDK but is not documented on OANDA `{definition.name}`.",
                official=_source_ref(definition.source_file, definition.source_line, definition.source_url),
                library=_source_ref(extra_field.source_file, extra_field.source_line),
            ),
        )

    return issues


def _validate_requiredness(definition: OfficialDefinition, official_field: OfficialField, library_field: LibraryField) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    if official_field.required and library_field.optional and not library_field.has_default:
        issues.append(
            ValidationIssue(
                severity="P2",
                code="requiredness_drift",
                model=definition.name,
                field=official_field.name,
                expected="required",
                actual="optional",
                message=f"`{definition.name}.{official_field.name}` is required by OANDA but optional in the SDK.",
                official=_source_ref(official_field.source_file, official_field.source_line, official_field.source_url),
                library=_source_ref(library_field.source_file, library_field.source_line),
            ),
        )
    # Most OANDA definition fields omit an explicit requiredness marker, even
    # for stable response fields. Treat absence of `required` as unknown rather
    # than optional so the report does not manufacture optionality drift.
    return issues


def _validate_default(definition: OfficialDefinition, official_field: OfficialField, library_field: LibraryField) -> list[ValidationIssue]:
    expected = _normalize_default(official_field.default)
    if expected is None:
        return []
    actual = _normalize_default(library_field.default)
    if actual == expected:
        return []
    return [
        ValidationIssue(
            severity="P2",
            code="default_drift",
            model=definition.name,
            field=official_field.name,
            expected=expected,
            actual=actual,
            message=f"`{definition.name}.{official_field.name}` default drift: OANDA `{expected}`, SDK `{actual}`.",
            official=_source_ref(official_field.source_file, official_field.source_line, official_field.source_url),
            library=_source_ref(library_field.source_file, library_field.source_line),
        ),
    ]


def _validate_enum(definition: OfficialDefinition, library: LibraryCatalog) -> list[ValidationIssue]:
    enum = library.enums.get(definition.name)
    if enum is None:
        return [
            ValidationIssue(
                severity="P1",
                code="missing_enum",
                model=definition.name,
                message=f"Official OANDA enum `{definition.name}` is missing from SDK enums.",
                official=_source_ref(definition.source_file, definition.source_line, definition.source_url),
            ),
        ]
    official_values = set(definition.enum_values)
    sdk_values = set(enum["values"].values())
    issues: list[ValidationIssue] = []
    missing = sorted(official_values - sdk_values)
    extra = sorted(sdk_values - official_values)
    if missing:
        issues.append(
            ValidationIssue(
                severity="P1",
                code="missing_enum_values",
                model=definition.name,
                expected=", ".join(missing),
                message=f"SDK enum `{definition.name}` is missing OANDA values: {', '.join(missing)}.",
                official=_source_ref(definition.source_file, definition.source_line, definition.source_url),
                library=_source_ref(enum["source_file"], enum.get("line")),
            ),
        )
    if extra:
        issues.append(
            ValidationIssue(
                severity="P3",
                code="extra_enum_values",
                model=definition.name,
                actual=", ".join(extra),
                message=f"SDK enum `{definition.name}` has values not present in current OANDA docs: {', '.join(extra)}.",
                official=_source_ref(definition.source_file, definition.source_line, definition.source_url),
                library=_source_ref(enum["source_file"], enum.get("line")),
            ),
        )
    return issues


def _validate_primitive(definition: OfficialDefinition, library: LibraryCatalog) -> list[ValidationIssue]:
    if definition.name in library.aliases or definition.name in library.enums or definition.name in library.types:
        return []
    severity = "P1" if definition.name in {"AcceptDatetimeFormat", "PricingComponent", "TransactionFilter"} else "P3"
    return [
        ValidationIssue(
            severity=severity,
            code="missing_primitive",
            model=definition.name,
            expected=definition.primitive.get("Type"),
            message=f"Official OANDA primitive `{definition.name}` is not represented as an SDK alias, enum, or model.",
            official=_source_ref(definition.source_file, definition.source_line, definition.source_url),
        ),
    ]


def _waiver_audit_issues(unused_waivers: list[ParityWaiver], expired_waivers: list[ParityWaiver]) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    for waiver in expired_waivers:
        issues.append(
            ValidationIssue(
                severity="P1",
                code="expired_waiver",
                model=waiver.target,
                message=f"Parity waiver `{waiver.code}` for `{waiver.target}` expired on {waiver.expires}. Remove it or re-review the drift.",
                official=waiver.source_url,
                expected=waiver.reason,
            ),
        )
    for waiver in unused_waivers:
        issues.append(
            ValidationIssue(
                severity="P3",
                code="unused_waiver",
                model=waiver.target,
                message=f"Parity waiver `{waiver.code}` for `{waiver.target}` did not match any current issue. Remove stale waiver entries.",
                official=waiver.source_url,
                expected=waiver.reason,
            ),
        )
    return issues


def apply_waivers(issues: list[ValidationIssue], waiver_path: Path) -> tuple[list[ValidationIssue], list[WaivedIssue[ValidationIssue]]]:
    result = split_waived_issues(issues, load_waivers(waiver_path))
    active_issues = [*result.active_issues, *_waiver_audit_issues(result.unused_waivers, result.expired_waivers)]
    return sorted(active_issues, key=lambda issue: (SEVERITY_ORDER[issue.severity], issue.model or "", issue.field or "", issue.code)), result.waived_issues


def write_json(issues: list[ValidationIssue], out_path: Path, waived_issues: list[WaivedIssue[ValidationIssue]] | None = None) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "summary": _summary(issues),
        "issues": [asdict(issue) for issue in issues],
        "waived_issues": [
            {
                "issue": asdict(waived.issue),
                "waiver": asdict(waived.waiver),
            }
            for waived in (waived_issues or [])
        ],
    }
    out_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def write_markdown(issues: list[ValidationIssue], out_path: Path, waived_issues: list[WaivedIssue[ValidationIssue]] | None = None) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    waived_issues = waived_issues or []
    lines = [
        "# Field Validation Report",
        "",
        "Source of truth: official OANDA REST v20 documentation under `https://developer.oanda.com/rest-live-v20/`.",
        "",
        "Waivers are loaded from `docs_validation/config/parity-waivers.yml`. Active waivers are reported separately and are excluded from the severity summary.",
        "",
        "## Summary",
        "",
        "| Severity | Count |",
        "|---|---:|",
    ]
    summary = _summary(issues)
    for severity in ("P0", "P1", "P2", "P3"):
        lines.append(f"| {severity} | {summary.get(severity, 0)} |")
    lines.append("")
    if waived_issues:
        lines.extend(["| Waived | Count |", "|---|---:|", f"| active | {len(waived_issues)} |", ""])

    if not issues and not waived_issues:
        lines.extend(["No field-level drift detected.", ""])
        out_path.write_text("\n".join(lines), encoding="utf-8")
        return

    for severity in ("P0", "P1", "P2", "P3"):
        severity_issues = [issue for issue in issues if issue.severity == severity]
        if not severity_issues:
            continue
        lines.extend([f"## {severity}", ""])
        for issue in severity_issues:
            label = issue.model or "global"
            if issue.field:
                label = f"{label}.{issue.field}"
            lines.append(f"- `{issue.code}` `{label}`: {issue.message}")
            if issue.expected is not None or issue.actual is not None:
                lines.append(f"  - expected: `{issue.expected or ''}`; actual: `{issue.actual or ''}`")
            if issue.official:
                lines.append(f"  - official: `{issue.official}`")
            if issue.library:
                lines.append(f"  - library: `{issue.library}`")
        lines.append("")

    if waived_issues:
        lines.extend(["## Waived", ""])
        for waived in waived_issues:
            issue = waived.issue
            waiver = waived.waiver
            label = issue.model or "global"
            if issue.field:
                label = f"{label}.{issue.field}"
            lines.append(f"- `{issue.code}` `{label}`: {issue.message}")
            lines.append(f"  - waiver reason: {waiver.reason}")
            lines.append(f"  - waiver source: `{waiver.source_url}`")
            lines.append(f"  - waiver expires: `{waiver.expires}`")
        lines.append("")

    out_path.write_text("\n".join(lines), encoding="utf-8")


def _summary(issues: list[ValidationIssue]) -> dict[str, int]:
    return {severity: sum(1 for issue in issues if issue.severity == severity) for severity in SEVERITY_ORDER}


def _missing_cache_pages() -> list[str]:
    return [name for name in OFFICIAL_DEFINITION_PAGES if not (OANDA_CACHE / name).exists()]


def _refresh_cache() -> int:
    from .live_oanda_fetch import fetch_page

    failures: list[str] = []
    for page_name in OFFICIAL_DEFINITION_PAGES:
        slug = page_name.removesuffix(".md")
        try:
            fetch_page(slug, force=True)
        except Exception as exc:
            failures.append(f"{slug}: {exc}")
    if failures:
        print("Failed to refresh official OANDA definition pages:", file=sys.stderr)
        for failure in failures:
            print(f"- {failure}", file=sys.stderr)
        return 1
    return 0


def _should_fail(issues: list[ValidationIssue], fail_on: str) -> bool:
    if fail_on == "none":
        return False
    threshold = SEVERITY_ORDER[fail_on]
    return any(SEVERITY_ORDER[issue.severity] <= threshold for issue in issues)


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate SDK fields against official OANDA REST v20 definitions.")
    parser.add_argument("--refresh", action="store_true", help="Re-fetch official OANDA pages before validating.")
    parser.add_argument("--out-json", default=str(CACHE_DIR / "field-validation.json"))
    parser.add_argument("--out-md", default=str(REPORTS_DIR / "field-validation.md"))
    parser.add_argument("--waivers", default=str(DEFAULT_WAIVERS_PATH), help="YAML file containing reviewed parity waivers.")
    parser.add_argument("--fail-on", choices=("P0", "P1", "P2", "P3", "none"), default="none", help="Exit 1 if any issue at or above this severity exists.")
    args = parser.parse_args()

    if args.refresh:
        rc = _refresh_cache()
        if rc != 0:
            return rc

    missing = _missing_cache_pages()
    if missing:
        print("Missing official OANDA cache pages:", ", ".join(missing), file=sys.stderr)
        print("Run: uv run python -m docs_validation.src.parity.field_validate --refresh", file=sys.stderr)
        return 2

    official = build_official_catalog()
    library = build_library_catalog()
    issues = validate(official, library)
    issues, waived_issues = apply_waivers(issues, Path(args.waivers))

    write_json(issues, Path(args.out_json), waived_issues)
    write_markdown(issues, Path(args.out_md), waived_issues)

    summary = _summary(issues)
    print(f"wrote {Path(args.out_json).relative_to(REPO_ROOT)}")
    print(f"wrote {Path(args.out_md).relative_to(REPO_ROOT)}")
    print("field validation:", ", ".join(f"{severity}={summary[severity]}" for severity in ("P0", "P1", "P2", "P3")))
    if waived_issues:
        print(f"field validation: waived={len(waived_issues)}")

    return 1 if _should_fail(issues, args.fail_on) else 0


if __name__ == "__main__":
    sys.exit(main())
