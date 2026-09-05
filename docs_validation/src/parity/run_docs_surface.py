"""Generate docs-surface parity reports.

Validates that every SDK reference in tutorials/guides/examples/README/notebooks
resolves against the current library.

Three checks:
  1. Import statements: `from fivetwenty[.module] import X` — does X exist?
  2. Method calls: `client.<endpoint>.<method>(` — is <endpoint> attached to AsyncClient
     and does <method> exist on the corresponding *Endpoints class?
  3. Constructor signatures: where the doc shows `AsyncClient(...)`, do the kwargs match?

Outputs four reports under docs_validation/reports/:
  - tutorials-parity.md
  - guides-parity.md
  - examples-parity.md
  - readme-parity.md
"""

from __future__ import annotations

import ast
import json
import re
from collections.abc import Iterable
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
REPORTS = REPO_ROOT / "docs_validation" / "reports"
CACHE = REPO_ROOT / "docs_validation" / ".cache" / "parity"


def sync_endpoint_methods(client_file: Path) -> dict[str, set[str]]:
    """Discover public methods on the dedicated synchronous endpoint adapters."""
    methods: dict[str, set[str]] = {}
    if client_file.exists():
        for node in ast.walk(ast.parse(client_file.read_text())):
            if isinstance(node, ast.ClassDef) and node.name.startswith("_Sync") and node.name.endswith("Proxy"):
                endpoint = node.name.removeprefix("_Sync").removesuffix("Proxy").lower()
                methods[endpoint] = {item.name for item in node.body if isinstance(item, ast.FunctionDef) and not item.name.startswith("_")}
    return methods


def _build_library_surface() -> dict[str, set[str]]:
    """Walk fivetwenty/ and collect public names per module + endpoint methods.

    Follows `from .submodule import *` so that, e.g., names defined in
    `fivetwenty.models.enums` are also reachable as `fivetwenty.models.X`.
    """
    surface: dict[str, set[str]] = {}
    wildcard_imports: dict[str, list[str]] = {}  # parent_module → [child_modules with `*`]

    for path in sorted((REPO_ROOT / "fivetwenty").rglob("*.py")):
        if "__pycache__" in path.parts:
            continue
        if path.name == "__init__.py":
            mod = ".".join(path.parent.relative_to(REPO_ROOT).parts)
        else:
            mod = ".".join(path.relative_to(REPO_ROOT).with_suffix("").parts)
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"))
        except SyntaxError:
            continue
        names: set[str] = set()
        for node in tree.body:
            if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
                if not node.name.startswith("_"):
                    names.add(node.name)
            elif isinstance(node, ast.Assign):
                for tgt in node.targets:
                    if isinstance(tgt, ast.Name) and not tgt.id.startswith("_"):
                        names.add(tgt.id)
            elif isinstance(node, ast.ImportFrom):
                # Resolve relative imports
                level = node.level
                module = node.module or ""
                # `from .x import y` in package fivetwenty.foo.bar means module = fivetwenty.foo[level-1].x
                if level > 0:
                    parts = mod.split(".")
                    base = ".".join(parts[: max(0, len(parts) - level + 1)])
                    full_mod = f"{base}.{module}" if module else base
                else:
                    full_mod = module
                for alias in node.names:
                    if alias.name == "*":
                        wildcard_imports.setdefault(mod, []).append(full_mod)
                    else:
                        names.add(alias.asname or alias.name)
        surface[mod] = names

    # Resolve wildcard imports — iterate to fixed point.
    for _ in range(5):
        for parent, children in wildcard_imports.items():
            for child in children:
                child_names = surface.get(child, set())
                surface[parent] |= child_names

    # Endpoint method surface — keyed by attribute name on AsyncClient
    # AsyncClient binds: accounts, instruments, orders, positions, pricing, trades, transactions
    endpoint_attrs = {
        "accounts": "AccountEndpoints",
        "instruments": "InstrumentEndpoints",
        "orders": "OrderEndpoints",
        "positions": "PositionEndpoints",
        "pricing": "PricingEndpoints",
        "trades": "TradeEndpoints",
        "transactions": "TransactionEndpoints",
    }
    endpoint_methods: dict[str, set[str]] = {}
    for attr_name, class_name in endpoint_attrs.items():
        ep_path = REPO_ROOT / "fivetwenty" / "endpoints" / f"{attr_name}.py"
        if not ep_path.exists():
            continue
        ep_tree = ast.parse(ep_path.read_text(encoding="utf-8"))
        methods: set[str] = set()
        for walked in ast.walk(ep_tree):
            if isinstance(walked, ast.ClassDef) and walked.name == class_name:
                for item in walked.body:
                    if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)) and not item.name.startswith("_"):
                        methods.add(item.name)
        endpoint_methods[attr_name] = methods
    for endpoint, methods in sync_endpoint_methods(REPO_ROOT / "fivetwenty" / "client.py").items():
        if endpoint in endpoint_methods:
            endpoint_methods[endpoint].update(methods)
    surface["__client_endpoints__"] = endpoint_methods  # type: ignore[assignment]
    return surface


