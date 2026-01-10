# Configuration Guide

## Overview

The Residential Complex Tenant Management System uses a combination of environment variables and YAML configuration for maximum flexibility and security.

## Configuration Files

### .env (Environment Variables)

**Location**: Root directory (create from `.env.example`)

**Purpose**: Store sensitive secrets and environment-specific values

**Required Variables**:

| Variable | Description | Example |
|----------|-------------|---------|
| `EXCEL_DATABASE_PATH` | Path to Excel database file | `./data/excel/tenants.xlsx` |
| `MCP_SERVER_HOST` | MCP server hostname | `localhost` |
| `MCP_SERVER_PORT` | MCP server port | `8000` |
| `REACT_APP_API_BASE_URL` | Web UI API endpoint | `http://localhost:8000` |
| `REACT_APP_ENVIRONMENT` | Environment name | `development` |
| `AI_MODEL_PROVIDER` | AI provider name | `anthropic` |
| `AI_MODEL_NAME` | AI model identifier | `claude-sonnet-4-5` |
| `AI_API_KEY` | AI service API key | `sk-ant-...` |
| `LOG_LEVEL` | Logging level | `INFO` |
| `LOG_FILE_PATH` | Log file location | `./logs/app.log` |
| `SECRET_KEY` | JWT signing key (32+ chars) | (generate securely) |
| `JWT_EXPIRATION_HOURS` | JWT token lifetime | `24` |

**Optional Variables**:

| Variable | Description | Default |
|----------|-------------|---------|
| `WHATSAPP_API_ENABLED` | Enable WhatsApp integration | `false` |
| `WHATSAPP_API_KEY` | WhatsApp API key | - |

### config.yaml (Application Configuration)

**Location**: Root directory

**Purpose**: Non-sensitive application settings and defaults

**Configuration Sections**:

#### 1. Building Configuration

Defines the residential complex structure:
```yaml
buildings:
  - number: 11
    total_apartments: 40
  - number: 13
    total_apartments: 35
  - number: 15
    total_apartments: 40
  - number: 17
    total_apartments: 35
```

**Customization**: Update apartment counts to match your complex.

#### 2. MCP Server Configuration

```yaml
mcp_server:
  host: ${MCP_SERVER_HOST}
  port: ${MCP_SERVER_PORT}
  max_connections: 100
  timeout_seconds: 30
  enable_cors: true
  allowed_origins:
    - http://localhost:3000
```

**Production**: Update `allowed_origins` with your production domain.

#### 3. Database Configuration

```yaml
database:
  type: excel
  path: ${EXCEL_DATABASE_PATH}
  backup_enabled: true
  backup_interval_hours: 24
  backup_path: ./data/backups/
```

**Customization**:
- Adjust `backup_interval_hours` for backup frequency
- Change `backup_path` for backup location

#### 4. Web UI Configuration

```yaml
web_ui:
  api_base_url: ${REACT_APP_API_BASE_URL}
  environment: ${REACT_APP_ENVIRONMENT}
  session_timeout_minutes: 30
  pagination_page_size: 20
```

**Customization**: Adjust session timeout and pagination as needed.

#### 5. AI Agent Configuration

```yaml
ai_agent:
  provider: ${AI_MODEL_PROVIDER}
  model_name: ${AI_MODEL_NAME}
  max_tokens: 4000
  temperature: 0.7
  report_formats:
    - markdown
    - pdf
  output_directory: ./reports/
```

**Customization**:
- Adjust `max_tokens` and `temperature` for AI behavior
- Update `output_directory` for report storage

#### 6. Feature Flags

```yaml
features:
  enable_whatsapp_integration: false
  enable_parking_management: true
  enable_ai_reports: true
  enable_historical_data: true
```

**Usage**: Toggle features on/off without code changes.

## Environment-Specific Configuration

### Development

```bash
cp .env.example .env
# Edit .env with development values
export REACT_APP_ENVIRONMENT=development
```

### Production

```bash
# Use production environment variables
export REACT_APP_ENVIRONMENT=production
export MCP_SERVER_HOST=your-production-domain.com
export REACT_APP_API_BASE_URL=https://your-production-domain.com
```

**Important**: Use HTTPS in production, never HTTP.

## Configuration Loading

The system loads configuration in this order:

1. **Environment variables** from `.env` file
2. **config.yaml** with environment variable substitution
3. **Runtime overrides** (if applicable)

Environment variables always take precedence over defaults.

## Validation

### Startup Checks

The system validates configuration on startup:
- Required environment variables present
- Config file syntax valid
- Building numbers and apartment counts valid
- API keys format correct (if provided)

### Testing Configuration

Test your configuration:
```bash
python -c "from src.config import load_config; load_config()"
```

## Configuration Best Practices

1. **Never commit secrets**: Keep `.env` out of version control
2. **Use .env.example**: Document all required variables
3. **Validate inputs**: Check configuration values on startup
4. **Separate concerns**: Secrets in .env, settings in config.yaml
5. **Document changes**: Update this file when adding new config options
6. **Test changes**: Verify configuration in dev before production

## Troubleshooting

### Missing Environment Variable

**Error**: `KeyError: 'SOME_VAR'`

**Solution**:
1. Check `.env.example` for required variables
2. Add missing variable to `.env`
3. Restart application

### Invalid YAML Syntax

**Error**: `yaml.scanner.ScannerError`

**Solution**:
1. Validate YAML syntax online or with `yamllint config.yaml`
2. Check indentation (use spaces, not tabs)
3. Ensure proper quoting of special characters

### Path Not Found

**Error**: `FileNotFoundError: 'path/to/file'`

**Solution**:
1. Verify paths are absolute or relative to project root
2. Create required directories
3. Check file permissions

## Adding New Configuration

To add new configuration options:

1. Add to `.env.example` with example value
2. Add to `config.yaml` with reference: `${NEW_VAR}`
3. Update this documentation
4. Update validation logic if needed
5. Add to security review if sensitive

## Support

For configuration issues:
- Check this documentation
- Review `.env.example` for examples
- Check logs for validation errors
- Consult docs/SECURITY.md for security-related config
