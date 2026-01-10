# Product Requirements Document (PRD)
# Residential Complex Tenant Management System

**Version**: 1.0
**Date**: 2026-01-10
**Status**: Draft

---

## Problem Statement

### Current Situation

Residential complexes manage tenant information through fragmented, manual processes involving spreadsheets, paper records, and ad-hoc communication channels. This leads to:

- **Data inconsistency**: Multiple versions of tenant records across different files and systems
- **Historical data loss**: Previous tenant information is overwritten when new tenants move in
- **Limited accessibility**: Building managers struggle to access tenant information quickly for emergency contacts, parking authorization, and WhatsApp group management
- **Manual reporting**: Generating reports about occupancy, tenant turnover, and building statistics requires hours of manual data compilation
- **Communication gaps**: No centralized system to track WhatsApp group memberships and parking access

### Why This Is a Problem

Without a centralized tenant management system:
- Building managers waste 5-10 hours per week on manual data entry and report generation
- Emergency situations are complicated by inability to quickly access tenant contact information
- Tenant history is lost, preventing analysis of turnover patterns and occupancy trends
- Parking access authorization requires manual coordination, leading to delays and errors
- WhatsApp group management is inconsistent across buildings

### Who Is Affected

**Primary**: Building managers and property administrators across buildings 11, 13, 15, and 17
**Secondary**: Tenants (delayed services, communication issues), Property owners (lack of insights)

### Consequences of Not Solving

- Continued operational inefficiency and wasted time
- Risk of data loss and compliance issues
- Poor tenant experience due to delayed responses
- Inability to make data-driven decisions about property management
- Potential security risks from outdated parking access lists

---

## Goals and Non-Goals

### Goals

1. Centralize tenant data management in a local, web-based system
2. Preserve complete historical tenant records for all apartments
3. Enable AI-powered report generation for management insights
4. Provide easy access to tenant information for daily operations
5. Support multi-building management (buildings 11, 13, 15, 17)

### Non-Goals

1. Cloud deployment or multi-tenant SaaS architecture
2. Financial management (rent collection, accounting)
3. Maintenance request tracking
4. Tenant portal for self-service
5. Mobile native applications (web-responsive is sufficient)
6. Integration with third-party property management systems

---

## Stakeholders and Actors

### Stakeholders

- **Building Managers**: Primary users who manage tenant data and generate reports
- **Property Administrators**: Secondary users who access reports and historical data
- **IT Support**: Responsible for system setup and maintenance

### Actors (System Users)

1. **Admin User**: Full access to all buildings and all features
2. **Building Manager**: Access to specific buildings, can add/edit/view tenants
3. **Report Viewer**: Read-only access to reports and historical data

---

## Functional Requirements

### FR-1: Tenant Registration and Management

**Description**: System must support adding, editing, and viewing tenant information for each apartment.

**Requirements**:
- FR-1.1: Support tenant registration with fields: building number, apartment number, owner name, tenant name (if different), move-in date, parking access (yes/no), WhatsApp group membership (yes/no)
- FR-1.2: Track ownership information separately from current tenant information
- FR-1.3: Allow updating tenant information without losing historical data
- FR-1.4: Support marking apartments as vacant
- FR-1.5: Validate building numbers (11, 13, 15, 17) and apartment ranges

**Acceptance Criteria**:
- User can add new tenant through web UI form
- System validates all required fields before saving
- Historical data is preserved when tenant information is updated
- Vacant apartments are clearly distinguished from occupied ones

### FR-2: Multi-Building Support

**Description**: System must manage multiple buildings with varying apartment counts.

**Requirements**:
- FR-2.1: Support buildings 11 (40 apartments), 13 (35 apartments), 15 (40 apartments), 17 (35 apartments)
- FR-2.2: Display building-specific views and filters
- FR-2.3: Allow cross-building searches and reports
- FR-2.4: Prevent duplicate apartment registrations within same building

