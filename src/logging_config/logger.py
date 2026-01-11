"""Structured logging configuration for the application.

Provides centralized logging setup with support for different log levels,
formats, and output destinations based on configuration.
"""

import logging
import sys
from pathlib import Path


def setup_logging(
    level: str = "INFO",
    log_format: str | None = None,
    log_file: str | None = None,
) -> None:
    """Set up application-wide logging configuration.

    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_format: Custom log format string (uses default if None)
        log_file: Optional log file path (logs to console if None)
    """
    # Default format with timestamp, level, module, and message
    if log_format is None:
        log_format = (
            "%(asctime)s - %(name)s - %(levelname)s - "
            "%(filename)s:%(lineno)d - %(message)s"
        )

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, level.upper(), logging.INFO))

    # Remove existing handlers to avoid duplicates
    root_logger.handlers.clear()

    # Create formatter
    formatter = logging.Formatter(log_format)

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(root_logger.level)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # File handler (if specified)
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        file_handler = logging.FileHandler(log_path)
        file_handler.setLevel(root_logger.level)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)

    # Log initial message
    root_logger.info("Logging configured: level=%s", level)
    if log_file:
        root_logger.info("Logging to file: %s", log_file)


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance for a module.

    Args:
        name: Logger name (typically __name__ from calling module)

    Returns:
        Configured logger instance
    """
    return logging.getLogger(name)
