"""Efficient file discovery and pattern matching."""

import fnmatch
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from docs_validation.validation.core.config import ValidationConfig


class FileFinder:
    """Efficient file discovery with caching and pattern matching."""

    def __init__(self, config: ValidationConfig) -> None:
        self.config = config
        self._cache: dict[str, list[Path]] = {}

    def find_files(self, patterns: list[str], base_path: Path | None = None) -> list[Path]:
        """Find files matching patterns."""
        if base_path is None:
            base_path = self.config.project_root

        # Create cache key
        cache_key = f"{base_path}:{':'.join(sorted(patterns))}"

        if cache_key not in self._cache:
            self._cache[cache_key] = self._find_files_impl(patterns, base_path)

        return self._cache[cache_key]

    def _find_files_impl(self, patterns: list[str], base_path: Path) -> list[Path]:
        """Implementation of file finding."""
        found_files: set[Path] = set()

        # Use glob for each pattern
        for pattern in patterns:
            try:
                # Handle absolute vs relative patterns
                if pattern.startswith("/"):
                    search_path = Path(pattern)
                    if search_path.exists():
                        pattern_files = [search_path] if search_path.is_file() else list(search_path.rglob("*"))
                else:
                    pattern_files = list(base_path.glob(pattern))

                # Filter files and apply exclusions
                for file_path in pattern_files:
                    if file_path.is_file() and not self._is_excluded(file_path, base_path):
                        found_files.add(file_path)

            except (OSError, ValueError) as e:
                # Skip invalid patterns
                print(f"Warning: Invalid pattern '{pattern}': {e}")
                continue

        return sorted(found_files)

    def _is_excluded(self, file_path: Path, base_path: Path) -> bool:
        """Check if file should be excluded."""
        try:
            # Get relative path for pattern matching
            rel_path = file_path.relative_to(base_path)
            rel_path_str = str(rel_path)

            # Check against exclude patterns
            for exclude_pattern in self.config.exclude_patterns:
                if fnmatch.fnmatch(rel_path_str, exclude_pattern):
                    return True

                # Also check directory patterns
                for parent in rel_path.parents:
                    if fnmatch.fnmatch(str(parent), exclude_pattern):
                        return True

        except ValueError:
            # File is not under base_path
            return True

        return False

    def find_files_parallel(self, pattern_groups: list[list[str]], base_path: Path | None = None) -> list[Path]:
        """Find files for multiple pattern groups in parallel."""
        if base_path is None:
            base_path = self.config.project_root

        all_files: set[Path] = set()

        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = [
                executor.submit(self.find_files, patterns, base_path)
                for patterns in pattern_groups
            ]

            for future in as_completed(futures):
                try:
                    files = future.result()
                    all_files.update(files)
                except Exception as e:
                    print(f"Error in parallel file finding: {e}")

        return sorted(all_files)

    def find_by_extension(self, extensions: list[str], base_path: Path | None = None) -> list[Path]:
        """Find files by extensions."""
        if base_path is None:
            base_path = self.config.project_root

        patterns = [f"**/*.{ext.lstrip('.')}" for ext in extensions]
        return self.find_files(patterns, base_path)

    def find_markdown_files(self, base_path: Path | None = None) -> list[Path]:
        """Find all markdown files."""
        return self.find_files(self.config.file_patterns.markdown, base_path)

    def find_python_files(self, base_path: Path | None = None) -> list[Path]:
        """Find all Python files."""
        return self.find_files(self.config.file_patterns.python, base_path)

    def find_documentation_files(self, base_path: Path | None = None) -> list[Path]:
        """Find all documentation files."""
        return self.find_files(self.config.file_patterns.documentation, base_path)

    def clear_cache(self) -> None:
        """Clear the file cache."""
        self._cache.clear()

    def get_cache_stats(self) -> dict[str, int]:
        """Get cache statistics."""
        return {
            "cached_patterns": len(self._cache),
            "total_cached_files": sum(len(files) for files in self._cache.values()),
        }
