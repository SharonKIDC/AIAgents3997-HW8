"""API routes for React web frontend.

Provides REST endpoints optimized for the React UI components.
"""

import re
from datetime import date, timedelta
from typing import Optional, List, Dict, Any

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, field_validator, model_validator

from src.sdk import TenantSDK
from src.config import get_config
from src.exceptions import ValidationError


router = APIRouter(prefix="/api", tags=["web-ui"])


def _get_validation_config() -> Dict[str, Any]:
    """Get validation configuration."""
    config = get_config()
    return {
        "phone": {
            "min_length": config.get("tenant_registration.phone.min_length", 9),
            "max_length": config.get("tenant_registration.phone.max_length", 15),
            "pattern": config.get("tenant_registration.phone.pattern", r"^[0-9\-\+]+$"),
            "pattern_description": config.get(
                "tenant_registration.phone.pattern_description",
                "Phone must contain only digits, dashes, and plus sign",
            ),
        },
        "name": {
            "min_length": config.get("tenant_registration.name.min_length", 2),
            "max_length": config.get("tenant_registration.name.max_length", 50),
            "pattern": config.get(
                "tenant_registration.name.pattern", r"^[a-zA-Z\u0590-\u05FF\s\-']+$"
            ),
            "pattern_description": config.get(
                "tenant_registration.name.pattern_description",
                "Name must contain only letters, spaces, hyphens, and apostrophes",
            ),
        },
        "family_members": {
            "max_whatsapp_members": config.get(
                "tenant_registration.family_members.max_whatsapp_members", 2
            ),
            "max_palgate_members": config.get(
                "tenant_registration.family_members.max_palgate_members", 4
            ),
            "main_tenant_always_included": config.get(
                "tenant_registration.family_members.main_tenant_always_included", True
            ),
        },
        "vehicle_plate": {
            "max_length": config.get("tenant_registration.vehicle_plate.max_length", 10),
            "pattern": config.get("tenant_registration.vehicle_plate.pattern", r"^[0-9\-]+$"),
            "pattern_description": config.get(
                "tenant_registration.vehicle_plate.pattern_description",
                "Vehicle plate must contain only digits and dashes",
            ),
        },
    }


def _validate_name(name: str, field_name: str, config: Dict) -> List[str]:
    """Validate a name field and return errors."""
    errors = []
    name_config = config["name"]

    if len(name) < name_config["min_length"]:
        errors.append(f"{field_name} must be at least {name_config['min_length']} characters")
    if len(name) > name_config["max_length"]:
        errors.append(f"{field_name} must be at most {name_config['max_length']} characters")
    if not re.match(name_config["pattern"], name):
        errors.append(f"{field_name}: {name_config['pattern_description']}")

    return errors


def _validate_phone(phone: str, field_name: str, config: Dict) -> List[str]:
    """Validate a phone field and return errors."""
    errors = []
    phone_config = config["phone"]

    if len(phone) < phone_config["min_length"]:
        errors.append(f"{field_name} must be at least {phone_config['min_length']} characters")
    if len(phone) > phone_config["max_length"]:
        errors.append(f"{field_name} must be at most {phone_config['max_length']} characters")
    if not re.match(phone_config["pattern"], phone):
        errors.append(f"{field_name}: {phone_config['pattern_description']}")

    return errors


def _validate_vehicle_plate(plate: str, config: Dict) -> List[str]:
    """Validate vehicle plate and return errors."""
    if not plate:
        return []

    errors = []
    plate_config = config["vehicle_plate"]

    if len(plate) > plate_config["max_length"]:
        errors.append(f"Vehicle plate must be at most {plate_config['max_length']} characters")
    if not re.match(plate_config["pattern"], plate):
        errors.append(plate_config["pattern_description"])

    return errors


class FamilyMember(BaseModel):
    """Family member with WhatsApp and PalGate flags."""

    first_name: str
    last_name: str
    phone: str
    whatsapp_enabled: bool = False
    palgate_enabled: bool = False
    vehicle_plate: Optional[str] = None


class OwnerInfoCreate(BaseModel):
    """Owner information for renters."""

    first_name: str
    last_name: str
    phone: str


