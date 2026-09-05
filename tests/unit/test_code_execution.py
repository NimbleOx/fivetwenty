"""The documentation runner must exercise actual SDK contracts and fail reliably."""

import json
import os
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pytest
from click.testing import CliRunner

from docs_validation.src import cli
from docs_validation.src.models import FileInfo
from docs_validation.src.validators.code_execution import CodeExecutionValidator

ROOT = Path(__file__).resolve().parents[2]


def validate(tmp_path, code, **options):
    path = tmp_path / "example.md"
    content = f"# Example\n\n```python\n{code}\n```\n"
    path.write_text(content)
    return CodeExecutionValidator().validate_file(FileInfo(path=path, size_bytes=path.stat().st_size, modified_time=0), content, options)


@pytest.mark.parametrize(
    "name",
    [
        "README.md",
        "docs/index.md",
        "docs/guides/understanding/environments.md",
        "docs/tutorials/getting-started/authentication.md",
        "docs/tutorials/getting-started/first-trade.md",
        "docs/tutorials/basic-trading/complete-system.md",
        "docs/tutorials/streaming-data.md",
        "docs/api-reference/endpoints/pricing.md",
        "docs/guides/practical-solutions/handle-connection-failures.md",
        "docs/guides/practical-solutions/setup-live-trading.md",
    ],
)
def test_previously_failing_published_documents_use_real_sdk(tmp_path, name):
    path = ROOT / name
    result = CodeExecutionValidator().validate_file(FileInfo(path=path, size_bytes=0, modified_time=0), path.read_text(), {})
    assert result.passed, result.issues
    assert result.metadata["executed_block_count"] > 0
    assert result.metadata["skipped_block_count"] == 0


@pytest.mark.parametrize(
    ("code", "expected"),
    [
        ("from fivetwenty import MissingPublicExport", "ImportError"),
        ("from fivetwenty import Client\nwith Client() as client:\n    client.accounts.nonexistent_method()", "AttributeError"),
        ("from fivetwenty import Client\nwith Client() as client:\n    client.accounts.get_accounts(unknown_argument=True)", "TypeError"),
        ('from fivetwenty.models import MarketOrderRequest\nMarketOrderRequest(instrument="EUR_USD", units="invalid")', "ValidationError"),
        ('import httpx\nhttpx.Client(transport=object()).get("https://api-fxpractice.oanda.com/v3/accounts")', "AttributeError"),
        (
            'import httpx\nfrom fivetwenty import Client\ntransport = httpx.AsyncClient(base_url="https://offline.example.test/v3", transport=httpx.MockTransport(lambda request: httpx.Response(200, json={"accounts": [{"id": None}]})))\nwith Client(transport=transport) as client:\n    client.accounts.get_accounts()',
            "ValidationError",
        ),
    ],
)
def test_broken_sdk_usage_and_invalid_response_payloads_fail(tmp_path, code, expected):
    result = validate(tmp_path, code)
    assert not result.passed
    assert expected in result.issues[0].message
    assert result.metadata["skipped_block_count"] == 0


def test_real_types_and_explicit_mock_transports_are_preserved(tmp_path):
    result = validate(
        tmp_path,
        """from datetime import datetime
from decimal import Decimal
from fivetwenty import Client, Environment
import httpx
with Client() as client:
    assert client.config.environment is Environment.PRACTICE
    account = client.accounts.get_account_summary(client.account_id)["account"]
    assert isinstance(account.balance, Decimal)
    assert isinstance(account.created_time, datetime)
transport = httpx.AsyncClient(base_url="https://offline.example.test/v3", transport=httpx.MockTransport(lambda request: httpx.Response(200, json={"accounts": [{"id": "custom", "tags": []}]})))
with Client(transport=transport) as client:
    assert client.accounts.get_accounts()[0].id == "custom"
print("real SDK")""",
    )
    assert result.passed, result.issues
    assert result.metadata["http_request_count"] == 1
    assert result.metadata["execution_results"][0]["output"] == "real SDK\n"


@pytest.mark.parametrize(
    "operation",
    [
        'httpx.get("https://unexpected.example.test/v3/accounts")',
        'httpx.get("https://api-fxpractice.oanda.com/v3/accounts/123/orders/42/unknown")',
        'httpx.delete("https://api-fxpractice.oanda.com/v3/accounts")',
        'socket.getaddrinfo("unexpected.example.test", 443)',
        'subprocess.run([sys.executable, "-c", "raise RuntimeError()"], check=True)',
    ],
)
def test_unexpected_requests_and_external_operations_fail_even_when_caught(tmp_path, operation):
    result = validate(tmp_path, f"import httpx, socket, subprocess, sys\ntry:\n    {operation}\nexcept Exception:\n    pass")
    assert not result.passed
    assert result.issues[0].rule_id == "code_external_operation"
    assert result.issues[0].line == 6


