"""AI Report Agent for generating tenant management reports.

Uses MCP prompts and LLM API to generate formatted reports.
"""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from abc import ABC, abstractmethod

from src.communication import MCPHttpClient
from src.config import get_config


@dataclass
class ReportResult:
    """Result of report generation."""

    content: str
    format: str = "markdown"
    metadata: Optional[Dict[str, Any]] = None


class LLMProvider(ABC):
    """Abstract base class for LLM providers."""

    @abstractmethod
    def generate(self, messages: List[Dict[str, Any]]) -> str:
        """Generate response from messages."""


class MockLLMProvider(LLMProvider):
    """Mock LLM provider for testing."""

    def generate(self, messages: List[Dict[str, Any]]) -> str:
        """Generate mock response."""
        user_msg = next((m for m in messages if m.get("role") == "user"), None)
        if not user_msg:
            return "No query provided."
        content = user_msg.get("content", {})
        text = content.get("text", "") if isinstance(content, dict) else str(content)
        return f"# Report\n\nGenerated report for query: {text[:100]}"


class ReportAgent:
    """AI agent for generating tenant management reports."""

    def __init__(self, llm_provider: LLMProvider = None, mcp_url: str = None):
        """Initialize report agent."""
        config = get_config()
        self._client = MCPHttpClient(base_url=mcp_url)
        self._llm = llm_provider or MockLLMProvider()
        self._default_format = config.get("ai_agent.default_format", "markdown")

    def generate_occupancy_report(self, building: int = None) -> ReportResult:
        """Generate occupancy report."""
        args = {"building": building} if building else {}
        response = self._client.generate_prompt("occupancy_report", args)
        if response.is_error():
            return ReportResult(content="Failed to generate prompt", metadata={"error": True})
        messages = response.data.get("messages", [])
        content = self._llm.generate(messages)
        return ReportResult(
            content=content,
            format=self._default_format,
            metadata={"report_type": "occupancy", "building": building}
        )

    def generate_tenant_list_report(
        self, building: int = None, include_contacts: bool = False
    ) -> ReportResult:
        """Generate tenant list report."""
        args = {"building": building, "include_contacts": include_contacts}
        response = self._client.generate_prompt("tenant_list_report", args)
        if response.is_error():
            return ReportResult(content="Failed to generate prompt", metadata={"error": True})
        messages = response.data.get("messages", [])
        content = self._llm.generate(messages)
        return ReportResult(
            content=content,
            format=self._default_format,
            metadata={"report_type": "tenant_list", "building": building}
        )

    def generate_history_report(self, building: int, apartment: int) -> ReportResult:
        """Generate tenant history report."""
        args = {"building": building, "apartment": apartment}
        response = self._client.generate_prompt("history_report", args)
        if response.is_error():
            return ReportResult(content="Failed to generate prompt", metadata={"error": True})
        messages = response.data.get("messages", [])
        content = self._llm.generate(messages)
        return ReportResult(
            content=content,
            format=self._default_format,
            metadata={"report_type": "history", "building": building, "apartment": apartment}
        )

    def process_custom_query(self, query: str) -> ReportResult:
        """Process custom natural language query."""
        args = {"query": query}
        response = self._client.generate_prompt("custom_query", args)
        if response.is_error():
            return ReportResult(content="Failed to generate prompt", metadata={"error": True})
        messages = response.data.get("messages", [])
        content = self._llm.generate(messages)
        return ReportResult(
            content=content,
            format=self._default_format,
            metadata={"report_type": "custom", "query": query}
        )

    def close(self) -> None:
        """Close agent resources."""
        self._client.close()

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
        return False
