"""Shared fence discovery for Markdown's Python code validators."""

import re
import shlex
from collections.abc import Iterator
from dataclasses import dataclass


@dataclass(frozen=True)
class FencedCodeBlock:
    fence_line: int
    language: str
    code: str
    closed: bool

    @property
    def is_python(self) -> bool:
        # Unlabelled fences retain the validators' existing Python convention.
        return self.language in {"python", "py", ""}


def _language(info: str) -> str:
    """Read the language separately from SuperFences options and attributes."""
    info = info.strip()
    if info.startswith("{") and info.endswith("}"):
        # With an attribute-only header, SuperFences uses the first .class as
        # the language. Quoted attribute values must not be mistaken for classes.
        try:
            attributes = shlex.split(info[1:-1])
        except ValueError:
            return info
        return next((attribute[1:].lower() for attribute in attributes if attribute.startswith(".")), "")
    return info.split(maxsplit=1)[0].removeprefix(".").lower() if info else ""


def iter_fenced_blocks(content: str) -> Iterator[FencedCodeBlock]:
    """Discover plain and indented fences, including an unfinished final block.

    Track non-Python fences too, so a Python fence shown inside a longer text
    fence is not executed. Preserve source line numbers and Python indentation
    relative to the opening fence.
    """
    lines = content.splitlines()
    opening: re.Match[str] | None = None
    start = 0
    for number, line in enumerate(lines, 1):
        if opening is None:
            opening = re.match(r"^([ \t]*)(`{3,}|~{3,})(.*)$", line)
            if opening:
                start = number
        elif re.fullmatch(r"[ \t]*" + re.escape(opening[2][0]) + "{" + str(len(opening[2])) + r",}[ \t]*", line):
            yield FencedCodeBlock(start, _language(opening[3]), "\n".join(item.removeprefix(opening[1]) for item in lines[start : number - 1]), closed=True)
            opening = None
    if opening is not None:
        yield FencedCodeBlock(start, _language(opening[3]), "\n".join(item.removeprefix(opening[1]) for item in lines[start:]), closed=False)
