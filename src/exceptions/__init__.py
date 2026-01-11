"""Custom exceptions package."""

from src.exceptions.base import (
    CommunicationError,
    ConfigurationError,
    DatabaseError,
    NotFoundError,
    TenantManagementError,
    ValidationError,
)

__all__ = [
    "TenantManagementError",
    "ConfigurationError",
    "DatabaseError",
    "ValidationError",
    "NotFoundError",
    "CommunicationError",
]
