"""Rich output formatters for validation results."""

import csv
import json
from abc import ABC, abstractmethod
from datetime import datetime
from io import StringIO
from typing import Any

from rich.console import Console
from rich.panel import Panel
from rich.progress import BarColumn, Progress, SpinnerColumn, TaskProgressColumn, TextColumn
from rich.table import Table
from rich.tree import Tree

from docs_validation.validation.core.results import IssueSeverity, ValidationIssue, ValidationResult, ValidationSummary


class BaseFormatter(ABC):
    """Base class for result formatters."""

    @abstractmethod
    def format_summary(self, summary: ValidationSummary) -> str:
        """Format a validation summary."""

    @abstractmethod
    def format_result(self, result: ValidationResult) -> str:
        """Format a single validation result."""

    @abstractmethod
    def format_issue(self, issue: ValidationIssue) -> str:
        """Format a single validation issue."""


class ConsoleFormatter(BaseFormatter):
    """Rich console formatter for interactive output."""

    def __init__(self, console: Console | None = None, show_progress: bool = True):
        self.console = console or Console()
        self.show_progress = show_progress

    def format_summary(self, summary: ValidationSummary) -> str:
        """Format validation summary with rich formatting."""
        # Create summary table
        table = Table(title="Validation Summary", show_header=True, header_style="bold blue")
        table.add_column("Metric", style="cyan", no_wrap=True)
        table.add_column("Value", style="green", justify="right")

        # Add summary metrics
        table.add_row("Total Checks", str(len(summary.results)))
        table.add_row("Passed", f"[green]{summary.passed_checks}[/green]")
        table.add_row("Failed", f"[red]{summary.failed_checks}[/red]")
        table.add_row("Success Rate", f"{summary.overall_success_rate:.1f}%")
        table.add_row("Total Issues", str(summary.total_issues))
        table.add_row("Files Checked", str(summary.total_files_checked))
        table.add_row("Duration", f"{summary.total_duration:.2f}s")

        with StringIO() as buffer:
            console = Console(file=buffer, force_terminal=True)
            console.print(table)
            return buffer.getvalue()

    def format_result(self, result: ValidationResult) -> str:
        """Format a single validation result."""
        # Status icon and color
        if result.is_successful:
            status_icon = "PASSED"
            status_color = "green"
        else:
            status_icon = "FAILED"
            status_color = "red"

        # Create result panel
        title = f"{status_icon} {result.check_name}"
        content = []

        content.append(f"Status: [{status_color}]{result.status.value}[/{status_color}]")
        content.append(f"Files checked: {result.files_checked}")
        content.append(f"Issues found: {result.issues_found}")
        content.append(f"Duration: {result.duration_seconds:.2f}s")

        if result.issues:
            content.append("")
            content.append("Issues:")
            for issue in result.issues[:5]:  # Show first 5 issues
                content.append(f"  - {self._format_issue_inline(issue)}")

            if len(result.issues) > 5:
                content.append(f"  ... and {len(result.issues) - 5} more issues")

        panel = Panel("\\n".join(content), title=title, border_style=status_color)

        with StringIO() as buffer:
            console = Console(file=buffer, force_terminal=True)
            console.print(panel)
            return buffer.getvalue()

    def format_issue(self, issue: ValidationIssue) -> str:
        """Format a single validation issue."""
        severity_colors = {
            IssueSeverity.ERROR: "red",
            IssueSeverity.WARNING: "yellow",
            IssueSeverity.INFO: "blue",
        }

        color = severity_colors.get(issue.severity, "white")

        lines = []
        lines.append(f"[{color}]{issue.severity.value.upper()}[/{color}]: {issue.message}")

        if issue.file_path:
            location = str(issue.file_path)
            if hasattr(issue, "line_number") and issue.line_number:
                location += f":{issue.line_number}"
                if hasattr(issue, "column_number") and issue.column_number:
                    location += f":{issue.column_number}"
            elif hasattr(issue, "line") and issue.line:
                location += f":{issue.line}"
                if hasattr(issue, "column") and issue.column:
                    location += f":{issue.column}"
            lines.append(f"  Location: {location}")

        if issue.context:
            lines.append(f"  Context: {issue.context}")

        if issue.suggestion:
            lines.append(f"  Suggestion: {issue.suggestion}")

        return "\\n".join(lines)

    def _format_issue_inline(self, issue: ValidationIssue) -> str:
        """Format issue for inline display."""
        severity_colors = {
            IssueSeverity.ERROR: "red",
            IssueSeverity.WARNING: "yellow",
            IssueSeverity.INFO: "blue",
        }

        color = severity_colors.get(issue.severity, "white")
        return f"[{color}]{issue.severity.value}[/{color}]: {issue.message}"

    def create_progress_tracker(self, total_checks: int) -> Progress:
        """Create a progress tracker for validation execution."""
        return Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            transient=True,
            console=self.console,
        )

    def format_check_tree(self, summary: ValidationSummary) -> str:
        """Format results as a tree structure."""
        tree = Tree("Validation Results")

        for result in summary.results:
            status_icon = "PASSED" if result.is_successful else "FAILED"
            branch = tree.add(f"{status_icon} {result.check_name} ({result.issues_found} issues)")

            if result.issues:
                issues_by_severity = {}
                for issue in result.issues:
                    severity = issue.severity.value
                    if severity not in issues_by_severity:
                        issues_by_severity[severity] = []
                    issues_by_severity[severity].append(issue)

                for severity, issues in issues_by_severity.items():
                    severity_branch = branch.add(f"{severity.upper()} ({len(issues)})")
                    for issue in issues[:3]:  # Show first 3 issues per severity
                        severity_branch.add(f"{issue.message}")

        with StringIO() as buffer:
            console = Console(file=buffer, force_terminal=True)
            console.print(tree)
            return buffer.getvalue()


