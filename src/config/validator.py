"""Configuration validator for application settings.

Validates configuration structure and required fields to ensure
system reliability and prevent runtime errors from misconfiguration.
"""

import logging
from typing import Any

logger = logging.getLogger(__name__)


class ConfigValidator:
    """Validates application configuration structure and values."""

    REQUIRED_FIELDS = {
        "application": ["name", "version", "environment"],
        "database": ["file_path", "backup_path", "backup_retention_days"],
        "server": ["host", "port"],
        "logging": ["level", "format"],
    }

    VALID_ENVIRONMENTS = ["development", "production", "testing"]
    VALID_LOG_LEVELS = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]

    @classmethod
    def validate(cls, config: dict[str, Any]) -> list[str]:
        """Validate configuration dictionary.

        Args:
            config: Configuration dictionary to validate

        Returns:
            List of validation error messages (empty if valid)
        """
        errors = []

        # Check required sections
        errors.extend(cls._validate_required_sections(config))

        # Validate specific fields
        errors.extend(cls._validate_environment(config))
        errors.extend(cls._validate_logging(config))
        errors.extend(cls._validate_server(config))
        errors.extend(cls._validate_database(config))

        if errors:
            logger.warning("Configuration validation found %d errors", len(errors))
        else:
            logger.info("Configuration validation passed")

        return errors

    @classmethod
    def _validate_required_sections(cls, config: dict[str, Any]) -> list[str]:
        """Validate presence of required configuration sections."""
        errors = []
        for section, fields in cls.REQUIRED_FIELDS.items():
            if section not in config:
                errors.append(f"Missing required section: {section}")
                continue

            for field in fields:
                if field not in config[section]:
                    errors.append(f"Missing required field: {section}.{field}")

        return errors

    @classmethod
    def _validate_environment(cls, config: dict[str, Any]) -> list[str]:
        """Validate environment setting."""
        errors = []
        if "application" in config:
            env = config["application"].get("environment")
            if env and env not in cls.VALID_ENVIRONMENTS:
                errors.append(
                    f"Invalid environment: {env}. " f"Must be one of {cls.VALID_ENVIRONMENTS}"
                )
        return errors

    @classmethod
    def _validate_logging(cls, config: dict[str, Any]) -> list[str]:
        """Validate logging configuration."""
        errors = []
        if "logging" in config:
            level = config["logging"].get("level")
            if level and level not in cls.VALID_LOG_LEVELS:
                errors.append(
                    f"Invalid log level: {level}. " f"Must be one of {cls.VALID_LOG_LEVELS}"
                )
        return errors

    @classmethod
    def _validate_server(cls, config: dict[str, Any]) -> list[str]:
        """Validate server configuration."""
        errors = []
        if "server" in config:
            port = config["server"].get("port")
            if port is not None:
                if not isinstance(port, int):
                    errors.append(f"Invalid port type: {type(port)}. Must be int")
                elif port < 1 or port > 65535:
                    errors.append(f"Invalid port number: {port}. Must be 1-65535")
        return errors

    @classmethod
    def _validate_database(cls, config: dict[str, Any]) -> list[str]:
        """Validate database configuration."""
        errors = []
        if "database" in config:
            retention = config["database"].get("backup_retention_days")
            if retention is not None:
                if not isinstance(retention, int):
                    errors.append(f"Invalid backup_retention_days type: {type(retention)}")
                elif retention < 1:
                    errors.append(f"Invalid backup_retention_days: {retention}. Must be >= 1")
        return errors
