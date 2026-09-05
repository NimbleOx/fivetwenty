"""Validate published stream and order contracts against SDK wire records."""

from pathlib import Path
from typing import get_args

import pytest
import yaml
from jsonschema import Draft202012Validator, ValidationError

from fivetwenty.endpoints.orders import OrderRequest
from fivetwenty.models import OrderFillTransaction
from fivetwenty.models.orders import _ORDER_TYPE_MAP

SPEC = yaml.safe_load((Path(__file__).resolve().parents[2] / "docs/api-reference/openapi.yaml").read_text())


def validator(schema):
    return Draft202012Validator({**schema, "components": SPEC["components"]})


def test_order_enums_cover_all_sdk_request_and_response_types():
    request_types = {model.model_fields["type"].default.value for model in get_args(OrderRequest)}
    assert set(SPEC["components"]["schemas"]["OrderRequest"]["properties"]["type"]["enum"]) == request_types
    assert set(SPEC["components"]["schemas"]["Order"]["properties"]["type"]["enum"]) == set(_ORDER_TYPE_MAP)


@pytest.mark.parametrize("order_type", ["GUARANTEED_STOP_LOSS", "FIXED_PRICE"])
def test_order_schema_accepts_supported_order_variants(order_type):
    validator({"$ref": "#/components/schemas/Order"}).validate({"id": "123", "createTime": "2024-01-01T12:00:00Z", "state": "FILLED", "type": order_type})
    request = validator({"$ref": "#/components/schemas/OrderRequest"})
    if order_type == "FIXED_PRICE":
        with pytest.raises(ValidationError):
            request.validate({"type": order_type})
    else:
        request.validate({"type": order_type})


@pytest.mark.parametrize("endpoint", ["pricing", "transactions"])
def test_stream_schemas_describe_bytes_and_validate_each_bare_record(endpoint):
    operation = SPEC["paths"][f"/v3/accounts/{{accountID}}/{endpoint}/stream"]["get"]
    content = operation["responses"]["200"]["content"]
    assert set(content) == {"application/octet-stream"}
    media = content["application/octet-stream"]
    assert media["schema"] == {"type": "string", "format": "binary"}
    records = validator(media["x-oanda-record-schema"])
    heartbeat = {"type": "HEARTBEAT", "time": "2024-01-01T12:00:00Z"}
    if endpoint == "transactions":
        heartbeat["lastTransactionID"] = "123"
        transaction = OrderFillTransaction(id="123", time="2024-01-01T12:00:00Z", userID=1, accountID="offline-account", batchID="123", orderID="122", instrument="EUR_USD", units="1", price="1.1", pl="0")
        payload = transaction.model_dump(mode="json", by_alias=True, exclude_none=True)
        records.validate(payload)
        with pytest.raises(ValidationError):
            records.validate({"type": "TRANSACTION", "transaction": payload})
    else:
        records.validate({"type": "PRICE", "instrument": "EUR_USD", "time": "2024-01-01T12:00:00Z", "status": "tradeable", "bids": [], "asks": []})
    records.validate(heartbeat)