class TenantCreate(BaseModel):
    """Request model for tenant creation."""

    building_number: int
    apartment_number: int
    first_name: str
    last_name: str
    phone: str
    is_owner: bool = True
    owner_info: Optional[OwnerInfoCreate] = None
    move_in_date: Optional[str] = None
    storage_number: Optional[int] = None
    parking_slot_1: Optional[int] = None
    parking_slot_2: Optional[int] = None
    family_members: List[FamilyMember] = []
    replace_existing: bool = False


class TenantUpdate(BaseModel):
    """Request model for tenant updates."""

    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    is_owner: Optional[bool] = None
    owner_info: Optional[OwnerInfoCreate] = None
    storage_number: Optional[int] = None
    parking_slot_1: Optional[int] = None
    parking_slot_2: Optional[int] = None
    whatsapp_group_enabled: Optional[bool] = None
    palgate_access_enabled: Optional[bool] = None
    family_members: Optional[List[FamilyMember]] = None


def _get_sdk() -> TenantSDK:
    """Get SDK instance."""
    return TenantSDK()


def _validate_tenant_data(tenant: TenantCreate) -> Dict[str, List[str]]:
    """Validate tenant data and return field-specific errors."""
    config = _get_validation_config()
    errors: Dict[str, List[str]] = {}

    # Validate tenant name
    first_name_errors = _validate_name(tenant.first_name, "First name", config)
    if first_name_errors:
        errors["first_name"] = first_name_errors

    last_name_errors = _validate_name(tenant.last_name, "Last name", config)
    if last_name_errors:
        errors["last_name"] = last_name_errors

    # Validate tenant phone
    phone_errors = _validate_phone(tenant.phone, "Phone", config)
    if phone_errors:
        errors["phone"] = phone_errors

    # Validate owner info for renters
    if not tenant.is_owner:
        if not tenant.owner_info:
            errors["owner_info"] = ["Owner information is required for renters"]
        else:
            owner_fn_errors = _validate_name(
                tenant.owner_info.first_name, "Owner first name", config
            )
            if owner_fn_errors:
                errors["owner_first_name"] = owner_fn_errors

            owner_ln_errors = _validate_name(tenant.owner_info.last_name, "Owner last name", config)
            if owner_ln_errors:
                errors["owner_last_name"] = owner_ln_errors

            owner_phone_errors = _validate_phone(tenant.owner_info.phone, "Owner phone", config)
            if owner_phone_errors:
                errors["owner_phone"] = owner_phone_errors

    # Validate family members
    family_config = config["family_members"]
    whatsapp_count = sum(1 for m in tenant.family_members if m.whatsapp_enabled)
    palgate_count = sum(1 for m in tenant.family_members if m.palgate_enabled)

    if whatsapp_count > family_config["max_whatsapp_members"]:
        errors["family_members"] = errors.get("family_members", [])
        errors["family_members"].append(
            f"Maximum {family_config['max_whatsapp_members']} additional WhatsApp members allowed"
        )

    if palgate_count > family_config["max_palgate_members"]:
        errors["family_members"] = errors.get("family_members", [])
        errors["family_members"].append(
            f"Maximum {family_config['max_palgate_members']} additional PalGate members allowed"
        )

    # Validate each family member
    for i, member in enumerate(tenant.family_members):
        member_errors = []

        fn_errors = _validate_name(member.first_name, "First name", config)
        member_errors.extend(fn_errors)

        ln_errors = _validate_name(member.last_name, "Last name", config)
        member_errors.extend(ln_errors)

        ph_errors = _validate_phone(member.phone, "Phone", config)
        member_errors.extend(ph_errors)

        if member.vehicle_plate:
            vp_errors = _validate_vehicle_plate(member.vehicle_plate, config)
            member_errors.extend(vp_errors)

        if member_errors:
            errors[f"family_member_{i}"] = member_errors

    return errors


@router.get("/config/validation")
async def get_validation_config():
    """Get validation configuration for frontend."""
    return _get_validation_config()


