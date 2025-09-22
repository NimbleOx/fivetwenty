"""
Markdown parsing utilities for documentation tooling.

Safe markdown table parsing with union type preservation and
advanced content extraction capabilities.
"""

import re
from pathlib import Path
from typing import Any, ClassVar


class MarkdownTableParser:
    """Safe markdown table parser with union type preservation."""

    @staticmethod
    def parse_parameter_table(content: str) -> dict[str, dict[str, str]]:
        """
        Parse parameter tables from markdown content.

        Handles escaped pipes in union types like `int | str` without corruption.
        """
        parameters = {}

        # Look for markdown tables with Parameter/Field, Type, Required, Description columns
        table_pattern = r"\|[^|]*(?:Parameter|Field)[^|]*\|[^|]*Type[^|]*\|[^|]*Required[^|]*\|[^|]*Description[^|]*\|.*?\n((?:\|[^|]*\|[^|]*\|[^|]*\|[^|]*\|.*?\n)*)"
        table_match = re.search(table_pattern, content, re.IGNORECASE | re.DOTALL)

        if table_match:
            table_rows = table_match.group(1).strip().split("\n")
            for row in table_rows:
                if "|" in row and not row.strip().startswith("|---"):
                    # Safe parsing with temporary placeholder replacement
                    safe_row = row.replace("\\|", "〈PIPE〉")
                    parts = [p.strip().replace("〈PIPE〉", "|") for p in safe_row.split("|")]

                    if len(parts) >= 5:  # | param | type | required | description |
                        param_name = parts[1].strip("` ")
                        param_type = parts[2].strip("` ")
                        param_required = parts[3].strip()
                        param_description = parts[4].strip()

                        if param_name and param_name not in ["Parameter", "Field", ""]:
                            parameters[param_name] = {"type": param_type, "required": param_required, "description": param_description}

        return parameters

    @staticmethod
    def extract_code_blocks(content: str, language: str | None = None) -> list[str]:
        """Extract code blocks from markdown content."""
        if language:
            pattern = rf"```{language}\n(.*?)\n```"
        else:
            pattern = r"```(?:python|bash|json|yaml)?\n(.*?)\n```"

        return re.findall(pattern, content, re.DOTALL)

    @staticmethod
    def extract_method_signature(content: str) -> dict[str, str] | None:
        """Extract method signature from markdown documentation."""
        # Look for method signature patterns
        sig_pattern = r"```python\n([a-zA-Z_][a-zA-Z0-9_]*\.)?([a-zA-Z_][a-zA-Z0-9_]*)\((.*?)\)(?: -> (.+?))?\n```"
        match = re.search(sig_pattern, content, re.DOTALL)

        if match:
            prefix = match.group(1) or ""
            method_name = match.group(2)
            parameters = match.group(3)
            return_type = match.group(4) or "Any"

            return {"name": method_name, "full_signature": f"{prefix}{method_name}({parameters})", "parameters": parameters, "return_type": return_type}

        return None

    @staticmethod
    def extract_http_info(content: str) -> dict[str, str]:
        """Extract HTTP method and path information from markdown."""
        http_info = {}

        # Look for OANDA Endpoint patterns
        endpoint_pattern = r"🔗 \*\*OANDA Endpoint\*\*: `(\w+) (.+?)`"
        match = re.search(endpoint_pattern, content)

        if match:
            http_info["method"] = match.group(1)
            http_info["path"] = match.group(2)

        return http_info


