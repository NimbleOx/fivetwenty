"""
Validation runner and orchestration utilities.
"""

from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .base import BaseValidator, ReportGenerator, ValidationResult
from .config import ValidationConfig


class ValidationRunner:
    """Orchestrates multiple validation scripts."""

    def __init__(self, config: ValidationConfig | None = None):
        self.config = config or ValidationConfig()
        self.validators: dict[str, BaseValidator] = {}
        self.results: list[ValidationResult] = []

    def register_validator(self, validator: BaseValidator) -> None:
        """Register a validator to be run."""
        self.validators[validator.name] = validator

    def register_validators(self, validators: list[BaseValidator]) -> None:
        """Register multiple validators."""
        for validator in validators:
            self.register_validator(validator)

    def run_sequential(self) -> list[ValidationResult]:
        """Run all validators sequentially."""
        self.results = []
        print(f"🔄 Running {len(self.validators)} validators sequentially...")

        for name, validator in self.validators.items():
            print(f"  ▶️  Running {name}...")
            result = validator.run()
            self.results.append(result)

            status_emoji = "✅" if result.status == "passed" else "❌" if result.status == "failed" else "⚠️"
            print(f"  {status_emoji} {name}: {result.issues_found} issues found")

        return self.results

    def run_parallel(self, max_workers: int = 4) -> list[ValidationResult]:
        """Run validators in parallel using ThreadPoolExecutor."""
        self.results = []
        print(f"🔄 Running {len(self.validators)} validators in parallel (max {max_workers} workers)...")

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all validation tasks
            future_to_validator = {executor.submit(validator.run): name for name, validator in self.validators.items()}

            # Collect results as they complete
            for future in as_completed(future_to_validator):
                validator_name = future_to_validator[future]
                try:
                    result = future.result()
                    self.results.append(result)

                    status_emoji = "✅" if result.status == "passed" else "❌" if result.status == "failed" else "⚠️"
                    print(f"  {status_emoji} {validator_name}: {result.issues_found} issues found")

                except Exception as e:
                    print(f"  ❌ {validator_name}: Exception - {e}")
                    error_result = ValidationResult(validator_name=validator_name, status="failed", issues_found=1, total_checked=0, details={"error": str(e)}, timestamp=datetime.now(timezone.utc).isoformat(), duration_seconds=0.0)
                    self.results.append(error_result)

        return self.results

    def run_filtered(self, validator_names: list[str]) -> list[ValidationResult]:
        """Run only specified validators."""
        filtered_validators = {name: validator for name, validator in self.validators.items() if name in validator_names}

        if not filtered_validators:
            print("⚠️  No matching validators found")
            return []

        original_validators = self.validators
        self.validators = filtered_validators
        results = self.run_sequential()
        self.validators = original_validators

        return results

    def check_quality_gates(self) -> dict[str, Any]:
        """Check if current results meet quality gates."""
        if not self.results:
            return {"status": "no_results", "passed": False}

        failed_gates = []
        gate_details = {}

        # Check each validator against thresholds
        for result in self.results:
            validator_name = result.validator_name.lower().replace("_", " ")

            # Map validator names to threshold keys
            threshold_key = None
            if "endpoint" in validator_name and "accuracy" in validator_name:
                threshold_key = "endpoint_accuracy"
            elif "model" in validator_name and "accuracy" in validator_name:
                threshold_key = "model_accuracy"
            elif "model" in validator_name:
                threshold_key = "model_coverage"
            elif "code" in validator_name and "example" in validator_name:
                threshold_key = "code_example_success"
            elif "link" in validator_name:
                threshold_key = "link_validation"
            elif "security" in validator_name:
                threshold_key = "security_score"
            elif "consistency" in validator_name:
                threshold_key = "consistency_score"
            elif "version" in validator_name:
                threshold_key = "version_consistency"

            if threshold_key:
                threshold = self.config.get_threshold(threshold_key)
                success_rate = result.success_rate

                gate_details[result.validator_name] = {"success_rate": success_rate, "threshold": threshold, "passed": success_rate >= threshold}

                if success_rate < threshold:
                    failed_gates.append(f"{result.validator_name}: {success_rate:.1f}% < {threshold}%")

        return {"status": "complete", "passed": len(failed_gates) == 0, "failed_gates": failed_gates, "gate_details": gate_details, "summary": {"total_validators": len(self.results), "passed_gates": len(gate_details) - len(failed_gates), "failed_gates": len(failed_gates)}}

    def generate_report(self, output_dir: Path | None = None) -> Path:
        """Generate comprehensive validation report."""
        if output_dir is None:
            # Use proper docs-tooling reports directory
            script_dir = Path(__file__).parent.parent
            output_dir = script_dir / "reports"

        output_dir.mkdir(parents=True, exist_ok=True)

        # Generate summary report
        summary = ReportGenerator.generate_summary_report(self.results)

        # Add quality gates information
        quality_gates = self.check_quality_gates()
        summary["quality_gates"] = quality_gates

        # Generate markdown report
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        md_path = output_dir / f"validation_report_{timestamp}.md"
        self._generate_markdown_report(summary, md_path)

        print("📊 Report generated:")
        print(f"  📝 Markdown: {md_path}")

        return md_path

    def _generate_markdown_report(self, summary: dict[str, Any], output_path: Path) -> None:
        """Generate markdown validation report."""
        report_data = summary["summary"]
        quality_gates = summary.get("quality_gates", {})

        md_content = f"""# Validation Report

**Generated**: {report_data["timestamp"]}

## Summary

- **Total Validators**: {report_data["total_validators"]}
- **Passed**: {report_data["passed_validators"]}
- **Failed**: {report_data["failed_validators"]}
- **Overall Success Rate**: {report_data["overall_success_rate"]:.1f}%

## Quality Gates

"""

        if quality_gates.get("passed"):
            md_content += "✅ **All quality gates PASSED**\n\n"
        else:
            md_content += "❌ **Quality gates FAILED**\n\n"
            for failure in quality_gates.get("failed_gates", []):
                md_content += f"- ⚠️  {failure}\n"
            md_content += "\n"

        md_content += "## Validator Results\n\n"

        for result_data in summary["validator_results"]:
            status_emoji = "✅" if result_data["status"] == "passed" else "❌"
            md_content += f"### {status_emoji} {result_data['name']}\n\n"
            md_content += f"- **Status**: {result_data['status']}\n"
            md_content += f"- **Issues Found**: {result_data['issues']}\n"
            md_content += f"- **Total Checked**: {result_data['total_checked']}\n"
            md_content += f"- **Success Rate**: {result_data['success_rate']:.1f}%\n"
            md_content += f"- **Duration**: {result_data['duration']:.2f}s\n\n"

            # Add detailed findings if available
            if result_data.get("details"):
                md_content += self._format_validator_details(result_data["name"], result_data["details"])
                md_content += "\n"

        # Add overall recommendations
        md_content += self._generate_overall_recommendations(summary)

        with output_path.open("w") as f:
            f.write(md_content)

    def _format_validator_details(self, validator_name: str, details: dict[str, Any]) -> str:
        """Format detailed validator findings for the report."""
        content = ""

        if validator_name == "link_validator" and "broken_links" in details:
            broken_links = details["broken_links"]
            if broken_links:
                content += "#### 🔗 Broken Links Found\n\n"

                # Group by file for better organization
                files_with_issues: dict[str, list[dict[str, Any]]] = {}
                for link in broken_links:
                    file_path = link.get("file", "Unknown")
                    if file_path not in files_with_issues:
                        files_with_issues[file_path] = []
                    files_with_issues[file_path].append(link)

                for file_path, file_links in sorted(files_with_issues.items()):
                    content += f"**{file_path}**\n"
                    for link in file_links:
                        line = link.get("line", "?")
                        url = link.get("url", "unknown")
                        text = link.get("text", "unknown")
                        content += f"- Line {line}: `{text}` → `{url}`\n"
                    content += "\n"

                # Add summary by link type
                content += "#### 📊 Issue Summary\n\n"

                # Categorize issues
                github_issues = [link for link in broken_links if "github.com/NimbleOx" in link.get("url", "")]
                external_issues = [link for link in broken_links if link not in github_issues]

                if github_issues:
                    content += f"- **GitHub Template URLs**: {len(github_issues)} (need repository configuration)\n"
                if external_issues:
                    content += f"- **Other External Links**: {len(external_issues)}\n"

                # Add recommendations for fixing broken links
                content += "#### 🔧 Recommended Actions\n\n"
                if github_issues:
                    content += "**GitHub Template URLs:**\n"
                    content += "1. Update `mkdocs.yml` or repository configuration with correct GitHub repository URL\n"
                    content += "2. Replace `NimbleOx/fivetwenty` with actual repository path\n"
                    content += "3. Verify GitHub Pages deployment is configured\n\n"

                if external_issues:
                    content += "**External Links:**\n"
                    content += "1. Verify external URLs are accessible and still valid\n"
                    content += "2. Check for redirects or moved resources\n"
                    content += "3. Consider adding retry logic for temporary failures\n\n"

                content += "\n"

        # Add other validator-specific details here as needed
        elif "files_checked" in details:
            content += "#### 📁 Files Processed\n\n"
            content += f"- **Files checked**: {details['files_checked']}\n\n"

        return content

    def _generate_overall_recommendations(self, summary: dict[str, Any]) -> str:
        """Generate overall recommendations based on validation results."""
        report_data = summary["summary"]
        quality_gates = summary.get("quality_gates", {})

        content = "## 📋 Next Steps\n\n"

        if report_data["failed_validators"] == 0:
            content += "🎉 **Excellent!** All validators passed successfully.\n\n"
            content += "**Maintenance Recommendations:**\n"
            content += "- Schedule regular validation runs (daily/weekly)\n"
            content += "- Monitor for new issues as documentation grows\n"
            content += "- Consider adding more validator types for comprehensive coverage\n\n"
        else:
            content += f"**Priority:** {report_data['failed_validators']} validator(s) need attention.\n\n"
            content += "**Immediate Actions:**\n"
            content += "1. Review detailed findings above for each failed validator\n"
            content += "2. Follow recommended actions for high-impact issues\n"
            content += "3. Re-run validation after fixes: `uv run python docs-tooling/validation/cli.py run --report`\n\n"

        if not quality_gates.get("passed", True):
            content += "⚠️  **Quality Gates Failed** - Issues exceed acceptable thresholds\n\n"

        content += "**Automation Setup:**\n"
        content += "```bash\n"
        content += "# Daily validation (recommended)\n"
        content += "0 8 * * * cd /path/to/project && uv run python docs-tooling/validation/cli.py run links --report\n\n"
        content += "# Weekly comprehensive validation\n"
        content += "0 9 * * 1 cd /path/to/project && uv run python docs-tooling/validation/cli.py run --parallel --gates --report\n"
        content += "```\n\n"

        content += "---\n*Report generated by FiveTwenty Documentation Validation System*\n"

        return content


class ValidatorRegistry:
    """Registry for managing available validators."""

    def __init__(self) -> None:
        self._validator_classes: dict[str, type[BaseValidator]] = {}
        self._descriptions: dict[str, str] = {}

    def register(self, name: str, validator_class: type[BaseValidator], description: str = "") -> None:
        """Register a validator class."""
        self._validator_classes[name] = validator_class
        self._descriptions[name] = description

    def get_validator(self, name: str, **kwargs: Any) -> BaseValidator | None:
        """Get a validator instance by name."""
        if name not in self._validator_classes:
            return None

        validator_class = self._validator_classes[name]
        return validator_class(**kwargs)

    def list_validators(self) -> dict[str, str]:
        """List all registered validators with descriptions."""
        return self._descriptions.copy()

    def create_all(self) -> list[BaseValidator]:
        """Create instances of all registered validators."""
        validators = []
        for name in self._validator_classes:
            validator = self.get_validator(name)
            if validator:
                validators.append(validator)
        return validators
