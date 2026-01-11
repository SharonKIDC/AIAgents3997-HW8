"""FastAPI MCP Server for tenant management.

Main server implementation providing REST API endpoints
for tools, resources, and prompts.
"""

from typing import Dict, Any, Optional
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from src.config import get_config
from src.exceptions import ValidationError, NotFoundError, DatabaseError
from src.mcp_server.tools import TenantTools
from src.mcp_server.resources import TenantResources
from src.mcp_server.prompts import ReportPrompts


class ToolRequest(BaseModel):
    """Request model for tool invocation."""

    name: str
    arguments: Dict[str, Any]


class PromptRequest(BaseModel):
    """Request model for prompt generation."""

    name: str
    arguments: Optional[Dict[str, Any]] = None


def _configure_cors(application: FastAPI) -> None:
    """Configure CORS middleware for the application."""
    config = get_config()
    if config.get("mcp_server.enable_cors", True):
        origins = config.get("mcp_server.allowed_origins", ["*"])
        application.add_middleware(
            CORSMiddleware,
            allow_origins=origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )


def create_app(db_path: str = None) -> FastAPI:
    """Create and configure FastAPI application."""
    application = FastAPI(
        title="Tenant Management MCP Server",
        description="MCP Server for residential complex tenant management",
        version="1.0.0",
    )
    _configure_cors(application)
    tools = TenantTools(db_path)
    resources = TenantResources(db_path)

    @application.get("/")
    async def root():
        """Server info endpoint."""
        return {"name": "Tenant Management MCP Server", "version": "1.0.0", "protocol": "mcp"}

    @application.get("/tools")
    async def list_tools():
        """List available MCP tools."""
        return {"tools": TenantTools.get_tool_definitions()}

    @application.post("/tools/invoke")
    async def invoke_tool(request: ToolRequest):
        """Invoke an MCP tool."""
        try:
            if request.name == "create_tenant":
                return tools.create_tenant(request.arguments)
            if request.name == "update_tenant":
                return tools.update_tenant(request.arguments)
            if request.name == "end_tenancy":
                return tools.end_tenancy(request.arguments)
            if request.name == "get_tenant":
                return tools.get_tenant(request.arguments)
            raise HTTPException(404, f"Tool not found: {request.name}")
        except ValidationError as e:
            raise HTTPException(400, str(e)) from e
        except NotFoundError as e:
            raise HTTPException(404, str(e)) from e
        except DatabaseError as e:
            raise HTTPException(500, str(e)) from e

    @application.get("/resources")
    async def list_resources():
        """List available MCP resources."""
        return {"resources": TenantResources.get_resource_definitions()}

    @application.get("/resources/buildings")
    async def get_buildings():
        """Get all buildings."""
        return resources.get_buildings()

    @application.get("/resources/buildings/{building_number}")
    async def get_building(building_number: int):
        """Get building details."""
        return resources.get_building_details(building_number)

    @application.get("/resources/tenants")
    async def get_tenants(building: Optional[int] = Query(None)):
        """Get all tenants."""
        return resources.get_all_tenants(building)

    @application.get("/resources/tenants/{building}/{apartment}/history")
    async def get_history(building: int, apartment: int):
        """Get tenant history for an apartment."""
        return resources.get_tenant_history(building, apartment)

    @application.get("/resources/occupancy")
    async def get_occupancy():
        """Get occupancy statistics."""
        return resources.get_occupancy_stats()

    @application.get("/resources/whatsapp")
    async def get_whatsapp(building: Optional[int] = Query(None)):
        """Get WhatsApp contacts."""
        return resources.get_whatsapp_contacts(building)

    @application.get("/resources/parking")
    async def get_parking(building: Optional[int] = Query(None)):
        """Get parking authorizations."""
        return resources.get_parking_authorizations(building)

    @application.get("/prompts")
    async def list_prompts():
        """List available MCP prompts."""
        return {"prompts": ReportPrompts.get_prompt_definitions()}

    @application.post("/prompts/generate")
    async def generate_prompt(request: PromptRequest):
        """Generate a prompt for AI processing."""
        args = request.arguments or {}
        if request.name == "occupancy_report":
            return ReportPrompts.get_occupancy_prompt(args.get("building"))
        if request.name == "tenant_list_report":
            return ReportPrompts.get_tenant_list_prompt(
                args.get("building"), args.get("include_contacts", False)
            )
        if request.name == "history_report":
            return ReportPrompts.get_history_prompt(args["building"], args["apartment"])
        if request.name == "custom_query":
            return ReportPrompts.get_custom_query_prompt(args["query"])
        raise HTTPException(404, f"Prompt not found: {request.name}")

    return application


app = create_app()
