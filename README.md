# Residential Complex Tenant Management System

A local web-based application for managing tenant information across multiple residential buildings, featuring Excel-based storage, MCP server abstraction, React UI, and AI-powered report generation.

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![React](https://img.shields.io/badge/React-18+-61DAFB.svg)](https://reactjs.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Requirements](#requirements)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Development](#development)
- [Testing](#testing)
- [Deployment](#deployment)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)

---

## Overview

This system centralizes tenant management for residential complexes with multiple buildings (Buildings 11, 13, 15, 17). It replaces manual Excel processes with a web-based interface while maintaining Excel as the underlying database for simplicity and transparency.

**Problem Solved**: Building managers spend 5-10 hours per week managing tenant records manually, leading to data inconsistencies, lost historical information, and delayed responses to tenant needs.

**Solution**: Centralized system with:
- Web-based tenant registration and management
- Complete historical data preservation
- AI-powered report generation
- Multi-building support
- Parking access and WhatsApp group tracking

---

## Features

### Core Features

- **Multi-Building Management**: Support for buildings 11, 13, 15, 17 with varying apartment counts
- **Tenant Registration**: Track owner, tenant, move-in/move-out dates, parking, WhatsApp groups
- **Historical Data**: Complete tenant history per apartment (never overwritten)
- **AI Reports**: Natural language queries generate Markdown and PDF reports
- **Search & Filter**: Quick search by tenant name, building, parking status, WhatsApp membership
- **Dashboard**: Occupancy overview, vacancy tracking, quick statistics

### Technical Features

- **Excel Database**: Simple XLSX storage with automatic backups
- **MCP Server**: Abstraction layer for database operations
- **React UI**: Responsive web interface (desktop and tablet)
- **5-Stage Architecture**: Infrastructure → Tools → MCP → Communication → UI
- **Git Worktrees**: Parallel development workflow
- **No Hardcoded Values**: All configuration externalized

---

## Architecture

The system follows a 5-stage MCP (Model Context Protocol) architecture:

```
┌─────────────────────────────────────────────────┐
│  Stage 5: SDK/UI (React Web Application)       │
└─────────────────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────┐
│  Stage 4: Communication Layer (API Client)      │
└─────────────────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────┐
│  Stage 3: Full MCP Server (REST API)            │
└─────────────────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────┐
│  Stage 2: Basic Tools (Excel Utilities)         │
└─────────────────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────┐
│  Stage 1: Infrastructure (Config, Logging)      │
└─────────────────────────────────────────────────┘
```

**See**: [docs/Architecture.md](docs/Architecture.md) for complete technical documentation.

---

## Requirements

### System Requirements

- **Operating System**: Linux, macOS, or Windows
- **Python**: 3.10 or higher
- **Node.js**: 16+ (for React frontend)
- **npm**: 8+ (comes with Node.js)
- **Disk Space**: 100 MB (excluding data)

### Browser Requirements

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

### Optional

- Git 2.23+ (for worktree support)
- AI API Access: Anthropic API key for report generation

---

## Installation

### 1. Clone Repository

```bash
git clone https://github.com/yourusername/tenant-management.git
cd tenant-management
```

### 2. Python Environment Setup

```bash
# Create virtual environment
python3 -m venv .venv

# Activate environment
source .venv/bin/activate  # Linux/Mac
# OR: .venv\Scripts\activate  # Windows

# Upgrade pip
python -m pip install --upgrade pip setuptools wheel

# Install dependencies
pip install -r requirements.txt -r requirements-dev.txt

# Install package in editable mode
pip install -e .
```

### 3. Frontend Setup

```bash
cd src/web_ui
npm install
cd ../..
```

### 4. Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your values
nano .env
```

**Required Configuration**:
- Set `EXCEL_DATABASE_PATH` (default: `./data/excel/tenants.xlsx`)
- Set `AI_API_KEY` if using AI report generation
- Review and update other settings as needed

**See**: [docs/CONFIG.md](docs/CONFIG.md) for detailed configuration guide.

### 5. Initialize Database

```bash
# Create data directories
mkdir -p data/excel data/backups logs reports

# Initialize Excel database (creates blank template)
python -m src.database.init_db
```

---

## Configuration

### Environment Variables

Create `.env` from `.env.example` and configure:

```bash
# Database
EXCEL_DATABASE_PATH=./data/excel/tenants.xlsx

# MCP Server
MCP_SERVER_HOST=localhost
MCP_SERVER_PORT=8000

# Web UI
REACT_APP_API_BASE_URL=http://localhost:8000
REACT_APP_ENVIRONMENT=development

# AI Agent
AI_MODEL_PROVIDER=anthropic
AI_MODEL_NAME=claude-sonnet-4-5
AI_API_KEY=sk-ant-your-key-here
```

### Application Configuration

Edit `config.yaml` to customize:
- Building numbers and apartment counts
- Backup intervals
- Feature flags
- Session timeouts

**See**: [docs/CONFIG.md](docs/CONFIG.md) for complete configuration reference.

---

## Usage

### Start MCP Server

```bash
# Activate virtual environment
source .venv/bin/activate

# Start server
python -m src.mcp_server.main

# Server runs on http://localhost:8000
```

### Start Web UI

```bash
# In a new terminal
cd src/web_ui
npm start

# UI opens at http://localhost:3000
```

### Access Application

1. Open browser to http://localhost:3000
2. Dashboard shows occupancy overview
3. Click "Add Tenant" to register new tenant
4. Use search/filter to find tenants
5. Click "Generate Report" for AI-powered insights

### Common Tasks

#### Add New Tenant

1. Navigate to "Tenants" → "Add New"
2. Fill in required fields (building, apartment, names, dates)
3. Set parking access and WhatsApp group status
4. Click "Save"

#### Generate AI Report

1. Navigate to "Reports"
2. Enter natural language query (e.g., "Show vacant apartments in Building 11")
3. Click "Generate"
4. View Markdown report or download PDF

#### View Tenant History

1. Find tenant in search results
2. Click tenant name to view details
3. Click "View History" tab
4. See timeline of all previous tenants for that apartment

**See**: [docs/USAGE.md](docs/USAGE.md) for detailed usage guide (coming soon).

---

## Development

### Project Structure

```
tenant-management/
├── src/
│   ├── mcp_server/       # MCP server and API
│   ├── web_ui/           # React frontend
│   ├── ai_agent/         # AI report generation
│   └── database/         # Excel utilities
├── tests/
│   ├── unit/             # Unit tests
│   └── integration/      # Integration tests
├── docs/                 # Documentation
├── data/                 # Excel database and backups
├── config.yaml           # Application config
└── .env                  # Environment variables
```

### Git Worktree Workflow

This project uses Git worktrees for parallel development:

```bash
# Create worktree for each stage
git worktree add worktrees/01-infrastructure 01-infrastructure
git worktree add worktrees/02-basic-tools 02-basic-tools
git worktree add worktrees/03-full-mcp 03-full-mcp
git worktree add worktrees/04-communication 04-communication
git worktree add worktrees/05-sdk-ui 05-sdk-ui

# Work in each worktree independently
cd worktrees/02-basic-tools
# Make changes, commit, push
```

**See**: [docs/development/GIT_WORKFLOW.md](docs/development/GIT_WORKFLOW.md) for workflow details.

### Code Quality

Before committing:

```bash
# Linting
pylint src/ --score=y     # Must be 10/10
ruff check src/ tests/

# Formatting
black src/ tests/
isort --profile black src/ tests/

# Tests
pytest tests/ --cov=src

# Security
bandit -r src/
```

**See**: [docs/CONTRIBUTING.md](docs/CONTRIBUTING.md) for development standards.

---

## Testing

### Run All Tests

```bash
pytest tests/ -v
```

### Run Unit Tests Only

```bash
pytest tests/unit/ -v
```

### Run with Coverage

```bash
pytest tests/ --cov=src --cov-report=html
open htmlcov/index.html
```

### Run Integration Tests

```bash
pytest tests/integration/ -v
```

### Run Specific Test

```bash
pytest tests/unit/test_tenant_service.py::test_create_tenant -v
```

**Test Coverage Target**: > 80%

---

## Deployment

### Local Deployment (Development)

```bash
# Start MCP server
python -m src.mcp_server.main

# Start React dev server
cd src/web_ui && npm start
```

### Production Build

```bash
# Build React frontend
cd src/web_ui
npm run build

# Production build in src/web_ui/build/
```

### Production Deployment (Future)

- **MCP Server**: Docker container with Gunicorn/Uvicorn
- **Frontend**: Serve static build with Nginx
- **Database**: Consider migration to PostgreSQL
- **HTTPS**: Enable with Let's Encrypt
- **Monitoring**: Prometheus + Grafana

**See**: [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) for production deployment guide (coming soon).

---

## Troubleshooting

### Common Issues

#### ModuleNotFoundError: No module named 'src'

**Solution**:
```bash
# Install package in editable mode
pip install -e .
```

#### Excel file not found

**Solution**:
```bash
# Initialize database
python -m src.database.init_db
```

#### Port 8000 already in use

**Solution**:
```bash
# Change port in .env
MCP_SERVER_PORT=8001

# Or kill process using port
lsof -ti:8000 | xargs kill -9  # Mac/Linux
```

#### React app not connecting to API

**Solution**:
1. Verify MCP server is running on correct port
2. Check `REACT_APP_API_BASE_URL` in `.env`
3. Restart React dev server after changing `.env`

### Getting Help

1. Check [docs/](docs/) directory for documentation
2. Review error logs in `logs/app.log`
3. Search existing issues on GitHub
4. Open new issue with error details

---

## Contributing

We welcome contributions! Please see [docs/CONTRIBUTING.md](docs/CONTRIBUTING.md) for:
- Code of conduct
- Development setup
- Coding standards
- Pull request process
- Testing requirements

---

## License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file for details.

---

## Acknowledgments

- **MCP Protocol**: [Model Context Protocol](https://modelcontextprotocol.io/)
- **Excel Library**: [openpyxl](https://openpyxl.readthedocs.io/)
- **AI Model**: [Anthropic Claude](https://www.anthropic.com/)
- **React**: [React Documentation](https://react.dev/)

---

## Contact

For questions or support:
- **Issues**: [GitHub Issues](https://github.com/yourusername/tenant-management/issues)
- **Email**: support@example.com (update with actual contact)

---

**Version**: 1.0.0
**Last Updated**: 2026-01-10