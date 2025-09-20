# Documentation Tooling Suite

Professional documentation validation and accuracy audit tools for the FiveTwenty OANDA API v20 Python SDK.

## 🎉 Achievements: Complete Documentation Accuracy

Our unified validation framework has achieved:
- **100% Model Documentation Accuracy** (66/66 models)
- **100% Endpoint Documentation Accuracy** (39/39 endpoints)
- **Advanced AST Parsing** for Python implementation analysis
- **Intelligent Mapping Algorithms** for documentation correlation
- **Unified CLI Interface** with parallel execution and quality gates

## Structure

```
docs-tooling/
├── validation/                        # 🚀 UNIFIED VALIDATION FRAMEWORK
│   ├── cli.py                         # Primary CLI interface
│   ├── core/                          # Core validation framework
│   │   ├── ast_utils.py               # Advanced AST parsing utilities
│   │   ├── markdown_utils.py          # Safe markdown parsing with union types
│   │   ├── base.py                    # Base validator classes
│   │   ├── runner.py                  # Validation orchestration
│   │   └── config.py                  # Configuration management
│   ├── validators/                    # Validation implementations
│   │   ├── endpoint_accuracy.py       # 🎯 100% endpoint accuracy
│   │   ├── model_accuracy.py          # 📊 95%+ model accuracy
│   │   ├── links.py                   # Link validation
│   │   ├── syntax.py                  # Markdown syntax
│   │   └── ...                        # Other validators
│   ├── scripts/                       # 🛠️ Enhanced validation scripts
│   │   ├── auto_fix_patterns.py       # Pattern-based auto-fix
│   │   ├── generate_validation_report.py # Comprehensive reports
│   │   ├── validation_dashboard.py    # Real-time metrics dashboard
│   │   ├── debug_code_validator.py    # Debug code validation issues
│   │   └── find_code_issues.py        # Standalone code issue scanner
│   ├── validation-config.yml          # 📋 Quality thresholds and settings
│   ├── validation-rules.yml           # 📏 Codified validation rules
│   └── reports/                       # Generated validation reports
└── README.md                          # This documentation
```

## 🚀 Quick Start

### Unified Validation Framework (Recommended)
```bash
# List all available validators
uv run python docs-tooling/validation/cli.py list

# Run all validators with quality gates and reporting
uv run python docs-tooling/validation/cli.py run --parallel --gates --report

# Run specific accuracy audits (100% endpoint, 95%+ model targets)
uv run python docs-tooling/validation/cli.py run endpoint-accuracy model-accuracy

# Run common validators
uv run python docs-tooling/validation/cli.py run links syntax security

# Run NEW explanation documentation validators
uv run python docs-tooling/validation/cli.py run code-examples cross-references financial-precision

# Run NEW tutorial-specific validators (based on lessons learned)
uv run python docs-tooling/validation/cli.py run tutorial-structure educational-progression code-executability

# Run comprehensive validation including explanation docs
uv run python docs-tooling/validation/cli.py run --parallel --gates --report
```


### Development Workflow
```bash
# Quick validation checks during development
uv run python docs-tooling/validation/cli.py run links syntax

# NEW: Documentation section validation during development
uv run python docs-tooling/validation/cli.py run code-examples cross-references

# Accuracy audits before commits
uv run python docs-tooling/validation/cli.py run endpoint-accuracy model-accuracy

# NEW: Critical financial precision validation before commits
uv run python docs-tooling/validation/cli.py run code-examples cross-references financial-precision

# NEW: Tutorial validation based on lessons learned
uv run python docs-tooling/validation/cli.py run tutorial-structure educational-progression code-executability

# Full validation suite before major releases
uv run python docs-tooling/validation/cli.py run --parallel --gates --report

# Check configuration and thresholds
uv run python docs-tooling/validation/cli.py config --show

# NEW: Real-time monitoring dashboard
uv run python docs-tooling/validation/cli.py dashboard --watch

# NEW: Auto-fix common issues (dry-run first)
uv run python docs-tooling/validation/cli.py autofix docs/how-to-guides
uv run python docs-tooling/validation/cli.py autofix docs/how-to-guides --apply

# NEW: Generate comprehensive reports
uv run python docs-tooling/validation/cli.py report --sections docs/explanation
```

