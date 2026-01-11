"""Communication layer for MCP server interaction.

Provides HTTP client and base abstractions for communicating
with the MCP server.
"""

from src.communication.base import BaseMCPClient, MCPResponse
from src.communication.http_client import MCPHttpClient

__all__ = ["BaseMCPClient", "MCPResponse", "MCPHttpClient"]
