# FiveTwenty Documentation Validation System

A comprehensive validation framework for the FiveTwenty SDK documentation, ensuring high-quality, accurate, and maintainable documentation with automated quality checks.

## 🚀 Quick Start

```bash
# Install dependencies
uv sync

# Run validation on all documentation
uv run python -m docs_validation.src.cli validate

# Run fast validation (core validators only)
uv run python -m docs_validation.src.cli validate --config config/validation-fast.yml

# Validate specific files
uv run python -m docs_validation.src.cli validate --files "docs/tutorials/getting-started/authentication.md"

# Run validation in parallel for better performance
uv run python -m docs_validation.src.cli validate --parallel --max-workers 8
```

## 📋 Features

### 🔍 Comprehensive Validation

- **Python Syntax Validation** - Ensures all Python code blocks are syntactically correct
- **Code Linting** - Enforces Python best practices using Ruff linter with comprehensive rule set
- **Type Checking** - Validates type safety using MyPy in strict mode
- **Cross-Reference Validation** - Checks internal documentation links and references
- **Security Scanning** - Detects exposed credentials and security vulnerabilities
- **Financial Precision** - Ensures proper Decimal usage for monetary values
- **Markdown Syntax** - Validates markdown structure and formatting
- **SDK Method Validation** - Verifies SDK usage patterns and method calls

### 🎯 Smart Code Analysis

- **Automatic Import Enhancement** - Adds common FiveTwenty imports to code examples
- **Placeholder Detection** - Automatically skips validation for placeholder code
- **Fragment Marking System** - HTML comment-based control over validation behavior
- **Context-Aware Suggestions** - Provides specific fix recommendations for each issue

### 📊 Rich Reporting

- **Detailed Markdown Reports** - Comprehensive analysis with actionable insights
- **Real-time Progress** - Visual progress indicators during validation
- **Quality Metrics** - Success rates, error counts, and performance statistics
- **Issue Classification** - Categorized by severity (errors, warnings, info)

## 🛠 Installation & Setup

### Prerequisites

- Python 3.11+
- uv package manager
- FiveTwenty SDK development environment

### Install Dependencies

```bash
# From the docs_validation directory
uv sync

# Install additional development tools (optional)
uv sync --extra dev
```

## 📚 Usage Guide

### Basic Commands

```bash
# Run all validators on entire documentation
uv run python -m docs_validation.src.cli validate

# Use specific configuration
uv run python -m docs_validation.src.cli validate --config config/validation-complete.yml

# Validate specific files or directories
uv run python -m docs_validation.src.cli validate --files "docs/tutorials/**/*.md"

# Run in sequential mode (for debugging)
uv run python -m docs_validation.src.cli validate --sequential

# List available validators
uv run python -m docs_validation.src.cli list-validators
```

### Configuration Files

The system supports multiple configuration profiles:

- **`config/validation-fast.yml`** - Core validators only, faster execution
- **`config/validation-complete.yml`** - All validators, comprehensive analysis
- **`config/validation.yml`** - Default balanced configuration

### Fragment Marking System

Control validation behavior with HTML comments:

```markdown
<!-- validation: skip -->
```python
# This code block will be skipped entirely
placeholder_code = "your-api-token"
```

<!-- validation: skip-linting -->
```python
# Only skip linting, allow type checking
from fivetwenty import AsyncClient  # Import in function (bad style but valid)
```

See [FRAGMENT_MARKING.md](FRAGMENT_MARKING.md) for complete documentation.

## 🏗 Architecture

### Core Components

```
docs_validation/
├── src/
│   ├── cli.py              # Command-line interface
│   ├── engine.py           # Validation orchestration
│   ├── config.py           # Configuration management
│   ├── base.py             # Validator registry and base classes
│   ├── models.py           # Data models and schemas
│   ├── reporters/          # Report generation
│   └── validators/         # Individual validator implementations
├── config/                 # Validation configuration files
├── reports/                # Generated validation reports
└── tests/                  # Comprehensive test suite
```

### Validator Architecture

Each validator inherits from `BaseValidator` and implements:

- `supports_file()` - File type filtering
- `validate_file()` - Core validation logic
- `get_file_patterns()` - File discovery patterns

### Parallel Processing

The system supports parallel validation with:

- Configurable worker threads
- Thread-safe validator implementations
- Efficient resource utilization
- Progress tracking across workers

## 🔧 Configuration

### Validation Configuration

```yaml
# config/validation.yml
validators:
  code_linting:
    enabled: true
    options:
      severity_filter: 'warning'
      ignore_rules: ['E501']  # Line length

  code_typing:
    enabled: true
    options:
      strict_mode: false
      enhanced_imports: true

discovery:
  include_patterns:
    - "docs/**/*.md"
    - "docs/**/*.markdown"
  exclude_patterns:
    - "docs/archive/**"
    - "**/.archive/**"

execution:
  parallel_execution: true
  max_workers: 4
  timeout_seconds: 300

reporting:
  output_format: "markdown"
  include_context: true
  detailed_suggestions: true
```

### Environment Variables

```bash
# Optional: Customize validation behavior
export DOCS_VALIDATION_CONFIG="path/to/custom/config.yml"
export DOCS_VALIDATION_PARALLEL="true"
export DOCS_VALIDATION_MAX_WORKERS="8"
```

## 📊 Validation Reports

### Report Structure

Generated reports include:

1. **Executive Summary** - Overall status and key metrics
2. **Validator Performance** - Per-validator statistics and timing
3. **File-Level Analysis** - Issues by file with rankings
4. **Rule Violation Analysis** - Most common issues and patterns
5. **Detailed Issue Analysis** - Line-by-line issue breakdown
6. **Action Plan** - Prioritized recommendations for improvement

### Sample Report Output

```
📊 Validation Results: ✅ PASSED | 66 files | 95.2% success rate | 23 issues

