"""Compute parity diffs between extracted JSON surfaces and emit markdown tables.

Three diff modes:
  - models   : compare two model-shape JSONs (library vs OANDA, library vs docs).
               Inputs: pydantic-extractor output, oanda-md definitions, doc-tables models.
  - methods  : compare endpoint-method JSONs (library endpoints vs doc endpoints).
  - enums    : compare enum value sets.

Each mode emits four tables: missing, extra, type-drift, optionality-drift.

Usage:
    uv run python -m docs_validation.src.parity.diff models \
        --left docs_validation/.cache/parity/orders-library.json \
        --right docs_validation/.cache/parity/order-models-docs.json \
        --left-source library --right-source docs \
        --out docs_validation/.cache/parity/orders-library-vs-docs-models.md

Diffs are intentionally simple — name-only matching with a few normalizations:
  - snake_case (library) ↔ camelCase (OANDA)
  - alias (library) ↔ field name (OANDA/docs)
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[3]


def _camel_to_snake(name: str) -> str:
    s1 = re.sub(r"(.)([A-Z][a-z]+)", r"\1_\2", name)
    return re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", s1).lower()


def _snake_to_camel(name: str) -> str:
    parts = name.split("_")
    if not parts:
        return name
    return parts[0] + "".join(p.title() for p in parts[1:])


# OANDA convention preserves these as uppercase suffix in camelCase identifiers.
_UPPERCASE_SUFFIXES = {"id", "ids", "url", "uri", "ip", "api"}


def _snake_to_oanda(name: str) -> str:
    """Convert snake_case to OANDA-style camelCase (e.g. trade_id → tradeID)."""
    parts = name.split("_")
    if not parts:
        return name
    out = [parts[0]]
    for p in parts[1:]:
        out.append(p.upper() if p in _UPPERCASE_SUFFIXES else p.title())
    return "".join(out)


# Type-equivalence groups: members are interchangeable for parity purposes.
_TYPE_ALIAS_GROUPS = [
    {"datetime", "DateTime"},
    {"PriceValue", "Decimal", "str"},
    {"OrderID", "TransactionID", "TradeID", "AccountID", "InstrumentName", "ClientID", "ClientOrderID", "ClientTradeID", "RequestID", "OrderSpecifier", "TradeSpecifier", "str"},
    {"DecimalNumber", "Decimal", "str"},
    {"AccountUnits", "Decimal", "str"},
]


def _canonical_type(t: str) -> str:
    """Map a type to its canonical alias-group representative if applicable."""
    for grp in _TYPE_ALIAS_GROUPS:
        if t in grp:
            return next(iter(sorted(grp)))
    return t


def _norm_type(t: str, *, strip_optional: bool = True) -> str:
    """Normalize type strings for loose comparison.

    - Unwrap markdown links `[text](url)` → text.
    - Strip whitespace.
    - Strip `| None` and `Optional[...]` wrapper (optionality compared separately).
    - Map to canonical alias group (datetime ↔ DateTime, etc.).
    """
    t = t.strip()
    t = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", t)
    t = t.replace(" ", "")
    if strip_optional:
        # Strip outer `| None` / `Optional[...]`
        if t.endswith("|None"):
            t = t[: -len("|None")]
        elif t.startswith("None|"):
            t = t[len("None|") :]
        m = re.match(r"^Optional\[(.+)\]$", t)
        if m:
            t = m.group(1)
    return _canonical_type(t)


def _shape_library(data: dict[str, Any], *, key_mode: str = "snake") -> dict[str, dict[str, dict[str, Any]]]:
    """Normalize library JSON to {model: {field_key: {...}}}.

    key_mode: 'snake' uses Python attribute name; 'oanda' uses alias (or OANDA-cased fallback).
    """
    out: dict[str, dict[str, dict[str, Any]]] = {}
    for name, fields in data.get("models", {}).items():
        norm: dict[str, dict[str, Any]] = {}
        for fname, meta in fields.items():
            alias = meta.get("alias")
            key = fname if key_mode == "snake" else (alias or _snake_to_oanda(fname))
            norm[key] = {
                "library_name": fname,
                "alias": alias,
                "type": meta.get("annotation", ""),
                "optional": bool(meta.get("optional")),
                "default": meta.get("default"),
            }
        out[name] = norm
    return out


def _shape_oanda(data: dict[str, Any]) -> dict[str, dict[str, dict[str, Any]]]:
    out: dict[str, dict[str, dict[str, Any]]] = {}
    for name, body in data.get("definitions", {}).items():
        norm: dict[str, dict[str, Any]] = {}
        for f in body.get("fields", []):
            key = f["name"]
            norm[key] = {
                "type": f.get("type", ""),
                "optional": not f.get("required", False),
                "default": f.get("default", ""),
            }
        out[name] = norm
    return out


def _shape_docs(data: dict[str, Any]) -> dict[str, dict[str, dict[str, Any]]]:
    """Project docs use snake_case field names — keep them as-is."""
    out: dict[str, dict[str, dict[str, Any]]] = {}
    for name, body in data.get("models", {}).items():
        norm: dict[str, dict[str, Any]] = {}
        for f in body.get("fields", []):
            fname = f["name"]
            norm[fname] = {
                "doc_name": fname,
                "type": f.get("type", ""),
                "optional": not f.get("required", False),
            }
        out[name] = norm
    return out


def _shape_endpoints_library(data: dict[str, Any]) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    for cls_name, methods in data.get("endpoint_classes", {}).items():
        for m_name, meta in methods.items():
            calls = meta.get("request_calls", [])
            verb_path = ""
            if calls:
                verb_path = f"{calls[0]['verb']} {calls[0]['path_template']}"
            params = []
            params.extend(meta.get("params", {}).get("positional", []))
            params.extend(meta.get("params", {}).get("keyword_only", []))
            out[m_name] = {
                "class": cls_name,
                "verb_path": verb_path,
                "param_names": [p["name"] for p in params],
                "param_types": {p["name"]: p["annotation"] for p in params},
                "return": meta.get("return_annotation", ""),
                "line": meta.get("line"),
            }
    return out


def _shape_endpoints_docs(data: dict[str, Any]) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    for m_name, meta in data.get("methods", {}).items():
        params = meta.get("params", [])
        out[m_name] = {
            "verb_path": f"{meta.get('http_method', '')} {meta.get('url_template', '')}".strip(),
            "param_names": [p["name"] for p in params],
            "param_types": {p["name"]: p["type"] for p in params},
            "source_link": meta.get("source_link", ""),
            "oanda_link": meta.get("oanda_link", ""),
        }
    return out


# ---------- Diffing -------------------------------------------------------


def _diff_field_set(
    left: dict[str, dict[str, Any]],
    right: dict[str, dict[str, Any]],
    left_label: str,
    right_label: str,
) -> dict[str, list[dict[str, Any]]]:
    missing: list[dict[str, Any]] = []  # in left, not in right
    extra: list[dict[str, Any]] = []  # in right, not in left
    type_drift: list[dict[str, Any]] = []
    opt_drift: list[dict[str, Any]] = []

    for k, lv in left.items():
        rv = right.get(k)
        if rv is None:
            missing.append({"name": k, **lv})
            continue
        lt = _norm_type(lv.get("type", ""))
        rt = _norm_type(rv.get("type", ""))
        if lt and rt and lt != rt:
            type_drift.append({"name": k, f"{left_label}_type": lv.get("type"), f"{right_label}_type": rv.get("type")})
        if "optional" in lv and "optional" in rv and lv["optional"] != rv["optional"]:
            opt_drift.append({"name": k, f"{left_label}_optional": lv["optional"], f"{right_label}_optional": rv["optional"]})

    for k, rv in right.items():
        if k not in left:
            extra.append({"name": k, **rv})

    return {"missing": missing, "extra": extra, "type_drift": type_drift, "opt_drift": opt_drift}


def diff_models(left: dict[str, dict[str, dict[str, Any]]], right: dict[str, dict[str, dict[str, Any]]], left_label: str, right_label: str) -> dict[str, Any]:
    """Diff two model surfaces."""
    out: dict[str, Any] = {
        "models_missing_in_right": sorted(set(left.keys()) - set(right.keys())),
        "models_extra_in_right": sorted(set(right.keys()) - set(left.keys())),
        "per_model": {},
    }
    for model in sorted(set(left.keys()) & set(right.keys())):
        out["per_model"][model] = _diff_field_set(left[model], right[model], left_label, right_label)
    return out


def diff_endpoints(left: dict[str, dict[str, Any]], right: dict[str, dict[str, Any]], left_label: str, right_label: str) -> dict[str, Any]:
    out: dict[str, Any] = {
        "methods_missing_in_right": sorted(set(left.keys()) - set(right.keys())),
        "methods_extra_in_right": sorted(set(right.keys()) - set(left.keys())),
        "per_method": {},
    }
    for m in sorted(set(left.keys()) & set(right.keys())):
        lv = left[m]
        rv = right[m]
        per: dict[str, Any] = {}
        if lv.get("verb_path") and rv.get("verb_path") and lv["verb_path"] != rv["verb_path"]:
            per["verb_path_drift"] = {f"{left_label}": lv["verb_path"], f"{right_label}": rv["verb_path"]}
        l_params = set(lv.get("param_names", []))
        r_params = set(rv.get("param_names", []))
        only_left = sorted(l_params - r_params)
        only_right = sorted(r_params - l_params)
        if only_left:
            per[f"params_only_in_{left_label}"] = only_left
        if only_right:
            per[f"params_only_in_{right_label}"] = only_right
        type_drift: list[dict[str, str]] = []
        for p in sorted(l_params & r_params):
            lt = _norm_type(lv["param_types"].get(p, ""))
            rt = _norm_type(rv["param_types"].get(p, ""))
            if lt and rt and lt != rt:
                type_drift.append({"param": p, f"{left_label}_type": lv["param_types"][p], f"{right_label}_type": rv["param_types"][p]})
        if type_drift:
            per["param_type_drift"] = type_drift
        if per:
            out["per_method"][m] = per
    return out


# ---------- Markdown rendering -------------------------------------------


def _render_models_md(diff: dict[str, Any], left_label: str, right_label: str, title: str) -> str:
    lines: list[str] = [f"# {title}", ""]

    if diff["models_missing_in_right"]:
        lines.append(f"## Models present in {left_label} but missing in {right_label}")
        lines.append("")
        for m in diff["models_missing_in_right"]:
            lines.append(f"- `{m}`")
        lines.append("")

    if diff["models_extra_in_right"]:
        lines.append(f"## Models present in {right_label} but missing in {left_label}")
        lines.append("")
        for m in diff["models_extra_in_right"]:
            lines.append(f"- `{m}`")
        lines.append("")

    lines.append("## Field-level drift (per model)")
    lines.append("")

    for model, fdiff in diff["per_model"].items():
        if not (fdiff["missing"] or fdiff["extra"] or fdiff["type_drift"] or fdiff["opt_drift"]):
            continue
        lines.append(f"### {model}")
        lines.append("")
        if fdiff["missing"]:
            lines.append(f"**Fields in {left_label} but missing in {right_label}:**")
            lines.append("")
            lines.append(f"| Field | Type ({left_label}) | Optional |")
            lines.append("|---|---|---|")
            for f in fdiff["missing"]:
                lines.append(f"| `{f['name']}` | `{f.get('type', '')}` | {f.get('optional', '')} |")
            lines.append("")
        if fdiff["extra"]:
            lines.append(f"**Fields in {right_label} but missing in {left_label}:**")
            lines.append("")
            lines.append(f"| Field | Type ({right_label}) | Optional |")
            lines.append("|---|---|---|")
            for f in fdiff["extra"]:
                lines.append(f"| `{f['name']}` | `{f.get('type', '')}` | {f.get('optional', '')} |")
            lines.append("")
        if fdiff["type_drift"]:
            lines.append("**Type drift:**")
            lines.append("")
            lines.append(f"| Field | {left_label} | {right_label} |")
            lines.append("|---|---|---|")
            for f in fdiff["type_drift"]:
                lines.append(f"| `{f['name']}` | `{f.get(f'{left_label}_type', '')}` | `{f.get(f'{right_label}_type', '')}` |")
            lines.append("")
        if fdiff["opt_drift"]:
            lines.append("**Optionality drift:**")
            lines.append("")
            lines.append(f"| Field | {left_label} optional | {right_label} optional |")
            lines.append("|---|---|---|")
            for f in fdiff["opt_drift"]:
                lines.append(f"| `{f['name']}` | {f.get(f'{left_label}_optional', '')} | {f.get(f'{right_label}_optional', '')} |")
            lines.append("")

    if all(not (d["missing"] or d["extra"] or d["type_drift"] or d["opt_drift"]) for d in diff["per_model"].values()):
        lines.append("_No field-level drift on shared models._")
        lines.append("")

    return "\n".join(lines)


def _render_endpoints_md(diff: dict[str, Any], left_label: str, right_label: str, title: str) -> str:
    lines = [f"# {title}", ""]

    if diff["methods_missing_in_right"]:
        lines.append(f"## Methods in {left_label} but missing in {right_label}")
        lines.append("")
        for m in diff["methods_missing_in_right"]:
            lines.append(f"- `{m}`")
        lines.append("")

    if diff["methods_extra_in_right"]:
        lines.append(f"## Methods in {right_label} but missing in {left_label}")
        lines.append("")
        for m in diff["methods_extra_in_right"]:
            lines.append(f"- `{m}`")
        lines.append("")

    lines.append("## Per-method drift")
    lines.append("")

    if not diff["per_method"]:
        lines.append("_No per-method drift on shared methods._")
        return "\n".join(lines)

    for m, per in diff["per_method"].items():
        lines.append(f"### `{m}`")
        lines.append("")
        if "verb_path_drift" in per:
            d = per["verb_path_drift"]
            lines.append(f"- **Verb/path drift:** {left_label}=`{d.get(left_label, '')}`, {right_label}=`{d.get(right_label, '')}`")
        if f"params_only_in_{left_label}" in per:
            lines.append(f"- **Params only in {left_label}:** {', '.join(f'`{p}`' for p in per[f'params_only_in_{left_label}'])}")
        if f"params_only_in_{right_label}" in per:
            lines.append(f"- **Params only in {right_label}:** {', '.join(f'`{p}`' for p in per[f'params_only_in_{right_label}'])}")
        if "param_type_drift" in per:
            lines.append("- **Param type drift:**")
            for d in per["param_type_drift"]:
                lines.append(f"  - `{d['param']}`: {left_label}=`{d.get(f'{left_label}_type', '')}`, {right_label}=`{d.get(f'{right_label}_type', '')}`")
        lines.append("")

    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=("models", "endpoints", "enums"))
    parser.add_argument("--left", required=True, help="Left JSON file")
    parser.add_argument("--right", required=True, help="Right JSON file")
    parser.add_argument("--left-source", required=True, choices=("library", "oanda", "docs"))
    parser.add_argument("--right-source", required=True, choices=("library", "oanda", "docs"))
    parser.add_argument("--left-label", default=None)
    parser.add_argument("--right-label", default=None)
    parser.add_argument("--out", required=True)
    parser.add_argument("--title", default="Parity Diff")
    args = parser.parse_args()

    left = json.loads(Path(args.left).read_text())
    right = json.loads(Path(args.right).read_text())
    left_label = args.left_label or args.left_source
    right_label = args.right_label or args.right_source

    if args.mode == "models":
        # Pick library key_mode based on what it's being compared against:
        # - vs docs (snake_case in markdown): key on snake
        # - vs OANDA (camelCase in spec): key on alias/OANDA-cased
        if args.left_source == "library":
            ldata = _shape_library(left, key_mode="snake" if args.right_source == "docs" else "oanda")
        elif args.left_source == "oanda":
            ldata = _shape_oanda(left)
        else:
            ldata = _shape_docs(left)
        if args.right_source == "library":
            rdata = _shape_library(right, key_mode="snake" if args.left_source == "docs" else "oanda")
        elif args.right_source == "oanda":
            rdata = _shape_oanda(right)
        else:
            rdata = _shape_docs(right)
        result = diff_models(ldata, rdata, left_label, right_label)
        md = _render_models_md(result, left_label, right_label, args.title)
    elif args.mode == "endpoints":
        ep_shape = {"library": _shape_endpoints_library, "docs": _shape_endpoints_docs}
        if args.left_source not in ep_shape or args.right_source not in ep_shape:
            print("endpoints diff supports library/docs only", file=sys.stderr)
            return 2
        ldata2 = ep_shape[args.left_source](left)
        rdata2 = ep_shape[args.right_source](right)
        result = diff_endpoints(ldata2, rdata2, left_label, right_label)
        md = _render_endpoints_md(result, left_label, right_label, args.title)
    else:
        # enums: compare enum value sets across two source files (library extract)
        l_enums = left.get("enums", {})
        r_enums = right.get("enums", {})
        out_lines = [f"# {args.title}", ""]
        for ename in sorted(set(l_enums) | set(r_enums)):
            lvals = set(l_enums.get(ename, {}).get("values", {}).keys())
            rvals = set(r_enums.get(ename, {}).get("values", {}).keys())
            only_left = sorted(lvals - rvals)
            only_right = sorted(rvals - lvals)
            if only_left or only_right or ename not in r_enums or ename not in l_enums:
                out_lines.append(f"### {ename}")
                if ename not in r_enums:
                    out_lines.append(f"- Missing in {right_label}")
                elif ename not in l_enums:
                    out_lines.append(f"- Missing in {left_label}")
                if only_left:
                    out_lines.append(f"- Values only in {left_label}: {', '.join(only_left)}")
                if only_right:
                    out_lines.append(f"- Values only in {right_label}: {', '.join(only_right)}")
                out_lines.append("")
        md = "\n".join(out_lines)

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(md, encoding="utf-8")
    # Also save raw JSON diff alongside
    out_path.with_suffix(".json").write_text(json.dumps(result, indent=2) if args.mode != "enums" else "{}", encoding="utf-8")
    print(f"wrote {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
