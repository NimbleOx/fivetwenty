"""Benchmark reporting and visualization."""

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from docs_validation.validation.benchmarks.runner import BenchmarkResults


class BenchmarkReporter:
    """Generate comprehensive benchmark reports."""

    def __init__(self, output_dir: Path | None = None):
        self.output_dir = output_dir or Path("benchmark_reports")
        self.output_dir.mkdir(exist_ok=True)

    def generate_comparison_report(
        self,
        comparison_results: dict[str, dict[str, BenchmarkResults]],
        output_format: str = "html",
    ) -> Path:
        """Generate a comprehensive comparison report."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        if output_format == "html":
            return self._generate_html_report(comparison_results, timestamp)
        if output_format == "json":
            return self._generate_json_report(comparison_results, timestamp)
        if output_format == "markdown":
            return self._generate_markdown_report(comparison_results, timestamp)
        raise ValueError(f"Unsupported output format: {output_format}")

    def _generate_html_report(
        self,
        comparison_results: dict[str, dict[str, BenchmarkResults]],
        timestamp: str,
    ) -> Path:
        """Generate HTML benchmark report with charts."""
        output_path = self.output_dir / f"benchmark_report_{timestamp}.html"

        html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Validation System Performance Benchmark</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            margin: 40px;
            background-color: #f5f5f5;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        h1 {{ color: #2c3e50; text-align: center; }}
        h2 {{ color: #34495e; border-bottom: 2px solid #3498db; padding-bottom: 10px; }}
        .summary-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }}
        .metric-card {{
            background: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            border-left: 4px solid #3498db;
        }}
        .metric-value {{
            font-size: 2em;
            font-weight: bold;
            color: #2c3e50;
        }}
        .metric-label {{
            color: #7f8c8d;
            font-size: 0.9em;
        }}
        .chart-container {{
            width: 100%;
            max-width: 600px;
            margin: 20px auto;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }}
        th, td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }}
        th {{
            background-color: #3498db;
            color: white;
        }}
        .improvement {{
            color: #27ae60;
            font-weight: bold;
        }}
        .regression {{
            color: #e74c3c;
            font-weight: bold;
        }}
        .neutral {{
            color: #7f8c8d;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 Validation System Performance Benchmark</h1>
        <p style="text-align: center; color: #7f8c8d;">
            Generated on {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
        </p>

        <h2>📊 Executive Summary</h2>
        <div class="summary-grid">
        """

        # Generate summary metrics
        if comparison_results:
            # Calculate overall improvements
            total_improvement_data = self._calculate_improvements(comparison_results)

            html_content += f"""
            <div class="metric-card">
                <div class="metric-value improvement">{total_improvement_data.get('avg_speedup', 0):.1f}x</div>
                <div class="metric-label">Average Speedup</div>
            </div>
            <div class="metric-card">
                <div class="metric-value improvement">{total_improvement_data.get('throughput_improvement', 0):.1f}%</div>
                <div class="metric-label">Throughput Improvement</div>
            </div>
            <div class="metric-card">
                <div class="metric-value neutral">{total_improvement_data.get('memory_change', 0):.1f}%</div>
                <div class="metric-label">Memory Usage Change</div>
            </div>
            <div class="metric-card">
                <div class="metric-value improvement">{total_improvement_data.get('parallel_benefit', 0):.1f}%</div>
                <div class="metric-label">Parallel Processing Benefit</div>
            </div>
            """

        html_content += """
        </div>

        <h2>📈 Performance Comparison</h2>
        <div class="chart-container">
            <canvas id="performanceChart"></canvas>
        </div>

        <h2>📋 Detailed Results</h2>
        """

        # Generate detailed tables
        for test_size, results in comparison_results.items():
            html_content += f"""
            <h3>🔍 {test_size.title()} Dataset Results</h3>
            <table>
                <thead>
                    <tr>
                        <th>System</th>
                        <th>Avg Duration (s)</th>
                        <th>Throughput (files/s)</th>
                        <th>Peak Memory (MB)</th>
                        <th>Files Processed</th>
                        <th>Success Rate (%)</th>
                    </tr>
                </thead>
                <tbody>
            """

            for system_name, result in results.items():
                if result.runs:  # Only show results that have data
                    improvement_class = self._get_improvement_class(system_name, result, results)
                    html_content += f"""
                    <tr class="{improvement_class}">
                        <td>{system_name.replace('_', ' ').title()}</td>
                        <td>{result.avg_duration:.2f}</td>
                        <td>{result.avg_throughput:.1f}</td>
                        <td>{result.peak_memory:.1f}</td>
                        <td>{result.runs[0].files_processed if result.runs else 0}</td>
                        <td>{result.runs[0].success_rate if result.runs else 0:.1f}</td>
                    </tr>
                    """

            html_content += """
                </tbody>
            </table>
            """

        # Add JavaScript for charts
        html_content += """
        <script>
        // Performance comparison chart
        const ctx = document.getElementById('performanceChart').getContext('2d');
        """

        # Generate chart data
        chart_data = self._generate_chart_data(comparison_results)
        html_content += f"""
        new Chart(ctx, {{
            type: 'bar',
            data: {json.dumps(chart_data)},
            options: {{
                responsive: true,
                plugins: {{
                    title: {{
                        display: true,
                        text: 'System Performance Comparison'
                    }}
                }},
                scales: {{
                    y: {{
                        beginAtZero: true,
                        title: {{
                            display: true,
                            text: 'Throughput (files/second)'
                        }}
                    }}
                }}
            }}
        }});
        """

        html_content += """
        </script>
    </div>
</body>
</html>
        """

        output_path.write_text(html_content, encoding="utf-8")
        return output_path

    def _generate_json_report(
        self,
        comparison_results: dict[str, dict[str, BenchmarkResults]],
        timestamp: str,
    ) -> Path:
        """Generate JSON benchmark report."""
        output_path = self.output_dir / f"benchmark_report_{timestamp}.json"

        report_data = {
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "report_type": "validation_system_benchmark",
                "version": "2.0.0",
            },
            "summary": self._calculate_improvements(comparison_results),
            "detailed_results": {},
        }

        for test_size, results in comparison_results.items():
            report_data["detailed_results"][test_size] = {}

            for system_name, result in results.items():
                report_data["detailed_results"][test_size][system_name] = {
                    "benchmark_name": result.benchmark_name,
                    "description": result.test_description,
                    "metrics": {
                        "avg_duration": result.avg_duration,
                        "median_duration": result.median_duration,
                        "duration_stdev": result.duration_stdev,
                        "avg_throughput": result.avg_throughput,
                        "peak_memory_mb": result.peak_memory,
                        "avg_memory_mb": result.avg_memory,
                    },
                    "individual_runs": [
                        {
                            "duration_seconds": run.duration_seconds,
                            "throughput_files_per_second": run.throughput_files_per_second,
                            "peak_memory_mb": run.peak_memory_mb,
                            "files_processed": run.files_processed,
                            "issues_found": run.issues_found,
                            "success_rate": run.success_rate,
                        }
                        for run in result.runs
                    ],
                }

        output_path.write_text(json.dumps(report_data, indent=2), encoding="utf-8")
        return output_path

    def _generate_markdown_report(
        self,
        comparison_results: dict[str, dict[str, BenchmarkResults]],
        timestamp: str,
    ) -> Path:
        """Generate Markdown benchmark report."""
        output_path = self.output_dir / f"benchmark_report_{timestamp}.md"

        md_lines = [
            "# 🚀 Validation System Performance Benchmark",
            "",
            f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "## 📊 Executive Summary",
            "",
        ]

        # Add summary
        summary_data = self._calculate_improvements(comparison_results)
        md_lines.extend([
            f"- **Average Speedup:** {summary_data.get('avg_speedup', 0):.1f}x",
            f"- **Throughput Improvement:** {summary_data.get('throughput_improvement', 0):.1f}%",
            f"- **Memory Usage Change:** {summary_data.get('memory_change', 0):+.1f}%",
            f"- **Parallel Processing Benefit:** {summary_data.get('parallel_benefit', 0):.1f}%",
            "",
            "## 📈 Detailed Results",
            "",
        ])

        # Add detailed results
        for test_size, results in comparison_results.items():
            md_lines.extend([
                f"### 🔍 {test_size.title()} Dataset Results",
                "",
                "| System | Avg Duration (s) | Throughput (files/s) | Peak Memory (MB) | Files Processed | Success Rate (%) |",
                "|--------|------------------|---------------------|------------------|-----------------|------------------|",
            ])

            for system_name, result in results.items():
                if result.runs:
                    md_lines.append(
                        f"| {system_name.replace('_', ' ').title()} | "
                        f"{result.avg_duration:.2f} | "
                        f"{result.avg_throughput:.1f} | "
                        f"{result.peak_memory:.1f} | "
                        f"{result.runs[0].files_processed} | "
                        f"{result.runs[0].success_rate:.1f} |",
                    )

            md_lines.append("")

        output_path.write_text("\n".join(md_lines), encoding="utf-8")
        return output_path

    def _calculate_improvements(self, comparison_results: dict[str, dict[str, BenchmarkResults]]) -> dict[str, float]:
        """Calculate overall performance improvements."""
        total_speedups = []
        total_throughput_improvements = []
        total_memory_changes = []
        parallel_benefits = []

        for test_size, results in comparison_results.items():
            new_system = results.get("new_system")
            old_system = results.get("old_system")
            new_sequential = results.get("new_system_sequential")

            if new_system and old_system and new_system.runs and old_system.runs:
                # Calculate speedup
                speedup = old_system.avg_duration / new_system.avg_duration
                total_speedups.append(speedup)

                # Calculate throughput improvement
                throughput_improvement = ((new_system.avg_throughput - old_system.avg_throughput) /
                                        old_system.avg_throughput) * 100
                total_throughput_improvements.append(throughput_improvement)

                # Calculate memory change
                memory_change = ((new_system.peak_memory - old_system.peak_memory) /
                               old_system.peak_memory) * 100
                total_memory_changes.append(memory_change)

            # Calculate parallel benefit
            if new_system and new_sequential and new_system.runs and new_sequential.runs:
                parallel_benefit = ((new_sequential.avg_duration - new_system.avg_duration) /
                                  new_sequential.avg_duration) * 100
                parallel_benefits.append(parallel_benefit)

        return {
            "avg_speedup": sum(total_speedups) / len(total_speedups) if total_speedups else 0,
            "throughput_improvement": sum(total_throughput_improvements) / len(total_throughput_improvements) if total_throughput_improvements else 0,
            "memory_change": sum(total_memory_changes) / len(total_memory_changes) if total_memory_changes else 0,
            "parallel_benefit": sum(parallel_benefits) / len(parallel_benefits) if parallel_benefits else 0,
        }

    def _get_improvement_class(self, system_name: str, result: BenchmarkResults, all_results: dict[str, BenchmarkResults]) -> str:
        """Get CSS class based on performance improvement."""
        if "new_system" in system_name:
            return "improvement"
        if "old_system" in system_name:
            return "neutral"
        return "neutral"

    def _generate_chart_data(self, comparison_results: dict[str, dict[str, BenchmarkResults]]) -> dict[str, Any]:
        """Generate data for Chart.js."""
        labels = []
        new_system_data = []
        old_system_data = []
        sequential_data = []

        for test_size, results in comparison_results.items():
            labels.append(test_size.title())

            new_system = results.get("new_system")
            old_system = results.get("old_system")
            sequential = results.get("new_system_sequential")

            new_system_data.append(new_system.avg_throughput if new_system and new_system.runs else 0)
            old_system_data.append(old_system.avg_throughput if old_system and old_system.runs else 0)
            sequential_data.append(sequential.avg_throughput if sequential and sequential.runs else 0)

        return {
            "labels": labels,
            "datasets": [
                {
                    "label": "New System (Parallel)",
                    "data": new_system_data,
                    "backgroundColor": "rgba(52, 152, 219, 0.8)",
                    "borderColor": "rgba(52, 152, 219, 1)",
                    "borderWidth": 1,
                },
                {
                    "label": "New System (Sequential)",
                    "data": sequential_data,
                    "backgroundColor": "rgba(155, 89, 182, 0.8)",
                    "borderColor": "rgba(155, 89, 182, 1)",
                    "borderWidth": 1,
                },
                {
                    "label": "Old System",
                    "data": old_system_data,
                    "backgroundColor": "rgba(231, 76, 60, 0.8)",
                    "borderColor": "rgba(231, 76, 60, 1)",
                    "borderWidth": 1,
                },
            ],
        }

    def generate_scalability_report(
        self,
        scalability_results: dict[int, BenchmarkResults],
        output_format: str = "html",
    ) -> Path:
        """Generate scalability analysis report."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = self.output_dir / f"scalability_report_{timestamp}.{output_format}"

        if output_format == "html":
            # Generate HTML scalability report
            html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Scalability Analysis Report</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 40px; }}
        .chart-container {{ width: 100%; max-width: 800px; margin: 20px auto; }}
        table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
        th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }}
        th {{ background-color: #3498db; color: white; }}
    </style>
</head>
<body>
    <h1>📈 Scalability Analysis Report</h1>
    <p>Generated on {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>

    <div class="chart-container">
        <canvas id="scalabilityChart"></canvas>
    </div>

    <h2>📊 Scalability Data</h2>
    <table>
        <thead>
            <tr>
                <th>Worker Count</th>
                <th>Avg Duration (s)</th>
                <th>Throughput (files/s)</th>
                <th>Efficiency (%)</th>
                <th>Peak Memory (MB)</th>
            </tr>
        </thead>
        <tbody>
            """

            # Calculate efficiency relative to single worker
            single_worker_throughput = scalability_results.get(1)
            if single_worker_throughput:
                single_throughput = single_worker_throughput.avg_throughput
            else:
                single_throughput = 1  # Fallback

            for worker_count in sorted(scalability_results.keys()):
                result = scalability_results[worker_count]
                efficiency = (result.avg_throughput / (single_throughput * worker_count)) * 100 if single_throughput > 0 else 0

                html_content += f"""
                <tr>
                    <td>{worker_count}</td>
                    <td>{result.avg_duration:.2f}</td>
                    <td>{result.avg_throughput:.1f}</td>
                    <td>{efficiency:.1f}</td>
                    <td>{result.peak_memory:.1f}</td>
                </tr>
                """

            # Generate chart data
            worker_counts = sorted(scalability_results.keys())
            throughputs = [scalability_results[w].avg_throughput for w in worker_counts]

            html_content += f"""
        </tbody>
    </table>

    <script>
        const ctx = document.getElementById('scalabilityChart').getContext('2d');
        new Chart(ctx, {{
            type: 'line',
            data: {{
                labels: {worker_counts},
                datasets: [{{
                    label: 'Throughput (files/s)',
                    data: {throughputs},
                    borderColor: 'rgba(52, 152, 219, 1)',
                    backgroundColor: 'rgba(52, 152, 219, 0.1)',
                    tension: 0.1
                }}]
            }},
            options: {{
                responsive: true,
                plugins: {{
                    title: {{
                        display: true,
                        text: 'Scalability: Throughput vs Worker Count'
                    }}
                }},
                scales: {{
                    y: {{
                        beginAtZero: true,
                        title: {{
                            display: true,
                            text: 'Throughput (files/second)'
                        }}
                    }},
                    x: {{
                        title: {{
                            display: true,
                            text: 'Number of Workers'
                        }}
                    }}
                }}
            }}
        }});
    </script>
</body>
</html>
            """

            output_path.write_text(html_content, encoding="utf-8")

        return output_path
