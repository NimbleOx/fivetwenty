"""Command-line interface for the validation framework."""

import sys
from pathlib import Path

import click
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, TimeElapsedColumn
from rich.table import Table
from rich.text import Text

from .base import registry
from .config import ValidationConfig
from .engine import ValidationEngine
from .models import ValidationSummary
from .reporters import MarkdownReporter

# Import and register validators
from .validators import (
    CodeExecutionValidator,
    CodeLintingValidator,
    CodeTypingValidator,
    CrossReferenceValidator,
    ExternalLinkValidator,
    FinancialPrecisionValidator,
    MarkdownSyntaxValidator,
    PythonSyntaxValidator,
    SDKMethodsValidator,
    SecurityValidator,
)

# Register all validators
registry.register(FinancialPrecisionValidator())
registry.register(SecurityValidator())
registry.register(MarkdownSyntaxValidator())
registry.register(PythonSyntaxValidator())
registry.register(CrossReferenceValidator())
registry.register(SDKMethodsValidator())
registry.register(CodeExecutionValidator())
registry.register(CodeLintingValidator())
registry.register(CodeTypingValidator())
registry.register(ExternalLinkValidator())

console = Console()


@click.group()
@click.version_option(version="2.0.0", prog_name="docs-validate")
def cli() -> None:
    """FiveTwenty Documentation Validation v2.0

    Fast, reliable validation for trading SDK documentation.
    """


@cli.command()
@click.option(
    "--config",
    type=click.Path(exists=True, path_type=Path),
    help="Path to YAML configuration file",
)
@click.option("--parallel/--sequential", default=True, help="Run validation in parallel")
@click.option("--max-workers", type=int, default=4, help="Maximum number of worker threads")
@click.option(
    "--files",
    multiple=True,
    type=click.Path(exists=True, path_type=Path),
    help="Specific files to validate (can be used multiple times)",
)
def validate(
    config: Path | None,
    parallel: bool,
    max_workers: int,
    files: tuple[Path, ...],
) -> None:
    """Run validation on documentation files."""

    # Hardcode project root to current working directory
    project_root = Path.cwd()

    # Load configuration
    if config and config.exists():
        validation_config = ValidationConfig.load_from_file(config)
    else:
        # Try to find validation.yml in docs_validation/config, then config/, then current directory
        docs_config_path = Path("docs_validation/config/validation.yml")
        config_dir_path = Path("config/validation.yml")
        default_config_path = Path("validation.yml")
        if docs_config_path.exists():
            validation_config = ValidationConfig.load_from_file(docs_config_path)
        elif config_dir_path.exists():
            validation_config = ValidationConfig.load_from_file(config_dir_path)
        elif default_config_path.exists():
            validation_config = ValidationConfig.load_from_file(default_config_path)
        else:
            validation_config = ValidationConfig.get_default_config()

    # Override settings from command line
    if not parallel:
        validation_config.parallel_execution = False
    validation_config.max_workers = max_workers

    # Create engine
    engine = ValidationEngine(validation_config, project_root)

    # Run validation with progress indicator
    if files:
        console.print(f"🔍 Validating {len(files)} specific file(s)")

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            TimeElapsedColumn(),
            console=console,
            transient=True,
        ) as progress:
            task = progress.add_task("Running validation...", total=None)

            summary = engine.validate_incremental(list(files))

            progress.update(task, description="Validation complete")
    else:
        console.print(f"🔍 Discovering files in {project_root}")

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            TimeElapsedColumn(),
            console=console,
            transient=True,
        ) as progress:
            task = progress.add_task("Running validation...", total=None)

            summary = engine.validate()

            progress.update(task, description="Validation complete")

    # Display results and always generate report
    _display_results(summary)

    # Always exit with success - this is informational validation
    sys.exit(0)


@cli.command()
@click.argument("files", nargs=-1, type=click.Path(exists=True, path_type=Path))
@click.option(
    "--config",
    type=click.Path(exists=True, path_type=Path),
    help="Path to YAML configuration file",
)
def check(files: tuple[Path, ...], config: Path | None) -> None:
    """Run validation on specific files (incremental mode)."""

    if not files:
        console.print("❌ No files specified", style="red")
        sys.exit(1)

    # Load configuration
    if config and config.exists():
        validation_config = ValidationConfig.load_from_file(config)
    else:
        # Try to find validation.yml in docs_validation/config, then config/, then current directory
        docs_config_path = Path("docs_validation/config/validation.yml")
        config_dir_path = Path("config/validation.yml")
        default_config_path = Path("validation.yml")
        if docs_config_path.exists():
            validation_config = ValidationConfig.load_from_file(docs_config_path)
        elif config_dir_path.exists():
            validation_config = ValidationConfig.load_from_file(config_dir_path)
        elif default_config_path.exists():
            validation_config = ValidationConfig.load_from_file(default_config_path)
        else:
            validation_config = ValidationConfig.get_default_config()

    # Create engine
    engine = ValidationEngine(validation_config)

    # Run incremental validation
    console.print(f"🔍 Validating {len(files)} file(s)")

    summary = engine.validate_incremental(list(files))

    # Display results and always generate report
    _display_results(summary)

    # Always exit with success - this is informational validation
    sys.exit(0)


