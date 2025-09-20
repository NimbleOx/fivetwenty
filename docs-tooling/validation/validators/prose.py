"""
Prose quality validation using Vale.

Validates writing quality, style, and consistency using Vale with multiple style packages.
"""

import json
import subprocess
import sys
from pathlib import Path
from typing import Any

# Import path setup
validation_dir = Path(__file__).parent.parent
sys.path.insert(0, str(validation_dir))

from core.base import FileValidator, ValidationResult  # noqa: E402


class ProseValidator(FileValidator):
    """Validates prose quality using Vale."""

    def __init__(self) -> None:
        super().__init__("prose", "Validates prose quality and style using Vale", ["../../docs/**/*.md"])
        self.vale_executable = self._find_vale_executable()

    def _find_vale_executable(self) -> str | None:
        """Find Vale executable in PATH."""
        try:
            result = subprocess.run(["which", "vale"], capture_output=True, text=True, check=False)
            if result.returncode == 0:
                return result.stdout.strip()
        except Exception:
            pass
        return None

    def _is_vale_available(self) -> bool:
        """Check if Vale is available and properly configured."""
        if not self.vale_executable:
            return False

        try:
            # Test Vale with a simple command
            result = subprocess.run([self.vale_executable, "--version"], capture_output=True, text=True, check=False, timeout=10)
            return result.returncode == 0
        except Exception:
            return False

    def _run_vale_on_file(self, file_path: Path) -> dict[str, Any]:
        """Run Vale on a single file and return parsed results."""
        if not self._is_vale_available():
            return {"errors": [], "warnings": [], "suggestions": []}

        try:
            # Run Vale with JSON output from project root
            project_root = Path.cwd()
            # If we're in the validation directory, go up two levels to project root
            if "docs-tooling/validation" in str(project_root):
                project_root = project_root.parent.parent

            # Convert file path to be relative to project root
            if file_path.is_absolute():
                vale_file_path = str(file_path)
            else:
                # File path is relative to validation dir, resolve it properly
                resolved_path = (Path.cwd() / file_path).resolve()
                vale_file_path = str(resolved_path)

            if self.vale_executable:
                result = subprocess.run(
                    [self.vale_executable, "--output=JSON", vale_file_path],
                    capture_output=True,
                    text=True,
                    check=False,
                    timeout=30,
                    cwd=project_root,  # Run from project root where .vale.ini is
                )
            else:
                return {"errors": [], "warnings": [], "suggestions": []}

            # Vale returns 0 for no issues, 1 for suggestions, 2 for warnings/errors
            # We should parse output regardless of return code

            # Parse JSON output
            try:
                vale_output = json.loads(result.stdout) if result.stdout.strip() else {}
                # Vale uses the full resolved path as the key
                file_results = vale_output.get(vale_file_path, [])

                # Categorize issues by severity
                errors = [issue for issue in file_results if issue.get("Severity") == "error"]
                warnings = [issue for issue in file_results if issue.get("Severity") == "warning"]
                suggestions = [issue for issue in file_results if issue.get("Severity") == "suggestion"]

                return {"errors": errors, "warnings": warnings, "suggestions": suggestions}
            except json.JSONDecodeError:
                # Fall back to text parsing if JSON fails
                return self._parse_text_output(result.stderr or result.stdout, file_path)

        except subprocess.TimeoutExpired:
            self.add_issue("Vale timed out after 30 seconds", str(file_path))
            return {"errors": [], "warnings": [], "suggestions": []}
        except Exception as e:
            self.add_issue(f"Vale execution failed: {e}", str(file_path))
            return {"errors": [], "warnings": [], "suggestions": []}

    def _parse_text_output(self, output: str, file_path: Path) -> dict[str, Any]:
        """Parse Vale text output as fallback."""
        errors: list[dict[str, Any]] = []
        warnings: list[dict[str, Any]] = []
        suggestions: list[dict[str, Any]] = []

        if not output:
            return {"errors": errors, "warnings": warnings, "suggestions": suggestions}

        lines = output.split("\n")
        for original_line in lines:
            line = original_line.strip()
            if not line or line.startswith("✖"):
                continue

            # Parse format: "line:col  severity  message  rule"
            parts = line.split(None, 3)
            if len(parts) >= 3:
                location = parts[0] if parts[0] else "1:1"
                severity = parts[1].lower().strip("[]")
                message = parts[2] if len(parts) > 2 else "Style issue"
                rule = parts[3] if len(parts) > 3 else "Vale"

                issue = {"Check": rule, "Description": message, "Line": int(location.split(":")[0]) if ":" in location else 1, "Severity": severity}

                if severity == "error":
                    errors.append(issue)
                elif severity == "warning":
                    warnings.append(issue)
                else:
                    suggestions.append(issue)

        return {"errors": errors, "warnings": warnings, "suggestions": suggestions}

    def _format_vale_issue(self, issue: dict[str, Any], file_path: Path) -> str:
        """Format a Vale issue for reporting."""
        check = issue.get("Check", "Vale")
        description = issue.get("Description", "Style issue")
        severity = issue.get("Severity", "suggestion").upper()

        return f"[{severity}] {description} ({check})"

    def validate_file(self, file_path: Path) -> None:
        """Validate prose quality in a single markdown file."""
        if file_path.suffix.lower() != ".md":
            return

        if not self._is_vale_available():
            self.add_issue("Vale not available - install with 'brew install vale' or see https://vale.sh/docs/vale-cli/installation/", str(file_path))
            return

        results = self._run_vale_on_file(file_path)

        # Process errors
        for error in results["errors"]:
            issue_msg = self._format_vale_issue(error, file_path)
            line_num = error.get("Line", 1)
            self.add_issue(issue_msg, str(file_path), line_num)

        # Process warnings (add as issues but with lower severity)
        for warning in results["warnings"]:
            issue_msg = self._format_vale_issue(warning, file_path)
            line_num = warning.get("Line", 1)
            self.add_issue(issue_msg, str(file_path), line_num)

        # Track suggestions separately for reporting
        suggestion_count = len(results["suggestions"])
        if suggestion_count > 0:
            self.add_issue(f"{suggestion_count} style suggestions available (run 'vale {file_path}' for details)", str(file_path))

    def validate(self) -> ValidationResult:
        """Run prose validation on all markdown files."""
        if not self._is_vale_available():
            return ValidationResult(
                validator_name=self.name,
                status="failed",
                issues_found=1,
                total_checked=0,
                details={
                    "error": "Vale not available",
                    "installation": "Install with 'brew install vale' or see https://vale.sh/docs/vale-cli/installation/",
                    "config_file": ".vale.ini",
                    "prose_issues": [{"file": "system", "line": 1, "message": "Vale not available - install with 'brew install vale'", "severity": "error"}],
                },
                timestamp=self.start_time.isoformat() if self.start_time else "",
                duration_seconds=self.get_elapsed_time(),
            )

        # Get files to validate using the base class method
        files = self.get_files_to_validate()
        total_files = len(files)

        if total_files == 0:
            return ValidationResult(validator_name=self.name, status="passed", issues_found=0, total_checked=0, details={"message": "No markdown files found", "prose_issues": []}, timestamp=self.start_time.isoformat() if self.start_time else "", duration_seconds=self.get_elapsed_time())

        # Process each file
        prose_issues = []
        total_issues = 0

        for file_path in files:
            results = self._run_vale_on_file(file_path)

            # Process errors and warnings as issues
            for error in results["errors"]:
                line = error.get("Line", 1)
                message = error.get("Message", error.get("Description", "Prose error"))
                check = error.get("Check", "Vale")
                prose_issues.append({"file": str(file_path), "line": line, "message": f"[ERROR] {message} ({check})", "severity": "error", "check": check})
                total_issues += 1

            for warning in results["warnings"]:
                line = warning.get("Line", 1)
                message = warning.get("Message", warning.get("Description", "Prose warning"))
                check = warning.get("Check", "Vale")
                prose_issues.append({"file": str(file_path), "line": line, "message": f"[WARNING] {message} ({check})", "severity": "warning", "check": check})
                total_issues += 1

            # Track suggestions separately
            suggestion_count = len(results["suggestions"])
            if suggestion_count > 0:
                prose_issues.append({"file": str(file_path), "line": 1, "message": f"[INFO] {suggestion_count} style suggestions available", "severity": "suggestion", "check": "Vale"})

        # Determine status - only errors and warnings count as failures
        error_count = len([issue for issue in prose_issues if issue["severity"] in ["error", "warning"]])
        status = "failed" if error_count > 0 else "passed"

        return ValidationResult(
            validator_name=self.name,
            status=status,
            issues_found=error_count,
            total_checked=total_files,
            details={
                "files_checked": total_files,
                "prose_issues": prose_issues[:20],  # Limit for readability
                "total_issues": len(prose_issues),
                "error_count": error_count,
                "vale_config": ".vale.ini",
                "styles_path": "styles/",
            },
            timestamp=self.start_time.isoformat() if self.start_time else "",
            duration_seconds=self.get_elapsed_time(),
        )
