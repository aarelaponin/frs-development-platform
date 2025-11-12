"""
Joget API Client

REST API client for Joget DX instances.
"""

from typing import Optional, Dict, List, Any
from pathlib import Path
import requests
from requests.auth import HTTPBasicAuth
import logging

from frs_platform.models.config import JogetInstance

logger = logging.getLogger(__name__)


class JogetAPIClient:
    """REST API client for Joget DX"""

    def __init__(self, instance: JogetInstance):
        """
        Initialize Joget API client

        Args:
            instance: Joget instance configuration
        """
        self.instance = instance
        self.base_url = instance.base_url
        self.session = requests.Session()
        self.session.auth = HTTPBasicAuth(
            instance.credentials.username,
            instance.credentials.get_password()
        )
        self.session.headers.update({
            "User-Agent": "FRS-Platform/0.1.0"
        })

    def test_connection(self, timeout: int = 10) -> bool:
        """
        Test if instance is reachable

        Args:
            timeout: Request timeout in seconds

        Returns:
            True if instance is reachable
        """
        try:
            response = self.session.get(
                f"{self.base_url}/",
                timeout=timeout,
                allow_redirects=True
            )
            return response.status_code in [200, 302]
        except requests.exceptions.RequestException as e:
            logger.debug(f"Connection test failed: {e}")
            return False

    def get_system_info(self) -> Dict[str, Any]:
        """
        Get system information

        Returns:
            System information dict
        """
        try:
            response = self.session.get(
                f"{self.base_url}/web/json/monitoring/info",
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.warning(f"Failed to get system info: {e}")
            return {}

    def list_applications(self) -> List[Dict[str, Any]]:
        """
        List all applications

        Returns:
            List of application info dicts
        """
        try:
            response = self.session.get(
                f"{self.base_url}/web/json/apps/published/list",
                timeout=30
            )
            response.raise_for_status()
            data = response.json()
            return data.get("data", [])
        except Exception as e:
            logger.error(f"Failed to list applications: {e}")
            raise

    def get_application(self, app_id: str) -> Optional[Dict[str, Any]]:
        """
        Get application information

        Args:
            app_id: Application ID

        Returns:
            Application info dict or None if not found
        """
        try:
            response = self.session.get(
                f"{self.base_url}/web/json/console/app/{app_id}",
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                return None
            raise
        except Exception as e:
            logger.error(f"Failed to get application {app_id}: {e}")
            raise

    def export_application(self, app_id: str, output_path: Path) -> None:
        """
        Export application as ZIP

        Args:
            app_id: Application ID
            output_path: Path to save exported ZIP
        """
        try:
            response = self.session.get(
                f"{self.base_url}/web/json/console/app/{app_id}/export",
                timeout=60,
                stream=True
            )
            response.raise_for_status()

            # Save to file
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

            logger.info(f"Exported {app_id} to {output_path}")

        except Exception as e:
            logger.error(f"Failed to export application {app_id}: {e}")
            raise

    def import_application(
        self,
        app_zip_path: Path,
        overwrite: bool = False
    ) -> Dict[str, Any]:
        """
        Import application from ZIP

        Args:
            app_zip_path: Path to application ZIP file
            overwrite: Whether to overwrite existing application

        Returns:
            Import result dict
        """
        try:
            with open(app_zip_path, "rb") as f:
                files = {"appZip": (app_zip_path.name, f, "application/zip")}
                data = {"overwrite": str(overwrite).lower()}

                response = self.session.post(
                    f"{self.base_url}/web/json/console/app/import",
                    files=files,
                    data=data,
                    timeout=120
                )
                response.raise_for_status()
                return response.json()

        except Exception as e:
            logger.error(f"Failed to import application from {app_zip_path}: {e}")
            raise

    def list_plugins(self) -> List[Dict[str, Any]]:
        """
        List installed plugins

        Returns:
            List of plugin info dicts
        """
        try:
            response = self.session.get(
                f"{self.base_url}/web/json/console/setting/plugin/list/available",
                timeout=30
            )
            response.raise_for_status()
            data = response.json()
            return data.get("data", [])
        except Exception as e:
            logger.error(f"Failed to list plugins: {e}")
            raise

    def get_health_status(self) -> Dict[str, Any]:
        """
        Get instance health status

        Returns:
            Health status dict with various metrics
        """
        health = {
            "reachable": False,
            "authenticated": False,
            "version": None,
            "applications": 0,
            "plugins": 0
        }

        try:
            # Test basic connectivity
            health["reachable"] = self.test_connection()

            if health["reachable"]:
                # Test authentication by listing apps
                try:
                    apps = self.list_applications()
                    health["authenticated"] = True
                    health["applications"] = len(apps)
                except Exception:
                    health["authenticated"] = False

                # Get system info
                sys_info = self.get_system_info()
                if sys_info:
                    health["version"] = sys_info.get("version")

                # Count plugins
                if health["authenticated"]:
                    try:
                        plugins = self.list_plugins()
                        health["plugins"] = len(plugins)
                    except Exception:
                        pass

        except Exception as e:
            logger.debug(f"Health check failed: {e}")

        return health
