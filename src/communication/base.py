"""Base abstractions for MCP client communication.

Defines interfaces and data models for MCP server communication.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List


@dataclass
class MCPResponse:
    """Standard response from MCP server."""

    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    status_code: int = 200

    def is_error(self) -> bool:
        """Check if response indicates an error."""
        return not self.success or self.error is not None


@dataclass
class ToolDefinition:
    """Definition of an MCP tool."""

    name: str
    description: str
    parameters: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ResourceDefinition:
    """Definition of an MCP resource."""

    uri: str
    name: str
    description: str


@dataclass
class PromptDefinition:
    """Definition of an MCP prompt."""

    name: str
    description: str
    arguments: List[Dict[str, Any]] = field(default_factory=list)


class BaseMCPClient(ABC):
    """Abstract base class for MCP client implementations."""

    @abstractmethod
    def get_server_info(self) -> MCPResponse:
        """Get server information."""

    @abstractmethod
    def list_tools(self) -> List[ToolDefinition]:
        """List available tools."""

    @abstractmethod
    def invoke_tool(self, name: str, arguments: Dict[str, Any]) -> MCPResponse:
        """Invoke a tool with arguments."""

    @abstractmethod
    def list_resources(self) -> List[ResourceDefinition]:
        """List available resources."""

    @abstractmethod
    def get_resource(self, uri: str, params: Optional[Dict[str, Any]] = None) -> MCPResponse:
        """Get a resource by URI."""

    @abstractmethod
    def list_prompts(self) -> List[PromptDefinition]:
        """List available prompts."""

    @abstractmethod
    def generate_prompt(self, name: str, arguments: Dict[str, Any]) -> MCPResponse:
        """Generate a prompt with arguments."""