def test_disabling_fixtures_never_enables_real_http(tmp_path):
    result = validate(tmp_path, 'import httpx\nhttpx.get("https://api-fxpractice.oanda.com/v3/accounts")', mock_api_calls=False)
    assert not result.passed
    assert "HTTP requests are disabled" in result.issues[0].message


@pytest.mark.parametrize("dotenv_module", ["dotenv", "dotenv.main"])
def test_worker_environment_files_and_modules_are_isolated(tmp_path, monkeypatch, dotenv_module):
    monkeypatch.setenv("PRIVATE_PARENT_CREDENTIAL", "must-not-be-inherited")
    monkeypatch.setenv("LIVE_FIVETWENTY_OANDA_TOKEN", "must-not-be-inherited")
    dotenv = tmp_path / ".env"
    dotenv.write_text("FIVETWENTY_OANDA_TOKEN=must-not-be-loaded\n")
    import fivetwenty

    original = fivetwenty
    code = f"""import os, sys
from pathlib import Path
from {dotenv_module} import load_dotenv, dotenv_values
assert "PRIVATE_PARENT_CREDENTIAL" not in os.environ
assert load_dotenv({str(dotenv)!r}, override=True) is False
assert dotenv_values({str(dotenv)!r}) == {{}}
assert "must-not" not in os.environ["FIVETWENTY_OANDA_TOKEN"]
assert "must-not" not in os.environ["LIVE_FIVETWENTY_OANDA_TOKEN"]
assert Path.cwd() != Path({str(ROOT)!r})
Path("worker-created-file").write_text("local")
os.environ["WORKER_STATE"] = "changed"
sys.modules["fivetwenty"] = None
print(Path.cwd())"""
    result = validate(tmp_path, code)
    assert result.passed, result.issues
    directory = Path(result.metadata["execution_results"][0]["output"].strip())
    assert not directory.exists()
    assert "WORKER_STATE" not in os.environ
    assert sys.modules["fivetwenty"] is original


def test_document_blocks_share_context_and_errors_point_to_original_definition(tmp_path):
    path = tmp_path / "context.md"
    content = '# Context\n\n```python\nvalue = 41\ndef fail():\n    raise ValueError("from earlier block")\n```\n\n```python\nassert value + 1 == 42\nfail()\n```\n'
    result = CodeExecutionValidator().validate_file(FileInfo(path=path, size_bytes=0, modified_time=0), content, {})
    assert not result.passed
    assert result.issues[0].line == 6
    assert result.issues[0].context == '    raise ValueError("from earlier block")'
    assert result.metadata["executed_block_count"] == 2


def test_documents_do_not_share_interpreter_state_even_in_parallel(tmp_path):
    files = [tmp_path / f"{index}.md" for index in range(2)]
    contents = ['```python\nimport os\nassert "DOCUMENT_STATE" not in os.environ\nos.environ["DOCUMENT_STATE"] = "set"\n```'] * 2
    validator = CodeExecutionValidator()
    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(lambda args: validator.validate_file(FileInfo(path=args[0], size_bytes=0, modified_time=0), args[1], {}), zip(files, contents, strict=True)))
    assert all(result.passed for result in results), results


def test_hung_worker_times_out_at_active_block_and_keeps_prior_results(tmp_path):
    path = tmp_path / "timeout.md"
    content = '```python\nprint("finished first block")\n```\n\n```python\nwhile True:\n    pass\n```\n'
    result = CodeExecutionValidator().validate_file(FileInfo(path=path, size_bytes=0, modified_time=0), content, {"timeout_seconds": 3})
    assert not result.passed
    assert result.issues[0].rule_id == "code_timeout"
    assert result.issues[0].line == 6
    assert result.metadata["executed_block_count"] == 1
    assert result.metadata["execution_results"][0]["output"] == "finished first block\n"


@pytest.mark.parametrize("exit_code", [0, 7])
def test_abrupt_worker_exit_is_a_failure_even_with_zero_exit_code(tmp_path, exit_code):
    result = validate(tmp_path, f"import os\nos._exit({exit_code})")
    assert not result.passed
    assert result.issues[0].rule_id == "code_worker_failure"
    assert f"exit {exit_code}" in result.issues[0].message


