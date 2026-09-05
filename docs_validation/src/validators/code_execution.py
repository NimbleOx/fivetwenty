"""Validate Markdown examples using the real SDK in offline worker processes."""

import math
from pathlib import Path
from typing import Any

from ..base import BaseValidator
from ..execution import CodeBlock, run_document
from ..models import FileInfo, ValidationIssue, ValidationResult
from .code_blocks import iter_fenced_blocks
from .fragments import FragmentTarget, find_fragment_marker, fragment_metadata, implicit_skip_metadata, is_placeholder_code, marker_skip_metadata


class CodeExecutionValidator(BaseValidator):
    """Execute each document separately, preserving context between its blocks."""

    def __init__(self) -> None:
        super().__init__(name="code_execution", description="Executes Python examples with the real SDK and offline HTTP fixtures")

    def supports_file(self, file_path: Path) -> bool:
        return file_path.suffix.lower() in {".md", ".markdown"}

    def _is_file_included(self, file_path: Path, include_list: list[str]) -> bool:
        file_str = file_path.as_posix()
        return not include_list or any(pattern.replace("\\", "/") in file_str for pattern in include_list)

    def _is_placeholder_code(self, code: str) -> bool:
        return is_placeholder_code(code)

    def validate_file(self, file_info: FileInfo, content: str, options: dict[str, Any]) -> ValidationResult:
        included = self._is_file_included(file_info.path, options.get("include_files", []))
        blocks: list[CodeBlock] = []
        skipped: list[dict[str, Any]] = []
        lines = content.splitlines()
        issues: list[ValidationIssue] = []
        for block in iter_fenced_blocks(content):
            if not block.is_python:
                continue
            if not block.closed:
                issues.append(ValidationIssue(file_path=file_info.path, line=block.fence_line, rule_id="code_unclosed_block", message="Unclosed Python code fence"))
                continue
            if not block.code.strip():
                continue
            marker = find_fragment_marker(lines, block.fence_line, FragmentTarget.EXECUTION)
            if not included:
                skipped.append(implicit_skip_metadata(block.fence_line, "File is outside code_execution include_files"))
            elif marker:
                skipped.append(marker_skip_metadata(marker, block.fence_line))
            elif is_placeholder_code(block.code):
                skipped.append(implicit_skip_metadata(block.fence_line, "Standalone ellipsis marks an incomplete example"))
            else:
                blocks.append(CodeBlock(start_line=block.fence_line + 1, code=block.code))

        metadata: dict[str, Any] = {**fragment_metadata(skipped), "skipped": not included, "executed_block_count": 0, "execution_results": []}
        if blocks:
            timeout = float(options.get("timeout_seconds", 15.0))
            if not math.isfinite(timeout) or timeout <= 0:
                issues.append(ValidationIssue(file_path=file_info.path, rule_id="code_execution_config", message="timeout_seconds must be a positive finite number"))
            else:
                results, worker_issues = run_document(file_info.path, blocks, timeout=timeout, mock_api_calls=options.get("mock_api_calls", True))
                issues.extend(worker_issues)
                for result in results:
                    issues.extend(result.issues)
                metadata.update(executed_block_count=len(results), execution_results=[result.model_dump(mode="json") for result in results], http_request_count=sum(result.request_count for result in results))
        for issue in issues:
            issue.file_path = file_info.path
            if issue.line and 0 < issue.line <= len(lines):
                issue.context = lines[issue.line - 1]
        return ValidationResult(validator_name=self.name, file_path=file_info.path, passed=not issues, issues=issues, metadata=metadata)
