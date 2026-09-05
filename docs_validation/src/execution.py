"""Run trusted repository examples in disposable, offline worker processes."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field, ValidationError

from .models import ValidationIssue


class CodeBlock(BaseModel):
    start_line: int
    code: str


class ExecutedBlock(BaseModel):
    start_line: int
    output: str = ""
    output_truncated: bool = False
    request_count: int = 0
    issues: list[ValidationIssue] = Field(default_factory=list)


class WorkerEvent(BaseModel):
    kind: Literal["started", "result", "complete"]
    start_line: int | None = None
    result: ExecutedBlock | None = None


def run_document(file_path: Path, blocks: list[CodeBlock], *, timeout: float, mock_api_calls: bool) -> tuple[list[ExecutedBlock], list[ValidationIssue]]:
    """Preserve block context within a document, never across documents."""
    payload = {"file_path": str(file_path.resolve()), "blocks": [block.model_dump() for block in blocks], "mock_api_calls": mock_api_calls}
    timeout_expired = False
    with tempfile.TemporaryDirectory(prefix="fivetwenty-doc-example-") as directory:
        # Do not inherit credentials, proxy settings, Python startup hooks or .env.
        environment = {"PATH": os.defpath, "HOME": directory, "TMPDIR": directory, "PYTHONPATH": str(Path(__file__).resolve().parents[2]), "PYTHONIOENCODING": "utf-8", "PYTHONDONTWRITEBYTECODE": "1"}
        if "SYSTEMROOT" in os.environ:
            environment["SYSTEMROOT"] = os.environ["SYSTEMROOT"]
        try:
            completed = subprocess.run([sys.executable, "-m", "docs_validation.src.execution_worker"], input=json.dumps(payload), capture_output=True, text=True, cwd=directory, env=environment, timeout=timeout, check=False)
            stdout, stderr, returncode = completed.stdout, completed.stderr, completed.returncode
        except subprocess.TimeoutExpired as exc:
            timeout_expired = True
            stdout = exc.stdout.decode("utf-8", errors="replace") if isinstance(exc.stdout, bytes) else exc.stdout or ""
            stderr, returncode = "", -1
        except OSError as exc:
            return [], [ValidationIssue(file_path=file_path, line=blocks[0].start_line, rule_id="code_worker_failure", message=f"Cannot start example worker: {exc}")]

    results: list[ExecutedBlock] = []
    active_line = blocks[0].start_line
    complete = False
    try:
        for raw in stdout.splitlines():
            event = WorkerEvent.model_validate_json(raw)
            if event.kind == "started":
                active_line = event.start_line or active_line
            elif event.kind == "result" and event.result is not None:
                results.append(event.result)
            elif event.kind == "complete":
                complete = True
    except ValidationError:
        complete = False

    if timeout_expired:
        issues = [ValidationIssue(file_path=file_path, line=active_line, rule_id="code_timeout", message=f"Document execution exceeded {timeout:g} seconds; worker terminated", suggestion="Check for blocking calls, unclosed clients or unbounded loops")]
    elif returncode != 0 or not complete or [result.start_line for result in results] != [block.start_line for block in blocks]:
        issues = [ValidationIssue(file_path=file_path, line=active_line, rule_id="code_worker_failure", message=f"Example worker did not complete its report (exit {returncode}). {stderr[-2000:].strip()}")]
    else:
        issues = []
    return results, issues
