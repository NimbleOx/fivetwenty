#!/usr/bin/env python3
"""
FiveTwenty Documentation Validation Report Generator

Generates comprehensive validation reports with metrics, trends, and actionable insights.
Based on lessons learned from explanation and how-to-guides validation.
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

# Add the validation directory to the path for imports
validation_dir = Path(__file__).parent.parent
sys.path.insert(0, str(validation_dir))

try:
    from core.config import ValidationConfig
    from core.runner import ValidationRunner, ValidatorRegistry
    from validators import *
except ImportError as e:
    print(f"Import error: {e}")
    sys.exit(1)


class ValidationReportGenerator:
    """Generate comprehensive validation reports."""

    def __init__(self, output_dir: Path | None = None):
        self.output_dir = output_dir or Path("docs-tooling/validation/reports")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    def generate_comprehensive_report(self, target_dirs: list[str] | None = None) -> str:
        """Generate a comprehensive validation report for all documentation sections."""

        target_dirs = target_dirs or [
            "docs/explanation",
            "docs/how-to-guides",
            "docs/tutorials",
            "docs/api-reference"
        ]

        report_data = {
            "metadata": {
                "timestamp": datetime.now().isoformat(),
                "generator_version": "1.0.0",
                "target_directories": target_dirs
            },
            "summary": {},
            "section_reports": {},
            "critical_issues": [],
            "recommendations": [],
            "trends": {}
        }

        print("🔍 Generating comprehensive validation report...")
        print(f"📂 Target directories: {', '.join(target_dirs)}")

        # Run validation for each section
        for section in target_dirs:
            print(f"\n📋 Validating {section}...")
            section_report = self._validate_section(section)
            report_data["section_reports"][section] = section_report

        # Generate summary and analysis
        report_data["summary"] = self._generate_summary(report_data["section_reports"])
        report_data["critical_issues"] = self._identify_critical_issues(report_data["section_reports"])
        report_data["recommendations"] = self._generate_recommendations(report_data)

        # Save reports in multiple formats
        report_path = self._save_reports(report_data)

        print(f"\n✅ Validation report generated: {report_path}")
        return report_path

    def _validate_section(self, section_path: str) -> dict[str, Any]:
        """Validate a specific documentation section."""

        # Define section-specific validator sets based on our lessons learned
        section_validators = {
            "docs/explanation": ["code-examples", "financial-precision", "sdk-methods", "cross-references"],
            "docs/how-to-guides": ["code-examples", "financial-precision", "cross-references", "syntax"],
            "docs/tutorials": ["code-examples", "financial-precision", "links"],
            "docs/api-reference": ["syntax", "links", "terminology"]
        }

        validators_to_run = section_validators.get(section_path, ["links", "syntax"])

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
            results = runner.run_validation(parallel=True)

            return {
                "path": section_path,
                "validators_run": validators_to_run,
                "total_issues": sum(r.issues_found for r in results),
                "total_files_checked": sum(r.total_checked for r in results),
                "validation_results": [self._format_result(r) for r in results],
                "status": "passed" if all(r.status == "passed" for r in results) else "failed"
            }

        except Exception as e:
            return {
                "path": section_path,
                "error": str(e),
                "status": "error"
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

        # Register new validators from our work
        registry.register("code-examples", CodeExampleValidator, "Validates Python code examples for syntax and best practices")
        registry.register("cross-references", CrossReferenceValidator, "Validates internal documentation links and cross-references")
        registry.register("financial-precision", FinancialPrecisionValidator, "Validates financial examples follow precision and type safety best practices")

        return registry

    def _format_result(self, result) -> dict[str, Any]:
        """Format validation result for reporting."""
        return {
            "validator": result.validator_name,
            "status": result.status,
            "issues_found": result.issues_found,
            "total_checked": result.total_checked,
            "duration_seconds": result.duration_seconds,
            "details": result.details
        }

    def _generate_summary(self, section_reports: dict[str, Any]) -> dict[str, Any]:
        """Generate overall summary statistics."""
        total_issues = 0
        total_files = 0
        sections_passed = 0
        sections_failed = 0

        for report in section_reports.values():
            if report.get("status") == "passed":
                sections_passed += 1
            else:
                sections_failed += 1

            total_issues += report.get("total_issues", 0)
            total_files += report.get("total_files_checked", 0)

        return {
            "total_sections": len(section_reports),
            "sections_passed": sections_passed,
            "sections_failed": sections_failed,
            "total_issues_found": total_issues,
            "total_files_checked": total_files,
            "overall_status": "passed" if sections_failed == 0 else "failed",
            "success_rate": round((sections_passed / len(section_reports)) * 100, 2) if section_reports else 0
        }

    def _identify_critical_issues(self, section_reports: dict[str, Any]) -> list[dict[str, Any]]:
        """Identify critical issues requiring immediate attention."""
        critical_issues = []

        critical_validators = ["financial-precision", "code-examples", "sdk-methods"]

        for section, report in section_reports.items():
            if report.get("validation_results"):
                for result in report["validation_results"]:
                    if (result["validator"] in critical_validators and
                        result["issues_found"] > 0):
                        critical_issues.append({
                            "section": section,
                            "validator": result["validator"],
                            "issues_count": result["issues_found"],
                            "severity": "critical" if result["validator"] == "financial-precision" else "high"
                        })

        return sorted(critical_issues, key=lambda x: x["issues_count"], reverse=True)

    def _generate_recommendations(self, report_data: dict[str, Any]) -> list[str]:
        """Generate actionable recommendations based on validation results."""
        recommendations = []

        summary = report_data["summary"]
        critical_issues = report_data["critical_issues"]

        # Overall recommendations
        if summary["success_rate"] < 80:
            recommendations.append("🚨 URGENT: Less than 80% of documentation sections are passing validation")

        # Financial precision recommendations
        financial_issues = [issue for issue in critical_issues if issue["validator"] == "financial-precision"]
        if financial_issues:
            recommendations.append("💰 CRITICAL: Fix financial precision issues immediately - these can cause monetary errors in production")

        # Code example recommendations
        code_issues = [issue for issue in critical_issues if issue["validator"] == "code-examples"]
        if code_issues:
            recommendations.append("🔧 HIGH: Fix code example issues - users cannot run examples with missing imports or syntax errors")

        # Success recommendations
        if summary["success_rate"] >= 95:
            recommendations.append("✅ EXCELLENT: Documentation quality is very high, consider adding advanced validation rules")

        if not critical_issues:
            recommendations.append("🎉 SUCCESS: No critical issues found - documentation meets production standards")

        return recommendations

    def _save_reports(self, report_data: dict[str, Any]) -> str:
        """Save reports in multiple formats."""
        base_filename = f"validation_report_{self.timestamp}"

        # Save JSON report
        json_path = self.output_dir / f"{base_filename}.json"
        with open(json_path, 'w') as f:
            json.dump(report_data, f, indent=2)

        # Save human-readable report
        md_path = self.output_dir / f"{base_filename}.md"
        with open(md_path, 'w') as f:
            f.write(self._generate_markdown_report(report_data))

        # Save CSV summary for spreadsheet analysis
        csv_path = self.output_dir / f"{base_filename}_summary.csv"
        self._generate_csv_summary(report_data, csv_path)

        return str(md_path)

    def _generate_markdown_report(self, report_data: dict[str, Any]) -> str:
        """Generate human-readable markdown report."""
        md = []

        # Header
        md.append("# FiveTwenty Documentation Validation Report")
        md.append(f"**Generated:** {report_data['metadata']['timestamp']}")
        md.append(f"**Directories:** {', '.join(report_data['metadata']['target_directories'])}")
        md.append("")

        # Summary
        summary = report_data["summary"]
        md.append("## 📊 Summary")
        md.append(f"- **Overall Status:** {'✅ PASSED' if summary['overall_status'] == 'passed' else '❌ FAILED'}")
        md.append(f"- **Success Rate:** {summary['success_rate']}%")
        md.append(f"- **Sections Passed:** {summary['sections_passed']}/{summary['total_sections']}")
        md.append(f"- **Total Issues Found:** {summary['total_issues_found']}")
        md.append(f"- **Files Checked:** {summary['total_files_checked']}")
        md.append("")

        # Critical Issues
        if report_data["critical_issues"]:
            md.append("## 🚨 Critical Issues")
            for issue in report_data["critical_issues"]:
                md.append(f"- **{issue['section']}** - {issue['validator']}: {issue['issues_count']} issues ({issue['severity']} priority)")
            md.append("")

        # Recommendations
        md.append("## 💡 Recommendations")
        for rec in report_data["recommendations"]:
            md.append(f"- {rec}")
        md.append("")

        # Section Details
        md.append("## 📋 Section Reports")
        for section, report in report_data["section_reports"].items():
            status_icon = "✅" if report.get("status") == "passed" else "❌"
            md.append(f"### {status_icon} {section}")

            if "error" in report:
                md.append(f"**Error:** {report['error']}")
            else:
                md.append(f"- **Status:** {report['status']}")
                md.append(f"- **Issues Found:** {report['total_issues']}")
                md.append(f"- **Files Checked:** {report['total_files_checked']}")
                md.append(f"- **Validators:** {', '.join(report['validators_run'])}")
            md.append("")

        return '\n'.join(md)

    def _generate_csv_summary(self, report_data: dict[str, Any], csv_path: Path) -> None:
        """Generate CSV summary for analysis."""
        import csv

        with open(csv_path, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Section', 'Status', 'Total Issues', 'Files Checked', 'Validators'])

            for section, report in report_data["section_reports"].items():
                writer.writerow([
                    section,
                    report.get("status", "error"),
                    report.get("total_issues", 0),
                    report.get("total_files_checked", 0),
                    ', '.join(report.get("validators_run", []))
                ])


def main():
    """Main entry point for the validation report generator."""
    parser = argparse.ArgumentParser(description="Generate comprehensive validation report")
    parser.add_argument("--output-dir", type=str, help="Output directory for reports")
    parser.add_argument("--sections", nargs="+", help="Specific sections to validate")
    parser.add_argument("--format", choices=["json", "markdown", "csv", "all"], default="all", help="Output format")

    args = parser.parse_args()

    output_dir = Path(args.output_dir) if args.output_dir else None
    generator = ValidationReportGenerator(output_dir)

    try:
        report_path = generator.generate_comprehensive_report(args.sections)
        print(f"\n🎉 Report generated successfully: {report_path}")
        return 0
    except Exception as e:
        print(f"❌ Error generating report: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
