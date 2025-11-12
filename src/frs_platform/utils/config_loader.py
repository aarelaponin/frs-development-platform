"""
Configuration Loader

Loads and manages FRS platform configuration from YAML files and environment variables.
"""

from pathlib import Path
from typing import Optional
import yaml
from rich.console import Console
from rich.panel import Panel

from frs_platform.models.config import FRSPlatformConfig, EnvironmentSettings

console = Console()


class ConfigLoader:
    """Loads and validates FRS platform configuration"""

    def __init__(self, config_path: Optional[Path] = None):
        """
        Initialize configuration loader

        Args:
            config_path: Path to configuration file. If None, uses default from environment.
        """
        self.env_settings = EnvironmentSettings()
        self.config_path = config_path or self.env_settings.frs_dev_config
        self._config: Optional[FRSPlatformConfig] = None

    def load(self, create_if_missing: bool = False) -> FRSPlatformConfig:
        """
        Load configuration from file

        Args:
            create_if_missing: If True, create default config if file doesn't exist

        Returns:
            Loaded configuration

        Raises:
            FileNotFoundError: If config file doesn't exist and create_if_missing=False
        """
        if not self.config_path.exists():
            if create_if_missing:
                console.print(
                    f"[yellow]Configuration file not found at {self.config_path}[/yellow]"
                )
                console.print("[yellow]Creating default configuration...[/yellow]")
                self._create_default_config()
            else:
                raise FileNotFoundError(
                    f"Configuration file not found: {self.config_path}\n"
                    f"Run 'frs-dev config init' to create a default configuration."
                )

        # Load YAML configuration
        with open(self.config_path, "r") as f:
            config_data = yaml.safe_load(f) or {}

        # Create config object
        self._config = FRSPlatformConfig(**config_data)

        # Apply environment overrides
        if self.env_settings.frs_dev_log_level:
            self._config.log_level = self.env_settings.frs_dev_log_level

        return self._config

    def _create_default_config(self) -> None:
        """Create default configuration file"""
        # Ensure config directory exists
        self.config_path.parent.mkdir(parents=True, exist_ok=True)

        # Create default configuration
        default_config = {
            "instances": {
                "jdx1": {
                    "name": "jdx1",
                    "url": "http://localhost:8080",
                    "web_port": 8080,
                    "db_port": 3306,
                    "db_name": "jwdb",
                    "version": "8.1.6",
                    "installation_path": "/Users/aarelaponin/joget-enterprise-linux-joget-enterprise-linux-8.1.6",
                    "credentials": {
                        "username": "admin",
                        "password_env": "JDX1_PASSWORD"
                    }
                },
                "jdx2": {
                    "name": "jdx2",
                    "url": "http://localhost:9999",
                    "web_port": 9999,
                    "db_port": 3307,
                    "db_name": "jwdb",
                    "version": "8.1.6",
                    "installation_path": "/Users/aarelaponin/joget-enterprise-linux-joget-enterprise-linux-8.1.6-2",
                    "credentials": {
                        "username": "admin",
                        "password_env": "JDX2_PASSWORD"
                    }
                },
                "jdx3": {
                    "name": "jdx3",
                    "url": "http://localhost:8888",
                    "web_port": 8888,
                    "db_port": 3308,
                    "db_name": "jwdb",
                    "version": "9.0.0",
                    "installation_path": "/Users/aarelaponin/joget-enterprise-linux-joget-enterprise-linux-9.0.0",
                    "credentials": {
                        "username": "admin",
                        "password_env": "JDX3_PASSWORD"
                    }
                },
                "jdx4": {
                    "name": "jdx4",
                    "url": "http://localhost:7777",
                    "web_port": 7777,
                    "db_port": 3309,
                    "db_name": "jwdb",
                    "version": "9.0.0",
                    "installation_path": "/Users/aarelaponin/joget-enterprise-linux-joget-enterprise-linux-9.0.0-4",
                    "credentials": {
                        "username": "admin",
                        "password_env": "JDX4_PASSWORD"
                    }
                },
                "jdx5": {
                    "name": "jdx5",
                    "url": "http://localhost:6666",
                    "web_port": 6666,
                    "db_port": 3310,
                    "db_name": "jwdb",
                    "version": "9.0.0",
                    "installation_path": "/Users/aarelaponin/joget-enterprise-linux-joget-enterprise-linux-9.0.0-5",
                    "credentials": {
                        "username": "admin",
                        "password_env": "JDX5_PASSWORD"
                    }
                },
                "jdx6": {
                    "name": "jdx6",
                    "url": "http://localhost:5555",
                    "web_port": 5555,
                    "db_port": 3311,
                    "db_name": "jwdb",
                    "version": "9.0.0",
                    "installation_path": "/Users/aarelaponin/joget-enterprise-linux-joget-enterprise-linux-9.0.0-6",
                    "credentials": {
                        "username": "admin",
                        "password_env": "JDX6_PASSWORD"
                    }
                }
            },
            "paths": {
                "plugin_repos": [
                    "/Users/aarelaponin/IdeaProjects"
                ],
                "utilities": [
                    "/Users/aarelaponin/PycharmProjects/dev"
                ],
                "backups": "~/.frs-dev/backups",
                "exports": "~/.frs-dev/exports",
                "reports": "~/.frs-dev/reports",
                "workflows": "~/PycharmProjects/dev/frs-development-platform/workflows",
                "temp": "~/.frs-dev/temp"
            },
            "notifications": {
                "slack": {
                    "enabled": False,
                    "config": {
                        "webhook_url_env": "SLACK_WEBHOOK_URL",
                        "default_channel": "#frs-deployments"
                    }
                },
                "email": {
                    "enabled": False,
                    "config": {
                        "smtp_server": "smtp.example.com",
                        "from_address": "frs-automation@example.com"
                    }
                }
            },
            "validation": {
                "require_backup": True,
                "require_approval_for": [
                    "production_deploy",
                    "data_migration",
                    "plugin_update"
                ],
                "risk_thresholds": {
                    "auto_approve": "LOW",
                    "notify_only": "MEDIUM",
                    "require_approval": "HIGH"
                }
            },
            "workflows": {
                "default_timeout": 3600,
                "rollback_on_failure": True,
                "enable_dry_run": True,
                "max_parallel_operations": 4
            },
            "log_level": "INFO"
        }

        # Write configuration
        with open(self.config_path, "w") as f:
            yaml.dump(default_config, f, default_flow_style=False, sort_keys=False)

        console.print(f"[green]✓ Configuration created at {self.config_path}[/green]")
        console.print(
            "\n[yellow]Important:[/yellow] Set instance passwords in environment variables:"
        )
        console.print("  export JDX1_PASSWORD='your-password'")
        console.print("  export JDX2_PASSWORD='your-password'")
        console.print("  # ... etc\n")

    def save(self, config: FRSPlatformConfig) -> None:
        """
        Save configuration to file

        Args:
            config: Configuration to save
        """
        # Ensure config directory exists
        self.config_path.parent.mkdir(parents=True, exist_ok=True)

        # Convert to dict and save
        config_dict = config.model_dump(mode="python", exclude_none=True)

        with open(self.config_path, "w") as f:
            yaml.dump(config_dict, f, default_flow_style=False, sort_keys=False)

        console.print(f"[green]✓ Configuration saved to {self.config_path}[/green]")

    def validate(self) -> bool:
        """
        Validate current configuration

        Returns:
            True if configuration is valid, False otherwise
        """
        try:
            config = self.load()

            # Check if instances are configured
            if not config.instances:
                console.print("[red]✗ No instances configured[/red]")
                return False

            # Check if required directories exist
            paths_to_check = [
                config.paths.backups,
                config.paths.exports,
                config.paths.reports,
                config.paths.temp
            ]

            missing_dirs = []
            for path in paths_to_check:
                if not path.exists():
                    missing_dirs.append(path)

            if missing_dirs:
                console.print("[yellow]Warning: Some directories don't exist:[/yellow]")
                for path in missing_dirs:
                    console.print(f"  - {path}")
                console.print("\n[dim]These will be created automatically when needed.[/dim]")

            console.print("[green]✓ Configuration is valid[/green]")
            return True

        except Exception as e:
            console.print(f"[red]✗ Configuration validation failed: {e}[/red]")
            return False

    def get_config(self) -> FRSPlatformConfig:
        """
        Get loaded configuration

        Returns:
            Configuration object

        Raises:
            RuntimeError: If configuration hasn't been loaded
        """
        if self._config is None:
            raise RuntimeError("Configuration not loaded. Call load() first.")
        return self._config

    def ensure_directories(self) -> None:
        """Create required directories if they don't exist"""
        if self._config is None:
            self.load()

        dirs_to_create = [
            self._config.paths.backups,
            self._config.paths.exports,
            self._config.paths.reports,
            self._config.paths.temp
        ]

        for directory in dirs_to_create:
            if not directory.exists():
                directory.mkdir(parents=True, exist_ok=True)
                console.print(f"[dim]Created directory: {directory}[/dim]")


# Global config loader instance
_config_loader: Optional[ConfigLoader] = None


def get_config_loader(config_path: Optional[Path] = None) -> ConfigLoader:
    """
    Get global configuration loader instance

    Args:
        config_path: Optional custom config path

    Returns:
        ConfigLoader instance
    """
    global _config_loader
    if _config_loader is None or config_path is not None:
        _config_loader = ConfigLoader(config_path)
    return _config_loader


def get_config() -> FRSPlatformConfig:
    """
    Get loaded configuration

    Returns:
        Configuration object
    """
    loader = get_config_loader()
    if loader._config is None:
        loader.load(create_if_missing=False)
    return loader.get_config()
