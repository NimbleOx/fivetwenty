"""Profile management and execution."""

from typing import Any

from docs_validation.validation.config.loader import ConfigLoader, ValidationProfile
from docs_validation.validation.config.quality_gates import QualityGateManager
from docs_validation.validation.core.context import ValidationContext
from docs_validation.validation.core.results import ValidationSummary
from docs_validation.validation.validators.registry import default_registry


class ProfileManager:
    """Manages validation profiles and their execution."""

    def __init__(self, config_loader: ConfigLoader | None = None):
        self.config_loader = config_loader or ConfigLoader()
        self.current_profile: ValidationProfile | None = None

    def load_profile(self, profile_name: str) -> ValidationProfile:
        """Load and set the current profile."""
        self.current_profile = self.config_loader.load_profile(profile_name)
        return self.current_profile

    def get_enabled_checks(self, profile: ValidationProfile | None = None) -> list[str]:
        """Get list of enabled checks for a profile."""
        if profile is None:
            profile = self.current_profile

        if not profile:
            raise ValueError("No profile loaded")

        return [
            check_name for check_name, check_config in profile.checks.items()
            if check_config.enabled
        ]

    def apply_check_config(self, check_name: str, profile: ValidationProfile | None = None) -> dict[str, Any]:
        """Apply profile configuration to a specific check."""
        if profile is None:
            profile = self.current_profile

        if not profile or check_name not in profile.checks:
            return {}

        check_config = profile.checks[check_name]

        config = {
            "enabled": check_config.enabled,
            "severity_override": check_config.severity_override,
            "custom_patterns": check_config.custom_patterns,
            "exclude_patterns": check_config.exclude_patterns,
            "options": check_config.options,
        }

        return {k: v for k, v in config.items() if v is not None}

    def create_quality_gate_manager(self, profile: ValidationProfile | None = None) -> QualityGateManager:
        """Create quality gate manager from profile configuration."""
        if profile is None:
            profile = self.current_profile

        if not profile:
            raise ValueError("No profile loaded")

        manager = QualityGateManager()

        gates_config = profile.quality_gates
        config_dict = {
            "max_errors": gates_config.max_errors,
            "max_warnings": gates_config.max_warnings,
            "min_success_rate": gates_config.min_success_rate,
            "max_issues_per_file": gates_config.max_issues_per_file,
            "required_checks": gates_config.required_checks,
            "fail_on_security_issues": gates_config.fail_on_security_issues,
        }

        return manager.create_from_config(config_dict)

    def execute_profile(
        self,
        profile_name: str,
        context: ValidationContext,
        specific_checks: list[str] | None = None,
    ) -> ValidationSummary:
        """Execute validation using a specific profile."""
        # Load the profile
        profile = self.load_profile(profile_name)

        # Get checks to run
        if specific_checks:
            # Filter specific checks through profile configuration
            checks_to_run = [
                check for check in specific_checks
                if check in profile.checks and profile.checks[check].enabled
            ]
        else:
            checks_to_run = self.get_enabled_checks(profile)

        if not checks_to_run:
            raise ValueError(f"No enabled checks found in profile '{profile_name}'")

        # Update context with profile settings
        context.config.tools.parallel_workers = profile.max_workers
        context.config.tools.timeout_seconds = profile.timeout_seconds

        # Apply file patterns from profile
        if profile.file_patterns:
            # Update context file patterns
            original_patterns = context.config.file_patterns.documentation
            context.config.file_patterns.documentation = profile.file_patterns

        try:
            # Execute validation
            summary = default_registry.run_checks(
                checks_to_run,
                context,
                parallel=profile.parallel_execution,
            )

            return summary

        finally:
            # Restore original patterns
            if profile.file_patterns:
                context.config.file_patterns.documentation = original_patterns

    def validate_with_quality_gates(
        self,
        profile_name: str,
        context: ValidationContext,
        specific_checks: list[str] | None = None,
    ) -> dict[str, Any]:
        """Execute validation with quality gate evaluation."""
        # Execute validation
        summary = self.execute_profile(profile_name, context, specific_checks)

        # Load profile for quality gates
        profile = self.current_profile or self.load_profile(profile_name)

        # Create and run quality gates
        gate_manager = self.create_quality_gate_manager(profile)
        gate_report = gate_manager.evaluate_summary(summary)

        return {
            "validation_summary": summary,
            "quality_gate_report": gate_report,
            "profile": profile,
            "overall_passed": gate_report.overall_status.value == "passed",
        }

    def list_available_profiles(self) -> dict[str, str]:
        """List all available profiles with descriptions."""
        profile_names = self.config_loader.list_profiles()
        profiles_info = {}

        for name in profile_names:
            try:
                info = self.config_loader.get_profile_info(name)
                profiles_info[name] = info["description"]
            except Exception as e:
                profiles_info[name] = f"Error loading profile: {e}"

        return profiles_info

    def create_profile_comparison(self, profile_names: list[str]) -> dict[str, Any]:
        """Create a comparison of multiple profiles."""
        comparison = {
            "profiles": {},
            "comparison_matrix": {},
        }

        all_checks = set()
        profile_data = {}

        for name in profile_names:
            try:
                info = self.config_loader.get_profile_info(name)
                profile_data[name] = info
                all_checks.update(info["enabled_checks"])
            except Exception as e:
                profile_data[name] = {"error": str(e)}

        # Create comparison matrix
        for check in sorted(all_checks):
            comparison["comparison_matrix"][check] = {}
            for profile_name in profile_names:
                if "enabled_checks" in profile_data[profile_name]:
                    enabled = check in profile_data[profile_name]["enabled_checks"]
                    comparison["comparison_matrix"][check][profile_name] = enabled
                else:
                    comparison["comparison_matrix"][check][profile_name] = "error"

        comparison["profiles"] = profile_data
        return comparison

    def generate_profile_report(self, profile_name: str) -> str:
        """Generate a detailed report for a profile."""
        try:
            info = self.config_loader.get_profile_info(profile_name)
            profile = self.config_loader.load_profile(profile_name)

            lines = []
            lines.append(f"📋 Profile Report: {profile_name}")
            lines.append("=" * 50)
            lines.append(f"Description: {info['description']}")
            lines.append(f"Extends: {info.get('extends', 'None')}")
            lines.append(f"Parallel Execution: {info['parallel_execution']}")
            lines.append("")

            lines.append("📝 Enabled Checks:")
            lines.append("-" * 20)
            for check in info["enabled_checks"]:
                check_config = profile.checks.get(check)
                if check_config:
                    options_info = ""
                    if check_config.options:
                        options_info = f" (options: {check_config.options})"
                    lines.append(f"  ✅ {check}{options_info}")

            lines.append("")
            lines.append("🚦 Quality Gates:")
            lines.append("-" * 20)
            gates = info["quality_gates"]
            lines.append(f"  Max Errors: {gates['max_errors']}")
            lines.append(f"  Max Warnings: {gates['max_warnings']}")
            lines.append(f"  Min Success Rate: {gates['min_success_rate']}%")

            lines.append("")
            lines.append("📊 Reporting:")
            lines.append("-" * 15)
            lines.append(f"  Formats: {', '.join(info['reporting_formats'])}")

            return "\n".join(lines)

        except Exception as e:
            return f"Error generating report for profile '{profile_name}': {e}"

    def create_custom_profile(
        self,
        name: str,
        description: str,
        enabled_checks: list[str],
        quality_gates: dict[str, Any] | None = None,
        base_profile: str | None = None,
    ) -> ValidationProfile:
        """Create a custom validation profile programmatically."""
        from docs_validation.validation.config.loader import CheckConfig, QualityGateConfig

        profile = ValidationProfile(name=name, description=description)

        if base_profile:
            profile.extends = base_profile

        # Configure checks
        for check_name in enabled_checks:
            profile.checks[check_name] = CheckConfig(enabled=True)

        # Configure quality gates
        if quality_gates:
            profile.quality_gates = QualityGateConfig(**quality_gates)

        return profile


# Global profile manager instance
default_profile_manager = ProfileManager()
