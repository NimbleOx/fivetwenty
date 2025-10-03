"""Configuration management for the validation framework."""

from __future__ import annotations

from pathlib import Path  # noqa: TC003
from typing import Any

import yaml
from pydantic import BaseModel, Field


class ValidatorConfig(BaseModel):
    """Configuration for a single validator."""

    enabled: bool = True
    options: dict[str, Any] = Field(default_factory=dict)


class ValidationConfig(BaseModel):
    """Main validation configuration."""

    # File discovery
    file_patterns: list[str] = Field(default_factory=lambda: ["docs/**/*.md"])
    exclude_patterns: list[str] = Field(
        default_factory=lambda: [
            "**/.git/**",
            "**/node_modules/**",
            "**/__pycache__/**",
            "**/validation_reports/**",
        ]
    )

    # Execution settings
    parallel_execution: bool = True
    max_workers: int = 4
    timeout_seconds: float = 30.0

    # Validator configurations
    validators: dict[str, ValidatorConfig] = Field(default_factory=dict)

    @classmethod
    def load_from_file(cls, config_path: Path) -> ValidationConfig:
        """Load configuration from YAML file."""
        if not config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")

        with config_path.open(encoding="utf-8") as f:
            data = yaml.safe_load(f)

        return cls.model_validate(data)

    @classmethod
    def get_default_config(cls) -> ValidationConfig:
        """Get default configuration for FiveTwenty documentation - docs/ directory only."""
        return cls(
            file_patterns=[
                "docs/**/*.md",
            ],
            exclude_patterns=[
                # Version control and caches
                "**/.git/**",
                "**/__pycache__/**",
                "**/.mypy_cache/**",
                "**/.ruff_cache/**",
                "**/.pytest_cache/**",
                "**/.venv/**",
                # Build artifacts
                "**/build/**",
                "**/dist/**",
                "**/*.egg-info/**",
                "**/node_modules/**",
                # Validation outputs
                "**/validation_reports/**",
                "**/validation_old/**",
                # Exclude everything outside docs/
                "fivetwenty/**",
                "tests/**",
                "examples/**",
                "docs_validation/**",
                "oanda-api-reference/**",
                "*.py",
                "/*.md",  # Root level markdown files only
            ],
            validators={
                "financial_precision": ValidatorConfig(enabled=True, options={"strict_mode": True}),
                "security": ValidatorConfig(enabled=True, options={"severity_filter": "high", "exclude_patterns": ["example", "demo", "tutorial", "YOUR_TOKEN_HERE", "abc123", "practice-token", "live-token", "your-token", "your-api-token"]}),
                "markdown_syntax": ValidatorConfig(enabled=True),
                "python_syntax": ValidatorConfig(enabled=True),
                "cross_references": ValidatorConfig(enabled=True),
                "sdk_methods": ValidatorConfig(enabled=False),  # Disabled due to many missing docs (334 issues)
            },
        )

    def is_validator_enabled(self, validator_name: str) -> bool:
        """Check if a validator is enabled."""
        config = self.validators.get(validator_name)
        return config.enabled if config else False

    def get_validator_options(self, validator_name: str) -> dict[str, Any]:
        """Get options for a specific validator."""
        config = self.validators.get(validator_name)
        return config.options if config else {}
