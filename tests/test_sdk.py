"""Tests for SDK client."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import date

from src.sdk import TenantSDK
from src.sdk.client import TenantInfo, BuildingInfo
from src.communication import MCPResponse
from src.exceptions import ValidationError


class TestTenantInfo:
    """Tests for TenantInfo dataclass."""

    def test_tenant_info_creation(self):
        """Test tenant info creation."""
        tenant = TenantInfo(
            building_number=11,
            apartment_number=1,
            first_name="John",
            last_name="Doe",
            phone="0501234567",
            is_owner=True,
        )
        assert tenant.building_number == 11
        assert tenant.full_name == "John Doe"

    def test_tenant_info_with_optional_fields(self):
        """Test tenant info with optional fields."""
        tenant = TenantInfo(
            building_number=13,
            apartment_number=5,
            first_name="Jane",
            last_name="Smith",
            phone="0507654321",
            is_owner=False,
            move_in_date=date(2024, 1, 15),
            storage_number=5,
            parking_slot_1=10,
        )
        assert tenant.move_in_date == date(2024, 1, 15)
        assert tenant.parking_slot_1 == 10


class TestBuildingInfo:
    """Tests for BuildingInfo dataclass."""

    def test_building_info_creation(self):
        """Test building info creation."""
        building = BuildingInfo(
            number=11, total_apartments=17, occupied=15, vacant=2, occupancy_rate=88.2
        )
        assert building.number == 11
        assert building.vacant == 2


class TestTenantSDK:
    """Tests for TenantSDK."""

    @pytest.fixture
    def mock_client(self):
        """Create mock MCP client."""
        with patch("src.sdk.client.MCPHttpClient") as mock:
            client_instance = MagicMock()
            mock.return_value = client_instance
            yield client_instance

    @pytest.fixture
    def sdk(self, mock_client):
        """Create SDK with mock client."""
        return TenantSDK(base_url="http://test:8000")

    def test_sdk_initialization(self, mock_client):
        """Test SDK initialization."""
        sdk = TenantSDK(base_url="http://localhost:9000", timeout=15)
        assert sdk is not None

    def test_create_tenant(self, sdk, mock_client):
        """Test tenant creation."""
        mock_client.invoke_tool.return_value = MCPResponse(
            success=True, data={"building_number": 11, "apartment_number": 1}
        )
        result = sdk.create_tenant(
            building=11, apartment=1, first_name="John", last_name="Doe", phone="0501234567"
        )
        assert result["building_number"] == 11
        mock_client.invoke_tool.assert_called_once()

    def test_create_tenant_error(self, sdk, mock_client):
        """Test tenant creation with error."""
        mock_client.invoke_tool.return_value = MCPResponse(
            success=False, error="Apartment occupied"
        )
        with pytest.raises(ValidationError):
            sdk.create_tenant(
                building=11, apartment=1, first_name="John", last_name="Doe", phone="0501234567"
            )

    def test_get_tenant(self, sdk, mock_client):
        """Test getting tenant."""
        mock_client.invoke_tool.return_value = MCPResponse(
            success=True,
            data={
                "building_number": 11,
                "apartment_number": 1,
                "first_name": "John",
                "last_name": "Doe",
                "phone": "0501234567",
                "is_owner": True,
                "move_in_date": "2024-01-15",
            },
        )
        tenant = sdk.get_tenant(11, 1)
        assert tenant is not None
        assert tenant.first_name == "John"
        assert tenant.move_in_date == date(2024, 1, 15)

    def test_get_tenant_not_found(self, sdk, mock_client):
        """Test getting non-existent tenant."""
        mock_client.invoke_tool.return_value = MCPResponse(success=False)
        tenant = sdk.get_tenant(11, 99)
        assert tenant is None

    def test_update_tenant(self, sdk, mock_client):
        """Test tenant update."""
        mock_client.invoke_tool.return_value = MCPResponse(success=True, data={"updated": True})
        result = sdk.update_tenant(11, 1, phone="0509999999")
        assert result["updated"] is True

    def test_end_tenancy(self, sdk, mock_client):
        """Test ending tenancy."""
        mock_client.invoke_tool.return_value = MCPResponse(success=True, data={"ended": True})
        result = sdk.end_tenancy(11, 1)
        assert result["ended"] is True

    def test_get_buildings(self, sdk, mock_client):
        """Test getting buildings."""
        mock_client.get_resource.return_value = MCPResponse(
            success=True,
            data={
                "buildings": [
                    {"number": 11, "total_apartments": 17},
                    {"number": 13, "total_apartments": 24},
                ]
            },
        )
        buildings = sdk.get_buildings()
        assert len(buildings) == 2
        assert buildings[0].number == 11

    def test_get_all_tenants(self, sdk, mock_client):
        """Test getting all tenants."""
        mock_client.get_resource.return_value = MCPResponse(
            success=True, data={"tenants": [{"name": "John"}]}
        )
        tenants = sdk.get_all_tenants()
        assert len(tenants) == 1

    def test_get_tenant_history(self, sdk, mock_client):
        """Test getting tenant history."""
        mock_client.get_resource.return_value = MCPResponse(
            success=True, data={"history": [{"tenant": "Previous"}]}
        )
        history = sdk.get_tenant_history(11, 1)
        assert len(history) == 1

    def test_get_occupancy_report(self, sdk, mock_client):
        """Test getting occupancy report prompt."""
        mock_client.generate_prompt.return_value = MCPResponse(success=True, data={"messages": []})
        response = sdk.get_occupancy_report(11)
        assert response.success is True

    def test_context_manager(self, mock_client):
        """Test context manager usage."""
        with TenantSDK() as sdk:
            assert sdk is not None
        mock_client.close.assert_called_once()
