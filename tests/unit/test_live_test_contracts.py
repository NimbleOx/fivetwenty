"""Check explicit SDK calls in live tests before allowing expensive server runs."""

import ast
import inspect
from pathlib import Path

from fivetwenty.endpoints import accounts, instruments, orders, positions, pricing, trades, transactions


def test_explicit_integration_calls_match_public_sdk_signatures():
    endpoints = {"accounts": accounts.AccountEndpoints, "instruments": instruments.InstrumentEndpoints, "orders": orders.OrderEndpoints, "positions": positions.PositionEndpoints, "pricing": pricing.PricingEndpoints, "trades": trades.TradeEndpoints, "transactions": transactions.TransactionEndpoints}
    checked = 0
    for path in (Path(__file__).parents[1] / "integration").glob("test_*.py"):
        for node in ast.walk(ast.parse(path.read_text())):
            if not isinstance(node, ast.Call) or not isinstance(node.func, ast.Attribute) or not isinstance(node.func.value, ast.Attribute):
                continue
            surface = node.func.value
            if not isinstance(surface.value, ast.Name) or surface.value.id not in {"client", "sandbox_client", "trading_client"} or surface.attr not in endpoints:
                continue
            method = getattr(endpoints[surface.attr], node.func.attr)
            if any(isinstance(arg, ast.Starred) for arg in node.args) or any(keyword.arg is None for keyword in node.keywords):
                continue
            signature = inspect.signature(method)
            try:
                signature.bind(object(), *[object() for _ in node.args], **{keyword.arg: object() for keyword in node.keywords})
            except TypeError as exc:
                raise AssertionError(f"{path.name}:{node.lineno}: {exc}") from exc
            checked += 1
    assert checked >= 25
