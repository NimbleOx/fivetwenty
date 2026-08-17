"""Execute the documentation notebooks headlessly against a mocked OANDA API.

Run via ``poe docs-validate-notebooks``. Every notebook under
``docs/examples/notebooks/`` is executed top to bottom in a throwaway copy; any
cell that raises fails the run. This is a local-only gate -- it is deliberately
not wired into CI, because a Jupyter kernel per notebook exceeds the memory
budget of the GitHub Actions runners.
"""

from __future__ import annotations

import json
import os
import shutil
import sys
import tempfile
import time
from pathlib import Path
from typing import Any

import nbformat
from nbclient import NotebookClient
from nbclient.exceptions import CellExecutionError
from notebook_mocks import AUDIT_ENV

REPO_ROOT = Path(__file__).resolve().parent.parent
NOTEBOOK_DIR = REPO_ROOT / "docs" / "examples" / "notebooks"
SCRIPTS_DIR = REPO_ROOT / "scripts"
KERNEL_NAME = "fivetwenty-notebooks"
CELL_TIMEOUT = 600

# Several notebooks wrap their API calls in `except Exception`, so a broken cell
# can print an error and still "succeed". These phrases only ever come from such
# a handler, so treat them as failures too.
SWALLOWED_FAILURE_MARKERS = ("Unexpected error", "unmocked path", "Traceback (most recent call last)")

# Injected as the notebook's first cell so it runs before any cell builds an
# AsyncClient. The notebooks talk to the real SDK and some of them place orders,
# so execution has to be redirected at the HTTP boundary: notebook_mocks.install()
# swaps an httpx.MockTransport into every httpx client constructed afterwards,
# which covers both the SDK's pooled REST client and the throwaway clients
# AsyncClient._stream builds per streaming connection. Everything above the
# transport -- endpoint methods, Pydantic parsing, streaming reconnection -- is
# the real code path, which is the point: stale SDK usage still fails the cell.
SETUP_CELL = """\
import matplotlib

matplotlib.use("Agg")

import notebook_mocks

notebook_mocks.install()
"""


def _write_kernelspec(root: Path) -> None:
    kernel_dir = root / "kernels" / KERNEL_NAME
    kernel_dir.mkdir(parents=True, exist_ok=True)
    spec = {
        "argv": [sys.executable, "-m", "ipykernel_launcher", "-f", "{connection_file}"],
        "display_name": KERNEL_NAME,
        "language": "python",
    }
    (kernel_dir / "kernel.json").write_text(json.dumps(spec), encoding="utf-8")


def _failing_cell(notebook: Any) -> tuple[int, str] | None:
    for index, cell in enumerate(notebook.cells):
        for output in cell.get("outputs", []):
            if output.get("output_type") == "error":
                return index, "\n".join(output.get("traceback", []))
    return None


def _swallowed_failures(notebook: Any) -> list[str]:
    reports: list[str] = []
    for index, cell in enumerate(notebook.cells):
        for output in cell.get("outputs", []):
            text = output.get("text", "") if output.get("output_type") == "stream" else ""
            reports.extend(f"cell {index - 1} printed a handled failure: {line.strip()}" for line in text.splitlines() if any(marker in line for marker in SWALLOWED_FAILURE_MARKERS))
    return reports


def _execute(path: Path, work_dir: Path) -> str | None:
    """Execute one notebook; return an error report, or None on success."""
    audit = work_dir / "unmocked-requests.log"
    os.environ[AUDIT_ENV] = str(audit)

    notebook = nbformat.read(path, as_version=4)
    notebook.cells.insert(0, nbformat.v4.new_code_cell(SETUP_CELL))
    notebook.metadata["kernelspec"] = {"name": KERNEL_NAME, "display_name": KERNEL_NAME, "language": "python"}

    client = NotebookClient(
        notebook,
        kernel_name=KERNEL_NAME,
        timeout=CELL_TIMEOUT,
        allow_errors=False,
        resources={"metadata": {"path": str(work_dir)}},
    )

    try:
        client.execute()
    except CellExecutionError as error:
        failure = _failing_cell(notebook)
        if failure is None:
            return str(error)
        index, traceback = failure
        return f"cell {index - 1} (source index in {path.name}) raised:\n{traceback}"

    reports = _swallowed_failures(notebook)
    if audit.exists():
        reports.append("requests the mock does not cover:\n  " + "\n  ".join(sorted(set(audit.read_text(encoding="utf-8").split("\n")))).strip())
    return "\n".join(reports) or None


def main() -> int:
    requested = sys.argv[1:]
    notebooks = sorted(NOTEBOOK_DIR.glob("*.ipynb"))
    if requested:
        wanted = {name if name.endswith(".ipynb") else f"{name}.ipynb" for name in requested}
        notebooks = [path for path in notebooks if path.name in wanted]

    if not notebooks:
        print(f"No notebooks found in {NOTEBOOK_DIR}")
        return 1

    os.environ["PYTHONPATH"] = os.pathsep.join(filter(None, [str(SCRIPTS_DIR), os.environ.get("PYTHONPATH", "")]))
    os.environ["MPLBACKEND"] = "Agg"

    failures: list[tuple[Path, str]] = []
    root = Path(tempfile.mkdtemp(prefix="fivetwenty-notebooks-"))
    os.environ["JUPYTER_PATH"] = str(root)
    _write_kernelspec(root)

    try:
        for path in notebooks:
            work_dir = root / path.stem
            work_dir.mkdir(parents=True, exist_ok=True)
            print(f"executing {path.relative_to(REPO_ROOT)} ... ", end="", flush=True)
            started = time.monotonic()
            report = _execute(path, work_dir)
            elapsed = time.monotonic() - started
            if report is None:
                print(f"ok ({elapsed:.1f}s)")
            else:
                print(f"FAILED ({elapsed:.1f}s)")
                failures.append((path, report))
    finally:
        shutil.rmtree(root, ignore_errors=True)

    if failures:
        for path, report in failures:
            print(f"\n{'=' * 72}\n{path.relative_to(REPO_ROOT)}\n{'=' * 72}\n{report}")
        print(f"\n{len(failures)} of {len(notebooks)} notebooks failed")
        return 1

    print(f"\nAll {len(notebooks)} notebooks executed cleanly")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
