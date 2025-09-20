# FiveTwenty Documentation Validation System

A comprehensive validation system for ensuring documentation quality, consistency, and accuracy across the FiveTwenty project.

## Overview

This validation system provides automated quality checks for:
- **Link validation**: Internal and external link integrity
- **Code examples**: Syntax validation and execution testing
- **Model coverage**: API model documentation completeness
- **Build process**: MkDocs build verification
- **Security scanning**: Documentation security compliance
- **Terminology consistency**: OANDA API terminology accuracy

## Quick Start

```bash
# List available validators
uv run python docs-tooling/validation/cli.py list

# Run all validators
uv run python docs-tooling/validation/cli.py run

# Run specific validators
uv run python docs-tooling/validation/cli.py run links models

# Run with quality gates and reporting
uv run python docs-tooling/validation/cli.py run --parallel --gates --report
```

## Directory Structure

```
docs-tooling/validation/
├── README.md                    # This documentation
├── cli.py                       # Main CLI interface
├── __init__.py                  # Package initialization
├── core/                        # Core validation framework
│   ├── __init__.py             # Core package init
│   ├── base.py                 # BaseValidator and ValidationResult classes
│   ├── config.py               # Configuration management
│   └── runner.py               # Validation orchestration and reporting
├── validators/                  # Specific validation implementations
│   ├── __init__.py             # Validators package init
│   └── links.py                # Link validation implementation
├── hooks/                       # Pre-commit integration scripts
│   ├── check_docs_links.py     # Pre-commit link checking
│   ├── check_docs_syntax.py    # Pre-commit syntax validation
│   ├── check_terminology.py    # Pre-commit terminology checking
│   └── scan_docs_security.py   # Pre-commit security scanning
└── reports/                     # Generated validation reports (auto-created)
    └── validation_report_*.md   # Timestamped validation reports
```

## CLI Reference

### Commands

**`list`** - List available validators
```bash
uv run python docs-tooling/validation/cli.py list
```

**`run`** - Execute validators
```bash
# Run all validators sequentially
uv run python docs-tooling/validation/cli.py run

# Run specific validators
uv run python docs-tooling/validation/cli.py run links models

# Run with options
uv run python docs-tooling/validation/cli.py run --parallel --gates --report
```

Options:
- `--parallel`: Run validators concurrently for faster execution
- `--gates`: Apply quality gates (fail if thresholds not met)
- `--report`: Generate detailed validation report
- `--workers N`: Number of parallel workers (default: 4)

**`config`** - Configuration management
```bash
# Show current configuration
uv run python docs-tooling/validation/cli.py config --show

# Show quality thresholds
uv run python docs-tooling/validation/cli.py config --thresholds
```

### Available Validators

- **`links`**: Validates internal and external links

## Architecture

### Core Components

**BaseValidator** (`core/base.py`)
- Abstract base class for all validators
- Defines common validation interface and result structure
- Provides file discovery and filtering utilities

**ValidationRunner** (`core/runner.py`)
- Orchestrates multiple validators (sequential/parallel execution)
- Implements quality gates with configurable thresholds
- Generates comprehensive validation reports

**ValidationConfig** (`core/config.py`)
- Manages quality standards and thresholds
- Defines validation schedules and notification settings
- Provides runtime configuration updates

**ValidationResult** (`core/base.py`)
- Standardized result format across all validators
- Includes status, issue counts, timing, and detailed findings
- Supports structured reporting and analysis

### Quality Gates

The system enforces quality standards through configurable thresholds:

**Minimum Thresholds:**
- Model coverage: 85%
- Code example success: 75%
- Link validation: 95%
- Security score: 90%
- Consistency score: 80%
- Version consistency: 95%

**Blocking Thresholds:**
- Critical security issues: 0
- Build failures: 0
- Broken critical links: 0

## Adding New Validators

1. **Create validator class** in `validators/` extending `BaseValidator`
2. **Implement validation logic** in the `validate()` method
3. **Register validator** in `validators/__init__.py`
4. **Add CLI integration** if needed

Example validator structure:
```python
from ..core.base import BaseValidator, ValidationResult

class MyValidator(BaseValidator):
    def validate(self) -> ValidationResult:
        # Implementation here
        return ValidationResult(
            validator_name="my_validator",
            status="passed",  # or "failed", "warning"
            issues_found=0,
            total_checked=100,
            details={},
            timestamp=datetime.now().isoformat(),
            duration_seconds=1.5
        )
```

## Automation & CI Integration

### Pre-commit Hooks

Individual validation hooks are available in `hooks/` for pre-commit integration:
- `check_docs_links.py` - Link validation
- `check_docs_syntax.py` - Syntax checking
- `check_terminology.py` - Terminology validation
- `scan_docs_security.py` - Security scanning

### Scheduled Validation

For automated validation schedules, use cron or CI/CD pipelines with these commands:

**Daily validation** (quick checks):
```bash
# Run link validation with reporting
uv run python docs-tooling/validation/cli.py run links security build --report
```

**Weekly validation** (comprehensive):
```bash
# Run all validators in parallel with quality gates
uv run python docs-tooling/validation/cli.py run --parallel --gates --report
```

**Example cron entries**:
```bash
# Daily validation at 8 AM UTC
0 8 * * * cd /path/to/project && uv run python docs-tooling/validation/cli.py run links --report

# Weekly validation every Monday at 9 AM UTC
0 9 * * 1 cd /path/to/project && uv run python docs-tooling/validation/cli.py run --parallel --gates --report
```

## Configuration

All configuration is embedded in `core/config.py` as Python dictionaries, including:

- **Quality standards**: Minimum and blocking thresholds
- **Validation schedules**: Daily, weekly, monthly, quarterly
- **Notification settings**: Email and Slack integration options

Configuration can be overridden at runtime through the `ValidationConfig` constructor.

## Reporting

The system generates timestamped Markdown reports in `reports/` with:
- Executive summary of validation results
- Detailed findings for each validator
- Quality gates assessment
- Recommendations for addressing issues

Reports are human-readable and version-control friendly for tracking quality trends over time.

**Note**: The `reports/` directory is automatically created when needed and excluded from version control via `.gitignore`.

## Development

### Running Tests
```bash
# Run validation system tests
uv run pytest tests/validation/ -v

# Run specific validator tests
uv run pytest tests/validation/test_links.py -v
```

### Code Quality
```bash
# Format code
uv run ruff format docs-tooling/validation/

# Lint code
uv run ruff check docs-tooling/validation/

# Type check
uv run mypy docs-tooling/validation/
```

The validation system follows the same quality standards as the rest of the FiveTwenty project.