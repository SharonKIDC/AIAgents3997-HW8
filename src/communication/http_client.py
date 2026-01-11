"""HTTP client implementation for MCP server communication.

Provides HTTP-based communication with the MCP server using requests library.
"""

from typing import Dict, Any, Optional, List

import requests

from src.config import get_config
from src.exceptions import CommunicationError
from src.communication.base import (
    BaseMCPClient,
    MCPResponse,
    ToolDefinition,
    ResourceDefinition,
    PromptDefinition,
)


class MCPHttpClient(BaseMCPClient):
    """HTTP client for MCP server communication."""

    def __init__(self, base_url: str = None, timeout: int = None):
        """Initialize HTTP client with server URL."""
        config = get_config()
        self._base_url = base_url or config.get("mcp_server.url", "http://localhost:8000")
        self._timeout = timeout or config.get("mcp_server.timeout", 30)
        self._session = requests.Session()

    def _request(
        self,
        method: str,
        endpoint: str,
        json_data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> MCPResponse:
        """Make HTTP request to MCP server."""
        url = f"{self._base_url}{endpoint}"
        try:
            response = self._session.request(
                method=method, url=url, json=json_data, params=params, timeout=self._timeout
            )
            if response.status_code >= 400:
                return MCPResponse(
                    success=False, error=response.text, status_code=response.status_code
                )
            return MCPResponse(success=True, data=response.json(), status_code=response.status_code)
        except requests.exceptions.ConnectionError as e:
            raise CommunicationError(f"Connection failed: {e}") from e
        except requests.exceptions.Timeout as e:
            raise CommunicationError(f"Request timed out: {e}") from e
        except requests.exceptions.RequestException as e:
            raise CommunicationError(f"Request failed: {e}") from e

    def get_server_info(self) -> MCPResponse:
        """Get server information."""
        return self._request("GET", "/")

    def list_tools(self) -> List[ToolDefinition]:
        """List available tools."""
        response = self._request("GET", "/tools")
        if response.is_error():
            return []
        tools = response.data.get("tools", [])
        return [
            ToolDefinition(
                name=t["name"], description=t["description"], parameters=t.get("parameters", {})
            )
            for t in tools
        ]

    def invoke_tool(self, name: str, arguments: Dict[str, Any]) -> MCPResponse:
        """Invoke a tool with arguments."""
        payload = {"name": name, "arguments": arguments}
        return self._request("POST", "/tools/invoke", json_data=payload)

    def list_resources(self) -> List[ResourceDefinition]:
        """List available resources."""
        response = self._request("GET", "/resources")
        if response.is_error():
            return []
        resources = response.data.get("resources", [])
        return [
            ResourceDefinition(uri=r["uri"], name=r["name"], description=r["description"])
            for r in resources
        ]

    def get_resource(self, uri: str, params: Optional[Dict[str, Any]] = None) -> MCPResponse:
        """Get a resource by URI."""
        endpoint = f"/resources{uri}" if uri.startswith("/") else f"/resources/{uri}"
        return self._request("GET", endpoint, params=params)

    def list_prompts(self) -> List[PromptDefinition]:
        """List available prompts."""
        response = self._request("GET", "/prompts")
        if response.is_error():
            return []
        prompts = response.data.get("prompts", [])
        return [
            PromptDefinition(
                name=p["name"], description=p["description"], arguments=p.get("arguments", [])
            )
            for p in prompts
        ]

    def generate_prompt(self, name: str, arguments: Dict[str, Any]) -> MCPResponse:
        """Generate a prompt with arguments."""
        return self._request(
            "POST", "/prompts/generate", json_data={"name": name, "arguments": arguments}
        )

    def close(self) -> None:
        """Close the HTTP session."""
        self._session.close()

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
        return False
