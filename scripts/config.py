"""Configuration loading module for File Organizer."""
import os
import yaml
from pathlib import Path
from typing import Any, Dict, Optional

# Default config paths
DEFAULT_CONFIG_DIR = Path.home() / ".file-organizer"
DEFAULT_RULES_DIR = DEFAULT_CONFIG_DIR / "rules"
DEFAULT_LOGS_DIR = DEFAULT_CONFIG_DIR / "logs"
DEFAULT_CONFIG_FILE = DEFAULT_CONFIG_DIR / "config.yaml"


class Config:
    """Configuration manager for File Organizer."""

    def __init__(self, config_dir: Optional[Path] = None):
        self.config_dir = config_dir or DEFAULT_CONFIG_DIR
        self.rules_dir = DEFAULT_RULES_DIR
        self.logs_dir = DEFAULT_LOGS_DIR
        self.config_file = DEFAULT_CONFIG_FILE
        self._config: Dict[str, Any] = {}

    def ensure_directories(self) -> None:
        """Create necessary directories if they don't exist."""
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.rules_dir.mkdir(parents=True, exist_ok=True)
        self.logs_dir.mkdir(parents=True, exist_ok=True)

    def load(self) -> Dict[str, Any]:
        """Load configuration from file."""
        if self.config_file.exists():
            with open(self.config_file, "r", encoding="utf-8") as f:
                self._config = yaml.safe_load(f) or {}
        return self._config

    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by key."""
        return self._config.get(key, default)

    def save(self, config: Dict[str, Any]) -> None:
        """Save configuration to file."""
        self.ensure_directories()
        with open(self.config_file, "w", encoding="utf-8") as f:
            yaml.safe_dump(config, f, allow_unicode=True, default_flow_style=False)
        self._config = config

    @property
    def dry_run(self) -> bool:
        """Check if dry run mode is enabled."""
        return self.get("dry_run", True)

    @dry_run.setter
    def dry_run(self, value: bool) -> None:
        """Set dry run mode."""
        self._config["dry_run"] = value
        self.save(self._config)


def get_config(config_dir: Optional[Path] = None) -> Config:
    """Get configuration instance."""
    config = Config(config_dir)
    config.ensure_directories()
    config.load()
    return config
