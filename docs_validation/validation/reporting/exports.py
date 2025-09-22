"""Export utilities for validation reports."""

import json
import zipfile
from datetime import datetime
from pathlib import Path
from typing import Any

from docs_validation.validation.core.results import ValidationSummary
from docs_validation.validation.reporting.aggregators import ResultAggregator, TrendAnalyzer
from docs_validation.validation.reporting.formatters import (
    CSVFormatter,
    HTMLFormatter,
    JSONFormatter,
    MarkdownFormatter,
)


class ReportExporter:
    """Export validation reports in multiple formats."""

    def __init__(self, output_dir: Path | None = None):
        self.output_dir = output_dir or Path("validation_reports")
        self.output_dir.mkdir(exist_ok=True)

        # Initialize formatters
        self.formatters = {
            "json": JSONFormatter(),
            "html": HTMLFormatter(),
            "markdown": MarkdownFormatter(),
            "csv": CSVFormatter(),
        }

    def export_summary(
        self,
        summary: ValidationSummary,
        formats: list[str] | None = None,
        filename_prefix: str = "validation_report",
    ) -> dict[str, Path]:
        """Export validation summary in specified formats."""
        if formats is None:
            formats = ["json", "html", "markdown"]

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        exported_files = {}

        for format_name in formats:
            if format_name not in self.formatters:
                raise ValueError(f"Unsupported format: {format_name}")

            formatter = self.formatters[format_name]
            content = formatter.format_summary(summary)

            # Generate filename
            filename = f"{filename_prefix}_{timestamp}.{format_name}"
            if format_name == "markdown":
                filename = filename.replace(".markdown", ".md")
            elif format_name == "html":
                filename = filename.replace(".html", ".html")

            output_path = self.output_dir / filename

            # Write content
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(content)

            exported_files[format_name] = output_path

        return exported_files

    def export_aggregated_report(
        self,
        aggregator: ResultAggregator,
        trend_analyzer: TrendAnalyzer | None = None,
        formats: list[str] | None = None,
    ) -> dict[str, Path]:
        """Export comprehensive aggregated report."""
        if formats is None:
            formats = ["json", "html"]

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        exported_files = {}

        # Collect aggregated data
        aggregated_data = {
            "timestamp": datetime.now().isoformat(),
            "check_statistics": aggregator.get_check_statistics(),
            "file_hotspots": aggregator.get_file_hotspots(),
            "severity_distribution": aggregator.get_severity_distribution(),
            "common_issues": aggregator.get_most_common_issues(),
        }

        # Add trend data if available
        if trend_analyzer:
            aggregated_data["trends"] = {
                "overall_trend": [
                    {
                        "timestamp": point.timestamp.isoformat(),
                        "total_checks": point.total_checks,
                        "passed_checks": point.passed_checks,
                        "failed_checks": point.failed_checks,
                        "total_issues": point.total_issues,
                        "success_rate": point.success_rate,
                        "duration": point.duration,
                    }
                    for point in trend_analyzer.get_overall_trend()
                ],
                "check_trends": {
                    check_name: {
                        "average_duration": trend.average_duration,
                        "issue_trend": trend.issue_trend,
                        "data_points": len(trend.points),
                    }
                    for check_name, trend in trend_analyzer.get_check_trends().items()
                },
                "performance_metrics": trend_analyzer.get_performance_metrics(),
            }

        for format_name in formats:
            filename = f"aggregated_report_{timestamp}.{format_name}"
            output_path = self.output_dir / filename

            if format_name == "json":
                with open(output_path, "w", encoding="utf-8") as f:
                    json.dump(aggregated_data, f, indent=2, ensure_ascii=False)

            elif format_name == "html":
                html_content = self._generate_aggregated_html(aggregated_data)
                with open(output_path, "w", encoding="utf-8") as f:
                    f.write(html_content)

            elif format_name == "markdown":
                md_content = self._generate_aggregated_markdown(aggregated_data)
                output_path = output_path.with_suffix(".md")
                with open(output_path, "w", encoding="utf-8") as f:
                    f.write(md_content)

            exported_files[format_name] = output_path

        return exported_files

    def create_report_bundle(
        self,
        summary: ValidationSummary,
        aggregator: ResultAggregator | None = None,
        trend_analyzer: TrendAnalyzer | None = None,
    ) -> Path:
        """Create a comprehensive report bundle as a ZIP file."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        bundle_path = self.output_dir / f"validation_bundle_{timestamp}.zip"

        with zipfile.ZipFile(bundle_path, "w", zipfile.ZIP_DEFLATED) as zipf:
            # Export basic summary in all formats
            summary_files = self.export_summary(summary, ["json", "html", "markdown", "csv"])
            for format_name, file_path in summary_files.items():
                zipf.write(file_path, f"summary.{format_name}")

            # Export aggregated report if available
            if aggregator:
                agg_files = self.export_aggregated_report(aggregator, trend_analyzer, ["json", "html"])
                for format_name, file_path in agg_files.items():
                    zipf.write(file_path, f"aggregated.{format_name}")

            # Add metadata
            metadata = {
                "created_at": datetime.now().isoformat(),
                "summary": {
                    "total_checks": len(summary.results),
                    "passed_checks": summary.passed_checks,
                    "failed_checks": summary.failed_checks,
                    "success_rate": summary.overall_success_rate,
                    "total_issues": summary.total_issues,
                    "duration": summary.total_duration,
                },
                "included_files": [
                    "summary.json",
                    "summary.html",
                    "summary.md",
                    "summary.csv",
                ],
            }

            if aggregator:
                metadata["included_files"].extend(["aggregated.json", "aggregated.html"])

            # Write metadata
            metadata_path = self.output_dir / "metadata.json"
            with open(metadata_path, "w", encoding="utf-8") as f:
                json.dump(metadata, f, indent=2)
            zipf.write(metadata_path, "metadata.json")

        return bundle_path

    def _generate_aggregated_html(self, data: dict[str, Any]) -> str:
        """Generate HTML for aggregated report."""
        html = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Aggregated Validation Report</title>
            <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
            <style>
                body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 40px; }}
                .section {{ margin: 30px 0; padding: 20px; border: 1px solid #ddd; border-radius: 8px; }}
                .metric {{ display: inline-block; margin: 10px 20px; text-align: center; }}
                .metric-value {{ font-size: 1.5em; font-weight: bold; }}
                .metric-label {{ color: #666; font-size: 0.9em; }}
                .chart-container {{ width: 100%; max-width: 600px; margin: 20px auto; }}
                table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
                th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }}
                th {{ background-color: #f8f9fa; font-weight: bold; }}
                .error {{ color: #dc3545; }}
                .warning {{ color: #ffc107; }}
                .info {{ color: #17a2b8; }}
                .improving {{ color: #28a745; }}
                .declining {{ color: #dc3545; }}
                .stable {{ color: #6c757d; }}
            </style>
        </head>
        <body>
            <h1>📊 Aggregated Validation Report</h1>
            <p>Generated on: {data["timestamp"]}</p>

            <div class="section">
                <h2>📈 Check Statistics</h2>
                <table>
                    <thead>
                        <tr>
                            <th>Check Name</th>
                            <th>Total Runs</th>
                            <th>Success Rate</th>
                            <th>Avg Issues</th>
                            <th>Avg Duration</th>
                            <th>Errors</th>
                            <th>Warnings</th>
                        </tr>
                    </thead>
                    <tbody>
        """

        for check_name, stats in data.get("check_statistics", {}).items():
            html += f"""
                        <tr>
                            <td>{check_name}</td>
                            <td>{stats["total_runs"]}</td>
                            <td>{stats["success_rate"]:.1f}%</td>
                            <td>{stats["average_issues_per_run"]:.1f}</td>
                            <td>{stats["average_duration"]:.2f}s</td>
                            <td class="error">{stats["errors"]}</td>
                            <td class="warning">{stats["warnings"]}</td>
                        </tr>
            """

        html += """
                    </tbody>
                </table>
            </div>

            <div class="section">
                <h2>🔥 File Hotspots</h2>
                <table>
                    <thead>
                        <tr>
                            <th>File Path</th>
                            <th>Total Issues</th>
                            <th>Errors</th>
                            <th>Warnings</th>
                            <th>Info</th>
                        </tr>
                    </thead>
                    <tbody>
        """

        for hotspot in data.get("file_hotspots", [])[:10]:  # Top 10
            file_path = hotspot[0] if isinstance(hotspot, tuple) else hotspot["file_path"]
            total_issues = hotspot[1] if isinstance(hotspot, tuple) else hotspot["total_issues"]
            severity_breakdown = hotspot[2] if isinstance(hotspot, tuple) else hotspot["severity_breakdown"]

            html += f"""
                        <tr>
                            <td><code>{file_path}</code></td>
                            <td>{total_issues}</td>
                            <td class="error">{severity_breakdown.get("error", 0)}</td>
                            <td class="warning">{severity_breakdown.get("warning", 0)}</td>
                            <td class="info">{severity_breakdown.get("info", 0)}</td>
                        </tr>
            """

        html += """
                    </tbody>
                </table>
            </div>

            <div class="section">
                <h2>📊 Severity Distribution</h2>
                <div class="chart-container">
                    <canvas id="severityChart"></canvas>
                </div>
            </div>
        """

        # Add trend section if available
        if "trends" in data:
            html += """
            <div class="section">
                <h2>📈 Trends</h2>
                <div class="chart-container">
                    <canvas id="trendChart"></canvas>
                </div>
            </div>
            """

        html += """
            <script>
                // Severity distribution chart
                const severityCtx = document.getElementById('severityChart').getContext('2d');
        """

        # Add severity distribution data
        severity_dist = data.get("severity_distribution", {})
        if severity_dist:
            labels = list(severity_dist.keys())
            values = [severity_dist[label]["count"] for label in labels]

            html += f"""
                new Chart(severityCtx, {{
                    type: 'doughnut',
                    data: {{
                        labels: {labels},
                        datasets: [{{
                            data: {values},
                            backgroundColor: ['#dc3545', '#ffc107', '#17a2b8']
                        }}]
                    }},
                    options: {{
                        responsive: true,
                        plugins: {{
                            title: {{
                                display: true,
                                text: 'Issue Distribution by Severity'
                            }}
                        }}
                    }}
                }});
            """

        # Add trend chart if available
        if "trends" in data and data["trends"].get("overall_trend"):
            trend_data = data["trends"]["overall_trend"]
            timestamps = [point["timestamp"] for point in trend_data]
            success_rates = [point["success_rate"] for point in trend_data]

            html += f"""
                // Trend chart
                const trendCtx = document.getElementById('trendChart').getContext('2d');
                new Chart(trendCtx, {{
                    type: 'line',
                    data: {{
                        labels: {[ts[:10] for ts in timestamps]},  # Just dates
                        datasets: [{{
                            label: 'Success Rate (%)',
                            data: {success_rates},
                            borderColor: '#28a745',
                            backgroundColor: 'rgba(40, 167, 69, 0.1)',
                            tension: 0.1
                        }}]
                    }},
                    options: {{
                        responsive: true,
                        plugins: {{
                            title: {{
                                display: true,
                                text: 'Validation Success Rate Trend'
                            }}
                        }},
                        scales: {{
                            y: {{
                                beginAtZero: true,
                                max: 100
                            }}
                        }}
                    }}
                }});
            """

        html += """
            </script>
        </body>
        </html>
        """

        return html

    def _generate_aggregated_markdown(self, data: dict[str, Any]) -> str:
        """Generate Markdown for aggregated report."""
        md = f"""# 📊 Aggregated Validation Report

Generated on: {data["timestamp"]}

## 📈 Check Statistics

| Check Name | Runs | Success Rate | Avg Issues | Avg Duration | Errors | Warnings |
|------------|------|--------------|------------|--------------|--------|----------|
"""

        for check_name, stats in data.get("check_statistics", {}).items():
            md += f"| {check_name} | {stats['total_runs']} | {stats['success_rate']:.1f}% | {stats['average_issues_per_run']:.1f} | {stats['average_duration']:.2f}s | {stats['errors']} | {stats['warnings']} |\\n"

        md += """
## 🔥 File Hotspots

| File Path | Total Issues | Errors | Warnings | Info |
|-----------|--------------|--------|----------|------|
"""

        for hotspot in data.get("file_hotspots", [])[:10]:  # Top 10
            file_path = hotspot[0] if isinstance(hotspot, tuple) else hotspot["file_path"]
            total_issues = hotspot[1] if isinstance(hotspot, tuple) else hotspot["total_issues"]
            severity_breakdown = hotspot[2] if isinstance(hotspot, tuple) else hotspot["severity_breakdown"]

            md += f"| `{file_path}` | {total_issues} | {severity_breakdown.get('error', 0)} | {severity_breakdown.get('warning', 0)} | {severity_breakdown.get('info', 0)} |\\n"

        md += """
## 📊 Severity Distribution

"""

        severity_dist = data.get("severity_distribution", {})
        for severity, info in severity_dist.items():
            md += f"- **{severity.title()}**: {info['count']} ({info['percentage']:.1f}%)\\n"

        md += """
## 🔍 Most Common Issues

"""

        for i, (message, count, files) in enumerate(data.get("common_issues", [])[:5], 1):
            md += f"### {i}. {message}\\n"
            md += f"**Occurrences**: {count}\\n"
            md += f"**Affected files**: {len(files)}\\n\\n"

        # Add trend information if available
        if "trends" in data:
            trends = data["trends"]
            md += """
## 📈 Trends

### Performance Metrics
"""

            perf_metrics = trends.get("performance_metrics", {})
            if "recent_metrics" in perf_metrics:
                recent = perf_metrics["recent_metrics"]
                md += f"""
**Recent Performance** (last 5 runs):
- Success Rate: {recent["success_rate"]:.1f}%
- Average Duration: {recent["average_duration"]:.2f}s
- Average Issues: {recent["average_issues"]:.1f}
"""

            if "trends" in perf_metrics:
                trend_data = perf_metrics["trends"]
                md += f"""
**Trends**:
- Success Rate: {"+" if trend_data["success_rate_change"] >= 0 else ""}{trend_data["success_rate_change"]:.1f}%
- Duration: {"+" if trend_data["duration_change"] >= 0 else ""}{trend_data["duration_change"]:.2f}s
- Issues: {"+" if trend_data["issues_change"] >= 0 else ""}{trend_data["issues_change"]:.1f}
"""

        return md
