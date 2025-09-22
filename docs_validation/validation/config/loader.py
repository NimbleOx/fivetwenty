"""Configuration loader supporting YAML and JSON formats."""

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml


@dataclass
class CheckConfig:
    """Configuration for individual validation checks."""
    enabled: bool = True
    severity_override: str | None = None
    custom_patterns: list[str] = field(default_factory=list)
    exclude_patterns: list[str] = field(default_factory=list)
    options: dict[str, Any] = field(default_factory=dict)


@dataclass
class QualityGateConfig:
    """Configuration for quality gates."""
    max_errors: int = 0
    max_warnings: int = 50
    max_issues_per_file: int = 10
    min_success_rate: float = 95.0
    required_checks: list[str] = field(default_factory=list)
    fail_on_error: bool = True
    fail_on_security_issues: bool = True


@dataclass
class ReportingConfig:
    """Configuration for reporting and output."""
    formats: list[str] = field(default_factory=lambda: ["console", "json"])
    output_dir: str = "validation_reports"
    include_passed: bool = False
    include_file_details: bool = True
    group_by_severity: bool = True
    export_trends: bool = False


@dataclass
class ValidationProfile:
    """Complete validation profile configuration."""
    name: str
    description: str = ""
    checks: dict[str, CheckConfig] = field(default_factory=dict)
    quality_gates: QualityGateConfig = field(default_factory=QualityGateConfig)
    reporting: ReportingConfig = field(default_factory=ReportingConfig)
    file_patterns: list[str] = field(default_factory=lambda: ["**/*.md"])
    exclude_paths: list[str] = field(default_factory=list)
    parallel_execution: bool = True
    max_workers: int = 4
    timeout_seconds: float = 300.0
    extends: str | None = None  # Profile inheritance