┏━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━┳━━━━━━━━━┳━━━━━━━━┳━━━━━━━━┳━━━━━━━━━━┓
┃ Validator           ┃ Files ┃ Success ┃ Issues ┃ Errors ┃ Duration ┃
┡━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━╇━━━━━━━━━╇━━━━━━━━╇━━━━━━━━╇━━━━━━━━━━┩
│ code_linting        │    66 │   92.4% │     18 │     18 │   3.2s   │
│ code_typing         │    66 │   97.0% │      4 │      4 │  12.8s   │
│ cross_references    │    66 │  100.0% │      0 │      0 │   0.2s   │
│ security            │    66 │   98.5% │      1 │      1 │   0.8s   │
└─────────────────────┴───────┴─────────┴────────┴────────┴──────────┘
```

## 🧪 Testing

### Run Test Suite

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=src

# Run specific test categories
uv run pytest tests/unit/
uv run pytest tests/integration/

# Run tests in parallel
uv run pytest -n auto
```

### Test Structure

```
tests/
├── unit/
│   ├── test_validators/     # Individual validator tests
│   ├── test_engine.py       # Validation engine tests
│   └── test_config.py       # Configuration tests
├── integration/
│   ├── test_cli.py          # CLI integration tests
│   └── test_full_validation.py  # End-to-end tests
└── fixtures/
    ├── sample_docs/         # Test documentation files
    └── configs/             # Test configurations
```

## 🚀 Performance

### Optimization Features

- **Parallel Processing** - Multi-threaded validation with configurable workers
- **Smart Caching** - Validator results caching for repeated runs
- **File Filtering** - Pattern-based inclusion/exclusion for targeted validation
- **Incremental Validation** - Validate only changed files in CI/CD pipelines
- **Fast Mode** - Core validators only for rapid feedback

### Performance Metrics

Typical performance on FiveTwenty documentation (66 files):

- **Full Validation** - ~25 seconds (all validators)
- **Fast Validation** - ~8 seconds (core validators only)
- **Parallel Speedup** - 3-4x improvement with 4-8 workers
- **Memory Usage** - <200MB peak usage during validation

## 🔌 Extensibility

### Adding Custom Validators

```python
from src.base import BaseValidator
from src.models import ValidationResult, ValidationIssue

class CustomValidator(BaseValidator):
    def __init__(self):
        super().__init__(
            name="custom_validator",
            description="Custom validation logic"
        )

    def supports_file(self, file_path: Path) -> bool:
        return file_path.suffix.lower() in {".md", ".markdown"}

    def validate_file(self, file_info: FileInfo, content: str, options: dict) -> ValidationResult:
        # Implement validation logic
        issues = []
        # ... validation code ...
        return ValidationResult(
            validator_name=self.name,
            file_path=file_info.path,
            passed=len(issues) == 0,
            issues=issues
        )

# Register the validator
from src.base import registry
registry.register(CustomValidator())
```

### Custom Reporter

```python
from src.reporters.base import BaseReporter

class CustomReporter(BaseReporter):
    def generate_report(self, summary, all_issues, output_path, **kwargs):
        # Implement custom report generation
        pass
```

## 🐛 Troubleshooting

### Common Issues

**Validation timeouts:**
```bash
# Increase timeout or reduce workers
uv run python -m docs_validation.src.cli validate --max-workers 2
```

**Import errors in code blocks:**
```bash
# Check if FiveTwenty SDK is properly installed
pip show fivetwenty
```

**Permission errors:**
```bash
# Ensure write permissions for reports directory
chmod 755 reports/
```

### Debug Mode

```bash
# Run with verbose output
uv run python -m docs_validation.src.cli validate --sequential --max-workers 1

# Validate single file for debugging
uv run python -m docs_validation.src.cli validate --files "problematic_file.md"
```

### Configuration Issues

```bash
# Validate configuration file
uv run python -c "from src.config import ValidationConfig; ValidationConfig.load_from_file('config/validation.yml')"

# Use default configuration
uv run python -m docs_validation.src.cli validate  # Uses built-in defaults
```

## 🤝 Contributing

### Development Setup

```bash
# Clone and setup
git clone <repository>
cd docs_validation
uv sync --extra dev

# Install pre-commit hooks
pre-commit install

# Run tests
uv run pytest

# Format code
uv run ruff format .
uv run ruff check --fix .
```

### Adding New Validators

1. Create validator class in `src/validators/`
2. Register in `src/validators/__init__.py`
3. Add tests in `tests/unit/test_validators/`
4. Update configuration schema if needed
5. Add documentation

### Code Style

- Use Ruff for formatting and linting
- Follow type hints with MyPy
- Maintain comprehensive test coverage
- Document public APIs with docstrings

## 📜 License

This validation system is part of the FiveTwenty SDK project. See the main project license for details.

## 🆘 Support

- **Documentation Issues**: Create GitHub issue with validation report
- **Feature Requests**: Use GitHub discussions
- **Bug Reports**: Include configuration file and error output
- **Performance Issues**: Include timing information and system specs

---

Built with ❤️ for the FiveTwenty SDK documentation team.