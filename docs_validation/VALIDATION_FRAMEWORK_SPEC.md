# FiveTwenty Documentation Validation Framework Specification

## Executive Summary

This specification defines requirements for a ground-up rewrite of the FiveTwenty documentation validation framework. The current system validates 139 files across docs, tutorials, and code examples but suffers from architectural debt, performance issues, and maintainability problems.

**Primary Goals:**
- **Developer Velocity**: Fast feedback cycles (< 2 seconds for typical runs)
- **Quality Assurance**: Zero false positives, actionable error messages
- **Financial Safety**: Mandatory validation for trading documentation
- **CI/CD Integration**: Reliable quality gates for release processes

**Success Metrics:**
- 10x faster execution than current system
- Zero configuration system bugs
- 100% test coverage for all validators
- Sub-second feedback for incremental validation

## Architecture

### Core Components

```
docs_validation/
├── validation/
│   ├── cli/                    # Command-line interface
│   │   ├── main.py            # Primary CLI entry point
│   │   └── advanced.py        # Advanced CLI features
│   ├── config/                # Configuration management
│   │   ├── loader.py          # Profile and config loading
│   │   ├── profiles.py        # Built-in profiles
│   │   └── quality_gates.py   # Quality gate definitions
│   ├── core/                  # Core framework
│   │   ├── config.py          # Global configuration (legacy)
│   │   ├── context.py         # Validation context
│   │   ├── results.py         # Result models
│   │   ├── executor.py        # Validation execution
│   │   └── file_finder.py     # File discovery
│   ├── checks/                # Validation checks
│   │   ├── base.py            # Base check classes
│   │   ├── content/           # Content validation
│   │   ├── code/              # Code validation
│   │   ├── links/             # Link validation
│   │   ├── prose/             # Prose validation
│   │   ├── security/          # Security scanning
│   │   └── syntax/            # Syntax validation
│   ├── validators/            # Validator registry
│   │   └── registry.py        # Check registration and execution
│   ├── reporting/             # Report generation
│   │   ├── formatters.py      # Output formatters
│   │   ├── aggregators.py     # Data aggregation
│   │   └── exports.py         # Export utilities
│   ├── benchmarks/            # Performance monitoring
│   │   ├── profiler.py        # Performance profiling
│   │   ├── runner.py          # Benchmark execution
│   │   └── reporter.py        # Performance reporting
│   └── utils/                 # Utilities
└── .validation.yml            # Configuration file
```

### Configuration System

#### Profile-Based Configuration

The framework uses a profile-based configuration system defined in `.validation.yml`:

```yaml
default_profile: "fivetwenty"

profiles:
  fivetwenty:
    description: "Comprehensive validation for FiveTwenty documentation"
    file_patterns:
      - "docs/**/*.md"
      - "**/*.py"
      - "*.md"
    exclude_paths:
      - "validation_reports/**"
      - "node_modules/**"
      - ".git/**"
      # ... extensive exclusion list
    parallel_execution: true
    max_workers: 4
    timeout_seconds: 300

    checks:
      financial_precision:
        enabled: true
        options:
          strict_mode: true

      security:
        enabled: true
        options:
          severity_filter: "high"
          exclude_patterns:
            - "example"
            - "demo"
            - "tutorial"

      terminology:
        enabled: false  # Disabled due to bugs

      # ... 14 total validators

    quality_gates:
      max_errors: 5
      max_warnings: 100
      max_issues_per_file: 15
      min_success_rate: 90.0
      required_checks:
        - "security"
        - "financial_precision"
      fail_on_error: true
      fail_on_security_issues: true

    reporting:
      formats:
        - "console"
        - "json"
        - "html"
      output_dir: "validation_reports"
      include_passed: false
      include_file_details: true
      group_by_severity: true
      export_trends: true
```

#### Profile Inheritance

Profiles support inheritance via the `extends` field:

```yaml
profiles:
  release:
    extends: "fivetwenty"
    description: "Strict validation for release candidates"
    quality_gates:
      max_errors: 0
      max_warnings: 20
      min_success_rate: 98.0
```

### Validation Checks

#### Check Categories

1. **Content Validation**
   - Financial precision validation
   - Terminology consistency
   - Cross-reference validation
   - SDK method documentation
   - Educational progression
   - Tutorial structure

