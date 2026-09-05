"""Independent source fixtures keep parity checks from agreeing on empty data."""

import pytest

from docs_validation.src.parity import extract_endpoints, extract_oanda_md, extract_pydantic, run_docs_surface


def test_endpoint_extraction_keeps_wire_calls_defaults_and_optional_response_keys(tmp_path, monkeypatch):
    monkeypatch.setattr(extract_endpoints, "REPO_ROOT", tmp_path)
    path = tmp_path / "endpoints.py"
    path.write_text("""from typing import TypedDict
class Reply(TypedDict, total=False):
    orderID: str
class ExampleEndpoints:
    async def get(self, account: str, *, count: int = 5) -> Reply:
        return await self._client._request("GET", f"/accounts/{account}/orders", params={"count": count})
    async def stream(self, account: str):
        async for item in self._client._stream(path=f"/accounts/{account}/stream"):
            yield item
""")
    result = extract_endpoints.extract_module(path)
    methods = result["endpoint_classes"]["ExampleEndpoints"]
    assert methods["get"]["params"]["keyword_only"] == [{"name": "count", "annotation": "int", "default": "5"}]
    assert methods["get"]["request_calls"][0]["verb"] == "GET"
    assert "{account}" in methods["get"]["request_calls"][0]["path_template"]
    assert methods["stream"]["request_calls"][0]["via"] == "_stream"
    assert result["typeddicts"]["Reply"]["total"] == "False"


def test_model_extraction_preserves_aliases_defaults_inheritance_and_enum_values(tmp_path, monkeypatch):
    monkeypatch.setattr(extract_pydantic, "REPO_ROOT", tmp_path)
    path = tmp_path / "models.py"
    path.write_text("""from typing import TypeAlias
OrderID: TypeAlias = str
class Kind(str, Enum):
    LIMIT = "LIMIT"
class Order(ApiModel):
    id: str
    client_id: str | None = Field(None, alias="clientID")
    tags: list[str] = Field(default_factory=list)
class LimitOrder(Order):
    price: Decimal
__all__ = ["Order", "LimitOrder", "Kind"]
""")
    result = extract_pydantic.extract_module(path)
    assert result["models"]["Order"]["id"]["optional"] is False
    assert result["models"]["Order"]["client_id"]["alias"] == "clientID"
    assert result["models"]["Order"]["client_id"]["optional"] is True
    assert result["models"]["Order"]["tags"]["default"] == "factory:list"
    assert result["model_bases"]["LimitOrder"] == ["Order"]
    assert result["type_aliases"]["OrderID"] == "str"
    assert set(result["enums"]["Kind"]["values"]) == {"LIMIT"}
    assert result["exports"] == ["Order", "LimitOrder", "Kind"]


def test_official_schema_fixture_distinguishes_required_and_defaulted_fields(tmp_path, monkeypatch):
    monkeypatch.setattr(extract_oanda_md, "REPO_ROOT", tmp_path)
    path = tmp_path / "order-df.md"
    path.write_text("""# Source: https://developer.oanda.com/rest-live-v20/order-df/

Order is an application/json object with the following Schema:
```
{
    id : (OrderID, required),
    price : (PriceValue),
    units : (DecimalNumber, default=1)
}
```
OrderState The current state of an order.
| Value | Description |
| --- | --- |
| PENDING | Active |
| CANCELLED | Cancelled |
""")
    result = extract_oanda_md.extract_definition(path)
    fields = {field["name"]: field for field in result["definitions"]["Order"]["fields"]}
    assert fields["id"]["required"] is True
    assert fields["price"]["required"] is False
    assert fields["units"]["default"] == "1"
    assert result["definitions"]["OrderState"]["enum_values"] == ["PENDING", "CANCELLED"]


@pytest.mark.parametrize("module", ["fivetwenty", "fivetwenty.models"])
def test_document_surface_flags_unknown_imports_and_methods(tmp_path, monkeypatch, module):
    monkeypatch.setattr(run_docs_surface, "REPO_ROOT", tmp_path)
    path = tmp_path / "example.md"
    path.write_text(f"from {module} import MissingType\nclient.orders.nonexistent()\nclient.orders.nonexistent()\n")
    surface = {"fivetwenty": {"AsyncClient"}, "fivetwenty.models": {"Trade"}, "__client_endpoints__": {"orders": {"get_orders"}}}
    results = run_docs_surface.scan_files([path], surface)
    assert len(results["example.md"]["imports"]) == 1
    assert "MissingType" in results["example.md"]["imports"][0]
    assert len(results["example.md"]["methods"]) == 1
    report = run_docs_surface.render_report("examples", results, 1)
    assert "Stale import refs: 1" in report
    assert "Stale method refs: 1" in report
