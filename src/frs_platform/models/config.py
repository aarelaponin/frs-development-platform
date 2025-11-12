"""
Configuration Models

Pydantic models for type-safe configuration management.
"""

from pathlib import Path
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field, field_validator
from pydantic_settings import BaseSettings
import os


class InstanceCredentials(BaseModel):
    """Credentials for Joget instance access"""
    username: str = "admin"
    password: Optional[str] = None
    password_env: Optional[str] = None  # Name of env var containing password

    def get_password(self) -> str:
        """Get password from direct value or environment variable"""
        if self.password:
            return self.password
        if self.password_env:
            password = os.getenv(self.password_env)
            if password:
                return password
            raise ValueError(f"Environment variable {self.password_env} not set")
        raise ValueError("No password or password_env configured")


class JogetInstance(BaseModel):
    """Configuration for a Joget DX instance"""
    name: str
    url: str
    web_port: int
    db_port: int
    db_name: str = "jwdb"
    db_host: str = "localhost"
    db_user: str = "root"
    version: Optional[str] = None
    installation_path: Optional[Path] = None
    credentials: InstanceCredentials = Field(default_factory=InstanceCredentials)

    @property
    def base_url(self) -> str:
        """Get base URL for API calls"""
        return f"{self.url}/jw"

    @property
    def console_url(self) -> str:
        """Get admin console URL"""
        return f"{self.url}/jw/web/console/home"


class PathsConfig(BaseModel):
    """Directory paths configuration"""
    plugin_repos: List[Path] = Field(default_factory=list)
    utilities: List[Path] = Field(default_factory=list)
    backups: Path = Field(default_factory=lambda: Path.home() / ".frs-dev" / "backups")
    exports: Path = Field(default_factory=lambda: Path.home() / ".frs-dev" / "exports")
    reports: Path = Field(default_factory=lambda: Path.home() / ".frs-dev" / "reports")
    workflows: Optional[Path] = None
    temp: Path = Field(default_factory=lambda: Path.home() / ".frs-dev" / "temp")

    @field_validator('*', mode='before')
    @classmethod
    def convert_to_path(cls, v: any) -> Path:
        """Convert string paths to Path objects"""
        if isinstance(v, str):
            return Path(v).expanduser()
        if isinstance(v, list):
            return [Path(p).expanduser() if isinstance(p, str) else p for p in v]
        return v


class NotificationChannelConfig(BaseModel):
    """Configuration for a notification channel"""
    enabled: bool = True
    config: Dict[str, Any] = Field(default_factory=dict)


class NotificationsConfig(BaseModel):
    """Notifications configuration"""
    slack: Optional[NotificationChannelConfig] = None
    email: Optional[NotificationChannelConfig] = None
    webhook: Optional[NotificationChannelConfig] = None


class ValidationConfig(BaseModel):
    """Validation and safety settings"""
    require_backup: bool = True
    require_approval_for: List[str] = Field(
        default_factory=lambda: ["production_deploy", "data_migration", "plugin_update"]
    )
    risk_thresholds: Dict[str, str] = Field(
        default_factory=lambda: {
            "auto_approve": "LOW",
            "notify_only": "MEDIUM",
            "require_approval": "HIGH",
        }
    )


class WorkflowConfig(BaseModel):
    """Workflow execution settings"""
    default_timeout: int = 3600  # seconds
    rollback_on_failure: bool = True
    enable_dry_run: bool = True
    max_parallel_operations: int = 4


class FRSPlatformConfig(BaseModel):
    """Main FRS Development Platform configuration"""

    # Instance configurations
    instances: Dict[str, JogetInstance] = Field(default_factory=dict)

    # Paths
    paths: PathsConfig = Field(default_factory=PathsConfig)

    # Notifications
    notifications: NotificationsConfig = Field(default_factory=NotificationsConfig)

    # Validation settings
    validation: ValidationConfig = Field(default_factory=ValidationConfig)

    # Workflow settings
    workflows: WorkflowConfig = Field(default_factory=WorkflowConfig)

    # Logging
    log_level: str = "INFO"
    log_file: Optional[Path] = None

    def get_instance(self, name: str) -> JogetInstance:
        """Get instance configuration by name"""
        if name not in self.instances:
            raise ValueError(f"Instance '{name}' not found in configuration")
        return self.instances[name]

    def list_instances(self) -> List[str]:
        """Get list of configured instance names"""
        return list(self.instances.keys())


class EnvironmentSettings(BaseSettings):
    """Environment-specific settings loaded from environment variables"""

    # Configuration file path
    frs_dev_config: Path = Field(
        default=Path.home() / ".frs-dev" / "config.yaml",
        alias="FRS_DEV_CONFIG"
    )

    # Log level override
    frs_dev_log_level: Optional[str] = Field(default=None, alias="FRS_DEV_LOG_LEVEL")

    # Instance passwords (can be set via environment)
    jdx1_password: Optional[str] = Field(default=None, alias="JDX1_PASSWORD")
    jdx2_password: Optional[str] = Field(default=None, alias="JDX2_PASSWORD")
    jdx3_password: Optional[str] = Field(default=None, alias="JDX3_PASSWORD")
    jdx4_password: Optional[str] = Field(default=None, alias="JDX4_PASSWORD")
    jdx5_password: Optional[str] = Field(default=None, alias="JDX5_PASSWORD")
    jdx6_password: Optional[str] = Field(default=None, alias="JDX6_PASSWORD")

    # Notification credentials
    slack_webhook_url: Optional[str] = Field(default=None, alias="SLACK_WEBHOOK_URL")
    email_smtp_password: Optional[str] = Field(default=None, alias="EMAIL_SMTP_PASSWORD")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