2. **Code Validation**
   - Python syntax validation
   - Python style checking
   - Code executability testing

3. **Security Validation**
   - Secret scanning
   - API token detection
   - Credential exposure prevention

4. **Syntax Validation**
   - Markdown syntax checking

5. **Link Validation**
   - Internal link verification
   - External link checking

6. **Prose Validation**
   - Vale integration for writing quality

#### Check Implementation Pattern

All checks inherit from `BaseCheck`:

```python
class BaseCheck(ABC):
    def __init__(self, name: str, description: str, file_patterns: list[str]):
        self.name = name
        self.description = description
        self.file_patterns = file_patterns

    @abstractmethod
    def run(self, context: ValidationContext) -> ValidationResult:
        """Execute the validation check."""
        pass

    def supports_file(self, file_path: Path) -> bool:
        """Check if validator supports the given file."""
        pass

    def get_check_metadata(self) -> dict[str, Any]:
        """Get metadata for optimization."""
        pass
```

#### Current Validators (14 Total)

1. **financial_precision** - Validates monetary values use Decimal, proper precision
2. **financial_terminology** - Checks financial term consistency
3. **terminology** - General terminology validation (buggy, disabled)
4. **security** - Scans for secrets, tokens, credentials
5. **cross_references** - Validates internal documentation links
6. **python_syntax** - Checks Python code syntax
7. **python_style** - Python code style validation
8. **code_executability** - Tests if code examples execute
9. **markdown_syntax** - Markdown syntax validation
10. **sdk_methods** - Validates SDK API documentation
11. **educational_progression** - Checks tutorial learning progression
12. **tutorial_structure** - Validates tutorial organization
13. **link_validation** - Internal/external link checking
14. **prose** - Vale prose quality checking

### Results and Reporting

#### Result Model

```python
class ValidationResult:
    check_name: str
    status: ValidationStatus  # PASSED, FAILED, ERROR, SKIPPED
    issues: list[ValidationIssue]
    files_checked: int
    duration: float
    metadata: dict[str, Any]
```

#### Issue Model

```python
class ValidationIssue:
    message: str
    file_path: str
    line: int | None
    column: int | None
    severity: IssueSeverity  # ERROR, WARNING, INFO, SUGGESTION
    context: str | None
    suggestion: str | None
    rule_id: str | None
```

#### Report Formats

- **Console** - Rich terminal output with colors and tables
- **JSON** - Machine-readable structured data
- **HTML** - Web-based report with interactive features
- **JUnit** - CI/CD integration format

### Quality Gates

Quality gates enforce quality standards:

```python
class QualityGateConfig:
    max_errors: int = 0
    max_warnings: int = 50
    max_issues_per_file: int = 10
    min_success_rate: float = 95.0
    required_checks: list[str] = []
    fail_on_error: bool = True
    fail_on_security_issues: bool = True
```

### CLI Interface

#### Commands

```bash
# List available checks
python -m validation.cli.main list-checks

# Run all enabled checks (default profile)
python -m validation.cli.main run

# Run specific checks
python -m validation.cli.main run terminology security

# Run with specific profile
python -m validation.cli.main run --profile release

# Generate detailed report
python -m validation.cli.main run --report

# Run in parallel/sequential mode
python -m validation.cli.main run --parallel
python -m validation.cli.main run --sequential
```

#### CLI Options

- `--config PATH` - Custom configuration file
- `--project-root PATH` - Project root directory
- `--profile NAME` - Validation profile to use
- `--parallel/--sequential` - Execution mode
- `--report` - Generate detailed report

### Performance and Execution

#### Parallel Execution

- Configurable worker pool (default: 4 workers)
- Thread-based parallelism via `ThreadPoolExecutor`
- Per-check timeout configuration
- Graceful error handling and result aggregation

#### Optimization Features

- File pattern-based filtering
- Extensive exclude pattern support
- Check metadata for optimization hints
- Estimated performance metrics per check

### File Discovery

#### File Patterns

Support for glob patterns:
- `**/*.md` - All markdown files recursively
- `docs/**/*.py` - Python files in docs
- Configurable per profile and per check

#### Exclusion Patterns

