# Comprehensive Usage Examples

This document provides detailed, working examples for all major operations in the Tenant Management System.

---

## Table of Contents

- [Getting Started](#getting-started)
- [SDK Examples](#sdk-examples)
- [REST API Examples](#rest-api-examples)
- [AI Report Examples](#ai-report-examples)
- [Database Operations](#database-operations)
- [Web UI Walkthrough](#web-ui-walkthrough)
- [Common Workflows](#common-workflows)

---

## Getting Started

### Starting the Servers

```bash
# Terminal 1: Start MCP Server
source .venv/bin/activate
uvicorn src.mcp_server.server:app --host 0.0.0.0 --port 8000 --reload

# Terminal 2: Start Web UI Server
source .venv/bin/activate
uvicorn src.web_ui.backend:web_app --host 0.0.0.0 --port 8080 --reload
```

### Verify Servers are Running

```bash
# Check MCP Server
curl http://localhost:8000/
# Response: {"name": "Tenant Management MCP Server", "version": "1.0.0", "protocol": "mcp"}

# Check Web UI
curl http://localhost:8080/health
# Response: {"status": "healthy", "service": "web-ui"}
```

---

## SDK Examples

### Initialize SDK

```python
from src.sdk import TenantSDK

# Default connection (localhost:8000)
sdk = TenantSDK()

# Custom connection
sdk = TenantSDK(base_url="http://192.168.1.100:8000", timeout=30)

# Using context manager (recommended)
with TenantSDK() as sdk:
    # operations here
    pass
```

### Create Tenant (Owner)

```python
from src.sdk import TenantSDK
from datetime import date

with TenantSDK() as sdk:
    result = sdk.create_tenant(
        building=11,
        apartment=101,
        first_name="David",
        last_name="Cohen",
        phone="054-1234567",
        is_owner=True,
        storage_number=5,
        parking_slot_1=12
    )
    print(f"Created tenant: {result}")
```

### Create Tenant (Renter with Owner Info)

```python
from src.sdk import TenantSDK

with TenantSDK() as sdk:
    result = sdk.create_tenant(
        building=13,
        apartment=205,
        first_name="Sarah",
        last_name="Levi",
        phone="052-9876543",
        is_owner=False,
        owner_info={
            "first_name": "Moshe",
            "last_name": "Goldberg",
            "phone": "054-5555555"
        }
    )
    print(f"Created renter: {result}")
```

### Get Tenant Information

```python
from src.sdk import TenantSDK

with TenantSDK() as sdk:
    tenant = sdk.get_tenant(building=11, apartment=101)

    if tenant:
        print(f"Name: {tenant.full_name}")
        print(f"Phone: {tenant.phone}")
        print(f"Owner: {tenant.is_owner}")
        print(f"Move-in: {tenant.move_in_date}")
        print(f"Parking: {tenant.parking_slot_1}")
    else:
        print("Apartment is vacant")
```

### List All Tenants

```python
from src.sdk import TenantSDK

with TenantSDK() as sdk:
    # All buildings
    all_tenants = sdk.get_all_tenants()
    print(f"Total tenants: {len(all_tenants)}")

    # Specific building
    building_11 = sdk.get_all_tenants(building=11)
    print(f"\nBuilding 11 tenants ({len(building_11)}):")
    for t in building_11:
        print(f"  Apt {t['apartment_number']}: {t['first_name']} {t['last_name']}")
```

### Get Building Occupancy

```python
from src.sdk import TenantSDK

with TenantSDK() as sdk:
    # Get all buildings
    buildings = sdk.get_buildings()
    for b in buildings:
        print(f"Building {b.number}: {b.total_apartments} apartments")

    # Get detailed occupancy for one building
    b11 = sdk.get_building_occupancy(11)
    if b11:
        print(f"\nBuilding {b11.number}:")
        print(f"  Total: {b11.total_apartments}")
        print(f"  Occupied: {b11.occupied}")
        print(f"  Vacant: {b11.vacant}")
        print(f"  Rate: {b11.occupancy_rate:.1f}%")
```

### Get Tenant History

```python
from src.sdk import TenantSDK

with TenantSDK() as sdk:
    history = sdk.get_tenant_history(building=11, apartment=101)

    print(f"Tenant history for Building 11, Apt 101:")
    for record in history:
        print(f"  {record['first_name']} {record['last_name']}")
        print(f"    Move-in: {record['move_in_date']}")
        print(f"    Move-out: {record.get('move_out_date', 'Current')}")
        print()
```

### End Tenancy

```python
from src.sdk import TenantSDK
from datetime import date

with TenantSDK() as sdk:
    # End tenancy with specific date
    result = sdk.end_tenancy(
        building=11,
        apartment=101,
        move_out_date=date(2026, 1, 31)
    )
    print(f"Tenancy ended: {result}")

    # End tenancy today
    result = sdk.end_tenancy(building=13, apartment=205)
    print(f"Tenancy ended today: {result}")
```

---

## REST API Examples

### Using curl

```bash
# Get server info
curl http://localhost:8000/

# List available tools
curl http://localhost:8000/tools

# List available resources
curl http://localhost:8000/resources

# List available prompts
curl http://localhost:8000/prompts
```

### Get Buildings

```bash
# All buildings
curl http://localhost:8000/resources/buildings

# Example response:
# {
#   "buildings": [
#     {"number": 11, "total_apartments": 40, "floors": 10},
#     {"number": 13, "total_apartments": 35, "floors": 9},
#     {"number": 15, "total_apartments": 40, "floors": 10},
#     {"number": 17, "total_apartments": 35, "floors": 9}
#   ]
# }

# Specific building with occupancy
curl http://localhost:8000/resources/buildings/11

# Example response:
# {
#   "building": {"number": 11, "total_apartments": 40, "floors": 10},
#   "occupancy": {"occupied": 34, "vacant": 6, "occupancy_rate": 85.0},
#   "tenants": [...]
# }
```

### Get Tenants

```bash
# All tenants
curl http://localhost:8000/resources/tenants

# Tenants in building 11
curl "http://localhost:8000/resources/tenants?building=11"

# Tenant history
curl http://localhost:8000/resources/tenants/11/101/history
```

### Get Occupancy Statistics

```bash
curl http://localhost:8000/resources/occupancy

# Example response:
# {
#   "total_apartments": 150,
#   "occupied": 126,
#   "vacant": 24,
#   "occupancy_rate": 84.0,
#   "buildings": [
#     {"building": 11, "total": 40, "occupied": 34, "vacant": 6, "rate": 85.0},
#     {"building": 13, "total": 35, "occupied": 32, "vacant": 3, "rate": 91.4},
#     ...
#   ]
# }
```

### Create Tenant

```bash
curl -X POST http://localhost:8000/tools/invoke \
  -H "Content-Type: application/json" \
  -d '{
    "name": "create_tenant",
    "arguments": {
      "building_number": 11,
      "apartment_number": 102,
      "first_name": "Rachel",
      "last_name": "Stern",
      "phone": "054-7777777",
      "is_owner": true,
      "storage_number": 10,
      "parking_slot_1": 25
    }
  }'
```

### Update Tenant

```bash
curl -X POST http://localhost:8000/tools/invoke \
  -H "Content-Type: application/json" \
  -d '{
    "name": "update_tenant",
    "arguments": {
      "building_number": 11,
      "apartment_number": 102,
      "updates": {
        "phone": "054-8888888",
        "parking_slot_2": 26
      }
    }
  }'
```

### End Tenancy

```bash
curl -X POST http://localhost:8000/tools/invoke \
  -H "Content-Type: application/json" \
  -d '{
    "name": "end_tenancy",
    "arguments": {
      "building_number": 11,
      "apartment_number": 102,
      "move_out_date": "2026-01-31"
    }
  }'
```

### Get WhatsApp Contacts

```bash
# All contacts
curl http://localhost:8000/resources/whatsapp

# Building 11 contacts
curl "http://localhost:8000/resources/whatsapp?building=11"
```

### Get Parking Authorizations

```bash
curl http://localhost:8000/resources/parking
curl "http://localhost:8000/resources/parking?building=11"
```

---

## AI Report Examples

### Using the ReportAgent

```python
from src.ai_agent import ReportAgent

with ReportAgent() as agent:
    # Occupancy report for all buildings
    report = agent.generate_occupancy_report()
    print(report.content)

    # Occupancy report for specific building
    report = agent.generate_occupancy_report(building=11)
    print(report.content)

    # Tenant list with contacts
    report = agent.generate_tenant_list_report(building=15, include_contacts=True)
    print(report.content)

    # Apartment history
    report = agent.generate_history_report(building=11, apartment=101)
    print(report.content)

    # Custom natural language query
    report = agent.process_custom_query(
        "How many apartments have parking access but no WhatsApp group membership?"
    )
    print(report.content)
```

### Generate AI Prompt via API

```bash
# Occupancy report prompt
curl -X POST http://localhost:8000/prompts/generate \
  -H "Content-Type: application/json" \
  -d '{
    "name": "occupancy_report",
    "arguments": {"building": 11}
  }'

# Custom query prompt
curl -X POST http://localhost:8000/prompts/generate \
  -H "Content-Type: application/json" \
  -d '{
    "name": "custom_query",
    "arguments": {"query": "List all renters in building 15 with their owner info"}
  }'
```

### Example Query Results

**Query**: "How many residents live in building #15?"

**AI Response**:
```markdown
# Building 15 Resident Count

## Summary
Building 15 currently has **36 occupied apartments** out of 40 total units.

## Breakdown
| Metric | Value |
|--------|-------|
| Total Apartments | 40 |
| Occupied | 36 |
| Vacant | 4 |
| Occupancy Rate | 90% |

## Vacant Apartments
- Apartment 105
- Apartment 218
- Apartment 307
- Apartment 412
```

---

## Database Operations

### Direct Database Access (for testing/debugging)

```python
from src.database import ExcelManager, TenantQueries, DataValidator

# Initialize
db_path = "./data/excel/tenants.xlsx"
manager = ExcelManager(db_path)
queries = TenantQueries(db_path)
validator = DataValidator()

# Load database
manager.load()

# Get all tenants from building 11
tenants = queries.get_tenants_by_building(11)
for tenant in tenants:
    print(f"{tenant.first_name} {tenant.last_name}")

# Validate phone number
if validator.validate_phone("054-1234567"):
    print("Valid phone")
else:
    print("Invalid phone")

# Get occupancy stats
stats = queries.get_occupancy_stats()
print(f"Total: {stats['total']}, Occupied: {stats['occupied']}")
```

### Data Models

```python
from src.database.models import Tenant, Building, OwnerInfo, WhatsAppMember
from datetime import date

# Create tenant model
tenant = Tenant(
    building_number=11,
    apartment_number=101,
    first_name="David",
    last_name="Cohen",
    phone="054-1234567",
    is_owner=True,
    move_in_date=date.today(),
    storage_number=5,
    parking_slot_1=12
)

# Create renter with owner info
owner = OwnerInfo(
    first_name="Moshe",
    last_name="Goldberg",
    phone="054-5555555"
)

renter = Tenant(
    building_number=13,
    apartment_number=205,
    first_name="Sarah",
    last_name="Levi",
    phone="052-9876543",
    is_owner=False,
    owner_info=owner,
    move_in_date=date.today()
)

# Get building info
building = Building.get_building(11)
print(f"Building {building.number}: {building.total_apartments} apartments")

# All buildings
for b in Building.get_all_buildings():
    print(f"Building {b.number}: {b.total_apartments} apartments on {b.floors} floors")
```

---

## Web UI Walkthrough

### Dashboard

1. **Access**: Navigate to http://localhost:8080
2. **Overview Cards**: Shows total apartments, occupied, vacant, and occupancy rate
3. **Building Cards**: Click on any building card to see details
4. **AI Query**: Enter natural language queries in the query box

### Register New Tenant

1. Click "Register Tenant" in navigation
2. Select building from dropdown
3. Enter apartment number
4. Fill in tenant details:
   - First name, last name, phone
   - Check "Is Owner" for owners
   - Uncheck for renters (owner fields will appear)
5. Add parking/storage numbers if applicable
6. Add family members for WhatsApp/PalGate
7. Click "Register"

### View/Edit Tenant

1. Click on tenant name in list
2. View all tenant details
3. Click "Edit" to modify
4. Click "End Tenancy" to move tenant out

### Generate Reports

1. Navigate to "Reports" or use AI Query box
2. Enter query like:
   - "Show all tenants in building 11"
   - "List vacant apartments"
   - "Show tenants with parking access"
   - "Generate occupancy report for building 15"
3. View Markdown report
4. Click "Export PDF" to download

---

## Common Workflows

### Workflow 1: New Tenant Move-In (Owner)

```python
from src.sdk import TenantSDK
from datetime import date

with TenantSDK() as sdk:
    # Check if apartment is vacant
    existing = sdk.get_tenant(building=11, apartment=103)
    if existing:
        print(f"Apartment is occupied by {existing.full_name}")
        return

    # Register new owner
    result = sdk.create_tenant(
        building=11,
        apartment=103,
        first_name="Yossi",
        last_name="Mizrachi",
        phone="054-2222222",
        is_owner=True,
        move_in_date=date(2026, 2, 1),
        storage_number=8,
        parking_slot_1=15
    )
    print(f"New owner registered: {result}")
```

### Workflow 2: Tenant Replacement (Renter to New Renter)

```python
from src.sdk import TenantSDK
from datetime import date

with TenantSDK() as sdk:
    # End current tenancy
    sdk.end_tenancy(
        building=13,
        apartment=205,
        move_out_date=date(2026, 1, 31)
    )
    print("Previous tenant moved out")

    # Register new renter
    result = sdk.create_tenant(
        building=13,
        apartment=205,
        first_name="Noa",
        last_name="Peretz",
        phone="052-3333333",
        is_owner=False,
        owner_info={
            "first_name": "Moshe",
            "last_name": "Goldberg",
            "phone": "054-5555555"
        },
        move_in_date=date(2026, 2, 1)
    )
    print(f"New renter registered: {result}")
```

### Workflow 3: Generate WhatsApp Contact List

```python
from src.sdk import TenantSDK

with TenantSDK() as sdk:
    # Get all tenants for WhatsApp
    tenants = sdk.get_all_tenants(building=11)

    print("WhatsApp Contacts - Building 11:")
    print("-" * 40)
    for t in tenants:
        name = f"{t['first_name']} {t['last_name']}"
        phone = t['phone']
        apt = t['apartment_number']
        print(f"Apt {apt}: {name} - {phone}")

        # Include family members if available
        for member in t.get('whatsapp_members', []):
            print(f"       Family: {member['name']} - {member['phone']}")
```

### Workflow 4: Monthly Occupancy Report

```python
from src.sdk import TenantSDK
from src.ai_agent import ReportAgent

# Get raw data
with TenantSDK() as sdk:
    buildings = sdk.get_buildings()

    print("Monthly Occupancy Report")
    print("=" * 50)

    total_apts = 0
    total_occupied = 0

    for b in buildings:
        occupancy = sdk.get_building_occupancy(b.number)
        if occupancy:
            total_apts += occupancy.total_apartments
            total_occupied += occupancy.occupied
            print(f"Building {b.number}: {occupancy.occupied}/{occupancy.total_apartments} ({occupancy.occupancy_rate:.1f}%)")

    overall_rate = (total_occupied / total_apts * 100) if total_apts > 0 else 0
    print("-" * 50)
    print(f"Overall: {total_occupied}/{total_apts} ({overall_rate:.1f}%)")

# Generate AI report
with ReportAgent() as agent:
    report = agent.generate_occupancy_report()
    print("\n" + report.content)
```

---

## Error Handling

```python
from src.sdk import TenantSDK
from src.exceptions import ValidationError, NotFoundError, DatabaseError

with TenantSDK() as sdk:
    try:
        # This will fail validation
        sdk.create_tenant(
            building=11,
            apartment=101,
            first_name="",  # Empty name
            last_name="Test",
            phone="invalid"  # Invalid phone
        )
    except ValidationError as e:
        print(f"Validation failed: {e}")

    try:
        # This will fail if tenant doesn't exist
        sdk.update_tenant(
            building=11,
            apartment=999,  # Non-existent
            phone="054-1111111"
        )
    except NotFoundError as e:
        print(f"Not found: {e}")

    try:
        # Database operations
        pass
    except DatabaseError as e:
        print(f"Database error: {e}")
```

---

**Document Version**: 1.0.0
**Last Updated**: 2026-01-11
