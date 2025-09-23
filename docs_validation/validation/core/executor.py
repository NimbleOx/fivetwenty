"""Advanced parallel execution engine for validation checks."""

import multiprocessing
import threading
import time
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any

from validation.checks.base import BaseCheck
from validation.core.context import ValidationContext
from validation.core.results import ValidationResult, ValidationStatus, ValidationSummary


class ExecutionMode(str, Enum):
    """Execution mode for validation checks."""

    SEQUENTIAL = "sequential"
    THREADED = "threaded"
    PROCESS = "process"
    MIXED = "mixed"  # Smart selection based on check type


class CheckType(str, Enum):
    """Types of validation checks for execution optimization."""

    IO_BOUND = "io_bound"  # File reading, network requests
    CPU_BOUND = "cpu_bound"  # Heavy computation, parsing
    EXTERNAL = "external"  # External tool execution
    MIXED = "mixed"  # Combination


@dataclass
class ExecutionProfile:
    """Execution profile for optimizing performance."""

    max_workers: int = 4
    chunk_size: int = 50
    timeout_seconds: float = 300.0
    memory_limit_mb: int = 512
    enable_progress: bool = True
    execution_mode: ExecutionMode = ExecutionMode.MIXED


@dataclass
class CheckMetadata:
    """Metadata about a validation check for optimization."""

    check_name: str
    check_type: CheckType
    estimated_files_per_second: float = 10.0
    memory_usage_mb: float = 10.0
    supports_batching: bool = True
    requires_context_isolation: bool = False