@router.get("/buildings")
async def list_buildings():
    """Get all buildings with occupancy info."""
    try:
        with _get_sdk() as sdk:
            buildings = sdk.get_buildings()
            result = []
            for b in buildings:
                # Get occupancy data for each building
                occupancy = sdk.get_building_occupancy(b.number)
                if occupancy:
                    result.append({
                        "number": occupancy.number,
                        "total_apartments": occupancy.total_apartments,
                        "occupied": occupancy.occupied,
                        "vacant": occupancy.vacant,
                        "occupancy_rate": occupancy.occupancy_rate,
                    })
                else:
                    result.append({
                        "number": b.number,
                        "total_apartments": b.total_apartments,
                        "occupied": 0,
                        "vacant": b.total_apartments,
                        "occupancy_rate": 0.0,
                    })
            return {"buildings": result}
    except Exception:
        # Return empty list if MCP server is unavailable
        return {"buildings": []}


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
            "occupancy_rate": building.occupancy_rate,
        }


@router.get("/buildings/{building_number}/floor-map")
async def get_building_floor_map(building_number: int):
    """Get building floor map with tenant information for visualization."""
    config = get_config()
    buildings_config = config.get("buildings", [])

    # Find building config
    building_config = None
    for b in buildings_config:
        if b.get("number") == building_number:
            building_config = b
            break

    if not building_config:
        raise HTTPException(404, f"Building {building_number} not found")

    floors_config = building_config.get("floors", [])
    if not floors_config:
        raise HTTPException(404, f"Floor configuration not found for building {building_number}")

    # Get all tenants for this building
    with _get_sdk() as sdk:
        tenants_list = sdk.get_all_tenants(building_number)

    # Create a map of apartment -> tenant
    tenant_map = {}
    for t in tenants_list:
        apt_num = t.get("apartment_number")
        tenant_map[apt_num] = {
            "first_name": t.get("first_name"),
            "last_name": t.get("last_name"),
            "full_name": f"{t.get('first_name')} {t.get('last_name')}",
            "phone": t.get("phone"),
            "is_owner": t.get("is_owner", True),
            "move_in_date": t.get("move_in_date"),
        }

    # Build floor map response
    floor_map = []
    for floor in sorted(floors_config, key=lambda f: f.get("level", 0), reverse=True):
        level = floor.get("level", 0)
        apartments = floor.get("apartments", [])
        floor_data = {
            "level": level,
            "apartments": []
        }
        for apt_num in apartments:
            tenant = tenant_map.get(apt_num)
            floor_data["apartments"].append({
                "apartment_number": apt_num,
                "occupied": tenant is not None,
                "tenant": tenant
            })
        floor_map.append(floor_data)

    return {
        "building_number": building_number,
        "total_apartments": building_config.get("total_apartments", 0),
        "total_floors": len(floors_config),
        "floors": floor_map
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
            return {"exists": False}
        return {
            "exists": True,
            "building_number": tenant.building_number,
            "apartment_number": tenant.apartment_number,
            "first_name": tenant.first_name,
            "last_name": tenant.last_name,
            "full_name": tenant.full_name,
            "phone": tenant.phone,
            "is_owner": tenant.is_owner,
            "move_in_date": tenant.move_in_date.isoformat() if tenant.move_in_date else None,
        }


@router.post("/tenants")
async def create_tenant(tenant: TenantCreate):
    """Create a new tenant with validation."""
    # Validate all fields first
    validation_errors = _validate_tenant_data(tenant)
    if validation_errors:
        return {
            "success": False,
            "validation_errors": validation_errors,
            "message": "Please fix the validation errors",
        }

    try:
        move_in = date.today()
        if tenant.move_in_date:
            move_in = date.fromisoformat(tenant.move_in_date)

        with _get_sdk() as sdk:
            # Check if apartment is already occupied
            existing = sdk.get_tenant(tenant.building_number, tenant.apartment_number)
            if existing and not tenant.replace_existing:
                return {
                    "success": False,
                    "requires_confirmation": True,
                    "existing_tenant": {
                        "first_name": existing.first_name,
                        "last_name": existing.last_name,
                        "phone": existing.phone,
                        "move_in_date": (
                            existing.move_in_date.isoformat() if existing.move_in_date else None
                        ),
                    },
                    "message": f"Apartment already occupied by {existing.full_name}",
                }

            # If replacing, end the existing tenancy first
            if existing and tenant.replace_existing:
                move_out = move_in - timedelta(days=1)
                sdk.end_tenancy(
                    tenant.building_number, tenant.apartment_number, move_out_date=move_out
                )

            # Build owner_info dict if provided
            owner_info = None
            if tenant.owner_info:
                owner_info = {
                    "first_name": tenant.owner_info.first_name,
                    "last_name": tenant.owner_info.last_name,
                    "phone": tenant.owner_info.phone,
                }

            # Build WhatsApp and PalGate member lists from family members
            whatsapp_members = [
                {"first_name": m.first_name, "last_name": m.last_name, "phone": m.phone}
                for m in tenant.family_members
                if m.whatsapp_enabled
            ]
            palgate_members = [
                {
                    "first_name": m.first_name,
                    "last_name": m.last_name,
                    "phone": m.phone,
                    "vehicle_plate": m.vehicle_plate,
                }
                for m in tenant.family_members
                if m.palgate_enabled
            ]

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
                parking_slot_2=tenant.parking_slot_2,
                owner_info=owner_info,
                whatsapp_members=whatsapp_members,
                palgate_members=palgate_members,
            )
            return {"success": True, "data": result}
    except ValidationError as e:
        return {"success": False, "validation_errors": {"_general": [str(e)]}, "message": str(e)}
    except Exception as e:
        return {
            "success": False,
            "validation_errors": {"_general": [str(e)]},
            "message": "An unexpected error occurred",
        }


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
    building: Optional[int] = Query(None), include_contacts: bool = Query(False)
):
    """Generate tenant list report prompt for AI."""
    with _get_sdk() as sdk:
        response = sdk.get_tenant_list_report(building, include_contacts)
        if response.is_error():
            raise HTTPException(500, "Failed to generate report")
        return response.data


