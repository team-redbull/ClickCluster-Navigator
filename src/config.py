"""
Configuration loader for the application.
"""
import json
import os
from pathlib import Path
from typing import Dict, Any

# Default configuration
DEFAULT_CONFIG = {
    "segments_manager": {
        "url": "http://0.0.0.0:9000",
        "sync_interval_seconds": 300,
        "insecure_tls_verify": False,
        "segment_types": ["HC", "MCE"]
    },
    "application": {
        "host": "0.0.0.0",
        "port": 8000,
        "default_domain": "example.com"
    },
    "dns": {
        "server": "8.8.8.8",
        "timeout_seconds": 3,
        "resolution_path": "ingress.{cluster_name}.{domain_name}"
    },
    "auth": {
        "admin_username": "admin",
        "admin_password": "Password1"
    }
}

# Path to config file
CONFIG_FILE = Path(__file__).parent.parent / "config.json"


class Config:
    """Configuration class for the application."""

    def __init__(self):
        self._config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file or use defaults."""
        if CONFIG_FILE.exists():
            try:
                with open(CONFIG_FILE, 'r') as f:
                    config = json.load(f)
                print(f"✓ Configuration loaded from {CONFIG_FILE}")
                return config
            except Exception as e:
                print(f"⚠ Failed to load config file: {e}, using defaults")
                return DEFAULT_CONFIG
        else:
            print(f"⚠ Config file not found, using defaults")
            return DEFAULT_CONFIG

    @property
    def segments_manager_url(self) -> str:
        """Get Segments Manager API URL from environment or config."""
        return os.getenv("SEGMENTS_MANAGER_URL", self._config["segments_manager"]["url"])

    @property
    def sync_interval(self) -> int:
        """Get sync interval in seconds."""
        return self._config["segments_manager"]["sync_interval_seconds"]

    @property
    def app_host(self) -> str:
        """Get application host."""
        return self._config["application"]["host"]

    @property
    def app_port(self) -> int:
        """Get application port."""
        return self._config["application"]["port"]

    @property
    def admin_username(self) -> str:
        """Get admin username from environment or config."""
        return os.getenv("ADMIN_USERNAME", self._config["auth"]["admin_username"])

    @property
    def admin_password(self) -> str:
        """Get admin password from environment or config."""
        return os.getenv("ADMIN_PASSWORD", self._config["auth"]["admin_password"])

    @property
    def app_title(self) -> str:
        """Get application title from environment or default."""
        return os.getenv("APP_TITLE", "OpenShift Cluster Navigator")

    @property
    def default_domain(self) -> str:
        """Get default domain from environment or config."""
        return os.getenv("DEFAULT_DOMAIN", self._config.get("application", {}).get("default_domain", "example.com"))

    @property
    def dns_server(self) -> str:
        """Get DNS server from environment or config."""
        return os.getenv("DNS_SERVER", self._config.get("dns", {}).get("server", "8.8.8.8"))

    @property
    def dns_timeout(self) -> int:
        """Get DNS timeout in seconds from environment or config."""
        timeout_str = os.getenv("DNS_TIMEOUT", str(self._config.get("dns", {}).get("timeout_seconds", 3)))
        try:
            return int(timeout_str)
        except ValueError:
            return 3

    @property
    def dns_resolution_path(self) -> str:
        """Get DNS resolution path template from environment or config."""
        return os.getenv("DNS_RESOLUTION_PATH", self._config.get("dns", {}).get("resolution_path", "ingress.{cluster_name}.{domain_name}"))

    @property
    def segments_manager_insecure_tls_verify(self) -> bool:
        """Get Segments Manager insecure TLS verification setting (verify=False when True)."""
        return self._config.get("segments_manager", {}).get("insecure_tls_verify", False)

    @property
    def segment_types(self) -> list:
        """Get the list of segment types to sync from Segments Manager (e.g. HC, MCE)."""
        env_value = os.getenv("SEGMENT_TYPES")
        if env_value:
            return [t.strip() for t in env_value.split(",") if t.strip()]
        return self._config.get("segments_manager", {}).get("segment_types", ["HC", "MCE"])


# Global config instance
config = Config()