def _display_results(
    summary: ValidationSummary,
) -> None:
    """Display validation results and always generate report."""

    console.print()

    # Show per-validator summary (contains all necessary information)
    _display_validator_summaries(summary)

    # Show total runtime
    runtime_seconds = summary.duration_ms / 1000.0
    console.print(f"\n⏱️  Total validation runtime: {runtime_seconds:.2f}s", style="cyan")

    # Show brief issues summary if any (detailed issues are in the report)
    if summary.total_issues > 0:
        _display_brief_issues_summary(summary)

    # Always generate markdown report
    _generate_markdown_report(summary)


def _display_brief_issues_summary(summary: ValidationSummary) -> None:
    """Display a brief summary of issues without details."""
    console.print(f"\n📋 Found {summary.total_issues} issues across {len([r for r in summary.results if r.issues])} files")

    if summary.error_count > 0:
        console.print(f"   ❌ {summary.error_count} errors", style="red")
    if summary.warning_count > 0:
        console.print(f"   ⚠️ {summary.warning_count} warnings", style="yellow")

    console.print("   💡 See detailed analysis in the generated validation report")


def _display_validator_summaries(summary: ValidationSummary) -> None:
    """Display per-validator summary statistics."""
    if not summary.validator_summaries:
        return

    # Display overall status
    overall_status = "✅ PASSED" if summary.passed_files == summary.total_files else "❌ FAILED"
    status_style = "green" if summary.passed_files == summary.total_files else "red"

    console.print(f"📊 Validation Results: {Text(overall_status, style=status_style)} | {summary.total_files} files | {summary.success_rate:.1f}% success rate | {summary.total_issues} issues")

    # Create table for validator summaries
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Validator", style="cyan", no_wrap=True)
    table.add_column("Files", justify="right")
    table.add_column("Success Rate", justify="right")
    table.add_column("Issues", justify="right")
    table.add_column("Errors", justify="right")
    table.add_column("Warnings", justify="right")
    table.add_column("Duration", justify="right")

    for validator_summary in summary.validator_summaries:
        if not validator_summary.enabled:
            # Disabled validator - show with disabled styling
            table.add_row(
                Text(validator_summary.name, style="dim"),
                Text("—", style="dim"),  # No files checked
                Text("DISABLED", style="dim italic"),
                Text("—", style="dim"),  # No issues
                Text("—", style="dim"),  # No errors
                Text("—", style="dim"),  # No warnings
                Text("—", style="dim"),  # No duration
            )
        else:
            # Enabled validator - show normal statistics
            # Format success rate with color
            success_rate = f"{validator_summary.success_rate:.1f}%"
            if validator_summary.success_rate == 100.0:
                success_rate_text = Text(success_rate, style="green")
            elif validator_summary.success_rate >= 80.0:
                success_rate_text = Text(success_rate, style="yellow")
            else:
                success_rate_text = Text(success_rate, style="red")

            # Format errors and warnings with color
            errors_text = Text(str(validator_summary.error_count), style="red") if validator_summary.error_count > 0 else str(validator_summary.error_count)
            warnings_text = Text(str(validator_summary.warning_count), style="yellow") if validator_summary.warning_count > 0 else str(validator_summary.warning_count)

            table.add_row(validator_summary.name, str(validator_summary.files_checked), success_rate_text, str(validator_summary.total_issues), errors_text, warnings_text, f"{validator_summary.duration_ms:.0f}ms")

    console.print(table)


def _generate_markdown_report(
    summary: ValidationSummary,
) -> None:
    """Generate markdown validation report."""
    # Always use the reports directory
    reports_dir = Path(__file__).parent.parent / "reports"
    reports_dir.mkdir(exist_ok=True)
    output_file = reports_dir / "validation-report.md"

    # Collect all issues from validation results
    all_issues = []
    for result in summary.results:
        if result.issues:
            all_issues.extend(result.issues)

    try:
        # Create markdown reporter and generate report
        reporter = MarkdownReporter()
        reporter.generate_report(summary=summary, all_issues=all_issues, output_path=output_file, include_detailed_issues=True)

        # Display success message
        console.print(f"\n📄 Markdown report generated: {output_file}", style="green")

    except Exception as e:
        console.print(f"\n❌ Failed to generate markdown report: {e}", style="red")


def main() -> None:
    """Main entry point."""
    cli()


if __name__ == "__main__":
    main()
