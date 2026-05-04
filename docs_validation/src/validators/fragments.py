"""Shared fragment-marker parsing for documentation code-block validators."""

from __future__ import annotations

import re
from dataclasses import dataclass
from enum import Enum
from typing import Any

MARKER_LOOKBACK_LINES = 3


class FragmentTarget(str, Enum):
    """Validators that can be controlled by fragment markers."""

    EXECUTION = "execution"
    LINTING = "linting"
    PYTHON_SYNTAX = "python_syntax"
    TYPING = "typing"


@dataclass(frozen=True)
class FragmentMarker:
    """A parsed HTML fragment marker."""

    line_number: int
    text: str
    kind: str
    targets: frozenset[FragmentTarget]
    reason: str

    def skips(self, target: FragmentTarget) -> bool:
        """Return whether this marker skips the requested validator target."""
        return target in self.targets


ALL_TARGETS = frozenset(FragmentTarget)

_COMMENT_RE = re.compile(r"<!--(?P<body>.*?)-->", re.IGNORECASE)

_MARKER_PATTERNS: tuple[tuple[str, frozenset[FragmentTarget], tuple[re.Pattern[str], ...]], ...] = (
    (
        "linting",
        frozenset({FragmentTarget.LINTING}),
        (
            re.compile(r"\bvalidation\s*:\s*skip-linting\b"),
            re.compile(r"\bskip-linting\b"),
            re.compile(r"\bno-linting\b"),
            re.compile(r"\bskip-lint\b"),
            re.compile(r"\bno-lint\b"),
        ),
    ),
    (
        "typing",
        frozenset({FragmentTarget.TYPING}),
        (
            re.compile(r"\bvalidation\s*:\s*skip-typing\b"),
            re.compile(r"\bskip-typing\b"),
            re.compile(r"\bno-typing\b"),
            re.compile(r"\bskip-type\b"),
            re.compile(r"\bno-type\b"),
        ),
    ),
    (
        "python_syntax",
        frozenset({FragmentTarget.PYTHON_SYNTAX}),
        (
            re.compile(r"\bvalidation\s*:\s*skip-syntax\b"),
            re.compile(r"\bskip-syntax\b"),
            re.compile(r"\bno-syntax\b"),
        ),
    ),
    (
        "execution",
        frozenset({FragmentTarget.EXECUTION}),
        (
            re.compile(r"\bvalidation\s*:\s*skip-execution\b"),
            re.compile(r"\bskip-execution\b"),
            re.compile(r"\bno-execution\b"),
        ),
    ),
    (
        "all",
        ALL_TARGETS,
        (
            re.compile(r"\bvalidation\s*:\s*skip-all\b"),
            re.compile(r"\bvalidation\s*:\s*skip(?![-\w])"),
            re.compile(r"\bfragment\s*:"),
            re.compile(r"\bpartial\s*:"),
            re.compile(r"\bexample\s*:"),
        ),
    ),
)


def parse_fragment_marker(line: str, line_number: int) -> FragmentMarker | None:
    """Parse a single markdown line as an HTML fragment marker."""
    comment = _COMMENT_RE.search(line)
    if comment is None:
        return None

    body = comment.group("body").strip()
    normalized = body.lower()
    for kind, targets, patterns in _MARKER_PATTERNS:
        if any(pattern.search(normalized) for pattern in patterns):
            return FragmentMarker(
                line_number=line_number,
                text=f"<!-- {body} -->",
                kind=kind,
                targets=targets,
                reason=_extract_marker_reason(body, kind),
            )

    return None


def find_fragment_marker(
    lines: list[str],
    code_block_start_line: int,
    target: FragmentTarget,
    *,
    lookback_lines: int = MARKER_LOOKBACK_LINES,
) -> FragmentMarker | None:
    """Find the nearest marker that applies to a code block and validator target.

    Args:
        lines: Full markdown file content split into lines.
        code_block_start_line: 1-based line number of the opening code fence.
        target: Validator target to check.
        lookback_lines: Number of lines before the fence to inspect.

    Returns:
        The nearest applicable marker, or None.
    """
    start_line = max(1, code_block_start_line - lookback_lines)
    for line_number in range(code_block_start_line - 1, start_line - 1, -1):
        marker = parse_fragment_marker(lines[line_number - 1], line_number)
        if marker is not None and marker.skips(target):
            return marker

    return None


def marker_skip_metadata(marker: FragmentMarker, code_block_start_line: int) -> dict[str, Any]:
    """Return serializable metadata for a marker-skipped code block."""
    return {
        "code_block_start_line": code_block_start_line,
        "code_start_line": code_block_start_line + 1,
        "marker_line": marker.line_number,
        "marker": marker.text,
        "marker_kind": marker.kind,
        "reason": marker.reason,
    }


def fragment_metadata(skipped_blocks: list[dict[str, Any]]) -> dict[str, Any]:
    """Return standard ValidationResult metadata for skipped code blocks."""
    return {
        "skipped_block_count": len(skipped_blocks),
        "skipped_blocks": skipped_blocks,
    }


def _extract_marker_reason(body: str, kind: str) -> str:
    """Extract the human-authored reason from a marker body."""
    if kind == "all":
        for pattern in (r"\bfragment\s*:\s*(.*)", r"\bpartial\s*:\s*(.*)", r"\bexample\s*:\s*(.*)"):
            match = re.search(pattern, body, flags=re.IGNORECASE)
            if match:
                return match.group(1).strip() or kind

    return body.strip()