class JSONFormatter(BaseFormatter):
    """JSON formatter for programmatic consumption."""

    def __init__(self, indent: int = 2):
        self.indent = indent

    def format_summary(self, summary: ValidationSummary) -> str:
        """Format summary as JSON."""
        data = {
            "summary": {
                "total_checks": len(summary.results),
                "passed_checks": summary.passed_checks,
                "failed_checks": summary.failed_checks,
                "success_rate": summary.overall_success_rate,
                "total_issues": summary.total_issues,
                "total_files_checked": summary.total_files_checked,
                "duration_seconds": summary.total_duration,
                "timestamp": datetime.now().isoformat(),
            },
            "results": [self._result_to_dict(result) for result in summary.results],
        }

        return json.dumps(data, indent=self.indent, ensure_ascii=False)

    def format_result(self, result: ValidationResult) -> str:
        """Format result as JSON."""
        return json.dumps(self._result_to_dict(result), indent=self.indent)

    def format_issue(self, issue: ValidationIssue) -> str:
        """Format issue as JSON."""
        return json.dumps(self._issue_to_dict(issue), indent=self.indent)

    def _result_to_dict(self, result: ValidationResult) -> dict[str, Any]:
        """Convert validation result to dictionary."""
        return {
            "check_name": result.check_name,
            "status": result.status.value,
            "is_successful": result.is_successful,
            "files_checked": result.files_checked,
            "issues_found": result.issues_found,
            "duration_seconds": result.duration_seconds,
            "issues": [self._issue_to_dict(issue) for issue in result.issues],
        }

    def _issue_to_dict(self, issue: ValidationIssue) -> dict[str, Any]:
        """Convert validation issue to dictionary."""
        return {
            "severity": issue.severity.value,
            "message": issue.message,
            "file_path": str(issue.file_path) if issue.file_path else None,
            "line_number": getattr(issue, "line_number", None) or getattr(issue, "line", None),
            "column_number": getattr(issue, "column_number", None) or getattr(issue, "column", None),
            "context": issue.context,
            "suggestion": issue.suggestion,
        }


