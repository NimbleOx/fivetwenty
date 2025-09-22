"""Prose quality validation using Vale."""

import json
import subprocess
import tempfile
from pathlib import Path
from typing import Any

from docs_validation.validation.checks.base import ContentCheck
from docs_validation.validation.core.context import ValidationContext
from docs_validation.validation.core.results import IssueSeverity, ValidationResult


class ProseCheck(ContentCheck):
    """Validates prose quality using Vale style checker."""

    def __init__(self):
        super().__init__(
            name="prose",
            description="Validates prose quality and style using Vale",
            file_patterns=["**/*.md"],
        )
        self.vale_executable = self._find_vale_executable()

    def _find_vale_executable(self) -> str | None:
        """Find Vale executable in PATH."""
        try:
            result = subprocess.run(
                ["which", "vale"],
                capture_output=True,
                text=True,
                check=False,
                timeout=5,
            )
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
            result = subprocess.run(
                [self.vale_executable, "--version"],
                capture_output=True,
                text=True,
                check=False,
                timeout=10,
            )
            return result.returncode == 0
        except Exception:
            return False

    def check_content(
        self,
        file_path: Path,
        content: str,
        context: ValidationContext,
        result: ValidationResult,
    ) -> None:
        """Check prose quality using Vale."""
        if not self._is_vale_available():
            result.add_issue(
                message="Vale is not available or not properly configured",
                file_path=str(file_path),
                severity=IssueSeverity.WARNING,
            )
            return

        try:
            # Write content to temporary file for Vale
            with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as temp_file:
                temp_file.write(content)
                temp_path = Path(temp_file.name)

            try:
                # Run Vale on the temporary file
                vale_results = self._run_vale_on_file(temp_path, context)

                # Process Vale results
                for issue in vale_results.get("issues", []):
                    severity = self._map_vale_severity(issue.get("Severity", ""))

                    result.add_issue(
                        message=f"{issue.get('Check', '')}: {issue.get('Message', '')}",
                        file_path=str(file_path),
                        line=issue.get("Line"),
                        severity=severity,
                        context=issue.get("Match", ""),
                        suggestion=issue.get("Action", {}).get("Name") if issue.get("Action") else None,
                    )

            finally:
                # Clean up temporary file
                temp_path.unlink(missing_ok=True)

        except Exception as e:
            result.add_issue(
                message=f"Error running Vale: {e}",
                file_path=str(file_path),
                severity=IssueSeverity.ERROR,
            )

    def _run_vale_on_file(self, file_path: Path, context: ValidationContext) -> dict[str, Any]:
        """Run Vale on a single file and return parsed results."""
        try:
            # Look for Vale config in docs_validation directory
            config_path = context.config.project_root / "docs_validation" / ".vale.ini"

            cmd = [self.vale_executable, "--output=JSON"]

            if config_path.exists():
                cmd.extend(["--config", str(config_path)])

            cmd.append(str(file_path))

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=False,
                timeout=30,
                cwd=str(context.config.project_root),
            )

            if result.returncode in [0, 1]:  # 0 = no issues, 1 = issues found
                try:
                    output = json.loads(result.stdout) if result.stdout.strip() else {}

                    # Vale JSON output format: {file_path: [issues]}
                    file_key = str(file_path)
                    issues = list(output.values())[0] if output else []

                    return {"issues": issues}
                except json.JSONDecodeError:
                    return {"issues": [], "error": "Failed to parse Vale JSON output"}
            else:
                return {"issues": [], "error": f"Vale failed with exit code {result.returncode}: {result.stderr}"}

        except subprocess.TimeoutExpired:
            return {"issues": [], "error": "Vale execution timed out"}
        except Exception as e:
            return {"issues": [], "error": f"Vale execution failed: {e}"}

    def _map_vale_severity(self, vale_severity: str) -> IssueSeverity:
        """Map Vale severity levels to our severity enum."""
        severity_map = {
            "error": IssueSeverity.ERROR,
            "warning": IssueSeverity.WARNING,
            "suggestion": IssueSeverity.INFO,
            "info": IssueSeverity.INFO,
        }
        return severity_map.get(vale_severity.lower(), IssueSeverity.WARNING)

    def supports_file(self, file_path: Path) -> bool:
        """Check if this validator supports the given file."""
        return file_path.suffix.lower() == ".md"

    def get_check_metadata(self) -> dict[str, Any]:
        """Get metadata about this check for optimization."""
        return {
            "check_type": "external",  # Uses external Vale tool
            "estimated_files_per_second": 25.0,  # Vale is reasonably fast
            "memory_usage_mb": 30.0,
            "supports_batching": False,  # Vale works on individual files
            "requires_context_isolation": False,
        }