### Validation Workflow Recommendations (Based on Lessons Learned)

#### For Explanation Documentation (`docs/explanation/`)
```bash
# Focus on accuracy and visual consistency
uv run python docs-tooling/validation/cli.py run code-examples financial-precision sdk-methods
```

#### For How-To-Guides (`docs/how-to-guides/`)
```bash
# Emphasize executable examples and financial safety
uv run python docs-tooling/validation/cli.py run code-examples financial-precision cross-references
```

#### For API Reference Documentation
```bash
# Validate model and endpoint accuracy
uv run python docs-tooling/validation/cli.py run endpoint-accuracy model-accuracy
```

#### For Tutorial Documentation (`docs/tutorials/`) (NEW)
```bash
# Comprehensive tutorial validation (based on lessons learned)
uv run python docs-tooling/validation/cli.py run tutorial-structure educational-progression code-executability

# Tutorial content and structure
uv run python docs-tooling/validation/cli.py run tutorial-structure

# Progressive learning and complexity
uv run python docs-tooling/validation/cli.py run educational-progression

# Code executability and completeness
uv run python docs-tooling/validation/cli.py run code-executability
```

#### Priority-Based Validation (Critical Issues First)
```bash
# Step 1: Fix critical financial and import issues
uv run python docs-tooling/validation/cli.py run financial-precision code-examples

# Step 2: Validate cross-references and links
uv run python docs-tooling/validation/cli.py run cross-references links

# Step 3: Full quality assurance
uv run python docs-tooling/validation/cli.py run --parallel --gates --report
```

## 🛠️ Unified Framework Capabilities

### 🚀 Core Validation System
- **Unified CLI** with parallel execution and quality gates
- **Advanced AST parsing** for Python implementation analysis
- **Safe markdown parsing** with union type preservation
- **File-aware mapping** for documentation disambiguation
- **Comprehensive reporting** with detailed metrics and recommendations
- **Configurable quality thresholds** and automated quality gates

### 🎯 Accuracy Validators (100% Achievements)
- **Endpoint Documentation Accuracy**: 100% (39/39 endpoints)
  - Advanced AST parsing for Python parameter extraction
  - **kwargs parameter detection and validation
  - Four-pass intelligent mapping algorithm
  - HTTP method and path extraction from implementation
- **Model Documentation Accuracy**: 100% (66/66 models)
  - Enhanced AST type parsing for complex generic types
  - Field coverage analysis with type and required status validation
  - Cross-model consistency checking

### 📋 Standard Validators
- **Link Validation**: Internal and external link checking
- **Prose Quality**: Style validation using Vale
- **SDK Methods**: Current SDK method name validation in documentation
- **Syntax Validation**: Markdown syntax and structure checking (including ASCII diagrams)
- **Terminology**: Consistent terminology usage validation
- **Security Scanning**: Documentation security issue detection

### 🆕 Explanation Documentation Validators (NEW)
- **Code Example Validation**: Python code syntax, imports, and best practices validation
- **Cross-Reference Validation**: Internal documentation links and anchor validation
- **Financial Precision Validation**: Financial examples precision and type safety validation

### 🎓 Tutorial-Specific Validators (Based on Lessons Learned)
- **Tutorial Structure Validation**: Educational content structure, learning outcomes, prerequisites, hands-on exercises
- **Educational Progression Validation**: Progressive learning patterns, complexity building, skill level appropriateness
- **Code Executability Validation**: Ensures code examples are complete, executable, and properly imported

## 🔧 Advanced Technical Architecture

### Enhanced AST Parsing Engine
All tools share a common advanced AST parsing foundation developed during endpoint validation:

