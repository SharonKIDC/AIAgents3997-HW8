"""Base exception classes for the tenant management system.

Provides a hierarchy of custom exceptions for different error scenarios,
enabling precise error handling and meaningful error messages.
"""


class TenantManagementError(Exception):
    """Base exception for all tenant management system errors."""

    def __init__(self, message: str, details: dict = None):
        """Initialize exception with message and optional details.

        Args:
            message: Human-readable error message
            details: Optional dictionary of additional error context
        """
        super().__init__(message)
        self.message = message
        self.details = details or {}

    def __str__(self) -> str:
        """Return string representation of exception."""
        if self.details:
            return f"{self.message} | Details: {self.details}"
        return self.message


class ConfigurationError(TenantManagementError):
    """Exception raised for configuration-related errors.

    Examples:
        - Missing required configuration fields
        - Invalid configuration values
        - Failed to load configuration files
    """


class DatabaseError(TenantManagementError):
    """Exception raised for database operation errors.

    Examples:
        - Failed to read/write Excel file
        - Data corruption detected
        - Concurrent access conflicts
    """


class ValidationError(TenantManagementError):
    """Exception raised for data validation errors.

    Examples:
        - Invalid building number
        - Invalid apartment number
        - Missing required tenant fields
        - Data type mismatches
    """


class NotFoundError(TenantManagementError):
    """Exception raised when requested resource is not found.

    Examples:
        - Tenant not found
        - Building not found
        - Apartment not found
    """