Comprehensive exclusion system:
- Cache directories (`**/__pycache__/**`, `**/.mypy_cache/**`)
- Build artifacts (`**/build/**`, `**/dist/**`)
- Version control (`**/.git/**`)
- Node modules (`**/node_modules/**`)
- Validation reports (`validation_reports/**`)

## Requirements Analysis

### Functional Requirements

#### FR1: Financial Safety (Critical)
- **MUST** validate all monetary values use `Decimal` type
- **MUST** detect hardcoded API tokens in examples
- **MUST** validate OANDA API usage patterns
- **MUST** enforce 5-decimal precision for forex prices

#### FR2: Documentation Quality (High)
- **SHOULD** validate internal cross-references
- **SHOULD** check markdown syntax and structure
- **SHOULD** validate code example executability
- **MAY** integrate prose quality checking (Vale)

#### FR3: Developer Experience (High)
- **MUST** provide actionable error messages with suggestions
- **MUST** support incremental validation (changed files only)
- **SHOULD** integrate with IDE/editor workflows
- **SHOULD** provide real-time feedback during development

#### FR4: CI/CD Integration (Medium)
- **MUST** support quality gates with configurable thresholds
- **MUST** generate machine-readable reports (JSON, JUnit)
- **SHOULD** support multiple validation profiles
- **MAY** integrate with GitHub Actions/other CI systems

### Non-Functional Requirements

#### NFR1: Performance
- **Target**: < 2 seconds for typical validation run (139 files)
- **Target**: < 500ms for incremental validation (< 10 changed files)
- **Target**: < 100MB memory usage for largest documentation sets
- **Constraint**: Must support parallel execution

#### NFR2: Reliability
- **Target**: Zero false positives on current documentation
- **Target**: 100% test coverage for validation logic
- **Constraint**: Must handle malformed input gracefully
- **Constraint**: Must provide deterministic results

#### NFR3: Maintainability
- **Target**: New validator implementation in < 50 lines of code
- **Target**: Zero configuration system bugs
- **Constraint**: Single configuration format (YAML)
- **Constraint**: Type-safe configuration validation

### Current Pain Points

#### Critical Issues (Blocking)
1. **False Positives**: Terminology validator flags correct capitalizations
2. **Configuration Bugs**: `enabled: false` was ignored until recent fix
3. **Performance**: 14 validators run unnecessarily, redundant file processing

#### Major Issues (High Impact)
1. **Developer Experience**: No incremental validation, slow feedback
2. **Error Messages**: Generic messages without actionable suggestions
3. **Maintenance Burden**: Complex inheritance logic, dual config systems

#### Minor Issues (Quality of Life)
1. **CLI UX**: Verbose output, unclear progress indication
2. **Documentation**: Limited validator documentation
3. **Testing**: Incomplete test coverage for edge cases

## Dependencies

### Runtime Dependencies

- **pydantic** - Data validation and serialization
- **pathspec** - Path pattern matching
- **rich** - Terminal formatting and output
- **click** - CLI framework
- **PyYAML** - YAML configuration parsing

### Optional Tool Dependencies

- **vale** - Prose quality checking
- **ruff** - Python code formatting/linting
- **mypy** - Python type checking

## Performance Characteristics

### Current Metrics

- **Typical execution time**: 0.1-0.5 seconds for 4 enabled checks
- **File processing rate**: ~300-500 files/second for simple checks
- **Memory usage**: 20-50MB for typical documentation sets
- **Parallelization**: Effective for I/O-bound checks

### Bottlenecks

1. **Regex-heavy validators** - Terminology, cross-references
2. **File I/O** - No caching, repeated reads
3. **External tool integration** - Vale, ruff execution overhead

## Usage Patterns

### Development Workflow

```bash
# Fast development checks
python -m validation.cli.main run --profile dev

# Pre-commit validation
python -m validation.cli.main run --profile fivetwenty

# Release validation
python -m validation.cli.main run --profile release --report
```

### CI/CD Integration

```bash
# CI pipeline
python -m validation.cli.main run --profile ci
exit_code=$?

# Quality gate enforcement
if [ $exit_code -ne 0 ]; then
    echo "Validation failed - blocking deployment"
    exit 1
fi
```

## Design Principles for Rewrite

### Core Principles

