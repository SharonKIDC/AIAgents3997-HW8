# Extensibility Guide

This document describes the extension points in the Tenant Management System and provides guidelines for extending functionality safely.

---

## Table of Contents

- [Extension Axes](#extension-axes)
- [Extension Points](#extension-points)
- [Interfaces and Base Classes](#interfaces-and-base-classes)
- [Extension Examples](#extension-examples)
- [Safety Guidelines](#safety-guidelines)
- [Version Compatibility](#version-compatibility)

---

## Extension Axes

The system can be extended along several axes:

| Axis | Description | Difficulty | Examples |
|------|-------------|------------|----------|
| **LLM Providers** | Add new AI model integrations | Low | Anthropic, Google Gemini, local models |
| **Database Backends** | Replace Excel with other storage | Medium | SQLite, PostgreSQL, MongoDB |
| **Report Types** | Add new report templates | Low | Financial reports, maintenance logs |
| **Validation Rules** | Add custom validation patterns | Low | Custom phone formats, new fields |
| **MCP Tools** | Add new state-changing operations | Medium | Bulk import, data migration |
| **MCP Resources** | Add new read-only endpoints | Low | Analytics, exports |
| **UI Components** | Add new React components | Medium | Charts, forms, dashboards |

---

## Extension Points

### 1. LLM Provider Extension

**Location:** `src/ai_agent/reporter.py`

**Interface:**
```python
from abc import ABC, abstractmethod
from typing import Any

class LLMProvider(ABC):
    """Abstract base class for LLM providers."""

    @abstractmethod
    def generate(self, messages: list[dict[str, Any]]) -> str:
        """Generate response from messages.

        Args:
            messages: List of message dicts with 'role' and 'content' keys

        Returns:
            Generated text response
        """
        pass
```

**Extension Point:**
```python
# Add new provider in src/ai_agent/providers/anthropic_provider.py
from anthropic import Anthropic
from src.ai_agent.reporter import LLMProvider

class AnthropicProvider(LLMProvider):
    def __init__(self, api_key: str = None, model: str = "claude-sonnet-4-20250514"):
        self._client = Anthropic(api_key=api_key)
        self._model = model

    def generate(self, messages: list[dict]) -> str:
        response = self._client.messages.create(
            model=self._model,
            messages=self._format_messages(messages),
            max_tokens=4096
        )
        return response.content[0].text
```

### 2. Database Backend Extension

**Location:** `src/database/`

**Interface:**
```python
from abc import ABC, abstractmethod
from typing import Optional
from src.database.models import Tenant, TenantHistory

class DatabaseBackend(ABC):
    """Abstract database backend interface."""

    @abstractmethod
    def get_tenant(self, building: int, apartment: int) -> Optional[Tenant]:
        """Get tenant by building and apartment."""
        pass

    @abstractmethod
    def create_tenant(self, tenant: Tenant) -> Tenant:
        """Create a new tenant record."""
        pass

    @abstractmethod
    def update_tenant(self, tenant: Tenant) -> Tenant:
        """Update existing tenant."""
        pass

    @abstractmethod
    def get_all_tenants(self, building: Optional[int] = None) -> list[Tenant]:
        """Get all tenants, optionally filtered by building."""
        pass

    @abstractmethod
    def get_tenant_history(self, building: int, apartment: int) -> list[TenantHistory]:
        """Get tenant history for an apartment."""
        pass
```

**Extension Point:**
```python
# Add new backend in src/database/backends/sqlite_backend.py
import sqlite3
from src.database.backend import DatabaseBackend

class SQLiteBackend(DatabaseBackend):
    def __init__(self, db_path: str):
        self._conn = sqlite3.connect(db_path)
        self._init_schema()

    def get_tenant(self, building: int, apartment: int) -> Optional[Tenant]:
        cursor = self._conn.execute(
            "SELECT * FROM tenants WHERE building = ? AND apartment = ?",
            (building, apartment)
        )
        row = cursor.fetchone()
        return Tenant(**row) if row else None
```

### 3. Report Type Extension

**Location:** `src/mcp_server/prompt_templates.py`

**Extension Point:**
```python
# Add new template
PARKING_REPORT_TEMPLATE = """
Generate parking allocation report for {context}.

Include:
1. Total parking slots available
2. Allocated vs unallocated slots
3. Tenants with multiple slots
4. Waitlist if applicable

Format as Markdown with tables.
"""

# Register in prompts.py
@staticmethod
def get_parking_prompt(building: int = None) -> dict[str, Any]:
    context = f"building {building}" if building else "all buildings"
    text = PARKING_REPORT_TEMPLATE.format(context=context)
    return {"messages": [{"role": "user", "content": {"type": "text", "text": text}}]}
```

### 4. Validation Rule Extension

**Location:** `src/database/validator.py`

**Extension Point:**
```python
from src.database.validator import DataValidator

class ExtendedValidator(DataValidator):
    """Extended validator with custom rules."""

    # Add new phone format pattern
    PHONE_PATTERNS = {
        **DataValidator.PHONE_PATTERNS,
        "international": r"^\+\d{1,3}-\d{9,12}$"
    }

    def validate_vehicle_plate(self, plate: str) -> bool:
        """Validate Israeli vehicle plate format."""
        pattern = r"^\d{2,3}-\d{2,3}-\d{2,3}$"
        return bool(re.match(pattern, plate))
```

### 5. MCP Tool Extension

**Location:** `src/mcp_server/tools.py`

**Extension Point:**
```python
# Add to TenantTools class
def bulk_import(self, params: dict[str, Any]) -> dict[str, Any]:
    """Bulk import tenants from CSV."""
    csv_data = params.get("data", [])
    imported = 0
    errors = []

    for row in csv_data:
        try:
            tenant = Tenant(**row)
            self._operations.create_tenant(tenant)
            imported += 1
        except Exception as e:
            errors.append({"row": row, "error": str(e)})

    return {"imported": imported, "errors": errors}

# Register in get_tool_definitions()
{
    "name": "bulk_import",
    "description": "Import multiple tenants from CSV data",
    "inputSchema": {
        "type": "object",
        "properties": {
            "data": {
                "type": "array",
                "items": {"type": "object"}
            }
        },
        "required": ["data"]
    }
}
```

### 6. MCP Resource Extension

**Location:** `src/mcp_server/resources.py`

**Extension Point:**
```python
# Add to TenantResources class
def get_analytics(self) -> dict[str, Any]:
    """Get tenant analytics."""
    tenants = self._queries.get_all_tenants()

    return {
        "total_tenants": len(tenants),
        "owners": len([t for t in tenants if t.is_owner]),
        "renters": len([t for t in tenants if not t.is_owner]),
        "avg_tenancy_months": self._calculate_avg_tenancy(tenants),
        "turnover_rate": self._calculate_turnover_rate()
    }

# Register in server.py
@application.get("/resources/analytics")
async def get_analytics():
    return resources.get_analytics()
```

---

## Interfaces and Base Classes

### Core Interfaces

```python
# src/interfaces/__init__.py

from abc import ABC, abstractmethod
from typing import Any, Optional

class LLMProvider(ABC):
    """Interface for LLM integrations."""
    @abstractmethod
    def generate(self, messages: list[dict[str, Any]]) -> str: ...

class DatabaseBackend(ABC):
    """Interface for database backends."""
    @abstractmethod
    def get_tenant(self, building: int, apartment: int) -> Optional[Tenant]: ...
    @abstractmethod
    def create_tenant(self, tenant: Tenant) -> Tenant: ...

class MCPClient(ABC):
    """Interface for MCP communication."""
    @abstractmethod
    def invoke_tool(self, name: str, arguments: dict) -> MCPResponse: ...
    @abstractmethod
    def get_resource(self, uri: str) -> MCPResponse: ...

class ReportGenerator(ABC):
    """Interface for report generation."""
    @abstractmethod
    def generate(self, report_type: str, params: dict) -> ReportResult: ...
```

### Base Classes

```python
# src/base/__init__.py

class BaseValidator:
    """Base class for validators with common utilities."""

    @staticmethod
    def compile_patterns(patterns: dict[str, str]) -> dict[str, re.Pattern]:
        return {k: re.compile(v) for k, v in patterns.items()}

class BaseRepository:
    """Base class for data repositories."""

    def __init__(self, backend: DatabaseBackend):
        self._backend = backend

class BaseService:
    """Base class for business services."""

    def __init__(self, repository: BaseRepository):
        self._repo = repository
```

---

## Extension Examples

### Example 1: Adding Anthropic Claude Support

```python
# src/ai_agent/providers/anthropic_provider.py
"""Anthropic Claude provider for report generation."""

import os
from typing import Any
from anthropic import Anthropic
from src.ai_agent.reporter import LLMProvider

class AnthropicProvider(LLMProvider):
    """Anthropic Claude provider."""

    def __init__(self, api_key: str = None, model: str = None):
        self._api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        self._model = model or os.getenv("AI_MODEL_NAME", "claude-sonnet-4-20250514")
        self._client = Anthropic(api_key=self._api_key)

    def generate(self, messages: list[dict[str, Any]]) -> str:
        formatted = self._format_messages(messages)
        response = self._client.messages.create(
            model=self._model,
            messages=formatted,
            max_tokens=4096
        )
        return response.content[0].text

    def _format_messages(self, messages: list[dict]) -> list[dict]:
        result = []
        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", {})
            text = content.get("text", "") if isinstance(content, dict) else str(content)
            if role == "system":
                result.insert(0, {"role": "user", "content": f"[System]: {text}"})
            else:
                result.append({"role": role, "content": text})
        return result

# Usage:
# agent = ReportAgent(llm_provider=AnthropicProvider())
```

### Example 2: Adding SQLite Backend

```python
# src/database/backends/sqlite_backend.py
"""SQLite database backend implementation."""

import sqlite3
from contextlib import contextmanager
from typing import Optional
from src.database.models import Tenant, TenantHistory, Building

class SQLiteBackend:
    """SQLite implementation of database backend."""

    def __init__(self, db_path: str = "data/tenants.db"):
        self._db_path = db_path
        self._init_schema()

    @contextmanager
    def _get_connection(self):
        conn = sqlite3.connect(self._db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()

    def _init_schema(self):
        with self._get_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS tenants (
                    id INTEGER PRIMARY KEY,
                    building_number INTEGER NOT NULL,
                    apartment_number INTEGER NOT NULL,
                    first_name TEXT NOT NULL,
                    last_name TEXT NOT NULL,
                    phone TEXT NOT NULL,
                    is_owner BOOLEAN DEFAULT 1,
                    move_in_date DATE,
                    move_out_date DATE,
                    UNIQUE(building_number, apartment_number, move_out_date)
                )
            """)
            conn.commit()

    def get_tenant(self, building: int, apartment: int) -> Optional[Tenant]:
        with self._get_connection() as conn:
            cursor = conn.execute(
                """SELECT * FROM tenants
                   WHERE building_number = ? AND apartment_number = ?
                   AND move_out_date IS NULL""",
                (building, apartment)
            )
            row = cursor.fetchone()
            return Tenant(**dict(row)) if row else None
```

### Example 3: Adding Custom Report Type

```python
# src/mcp_server/custom_reports.py
"""Custom report type extensions."""

from src.mcp_server.prompt_templates import SYSTEM_PROMPT_TEMPLATE

MAINTENANCE_REPORT_TEMPLATE = """
Generate maintenance needs report for {context}.

Include:
1. Buildings requiring attention
2. Common issues by building age
3. Priority maintenance items
4. Estimated costs

Format as Markdown with priority indicators.
"""

FINANCIAL_SUMMARY_TEMPLATE = """
Generate financial summary for {context}.

Include:
1. Occupancy-based revenue potential
2. Vacancy cost impact
3. Owner vs renter distribution impact
4. Recommendations

Format as Markdown with financial tables.
"""

# Register in prompts.py get_prompt_definitions()
{
    "name": "maintenance_report",
    "description": "Generate maintenance needs report",
    "arguments": [
        {"name": "building", "description": "Building number", "required": False}
    ]
},
{
    "name": "financial_summary",
    "description": "Generate financial summary report",
    "arguments": [
        {"name": "period", "description": "Time period", "required": False}
    ]
}
```

---

## Safety Guidelines

### 1. Input Validation

Always validate extension inputs:

```python
def validate_extension_input(data: dict) -> dict:
    """Validate input before processing."""
    required_fields = ["building_number", "apartment_number"]
    for field in required_fields:
        if field not in data:
            raise ValidationError(f"Missing required field: {field}")

    # Sanitize string inputs
    for key, value in data.items():
        if isinstance(value, str):
            data[key] = sanitize_string(value)

    return data
```

### 2. Error Handling

Extensions must handle errors gracefully:

```python
class ExtensionError(Exception):
    """Base exception for extension errors."""
    pass

class ExtensionValidationError(ExtensionError):
    """Validation error in extension."""
    pass

def safe_extension_call(func):
    """Decorator for safe extension execution."""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ExtensionError:
            raise
        except Exception as e:
            raise ExtensionError(f"Extension failed: {e}") from e
    return wrapper
```

### 3. Resource Cleanup

Extensions must clean up resources:

```python
class ExtensionWithResources:
    """Extension that manages resources."""

    def __enter__(self):
        self._initialize_resources()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._cleanup_resources()
        return False

    def _cleanup_resources(self):
        """Clean up all acquired resources."""
        # Close connections, file handles, etc.
        pass
```

### 4. Configuration Isolation

Extensions should use namespaced configuration:

```yaml
# config.yaml
extensions:
  anthropic_provider:
    enabled: true
    model: "claude-sonnet-4-20250514"
    max_tokens: 4096

  sqlite_backend:
    enabled: false
    db_path: "data/tenants.db"
```

---

## Version Compatibility

### Semantic Versioning

The system follows semantic versioning (MAJOR.MINOR.PATCH):

- **MAJOR**: Breaking changes to extension interfaces
- **MINOR**: New extension points, backward compatible
- **PATCH**: Bug fixes, no interface changes

### Interface Stability

| Interface | Stability | Notes |
|-----------|-----------|-------|
| LLMProvider | Stable | No breaking changes planned |
| DatabaseBackend | Beta | May evolve in v2.0 |
| MCPClient | Stable | Follows MCP spec |
| Validation | Stable | Additive only |

### Deprecation Policy

1. Deprecated features are marked in release notes
2. Deprecation warnings added to code
3. Deprecated features supported for 2 minor versions
4. Removed in next major version

```python
import warnings

def deprecated_method(self):
    """Old method - deprecated in v1.1, removed in v2.0."""
    warnings.warn(
        "deprecated_method is deprecated, use new_method instead",
        DeprecationWarning,
        stacklevel=2
    )
    return self.new_method()
```

---

**Document Version:** 1.0.0
**Last Updated:** 2026-01-11
