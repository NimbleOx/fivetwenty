"""Extract endpoint and definition surface from OANDA markdown.

Live OANDA pages (cached under .cache/oanda/) use a JSON-schema-style format
inside fenced code blocks:

    TypeName is an application/json object with the following Schema:

    ```
    {
        # description
        fieldName : (Type, required, default=VALUE),
        ...
    }
    ```

The local oanda-api-reference/ snapshot uses brief markdown bullet summaries
instead. This extractor handles both shapes; the live JSON-schema parser is
the high-fidelity path used for parity diffs.

Usage:
    uv run python -m docs_validation.src.parity.extract_oanda_md \\
        --kind definition docs_validation/.cache/oanda/order-df.md
    uv run python -m docs_validation.src.parity.extract_oanda_md \\
        --kind endpoint docs_validation/.cache/oanda/order-ep.md
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[3]
CACHE_DIR = REPO_ROOT / "docs_validation" / ".cache" / "parity"

# "TypeName is an application/json object with the following Schema:"
SCHEMA_INTRO_RE = re.compile(
    r"^([A-Z][A-Za-z0-9]*)\s+is an (?:application/json|application/octet-stream)\s+(?:object|array)\s+with the following Schema:\s*$",
    re.MULTILINE,
)
# "TypeName is an Array of (Type)"
ARRAY_INTRO_RE = re.compile(
    r"^([A-Z][A-Za-z0-9]*)\s+is an Array of \(([^)]+)\)",
    re.MULTILINE,
)
# Field line: "    fieldName : (Type, required, default=X),"
FIELD_RE = re.compile(r"^\s*([A-Za-z_][A-Za-z0-9_]*)\s*:\s*\(([^)]+)\),?\s*$", re.MULTILINE)
# Code block boundaries
CODE_FENCE_RE = re.compile(r"^```", re.MULTILINE)
# Endpoint header line: "POST /v3/accounts/{accountID}/orders Description"
HTTP_LINE_RE = re.compile(r"^(POST|GET|PUT|DELETE|PATCH)\s+(/[^\s]+)\s+(.+?)\s*$", re.MULTILINE)
# Enum value table: bullets with VALUE - description
ENUM_BULLET_RE = re.compile(r"^\s*-\s+([A-Z][A-Z0-9_]+)\b", re.MULTILINE)


def _split_sections(content: str, level: int) -> list[tuple[str, str]]:
    pattern = re.compile(rf"^{'#' * level} (.+)$", re.MULTILINE)
    matches = list(pattern.finditer(content))
    sections: list[tuple[str, str]] = []
    for i, m in enumerate(matches):
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(content)
        sections.append((m.group(1).strip(), content[start:end]))
    return sections


def _parse_first_table(body: str) -> tuple[list[str], list[dict[str, str]]]:
    lines = body.splitlines()
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith("|") and stripped.endswith("|") and i + 1 < len(lines):
            sep = lines[i + 1].strip()
            if sep.startswith("|") and re.match(r"^\|[\s\-:|]+\|$", sep):
                headers = [h.strip() for h in stripped.strip("|").split("|")]
                rows: list[dict[str, str]] = []
                for body_line in lines[i + 2 :]:
                    if not body_line.strip().startswith("|"):
                        break
                    masked = body_line.strip().strip("|").replace(r"\|", "\x00")
                    cells = [c.strip().replace("\x00", "|") for c in masked.split("|")]
                    if len(cells) == len(headers):
                        rows.append(dict(zip(headers, cells, strict=True)))
                return (headers, rows)
    return ([], [])


def _parse_field_modifiers(spec: str) -> dict[str, Any]:
    """Parse "Type, required, default=X" into {type, required, default}."""
    parts = [p.strip() for p in spec.split(",")]
    type_str = parts[0]
    required = False
    default: str | None = None
    for p in parts[1:]:
        if p == "required":
            required = True
        elif p.startswith("default="):
            default = p.split("=", 1)[1].strip()
    return {"type": type_str, "required": required, "default": default}


def _extract_schema_blocks(content: str) -> dict[str, list[dict[str, Any]]]:
    """For each `TypeName is an application/json object with the following Schema:` heading,
    find the immediately-following code block and parse its fields.

    Returns: {TypeName: [{name, type, required, default}, ...]}
    """
    out: dict[str, list[dict[str, Any]]] = {}
    for intro in SCHEMA_INTRO_RE.finditer(content):
        type_name = intro.group(1)
        # Find the next code fence after this intro
        rest = content[intro.end() :]
        fence_open = CODE_FENCE_RE.search(rest)
        if not fence_open:
            continue
        after_open = rest[fence_open.end() :]
        fence_close = CODE_FENCE_RE.search(after_open)
        if not fence_close:
            continue
        code = after_open[: fence_close.start()]
        fields: list[dict[str, Any]] = []
        for fm in FIELD_RE.finditer(code):
            mod = _parse_field_modifiers(fm.group(2))
            fields.append({"name": fm.group(1), **mod})
        out[type_name] = fields
    # Also handle ArrayType:
    for arr in ARRAY_INTRO_RE.finditer(content):
        out[arr.group(1)] = [{"name": "items", "type": arr.group(2), "required": True, "default": None}]
    return out


def _extract_enums(content: str) -> dict[str, list[str]]:
    """Heuristically extract enum value lists from sections that have a TypeName followed
    by a bullet list of UPPERCASE names.

    Looks for: "TypeName ... <bullet list of UPPER_CASE values>"
    """
    out: dict[str, list[str]] = {}
    # Sections introduced as "TypeName is..." but with no schema block — likely enum.
    # Live OANDA enum sections look like:
    #   TypeName  Description
    #   - VALUE_A: desc
    #   - VALUE_B: desc
    # So look for an isolated TypeName paragraph followed by a bullet list of uppercase tokens.
    for m in re.finditer(r"^([A-Z][A-Za-z0-9]+)\b", content, re.MULTILINE):
        name = m.group(1)
        # If this name already has a schema, skip.
        rest = content[m.end() : m.end() + 800]
        if "application/json" in rest[:300]:
            continue
        bullets = ENUM_BULLET_RE.findall(rest)
        if len(bullets) >= 2:
            # Filter to bullets that are likely enum values (all-uppercase, no spaces in pattern).
            uniq = list(dict.fromkeys(bullets))
            if uniq and name not in out:
                out[name] = uniq[:50]  # cap to avoid runaway
    return out


_TYPE_INTRO_RE = re.compile(r"^([A-Z][A-Za-z0-9]+)\s+[A-Z]")


def _extract_enum_tables(content: str) -> dict[str, list[str]]:
    """Find OANDA-style enum sections: `<TypeName> ...` followed by `| Value | Description |` table.

    Stops the lookahead at the next type-intro line to prevent cross-attribution.
    """
    out: dict[str, list[str]] = {}
    lines = content.splitlines()
    for i, line in enumerate(lines):
        m = _TYPE_INTRO_RE.match(line)
        if not m:
            continue
        type_name = m.group(1)
        for j in range(i + 1, min(i + 12, len(lines))):
            # Bail if we hit another type intro before the table.
            if j != i and _TYPE_INTRO_RE.match(lines[j]):
                break
            stripped = lines[j].strip()
            if stripped.startswith("| Value |") and j + 1 < len(lines) and lines[j + 1].strip().startswith("|"):
                values: list[str] = []
                for body_line in lines[j + 2 :]:
                    if not body_line.strip().startswith("|"):
                        break
                    cells = [c.strip() for c in body_line.strip().strip("|").split("|")]
                    if cells and cells[0]:
                        values.append(cells[0])
                if values and type_name not in out:
                    out[type_name] = values
                break
    return out


def _extract_primitive_tables(content: str) -> dict[str, dict[str, str]]:
    """Find OANDA-style primitive type sections: `<TypeName> ...` followed by `| Type | string |` table."""
    out: dict[str, dict[str, str]] = {}
    lines = content.splitlines()
    for i, line in enumerate(lines):
        m = _TYPE_INTRO_RE.match(line)
        if not m:
            continue
        type_name = m.group(1)
        for j in range(i + 1, min(i + 12, len(lines))):
            if j != i and _TYPE_INTRO_RE.match(lines[j]):
                break
            stripped = lines[j].strip()
            if stripped.startswith("| Type |") and j + 1 < len(lines) and lines[j + 1].strip().startswith("|"):
                row_data: dict[str, str] = {}
                # OANDA primitive tables are 2-column row-labeled: each line is "| Label | Value |"
                # including the header line `| Type | string |`. Skip only the dashes separator.
                for body_line in lines[j:]:
                    if not body_line.strip().startswith("|"):
                        break
                    cells = [c.strip() for c in body_line.strip().strip("|").split("|")]
                    if len(cells) >= 2 and cells[0] != "---" and cells[0]:
                        row_data[cells[0]] = cells[1]
                if "Type" in row_data and type_name not in out:
                    out[type_name] = row_data
                break
    return out


def extract_definition(path: Path) -> dict[str, Any]:
    content = path.read_text(encoding="utf-8")

    # Live OANDA path
    schemas = _extract_schema_blocks(content)
    enums = _extract_enum_tables(content)
    primitives = _extract_primitive_tables(content)

    # Local snapshot fallback (### / ## sections with optional bullet lists)
    if not schemas and not enums and not primitives:
        sections = _split_sections(content, 3) or _split_sections(content, 2)
        for title, body in sections:
            name = title.strip()
            headers, rows = _parse_first_table(body)
            if headers and "Field" in headers:
                fields = [
                    {
                        "name": r.get("Field", ""),
                        "type": r.get("Type", ""),
                        "required": r.get("Required", "").lower() in {"yes", "y", "✅"},
                        "default": r.get("Default", "") or None,
                    }
                    for r in rows
                ]
                schemas[name] = fields
            else:
                vals = [m.group(1) for m in ENUM_BULLET_RE.finditer(body)]
                if vals:
                    enums[name] = vals

    out: dict[str, Any] = {
        "source_file": str(path.relative_to(REPO_ROOT)),
        "definitions": {name: {"fields": fields, "enum_values": [], "primitive": {}} for name, fields in schemas.items()},
    }
    for name, vals in enums.items():
        if name not in out["definitions"]:
            out["definitions"][name] = {"fields": [], "enum_values": vals, "primitive": {}}
        else:
            out["definitions"][name]["enum_values"] = vals
    for name, prim in primitives.items():
        if name not in out["definitions"]:
            out["definitions"][name] = {"fields": [], "enum_values": [], "primitive": prim}
        else:
            out["definitions"][name]["primitive"] = prim
    return out


def extract_endpoint(path: Path) -> dict[str, Any]:
    """Extract endpoints from a live OANDA endpoint page.

    Live OANDA endpoint pages list each operation as a block:
        POST /v3/accounts/{accountID}/orders  Description
        ... rate-limit ...
        Request Parameters table
        Request Body Schema (application/json) [code block]
        Responses... HTTP NNN ... Response Body Schema [code block]
    """
    content = path.read_text(encoding="utf-8")

    # Find endpoint blocks by HTTP_LINE_RE matches; each match starts a block,
    # which extends to the next HTTP_LINE_RE or end of file.
    matches = list(HTTP_LINE_RE.finditer(content))
    out: dict[str, Any] = {
        "source_file": str(path.relative_to(REPO_ROOT)),
        "endpoints": [],
    }

    for i, m in enumerate(matches):
        start = m.start()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(content)
        block = content[start:end]
        verb = m.group(1)
        path_template = m.group(2).rstrip(":-")
        summary = m.group(3).strip()

        # Parse Request Parameters table
        headers, rows = _parse_first_table(block)
        params: list[dict[str, Any]] = []
        if headers and ("Name" in headers or "Parameter" in headers):
            for r in rows:
                params.append(
                    {
                        "name": r.get("Name", r.get("Parameter", "")),
                        "located_in": r.get("Located In", r.get("In", "")),
                        "type": r.get("Type", ""),
                        "description": r.get("Description", ""),
                        "required": "[required]" in r.get("Description", "").lower(),
                    }
                )

        # Parse the schema blocks within this endpoint section.
        # First schema block after "Request Body Schema" → request body.
        # Schema blocks after "HTTP NNN" → response bodies, keyed by status.
        schema_blocks = _extract_schema_blocks(block)

        # Find HTTP response status codes mentioned
        statuses = re.findall(r"HTTP\s+(\d{3})", block)

        out["endpoints"].append(
            {
                "verb": verb,
                "path_template": path_template,
                "summary": summary,
                "parameters": params,
                "schemas": schema_blocks,
                "response_statuses": statuses,
            }
        )

    return out


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("paths", nargs="+")
    parser.add_argument("--kind", choices=("definition", "endpoint"), required=True)
    parser.add_argument("--out-suffix", default=None)
    args = parser.parse_args()

    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    suffix = args.out_suffix or ("-oanda-definitions.json" if args.kind == "definition" else "-oanda-endpoints.json")

    for raw in args.paths:
        path = Path(raw).resolve()
        result = extract_definition(path) if args.kind == "definition" else extract_endpoint(path)
        out_path = CACHE_DIR / f"{path.stem}{suffix}"
        out_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
        if args.kind == "definition":
            n_def = len(result["definitions"])
            n_fields = sum(len(d["fields"]) for d in result["definitions"].values())
            n_enum = sum(1 for d in result["definitions"].values() if d.get("enum_values"))
            print(f"wrote {out_path.relative_to(REPO_ROOT)}: {n_def} defs ({n_fields} fields total, {n_enum} enums)")
        else:
            print(f"wrote {out_path.relative_to(REPO_ROOT)}: {len(result['endpoints'])} endpoints")
    return 0


if __name__ == "__main__":
    sys.exit(main())
