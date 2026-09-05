from pathlib import Path

from docs_validation.src import cli as cli_module
from docs_validation.src.models import FileInfo, IssueSeverity, ValidationIssue, ValidationResult, ValidationSummary
from docs_validation.src.reporters.markdown_reporter import MarkdownReporter
from docs_validation.src.validators.code_execution import CodeExecutionValidator
from docs_validation.src.validators.fragments import (
    FragmentTarget,
    find_fragment_marker,
    marker_skip_metadata,
    parse_fragment_marker,
)


def test_skip_linting_marker_does_not_skip_other_targets() -> None:
    marker = parse_fragment_marker("<!-- validation: skip-linting -->", 1)

    assert marker is not None
    assert marker.skips(FragmentTarget.LINTING)
    assert not marker.skips(FragmentTarget.TYPING)
    assert not marker.skips(FragmentTarget.EXECUTION)


def test_skip_marker_skips_all_code_targets() -> None:
    marker = parse_fragment_marker("<!-- validation: skip -->", 1)

    assert marker is not None
    assert all(marker.skips(target) for target in FragmentTarget)


def test_find_fragment_marker_uses_nearest_applicable_marker() -> None:
    lines = [
        "<!-- validation: skip-typing -->",
        "<!-- validation: skip-linting -->",
        "```python",
        "print('hello')",
        "```",
    ]

    marker = find_fragment_marker(lines, 3, FragmentTarget.TYPING)

    assert marker is not None
    assert marker.line_number == 1


def test_find_fragment_marker_ignores_markers_outside_lookback() -> None:
    lines = [
        "<!-- validation: skip -->",
        "",
        "",
        "",
        "```python",
        "print('hello')",
        "```",
    ]

    assert find_fragment_marker(lines, 5, FragmentTarget.LINTING) is None


def test_marker_skip_metadata_records_code_and_marker_lines() -> None:
    marker = parse_fragment_marker("<!-- fragment: placeholder credentials -->", 10)

    assert marker is not None
    assert marker_skip_metadata(marker, 12) == {
        "code_block_start_line": 12,
        "code_start_line": 13,
        "marker_line": 10,
        "marker": "<!-- fragment: placeholder credentials -->",
        "marker_kind": "all",
        "reason": "placeholder credentials",
    }


def test_code_execution_honors_skip_execution_marker() -> None:
    validator = CodeExecutionValidator()
    file_info = FileInfo(path=Path("example.md"), size_bytes=0, modified_time=0)
    content = "\n".join(
        [
            "<!-- validation: skip-execution -->",
            "```python",
            "raise RuntimeError('should not execute')",
            "```",
        ]
    )

    result = validator.validate_file(file_info, content, {})

    assert result.passed
    assert result.metadata["skipped_block_count"] == 1
    assert result.metadata["skipped_blocks"][0]["marker_kind"] == "execution"


def test_fragment_reporter_flags_validation_debt_wording_variants() -> None:
    reporter = MarkdownReporter()

    flagged_reasons = [
        "response indexing issues",
        "await outside function patterns",
        "f-string patterns",
        "type assignment and argument type issues",
    ]

    for reason in flagged_reasons:
        assert reporter._fragment_marker_needs_review(reason)


def test_fragment_reporter_outputs_audit_flag_section(tmp_path: Path) -> None:
    reporter = MarkdownReporter(project_root=Path.cwd())
    output_path = tmp_path / "validation-report.md"
    summary = ValidationSummary(
        total_files=1,
        total_validators=1,
        passed_files=1,
        failed_files=0,
        total_issues=0,
        error_count=0,
        warning_count=0,
        duration_ms=1.0,
        results=[
            ValidationResult(
                validator_name="code_typing",
                file_path=Path("docs/example.md"),
                passed=True,
                metadata={
                    "skipped_blocks": [
                        {
                            "code_block_start_line": 10,
                            "marker_line": 9,
                            "marker": "<!-- fragment: response indexing issues -->",
                            "marker_kind": "all",
                            "reason": "response indexing issues",
                        }
                    ]
                },
            )
        ],
        validator_summaries=[],
    )

    reporter.generate_report(summary, [], output_path)

    report = output_path.read_text(encoding="utf-8")
    assert "Fragment Marker Usage" in report
    assert "- **Unique marked code blocks:** 1" in report
    assert "- **Validator skips:** 1" in report
    assert "- **Audit flags:** 1" in report
    assert "response indexing issues" in report


def test_markdown_reporter_marks_warning_only_runs_as_passed_with_warnings(tmp_path: Path) -> None:
    reporter = MarkdownReporter(project_root=Path.cwd())
    output_path = tmp_path / "validation-report.md"
    issue = ValidationIssue(
        message="Type checking timeout - code block too complex",
        file_path=Path("docs/example.md"),
        line=12,
        severity=IssueSeverity.WARNING,
        rule_id="code_typing_timeout",
    )
    summary = ValidationSummary(
        total_files=1,
        total_validators=1,
        passed_files=0,
        failed_files=1,
        total_issues=1,
        error_count=0,
        warning_count=1,
        duration_ms=1.0,
        results=[
            ValidationResult(
                validator_name="code_typing",
                file_path=Path("docs/example.md"),
                passed=False,
                issues=[issue],
            )
        ],
        validator_summaries=[],
    )

    reporter.generate_report(summary, [issue], output_path)

    report = output_path.read_text(encoding="utf-8")
    assert "**Overall Status:** ⚠️ PASSED WITH WARNINGS" in report


def test_fragment_reporter_exposes_audit_flags() -> None:
    reporter = MarkdownReporter(project_root=Path.cwd())
    summary = ValidationSummary(
        total_files=1,
        total_validators=1,
        passed_files=1,
        failed_files=0,
        total_issues=0,
        error_count=0,
        warning_count=0,
        duration_ms=1.0,
        results=[
            ValidationResult(
                validator_name="code_linting",
                file_path=Path("docs/example.md"),
                passed=True,
                metadata={
                    "skipped_blocks": [
                        {
                            "code_block_start_line": 10,
                            "marker_line": 9,
                            "marker": "<!-- fragment: undefined imports -->",
                            "marker_kind": "all",
                            "reason": "undefined imports",
                        }
                    ]
                },
            )
        ],
        validator_summaries=[],
    )

    flags = reporter.fragment_audit_flags(summary)

    assert len(flags) == 1
    assert flags[0]["reason"] == "undefined imports"


def test_cli_display_results_fails_on_fragment_audit_flags(monkeypatch) -> None:
    summary = ValidationSummary(
        total_files=1,
        total_validators=1,
        passed_files=1,
        failed_files=0,
        total_issues=0,
        error_count=0,
        warning_count=0,
        duration_ms=1.0,
        results=[],
        validator_summaries=[],
    )
    monkeypatch.setattr(cli_module, "_generate_markdown_report", lambda summary: [{"reason": "undefined imports"}])

    assert cli_module._display_results(summary) == 1
