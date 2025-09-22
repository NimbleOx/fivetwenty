"""Centralized validation configuration."""

from pathlib import Path

from pydantic import BaseModel, Field


class FilePatterns(BaseModel):
    """File pattern configuration for different content types."""

    markdown: list[str] = Field(default_factory=lambda: ["**/*.md"])
    python: list[str] = Field(default_factory=lambda: ["**/*.py"])
    documentation: list[str] = Field(default_factory=lambda: ["docs/**/*.md", "*.md"])
    tutorials: list[str] = Field(default_factory=lambda: ["docs/tutorials/**/*.md"])
    api_reference: list[str] = Field(default_factory=lambda: ["docs/api-reference/**/*.md"])


class ToolConfig(BaseModel):
    """External tool configuration."""

    vale_enabled: bool = True
    vale_config: Path | None = None
    ruff_enabled: bool = True
    mypy_enabled: bool = True

    # Tool-specific settings
    vale_min_alert_level: str = "warning"
    ruff_line_length: int = 120
    parallel_workers: int = 4
    timeout_seconds: float = 300.0


class QualityGates(BaseModel):
    """Quality gate thresholds."""

    max_error_rate: float = 0.05  # 5% error rate threshold
    max_critical_issues: int = 0
    min_success_rate: float = 95.0

    # Per-validator thresholds
    prose_max_issues: int = 50
    syntax_max_issues: int = 5
    links_max_broken: int = 3


class ValidationConfig(BaseModel):
    """Main validation configuration."""

    # Project paths
    project_root: Path = Field(default_factory=lambda: Path.cwd())
    docs_root: Path = Field(default_factory=lambda: Path("docs"))
    reports_dir: Path = Field(default_factory=lambda: Path("reports"))

    # File patterns
    file_patterns: FilePatterns = Field(default_factory=FilePatterns)

    # External tools
    tools: ToolConfig = Field(default_factory=ToolConfig)

    # Quality gates
    quality_gates: QualityGates = Field(default_factory=QualityGates)

    # Validation settings
    parallel_execution: bool = True
    cache_enabled: bool = True
    generate_reports: bool = True

    # Excluded paths
    exclude_patterns: list[str] = Field(default_factory=lambda: [
        "**/__pycache__/**",
        "**/.git/**",
        "**/node_modules/**",
        "**/.venv/**",
        "**/build/**",
        "**/dist/**",
    ])

    @classmethod
    def from_file(cls, config_path: Path) -> "ValidationConfig":
        """Load configuration from file."""
        if config_path.suffix == ".json":
            import json
            with config_path.open() as f:
                data = json.load(f)
        elif config_path.suffix in [".yaml", ".yml"]:
            import yaml
            with config_path.open() as f:
                data = yaml.safe_load(f)
        else:
            raise ValueError(f"Unsupported config format: {config_path.suffix}")

        return cls(**data)

    def resolve_paths(self) -> None:
        """Resolve all paths relative to project root."""
        self.docs_root = self.project_root / self.docs_root
        self.reports_dir = self.project_root / self.reports_dir

        if self.tools.vale_config:
            self.tools.vale_config = self.project_root / self.tools.vale_config

    def get_files_for_patterns(self, patterns: list[str]) -> list[Path]:
        """Get all files matching the given patterns."""
        from pathspec import PathSpec

        files = []
        exclude_spec = PathSpec.from_lines("gitwildmatch", self.exclude_patterns)

        for pattern in patterns:
            pattern_files = list(self.project_root.glob(pattern))
            # Filter out excluded files
            filtered_files = [
                f for f in pattern_files
                if f.is_file() and not exclude_spec.match_file(str(f.relative_to(self.project_root)))
            ]
            files.extend(filtered_files)

        return sorted(set(files))


# Global configuration instance
_config: ValidationConfig | None = None


def get_config() -> ValidationConfig:
    """Get the global configuration instance."""
    global _config
    if _config is None:
        _config = ValidationConfig()
        _config.resolve_paths()
    return _config


def set_config(config: ValidationConfig) -> None:
    """Set the global configuration instance."""
    global _config
    _config = config
    _config.resolve_paths()
