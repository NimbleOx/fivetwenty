"""Shared helpers for live integration tests."""

from __future__ import annotations

from decimal import Decimal
from typing import Any, NoReturn

import pytest

_ENVIRONMENT_ERROR_TERMS = (
    "insufficient",
    "margin",
    "funds",
    "market closed",
    "trading disabled",
    "trading is disabled",
    "trading halted",
    "market halted",
    "instrument halted",
)

_TOLERATED_CLEANUP_TERMS = (
    "already cancelled",
    "already canceled",
    "already filled",
    "already closed",
    "does not exist",
    "not found",
    "not open",
    "cannot be found",
)


def is_environment_error(exc: Exception) -> bool:
    """Return whether an integration failure is caused by mutable market state."""
    message = str(exc).lower()
    return any(term in message for term in _ENVIRONMENT_ERROR_TERMS)


def skip_or_raise_environment_error(exc: Exception, context: str) -> NoReturn:
    """Skip known market-state failures and raise everything else."""
    if is_environment_error(exc):
        pytest.skip(f"{context} skipped due to live account or market state: {exc}")
    raise exc


def is_tolerated_cleanup_error(exc: Exception) -> bool:
    """Return whether cleanup failed because the resource is already gone."""
    if getattr(exc, "status", None) == 404:
        return True

    message = str(exc).lower()
    return any(term in message for term in _TOLERATED_CLEANUP_TERMS)


def cleanup_error_message(resource_type: str, resource_id: str, exc: Exception) -> str:
    """Format a cleanup error with enough context to repair account state."""
    return f"{resource_type} {resource_id}: {type(exc).__name__}: {exc}"


def mid_price_from_pricing_response(pricing_response: object, fallback: Decimal) -> Decimal:
    """Extract a midpoint price from OANDA pricing response shapes."""
    prices = _value(pricing_response, "prices")
    if not prices:
        return fallback

    price_data = prices[0]
    bids = _value(price_data, "bids")
    asks = _value(price_data, "asks")
    if bids and asks:
        bid = Decimal(str(_value(bids[0], "price")))
        ask = Decimal(str(_value(asks[0], "price")))
        return (bid + ask) / 2

    bid = _value(price_data, "bid")
    ask = _value(price_data, "ask")
    if bid is not None and ask is not None:
        return (Decimal(str(bid)) + Decimal(str(ask))) / 2

    mid = _value(price_data, "mid")
    return Decimal(str(mid)) if mid is not None else fallback


async def display_precision_for_instrument(client: Any, account_id: str, instrument: str) -> int:
    """Return the OANDA display precision for an account instrument."""
    instruments_response = await client.accounts.get_account_instruments(account_id, instruments=[instrument])
    instruments = _value(instruments_response, "instruments")
    if not instruments:
        raise AssertionError(f"Instrument {instrument} was not returned for account {account_id}")

    precision = _value(instruments[0], "display_precision")
    if precision is None:
        precision = _value(instruments[0], "displayPrecision")
    if precision is None:
        raise AssertionError(f"Instrument {instrument} did not include display precision")

    return int(precision)


def quantize_instrument_price(value: Decimal, display_precision: int) -> Decimal:
    """Round a price the same way OANDA represents instrument prices."""
    return value.quantize(Decimal(10) ** -display_precision)


def _value(source: object, key: str) -> object | None:
    if isinstance(source, dict):
        return source.get(key)
    value = getattr(source, key, None)
    if value is not None:
        return value
    try:
        return source[key]  # type: ignore[index]
    except (KeyError, TypeError, AttributeError):
        return None
