"""Tests for communication layer."""

import pytest
from unittest.mock import Mock, patch, MagicMock
import requests

from src.communication import BaseMCPClient, MCPResponse, MCPHttpClient
from src.communication.base import ToolDefinition, ResourceDefinition, PromptDefinition
from src.exceptions import CommunicationError


class TestMCPResponse:
    """Tests for MCPResponse dataclass."""

    def test_successful_response(self):
        """Test successful response creation."""
        response = MCPResponse(success=True, data={"key": "value"})
        assert response.success is True
        assert response.data == {"key": "value"}
        assert response.error is None
        assert response.is_error() is False

    def test_error_response(self):
        """Test error response creation."""
        response = MCPResponse(success=False, error="Something went wrong", status_code=500)
        assert response.success is False
        assert response.error == "Something went wrong"
        assert response.status_code == 500
        assert response.is_error() is True

    def test_response_with_error_message(self):
        """Test response with error is detected."""
        response = MCPResponse(success=True, error="Warning message")
        assert response.is_error() is True


class TestToolDefinition:
    """Tests for ToolDefinition dataclass."""

    def test_tool_definition_creation(self):
        """Test tool definition creation."""
        tool = ToolDefinition(
            name="create_tenant", description="Create a new tenant", parameters={"type": "object"}
        )
        assert tool.name == "create_tenant"
        assert tool.description == "Create a new tenant"
        assert tool.parameters == {"type": "object"}

    def test_tool_definition_defaults(self):
        """Test tool definition with defaults."""
        tool = ToolDefinition(name="test", description="Test tool")
        assert tool.parameters == {}


class TestResourceDefinition:
    """Tests for ResourceDefinition dataclass."""

    def test_resource_definition_creation(self):
        """Test resource definition creation."""
        resource = ResourceDefinition(
            uri="/buildings", name="buildings", description="List of buildings"
        )
        assert resource.uri == "/buildings"
        assert resource.name == "buildings"


class TestPromptDefinition:
    """Tests for PromptDefinition dataclass."""

    def test_prompt_definition_creation(self):
        """Test prompt definition creation."""
        prompt = PromptDefinition(
            name="occupancy_report",
            description="Generate occupancy report",
            arguments=[{"name": "building", "required": False}],
        )
        assert prompt.name == "occupancy_report"
        assert len(prompt.arguments) == 1


class TestMCPHttpClient:
    """Tests for MCPHttpClient."""

    @pytest.fixture
    def mock_session(self):
        """Create mock session for testing."""
        with patch("src.communication.http_client.requests.Session") as mock:
            session_instance = MagicMock()
            mock.return_value = session_instance
            yield session_instance

    @pytest.fixture
    def client(self, mock_session):
        """Create client with mock session."""
        return MCPHttpClient(base_url="http://test:8000", timeout=10)

    def test_client_initialization(self, mock_session):
        """Test client initialization."""
        client = MCPHttpClient(base_url="http://localhost:9000", timeout=15)
        assert client._base_url == "http://localhost:9000"
        assert client._timeout == 15

    def test_get_server_info_success(self, client, mock_session):
        """Test successful server info request."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"name": "MCP Server", "version": "1.0.0"}
        mock_session.request.return_value = mock_response

        response = client.get_server_info()
        assert response.success is True
        assert response.data["name"] == "MCP Server"

    def test_get_server_info_error(self, client, mock_session):
        """Test server info request with error."""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"
        mock_session.request.return_value = mock_response

        response = client.get_server_info()
        assert response.success is False
        assert response.status_code == 500

    def test_list_tools(self, client, mock_session):
        """Test list tools request."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "tools": [
                {"name": "tool1", "description": "Tool 1", "parameters": {}},
                {"name": "tool2", "description": "Tool 2"},
            ]
        }
        mock_session.request.return_value = mock_response

        tools = client.list_tools()
        assert len(tools) == 2
        assert tools[0].name == "tool1"
        assert tools[1].description == "Tool 2"

    def test_invoke_tool(self, client, mock_session):
        """Test tool invocation."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"result": "success"}
        mock_session.request.return_value = mock_response

        response = client.invoke_tool("create_tenant", {"building": 11})
        assert response.success is True
        mock_session.request.assert_called_with(
            method="POST",
            url="http://test:8000/tools/invoke",
            json={"name": "create_tenant", "arguments": {"building": 11}},
            params=None,
            timeout=10,
        )

    def test_list_resources(self, client, mock_session):
        """Test list resources request."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "resources": [
                {"uri": "/buildings", "name": "buildings", "description": "List buildings"}
            ]
        }
        mock_session.request.return_value = mock_response

        resources = client.list_resources()
        assert len(resources) == 1
        assert resources[0].uri == "/buildings"

    def test_get_resource(self, client, mock_session):
        """Test get resource request."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"buildings": [11, 13, 15, 17]}
        mock_session.request.return_value = mock_response

        response = client.get_resource("/buildings")
        assert response.success is True
        mock_session.request.assert_called_with(
            method="GET",
            url="http://test:8000/resources/buildings",
            json=None,
            params=None,
            timeout=10,
        )

    def test_list_prompts(self, client, mock_session):
        """Test list prompts request."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "prompts": [{"name": "report", "description": "Generate report", "arguments": []}]
        }
        mock_session.request.return_value = mock_response

        prompts = client.list_prompts()
        assert len(prompts) == 1
        assert prompts[0].name == "report"

    def test_generate_prompt(self, client, mock_session):
        """Test prompt generation."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"messages": []}
        mock_session.request.return_value = mock_response

        response = client.generate_prompt("occupancy_report", {"building": 11})
        assert response.success is True

    def test_connection_error(self, client, mock_session):
        """Test connection error handling."""
        mock_session.request.side_effect = requests.exceptions.ConnectionError("Failed")

        with pytest.raises(CommunicationError) as exc:
            client.get_server_info()
        assert "Connection failed" in str(exc.value)

    def test_timeout_error(self, client, mock_session):
        """Test timeout error handling."""
        mock_session.request.side_effect = requests.exceptions.Timeout("Timed out")

        with pytest.raises(CommunicationError) as exc:
            client.get_server_info()
        assert "timed out" in str(exc.value)

    def test_context_manager(self, mock_session):
        """Test context manager usage."""
        with MCPHttpClient(base_url="http://test:8000") as client:
            assert client is not None
        mock_session.close.assert_called_once()

    def test_close(self, client, mock_session):
        """Test explicit close."""
        client.close()
        mock_session.close.assert_called_once()
