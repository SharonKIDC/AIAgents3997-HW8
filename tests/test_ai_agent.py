"""Tests for AI agent components."""

import pytest
from unittest.mock import Mock, patch, MagicMock

from src.ai_agent import ReportAgent, PDFGenerator
from src.ai_agent.reporter import ReportResult, MockLLMProvider, LLMProvider
from src.ai_agent.pdf_generator import PDFConfig
from src.communication import MCPResponse


class TestReportResult:
    """Tests for ReportResult dataclass."""

    def test_report_result_creation(self):
        """Test report result creation."""
        result = ReportResult(
            content="# Report\n\nContent here", format="markdown", metadata={"type": "occupancy"}
        )
        assert result.content.startswith("# Report")
        assert result.format == "markdown"

    def test_report_result_defaults(self):
        """Test report result defaults."""
        result = ReportResult(content="Test")
        assert result.format == "markdown"
        assert result.metadata is None


class TestMockLLMProvider:
    """Tests for MockLLMProvider."""

    def test_generate_with_user_message(self):
        """Test generation with user message."""
        provider = MockLLMProvider()
        messages = [{"role": "user", "content": {"type": "text", "text": "Generate report"}}]
        result = provider.generate(messages)
        assert "Report" in result
        assert "Generate report" in result

    def test_generate_without_user_message(self):
        """Test generation without user message."""
        provider = MockLLMProvider()
        messages = [{"role": "system", "content": "System prompt"}]
        result = provider.generate(messages)
        assert "No query provided" in result


class TestReportAgent:
    """Tests for ReportAgent."""

    @pytest.fixture
    def mock_client(self):
        """Create mock MCP client."""
        with patch("src.ai_agent.reporter.MCPHttpClient") as mock:
            client_instance = MagicMock()
            mock.return_value = client_instance
            yield client_instance

    @pytest.fixture
    def agent(self, mock_client):
        """Create agent with mock client."""
        return ReportAgent(mcp_url="http://test:8000")

    def test_generate_occupancy_report(self, agent, mock_client):
        """Test occupancy report generation."""
        mock_client.generate_prompt.return_value = MCPResponse(
            success=True,
            data={"messages": [{"role": "user", "content": {"text": "Occupancy report"}}]},
        )
        result = agent.generate_occupancy_report(building=11)
        assert result.content is not None
        assert result.metadata["report_type"] == "occupancy"
        assert result.metadata["building"] == 11

    def test_generate_occupancy_report_error(self, agent, mock_client):
        """Test occupancy report with error."""
        mock_client.generate_prompt.return_value = MCPResponse(success=False, error="Error")
        result = agent.generate_occupancy_report()
        assert "Failed" in result.content
        assert result.metadata["error"] is True

    def test_generate_tenant_list_report(self, agent, mock_client):
        """Test tenant list report generation."""
        mock_client.generate_prompt.return_value = MCPResponse(
            success=True, data={"messages": [{"role": "user", "content": {"text": "Tenant list"}}]}
        )
        result = agent.generate_tenant_list_report(building=13, include_contacts=True)
        assert result.metadata["report_type"] == "tenant_list"

    def test_generate_history_report(self, agent, mock_client):
        """Test history report generation."""
        mock_client.generate_prompt.return_value = MCPResponse(
            success=True,
            data={"messages": [{"role": "user", "content": {"text": "History report"}}]},
        )
        result = agent.generate_history_report(building=11, apartment=5)
        assert result.metadata["report_type"] == "history"
        assert result.metadata["apartment"] == 5

    def test_process_custom_query(self, agent, mock_client):
        """Test custom query processing."""
        mock_client.generate_prompt.return_value = MCPResponse(
            success=True, data={"messages": [{"role": "user", "content": {"text": "Custom query"}}]}
        )
        result = agent.process_custom_query("Who lives in apartment 1?")
        assert result.metadata["report_type"] == "custom"
        assert "query" in result.metadata

    def test_context_manager(self, mock_client):
        """Test context manager usage."""
        with ReportAgent() as agent:
            assert agent is not None
        mock_client.close.assert_called_once()


class TestPDFGenerator:
    """Tests for PDFGenerator."""

    @pytest.fixture
    def generator(self):
        """Create PDF generator."""
        return PDFGenerator()

    def test_generator_initialization(self):
        """Test generator initialization."""
        generator = PDFGenerator()
        assert generator is not None

    def test_generator_with_config(self):
        """Test generator with custom config."""
        config = PDFConfig(title_font_size=20)
        generator = PDFGenerator(config=config)
        assert generator._config.title_font_size == 20

    def test_generate_simple_pdf(self, generator):
        """Test simple PDF generation."""
        markdown = "# Test Report\n\nThis is a test report."
        pdf_bytes = generator.generate(markdown, title="Test")
        assert pdf_bytes is not None
        assert len(pdf_bytes) > 0
        assert pdf_bytes[:4] == b"%PDF"

    def test_generate_pdf_with_table(self, generator):
        """Test PDF generation with table."""
        markdown = """# Report

| Name | Value |
|------|-------|
| Test | 123   |
"""
        pdf_bytes = generator.generate(markdown, title="Table Report")
        assert pdf_bytes[:4] == b"%PDF"

    def test_generate_pdf_with_list(self, generator):
        """Test PDF generation with list."""
        markdown = """# Report

- Item 1
- Item 2
* Item 3
"""
        pdf_bytes = generator.generate(markdown, title="List Report")
        assert pdf_bytes[:4] == b"%PDF"

    def test_generate_pdf_with_formatting(self, generator):
        """Test PDF with Markdown formatting."""
        markdown = """# Report

**Bold text** and *italic text* and `code`.

## Section
Some content here.
"""
        pdf_bytes = generator.generate(markdown, title="Formatted Report")
        assert pdf_bytes[:4] == b"%PDF"

    def test_save_to_file(self, generator, tmp_path):
        """Test saving PDF to file."""
        markdown = "# Test\n\nContent"
        filepath = tmp_path / "test.pdf"
        generator.save_to_file(markdown, str(filepath), title="Test")
        assert filepath.exists()
        assert filepath.read_bytes()[:4] == b"%PDF"
