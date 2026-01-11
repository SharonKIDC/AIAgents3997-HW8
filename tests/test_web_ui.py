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


class TestValidationConfig:
    """Tests for validation configuration endpoint."""

    def test_get_validation_config(self, client):
        """Test validation config endpoint returns expected structure."""
        response = client.get("/api/config/validation")
        assert response.status_code == 200
        data = response.json()

        # Check phone config
        assert "phone" in data
        assert "min_length" in data["phone"]
        assert "max_length" in data["phone"]
        assert "pattern" in data["phone"]
        assert "pattern_description" in data["phone"]

        # Check name config
        assert "name" in data
        assert "min_length" in data["name"]
        assert "max_length" in data["name"]
        assert "pattern" in data["name"]

        # Check family_members config
        assert "family_members" in data
        assert "max_whatsapp_members" in data["family_members"]
        assert "max_palgate_members" in data["family_members"]
        assert "main_tenant_always_included" in data["family_members"]

        # Check vehicle_plate config
        assert "vehicle_plate" in data
        assert "max_length" in data["vehicle_plate"]
        assert "pattern" in data["vehicle_plate"]


class TestNameValidation:
    """Tests for name field validation."""

    def test_name_too_short(self, client, mock_sdk):
        """Test validation fails when name is too short."""
        mock_sdk.get_tenant.return_value = None
        response = client.post("/api/tenants", json={
            "building_number": 11,
            "apartment_number": 1,
            "first_name": "J",  # Too short (min 2)
            "last_name": "Doe",
            "phone": "0501234567",
            "is_owner": True
        })
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is False
        assert "first_name" in data["validation_errors"]
        assert any("at least" in err for err in data["validation_errors"]["first_name"])

    def test_last_name_too_short(self, client, mock_sdk):
        """Test validation fails when last name is too short."""
        mock_sdk.get_tenant.return_value = None
        response = client.post("/api/tenants", json={
            "building_number": 11,
            "apartment_number": 1,
            "first_name": "John",
            "last_name": "D",  # Too short
            "phone": "0501234567",
            "is_owner": True
        })
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is False
        assert "last_name" in data["validation_errors"]

    def test_name_with_invalid_characters(self, client, mock_sdk):
        """Test validation fails when name contains invalid characters."""
        mock_sdk.get_tenant.return_value = None
        response = client.post("/api/tenants", json={
            "building_number": 11,
            "apartment_number": 1,
            "first_name": "John123",  # Numbers not allowed
            "last_name": "Doe",
            "phone": "0501234567",
            "is_owner": True
        })
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is False
        assert "first_name" in data["validation_errors"]
        # Should contain pattern description error
        assert any("letters" in err.lower() for err in data["validation_errors"]["first_name"])

    def test_name_with_special_chars_fails(self, client, mock_sdk):
        """Test validation fails when name contains special characters."""
        mock_sdk.get_tenant.return_value = None
        response = client.post("/api/tenants", json={
            "building_number": 11,
            "apartment_number": 1,
            "first_name": "John@#$",
            "last_name": "Doe",
            "phone": "0501234567",
            "is_owner": True
        })
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is False
        assert "first_name" in data["validation_errors"]

    def test_name_with_hebrew_characters_valid(self, client, mock_sdk):
        """Test validation passes for Hebrew characters."""
        mock_sdk.get_tenant.return_value = None
        mock_sdk.create_tenant.return_value = {"success": True}
        response = client.post("/api/tenants", json={
            "building_number": 11,
            "apartment_number": 1,
            "first_name": "יוחנן",  # Hebrew name
            "last_name": "כהן",  # Hebrew last name
            "phone": "0501234567",
            "is_owner": True
        })
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

    def test_name_with_hyphen_valid(self, client, mock_sdk):
        """Test validation passes for hyphenated names."""
        mock_sdk.get_tenant.return_value = None
        mock_sdk.create_tenant.return_value = {"success": True}
        response = client.post("/api/tenants", json={
            "building_number": 11,
            "apartment_number": 1,
            "first_name": "Mary-Jane",
            "last_name": "O'Connor",
            "phone": "0501234567",
            "is_owner": True
        })
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

    def test_name_with_apostrophe_valid(self, client, mock_sdk):
        """Test validation passes for names with apostrophes."""
        mock_sdk.get_tenant.return_value = None
        mock_sdk.create_tenant.return_value = {"success": True}
        response = client.post("/api/tenants", json={
            "building_number": 11,
            "apartment_number": 1,
            "first_name": "John",
            "last_name": "O'Brien",
            "phone": "0501234567",
            "is_owner": True
        })
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True


