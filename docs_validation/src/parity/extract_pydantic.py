"""Extract Pydantic model surface from fivetwenty/models/*.py.

Emits JSON of: {model_name: {field_name: {alias, annotation, default, optional, source_line}}}.
Also captures Enum classes and their values, and TypedDict classes.

Usage:
    uv run python -m docs_validation.src.parity.extract_pydantic <module_path> [<module_path> ...]
    uv run python -m docs_validation.src.parity.extract_pydantic --all  # all models + enums

Output is written to docs_validation/.cache/parity/<stem>-library.json (one per source).
"""

from __future__ import annotations

import argparse
import ast
import json
import sys
from pathlib import Path
from typing import Any

from .ast_utils import ann_to_str, base_name, value_to_str

REPO_ROOT = Path(__file__).resolve().parents[3]
MODELS_DIR = REPO_ROOT / "fivetwenty" / "models"
CACHE_DIR = REPO_ROOT / "docs_validation" / ".cache" / "parity"


def _parse_field_default(default_node: ast.AST | None) -> tuple[str | None, str | None, bool]:
    """Return (alias, default_repr, is_optional_via_field_default).

    Handles patterns like:
        Field(alias="foo", default=None)
        Field(alias="foo", default_factory=list)
        Field(None, alias="foo")
        Field(default=Foo.BAR, alias="foo")
    """
    if default_node is None:
        return (None, None, False)

    alias: str | None = None
    default_repr: str | None = None
    is_optional = False

    if isinstance(default_node, ast.Call) and isinstance(default_node.func, ast.Name) and default_node.func.id == "Field":
        # First positional arg, if any, is the default
        if default_node.args:
            default_repr = value_to_str(default_node.args[0])
            if default_repr == "None":
                is_optional = True
        for kw in default_node.keywords:
            if kw.arg == "alias":
                alias = value_to_str(kw.value).strip("\"'")
            elif kw.arg == "default":
                default_repr = value_to_str(kw.value)
                if default_repr == "None":
                    is_optional = True
            elif kw.arg == "default_factory":
                default_repr = f"factory:{value_to_str(kw.value)}"
        return (alias, default_repr, is_optional)

    default_repr = value_to_str(default_node)
    if default_repr == "None":
        is_optional = True
    return (None, default_repr, is_optional)


def _is_optional_annotation(ann: str) -> bool:
    """Heuristic: True if annotation is `X | None` / `Optional[X]` / `None`."""
    if not ann:
        return False
    a = ann.replace(" ", "")
    return "|None" in a or a.startswith("Optional[") or a == "None"


def _is_pydantic_model(node: ast.ClassDef, *, known_models: set[str] | None = None) -> bool:
    """Detect Pydantic-derived classes.

    A class is Pydantic-derived if it (transitively) inherits from ApiModel/BaseModel.
    `known_models` is the set of already-recognized Pydantic class names in this module,
    used to follow inheritance within the file.
    """
    known_models = known_models or set()
    for base in node.bases:
        base_str = ann_to_str(base)
        if base_str in {"ApiModel", "BaseModel"}:
            return True
        if base_str.endswith("ApiModel") or base_str.endswith("BaseModel"):
            return True
        if base_str in known_models:
            return True
    return False


def _is_enum(node: ast.ClassDef) -> bool:
    for base in node.bases:
        base_str = ann_to_str(base)
        if base_str in {"Enum", "str", "IntEnum", "StrEnum"}:
            continue
        if base_str.endswith("Enum"):
            return True
    # str+Enum pattern: class X(str, Enum)
    base_strs = {ann_to_str(b) for b in node.bases}
    return "Enum" in base_strs or "IntEnum" in base_strs or "StrEnum" in base_strs


def _is_typeddict(node: ast.ClassDef) -> bool:
    for base in node.bases:
        if ann_to_str(base) == "TypedDict":
            return True
    return False


