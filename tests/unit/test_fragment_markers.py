from pathlib import Path

from docs_validation.src.models import FileInfo
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