class DocumentationExtractor:
    """High-level documentation content extractor."""

    def __init__(self) -> None:
        self.table_parser = MarkdownTableParser()

    def extract_endpoint_docs(self, file_path: Path) -> list[dict[str, Any]]:
        """Extract endpoint documentation from markdown file."""
        endpoints = []

        try:
            with Path(file_path).open(encoding="utf-8") as f:
                content = f.read()

            # Split content by endpoint sections (## headers)
            endpoint_sections = re.split(r"^## (.+)$", content, flags=re.MULTILINE)

            for i in range(1, len(endpoint_sections), 2):
                endpoint_name = endpoint_sections[i].strip()
                endpoint_content = endpoint_sections[i + 1] if i + 1 < len(endpoint_sections) else ""

                endpoint_info = self._parse_endpoint_section(endpoint_name, endpoint_content, str(file_path))
                if endpoint_info:
                    endpoints.append(endpoint_info)

        except Exception as e:
            print(f"Error processing endpoint documentation {file_path}: {e}")

        return endpoints

    def extract_model_docs(self, file_path: Path) -> list[dict[str, Any]]:
        """Extract model documentation from markdown file."""
        models = []

        try:
            with Path(file_path).open(encoding="utf-8") as f:
                content = f.read()

            # Split content by model sections (### headers)
            model_sections = re.split(r"^### (.+)$", content, flags=re.MULTILINE)

            for i in range(1, len(model_sections), 2):
                model_name = model_sections[i].strip()
                model_content = model_sections[i + 1] if i + 1 < len(model_sections) else ""

                model_info = self._parse_model_section(model_name, model_content, str(file_path))
                if model_info:
                    models.append(model_info)

        except Exception as e:
            print(f"Error processing model documentation {file_path}: {e}")

        return models

    def _parse_endpoint_section(self, endpoint_name: str, content: str, file_path: str) -> dict[str, Any] | None:
        """Parse an endpoint section from markdown content."""
        # Extract description (first paragraph)
        description_match = re.search(r"^([^\n|]+(?:\n[^\n|]+)*)", content.strip(), re.MULTILINE)
        description = description_match.group(1).strip() if description_match else ""

        # Extract method signature
        signature = self.table_parser.extract_method_signature(content)

        # Extract HTTP information
        http_info = self.table_parser.extract_http_info(content)

        # Extract parameters table
        parameters = self.table_parser.parse_parameter_table(content)

        # Extract examples
        examples = self.table_parser.extract_code_blocks(content)

        return {"name": endpoint_name, "description": description, "signature": signature, "http_method": http_info.get("method", ""), "path": http_info.get("path", ""), "parameters": parameters, "examples": examples, "file_path": file_path}

    def _parse_model_section(self, model_name: str, content: str, file_path: str) -> dict[str, Any] | None:
        """Parse a model section from markdown content."""
        # Extract description (first paragraph)
        description_match = re.search(r"^([^\n|]+(?:\n[^\n|]+)*)", content.strip(), re.MULTILINE)
        description = description_match.group(1).strip() if description_match else ""

        # Extract fields table
        documented_fields = self.table_parser.parse_parameter_table(content)

        # Extract examples
        examples = self.table_parser.extract_code_blocks(content, "python")

        return {"name": model_name, "description": description, "documented_fields": documented_fields, "examples": examples, "file_path": file_path}


class FileMapping:
    """Smart file-aware mapping for resolving documentation conflicts."""

    # File-specific mappings to resolve endpoint name conflicts
    FILE_SPECIFIC_MAPPINGS: ClassVar[dict[str, str]] = {
        "get_accounts": "accounts.list",
        "get_orders": "orders.list",
        "cancel_order": "orders.close",
        "close_position": "positions.close",
        "close_trade": "trades.close",
        "put_trade_orders": "trades.modify",
        "put_trade_client_extensions": "trades.modify_client_extensions",
        "get_pricing": "pricing.get",
        "stream_pricing": "pricing.stream",
        "get_instruments": "instruments.list",
        "get_candles": "instruments.candles",
    }

    @staticmethod
    def map_endpoint_name(impl_name: str, doc_name: str, _file_context: str) -> float:
        """
        Calculate mapping score between implementation and documentation names.

        Uses four-pass algorithm:
        1. File-specific mappings
        2. Direct name matches
        3. Exact implementation matching
        4. Fuzzy matching with similarity
        """
        # Pass 1: File-specific mappings
        if impl_name in FileMapping.FILE_SPECIFIC_MAPPINGS:
            expected_doc = FileMapping.FILE_SPECIFIC_MAPPINGS[impl_name]
            if expected_doc == doc_name:
                return 1.0

        # Pass 2: Direct name matches
        if impl_name == doc_name:
            return 1.0

        # Pass 3: Implementation-based matching
        if impl_name.replace("_", ".") in doc_name or doc_name.replace("_", ".") in impl_name:
            return 0.9

        # Pass 4: Fuzzy matching
        return FileMapping._calculate_similarity(impl_name, doc_name)

    @staticmethod
    def _calculate_similarity(str1: str, str2: str) -> float:
        """Calculate string similarity score."""
        if not str1 or not str2:
            return 0.0

        # Simple Levenshtein-based similarity
        max_len = max(len(str1), len(str2))
        if max_len == 0:
            return 1.0

        # Calculate edit distance
        distance = FileMapping._edit_distance(str1.lower(), str2.lower())
        return 1.0 - (distance / max_len)

    @staticmethod
    def _edit_distance(s1: str, s2: str) -> int:
        """Calculate edit distance between two strings."""
        if len(s1) < len(s2):
            return FileMapping._edit_distance(s2, s1)

        if len(s2) == 0:
            return len(s1)

        previous_row = list(range(len(s2) + 1))
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row

        return previous_row[-1]
