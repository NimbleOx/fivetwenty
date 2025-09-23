"""Command-line interface for the validation framework."""

import sys
import time
from pathlib import Path
from typing import Any

import click
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, TimeElapsedColumn
from rich.table import Table
from rich.text import Text

from .config import ValidationConfig
from .engine import ValidationEngine
from .models import IssueSeverity, ValidationSummary

# Import and register validators
from .validators import (
    CrossReferenceValidator,
    FinancialPrecisionValidator,
    MarkdownSyntaxValidator,
    PythonSyntaxValidator,
    SecurityValidator,
)
from .base import registry

# Register all validators
registry.register(FinancialPrecisionValidator())
registry.register(SecurityValidator())
registry.register(MarkdownSyntaxValidator())
registry.register(PythonSyntaxValidator())
registry.register(CrossReferenceValidator())

console = Console()


@click.group()
@click.version_option(version="2.0.0", prog_name="docs-validate")
def cli():
    """FiveTwenty Documentation Validation v2.0

    Fast, reliable validation for trading SDK documentation.
    """
    pass


@cli.command()
@click.option(
    "--config",
    type=click.Path(exists=True, path_type=Path),
    help="Path to YAML configuration file",
)
@click.option(
    "--project-root",
    type=click.Path(exists=True, file_okay=False, path_type=Path),
    default=Path.cwd(),
    help="Project root directory",
)
@click.option("--parallel/--sequential", default=True, help="Run validation in parallel")
@click.option("--max-workers", type=int, default=4, help="Maximum number of worker threads")
@click.option("--verbose", "-v", is_flag=True, help="Show detailed output")
@click.option("--quiet", "-q", is_flag=True, help="Show minimal output")
@click.option("--fail-fast", is_flag=True, help="Exit on first error")
def validate(
    config: Path | None,
    project_root: Path,
    parallel: bool,
    max_workers: int,
    verbose: bool,
    quiet: bool,
    fail_fast: bool,
):
    """Run validation on documentation files."""

    # Load configuration
    if config and config.exists():
        validation_config = ValidationConfig.load_from_file(config)
    else:
        validation_config = ValidationConfig.get_default_config()

    # Override settings from command line
    if not parallel:
        validation_config.parallel_execution = False
    validation_config.max_workers = max_workers

    # Create engine
    engine = ValidationEngine(validation_config, project_root)

    # Run validation with progress indicator
    if not quiet:
        console.print(f"🔍 Discovering files in {project_root}")

    start_time = time.perf_counter()

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        TimeElapsedColumn(),
        console=console if not quiet else None,
        transient=True,
    ) as progress:
        if not quiet:
            task = progress.add_task("Running validation...", total=None)

        summary = engine.validate()

        if not quiet:
            progress.update(task, description="Validation complete")

    duration = time.perf_counter() - start_time

    # Display results
    _display_results(summary, duration, verbose, quiet, fail_fast)

    # Exit with appropriate code
    if summary.has_errors or not _check_quality_gates(summary, validation_config):
        sys.exit(1)
    else:
        sys.exit(0)


@cli.command()
@click.argument("files", nargs=-1, type=click.Path(exists=True, path_type=Path))
@click.option(
    "--config",
    type=click.Path(exists=True, path_type=Path),
    help="Path to YAML configuration file",
)
@click.option("--verbose", "-v", is_flag=True, help="Show detailed output")
def check(files: tuple[Path, ...], config: Path | None, verbose: bool):
    """Run validation on specific files (incremental mode)."""

    if not files:
        console.print("❌ No files specified", style="red")
        sys.exit(1)

    # Load configuration
    if config and config.exists():
        validation_config = ValidationConfig.load_from_file(config)
    else:
        validation_config = ValidationConfig.get_default_config()

    # Create engine
    engine = ValidationEngine(validation_config)

    # Run incremental validation
    console.print(f"🔍 Validating {len(files)} file(s)")

    start_time = time.perf_counter()
    summary = engine.validate_incremental(list(files))
    duration = time.perf_counter() - start_time

    # Display results
    _display_results(summary, duration, verbose, quiet=False, fail_fast=False)

    # Exit with appropriate code
    sys.exit(1 if summary.has_errors else 0)