def extract_module(path: Path) -> dict[str, Any]:
    source = path.read_text(encoding="utf-8")
    tree = ast.parse(source)
    out: dict[str, Any] = {
        "source_file": str(path.relative_to(REPO_ROOT)),
        "models": {},
        "model_bases": {},
        "enums": {},
        "typeddicts": {},
        "typeddict_bases": {},
        "type_aliases": {},
        "exports": [],
    }

    # Pre-compute the set of Pydantic-derived class names by fixed-point iteration.
    class_defs = [n for n in tree.body if isinstance(n, ast.ClassDef)]
    pydantic_classes: set[str] = set()
    while True:
        added = False
        for node in class_defs:
            if node.name in pydantic_classes:
                continue
            if _is_typeddict(node) or _is_enum(node):
                continue
            if _is_pydantic_model(node, known_models=pydantic_classes):
                pydantic_classes.add(node.name)
                added = True
        if not added:
            break

    for item in tree.body:
        if isinstance(item, ast.ClassDef):
            if _is_typeddict(item):
                out["typeddicts"][item.name] = _extract_class_fields(item)
                out["typeddict_bases"][item.name] = [base_name(b) for b in item.bases]
            elif _is_enum(item):
                out["enums"][item.name] = _extract_enum_values(item)
            elif item.name in pydantic_classes:
                out["models"][item.name] = _extract_class_fields(item)
                out["model_bases"][item.name] = [base_name(b) for b in item.bases]
        elif isinstance(item, ast.Assign):
            # Module-level assignments: __all__ exports + simple type aliases
            for target in item.targets:
                if isinstance(target, ast.Name):
                    if target.id == "__all__" and isinstance(item.value, (ast.List, ast.Tuple)):
                        out["exports"] = [elt.value for elt in item.value.elts if isinstance(elt, ast.Constant)]
                    else:
                        # Simple type alias e.g. `OrderID = str`
                        out["type_aliases"][target.id] = value_to_str(item.value)
        elif isinstance(item, ast.AnnAssign) and isinstance(item.target, ast.Name):
            # Module-level annotated alias e.g. `OrderID: TypeAlias = str`
            out["type_aliases"][item.target.id] = ann_to_str(item.annotation) or ""

    return out


def _extract_class_fields(node: ast.ClassDef) -> dict[str, Any]:
    fields: dict[str, Any] = {}
    for item in node.body:
        if isinstance(item, ast.AnnAssign) and isinstance(item.target, ast.Name):
            field_name = item.target.id
            ann = ann_to_str(item.annotation)
            alias, default_repr, default_is_none = _parse_field_default(item.value)
            optional = _is_optional_annotation(ann) or default_is_none or default_repr is not None
            # If a default exists but isn't None, the field is "optional in construction"
            # but might still be "required by API spec" — record both signals.
            fields[field_name] = {
                "alias": alias,
                "annotation": ann,
                "default": default_repr,
                "optional": optional,
                "has_default": default_repr is not None,
                "line": item.lineno,
            }
    return fields


def _extract_enum_values(node: ast.ClassDef) -> dict[str, Any]:
    values: dict[str, str] = {}
    for item in node.body:
        if isinstance(item, ast.Assign):
            for target in item.targets:
                if isinstance(target, ast.Name):
                    values[target.id] = value_to_str(item.value)
        elif isinstance(item, ast.AnnAssign) and isinstance(item.target, ast.Name):
            values[item.target.id] = value_to_str(item.value) if item.value else ""
    return {"values": values, "line": node.lineno}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("modules", nargs="*", help="Module paths (e.g. fivetwenty/models/orders.py)")
    parser.add_argument("--all", action="store_true", help="Process all modules under fivetwenty/models/")
    args = parser.parse_args()

    CACHE_DIR.mkdir(parents=True, exist_ok=True)

    paths: list[Path] = []
    if args.all:
        paths = [p for p in MODELS_DIR.glob("*.py") if p.name != "__init__.py"]
    else:
        paths = [Path(p).resolve() for p in args.modules]

    if not paths:
        parser.print_help()
        return 1

    for path in paths:
        result = extract_module(path)
        out_path = CACHE_DIR / f"{path.stem}-library.json"
        out_path.write_text(json.dumps(result, indent=2, sort_keys=False), encoding="utf-8")
        print(f"wrote {out_path.relative_to(REPO_ROOT)}: {len(result['models'])} models, {len(result['enums'])} enums, {len(result['typeddicts'])} typeddicts, {len(result['type_aliases'])} aliases")

    return 0


if __name__ == "__main__":
    sys.exit(main())
