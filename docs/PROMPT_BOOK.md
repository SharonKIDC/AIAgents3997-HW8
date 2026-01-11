# AI Prompt Book

This document catalogs:
1. **Development Prompts**: Commands given to Claude to build this project
2. **Application Prompts**: AI prompts used in the system for report generation

---

## Table of Contents

- [Development Prompts](#development-prompts)
  - [PreProject Phase](#preproject-phase-prompts)
  - [TaskLoop Phase](#taskloop-phase-prompts)
  - [ReleaseGate Phase](#releasegate-phase-prompts)
- [Application Prompts](#application-prompts)
  - [Overview](#overview)
  - [System Architecture](#system-architecture)
- [Prompt Templates](#prompt-templates)
  - [Occupancy Report](#occupancy-report)
  - [Tenant List Report](#tenant-list-report)
  - [History Report](#history-report)
  - [Custom Query](#custom-query)
- [MCP Prompt Definitions](#mcp-prompt-definitions)
- [Usage Examples](#usage-examples)
- [Best Practices](#best-practices)

---

## Development Prompts

These are the key prompts/commands given to Claude AI to build this project.

### PreProject Phase Prompts

**1. Project Initialization**
```
Create a new project for a Residential Complex Tenant Management System.
Set up repository structure with Python 3.10+, FastAPI, and React.
Follow 5-stage MCP architecture.
```

**2. PRD Creation**
```
Create a comprehensive PRD document for the Tenant Management System.
Include problem statement, functional requirements, non-functional requirements,
success metrics, and risk mitigation strategies.
Support 4 buildings: 11 (40 apts), 13 (35 apts), 15 (40 apts), 17 (35 apts).
```

**3. Architecture Design**
```
Design system architecture using 5-stage MCP pattern:
Stage 1: Infrastructure (config, logging, exceptions)
Stage 2: Database (Excel operations, models, validation)
Stage 3: MCP Server (FastAPI with tools, resources, prompts)
Stage 4: Communication (HTTP client, SDK abstraction)
Stage 5: UI (React dashboard, AI query interface)
```

**4. Security Baseline**
```
Set up security configuration:
- Create .env.example with all required variables
- Create config.yaml for non-secret settings
- Add .gitignore for secrets protection
- Document security guidelines in docs/SECURITY.md
```

### TaskLoop Phase Prompts

**5. Stage 1 Implementation**
```
Implement Stage 1 Infrastructure:
- Config loading from YAML and .env
- Structured logging with file and console output
- Custom exception hierarchy (TenantError base class)
- Unit tests with pytest
```

**6. Stage 2 Implementation**
```
Implement Stage 2 Database Layer:
- Pydantic models for Tenant, Building, TenantHistory
- ExcelManager for low-level openpyxl operations
- ExcelOperations for business logic (CRUD)
- TenantQueries for complex data queries
- DataValidator for input validation
- Comprehensive unit tests
```

**7. Stage 3 Implementation**
```
Implement Stage 3 MCP Server:
- FastAPI application with CORS middleware
- TenantTools class (create_tenant, update_tenant, end_tenancy)
- TenantResources class (get buildings, tenants, occupancy, history)
- ReportPrompts class for AI prompt generation
- OpenAPI/Swagger documentation
- Integration tests
```

**8. Stage 4 Implementation**
```
Implement Stage 4 Communication Layer:
- BaseMCPClient abstract class
- MCPHttpClient implementation with requests
- Response types and error handling
- Session management with context managers
```

**9. Stage 5 Implementation**
```
Implement Stage 5 UI/SDK:
- TenantSDK high-level client
- React dashboard with building cards
- Tenant registration form with validation
- AI query interface with Markdown rendering
- Owner vs Renter workflow
- Tenant replacement flow
- Family member tracking (WhatsApp, PalGate)
```

**10. Testing & Quality**
```
Run all tests and fix any failures.
Ensure 80%+ code coverage.
Run linting with black, ruff, pylint.
Fix all linting errors.
```

### ReleaseGate Phase Prompts

**11. Packaging**
```
Configure Python packaging:
- Update pyproject.toml with all dependencies
- Verify pip install -e . works
- Ensure version numbers are synced
```

**12. Documentation Updates**
```
Update all documentation:
- README with comprehensive info and screenshot
- Architecture.md with Mermaid flowcharts
- Create EXAMPLE.md with usage examples
- Update PRD with flowcharts
- Create COSTS.md and BUDGET.md with Claude costs
```

**13. Quality Gates**
```
Run final quality gates:
- All tests passing
- Coverage > 80%
- No linting errors
- No security issues
- Documentation complete
```

### Ad-Hoc Development Prompts

**14. Feature: Owner Information**
```
When registering a renter (non-owner), require owner details:
- Owner first name, last name, phone
- Display owner info separately in tenant details
```

**15. Feature: Tenant Replacement**
```
When adding tenant to occupied apartment:
- Detect existing tenant
- Prompt for confirmation
- Auto-set move-out date for previous tenant
- Preserve history
```

**16. Feature: Family Members**
```
Add support for multiple family members per apartment:
- WhatsApp list with names and phones
- PalGate access list with names, phones, vehicle plates
- Generate export lists for both
```

**17. Documentation Overhaul**
```
Update all docs - links don't work.
Learn the project thoroughly.
Update README with all relevant info and app screenshot.
Create EXAMPLE.md with comprehensive explanations.
Convert all diagrams to Mermaid flowcharts.
```

---

## Application Prompts

This section describes the prompts used within the application for AI report generation.

## Overview

The Tenant Management System uses AI-powered report generation through a Model Context Protocol (MCP) architecture. Prompts are structured templates that guide the AI model (OpenAI GPT-4 or compatible) to generate formatted Markdown reports based on tenant data.

**Key Principles:**
- All prompts produce Markdown output for consistency
- Templates are parameterized for flexibility
- System prompts provide context about available data
- User prompts contain specific queries and formatting instructions

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      React Web UI                           │
│            (Natural Language Query Input)                   │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    MCP HTTP Client                          │
│               (POST /prompts/generate)                      │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    MCP Server                               │
│              (ReportPrompts class)                          │
│                                                             │
│   ┌─────────────────┐  ┌─────────────────────────────────┐ │
│   │ Prompt Templates│  │ Prompt Definitions (MCP Schema) │ │
│   └─────────────────┘  └─────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    AI Report Agent                          │
│         (OpenAI GPT-4 / Mock Provider)                      │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│              Markdown Report Output                         │
│           (Optional: PDF Export)                            │
└─────────────────────────────────────────────────────────────┘
```

---

## Prompt Templates

### Occupancy Report

**Purpose:** Generate occupancy statistics and vacancy information for buildings.

**Template Location:** `src/mcp_server/prompt_templates.py`

```python
OCCUPANCY_TEMPLATE = """
{context}

Include:
1. Total apartments vs occupied
2. Vacancy rate
3. List of vacant apartments
4. Summary statistics

Format as Markdown with tables where appropriate.
"""
```

**Parameters:**
- `context`: Dynamic context string (e.g., "Generate occupancy report for building 11" or "Generate occupancy report for all buildings")

**Example Output:**
```markdown
# Occupancy Report - Building 11

## Summary
| Metric | Value |
|--------|-------|
| Total Apartments | 40 |
| Occupied | 34 |
| Vacant | 6 |
| Occupancy Rate | 85% |

## Vacant Apartments
- Apartment 103
- Apartment 207
- Apartment 315
- Apartment 402
- Apartment 501
- Apartment 512
```

---

### Tenant List Report

**Purpose:** Generate a list of current tenants with optional contact information.

**Template Location:** `src/mcp_server/prompt_templates.py`

```python
TENANT_LIST_TEMPLATE = """
{context} {contact_text}

Include:
1. Tenant names and apartment numbers
2. Owner/renter status
3. Move-in dates
4. Organized by building

Format as Markdown with tables.
"""
```

**Parameters:**
- `context`: Dynamic context (e.g., "Generate tenant list for building 15")
- `contact_text`: Optional string ("Include phone numbers." or empty)

**Example Output:**
```markdown
# Tenant List - Building 15

| Apartment | Tenant Name | Status | Move-In Date | Phone |
|-----------|-------------|--------|--------------|-------|
| 101 | John Smith | Owner | 2023-01-15 | 054-1234567 |
| 102 | Sarah Cohen | Renter | 2024-03-20 | 052-9876543 |
| 103 | - | Vacant | - | - |
...
```

---

### History Report

**Purpose:** Generate tenant history timeline for a specific apartment.

**Template Location:** `src/mcp_server/prompt_templates.py`

```python
HISTORY_TEMPLATE = """
Generate tenant history report for Building {building}, Apartment {apartment}.

Include:
1. Current tenant information
2. Timeline of all previous tenants
3. Duration of each tenancy
4. Owner/renter status for each period

Format as Markdown with a timeline visualization.
"""
```

**Parameters:**
- `building`: Building number (integer)
- `apartment`: Apartment number (integer)

**Example Output:**
```markdown
# Tenant History - Building 11, Apartment 205

## Current Tenant
**John Smith** (Owner)
- Move-in: March 15, 2023
- Duration: 1 year, 10 months (ongoing)

## Previous Tenants

### 2021-2023: David Cohen (Renter)
- Move-in: January 10, 2021
- Move-out: March 14, 2023
- Duration: 2 years, 2 months

### 2018-2021: Rachel Levi (Owner)
- Move-in: June 1, 2018
- Move-out: January 9, 2021
- Duration: 2 years, 7 months
```

---

### Custom Query

**Purpose:** Process natural language queries about tenant data.

**Template Location:** `src/mcp_server/prompt_templates.py`

```python
SYSTEM_PROMPT_TEMPLATE = """
You are a tenant management assistant. You have access to tenant data for:
{building_info}

You can query:
- Current tenants and their details
- Tenant history for apartments
- Occupancy statistics
- WhatsApp group contacts
- Parking authorizations

Respond in Markdown format.
"""
```

**Parameters:**
- `building_info`: Formatted string with building details (e.g., "Building 11 (40 apartments), Building 13 (35 apartments), Building 15 (40 apartments), Building 17 (35 apartments)")

**Example Queries:**
- "How many residents live in building #15?"
- "Show me all tenants who moved in during 2024"
- "List apartments with parking access but no WhatsApp group membership"
- "What's the average tenancy duration across all buildings?"

---

## MCP Prompt Definitions

The MCP server exposes prompt definitions following the Model Context Protocol schema:

```json
{
  "prompts": [
    {
      "name": "occupancy_report",
      "description": "Generate occupancy report for buildings",
      "arguments": [
        {
          "name": "building",
          "description": "Building number (optional)",
          "required": false
        }
      ]
    },
    {
      "name": "tenant_list_report",
      "description": "Generate tenant list report",
      "arguments": [
        {
          "name": "building",
          "description": "Building number (optional)",
          "required": false
        },
        {
          "name": "include_contacts",
          "description": "Include phone numbers",
          "required": false
        }
      ]
    },
    {
      "name": "history_report",
      "description": "Generate tenant history report for an apartment",
      "arguments": [
        {
          "name": "building",
          "description": "Building number",
          "required": true
        },
        {
          "name": "apartment",
          "description": "Apartment number",
          "required": true
        }
      ]
    },
    {
      "name": "custom_query",
      "description": "Process a natural language query about tenants",
      "arguments": [
        {
          "name": "query",
          "description": "Natural language query",
          "required": true
        }
      ]
    }
  ]
}
```

---

## Usage Examples

### Python SDK Usage

```python
from src.ai_agent import ReportAgent

# Initialize report agent
with ReportAgent() as agent:
    # Generate occupancy report for all buildings
    result = agent.generate_occupancy_report()
    print(result.content)

    # Generate occupancy for specific building
    result = agent.generate_occupancy_report(building=11)
    print(result.content)

    # Generate tenant list with contacts
    result = agent.generate_tenant_list_report(
        building=15,
        include_contacts=True
    )
    print(result.content)

    # Get apartment history
    result = agent.generate_history_report(building=11, apartment=205)
    print(result.content)

    # Custom natural language query
    result = agent.process_custom_query(
        "How many residents live in building #15?"
    )
    print(result.content)
```

### REST API Usage

```bash
# Generate occupancy report prompt
curl -X POST http://localhost:8000/prompts/generate \
  -H "Content-Type: application/json" \
  -d '{
    "name": "occupancy_report",
    "arguments": {"building": 11}
  }'

# Generate custom query prompt
curl -X POST http://localhost:8000/prompts/generate \
  -H "Content-Type: application/json" \
  -d '{
    "name": "custom_query",
    "arguments": {"query": "Show all vacant apartments"}
  }'
```

### JavaScript/React Usage

```javascript
// Using fetch API
const generateReport = async (query) => {
  const response = await fetch('http://localhost:8000/prompts/generate', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      name: 'custom_query',
      arguments: { query }
    })
  });
  return await response.json();
};

// Example usage in React component
const [report, setReport] = useState('');

const handleQuery = async () => {
  const result = await generateReport('How many residents in building 15?');
  setReport(result.content);
};
```

---

## Best Practices

### Writing Effective Queries

1. **Be Specific**: "Show tenants in building 11 who moved in after January 2024" is better than "Show recent tenants"

2. **Use Building Numbers**: Reference buildings by their actual numbers (11, 13, 15, 17)

3. **Specify Output Format**: If you need specific formatting, mention it in the query

4. **Include Filters**: Add relevant filters like date ranges, status (owner/renter), or access permissions

### Extending Prompts

To add new prompt templates:

1. Add template in `src/mcp_server/prompt_templates.py`:
```python
NEW_TEMPLATE = """
{context}

Include specific instructions...

Format as Markdown.
"""
```

2. Add prompt definition in `src/mcp_server/prompts.py`:
```python
@staticmethod
def get_prompt_definitions() -> list:
    return [
        # ... existing prompts
        {
            "name": "new_report",
            "description": "Description of new report",
            "arguments": [
                {"name": "param", "description": "Parameter description", "required": True}
            ],
        },
    ]
```

3. Add generation method:
```python
@staticmethod
def get_new_report_prompt(param: str) -> dict[str, Any]:
    text = NEW_TEMPLATE.format(context=param)
    return {"messages": [{"role": "user", "content": {"type": "text", "text": text}}]}
```

4. Register in server (`src/mcp_server/server.py`):
```python
if request.name == "new_report":
    return ReportPrompts.get_new_report_prompt(args["param"])
```

---

## LLM Provider Configuration

The system supports multiple LLM providers:

### OpenAI (Default for Production)

```bash
# .env configuration
AI_MODEL_PROVIDER=openai
AI_MODEL_NAME=gpt-4o
OPENAI_API_KEY=sk-your-key-here
```

### Mock Provider (Testing)

When no valid API key is configured, the system automatically uses a mock provider that returns template responses for testing.

### Custom Provider

Implement `LLMProvider` interface:

```python
from src.ai_agent.reporter import LLMProvider

class CustomProvider(LLMProvider):
    def generate(self, messages: list[dict]) -> str:
        # Your implementation
        pass

# Use with ReportAgent
agent = ReportAgent(llm_provider=CustomProvider())
```

---

**Document Version:** 1.0.0
**Last Updated:** 2026-01-11
