"""Extract documented method/model surface from docs/api-reference/**/*.md.

Strategy:
- For endpoint docs (docs/api-reference/endpoints/*.md): split on `## ` headings;
  each section is a method. Within a section, find the `**Parameters:**` table
  and the `**OANDA Endpoint**:` line.
- For model docs (docs/api-reference/models/*.md): split on `### ` headings;
  each section is a model. The first markdown table after the heading is the
  field table.
- Capture: source links (🔗), OANDA definition links, and any code-block
  anchors (`<!-- code-block: ... -->`).

Emits one JSON file per source markdown file in docs_validation/.cache/parity/.

Usage:
    uv run python -m docs_validation.src.parity.extract_doc_tables docs/api-reference/endpoints/orders.md
    uv run python -m docs_validation.src.parity.extract_doc_tables --all
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[3]
ENDPOINTS_DOCS = REPO_ROOT / "docs" / "api-reference" / "endpoints"
MODELS_DOCS = REPO_ROOT / "docs" / "api-reference" / "models"
CACHE_DIR = REPO_ROOT / "docs_validation" / ".cache" / "parity"

SOURCE_LINK_RE = re.compile(r"🔗 \*\*Source\*\*:\s*\[([^\]]+)\]\(([^)]+)\)")
OANDA_LINK_RE = re.compile(r"🔗 \*\*OANDA (?:Documentation|Definition)\*\*:\s*\[([^\]]+)\]\(([^)]+)\)")
ENDPOINT_LINE_RE = re.compile(r"^\*\*OANDA Endpoint\*\*:\s*`([A-Z]+)\s+(.+)`", re.MULTILINE)
CODEBLOCK_ANCHOR_RE = re.compile(r"<!--\s*code-block:\s*([^\s]+)\s*-->")


def _split_sections(content: str, level: int) -> list[tuple[str, str]]:
    """Split markdown by header level, return [(title, body), ...]."""
    pattern = re.compile(rf"^{'#' * level} (.+)$", re.MULTILINE)
    matches = list(pattern.finditer(content))
    sections: list[tuple[str, str]] = []
    for i, m in enumerate(matches):
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(content)
        sections.append((m.group(1).strip(), content[start:end]))
    return sections


def _parse_first_table(body: str) -> list[dict[str, str]]:
    """Find the first markdown pipe-table in body, return list of row dicts.

    Assumes header row + alignment row + body rows.
    """
    lines = body.splitlines()
    # Find a header row that looks like `| ... | ... |`
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith("|") and stripped.endswith("|") and i + 1 < len(lines):
            sep = lines[i + 1].strip()
            if sep.startswith("|") and re.match(r"^\|[\s\-:|]+\|$", sep):
                # Found a table
                headers = [h.strip() for h in stripped.strip("|").split("|")]
                rows: list[dict[str, str]] = []
                for body_line in lines[i + 2 :]:
                    if not body_line.strip().startswith("|"):
                        break
                    # Mask escaped pipes so we don't split on them, then restore.
                    masked = body_line.strip().strip("|").replace(r"\|", "\x00")
                    cells = [c.strip().replace("\x00", "|") for c in masked.split("|")]
                    if len(cells) == len(headers):
                        rows.append(dict(zip(headers, cells, strict=True)))
                return rows
    return []


def _strip_md_link(s: str) -> str:
    """Replace `[text](url)` with `text`."""
    return re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", s)


def extract_endpoint_doc(path: Path) -> dict[str, Any]:
    content = path.read_text(encoding="utf-8")
    sections = _split_sections(content, 2)
    out: dict[str, Any] = {
        "source_file": str(path.relative_to(REPO_ROOT)),
        "methods": {},
    }
    for title, body in sections:
        # Skip non-method sections (e.g. intro).
        if title.startswith(("post_", "get_", "put_", "delete_", "patch_", "stream_", "cancel_", "close_")) or "_" in title:
            method_name = title.strip()
            ep_match = ENDPOINT_LINE_RE.search(body)
            param_table = _parse_first_table(body)
            params: list[dict[str, str]] = []
            for row in param_table:
                pname_raw = row.get("Parameter", "").strip("`* ")
                if pname_raw == "*" or not pname_raw:
                    continue
                params.append(
                    {
                        "name": pname_raw,
                        "type": _strip_md_link(row.get("Type", "")),
                        "required": "✅" in row.get("Required", ""),
                        "description": row.get("Description", ""),
                    }
                )
            source_link = SOURCE_LINK_RE.search(body)
            oanda_link = OANDA_LINK_RE.search(body)
            code_anchor = CODEBLOCK_ANCHOR_RE.search(body)
            out["methods"][method_name] = {
                "http_method": ep_match.group(1) if ep_match else "",
                "url_template": ep_match.group(2).strip() if ep_match else "",
                "params": params,
                "source_link": source_link.group(2) if source_link else "",
                "oanda_link": oanda_link.group(2) if oanda_link else "",
                "code_block_anchor": code_anchor.group(1) if code_anchor else "",
            }
    return out


def extract_model_doc(path: Path) -> dict[str, Any]:
    content = path.read_text(encoding="utf-8")
    out: dict[str, Any] = {
        "source_file": str(path.relative_to(REPO_ROOT)),
        "models": {},
    }
    for title, body in _split_sections(content, 3):
        model_name = title.strip()
        field_table = _parse_first_table(body)
        fields: list[dict[str, Any]] = []
        for row in field_table:
            fname = row.get("Field", "").strip("`* ")
            if not fname:
                continue
            fields.append(
                {
                    "name": fname,
                    "type": _strip_md_link(row.get("Type", "")),
                    "required": "✅" in row.get("Required", ""),
                    "description": row.get("Description", ""),
                }
            )
        source_link = SOURCE_LINK_RE.search(body)
        oanda_link = OANDA_LINK_RE.search(body)
        out["models"][model_name] = {
            "fields": fields,
            "source_link": source_link.group(2) if source_link else "",
            "oanda_link": oanda_link.group(2) if oanda_link else "",
        }
    return out


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("paths", nargs="*")
    parser.add_argument("--all", action="store_true")
    args = parser.parse_args()

    CACHE_DIR.mkdir(parents=True, exist_ok=True)

    paths: list[Path] = []
    if args.all:
        paths = [p for p in ENDPOINTS_DOCS.glob("*.md") if p.name != "index.md"]
        paths.extend(p for p in MODELS_DOCS.glob("*.md") if p.name != "index.md")
    else:
        paths = [Path(p).resolve() for p in args.paths]

    if not paths:
        parser.print_help()
        return 1

    for path in paths:
        is_model_doc = "models" in path.parts
        result = extract_model_doc(path) if is_model_doc else extract_endpoint_doc(path)
        out_path = CACHE_DIR / f"{path.stem}-docs.json"
        out_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
        if is_model_doc:
            print(f"wrote {out_path.relative_to(REPO_ROOT)}: {len(result['models'])} models")
        else:
            print(f"wrote {out_path.relative_to(REPO_ROOT)}: {len(result['methods'])} methods")

    return 0


if __name__ == "__main__":
    sys.exit(main())
