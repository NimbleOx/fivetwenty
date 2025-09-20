"""
Configuration management for validation system.
"""

import os
from pathlib import Path
from typing import Any

try:
    import yaml  # type: ignore[import-untyped]

    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False


class ValidationConfig:
    """Manages validation configuration and settings."""

    def __init__(self, config_override: dict[str, Any] | None = None, config_file: Path | None = None):
        """Initialize configuration with optional override and file support."""
        self._config_file = config_file or self._find_config_file()
        base_config = self._load_config_from_file() if self._config_file else self._get_default_config()

        # Apply environment variable overrides
        base_config = self._apply_env_overrides(base_config)

        # Apply explicit overrides last
        if config_override:
            base_config = self._deep_merge(base_config, config_override)

        self._config = base_config

    def _get_default_config(self) -> dict[str, Any]:
        """Get default configuration."""
        return {
            "validation_schedule": {
                "daily": {"enabled": True, "time": "08:00", "timezone": "UTC", "tasks": ["Link validation", "Code example testing", "Security scanning"]},
                "weekly": {"enabled": True, "day": "Monday", "time": "09:00", "timezone": "UTC", "tasks": ["Model documentation validation", "Endpoint coverage validation", "Version consistency check"]},
                "monthly": {"enabled": True, "day": 1, "time": "10:00", "timezone": "UTC", "tasks": ["Full documentation accuracy review", "Quality metrics assessment", "Executive report generation"]},
                "quarterly": {"enabled": True, "months": [1, 4, 7, 10], "day": 15, "time": "14:00", "timezone": "UTC", "tasks": ["Comprehensive consistency audit", "Completeness review", "Strategic quality planning"]},
            },
            "quality_standards": {
                "minimum_thresholds": {"endpoint_accuracy": 100.0, "model_accuracy": 95.0, "model_coverage": 85.0, "code_example_success": 75.0, "link_validation": 95.0, "security_score": 90.0, "consistency_score": 80.0, "version_consistency": 95.0},
                "blocking_thresholds": {"critical_security_issues": 0, "build_failures": 0, "broken_links_critical": 0},
            },
            "notification_settings": {"email_alerts": {"enabled": False, "recipients": [], "threshold_breaches": True, "daily_summary": False}, "slack_integration": {"enabled": False, "webhook_url": "", "channel": "#documentation", "mention_on_failures": True}},
        }

    def get_threshold(self, metric: str) -> float:
        """Get threshold value for a metric."""
        thresholds = self._config.get("quality_standards", {}).get("minimum_thresholds", {})
        return float(thresholds.get(metric, 0.0))

    def get_blocking_threshold(self, metric: str) -> int:
        """Get blocking threshold for a metric."""
        thresholds = self._config.get("quality_standards", {}).get("blocking_thresholds", {})
        return int(thresholds.get(metric, 0))

    def is_task_enabled(self, schedule: str, task: str) -> bool:
        """Check if a scheduled task is enabled."""
        schedule_config = self._config.get("validation_schedule", {}).get(schedule, {})
        return schedule_config.get("enabled", False) and task in schedule_config.get("tasks", [])

    def get_all_thresholds(self) -> dict[str, float]:
        """Get all minimum thresholds."""
        thresholds = self._config.get("quality_standards", {}).get("minimum_thresholds", {})
        return {k: float(v) for k, v in thresholds.items()}

    def update_config(self, updates: dict[str, Any]) -> None:
        """Update configuration with new values."""

        def deep_update(d: dict[str, Any], u: dict[str, Any]) -> dict[str, Any]:
            for k, v in u.items():
                if isinstance(v, dict) and k in d and isinstance(d[k], dict):
                    d[k] = deep_update(d[k], v)
                else:
                    d[k] = v
            return d

        self._config = deep_update(self._config.copy(), updates)

    def _find_config_file(self) -> Path | None:
        """Find validation configuration file in standard locations."""
        candidates = [
            Path(__file__).parent.parent / "validation-config.yml",  # Primary: validation/validation-config.yml
            Path(__file__).parent.parent / "validation-rules.yml",  # Alternative: validation/validation-rules.yml
            Path("docs-tooling/validation/validation-config.yml"),  # Absolute path from project root
            Path("docs-tooling/validation-config.yml"),  # Legacy location
            Path("docs-tooling/validation.yml"),  # Alternative in tooling directory
            Path("docs-tooling/validation.yaml"),
            Path(".validation.yml"),  # Legacy location for backward compatibility
            Path(".validation.yaml"),
            Path.cwd() / ".validation.yml",
            Path.home() / ".fivetwenty" / "validation.yml",
        ]

        for candidate in candidates:
            if candidate.exists() and candidate.is_file():
                return candidate

        return None

    def _load_config_from_file(self) -> dict[str, Any]:
        """Load configuration from YAML file."""
        if not self._config_file or not YAML_AVAILABLE:
            return self._get_default_config()

        try:
            with self._config_file.open(encoding="utf-8") as f:
                file_config = yaml.safe_load(f) or {}

            # Merge with defaults
            return self._deep_merge(self._get_default_config(), file_config)

        except Exception:
            # Fallback to defaults if file can't be loaded
            return self._get_default_config()

    def _apply_env_overrides(self, config: dict[str, Any]) -> dict[str, Any]:
        """Apply environment variable overrides to configuration."""
        env_mappings = {
            "VALIDATION_LINK_THRESHOLD": ["quality_standards", "minimum_thresholds", "link_validation"],
            "VALIDATION_SECURITY_THRESHOLD": ["quality_standards", "minimum_thresholds", "security_score"],
            "VALIDATION_SYNTAX_THRESHOLD": ["quality_standards", "minimum_thresholds", "syntax_score"],
            "VALIDATION_CACHE_TTL": ["cache_settings", "ttl_seconds"],
        }

        for env_var, config_path in env_mappings.items():
            if env_var in os.environ:
                try:
                    value = float(os.environ[env_var]) if "threshold" in env_var.lower() else int(os.environ[env_var])
                    self._set_nested_value(config, config_path, value)
                except ValueError:
                    pass  # Skip invalid values

        return config

    def _set_nested_value(self, config: dict[str, Any], path: list[str], value: Any) -> None:
        """Set a nested configuration value using a path list."""
        current = config
        for key in path[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
        current[path[-1]] = value

    def _deep_merge(self, base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
        """Deep merge two dictionaries."""
        result = base.copy()

        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value

        return result
