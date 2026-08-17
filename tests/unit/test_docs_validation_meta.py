"""Tests for the docs_validation parity harness meta checks.

Covers:
  - check_docs_meta: default normalization, default drift, source-anchor drift, main()
  - live_oanda_fetch: fetch-status degradation (fresh / stale / missing)
  - run_domain: missing-doc-page P1 marker and BLOCKED-file lifecycle
  - run_all: critical-findings summary scanning
"""

import json
import re
import sys
from pathlib import Path
from typing import Any

import pytest

from docs_validation.src.parity import build_inventory, check_docs_meta, live_oanda_fetch, run_all, run_domain
from docs_validation.src.parity.check_docs_meta import _check_anchors, _check_defaults, _find_symbol_line, _normalize_default
from docs_validation.src.parity.run_all import _count_critical_findings

# ---------------------------------------------------------------------------
# check_docs_meta._normalize_default
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("'PENDING'", "pending"),
        ("PENDING", "pending"),
        ("Decimal('1.0')", "1.0"),
        ('Decimal("1.0")', "1.0"),
        ("1.0", "1.0"),
        ("1", "1.0"),
        ("TimeInForce.GTC", "gtc"),
        ("GTC", "gtc"),
        ("True", "true"),
        ("true", "true"),
        ("30.0", "30.0"),
        ("30", "30.0"),
        ("`50`", "50.0"),
        ("ALL", "all"),
    ],
)
def test_normalize_default(raw: str, expected: str) -> None:
    assert _normalize_default(raw) == expected


@pytest.mark.parametrize(
    ("doc_form", "sig_form"),
    [
        ("PENDING", "'PENDING'"),
        ("1.0", "Decimal('1.0')"),
        ("1", "Decimal('1.0')"),
        ("GTC", "TimeInForce.GTC"),
        ("true", "True"),
        ("30", "30.0"),
    ],
)
def test_normalize_default_equates_doc_and_signature_forms(doc_form: str, sig_form: str) -> None:
    assert _normalize_default(doc_form) == _normalize_default(sig_form)


# ---------------------------------------------------------------------------
# check_docs_meta._check_defaults / _check_anchors / main
# ---------------------------------------------------------------------------


