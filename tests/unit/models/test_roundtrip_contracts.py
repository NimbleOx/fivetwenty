"""Generated round-trip contract tests for model serialization."""

from __future__ import annotations

import inspect
from datetime import datetime
from decimal import Decimal
from enum import Enum
from types import UnionType
from typing import Annotated, Any, Literal, Union, get_args, get_origin

import pytest
from pydantic import BaseModel

import fivetwenty.models.accounts as accounts_models
import fivetwenty.models.error_details as error_detail_models
import fivetwenty.models.instruments as instrument_models
import fivetwenty.models.orders as order_models
import fivetwenty.models.positions as position_models
import fivetwenty.models.pricing as pricing_models
import fivetwenty.models.streaming as streaming_models
import fivetwenty.models.trades as trade_models
import fivetwenty.models.transactions as transaction_models
from fivetwenty.models.base import ApiModel

MODEL_MODULES = (
    accounts_models,
    error_detail_models,
    instrument_models,
    order_models,
    position_models,
    pricing_models,
    streaming_models,
    trade_models,
    transaction_models,
)
MODEL_REBUILD_TYPES: dict[str, Any] = {
    "datetime": datetime,
    "Decimal": Decimal,
    "Position": position_models.Position,
    "CalculatedPositionState": position_models.CalculatedPositionState,
    "TradeSummary": trade_models.TradeSummary,
    "CalculatedTradeState": trade_models.CalculatedTradeState,
    "Transaction": transaction_models.Transaction,
}

_MISSING = object()


def _all_model_classes() -> list[type[BaseModel]]:
    classes: set[type[BaseModel]] = set()
    for module in MODEL_MODULES:
        for _, value in inspect.getmembers(module, inspect.isclass):
            if value in {BaseModel, ApiModel}:
                continue
            if issubclass(value, BaseModel) and value.__module__.startswith("fivetwenty.models."):
                value.model_rebuild(_types_namespace=MODEL_REBUILD_TYPES)
                classes.add(value)
    return sorted(classes, key=lambda cls: f"{cls.__module__}.{cls.__name__}")


def _contains_model_annotation(annotation: Any) -> bool:
    origin = get_origin(annotation)
    if origin is Annotated:
        return _contains_model_annotation(get_args(annotation)[0])
    if origin in {Union, UnionType, list, dict}:
        return any(_contains_model_annotation(arg) for arg in get_args(annotation) if arg is not type(None))
    return inspect.isclass(annotation) and issubclass(annotation, BaseModel)


def _sample_payload(model_cls: type[BaseModel], seen: set[type[BaseModel]] | None = None) -> dict[str, Any]:
    seen = set() if seen is None else seen
    if model_cls in seen:
        return {}

    seen.add(model_cls)
    payload: dict[str, Any] = {}
    for field_name, field_info in model_cls.model_fields.items():
        if not field_info.is_required() and _contains_model_annotation(field_info.annotation):
            continue
        value = _sample_value(field_name, field_info.annotation, seen)
        if value is _MISSING:
            continue
        alias = field_info.alias or field_name
        payload[alias] = value
    seen.remove(model_cls)
    return payload


def _sample_value(field_name: str, annotation: Any, seen: set[type[BaseModel]]) -> Any:  # noqa: PLR0911
    origin = get_origin(annotation)
    if origin is Annotated:
        return _sample_value(field_name, get_args(annotation)[0], seen)
    if origin in {Union, UnionType}:
        for arg in get_args(annotation):
            if arg is type(None):
                continue
            if _contains_model_annotation(arg) and inspect.isclass(arg) and arg in seen:
                continue
            return _sample_value(field_name, arg, seen)
        return None
    if origin is Literal:
        args = get_args(annotation)
        return args[0] if args else _MISSING
    if origin is list:
        args = get_args(annotation)
        return [_sample_value(field_name, args[0], seen)] if args else []
    if origin is dict:
        args = get_args(annotation)
        value_annotation = args[1] if len(args) == 2 else Any
        return {"key": _sample_value(field_name, value_annotation, seen)}

    if annotation is Any:
        return "value"
    if annotation is str:
        return _sample_string(field_name)
    if annotation is int:
        return 1
    if annotation is float:
        return 1.25
    if annotation is bool:
        return True
    if annotation is Decimal:
        return "1.2345"
    if annotation is datetime:
        return "2024-01-02T03:04:05Z"
    if inspect.isclass(annotation) and issubclass(annotation, Enum):
        return next(iter(annotation)).value
    if inspect.isclass(annotation) and issubclass(annotation, BaseModel):
        return _sample_payload(annotation, seen)

    return _sample_string(field_name)


def _sample_string(field_name: str) -> str:  # noqa: PLR0911
    if field_name in {"currency", "home_currency"} or field_name.endswith("_currency"):
        return "USD"
    if field_name == "instrument":
        return "EUR_USD"
    if field_name == "time" or field_name.endswith(("_time", "_timestamp")):
        return "2024-01-02T03:04:05Z"
    if field_name == "type":
        return "TEST"
    if field_name == "units":
        return "1000"
    if field_name == "price" or field_name.endswith("_price"):
        return "1.2345"
    if field_name == "email":
        return "user@example.com"
    if field_name == "url" or field_name.endswith("_url"):
        return "https://example.com/docs"
    if field_name == "method":
        return "GET"
    if field_name == "endpoint":
        return "/v3/accounts"
    if field_name == "ip_address":
        return "127.0.0.1"
    return f"{field_name}-value"


@pytest.mark.parametrize("model_cls", _all_model_classes(), ids=lambda cls: f"{cls.__module__}.{cls.__name__}")
def test_pydantic_models_round_trip_api_payloads(model_cls: type[BaseModel]) -> None:
    payload = _sample_payload(model_cls)

    model = model_cls.model_validate(payload)
    dumped = model.model_dump(by_alias=True, mode="json")
    reparsed = model_cls.model_validate(dumped)

    assert reparsed.model_dump(by_alias=True, mode="json") == dumped


@pytest.mark.parametrize(("transaction_type", "model_cls"), transaction_models._TRANSACTION_TYPE_MAP.items())
def test_account_changes_preserve_every_transaction_subtype(transaction_type: str, model_cls: type[BaseModel]) -> None:
    """Every supported transaction keeps its fields inside the base-typed collection."""
    payload = {**_sample_payload(model_cls), "type": transaction_type}
    standalone = model_cls.model_validate(payload)
    changes = accounts_models.AccountChanges.model_validate({"transactions": [payload]})

    assert type(changes.transactions[0]) is model_cls
    dumped = changes.model_dump(by_alias=True, mode="json", exclude_none=True)
    assert dumped["transactions"] == [standalone.model_dump(by_alias=True, mode="json", exclude_none=True)]
    reparsed = accounts_models.AccountChanges.model_validate_json(changes.model_dump_json(by_alias=True))
    assert type(reparsed.transactions[0]) is model_cls
    assert reparsed.transactions[0] == standalone
