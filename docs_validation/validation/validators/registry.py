"""Validator registry and management."""

import time
from concurrent.futures import ThreadPoolExecutor, as_completed

from validation.checks.base import BaseCheck
from validation.core.context import ValidationContext
from validation.core.results import ValidationResult, ValidationStatus, ValidationSummary


class ValidatorRegistry:
    """Registry for managing validation checks."""

    def __init__(self) -> None:
        self._checks: dict[str, BaseCheck] = {}
        self._check_classes: dict[str, type[BaseCheck]] = {}

    def register(self, check_name: str, check_class: type[BaseCheck]) -> None:
        """Register a validation check class."""
        self._check_classes[check_name] = check_class

    def register_instance(self, check: BaseCheck) -> None:
        """Register a validation check instance."""
        self._checks[check.name] = check

    def create_check(self, check_name: str) -> BaseCheck | None:
        """Create a check instance from registered class."""
        if check_name in self._check_classes:
            return self._check_classes[check_name]()
        return None

    def get_check(self, check_name: str) -> BaseCheck | None:
        """Get a check instance."""
        if check_name in self._checks:
            return self._checks[check_name]

        # Try to create from class
        check = self.create_check(check_name)
        if check:
            self._checks[check_name] = check

        return check

    def list_available_checks(self) -> dict[str, str]:
        """List all available checks with descriptions."""
        checks = {}

        # From registered instances
        for name, check in self._checks.items():
            checks[name] = check.description

        # From registered classes
        for name, check_class in self._check_classes.items():
            if name not in checks:
                # Create temporary instance to get description
                temp_check = check_class()
                checks[name] = temp_check.description

        return checks

    def run_check(self, check_name: str, context: ValidationContext) -> ValidationResult:
        """Run a single validation check."""
        check = self.get_check(check_name)
        if not check:
            result = ValidationResult(
                check_name=check_name,
                status=ValidationStatus.ERROR,
            )
            result.add_issue(
                message=f"Check '{check_name}' not found",
                file_path="<registry>",
            )
            return result

        return check.run(context)

    def run_checks(
        self,
        check_names: list[str],
        context: ValidationContext,
        parallel: bool = True,
    ) -> ValidationSummary:
        """Run multiple validation checks."""
        start_time = time.time()
        results: list[ValidationResult] = []

        if parallel and len(check_names) > 1:
            results = self._run_checks_parallel(check_names, context)
        else:
            results = self._run_checks_sequential(check_names, context)

        total_duration = time.time() - start_time

        return ValidationSummary(
            results=results,
            total_duration=total_duration,
        )

    def _run_checks_sequential(
        self,
        check_names: list[str],
        context: ValidationContext,
    ) -> list[ValidationResult]:
        """Run checks sequentially."""
        results = []

        for check_name in check_names:
            print(f"  ▶️  Running {check_name}...")
            result = self.run_check(check_name, context)
            results.append(result)

            # Print immediate result
            status_icon = "✅" if result.is_successful else "❌"
            print(f"  {status_icon} {check_name}: {result.issues_found} issues found")

        return results

    def _run_checks_parallel(
        self,
        check_names: list[str],
        context: ValidationContext,
    ) -> list[ValidationResult]:
        """Run checks in parallel."""
        results = []
        max_workers = min(len(check_names), context.config.tools.parallel_workers)

        print(f"🔄 Running {len(check_names)} checks in parallel (max {max_workers} workers)...")

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all checks
            future_to_name = {executor.submit(self.run_check, check_name, context): check_name for check_name in check_names}

            # Collect results as they complete
            for future in as_completed(future_to_name):
                check_name = future_to_name[future]
                try:
                    result = future.result()
                    results.append(result)

                    # Print immediate result
                    status_icon = "✅" if result.is_successful else "❌"
                    print(f"  {status_icon} {check_name}: {result.issues_found} issues found")

                except Exception as e:
                    # Create error result
                    error_result = ValidationResult(
                        check_name=check_name,
                        status=ValidationStatus.ERROR,
                    )
                    error_result.add_issue(
                        message=f"Check execution failed: {e}",
                        file_path="<execution>",
                    )
                    results.append(error_result)

                    print(f"  ❌ {check_name}: execution failed ({e})")

        # Sort results by original order
        name_to_result = {r.check_name: r for r in results}
        return [name_to_result[name] for name in check_names if name in name_to_result]

    def run_all_checks(self, context: ValidationContext, parallel: bool = True) -> ValidationSummary:
        """Run all registered checks."""
        all_check_names = list(self.list_available_checks().keys())
        return self.run_checks(all_check_names, context, parallel)


# Default registry instance
default_registry = ValidatorRegistry()


# Register built-in checks
def register_builtin_checks() -> None:
    """Register all built-in validation checks."""
    from validation.checks.code.executability import CodeExecutabilityCheck
    from validation.checks.code.python import PythonStyleCheck, PythonSyntaxCheck
    from validation.checks.content.cross_references import CrossReferenceCheck
    from validation.checks.content.educational_progression import EducationalProgressionCheck
    from validation.checks.content.financial import FinancialPrecisionCheck, FinancialTerminologyCheck
    from validation.checks.content.sdk_methods import SDKMethodsCheck
    from validation.checks.content.terminology import TerminologyCheck
    from validation.checks.content.tutorial_structure import TutorialStructureCheck
    from validation.checks.links.validator import LinkValidationCheck
    from validation.checks.prose.validator import ProseCheck
    from validation.checks.security.scanner import SecurityCheck
    from validation.checks.syntax.markdown import MarkdownSyntaxCheck

    # Syntax checks
    default_registry.register("markdown_syntax", MarkdownSyntaxCheck)

    # Content checks
    default_registry.register("financial_precision", FinancialPrecisionCheck)
    default_registry.register("financial_terminology", FinancialTerminologyCheck)
    default_registry.register("terminology", TerminologyCheck)
    default_registry.register("cross_references", CrossReferenceCheck)
    default_registry.register("sdk_methods", SDKMethodsCheck)
    default_registry.register("educational_progression", EducationalProgressionCheck)
    default_registry.register("tutorial_structure", TutorialStructureCheck)

    # Link checks
    default_registry.register("link_validation", LinkValidationCheck)

    # Code checks
    default_registry.register("python_syntax", PythonSyntaxCheck)
    default_registry.register("python_style", PythonStyleCheck)
    default_registry.register("code_executability", CodeExecutabilityCheck)

    # Prose checks
    default_registry.register("prose", ProseCheck)

    # Security checks
    default_registry.register("security", SecurityCheck)


# Auto-register built-in checks
register_builtin_checks()
