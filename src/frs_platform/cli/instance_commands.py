"""
Instance Management Commands

Commands for managing Joget DX instances.
"""

import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from typing import Optional, List
from pathlib import Path
from datetime import datetime
import subprocess

from frs_platform.utils.config_loader import get_config_loader
from frs_platform.utils.logger import get_logger
from frs_platform.clients.joget_client import JogetAPIClient

app = typer.Typer(help="Instance management commands")
console = Console()
logger = get_logger()


def get_client_for_instance(ctx: typer.Context, instance_name: str) -> JogetAPIClient:
    """
    Get API client for instance

    Args:
        ctx: Typer context
        instance_name: Instance name

    Returns:
        JogetAPIClient instance
    """
    loader = get_config_loader(ctx.obj.get("config_path"))
    config = loader.load()
    instance = config.get_instance(instance_name)
    return JogetAPIClient(instance)


@app.command("list")
def list_instances(ctx: typer.Context) -> None:
    """List all configured instances"""
    try:
        loader = get_config_loader(ctx.obj.get("config_path"))
        config = loader.load()

        if not config.instances:
            console.print("[yellow]No instances configured[/yellow]")
            console.print("Run 'frs-dev config init' to create default configuration")
            return

        table = Table(title="Configured Instances", show_header=True, header_style="bold magenta")
        table.add_column("Name", style="cyan", width=10)
        table.add_column("URL", style="blue")
        table.add_column("Web Port", justify="center", style="green", width=10)
        table.add_column("DB Port", justify="center", style="green", width=10)
        table.add_column("Version", style="yellow", width=10)
        table.add_column("Status", justify="center", width=12)

        for name, instance in config.instances.items():
            # Quick connectivity test
            try:
                client = JogetAPIClient(instance)
                if client.test_connection(timeout=2):
                    status = "[green]● Online[/green]"
                else:
                    status = "[red]● Offline[/red]"
            except Exception:
                status = "[dim]● Unknown[/dim]"

            table.add_row(
                name,
                instance.url,
                str(instance.web_port),
                str(instance.db_port),
                instance.version or "-",
                status
            )

        console.print(table)
        console.print(f"\n[dim]Total instances: {len(config.instances)}[/dim]")

    except FileNotFoundError:
        console.print("[red]Configuration not found[/red]")
        console.print("Run 'frs-dev config init' to create configuration")
        raise typer.Exit(code=1)
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(code=1)


@app.command("info")
def instance_info(
    ctx: typer.Context,
    instance: str = typer.Argument(..., help="Instance name (e.g., jdx1)")
) -> None:
    """Show detailed information about an instance"""
    try:
        loader = get_config_loader(ctx.obj.get("config_path"))
        config = loader.load()
        inst = config.get_instance(instance)

        # Get API client
        client = JogetAPIClient(inst)

        console.print(f"\n[bold]Instance: {instance}[/bold]\n")

        # Basic info
        info_table = Table(show_header=False, box=None, padding=(0, 2))
        info_table.add_column("Property", style="cyan")
        info_table.add_column("Value", style="white")

        info_table.add_row("Name", inst.name)
        info_table.add_row("URL", inst.url)
        info_table.add_row("Base URL", inst.base_url)
        info_table.add_row("Console URL", inst.console_url)
        info_table.add_row("Web Port", str(inst.web_port))
        info_table.add_row("Database Port", str(inst.db_port))
        info_table.add_row("Database Name", inst.db_name)
        info_table.add_row("Database Host", inst.db_host)
        info_table.add_row("Version", inst.version or "unknown")
        if inst.installation_path:
            info_table.add_row("Installation Path", str(inst.installation_path))

        console.print(Panel(info_table, title="Configuration", border_style="blue"))

        # Health check
        console.print("\n[bold]Checking health...[/bold]")
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Testing connectivity...", total=None)
            health = client.get_health_status()

        # Health status
        health_table = Table(show_header=False, box=None, padding=(0, 2))
        health_table.add_column("Check", style="cyan")
        health_table.add_column("Status", style="white")

        def status_icon(check: bool) -> str:
            return "[green]✓[/green]" if check else "[red]✗[/red]"

        health_table.add_row(
            "Reachable",
            f"{status_icon(health['reachable'])} {'Yes' if health['reachable'] else 'No'}"
        )
        health_table.add_row(
            "Authenticated",
            f"{status_icon(health['authenticated'])} {'Yes' if health['authenticated'] else 'No'}"
        )
        health_table.add_row("Applications", str(health.get('applications', 0)))
        health_table.add_row("Plugins", str(health.get('plugins', 0)))

        if health.get('version'):
            health_table.add_row("Detected Version", health['version'])

        console.print(Panel(health_table, title="Health Status", border_style="green"))

        # Overall status
        if health['reachable'] and health['authenticated']:
            console.print("\n[green]✓ Instance is healthy and accessible[/green]\n")
        elif health['reachable']:
            console.print("\n[yellow]⚠ Instance is reachable but authentication failed[/yellow]")
            console.print("[dim]Check your credentials in configuration[/dim]\n")
        else:
            console.print("\n[red]✗ Instance is not reachable[/red]")
            console.print("[dim]Check if the instance is running and ports are correct[/dim]\n")

    except ValueError as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(code=1)
    except Exception as e:
        console.print(f"[red]Error getting instance info: {e}[/red]")
        if ctx.obj.get("verbose"):
            import traceback
            console.print(traceback.format_exc())
        raise typer.Exit(code=1)