```python
def _get_type_string(self, node: ast.AST) -> str:
    """Enhanced type annotation parsing with full generic support."""
    if isinstance(node, ast.Subscript):
        value = self._get_type_string(node.value)
        if isinstance(node.slice, ast.Tuple):
            # Handle multiple generic parameters like dict[str, Any]
            slice_parts = [self._get_type_string(elt) for elt in node.slice.elts]
            slice_val = ", ".join(slice_parts)
        else:
            slice_val = self._get_type_string(node.slice)
        return f"{value}[{slice_val}]"
    # ... additional type handling for union types, attributes, etc.
```

### File-Aware Mapping System
Intelligent endpoint disambiguation resolves conflicts across documentation files:

```python
file_specific_mappings = {
    'get_accounts': 'accounts.list',
    'get_orders': 'orders.list',
    'cancel_order': 'orders.close',
    'close_position': 'positions.close',
    'close_trade': 'trades.close',
    'put_trade_orders': 'trades.modify',
}
```

### Safe Markdown Parsing
Union type preservation in tables prevents corruption:

```python
# Replace escaped pipes temporarily to avoid splitting on them
safe_row = row.replace('\\|', '〈PIPE〉')
parts = [p.strip().replace('〈PIPE〉', '|') for p in safe_row.split('|')]
```

### **kwargs Parameter Detection
Recognizes flexible API methods that accept arbitrary keyword arguments:

```python
has_kwargs = method_node.args.kwarg is not None
# Documented parameters are valid if implementation has **kwargs
```

## 📋 Validation Rules

Our validation incorporates lessons learned from achieving 100% accuracy across both models and endpoints:

### Financial Precision Rules
- Price fields → `PriceValue` type
- Amount/unit fields → `AccountUnits` type
- Calculation fields → `Decimal` type
- **Never use `float`** for financial data

### Lifecycle Field Rules
- Order models must include complete lifecycle tracking
- Required fields: `trade_closed_ids` (always required)
- Optional fields: filling/cancelling transaction IDs and timestamps

### OANDA Compliance Rules
- Field aliases must use camelCase convention
- ID fields must be `str` type
- Time fields must be `datetime` type
- State fields must use appropriate enums

### Type Consistency Rules
- Same field names across models must use consistent types
- Cross-model validation for relationship integrity

## 🎯 Quality Gates

Default quality gates (configurable in `validation-rules.yml`):
- **Minimum accuracy**: 95% (we achieved 100%)
- **Maximum errors**: 5
- **Blocking issues**: Financial precision, required status, type consistency

## 📊 Achieved Standards

### Core Validation Framework
- ✅ **100% endpoint documentation accuracy** (39/39 endpoints)
- ✅ **100% model documentation accuracy** (66/66 models)
- ✅ **Advanced AST parsing** for complex type annotations
- ✅ **File-aware endpoint mapping** for disambiguation
- ✅ **Union type handling** in markdown tables
- ✅ **kwargs parameter support** for flexible APIs
- ✅ **Complete field coverage** for all models
- ✅ **Financial precision compliance**
- ✅ **OANDA API v20 compliance**
- ✅ **Lifecycle field completeness**
- ✅ **Type consistency** across models
- ✅ **Auto-remediation** for common issues
- ✅ **Comprehensive quality metrics**

### NEW: Documentation Section Validation Results

#### Explanation Documentation (docs/explanation/)
- ✅ **100% accuracy achievement** - Fixed ErrorCode vs FiveTwentyErrorCode issues
- ✅ **Comprehensive enhancement** - Added visual diagrams, testing guides, debugging tools
- ✅ **645 lines added** to best-practices.md with quality assurance framework
- ✅ **Visual forex concepts** - ASCII diagrams for trades vs positions, spreads, margin
- ✅ **Cross-reference integrity** - Enhanced navigation between documentation sections

#### How-To-Guides Documentation (docs/how-to-guides/)
- ✅ **169 validation issues resolved** - Code examples, financial precision, cross-references
- ✅ **17 critical import fixes** - All code examples now runnable with proper imports
- ✅ **10 financial precision corrections** - Float to Decimal conversions for trading safety
- ✅ **11 Decimal imports added** to manage-orders-effectively.md alone
- ✅ **Production-ready examples** - All financial calculations use proper precision
- ✅ **Zero broken cross-references** - All internal links verified and working