class TestPhoneValidation:
    """Tests for phone field validation."""

    def test_phone_too_short(self, client, mock_sdk):
        """Test validation fails when phone is too short."""
        mock_sdk.get_tenant.return_value = None
        response = client.post("/api/tenants", json={
            "building_number": 11,
            "apartment_number": 1,
            "first_name": "John",
            "last_name": "Doe",
            "phone": "12345678",  # Too short (min 9)
            "is_owner": True
        })
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is False
        assert "phone" in data["validation_errors"]
        assert any("at least" in err for err in data["validation_errors"]["phone"])

    def test_phone_too_long(self, client, mock_sdk):
        """Test validation fails when phone is too long."""
        mock_sdk.get_tenant.return_value = None
        response = client.post("/api/tenants", json={
            "building_number": 11,
            "apartment_number": 1,
            "first_name": "John",
            "last_name": "Doe",
            "phone": "1234567890123456",  # Too long (max 15)
            "is_owner": True
        })
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is False
        assert "phone" in data["validation_errors"]
        assert any("at most" in err for err in data["validation_errors"]["phone"])

    def test_phone_with_invalid_characters(self, client, mock_sdk):
        """Test validation fails when phone contains invalid characters."""
        mock_sdk.get_tenant.return_value = None
        response = client.post("/api/tenants", json={
            "building_number": 11,
            "apartment_number": 1,
            "first_name": "John",
            "last_name": "Doe",
            "phone": "050-ABC-1234",  # Letters not allowed
            "is_owner": True
        })
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is False
        assert "phone" in data["validation_errors"]

    def test_phone_with_dashes_valid(self, client, mock_sdk):
        """Test validation passes for phone with dashes."""
        mock_sdk.get_tenant.return_value = None
        mock_sdk.create_tenant.return_value = {"success": True}
        response = client.post("/api/tenants", json={
            "building_number": 11,
            "apartment_number": 1,
            "first_name": "John",
            "last_name": "Doe",
            "phone": "050-123-4567",
            "is_owner": True
        })
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

    def test_phone_with_plus_valid(self, client, mock_sdk):
        """Test validation passes for phone with plus sign."""
        mock_sdk.get_tenant.return_value = None
        mock_sdk.create_tenant.return_value = {"success": True}
        response = client.post("/api/tenants", json={
            "building_number": 11,
            "apartment_number": 1,
            "first_name": "John",
            "last_name": "Doe",
            "phone": "+972501234567",
            "is_owner": True
        })
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

    def test_phone_with_spaces_fails(self, client, mock_sdk):
        """Test validation fails when phone contains spaces."""
        mock_sdk.get_tenant.return_value = None
        response = client.post("/api/tenants", json={
            "building_number": 11,
            "apartment_number": 1,
            "first_name": "John",
            "last_name": "Doe",
            "phone": "050 123 4567",  # Spaces not allowed
            "is_owner": True
        })
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is False
        assert "phone" in data["validation_errors"]