def test_large_stdout_and_stderr_are_captured_with_bounded_size(tmp_path):
    result = validate(tmp_path, 'import sys\nprint("stdout")\nprint("stderr", file=sys.stderr)\nprint("x" * 20000)')
    assert result.passed
    captured = result.metadata["execution_results"][0]
    assert captured["output"].startswith("stdout\nstderr\n")
    assert len(captured["output"]) == 16000
    assert captured["output_truncated"] is True


@pytest.mark.parametrize("fence", ["```", "````", "~~~"])
def test_fences_and_explicit_skips_are_accounted_for(tmp_path, fence):
    content = f'<!-- validation: skip-execution -->\n{fence}python\nraise RuntimeError()\n{fence}\n\n{fence}python\nprint("ok")\n{fence}\n'
    result = CodeExecutionValidator().validate_file(FileInfo(path=tmp_path / "fences.md", size_bytes=0, modified_time=0), content, {})
    assert result.passed, result.issues
    assert result.metadata["executed_block_count"] == 1
    assert result.metadata["skipped_block_count"] == 1


def test_unclosed_python_block_fails_without_silent_omission(tmp_path):
    result = CodeExecutionValidator().validate_file(FileInfo(path=tmp_path / "open.md", size_bytes=0, modified_time=0), '```python\nprint("unfinished fence")\n', {})
    assert not result.passed
    assert result.issues[0].rule_id == "code_unclosed_block"


@pytest.mark.parametrize("timeout", [0, -1, float("inf"), float("nan")])
def test_invalid_timeout_is_reported(tmp_path, timeout):
    result = validate(tmp_path, "pass", timeout_seconds=timeout)
    assert not result.passed
    assert result.issues[0].rule_id == "code_execution_config"


@pytest.mark.parametrize("broken", [False, True])
def test_cli_runs_real_worker_and_propagates_example_failure(tmp_path, monkeypatch, broken):
    example = tmp_path / "example.md"
    example.write_text("```python\nfrom fivetwenty import " + ("MissingExport" if broken else "Environment") + "\n```\n")
    config = tmp_path / "validation.yml"
    config.write_text("validators:\n  code_execution:\n    enabled: true\n")
    monkeypatch.setattr(cli, "_generate_markdown_report", lambda summary: [])
    result = CliRunner().invoke(cli.cli, ["validate", "--config", str(config), "--files", str(example)])
    assert result.exit_code == int(broken), result.output


@pytest.mark.parametrize("failure", ["missing_worker", "invalid_report"])
def test_worker_infrastructure_failures_cannot_pass(tmp_path, monkeypatch, failure):
    def run(*args, **kwargs):
        if failure == "missing_worker":
            raise OSError("worker unavailable")
        return subprocess.CompletedProcess([], 0, stdout=json.dumps({"kind": "complete"}), stderr="")

    monkeypatch.setattr(subprocess, "run", run)
    result = validate(tmp_path, "pass")
    assert not result.passed
    assert result.issues[0].rule_id == "code_worker_failure"


def test_execution_config_selects_only_published_docs_and_root_readme(tmp_path):
    from docs_validation.src.config import ValidationConfig
    from docs_validation.src.engine import ValidationEngine

    paths = ["README.md", "docs/guide.md", "docs/nested/README.md", ".venv/package/README.md", "docs_validation/README.md", "external/README.md"]
    for name in paths:
        path = tmp_path / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("# Example\n")
    config = ValidationConfig.load_from_file(ROOT / "docs_validation/config/validation-execution.yml")
    discovered = ValidationEngine(config, tmp_path).discover_files()
    assert {file.path.relative_to(tmp_path).as_posix() for file in discovered} == set(paths[:3])


def test_report_exposes_execution_counts_and_failed_output(tmp_path):
    from docs_validation.src.models import ValidationSummary
    from docs_validation.src.reporters.markdown_reporter import MarkdownReporter

    result = validate(tmp_path, 'print("context before failure")\nraise ValueError("broken")')
    summary = ValidationSummary(total_files=1, total_validators=1, passed_files=0, failed_files=1, total_issues=1, error_count=1, warning_count=0, duration_ms=0, results=[result])
    report = tmp_path / "report.md"
    MarkdownReporter(project_root=tmp_path).generate_report(summary, result.issues, report)
    text = report.read_text()
    assert "Executed Python blocks:** 1" in text
    assert "HTTP requests served by shared fixtures:** 0" in text
    assert "context before failure" in text
    assert "**Line 5**" in text
