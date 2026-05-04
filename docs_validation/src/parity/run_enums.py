"""Generate the cross-cutting enums parity report.

Aggregates enum value sets from all OANDA *-df pages and from
fivetwenty/models/enums.py, then emits per-enum diff tables.
"""

from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
CACHE = REPO_ROOT / "docs_validation" / ".cache" / "parity"
OANDA_CACHE = REPO_ROOT / "docs_validation" / ".cache" / "oanda"
REPORTS = REPO_ROOT / "docs_validation" / "reports"


def _collect_oanda_enums() -> dict[str, list[str]]:
    """Walk all cached OANDA pages and aggregate enums from each."""
    from .extract_oanda_md import extract_definition

    out: dict[str, list[str]] = {}
    for path in sorted(OANDA_CACHE.glob("*-df.md")):
        data = extract_definition(path)
        for name, body in data.get("definitions", {}).items():
            vals = body.get("enum_values") or []
            if vals and name not in out:
                out[name] = vals
    return out


def _collect_library_enums() -> tuple[dict[str, list[str]], dict[str, str]]:
    """Walk fivetwenty/models/enums.py for enums and primitive type aliases."""
    from .extract_pydantic import extract_module

    enums_path = REPO_ROOT / "fivetwenty" / "models" / "enums.py"
    data = extract_module(enums_path)
    enums = {name: [value.strip("\"'") for value in body.get("values", {}).values()] for name, body in data.get("enums", {}).items()}
    aliases = data.get("type_aliases", {})
    return enums, aliases


def main() -> None:
    REPORTS.mkdir(parents=True, exist_ok=True)
    oanda_enums = _collect_oanda_enums()
    lib_enums, lib_aliases = _collect_library_enums()

    parts: list[str] = ["# Enums Parity Report", ""]
    parts.append("Cross-cutting comparison of enum value sets between OANDA's REST v20 documentation and `fivetwenty/models/enums.py`.")
    parts.append("")
    parts.append("## Inventory")
    parts.append("")
    parts.append("| Side | Count |")
    parts.append("|---|---|")
    parts.append(f"| OANDA enums (across all *-df pages) | {len(oanda_enums)} |")
    parts.append(f"| Library enums (`models/enums.py`) | {len(lib_enums)} |")
    parts.append(f"| Library type aliases | {len(lib_aliases)} |")
    parts.append("")

    only_oanda = sorted(set(oanda_enums) - set(lib_enums))
    only_lib = sorted(set(lib_enums) - set(oanda_enums))
    common = sorted(set(oanda_enums) & set(lib_enums))

    parts.append("## Enums in OANDA but not in library")
    parts.append("")
    if only_oanda:
        for name in only_oanda:
            parts.append(f"- `{name}` (values: {', '.join(oanda_enums[name][:8])}{', ...' if len(oanda_enums[name]) > 8 else ''})")
    else:
        parts.append("_None._")
    parts.append("")

    parts.append("## Enums in library but not on any OANDA page (likely SDK convenience)")
    parts.append("")
    if only_lib:
        for name in only_lib:
            parts.append(f"- `{name}` (values: {', '.join(lib_enums[name][:8])}{', ...' if len(lib_enums[name]) > 8 else ''})")
    else:
        parts.append("_None._")
    parts.append("")

    parts.append("## Per-enum value-set diffs (shared)")
    parts.append("")
    drift_count = 0
    for name in common:
        l_vals = set(lib_enums[name])
        o_vals = set(oanda_enums[name])
        only_l = sorted(l_vals - o_vals)
        only_o = sorted(o_vals - l_vals)
        if only_l or only_o:
            drift_count += 1
            parts.append(f"### `{name}`")
            parts.append("")
            if only_l:
                parts.append(f"- Values in library but not OANDA: {', '.join(f'`{v}`' for v in only_l)}")
            if only_o:
                parts.append(f"- Values in OANDA but not library: {', '.join(f'`{v}`' for v in only_o)}")
            parts.append("")
    if drift_count == 0:
        parts.append("_No value-set drift on shared enums._")
        parts.append("")

    out_path = REPORTS / "enums-parity.md"
    out_path.write_text("\n".join(parts), encoding="utf-8")
    print(f"wrote {out_path.relative_to(REPO_ROOT)}: {len(common)} shared enums, {drift_count} with drift")


if __name__ == "__main__":
    main()