class AIQueryRequest(BaseModel):
    """Request model for AI query."""

    query: str
    building: Optional[int] = None


@router.post("/query")
async def process_ai_query(request: AIQueryRequest):
    """Process natural language query about tenants.

    Uses AI to analyze tenant data and generate responses to questions like:
    - "Show me all tenants who moved in during 2024"
    - "List vacant apartments in building 11"
    - "Which tenants are renters?"
    """
    from src.ai_agent.reporter import ReportAgent

    if not request.query or len(request.query.strip()) < 3:
        return {"success": False, "error": "Query must be at least 3 characters"}

    try:
        with ReportAgent() as agent:
            # Get all tenant data for context
            with _get_sdk() as sdk:
                if request.building:
                    tenants = sdk.get_all_tenants(request.building)
                else:
                    tenants = sdk.get_all_tenants()
                buildings = sdk.get_buildings()

            # Build context with tenant data
            context = _build_query_context(tenants, buildings, request.building)

            # Process the query with context
            result = agent.process_custom_query(f"{request.query}\n\nContext:\n{context}")

            return {"success": True, "response": result.content, "metadata": result.metadata}
    except Exception as e:
        return {"success": False, "error": str(e)}


def _build_query_context(tenants: List, buildings: List, building_filter: Optional[int]) -> str:
    """Build context string from tenant and building data."""
    lines = []

    # Building info
    lines.append("## Buildings")
    for b in buildings:
        lines.append(f"- Building {b.number}: {b.total_apartments} apartments")

    # Tenant data
    lines.append("\n## Current Tenants")
    if not tenants:
        lines.append("No tenants found.")
    else:
        for t in tenants:
            tenant_type = "Owner" if t.get("is_owner", True) else "Renter"
            move_in = t.get("move_in_date", "N/A")
            lines.append(
                f"- Bldg {t.get('building_number')}, Apt {t.get('apartment_number')}: "
                f"{t.get('first_name')} {t.get('last_name')} ({tenant_type}), "
                f"Phone: {t.get('phone')}, Move-in: {move_in}"
            )

    if building_filter:
        lines.append(f"\n(Filtered to building {building_filter})")

    return "\n".join(lines)
