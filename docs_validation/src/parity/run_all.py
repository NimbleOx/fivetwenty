"""Run the entire parity pipeline end-to-end.

Steps:
  1. Fetch live OANDA pages into .cache/oanda/ (skip if cached unless --refresh)
  2. Build the global inventory
  3. Run the per-domain parity reports
  4. Run the cross-cutting enums report
  5. Run the docs-surface reports (tutorials/guides/examples/readme)
  6. Run strict field-by-field validation against official OANDA definitions

Designed to be invoked from a `poe` task. Exits non-zero on any P0-class drift
that the user should know about (so CI can gate on it).

Usage:
    uv run python -m docs_validation.src.parity.run_all
    uv run python -m docs_validation.src.parity.run_all --refresh   # re-fetch OANDA
    uv run python -m docs_validation.src.parity.run_all --no-fetch  # cached only

Exit codes:
  0 — pipeline completed; no fatal P0 drift detected
  1 — pipeline completed but found P0-class drift (CI signal)
  2 — pipeline failed (missing cache, network error, etc.)
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
OANDA_CACHE = REPO_ROOT / "docs_validation" / ".cache" / "oanda"
CACHE_DIR = REPO_ROOT / "docs_validation" / ".cache" / "parity"
REPORTS_DIR = REPO_ROOT / "docs_validation" / "reports"

# Required cached pages — if any are missing, we must fetch.
REQUIRED_OANDA_PAGES = [
    "account-df.md",
    "account-ep.md",
    "instrument-df.md",
    "instrument-ep.md",
    "order-df.md",
    "order-ep.md",
    "position-df.md",
    "position-ep.md",
    "pricing-df.md",
    "pricing-ep.md",
    "trade-df.md",
    "trade-ep.md",
    "transaction-df.md",
    "transaction-ep.md",
    "pricing-common-df.md",
    "primitives-df.md",
]

# OANDA no longer exposes this live page in the REST-v20 documentation
# navigation, and https://developer.oanda.com/rest-live-v20/instrument-ep/
# returns 404 as of 2026-08-28. The endpoint definitions are still present in
# OANDA's official v20 OpenAPI repository and in our cached snapshot, so treat
# this as an explicit source note instead of unexpected parity drift.
KNOWN_STALE_OANDA_PAGES = {
    "instrument-ep": "OANDA live page returns 404; official v20 OpenAPI still lists the instrument endpoints",
}


def _has_cache() -> bool:
    return all((OANDA_CACHE / name).exists() for name in REQUIRED_OANDA_PAGES)


def _maybe_fetch(refresh: bool, no_fetch: bool) -> bool:
    """Returns True if cache is ready, False if we couldn't fetch."""
    if no_fetch:
        if not _has_cache():
            print("ERROR: --no-fetch but cache is incomplete. Run without --no-fetch first.", file=sys.stderr)
            return False
        return True
    if refresh or not _has_cache():
        from .live_oanda_fetch import main as fetch_main

        argv = sys.argv[:]
        sys.argv = ["live_oanda_fetch"] + (["--force"] if refresh else [])
        try:
            rc = fetch_main()
        finally:
            sys.argv = argv
        if rc != 0:
            print("ERROR: live_oanda_fetch returned non-zero", file=sys.stderr)
            return False
    return _has_cache()


def _count_critical_findings() -> tuple[int, list[str], list[str]]:
    """Scan reports for P0-class signals. Returns (count, summary_lines, notes)."""
    findings: list[str] = []
    notes: list[str] = []
    count = 0

    # Per-domain reports: surface missing project-doc pages (P1) so they can't hide.
    for path in sorted(REPORTS_DIR.glob("*-parity.md")):
        content = path.read_text(encoding="utf-8")
        for missing_match in re.finditer(r"\*\*P1 — documentation page missing:\*\* `([^`]+)`", content):
            findings.append(f"{path.name}: P1 missing documentation page {missing_match.group(1)}")

    # Docs-surface reports: count stale imports/methods (excluding the known false positives)
    for name in ("tutorials-parity.md", "guides-parity.md", "examples-parity.md"):
        path = REPORTS_DIR / name
        if not path.exists():
            continue
        content = path.read_text(encoding="utf-8")
        m = re.search(r"Stale import refs:\s*(\d+)", content)
        n_imp = int(m.group(1)) if m else 0
        m = re.search(r"Stale method refs:\s*(\d+)", content)
        n_meth = int(m.group(1)) if m else 0
        if n_imp + n_meth > 0:
            findings.append(f"{name}: {n_imp} stale imports, {n_meth} stale method calls")
            # Don't fail CI on these by default — they include known false positives
            # (sync proxy, hypothetical extension examples). User can opt-in via --strict.

    fetch_status_json = OANDA_CACHE / "fetch-status.json"
    if fetch_status_json.exists():
        status = json.loads(fetch_status_json.read_text(encoding="utf-8"))
        for slug, state in sorted(status.items()):
            if state != "fresh":
                if slug in KNOWN_STALE_OANDA_PAGES:
                    notes.append(f"oanda cache: `{slug}` is {state} — {KNOWN_STALE_OANDA_PAGES[slug]}")
                    continue
                findings.append(f"oanda cache: `{slug}` is {state} — live page could not be fetched; parity for it ran against a stale snapshot")

    docs_meta_json = CACHE_DIR / "docs-meta.json"
    if docs_meta_json.exists():
        meta = json.loads(docs_meta_json.read_text(encoding="utf-8"))
        if meta.get("P2_defaults"):
            findings.append(f"docs-meta-parity.md: {meta['P2_defaults']} P2 default-value drift items")
        if meta.get("P3_anchors"):
            findings.append(f"docs-meta-parity.md: {meta['P3_anchors']} P3 stale source anchors")

    field_validation_json = CACHE_DIR / "field-validation.json"
    if field_validation_json.exists():
        payload = json.loads(field_validation_json.read_text(encoding="utf-8"))
        summary = payload.get("summary", {})
        p0_count = int(summary.get("P0", 0))
        p1_count = int(summary.get("P1", 0))
        if p0_count:
            count += p0_count
            findings.append(f"field-validation.md: {p0_count} P0 field-level drift items")
        if p1_count:
            findings.append(f"field-validation.md: {p1_count} P1 enum/primitive drift items")

    return count, findings, notes


