"""Advanced CLI with configuration management and quality gates."""

import sys
from pathlib import Path

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

# Add the src directory to Python path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from docs_validation.validation.config.loader import default_config_loader
from docs_validation.validation.config.profiles import default_profile_manager
from docs_validation.validation.config.quality_gates import QualityGateManager
from docs_validation.validation.core.config import ValidationConfig, set_config
from docs_validation.validation.core.context import ValidationContext

console = Console()


@click.group()
@click.option("--project-root", type=click.Path(exists=True), help="Project root directory")
@click.pass_context
def cli(ctx, project_root):
    """Advanced validation system with configuration management."""
    if project_root:
        project_path = Path(project_root).resolve()
    else:
        project_path = Path.cwd()

    # Set up global configuration
    config = ValidationConfig(project_root=project_path)
    set_config(config)

    # Store in context for subcommands
    ctx.ensure_object(dict)
    ctx.obj["project_root"] = project_path
    ctx.obj["config"] = config


@cli.group()
def config():
    """Configuration management commands."""


@config.command("init")
@click.option("--format", "config_format", type=click.Choice(["yaml", "json"]), default="yaml", help="Configuration format")
@click.option("--profile", default="default", help="Initial profile to configure")
@click.pass_context
def config_init(ctx, config_format, profile):
    """Initialize validation configuration file."""
    project_root = ctx.obj["project_root"]

    config_file = project_root / f".validation.{config_format}"

    if config_file.exists():
        if not click.confirm(f"Configuration file {config_file} already exists. Overwrite?"):
            return

    try:
        default_config_loader.create_sample_config(config_file, config_format)
        console.print(f"Created configuration file: {config_file}")
        console.print("Edit this file to customize validation settings for your project")

        # Show quick start info
        panel = Panel(
            f"""[green]Quick Start:[/green]

1. Edit {config_file.name} to customize validation settings
2. Run [cyan]validation run --profile {profile}[/cyan] to validate with the new config
3. Use [cyan]validation profiles list[/cyan] to see all available profiles
4. Use [cyan]validation gates --help[/cyan] to learn about quality gates""",
            title="Configuration Created",
            border_style="green",
        )
        console.print(panel)

    except Exception as e:
        console.print(f"Error creating configuration: {e}", style="red")


@config.command("validate")
@click.pass_context
def config_validate(ctx):
    """Validate the current configuration file."""
    project_root = ctx.obj["project_root"]

    try:
        config_file = default_config_loader.find_config_file()

        if not config_file:
            console.print("No configuration file found", style="yellow")
            console.print("Run [cyan]validation config init[/cyan] to create one")
            return

        # Try to load the configuration
        config_data = default_config_loader.load_config_file(config_file)

        console.print(f"Configuration file is valid: {config_file}")

        # Show summary
        profiles = config_data.get("profiles", {})
        default_profile = config_data.get("default_profile", "default")

        table = Table(title="Configuration Summary")
        table.add_column("Setting", style="cyan")
        table.add_column("Value", style="green")

        table.add_row("Config File", str(config_file))
        table.add_row("Format", config_file.suffix[1:].upper())
        table.add_row("Default Profile", default_profile)
        table.add_row("Profiles Defined", str(len(profiles)))

        console.print(table)

        # List profiles
        if profiles:
            console.print("\nAvailable Profiles:")
            for name, profile_config in profiles.items():
                description = profile_config.get("description", "No description")
                extends = profile_config.get("extends")
                extends_info = f" (extends {extends})" if extends else ""
                console.print(f"  - [cyan]{name}[/cyan]: {description}{extends_info}")

    except Exception as e:
        console.print(f"Configuration validation failed: {e}", style="red")


@cli.group()
def profiles():
    """Profile management commands."""