1. **Fail Fast, Fail Clear** - Provide immediate, actionable feedback
2. **Zero Configuration** - Work out-of-the-box with sensible defaults
3. **Incremental by Default** - Only validate what changed
4. **Type Safety First** - Leverage Rust/TypeScript for compile-time guarantees
5. **Financial Domain Aware** - Built-in understanding of trading documentation

### Technology Recommendations

#### Option 1: Rust (Recommended)
**Pros:**
- Excellent performance (10-100x faster than Python)
- Memory safety prevents entire classes of bugs
- Rich ecosystem for text processing (regex, tree-sitter)
- Single binary distribution, no dependency hell
- Excellent parallelism support

**Cons:**
- Steeper learning curve for Python developers
- Smaller ecosystem for documentation-specific tools

#### Option 2: Go
**Pros:**
- Simple language, fast compilation
- Great concurrency primitives
- Single binary distribution
- Good performance

**Cons:**
- Less sophisticated type system
- Weaker ecosystem for text processing

#### Option 3: TypeScript/Node.js
**Pros:**
- Familiar to web developers
- Rich ecosystem for markdown/text processing
- Good IDE integration
- Excellent async/await support

**Cons:**
- Runtime overhead compared to compiled languages
- Dependency management complexity
- Memory usage concerns for large document sets

### Proposed Architecture (Rust)

```rust
// Core types
pub struct ValidationEngine {
    config: ValidationConfig,
    validators: ValidatorRegistry,
    cache: FileCache,
}

pub trait Validator {
    fn name(&self) -> &str;
    fn validate(&self, file: &DocumentFile) -> Result<Vec<Issue>, ValidationError>;
    fn supports_file(&self, path: &Path) -> bool;
}

// Domain-specific validators
pub struct FinancialPrecisionValidator;
pub struct SecurityValidator;
pub struct CrossReferenceValidator;

// Fast incremental validation
pub struct FileWatcher {
    engine: ValidationEngine,
    last_run: HashMap<PathBuf, SystemTime>,
}
```

### Minimum Viable Product (MVP)

#### Week 1: Core Infrastructure
- [x] Configuration parsing (YAML)
- [x] File discovery and filtering
- [x] Basic validator trait
- [x] CLI argument parsing

#### Week 2: Essential Validators
- [x] Financial precision validator
- [x] Security scanner (hardcoded tokens)
- [x] Basic markdown syntax checker
- [x] Python code syntax validator

#### Week 3: Developer Experience
- [x] Incremental validation
- [x] Rich terminal output
- [x] Configuration validation
- [x] Basic error suggestions

#### Week 4: CI/CD Integration
- [x] JSON/JUnit report generation
- [x] Quality gates implementation
- [x] Performance benchmarking
- [x] Migration tooling

### Migration Strategy

#### Phase 1: Parallel Development (2-3 weeks)
- Develop new system alongside current one
- Focus on MVP feature set
- Validate performance assumptions
- Test on subset of documentation

#### Phase 2: Feature Parity (2-3 weeks)
- Port remaining validators
- Achieve 100% test coverage
- Performance optimization
- Documentation and tooling

#### Phase 3: Migration (1 week)
- Update CI/CD pipelines
- Developer onboarding
- Monitor for regressions
- Retire old system

#### Phase 4: Enhancement (Ongoing)
- Advanced features (LSP integration, watch mode)
- Performance improvements
- Additional validators as needed

## Success Criteria

### Technical Metrics
- [ ] **Performance**: < 2s for full validation, < 500ms incremental
- [ ] **Reliability**: Zero false positives on current docs
- [ ] **Coverage**: 100% test coverage for validation logic
- [ ] **Memory**: < 100MB for largest documentation sets

### Process Metrics
- [ ] **Developer Adoption**: 100% team usage within 2 weeks
- [ ] **CI/CD Integration**: Zero pipeline failures due to validator bugs
- [ ] **Maintenance**: New validators implemented in < 1 day
- [ ] **Documentation**: Complete API documentation and examples

### Quality Metrics
- [ ] **Error Messages**: 90% of errors include actionable suggestions
- [ ] **Configuration**: Zero configuration-related issues
- [ ] **False Positives**: < 1% false positive rate
- [ ] **Coverage**: Detects 100% of known issue categories

---

This specification prioritizes measurable outcomes, clear technical decisions, and a realistic migration path for the ground-up rewrite of the validation framework.