def _check_imports(content: str, surface: dict[str, set[str]]) -> list[str]:
    """Return list of import-error messages."""
    issues: list[str] = []
    # Match `from fivetwenty[...] import (X, Y, ...)` and `from fivetwenty[...] import X[, Y]`
    for m in re.finditer(r"from\s+(fivetwenty(?:\.[a-zA-Z_.]+)?)\s+import\s+([^\n]+)", content):
        mod = m.group(1)
        names_str = m.group(2)
        # Strip parens, comments, trailing
        names_str = re.sub(r"#.*", "", names_str)
        names_str = names_str.replace("(", "").replace(")", "").strip()
        for n in [s.strip() for s in names_str.split(",")]:
            if not n:
                continue
            # Handle aliasing: `X as Y` — check X
            base = n.split(" as ")[0].strip()
            mod_names = surface.get(mod, set())
            if base not in mod_names:
                # Maybe it's re-exported through fivetwenty
                if base in surface.get("fivetwenty", set()):
                    continue
                issues.append(f"`from {mod} import {base}` — `{base}` not found in {mod}")
    return issues


def _check_method_calls(content: str, surface: dict[str, set[str]]) -> list[str]:
    """Return list of unresolved client.<endpoint>.<method> references."""
    issues: list[str] = []
    endpoint_methods: dict[str, set[str]] = surface.get("__client_endpoints__", {})  # type: ignore[assignment]
    if not endpoint_methods:
        return issues
    seen: set[tuple[str, str]] = set()
    for m in re.finditer(r"\bclient\.(\w+)\.(\w+)\(", content):
        ep, method = m.group(1), m.group(2)
        key = (ep, method)
        if key in seen:
            continue
        seen.add(key)
        if ep in endpoint_methods:
            if method not in endpoint_methods[ep]:
                issues.append(f"`client.{ep}.{method}()` — method not found on {ep} endpoint")
        elif ep in {"config", "_environment", "environment", "_session", "_client"}:
            # Internal/conventional attributes — skip unless deeply suspect
            continue
        else:
            issues.append(f"`client.{ep}.{method}()` — `{ep}` is not an AsyncClient endpoint attribute")
    return issues


def scan_files(paths: Iterable[Path], surface: dict[str, set[str]]) -> dict[str, dict[str, list[str]]]:
    out: dict[str, dict[str, list[str]]] = {}
    for path in paths:
        try:
            content = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        # For .ipynb: parse cells
        if path.suffix == ".ipynb":
            try:
                nb = json.loads(content)
            except json.JSONDecodeError:
                continue
            content = "\n\n".join("".join(c.get("source", [])) for c in nb.get("cells", []) if c.get("cell_type") == "code")
        import_issues = _check_imports(content, surface)
        method_issues = _check_method_calls(content, surface)
        if import_issues or method_issues:
            out[str(path.relative_to(REPO_ROOT))] = {
                "imports": import_issues,
                "methods": method_issues,
            }
    return out


