from pathlib import Path

from docs_validation.src.parity import diff, extract_doc_tables
from docs_validation.src.parity.markdown_utils import parse_first_table_rows, split_sections


def test_markdown_utils_split_sections_and_parse_escaped_pipe_table() -> None:
    content = """# Title

## first_section
Body

| Field | Description |
| --- | --- |
| `price` | bid \\| ask |

## second_section
More body
"""

    sections = split_sections(content, 2)
    rows = parse_first_table_rows(sections[0][1])

    assert [title for title, _ in sections] == ["first_section", "second_section"]
    assert rows == [{"Field": "`price`", "Description": "bid | ask"}]


def test_extract_endpoint_doc_captures_endpoint_metadata(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(extract_doc_tables, "REPO_ROOT", tmp_path)
    doc_path = tmp_path / "docs" / "api-reference" / "endpoints" / "orders.md"
    doc_path.parent.mkdir(parents=True)
    link_icon = "\U0001f517"
    required_icon = "\u2705"
    optional_icon = "\u274c"
    doc_path.write_text(
        f"""# Orders

## get_orders

{link_icon} **Source**: [orders.py](../../../fivetwenty/endpoints/orders.py)
{link_icon} **OANDA Documentation**: [orders](https://developer.oanda.com/rest-live-v20/order-ep/)

**OANDA Endpoint**: `GET /v3/accounts/{{accountID}}/orders`

<!-- code-block: get-orders -->

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `account_id` | `AccountID` | {required_icon} | Account identifier |
| `state` | `[OrderStateFilter](../models/order-models.md)` | {optional_icon} | State filter |
""",
        encoding="utf-8",
    )

    result = extract_doc_tables.extract_endpoint_doc(doc_path)

    method = result["methods"]["get_orders"]
    assert result["source_file"] == "docs/api-reference/endpoints/orders.md"
    assert method["http_method"] == "GET"
    assert method["url_template"] == "/v3/accounts/{accountID}/orders"
    assert method["source_link"] == "../../../fivetwenty/endpoints/orders.py"
    assert method["oanda_link"] == "https://developer.oanda.com/rest-live-v20/order-ep/"
    assert method["code_block_anchor"] == "get-orders"
    assert method["params"] == [
        {
            "name": "account_id",
            "type": "`AccountID`",
            "required": True,
            "description": "Account identifier",
        },
        {
            "name": "state",
            "type": "`OrderStateFilter`",
            "required": False,
            "description": "State filter",
        },
    ]


def test_diff_models_reports_missing_extra_and_real_drift() -> None:
    left = {
        "Order": {
            "tradeID": {"type": "TradeID", "optional": False},
            "price": {"type": "Decimal", "optional": True},
            "clientExtensions": {"type": "ClientExtensions", "optional": True},
        },
    }
    right = {
        "Order": {
            "tradeID": {"type": "OrderID", "optional": False},
            "price": {"type": "DateTime", "optional": False},
            "timeInForce": {"type": "TimeInForce", "optional": False},
        },
    }

    result = diff.diff_models(left, right, "library", "oanda")
    order_diff = result["per_model"]["Order"]

    assert order_diff["missing"] == [{"name": "clientExtensions", "type": "ClientExtensions", "optional": True}]
    assert order_diff["extra"] == [{"name": "timeInForce", "type": "TimeInForce", "optional": False}]
    assert order_diff["type_drift"] == [{"name": "price", "library_type": "Decimal", "oanda_type": "DateTime"}]
    assert order_diff["opt_drift"] == [{"name": "price", "library_optional": True, "oanda_optional": False}]
