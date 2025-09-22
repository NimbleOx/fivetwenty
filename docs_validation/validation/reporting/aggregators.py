"""Result aggregation and trend analysis for validation results."""

import json
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

from docs_validation.validation.core.results import IssueSeverity, ValidationIssue, ValidationResult, ValidationSummary


@dataclass
class TrendPoint:
    """A point in time for trend analysis."""
    timestamp: datetime
    total_checks: int
    passed_checks: int
    failed_checks: int
    total_issues: int
    success_rate: float
    duration: float


@dataclass
class CheckTrend:
    """Trend data for a specific check."""
    check_name: str
    points: list[TrendPoint]
    average_duration: float
    issue_trend: str  # "improving", "stable", "declining"


class ResultAggregator:
    """Aggregates validation results for analysis and reporting."""

    def __init__(self):
        self.results_by_check: dict[str, list[ValidationResult]] = defaultdict(list)
        self.results_by_file: dict[str, list[ValidationIssue]] = defaultdict(list)
        self.results_by_severity: dict[IssueSeverity, list[ValidationIssue]] = defaultdict(list)

    def add_summary(self, summary: ValidationSummary) -> None:
        """Add a validation summary to the aggregation."""
        for result in summary.results:
            self.results_by_check[result.check_name].append(result)

            for issue in result.issues:
                if issue.file_path:
                    self.results_by_file[str(issue.file_path)].append(issue)
                self.results_by_severity[issue.severity].append(issue)

    def get_check_statistics(self) -> dict[str, dict[str, Any]]:
        """Get detailed statistics for each check."""
        stats = {}

        for check_name, results in self.results_by_check.items():
            if not results:
                continue

            total_runs = len(results)
            successful_runs = sum(1 for r in results if r.is_successful)
            total_issues = sum(r.issues_found for r in results)
            total_files = sum(r.files_checked for r in results)
            total_duration = sum(r.duration_seconds for r in results)

            # Calculate severity breakdown
            severity_counts = {
                IssueSeverity.ERROR: 0,
                IssueSeverity.WARNING: 0,
                IssueSeverity.INFO: 0,
            }

            for result in results:
                for issue in result.issues:
                    severity_counts[issue.severity] += 1

            stats[check_name] = {
                "total_runs": total_runs,
                "successful_runs": successful_runs,
                "success_rate": (successful_runs / total_runs) * 100 if total_runs > 0 else 0,
                "total_issues": total_issues,
                "average_issues_per_run": total_issues / total_runs if total_runs > 0 else 0,
                "total_files_checked": total_files,
                "average_files_per_run": total_files / total_runs if total_runs > 0 else 0,
                "total_duration": total_duration,
                "average_duration": total_duration / total_runs if total_runs > 0 else 0,
                "errors": severity_counts[IssueSeverity.ERROR],
                "warnings": severity_counts[IssueSeverity.WARNING],
                "info": severity_counts[IssueSeverity.INFO],
            }

        return stats

    def get_file_hotspots(self, limit: int = 20) -> list[tuple[str, int, dict[IssueSeverity, int]]]:
        """Get files with the most issues (hotspots)."""
        hotspots = []

        for file_path, issues in self.results_by_file.items():
            severity_counts = {
                IssueSeverity.ERROR: 0,
                IssueSeverity.WARNING: 0,
                IssueSeverity.INFO: 0,
            }

            for issue in issues:
                severity_counts[issue.severity] += 1

            hotspots.append((file_path, len(issues), severity_counts))

        # Sort by total issues (descending)
        hotspots.sort(key=lambda x: x[1], reverse=True)
        return hotspots[:limit]

    def get_severity_distribution(self) -> dict[str, Any]:
        """Get distribution of issues by severity."""
        total_issues = sum(len(issues) for issues in self.results_by_severity.values())

        distribution = {}
        for severity, issues in self.results_by_severity.items():
            count = len(issues)
            distribution[severity.value] = {
                "count": count,
                "percentage": (count / total_issues) * 100 if total_issues > 0 else 0,
            }

        return distribution

    def get_most_common_issues(self, limit: int = 10) -> list[tuple[str, int, list[str]]]:
        """Get the most common validation issues."""
        issue_counts = defaultdict(int)
        issue_files = defaultdict(set)

        for issues in self.results_by_file.values():
            for issue in issues:
                # Group by message pattern
                message = issue.message
                issue_counts[message] += 1
                if issue.file_path:
                    issue_files[message].add(str(issue.file_path))

        # Sort by frequency
        sorted_issues = sorted(issue_counts.items(), key=lambda x: x[1], reverse=True)

        result = []
        for message, count in sorted_issues[:limit]:
            files = list(issue_files[message])
            result.append((message, count, files))

        return result

    def export_aggregated_data(self, output_path: Path) -> None:
        """Export aggregated data to JSON."""
        data = {
            "timestamp": datetime.now().isoformat(),
            "check_statistics": self.get_check_statistics(),
            "file_hotspots": [
                {
                    "file_path": file_path,
                    "total_issues": total_issues,
                    "severity_breakdown": {sev.value: count for sev, count in severity_counts.items()},
                }
                for file_path, total_issues, severity_counts in self.get_file_hotspots()
            ],
            "severity_distribution": self.get_severity_distribution(),
            "common_issues": [
                {
                    "message": message,
                    "count": count,
                    "affected_files": files[:10],  # Limit files for readability
                }
                for message, count, files in self.get_most_common_issues()
            ],
        }

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)


