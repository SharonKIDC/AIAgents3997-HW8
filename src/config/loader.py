"""Configuration loader for application settings.

This module provides centralized configuration loading from YAML files
and environment variables, ensuring no hardcoded values in the codebase.
"""

import logging
import os
from pathlib import Path
from typing import Any

import yaml
from dotenv import load_dotenv

logger = logging.getLogger(__name__)


class ConfigLoader:
    """Loads and manages application configuration.

    Loads configuration from:
    1. config.yaml for application settings
    2. .env for sensitive environment variables
    """

    def __init__(self, config_path: str = "config.yaml", env_path: str = ".env"):
        """Initialize configuration loader.

        Args:
            config_path: Path to YAML configuration file
            env_path: Path to environment variables file
        """
        self.config_path = Path(config_path)
        self.env_path = Path(env_path)
        self._config: dict[str, Any] = {}
        self._load_configuration()

    def _load_configuration(self) -> None:
        """Load configuration from YAML and environment files."""
        # Load environment variables first
        if self.env_path.exists():
            load_dotenv(self.env_path)
            logger.info("Loaded environment variables from %s", self.env_path)
        else:
            logger.warning("Environment file not found: %s", self.env_path)

        # Load YAML configuration
        if self.config_path.exists():
            with open(self.config_path, encoding="utf-8") as config_file:
                self._config = yaml.safe_load(config_file) or {}
            logger.info("Loaded configuration from %s", self.config_path)
        else:
            logger.warning("Configuration file not found: %s", self.config_path)
            self._config = {}

        # Override with environment variables where specified
        self._apply_env_overrides()

    def _apply_env_overrides(self) -> None:
        """Apply environment variable overrides to configuration."""
        self._config = self._substitute_env_vars(self._config)

    def _substitute_env_vars(self, obj: Any) -> Any:
        """Recursively substitute ${VAR} patterns with environment variables."""
        if isinstance(obj, dict):
            return {k: self._substitute_env_vars(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._substitute_env_vars(item) for item in obj]
        elif isinstance(obj, str) and obj.startswith("${") and obj.endswith("}"):
            var_name = obj[2:-1]
            return os.getenv(var_name, obj)
        return obj

    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by key.

        Supports nested keys with dot notation (e.g., 'database.backup_path').

        Args:
            key: Configuration key (supports dot notation)
            default: Default value if key not found

        Returns:
            Configuration value or default
        """
        keys = key.split(".")
        value = self._config

        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
                if value is None:
                    return default
            else:
                return default

        return value

    def get_all(self) -> dict[str, Any]:
        """Get all configuration as dictionary.

        Returns:
            Complete configuration dictionary
        """
        return self._config.copy()

    def reload(self) -> None:
        """Reload configuration from files."""
        self._load_configuration()
        logger.info("Configuration reloaded")


# Global configuration instance
_CONFIG_INSTANCE: ConfigLoader = None


def get_config() -> ConfigLoader:
    """Get global configuration instance.

    Returns:
        Global ConfigLoader instance
    """
    global _CONFIG_INSTANCE  # pylint: disable=global-statement
    if _CONFIG_INSTANCE is None:
        _CONFIG_INSTANCE = ConfigLoader()
    return _CONFIG_INSTANCE
