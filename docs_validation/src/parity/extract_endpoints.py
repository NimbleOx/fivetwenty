"""Extract endpoint method surface from fivetwenty/endpoints/*.py.

For each method on a *Endpoints class, extract:
  - method name, async flag, source line
  - signature: positional + keyword-only params (name, annotation, default)
  - return annotation
  - resolved (HTTP method, URL template) by walking `await self._client._request(...)` calls

Usage:
    uv run python -m docs_validation.src.parity.extract_endpoints fivetwenty/endpoints/orders.py
    uv run python -m docs_validation.src.parity.extract_endpoints --all
"""

from __future__ import annotations

import argparse
import ast
import json
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[3]
ENDPOINTS_DIR = REPO_ROOT / "fivetwenty" / "endpoints"
CACHE_DIR = REPO_ROOT / "docs_validation" / ".cache" / "parity"


def _ann_to_str(node: ast.AST | None) -> str:
    return "" if node is None else ast.unparse(node)


def _value_to_str(node: ast.AST | None) -> str:
    return "" if node is None else ast.unparse(node)


def _extract_request_calls(body: list[ast.stmt]) -> list[dict[str, str]]:
    """Find `self._client._request(METHOD, PATH, ...)` calls and extract verb/path."""
    calls: list[dict[str, str]] = []
    for node in ast.walk(ast.Module(body=body, type_ignores=[])):
        if not isinstance(node, ast.Call):
            continue
        # await self._client._request(...) appears as Call directly
        func = node.func
        # Match self._client._request or self._client.streaming, etc.
        if isinstance(func, ast.Attribute) and func.attr in {"_request", "_stream"}:
            verb = ""
            path = ""
            if node.args:
                if isinstance(node.args[0], ast.Constant):
                    verb = str(node.args[0].value)
                else:
                    verb = _value_to_str(node.args[0])
            if len(node.args) > 1:
                path = _value_to_str(node.args[1]).strip("\"'")
            calls.append({"verb": verb, "path_template": path, "via": func.attr})
    return calls


def _extract_args(args: ast.arguments) -> dict[str, Any]:
    """Capture positional, keyword-only, defaults."""
    out: dict[str, Any] = {"positional": [], "keyword_only": []}

    pos_args = args.args
    pos_defaults = args.defaults
    n_pos = len(pos_args)
    n_def = len(pos_defaults)
    pos_default_offset = n_pos - n_def

    for i, arg in enumerate(pos_args):
        if arg.arg in {"self", "cls"}:
            continue
        default_repr = None
        if i >= pos_default_offset:
            default_repr = _value_to_str(pos_defaults[i - pos_default_offset])
        out["positional"].append(
            {
                "name": arg.arg,
                "annotation": _ann_to_str(arg.annotation),
                "default": default_repr,
            }
        )

    for kw, kwd in zip(args.kwonlyargs, args.kw_defaults, strict=True):
        out["keyword_only"].append(
            {
                "name": kw.arg,
                "annotation": _ann_to_str(kw.annotation),
                "default": _value_to_str(kwd) if kwd else None,
            }
        )

    return out


def _extract_method(item: ast.AsyncFunctionDef | ast.FunctionDef) -> dict[str, Any]:
    return {
        "name": item.name,
        "is_async": isinstance(item, ast.AsyncFunctionDef),
        "line": item.lineno,
        "params": _extract_args(item.args),
        "return_annotation": _ann_to_str(item.returns),
        "request_calls": _extract_request_calls(item.body),
        "docstring_first_line": (ast.get_docstring(item) or "").splitlines()[0] if ast.get_docstring(item) else "",
    }


def extract_module(path: Path) -> dict[str, Any]:
    source = path.read_text(encoding="utf-8")
    tree = ast.parse(source)

    out: dict[str, Any] = {
        "source_file": str(path.relative_to(REPO_ROOT)),
        "endpoint_classes": {},
        "typeddicts": {},
        "type_aliases": {},
    }

    for node in tree.body:
        if isinstance(node, ast.ClassDef):
            if node.name.endswith("Endpoints"):
                methods: dict[str, Any] = {}
                for item in node.body:
                    if isinstance(item, (ast.AsyncFunctionDef, ast.FunctionDef)) and not item.name.startswith("_"):
                        methods[item.name] = _extract_method(item)
                out["endpoint_classes"][node.name] = methods
            else:
                # Capture TypedDicts (e.g. OrderResponse) for response-shape parity
                base_strs = {_ann_to_str(b) for b in node.bases}
                if "TypedDict" in base_strs:
                    fields: dict[str, Any] = {}
                    for item in node.body:
                        if isinstance(item, ast.AnnAssign) and isinstance(item.target, ast.Name):
                            fields[item.target.id] = {
                                "annotation": _ann_to_str(item.annotation),
                                "line": item.lineno,
                            }
                    out["typeddicts"][node.name] = {
                        "fields": fields,
                        "line": node.lineno,
                        "total": next(
                            (_value_to_str(kw.value) for b in node.bases if isinstance(b, ast.Call) for kw in b.keywords if kw.arg == "total"),
                            "True",
                        ),
                    }
        elif isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    out["type_aliases"][target.id] = _value_to_str(node.value)

    return out


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("modules", nargs="*")
    parser.add_argument("--all", action="store_true")
    args = parser.parse_args()

    CACHE_DIR.mkdir(parents=True, exist_ok=True)

    paths = [p for p in ENDPOINTS_DIR.glob("*.py") if p.name != "__init__.py"] if args.all else [Path(p).resolve() for p in args.modules]

    if not paths:
        parser.print_help()
        return 1

    for path in paths:
        result = extract_module(path)
        out_path = CACHE_DIR / f"{path.stem}-endpoints-library.json"
        out_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
        cls_count = sum(len(m) for m in result["endpoint_classes"].values())
        print(f"wrote {out_path.relative_to(REPO_ROOT)}: {cls_count} methods, {len(result['typeddicts'])} typeddicts")

    return 0


if __name__ == "__main__":
    sys.exit(main())
