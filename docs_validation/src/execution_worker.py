"""Child-process entry point for trusted, offline documentation examples.

Process isolation protects the validator's interpreter state. Network and process
guards prevent accidental external operations; this is not a hostile-code sandbox.
"""

from __future__ import annotations

import contextlib
import io
import json
import os
import sys
import traceback
from pathlib import Path
from typing import Any, NoReturn
from unittest.mock import patch

import dotenv
import httpx

from .example_api import ACCOUNT_ID, TOKEN, MockOandaApi
from .execution import CodeBlock, ExecutedBlock, WorkerEvent
from .models import ValidationIssue

OUTPUT_LIMIT = 16000


class CapturedOutput(io.StringIO):
    """Keep a bounded preview even when an example prints repeatedly."""

    truncated = False

    def write(self, text: str) -> int:
        remaining = max(0, OUTPUT_LIMIT - self.tell())
        if len(text) > remaining:
            self.truncated = True
        super().write(text[:remaining])
        return len(text)


def _source_line(file_path: str, fallback: int, frames: list[traceback.FrameSummary]) -> int:
    return next((frame.lineno or fallback for frame in reversed(frames) if frame.filename == file_path), fallback)


def main() -> None:
    payload = json.load(sys.stdin)
    file_path = payload["file_path"]
    blocks = [CodeBlock.model_validate(block) for block in payload["blocks"]]
    protocol = sys.stdout

    def emit(event: WorkerEvent) -> None:
        protocol.write(event.model_dump_json() + "\n")
        protocol.flush()

    api = MockOandaApi()
    api.empty_account = True
    violations: list[ValidationIssue] = []
    active_line = blocks[0].start_line

    def violation(message: str) -> NoReturn:
        line = _source_line(file_path, active_line, traceback.extract_stack())
        violations.append(ValidationIssue(file_path=Path(file_path), line=line, rule_id="code_external_operation", message=message))
        raise AssertionError(message)

    def audit(event: str, _args: tuple[Any, ...]) -> None:
        if event in {"socket.connect", "socket.getaddrinfo", "socket.sendto", "subprocess.Popen", "os.system", "os.posix_spawn", "os.fork", "os.exec"}:
            violation(f"External operation blocked during documentation execution: {event}")

    sys.addaudithook(audit)

    def handle(request: httpx.Request) -> httpx.Response:
        if not payload["mock_api_calls"]:
            violation("HTTP requests are disabled when mock_api_calls is false")
        try:
            return api.handle(request)
        except AssertionError as exc:
            violation(str(exc))

    transport = httpx.MockTransport(handle)
    with contextlib.ExitStack() as stack:
        for prefix in ("", "RESEARCH_", "MONITOR_", "LIVE_"):
            os.environ.update({prefix + "FIVETWENTY_OANDA_TOKEN": TOKEN, prefix + "FIVETWENTY_OANDA_ACCOUNT": ACCOUNT_ID, prefix + "FIVETWENTY_OANDA_ENVIRONMENT": "live" if prefix == "LIVE_" else "practice"})
        for module in (dotenv, dotenv.main):
            stack.enter_context(patch.object(module, "load_dotenv", return_value=False))
            stack.enter_context(patch.object(module, "dotenv_values", return_value={}))
        for client_class in (httpx.AsyncClient, httpx.Client):
            original = client_class.__init__

            def create(self: Any, *args: Any, _original: Any = original, **kwargs: Any) -> None:
                # Preserve explicit transports so invalid or independently mocked
                # transports exercise their actual behavior. Network guards apply.
                if kwargs.get("transport") is None:
                    kwargs["transport"] = transport
                kwargs["trust_env"] = False
                _original(self, *args, **kwargs)

            stack.enter_context(patch.object(client_class, "__init__", create))

        namespace: dict[str, Any] = {"__name__": "__main__", "__file__": file_path}
        for block in blocks:
            active_line = block.start_line
            emit(WorkerEvent(kind="started", start_line=active_line))
            output = CapturedOutput()
            issues: list[ValidationIssue] = []
            violations.clear()
            request_count = api.request_count
            try:
                with contextlib.redirect_stdout(output), contextlib.redirect_stderr(output):
                    # Padding keeps tracebacks accurate for functions defined in
                    # earlier blocks and called by later ones.
                    code = compile("\n" * (block.start_line - 1) + block.code, file_path, "exec")
                    exec(code, namespace)
            except BaseException as exc:
                line = exc.lineno if isinstance(exc, SyntaxError) else _source_line(file_path, block.start_line, traceback.extract_tb(exc.__traceback__))
                issues.append(ValidationIssue(file_path=Path(file_path), line=line, rule_id="code_runtime_error", message=f"Runtime error: {type(exc).__name__}: {str(exc)[:2000]}"))
            # A caught transport/operation failure must still fail the document.
            issues.extend(issue for issue in violations if not any(issue.message in error.message for error in issues))
            emit(WorkerEvent(kind="result", result=ExecutedBlock(start_line=block.start_line, output=output.getvalue(), output_truncated=output.truncated, request_count=api.request_count - request_count, issues=issues)))
        emit(WorkerEvent(kind="complete"))


if __name__ == "__main__":
    main()