@profiles.command("list")
@click.pass_context
def profiles_list(ctx):
    """List all available validation profiles."""
    try:
        available_profiles = default_profile_manager.list_available_profiles()

        table = Table(title="Available Validation Profiles")
        table.add_column("Profile Name", style="cyan", no_wrap=True)
        table.add_column("Description", style="white")
        table.add_column("Type", style="yellow")

        # Load config to check which are custom
        config_file = default_config_loader.find_config_file()
        custom_profiles = set()
        if config_file:
            try:
                config_data = default_config_loader.load_config_file(config_file)
                custom_profiles = set(config_data.get("profiles", {}).keys())
            except Exception:
                pass

        for name, description in available_profiles.items():
            profile_type = "Custom" if name in custom_profiles else "Built-in"
            table.add_row(name, description, profile_type)

        console.print(table)

        # Show usage examples
        panel = Panel(
            """[green]Usage Examples:[/green]

• [cyan]validation run --profile strict[/cyan] - Run with strict quality standards
• [cyan]validation run --profile fast[/cyan] - Quick validation with essential checks
• [cyan]validation run --profile security[/cyan] - Security-focused validation
• [cyan]validation profiles info <name>[/cyan] - Get detailed profile information""",
            title="Profile Usage",
            border_style="blue",
        )
        console.print(panel)

    except Exception as e:
        console.print(f"Error listing profiles: {e}", style="red")


@profiles.command("info")
@click.argument("profile_name")
@click.pass_context
def profiles_info(ctx, profile_name):
    """Show detailed information about a profile."""
    try:
        report = default_profile_manager.generate_profile_report(profile_name)
        console.print(report)

    except Exception as e:
        console.print(f"Error getting profile info: {e}", style="red")


@profiles.command("compare")
@click.argument("profile_names", nargs=-1, required=True)
@click.pass_context
def profiles_compare(ctx, profile_names):
    """Compare multiple validation profiles."""
    try:
        comparison = default_profile_manager.create_profile_comparison(list(profile_names))

        # Create comparison table
        table = Table(title="Profile Comparison")
        table.add_column("Check", style="cyan")

        for profile_name in profile_names:
            table.add_column(profile_name, justify="center")

        for check, profile_data in comparison["comparison_matrix"].items():
            row = [check]
            for profile_name in profile_names:
                enabled = profile_data.get(profile_name, False)
                if enabled is True:
                    row.append("ENABLED")
                elif enabled is False:
                    row.append("DISABLED")
                else:
                    row.append("UNKNOWN")
            table.add_row(*row)

        console.print(table)

        # Show profile summaries
        for profile_name in profile_names:
            profile_data = comparison["profiles"].get(profile_name, {})
            if "error" not in profile_data:
                console.print(f"\n{profile_name}: {profile_data.get('description', 'No description')}")
                console.print(f"   Quality Gates: {profile_data.get('quality_gates', {})}")

    except Exception as e:
        console.print(f"❌ Error comparing profiles: {e}", style="red")


@cli.group()
def gates():
    """Quality gate management commands."""


@gates.command("test")
@click.option("--profile", default="default", help="Profile to use for quality gates")
@click.option("--max-errors", type=int, help="Override max errors threshold")
@click.option("--max-warnings", type=int, help="Override max warnings threshold")
@click.option("--min-success-rate", type=float, help="Override min success rate threshold")
@click.pass_context
def gates_test(ctx, profile, max_errors, max_warnings, min_success_rate):
    """Test quality gates against current project."""
    project_root = ctx.obj["project_root"]
    config = ctx.obj["config"]

    try:
        context = ValidationContext(config)

        console.print(f"Testing quality gates with profile: {profile}")

        # Execute validation with quality gates
        result = default_profile_manager.validate_with_quality_gates(
            profile,
            context,
        )

        summary = result["validation_summary"]
        gate_report = result["quality_gate_report"]

        # Print validation summary
        console.print("\nValidation Summary:")
        console.print(f"   Total Checks: {len(summary.results)}")
        console.print(f"   Total Issues: {summary.total_issues}")
        console.print(f"   Success Rate: {summary.overall_success_rate:.1f}%")
        console.print(f"   Duration: {summary.total_duration:.2f}s")

        # Print quality gate results
        console.print("\n" + "=" * 50)
        gate_manager = QualityGateManager()
        formatted_report = gate_manager.format_report(gate_report)
        console.print(formatted_report)

        # Exit with appropriate code
        if result["overall_passed"]:
            console.print("\nAll quality gates passed!", style="green")
            sys.exit(0)
        else:
            console.print("\nQuality gates failed!", style="red")
            sys.exit(1)

    except Exception as e:
        console.print(f"Error testing quality gates: {e}", style="red")
        sys.exit(1)


