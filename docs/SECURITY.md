# Security Guidelines

## Overview

This document outlines security best practices and guidelines for the Residential Complex Tenant Management System.

## Secret Management

### Environment Variables

**CRITICAL**: Never commit secrets to version control.

All sensitive information must be stored in environment variables:
- API keys
- Secret keys
- Database credentials
- JWT tokens
- Third-party service credentials

### Using .env Files

1. Copy `.env.example` to `.env`
2. Update `.env` with actual values
3. **NEVER** commit `.env` to git (it's in .gitignore)
4. Share secrets securely via password managers or secret management services

### Configuration Separation

- **config.yaml**: Non-sensitive configuration (references env vars with `${VAR_NAME}`)
- **.env**: Sensitive secrets and credentials
- **.env.example**: Template with placeholder values for documentation

## Authentication & Authorization

### JWT Tokens

- Tokens expire after 24 hours (configurable via `JWT_EXPIRATION_HOURS`)
- Store secret key in `SECRET_KEY` environment variable
- Minimum secret key length: 32 characters
- Use cryptographically secure random keys

### Password Requirements

- Minimum length: 8 characters
- Should include uppercase, lowercase, numbers, and special characters
- Store passwords using bcrypt or similar hashing algorithm
- Never log passwords or tokens

### Session Management

- Sessions timeout after 30 minutes of inactivity
- Maximum login attempts: 5
- Account lockout duration: 15 minutes after failed attempts

## API Security

### CORS Configuration

- Configure allowed origins in `config.yaml`
- Default: localhost only for development
- Update for production deployment

### Rate Limiting

- WhatsApp API: 10 requests per minute
- Implement rate limiting on all public endpoints
- Monitor for unusual activity patterns

## Data Protection

### Excel Database Security

- Store database file outside web root
- Limit file permissions (read/write for application only)
- Enable automatic backups (every 24 hours)
- Encrypt backups if storing offsite

### Personal Data

This system handles personal information:
- Tenant names and contact information
- Ownership records
- Move-in/move-out dates
- Parking access credentials

**Compliance**: Ensure compliance with local data protection regulations.

## Vulnerability Reporting

If you discover a security vulnerability:

1. **Do NOT** open a public issue
2. Email: security@example.com (update with actual contact)
3. Include:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if available)

## Security Scanning

### Pre-Commit Checks

Run security scans before every commit:
```bash
bandit -r src/
```

### CI/CD Pipeline

Automated security scans run on every PR:
- Bandit (Python security linter)
- Dependency vulnerability scanning
- Secret detection

## Secure Development Practices

### Code Review

- All code changes require review
- Security-sensitive changes require additional security review
- Check for hardcoded secrets in PR diffs

### Dependency Management

- Keep dependencies up to date
- Review security advisories for dependencies
- Use `pip-audit` to check for known vulnerabilities

### Logging

- **DO**: Log authentication events, errors, API calls
- **DON'T**: Log passwords, tokens, API keys, PII

## Production Deployment

### Checklist

- [ ] All secrets in environment variables
- [ ] `.env` file never committed
- [ ] CORS configured for production domain
- [ ] HTTPS enabled (never HTTP in production)
- [ ] Secret key is cryptographically random and unique
- [ ] Database backups automated and tested
- [ ] Security headers configured (CSP, X-Frame-Options, etc.)
- [ ] Rate limiting enabled
- [ ] Monitoring and alerting configured

## Incident Response

In case of a security incident:

1. **Isolate**: Disconnect affected systems if necessary
2. **Assess**: Determine scope and impact
3. **Contain**: Prevent further damage
4. **Eradicate**: Remove threat and vulnerabilities
5. **Recover**: Restore normal operations
6. **Learn**: Document incident and improve processes

## References

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [OWASP API Security Top 10](https://owasp.org/www-project-api-security/)
- [Python Security Best Practices](https://python.readthedocs.io/en/stable/library/security.html)
