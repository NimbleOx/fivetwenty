"""Shared AST helpers for parity extractors."""

from __future__ import annotations

import ast


def ann_to_str(node: ast.AST | None) -> str:
    """Return a stable string representation for an annotation AST node."""
    return "" if node is None else ast.unparse(node)


def value_to_str(node: ast.AST | None) -> str:
    """Return a stable string representation for a value AST node."""
    return "" if node is None else ast.unparse(node)


def base_name(node: ast.AST) -> str:
    """Return the final, unsubscripted class base name for an AST node."""
    raw = ann_to_str(node)
    if "[" in raw:
        raw = raw.split("[", 1)[0]
    if "." in raw:
        raw = raw.rsplit(".", 1)[-1]
    return raw
