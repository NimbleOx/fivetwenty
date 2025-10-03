"""Enhanced markdown reporter for validation results."""

from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

from ..models import IssueSeverity, ValidationIssue, ValidationSummary


class MarkdownReporter:
    """Generates comprehensive markdown reports for validation results."""

    def __init__(self, project_root: Path = Path()):
        self.project_root = project_root

    def generate_report(self, summary: ValidationSummary, all_issues: list[ValidationIssue], output_path: Path, include_detailed_issues: bool = True, max_issues_per_file: int = 10, include_code_snippets: bool = True) -> None:
        """Generate a comprehensive markdown validation report."""

        # Organize data for reporting
        issues_by_file = self._group_issues_by_file(all_issues)
        issues_by_validator = self._group_issues_by_validator(all_issues)
        issues_by_severity = self._group_issues_by_severity(all_issues)
        rule_statistics = self._calculate_rule_statistics(all_issues)

        # Generate markdown content
        report_content = self._build_report_content(summary, issues_by_file, issues_by_validator, issues_by_severity, rule_statistics, include_detailed_issues, max_issues_per_file, include_code_snippets)

        # Write report
        output_path.write_text(report_content, encoding="utf-8")

    def _build_report_content(
        self,
        summary: ValidationSummary,
        issues_by_file: dict[str, list[ValidationIssue]],
        issues_by_validator: dict[str, list[ValidationIssue]],
        issues_by_severity: dict[IssueSeverity, list[ValidationIssue]],
        rule_statistics: dict[str, int],
        include_detailed_issues: bool,
        max_issues_per_file: int,
        include_code_snippets: bool,
    ) -> str:
        """Build the complete markdown report content."""

        content = []

        # Header and metadata
        content.extend(self._generate_header(summary))
        content.extend(self._generate_executive_summary(summary, issues_by_severity))

        # High-level statistics
        content.extend(self._generate_statistics_section(summary, issues_by_validator, rule_statistics))

        # Validator performance analysis
        content.extend(self._generate_validator_analysis(summary, issues_by_validator))

        # File-level analysis
        content.extend(self._generate_file_analysis(issues_by_file))

        # Rule breakdown
        content.extend(self._generate_rule_breakdown(rule_statistics))

        # Detailed issues (if requested)
        if include_detailed_issues:
            content.extend(self._generate_detailed_issues(issues_by_file, max_issues_per_file, include_code_snippets))

        # Recommendations and next steps
        content.extend(self._generate_recommendations(summary, issues_by_severity, rule_statistics))

        # Appendices
        content.extend(self._generate_appendices(summary))

        return "\n".join(content)

    def _generate_header(self, summary: ValidationSummary) -> list[str]:
        """Generate report header with metadata."""
        timestamp = datetime.now(tz=timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

        return [
            "# FiveTwenty Documentation Validation Report",
            "",
            f"**Generated:** {timestamp}",
            f"**Project Root:** `{self.project_root.resolve()}`",
            f"**Files Analyzed:** {summary.total_files}",
            f"**Validators Used:** {len(summary.validator_summaries)}",
            f"**Total Runtime:** {summary.duration_ms / 1000:.2f}s",
            "",
            "---",
            "",
        ]

    def _generate_executive_summary(self, summary: ValidationSummary, issues_by_severity: dict[IssueSeverity, list[ValidationIssue]]) -> list[str]:
        """Generate executive summary section."""
        success_rate = (summary.passed_files / max(summary.total_files, 1)) * 100
        total_issues = summary.total_issues

        status_emoji = "✅" if summary.total_issues == 0 else "❌"
        urgency_level = self._get_urgency_level(issues_by_severity)

        return [
            "## 📊 Executive Summary",
            "",
            f"**Overall Status:** {status_emoji} {'PASSED' if summary.total_issues == 0 else 'FAILED'}",
            f"**Success Rate:** {success_rate:.1f}%",
            f"**Urgency Level:** {urgency_level}",
            "",
            "### Issue Breakdown",
            "",
            "| Severity | Count | Impact |",
            "|----------|-------|---------|",
            f"| 🔴 Errors | {len(issues_by_severity.get(IssueSeverity.ERROR, []))} | Critical - Prevents code execution |",
            f"| 🟡 Warnings | {len(issues_by_severity.get(IssueSeverity.WARNING, []))} | Important - Style/best practice issues |",
            f"| 🔵 Info | {len(issues_by_severity.get(IssueSeverity.INFO, []))} | Minor - Suggestions for improvement |",
            f"| **Total** | **{total_issues}** | |",
            "",
            self._generate_quality_assessment(success_rate),
            "",
        ]

    def _generate_statistics_section(self, summary: ValidationSummary, issues_by_validator: dict[str, list[ValidationIssue]], rule_statistics: dict[str, int]) -> list[str]:
        """Generate detailed statistics section."""
        return [
            "## 📈 Detailed Statistics",
            "",
            "### Files Analysis",
            "",
            f"- **Total Files Processed:** {summary.total_files}",
            f"- **Files with Issues:** {summary.total_files - summary.passed_files}",
            f"- **Clean Files:** {summary.passed_files}",
            f"- **Average Issues per File:** {(sum(len(issues) for issues in issues_by_validator.values()) / max(summary.total_files, 1)):.1f}",
            "",
            "### Processing Performance",
            "",
            f"- **Total Processing Time:** {summary.duration_ms / 1000:.2f}s",
            f"- **Average Time per File:** {(summary.duration_ms / 1000 / max(summary.total_files, 1)):.3f}s",
            f"- **Validators Active:** {len(summary.validator_summaries)}",
            "",
            "### Rule Distribution",
            "",
            f"- **Unique Rules Triggered:** {len(rule_statistics)}",
            f"- **Most Common Rule:** {max(rule_statistics.items(), key=lambda x: x[1]) if rule_statistics else 'None'}",
            f"- **Average Issues per Rule:** {(sum(rule_statistics.values()) / max(len(rule_statistics), 1)):.1f}",
            "",
        ]

    def _generate_validator_analysis(self, summary: ValidationSummary, issues_by_validator: dict[str, list[ValidationIssue]]) -> list[str]:
        """Generate per-validator analysis."""
        content = ["## 🔍 Validator Performance Analysis", "", "| Validator | Files | Issues | Errors | Warnings | Success Rate | Duration |", "|-----------|-------|--------|--------|----------|--------------|----------|"]

        for result in summary.validator_summaries:
            validator_issues = issues_by_validator.get(result.name, [])
            error_count = len([i for i in validator_issues if i.severity == IssueSeverity.ERROR])
            warning_count = len([i for i in validator_issues if i.severity == IssueSeverity.WARNING])
            success_rate = result.success_rate

            content.append(f"| **{result.name}** | {result.files_checked} | {len(validator_issues)} | {error_count} | {warning_count} | {success_rate:.1f}% | {result.duration_ms:.0f}ms |")

        content.extend(["", "### Validator Insights", ""])

        # Add insights for each validator
        for result in summary.validator_summaries:
            validator_issues = issues_by_validator.get(result.name, [])
            if validator_issues:
                insight = self._get_validator_insight(result.name, validator_issues)
                content.append(f"**{result.name}**: {insight}")

        content.append("")
        return content

    def _generate_file_analysis(self, issues_by_file: dict[str, list[ValidationIssue]]) -> list[str]:
        """Generate file-level analysis."""
        # Sort files by issue count
        files_with_issues = [(file_path, len(issues)) for file_path, issues in issues_by_file.items()]
        files_with_issues.sort(key=lambda x: x[1], reverse=True)

        content = ["## 📁 File-Level Analysis", "", "### Top 20 Files by Issue Count", "", "| Rank | File | Issues | Errors | Warnings |", "|------|------|--------|--------|----------|"]

        for rank, (file_path, issue_count) in enumerate(files_with_issues[:20], 1):
            issues = issues_by_file[file_path]
            error_count = len([i for i in issues if i.severity == IssueSeverity.ERROR])
            warning_count = len([i for i in issues if i.severity == IssueSeverity.WARNING])

            # Truncate long file paths for readability
            display_path = file_path if len(file_path) <= 60 else f"...{file_path[-57:]}"

            content.append(f"| {rank} | `{display_path}` | {issue_count} | {error_count} | {warning_count} |")

        content.extend(["", "### File Categories Analysis", ""])

        # Categorize files by type
        categories = defaultdict(list)
        for file_path, issues in issues_by_file.items():
            category = self._categorize_file(file_path)
            categories[category].append((file_path, len(issues)))

        for category, files in categories.items():
            avg_issues = sum(count for _, count in files) / len(files)
            content.append(f"**{category}**: {len(files)} files, {avg_issues:.1f} avg issues per file")

        content.append("")
        return content

    def _generate_rule_breakdown(self, rule_statistics: dict[str, int]) -> list[str]:
        """Generate rule breakdown analysis."""
        # Sort rules by frequency
        sorted_rules = sorted(rule_statistics.items(), key=lambda x: x[1], reverse=True)

        content = ["## 📋 Rule Violation Analysis", "", "### Top 15 Most Frequent Rules", "", "| Rank | Rule ID | Count | Description | Severity |", "|------|---------|-------|-------------|----------|"]

        for rank, (rule_id, count) in enumerate(sorted_rules[:15], 1):
            description = self._get_rule_description(rule_id)
            severity = self._get_rule_severity_indicator(rule_id)

            content.append(f"| {rank} | `{rule_id}` | {count} | {description} | {severity} |")

        content.extend(["", "### Rule Categories", ""])

        # Group rules by category
        rule_categories = defaultdict(list)
        for rule_id, count in rule_statistics.items():
            category = self._categorize_rule(rule_id)
            rule_categories[category].append((rule_id, count))

        for category, rules in rule_categories.items():
            total_issues = sum(count for _, count in rules)
            content.append(f"**{category}**: {len(rules)} rules, {total_issues} total violations")

        content.append("")
        return content

    def _generate_detailed_issues(self, issues_by_file: dict[str, list[ValidationIssue]], max_issues_per_file: int, include_code_snippets: bool) -> list[str]:
        """Generate detailed issue listings."""
        content = ["## 🔍 Detailed Issue Analysis", ""]

        # First, show most problematic files
        content.extend(["### Most Problematic Files", "", f"*Showing up to {max_issues_per_file} issues per file for files with the most issues.*", ""])

        # Sort files by issue count and show top files
        sorted_files = sorted(issues_by_file.items(), key=lambda x: len(x[1]), reverse=True)

        for file_path, issues in sorted_files[:10]:  # Top 10 files
            if not issues:
                continue

            content.extend([f"#### 📄 `{file_path}`", "", f"**Total Issues**: {len(issues)} | **Errors**: {len([i for i in issues if i.severity == IssueSeverity.ERROR])} | **Warnings**: {len([i for i in issues if i.severity == IssueSeverity.WARNING])}", ""])

            # Show issues grouped by severity
            issues_by_sev = defaultdict(list)
            for issue in issues:
                issues_by_sev[issue.severity].append(issue)

            # Show errors first, then warnings
            for severity in [IssueSeverity.ERROR, IssueSeverity.WARNING]:
                sev_issues = issues_by_sev[severity]
                if not sev_issues:
                    continue

                severity_emoji = {"ERROR": "🔴", "WARNING": "🟡", "INFO": "🔵"}
                content.append(f"##### {severity_emoji.get(severity.value, '•')} {severity.value.title()}s")
                content.append("")

                for issue in sev_issues[:max_issues_per_file]:
                    content.extend(self._format_issue_details(issue, include_code_snippets))

            content.append("---")
            content.append("")

        # Second, show examples from each validator type to ensure visibility of all issue types
        content.extend(self._generate_validator_examples(issues_by_file, include_code_snippets))

        return content

    def _generate_validator_examples(self, issues_by_file: dict[str, list[ValidationIssue]], include_code_snippets: bool) -> list[str]:
        """Generate examples from each validator type to ensure all issue types are visible."""
        content = ["### Examples by Validator Type", "", "*Representative examples from each validator to ensure all issue types are visible.*", ""]

        # Group issues by validator (rule_id prefix)
        issues_by_validator: dict[str, list[ValidationIssue]] = defaultdict(list)
        for issues in issues_by_file.values():
            for issue in issues:
                # Extract validator name from rule_id (e.g., "markdown_syntax_list_spacing" -> "markdown_syntax")
                if issue.rule_id:
                    validator_name = issue.rule_id.split("_")[0:2]  # Take first two parts for compound names
                    if len(validator_name) >= 2:
                        validator_key = "_".join(validator_name)
                    else:
                        validator_key = validator_name[0] if validator_name else "unknown"
                else:
                    validator_key = "unknown"

                issues_by_validator[validator_key].append(issue)

        # Define validator display names and priorities
        validator_priorities = {
            "markdown_syntax": ("📝 Markdown Syntax", 1),
            "code_linting": ("🔍 Code Linting", 2),
            "code_typing": ("🔧 Type Checking", 3),
            "python_syntax": ("🐍 Python Syntax", 4),
            "cross_references": ("🔗 Cross References", 5),
            "sdk_methods": ("📚 SDK Methods", 6),
            "security": ("🔒 Security", 7),
            "financial_precision": ("💰 Financial Precision", 8),
            "code_execution": ("⚡ Code Execution", 9),
            "external_links": ("🌐 External Links", 10),
        }

        # Sort validators by priority, ensuring markdown_syntax appears first
        sorted_validators = sorted(issues_by_validator.items(), key=lambda x: validator_priorities.get(x[0], (x[0], 999))[1])

        for validator_key, validator_issues in sorted_validators:
            if not validator_issues:
                continue

            display_name = validator_priorities.get(validator_key, (validator_key.replace("_", " ").title(), 999))[0]

            # Show up to 2 examples from this validator
            example_issues = validator_issues[:2]

            content.extend([f"#### {display_name}", ""])

            for issue in example_issues:
                content.append(f"**File**: `{issue.file_path}` (Line {issue.line})")
                content.append(f"**Issue**: {issue.message}")
                content.append(f"**Rule**: `{issue.rule_id}`")

                if issue.context:
                    content.append(f"**Context**: {issue.context}")

                if issue.suggestion:
                    content.append(f"💡 **Suggestion**: {issue.suggestion}")

                content.append("")

            content.append("---")
            content.append("")

        return content

    def _generate_recommendations(self, summary: ValidationSummary, issues_by_severity: dict[IssueSeverity, list[ValidationIssue]], rule_statistics: dict[str, int]) -> list[str]:
        """Generate recommendations and action plan."""
        error_count = len(issues_by_severity.get(IssueSeverity.ERROR, []))
        warning_count = len(issues_by_severity.get(IssueSeverity.WARNING, []))

        content = ["## 🎯 Recommendations & Action Plan", "", "### Immediate Actions (High Priority)", ""]

        if error_count > 0:
            content.extend([f"1. **Fix Critical Errors ({error_count} issues)**", "   - These prevent code from executing and must be addressed first", "   - Focus on syntax errors, import issues, and type mismatches", "   - Prioritize API reference and tutorial documentation", ""])

        if warning_count > 50:
            content.extend([f"2. **Address High-Frequency Warnings ({warning_count} issues)**", "   - Focus on the most common rule violations first", "   - Implement consistent style guidelines across documentation", "   - Consider automated fixing for style issues", ""])

        # Generate specific recommendations based on most common issues
        if rule_statistics:
            top_rule, top_count = max(rule_statistics.items(), key=lambda x: x[1])
            recommendation = self._get_rule_recommendation(top_rule)
            content.extend([f"3. **Most Critical Pattern ({top_rule}: {top_count} occurrences)**", f"   - {recommendation}", ""])

        content.extend(
            [
                "### Long-term Improvements",
                "",
                "1. **Establish Code Standards**",
                "   - Create coding guidelines for documentation examples",
                "   - Implement pre-commit hooks for validation",
                "   - Set up automated quality gates",
                "",
                "2. **Template Development**",
                "   - Create standard templates for common code patterns",
                "   - Ensure consistent import statements across examples",
                "   - Establish type annotation standards",
                "",
                "3. **Process Integration**",
                "   - Add validation to CI/CD pipeline",
                "   - Implement quality metrics tracking",
                "   - Regular validation report reviews",
                "",
                "### Success Metrics",
                "",
                f"- **Target Success Rate**: 95%+ (currently {(summary.passed_files / max(summary.total_files, 1)) * 100:.1f}%)",
                f"- **Error Reduction**: Reduce from {error_count} to <10 errors",
                f"- **Warning Management**: Keep warnings under 100 (currently {warning_count})",
                "",
            ]
        )

        return content

    def _generate_appendices(self, summary: ValidationSummary) -> list[str]:
        """Generate appendices with technical details."""
        return [
            "## 📚 Appendices",
            "",
            "### Appendix A: Validator Descriptions",
            "",
            "| Validator | Purpose | Technology |",
            "|-----------|---------|------------|",
            "| `code_execution` | Executes code examples to verify runtime behavior | exec() with mocking |",
            "| `code_linting` | Validates code style and best practices | Ruff linter |",
            "| `code_typing` | Checks type safety and annotations | MyPy type checker |",
            "| `cross_references` | Validates internal links and references | Link resolution |",
            "| `financial_precision` | Ensures proper Decimal usage for money | Pattern matching |",
            "| `markdown_syntax` | Validates markdown structure | Markdown parsing |",
            "| `python_syntax` | Checks Python syntax validity | AST parsing |",
            "| `security` | Scans for exposed credentials | Pattern matching |",
            "",
            "### Appendix B: Configuration",
            "",
            "```yaml",
            "# Validation configuration used for this report",
            "validators:",
            "  code_linting:",
            "    enabled: true",
            "    options:",
            "      severity_filter: 'warning'",
            "  code_typing:",
            "    enabled: true",
            "    options:",
            "      strict_mode: false",
            "```",
            "",
            "### Appendix C: Report Generation",
            "",
            "- **Generated by**: FiveTwenty Documentation Validation System v2.0",
            "- **Report format**: Enhanced Markdown",
            f"- **Processing time**: {summary.duration_ms / 1000:.2f} seconds",
            f"- **Files analyzed**: {summary.total_files}",
            "",
        ]

    # Helper methods for analysis and formatting
    def _group_issues_by_file(self, issues: list[ValidationIssue]) -> dict[str, list[ValidationIssue]]:
        """Group issues by file path."""
        grouped = defaultdict(list)
        for issue in issues:
            grouped[str(issue.file_path)].append(issue)
        return dict(grouped)

    def _group_issues_by_validator(self, issues: list[ValidationIssue]) -> dict[str, list[ValidationIssue]]:
        """Group issues by validator name."""
        grouped = defaultdict(list)
        for issue in issues:
            # Extract validator name from rule_id (e.g., "code_lint_f401" -> "code_linting")
            validator_name = self._extract_validator_name(issue.rule_id or "unknown")
            grouped[validator_name].append(issue)
        return dict(grouped)

    def _group_issues_by_severity(self, issues: list[ValidationIssue]) -> dict[IssueSeverity, list[ValidationIssue]]:
        """Group issues by severity level."""
        grouped = defaultdict(list)
        for issue in issues:
            grouped[issue.severity].append(issue)
        return dict(grouped)

    def _calculate_rule_statistics(self, issues: list[ValidationIssue]) -> dict[str, int]:
        """Calculate statistics for each rule."""
        stats: defaultdict[str, int] = defaultdict(int)
        for issue in issues:
            rule_id = issue.rule_id or "unknown"
            stats[rule_id] += 1
        return dict(stats)

    def _get_urgency_level(self, issues_by_severity: dict[IssueSeverity, list[ValidationIssue]]) -> str:
        """Determine overall urgency level."""
        error_count = len(issues_by_severity.get(IssueSeverity.ERROR, []))
        warning_count = len(issues_by_severity.get(IssueSeverity.WARNING, []))

        if error_count > 100:
            return "🚨 CRITICAL - Immediate action required"
        if error_count > 20:
            return "🔥 HIGH - Address within 1 week"
        if error_count > 0:
            return "⚠️ MEDIUM - Address within 1 month"
        if warning_count > 100:
            return "📋 LOW - Address during next maintenance cycle"
        return "✅ MINIMAL - Maintenance as needed"

    def _generate_quality_assessment(self, success_rate: float) -> str:
        """Generate quality assessment based on success rate."""
        if success_rate >= 95:
            return "🏆 **Quality Assessment**: Excellent - Documentation meets high quality standards"
        if success_rate >= 80:
            return "✅ **Quality Assessment**: Good - Minor issues to address"
        if success_rate >= 60:
            return "⚠️ **Quality Assessment**: Fair - Significant improvements needed"
        return "🚨 **Quality Assessment**: Poor - Major quality issues require immediate attention"

    def _get_validator_insight(self, validator_name: str, issues: list[ValidationIssue]) -> str:
        """Get insight for a specific validator."""
        insights = {
            "code_linting": f"Found {len(issues)} style/best practice violations. Focus on import organization and code formatting.",
            "code_typing": f"Identified {len(issues)} type-related issues. Consider adding type annotations to improve code clarity.",
            "code_execution": f"Detected {len(issues)} runtime errors. Fix code examples that fail when executed.",
            "cross_references": f"Found {len(issues)} broken internal links. Verify all documentation cross-references are valid.",
            "financial_precision": f"Located {len(issues)} financial precision issues. Use Decimal type for all monetary calculations.",
            "markdown_syntax": f"Discovered {len(issues)} markdown formatting issues. Review documentation structure.",
            "python_syntax": f"Found {len(issues)} Python syntax errors. Fix code blocks that cannot be parsed.",
            "security": f"Identified {len(issues)} potential security issues. Remove any exposed credentials or sensitive data.",
        }
        return insights.get(validator_name, f"Found {len(issues)} issues requiring attention.")

    def _categorize_file(self, file_path: str) -> str:
        """Categorize file by its path."""
        path = file_path.lower()
        if "/api-reference/" in path:
            return "API Reference"
        if "/tutorials/" in path:
            return "Tutorials"
        if "/how-to-guides/" in path:
            return "How-to Guides"
        if "/explanation/" in path:
            return "Explanation"
        if "/contributing/" in path:
            return "Contributing"
        return "Other"

    def _get_rule_description(self, rule_id: str) -> str:
        """Get human-readable description for rule ID."""
        descriptions = {
            "code_undefined_variable": "Variable used without definition",
            "code_async_outside_function": "Async code outside function context",
            "code_missing_account_id": "Missing required account_id parameter",
            "code_lint_f401": "Unused import statement",
            "code_lint_e501": "Line too long (>79 characters)",
            "code_lint_w291": "Trailing whitespace",
            "code_typing_attr-defined": "Attribute not defined on type",
            "code_typing_name-defined": "Name not defined in scope",
            "markdown_list_spacing": "Missing blank line before list",
        }
        return descriptions.get(rule_id, "See documentation for details")

    def _get_rule_severity_indicator(self, rule_id: str) -> str:
        """Get severity indicator for rule."""
        if "error" in rule_id.lower() or "async_outside" in rule_id or "undefined" in rule_id:
            return "🔴 High"
        if "lint_f" in rule_id or "typing_" in rule_id:
            return "🟡 Medium"
        return "🔵 Low"

    def _categorize_rule(self, rule_id: str) -> str:
        """Categorize rule by type."""
        if rule_id.startswith("code_lint"):
            return "Code Linting"
        if rule_id.startswith("code_typing"):
            return "Type Checking"
        if rule_id.startswith("code_"):
            return "Code Quality"
        if rule_id.startswith("markdown"):
            return "Markdown"
        return "Other"

    def _get_rule_recommendation(self, rule_id: str) -> str:
        """Get specific recommendation for a rule."""
        recommendations = {
            "code_undefined_variable": "Add proper import statements to all code examples",
            "code_async_outside_function": "Wrap all async code in proper function definitions",
            "code_lint_f401": "Remove unused imports or demonstrate their usage",
            "code_lint_e501": "Break long lines or simplify complex examples",
            "code_typing_attr-defined": "Verify object attributes exist or add proper type annotations",
        }
        return recommendations.get(rule_id, "Review and fix according to best practices")

    def _extract_validator_name(self, rule_id: str) -> str:
        """Extract validator name from rule ID."""
        if rule_id.startswith("code_lint"):
            return "code_linting"
        if rule_id.startswith("code_typing"):
            return "code_typing"
        if rule_id.startswith("code_"):
            return "code_execution"
        return rule_id.split("_")[0] if "_" in rule_id else "unknown"

    def _format_issue_details(self, issue: ValidationIssue, include_code_snippets: bool) -> list[str]:
        """Format detailed issue information."""
        content = [f"**Line {issue.line}**: {issue.message}", ""]

        if issue.context and include_code_snippets:
            content.extend(["```python", issue.context, "```", ""])

        if issue.suggestion:
            content.extend([f"💡 **Suggestion**: {issue.suggestion}", ""])

        content.extend([f"*Rule: `{issue.rule_id}`*", ""])

        return content