@cli.command("run")
@click.option("--profile", default="default", help="Validation profile to use")
@click.option("--checks", help="Specific checks to run (comma-separated)")
@click.option("--gates/--no-gates", default=True, help="Enable/disable quality gates")
@click.option("--output-format", type=click.Choice(["console", "json", "html", "markdown"]), default="console", help="Output format")
@click.option("--output-dir", type=click.Path(), help="Output directory for reports")
@click.pass_context
def run(ctx, profile, checks, gates, output_format, output_dir):
    """Run validation with advanced configuration."""
    project_root = ctx.obj["project_root"]
    config = ctx.obj["config"]

    try:
        context = ValidationContext(config)

        # Parse specific checks if provided
        specific_checks = None
        if checks:
            specific_checks = [check.strip() for check in checks.split(",")]

        console.print(f"Running validation with profile: [cyan]{profile}[/cyan]")

        if gates:
            # Run with quality gates
            result = default_profile_manager.validate_with_quality_gates(
                profile,
                context,
                specific_checks,
            )

            summary = result["validation_summary"]
            gate_report = result["quality_gate_report"]

            # Show validation results
            _display_validation_summary(summary)

            # Show quality gate results
            console.print("\n" + "=" * 50)
            gate_manager = QualityGateManager()
            formatted_report = gate_manager.format_report(gate_report)
            console.print(formatted_report)

            # Export reports if needed
            if output_format != "console" or output_dir:
                _export_reports(summary, output_format, output_dir, project_root)

            # Exit with appropriate code
            if result["overall_passed"]:
                console.print("\nValidation completed successfully!", style="green")
                sys.exit(0)
            else:
                console.print("\nValidation failed quality gates!", style="red")
                sys.exit(1)
        else:
            # Run without quality gates
            summary = default_profile_manager.execute_profile(
                profile,
                context,
                specific_checks,
            )

            _display_validation_summary(summary)

            # Export reports if needed
            if output_format != "console" or output_dir:
                _export_reports(summary, output_format, output_dir, project_root)

            console.print("\nValidation completed!", style="green")

    except Exception as e:
        console.print(f"Validation failed: {e}", style="red")
        sys.exit(1)


def _display_validation_summary(summary):
    """Display validation summary in console."""
    console.print("\nValidation Results:")
    console.print(f"   Total Checks: {len(summary.results)}")
    console.print(f"   Passed: {summary.passed_checks}")
    console.print(f"   Failed: {summary.failed_checks}")
    console.print(f"   Total Issues: {summary.total_issues}")
    console.print(f"   Files Checked: {summary.total_files_checked}")
    console.print(f"   Success Rate: {summary.overall_success_rate:.1f}%")
    console.print(f"   Duration: {summary.total_duration:.2f}s")

    # Show check details
    for result in summary.results:
        status_icon = "PASSED" if result.is_successful else "FAILED"
        console.print(f"   [{status_icon}] {result.check_name}: {result.issues_found} issues")


def _export_reports(summary, output_format, output_dir, project_root):
    """Export validation reports."""
    try:
        from docs_validation.validation.reporting.exports import ReportExporter

        if output_dir:
            export_dir = Path(output_dir)
        else:
            export_dir = project_root / "validation_reports"

        exporter = ReportExporter(export_dir)

        if output_format == "console":
            formats = ["json", "html"]
        else:
            formats = [output_format]

        exported_files = exporter.export_summary(summary, formats)

        console.print("\nReports exported:")
        for format_name, file_path in exported_files.items():
            console.print(f"   {format_name.upper()}: {file_path}")

    except Exception as e:
        console.print(f"Warning: Error exporting reports: {e}", style="yellow")


if __name__ == "__main__":
    cli()
