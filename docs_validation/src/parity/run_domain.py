"""Run the parity pipeline for a single domain and emit a per-domain report.

Pipeline:
  1. Extract library models  → <stem>-library.json
  2. Extract library endpoints → <stem>-endpoints-library.json
  3. Extract OANDA definitions (live cache) → <stem>-df-oanda-definitions.json
  4. Extract OANDA endpoints when the official endpoint page exists
  5. Extract project doc tables (endpoint page when present + grouped models)
  6. Run model diffs (lib↔OANDA, lib↔docs)
  7. Run endpoint diffs when endpoint docs exist (lib↔docs)
  8. Render a domain parity report into docs_validation/reports/<domain>-parity.md

Domain configuration is hardcoded for the OANDA definition domains.

Usage:
    uv run python -m docs_validation.src.parity.run_domain orders
    uv run python -m docs_validation.src.parity.run_domain --all
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any, cast

REPO_ROOT = Path(__file__).resolve().parents[3]
CACHE_DIR = REPO_ROOT / "docs_validation" / ".cache" / "parity"
OANDA_CACHE = REPO_ROOT / "docs_validation" / ".cache" / "oanda"
REPORTS_DIR = REPO_ROOT / "docs_validation" / "reports"

# domain_name → {library_module_stem, oanda_stem, doc_endpoint_stem, doc_model_stems, has_oanda_endpoint}
DOMAINS: dict[str, dict[str, Any]] = {
    "accounts": {
        "library_module": "accounts",
        "oanda_stem": "account",
        "doc_endpoint": "accounts",
        "doc_models": ["account-models"],
    },
    "instruments": {
        "library_module": "instruments",
        "oanda_stem": "instrument",
        "doc_endpoint": "instruments",
        "doc_models": ["market-data-models"],
    },
    "orders": {
        "library_module": "orders",
        "oanda_stem": "order",
        "doc_endpoint": "orders",
        "doc_models": ["order-models"],
    },
    "positions": {
        "library_module": "positions",
        "oanda_stem": "position",
        "doc_endpoint": "positions",
        "doc_models": ["trading-models"],
    },
    "pricing": {
        "library_module": "pricing",
        "oanda_stem": "pricing",
        "doc_endpoint": "pricing",
        "doc_models": ["market-data-models"],
    },
    "trades": {
        "library_module": "trades",
        "oanda_stem": "trade",
        "doc_endpoint": "trades",
        "doc_models": ["trading-models"],
    },
    "transactions": {
        "library_module": "transactions",
        "oanda_stem": "transaction",
        "doc_endpoint": "transactions",
        "doc_models": ["transaction-models"],
    },
}


def _run(*cmd: str) -> None:
    print("$", " ".join(cmd))
    result = subprocess.run(cmd, cwd=REPO_ROOT, check=False, capture_output=True, text=True)
    if result.returncode != 0:
        print(result.stdout)
        print(result.stderr, file=sys.stderr)
        raise SystemExit(f"command failed: {cmd}")


def _load(p: Path) -> dict[str, Any]:
    return cast("dict[str, Any]", json.loads(p.read_text()))


def run_domain(domain: str, *, inventory: dict[str, Any] | None = None) -> dict[str, Any]:
    if inventory is None:
        inv_path = CACHE_DIR / "inventory.json"
        if not inv_path.exists():
            from .build_inventory import build as _build_inv

            inventory = _build_inv()
        else:
            inventory = _load(inv_path)
    cfg = DOMAINS[domain]
    lib_module = cfg["library_module"]
    oanda_stem = cfg["oanda_stem"]
    doc_endpoint = cfg["doc_endpoint"]
    doc_models: list[str] = cfg["doc_models"]
    has_oanda_endpoint = bool(cfg.get("has_oanda_endpoint", True))

    # 1. Extract library models
    _run(
        "uv",
        "run",
        "python",
        "-m",
        "docs_validation.src.parity.extract_pydantic",
        f"fivetwenty/models/{lib_module}.py",
    )
    # 2. Extract library endpoints
    _run(
        "uv",
        "run",
        "python",
        "-m",
        "docs_validation.src.parity.extract_endpoints",
        f"fivetwenty/endpoints/{lib_module}.py",
    )
    # 3. Extract OANDA definitions
    _run(
        "uv",
        "run",
        "python",
        "-m",
        "docs_validation.src.parity.extract_oanda_md",
        "--kind",
        "definition",
        f"docs_validation/.cache/oanda/{oanda_stem}-df.md",
    )
    oanda_eps_json = CACHE_DIR / f"{oanda_stem}-ep-oanda-endpoints.json"
    if has_oanda_endpoint:
        # 4. Extract OANDA endpoints
        _run(
            "uv",
            "run",
            "python",
            "-m",
            "docs_validation.src.parity.extract_oanda_md",
            "--kind",
            "endpoint",
            f"docs_validation/.cache/oanda/{oanda_stem}-ep.md",
        )
    else:
        oanda_eps_json.write_text(
            json.dumps(
                {
                    "source": f"docs_validation/.cache/oanda/{oanda_stem}-ep.md",
                    "endpoints": [],
                },
                indent=2,
            ),
            encoding="utf-8",
        )
    # 5. Extract project doc tables. A missing page is a P1 finding, not a pipeline failure —
    # the lane must still run so library-vs-OANDA drift stays visible.
    missing_doc_pages: list[str] = []
    doc_paths = []
    for m in doc_models:
        rel = f"docs/api-reference/models/{m}.md"
        if (REPO_ROOT / rel).exists():
            doc_paths.append(rel)
        else:
            missing_doc_pages.append(rel)
    if doc_endpoint is not None:
        rel = f"docs/api-reference/endpoints/{doc_endpoint}.md"
        if (REPO_ROOT / rel).exists():
            doc_paths.insert(0, rel)
        else:
            missing_doc_pages.append(rel)
            doc_endpoint = None
    doc_models = [m for m in doc_models if f"docs/api-reference/models/{m}.md" in doc_paths]
    if doc_paths:
        _run(
            "uv",
            "run",
            "python",
            "-m",
            "docs_validation.src.parity.extract_doc_tables",
            *doc_paths,
        )

    # 6 / 7: Run diffs
    lib_models_json = CACHE_DIR / f"{lib_module}-library.json"
    lib_endpoints_json = CACHE_DIR / f"{lib_module}-endpoints-library.json"
    oanda_models_json = CACHE_DIR / f"{oanda_stem}-df-oanda-definitions.json"
    docs_eps_json = CACHE_DIR / f"{doc_endpoint}-docs.json" if doc_endpoint is not None else None

    _run(
        "uv",
        "run",
        "python",
        "-m",
        "docs_validation.src.parity.diff",
        "models",
        "--left",
        str(lib_models_json),
        "--right",
        str(oanda_models_json),
        "--left-source",
        "library",
        "--right-source",
        "oanda",
        "--left-label",
        "library",
        "--right-label",
        "oanda",
        "--out",
        str(CACHE_DIR / f"{domain}-library-vs-oanda.md"),
        "--title",
        f"{domain}: library vs OANDA",
    )

    # For library vs docs, combine the doc-model files since multiple may apply.
    # Simple approach: run one diff per doc-model file and concatenate fragments.
    lib_vs_docs_outs: list[Path] = []
    for dm in doc_models:
        docs_models_json = CACHE_DIR / f"{dm}-docs.json"
        out_md = CACHE_DIR / f"{domain}-library-vs-docs-{dm}.md"
        _run(
            "uv",
            "run",
            "python",
            "-m",
            "docs_validation.src.parity.diff",
            "models",
            "--left",
            str(lib_models_json),
            "--right",
            str(docs_models_json),
            "--left-source",
            "library",
            "--right-source",
            "docs",
            "--left-label",
            "library",
            "--right-label",
            "docs",
            "--out",
            str(out_md),
            "--title",
            f"{domain}: library vs docs ({dm})",
        )
        lib_vs_docs_outs.append(out_md)

    lib_vs_docs_eps_md: str | None = None
    docs_eps: dict[str, Any] = {"methods": {}}
    if docs_eps_json is not None:
        _run(
            "uv",
            "run",
            "python",
            "-m",
            "docs_validation.src.parity.diff",
            "endpoints",
            "--left",
            str(lib_endpoints_json),
            "--right",
            str(docs_eps_json),
            "--left-source",
            "library",
            "--right-source",
            "docs",
            "--left-label",
            "library",
            "--right-label",
            "docs",
            "--out",
            str(CACHE_DIR / f"{domain}-endpoints-library-vs-docs.md"),
            "--title",
            f"{domain} endpoints: library vs docs",
        )
        lib_vs_docs_eps_md = (CACHE_DIR / f"{domain}-endpoints-library-vs-docs.md").read_text()
        docs_eps = _load(docs_eps_json)

    # Final assembly: render a single per-domain report.
    return assemble_domain_report(
        domain=domain,
        lib_models=_load(lib_models_json),
        lib_eps=_load(lib_endpoints_json),
        oanda_defs=_load(oanda_models_json),
        oanda_eps=_load(oanda_eps_json),
        docs_eps=docs_eps,
        lib_vs_oanda_md=(CACHE_DIR / f"{domain}-library-vs-oanda.md").read_text(),
        lib_vs_docs_mds={dm: (CACHE_DIR / f"{domain}-library-vs-docs-{dm}.md").read_text() for dm in doc_models},
        lib_vs_docs_eps_md=lib_vs_docs_eps_md,
        inventory=inventory,
        has_oanda_endpoint=has_oanda_endpoint,
        missing_doc_pages=missing_doc_pages,
    )


def _filter_cross_page(md: str, *, library_known: set[str], oanda_known: set[str]) -> str:
    """In a model-vs-OANDA diff, drop bullets from the 'Models present in X but missing in Y'
    sections when the symbol is known to exist somewhere in the inventory.

    Operates on the rendered markdown — drops list items inline, leaves headings intact.
    Annotates filtered items with `(in {file})` is left to a future enhancement.
    """
    lines = md.splitlines()
    out: list[str] = []
    state: str | None = None  # 'lib_missing' | 'oanda_missing' | None
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("## Models present in library but missing in"):
            state = "in_oanda_check"  # listing items that are in library but not on this OANDA page
            out.append(line + " (this page)")
            continue
        if stripped.startswith("## Models present in oanda but missing in"):
            state = "in_library_check"  # items on OANDA page but not the matched library file
            out.append(line + " (this domain)")
            continue
        if stripped.startswith("##"):
            state = None
            out.append(line)
            continue
        if state and stripped.startswith("- `") and stripped.endswith("`"):
            name = stripped.strip("- `")
            if state == "in_oanda_check" and name in oanda_known:
                out.append(f"- `{name}` _(found elsewhere in OANDA inventory — not a true gap)_")
            elif state == "in_library_check" and name in library_known:
                out.append(f"- `{name}` _(found elsewhere in library — not a true gap)_")
            else:
                out.append(line)
            continue
        out.append(line)
    return "\n".join(out)


def _normalize_path(p: str) -> str:
    """Normalize URL templates so {accountID} ≡ {account_id} ≡ {ID}."""
    import re as _re

    p = p.lstrip("f").strip("'\"")
    p = _re.sub(r"\{[^}]+\}", "{X}", p)
    if not p.startswith("/v3"):
        p = "/v3" + p
    return p.rstrip("/")


def assemble_domain_report(
    *,
    domain: str,
    lib_models: dict[str, Any],
    lib_eps: dict[str, Any],
    oanda_defs: dict[str, Any],
    oanda_eps: dict[str, Any],
    docs_eps: dict[str, Any],
    lib_vs_oanda_md: str,
    lib_vs_docs_mds: dict[str, str],
    lib_vs_docs_eps_md: str | None,
    inventory: dict[str, Any],
    has_oanda_endpoint: bool,
    missing_doc_pages: list[str] | None = None,
) -> dict[str, Any]:
    """Compose the per-domain parity report and write it to reports/<domain>-parity.md."""
    out_path = REPORTS_DIR / f"{domain}-parity.md"

    n_lib_models = len(lib_models.get("models", {}))
    n_oanda_defs = len(oanda_defs.get("definitions", {}))
    n_lib_methods = sum(len(m) for m in lib_eps.get("endpoint_classes", {}).values())
    n_oanda_eps = len(oanda_eps.get("endpoints", []))
    n_docs_methods = len(docs_eps.get("methods", {})) if lib_vs_docs_eps_md is not None else None

    # Symbols known elsewhere — used to suppress cross-page false positives.
    library_known = set(inventory.get("library_models", [])) | set(inventory.get("library_enums", [])) | set(inventory.get("library_typeddicts", [])) | set(inventory.get("library_aliases", []))
    oanda_known = set(inventory.get("oanda_definitions", [])) | set(inventory.get("oanda_enums", [])) | set(inventory.get("oanda_primitives", []))

    parts: list[str] = []
    parts.append(f"# {domain.title()} Parity Report")
    parts.append("")
    parts.append("Generated by `docs_validation/src/parity/run_domain.py`. Diffs:")
    parts.append("")
    parts.append("- **Diff A1**: library ↔ live OANDA docs (this domain's OANDA page only)")
    parts.append("- **Diff B-models**: library ↔ project docs (model field tables)")
    if lib_vs_docs_eps_md is not None:
        parts.append("- **Diff B-endpoints**: library ↔ project docs (endpoint method signatures)")
    parts.append("")
    parts.append("Cross-page references (e.g. `ClientExtensions` shared with trades) are suppressed in the *missing* lists when the symbol exists somewhere in the inventory.")
    parts.append("")
    parts.append("## Inventory")
    parts.append("")
    parts.append("| Surface | Count |")
    parts.append("|---|---|")
    parts.append(f"| Library Pydantic models | {n_lib_models} |")
    parts.append(f"| Library endpoint methods | {n_lib_methods} |")
    parts.append(f"| OANDA definitions (live page) | {n_oanda_defs} |")
    parts.append(f"| OANDA endpoints (live page) | {n_oanda_eps} |")
    parts.append(f"| Project-doc methods | {n_docs_methods if n_docs_methods is not None else 'n/a'} |")
    parts.append("")
    if not has_oanda_endpoint:
        parts.append("This domain has official OANDA definitions but no official OANDA endpoint page.")
        parts.append("")
    for missing in missing_doc_pages or []:
        parts.append(f"> **P1 — documentation page missing:** `{missing}` does not exist. Documentation parity cannot be checked against it for this domain.")
        parts.append("")

    # Endpoint coverage with normalized path matching.
    oanda_paths = sorted({(e["verb"], _normalize_path(e["path_template"])) for e in oanda_eps.get("endpoints", [])})
    lib_paths: set[tuple[str, str]] = set()
    for cls in lib_eps.get("endpoint_classes", {}).values():
        for m in cls.values():
            for c in m.get("request_calls", []):
                lib_paths.add((c["verb"], _normalize_path(c["path_template"])))
    parts.append("## Endpoint coverage (OANDA → library)")
    parts.append("")
    parts.append("| Verb | OANDA path | Library has it? |")
    parts.append("|---|---|---|")
    for verb, path in oanda_paths:
        match = "✅" if (verb, path) in lib_paths else "❌"
        parts.append(f"| `{verb}` | `{path}` | {match} |")
    parts.append("")
    extras_in_lib = lib_paths - set(oanda_paths)
    if extras_in_lib:
        parts.append("**Extra paths in library** (no OANDA equivalent on this page; may live on another domain):")
        parts.append("")
        for verb, path in sorted(extras_in_lib):
            parts.append(f"- `{verb} {path}`")
        parts.append("")

    parts.append("## Diff A1 — library ↔ live OANDA docs")
    parts.append("")
    parts.append(_filter_cross_page(lib_vs_oanda_md, library_known=library_known, oanda_known=oanda_known))
    parts.append("")

    for dm, md in lib_vs_docs_mds.items():
        parts.append(f"## Diff B-models ({dm}) — library ↔ project docs")
        parts.append("")
        parts.append(md.split("\n", 1)[1] if "\n" in md else md)
        parts.append("")

    if lib_vs_docs_eps_md is not None:
        parts.append("## Diff B-endpoints — library ↔ project docs (method signatures)")
        parts.append("")
        parts.append(lib_vs_docs_eps_md.split("\n", 1)[1] if "\n" in lib_vs_docs_eps_md else lib_vs_docs_eps_md)
        parts.append("")

    parts.append("## Punch list (auto-generated, prioritize manually)")
    parts.append("")
    parts.append("Skim the diff sections above. P0 items typically come from Diff A1's:")
    parts.append("- *Models present in OANDA but missing in library* (deserialization gaps)")
    parts.append("- *Fields in OANDA but missing in library* (data-loss risk)")
    parts.append("- *Optionality drift where library is `False` but OANDA is `True`* (deserialization will fail when OANDA omits the field)")
    parts.append("")
    parts.append("P3 items typically come from Diff B-endpoints (stale source line numbers, missing parameters in doc tables).")

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(parts), encoding="utf-8")
    print(f"wrote {out_path.relative_to(REPO_ROOT)}")
    return {"path": str(out_path), "n_lib_models": n_lib_models, "n_oanda_defs": n_oanda_defs}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("domains", nargs="*")
    parser.add_argument("--all", action="store_true")
    args = parser.parse_args()

    domains = list(DOMAINS.keys()) if args.all else args.domains
    if not domains:
        parser.print_help()
        return 1

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    # Build inventory once for all domains
    from .build_inventory import build as _build_inv

    inventory = _build_inv()
    blocked: list[str] = []
    for d in domains:
        if d not in DOMAINS:
            print(f"unknown domain: {d}; known: {list(DOMAINS)}", file=sys.stderr)
            continue
        try:
            run_domain(d, inventory=inventory)
        except SystemExit as e:
            blocked.append(d)
            print(f"BLOCKED on {d}: {e}", file=sys.stderr)
            (REPORTS_DIR / f"BLOCKED-{d}.md").write_text(f"# Blocked: {d}\n\n{e}\n", encoding="utf-8")
        else:
            # A successful run supersedes any stale blocker from a previous failure.
            (REPORTS_DIR / f"BLOCKED-{d}.md").unlink(missing_ok=True)
    return 2 if blocked else 0


if __name__ == "__main__":
    sys.exit(main())
