"""MCP Server package for tenant management.

Provides Model Context Protocol server implementation with
tools, resources, and prompts for tenant data operations.
"""

from src.mcp_server.prompts import ReportPrompts
from src.mcp_server.resources import TenantResources
from src.mcp_server.server import app, create_app
from src.mcp_server.tools import TenantTools

__all__ = [
    "TenantTools",
    "TenantResources",
    "ReportPrompts",
    "create_app",
    "app",
]
