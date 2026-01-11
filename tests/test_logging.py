"""Tests for logging configuration."""

import logging
import tempfile
from pathlib import Path

from src.logging_config import get_logger, setup_logging


class TestLoggingSetup:
    """Test suite for logging configuration."""

    def test_setup_logging_default(self):
        """Test default logging setup."""
        setup_logging()
        root_logger = logging.getLogger()
        assert root_logger.level == logging.INFO

    def test_setup_logging_custom_level(self):
        """Test logging setup with custom level."""
        setup_logging(level="DEBUG")
        root_logger = logging.getLogger()
        assert root_logger.level == logging.DEBUG

    def test_setup_logging_with_file(self):
        """Test logging setup with file output."""
        with tempfile.TemporaryDirectory() as temp_dir:
            log_file = Path(temp_dir) / "test.log"
            setup_logging(level="INFO", log_file=str(log_file))

            logger = get_logger(__name__)
            logger.info("Test message")

            assert log_file.exists()
            content = log_file.read_text()
            assert "Test message" in content

    def test_get_logger(self):
        """Test getting logger instance."""
        logger = get_logger("test_module")
        assert isinstance(logger, logging.Logger)
        assert logger.name == "test_module"