class HTMLFormatter(BaseFormatter):
    """HTML formatter for web-based reports."""

    def format_summary(self, summary: ValidationSummary) -> str:
        """Format summary as HTML."""
        # Calculate severity breakdown
        severity_counts = {"error": 0, "warning": 0, "info": 0}
        for result in summary.results:
            for issue in result.issues:
                severity_counts[issue.severity.value] += 1

        html = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Validation Report</title>
            <style>
                body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 40px; }}
                .summary {{ background: #f8f9fa; padding: 20px; border-radius: 8px; margin-bottom: 30px; }}
                .metric {{ display: inline-block; margin: 10px 20px; text-align: center; }}
                .metric-value {{ font-size: 2em; font-weight: bold; }}
                .metric-label {{ color: #666; font-size: 0.9em; }}
                .success {{ color: #28a745; }}
                .warning {{ color: #ffc107; }}
                .error {{ color: #dc3545; }}
                .check-result {{ border: 1px solid #ddd; margin: 10px 0; border-radius: 5px; }}
                .check-header {{ padding: 15px; background: #f8f9fa; border-bottom: 1px solid #ddd; }}
                .check-name {{ font-weight: bold; font-size: 1.1em; }}
                .check-status {{ float: right; }}
                .issues {{ padding: 15px; }}
                .issue {{ margin: 10px 0; padding: 10px; border-left: 4px solid; }}
                .issue.error {{ border-left-color: #dc3545; background: #f8d7da; }}
                .issue.warning {{ border-left-color: #ffc107; background: #fff3cd; }}
                .issue.info {{ border-left-color: #17a2b8; background: #d1ecf1; }}
            </style>
        </head>
        <body>
            <h1>Validation Report</h1>

            <div class="summary">
                <div class="metric">
                    <div class="metric-value">{len(summary.results)}</div>
                    <div class="metric-label">Total Checks</div>
                </div>
                <div class="metric">
                    <div class="metric-value success">{summary.passed_checks}</div>
                    <div class="metric-label">Passed</div>
                </div>
                <div class="metric">
                    <div class="metric-value error">{summary.failed_checks}</div>
                    <div class="metric-label">Failed</div>
                </div>
                <div class="metric">
                    <div class="metric-value">{summary.overall_success_rate:.1f}%</div>
                    <div class="metric-label">Success Rate</div>
                </div>
                <div class="metric">
                    <div class="metric-value error">{severity_counts["error"]}</div>
                    <div class="metric-label">Errors</div>
                </div>
                <div class="metric">
                    <div class="metric-value warning">{severity_counts["warning"]}</div>
                    <div class="metric-label">Warnings</div>
                </div>
                <div class="metric">
                    <div class="metric-value">{summary.total_duration:.2f}s</div>
                    <div class="metric-label">Duration</div>
                </div>
            </div>

            <h2>Check Results</h2>
        """

        for result in summary.results:
            html += self._format_result_html(result)

        html += """
        </body>
        </html>
        """

        return html

    def format_result(self, result: ValidationResult) -> str:
        """Format result as HTML fragment."""
        return self._format_result_html(result)

    def format_issue(self, issue: ValidationIssue) -> str:
        """Format issue as HTML fragment."""
        return self._format_issue_html(issue)

    def _format_result_html(self, result: ValidationResult) -> str:
        """Format a validation result as HTML."""
        status_class = "success" if result.is_successful else "error"
        status_text = "PASSED" if result.is_successful else "FAILED"

        html = f"""
        <div class="check-result">
            <div class="check-header">
                <span class="check-name">{result.check_name}</span>
                <span class="check-status {status_class}">{status_text}</span>
                <div style="clear: both; margin-top: 10px; color: #666;">
                    Files: {result.files_checked} | Issues: {result.issues_found} | Duration: {result.duration_seconds:.2f}s
                </div>
            </div>
        """

        if result.issues:
            html += '<div class="issues">'
            for issue in result.issues:
                html += self._format_issue_html(issue)
            html += "</div>"

        html += "</div>"
        return html

    def _format_issue_html(self, issue: ValidationIssue) -> str:
        """Format a validation issue as HTML."""
        location = ""
        if issue.file_path:
            location = str(issue.file_path)
            line_num = getattr(issue, "line_number", None) or getattr(issue, "line", None)
            col_num = getattr(issue, "column_number", None) or getattr(issue, "column", None)
            if line_num:
                location += f":{line_num}"
                if col_num:
                    location += f":{col_num}"

        html = f"""
        <div class="issue {issue.severity.value}">
            <strong>{issue.severity.value.upper()}:</strong> {issue.message}
        """

        if location:
            html += f"<br><small>Location: {location}</small>"

        if issue.context:
            html += f"<br><small>Context: {issue.context}</small>"

        if issue.suggestion:
            html += f"<br><small>Suggestion: {issue.suggestion}</small>"

        html += "</div>"
        return html


class MarkdownFormatter(BaseFormatter):
    """Markdown formatter for documentation and reports."""

    def format_summary(self, summary: ValidationSummary) -> str:
        """Format summary as Markdown."""
        # Calculate severity breakdown
        severity_counts = {"error": 0, "warning": 0, "info": 0}
        for result in summary.results:
            for issue in result.issues:
                severity_counts[issue.severity.value] += 1

        md = f"""# Validation Report

## Summary

| Metric | Value |
|--------|-------|
| Total Checks | {len(summary.results)} |
| Passed | {summary.passed_checks} |
| Failed | {summary.failed_checks} |
| Success Rate | {summary.overall_success_rate:.1f}% |
| Total Issues | {summary.total_issues} |
| Files Checked | {summary.total_files_checked} |
| Duration | {summary.total_duration:.2f}s |

### Issue Breakdown

| Severity | Count |
|----------|-------|
| Errors | {severity_counts["error"]} |
| Warnings | {severity_counts["warning"]} |
| Info | {severity_counts["info"]} |

## Check Results

"""

        for result in summary.results:
            md += self._format_result_markdown(result) + "\\n"

        return md

    def format_result(self, result: ValidationResult) -> str:
        """Format result as Markdown."""
        return self._format_result_markdown(result)

    def format_issue(self, issue: ValidationIssue) -> str:
        """Format issue as Markdown."""
        return self._format_issue_markdown(issue)

    def _format_result_markdown(self, result: ValidationResult) -> str:
        """Format a validation result as Markdown."""
        status_icon = "PASSED" if result.is_successful else "FAILED"

        md = f"""### {status_icon} {result.check_name}

**Status:** {result.status.value}
**Files checked:** {result.files_checked}
**Issues found:** {result.issues_found}
**Duration:** {result.duration_seconds:.2f}s

"""

        if result.issues:
            md += "#### Issues\\n\\n"
            for issue in result.issues:
                md += self._format_issue_markdown(issue) + "\\n"

        return md

    def _format_issue_markdown(self, issue: ValidationIssue) -> str:
        """Format a validation issue as Markdown."""
        severity_icons = {
            IssueSeverity.ERROR: "ERROR",
            IssueSeverity.WARNING: "WARNING",
            IssueSeverity.INFO: "INFO",
        }

        icon = severity_icons.get(issue.severity, "UNKNOWN")

        md = f"- {icon} **{issue.severity.value.upper()}:** {issue.message}"

        if issue.file_path:
            location = str(issue.file_path)
            line_num = getattr(issue, "line_number", None) or getattr(issue, "line", None)
            col_num = getattr(issue, "column_number", None) or getattr(issue, "column", None)
            if line_num:
                location += f":{line_num}"
                if col_num:
                    location += f":{col_num}"
            md += f"\\n  - Location: `{location}`"

        if issue.context:
            md += f"\\n  - Context: {issue.context}"

        if issue.suggestion:
            md += f"\\n  - Suggestion: {issue.suggestion}"

        return md


class CSVFormatter(BaseFormatter):
    """CSV formatter for data analysis."""

    def format_summary(self, summary: ValidationSummary) -> str:
        """Format summary as CSV."""
        output = StringIO()
        writer = csv.writer(output)

        # Write header
        writer.writerow(
            [
                "check_name",
                "status",
                "files_checked",
                "issues_found",
                "duration_seconds",
                "severity",
                "message",
                "file_path",
                "line_number",
                "column_number",
                "context",
                "suggestion",
            ]
        )

        # Write data
        for result in summary.results:
            if result.issues:
                for issue in result.issues:
                    writer.writerow(
                        [
                            result.check_name,
                            result.status.value,
                            result.files_checked,
                            result.issues_found,
                            result.duration_seconds,
                            issue.severity.value,
                            issue.message,
                            str(issue.file_path) if issue.file_path else "",
                            getattr(issue, "line_number", None) or getattr(issue, "line", None) or "",
                            getattr(issue, "column_number", None) or getattr(issue, "column", None) or "",
                            issue.context or "",
                            issue.suggestion or "",
                        ]
                    )
            else:
                # Write row for checks with no issues
                writer.writerow(
                    [
                        result.check_name,
                        result.status.value,
                        result.files_checked,
                        result.issues_found,
                        result.duration_seconds,
                        "",
                        "",
                        "",
                        "",
                        "",
                        "",
                        "",
                    ]
                )

        return output.getvalue()

    def format_result(self, result: ValidationResult) -> str:
        """Format result as CSV (single check)."""
        # Create a mini-summary for this result
        from docs_validation.validation.core.results import ValidationSummary

        mini_summary = ValidationSummary(results=[result])
        return self.format_summary(mini_summary)

    def format_issue(self, issue: ValidationIssue) -> str:
        """Format issue as CSV row."""
        output = StringIO()
        writer = csv.writer(output)

        writer.writerow(
            [
                "severity",
                "message",
                "file_path",
                "line_number",
                "column_number",
                "context",
                "suggestion",
            ]
        )
        writer.writerow(
            [
                issue.severity.value,
                issue.message,
                str(issue.file_path) if issue.file_path else "",
                getattr(issue, "line_number", None) or getattr(issue, "line", None) or "",
                getattr(issue, "column_number", None) or getattr(issue, "column", None) or "",
                issue.context or "",
                issue.suggestion or "",
            ]
        )

        return output.getvalue()