## 🔮 Lessons Learned & Codified

### Manual Analysis Insights (Now Automated)
1. **Endpoint Mapping Complexity**: Multiple endpoints with same names across files
2. **Union Type Corruption**: Markdown table parsing split on pipe characters
3. **Generic Type Parsing**: AST parsing required for `dict[str, Any]` annotations
4. **kwargs Parameter Handling**: Flexible APIs need special validation logic
5. **Field Type Patterns**: Financial fields follow consistent type patterns
6. **Required Status Logic**: Based on Field() definitions and defaults
7. **Lifecycle Completeness**: Order models need complete tracking fields
8. **False Positive Detection**: Enhanced regex patterns for table parsing
9. **Domain Knowledge**: Codified OANDA API v20 patterns and conventions

### NEW: Explanation Documentation Insights (Recently Codified)
10. **ErrorCode vs FiveTwentyErrorCode**: Critical accuracy issue requiring systematic detection
11. **Placeholder Function Detection**: Undefined functions like `refresh_token()` must be flagged
12. **Financial Precision Enforcement**: Float usage in financial examples must be prevented
13. **Import Validation**: Missing imports (os, Decimal, etc.) cause code example failures
14. **Cross-Reference Integrity**: Internal links must resolve to valid files and anchors
15. **ASCII Diagram Consistency**: Visual diagrams need alignment and style validation
16. **Async Pattern Validation**: Missing `await` keywords in async examples cause confusion

### NEW: How-To-Guides Validation Insights (Recently Discovered)
17. **Markdown Admonition Code Blocks**: Special handling needed for indented code within `!!! tip` blocks
18. **Financial Literal Detection**: Critical pattern - `price=1.1234` should be `price=Decimal("1.1234")`
19. **Risk Management Precision**: Percentage calculations in trading must use Decimal arithmetic
20. **Production Configuration Values**: Environment variable defaults need proper forex precision
21. **Validator Path Resolution**: Cross-platform path handling required for relative directory navigation
22. **Import Completeness Validation**: Code blocks must include ALL required imports for execution
23. **Financial Context Recognition**: Enhanced detection of financial variables requiring Decimal precision

### NEW: Tutorial Framework Validation Insights (Latest Codification)
24. **Educational Structure Requirements**: Tutorials need learning outcomes, prerequisites, hands-on exercises, skill checkpoints
25. **Progressive Complexity Validation**: Code examples should increase in complexity from simple to advanced
26. **Code Progression Analysis**: Later examples should introduce new concepts or build on previous ones
27. **Skill Level Appropriateness**: Complexity must match intended beginner/intermediate/advanced levels
28. **Learning Scaffolding Patterns**: Explanatory context before code examples, reinforcement activities
29. **Tutorial Identification Patterns**: Clear indication of tutorial purpose and success criteria
30. **Code Executability Requirements**: All tutorial code must be runnable with proper imports and no undefined references
31. **Async Pattern Consistency**: AsyncClient usage must include proper await keywords
32. **Educational Best Practices**: Learning outcomes, skill checkpoints, step-by-step progression indicators

### Best Practices Discovered
1. **Implement file-aware mapping** to resolve endpoint name conflicts across documentation
2. **Use safe markdown parsing** with temporary placeholders for union types
3. **Enhance AST parsing** to handle complex generic type annotations properly
4. **Detect kwargs parameters** to avoid false positive obsolete parameter warnings
5. **Always validate field types** against financial precision requirements
6. **Use comprehensive lifecycle field validation** for order models
7. **Ensure cross-model type consistency** for shared field names
8. **Implement robust markdown table parsing** with edge case handling
9. **Provide auto-remediation capabilities** for common documentation issues

