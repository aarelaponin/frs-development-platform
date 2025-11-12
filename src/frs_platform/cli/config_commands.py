"""
Configuration Management Commands

Commands for managing FRS platform configuration.
"""

import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import print_json
from pathlib import Path
from typing import Optional
import yaml
import json

from frs_platform.utils.config_loader import get_config_loader, ConfigLoader
from frs_platform.utils.logger import get_logger

app = typer.Typer(help="Configuration management commands")
console = Console()
logger = get_logger()


@app.command("init")
def init_config(
    ctx: typer.Context,
    force: bool = typer.Option(False, "--force", "-f", help="Overwrite existing configuration")
) -> None:
    """Initialize configuration file with defaults"""
    config_path = ctx.obj.get("config_path")
    loader = get_config_loader(config_path)

    if loader.config_path.exists() and not force:
        console.print(f"[yellow]Configuration already exists at {loader.config_path}[/yellow]")
        console.print("Use --force to overwrite")
        raise typer.Exit(code=1)

    try:
        loader._create_default_config()
        loader.ensure_directories()
        console.print(
            Panel(
                f"[green]✓ Configuration initialized successfully[/green]\n\n"
                f"Location: {loader.config_path}\n\n"
                f"Next steps:\n"
                f"1. Set instance passwords in environment:\n"
                f"   export JDX1_PASSWORD='your-password'\n"
                f"2. Edit configuration: frs-dev config edit\n"
                f"3. Validate: frs-dev config validate",
                title="Configuration Initialized",
                border_style="green"
            )
        )
    except Exception as e:
        console.print(f"[red]Failed to initialize configuration: {e}[/red]")
        raise typer.Exit(code=1)


@app.command("show")
def show_config(
    ctx: typer.Context,
    format: str = typer.Option("yaml", "--format", "-f", help="Output format (yaml, json)"),
    section: Optional[str] = typer.Option(None, "--section", "-s", help="Show specific section only")
) -> None:
    """Show current configuration"""
    try:
        loader = get_config_loader(ctx.obj.get("config_path"))
        config = loader.load()

        # Convert to dict
        config_dict = config.model_dump(mode="python", exclude_none=True)

        # Filter to section if specified
        if section:
            if section not in config_dict:
                console.print(f"[red]Section '{section}' not found[/red]")
                console.print(f"Available sections: {', '.join(config_dict.keys())}")
                raise typer.Exit(code=1)
            config_dict = {section: config_dict[section]}

        # Output in requested format
        if format == "json":
            print_json(data=config_dict)
        else:
            console.print(yaml.dump(config_dict, default_flow_style=False, sort_keys=False))

    except FileNotFoundError:
        console.print(
            "[red]Configuration not found[/red]\n"
            "Run 'frs-dev config init' to create a default configuration"
        )
        raise typer.Exit(code=1)
    except Exception as e:
        console.print(f"[red]Failed to load configuration: {e}[/red]")
        raise typer.Exit(code=1)


@app.command("validate")
def validate_config(ctx: typer.Context) -> None:
    """Validate configuration file"""
    try:
        loader = get_config_loader(ctx.obj.get("config_path"))

        console.print(f"[blue]Validating configuration: {loader.config_path}[/blue]\n")

        if loader.validate():
            console.print(
                Panel(
                    "[green]✓ Configuration is valid[/green]",
                    title="Validation Result",
                    border_style="green"
                )
            )
        else:
            console.print(
                Panel(
                    "[red]✗ Configuration has errors[/red]",
                    title="Validation Result",
                    border_style="red"
                )
            )
            raise typer.Exit(code=1)

    except FileNotFoundError:
        console.print(
            "[red]Configuration not found[/red]\n"
            "Run 'frs-dev config init' to create a default configuration"
        )
        raise typer.Exit(code=1)
    except Exception as e:
        console.print(f"[red]Validation failed: {e}[/red]")
        raise typer.Exit(code=1)


@app.command("path")
def show_config_path(ctx: typer.Context) -> None:
    """Show configuration file path"""
    loader = get_config_loader(ctx.obj.get("config_path"))
    console.print(f"Configuration file: [blue]{loader.config_path}[/blue]")

    if loader.config_path.exists():
        console.print(f"Status: [green]✓ exists[/green]")
    else:
        console.print(f"Status: [red]✗ not found[/red]")
        console.print("\nRun 'frs-dev config init' to create it")


@app.command("edit")
def edit_config(ctx: typer.Context) -> None:
    """Open configuration file in default editor"""
    import subprocess
    import os

    loader = get_config_loader(ctx.obj.get("config_path"))

    if not loader.config_path.exists():
        console.print("[red]Configuration file not found[/red]")
        console.print("Run 'frs-dev config init' first")
        raise typer.Exit(code=1)

    # Try to open in editor
    editor = os.environ.get("EDITOR", "nano")

    try:
        console.print(f"Opening {loader.config_path} in {editor}...")
        subprocess.run([editor, str(loader.config_path)], check=True)

        # Validate after editing
        console.print("\n[blue]Validating changes...[/blue]")
        loader.validate()

    except subprocess.CalledProcessError:
        console.print(f"[red]Failed to open editor[/red]")
        console.print(f"Set EDITOR environment variable or edit directly: {loader.config_path}")
        raise typer.Exit(code=1)
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(code=1)


@app.command("get")
def get_config_value(
    ctx: typer.Context,
    key: str = typer.Argument(..., help="Configuration key (e.g., 'instances.jdx1.url')")
) -> None:
    """Get a specific configuration value"""
    try:
        loader = get_config_loader(ctx.obj.get("config_path"))
        config = loader.load()
        config_dict = config.model_dump(mode="python")

        # Navigate to key
        keys = key.split(".")
        value = config_dict
        for k in keys:
            if isinstance(value, dict):
                if k not in value:
                    console.print(f"[red]Key '{key}' not found[/red]")
                    raise typer.Exit(code=1)
                value = value[k]
            else:
                console.print(f"[red]Cannot access '{k}' in non-dict value[/red]")
                raise typer.Exit(code=1)

        # Print value
        if isinstance(value, (dict, list)):
            print_json(data=value)
        else:
            console.print(value)

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(code=1)


@app.command("list-instances")
def list_instances(ctx: typer.Context) -> None:
    """List configured instances"""
    try:
        loader = get_config_loader(ctx.obj.get("config_path"))
        config = loader.load()

        if not config.instances:
            console.print("[yellow]No instances configured[/yellow]")
            return

        table = Table(title="Configured Instances")
        table.add_column("Name", style="cyan")
        table.add_column("URL", style="blue")
        table.add_column("Web Port", style="green")
        table.add_column("DB Port", style="green")
        table.add_column("Version", style="yellow")

        for name, instance in config.instances.items():
            table.add_row(
                name,
                instance.url,
                str(instance.web_port),
                str(instance.db_port),
                instance.version or "unknown"
            )

        console.print(table)

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(code=1)
