"""Base validator interface and registry."""

from __future__ import annotations

import time
from abc import ABC, abstractmethod
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from pathlib import Path

from .models import FileInfo, ValidationResult, ValidationSummary, ValidatorSummary


class BaseValidator(ABC):
    """Base class for all validators."""

    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description

    @abstractmethod
    def supports_file(self, file_path: Path) -> bool:
        """Check if this validator can validate the given file."""

    @abstractmethod
    def validate_file(self, file_info: FileInfo, content: str, options: dict[str, Any]) -> ValidationResult:
        """Validate a single file and return the result."""

    def get_file_patterns(self) -> list[str]:
        """Get glob patterns for files this validator can handle."""
        return ["**/*"]


class ValidatorRegistry:
    """Registry for managing and running validators."""

    def __init__(self) -> None:
        self._validators: dict[str, BaseValidator] = {}

    def register(self, validator: BaseValidator) -> None:
        """Register a validator."""
        self._validators[validator.name] = validator

    def get_validator(self, name: str) -> BaseValidator | None:
        """Get a validator by name."""
        return self._validators.get(name)

    def list_validators(self) -> list[str]:
        """List all registered validator names."""
        return list(self._validators.keys())

    def validate_file(
        self,
        file_info: FileInfo,
        content: str,
        enabled_validators: list[str],
        validator_options: dict[str, dict[str, Any]],
    ) -> list[ValidationResult]:
        """Validate a single file with multiple validators."""
        results: list[ValidationResult] = []

        for validator_name in enabled_validators:
            validator = self._validators.get(validator_name)
            if not validator:
                continue

            if not validator.supports_file(file_info.path):
                continue

            start_time = time.perf_counter()
            try:
                options = validator_options.get(validator_name, {})
                result = validator.validate_file(file_info, content, options)
                result.duration_ms = (time.perf_counter() - start_time) * 1000
                results.append(result)
            except Exception as e:
                # Create error result for failed validation
                error_result = ValidationResult(validator_name=validator_name, file_path=file_info.path, passed=False, duration_ms=(time.perf_counter() - start_time) * 1000, metadata={"error": str(e)})
                results.append(error_result)

        return results

    def validate_files(
        self,
        files: list[tuple[FileInfo, str]],  # (file_info, content)
        enabled_validators: list[str],
        validator_options: dict[str, dict[str, Any]],
        parallel: bool = True,
        max_workers: int = 4,
    ) -> ValidationSummary:
        """Validate multiple files and return a summary."""
        start_time = time.perf_counter()
        all_results: list[ValidationResult] = []

        # Split validators into parallel-safe and sequential-only
        # code_execution uses signal handlers and I/O redirection which don't work well in threads
        sequential_validators = {"code_execution"}
        parallel_validators = [v for v in enabled_validators if v not in sequential_validators]
        sequential_only = [v for v in enabled_validators if v in sequential_validators]

        # Run parallel-safe validators in parallel if requested
        if parallel and len(files) > 1 and parallel_validators:
            all_results.extend(self._validate_parallel(files, parallel_validators, validator_options, max_workers))
        elif parallel_validators:
            all_results.extend(self._validate_sequential(files, parallel_validators, validator_options))

        # Always run sequential-only validators sequentially
        if sequential_only:
            all_results.extend(self._validate_sequential(files, sequential_only, validator_options))

        duration_ms = (time.perf_counter() - start_time) * 1000

        # Calculate summary statistics
        files_with_results = set()
        total_issues = 0
        error_count = 0
        warning_count = 0

        for result in all_results:
            files_with_results.add(result.file_path)
            total_issues += len(result.issues)
            error_count += result.error_count
            warning_count += result.warning_count

        # Count files that passed (have no failing results)
        file_results: dict[Path, list[ValidationResult]] = {}
        for result in all_results:
            if result.file_path not in file_results:
                file_results[result.file_path] = []
            file_results[result.file_path].append(result)

        passed_files = sum(1 for results in file_results.values() if all(r.passed for r in results))

        # Calculate per-validator summaries
        validator_summaries = self._calculate_validator_summaries(all_results, enabled_validators)

        return ValidationSummary(
            total_files=len(files),
            total_validators=len(enabled_validators),
            passed_files=passed_files,
            failed_files=len(files) - passed_files,
            total_issues=total_issues,
            error_count=error_count,
            warning_count=warning_count,
            duration_ms=duration_ms,
            results=all_results,
            validator_summaries=validator_summaries,
        )

    def _validate_sequential(
        self,
        files: list[tuple[FileInfo, str]],
        enabled_validators: list[str],
        validator_options: dict[str, dict[str, Any]],
    ) -> list[ValidationResult]:
        """Validate files sequentially."""
        results: list[ValidationResult] = []

        for file_info, content in files:
            file_results = self.validate_file(file_info, content, enabled_validators, validator_options)
            results.extend(file_results)

        return results

    def _validate_parallel(
        self,
        files: list[tuple[FileInfo, str]],
        enabled_validators: list[str],
        validator_options: dict[str, dict[str, Any]],
        max_workers: int,
    ) -> list[ValidationResult]:
        """Validate files in parallel."""
        results: list[ValidationResult] = []

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_file = {executor.submit(self.validate_file, file_info, content, enabled_validators, validator_options): file_info for file_info, content in files}

            for future in as_completed(future_to_file):
                try:
                    file_results = future.result()
                    results.extend(file_results)
                except Exception as e:  # noqa: PERF203
                    file_info = future_to_file[future]
                    # Create error result for completely failed file
                    error_result = ValidationResult(validator_name="system", file_path=file_info.path, passed=False, metadata={"error": f"Failed to validate file: {e}"})
                    results.append(error_result)

        return results

    def _calculate_validator_summaries(self, results: list[ValidationResult], enabled_validators: list[str]) -> list[ValidatorSummary]:
        """Calculate per-validator summary statistics."""
        validator_stats: dict[str, dict[str, Any]] = {}

        # Initialize stats for ALL registered validators (not just enabled ones)
        for validator_name in self._validators:
            validator_stats[validator_name] = {"files_checked": set(), "files_passed": set(), "files_failed": set(), "total_issues": 0, "error_count": 0, "warning_count": 0, "duration_ms": 0.0, "enabled": validator_name in enabled_validators}

        # Process each result
        for result in results:
            if result.validator_name not in validator_stats:
                continue

            # Skip results that were marked as skipped (e.g., files excluded by include_files option)
            if result.metadata.get("skipped", False):
                continue

            stats = validator_stats[result.validator_name]

            # Track files
            stats["files_checked"].add(result.file_path)
            if result.passed:
                stats["files_passed"].add(result.file_path)
            else:
                stats["files_failed"].add(result.file_path)

            # Count issues
            stats["total_issues"] += len(result.issues)
            stats["error_count"] += result.error_count
            stats["warning_count"] += result.warning_count
            stats["duration_ms"] += result.duration_ms

        # Create ValidatorSummary objects
        summaries = []
        for validator_name, stats in validator_stats.items():
            files_checked = len(stats["files_checked"])
            files_passed = len(stats["files_passed"])
            files_failed = len(stats["files_failed"])

            success_rate = (files_passed / files_checked * 100.0) if files_checked > 0 else 100.0

            summary = ValidatorSummary(
                name=validator_name, files_checked=files_checked, files_passed=files_passed, files_failed=files_failed, total_issues=stats["total_issues"], error_count=stats["error_count"], warning_count=stats["warning_count"], duration_ms=stats["duration_ms"], success_rate=success_rate, enabled=stats["enabled"]
            )
            summaries.append(summary)

        # Sort by validator name for consistent output
        return sorted(summaries, key=lambda s: s.name)


# Global registry instance
registry = ValidatorRegistry()