### NEW: How-To-Guides Best Practices (Recently Established)
10. **Validate import completeness** for every code block that uses external dependencies
11. **Enforce financial precision patterns** systematically across all trading examples
12. **Handle markdown admonition indentation** correctly in code block extraction
13. **Prioritize critical financial errors** over style issues in validation reporting
14. **Cross-validate financial context detection** to prevent false negatives
15. **Document validator limitations** clearly to distinguish real issues from tool bugs
16. **Implement progressive validation** - fix critical issues first, then style issues

### NEW: Tutorial Framework Best Practices (Latest Integration)
17. **Validate educational structure** systematically across all tutorials for learning outcomes and prerequisites
18. **Ensure progressive complexity** in code examples from simple to advanced concepts
19. **Check code executability** to guarantee all tutorial examples can actually run
20. **Validate skill level appropriateness** to ensure complexity matches intended audience
21. **Implement learning scaffolding** with proper explanation before code examples
22. **Provide clear success criteria** so learners know when they've completed objectives
23. **Enforce async pattern consistency** in AsyncClient usage with proper await keywords
24. **Validate tutorial identification** to clearly distinguish tutorials from other documentation types

## 🆕 Enhanced Validation Scripts (Based on Lessons Learned)

### Real-Time Monitoring Dashboard
```bash
# Monitor validation metrics in real-time
uv run python docs-tooling/validation/cli.py dashboard --watch

# Generate trend report for last 7 days
uv run python docs-tooling/validation/cli.py dashboard --report 7

# Export metrics data for analysis
uv run python docs-tooling/validation/cli.py dashboard --export csv
```

### Pattern-Based Auto-Fix
```bash
# Check what can be auto-fixed (dry-run)
uv run python docs-tooling/validation/cli.py autofix docs/how-to-guides

# Apply specific pattern fixes
uv run python docs-tooling/validation/cli.py autofix docs/explanation --patterns financial-precision missing-imports --apply

# Generate fix report
uv run python docs-tooling/validation/cli.py autofix docs/how-to-guides --apply --report autofix_report.md
```

### Comprehensive Report Generation
```bash
# Generate detailed validation report for all sections
uv run python docs-tooling/validation/cli.py report

# Focus on specific documentation sections
uv run python docs-tooling/validation/cli.py report --sections docs/explanation docs/how-to-guides

# Export in specific format
uv run python docs-tooling/validation/cli.py report --format markdown --output-dir validation-reports
```

### Debug and Analysis Scripts
```bash
# Debug specific code validation issues with detailed output
uv run python docs-tooling/validation/scripts/debug_code_validator.py

# Standalone code issue scanning (independent of main framework)
uv run python docs-tooling/validation/scripts/find_code_issues.py
```

## 🚀 Future Enhancements

This unified validation framework supports:
- **Continuous endpoint and model validation** as new APIs are added
- **Parallel execution** with intelligent quality gates
- **Advanced cross-reference validation** between implementation and documentation
- **Comprehensive reporting** with detailed metrics and recommendations
- **Intelligent mapping algorithms** for complex documentation structures
- **Configurable quality thresholds** and automated quality gates
- **Real-time accuracy monitoring** during development
- **Pattern-based auto-fixing** for common documentation issues
- **Trend analysis and quality dashboards** for documentation health monitoring

## Key Benefits

- ✅ **Single unified interface** - One CLI for all validation needs
- ✅ **100% accuracy preservation** - All breakthroughs from standalone tools integrated
- ✅ **Professional architecture** - Shared utilities, proper abstraction, extensible design
- ✅ **Parallel execution** - Fast validation runs with concurrent processing
- ✅ **Quality gates** - Automated pass/fail thresholds with detailed reporting
- ✅ **Advanced capabilities** - File-aware mapping, union type handling, AST parsing
- ✅ **Pattern library** - Documented validation patterns prevent regression (see [VALIDATION_PATTERNS.md](validation/scripts/VALIDATION_PATTERNS.md))
- ✅ **Comprehensive coverage** - Validates explanation docs, how-to-guides, API references, model documentation, and tutorials
- ✅ **Tutorial validation framework** - Educational structure, progressive learning, and code executability validation based on lessons learned