**Acceptance Criteria**:
- User can filter tenants by building
- System prevents registering apartment numbers beyond building capacity
- Reports can be generated per-building or across all buildings

### FR-3: Historical Data Preservation

**Description**: System must maintain complete historical records of all previous tenants.

**Requirements**:
- FR-3.1: Record move-out dates when tenants leave
- FR-3.2: Maintain full history of all previous tenants per apartment
- FR-3.3: Support viewing tenant history timeline for any apartment
- FR-3.4: Enable historical data analysis (e.g., average tenancy duration)

**Acceptance Criteria**:
- Moving in new tenant does not delete previous tenant data
- User can view complete tenant history for any apartment
- Historical reports show turnover trends over time

### FR-4: Parking Access Management

**Description**: System must track parking access authorization for tenants.

**Requirements**:
- FR-4.1: Record parking access status (yes/no) for each tenant
- FR-4.2: Generate list of current tenants with parking access
- FR-4.3: Support filtering and searching by parking access status
- FR-4.4: Track parking access changes over time

**Acceptance Criteria**:
- Admin can quickly generate parking authorization list
- Reports show which apartments have parking access
- Historical parking access data is preserved

### FR-5: WhatsApp Group Management

**Description**: System must track WhatsApp group membership for building communication.

**Requirements**:
- FR-5.1: Record WhatsApp group membership status per tenant
- FR-5.2: Generate list of tenants for WhatsApp group addition
- FR-5.3: Support building-specific WhatsApp group tracking
- FR-5.4: Identify tenants not yet added to WhatsApp groups

**Acceptance Criteria**:
- User can generate list of phone numbers for WhatsApp group
- System identifies new tenants not yet in WhatsApp group
- Reports show WhatsApp membership status

### FR-6: AI-Powered Report Generation

**Description**: System must generate reports using AI based on natural language queries.

**Requirements**:
- FR-6.1: Accept natural language queries (e.g., "Show me all tenants who moved in during 2024")
- FR-6.2: Generate reports in Markdown format
- FR-6.3: Support PDF export of generated reports
- FR-6.4: Include visualizations and summaries in AI reports
- FR-6.5: Support queries about occupancy rates, turnover, and trends

**Acceptance Criteria**:
- User enters plain English query and receives relevant report
- Reports are generated in Markdown format
- Reports can be exported to PDF
- AI correctly interprets common query patterns

### FR-7: Excel-Based Database

**Description**: System must use Excel as the primary data store with proper abstraction.

**Requirements**:
- FR-7.1: Store all tenant data in structured Excel workbook
- FR-7.2: Support concurrent read access (single write access acceptable)
- FR-7.3: Automatic backup of Excel database daily
- FR-7.4: Data validation to prevent corruption
- FR-7.5: Support data export to CSV format

**Acceptance Criteria**:
- All tenant data persists in Excel file
- Database file is backed up automatically
- System prevents data corruption through validation
- Exported data matches database contents

### FR-8: Web-Based User Interface

**Description**: System must provide React-based web interface for all operations.

**Requirements**:
- FR-8.1: Dashboard showing occupancy summary across all buildings
- FR-8.2: Tenant registration form with validation
- FR-8.3: Tenant search and filtering (by building, name, parking, WhatsApp status)
- FR-8.4: Tenant detail view with edit capabilities
- FR-8.5: Report generation interface with AI query input
- FR-8.6: Historical data visualization (timeline, charts)

**Acceptance Criteria**:
- UI is responsive and works on desktop and tablet
- All CRUD operations available through UI
- Search returns results within 1 second
- Forms provide clear validation feedback

### FR-9: MCP Server Abstraction Layer

**Description**: System must implement MCP server as abstraction layer between UI and database.

**Requirements**:
- FR-9.1: 5-stage MCP architecture (Infrastructure → Basic Tools → Full MCP → Communication → SDK/UI)
- FR-9.2: RESTful API for all database operations
- FR-9.3: API endpoints for tenant CRUD operations
- FR-9.4: API endpoints for report generation
- FR-9.5: API documentation (OpenAPI/Swagger)

