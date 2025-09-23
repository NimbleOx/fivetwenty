"""Benchmark runner for performance testing validation systems."""

import gc
import subprocess
import sys
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path
from statistics import mean, median, stdev
from typing import Any

import psutil

from validation.core.config import ValidationConfig
from validation.core.context import ValidationContext
from validation.validators.registry import default_registry


@dataclass
class SystemMetrics:
    """System resource metrics."""

    cpu_percent: float
    memory_mb: float
    memory_percent: float
    disk_io_read_mb: float
    disk_io_write_mb: float


@dataclass
class BenchmarkMetrics:
    """Performance metrics for a single benchmark run."""

    duration_seconds: float
    peak_memory_mb: float
    avg_memory_mb: float
    cpu_usage_percent: float
    files_processed: int
    issues_found: int
    success_rate: float
    throughput_files_per_second: float
    system_metrics_start: SystemMetrics
    system_metrics_end: SystemMetrics


@dataclass
class BenchmarkResults:
    """Results from multiple benchmark runs."""

    benchmark_name: str
    test_description: str
    runs: list[BenchmarkMetrics] = field(default_factory=list)

    @property
    def avg_duration(self) -> float:
        return mean([r.duration_seconds for r in self.runs]) if self.runs else 0.0

    @property
    def median_duration(self) -> float:
        return median([r.duration_seconds for r in self.runs]) if self.runs else 0.0

    @property
    def duration_stdev(self) -> float:
        return stdev([r.duration_seconds for r in self.runs]) if len(self.runs) > 1 else 0.0

    @property
    def avg_throughput(self) -> float:
        return mean([r.throughput_files_per_second for r in self.runs]) if self.runs else 0.0

    @property
    def peak_memory(self) -> float:
        return max([r.peak_memory_mb for r in self.runs]) if self.runs else 0.0

    @property
    def avg_memory(self) -> float:
        return mean([r.avg_memory_mb for r in self.runs]) if self.runs else 0.0


