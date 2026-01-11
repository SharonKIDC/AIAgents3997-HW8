"""Tests for database module.

Comprehensive tests for models, validators, and Excel operations.
"""

import os
import tempfile
from datetime import date
from pathlib import Path

import pytest

from src.database.models import Building, Tenant, TenantHistory, OwnerInfo
from src.database.validators import DataValidator
from src.database.excel_manager import ExcelManager
from src.database.excel_operations import ExcelOperations
from src.exceptions import ValidationError


class TestBuilding:
    """Tests for Building model."""

    def test_get_all_buildings(self):
        """Test retrieving all buildings from config."""
        buildings = Building.get_all_buildings()
        assert len(buildings) == 4
        # Config has buildings 11, 13, 15, 17
        assert buildings[0].number == 11

    def test_get_building_valid(self):
        """Test retrieving a valid building."""
        building = Building.get_building(11)
        assert building is not None
        assert building.number == 11
        # Building 11 has 17 apartments per requirements
        assert building.total_apartments == 17

    def test_get_building_invalid(self):
        """Test retrieving an invalid building."""
        building = Building.get_building(99)
        assert building is None


class TestOwnerInfo:
    """Tests for OwnerInfo model."""

    def test_owner_info_creation(self):
        """Test creating owner info."""
        owner = OwnerInfo(first_name="John", last_name="Doe", phone="0501234567")
        assert owner.full_name == "John Doe"

    def test_owner_info_validation(self):
        """Test owner info validation."""
        with pytest.raises(ValueError):
            OwnerInfo(first_name="", last_name="Doe", phone="0501234567")


class TestTenant:
    """Tests for Tenant model."""

    def test_tenant_creation_owner(self):
        """Test creating a tenant who is the owner."""
        tenant = Tenant(
            building_number=11,
            apartment_number=1,
            first_name="Jane",
            last_name="Smith",
            phone="0509876543",
            is_owner=True,
        )
        assert tenant.full_name == "Jane Smith"
        assert tenant.is_active is True

    def test_tenant_creation_renter(self):
        """Test creating a tenant who is a renter."""
        owner = OwnerInfo(first_name="John", last_name="Doe", phone="0501234567")
        tenant = Tenant(
            building_number=11,
            apartment_number=1,
            first_name="Jane",
            last_name="Smith",
            phone="0509876543",
            is_owner=False,
            owner_info=owner,
        )
        assert tenant.is_owner is False
        assert tenant.owner_info.full_name == "John Doe"

    def test_tenant_inactive_with_move_out(self):
        """Test tenant is inactive when move_out_date is set."""
        tenant = Tenant(
            building_number=11,
            apartment_number=1,
            first_name="Jane",
            last_name="Smith",
            phone="0509876543",
            move_out_date=date(2025, 1, 1),
        )
        assert tenant.is_active is False


class TestTenantHistory:
    """Tests for TenantHistory model."""

    def test_history_duration(self):
        """Test tenancy duration calculation."""
        history = TenantHistory(
            building_number=11,
            apartment_number=1,
            first_name="Jane",
            last_name="Smith",
            phone="0509876543",
            move_in_date=date(2024, 1, 1),
            move_out_date=date(2024, 12, 31),
            was_owner=True,
        )
        assert history.tenancy_duration_days == 365


class TestDataValidator:
    """Tests for DataValidator."""

    def test_valid_building_numbers(self):
        """Test getting valid building numbers."""
        validator = DataValidator()
        valid = validator.get_valid_building_numbers()
        assert valid == [11, 13, 15, 17]

    def test_validate_building_number_valid(self):
        """Test validating a valid building number."""
        validator = DataValidator()
        assert validator.validate_building_number(11) is True

    def test_validate_building_number_invalid(self):
        """Test validating an invalid building number."""
        validator = DataValidator()
        with pytest.raises(ValidationError):
            validator.validate_building_number(99)

    def test_validate_apartment_number_valid(self):
        """Test validating a valid apartment number."""
        validator = DataValidator()
        assert validator.validate_apartment_number(11, 17) is True

    def test_validate_apartment_number_invalid(self):
        """Test validating an invalid apartment number."""
        validator = DataValidator()
        with pytest.raises(ValidationError):
            validator.validate_apartment_number(11, 99)

    def test_validate_phone_valid(self):
        """Test validating a valid phone number."""
        validator = DataValidator()
        assert validator.validate_phone_number("0501234567") is True

    def test_validate_phone_invalid(self):
        """Test validating an invalid phone number."""
        validator = DataValidator()
        with pytest.raises(ValidationError):
            validator.validate_phone_number("123")

    def test_validate_dates_valid(self):
        """Test validating valid dates."""
        validator = DataValidator()
        assert validator.validate_dates(date(2024, 1, 1), date(2024, 12, 31))

    def test_validate_dates_invalid(self):
        """Test validating invalid dates."""
        validator = DataValidator()
        with pytest.raises(ValidationError):
            validator.validate_dates(date(2024, 12, 31), date(2024, 1, 1))

    def test_validate_tenant_data_complete(self):
        """Test validating complete tenant data."""
        validator = DataValidator()
        data = {
            "building_number": 11,
            "apartment_number": 1,
            "first_name": "Jane",
            "last_name": "Smith",
            "phone": "0509876543",
            "is_owner": True,
        }
        valid, errors = validator.validate_tenant_data(data)
        assert valid is True
        assert len(errors) == 0