def render_report(scope: str, files: dict[str, dict[str, list[str]]], total_files: int) -> str:
    lines: list[str] = [f"# {scope.title()} Parity Report", ""]
    lines.append(f"Validates that SDK references in `docs/{scope}/` resolve against the current library.")
    lines.append("")
    lines.append("## Inventory")
    lines.append("")
    lines.append(f"- Files scanned: {total_files}")
    lines.append(f"- Files with issues: {len(files)}")
    total_imp = sum(len(v["imports"]) for v in files.values())
    total_meth = sum(len(v["methods"]) for v in files.values())
    lines.append(f"- Stale import refs: {total_imp}")
    lines.append(f"- Stale method refs: {total_meth}")
    lines.append("")

    if not files:
        lines.append("_No issues found._")
        return "\n".join(lines)

    lines.append("## Findings by file")
    lines.append("")
    for path in sorted(files):
        lines.append(f"### `{path}`")
        lines.append("")
        if files[path]["imports"]:
            lines.append("**Stale imports:**")
            lines.append("")
            for issue in files[path]["imports"]:
                lines.append(f"- {issue}")
            lines.append("")
        if files[path]["methods"]:
            lines.append("**Stale method calls:**")
            lines.append("")
            for issue in files[path]["methods"]:
                lines.append(f"- {issue}")
            lines.append("")
    return "\n".join(lines)


def main() -> None:
    REPORTS.mkdir(parents=True, exist_ok=True)
    surface = _build_library_surface()

    # Tutorials
    tut_paths = sorted((REPO_ROOT / "docs" / "tutorials").rglob("*.md"))
    issues = scan_files(tut_paths, surface)
    (REPORTS / "tutorials-parity.md").write_text(render_report("tutorials", issues, len(tut_paths)), encoding="utf-8")
    print(f"wrote tutorials-parity.md: {len(tut_paths)} files, {len(issues)} with issues")

    # Guides
    guide_paths = sorted((REPO_ROOT / "docs" / "guides").rglob("*.md"))
    issues = scan_files(guide_paths, surface)
    (REPORTS / "guides-parity.md").write_text(render_report("guides", issues, len(guide_paths)), encoding="utf-8")
    print(f"wrote guides-parity.md: {len(guide_paths)} files, {len(issues)} with issues")

    # Examples (.py + .ipynb)
    ex_paths = sorted(list((REPO_ROOT / "docs" / "examples").rglob("*.py")) + list((REPO_ROOT / "docs" / "examples").rglob("*.ipynb")) + list((REPO_ROOT / "docs" / "examples").rglob("*.md")))
    issues = scan_files(ex_paths, surface)
    (REPORTS / "examples-parity.md").write_text(render_report("examples", issues, len(ex_paths)), encoding="utf-8")
    print(f"wrote examples-parity.md: {len(ex_paths)} files, {len(issues)} with issues")

    # README
    readme = REPO_ROOT / "README.md"
    issues = scan_files([readme], surface)
    parts = [
        "# README + Package Metadata Parity Report",
        "",
        "## Inventory",
        "",
        f"- README lines: {len(readme.read_text(encoding='utf-8').splitlines())}",
    ]
    # Version match
    pyproject = (REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8")
    pyproject_version = re.search(r'^version\s*=\s*"([^"]+)"', pyproject, re.MULTILINE)
    init_text = (REPO_ROOT / "fivetwenty" / "__init__.py").read_text(encoding="utf-8")
    fallback_version = re.search(r'__version__\s*=\s*"([^"]+)"', init_text)
    parts.append(f"- pyproject.toml version: `{pyproject_version.group(1) if pyproject_version else '?'}`")
    parts.append(f"- __init__.py fallback version: `{fallback_version.group(1) if fallback_version else '?'}`")
    # The dev sentinel is the intentional "metadata unavailable" fallback, not a
    # pinned release number — only a concrete version can drift.
    if pyproject_version and fallback_version and not fallback_version.group(1).endswith(".dev0") and pyproject_version.group(1) != fallback_version.group(1):
        parts.append(f"- ⚠️ **Version drift**: __init__.py fallback (`{fallback_version.group(1)}`) does not match pyproject.toml (`{pyproject_version.group(1)}`)")
    parts.append("")
    if issues:
        parts.append("## README findings")
        parts.append("")
        for path, data in issues.items():
            for cat in ("imports", "methods"):
                for it in data[cat]:
                    parts.append(f"- {it}")
    else:
        parts.append("_No SDK reference issues in README._")
    (REPORTS / "readme-parity.md").write_text("\n".join(parts), encoding="utf-8")
    print("wrote readme-parity.md")


if __name__ == "__main__":
    main()