class TrendAnalyzer:
    """Analyzes trends in validation results over time."""

    def __init__(self, history_path: Path | None = None):
        self.history_path = history_path or Path("validation_history.json")
        self.history: list[dict[str, Any]] = []
        self._load_history()

    def _load_history(self) -> None:
        """Load historical validation data."""
        if self.history_path.exists():
            try:
                with open(self.history_path, encoding="utf-8") as f:
                    self.history = json.load(f)
            except (OSError, json.JSONDecodeError):
                self.history = []

    def _save_history(self) -> None:
        """Save historical validation data."""
        with open(self.history_path, "w", encoding="utf-8") as f:
            json.dump(self.history, f, indent=2, ensure_ascii=False)

    def add_summary(self, summary: ValidationSummary) -> None:
        """Add a validation summary to trend history."""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "total_checks": len(summary.results),
            "passed_checks": summary.passed_checks,
            "failed_checks": summary.failed_checks,
            "total_issues": summary.total_issues,
            "success_rate": summary.overall_success_rate,
            "duration": summary.total_duration,
            "checks": {},
        }

        # Add per-check data
        for result in summary.results:
            entry["checks"][result.check_name] = {
                "status": result.status.value,
                "issues_found": result.issues_found,
                "files_checked": result.files_checked,
                "duration": result.duration_seconds,
            }

        self.history.append(entry)
        self._save_history()

    def get_overall_trend(self, days: int = 30) -> list[TrendPoint]:
        """Get overall validation trend for the last N days."""
        cutoff_date = datetime.now() - timedelta(days=days)
        recent_history = [
            entry for entry in self.history
            if datetime.fromisoformat(entry["timestamp"]) >= cutoff_date
        ]

        trend_points = []
        for entry in recent_history:
            point = TrendPoint(
                timestamp=datetime.fromisoformat(entry["timestamp"]),
                total_checks=entry["total_checks"],
                passed_checks=entry["passed_checks"],
                failed_checks=entry["failed_checks"],
                total_issues=entry["total_issues"],
                success_rate=entry["success_rate"],
                duration=entry["duration"],
            )
            trend_points.append(point)

        return trend_points

    def get_check_trends(self, days: int = 30) -> dict[str, CheckTrend]:
        """Get trends for individual checks."""
        cutoff_date = datetime.now() - timedelta(days=days)
        recent_history = [
            entry for entry in self.history
            if datetime.fromisoformat(entry["timestamp"]) >= cutoff_date
        ]

        check_trends = {}
        check_data = defaultdict(list)

        # Collect data by check
        for entry in recent_history:
            timestamp = datetime.fromisoformat(entry["timestamp"])
            for check_name, check_info in entry.get("checks", {}).items():
                check_data[check_name].append({
                    "timestamp": timestamp,
                    "issues_found": check_info["issues_found"],
                    "duration": check_info.get("duration", 0.0),
                })

        # Analyze trends for each check
        for check_name, data_points in check_data.items():
            if len(data_points) < 2:
                continue

            # Calculate average duration
            avg_duration = sum(point["duration"] for point in data_points) / len(data_points)

            # Analyze issue trend
            recent_issues = [point["issues_found"] for point in data_points[-5:]]  # Last 5 runs
            earlier_issues = [point["issues_found"] for point in data_points[:-5]]  # Earlier runs

            if not earlier_issues:
                trend = "stable"
            else:
                recent_avg = sum(recent_issues) / len(recent_issues)
                earlier_avg = sum(earlier_issues) / len(earlier_issues)

                if recent_avg < earlier_avg * 0.8:  # 20% improvement
                    trend = "improving"
                elif recent_avg > earlier_avg * 1.2:  # 20% decline
                    trend = "declining"
                else:
                    trend = "stable"

            # Create trend points for visualization
            trend_points = []
            for point in data_points:
                trend_point = TrendPoint(
                    timestamp=point["timestamp"],
                    total_checks=1,  # Single check
                    passed_checks=1 if point["issues_found"] == 0 else 0,
                    failed_checks=0 if point["issues_found"] == 0 else 1,
                    total_issues=point["issues_found"],
                    success_rate=100.0 if point["issues_found"] == 0 else 0.0,
                    duration=point["duration"],
                )
                trend_points.append(trend_point)

            check_trends[check_name] = CheckTrend(
                check_name=check_name,
                points=trend_points,
                average_duration=avg_duration,
                issue_trend=trend,
            )

        return check_trends

    def get_performance_metrics(self) -> dict[str, Any]:
        """Get performance metrics and trends."""
        if len(self.history) < 2:
            return {"message": "Insufficient data for trend analysis"}

        recent = self.history[-5:]  # Last 5 runs
        earlier = self.history[-10:-5] if len(self.history) >= 10 else self.history[:-5]

        if not earlier:
            return {"message": "Insufficient data for comparison"}

        # Calculate averages
        recent_success_rate = sum(entry["success_rate"] for entry in recent) / len(recent)
        recent_duration = sum(entry["duration"] for entry in recent) / len(recent)
        recent_issues = sum(entry["total_issues"] for entry in recent) / len(recent)

        earlier_success_rate = sum(entry["success_rate"] for entry in earlier) / len(earlier)
        earlier_duration = sum(entry["duration"] for entry in earlier) / len(earlier)
        earlier_issues = sum(entry["total_issues"] for entry in earlier) / len(earlier)

        return {
            "recent_metrics": {
                "success_rate": recent_success_rate,
                "average_duration": recent_duration,
                "average_issues": recent_issues,
            },
            "earlier_metrics": {
                "success_rate": earlier_success_rate,
                "average_duration": earlier_duration,
                "average_issues": earlier_issues,
            },
            "trends": {
                "success_rate_change": recent_success_rate - earlier_success_rate,
                "duration_change": recent_duration - earlier_duration,
                "issues_change": recent_issues - earlier_issues,
            },
        }
