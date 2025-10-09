"""Code execution validator for testing code examples actually run.

IMPLEMENTATION NOTES:
--------------------
This validator executes Python code blocks in markdown files within a sandboxed environment.
It uses signal handlers (SIGALRM) for timeouts and redirects stdout/stderr, which are not
thread-safe. Therefore, this validator always runs sequentially even when parallel mode is
enabled for other validators.

The registry automatically handles this by splitting validators into parallel-safe and
sequential-only groups during execution.
"""

import asyncio
import io
import re
import resource
import signal
import sys
from decimal import Decimal
from pathlib import Path
from typing import Any
from unittest.mock import AsyncMock, MagicMock

from ..base import BaseValidator
from ..models import FileInfo, IssueSeverity, ValidationIssue, ValidationResult


class CodeExecutionValidator(BaseValidator):
    """Executes Python code examples to catch runtime errors."""

    def __init__(self) -> None:
        super().__init__(name="code_execution", description="Executes Python code examples to verify they run correctly")

    def supports_file(self, file_path: Path) -> bool:
        """Support markdown files."""
        return file_path.suffix.lower() in {".md", ".markdown"}

    def _is_file_included(self, file_path: Path, include_list: list[str]) -> bool:
        """Check if file is in the include list for execution.

        Args:
            file_path: Path to the file being validated
            include_list: List of file patterns to include for execution

        Returns:
            True if file is included or include list is empty (all files included)
        """
        # Empty include list means all files are included (original behavior)
        if not include_list:
            return True

        # Convert to string and normalize path separators
        file_str = str(file_path).replace("\\", "/")

        # Check against each include pattern
        for pattern in include_list:
            pattern_normalized = pattern.replace("\\", "/")
            # Support both exact match and glob-style patterns
            if file_str.endswith(pattern_normalized) or pattern_normalized in file_str:
                return True

        return False

    def validate_file(self, file_info: FileInfo, content: str, options: dict[str, Any]) -> ValidationResult:
        """Execute code blocks in file content."""
        issues: list[ValidationIssue] = []

        # Check if file is included for execution
        include_list = options.get("include_files", [])
        is_included = self._is_file_included(file_info.path, include_list)

        # If include list exists and file is not included, skip execution
        if include_list and not is_included:
            return ValidationResult(validator_name=self.name, file_path=file_info.path, passed=True, issues=[], metadata={"skipped": True})

        lines = content.split("\n")

        # Track code block state
        in_code_block = False
        code_block_lines: list[str] = []
        code_block_start = 0
        code_block_language = ""

        # Create a shared namespace for code execution across all blocks in this file
        execution_namespace: dict[str, Any] = {}

        # Set up mocking if enabled
        if options.get("mock_api_calls", True):
            execution_namespace.update(self._create_mocks())

        for line_num, line in enumerate(lines, 1):
            stripped = line.strip()

            if stripped.startswith("```"):
                if not in_code_block:
                    # Starting a code block
                    in_code_block = True
                    code_block_start = line_num
                    code_block_lines = []

                    # Extract language specification
                    code_block_language = stripped[3:].strip().lower()
                else:
                    # Ending a code block
                    in_code_block = False

                    # Execute the code block if it's Python
                    if code_block_language in ["python", "py", ""] and code_block_lines:
                        block_issues = self._execute_python_code(
                            code_block_lines,
                            code_block_start + 1,  # +1 because code starts after ```
                            file_info.path,
                            execution_namespace,
                        )
                        issues.extend(block_issues)

                    # Reset for next block
                    code_block_lines = []
                    code_block_language = ""
            elif in_code_block:
                # Collect code block content
                code_block_lines.append(line)

        return ValidationResult(validator_name=self.name, file_path=file_info.path, passed=len(issues) == 0, issues=issues)

    def _is_placeholder_code(self, code: str) -> bool:
        """Check if code is clearly a placeholder/example that shouldn't be executed."""
        placeholder_patterns = [
            r"your[-_]token[-_]here",
            r"your[-_]api[-_]key",
            r"your[-_]account[-_]id",
            r"your[-_]practice[-_]token",
            r"your[-_]api[-_]token",
            r"replace[-_]with[-_]your",
            r"<[^>]+>",  # HTML-like placeholders
            r"\.\.\.",  # Ellipsis indicating continuation
            r"# TODO",
            r"# FIXME",
            r"# Your code here",
            r"pass\s*#.*example",
            r"# File: \.env",  # .env file examples
            r"FIVETWENTY_OANDA_TOKEN=your-",  # Environment variable examples
        ]

        code_lower = code.lower()
        return any(re.search(pattern, code_lower) for pattern in placeholder_patterns)

    def _execute_python_code(
        self,
        code_lines: list[str],
        start_line: int,
        file_path: Path,
        execution_namespace: dict[str, Any],
    ) -> list[ValidationIssue]:
        """Execute Python code and catch runtime errors."""
        issues: list[ValidationIssue] = []

        if not code_lines or all(not line.strip() for line in code_lines):
            return issues

        code = "\n".join(code_lines)

        # Skip code blocks that are clearly examples/placeholders
        if self._is_placeholder_code(code):
            return issues

        # Set resource limits (256MB memory, 5 seconds CPU time)
        old_limits = self._set_resource_limits()

        # Capture stdout/stderr
        old_stdout = sys.stdout
        old_stderr = sys.stderr
        sys.stdout = io.StringIO()
        sys.stderr = io.StringIO()

        # Set timeout alarm
        def timeout_handler(_signum: int, _frame: Any) -> None:
            raise TimeoutError("Code execution exceeded 5 second timeout")

        old_alarm_handler = signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(5)  # 5 second timeout

        # Store original sys.modules state for fivetwenty (to restore later)
        original_fivetwenty = sys.modules.get("fivetwenty")

        try:
            # Add security restrictions to namespace
            restricted_namespace = self._create_restricted_namespace(execution_namespace)

            # Execute the code in the restricted namespace
            exec(code, restricted_namespace)

            # Update the original namespace with new definitions (but not builtins)
            for key, value in restricted_namespace.items():
                if not key.startswith("__") and key not in execution_namespace.get("__builtins__", {}):
                    execution_namespace[key] = value

        except TimeoutError:
            issues.append(
                ValidationIssue(
                    message="Execution timeout: Code exceeded 5 second limit",
                    file_path=file_path,
                    line=start_line,
                    severity=IssueSeverity.ERROR,
                    rule_id="code_timeout",
                    context=code_lines[0] if code_lines else "",
                    suggestion="Reduce complexity or remove infinite loops",
                )
            )
        except MemoryError:
            issues.append(
                ValidationIssue(
                    message="Memory limit exceeded: Code used more than 256MB",
                    file_path=file_path,
                    line=start_line,
                    severity=IssueSeverity.ERROR,
                    rule_id="code_memory_limit",
                    context=code_lines[0] if code_lines else "",
                    suggestion="Reduce memory usage in code example",
                )
            )
        except Exception as e:
            # Extract line number from traceback if possible
            import traceback

            tb = traceback.extract_tb(e.__traceback__)
            error_line = start_line
            if tb:
                # Find the frame that corresponds to our code
                for frame in tb:
                    if frame.filename == "<string>" and frame.lineno is not None:
                        error_line = start_line + frame.lineno - 1
                        break

            # Get context line
            context = ""
            relative_line = error_line - start_line
            if 0 <= relative_line < len(code_lines):
                context = code_lines[relative_line]

            issues.append(
                ValidationIssue(
                    message=f"Runtime error: {type(e).__name__}: {e}",
                    file_path=file_path,
                    line=error_line,
                    severity=IssueSeverity.ERROR,
                    rule_id="code_runtime_error",
                    context=context,
                    suggestion="Fix the runtime error or check if code depends on previous examples",
                )
            )
        finally:
            # Cancel timeout alarm
            signal.alarm(0)
            signal.signal(signal.SIGALRM, old_alarm_handler)

            # Restore stdout/stderr
            sys.stdout = old_stdout
            sys.stderr = old_stderr

            # Restore resource limits
            self._restore_resource_limits(old_limits)

            # Restore sys.modules state for fivetwenty and its submodules
            if original_fivetwenty is not None:
                sys.modules["fivetwenty"] = original_fivetwenty
            elif "fivetwenty" in sys.modules:
                del sys.modules["fivetwenty"]

            # Clean up all fivetwenty submodules
            submodules_to_remove = [key for key in sys.modules if key.startswith("fivetwenty.")]
            for submodule in submodules_to_remove:
                del sys.modules[submodule]

        return issues

    def _set_resource_limits(self) -> tuple[tuple[int, int], tuple[int, int]]:
        """Set resource limits for code execution.

        Returns:
            Tuple of (old_memory_limit, old_cpu_limit) for restoration
        """
        try:
            # Get current limits
            old_memory = resource.getrlimit(resource.RLIMIT_AS)
            old_cpu = resource.getrlimit(resource.RLIMIT_CPU)

            # Set memory limit to 256MB
            resource.setrlimit(resource.RLIMIT_AS, (256 * 1024 * 1024, 256 * 1024 * 1024))

            # Set CPU time limit to 5 seconds
            resource.setrlimit(resource.RLIMIT_CPU, (5, 5))

            return (old_memory, old_cpu)
        except (OSError, ValueError):
            # Resource limits not supported on this platform (e.g., Windows)
            return ((0, 0), (0, 0))

    def _restore_resource_limits(self, old_limits: tuple[tuple[int, int], tuple[int, int]]) -> None:
        """Restore previous resource limits."""
        old_memory, old_cpu = old_limits
        if old_memory != (0, 0):
            try:
                resource.setrlimit(resource.RLIMIT_AS, old_memory)
                resource.setrlimit(resource.RLIMIT_CPU, old_cpu)
            except (OSError, ValueError):
                pass

    def _create_restricted_namespace(self, base_namespace: dict[str, Any]) -> dict[str, Any]:
        """Create a restricted namespace with security limitations.

        Restricts access to:
        - File I/O (open, file operations)
        - Network operations (socket, urllib) via controlled import
        - Subprocess execution
        - Dangerous builtins (eval, exec, compile)
        - Allows safe imports (stdlib, fivetwenty, dotenv, etc.)
        """
        # Start with the base namespace
        restricted = base_namespace.copy()

        # Create a mocked fivetwenty module to inject into sys.modules
        # This ensures that imports of fivetwenty use mocks instead of the real module
        mocked_fivetwenty = MagicMock()

        # Set __path__ to make it look like a package (enables submodule imports)
        mocked_fivetwenty.__path__ = []
        mocked_fivetwenty.__package__ = "fivetwenty"
        mocked_fivetwenty.__name__ = "fivetwenty"
        mocked_fivetwenty.__version__ = "0.0.0-mock"

        # Get the mocked AsyncClient and Client from base_namespace
        if "AsyncClient" in base_namespace:
            mocked_fivetwenty.AsyncClient = base_namespace["AsyncClient"]
        if "Client" in base_namespace:
            mocked_fivetwenty.Client = base_namespace["Client"]
        if "AccountConfig" in base_namespace:
            mocked_fivetwenty.AccountConfig = base_namespace["AccountConfig"]
        if "AccountConfigLoader" in base_namespace:
            mocked_fivetwenty.AccountConfigLoader = base_namespace["AccountConfigLoader"]
        if "Environment" in base_namespace:
            mocked_fivetwenty.Environment = base_namespace["Environment"]

        # Create mock exception that inherits from BaseException for proper exception handling
        class MockFiveTwentyError(Exception):
            """Mock FiveTwentyError for exception handling."""

        # Create submodules that return MagicMocks for any attribute access
        # This allows imports like: from fivetwenty.models import InstrumentName
        mocked_submodules = ["models", "exceptions", "endpoints", "endpoints.orders", "endpoints.trades", "endpoints.accounts", "endpoints.pricing", "endpoints.positions", "endpoints.transactions", "endpoints.instruments"]

        for submodule_name in mocked_submodules:
            full_name = f"fivetwenty.{submodule_name}"
            mock_submodule = MagicMock()
            mock_submodule.__name__ = full_name
            mock_submodule.__package__ = full_name.rsplit(".", 1)[0] if "." in submodule_name else "fivetwenty"

            # Add FiveTwentyError to exceptions submodule
            if submodule_name == "exceptions":
                mock_submodule.FiveTwentyError = MockFiveTwentyError

            sys.modules[full_name] = mock_submodule

            # Set the submodule on the parent
            parts = submodule_name.split(".")
            parent = mocked_fivetwenty
            for part in parts[:-1]:
                if not hasattr(parent, part):
                    setattr(parent, part, MagicMock())
                parent = getattr(parent, part)
            setattr(parent, parts[-1], mock_submodule)

        # Inject mocked module into sys.modules (cleanup happens in _execute_python_code finally block)
        sys.modules["fivetwenty"] = mocked_fivetwenty

        # Create a safe __import__ that allows standard library and safe packages
        def safe_import(name: str, *args: Any, **kwargs: Any) -> Any:
            """Allow safe imports, block dangerous ones."""
            dangerous_modules = {"subprocess", "socket", "urllib", "urllib3", "requests", "httpx"}

            if name.split(".")[0] in dangerous_modules:
                raise ImportError(f"Importing {name} is not allowed in documentation code examples")

            # Use the real __import__ for safe modules
            import builtins

            return builtins.__import__(name, *args, **kwargs)

        # Create restricted builtins
        import builtins

        safe_builtins = {
            # Keep safe builtins
            "abs": abs,
            "all": all,
            "any": any,
            "bool": bool,
            "dict": dict,
            "enumerate": enumerate,
            "filter": filter,
            "float": float,
            "int": int,
            "len": len,
            "list": list,
            "map": map,
            "max": max,
            "min": min,
            "print": print,
            "range": range,
            "reversed": reversed,
            "set": set,
            "sorted": sorted,
            "str": str,
            "sum": sum,
            "tuple": tuple,
            "zip": zip,
            "hasattr": hasattr,
            "getattr": getattr,
            "isinstance": isinstance,
            "repr": repr,
            "type": type,
            # Exceptions
            "Exception": Exception,
            "ValueError": ValueError,
            "TypeError": TypeError,
            "KeyError": KeyError,
            "AttributeError": AttributeError,
            "ImportError": ImportError,
            # Decimal for financial calculations
            "Decimal": Decimal,
            # Safe controlled import
            "__import__": safe_import,
            # Special builtins needed for class definitions
            "__build_class__": builtins.__build_class__,
            "__name__": builtins.__name__,
        }

        # Block dangerous operations
        def blocked_function(*_args: Any, **_kwargs: Any) -> None:
            raise PermissionError("This operation is not allowed in documentation code examples")

        dangerous = {
            "open": blocked_function,
            "exec": blocked_function,
            "eval": blocked_function,
            "compile": blocked_function,
        }

        restricted["__builtins__"] = {**safe_builtins, **dangerous}

        # Add common dunder variables that code expects
        if "__name__" not in restricted:
            restricted["__name__"] = "__main__"
        if "__file__" not in restricted:
            restricted["__file__"] = "<documentation>"

        return restricted

    def _create_mocks(self) -> dict[str, Any]:
        """Create mock objects for FiveTwenty API to prevent real API calls."""

        # Create realistic mock account with proper numeric field support
        class MockAccount:
            """Mock account that supports Decimal conversion and both camelCase/snake_case.

            Note: Intentionally supports both naming conventions to match OANDA API (camelCase)
            and Python conventions (snake_case) used in different parts of the codebase.
            """

            id = "001-001-0000000-001"
            alias = "Primary"
            currency = "USD"
            balance = Decimal("100000.00")
            # Support both camelCase (API) and snake_case (Python) naming
            unrealizedPL = Decimal("0.00")  # noqa: N815
            unrealized_pl = Decimal("0.00")
            pl = Decimal("0.00")
            marginUsed = Decimal("0.00")  # noqa: N815
            margin_used = Decimal("0.00")
            marginAvailable = Decimal("100000.00")  # noqa: N815
            margin_available = Decimal("100000.00")
            openTradeCount = 0  # noqa: N815
            open_trade_count = 0
            openPositionCount = 0  # noqa: N815
            open_position_count = 0
            pendingOrderCount = 0  # noqa: N815
            pending_order_count = 0
            NAV = Decimal("100000.00")
            nav = Decimal("100000.00")
            marginRate = Decimal("0.02")  # noqa: N815
            margin_rate = Decimal("0.02")
            marginCallMarginUsed = Decimal("0.00")  # noqa: N815
            margin_call_margin_used = Decimal("0.00")
            withdrawalLimit = Decimal("100000.00")  # noqa: N815
            withdrawal_limit = Decimal("100000.00")
            positionValue = Decimal("0.00")  # noqa: N815
            position_value = Decimal("0.00")

            def __getitem__(self, key):
                """Support dict-like access."""
                return getattr(self, key, None)

        mock_account = MockAccount()

        # Create realistic mock price data with proper object structure
        # Create bid/ask objects
        mock_bid = MagicMock()
        mock_bid.price = Decimal("1.12345")
        mock_bid.liquidity = 1000000

        mock_ask = MagicMock()
        mock_ask.price = Decimal("1.12350")
        mock_ask.liquidity = 1000000

        # Create ClientPrice object
        mock_price = MagicMock()
        mock_price.instrument = "EUR_USD"
        mock_price.bids = [mock_bid]
        mock_price.asks = [mock_ask]
        mock_price.closeoutBid = Decimal("1.12340")
        mock_price.closeoutAsk = Decimal("1.12355")
        mock_price.time = "2024-01-01T00:00:00.000000000Z"
        # Support indexing for prices[0]
        mock_price.__getitem__ = lambda _self, key: mock_price if key == 0 else None

        # Create realistic mock order response
        mock_order_response = MagicMock()
        mock_order_response.order_fill_transaction = MagicMock()
        mock_order_response.order_fill_transaction.id = "1234"
        mock_order_response.order_fill_transaction.pl = Decimal("0.00")
        mock_order_response.order_fill_transaction.units = "1000"
        mock_order_response.order_fill_transaction.price = Decimal("1.12345")
        mock_order_response.order_fill_transaction.account_balance = Decimal("100000.00")

        # Mock AsyncClient
        mock_async_client = MagicMock()
        mock_async_client.__aenter__ = AsyncMock(return_value=mock_async_client)
        mock_async_client.__aexit__ = AsyncMock(return_value=None)
        mock_async_client.account_id = "001-001-0000000-001"
        mock_async_client.config = MagicMock()
        mock_async_client.config.summary = MagicMock(return_value="mock_config (practice)")

        # Mock all async endpoint methods explicitly
        # This is necessary because MagicMock doesn't work with 'await' -
        # we need AsyncMock for any method that will be awaited

        mock_async_client.accounts = MagicMock()
        # get_accounts returns list directly, not wrapped in dict
        mock_async_client.accounts.get_accounts = AsyncMock(return_value=[mock_account])
        # get_account and get_account_summary return TypedDict with "account" key
        mock_async_client.accounts.get_account = AsyncMock(return_value={"account": mock_account, "lastTransactionID": "12345"})
        mock_async_client.accounts.get_account_summary = AsyncMock(return_value={"account": mock_account, "lastTransactionID": "12345"})
        mock_async_client.accounts.get_account_instruments = AsyncMock(return_value={"instruments": []})
        mock_async_client.accounts.patch_account_configuration = AsyncMock(return_value={})

        mock_async_client.orders = MagicMock()
        mock_async_client.orders.post_market_order = AsyncMock(return_value=mock_order_response)
        mock_async_client.orders.post_limit_order = AsyncMock(return_value=mock_order_response)
        mock_async_client.orders.post_stop_order = AsyncMock(return_value=mock_order_response)
        mock_async_client.orders.post_market_if_touched_order = AsyncMock(return_value=mock_order_response)
        mock_async_client.orders.post_order = AsyncMock(return_value=mock_order_response)
        mock_async_client.orders.get_orders = AsyncMock(return_value={"orders": [], "lastTransactionID": "12345"})
        mock_async_client.orders.get_pending_orders = AsyncMock(return_value={"orders": [], "lastTransactionID": "12345"})
        mock_async_client.orders.get_order = AsyncMock(return_value={"order": MagicMock(), "lastTransactionID": "12345"})
        mock_async_client.orders.put_order = AsyncMock(return_value=mock_order_response)
        mock_async_client.orders.put_order_client_extensions = AsyncMock(return_value={"lastTransactionID": "12345"})
        mock_async_client.orders.cancel_order = AsyncMock(return_value={"lastTransactionID": "12345"})

        mock_async_client.trades = MagicMock()
        mock_async_client.trades.get_trades = AsyncMock(return_value={"trades": []})
        mock_async_client.trades.get_open_trades = AsyncMock(return_value={"trades": []})
        mock_async_client.trades.get_trade = AsyncMock(return_value={"trade": MagicMock()})
        mock_async_client.trades.close_trade = AsyncMock(return_value={})
        mock_async_client.trades.put_trade_client_extensions = AsyncMock(return_value={})
        mock_async_client.trades.put_trade_orders = AsyncMock(return_value={})

        mock_async_client.pricing = MagicMock()
        mock_async_client.pricing.get_pricing = AsyncMock(return_value={"prices": [mock_price], "time": "2024-01-01T00:00:00Z"})
        mock_async_client.pricing.get_pricing_stream = AsyncMock(return_value=AsyncMock())
        mock_async_client.pricing.get_account_instrument_candles = AsyncMock(return_value={"candles": [], "instrument": "EUR_USD", "granularity": "H1"})
        mock_async_client.pricing.get_latest_candles = AsyncMock(return_value={"latestCandles": []})
        mock_async_client.pricing.stream_pricing_with_retries = AsyncMock(return_value=AsyncMock())
        mock_async_client.pricing.get_candles = AsyncMock(return_value={"candles": []})

        mock_async_client.positions = MagicMock()
        mock_async_client.positions.get_positions = AsyncMock(return_value={"positions": []})
        mock_async_client.positions.get_open_positions = AsyncMock(return_value={"positions": []})
        mock_async_client.positions.get_position = AsyncMock(return_value={"position": MagicMock()})
        mock_async_client.positions.close_position = AsyncMock(return_value={})

        mock_async_client.instruments = MagicMock()
        mock_async_client.instruments.get_instrument_candles = AsyncMock(return_value={"candles": []})

        mock_async_client.transactions = MagicMock()
        mock_async_client.transactions.get_transactions = AsyncMock(return_value={"transactions": [], "lastTransactionID": "12345"})
        mock_async_client.transactions.get_transaction = AsyncMock(return_value={"transaction": MagicMock(), "lastTransactionID": "12345"})
        mock_async_client.transactions.get_recent_transactions = AsyncMock(return_value={"transactions": [], "lastTransactionID": "12345"})

        # Mock Client (sync version)
        mock_client = MagicMock()
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=None)
        mock_client.account_id = "001-001-0000000-001"
        mock_client.accounts = MagicMock()
        mock_client.accounts.get_accounts = MagicMock(return_value=[mock_account])
        mock_client.accounts.get_account = MagicMock(return_value=mock_account)

        # Mock AccountConfig
        mock_config = MagicMock()
        mock_config.token = "***"
        mock_config.account_id = "***"
        mock_config.environment = "practice"
        mock_config.alias = "demo_trading"
        mock_config.summary = MagicMock(return_value="demo_trading (practice)")

        # Mock AccountConfigLoader
        mock_loader = MagicMock()
        mock_loader.from_env_prefix = MagicMock(return_value=mock_config)

        # Mock Environment
        mock_env = MagicMock()
        mock_env.PRACTICE = MagicMock()
        mock_env.PRACTICE.base_url = "https://api-fxpractice.oanda.com/v3"
        mock_env.LIVE = MagicMock()
        mock_env.LIVE.base_url = "https://api-fxtrade.oanda.com/v3"

        return {
            "AsyncClient": MagicMock(return_value=mock_async_client),
            "Client": MagicMock(return_value=mock_client),
            "AccountConfig": MagicMock(return_value=mock_config),
            "AccountConfigLoader": mock_loader,
            "Environment": mock_env,
            "asyncio": asyncio,  # Provide real asyncio module
            "Decimal": Decimal,  # Provide real Decimal class
        }

    def get_file_patterns(self) -> list[str]:
        """Get patterns for files this validator handles."""
        return ["**/*.md", "**/*.markdown"]
