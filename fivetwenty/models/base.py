"""
Base model classes for OANDA API.

Provides the foundational ApiModel class that all OANDA models inherit from.
"""

from datetime import datetime, timedelta
from decimal import Decimal
from typing import Any

from pydantic import BaseModel, ConfigDict, FieldSerializationInfo, field_serializer

from .._internal.datetime import format_datetime_for_oanda


class ApiModel(BaseModel):
    """Base model for OANDA API data structures with automatic Decimal handling."""

    model_config = ConfigDict(
        populate_by_name=True,
        use_enum_values=True,
        validate_assignment=True,
    )

    @field_serializer("*")
    def serialize_decimals_and_datetimes(self, value: Any, info: FieldSerializationInfo) -> Any:  # noqa: PLR0911
        """Convert Decimal and datetime fields to strings for API compatibility (recursive)."""
        if isinstance(value, Decimal):
            return format(value, "f")  # No scientific notation
        if isinstance(value, datetime):
            if info.context and info.context.get("datetime_format") == "UNIX":
                return format_datetime_for_oanda(value, "UNIX")
            # Use Z suffix for UTC timezone, otherwise include offset
            if value.tzinfo and value.utcoffset() == timedelta(0):
                return value.replace(tzinfo=None).isoformat() + "Z"
            return value.isoformat()
        if isinstance(value, dict):
            return {k: self.serialize_decimals_and_datetimes(v, info) for k, v in value.items()}
        if isinstance(value, list):
            return [self.serialize_decimals_and_datetimes(item, info) for item in value]
        return value

    @classmethod
    def _resolve_key(cls, key: str) -> str | None:
        """Resolve a field name or OANDA alias to the model's Python field name."""
        if key in cls.model_fields:
            return key
        for field_name, field_info in cls.model_fields.items():
            if field_info.alias == key:
                return field_name
        return None

    def __getitem__(self, key: str) -> Any:
        """Provide JSON-like access for SDK models using field names or OANDA aliases."""
        resolved = self._resolve_key(key)
        if resolved is None:
            raise KeyError(key)
        value = getattr(self, resolved)
        if value is None and resolved not in self.model_fields_set:
            raise KeyError(key)
        data = self.model_dump(by_alias=True, mode="json")
        serialized_key = type(self).model_fields[resolved].alias or resolved
        return data[serialized_key]

    def __contains__(self, key: object) -> bool:
        """Return whether a field or alias is present with a non-None value."""
        if not isinstance(key, str):
            return False
        try:
            self[key]
        except KeyError:
            return False
        return True

    def get(self, key: str, default: Any = None) -> Any:
        """Return a JSON-like value by field name or OANDA alias, like ``dict.get``."""
        try:
            return self[key]
        except KeyError:
            return default

    def __getattr__(self, name: str) -> Any:
        """Provide attribute compatibility for OANDA aliases such as ``tradeID``."""
        resolved = type(self)._resolve_key(name)
        if resolved is not None and resolved != name:
            return getattr(self, resolved)
        return super().__getattr__(name)  # type: ignore[misc]
