"""Fetch live OANDA REST v20 documentation pages and cache as markdown.

The live OANDA docs are HTML; this script fetches each page, converts to a
parser-friendly markdown form (preserving field tables), and caches under
docs_validation/.cache/oanda/.

Usage:
    uv run python -m docs_validation.src.parity.live_oanda_fetch          # all known pages
    uv run python -m docs_validation.src.parity.live_oanda_fetch order    # specific page slugs

Pages fetched:
  - <domain>-ep/  (endpoints) for: account, order, position, pricing, trade, transaction
  - <domain>-df/  (definitions) for: account, instrument, order, position, pricing, trade, transaction, plus pricing-common-df and primitives-df
  - introduction/, authentication/, troubleshooting-errors/, best-practices/, development-guide/

Conversion strategy:
  - Use httpx to GET the HTML
  - Parse with BeautifulSoup, walking the main content container
  - Headings become markdown headings
  - <table> → markdown pipe table (preserves Field/Type/Required/Default columns)
  - <ul>/<li> → markdown bullet lists (for enum value listings)
  - <code> → backticks
  - other inline elements stripped to text

This gives us pages that extract_oanda_md.py can parse correctly.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import httpx
from bs4 import BeautifulSoup, Tag
from bs4.element import NavigableString

REPO_ROOT = Path(__file__).resolve().parents[3]
CACHE_DIR = REPO_ROOT / "docs_validation" / ".cache" / "oanda"
BASE_URL = "https://developer.oanda.com/rest-live-v20"

ENDPOINT_DOMAINS = ["account", "instrument", "order", "position", "pricing", "trade", "transaction"]
DEFINITION_DOMAINS = ["account", "instrument", "order", "position", "pricing", "trade", "transaction"]
EXTRA_PAGES = ["introduction", "authentication", "troubleshooting-errors", "best-practices", "development-guide", "pricing-common-df", "primitives-df"]


def _all_slugs() -> list[str]:
    slugs = [f"{d}-ep" for d in ENDPOINT_DOMAINS] + [f"{d}-df" for d in DEFINITION_DOMAINS] + EXTRA_PAGES
    return slugs


def _walk_to_md(node: Tag, level: int = 0) -> str:
    """Convert a BeautifulSoup node tree to simplified markdown."""
    out: list[str] = []
    for child in node.children:
        if isinstance(child, NavigableString):
            text = str(child)
            if text.strip():
                out.append(text)
            continue
        if not isinstance(child, Tag):
            continue
        name = child.name.lower()
        if name in {"script", "style", "noscript", "nav", "footer", "header"}:
            continue
        if name in {"h1", "h2", "h3", "h4", "h5", "h6"}:
            depth = int(name[1])
            out.append(f"\n\n{'#' * depth} {child.get_text(strip=True)}\n\n")
        elif name == "table":
            out.append("\n\n" + _table_to_md(child) + "\n\n")
        elif name in {"ul", "ol"}:
            for li in child.find_all("li", recursive=False):
                out.append(f"- {li.get_text(' ', strip=True)}\n")
            out.append("\n")
        elif name == "p":
            out.append("\n" + child.get_text(" ", strip=True) + "\n")
        elif name == "pre":
            out.append("\n```\n" + child.get_text() + "\n```\n")
        elif name == "code":
            out.append(f"`{child.get_text()}`")
        elif name == "br":
            out.append("\n")
        elif name in {"div", "section", "article", "main", "span", "body", "html"}:
            out.append(_walk_to_md(child, level + 1))
        else:
            # Generic: emit text content
            text = child.get_text(" ", strip=True)
            if text:
                out.append(text)
    return "".join(out)


def _table_to_md(table: Tag) -> str:
    """Convert an HTML table to a markdown pipe table."""
    rows: list[list[str]] = []
    for tr in table.find_all("tr"):
        cells = []
        for cell in tr.find_all(["th", "td"]):
            text = cell.get_text(" ", strip=True).replace("|", r"\|").replace("\n", " ")
            cells.append(text)
        if cells:
            rows.append(cells)
    if not rows:
        return ""
    # Pad to common width
    width = max(len(r) for r in rows)
    for r in rows:
        r.extend([""] * (width - len(r)))
    md_lines = ["| " + " | ".join(rows[0]) + " |"]
    md_lines.append("| " + " | ".join(["---"] * width) + " |")
    for r in rows[1:]:
        md_lines.append("| " + " | ".join(r) + " |")
    return "\n".join(md_lines)


def fetch_page(slug: str, *, force: bool = False) -> Path:
    """Fetch and convert one OANDA doc page; return the cached path."""
    out_path = CACHE_DIR / f"{slug}.md"
    if out_path.exists() and not force:
        return out_path
    url = f"{BASE_URL}/{slug}/"
    print(f"GET {url} → {out_path.relative_to(REPO_ROOT)}")
    resp = httpx.get(url, timeout=30, follow_redirects=True)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")
    # OANDA's page structure: prefer #content, then main, then body.
    container = soup.find("div", id="content") or soup.find("main") or soup.body
    if container is None:
        container = soup
    md = _walk_to_md(container)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(f"# Source: {url}\n\n{md.strip()}\n", encoding="utf-8")
    return out_path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("slugs", nargs="*", help="Specific page slugs (e.g. order-ep). Default: all known pages.")
    parser.add_argument("--force", action="store_true", help="Re-fetch even if cached.")
    parser.add_argument("--sleep", type=float, default=0.5, help="Pause between requests (seconds).")
    args = parser.parse_args()

    slugs = args.slugs or _all_slugs()
    CACHE_DIR.mkdir(parents=True, exist_ok=True)

    # A failed fetch with a cached copy degrades to the stale copy (loudly);
    # a failed fetch with no cached copy is fatal. Status is recorded so the
    # pipeline summary can surface stale pages instead of silently trusting them.
    status: dict[str, str] = {}
    fatal = False
    for i, slug in enumerate(slugs):
        cached = CACHE_DIR / f"{slug}.md"
        try:
            fetch_page(slug, force=args.force)
            status[slug] = "fresh"
        except Exception as e:
            if cached.exists():
                mtime = datetime.fromtimestamp(cached.stat().st_mtime, tz=timezone.utc).date().isoformat()
                print(f"WARNING {slug}: fetch failed ({e}); using stale cache from {mtime}", file=sys.stderr)
                status[slug] = f"stale ({mtime})"
            else:
                print(f"FAILED {slug}: {e} (no cached copy available)", file=sys.stderr)
                status[slug] = "missing"
                fatal = True
        if i + 1 < len(slugs):
            time.sleep(args.sleep)

    (CACHE_DIR / "fetch-status.json").write_text(json.dumps(status, indent=2), encoding="utf-8")
    stale = sorted(s for s, v in status.items() if v.startswith("stale"))
    if stale:
        print(f"NOTE: {len(stale)} page(s) served from stale cache: {', '.join(stale)}", file=sys.stderr)
    return 1 if fatal else 0


if __name__ == "__main__":
    sys.exit(main())
