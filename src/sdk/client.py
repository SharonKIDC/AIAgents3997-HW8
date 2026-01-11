"""High-level SDK client for tenant management system.

Provides a clean, typed interface for all tenant management operations.
"""

from datetime import date
from typing import Dict, Any, Optional, List
from dataclasses import dataclass

from src.communication import MCPHttpClient, MCPResponse
from src.exceptions import ValidationError


@dataclass
class TenantInfo:
    """Tenant information data class."""

    building_number: int
    apartment_number: int
    first_name: str
    last_name: str
    phone: str
    is_owner: bool
    move_in_date: Optional[date] = None
    storage_number: Optional[int] = None
    parking_slot_1: Optional[int] = None
    parking_slot_2: Optional[int] = None

    @property
    def full_name(self) -> str:
        """Get full name."""
        return f"{self.first_name} {self.last_name}"


@dataclass
class BuildingInfo:
    """Building information data class."""

    number: int
    total_apartments: int
    occupied: int = 0
    vacant: int = 0
    occupancy_rate: float = 0.0


class TenantSDK:
    """High-level SDK for tenant management operations."""

    def __init__(self, base_url: str = None, timeout: int = None):
        """Initialize SDK with MCP server connection."""
        self._client = MCPHttpClient(base_url=base_url, timeout=timeout)

    def create_tenant(
        self,
        building: int,
        apartment: int,
        first_name: str,
        last_name: str,
        phone: str,
        is_owner: bool = True,
        move_in_date: date = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """Create a new tenant."""
        params = {
            "building_number": building,
            "apartment_number": apartment,
            "first_name": first_name,
            "last_name": last_name,
            "phone": phone,
            "is_owner": is_owner,
            "move_in_date": (move_in_date or date.today()).isoformat(),
        }
        params.update(kwargs)
        response = self._client.invoke_tool("create_tenant", params)
        if response.is_error():
            raise ValidationError(response.error or "Failed to create tenant")
        return response.data

    def get_tenant(self, building: int, apartment: int) -> Optional[TenantInfo]:
        """Get tenant information for an apartment."""
        response = self._client.invoke_tool(
            "get_tenant", {"building_number": building, "apartment_number": apartment}
        )
        if response.is_error() or not response.data:
            return None
        # MCP server returns {"success": True, "tenant": {...}} or {"success": True, "tenant": None}
        tenant_data = response.data.get("tenant")
        if not tenant_data:
            return None
        return TenantInfo(
            building_number=tenant_data["building_number"],
            apartment_number=tenant_data["apartment_number"],
            first_name=tenant_data["first_name"],
            last_name=tenant_data["last_name"],
            phone=tenant_data["phone"],
            is_owner=tenant_data["is_owner"],
            move_in_date=(
                date.fromisoformat(tenant_data["move_in_date"])
                if tenant_data.get("move_in_date")
                else None
            ),
            storage_number=tenant_data.get("storage_number"),
            parking_slot_1=tenant_data.get("parking_slot_1"),
            parking_slot_2=tenant_data.get("parking_slot_2"),
        )

    def update_tenant(self, building: int, apartment: int, **updates) -> Dict[str, Any]:
        """Update tenant information."""
        params = {"building_number": building, "apartment_number": apartment, **updates}
        response = self._client.invoke_tool("update_tenant", params)
        if response.is_error():
            raise ValidationError(response.error or "Failed to update tenant")
        return response.data

    def end_tenancy(
        self, building: int, apartment: int, move_out_date: date = None
    ) -> Dict[str, Any]:
        """End a tenancy (move out)."""
        params = {
            "building_number": building,
            "apartment_number": apartment,
            "move_out_date": (move_out_date or date.today()).isoformat(),
        }
        response = self._client.invoke_tool("end_tenancy", params)
        if response.is_error():
            raise ValidationError(response.error or "Failed to end tenancy")
        return response.data

    def get_buildings(self) -> List[BuildingInfo]:
        """Get list of all buildings with occupancy info."""
        response = self._client.get_resource("/buildings")
        if response.is_error():
            return []
        buildings = response.data.get("buildings", [])
        return [
            BuildingInfo(number=b["number"], total_apartments=b["total_apartments"])
            for b in buildings
        ]

    def get_building_occupancy(self, building: int) -> Optional[BuildingInfo]:
        """Get occupancy statistics for a building."""
        response = self._client.get_resource(f"/buildings/{building}")
        if response.is_error():
            return None
        data = response.data
        # MCP server returns {"building": {...}, "occupancy": {...}, "tenants": [...]}
        building_data = data.get("building", {})
        occupancy_data = data.get("occupancy", {})
        if not building_data:
            return None
        return BuildingInfo(
            number=building_data["number"],
            total_apartments=building_data["total_apartments"],
            occupied=occupancy_data.get("occupied", 0),
            vacant=occupancy_data.get("vacant", 0),
            occupancy_rate=occupancy_data.get("occupancy_rate", 0.0),
        )

    def get_all_tenants(self, building: int = None) -> List[Dict[str, Any]]:
        """Get all tenants, optionally filtered by building."""
        params = {"building": building} if building else None
        response = self._client.get_resource("/tenants", params=params)
        if response.is_error():
            return []
        return response.data.get("tenants", [])

    def get_tenant_history(self, building: int, apartment: int) -> List[Dict[str, Any]]:
        """Get tenant history for an apartment."""
        response = self._client.get_resource(f"/tenants/{building}/{apartment}/history")
        if response.is_error():
            return []
        return response.data.get("history", [])

    def get_occupancy_report(self, building: int = None) -> MCPResponse:
        """Generate AI prompt for occupancy report."""
        args = {"building": building} if building else {}
        return self._client.generate_prompt("occupancy_report", args)

    def get_tenant_list_report(
        self, building: int = None, include_contacts: bool = False
    ) -> MCPResponse:
        """Generate AI prompt for tenant list report."""
        args = {"building": building, "include_contacts": include_contacts}
        return self._client.generate_prompt("tenant_list_report", args)

    def close(self) -> None:
        """Close SDK connection."""
        self._client.close()

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
        return False
