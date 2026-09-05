"""Documentation checks must expose failures and every intentional skip."""

import subprocess
import sys
from pathlib import Path
from unittest.mock import Mock

import pytest
from click.testing import CliRunner

from docs_validation.src import cli as cli_module
from docs_validation.src.models import FileInfo, IssueSeverity
from docs_validation.src.validators.code_execution import CodeExecutionValidator
from docs_validation.src.validators.code_linting import CodeLintingValidator
from docs_validation.src.validators.code_typing import CodeTypingValidator

VALIDATORS = [CodeExecutionValidator, CodeLintingValidator, CodeTypingValidator]
INFO = FileInfo(path=Path("example.md"), size_bytes=0, modified_time=0)


@pytest.mark.parametrize("validator_type", VALIDATORS)
@pytest.mark.parametrize("code", ['print("Starting...")', 'label = "<token>"', "# TODO: improve this\nvalue = 1", "shape: tuple[int, ...] = (1,)", "result = values[..., 0]", "result = 1 < 2 > 0"])
def test_valid_python_is_not_a_placeholder(validator_type, code):
    assert not validator_type()._is_placeholder_code(code)


@pytest.mark.parametrize("validator_type", VALIDATORS)
@pytest.mark.parametrize("code", ["...", "def unfinished():\n    ..."])
def test_ellipsis_stubs_are_counted_as_skips(validator_type, code):
    result = validator_type().validate_file(INFO, f"```python\n{code}\n```", {})
    assert result.passed
    assert result.metadata["skipped_block_count"] == 1
    assert "ellipsis" in result.metadata["skipped_blocks"][0]["reason"]


@pytest.mark.parametrize("validator_type", [CodeLintingValidator, CodeTypingValidator])
def test_unavailable_tools_fail_even_for_a_single_line(monkeypatch, validator_type):
    run = Mock(side_effect=FileNotFoundError("tool missing"))
    monkeypatch.setattr(subprocess, "run", run)
    result = validator_type().validate_file(INFO, '```python\nvalue: int = "bad..."\n```', {})
    run.assert_called_once()
    assert not result.passed
    assert result.metadata["skipped_block_count"] == 0
    assert result.issues[0].severity == IssueSeverity.ERROR
    assert result.issues[0].rule_id.endswith("_unavailable")


@pytest.mark.parametrize("validator_type", [CodeLintingValidator, CodeTypingValidator])
def test_tool_failure_without_diagnostics_is_not_success(monkeypatch, validator_type):
    monkeypatch.setattr(subprocess, "run", Mock(return_value=subprocess.CompletedProcess([], 2, stdout="", stderr="bad configuration")))
    result = validator_type().validate_file(INFO, "```python\nvalue: int = 1\n```", {})
    assert not result.passed
    assert "bad configuration" in result.issues[0].message


@pytest.mark.parametrize("diagnostics", ["[]", "[{}]", '[{"filename": "different.py"}]'])
def test_lint_failure_without_matching_diagnostics_is_not_success(monkeypatch, diagnostics):
    monkeypatch.setattr(subprocess, "run", Mock(return_value=subprocess.CompletedProcess([], 2, stdout=diagnostics, stderr="")))
    result = CodeLintingValidator().validate_file(INFO, "```python\nvalue = 1\n```", {})
    assert not result.passed
    assert result.issues[0].rule_id == "code_linting_failed"


@pytest.mark.parametrize("tool_available", [False, True])
def test_cli_exit_status_reflects_code_validation(monkeypatch, tmp_path, tool_available):
    example = tmp_path / "example.md"
    example.write_text("```python\nvalue: int = 1\n```\n")
    config = tmp_path / "validation.yml"
    config.write_text("validators:\n  code_typing:\n    enabled: true\n")
    run = Mock(return_value=subprocess.CompletedProcess([], 0, stdout="", stderr="")) if tool_available else Mock(side_effect=FileNotFoundError("mypy unavailable"))
    monkeypatch.setattr(subprocess, "run", run)
    report = Mock(return_value=[])
    monkeypatch.setattr(cli_module, "_generate_markdown_report", report)
    result = CliRunner().invoke(cli_module.cli, ["validate", "--config", str(config), "--files", str(example)])
    assert result.exit_code == (0 if tool_available else 1), result.output
    report.assert_called_once()
    summary = report.call_args.args[0]
    assert summary.has_errors is not tool_available


@pytest.mark.parametrize("validator_type", [CodeLintingValidator, CodeTypingValidator])
def test_invalid_syntax_is_reported_when_checking_code(monkeypatch, validator_type):
    run = Mock()
    monkeypatch.setattr(subprocess, "run", run)
    result = validator_type().validate_file(INFO, "```python\nif\n```", {})
    assert not result.passed
    assert result.issues[0].rule_id.endswith("_syntax")
    run.assert_not_called()


def test_execution_does_not_skip_a_failure_after_printed_dots():
    result = CodeExecutionValidator().validate_file(INFO, '```python\nprint("Starting...")\nraise RuntimeError("sentinel failure")\n```', {"mock_api_calls": False})
    assert not result.passed
    assert result.metadata["skipped_block_count"] == 0
    assert "sentinel failure" in result.issues[0].message


def test_example_exit_cannot_terminate_validation_and_restores_loaded_modules():
    original = {name: module for name, module in sys.modules.items() if name == "fivetwenty" or name.startswith("fivetwenty.")}
    result = CodeExecutionValidator().validate_file(INFO, "```python\nimport sys\nsys.exit(0)\n```", {})
    assert not result.passed
    assert "SystemExit" in result.issues[0].message
    assert all(sys.modules.get(name) is module for name, module in original.items())


def test_excluded_file_reports_each_skipped_block():
    result = CodeExecutionValidator().validate_file(INFO, "```python\nvalue = 1\n```\n```python\nvalue = 2\n```", {"include_files": ["different.md"]})
    assert result.metadata["skipped"]
    assert result.metadata["skipped_block_count"] == 2
