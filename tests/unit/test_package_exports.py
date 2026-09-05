"""Public imports work in isolation, without optional development dependencies."""

import subprocess
import sys

import pytest

import fivetwenty


def test_star_import_preserves_the_public_contract():
    expected = {"AccountConfig", "AccountConfigLoader", "AsyncClient", "Client", "ConfigValidator", "Environment", "ErrorCategory", "ErrorDetails", "ErrorSeverity", "FiveTwentyError", "FiveTwentyErrorCode", "StreamStall", "ValidationViolation", "__version__"}
    namespace = {}
    exec("from fivetwenty import *", namespace)
    assert set(fivetwenty.__all__) == expected
    assert set(namespace) - {"__builtins__"} == expected
    assert all(namespace[name] is getattr(fivetwenty, name) for name in expected)


@pytest.mark.parametrize("installed_metadata", [False, True])
def test_import_in_a_fresh_process_without_optional_dependencies(installed_metadata):
    code = f"""
import importlib.abc
import importlib.metadata
import sys

class RuntimeOnly(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):
        if fullname.split(".")[0] in {{"numpy", "pandas", "matplotlib", "pytest", "rich", "yaml", "docs_validation"}}:
            raise ModuleNotFoundError("Optional dependency unavailable: " + fullname)

sys.meta_path.insert(0, RuntimeOnly())
actual_version = importlib.metadata.version
def metadata_version(name):
    if name != "fivetwenty":
        return actual_version(name)
    if {installed_metadata!r}:
        return "9.8.7"
    raise importlib.metadata.PackageNotFoundError(name)
importlib.metadata.version = metadata_version

import fivetwenty
assert fivetwenty.__version__ == ("9.8.7" if {installed_metadata!r} else "0.0.0.dev0")
assert fivetwenty.AsyncClient.__module__ == "fivetwenty.client"
"""
    result = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, check=False, timeout=15)
    assert result.returncode == 0, result.stderr