class TestOwnerInfoValidation:
    """Tests for owner info validation when registering renters."""

    def test_renter_without_owner_info_fails(self, client, mock_sdk):
        """Test validation fails when renter doesn't provide owner info."""
        mock_sdk.get_tenant.return_value = None
        response = client.post("/api/tenants", json={
            "building_number": 11,
            "apartment_number": 1,
            "first_name": "John",
            "last_name": "Doe",
            "phone": "0501234567",
            "is_owner": False,
            # Missing owner_info
        })
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is False
        assert "owner_info" in data["validation_errors"]
        assert any("required" in err.lower() for err in data["validation_errors"]["owner_info"])

    def test_renter_with_invalid_owner_first_name(self, client, mock_sdk):
        """Test validation fails when owner first name is invalid."""
        mock_sdk.get_tenant.return_value = None
        response = client.post("/api/tenants", json={
            "building_number": 11,
            "apartment_number": 1,
            "first_name": "John",
            "last_name": "Doe",
            "phone": "0501234567",
            "is_owner": False,
            "owner_info": {
                "first_name": "X",  # Too short
                "last_name": "Smith",
                "phone": "0509876543"
            }
        })
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is False
        assert "owner_first_name" in data["validation_errors"]

    def test_renter_with_invalid_owner_last_name(self, client, mock_sdk):
        """Test validation fails when owner last name is invalid."""
        mock_sdk.get_tenant.return_value = None
        response = client.post("/api/tenants", json={
            "building_number": 11,
            "apartment_number": 1,
            "first_name": "John",
            "last_name": "Doe",
            "phone": "0501234567",
            "is_owner": False,
            "owner_info": {
                "first_name": "Jane",
                "last_name": "S",  # Too short
                "phone": "0509876543"
            }
        })
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is False
        assert "owner_last_name" in data["validation_errors"]

    def test_renter_with_invalid_owner_phone(self, client, mock_sdk):
        """Test validation fails when owner phone is invalid."""
        mock_sdk.get_tenant.return_value = None
        response = client.post("/api/tenants", json={
            "building_number": 11,
            "apartment_number": 1,
            "first_name": "John",
            "last_name": "Doe",
            "phone": "0501234567",
            "is_owner": False,
            "owner_info": {
                "first_name": "Jane",
                "last_name": "Smith",
                "phone": "123"  # Too short
            }
        })
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is False
        assert "owner_phone" in data["validation_errors"]

    def test_renter_with_valid_owner_info_succeeds(self, client, mock_sdk):
        """Test validation passes for renter with valid owner info."""
        mock_sdk.get_tenant.return_value = None
        mock_sdk.create_tenant.return_value = {"success": True}
        response = client.post("/api/tenants", json={
            "building_number": 11,
            "apartment_number": 1,
            "first_name": "John",
            "last_name": "Doe",
            "phone": "0501234567",
            "is_owner": False,
            "owner_info": {
                "first_name": "Jane",
                "last_name": "Smith",
                "phone": "0509876543"
            }
        })
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

    def test_owner_does_not_need_owner_info(self, client, mock_sdk):
        """Test that owners don't need to provide owner_info."""
        mock_sdk.get_tenant.return_value = None
        mock_sdk.create_tenant.return_value = {"success": True}
        response = client.post("/api/tenants", json={
            "building_number": 11,
            "apartment_number": 1,
            "first_name": "John",
            "last_name": "Doe",
            "phone": "0501234567",
            "is_owner": True
            # No owner_info needed
        })
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True


