"""Main CLI entry point."""

import sys
from pathlib import Path

import click
from rich.console import Console
from rich.table import Table

from validation.core.config import ValidationConfig, set_config
from validation.core.context import ValidationContext
from validation.validators.registry import default_registry

console = Console()


@click.group()
@click.option(
    "--config",
    type=click.Path(exists=True, path_type=Path),
    help="Configuration file path",
)
@click.option(
    "--project-root",
    type=click.Path(exists=True, file_okay=False, path_type=Path),
    default=Path.cwd(),
    help="Project root directory",
)
def cli(config: Path | None, project_root: Path) -> None:
    """FiveTwenty Documentation Validation System v2.0."""
    # Load configuration
    if config:
        validation_config = ValidationConfig.from_file(config)
    else:
        validation_config = ValidationConfig(project_root=project_root)

    set_config(validation_config)


@cli.command()
def list_checks() -> None:
    """List all available validation checks."""
    checks = default_registry.list_available_checks()

    if not checks:
        console.print("No validation checks available.", style="yellow")
        return

    table = Table(title="Available Validation Checks")
    table.add_column("Check Name", style="cyan", no_wrap=True)
    table.add_column("Description", style="white")

    for name, description in sorted(checks.items()):
        table.add_row(name, description)

    console.print(table)


@cli.command()
@click.argument("checks", nargs=-1)
@click.option("--parallel/--sequential", default=True, help="Run checks in parallel")
@click.option("--report", is_flag=True, help="Generate detailed report")
def run(checks: tuple[str, ...], parallel: bool, report: bool) -> None:
    """Run validation checks."""
    if not checks:
        # Run all checks
        available_checks = list(default_registry.list_available_checks().keys())
        check_names = available_checks
    else:
        check_names = list(checks)

    if not check_names:
        console.print("No checks to run.", style="yellow")
        return

    # Create validation context
    context = ValidationContext()

    # Run checks
    console.print(f"Running {len(check_names)} validation checks...")

    summary = default_registry.run_checks(check_names, context, parallel)

    # Display summary
    _display_summary(summary, report)

    # Exit with appropriate code
    sys.exit(0 if summary.is_successful else 1)


def _display_summary(summary, report: bool) -> None:
    """Display validation summary."""
    console.print()

    # Summary statistics
    table = Table(title="Validation Summary")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="white")

    table.add_row("Total Checks", str(len(summary.results)))
    table.add_row("Passed", str(summary.passed_checks))
    table.add_row("Failed", str(summary.failed_checks))
    table.add_row("Total Issues", str(summary.total_issues))
    table.add_row("Files Checked", str(summary.total_files_checked))
    table.add_row("Success Rate", f"{summary.overall_success_rate:.1f}%")
    table.add_row("Duration", f"{summary.total_duration:.2f}s")

    console.print(table)

    if report:
        _display_detailed_report(summary)


def _display_detailed_report(summary) -> None:
    """Display detailed validation report."""
    console.print("\nDetailed Report")

    for result in summary.results:
        status_icon = "PASSED" if result.is_successful else "FAILED"
        console.print(f"\n[{status_icon}] **{result.check_name}**")

        if result.issues:
            for issue in result.issues[:10]:  # Show first 10 issues
                severity_color = {
                    "error": "red",
                    "warning": "yellow",
                    "info": "blue",
                    "suggestion": "green",
                }.get(issue.severity.value, "white")

                console.print(
                    f"  • {issue.message} ({issue.file_path}:{issue.line or '?'})",
                    style=severity_color,
                )

            if len(result.issues) > 10:
                console.print(f"  ... and {len(result.issues) - 10} more issues")


if __name__ == "__main__":
    cli()
