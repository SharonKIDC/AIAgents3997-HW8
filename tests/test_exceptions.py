"""Tests for custom exceptions."""

import pytest

from src.exceptions import (
    ConfigurationError,
    DatabaseError,
    NotFoundError,
    TenantManagementError,
    ValidationError,
)


class TestExceptions:
    """Test suite for custom exceptions."""

    def test_base_exception(self):
        """Test base TenantManagementError."""
        error = TenantManagementError("Test error")
        assert str(error) == "Test error"
        assert error.message == "Test error"

    def test_exception_with_details(self):
        """Test exception with additional details."""
        details = {"field": "apartment_number", "value": 999}
        error = ValidationError("Invalid apartment", details=details)
        assert error.message == "Invalid apartment"
        assert error.details == details
        assert "Details:" in str(error)

    def test_configuration_error(self):
        """Test ConfigurationError."""
        with pytest.raises(ConfigurationError):
            raise ConfigurationError("Missing config field")

    def test_database_error(self):
        """Test DatabaseError."""
        with pytest.raises(DatabaseError):
            raise DatabaseError("Excel file not found")

    def test_validation_error(self):
        """Test ValidationError."""
        with pytest.raises(ValidationError):
            raise ValidationError("Invalid tenant data")

    def test_not_found_error(self):
        """Test NotFoundError."""
        with pytest.raises(NotFoundError):
            raise NotFoundError("Tenant not found")

    def test_exception_inheritance(self):
        """Test that all exceptions inherit from base."""
        assert issubclass(ConfigurationError, TenantManagementError)
        assert issubclass(DatabaseError, TenantManagementError)
        assert issubclass(ValidationError, TenantManagementError)
        assert issubclass(NotFoundError, TenantManagementError)
