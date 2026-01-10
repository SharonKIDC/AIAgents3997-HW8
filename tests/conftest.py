"""Pytest configuration and fixtures."""

import pytest


@pytest.fixture
def sample_tenant_data():
    """Sample tenant data for testing."""
    return {
        "building": "11",
        "apartment": "101",
        "owner_name": "John Doe",
        "tenant_name": "Jane Smith",
        "move_in_date": "2024-01-01",
        "parking_access": True,
    }