class TestFamilyMemberValidation:
    """Tests for family member validation."""

    def test_too_many_whatsapp_members(self, client, mock_sdk):
        """Test validation fails when too many WhatsApp members."""
        mock_sdk.get_tenant.return_value = None
        response = client.post("/api/tenants", json={
            "building_number": 11,
            "apartment_number": 1,
            "first_name": "John",
            "last_name": "Doe",
            "phone": "0501234567",
            "is_owner": True,
            "family_members": [
                {"first_name": "Jane", "last_name": "Doe", "phone": "0502222222", "whatsapp_enabled": True, "palgate_enabled": False},
                {"first_name": "Bob", "last_name": "Doe", "phone": "0503333333", "whatsapp_enabled": True, "palgate_enabled": False},
                {"first_name": "Alice", "last_name": "Doe", "phone": "0504444444", "whatsapp_enabled": True, "palgate_enabled": False},
            ]
        })
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is False
        assert "family_members" in data["validation_errors"]
        assert any("WhatsApp" in err for err in data["validation_errors"]["family_members"])

    def test_too_many_palgate_members(self, client, mock_sdk):
        """Test validation fails when too many PalGate members."""
        mock_sdk.get_tenant.return_value = None
        response = client.post("/api/tenants", json={
            "building_number": 11,
            "apartment_number": 1,
            "first_name": "John",
            "last_name": "Doe",
            "phone": "0501234567",
            "is_owner": True,
            "family_members": [
                {"first_name": "Jane", "last_name": "Doe", "phone": "0502222222", "whatsapp_enabled": False, "palgate_enabled": True},
                {"first_name": "Bob", "last_name": "Doe", "phone": "0503333333", "whatsapp_enabled": False, "palgate_enabled": True},
                {"first_name": "Alice", "last_name": "Doe", "phone": "0504444444", "whatsapp_enabled": False, "palgate_enabled": True},
                {"first_name": "Charlie", "last_name": "Doe", "phone": "0505555555", "whatsapp_enabled": False, "palgate_enabled": True},
                {"first_name": "Eve", "last_name": "Doe", "phone": "0506666666", "whatsapp_enabled": False, "palgate_enabled": True},
            ]
        })
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is False
        assert "family_members" in data["validation_errors"]
        assert any("PalGate" in err for err in data["validation_errors"]["family_members"])

    def test_family_member_invalid_name(self, client, mock_sdk):
        """Test validation fails for family member with invalid name."""
        mock_sdk.get_tenant.return_value = None
        response = client.post("/api/tenants", json={
            "building_number": 11,
            "apartment_number": 1,
            "first_name": "John",
            "last_name": "Doe",
            "phone": "0501234567",
            "is_owner": True,
            "family_members": [
                {"first_name": "J", "last_name": "Doe", "phone": "0502222222", "whatsapp_enabled": True, "palgate_enabled": False},
            ]
        })
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is False
        assert "family_member_0" in data["validation_errors"]

    def test_family_member_invalid_phone(self, client, mock_sdk):
        """Test validation fails for family member with invalid phone."""
        mock_sdk.get_tenant.return_value = None
        response = client.post("/api/tenants", json={
            "building_number": 11,
            "apartment_number": 1,
            "first_name": "John",
            "last_name": "Doe",
            "phone": "0501234567",
            "is_owner": True,
            "family_members": [
                {"first_name": "Jane", "last_name": "Doe", "phone": "123", "whatsapp_enabled": True, "palgate_enabled": False},
            ]
        })
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is False
        assert "family_member_0" in data["validation_errors"]

    def test_family_member_invalid_vehicle_plate(self, client, mock_sdk):
        """Test validation fails for family member with invalid vehicle plate."""
        mock_sdk.get_tenant.return_value = None
        response = client.post("/api/tenants", json={
            "building_number": 11,
            "apartment_number": 1,
            "first_name": "John",
            "last_name": "Doe",
            "phone": "0501234567",
            "is_owner": True,
            "family_members": [
                {
                    "first_name": "Jane",
                    "last_name": "Doe",
                    "phone": "0502222222",
                    "whatsapp_enabled": False,
                    "palgate_enabled": True,
                    "vehicle_plate": "ABC123"  # Letters not allowed
                },
            ]
        })
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is False
        assert "family_member_0" in data["validation_errors"]

    def test_family_member_valid_vehicle_plate(self, client, mock_sdk):
        """Test validation passes for family member with valid vehicle plate."""
        mock_sdk.get_tenant.return_value = None
        mock_sdk.create_tenant.return_value = {"success": True}
        response = client.post("/api/tenants", json={
            "building_number": 11,
            "apartment_number": 1,
            "first_name": "John",
            "last_name": "Doe",
            "phone": "0501234567",
            "is_owner": True,
            "family_members": [
                {
                    "first_name": "Jane",
                    "last_name": "Doe",
                    "phone": "0502222222",
                    "whatsapp_enabled": False,
                    "palgate_enabled": True,
                    "vehicle_plate": "12-345-67"
                },
            ]
        })
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

    def test_valid_family_members_with_both_enabled(self, client, mock_sdk):
        """Test validation passes for valid family members with both services enabled."""
        mock_sdk.get_tenant.return_value = None
        mock_sdk.create_tenant.return_value = {"success": True}
        response = client.post("/api/tenants", json={
            "building_number": 11,
            "apartment_number": 1,
            "first_name": "John",
            "last_name": "Doe",
            "phone": "0501234567",
            "is_owner": True,
            "family_members": [
                {
                    "first_name": "Jane",
                    "last_name": "Doe",
                    "phone": "0502222222",
                    "whatsapp_enabled": True,
                    "palgate_enabled": True,
                    "vehicle_plate": "12-345-67"
                },
                {
                    "first_name": "Bob",
                    "last_name": "Doe",
                    "phone": "0503333333",
                    "whatsapp_enabled": True,
                    "palgate_enabled": True,
                    "vehicle_plate": "98-765-43"
                },
            ]
        })
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

    def test_empty_vehicle_plate_is_allowed(self, client, mock_sdk):
        """Test that empty vehicle plate is allowed."""
        mock_sdk.get_tenant.return_value = None
        mock_sdk.create_tenant.return_value = {"success": True}
        response = client.post("/api/tenants", json={
            "building_number": 11,
            "apartment_number": 1,
            "first_name": "John",
            "last_name": "Doe",
            "phone": "0501234567",
            "is_owner": True,
            "family_members": [
                {
                    "first_name": "Jane",
                    "last_name": "Doe",
                    "phone": "0502222222",
                    "whatsapp_enabled": False,
                    "palgate_enabled": True,
                    "vehicle_plate": ""  # Empty is allowed
                },
            ]
        })
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True


