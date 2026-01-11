"""MCP Prompts for AI report generation.

Provides structured templates for guiding AI model in generating
tenant management reports.
"""

from typing import Any

from src.database import Building
from src.mcp_server.prompt_templates import (
    HISTORY_TEMPLATE,
    OCCUPANCY_TEMPLATE,
    SYSTEM_PROMPT_TEMPLATE,
    TENANT_LIST_TEMPLATE,
)


class ReportPrompts:
    """MCP prompts for AI report generation."""

    @staticmethod
    def get_prompt_definitions() -> list:
        """Get MCP prompt definitions."""
        return [
            {
                "name": "occupancy_report",
                "description": "Generate occupancy report for buildings",
                "arguments": [
                    {
                        "name": "building",
                        "description": "Building number (optional)",
                        "required": False,
                    }
                ],
            },
            {
                "name": "tenant_list_report",
                "description": "Generate tenant list report",
                "arguments": [
                    {
                        "name": "building",
                        "description": "Building number (optional)",
                        "required": False,
                    },
                    {
                        "name": "include_contacts",
                        "description": "Include phone numbers",
                        "required": False,
                    },
                ],
            },
            {
                "name": "history_report",
                "description": "Generate tenant history report for an apartment",
                "arguments": [
                    {"name": "building", "description": "Building number", "required": True},
                    {"name": "apartment", "description": "Apartment number", "required": True},
                ],
            },
            {
                "name": "custom_query",
                "description": "Process a natural language query about tenants",
                "arguments": [
                    {"name": "query", "description": "Natural language query", "required": True}
                ],
            },
        ]

    @staticmethod
    def get_occupancy_prompt(building: int = None) -> dict[str, Any]:
        """Get prompt for occupancy report."""
        if building:
            context = f"Generate occupancy report for building {building}."
        else:
            context = "Generate occupancy report for all buildings."
        text = OCCUPANCY_TEMPLATE.format(context=context)
        return {"messages": [{"role": "user", "content": {"type": "text", "text": text}}]}

    @staticmethod
    def get_tenant_list_prompt(
        building: int = None, include_contacts: bool = False
    ) -> dict[str, Any]:
        """Get prompt for tenant list report."""
        if building:
            context = f"Generate tenant list for building {building}."
        else:
            context = "Generate tenant list for all buildings."
        contact_text = "Include phone numbers." if include_contacts else ""
        text = TENANT_LIST_TEMPLATE.format(context=context, contact_text=contact_text)
        return {"messages": [{"role": "user", "content": {"type": "text", "text": text}}]}

    @staticmethod
    def get_history_prompt(building: int, apartment: int) -> dict[str, Any]:
        """Get prompt for tenant history report."""
        text = HISTORY_TEMPLATE.format(building=building, apartment=apartment)
        return {"messages": [{"role": "user", "content": {"type": "text", "text": text}}]}

    @staticmethod
    def get_custom_query_prompt(query: str) -> dict[str, Any]:
        """Get prompt for custom natural language query."""
        buildings = Building.get_all_buildings()
        building_info = ", ".join(
            [f"Building {b.number} ({b.total_apartments} apartments)" for b in buildings]
        )
        system_text = SYSTEM_PROMPT_TEMPLATE.format(building_info=building_info)
        return {
            "messages": [
                {"role": "system", "content": {"type": "text", "text": system_text}},
                {"role": "user", "content": {"type": "text", "text": query}},
            ]
        }
