"""Data models for the tenant management system.

Pydantic models representing buildings, tenants, and historical records.
All models use configuration-driven validation with no hardcoded values.
"""

from datetime import date
from typing import Optional, List
from pydantic import BaseModel, Field, field_validator

from src.config import get_config


class OwnerInfo(BaseModel):
    """Owner information for rented apartments."""

    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    phone: str = Field(..., min_length=9, max_length=20)

    @property
    def full_name(self) -> str:
        """Return full name of owner."""
        return f"{self.first_name} {self.last_name}"


class WhatsAppMember(BaseModel):
    """WhatsApp group member information."""

    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    phone: str = Field(..., min_length=9, max_length=20)


class ParkingAuthorization(BaseModel):
    """Parking access authorization information."""

    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    phone: str = Field(..., min_length=9, max_length=20)


class PalGateMember(BaseModel):
    """PalGate access authorization for gate entry."""

    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    phone: str = Field(..., min_length=9, max_length=20)
    vehicle_plate: Optional[str] = Field(None, max_length=20)


class Building(BaseModel):
    """Building model with apartment count from configuration."""

    number: int
    total_apartments: int

    @classmethod
    def get_all_buildings(cls) -> List["Building"]:
        """Get all buildings from configuration."""
        config = get_config()
        buildings_config = config.get("buildings", [])
        buildings = []
        for bldg in buildings_config:
            buildings.append(cls(
                number=bldg.get("number", 0),
                total_apartments=bldg.get("total_apartments", 0)
            ))
        return sorted(buildings, key=lambda b: b.number)

    @classmethod
    def get_building(cls, number: int) -> Optional["Building"]:
        """Get a specific building by number."""
        config = get_config()
        buildings_config = config.get("buildings", [])
        for bldg in buildings_config:
            if bldg.get("number") == number:
                return cls(
                    number=number,
                    total_apartments=bldg.get("total_apartments", 0)
                )
        return None


class Tenant(BaseModel):
    """Tenant model for apartment registration."""

    building_number: int
    apartment_number: int
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    phone: str = Field(..., min_length=9, max_length=20)
    storage_number: Optional[str] = None
    parking_slot_1: Optional[str] = None
    parking_slot_2: Optional[str] = None
    is_owner: bool = True
    owner_info: Optional[OwnerInfo] = None
    whatsapp_members: List[WhatsAppMember] = Field(default_factory=list)
    parking_authorizations: List[ParkingAuthorization] = Field(default_factory=list)
    palgate_members: List["PalGateMember"] = Field(default_factory=list)
    move_in_date: date = Field(default_factory=date.today)
    move_out_date: Optional[date] = None
    palgate_access_enabled: bool = False
    whatsapp_group_enabled: bool = False

    @property
    def full_name(self) -> str:
        """Return full name of tenant."""
        return f"{self.first_name} {self.last_name}"

    @property
    def is_active(self) -> bool:
        """Check if tenant is currently active."""
        return self.move_out_date is None

    @field_validator("owner_info", mode="before")
    @classmethod
    def validate_owner_info(cls, v, info):
        """Validate owner info is provided when tenant is renter."""
        values = info.data
        if not values.get("is_owner", True) and v is None:
            raise ValueError("Owner info required when tenant is renter")
        return v

    @field_validator("parking_authorizations", mode="before")
    @classmethod
    def validate_parking_limit(cls, v):
        """Validate maximum 4 parking authorizations."""
        config = get_config()
        max_parking = config.get("validation.max_parking_authorizations", 4)
        if v and len(v) > max_parking:
            raise ValueError(f"Maximum {max_parking} parking authorizations")
        return v or []


class TenantHistory(BaseModel):
    """Historical tenant record for tracking previous occupants."""

    building_number: int
    apartment_number: int
    first_name: str
    last_name: str
    phone: str
    move_in_date: date
    move_out_date: date
    was_owner: bool
    owner_first_name: Optional[str] = None
    owner_last_name: Optional[str] = None
    owner_phone: Optional[str] = None

    @property
    def full_name(self) -> str:
        """Return full name of historical tenant."""
        return f"{self.first_name} {self.last_name}"

    @property
    def tenancy_duration_days(self) -> int:
        """Calculate duration of tenancy in days."""
        return (self.move_out_date - self.move_in_date).days
