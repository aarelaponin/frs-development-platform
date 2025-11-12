"""
FRS Development Platform - Main CLI Entry Point

Command-line interface for managing Joget DX development workflows.
"""

import typer
from rich.console import Console
from rich.panel import Panel
from typing import Optional
from pathlib import Path

from frs_platform import __version__
from frs_platform.utils.logger import setup_logging, get_logger
from frs_platform.utils.config_loader import get_config_loader

# Create main Typer app
app = typer.Typer(
    name="frs-dev",
    help="FRS Development Platform - Command Control Center for Joget DX Development",
    no_args_is_help=True,
    add_completion=False,
)

console = Console()
logger = get_logger()

# Global options
verbose_option = typer.Option(False, "--verbose", "-v", help="Enable verbose output")
config_path_option = typer.Option(
    None,
    "--config",
    "-c",
    help="Path to configuration file",
    envvar="FRS_DEV_CONFIG"
)


@app.callback()
def main_callback(
    ctx: typer.Context,
    verbose: bool = verbose_option,
    config: Optional[Path] = config_path_option,
) -> None:
    """
    FRS Development Platform - Command Control Center

    Manage Joget DX instances, applications, forms, plugins, and deployments.
    """
    # Setup logging
    log_level = "DEBUG" if verbose else "INFO"
    setup_logging(level=log_level)

    # Store config path in context for subcommands
    ctx.obj = {"config_path": config, "verbose": verbose}


@app.command()
def version() -> None:
    """Show version information"""
    console.print(Panel(
        f"[bold]FRS Development Platform[/bold]\n"
        f"Version: {__version__}\n"
        f"Python Package: frs-platform",
        title="Version Info",
        border_style="blue"
    ))


# Import and register command groups
from frs_platform.cli import config_commands, instance_commands

app.add_typer(config_commands.app, name="config", help="Configuration management")
app.add_typer(instance_commands.app, name="instance", help="Instance management")


# Entry point for console script
def cli_main() -> None:
    """Main CLI entry point"""
    try:
        app()
    except KeyboardInterrupt:
        console.print("\n[yellow]Operation cancelled by user[/yellow]")
        raise typer.Exit(code=1)
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        console.print(f"\n[red]Error: {e}[/red]")
        console.print("[dim]Run with --verbose for more details[/dim]")
        raise typer.Exit(code=1)


if __name__ == "__main__":
    cli_main()