class TestExcelManager:
    """Tests for ExcelManager."""

    @pytest.fixture
    def temp_db(self):
        """Create temporary database file path."""
        temp_dir = tempfile.mkdtemp()
        db_path = os.path.join(temp_dir, "test_tenants.xlsx")
        yield db_path
        if os.path.exists(db_path):
            os.unlink(db_path)
        if os.path.exists(temp_dir):
            os.rmdir(temp_dir)

    def test_create_database(self, temp_db):
        """Test creating a new database."""
        ExcelManager(db_path=temp_db)  # Creates database on init
        assert Path(temp_db).exists()

    def test_get_tenant_not_found(self, temp_db):
        """Test getting a non-existent tenant."""
        excel_manager = ExcelManager(db_path=temp_db)
        tenant = excel_manager.get_tenant(11, 1)
        assert tenant is None


class TestExcelOperations:
    """Tests for ExcelOperations."""

    @pytest.fixture
    def temp_db(self):
        """Create temporary database file with initialized structure."""
        temp_dir = tempfile.mkdtemp()
        db_path = os.path.join(temp_dir, "test_tenants.xlsx")
        ExcelManager(db_path=db_path)  # Initialize database structure
        yield db_path
        if os.path.exists(db_path):
            os.unlink(db_path)
        if os.path.exists(temp_dir):
            os.rmdir(temp_dir)

    def test_create_tenant(self, temp_db):
        """Test creating a tenant."""
        ops = ExcelOperations(db_path=temp_db)
        tenant = Tenant(
            building_number=11,
            apartment_number=1,
            first_name="Jane",
            last_name="Smith",
            phone="0509876543",
        )
        created = ops.create_tenant(tenant)
        assert created.first_name == "Jane"

    def test_create_duplicate_tenant(self, temp_db):
        """Test creating a duplicate tenant fails."""
        ops = ExcelOperations(db_path=temp_db)
        tenant = Tenant(
            building_number=11,
            apartment_number=1,
            first_name="Jane",
            last_name="Smith",
            phone="0509876543",
        )
        ops.create_tenant(tenant)
        with pytest.raises(ValidationError):
            ops.create_tenant(tenant)

    def test_update_tenant(self, temp_db):
        """Test updating a tenant."""
        ops = ExcelOperations(db_path=temp_db)
        tenant = Tenant(
            building_number=11,
            apartment_number=1,
            first_name="Jane",
            last_name="Smith",
            phone="0509876543",
        )
        ops.create_tenant(tenant)
        tenant.first_name = "Janet"
        updated = ops.update_tenant(tenant)
        assert updated.first_name == "Janet"

    def test_end_tenancy(self, temp_db):
        """Test ending a tenancy."""
        ops = ExcelOperations(db_path=temp_db)
        tenant = Tenant(
            building_number=11,
            apartment_number=1,
            first_name="Jane",
            last_name="Smith",
            phone="0509876543",
        )
        ops.create_tenant(tenant)
        history = ops.end_tenancy(11, 1, date(2025, 12, 31))
        assert history.first_name == "Jane"

    def test_get_all_tenants(self, temp_db):
        """Test getting all tenants."""
        ops = ExcelOperations(db_path=temp_db)
        for i in range(3):
            tenant = Tenant(
                building_number=11,
                apartment_number=i + 1,
                first_name=f"Tenant{i}",
                last_name="Test",
                phone=f"050123456{i}",
            )
            ops.create_tenant(tenant)
        tenants = ops.get_all_tenants()
        assert len(tenants) == 3

    def test_get_all_tenants_by_building(self, temp_db):
        """Test getting tenants filtered by building."""
        ops = ExcelOperations(db_path=temp_db)
        for bldg in [11, 13]:
            tenant = Tenant(
                building_number=bldg,
                apartment_number=1,
                first_name=f"Tenant{bldg}",
                last_name="Test",
                phone=f"050{bldg}34567",
            )
            ops.create_tenant(tenant)
        tenants = ops.get_all_tenants(building=11)
        assert len(tenants) == 1
        assert tenants[0].building_number == 11