def _meta_env(tmp_path: Path, monkeypatch) -> tuple[Path, Path]:
    """Point check_docs_meta at temp cache/report dirs; return (cache_dir, reports_dir)."""
    cache = tmp_path / "cache"
    reports = tmp_path / "reports"
    cache.mkdir()
    monkeypatch.setattr(check_docs_meta, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(check_docs_meta, "CACHE_DIR", cache)
    monkeypatch.setattr(check_docs_meta, "REPORTS_DIR", reports)
    return cache, reports


def _write_library(cache: Path, stem: str, methods: dict[str, dict[str, Any]]) -> None:
    payload = {"endpoint_classes": {"Endpoint": methods}}
    (cache / f"{stem}-endpoints-library.json").write_text(json.dumps(payload), encoding="utf-8")


def _write_docs(cache: Path, stem: str, methods: dict[str, Any], models: dict[str, Any] | None = None) -> None:
    payload = {"source_file": f"docs/api-reference/endpoints/{stem}.md", "methods": methods, "models": models or {}}
    (cache / f"{stem}-docs.json").write_text(json.dumps(payload), encoding="utf-8")


def _lib_method(**defaults: str | None) -> dict[str, Any]:
    return {"params": {"positional": [], "keyword_only": [{"name": name, "default": default} for name, default in defaults.items()]}}


def test_check_defaults_matching_and_prose_cases_produce_no_findings(tmp_path: Path, monkeypatch) -> None:
    cache, _ = _meta_env(tmp_path, monkeypatch)
    _write_library(cache, "orders", {"get_orders": _lib_method(state="'PENDING'", count="50", units=None)})
    _write_docs(
        cache,
        "orders",
        {
            "get_orders": {
                "params": [
                    {"name": "state", "description": "State filter (default: PENDING)"},
                    {"name": "count", "description": "Page size (default: 50, max: 500)"},
                    {"name": "units", "description": "Units to close (default: ALL for full closure)"},
                ],
            },
            "not_in_library": {"params": [{"name": "depth", "description": "(default: 5)"}]},
        },
    )

    assert _check_defaults() == []


def test_check_defaults_reports_mismatch_and_missing_signature_default(tmp_path: Path, monkeypatch) -> None:
    cache, _ = _meta_env(tmp_path, monkeypatch)
    _write_library(cache, "orders", {"get_orders": _lib_method(page_size="100", account_id=None)})
    _write_docs(
        cache,
        "orders",
        {
            "get_orders": {
                "params": [
                    {"name": "page_size", "description": "Page size (default: 500)"},
                    {"name": "account_id", "description": "Account (default: primary)"},
                ],
            },
        },
    )

    findings = _check_defaults()

    assert len(findings) == 2
    mismatch = next(f for f in findings if "page_size" in f)
    no_default = next(f for f in findings if "account_id" in f)
    assert mismatch.startswith("P2 ")
    assert "docs claim default `500` but signature default is `100`" in mismatch
    assert "docs claim default `primary` but the parameter has no default in the signature" in no_default


def test_find_symbol_line_locates_defs_and_classes(tmp_path: Path) -> None:
    target = tmp_path / "mod.py"
    target.write_text("# module\n\ndef foo():\n    pass\n\n\nclass Bar:\n    pass\n", encoding="utf-8")

    assert _find_symbol_line(target, "foo") == 3
    assert _find_symbol_line(target, "Bar") == 7
    assert _find_symbol_line(target, "missing") is None
    assert _find_symbol_line(tmp_path / "nope.py", "foo") is None


def test_check_anchors_reports_drift_missing_symbol_and_missing_file(tmp_path: Path, monkeypatch) -> None:
    cache, _ = _meta_env(tmp_path, monkeypatch)
    src = tmp_path / "pkg" / "mod.py"
    src.parent.mkdir()
    src.write_text("# module\n\ndef foo():\n    pass\n\n\nclass Bar:\n    pass\n", encoding="utf-8")
    blob = "https://github.com/example/repo/blob/main"
    _write_docs(
        cache,
        "orders",
        methods={
            "foo": {"source_link": f"{blob}/pkg/mod.py#L3"},  # exact match
            "baz": {"source_link": f"{blob}/pkg/mod.py#L3"},  # symbol not in file
            "ghost": {"source_link": f"{blob}/pkg/nope.py#L1"},  # nonexistent file
            "nolink": {"source_link": "../relative/link.py"},  # no #L anchor: skipped
        },
        models={"Bar": {"source_link": f"{blob}/pkg/mod.py#L20"}},  # off by 13 > tolerance
    )
    _write_docs(cache, "trades", methods={"foo": {"source_link": f"{blob}/pkg/mod.py#L6"}})  # off by exactly ANCHOR_TOLERANCE: ok

    findings = _check_anchors()

    assert len(findings) == 3
    assert all(f.startswith("P3 ") for f in findings)
    assert any("`baz`: symbol not found in `pkg/mod.py` (link anchor #L3)" in f for f in findings)
    assert any("`ghost`: source link targets nonexistent file `pkg/nope.py`" in f for f in findings)
    assert any("`Bar`: link anchor #L20 but symbol is defined at `pkg/mod.py:7`" in f for f in findings)


def test_check_docs_meta_main_writes_report_and_json_counts(tmp_path: Path, monkeypatch, capsys) -> None:
    cache, reports = _meta_env(tmp_path, monkeypatch)
    src = tmp_path / "pkg" / "mod.py"
    src.parent.mkdir()
    src.write_text("def foo():\n    pass\n", encoding="utf-8")
    _write_library(cache, "orders", {"get_orders": _lib_method(count="50")})
    _write_docs(
        cache,
        "orders",
        {
            "get_orders": {
                "params": [{"name": "count", "description": "(default: 100)"}],
                "source_link": "https://github.com/example/repo/blob/main/pkg/mod.py#L40",
            },
        },
    )

    rc = check_docs_meta.main()

    assert rc == 0
    report = (reports / "docs-meta-parity.md").read_text(encoding="utf-8")
    assert "## Default-value drift (P2) — 1 finding(s)" in report
    assert "## Source-anchor drift (P3) — 1 finding(s)" in report
    meta = json.loads((cache / "docs-meta.json").read_text(encoding="utf-8"))
    assert meta == {"P2_defaults": 1, "P3_anchors": 1}
    assert "1 default drift, 1 anchor drift" in capsys.readouterr().out


def test_check_docs_meta_main_clean_run_reports_zero_findings(tmp_path: Path, monkeypatch) -> None:
    cache, reports = _meta_env(tmp_path, monkeypatch)
    _write_library(cache, "orders", {"get_orders": _lib_method(count="50")})
    _write_docs(cache, "orders", {"get_orders": {"params": [{"name": "count", "description": "(default: 50)"}]}})

    assert check_docs_meta.main() == 0
    report = (reports / "docs-meta-parity.md").read_text(encoding="utf-8")
    assert "_No default-value drift._" in report
    assert "_No stale source anchors._" in report
    assert json.loads((cache / "docs-meta.json").read_text(encoding="utf-8")) == {"P2_defaults": 0, "P3_anchors": 0}


# ---------------------------------------------------------------------------
# live_oanda_fetch.main degradation
# ---------------------------------------------------------------------------


def _fetch_env(tmp_path: Path, monkeypatch, *, ok_slugs: set[str]) -> Path:
    """Point live_oanda_fetch at a temp cache and stub fetch_page to succeed only for ok_slugs."""
    cache = tmp_path / "oanda"
    cache.mkdir()
    monkeypatch.setattr(live_oanda_fetch, "CACHE_DIR", cache)

    def fake_fetch(slug: str, *, force: bool = False) -> Path:
        if slug not in ok_slugs:
            raise RuntimeError("boom")
        out = cache / f"{slug}.md"
        out.write_text("# fresh\n", encoding="utf-8")
        return out

    monkeypatch.setattr(live_oanda_fetch, "fetch_page", fake_fetch)
    return cache


def test_fetch_main_records_fresh_stale_and_missing_and_exits_nonzero(tmp_path: Path, monkeypatch, capsys) -> None:
    cache = _fetch_env(tmp_path, monkeypatch, ok_slugs={"order-ep"})
    (cache / "trade-df.md").write_text("# stale copy\n", encoding="utf-8")
    monkeypatch.setattr(sys, "argv", ["live_oanda_fetch", "order-ep", "trade-df", "primitives-df", "--sleep", "0"])

    rc = live_oanda_fetch.main()

    assert rc == 1
    status = json.loads((cache / "fetch-status.json").read_text(encoding="utf-8"))
    assert status["order-ep"] == "fresh"
    assert re.fullmatch(r"stale \(\d{4}-\d{2}-\d{2}\)", status["trade-df"])
    assert status["primitives-df"] == "missing"
    err = capsys.readouterr().err
    assert "WARNING trade-df: fetch failed (boom); using stale cache from" in err
    assert "FAILED primitives-df: boom (no cached copy available)" in err
    assert "1 page(s) served from stale cache: trade-df" in err


def test_fetch_main_exits_zero_when_only_stale(tmp_path: Path, monkeypatch, capsys) -> None:
    cache = _fetch_env(tmp_path, monkeypatch, ok_slugs={"order-ep"})
    (cache / "trade-df.md").write_text("# stale copy\n", encoding="utf-8")
    monkeypatch.setattr(sys, "argv", ["live_oanda_fetch", "order-ep", "trade-df", "--sleep", "0"])

    rc = live_oanda_fetch.main()

    assert rc == 0
    status = json.loads((cache / "fetch-status.json").read_text(encoding="utf-8"))
    assert status["order-ep"] == "fresh"
    assert status["trade-df"].startswith("stale (")
    assert "served from stale cache" in capsys.readouterr().err


# ---------------------------------------------------------------------------
# run_domain: missing-doc-page marker and BLOCKED lifecycle
# ---------------------------------------------------------------------------


def _minimal_report_inputs() -> dict[str, Any]:
    return {
        "lib_models": {"models": {}},
        "lib_eps": {"endpoint_classes": {}},
        "oanda_defs": {"definitions": {}},
        "oanda_eps": {"endpoints": []},
        "docs_eps": {"methods": {}},
        "lib_vs_oanda_md": "# diff\n\n## Models present in library but missing in oanda\n",
        "lib_vs_docs_mds": {},
        "lib_vs_docs_eps_md": None,
        "inventory": {},
        "has_oanda_endpoint": True,
    }


def test_assemble_domain_report_emits_p1_marker_for_missing_doc_page(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(run_domain, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(run_domain, "REPORTS_DIR", tmp_path / "reports")

    result = run_domain.assemble_domain_report(
        domain="instruments",
        missing_doc_pages=["docs/api-reference/endpoints/instruments.md"],
        **_minimal_report_inputs(),
    )

    content = (tmp_path / "reports" / "instruments-parity.md").read_text(encoding="utf-8")
    assert result["path"] == str(tmp_path / "reports" / "instruments-parity.md")
    assert "> **P1 — documentation page missing:** `docs/api-reference/endpoints/instruments.md` does not exist." in content


def test_assemble_domain_report_without_missing_pages_has_no_p1_marker(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(run_domain, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(run_domain, "REPORTS_DIR", tmp_path / "reports")

    run_domain.assemble_domain_report(domain="orders", missing_doc_pages=[], **_minimal_report_inputs())

    content = (tmp_path / "reports" / "orders-parity.md").read_text(encoding="utf-8")
    assert "P1 — documentation page missing" not in content


def test_run_domain_main_unlinks_stale_blocked_marker_on_success(tmp_path: Path, monkeypatch) -> None:
    reports = tmp_path / "reports"
    reports.mkdir()
    (reports / "BLOCKED-orders.md").write_text("# Blocked: orders\n\nold failure\n", encoding="utf-8")
    monkeypatch.setattr(run_domain, "REPORTS_DIR", reports)
    monkeypatch.setattr(build_inventory, "build", dict)
    monkeypatch.setattr(run_domain, "run_domain", lambda domain, *, inventory: {"path": "unused"})
    monkeypatch.setattr(sys, "argv", ["run_domain", "orders"])

    rc = run_domain.main()

    assert rc == 0
    assert not (reports / "BLOCKED-orders.md").exists()


def test_run_domain_main_writes_blocked_marker_on_failure(tmp_path: Path, monkeypatch, capsys) -> None:
    reports = tmp_path / "reports"
    monkeypatch.setattr(run_domain, "REPORTS_DIR", reports)
    monkeypatch.setattr(build_inventory, "build", dict)

    def _boom(domain: str, *, inventory: dict[str, Any]) -> dict[str, Any]:
        raise SystemExit("extraction failed")

    monkeypatch.setattr(run_domain, "run_domain", _boom)
    monkeypatch.setattr(sys, "argv", ["run_domain", "orders"])

    rc = run_domain.main()

    assert rc == 2
    blocked = (reports / "BLOCKED-orders.md").read_text(encoding="utf-8")
    assert blocked == "# Blocked: orders\n\nextraction failed\n"
    assert "BLOCKED on orders: extraction failed" in capsys.readouterr().err


# ---------------------------------------------------------------------------
# run_all._count_critical_findings
# ---------------------------------------------------------------------------


def test_count_critical_findings_scans_all_summary_sources(tmp_path: Path, monkeypatch) -> None:
    reports = tmp_path / "reports"
    cache = tmp_path / "parity"
    oanda = tmp_path / "oanda"
    for d in (reports, cache, oanda):
        d.mkdir()
    monkeypatch.setattr(run_all, "REPORTS_DIR", reports)
    monkeypatch.setattr(run_all, "CACHE_DIR", cache)
    monkeypatch.setattr(run_all, "OANDA_CACHE", oanda)

    (reports / "instruments-parity.md").write_text(
        "# Instruments Parity Report\n\n> **P1 — documentation page missing:** `docs/api-reference/endpoints/instruments.md` does not exist.\n",
        encoding="utf-8",
    )
    (cache / "docs-meta.json").write_text(json.dumps({"P2_defaults": 2, "P3_anchors": 1}), encoding="utf-8")
    (oanda / "fetch-status.json").write_text(json.dumps({"order-ep": "fresh", "trade-df": "stale (2026-08-01)"}), encoding="utf-8")
    (cache / "field-validation.json").write_text(json.dumps({"summary": {"P0": 3, "P1": 1}}), encoding="utf-8")

    count, findings = _count_critical_findings()

    assert count == 3
    joined = "\n".join(findings)
    assert "instruments-parity.md: P1 missing documentation page docs/api-reference/endpoints/instruments.md" in joined
    assert "oanda cache: `trade-df` is stale (2026-08-01)" in joined
    assert "docs-meta-parity.md: 2 P2 default-value drift items" in joined
    assert "docs-meta-parity.md: 1 P3 stale source anchors" in joined
    assert "field-validation.md: 3 P0 field-level drift items" in joined
    assert "field-validation.md: 1 P1 enum/primitive drift items" in joined
    assert not any("order-ep" in line for line in findings)


def test_count_critical_findings_clean_environment_returns_nothing(tmp_path: Path, monkeypatch) -> None:
    reports = tmp_path / "reports"
    cache = tmp_path / "parity"
    oanda = tmp_path / "oanda"
    for d in (reports, cache, oanda):
        d.mkdir()
    monkeypatch.setattr(run_all, "REPORTS_DIR", reports)
    monkeypatch.setattr(run_all, "CACHE_DIR", cache)
    monkeypatch.setattr(run_all, "OANDA_CACHE", oanda)
    (reports / "orders-parity.md").write_text("# Orders Parity Report\n\nAll clean.\n", encoding="utf-8")
    (oanda / "fetch-status.json").write_text(json.dumps({"order-ep": "fresh"}), encoding="utf-8")
    (cache / "docs-meta.json").write_text(json.dumps({"P2_defaults": 0, "P3_anchors": 0}), encoding="utf-8")
    (cache / "field-validation.json").write_text(json.dumps({"summary": {"P0": 0, "P1": 0}}), encoding="utf-8")

    assert _count_critical_findings() == (0, [])