class ExecutionScheduler:
    """Smart scheduler for optimizing validation execution."""

    def __init__(self, profile: ExecutionProfile) -> None:
        self.profile = profile
        self.check_metadata: dict[str, CheckMetadata] = {}
        self.execution_stats: dict[str, dict[str, float]] = {}

    def register_check_metadata(self, metadata: CheckMetadata) -> None:
        """Register metadata for a check to optimize execution."""
        self.check_metadata[metadata.check_name] = metadata

    def get_optimal_execution_plan(
        self,
        check_names: list[str],
        file_count: int,
    ) -> dict[str, Any]:
        """Create optimal execution plan based on check characteristics."""
        # Categorize checks
        io_bound_checks = []
        cpu_bound_checks = []
        external_checks = []

        for check_name in check_names:
            metadata = self.check_metadata.get(
                check_name,
                CheckMetadata(check_name=check_name, check_type=CheckType.MIXED),
            )

            if metadata.check_type == CheckType.IO_BOUND:
                io_bound_checks.append(check_name)
            elif metadata.check_type == CheckType.CPU_BOUND:
                cpu_bound_checks.append(check_name)
            elif metadata.check_type == CheckType.EXTERNAL:
                external_checks.append(check_name)
            else:
                # Default to IO bound for mixed
                io_bound_checks.append(check_name)

        # Calculate optimal worker counts
        cpu_count = multiprocessing.cpu_count()

        return {
            "io_bound": {
                "checks": io_bound_checks,
                "workers": min(self.profile.max_workers * 2, 16),  # IO can handle more workers
                "execution_mode": ExecutionMode.THREADED,
                "chunk_size": max(1, file_count // (len(io_bound_checks) or 1) // 10),
            },
            "cpu_bound": {
                "checks": cpu_bound_checks,
                "workers": min(cpu_count, self.profile.max_workers),
                "execution_mode": ExecutionMode.PROCESS,
                "chunk_size": max(1, file_count // (len(cpu_bound_checks) or 1) // 4),
            },
            "external": {
                "checks": external_checks,
                "workers": min(4, self.profile.max_workers),  # Limited for external tools
                "execution_mode": ExecutionMode.THREADED,
                "chunk_size": max(1, file_count // (len(external_checks) or 1) // 8),
            },
        }


    def estimate_execution_time(self, check_names: list[str], file_count: int) -> float:
        """Estimate total execution time."""
        total_time = 0.0

        for check_name in check_names:
            metadata = self.check_metadata.get(
                check_name,
                CheckMetadata(check_name=check_name, check_type=CheckType.MIXED),
            )

            check_time = file_count / metadata.estimated_files_per_second
            total_time = max(total_time, check_time)  # Parallel execution

        return total_time


class ProgressTracker:
    """Track and report validation progress."""

    def __init__(self, total_checks: int, total_files: int) -> None:
        self.total_checks = total_checks
        self.total_files = total_files
        self.completed_checks = 0
        self.completed_files = 0
        self.start_time = time.time()
        self.lock = threading.Lock()

    def update_check_progress(self, files_processed: int) -> None:
        """Update progress for a completed check."""
        with self.lock:
            self.completed_files += files_processed
            self.completed_checks += 1

    def get_progress_info(self) -> dict[str, Any]:
        """Get current progress information."""
        with self.lock:
            elapsed = time.time() - self.start_time
            files_per_second = self.completed_files / elapsed if elapsed > 0 else 0

            return {
                "completed_checks": self.completed_checks,
                "total_checks": self.total_checks,
                "completed_files": self.completed_files,
                "total_files": self.total_files,
                "check_progress": (self.completed_checks / self.total_checks) * 100,
                "file_progress": (self.completed_files / self.total_files) * 100 if self.total_files > 0 else 0,
                "elapsed_seconds": elapsed,
                "files_per_second": files_per_second,
                "estimated_remaining": (self.total_files - self.completed_files) / files_per_second if files_per_second > 0 else 0,
            }


class ValidationExecutor:
    """High-performance parallel validation executor."""

    def __init__(self, profile: ExecutionProfile | None = None) -> None:
        self.profile = profile or ExecutionProfile()
        self.scheduler = ExecutionScheduler(self.profile)
        self.progress_tracker: ProgressTracker | None = None

        # Register default check metadata
        self._register_default_metadata()

    def _register_default_metadata(self) -> None:
        """Register default metadata for known check types."""
        default_metadata = [
            CheckMetadata("markdown_syntax", CheckType.IO_BOUND, 100.0, 5.0),
            CheckMetadata("financial_precision", CheckType.IO_BOUND, 80.0, 8.0),
            CheckMetadata("financial_terminology", CheckType.IO_BOUND, 120.0, 3.0),
            CheckMetadata("link_validation", CheckType.IO_BOUND, 20.0, 15.0),  # Slower due to network
            CheckMetadata("python_syntax", CheckType.CPU_BOUND, 50.0, 20.0),
            CheckMetadata("python_style", CheckType.EXTERNAL, 30.0, 25.0),
            CheckMetadata("prose", CheckType.EXTERNAL, 25.0, 30.0),
        ]

        for metadata in default_metadata:
            self.scheduler.register_check_metadata(metadata)

    def execute_checks(
        self,
        checks: dict[str, BaseCheck],
        context: ValidationContext,
        parallel: bool = True,
    ) -> ValidationSummary:
        """Execute validation checks with optimal performance."""
        start_time = time.time()
        check_names = list(checks.keys())

        # Estimate file count for optimization
        file_count = len(context.get_files_for_validation())

        if self.profile.enable_progress:
            self.progress_tracker = ProgressTracker(len(checks), file_count * len(checks))

        print(f"Executing {len(checks)} checks on {file_count} files...")

        if not parallel or len(checks) == 1:
            results = self._execute_sequential(checks, context)
        else:
            # Get optimal execution plan
            execution_plan = self.scheduler.get_optimal_execution_plan(check_names, file_count)
            estimated_time = self.scheduler.estimate_execution_time(check_names, file_count)

            print(f"Estimated execution time: {estimated_time:.1f}s")
            results = self._execute_parallel_optimized(checks, context, execution_plan)

        total_duration = time.time() - start_time

        # Create summary
        summary = ValidationSummary(
            results=results,
            total_duration=total_duration,
        )

        self._print_execution_summary(summary)
        return summary

    def _execute_sequential(
        self,
        checks: dict[str, BaseCheck],
        context: ValidationContext,
    ) -> list[ValidationResult]:
        """Execute checks sequentially."""
        results = []

        for check_name, check in checks.items():
            print(f"  Running {check_name}...")

            try:
                result = check.run(context)
                results.append(result)

                if self.progress_tracker:
                    self.progress_tracker.update_check_progress(result.files_checked)

                status_icon = "PASSED" if result.is_successful else "FAILED"
                print(f"  {status_icon} {check_name}: {result.issues_found} issues found")

            except Exception as e:
                error_result = ValidationResult(
                    check_name=check_name,
                    status=ValidationStatus.ERROR,
                )
                error_result.add_issue(
                    message=f"Check execution failed: {e}",
                    file_path="<execution>",
                )
                results.append(error_result)
                print(f"  FAILED {check_name}: execution failed ({e})")

        return results

    def _execute_parallel_optimized(
        self,
        checks: dict[str, BaseCheck],
        context: ValidationContext,
        execution_plan: dict[str, Any],
    ) -> list[ValidationResult]:
        """Execute checks with optimized parallel execution."""
        all_results = []

        # Execute each category in optimal mode
        for category, plan in execution_plan.items():
            if not plan["checks"]:
                continue

            print(f"Executing {category} checks: {plan['checks']}")

            category_checks = {name: checks[name] for name in plan["checks"] if name in checks}

            if plan["execution_mode"] == ExecutionMode.THREADED:
                results = self._execute_threaded(category_checks, context, plan["workers"])
            elif plan["execution_mode"] == ExecutionMode.PROCESS:
                results = self._execute_process_based(category_checks, context, plan["workers"])
            else:
                results = self._execute_sequential(category_checks, context)

            all_results.extend(results)

        return all_results

    def _execute_threaded(
        self,
        checks: dict[str, BaseCheck],
        context: ValidationContext,
        max_workers: int,
    ) -> list[ValidationResult]:
        """Execute checks using thread pool."""
        results = []

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all checks
            future_to_name = {executor.submit(self._run_check_with_progress, check, context, name): name for name, check in checks.items()}

            # Collect results
            for future in as_completed(future_to_name):
                check_name = future_to_name[future]
                try:
                    result = future.result(timeout=self.profile.timeout_seconds)
                    results.append(result)

                    status_icon = "PASSED" if result.is_successful else "FAILED"
                    print(f"  {status_icon} {check_name}: {result.issues_found} issues found")

                except Exception as e:
                    error_result = ValidationResult(
                        check_name=check_name,
                        status=ValidationStatus.ERROR,
                    )
                    error_result.add_issue(
                        message=f"Check execution failed: {e}",
                        file_path="<execution>",
                    )
                    results.append(error_result)
                    print(f"  FAILED {check_name}: execution failed ({e})")

        return results

    def _execute_process_based(
        self,
        checks: dict[str, BaseCheck],
        context: ValidationContext,
        max_workers: int,
    ) -> list[ValidationResult]:
        """Execute CPU-bound checks using process pool."""
        # For now, fall back to threaded execution
        # Process-based execution requires serializable contexts
        # which would need additional implementation
        return self._execute_threaded(checks, context, max_workers)

    def _run_check_with_progress(
        self,
        check: BaseCheck,
        context: ValidationContext,
        check_name: str,
    ) -> ValidationResult:
        """Run a single check with progress tracking."""
        result = check.run(context)

        if self.progress_tracker:
            self.progress_tracker.update_check_progress(result.files_checked)

        return result

    def _print_execution_summary(self, summary: ValidationSummary) -> None:
        """Print execution summary with performance metrics."""
        if self.progress_tracker:
            progress = self.progress_tracker.get_progress_info()

            print("\nExecution Summary:")
            print(f"  Total time: {summary.total_duration:.2f}s")
            print(f"  Processing speed: {progress['files_per_second']:.1f} files/second")
            print(f"  Files processed: {progress['completed_files']}")
            print(f"  Success rate: {summary.overall_success_rate:.1f}%")
            print(f"  Total issues: {summary.total_issues}")


class BatchProcessor:
    """Batch processor for handling large file sets efficiently."""

    def __init__(self, batch_size: int = 100) -> None:
        self.batch_size = batch_size

    def process_files_in_batches(
        self,
        files: list[Path],
        processor: Callable[[list[Path]], Any],
        progress_callback: Callable[[int, int], None] | None = None,
    ) -> list[Any]:
        """Process files in batches to manage memory usage."""
        results = []
        total_batches = (len(files) + self.batch_size - 1) // self.batch_size

        for i in range(0, len(files), self.batch_size):
            batch = files[i : i + self.batch_size]
            batch_num = i // self.batch_size + 1

            if progress_callback:
                progress_callback(batch_num, total_batches)

            batch_result = processor(batch)
            results.append(batch_result)

        return results


# Global executor instance
default_executor = ValidationExecutor()
