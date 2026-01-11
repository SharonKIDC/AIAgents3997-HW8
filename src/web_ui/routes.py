"""API routes for React web frontend.

Provides REST endpoints optimized for the React UI components.
"""

from datetime import date
from typing import Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from src.sdk import TenantSDK
from src.exceptions import ValidationError


router = APIRouter(prefix="/api", tags=["web-ui"])


class TenantCreate(BaseModel):
    """Request model for tenant creation."""

    building_number: int
    apartment_number: int
    first_name: str
    last_name: str
    phone: str
    is_owner: bool = True
    move_in_date: Optional[str] = None
    storage_number: Optional[int] = None
    parking_slot_1: Optional[int] = None
    parking_slot_2: Optional[int] = None


class TenantUpdate(BaseModel):
    """Request model for tenant updates."""

    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    is_owner: Optional[bool] = None
    storage_number: Optional[int] = None
    parking_slot_1: Optional[int] = None
    parking_slot_2: Optional[int] = None
    whatsapp_group_enabled: Optional[bool] = None
    palgate_access_enabled: Optional[bool] = None


def _get_sdk() -> TenantSDK:
    """Get SDK instance."""
    return TenantSDK()


@router.get("/buildings")
async def list_buildings():
    """Get all buildings with occupancy info."""
    with _get_sdk() as sdk:
        buildings = sdk.get_buildings()
        result = [{"number": b.number, "total_apartments": b.total_apartments} for b in buildings]
        return {"buildings": result}


@router.get("/buildings/{building_number}")
async def get_building(building_number: int):
    """Get building details with occupancy."""
    with _get_sdk() as sdk:
        building = sdk.get_building_occupancy(building_number)
        if not building:
            raise HTTPException(404, f"Building {building_number} not found")
        return {
            "number": building.number,
            "total_apartments": building.total_apartments,
            "occupied": building.occupied,
            "vacant": building.vacant,
            "occupancy_rate": building.occupancy_rate
        }


@router.get("/tenants")
async def list_tenants(building: Optional[int] = Query(None)):
    """Get all tenants, optionally filtered by building."""
    with _get_sdk() as sdk:
        tenants = sdk.get_all_tenants(building)
        return {"tenants": tenants}


@router.get("/tenants/{building}/{apartment}")
async def get_tenant(building: int, apartment: int):
    """Get tenant for specific apartment."""
    with _get_sdk() as sdk:
        tenant = sdk.get_tenant(building, apartment)
        if not tenant:
            raise HTTPException(404, f"No tenant at Building {building}, Apt {apartment}")
        return {
            "building_number": tenant.building_number,
            "apartment_number": tenant.apartment_number,
            "first_name": tenant.first_name,
            "last_name": tenant.last_name,
            "full_name": tenant.full_name,
            "phone": tenant.phone,
            "is_owner": tenant.is_owner,
            "move_in_date": tenant.move_in_date.isoformat() if tenant.move_in_date else None
        }


@router.post("/tenants")
async def create_tenant(tenant: TenantCreate):
    """Create a new tenant."""
    try:
        move_in = None
        if tenant.move_in_date:
            move_in = date.fromisoformat(tenant.move_in_date)
        with _get_sdk() as sdk:
            result = sdk.create_tenant(
                building=tenant.building_number,
                apartment=tenant.apartment_number,
                first_name=tenant.first_name,
                last_name=tenant.last_name,
                phone=tenant.phone,
                is_owner=tenant.is_owner,
                move_in_date=move_in,
                storage_number=tenant.storage_number,
                parking_slot_1=tenant.parking_slot_1,
                parking_slot_2=tenant.parking_slot_2
            )
            return {"success": True, "data": result}
    except ValidationError as e:
        raise HTTPException(400, str(e)) from e


@router.patch("/tenants/{building}/{apartment}")
async def patch_tenant(building: int, apartment: int, updates: TenantUpdate):
    """Partial update of tenant information."""
    try:
        update_dict = {k: v for k, v in updates.model_dump().items() if v is not None}
        with _get_sdk() as sdk:
            result = sdk.update_tenant(building, apartment, **update_dict)
            return {"success": True, "data": result}
    except ValidationError as e:
        raise HTTPException(400, str(e)) from e


@router.put("/tenants/{building}/{apartment}")
async def update_tenant(building: int, apartment: int, updates: TenantUpdate):
    """Full update of tenant information."""
    try:
        update_dict = {k: v for k, v in updates.model_dump().items() if v is not None}
        with _get_sdk() as sdk:
            result = sdk.update_tenant(building, apartment, **update_dict)
            return {"success": True, "data": result}
    except ValidationError as e:
        raise HTTPException(400, str(e)) from e


@router.delete("/tenants/{building}/{apartment}")
async def end_tenancy(building: int, apartment: int):
    """End tenancy for an apartment."""
    try:
        with _get_sdk() as sdk:
            result = sdk.end_tenancy(building, apartment, move_out_date=date.today())
            return {"success": True, "data": result}
    except ValidationError as e:
        raise HTTPException(400, str(e)) from e


@router.get("/tenants/{building}/{apartment}/history")
async def get_tenant_history(building: int, apartment: int):
    """Get tenant history for an apartment."""
    with _get_sdk() as sdk:
        history = sdk.get_tenant_history(building, apartment)
        return {"history": history}


@router.get("/reports/occupancy")
async def get_occupancy_report(building: Optional[int] = Query(None)):
    """Generate occupancy report prompt for AI."""
    with _get_sdk() as sdk:
        response = sdk.get_occupancy_report(building)
        if response.is_error():
            raise HTTPException(500, "Failed to generate report")
        return response.data


@router.get("/reports/tenant-list")
async def get_tenant_list_report(
    building: Optional[int] = Query(None),
    include_contacts: bool = Query(False)
):
    """Generate tenant list report prompt for AI."""
    with _get_sdk() as sdk:
        response = sdk.get_tenant_list_report(building, include_contacts)
        if response.is_error():
            raise HTTPException(500, "Failed to generate report")
        return response.data