**Acceptance Criteria**:
- All database access goes through MCP server
- API endpoints are documented and tested
- API responses use consistent JSON format
- API supports proper error handling

### FR-10: Git Worktrees for Parallel Development

**Description**: Development workflow must use Git worktrees for parallel work on 5 MCP stages.

**Requirements**:
- FR-10.1: Support simultaneous development on different MCP stages
- FR-10.2: Enable independent testing of each stage
- FR-10.3: Clean integration path for merging stages
- FR-10.4: Documentation of worktree workflow

**Acceptance Criteria**:
- Developers can work on multiple stages simultaneously
- Each worktree has independent test environment
- Merge conflicts are minimized through proper stage isolation

---

## Non-Functional Requirements

### NFR-1: Performance

- System responds to queries within 2 seconds for datasets up to 500 tenants
- Report generation completes within 10 seconds for standard queries
- UI renders within 1 second on modern browsers

### NFR-2: Usability

- Non-technical building managers can use system with < 30 minutes training
- UI follows standard web conventions (no custom interaction patterns)
- All forms include inline help text
- Error messages are clear and actionable

### NFR-3: Reliability

- Database backups run automatically every 24 hours
- System handles Excel file corruption gracefully with backup restoration
- No data loss during normal operations

### NFR-4: Maintainability

- Code follows Python PEP 8 style guidelines (enforced via Black, Pylint)
- All modules < 150 lines per file
- Test coverage > 80%
- All configuration externalized (no hardcoded values)

### NFR-5: Security

- No secrets in source code (all in environment variables)
- Input validation on all user inputs
- SQL injection protection (N/A for Excel, but validate Excel formulas)
- Authentication required for all operations (implement in Phase 2)

### NFR-6: Scalability

- Support up to 500 tenant records (current + historical)
- Support up to 10 concurrent users
- Excel file size manageable (< 10 MB)

---

## Dependencies and Assumptions

### Dependencies

- Python 3.10+ runtime environment
- Node.js and npm for React frontend build
- Excel file format compatibility (xlsx)
- AI model API access (Anthropic Claude)

### Assumptions

- Building numbers and apartment counts remain stable
- Single deployment location (local/on-premise)
- Users have modern web browsers (Chrome, Firefox, Safari)
- Excel is acceptable primary database (not SQL)
- Internet connectivity available for AI API calls

---

## Success Metrics

### KPI-1: Time Savings

**Metric**: Reduction in time spent on tenant data management
**Baseline**: 5-10 hours per week (manual)
**Target**: < 1 hour per week (with system)
**Measurement**: Weekly time tracking survey with building managers

### KPI-2: Data Accuracy

**Metric**: Percentage of tenant records with complete and accurate data
**Baseline**: ~70% (estimated based on current manual process)
**Target**: > 95%
**Measurement**: Monthly data quality audit

### KPI-3: Report Generation Speed

**Metric**: Time to generate occupancy/turnover reports
**Baseline**: 2-3 hours (manual compilation)
**Target**: < 2 minutes (AI-powered)
**Measurement**: Time from query to PDF report

### KPI-4: Historical Data Retention

**Metric**: Percentage of apartments with complete tenant history
**Baseline**: < 20% (historical data often lost)
**Target**: 100% after system deployment
**Measurement**: Database audit of historical records

### KPI-5: User Adoption

**Metric**: Percentage of building managers actively using system
**Baseline**: 0% (no system)
**Target**: > 90% within 3 months of deployment
**Measurement**: Monthly active user count

### KPI-6: System Uptime

**Metric**: System availability during business hours (8am-6pm)
**Baseline**: N/A
**Target**: > 99% uptime
**Measurement**: Automated uptime monitoring

---

## Risks and Mitigation Strategies

### Risk 1: Excel File Corruption

**Probability**: Medium
**Impact**: High (data loss)
**Mitigation**:
- Automated daily backups
- Data validation on all writes
- Backup restoration procedure documented
- Consider migration to SQLite in future phase

