# ADR-001: Use Excel as Primary Database

**Status**: Accepted
**Date**: 2026-01-10
**Deciders**: Architecture Team

## Context

The Residential Complex Tenant Management System needs a data storage solution that is:
- Easy to backup and restore
- Accessible to non-technical users for manual inspection
- Sufficient for small-scale data (< 500 records)
- Compatible with existing workflows (building managers already use Excel)

## Decision

We will use Excel (XLSX format) as the primary database, accessed via the openpyxl Python library.

## Rationale

**Pros**:
- **Simplicity**: No database server setup required
- **Backups**: Copy file = complete backup
- **Transparency**: Users can inspect data directly in Excel if needed
- **Compatibility**: Building managers already familiar with Excel
- **Local Deployment**: No network database dependencies
- **Portability**: Single file contains entire database

**Cons**:
- **Concurrent Access**: Limited concurrent write operations
- **Performance**: Not optimized for large datasets
- **Querying**: No SQL, must load into memory
- **Scalability**: Not suitable for > 1000 records

## Alternatives Considered

### SQLite
- **Pros**: Better performance, SQL queries, ACID transactions
- **Cons**: Less transparent to users, requires SQL knowledge for inspection

### PostgreSQL/MySQL
- **Pros**: Robust, scalable, concurrent access
- **Cons**: Server setup complexity, overkill for 150-500 records

## Mitigation Strategies

1. **Concurrent Access**: Implement optimistic locking in MCP server
2. **Performance**: Load data on startup, cache in memory
3. **Scalability**: Plan migration path to SQLite in v2.0 if needed
4. **Data Integrity**: Implement validation layer in MCP server

## Consequences

- MCP server abstracts Excel access, making future migration easier
- Automatic daily backups essential (file corruption risk)
- Write operations should be serialized to prevent conflicts
- Maximum 10 concurrent users recommendation
