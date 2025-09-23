"""Core validation engine for file discovery and orchestration."""

import hashlib
import os
from collections.abc import Generator
from pathlib import Path

import pathspec

from .base import registry
from .config import ValidationConfig
from .models import FileInfo, ValidationSummary


class ValidationEngine:
    """Main validation engine that coordinates file discovery and validation."""

    def __init__(self, config: ValidationConfig, project_root: Path | None = None):
        self.config = config
        self.project_root = project_root or Path.cwd()

    def discover_files(self) -> list[FileInfo]:
        """Discover all files matching the configured patterns."""
        files: list[FileInfo] = []

        # Create pathspecs for inclusion and exclusion
        include_spec = pathspec.PathSpec.from_lines("gitwildmatch", self.config.file_patterns)
        exclude_spec = pathspec.PathSpec.from_lines("gitwildmatch", self.config.exclude_patterns)

        # Walk through project directory
        for file_path in self._walk_files():
            relative_path = file_path.relative_to(self.project_root)

            # Check inclusion patterns
            if not include_spec.match_file(str(relative_path)):
                continue

            # Check exclusion patterns
            if exclude_spec.match_file(str(relative_path)):
                continue

            # Get file info
            try:
                stat = file_path.stat()
                file_info = FileInfo(
                    path=file_path,
                    size_bytes=stat.st_size,
                    modified_time=stat.st_mtime,
                )
                files.append(file_info)
            except OSError:
                # Skip files that can't be read
                continue

        return sorted(files, key=lambda f: f.path)

    def _walk_files(self) -> Generator[Path, None, None]:
        """Walk through all files in the project directory."""
        for root, _, filenames in os.walk(self.project_root):
            root_path = Path(root)
            for filename in filenames:
                file_path = root_path / filename
                if file_path.is_file():
                    yield file_path

    def load_file_content(self, file_info: FileInfo) -> str:
        """Load and return the content of a file."""
        try:
            with file_info.path.open("r", encoding="utf-8", errors="replace") as f:
                content = f.read()

            # Update content hash if needed
            if file_info.content_hash is None:
                file_info.content_hash = hashlib.md5(content.encode("utf-8")).hexdigest()

            return content
        except (OSError, UnicodeDecodeError) as e:
            raise ValueError(f"Failed to read file {file_info.path}: {e}") from e

    def validate(self) -> ValidationSummary:
        """Run validation on all discovered files."""
        # Discover files
        files = self.discover_files()

        if not files:
            return ValidationSummary(
                total_files=0,
                total_validators=0,
                passed_files=0,
                failed_files=0,
                total_issues=0,
                error_count=0,
                warning_count=0,
                duration_ms=0.0,
                validator_summaries=[],
            )

        # Load file contents
        files_with_content: list[tuple[FileInfo, str]] = []
        for file_info in files:
            try:
                content = self.load_file_content(file_info)
                files_with_content.append((file_info, content))
            except ValueError:  # noqa: PERF203
                # Skip files that can't be loaded
                continue

        # Get enabled validators
        enabled_validators = [name for name, config in self.config.validators.items() if config.enabled]

        # Get validator options
        validator_options = {name: config.options for name, config in self.config.validators.items()}

        # Run validation
        return registry.validate_files(
            files=files_with_content,
            enabled_validators=enabled_validators,
            validator_options=validator_options,
            parallel=self.config.parallel_execution,
            max_workers=self.config.max_workers,
        )

    def validate_incremental(self, changed_files: list[Path]) -> ValidationSummary:
        """Run validation only on specified changed files."""
        # Convert to FileInfo objects
        files: list[FileInfo] = []
        for file_path in changed_files:
            if not file_path.exists():
                continue

            try:
                stat = file_path.stat()
                file_info = FileInfo(
                    path=file_path,
                    size_bytes=stat.st_size,
                    modified_time=stat.st_mtime,
                )
                files.append(file_info)
            except OSError:
                continue

        if not files:
            return ValidationSummary(
                total_files=0,
                total_validators=0,
                passed_files=0,
                failed_files=0,
                total_issues=0,
                error_count=0,
                warning_count=0,
                duration_ms=0.0,
                validator_summaries=[],
            )

        # Load file contents and validate
        files_with_content: list[tuple[FileInfo, str]] = []
        for file_info in files:
            try:
                content = self.load_file_content(file_info)
                files_with_content.append((file_info, content))
            except ValueError:  # noqa: PERF203
                continue

        enabled_validators = [name for name, config in self.config.validators.items() if config.enabled]

        validator_options = {name: config.options for name, config in self.config.validators.items()}

        return registry.validate_files(
            files=files_with_content,
            enabled_validators=enabled_validators,
            validator_options=validator_options,
            parallel=self.config.parallel_execution,
            max_workers=self.config.max_workers,
        )
