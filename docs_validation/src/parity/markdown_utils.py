"""Shared markdown parsing helpers for parity tooling."""

from __future__ import annotations

import re

TABLE_SEPARATOR_RE = re.compile(r"^\|[\s\-:|]+\|$")


def split_sections(content: str, level: int) -> list[tuple[str, str]]:
    """Split markdown by heading level, returning ``[(title, body), ...]``."""
    pattern = re.compile(rf"^{'#' * level} (.+)$", re.MULTILINE)
    matches = list(pattern.finditer(content))
    sections: list[tuple[str, str]] = []
    for i, match in enumerate(matches):
        start = match.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(content)
        sections.append((match.group(1).strip(), content[start:end]))
    return sections


def parse_first_table(body: str) -> tuple[list[str], list[dict[str, str]]]:
    """Find the first markdown pipe table in ``body``."""
    lines = body.splitlines()
    for i, line in enumerate(lines):
        stripped = line.strip()
        if not (stripped.startswith("|") and stripped.endswith("|") and i + 1 < len(lines)):
            continue

        separator = lines[i + 1].strip()
        if not (separator.startswith("|") and TABLE_SEPARATOR_RE.match(separator)):
            continue

        headers = [header.strip() for header in stripped.strip("|").split("|")]
        rows: list[dict[str, str]] = []
        for body_line in lines[i + 2 :]:
            if not body_line.strip().startswith("|"):
                break
            masked = body_line.strip().strip("|").replace(r"\|", "\x00")
            cells = [cell.strip().replace("\x00", "|") for cell in masked.split("|")]
            if len(cells) == len(headers):
                rows.append(dict(zip(headers, cells, strict=True)))
        return (headers, rows)

    return ([], [])


def parse_first_table_rows(body: str) -> list[dict[str, str]]:
    """Find the first markdown pipe table in ``body`` and return only row dicts."""
    return parse_first_table(body)[1]
