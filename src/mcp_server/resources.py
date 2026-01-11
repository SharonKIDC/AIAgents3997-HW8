"""MCP Resources for tenant data access.

Provides read-only access to tenant data including listings,
history, and occupancy statistics.
"""

from typing import Dict, Any

from src.database import Building, TenantQueries, HistoryManager


class TenantResources:
    """MCP resources for tenant data access."""

    def __init__(self, db_path: str = None):
        """Initialize resources with database path."""
        self._db_path = db_path
        self._queries = TenantQueries(db_path)
        self._history = HistoryManager(db_path)

    @staticmethod
    def get_resource_definitions() -> list:
        """Get MCP resource definitions."""
        return [
            {
                "uri": "tenants://buildings",
                "name": "All Buildings",
                "description": "List of all buildings with apartment counts",
                "mimeType": "application/json",
            },
            {
                "uri": "tenants://buildings/{building_number}",
                "name": "Building Details",
                "description": "Details and occupancy for a specific building",
                "mimeType": "application/json",
            },
            {
                "uri": "tenants://tenants",
                "name": "All Tenants",
                "description": "List of all active tenants",
                "mimeType": "application/json",
            },
            {
                "uri": "tenants://tenants/{building}/{apartment}/history",
                "name": "Tenant History",
                "description": "Historical tenants for an apartment",
                "mimeType": "application/json",
            },
            {
                "uri": "tenants://occupancy",
                "name": "Occupancy Statistics",
                "description": "Occupancy rates for all buildings",
                "mimeType": "application/json",
            },
            {
                "uri": "tenants://whatsapp",
                "name": "WhatsApp Contacts",
                "description": "Phone numbers for WhatsApp groups",
                "mimeType": "application/json",
            },
            {
                "uri": "tenants://parking",
                "name": "Parking Authorizations",
                "description": "List of parking access authorizations",
                "mimeType": "application/json",
            },
        ]

    def get_buildings(self) -> Dict[str, Any]:
        """Get all buildings with details."""
        buildings = Building.get_all_buildings()
        return {
            "buildings": [
                {"number": b.number, "total_apartments": b.total_apartments} for b in buildings
            ]
        }

    def get_building_details(self, building_number: int) -> Dict[str, Any]:
        """Get details for a specific building."""
        building = Building.get_building(building_number)
        if not building:
            return {"error": f"Building {building_number} not found"}
        occupancy = self._queries.get_building_occupancy(building_number)
        tenants = self._queries.get_all_tenants(building_number)
        return {
            "building": {"number": building.number, "total_apartments": building.total_apartments},
            "occupancy": occupancy,
            "tenants": [t.model_dump() for t in tenants],
        }

    def get_all_tenants(self, building: int = None) -> Dict[str, Any]:
        """Get all active tenants."""
        tenants = self._queries.get_all_tenants(building)
        return {"tenants": [t.model_dump() for t in tenants]}

    def get_tenant_history(self, building: int, apartment: int) -> Dict[str, Any]:
        """Get tenant history for an apartment."""
        history = self._history.get_apartment_history(building, apartment)
        return {"history": [h.model_dump() for h in history]}

    def get_occupancy_stats(self) -> Dict[str, Any]:
        """Get occupancy statistics for all buildings."""
        stats = self._queries.get_all_buildings_occupancy()
        total_apartments = sum(s["total_apartments"] for s in stats)
        total_occupied = sum(s["occupied"] for s in stats)
        return {
            "buildings": stats,
            "total": {
                "apartments": total_apartments,
                "occupied": total_occupied,
                "vacant": total_apartments - total_occupied,
                "occupancy_rate": (
                    round(total_occupied / total_apartments * 100, 1) if total_apartments > 0 else 0
                ),
            },
        }

    def get_whatsapp_contacts(self, building: int = None) -> Dict[str, Any]:
        """Get WhatsApp contact list."""
        contacts = self._queries.get_whatsapp_contacts(building)
        return {"contacts": contacts}

    def get_parking_authorizations(self, building: int = None) -> Dict[str, Any]:
        """Get parking authorization list."""
        authorizations = self._queries.get_parking_authorizations(building)
        return {"authorizations": authorizations}