class BenchmarkRunner:
    """Runs performance benchmarks on validation systems."""

    def __init__(self, project_root: Path | None = None):
        self.project_root = project_root or Path.cwd()
        self.results: dict[str, BenchmarkResults] = {}

    def run_benchmark(
        self,
        benchmark_name: str,
        test_function: Callable[[], Any],
        description: str = "",
        runs: int = 5,
        warmup_runs: int = 1,
    ) -> BenchmarkResults:
        """Run a performance benchmark with multiple iterations."""
        print(f"Running benchmark: {benchmark_name}")
        print(f"Description: {description}")
        print(f"Warmup runs: {warmup_runs}, Test runs: {runs}")

        # Warmup runs to stabilize performance
        for i in range(warmup_runs):
            print(f"  Warmup {i + 1}/{warmup_runs}")
            gc.collect()  # Force garbage collection
            test_function()

        results = BenchmarkResults(
            benchmark_name=benchmark_name,
            test_description=description,
        )

        # Actual benchmark runs
        for run_number in range(runs):
            print(f"  Run {run_number + 1}/{runs}")

            # Force garbage collection before each run
            gc.collect()

            # Capture metrics
            metrics = self._run_single_benchmark(test_function)
            results.runs.append(metrics)

            print(f"    Duration: {metrics.duration_seconds:.2f}s, Throughput: {metrics.throughput_files_per_second:.1f} files/s, Memory: {metrics.peak_memory_mb:.1f}MB")

        self.results[benchmark_name] = results
        return results

    def _run_single_benchmark(self, test_function: Callable[[], Any]) -> BenchmarkMetrics:
        """Run a single benchmark iteration with detailed metrics."""
        # Get initial system state
        process = psutil.Process()
        system_start = self._get_system_metrics(process)

        # Memory tracking
        start_time = time.time()

        try:
            # Run the test function
            result = test_function()

            end_time = time.time()
            duration = end_time - start_time

            # Get final system state
            system_end = self._get_system_metrics(process)

            # Extract validation results if available
            files_processed = 0
            issues_found = 0
            success_rate = 100.0

            if hasattr(result, "total_files_checked"):
                files_processed = result.total_files_checked
                issues_found = result.total_issues
                success_rate = result.overall_success_rate
            elif hasattr(result, "files_checked"):
                files_processed = result.files_checked
                issues_found = getattr(result, "issues_found", 0)

            # Calculate throughput
            throughput = files_processed / duration if duration > 0 else 0

            return BenchmarkMetrics(
                duration_seconds=duration,
                peak_memory_mb=system_end.memory_mb,
                avg_memory_mb=(system_start.memory_mb + system_end.memory_mb) / 2,
                cpu_usage_percent=system_end.cpu_percent,
                files_processed=files_processed,
                issues_found=issues_found,
                success_rate=success_rate,
                throughput_files_per_second=throughput,
                system_metrics_start=system_start,
                system_metrics_end=system_end,
            )

        except Exception:
            end_time = time.time()
            duration = end_time - start_time
            system_end = self._get_system_metrics(process)

            return BenchmarkMetrics(
                duration_seconds=duration,
                peak_memory_mb=system_end.memory_mb,
                avg_memory_mb=(system_start.memory_mb + system_end.memory_mb) / 2,
                cpu_usage_percent=system_end.cpu_percent,
                files_processed=0,
                issues_found=0,
                success_rate=0.0,
                throughput_files_per_second=0.0,
                system_metrics_start=system_start,
                system_metrics_end=system_end,
            )

    def _get_system_metrics(self, process: psutil.Process) -> SystemMetrics:
        """Get current system resource metrics."""
        memory_info = process.memory_info()

        # Get disk I/O if available
        try:
            io_counters = process.io_counters()
            disk_read_mb = io_counters.read_bytes / (1024 * 1024)
            disk_write_mb = io_counters.write_bytes / (1024 * 1024)
        except (AttributeError, psutil.AccessDenied):
            disk_read_mb = 0.0
            disk_write_mb = 0.0

        return SystemMetrics(
            cpu_percent=process.cpu_percent(),
            memory_mb=memory_info.rss / (1024 * 1024),
            memory_percent=process.memory_percent(),
            disk_io_read_mb=disk_read_mb,
            disk_io_write_mb=disk_write_mb,
        )

    def benchmark_new_system(
        self,
        checks: list[str],
        parallel: bool = True,
        profile: str = "default",
    ) -> Any:
        """Benchmark the new validation system."""
        config = ValidationConfig(project_root=self.project_root)
        context = ValidationContext(config)

        return default_registry.run_checks(checks, context, parallel=parallel)

    def benchmark_old_system(
        self,
        validation_type: str = "all",
    ) -> Any:
        """Benchmark the old validation system by running its CLI."""
        old_cli_path = self.project_root.parent / "validation" / "cli.py"

        if not old_cli_path.exists():
            raise FileNotFoundError(f"Old validation CLI not found at {old_cli_path}")

        try:
            # Run the old validation system
            result = subprocess.run(
                [sys.executable, str(old_cli_path), "run", validation_type],
                check=False,
                cwd=str(self.project_root.parent / "validation"),
                capture_output=True,
                text=True,
                timeout=600,  # 10 minute timeout
            )

            # Parse output to extract metrics
            files_checked = 0
            issues_found = 0

            if result.stdout:
                for line in result.stdout.split("\n"):
                    if "files checked" in line.lower():
                        try:
                            files_checked = int(line.split()[0])
                        except (ValueError, IndexError):
                            pass
                    elif "issues found" in line.lower():
                        try:
                            issues_found = int(line.split()[0])
                        except (ValueError, IndexError):
                            pass

            # Create a mock result object
            class OldSystemResult:
                def __init__(self):
                    self.files_checked = files_checked
                    self.issues_found = issues_found
                    self.returncode = result.returncode
                    self.stdout = result.stdout
                    self.stderr = result.stderr

            return OldSystemResult()

        except subprocess.TimeoutExpired:
            raise RuntimeError("Old validation system timed out")
        except Exception as e:
            raise RuntimeError(f"Failed to run old validation system: {e}")

    def run_comparison_benchmark(
        self,
        checks: list[str],
        test_sizes: list[str] | None = None,
        runs_per_test: int = 3,
    ) -> dict[str, dict[str, BenchmarkResults]]:
        """Run comprehensive comparison between old and new systems."""
        if test_sizes is None:
            test_sizes = ["small", "medium", "large"]
        comparison_results = {}

        for test_size in test_sizes:
            print(f"\nTesting with {test_size} dataset...")

            size_results = {}

            # Benchmark new system
            def run_new_system():
                return self.benchmark_new_system(checks, parallel=True)

            new_results = self.run_benchmark(
                f"new_system_{test_size}",
                run_new_system,
                f"New validation system with {test_size} dataset",
                runs=runs_per_test,
            )
            size_results["new_system"] = new_results

            # Benchmark new system without parallel processing
            def run_new_system_sequential():
                return self.benchmark_new_system(checks, parallel=False)

            new_sequential_results = self.run_benchmark(
                f"new_system_sequential_{test_size}",
                run_new_system_sequential,
                f"New validation system (sequential) with {test_size} dataset",
                runs=runs_per_test,
            )
            size_results["new_system_sequential"] = new_sequential_results

            # Try to benchmark old system if available
            try:

                def run_old_system():
                    return self.benchmark_old_system("all")

                old_results = self.run_benchmark(
                    f"old_system_{test_size}",
                    run_old_system,
                    f"Old validation system with {test_size} dataset",
                    runs=runs_per_test,
                )
                size_results["old_system"] = old_results

            except Exception as e:
                print(f"Warning: Could not benchmark old system: {e}")
                # Create placeholder results
                size_results["old_system"] = BenchmarkResults(
                    f"old_system_{test_size}",
                    f"Old system benchmark failed: {e}",
                )

            comparison_results[test_size] = size_results

        return comparison_results

    def run_scalability_test(
        self,
        checks: list[str],
        worker_counts: list[int] | None = None,
        runs_per_test: int = 3,
    ) -> dict[int, BenchmarkResults]:
        """Test scalability with different worker counts."""
        if worker_counts is None:
            worker_counts = [1, 2, 4, 8]
        print("\nRunning scalability tests...")
        scalability_results = {}

        for worker_count in worker_counts:
            print(f"\nTesting with {worker_count} workers...")

            def run_with_workers():
                config = ValidationConfig(project_root=self.project_root)
                config.tools.parallel_workers = worker_count
                context = ValidationContext(config)

                return default_registry.run_checks(checks, context, parallel=True)

            results = self.run_benchmark(
                f"workers_{worker_count}",
                run_with_workers,
                f"Validation with {worker_count} parallel workers",
                runs=runs_per_test,
            )

            scalability_results[worker_count] = results

        return scalability_results

    def run_memory_stress_test(
        self,
        checks: list[str],
        iterations: int = 10,
        monitor_interval: float = 0.1,
    ) -> dict[str, Any]:
        """Run memory stress test to detect leaks."""
        print("\nRunning memory stress test...")

        config = ValidationConfig(project_root=self.project_root)
        context = ValidationContext(config)

        memory_samples = []
        process = psutil.Process()

        for i in range(iterations):
            print(f"  Iteration {i + 1}/{iterations}")

            # Record memory before
            memory_before = process.memory_info().rss / (1024 * 1024)

            # Run validation
            summary = default_registry.run_checks(checks, context, parallel=True)

            # Force garbage collection
            gc.collect()

            # Record memory after
            memory_after = process.memory_info().rss / (1024 * 1024)

            memory_samples.append(
                {
                    "iteration": i + 1,
                    "memory_before_mb": memory_before,
                    "memory_after_mb": memory_after,
                    "memory_delta_mb": memory_after - memory_before,
                    "files_processed": summary.total_files_checked,
                    "issues_found": summary.total_issues,
                }
            )

        # Analyze memory trend
        memory_deltas = [s["memory_delta_mb"] for s in memory_samples]
        memory_trend = "increasing" if memory_deltas[-1] > memory_deltas[0] + 10 else "stable"

        return {
            "samples": memory_samples,
            "memory_trend": memory_trend,
            "total_memory_growth_mb": memory_samples[-1]["memory_after_mb"] - memory_samples[0]["memory_before_mb"],
            "avg_memory_delta_mb": mean(memory_deltas),
            "max_memory_delta_mb": max(memory_deltas),
        }