class TestTenantReplacement:
    """Tests for tenant replacement flow."""

    def test_existing_tenant_requires_confirmation(self, client, mock_sdk):
        """Test that existing tenant triggers confirmation requirement."""
        mock_sdk.get_tenant.return_value = TenantInfo(
            building_number=11, apartment_number=1,
            first_name="Existing", last_name="Tenant",
            phone="0509999999", is_owner=True,
            move_in_date=date(2023, 1, 1)
        )
        response = client.post("/api/tenants", json={
            "building_number": 11,
            "apartment_number": 1,
            "first_name": "John",
            "last_name": "Doe",
            "phone": "0501234567",
            "is_owner": True,
            "replace_existing": False
        })
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is False
        assert data["requires_confirmation"] is True
        assert "existing_tenant" in data
        assert data["existing_tenant"]["first_name"] == "Existing"

    def test_replace_existing_tenant(self, client, mock_sdk):
        """Test that tenant can be replaced with confirmation."""
        mock_sdk.get_tenant.return_value = TenantInfo(
            building_number=11, apartment_number=1,
            first_name="Existing", last_name="Tenant",
            phone="0509999999", is_owner=True,
            move_in_date=date(2023, 1, 1)
        )
        mock_sdk.end_tenancy.return_value = {"ended": True}
        mock_sdk.create_tenant.return_value = {"success": True}

        response = client.post("/api/tenants", json={
            "building_number": 11,
            "apartment_number": 1,
            "first_name": "John",
            "last_name": "Doe",
            "phone": "0501234567",
            "is_owner": True,
            "replace_existing": True
        })
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        # Verify end_tenancy was called
        mock_sdk.end_tenancy.assert_called_once()


class TestMultipleValidationErrors:
    """Tests for multiple validation errors at once."""

    def test_multiple_field_errors(self, client, mock_sdk):
        """Test multiple validation errors returned together."""
        mock_sdk.get_tenant.return_value = None
        response = client.post("/api/tenants", json={
            "building_number": 11,
            "apartment_number": 1,
            "first_name": "J",  # Too short
            "last_name": "D",  # Too short
            "phone": "123",  # Too short
            "is_owner": True
        })
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is False
        # All three fields should have errors
        assert "first_name" in data["validation_errors"]
        assert "last_name" in data["validation_errors"]
        assert "phone" in data["validation_errors"]

    def test_renter_with_all_invalid_fields(self, client, mock_sdk):
        """Test renter with all invalid fields returns all errors."""
        mock_sdk.get_tenant.return_value = None
        response = client.post("/api/tenants", json={
            "building_number": 11,
            "apartment_number": 1,
            "first_name": "J",  # Too short
            "last_name": "D",  # Too short
            "phone": "123",  # Too short
            "is_owner": False,
            "owner_info": {
                "first_name": "X",  # Too short
                "last_name": "Y",  # Too short
                "phone": "456"  # Too short
            }
        })
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is False
        # Both tenant and owner fields should have errors
        assert "first_name" in data["validation_errors"]
        assert "last_name" in data["validation_errors"]
        assert "phone" in data["validation_errors"]
        assert "owner_first_name" in data["validation_errors"]
        assert "owner_last_name" in data["validation_errors"]
        assert "owner_phone" in data["validation_errors"]


