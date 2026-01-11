"""Tests for MCP Server module.

Comprehensive tests for tools, resources, prompts, and API endpoints.
"""

import os
import tempfile
from datetime import date

import pytest
from fastapi.testclient import TestClient

from src.database import ExcelManager, Tenant
from src.mcp_server.tools import TenantTools
from src.mcp_server.resources import TenantResources
from src.mcp_server.prompts import ReportPrompts
from src.mcp_server.server import create_app


@pytest.fixture
def temp_db():
    """Create temporary database file with initialized structure."""
    temp_dir = tempfile.mkdtemp()
    db_path = os.path.join(temp_dir, "test_tenants.xlsx")
    ExcelManager(db_path=db_path)
    yield db_path
    if os.path.exists(db_path):
        os.unlink(db_path)
    if os.path.exists(temp_dir):
        os.rmdir(temp_dir)


@pytest.fixture
def test_client(temp_db):
    """Create test client with temp database."""
    app = create_app(db_path=temp_db)
    return TestClient(app)


class TestTenantTools:
    """Tests for TenantTools."""

    def test_get_tool_definitions(self):
        """Test getting tool definitions."""
        definitions = TenantTools.get_tool_definitions()
        assert len(definitions) == 4
        names = [d["name"] for d in definitions]
        assert "create_tenant" in names
        assert "update_tenant" in names
        assert "end_tenancy" in names
        assert "get_tenant" in names

    def test_create_tenant(self, temp_db):
        """Test creating a tenant via tool."""
        tools = TenantTools(db_path=temp_db)
        result = tools.create_tenant({
            "building_number": 11,
            "apartment_number": 1,
            "first_name": "John",
            "last_name": "Doe",
            "phone": "0501234567"
        })
        assert result["success"] is True
        assert result["tenant"]["first_name"] == "John"

    def test_get_tenant(self, temp_db):
        """Test getting a tenant via tool."""
        tools = TenantTools(db_path=temp_db)
        tools.create_tenant({
            "building_number": 11,
            "apartment_number": 1,
            "first_name": "John",
            "last_name": "Doe",
            "phone": "0501234567"
        })
        result = tools.get_tenant({
            "building_number": 11,
            "apartment_number": 1
        })
        assert result["success"] is True
        assert result["tenant"]["first_name"] == "John"

    def test_get_tenant_not_found(self, temp_db):
        """Test getting non-existent tenant."""
        tools = TenantTools(db_path=temp_db)
        result = tools.get_tenant({
            "building_number": 11,
            "apartment_number": 99
        })
        assert result["success"] is True
        assert result["tenant"] is None


class TestTenantResources:
    """Tests for TenantResources."""

    def test_get_resource_definitions(self):
        """Test getting resource definitions."""
        definitions = TenantResources.get_resource_definitions()
        assert len(definitions) == 7
        uris = [d["uri"] for d in definitions]
        assert "tenants://buildings" in uris
        assert "tenants://tenants" in uris

    def test_get_buildings(self, temp_db):
        """Test getting all buildings."""
        resources = TenantResources(db_path=temp_db)
        result = resources.get_buildings()
        assert "buildings" in result
        assert len(result["buildings"]) == 4

    def test_get_occupancy_stats(self, temp_db):
        """Test getting occupancy statistics."""
        resources = TenantResources(db_path=temp_db)
        result = resources.get_occupancy_stats()
        assert "buildings" in result
        assert "total" in result
        assert result["total"]["occupancy_rate"] == 0


class TestReportPrompts:
    """Tests for ReportPrompts."""

    def test_get_prompt_definitions(self):
        """Test getting prompt definitions."""
        definitions = ReportPrompts.get_prompt_definitions()
        assert len(definitions) == 4
        names = [d["name"] for d in definitions]
        assert "occupancy_report" in names
        assert "custom_query" in names

    def test_get_occupancy_prompt(self):
        """Test getting occupancy prompt."""
        prompt = ReportPrompts.get_occupancy_prompt()
        assert "messages" in prompt
        assert len(prompt["messages"]) == 1

    def test_get_custom_query_prompt(self):
        """Test getting custom query prompt."""
        prompt = ReportPrompts.get_custom_query_prompt("How many tenants?")
        assert "messages" in prompt
        assert len(prompt["messages"]) == 2


class TestMCPServerAPI:
    """Tests for MCP Server API endpoints."""

    def test_root_endpoint(self, test_client):
        """Test root endpoint."""
        response = test_client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Tenant Management MCP Server"

    def test_list_tools(self, test_client):
        """Test listing tools."""
        response = test_client.get("/tools")
        assert response.status_code == 200
        data = response.json()
        assert "tools" in data

    def test_list_resources(self, test_client):
        """Test listing resources."""
        response = test_client.get("/resources")
        assert response.status_code == 200
        data = response.json()
        assert "resources" in data

    def test_list_prompts(self, test_client):
        """Test listing prompts."""
        response = test_client.get("/prompts")
        assert response.status_code == 200
        data = response.json()
        assert "prompts" in data

    def test_get_buildings_api(self, test_client):
        """Test getting buildings via API."""
        response = test_client.get("/resources/buildings")
        assert response.status_code == 200
        data = response.json()
        assert "buildings" in data
        assert len(data["buildings"]) == 4

    def test_get_occupancy_api(self, test_client):
        """Test getting occupancy via API."""
        response = test_client.get("/resources/occupancy")
        assert response.status_code == 200
        data = response.json()
        assert "buildings" in data
        assert "total" in data

    def test_invoke_create_tenant(self, test_client):
        """Test invoking create_tenant tool via API."""
        response = test_client.post("/tools/invoke", json={
            "name": "create_tenant",
            "arguments": {
                "building_number": 11,
                "apartment_number": 1,
                "first_name": "Jane",
                "last_name": "Smith",
                "phone": "0509876543"
            }
        })
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

    def test_invoke_unknown_tool(self, test_client):
        """Test invoking unknown tool."""
        response = test_client.post("/tools/invoke", json={
            "name": "unknown_tool",
            "arguments": {}
        })
        assert response.status_code == 404

    def test_generate_prompt(self, test_client):
        """Test generating a prompt."""
        response = test_client.post("/prompts/generate", json={
            "name": "occupancy_report",
            "arguments": {}
        })
        assert response.status_code == 200
        data = response.json()
        assert "messages" in data
