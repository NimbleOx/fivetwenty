"""Build a global inventory of library symbols and OANDA-page symbols.

The inventory lets per-domain diffs suppress cross-page false positives
(e.g. `ClientExtensions` is defined on the OANDA trade-df page but referenced
by orders; `OrderType` lives in fivetwenty/models/enums.py, not orders.py).

Outputs:
  docs_validation/.cache/parity/inventory.json
    {
      "library_models": [...],     # all Pydantic model class names across fivetwenty/models/
      "library_enums": [...],      # all Enum class names
      "library_typeddicts": [...], # all TypedDict class names (response shapes from endpoints/)
      "library_aliases": [...],    # type aliases like OrderID = str
      "oanda_definitions": [...],  # all definition names across all *-df cached pages
      "oanda_enums": [...],        # enums (with values) across pages
      "oanda_primitives": [...],   # primitive types across pages
    }
"""

from __future__ import annotations

import json
from pathlib import Path

from .extract_endpoints import extract_module as extract_endpoints_module
from .extract_oanda_md import extract_definition as extract_oanda_definition
from .extract_pydantic import extract_module as extract_pydantic_module

REPO_ROOT = Path(__file__).resolve().parents[3]
CACHE = REPO_ROOT / "docs_validation" / ".cache" / "parity"
OANDA_CACHE = REPO_ROOT / "docs_validation" / ".cache" / "oanda"
MODELS_DIR = REPO_ROOT / "fivetwenty" / "models"
ENDPOINTS_DIR = REPO_ROOT / "fivetwenty" / "endpoints"


def build() -> dict[str, list[str]]:
    library_models: set[str] = set()
    library_enums: set[str] = set()
    library_typeddicts: set[str] = set()
    library_aliases: set[str] = set()

    for path in sorted(MODELS_DIR.glob("*.py")):
        if path.name == "__init__.py":
            continue
        data = extract_pydantic_module(path)
        library_models.update(data.get("models", {}).keys())
        library_enums.update(data.get("enums", {}).keys())
        library_typeddicts.update(data.get("typeddicts", {}).keys())
        library_aliases.update(data.get("type_aliases", {}).keys())

    for path in sorted(ENDPOINTS_DIR.glob("*.py")):
        if path.name == "__init__.py":
            continue
        data = extract_endpoints_module(path)
        library_typeddicts.update(data.get("typeddicts", {}).keys())
        library_aliases.update(data.get("type_aliases", {}).keys())

    oanda_defs: set[str] = set()
    oanda_enums: set[str] = set()
    oanda_primitives: set[str] = set()

    for path in sorted(OANDA_CACHE.glob("*-df.md")):
        data = extract_oanda_definition(path)
        for name, body in data.get("definitions", {}).items():
            if body.get("fields"):
                oanda_defs.add(name)
            if body.get("enum_values"):
                oanda_enums.add(name)
            if body.get("primitive"):
                oanda_primitives.add(name)
            if not body.get("fields") and not body.get("enum_values") and not body.get("primitive"):
                # Still capture the bare name as an OANDA-known symbol.
                oanda_defs.add(name)

    inventory = {
        "library_models": sorted(library_models),
        "library_enums": sorted(library_enums),
        "library_typeddicts": sorted(library_typeddicts),
        "library_aliases": sorted(library_aliases),
        "oanda_definitions": sorted(oanda_defs),
        "oanda_enums": sorted(oanda_enums),
        "oanda_primitives": sorted(oanda_primitives),
    }
    CACHE.mkdir(parents=True, exist_ok=True)
    out = CACHE / "inventory.json"
    out.write_text(json.dumps(inventory, indent=2), encoding="utf-8")
    print(f"wrote {out.relative_to(REPO_ROOT)}: lib({len(library_models)} models, {len(library_enums)} enums, {len(library_typeddicts)} typeddicts), oanda({len(oanda_defs)} defs, {len(oanda_enums)} enums, {len(oanda_primitives)} primitives)")
    return inventory


if __name__ == "__main__":
    build()
