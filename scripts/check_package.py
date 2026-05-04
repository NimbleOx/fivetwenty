"""Build and smoke-check release artifacts without writing to dist/."""

from __future__ import annotations

import os
import re
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
PYPROJECT = REPO_ROOT / "pyproject.toml"
REQUIRED_WHEEL_FILES = {
    "fivetwenty/__init__.py",
    "fivetwenty/client.py",
    "fivetwenty/models/base.py",
    "fivetwenty/endpoints/accounts.py",
    "docs_validation/src/cli.py",
    "docs_validation/src/parity/field_validate.py",
}


def main() -> int:
    expected_version = _project_version()
    with tempfile.TemporaryDirectory(prefix="fivetwenty-package-") as tmp:
        out_dir = Path(tmp)
        _run([sys.executable, "-m", "build", "--outdir", str(out_dir)], cwd=REPO_ROOT)

        artifacts = sorted(out_dir.iterdir())
        wheels = sorted(out_dir.glob("*.whl"))
        sdists = sorted(out_dir.glob("*.tar.gz"))
        if len(wheels) != 1 or len(sdists) != 1:
            _fail(f"Expected one wheel and one sdist, found: {', '.join(path.name for path in artifacts)}")

        _run([sys.executable, "-m", "twine", "check", *(str(path) for path in artifacts)], cwd=REPO_ROOT)
        _assert_wheel_contents(wheels[0])
        _smoke_import_wheel(wheels[0], expected_version, out_dir)

        print("package check passed:")
        for artifact in artifacts:
            print(f"  - {artifact.name}")
    return 0


def _project_version() -> str:
    match = re.search(r'^version = "([^"]+)"', PYPROJECT.read_text(encoding="utf-8"), re.MULTILINE)
    if match is None:
        _fail("Could not find project.version in pyproject.toml.")
    return match.group(1)


def _assert_wheel_contents(wheel_path: Path) -> None:
    with zipfile.ZipFile(wheel_path) as wheel:
        names = set(wheel.namelist())
    missing = sorted(REQUIRED_WHEEL_FILES - names)
    if missing:
        _fail(f"{wheel_path.name} is missing expected package files: {', '.join(missing)}")


def _smoke_import_wheel(wheel_path: Path, expected_version: str, cwd: Path) -> None:
    code = """
import importlib.metadata

import docs_validation.src.cli
import docs_validation.src.parity.field_validate
import fivetwenty
from fivetwenty import AsyncClient, Client

assert AsyncClient is not None
assert Client is not None
assert importlib.metadata.version("fivetwenty") == fivetwenty.__version__
assert fivetwenty.__version__ == EXPECTED_VERSION
"""
    env = os.environ.copy()
    env["PYTHONPATH"] = str(wheel_path)
    _run([sys.executable, "-c", f"EXPECTED_VERSION = {expected_version!r}\n{code}"], cwd=cwd, env=env)


def _run(args: list[str], *, cwd: Path, env: dict[str, str] | None = None) -> None:
    subprocess.run(args, cwd=cwd, env=env, check=True)


def _fail(message: str) -> None:
    raise RuntimeError(message)


if __name__ == "__main__":
    sys.exit(main())
