"""Shared validation context for caching and coordination."""

import hashlib
from datetime import datetime
from pathlib import Path
from typing import Any

from docs_validation.validation.core.config import ValidationConfig, get_config


class FileCache:
    """File content and metadata cache."""

    def __init__(self) -> None:
        self._content_cache: dict[str, str] = {}
        self._metadata_cache: dict[str, dict[str, Any]] = {}
        self._file_hashes: dict[str, str] = {}

    def get_content(self, file_path: Path) -> str:
        """Get cached file content or read from disk."""
        path_str = str(file_path)

        # Check if file has changed
        current_hash = self._get_file_hash(file_path)
        if path_str in self._file_hashes and self._file_hashes[path_str] != current_hash:
            # File changed, invalidate cache
            self._invalidate_file(path_str)

        if path_str not in self._content_cache:
            self._content_cache[path_str] = file_path.read_text(encoding="utf-8")
            self._file_hashes[path_str] = current_hash

        return self._content_cache[path_str]

    def get_metadata(self, file_path: Path, key: str) -> Any:
        """Get cached metadata for a file."""
        path_str = str(file_path)
        return self._metadata_cache.get(path_str, {}).get(key)

    def set_metadata(self, file_path: Path, key: str, value: Any) -> None:
        """Set metadata for a file."""
        path_str = str(file_path)
        if path_str not in self._metadata_cache:
            self._metadata_cache[path_str] = {}
        self._metadata_cache[path_str][key] = value

    def _get_file_hash(self, file_path: Path) -> str:
        """Calculate MD5 hash of file."""
        if not file_path.exists():
            return ""

        hasher = hashlib.md5()
        with file_path.open("rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hasher.update(chunk)
        return hasher.hexdigest()

    def _invalidate_file(self, path_str: str) -> None:
        """Remove file from all caches."""
        self._content_cache.pop(path_str, None)
        self._metadata_cache.pop(path_str, None)
        self._file_hashes.pop(path_str, None)

    def clear(self) -> None:
        """Clear all caches."""
        self._content_cache.clear()
        self._metadata_cache.clear()
        self._file_hashes.clear()


class ValidationContext:
    """Shared context for validation operations."""

    def __init__(self, config: ValidationConfig | None = None) -> None:
        self.config = config or get_config()
        self.file_cache = FileCache()
        self.session_data: dict[str, Any] = {}
        self.start_time = datetime.now()

        # Track validation state
        self._files_to_check: set[Path] = set()
        self._files_checked: set[Path] = set()
        self._external_tools: dict[str, bool] = {}

    def get_files_for_validation(self, patterns: list[str] | None = None) -> list[Path]:
        """Get files that need validation based on patterns."""
        if patterns is None:
            patterns = self.config.file_patterns.documentation

        if not self._files_to_check:
            self._files_to_check = set(self.config.get_files_for_patterns(patterns))

        return sorted(self._files_to_check)

    def mark_file_checked(self, file_path: Path) -> None:
        """Mark a file as checked."""
        self._files_checked.add(file_path)

    def is_file_checked(self, file_path: Path) -> bool:
        """Check if file has been checked."""
        return file_path in self._files_checked

    def get_file_content(self, file_path: Path) -> str:
        """Get file content (cached)."""
        return self.file_cache.get_content(file_path)

    def cache_file_metadata(self, file_path: Path, key: str, value: Any) -> None:
        """Cache metadata for a file."""
        self.file_cache.set_metadata(file_path, key, value)

    def get_cached_metadata(self, file_path: Path, key: str) -> Any:
        """Get cached metadata for a file."""
        return self.file_cache.get_metadata(file_path, key)

    def check_external_tool(self, tool_name: str) -> bool:
        """Check if external tool is available (cached)."""
        if tool_name not in self._external_tools:
            import shutil

            self._external_tools[tool_name] = shutil.which(tool_name) is not None

        return self._external_tools[tool_name]

    def get_session_data(self, key: str, default: Any = None) -> Any:
        """Get session-wide data."""
        return self.session_data.get(key, default)

    def set_session_data(self, key: str, value: Any) -> None:
        """Set session-wide data."""
        self.session_data[key] = value

    def clear_cache(self) -> None:
        """Clear all cached data."""
        self.file_cache.clear()
        self.session_data.clear()
        self._files_checked.clear()
        self._external_tools.clear()

    @property
    def elapsed_time(self) -> float:
        """Get elapsed time since context creation."""
        return (datetime.now() - self.start_time).total_seconds()

    def get_stats(self) -> dict[str, Any]:
        """Get context statistics."""
        return {
            "files_to_check": len(self._files_to_check),
            "files_checked": len(self._files_checked),
            "cache_size": len(self.file_cache._content_cache),
            "elapsed_time": self.elapsed_time,
            "external_tools": self._external_tools,
        }
