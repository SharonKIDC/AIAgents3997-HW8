"""Tests for configuration management."""

import os
import tempfile

import pytest
import yaml

from src.config.loader import ConfigLoader
from src.config.validator import ConfigValidator


class TestConfigLoader:
    """Test suite for ConfigLoader."""

    @pytest.fixture
    def temp_config_file(self):
        """Create temporary config file for testing."""
        config_data = {
            "application": {
                "name": "test-app",
                "version": "1.0.0",
                "environment": "testing",
            },
            "database": {
                "file_path": "data/test.xlsx",
                "backup_path": "data/backups",
                "backup_retention_days": 7,
            },
            "server": {"host": "localhost", "port": 8000},
            "logging": {"level": "INFO", "format": "simple"},
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as temp_file:
            yaml.dump(config_data, temp_file)
            temp_path = temp_file.name

        yield temp_path

        # Cleanup
        os.unlink(temp_path)

    def test_load_configuration_success(self, temp_config_file):
        """Test successful configuration loading."""
        loader = ConfigLoader(config_path=temp_config_file, env_path=".env.example")
        assert loader.get("application.name") == "test-app"
        assert loader.get("application.version") == "1.0.0"

    def test_get_nested_value(self, temp_config_file):
        """Test retrieving nested configuration values."""
        loader = ConfigLoader(config_path=temp_config_file, env_path=".env.example")
        assert loader.get("server.port") == 8000
        assert loader.get("database.backup_retention_days") == 7

    def test_get_with_default(self, temp_config_file):
        """Test get() with default value for missing keys."""
        loader = ConfigLoader(config_path=temp_config_file, env_path=".env.example")
        assert loader.get("nonexistent.key", "default") == "default"

    def test_get_all(self, temp_config_file):
        """Test getting complete configuration."""
        loader = ConfigLoader(config_path=temp_config_file, env_path=".env.example")
        all_config = loader.get_all()
        assert "application" in all_config
        assert "database" in all_config
        assert "server" in all_config


class TestConfigValidator:
    """Test suite for ConfigValidator."""

    def test_validate_valid_config(self):
        """Test validation of valid configuration."""
        config = {
            "application": {
                "name": "test",
                "version": "1.0",
                "environment": "development",
            },
            "database": {
                "file_path": "data/test.xlsx",
                "backup_path": "backups",
                "backup_retention_days": 7,
            },
            "server": {"host": "localhost", "port": 8000},
            "logging": {"level": "INFO", "format": "simple"},
        }
        errors = ConfigValidator.validate(config)
        assert len(errors) == 0

    def test_validate_missing_section(self):
        """Test validation with missing section."""
        config = {"application": {"name": "test", "version": "1.0"}}
        errors = ConfigValidator.validate(config)
        assert len(errors) > 0
        assert any("Missing required section" in err for err in errors)

    def test_validate_missing_field(self):
        """Test validation with missing required field."""
        config = {
            "application": {"name": "test"},
            "database": {
                "file_path": "data/test.xlsx",
                "backup_path": "backups",
                "backup_retention_days": 7,
            },
            "server": {"host": "localhost", "port": 8000},
            "logging": {"level": "INFO", "format": "simple"},
        }
        errors = ConfigValidator.validate(config)
        assert any("application.version" in err for err in errors)

    def test_validate_invalid_environment(self):
        """Test validation with invalid environment value."""
        config = {
            "application": {
                "name": "test",
                "version": "1.0",
                "environment": "invalid",
            },
            "database": {
                "file_path": "data/test.xlsx",
                "backup_path": "backups",
                "backup_retention_days": 7,
            },
            "server": {"host": "localhost", "port": 8000},
            "logging": {"level": "INFO", "format": "simple"},
        }
        errors = ConfigValidator.validate(config)
        assert any("Invalid environment" in err for err in errors)

    def test_validate_invalid_port(self):
        """Test validation with invalid port number."""
        config = {
            "application": {
                "name": "test",
                "version": "1.0",
                "environment": "development",
            },
            "database": {
                "file_path": "data/test.xlsx",
                "backup_path": "backups",
                "backup_retention_days": 7,
            },
            "server": {"host": "localhost", "port": 99999},
            "logging": {"level": "INFO", "format": "simple"},
        }
        errors = ConfigValidator.validate(config)
        assert any("Invalid port number" in err for err in errors)
