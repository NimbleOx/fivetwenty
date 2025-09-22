"""Quality gate implementation for validation results."""

from dataclasses import dataclass
from enum import Enum
from typing import Any

from validation.core.results import IssueSeverity, ValidationSummary


class GateStatus(str, Enum):
    """Quality gate status."""

    PASSED = "passed"
    FAILED = "failed"
    WARNING = "warning"
    SKIPPED = "skipped"


@dataclass
class GateResult:
    """Result of a quality gate check."""

    gate_name: str
    status: GateStatus
    message: str
    actual_value: Any
    threshold_value: Any
    severity: IssueSeverity = IssueSeverity.ERROR


@dataclass
class QualityGateReport:
    """Complete quality gate report."""

    overall_status: GateStatus
    gate_results: list[GateResult]
    summary: dict[str, Any]
    passed_gates: int
    failed_gates: int
    warning_gates: int


class QualityGate:
    """Individual quality gate implementation."""

    def __init__(
        self,
        name: str,
        description: str,
        threshold_value: Any,
        comparison_operator: str = "<=",
        severity: IssueSeverity = IssueSeverity.ERROR,
    ):
        self.name = name
        self.description = description
        self.threshold_value = threshold_value
        self.comparison_operator = comparison_operator
        self.severity = severity

    def evaluate(self, actual_value: Any) -> GateResult:
        """Evaluate the gate against an actual value."""
        passed = self._compare_values(actual_value, self.threshold_value, self.comparison_operator)

        status = GateStatus.PASSED if passed else GateStatus.FAILED
        if not passed and self.severity == IssueSeverity.WARNING:
            status = GateStatus.WARNING

        message = self._generate_message(actual_value, passed)

        return GateResult(
            gate_name=self.name,
            status=status,
            message=message,
            actual_value=actual_value,
            threshold_value=self.threshold_value,
            severity=self.severity,
        )

    def _compare_values(self, actual: Any, threshold: Any, operator: str) -> bool:
        """Compare actual value against threshold using the specified operator."""
        try:
            if operator == "<=":
                return actual <= threshold
            if operator == "<":
                return actual < threshold
            if operator == ">=":
                # Special case for set containment (required checks)
                if isinstance(actual, set) and isinstance(threshold, set):
                    return threshold.issubset(actual)
                return actual >= threshold
            if operator == ">":
                return actual > threshold
            if operator == "==":
                return actual == threshold
            if operator == "!=":
                return actual != threshold
            if operator == "contains":
                # For set containment
                if isinstance(actual, set) and isinstance(threshold, set):
                    return threshold.issubset(actual)
                return threshold in actual
            raise ValueError(f"Unsupported comparison operator: {operator}")
        except (TypeError, ValueError):
            return False

    def _generate_message(self, actual_value: Any, passed: bool) -> str:
        """Generate a descriptive message for the gate result."""
        status_word = "✅ Passed" if passed else "❌ Failed"
        return f"{status_word}: {self.description} (actual: {actual_value}, threshold: {self.comparison_operator} {self.threshold_value})"


