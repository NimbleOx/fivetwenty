#!/usr/bin/env python3
"""
FiveTwenty Documentation Validation CLI

Single entry point for all validation operations.
"""

import argparse
import sys
from pathlib import Path

# Add the validation package to path for imports
validation_dir = Path(__file__).parent
sys.path.insert(0, str(validation_dir))

try:
    from core.config import ValidationConfig  # type: ignore[import-not-found]
    from core.runner import ValidationRunner, ValidatorRegistry  # type: ignore[import-not-found]
    from validators.code_examples import CodeExampleValidator  # type: ignore[import-not-found]
    from validators.code_executability import CodeExecutabilityValidator  # type: ignore[import-not-found]
    from validators.code_linting import CodeLintingValidator  # type: ignore[import-not-found]
    from validators.cross_references import CrossReferenceValidator  # type: ignore[import-not-found]
    from validators.educational_progression import EducationalProgressionValidator  # type: ignore[import-not-found]
    from validators.financial_precision import FinancialPrecisionValidator  # type: ignore[import-not-found]
    from validators.links import LinkValidator  # type: ignore[import-not-found]
    from validators.prose import ProseValidator  # type: ignore[import-not-found]
    from validators.sdk_methods import SDKMethodValidator  # type: ignore[import-not-found]
    from validators.security import SecurityValidator  # type: ignore[import-not-found]
    from validators.syntax import SyntaxValidator  # type: ignore[import-not-found]
    from validators.terminology import TerminologyValidator  # type: ignore[import-not-found]
    from validators.tutorial_structure import TutorialStructureValidator  # type: ignore[import-not-found]
    # from validators.endpoint_accuracy import EndpointAccuracyValidator  # type: ignore[import-not-found]
    # from validators.model_accuracy import ModelAccuracyValidator  # type: ignore[import-not-found]
except ImportError as e:
    print(f"Import error: {e}")
    print("Make sure you're running from the validation directory")
    sys.exit(1)


def setup_registry() -> ValidatorRegistry:
    """Set up the validator registry with all available validators."""
    registry = ValidatorRegistry()

    # Register core validators
    registry.register("links", LinkValidator, "Validates internal and external links")
    registry.register("prose", ProseValidator, "Validates prose quality and style using Vale")
    registry.register("sdk-methods", SDKMethodValidator, "Validates current SDK method names in documentation")
    registry.register("syntax", SyntaxValidator, "Validates markdown syntax and structure")
    registry.register("terminology", TerminologyValidator, "Validates consistent terminology usage")
    registry.register("security", SecurityValidator, "Scans documentation for potential security issues")

    # Register explanation documentation validators (NEW)
    registry.register("code-examples", CodeExampleValidator, "Validates Python code examples for syntax and best practices")
    registry.register("code-linting", CodeLintingValidator, "Validates Python code blocks with comprehensive ruff linting")
    registry.register("cross-references", CrossReferenceValidator, "Validates internal documentation links and cross-references")
    registry.register("financial-precision", FinancialPrecisionValidator, "Validates financial examples follow precision and type safety best practices")

    # Register tutorial-specific validators (NEW)
    registry.register("tutorial-structure", TutorialStructureValidator, "Validates tutorial content follows educational best practices and proper structure")
    registry.register("educational-progression", EducationalProgressionValidator, "Validates progressive learning patterns and complexity building")
    registry.register("code-executability", CodeExecutabilityValidator, "Validates that code examples are executable and complete")

    # Register accuracy audit validators (100% accuracy achieved)
    # registry.register("endpoint-accuracy", EndpointAccuracyValidator, "Validates endpoint documentation accuracy (100% target)")
    # registry.register("model-accuracy", ModelAccuracyValidator, "Validates model documentation accuracy (95%+ target)")

    return registry


def cmd_list(_args: argparse.Namespace) -> None:
    """List all available validators."""
    registry = setup_registry()
    validators = registry.list_validators()

    print("📋 Available Validators:")
    for name, description in validators.items():
        print(f"  • {name}: {description}")


def cmd_run(args: argparse.Namespace) -> int:
    """Run validation."""
    registry = setup_registry()
    config = ValidationConfig()
    runner = ValidationRunner(config)

    # Determine which validators to run
    validator_names = args.validators or list(registry.list_validators().keys())

    # Create and register validators
    for name in validator_names:
        validator = registry.get_validator(name)
        if validator:
            runner.register_validator(validator)
        else:
            print(f"⚠️  Unknown validator: {name}")

    if not runner.validators:
        print("❌ No validators to run")
        return 1

    # Run validators
    results = runner.run_parallel(max_workers=args.workers) if args.parallel else runner.run_sequential()

    # Generate report
    if args.report:
        runner.generate_report()

    # Check quality gates
    if args.gates:
        gates = runner.check_quality_gates()
        if gates["passed"]:
            print("\n✅ All quality gates passed")
        else:
            print("\n❌ Quality gates failed:")
            for failure in gates["failed_gates"]:
                print(f"  - {failure}")
            return 1

    # Summary
    total_issues = sum(r.issues_found for r in results)
    print(f"\n📊 Summary: {total_issues} total issues found across {len(results)} validators")

    return 1 if total_issues > 0 else 0


def cmd_config(args: argparse.Namespace) -> None:
    """Configuration management."""
    config = ValidationConfig()

    if args.show:
        thresholds = config.get_all_thresholds()
        print("⚙️  Current Quality Thresholds:")
        for metric, threshold in thresholds.items():
            print(f"  • {metric}: {threshold}%")


