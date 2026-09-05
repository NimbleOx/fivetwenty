"""Parity reports must detect independent contract drift, including wire enum values."""

import json

import pytest

from docs_validation.src.parity import diff, extract_oanda_md, extract_pydantic, run_enums


def run_diff(tmp_path, monkeypatch, mode, left, right, right_source="oanda"):
    left_path, right_path, output = (tmp_path / name for name in ("left.json", "right.json", "report.md"))
    left_path.write_text(json.dumps(left))
    right_path.write_text(json.dumps(right))
    monkeypatch.setattr("sys.argv", ["parity-diff", mode, "--left", str(left_path), "--right", str(right_path), "--left-source", "library", "--right-source", right_source, "--out", str(output)])
    assert diff.main() == 0
    return output.read_text(), json.loads(output.with_suffix(".json").read_text())


def test_model_parity_reports_missing_extra_type_and_optionality_drift(tmp_path, monkeypatch):
    library = {"models": {"Order": {"trade_id": {"annotation": "TradeID", "optional": False}, "price": {"annotation": "Decimal", "optional": False}, "obsolete": {"annotation": "str"}}, "LibraryOnly": {}}}
    oanda = {"definitions": {"Order": {"fields": [{"name": "tradeID", "type": "TradeID", "required": True}, {"name": "price", "type": "bool", "required": False}, {"name": "newField", "type": "str"}]}, "ServerOnly": {"fields": []}}}
    report, result = run_diff(tmp_path, monkeypatch, "models", library, oanda)
    assert result["models_missing_in_right"] == ["LibraryOnly"]
    assert result["models_extra_in_right"] == ["ServerOnly"]
    fields = result["per_model"]["Order"]
    assert [field["name"] for field in fields["missing"]] == ["obsolete"]
    assert [field["name"] for field in fields["extra"]] == ["newField"]
    assert fields["type_drift"] == [{"name": "price", "library_type": "Decimal", "oanda_type": "bool"}]
    assert fields["opt_drift"] == [{"name": "price", "library_optional": False, "oanda_optional": True}]
    assert all(value in report for value in ("LibraryOnly", "ServerOnly", "obsolete", "newField", "Type drift", "Optionality drift"))


@pytest.mark.parametrize("right_source", ["docs", "oanda"])
def test_model_parity_accepts_attribute_aliases_and_documented_datetime_types(tmp_path, monkeypatch, right_source):
    library = {"models": {"Order": {"creation_time": {"annotation": "Optional[datetime]", "alias": "createTime", "optional": True}}}}
    right = {"models" if right_source == "docs" else "definitions": {"Order": {"fields": [{"name": "creation_time" if right_source == "docs" else "createTime", "type": "[DateTime](types.md)", "required": False}]}}}
    report, result = run_diff(tmp_path, monkeypatch, "models", library, right, right_source)
    assert all(not values for values in result["per_model"]["Order"].values())
    assert "No field-level drift" in report


def test_endpoint_parity_reports_route_parameter_and_type_changes(tmp_path, monkeypatch):
    library = {"endpoint_classes": {"Orders": {"get_orders": {"request_calls": [{"verb": "GET", "path_template": "/orders"}], "params": {"positional": [{"name": "account", "annotation": "str"}], "keyword_only": [{"name": "count", "annotation": "int"}]}}, "cancel_order": {}}}}
    docs = {"methods": {"get_orders": {"http_method": "POST", "url_template": "/stale", "params": [{"name": "count", "type": "bool"}, {"name": "obsolete", "type": "str"}]}, "stale_method": {}}}
    report, result = run_diff(tmp_path, monkeypatch, "endpoints", library, docs, "docs")
    assert result["methods_missing_in_right"] == ["cancel_order"]
    assert result["methods_extra_in_right"] == ["stale_method"]
    assert result["per_method"]["get_orders"] == {"verb_path_drift": {"library": "GET /orders", "docs": "POST /stale"}, "params_only_in_library": ["account"], "params_only_in_docs": ["obsolete"], "param_type_drift": [{"param": "count", "library_type": "int", "docs_type": "bool"}]}
    assert all(value in report for value in ("cancel_order", "stale_method", "Verb/path drift", "account", "obsolete", "Param type drift"))


@pytest.mark.parametrize(("right_values", "expected_drift"), [({"SAME_NAME": "'SELL'"}, True), ({"DIFFERENT_NAME": "'BUY'"}, False)])
def test_enum_diff_compares_serialized_values_instead_of_python_member_names(tmp_path, monkeypatch, right_values, expected_drift):
    report, _ = run_diff(tmp_path, monkeypatch, "enums", {"enums": {"Side": {"values": {"SAME_NAME": "'BUY'"}}}}, {"enums": {"Side": {"values": right_values}}}, "library")
    if expected_drift:
        assert "Values only in library: BUY" in report
        assert "Values only in library: SELL" in report
    else:
        assert "### Side" not in report


@pytest.mark.parametrize("server_value", ["BUY", "SELL"])
def test_cross_cutting_enum_report_extracts_source_values_and_detects_drift(tmp_path, monkeypatch, server_value):
    for module in (run_enums, extract_oanda_md, extract_pydantic):
        monkeypatch.setattr(module, "REPO_ROOT", tmp_path)
    cache = tmp_path / "cache"
    cache.mkdir()
    monkeypatch.setattr(run_enums, "OANDA_CACHE", cache)
    monkeypatch.setattr(run_enums, "REPORTS", tmp_path / "reports")
    models = tmp_path / "fivetwenty" / "models"
    models.mkdir(parents=True)
    (models / "enums.py").write_text("class Side(str, Enum):\n    PYTHON_MEMBER = 'BUY'\n")
    (cache / "order-df.md").write_text(f"Side The direction.\n| Value | Description |\n| --- | --- |\n| {server_value} | Direction |\n")
    run_enums.main()
    report = (tmp_path / "reports" / "enums-parity.md").read_text()
    assert "| OANDA enums (across all *-df pages) | 1 |" in report
    if server_value == "BUY":
        assert "No value-set drift" in report
    else:
        assert "Values in library but not OANDA: `BUY`" in report
        assert "Values in OANDA but not library: `SELL`" in report