@app.command("test")
def test_instance(
    ctx: typer.Context,
    instance: str = typer.Argument(..., help="Instance name (e.g., jdx1)"),
    timeout: int = typer.Option(10, "--timeout", "-t", help="Connection timeout in seconds")
) -> None:
    """Test connectivity to an instance"""
    try:
        client = get_client_for_instance(ctx, instance)

        console.print(f"Testing connectivity to [cyan]{instance}[/cyan]...")

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Connecting...", total=None)

            # Test connection
            if client.test_connection(timeout=timeout):
                progress.update(task, description="[green]✓ Connected[/green]")
                console.print(f"\n[green]✓ Successfully connected to {instance}[/green]")

                # Try to get additional info
                try:
                    apps = client.list_applications()
                    console.print(f"[dim]Applications: {len(apps)}[/dim]")
                except Exception:
                    pass

            else:
                progress.update(task, description="[red]✗ Failed[/red]")
                console.print(f"\n[red]✗ Failed to connect to {instance}[/red]")
                console.print("[dim]Instance may be offline or unreachable[/dim]")
                raise typer.Exit(code=1)

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(code=1)


@app.command("backup")
def backup_instance(
    ctx: typer.Context,
    instance: str = typer.Argument(..., help="Instance name (e.g., jdx1)"),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Output directory for backup"),
) -> None:
    """Backup instance database"""
    try:
        loader = get_config_loader(ctx.obj.get("config_path"))
        config = loader.load()
        inst = config.get_instance(instance)

        # Determine output path
        if output is None:
            output = config.paths.backups / datetime.now().strftime("%Y%m%d")

        output.mkdir(parents=True, exist_ok=True)

        # Generate backup filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = output / f"{instance}_backup_{timestamp}.sql"

        console.print(f"Backing up [cyan]{instance}[/cyan] database...")
        console.print(f"Database: {inst.db_name} on port {inst.db_port}")
        console.print(f"Output: {backup_file}\n")

        # Build mysqldump command
        cmd = [
            "mysqldump",
            "-P", str(inst.db_port),
            "-h", inst.db_host,
            "-u", inst.db_user,
            "--databases", inst.db_name,
            "--result-file", str(backup_file)
        ]

        # Execute backup
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Creating backup...", total=None)

            try:
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=300  # 5 minute timeout
                )

                if result.returncode == 0:
                    progress.update(task, description="[green]✓ Backup complete[/green]")

                    # Get file size
                    size_mb = backup_file.stat().st_size / (1024 * 1024)

                    console.print(
                        Panel(
                            f"[green]✓ Backup completed successfully[/green]\n\n"
                            f"File: {backup_file}\n"
                            f"Size: {size_mb:.2f} MB",
                            title="Backup Complete",
                            border_style="green"
                        )
                    )
                else:
                    progress.update(task, description="[red]✗ Backup failed[/red]")
                    console.print(f"\n[red]Backup failed:[/red] {result.stderr}")
                    raise typer.Exit(code=1)

            except subprocess.TimeoutExpired:
                console.print("[red]Backup timed out after 5 minutes[/red]")
                raise typer.Exit(code=1)
            except FileNotFoundError:
                console.print(
                    "[red]mysqldump command not found[/red]\n"
                    "[dim]Install MySQL client tools: brew install mysql-client (macOS)[/dim]"
                )
                raise typer.Exit(code=1)

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        if ctx.obj.get("verbose"):
            import traceback
            console.print(traceback.format_exc())
        raise typer.Exit(code=1)


@app.command("apps")
def list_apps(
    ctx: typer.Context,
    instance: str = typer.Argument(..., help="Instance name (e.g., jdx1)")
) -> None:
    """List applications on an instance"""
    try:
        client = get_client_for_instance(ctx, instance)

        console.print(f"Listing applications on [cyan]{instance}[/cyan]...\n")

        apps = client.list_applications()

        if not apps:
            console.print("[yellow]No applications found[/yellow]")
            return

        table = Table(title=f"Applications on {instance}", show_header=True)
        table.add_column("App ID", style="cyan")
        table.add_column("Name", style="white")
        table.add_column("Version", style="yellow", justify="center")
        table.add_column("Published", style="green", justify="center")

        for app in apps:
            table.add_row(
                app.get("id", "-"),
                app.get("name", "-"),
                str(app.get("version", "-")),
                "Yes" if app.get("published") else "No"
            )

        console.print(table)
        console.print(f"\n[dim]Total applications: {len(apps)}[/dim]")

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(code=1)