class ConfigLoader:
    """Loads and manages validation configurations."""

    def __init__(self, project_root: Path | None = None):
        self.project_root = project_root or Path.cwd()
        self._profiles: dict[str, ValidationProfile] = {}
        self._load_builtin_profiles()

    def load_config_file(self, config_path: Path) -> dict[str, Any]:
        """Load configuration from YAML or JSON file."""
        if not config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")

        content = config_path.read_text(encoding="utf-8")

        if config_path.suffix.lower() in [".yml", ".yaml"]:
            return yaml.safe_load(content)
        if config_path.suffix.lower() == ".json":
            return json.loads(content)
        raise ValueError(f"Unsupported configuration format: {config_path.suffix}")

    def find_config_file(self) -> Path | None:
        """Find validation configuration file in project."""
        config_names = [
            ".validation.yml",
            ".validation.yaml",
            ".validation.json",
            "validation.yml",
            "validation.yaml",
            "validation.json",
        ]

        # Check docs_validation directory first
        docs_validation_dir = self.project_root / "docs_validation"
        if docs_validation_dir.exists():
            for name in config_names:
                config_path = docs_validation_dir / name
                if config_path.exists():
                    return config_path

        # Fallback to project root
        for name in config_names:
            config_path = self.project_root / name
            if config_path.exists():
                return config_path

        return None

    def load_profile(self, profile_name: str) -> ValidationProfile:
        """Load a validation profile by name."""
        if profile_name in self._profiles:
            return self._profiles[profile_name]

        # Try to load from config file
        config_file = self.find_config_file()
        if config_file:
            config_data = self.load_config_file(config_file)
            profiles = config_data.get("profiles", {})

            if profile_name in profiles:
                profile_config = profiles[profile_name]
                profile = self._parse_profile(profile_name, profile_config)
                self._profiles[profile_name] = profile
                return profile

        raise ValueError(f"Profile '{profile_name}' not found")

    def load_default_profile(self) -> ValidationProfile:
        """Load the default validation profile."""
        config_file = self.find_config_file()

        if config_file:
            config_data = self.load_config_file(config_file)

            # Check if there's a default profile specified
            default_profile_name = config_data.get("default_profile", "default")

            if "profiles" in config_data and default_profile_name in config_data["profiles"]:
                return self.load_profile(default_profile_name)

            # Create profile from root-level config
            if any(key in config_data for key in ["checks", "quality_gates", "reporting"]):
                return self._parse_profile("default", config_data)

        # Return built-in default profile
        return self._profiles["default"]

    def _parse_profile(self, name: str, config: dict[str, Any]) -> ValidationProfile:
        """Parse profile configuration from dictionary."""
        profile = ValidationProfile(name=name)

        # Basic profile info
        profile.description = config.get("description", "")
        profile.file_patterns = config.get("file_patterns", ["**/*.md"])
        profile.exclude_paths = config.get("exclude_paths", [])
        profile.parallel_execution = config.get("parallel_execution", True)
        profile.max_workers = config.get("max_workers", 4)
        profile.timeout_seconds = config.get("timeout_seconds", 300.0)
        profile.extends = config.get("extends")

        # Parse checks configuration
        if "checks" in config:
            for check_name, check_config in config["checks"].items():
                if isinstance(check_config, bool):
                    # Simple enabled/disabled
                    profile.checks[check_name] = CheckConfig(enabled=check_config)
                elif isinstance(check_config, dict):
                    # Detailed configuration
                    profile.checks[check_name] = CheckConfig(
                        enabled=check_config.get("enabled", True),
                        severity_override=check_config.get("severity_override"),
                        custom_patterns=check_config.get("custom_patterns", []),
                        exclude_patterns=check_config.get("exclude_patterns", []),
                        options=check_config.get("options", {}),
                    )

        # Parse quality gates
        if "quality_gates" in config:
            gates_config = config["quality_gates"]
            profile.quality_gates = QualityGateConfig(
                max_errors=gates_config.get("max_errors", 0),
                max_warnings=gates_config.get("max_warnings", 50),
                max_issues_per_file=gates_config.get("max_issues_per_file", 10),
                min_success_rate=gates_config.get("min_success_rate", 95.0),
                required_checks=gates_config.get("required_checks", []),
                fail_on_error=gates_config.get("fail_on_error", True),
                fail_on_security_issues=gates_config.get("fail_on_security_issues", True),
            )

        # Parse reporting configuration
        if "reporting" in config:
            reporting_config = config["reporting"]
            profile.reporting = ReportingConfig(
                formats=reporting_config.get("formats", ["console", "json"]),
                output_dir=reporting_config.get("output_dir", "validation_reports"),
                include_passed=reporting_config.get("include_passed", False),
                include_file_details=reporting_config.get("include_file_details", True),
                group_by_severity=reporting_config.get("group_by_severity", True),
                export_trends=reporting_config.get("export_trends", False),
            )

        # Handle profile inheritance
        if profile.extends:
            base_profile = self.load_profile(profile.extends)
            profile = self._merge_profiles(base_profile, profile)

        return profile

    def _merge_profiles(self, base: ValidationProfile, override: ValidationProfile) -> ValidationProfile:
        """Merge two profiles with override taking precedence."""
        merged = ValidationProfile(name=override.name)

        # Copy base profile settings
        merged.description = override.description or base.description
        merged.file_patterns = override.file_patterns if override.file_patterns != ["**/*.md"] else base.file_patterns
        merged.exclude_paths = base.exclude_paths + override.exclude_paths
        merged.parallel_execution = override.parallel_execution
        merged.max_workers = override.max_workers
        merged.timeout_seconds = override.timeout_seconds

        # Merge checks (override wins)
        merged.checks = {**base.checks, **override.checks}

        # Override quality gates and reporting
        merged.quality_gates = override.quality_gates
        merged.reporting = override.reporting

        return merged

    def _load_builtin_profiles(self) -> None:
        """Load built-in validation profiles."""
        # Default profile - comprehensive validation
        default_profile = ValidationProfile(
            name="default",
            description="Comprehensive validation for documentation projects",
            file_patterns=["**/*.md", "**/*.py"],
            parallel_execution=True,
            max_workers=4,
        )

        # Enable all major checks
        default_profile.checks = {
            "markdown_syntax": CheckConfig(enabled=True),
            "financial_precision": CheckConfig(enabled=True),
            "terminology": CheckConfig(enabled=True),
            "security": CheckConfig(enabled=True),
            "cross_references": CheckConfig(enabled=True),
            "python_syntax": CheckConfig(enabled=True),
        }

        # Strict profile - high quality standards
        strict_profile = ValidationProfile(
            name="strict",
            description="Strict validation with high quality standards",
            extends="default",
        )
        strict_profile.quality_gates = QualityGateConfig(
            max_errors=0,
            max_warnings=10,
            max_issues_per_file=5,
            min_success_rate=98.0,
            fail_on_error=True,
            fail_on_security_issues=True,
        )

        # Fast profile - essential checks only
        fast_profile = ValidationProfile(
            name="fast",
            description="Fast validation with essential checks only",
            parallel_execution=True,
            max_workers=8,
        )
        fast_profile.checks = {
            "markdown_syntax": CheckConfig(enabled=True),
            "financial_precision": CheckConfig(enabled=True),
            "security": CheckConfig(enabled=True, options={"severity_filter": "high"}),
        }
        fast_profile.quality_gates = QualityGateConfig(
            max_errors=5,
            max_warnings=100,
            fail_on_error=False,
            fail_on_security_issues=True,
        )

        # CI profile - optimized for continuous integration
        ci_profile = ValidationProfile(
            name="ci",
            description="Optimized for continuous integration environments",
            extends="default",
        )
        ci_profile.reporting = ReportingConfig(
            formats=["json", "junit"],
            output_dir="ci_reports",
            include_passed=False,
            export_trends=True,
        )
        ci_profile.quality_gates = QualityGateConfig(
            max_errors=0,
            max_warnings=20,
            min_success_rate=96.0,
            fail_on_error=True,
            fail_on_security_issues=True,
        )

        # Development profile - lenient for development work
        dev_profile = ValidationProfile(
            name="dev",
            description="Lenient validation for development environments",
            extends="default",
        )
        dev_profile.quality_gates = QualityGateConfig(
            max_errors=10,
            max_warnings=200,
            min_success_rate=85.0,
            fail_on_error=False,
            fail_on_security_issues=False,
        )
        dev_profile.reporting = ReportingConfig(
            formats=["console"],
            include_passed=True,
        )

        # Security-focused profile
        security_profile = ValidationProfile(
            name="security",
            description="Security-focused validation with emphasis on security checks",
        )
        security_profile.checks = {
            "security": CheckConfig(enabled=True),
            "terminology": CheckConfig(
                enabled=True,
                custom_patterns=["password", "secret", "token", "key"],
            ),
        }
        security_profile.quality_gates = QualityGateConfig(
            max_errors=0,
            fail_on_security_issues=True,
            required_checks=["security"],
        )

        # Store all profiles
        self._profiles.update({
            "default": default_profile,
            "strict": strict_profile,
            "fast": fast_profile,
            "ci": ci_profile,
            "dev": dev_profile,
            "security": security_profile,
        })

    def list_profiles(self) -> list[str]:
        """List all available profiles."""
        profile_names = list(self._profiles.keys())

        # Also check config file for additional profiles
        config_file = self.find_config_file()
        if config_file:
            try:
                config_data = self.load_config_file(config_file)
                if "profiles" in config_data:
                    profile_names.extend(config_data["profiles"].keys())
            except Exception:
                pass

        return sorted(set(profile_names))

    def get_profile_info(self, profile_name: str) -> dict[str, Any]:
        """Get information about a specific profile."""
        profile = self.load_profile(profile_name)

        enabled_checks = [name for name, config in profile.checks.items() if config.enabled]

        return {
            "name": profile.name,
            "description": profile.description,
            "enabled_checks": enabled_checks,
            "quality_gates": {
                "max_errors": profile.quality_gates.max_errors,
                "max_warnings": profile.quality_gates.max_warnings,
                "min_success_rate": profile.quality_gates.min_success_rate,
            },
            "reporting_formats": profile.reporting.formats,
            "parallel_execution": profile.parallel_execution,
            "extends": profile.extends,
        }

    def create_sample_config(self, output_path: Path, format_type: str = "yaml") -> None:
        """Create a sample configuration file."""
        sample_config = {
            "default_profile": "default",
            "profiles": {
                "default": {
                    "description": "Default validation profile",
                    "file_patterns": ["**/*.md", "**/*.py"],
                    "parallel_execution": True,
                    "max_workers": 4,
                    "checks": {
                        "markdown_syntax": {"enabled": True},
                        "financial_precision": {"enabled": True},
                        "terminology": {
                            "enabled": True,
                            "custom_patterns": ["company-specific-term"],
                        },
                        "security": {
                            "enabled": True,
                            "options": {"severity_filter": "medium"},
                        },
                    },
                    "quality_gates": {
                        "max_errors": 0,
                        "max_warnings": 50,
                        "min_success_rate": 95.0,
                        "fail_on_security_issues": True,
                    },
                    "reporting": {
                        "formats": ["console", "json", "html"],
                        "output_dir": "validation_reports",
                        "include_file_details": True,
                    },
                },
                "strict": {
                    "extends": "default",
                    "description": "Strict validation with zero tolerance",
                    "quality_gates": {
                        "max_errors": 0,
                        "max_warnings": 10,
                        "min_success_rate": 98.0,
                    },
                },
            },
        }

        if format_type.lower() == "yaml":
            content = yaml.dump(sample_config, default_flow_style=False, indent=2)
        else:
            content = json.dumps(sample_config, indent=2)

        output_path.write_text(content, encoding="utf-8")

# Global config loader instance
default_config_loader = ConfigLoader()
