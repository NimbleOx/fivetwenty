"""Check documentation metadata against the extracted library surface.

Two checks over the cached parity JSON:
  1. Default-value drift (P2): a doc parameter table cell saying `(default: X)`
     must match the default in the extracted method signature.
  2. Source-anchor drift (P3): a `🔗 **Source**` link carrying a `#L<n>` fragment
     must point at (or within a few lines of) the named symbol's definition.

Writes docs_validation/reports/docs-meta-parity.md and .cache/parity/docs-meta.json.

Usage:
    uv run python -m docs_validation.src.parity.check_docs_meta
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[3]
CACHE_DIR = REPO_ROOT / "docs_validation" / ".cache" / "parity"
REPORTS_DIR = REPO_ROOT / "docs_validation" / "reports"

DEFAULT_RE = re.compile(r"\(default:\s*([^)]+)\)")
ANCHOR_RE = re.compile(r"/blob/[^/]+/([^#]+)#L(\d+)")
# Decorators and blank lines between the anchor and the def/class line are tolerable.
ANCHOR_TOLERANCE = 3


def _normalize_default(raw: str) -> str:
    """Normalize `'PENDING'`, `TradeStateFilter.OPEN`, `Decimal('1.0')`, `30.0` etc. to a comparable token."""
    s = raw.strip().strip("`").strip()
    m = re.fullmatch(r"Decimal\(\s*['\"]([^'\"]+)['\"]\s*\)", s)
    if m:
        s = m.group(1)
    s = s.strip("'\"")
    if "." in s and re.fullmatch(r"[A-Za-z_][A-Za-z0-9_.]*", s):
        s = s.rsplit(".", 1)[-1]
    try:
        return repr(float(s))
    except ValueError:
        return s.lower()


def _library_methods() -> dict[str, dict[str, Any]]:
    """Flatten every `*-endpoints-library.json` into {method_name: method_record}."""
    methods: dict[str, dict[str, Any]] = {}
    for path in sorted(CACHE_DIR.glob("*-endpoints-library.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        for cls_methods in data.get("endpoint_classes", {}).values():
            methods.update(cls_methods)
    return methods


def _check_defaults() -> list[str]:
    """Compare `(default: X)` prose in doc parameter tables against extracted signature defaults."""
    findings: list[str] = []
    lib_methods = _library_methods()
    for doc_path in sorted(CACHE_DIR.glob("*-docs.json")):
        data = json.loads(doc_path.read_text(encoding="utf-8"))
        source_file = data.get("source_file", doc_path.name)
        for method_name, method in data.get("methods", {}).items():
            lib = lib_methods.get(method_name)
            if lib is None:
                continue
            lib_defaults = {p["name"]: p["default"] for group in ("positional", "keyword_only") for p in lib.get("params", {}).get(group, []) if p.get("default") is not None}
            for param in method.get("params", []):
                m = DEFAULT_RE.search(param.get("description", ""))
                if not m:
                    continue
                # "(default: 50, max: 500)" → compare only the leading token; a token with
                # internal whitespace is prose ("ALL for full closure"), not a comparable value.
                doc_raw = m.group(1).split(",")[0].strip()
                if " " in doc_raw:
                    continue
                doc_default = _normalize_default(doc_raw)
                lib_raw = lib_defaults.get(param["name"])
                if lib_raw is None:
                    findings.append(f"P2 `{source_file}` `{method_name}({param['name']})`: docs claim default `{m.group(1).strip()}` but the parameter has no default in the signature")
                    continue
                if _normalize_default(lib_raw) != doc_default:
                    findings.append(f"P2 `{source_file}` `{method_name}({param['name']})`: docs claim default `{m.group(1).strip()}` but signature default is `{lib_raw}`")
    return findings


def _find_symbol_line(file_path: Path, symbol: str) -> int | None:
    """Return the 1-based line of `def symbol(`/`class symbol` in file_path, or None."""
    try:
        lines = file_path.read_text(encoding="utf-8").splitlines()
    except OSError:
        return None
    pattern = re.compile(rf"^\s*(?:async\s+def|def|class)\s+{re.escape(symbol)}\b")
    for i, line in enumerate(lines, start=1):
        if pattern.match(line):
            return i
    return None


def _check_anchors() -> list[str]:
    """Verify `#L<n>` fragments in Source links point at the named symbol's definition."""
    findings: list[str] = []
    for doc_path in sorted(CACHE_DIR.glob("*-docs.json")):
        data = json.loads(doc_path.read_text(encoding="utf-8"))
        source_file = data.get("source_file", doc_path.name)
        sections: dict[str, dict[str, Any]] = {}
        sections.update(data.get("methods", {}))
        sections.update(data.get("models", {}))
        for name, section in sections.items():
            link = section.get("source_link", "")
            m = ANCHOR_RE.search(link)
            if not m:
                continue
            rel_path, anchor_line = m.group(1), int(m.group(2))
            target = REPO_ROOT / rel_path
            if not target.exists():
                findings.append(f"P3 `{source_file}` `{name}`: source link targets nonexistent file `{rel_path}`")
                continue
            actual = _find_symbol_line(target, name)
            if actual is None:
                findings.append(f"P3 `{source_file}` `{name}`: symbol not found in `{rel_path}` (link anchor #L{anchor_line})")
            elif abs(actual - anchor_line) > ANCHOR_TOLERANCE:
                findings.append(f"P3 `{source_file}` `{name}`: link anchor #L{anchor_line} but symbol is defined at `{rel_path}:{actual}`")
    return findings


def main() -> int:
    default_findings = _check_defaults()
    anchor_findings = _check_anchors()

    parts = ["# Docs Metadata Parity Report", "", "Generated by `docs_validation/src/parity/check_docs_meta.py`.", ""]
    parts.append(f"## Default-value drift (P2) — {len(default_findings)} finding(s)")
    parts.append("")
    if default_findings:
        parts.extend(f"- {f}" for f in default_findings)
    else:
        parts.append("_No default-value drift._")
    parts.append("")
    parts.append(f"## Source-anchor drift (P3) — {len(anchor_findings)} finding(s)")
    parts.append("")
    if anchor_findings:
        parts.extend(f"- {f}" for f in anchor_findings)
    else:
        parts.append("_No stale source anchors._")
    parts.append("")

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    out_md = REPORTS_DIR / "docs-meta-parity.md"
    out_md.write_text("\n".join(parts), encoding="utf-8")
    (CACHE_DIR / "docs-meta.json").write_text(
        json.dumps({"P2_defaults": len(default_findings), "P3_anchors": len(anchor_findings)}, indent=2),
        encoding="utf-8",
    )
    print(f"wrote {out_md.relative_to(REPO_ROOT)}: {len(default_findings)} default drift, {len(anchor_findings)} anchor drift")
    return 0


if __name__ == "__main__":
    sys.exit(main())