def cmd_dashboard(args: argparse.Namespace) -> int:
    """Run validation dashboard."""
    import subprocess

    # Build command
    cmd = [sys.executable, str(validation_dir / "scripts" / "validation_dashboard.py")]

    if args.watch:
        cmd.append("--watch")
    if args.sections:
        cmd.extend(["--sections", *args.sections])
    if args.data_dir:
        cmd.extend(["--data-dir", args.data_dir])
    if args.report:
        cmd.extend(["--report", str(args.report)])
    if args.export:
        cmd.extend(["--export", args.export])

    try:
        result = subprocess.run(cmd, check=False)
        return result.returncode
    except Exception as e:
        print(f"❌ Dashboard error: {e}")
        return 1


def cmd_autofix(args: argparse.Namespace) -> int:
    """Run auto-fix script."""
    import subprocess

    # Build command
    cmd = [sys.executable, str(validation_dir / "scripts" / "auto_fix_patterns.py")]
    cmd.append(args.directory)

    if args.apply:
        cmd.append("--apply")
    if args.patterns:
        cmd.extend(["--patterns", *args.patterns])
    if args.report:
        cmd.extend(["--report", args.report])

    try:
        result = subprocess.run(cmd, check=False)
        return result.returncode
    except Exception as e:
        print(f"❌ Auto-fix error: {e}")
        return 1


def cmd_report(args: argparse.Namespace) -> int:
    """Generate comprehensive validation report."""
    import subprocess

    # Build command
    cmd = [sys.executable, str(validation_dir / "scripts" / "generate_validation_report.py")]

    if args.output_dir:
        cmd.extend(["--output-dir", args.output_dir])
    if args.sections:
        cmd.extend(["--sections", *args.sections])
    if args.format:
        cmd.extend(["--format", args.format])

    try:
        result = subprocess.run(cmd, check=False)
        return result.returncode
    except Exception as e:
        print(f"❌ Report generation error: {e}")
        return 1


def main() -> int:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="FiveTwenty Documentation Validation System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s list                              # List available validators
  %(prog)s run                               # Run all validators
  %(prog)s run endpoint-accuracy model-accuracy  # Run accuracy audits
  %(prog)s run links syntax                  # Run specific validators
  %(prog)s run --parallel --gates            # Run in parallel with quality gates
  %(prog)s config --show                     # Show current configuration
  %(prog)s dashboard --watch                 # Monitor validation metrics in real-time
  %(prog)s autofix docs/how-to-guides --apply # Auto-fix common issues
  %(prog)s report --sections docs/explanation # Generate comprehensive report
""",
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # List command
    subparsers.add_parser("list", help="List available validators")

    # Run command
    run_parser = subparsers.add_parser("run", help="Run validators")
    run_parser.add_argument("validators", nargs="*", help="Validators to run (default: all)")
    run_parser.add_argument("--parallel", action="store_true", help="Run validators in parallel")
    run_parser.add_argument("--workers", type=int, default=4, help="Number of parallel workers")
    run_parser.add_argument("--report", action="store_true", help="Generate detailed report")
    run_parser.add_argument("--gates", action="store_true", help="Check quality gates")

    # Config command
    config_parser = subparsers.add_parser("config", help="Configuration management")
    config_parser.add_argument("--show", action="store_true", help="Show current configuration")

    # Dashboard command
    dashboard_parser = subparsers.add_parser("dashboard", help="Real-time validation metrics dashboard")
    dashboard_parser.add_argument("--watch", action="store_true", help="Continuous monitoring mode")
    dashboard_parser.add_argument("--sections", nargs="+", help="Specific sections to monitor")
    dashboard_parser.add_argument("--data-dir", type=str, help="Directory to store dashboard data")
    dashboard_parser.add_argument("--report", type=int, metavar="DAYS", help="Generate trend report for N days")
    dashboard_parser.add_argument("--export", choices=["json", "csv"], help="Export metrics data")

    # Auto-fix command
    autofix_parser = subparsers.add_parser("autofix", help="Auto-fix common documentation issues")
    autofix_parser.add_argument("directory", help="Directory to process")
    autofix_parser.add_argument("--apply", action="store_true", help="Apply fixes (default is dry-run)")
    autofix_parser.add_argument("--patterns", nargs="+",
                               choices=["financial-precision", "missing-imports", "deprecated-patterns"],
                               help="Specific patterns to fix")
    autofix_parser.add_argument("--report", type=str, help="Save report to file")

    # Report generation command
    report_parser = subparsers.add_parser("report", help="Generate comprehensive validation report")
    report_parser.add_argument("--output-dir", type=str, help="Output directory for reports")
    report_parser.add_argument("--sections", nargs="+", help="Specific sections to validate")
    report_parser.add_argument("--format", choices=["json", "markdown", "csv", "all"], default="all", help="Output format")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 0

    # Dispatch to command handlers
    if args.command == "list":
        cmd_list(args)
        return 0
    if args.command == "run":
        return cmd_run(args)
    if args.command == "config":
        cmd_config(args)
        return 0
    if args.command == "dashboard":
        return cmd_dashboard(args)
    if args.command == "autofix":
        return cmd_autofix(args)
    if args.command == "report":
        return cmd_report(args)

    return 0


if __name__ == "__main__":
    sys.exit(main())
