"""Tests for web UI backend."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import date

from fastapi.testclient import TestClient

from src.web_ui.backend import create_web_app
from src.sdk.client import TenantInfo, BuildingInfo
from src.communication import MCPResponse


@pytest.fixture
def mock_sdk():
    """Create mock SDK."""
    with patch("src.web_ui.routes.TenantSDK") as mock:
        sdk_instance = MagicMock()
        mock.return_value = sdk_instance
        sdk_instance.__enter__ = Mock(return_value=sdk_instance)
        sdk_instance.__exit__ = Mock(return_value=False)
        yield sdk_instance


@pytest.fixture
def client(mock_sdk):
    """Create test client."""
    app = create_web_app()
    return TestClient(app)


class TestWebUIBackend:
    """Tests for web UI backend."""

    def test_health_check(self, client):
        """Test health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"

    def test_list_buildings(self, client, mock_sdk):
        """Test list buildings endpoint."""
        mock_sdk.get_buildings.return_value = [
            BuildingInfo(number=11, total_apartments=17),
            BuildingInfo(number=13, total_apartments=24)
        ]
        response = client.get("/api/buildings")
        assert response.status_code == 200
        data = response.json()
        assert len(data["buildings"]) == 2

    def test_get_building(self, client, mock_sdk):
        """Test get building endpoint."""
        mock_sdk.get_building_occupancy.return_value = BuildingInfo(
            number=11, total_apartments=17, occupied=15, vacant=2, occupancy_rate=88.2
        )
        response = client.get("/api/buildings/11")
        assert response.status_code == 200
        data = response.json()
        assert data["number"] == 11
        assert data["occupied"] == 15

    def test_get_building_not_found(self, client, mock_sdk):
        """Test get building not found."""
        mock_sdk.get_building_occupancy.return_value = None
        response = client.get("/api/buildings/99")
        assert response.status_code == 404

    def test_list_tenants(self, client, mock_sdk):
        """Test list tenants endpoint."""
        mock_sdk.get_all_tenants.return_value = [{"name": "John Doe"}]
        response = client.get("/api/tenants")
        assert response.status_code == 200
        assert len(response.json()["tenants"]) == 1

    def test_list_tenants_by_building(self, client, mock_sdk):
        """Test list tenants filtered by building."""
        mock_sdk.get_all_tenants.return_value = []
        response = client.get("/api/tenants?building=11")
        assert response.status_code == 200
        mock_sdk.get_all_tenants.assert_called_with(11)

    def test_get_tenant(self, client, mock_sdk):
        """Test get tenant endpoint."""
        mock_sdk.get_tenant.return_value = TenantInfo(
            building_number=11, apartment_number=1,
            first_name="John", last_name="Doe",
            phone="0501234567", is_owner=True,
            move_in_date=date(2024, 1, 15)
        )
        response = client.get("/api/tenants/11/1")
        assert response.status_code == 200
        data = response.json()
        assert data["full_name"] == "John Doe"

    def test_get_tenant_not_found(self, client, mock_sdk):
        """Test get tenant not found returns exists=False."""
        mock_sdk.get_tenant.return_value = None
        response = client.get("/api/tenants/11/99")
        assert response.status_code == 200
        assert response.json()["exists"] is False

    def test_create_tenant(self, client, mock_sdk):
        """Test create tenant endpoint."""
        mock_sdk.get_tenant.return_value = None  # No existing tenant
        mock_sdk.create_tenant.return_value = {"success": True}
        response = client.post("/api/tenants", json={
            "building_number": 11,
            "apartment_number": 1,
            "first_name": "John",
            "last_name": "Doe",
            "phone": "0501234567",
            "is_owner": True
        })
        assert response.status_code == 200
        assert response.json()["success"] is True

    def test_update_tenant(self, client, mock_sdk):
        """Test update tenant endpoint."""
        mock_sdk.update_tenant.return_value = {"updated": True}
        response = client.patch("/api/tenants/11/1", json={
            "phone": "0509999999"
        })
        assert response.status_code == 200

    def test_end_tenancy(self, client, mock_sdk):
        """Test end tenancy endpoint."""
        mock_sdk.end_tenancy.return_value = {"ended": True}
        response = client.delete("/api/tenants/11/1")
        assert response.status_code == 200

    def test_get_tenant_history(self, client, mock_sdk):
        """Test get tenant history endpoint."""
        mock_sdk.get_tenant_history.return_value = [{"tenant": "Previous"}]
        response = client.get("/api/tenants/11/1/history")
        assert response.status_code == 200
        assert len(response.json()["history"]) == 1

    def test_get_occupancy_report(self, client, mock_sdk):
        """Test occupancy report endpoint."""
        mock_sdk.get_occupancy_report.return_value = MCPResponse(
            success=True, data={"messages": []}
        )
        response = client.get("/api/reports/occupancy")
        assert response.status_code == 200

    def test_get_tenant_list_report(self, client, mock_sdk):
        """Test tenant list report endpoint."""
        mock_sdk.get_tenant_list_report.return_value = MCPResponse(
            success=True, data={"messages": []}
        )
        response = client.get("/api/reports/tenant-list?include_contacts=true")
        assert response.status_code == 200
