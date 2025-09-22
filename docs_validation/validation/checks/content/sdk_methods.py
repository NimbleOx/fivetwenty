"""SDK method validation checks."""

import re
from pathlib import Path
from typing import Any

from docs_validation.validation.checks.base import ContentCheck
from docs_validation.validation.core.context import ValidationContext
from docs_validation.validation.core.results import IssueSeverity, ValidationIssue, ValidationResult


class SDKMethodsCheck(ContentCheck):
    """Check for deprecated SDK method usage in documentation."""

    def __init__(self) -> None:
        super().__init__(
            name="sdk_methods",
            description="Validates current SDK method names and identifies deprecated patterns",
            file_patterns=["**/*.md"],
            required_extensions=[".md"],
        )

    def check_content(
        self,
        file_path: Path,
        content: str,
        context: ValidationContext,
        result: ValidationResult,
    ) -> None:
        """Check for deprecated SDK method usage."""
        # Get deprecated method patterns
        deprecated_patterns = self._get_deprecated_method_rules()

        lines = content.split('\n')

        for line_num, line in enumerate(lines, 1):
            for pattern, replacement, description in deprecated_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    result.add_issue(
                        message=f"Deprecated SDK method usage: {description}",
                        file_path=str(file_path),
                        line=line_num,
                        severity=IssueSeverity.ERROR,
                        suggestion=f"Replace with: {replacement}",
                    )

    def _get_deprecated_method_rules(self) -> list[tuple[str, str, str]]:
        """Get deprecated method validation rules.

        Returns:
            List of tuples (pattern, replacement, description)
        """
        return [
            # Order creation methods - most critical
            (r"\.create_market\s*\(", ".post_market_order(", "create_market() → post_market_order()"),
            (r"\.create_limit\s*\(", ".post_limit_order(", "create_limit() → post_limit_order()"),
            (r"\.create_stop\s*\(", ".post_stop_order(", "create_stop() → post_stop_order()"),
            (r"\.create_order\s*\(", ".post_order(", "create_order() → post_order()"),

            # Position management
            (r"\.get_position\s*\(", ".get_positions(", "get_position() → get_positions()"),
            (r"\.close_position\s*\(", ".close_positions(", "close_position() → close_positions()"),

            # Account methods
            (r"\.get_account_summary\s*\(", ".get_accounts(", "get_account_summary() → get_accounts()"),
            (r"\.get_account_instruments\s*\(", ".get_instruments(", "get_account_instruments() → get_instruments()"),

            # Pricing methods
            (r"\.get_latest_candles\s*\(", ".get_candles(", "get_latest_candles() → get_candles()"),
            (r"\.get_pricing_stream\s*\(", ".stream_pricing(", "get_pricing_stream() → stream_pricing()"),

            # Transaction methods
            (r"\.get_transaction_history\s*\(", ".get_transactions(", "get_transaction_history() → get_transactions()"),
            (r"\.get_transaction_details\s*\(", ".get_transaction(", "get_transaction_details() → get_transaction()"),

            # Configuration patterns
            (r"api_url\s*=", "environment=Environment.PRACTICE", "Use Environment enum instead of direct URLs"),
            (r"practice\.oanda\.com", "Environment.PRACTICE", "Use Environment.PRACTICE instead of hardcoded URL"),
            (r"api-fxtrade\.oanda\.com", "Environment.LIVE", "Use Environment.LIVE instead of hardcoded URL"),

            # Import patterns
            (r"from fivetwenty\.client import OandaClient", "from fivetwenty import Client", "Use Client instead of OandaClient"),
            (r"from fivetwenty\.async_client import AsyncOandaClient", "from fivetwenty import AsyncClient", "Use AsyncClient instead of AsyncOandaClient"),

            # Authentication patterns
            (r"\.set_token\s*\(", "Client(token=..., environment=...)", "Use constructor parameters instead of set_token()"),
            (r"\.authenticate\s*\(", "Client(token=..., environment=...)", "Use constructor parameters instead of authenticate()"),

            # Error handling patterns
            (r"OandaException", "VeeTwentyError", "Use VeeTwentyError instead of OandaException"),
            (r"OandaError", "VeeTwentyError", "Use VeeTwentyError instead of OandaError"),

            # Model patterns
            (r"\.to_dict\s*\(", ".model_dump()", "Use .model_dump() instead of .to_dict()"),
            (r"\.from_dict\s*\(", ".model_validate()", "Use .model_validate() instead of .from_dict()"),
        ]

    def _extract_code_blocks(self, content: str) -> list[dict[str, Any]]:
        """Extract code blocks from markdown content."""
        code_blocks = []
        lines = content.split('\n')
        in_code_block = False
        current_block = []
        block_start_line = 0
        block_language = ""

        for line_num, line in enumerate(lines, 1):
            if line.strip().startswith('```'):
                if in_code_block:
                    # End of code block
                    code_blocks.append({
                        'content': '\n'.join(current_block),
                        'start_line': block_start_line,
                        'end_line': line_num,
                        'language': block_language
                    })
                    in_code_block = False
                    current_block = []
                else:
                    # Start of code block
                    in_code_block = True
                    block_start_line = line_num + 1
                    block_language = line.strip()[3:].strip()
                    current_block = []
            elif in_code_block:
                current_block.append(line)

        return code_blocks