@cli.command("list-validators")
def list_validators():
    """List all available validators."""
    from .base import registry

    table = Table(title="Available Validators")
    table.add_column("Name", style="cyan", no_wrap=True)
    table.add_column("Description", style="white")

    for validator_name in sorted(registry.list_validators()):
        validator = registry.get_validator(validator_name)
        if validator:
            table.add_row(validator_name, validator.description)

    console.print(table)


def _display_results(
    summary: ValidationSummary,
    duration: float,
    verbose: bool,
    quiet: bool,
    fail_fast: bool,
) -> None:
    """Display validation results."""

    if quiet and summary.total_issues == 0:
        return

    console.print()

    # Summary table
    table = Table(title="Validation Summary")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="white")

    table.add_row("Files", str(summary.total_files))
    table.add_row("Validators", str(summary.total_validators))
    table.add_row("Duration", f"{duration:.2f}s")

    # Results with colors
    if summary.passed_files == summary.total_files:
        table.add_row("Status", Text("✅ PASSED", style="green"))
    else:
        table.add_row("Status", Text("❌ FAILED", style="red"))

    table.add_row("Success Rate", f"{summary.success_rate:.1f}%")
    table.add_row("Issues Found", str(summary.total_issues))

    if summary.error_count > 0:
        table.add_row("Errors", Text(str(summary.error_count), style="red"))
    if summary.warning_count > 0:
        table.add_row("Warnings", Text(str(summary.warning_count), style="yellow"))

    console.print(table)

    # Show issues if any
    if summary.total_issues > 0:
        _display_issues(summary, verbose)


def _display_issues(summary: ValidationSummary, verbose: bool) -> None:
    """Display detailed issues."""
    console.print("\n📋 Issues Found:")

    # Group issues by file
    issues_by_file: dict[Path, list[Any]] = {}
    for result in summary.results:
        if result.issues:
            if result.file_path not in issues_by_file:
                issues_by_file[result.file_path] = []
            issues_by_file[result.file_path].extend(result.issues)

    for file_path, issues in issues_by_file.items():
        console.print(f"\n📄 {file_path}")

        for issue in issues:
            # Format issue with appropriate styling
            severity_style = {
                IssueSeverity.ERROR: "red",
                IssueSeverity.WARNING: "yellow",
                IssueSeverity.INFO: "blue",
                IssueSeverity.SUGGESTION: "green",
            }.get(issue.severity, "white")

            severity_icon = {
                IssueSeverity.ERROR: "❌",
                IssueSeverity.WARNING: "⚠️",
                IssueSeverity.INFO: "ℹ️",
                IssueSeverity.SUGGESTION: "💡",
            }.get(issue.severity, "•")

            location = f":{issue.line}" if issue.line else ""

            console.print(
                f"  {severity_icon} {issue.message} {location}",
                style=severity_style
            )

            if verbose:
                if issue.context:
                    console.print(f"     Context: {issue.context}", style="dim")
                if issue.suggestion:
                    console.print(f"     💡 {issue.suggestion}", style="dim green")
                if issue.rule_id:
                    console.print(f"     Rule: {issue.rule_id}", style="dim")


def _check_quality_gates(summary: ValidationSummary, config: ValidationConfig) -> bool:
    """Check if validation meets quality gate requirements."""
    gates = config.quality_gates

    # Check error threshold
    if gates.fail_on_error and summary.error_count > gates.max_errors:
        console.print(
            f"❌ Quality gate failed: {summary.error_count} errors > {gates.max_errors} allowed",
            style="red"
        )
        return False

    # Check warning threshold
    if summary.warning_count > gates.max_warnings:
        console.print(
            f"❌ Quality gate failed: {summary.warning_count} warnings > {gates.max_warnings} allowed",
            style="red"
        )
        return False

    # Check success rate
    if summary.success_rate < gates.min_success_rate:
        console.print(
            f"❌ Quality gate failed: {summary.success_rate:.1f}% success rate < {gates.min_success_rate}% required",
            style="red"
        )
        return False

    return True


def main():
    """Main entry point."""
    cli()


if __name__ == "__main__":
    main()