"""Prompt templates for AI report generation.

Contains the actual template text for various report types.
"""

OCCUPANCY_TEMPLATE = """
{context}

Include:
1. Total apartments vs occupied
2. Vacancy rate
3. List of vacant apartments
4. Summary statistics

Format as Markdown with tables where appropriate.
"""

TENANT_LIST_TEMPLATE = """
{context} {contact_text}

Include:
1. Tenant names and apartment numbers
2. Owner/renter status
3. Move-in dates
4. Organized by building

Format as Markdown with tables.
"""

HISTORY_TEMPLATE = """
Generate tenant history report for Building {building}, Apartment {apartment}.

Include:
1. Current tenant information
2. Timeline of all previous tenants
3. Duration of each tenancy
4. Owner/renter status for each period

Format as Markdown with a timeline visualization.
"""

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
