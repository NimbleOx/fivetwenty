"""Runs every standalone script in docs/examples/scripts against a mocked OANDA API.

The scripts are shipped as runnable documentation, so the only way to catch stale
SDK usage in them is to execute them. Every httpx client built during a test is
routed through an httpx.MockTransport, so no request leaves the process and no
order is ever placed.
"""

import asyncio
import importlib.util
import inspect
from pathlib import Path
from types import ModuleType
from typing import Any

import httpx
import pytest

from docs_validation.src.example_api import ACCOUNT_ID, TOKEN, MockOandaApi

SCRIPTS_DIR = Path(__file__).resolve().parents[2] / "docs" / "examples" / "scripts"
SCRIPT_PATHS = sorted(SCRIPTS_DIR.glob("*.py"))


@pytest.fixture
def mock_oanda(monkeypatch: pytest.MonkeyPatch) -> MockOandaApi:
    """Force every httpx client created during the test through the mock transport."""
    api = MockOandaApi()
    transport = httpx.MockTransport(api.handle)

    monkeypatch.setenv("FIVETWENTY_OANDA_TOKEN", TOKEN)
    monkeypatch.setenv("FIVETWENTY_OANDA_ACCOUNT", ACCOUNT_ID)
    monkeypatch.setenv("FIVETWENTY_OANDA_ENVIRONMENT", "practice")

    for client_class in (httpx.AsyncClient, httpx.Client):
        original_init = client_class.__init__

        def patched_init(self: Any, *args: Any, _original_init: Any = original_init, **kwargs: Any) -> None:
            kwargs["transport"] = transport
            _original_init(self, *args, **kwargs)

        monkeypatch.setattr(client_class, "__init__", patched_init)

    return api


def _load_script(path: Path) -> ModuleType:
    spec = importlib.util.spec_from_file_location(f"example_script_{path.stem}", path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_every_example_script_is_covered() -> None:
    assert len(SCRIPT_PATHS) >= 11, f"expected the example scripts to be discovered under {SCRIPTS_DIR}"


@pytest.mark.parametrize("script_path", SCRIPT_PATHS, ids=lambda path: path.stem)
def test_example_script_runs_against_mocked_api(script_path: Path, mock_oanda: MockOandaApi) -> None:
    mock_oanda.empty_account = script_path.stem == "basic_usage"
    module = _load_script(script_path)
    main = module.main

    if inspect.iscoroutinefunction(main):
        asyncio.run(main())
    else:
        main()

    assert mock_oanda.unmocked == []
