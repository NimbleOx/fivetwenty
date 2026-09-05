"""Shared helpers for live integration tests."""

from __future__ import annotations

from typing import NoReturn

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