def _run_field_validation() -> None:
    from .field_validate import apply_waivers, build_library_catalog, build_official_catalog, validate, write_json, write_markdown
    from .waivers import DEFAULT_WAIVERS_PATH

    official = build_official_catalog()
    library = build_library_catalog()
    issues = validate(official, library)
    issues, waived_issues = apply_waivers(issues, DEFAULT_WAIVERS_PATH)
    write_json(issues, CACHE_DIR / "field-validation.json", waived_issues)
    write_markdown(issues, REPORTS_DIR / "field-validation.md", waived_issues)

    summary = {severity: sum(1 for issue in issues if issue.severity == severity) for severity in ("P0", "P1", "P2", "P3")}
    print("field validation:", ", ".join(f"{severity}={summary[severity]}" for severity in ("P0", "P1", "P2", "P3")))
    if waived_issues:
        print(f"field validation: waived={len(waived_issues)}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--refresh", action="store_true", help="Re-fetch live OANDA pages even if cached")
    parser.add_argument("--no-fetch", action="store_true", help="Use cached OANDA pages only; fail if missing")
    parser.add_argument("--strict", action="store_true", help="Exit non-zero on any drift, including docs-surface false positives")
    args = parser.parse_args()

    if not _maybe_fetch(args.refresh, args.no_fetch):
        return 2

    # Build inventory
    print("\n=== Building global inventory ===")
    from .build_inventory import build as build_inventory

    inventory = build_inventory()

    # Per-domain reports
    print("\n=== Running per-domain parity reports ===")
    from .run_domain import DOMAINS, run_domain

    blocked_domains: list[str] = []
    for d in DOMAINS:
        try:
            run_domain(d, inventory=inventory)
        except SystemExit as e:  # noqa: PERF203
            blocked_domains.append(d)
            print(f"BLOCKED on {d}: {e}", file=sys.stderr)
            (REPORTS_DIR / f"BLOCKED-{d}.md").write_text(f"# Blocked: {d}\n\n{e}\n", encoding="utf-8")
        else:
            (REPORTS_DIR / f"BLOCKED-{d}.md").unlink(missing_ok=True)

    # Cross-cutting reports
    print("\n=== Running enums parity ===")
    from .run_enums import main as run_enums_main

    run_enums_main()

    print("\n=== Running docs-surface parity ===")
    from .run_docs_surface import main as run_docs_surface_main

    run_docs_surface_main()

    print("\n=== Running docs metadata checks (defaults, source anchors) ===")
    from .check_docs_meta import main as check_docs_meta_main

    check_docs_meta_main()

    print("\n=== Running field validation ===")
    _run_field_validation()

    # Summarize
    count, findings, notes = _count_critical_findings()
    print("\n=== Parity pipeline summary ===")
    if blocked_domains:
        for d in blocked_domains:
            print(f"  - BLOCKED: {d} lane failed to run (see reports/BLOCKED-{d}.md)")
    if findings:
        for line in findings:
            print(f"  - {line}")
    if notes:
        for line in notes:
            print(f"  - NOTE: {line}")
    if not blocked_domains and not findings and not notes:
        print("  No drift detected.")

    if blocked_domains:
        print(f"\n❌ {len(blocked_domains)} parity lane(s) failed to run. The pipeline result is incomplete.", file=sys.stderr)
        return 2
    if count > 0:
        print(f"\n⚠️  {count} P0-class drift items detected. See docs_validation/reports/ for details.")
        return 1
    if findings and args.strict:
        print(f"\n⚠️  {len(findings)} non-P0 finding(s) detected (strict mode). See docs_validation/reports/ for details.")
        return 1
    print("\n✅ No P0-class drift.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
