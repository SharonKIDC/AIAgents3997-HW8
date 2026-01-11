"""MCP Tools for tenant management operations.

Provides state-changing operations (create, update, delete) for tenant data.
Each tool is defined with identifier, description, and JSON schema.
"""

from datetime import date
from typing import Any

from src.database import (
    DataValidator,
    ExcelManager,
    ExcelOperations,
    OwnerInfo,
    Tenant,
    TenantQueries,
)
from src.exceptions import NotFoundError


class TenantTools:
    """MCP tools for tenant management operations."""

    def __init__(self, db_path: str = None):
        """Initialize tools with database path."""
        self._db_path = db_path
        self._operations = ExcelOperations(db_path)
        self._manager = ExcelManager(db_path)
        self._queries = TenantQueries(db_path)
        self._validator = DataValidator()

    @staticmethod
    def get_tool_definitions() -> list:
        """Get MCP tool definitions with schemas."""
        return [
            {
                "name": "create_tenant",
                "description": "Register a new tenant in an apartment",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "building_number": {"type": "integer"},
                        "apartment_number": {"type": "integer"},
                        "first_name": {"type": "string"},
                        "last_name": {"type": "string"},
                        "phone": {"type": "string"},
                        "is_owner": {"type": "boolean", "default": True},
                        "owner_info": {
                            "type": "object",
                            "properties": {
                                "first_name": {"type": "string"},
                                "last_name": {"type": "string"},
                                "phone": {"type": "string"},
                            },
                        },
                    },
                    "required": [
                        "building_number",
                        "apartment_number",
                        "first_name",
                        "last_name",
                        "phone",
                    ],
                },
            },
            {
                "name": "update_tenant",
                "description": "Update existing tenant information",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "building_number": {"type": "integer"},
                        "apartment_number": {"type": "integer"},
                        "updates": {"type": "object"},
                    },
                    "required": ["building_number", "apartment_number", "updates"],
                },
            },
            {
                "name": "end_tenancy",
                "description": "End a tenant's residency and move to history",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "building_number": {"type": "integer"},
                        "apartment_number": {"type": "integer"},
                        "move_out_date": {"type": "string", "format": "date"},
                    },
                    "required": ["building_number", "apartment_number"],
                },
            },
            {
                "name": "get_tenant",
                "description": "Get current tenant for an apartment",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "building_number": {"type": "integer"},
                        "apartment_number": {"type": "integer"},
                    },
                    "required": ["building_number", "apartment_number"],
                },
            },
        ]

    def create_tenant(self, params: dict[str, Any]) -> dict[str, Any]:
        """Create a new tenant."""
        owner_info = None
        if not params.get("is_owner", True) and params.get("owner_info"):
            owner_info = OwnerInfo(**params["owner_info"])
        tenant = Tenant(
            building_number=params["building_number"],
            apartment_number=params["apartment_number"],
            first_name=params["first_name"],
            last_name=params["last_name"],
            phone=params["phone"],
            storage_number=params.get("storage_number"),
            parking_slot_1=params.get("parking_slot_1"),
            parking_slot_2=params.get("parking_slot_2"),
            is_owner=params.get("is_owner", True),
            owner_info=owner_info,
            move_in_date=date.today(),
        )
        created = self._operations.create_tenant(tenant)
        return {"success": True, "tenant": created.model_dump()}

    def update_tenant(self, params: dict[str, Any]) -> dict[str, Any]:
        """Update an existing tenant."""
        tenant = self._manager.get_tenant(params["building_number"], params["apartment_number"])
        if not tenant:
            raise NotFoundError("Tenant not found")
        updates = params.get("updates", {})
        for key, value in updates.items():
            if hasattr(tenant, key):
                setattr(tenant, key, value)
        updated = self._operations.update_tenant(tenant)
        return {"success": True, "tenant": updated.model_dump()}

    def end_tenancy(self, params: dict[str, Any]) -> dict[str, Any]:
        """End a tenant's residency."""
        move_out = params.get("move_out_date")
        move_out = date.fromisoformat(move_out) if move_out else date.today()
        history = self._operations.end_tenancy(
            params["building_number"], params["apartment_number"], move_out
        )
        return {"success": True, "history": history.model_dump()}

    def get_tenant(self, params: dict[str, Any]) -> dict[str, Any] | None:
        """Get current tenant for an apartment."""
        tenant = self._manager.get_tenant(params["building_number"], params["apartment_number"])
        if tenant:
            return {"success": True, "tenant": tenant.model_dump()}
        return {"success": True, "tenant": None}