class QualityGateManager:
    """Manages and evaluates quality gates for validation results."""

    def __init__(self):
        self.gates: list[QualityGate] = []

    def add_gate(self, gate: QualityGate) -> None:
        """Add a quality gate."""
        self.gates.append(gate)

    def add_error_threshold_gate(self, max_errors: int) -> None:
        """Add a gate for maximum allowed errors."""
        gate = QualityGate(
            name="max_errors",
            description=f"Total errors must not exceed {max_errors}",
            threshold_value=max_errors,
            comparison_operator="<=",
            severity=IssueSeverity.ERROR,
        )
        self.add_gate(gate)

    def add_warning_threshold_gate(self, max_warnings: int) -> None:
        """Add a gate for maximum allowed warnings."""
        gate = QualityGate(
            name="max_warnings",
            description=f"Total warnings must not exceed {max_warnings}",
            threshold_value=max_warnings,
            comparison_operator="<=",
            severity=IssueSeverity.WARNING,
        )
        self.add_gate(gate)

    def add_success_rate_gate(self, min_success_rate: float) -> None:
        """Add a gate for minimum success rate."""
        gate = QualityGate(
            name="min_success_rate",
            description=f"Success rate must be at least {min_success_rate}%",
            threshold_value=min_success_rate,
            comparison_operator=">=",
            severity=IssueSeverity.ERROR,
        )
        self.add_gate(gate)

    def add_issues_per_file_gate(self, max_issues_per_file: int) -> None:
        """Add a gate for maximum issues per file."""
        gate = QualityGate(
            name="max_issues_per_file",
            description=f"Average issues per file must not exceed {max_issues_per_file}",
            threshold_value=max_issues_per_file,
            comparison_operator="<=",
            severity=IssueSeverity.WARNING,
        )
        self.add_gate(gate)

    def add_required_checks_gate(self, required_checks: list[str]) -> None:
        """Add a gate for required validation checks."""
        gate = QualityGate(
            name="required_checks",
            description=f"All required checks must be present: {', '.join(required_checks)}",
            threshold_value=set(required_checks),
            comparison_operator=">=",  # Change to >= for subset comparison
            severity=IssueSeverity.ERROR,
        )
        self.add_gate(gate)

    def add_security_issues_gate(self, allow_security_issues: bool = False) -> None:
        """Add a gate for security issues."""
        if not allow_security_issues:
            gate = QualityGate(
                name="no_security_issues",
                description="No security issues allowed",
                threshold_value=0,
                comparison_operator="<=",
                severity=IssueSeverity.ERROR,
            )
            self.add_gate(gate)

    def evaluate_summary(self, summary: ValidationSummary) -> QualityGateReport:
        """Evaluate all quality gates against a validation summary."""
        gate_results = []

        # Calculate metrics from summary
        metrics = self._extract_metrics(summary)

        # Evaluate each gate
        for gate in self.gates:
            if gate.name in metrics:
                actual_value = metrics[gate.name]
                result = gate.evaluate(actual_value)
                gate_results.append(result)

        # Determine overall status
        failed_count = len([r for r in gate_results if r.status == GateStatus.FAILED])
        warning_count = len([r for r in gate_results if r.status == GateStatus.WARNING])
        passed_count = len([r for r in gate_results if r.status == GateStatus.PASSED])

        if failed_count > 0:
            overall_status = GateStatus.FAILED
        elif warning_count > 0:
            overall_status = GateStatus.WARNING
        else:
            overall_status = GateStatus.PASSED

        return QualityGateReport(
            overall_status=overall_status,
            gate_results=gate_results,
            summary={
                "total_gates": len(gate_results),
                "metrics": metrics,
            },
            passed_gates=passed_count,
            failed_gates=failed_count,
            warning_gates=warning_count,
        )

    def _extract_metrics(self, summary: ValidationSummary) -> dict[str, Any]:
        """Extract metrics from validation summary for gate evaluation."""
        # Count issues by severity
        error_count = 0
        warning_count = 0
        security_issue_count = 0

        for result in summary.results:
            for issue in result.issues:
                if issue.severity == IssueSeverity.ERROR:
                    error_count += 1
                elif issue.severity == IssueSeverity.WARNING:
                    warning_count += 1

                # Check if this is a security-related issue
                if any(keyword in issue.message.lower() for keyword in ["security", "secret", "password", "token", "key", "credential"]):
                    security_issue_count += 1

        # Calculate average issues per file
        avg_issues_per_file = summary.total_issues / summary.total_files_checked if summary.total_files_checked > 0 else 0

        # Get list of executed checks
        executed_checks = set(result.check_name for result in summary.results)

        return {
            "max_errors": error_count,
            "max_warnings": warning_count,
            "min_success_rate": summary.overall_success_rate,
            "max_issues_per_file": avg_issues_per_file,
            "no_security_issues": security_issue_count,
            "required_checks": executed_checks,
            "total_issues": summary.total_issues,
            "total_files": summary.total_files_checked,
            "total_checks": len(summary.results),
        }

    def create_from_config(self, config_dict: dict[str, Any]) -> "QualityGateManager":
        """Create quality gate manager from configuration dictionary."""
        manager = QualityGateManager()

        if "max_errors" in config_dict:
            manager.add_error_threshold_gate(config_dict["max_errors"])

        if "max_warnings" in config_dict:
            manager.add_warning_threshold_gate(config_dict["max_warnings"])

        if "min_success_rate" in config_dict:
            manager.add_success_rate_gate(config_dict["min_success_rate"])

        if "max_issues_per_file" in config_dict:
            manager.add_issues_per_file_gate(config_dict["max_issues_per_file"])

        if "required_checks" in config_dict:
            manager.add_required_checks_gate(config_dict["required_checks"])

        if "fail_on_security_issues" in config_dict:
            manager.add_security_issues_gate(not config_dict["fail_on_security_issues"])

        return manager

    def format_report(self, report: QualityGateReport) -> str:
        """Format quality gate report for display."""
        lines = []
        lines.append("🚦 Quality Gate Report")
        lines.append("=" * 50)

        # Overall status
        status_icon = {
            GateStatus.PASSED: "✅",
            GateStatus.FAILED: "❌",
            GateStatus.WARNING: "⚠️",
        }.get(report.overall_status, "❓")

        lines.append(f"Overall Status: {status_icon} {report.overall_status.value.upper()}")
        lines.append(f"Gates: {report.passed_gates} passed, {report.failed_gates} failed, {report.warning_gates} warnings")
        lines.append("")

        # Individual gate results
        lines.append("Gate Results:")
        lines.append("-" * 30)

        for result in report.gate_results:
            status_icon = {
                GateStatus.PASSED: "✅",
                GateStatus.FAILED: "❌",
                GateStatus.WARNING: "⚠️",
            }.get(result.status, "❓")

            lines.append(f"{status_icon} {result.gate_name}: {result.message}")

        lines.append("")
        lines.append("Summary Metrics:")
        lines.append("-" * 20)
        for key, value in report.summary.get("metrics", {}).items():
            if not key.startswith("required_checks"):  # Skip complex objects
                lines.append(f"  {key}: {value}")

        return "\n".join(lines)
