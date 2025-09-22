"""Performance profiler for detailed analysis of validation components."""

import cProfile
import functools
import io
import pstats
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path

import psutil


@dataclass
class FunctionProfile:
    """Profile data for a single function."""
    function_name: str
    call_count: int
    total_time: float
    cumulative_time: float
    avg_time_per_call: float
    time_percentage: float


@dataclass
class CheckProfile:
    """Profile data for a validation check."""
    check_name: str
    total_time: float
    setup_time: float
    execution_time: float
    cleanup_time: float
    files_processed: int
    time_per_file: float
    memory_usage_mb: float


@dataclass
class ProfileReport:
    """Comprehensive profiling report."""
    total_execution_time: float
    total_memory_usage_mb: float
    check_profiles: list[CheckProfile] = field(default_factory=list)
    function_profiles: list[FunctionProfile] = field(default_factory=list)
    bottlenecks: list[str] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)


class PerformanceProfiler:
    """Detailed performance profiler for validation system."""

    def __init__(self):
        self.profiler: cProfile.Profile | None = None
        self.start_time: float = 0
        self.start_memory: float = 0
        self.check_timings: dict[str, dict[str, float]] = {}

    def start_profiling(self) -> None:
        """Start detailed profiling."""
        self.profiler = cProfile.Profile()
        self.start_time = time.time()
        self.start_memory = psutil.Process().memory_info().rss / (1024 * 1024)
        self.profiler.enable()

    def stop_profiling(self) -> ProfileReport:
        """Stop profiling and generate report."""
        if not self.profiler:
            raise RuntimeError("Profiling not started")

        self.profiler.disable()
        end_time = time.time()
        end_memory = psutil.Process().memory_info().rss / (1024 * 1024)

        total_time = end_time - self.start_time
        total_memory = end_memory - self.start_memory

        # Generate profile report
        report = ProfileReport(
            total_execution_time=total_time,
            total_memory_usage_mb=total_memory,
        )

        # Analyze function profiles
        report.function_profiles = self._analyze_function_profiles()

        # Analyze check profiles
        report.check_profiles = self._analyze_check_profiles()

        # Identify bottlenecks
        report.bottlenecks = self._identify_bottlenecks(report)

        # Generate recommendations
        report.recommendations = self._generate_recommendations(report)

        return report

    def profile_check(self, check_name: str) -> Callable:
        """Decorator to profile individual validation checks."""
        def decorator(func: Callable) -> Callable:
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                start_time = time.time()
                start_memory = psutil.Process().memory_info().rss / (1024 * 1024)

                try:
                    result = func(*args, **kwargs)

                    end_time = time.time()
                    end_memory = psutil.Process().memory_info().rss / (1024 * 1024)

                    # Store timing information
                    if check_name not in self.check_timings:
                        self.check_timings[check_name] = {}

                    self.check_timings[check_name] = {
                        "total_time": end_time - start_time,
                        "memory_usage": end_memory - start_memory,
                        "files_processed": getattr(result, "files_checked", 0),
                        "issues_found": getattr(result, "issues_found", 0),
                    }

                    return result

                except Exception as e:
                    end_time = time.time()
                    self.check_timings[check_name] = {
                        "total_time": end_time - start_time,
                        "memory_usage": 0,
                        "files_processed": 0,
                        "issues_found": 0,
                        "error": str(e),
                    }
                    raise

            return wrapper
        return decorator

    def _analyze_function_profiles(self) -> list[FunctionProfile]:
        """Analyze function-level performance from cProfile data."""
        if not self.profiler:
            return []

        # Get profile statistics
        stats_buffer = io.StringIO()
        stats = pstats.Stats(self.profiler, stream=stats_buffer)
        stats.sort_stats("cumulative")

        function_profiles = []
        total_time = stats.total_tt

        for func_key, (call_count, _, total_time_func, cumulative_time) in stats.stats.items():
            filename, line_number, function_name = func_key

            # Skip system/library functions, focus on validation code
            if "validation" in filename or "test" in filename:
                avg_time = total_time_func / call_count if call_count > 0 else 0
                time_percentage = (cumulative_time / total_time * 100) if total_time > 0 else 0

                profile = FunctionProfile(
                    function_name=f"{Path(filename).name}:{function_name}",
                    call_count=call_count,
                    total_time=total_time_func,
                    cumulative_time=cumulative_time,
                    avg_time_per_call=avg_time,
                    time_percentage=time_percentage,
                )
                function_profiles.append(profile)

        # Sort by cumulative time (most expensive first)
        function_profiles.sort(key=lambda x: x.cumulative_time, reverse=True)
        return function_profiles[:20]  # Top 20 functions

    def _analyze_check_profiles(self) -> list[CheckProfile]:
        """Analyze check-level performance."""
        check_profiles = []

        for check_name, timing_data in self.check_timings.items():
            total_time = timing_data.get("total_time", 0)
            files_processed = timing_data.get("files_processed", 0)
            memory_usage = timing_data.get("memory_usage", 0)

            time_per_file = total_time / files_processed if files_processed > 0 else 0

            profile = CheckProfile(
                check_name=check_name,
                total_time=total_time,
                setup_time=0,  # Could be enhanced with more detailed timing
                execution_time=total_time,
                cleanup_time=0,
                files_processed=files_processed,
                time_per_file=time_per_file,
                memory_usage_mb=memory_usage,
            )
            check_profiles.append(profile)

        # Sort by total time
        check_profiles.sort(key=lambda x: x.total_time, reverse=True)
        return check_profiles

    def _identify_bottlenecks(self, report: ProfileReport) -> list[str]:
        """Identify performance bottlenecks."""
        bottlenecks = []

        # Check for slow functions (>10% of total time)
        for func_profile in report.function_profiles[:5]:
            if func_profile.time_percentage > 10:
                bottlenecks.append(
                    f"Function '{func_profile.function_name}' takes {func_profile.time_percentage:.1f}% of execution time",
                )

        # Check for slow validation checks
        for check_profile in report.check_profiles:
            if check_profile.time_per_file > 0.1:  # More than 100ms per file
                bottlenecks.append(
                    f"Check '{check_profile.check_name}' is slow: {check_profile.time_per_file:.3f}s per file",
                )

        # Check for memory usage
        if report.total_memory_usage_mb > 500:  # More than 500MB
            bottlenecks.append(
                f"High memory usage: {report.total_memory_usage_mb:.1f}MB",
            )

        return bottlenecks

    def _generate_recommendations(self, report: ProfileReport) -> list[str]:
        """Generate performance optimization recommendations."""
        recommendations = []

        # Analyze function call patterns
        high_call_count_functions = [
            f for f in report.function_profiles
            if f.call_count > 10000 and f.avg_time_per_call > 0.001
        ]

        if high_call_count_functions:
            recommendations.append(
                "Consider optimizing frequently called functions with high per-call overhead",
            )

        # Analyze check performance
        slow_checks = [c for c in report.check_profiles if c.time_per_file > 0.05]
        if slow_checks:
            recommendations.append(
                "Consider optimizing slow validation checks or implementing caching",
            )

        # Memory recommendations
        if report.total_memory_usage_mb > 200:
            recommendations.append(
                "Consider implementing streaming processing for large file sets",
            )

        # Parallel processing recommendations
        io_bound_checks = [
            c for c in report.check_profiles
            if "link" in c.check_name.lower() or "file" in c.check_name.lower()
        ]
        if len(io_bound_checks) > 2:
            recommendations.append(
                "I/O-bound checks could benefit from increased parallelization",
            )

        # General recommendations
        if report.total_execution_time > 30:
            recommendations.append(
                "Consider implementing incremental validation for large projects",
            )

        return recommendations

    def generate_profile_report(self, report: ProfileReport, output_path: Path | None = None) -> str:
        """Generate a detailed text report."""
        lines = []
        lines.append("📊 Performance Profile Report")
        lines.append("=" * 50)
        lines.append(f"Total Execution Time: {report.total_execution_time:.2f}s")
        lines.append(f"Total Memory Usage: {report.total_memory_usage_mb:.1f}MB")
        lines.append("")

        # Check profiles
        lines.append("🔍 Validation Check Performance:")
        lines.append("-" * 40)
        for check in report.check_profiles:
            lines.append(f"  {check.check_name}:")
            lines.append(f"    Total Time: {check.total_time:.3f}s")
            lines.append(f"    Files Processed: {check.files_processed}")
            lines.append(f"    Time per File: {check.time_per_file:.4f}s")
            lines.append(f"    Memory Usage: {check.memory_usage_mb:.1f}MB")
            lines.append("")

        # Function profiles
        lines.append("🔧 Function Performance (Top 10):")
        lines.append("-" * 40)
        for func in report.function_profiles[:10]:
            lines.append(f"  {func.function_name}:")
            lines.append(f"    Calls: {func.call_count}")
            lines.append(f"    Total Time: {func.total_time:.3f}s ({func.time_percentage:.1f}%)")
            lines.append(f"    Avg Time/Call: {func.avg_time_per_call:.6f}s")
            lines.append("")

        # Bottlenecks
        if report.bottlenecks:
            lines.append("⚠️  Performance Bottlenecks:")
            lines.append("-" * 30)
            for bottleneck in report.bottlenecks:
                lines.append(f"  • {bottleneck}")
            lines.append("")

        # Recommendations
        if report.recommendations:
            lines.append("💡 Optimization Recommendations:")
            lines.append("-" * 35)
            for rec in report.recommendations:
                lines.append(f"  • {rec}")
            lines.append("")

        report_text = "\n".join(lines)

        if output_path:
            output_path.write_text(report_text, encoding="utf-8")

        return report_text


class TimingContext:
    """Context manager for timing code blocks."""

    def __init__(self, name: str, profiler: PerformanceProfiler | None = None):
        self.name = name
        self.profiler = profiler
        self.start_time = 0
        self.start_memory = 0

    def __enter__(self):
        self.start_time = time.time()
        self.start_memory = psutil.Process().memory_info().rss / (1024 * 1024)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        end_time = time.time()
        end_memory = psutil.Process().memory_info().rss / (1024 * 1024)

        duration = end_time - self.start_time
        memory_delta = end_memory - self.start_memory

        print(f"⏱️  {self.name}: {duration:.3f}s, Memory: {memory_delta:+.1f}MB")

        if self.profiler and hasattr(self.profiler, "check_timings"):
            self.profiler.check_timings[self.name] = {
                "total_time": duration,
                "memory_usage": memory_delta,
                "files_processed": 0,
                "issues_found": 0,
            }