class TestEdgeCases:
    """Tests for edge cases and boundary conditions."""

    def test_name_at_minimum_length(self, client, mock_sdk):
        """Test name at exact minimum length passes."""
        mock_sdk.get_tenant.return_value = None
        mock_sdk.create_tenant.return_value = {"success": True}
        response = client.post("/api/tenants", json={
            "building_number": 11,
            "apartment_number": 1,
            "first_name": "Jo",  # Exactly 2 chars
            "last_name": "Li",  # Exactly 2 chars
            "phone": "050123456",  # Exactly 9 chars
            "is_owner": True
        })
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

    def test_phone_at_maximum_length(self, client, mock_sdk):
        """Test phone at exact maximum length passes."""
        mock_sdk.get_tenant.return_value = None
        mock_sdk.create_tenant.return_value = {"success": True}
        response = client.post("/api/tenants", json={
            "building_number": 11,
            "apartment_number": 1,
            "first_name": "John",
            "last_name": "Doe",
            "phone": "123456789012345",  # Exactly 15 chars
            "is_owner": True
        })
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

    def test_empty_family_members_list(self, client, mock_sdk):
        """Test empty family members list is valid."""
        mock_sdk.get_tenant.return_value = None
        mock_sdk.create_tenant.return_value = {"success": True}
        response = client.post("/api/tenants", json={
            "building_number": 11,
            "apartment_number": 1,
            "first_name": "John",
            "last_name": "Doe",
            "phone": "0501234567",
            "is_owner": True,
            "family_members": []
        })
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

    def test_family_member_at_max_limit(self, client, mock_sdk):
        """Test family members at exact limits pass."""
        mock_sdk.get_tenant.return_value = None
        mock_sdk.create_tenant.return_value = {"success": True}
        response = client.post("/api/tenants", json={
            "building_number": 11,
            "apartment_number": 1,
            "first_name": "John",
            "last_name": "Doe",
            "phone": "0501234567",
            "is_owner": True,
            "family_members": [
                # Exactly 2 WhatsApp (max)
                {"first_name": "Jane", "last_name": "Doe", "phone": "0502222222", "whatsapp_enabled": True, "palgate_enabled": False},
                {"first_name": "Bob", "last_name": "Doe", "phone": "0503333333", "whatsapp_enabled": True, "palgate_enabled": False},
            ]
        })
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

    def test_vehicle_plate_at_max_length(self, client, mock_sdk):
        """Test vehicle plate at exact max length passes."""
        mock_sdk.get_tenant.return_value = None
        mock_sdk.create_tenant.return_value = {"success": True}
        response = client.post("/api/tenants", json={
            "building_number": 11,
            "apartment_number": 1,
            "first_name": "John",
            "last_name": "Doe",
            "phone": "0501234567",
            "is_owner": True,
            "family_members": [
                {
                    "first_name": "Jane",
                    "last_name": "Doe",
                    "phone": "0502222222",
                    "whatsapp_enabled": False,
                    "palgate_enabled": True,
                    "vehicle_plate": "12-345-678"  # Exactly 10 chars
                },
            ]
        })
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

    def test_vehicle_plate_over_max_length(self, client, mock_sdk):
        """Test vehicle plate over max length fails."""
        mock_sdk.get_tenant.return_value = None
        response = client.post("/api/tenants", json={
            "building_number": 11,
            "apartment_number": 1,
            "first_name": "John",
            "last_name": "Doe",
            "phone": "0501234567",
            "is_owner": True,
            "family_members": [
                {
                    "first_name": "Jane",
                    "last_name": "Doe",
                    "phone": "0502222222",
                    "whatsapp_enabled": False,
                    "palgate_enabled": True,
                    "vehicle_plate": "12-345-67890"  # 12 chars, over limit
                },
            ]
        })
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is False
        assert "family_member_0" in data["validation_errors"]
