#!/usr/bin/env python3
"""
FiveTwenty Documentation Validation Dashboard

Real-time validation metrics dashboard with trend analysis and quality monitoring.
Based on comprehensive lessons learned from explanation and how-to-guides validation.
"""

import argparse
import json
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

# Add the validation directory to the path for imports
validation_dir = Path(__file__).parent.parent
sys.path.insert(0, str(validation_dir))

try:
    from core.base import ValidationResult
    from core.config import ValidationConfig
    from core.runner import ValidationRunner, ValidatorRegistry
    from validators.code_examples import CodeExampleValidator
    from validators.cross_references import CrossReferenceValidator
    from validators.financial_precision import FinancialPrecisionValidator
    from validators.links import LinkValidator
    from validators.prose import ProseValidator
    from validators.sdk_methods import SDKMethodValidator
    from validators.security import SecurityValidator
    from validators.syntax import SyntaxValidator
    from validators.terminology import TerminologyValidator
except ImportError as e:
    print(f"Import error: {e}")
    sys.exit(1)


class ValidationDashboard:
    """Real-time validation metrics dashboard with trend analysis."""

    def __init__(self, data_dir: Path | None = None):
        self.data_dir = data_dir or Path("docs-tooling/validation/dashboard-data")
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.metrics_file = self.data_dir / "metrics_history.json"

    def run_dashboard(self, watch_mode: bool = False, sections: list[str] | None = None) -> None:
        """Run the validation dashboard."""

        sections = sections or [
            "docs/explanation",
            "docs/how-to-guides",
            "docs/tutorials",
            "docs/api-reference"
        ]

        print("🔍 FiveTwenty Documentation Validation Dashboard")
        print("=" * 60)

        if watch_mode:
            print("🔄 Running in watch mode (Ctrl+C to exit)")
            try:
                while True:
                    self._run_validation_cycle(sections)
                    print("\n⏰ Next check in 30 seconds...")
                    time.sleep(30)
            except KeyboardInterrupt:
                print("\n👋 Dashboard stopped.")
        else:
            self._run_validation_cycle(sections)

    def _run_validation_cycle(self, sections: list[str]) -> None:
        """Run one validation cycle and update dashboard."""

        cycle_data: dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "sections": {},
            "summary": {}
        }

        print(f"\n📊 Validation Cycle - {datetime.now(timezone.utc).strftime('%H:%M:%S')}")
        print("-" * 40)

        total_issues = 0
        total_files = 0
        critical_issues = 0

        # Run validation for each section
        for section in sections:
            section_metrics = self._validate_section(section)
            cycle_data["sections"][section] = section_metrics

            total_issues += section_metrics.get("total_issues", 0)
            total_files += section_metrics.get("total_files", 0)
            critical_issues += section_metrics.get("critical_issues", 0)

            # Display section status
            status_icon = "✅" if section_metrics.get("status") == "passed" else "❌"
            print(f"{status_icon} {section:25} | {section_metrics.get('total_issues', 0):3d} issues | {section_metrics.get('total_files', 0):3d} files")

        # Calculate summary
        cycle_data["summary"] = {
            "total_issues": total_issues,
            "total_files": total_files,
            "critical_issues": critical_issues,
            "sections_count": len(sections),
            "overall_status": "passed" if total_issues == 0 else "failed"
        }

        # Display summary
        print("-" * 40)
        print(f"📋 Total: {total_issues} issues across {total_files} files")
        print(f"🚨 Critical: {critical_issues} financial/import issues")

        # Save metrics
        self._save_metrics(cycle_data)

        # Show trends if available
        self._display_trends()

        # Show quality assessment
        self._display_quality_assessment(cycle_data["summary"])

    def _validate_section(self, section_path: str) -> dict[str, Any]:
        """Validate a specific documentation section with optimized validators."""

        # Section-specific validator sets based on lessons learned
        validator_sets = {
            "docs/explanation": ["code-examples", "financial-precision", "sdk-methods"],
            "docs/how-to-guides": ["code-examples", "financial-precision", "cross-references"],
            "docs/tutorials": ["code-examples", "financial-precision", "syntax"],
            "docs/api-reference": ["syntax", "links", "terminology"]
        }

        validators_to_run = validator_sets.get(section_path, ["syntax", "links"])

        try:
            registry = self._setup_registry()
            config = ValidationConfig()
            runner = ValidationRunner(config)

            # Register validators for this section
            for validator_name in validators_to_run:
                validator = registry.get_validator(validator_name)
                if validator:
                    runner.register_validator(validator)

            # Run validation
            results = runner.run_parallel(max_workers=4)

            # Count critical issues (financial precision and missing imports)
            critical_count = 0
            for result in results:
                if result.validator_name in ["financial-precision", "code-examples"]:
                    critical_count += result.issues_found

            return {
                "status": "passed" if all(r.status == "passed" for r in results) else "failed",
                "total_issues": sum(r.issues_found for r in results),
                "total_files": sum(r.total_checked for r in results),
                "critical_issues": critical_count,
                "validators_run": validators_to_run,
                "duration": sum(r.duration_seconds for r in results),
                "results": [self._format_result(r) for r in results]
            }

        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "total_issues": 0,
                "total_files": 0,
                "critical_issues": 0
            }

    def _setup_registry(self) -> ValidatorRegistry:
        """Set up validator registry with all available validators."""
        registry = ValidatorRegistry()

        # Register core validators
        registry.register("links", LinkValidator, "Validates internal and external links")
        registry.register("syntax", SyntaxValidator, "Validates markdown syntax and structure")
        registry.register("security", SecurityValidator, "Scans documentation for potential security issues")
        registry.register("terminology", TerminologyValidator, "Validates consistent terminology usage")
        registry.register("prose", ProseValidator, "Validates prose quality and style using Vale")
        registry.register("sdk-methods", SDKMethodValidator, "Validates current SDK method names in documentation")

        # Register enhanced validators from our lessons learned
        registry.register("code-examples", CodeExampleValidator, "Validates Python code examples for syntax and best practices")
        registry.register("cross-references", CrossReferenceValidator, "Validates internal documentation links and cross-references")
        registry.register("financial-precision", FinancialPrecisionValidator, "Validates financial examples follow precision and type safety best practices")

        return registry

    def _format_result(self, result: ValidationResult) -> dict[str, Any]:
        """Format validation result for dashboard."""
        return {
            "validator": result.validator_name,
            "status": result.status,
            "issues": result.issues_found,
            "files": result.total_checked,
            "duration": round(result.duration_seconds, 2)
        }

    def _save_metrics(self, cycle_data: dict[str, Any]) -> None:
        """Save metrics to historical data file."""

        # Load existing metrics
        if self.metrics_file.exists():
            with self.metrics_file.open() as f:
                history = json.load(f)
        else:
            history = {"cycles": []}

        # Add new cycle
        history["cycles"].append(cycle_data)

        # Keep only last 100 cycles to prevent unbounded growth
        if len(history["cycles"]) > 100:
            history["cycles"] = history["cycles"][-100:]

        # Save updated history
        with self.metrics_file.open('w') as f:
            json.dump(history, f, indent=2)

    def _display_trends(self) -> None:
        """Display trend analysis based on historical data."""

        if not self.metrics_file.exists():
            return

        with self.metrics_file.open() as f:
            history = json.load(f)

        cycles = history.get("cycles", [])
        if len(cycles) < 2:
            return

        print("\n📈 Trends (vs previous cycle):")

        current = cycles[-1]["summary"]
        previous = cycles[-2]["summary"]

        # Calculate changes
        issue_change = current["total_issues"] - previous["total_issues"]
        critical_change = current["critical_issues"] - previous["critical_issues"]

        # Display trends with indicators
        issue_indicator = "📉" if issue_change < 0 else "📈" if issue_change > 0 else "➡️"
        critical_indicator = "📉" if critical_change < 0 else "📈" if critical_change > 0 else "➡️"

        print(f"   {issue_indicator} Total Issues: {current['total_issues']} ({issue_change:+d})")
        print(f"   {critical_indicator} Critical Issues: {current['critical_issues']} ({critical_change:+d})")

        # Show quality trend over last 10 cycles
        if len(cycles) >= 10:
            recent_issues = [c["summary"]["total_issues"] for c in cycles[-10:]]
            avg_issues = sum(recent_issues) / len(recent_issues)
            current_issues = current["total_issues"]

            if current_issues < avg_issues * 0.8:
                print("   🎉 Quality improving! (Below 10-cycle average)")
            elif current_issues > avg_issues * 1.2:
                print("   ⚠️  Quality declining (Above 10-cycle average)")

    def _display_quality_assessment(self, summary: dict[str, Any]) -> None:
        """Display overall quality assessment with recommendations."""

        print("\n🎯 Quality Assessment:")

        total_issues = summary["total_issues"]
        critical_issues = summary["critical_issues"]

        # Overall quality grade
        if total_issues == 0:
            grade = "A+"
            message = "Perfect! Documentation meets all standards."
        elif critical_issues == 0 and total_issues <= 5:
            grade = "A"
            message = "Excellent quality with minor issues."
        elif critical_issues == 0 and total_issues <= 20:
            grade = "B"
            message = "Good quality, some improvements needed."
        elif critical_issues <= 3:
            grade = "C"
            message = "Acceptable but needs attention to critical issues."
        else:
            grade = "D"
            message = "Poor quality - immediate action required."

        print(f"   📊 Grade: {grade}")
        print(f"   💬 {message}")

        # Specific recommendations
        if critical_issues > 0:
            print(f"   🚨 URGENT: Fix {critical_issues} critical financial/import issues first")

        if total_issues > 50:
            print("   🔧 RECOMMENDED: Run auto-fix script to resolve common patterns")

        if total_issues == 0:
            print("   ✨ NEXT: Consider adding advanced validation rules")

    def generate_report(self, days: int = 7) -> str:
        """Generate comprehensive trend report for specified days."""

        if not self.metrics_file.exists():
            return "No historical data available."

        with self.metrics_file.open() as f:
            history = json.load(f)

        cycles = history.get("cycles", [])
        if not cycles:
            return "No validation cycles found."

        # Filter cycles within time period
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)
        recent_cycles = []

        for cycle in cycles:
            cycle_date = datetime.fromisoformat(cycle["timestamp"])
            if cycle_date >= cutoff_date:
                recent_cycles.append(cycle)

        if not recent_cycles:
            return f"No validation data found for the last {days} days."

        # Generate report
        report = []
        report.append(f"# Validation Trend Report ({days} days)")
        report.append(f"**Generated:** {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"**Cycles Analyzed:** {len(recent_cycles)}")
        report.append("")

        # Summary statistics
        total_issues = [c["summary"]["total_issues"] for c in recent_cycles]
        critical_issues = [c["summary"]["critical_issues"] for c in recent_cycles]

        report.append("## Summary Statistics")
        report.append(f"- **Current Issues:** {total_issues[-1] if total_issues else 0}")
        report.append(f"- **Average Issues:** {sum(total_issues) / len(total_issues):.1f}")
        report.append(f"- **Peak Issues:** {max(total_issues) if total_issues else 0}")
        report.append(f"- **Best Day:** {min(total_issues) if total_issues else 0} issues")
        report.append(f"- **Critical Issues Peak:** {max(critical_issues) if critical_issues else 0}")
        report.append("")

        # Trend analysis
        if len(recent_cycles) >= 2:
            first_issues = recent_cycles[0]["summary"]["total_issues"]
            last_issues = recent_cycles[-1]["summary"]["total_issues"]
            trend = last_issues - first_issues

            report.append("## Trend Analysis")
            if trend < 0:
                report.append(f"📉 **Improving:** {abs(trend)} fewer issues than {days} days ago")
            elif trend > 0:
                report.append(f"📈 **Declining:** {trend} more issues than {days} days ago")
            else:
                report.append("➡️ **Stable:** No change in issue count")
            report.append("")

        # Critical issues analysis
        if any(critical_issues):
            report.append("## Critical Issues Alert")
            report.append("⚠️  Found critical financial/import issues in validation cycles")
            report.append("These issues can cause monetary errors or code execution failures.")
            report.append("")

        # Recommendations
        report.append("## Recommendations")
        current_summary = recent_cycles[-1]["summary"]

        if current_summary["critical_issues"] > 0:
            report.append("1. 🚨 **URGENT:** Run financial precision and code example validation")
            report.append("2. 🔧 **ACTION:** Use auto-fix script to resolve common patterns")
        elif current_summary["total_issues"] > 20:
            report.append("1. 🔧 **RECOMMENDED:** Run comprehensive validation with auto-fix")
            report.append("2. 📋 **FOLLOW-UP:** Review validation rules and thresholds")
        else:
            report.append("1. ✅ **MAINTAIN:** Current quality standards are good")
            report.append("2. 🎯 **ENHANCE:** Consider adding advanced validation rules")

        return '\n'.join(report)

    def export_metrics(self, output_format: str = "json") -> str:
        """Export metrics in specified format."""

        if not self.metrics_file.exists():
            return "No metrics data available."

        if output_format == "json":
            return str(self.metrics_file)
        if output_format == "csv":
            csv_path = self.data_dir / "metrics_export.csv"
            self._export_to_csv(csv_path)
            return str(csv_path)
        return "Unsupported format. Use 'json' or 'csv'."

    def _export_to_csv(self, csv_path: Path) -> None:
        """Export metrics to CSV format."""
        import csv

        with self.metrics_file.open() as f:
            history = json.load(f)

        cycles = history.get("cycles", [])

        with csv_path.open('w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Timestamp', 'Total Issues', 'Critical Issues', 'Total Files', 'Overall Status'])

            for cycle in cycles:
                summary = cycle["summary"]
                writer.writerow([
                    cycle["timestamp"],
                    summary["total_issues"],
                    summary["critical_issues"],
                    summary["total_files"],
                    summary["overall_status"]
                ])


def main() -> int:
    """Main entry point for the validation dashboard."""
    parser = argparse.ArgumentParser(description="FiveTwenty Documentation Validation Dashboard")
    parser.add_argument("--watch", action="store_true", help="Run in watch mode (continuous monitoring)")
    parser.add_argument("--sections", nargs="+", help="Specific documentation sections to monitor")
    parser.add_argument("--data-dir", type=str, help="Directory to store dashboard data")
    parser.add_argument("--report", type=int, metavar="DAYS", help="Generate trend report for N days")
    parser.add_argument("--export", choices=["json", "csv"], help="Export metrics data")

    args = parser.parse_args()

    data_dir = Path(args.data_dir) if args.data_dir else None
    dashboard = ValidationDashboard(data_dir)

    try:
        if args.report:
            report = dashboard.generate_report(days=args.report)
            print(report)
        elif args.export:
            export_path = dashboard.export_metrics(output_format=args.export)
            print(f"📄 Metrics exported to: {export_path}")
        else:
            dashboard.run_dashboard(watch_mode=args.watch, sections=args.sections)
        return 0
    except Exception as e:
        print(f"❌ Dashboard error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
