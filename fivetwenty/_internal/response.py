"""Runtime response containers used by endpoint methods."""

from __future__ import annotations

from typing import Any

from ..models.base import ApiModel

_UPPERCASE_SUFFIXES = {"id", "url", "uri", "ip", "api", "pl", "nav", "vwap"}
# OANDA pluralizes acronyms with a lowercase "s": tradeIDs, closingTransactionIDs.
_SPECIAL_SUFFIXES = {"ids": "IDs"}


def _convert_part(part: str) -> str:
    if part in _SPECIAL_SUFFIXES:
        return _SPECIAL_SUFFIXES[part]
    if part in _UPPERCASE_SUFFIXES:
        return part.upper()
    return part.title()


def _snake_to_oanda(name: str) -> str:
    parts = name.split("_")
    if not parts:
        return name
    return parts[0] + "".join(_convert_part(part) for part in parts[1:])


class ApiResponse(dict[str, Any]):
    """Dictionary response with compatibility attribute access.

    Endpoint responses remain dictionaries, but older integration code and user
    examples sometimes access transaction fields as snake_case attributes.
    """

    def __getattr__(self, name: str) -> Any:
        try:
            return self[name]
        except KeyError as exc:
            raise AttributeError(name) from exc

    def __getitem__(self, key: str) -> Any:
        if dict.__contains__(self, key):
            return dict.__getitem__(self, key)

        alias_key = _snake_to_oanda(key)
        if dict.__contains__(self, alias_key):
            return dict.__getitem__(self, alias_key)

        nested = self._single_nested_model()
        if nested is not None:
            try:
                return nested[key]
            except KeyError:
                pass

        raise KeyError(key)

    def __contains__(self, key: object) -> bool:
        if not isinstance(key, str):
            return False
        if dict.__contains__(self, key) or dict.__contains__(self, _snake_to_oanda(key)):
            return True
        nested = self._single_nested_model()
        return bool(nested is not None and key in nested)

    def get(self, key: str, default: Any = None) -> Any:
        try:
            return self[key]
        except KeyError:
            return default

    def _single_nested_model(self) -> ApiModel | None:
        for key in ("order", "trade", "position", "account", "transaction"):
            value = dict.get(self, key)
            if isinstance(value, ApiModel):
                return value
        return None