### Risk 2: Limited Concurrent Access

**Probability**: Medium
**Impact**: Medium (user frustration)
**Mitigation**:
- Implement optimistic locking
- Clear user feedback when write conflicts occur
- Consider queue system for write operations

### Risk 3: AI API Dependency

**Probability**: Low
**Impact**: Medium (report generation unavailable)
**Mitigation**:
- Fallback to template-based reports if API unavailable
- Cache common query results
- Document manual report generation process

### Risk 4: User Adoption Resistance

**Probability**: Low
**Impact**: High (project failure)
**Mitigation**:
- Involve building managers in design process
- Provide hands-on training sessions
- Offer ongoing support during transition period
- Demonstrate time savings with pilot deployment

### Risk 5: Data Migration from Current System

**Probability**: High
**Impact**: Medium (initial data quality issues)
**Mitigation**:
- Develop data import tools from existing Excel files
- Conduct data cleaning and validation sprint
- Pilot with one building before full rollout

---

## Milestones and Deliverables

### Milestone 1: PreProject Phase (Week 1)

**Deliverables**:
- ✅ Repository structure and scaffolding
- ✅ PRD, Architecture documentation
- ✅ Security baseline and configuration setup
- ✅ Development environment configured

### Milestone 2: Infrastructure Stage (Week 2)

**Deliverables**:
- Git worktrees setup for 5 stages
- Basic Python project structure
- Excel database schema design
- Configuration management implementation

### Milestone 3: Basic Tools Stage (Week 3)

**Deliverables**:
- Excel read/write utilities
- Data validation modules
- Backup/restore utilities
- Unit tests for core utilities

### Milestone 4: Full MCP Stage (Week 4)

**Deliverables**:
- MCP server implementation
- RESTful API endpoints
- API documentation (Swagger)
- Integration tests

### Milestone 5: Communication Layer Stage (Week 5)

**Deliverables**:
- React frontend foundation
- API client library
- Basic CRUD UI components
- End-to-end tests

### Milestone 6: SDK/UI Stage (Week 6)

**Deliverables**:
- Complete React UI with all features
- AI report generation integration
- Dashboard and visualizations
- User acceptance testing

### Milestone 7: Release Gate (Week 7)

**Deliverables**:
- Production packaging
- Deployment documentation
- User training materials
- Final quality gate approval

---

## Out of Scope (Future Phases)

The following features are explicitly out of scope for v1.0 but may be considered for future versions:

1. **Authentication & Authorization**: Multi-user access control (all users have full access in v1.0)
2. **Email Notifications**: Automated alerts for lease expirations, vacant apartments
3. **Document Management**: Upload and attach lease documents, ID copies
4. **Financial Tracking**: Rent payments, deposits, outstanding balances
5. **Maintenance Requests**: Tenant-reported issues and work order tracking
6. **Mobile Applications**: Native iOS/Android apps
7. **Advanced Analytics**: Predictive modeling for turnover, occupancy forecasting
8. **Cloud Deployment**: Multi-tenant SaaS version
9. **Integration APIs**: Third-party property management system integration
10. **Audit Logging**: Detailed change tracking and compliance reporting

---

## Appendix

### Glossary

- **Building Number**: Unique identifier for each residential building (11, 13, 15, 17)
- **Tenant**: Person or entity occupying an apartment (may differ from owner)
- **Owner**: Legal owner of the apartment unit
- **Historical Data**: Records of all previous tenants for an apartment
- **MCP Server**: Model Context Protocol server providing abstraction layer
- **Worktree**: Git feature allowing multiple working directories for one repository

### References

- MCP Specification: https://modelcontextprotocol.io/
- Excel Python Library (openpyxl): https://openpyxl.readthedocs.io/
- React Documentation: https://react.dev/
- Git Worktrees: https://git-scm.com/docs/git-worktree

---

**Document Control**

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-01-10 | System | Initial PRD creation |
