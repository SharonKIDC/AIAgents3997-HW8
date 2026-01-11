# Contributing to Residential Complex Tenant Management System

Thank you for your interest in contributing to this project! This document provides guidelines and standards for contributing.

---

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Coding Standards](#coding-standards)
- [Git Workflow](#git-workflow)
- [Pull Request Process](#pull-request-process)
- [Testing Requirements](#testing-requirements)
- [Documentation](#documentation)

---

## Code of Conduct

### Our Pledge

We are committed to providing a welcoming and inclusive environment for all contributors.

### Our Standards

**Positive behaviors**:
- Using welcoming and inclusive language
- Being respectful of differing viewpoints
- Gracefully accepting constructive criticism
- Focusing on what is best for the community
- Showing empathy towards other community members

**Unacceptable behaviors**:
- Trolling, insulting/derogatory comments, personal attacks
- Public or private harassment
- Publishing others' private information without permission
- Other conduct which could reasonably be considered inappropriate

### Enforcement

Violations may result in temporary or permanent ban from the project.

---

## Getting Started

### Prerequisites

Before contributing, ensure you have:

1. **Git** installed and configured
2. **Python 3.10+** with venv support
3. **Node.js 16+** and npm
4. Familiarity with React and Python
5. Understanding of project architecture (see docs/Architecture.md)

### First Contribution

Good first issues are tagged with `good-first-issue` label in GitHub Issues.

---

## Development Setup

### 1. Fork and Clone

```bash
# Fork repository on GitHub, then:
git clone https://github.com/YOUR-USERNAME/tenant-management.git
cd tenant-management

# Add upstream remote
git remote add upstream https://github.com/original/tenant-management.git
```

### 2. Create Virtual Environment

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip setuptools wheel
pip install -r requirements.txt -r requirements-dev.txt
pip install -e .
```

### 3. Install Pre-Commit Hooks

```bash
pip install pre-commit
pre-commit install
```

### 4. Verify Setup

```bash
# Run tests
pytest tests/

# Check linting
pylint src/ --score=y
ruff check src/ tests/

# Check formatting
black --check src/ tests/
isort --check-only --profile black src/ tests/
```

---

## Coding Standards

### Python Code Style

We follow **PEP 8** with these tools:

1. **Black**: Code formatter (line length: 100)
2. **isort**: Import sorting (compatible with Black)
3. **Ruff**: Fast linter replacing Flake8
4. **Pylint**: Code analysis (target: 10.00/10)

**Run before committing**:
```bash
black src/ tests/
isort --profile black src/ tests/
ruff check src/ tests/ --fix
pylint src/ --score=y
```

### File Size Limit

**Maximum 150 lines per file**. If a file grows beyond this:
1. Extract classes/functions into separate modules
2. Use composition over inheritance
3. Create helper modules for shared utilities

### Naming Conventions

- **Files**: `lowercase_with_underscores.py`
- **Classes**: `PascalCase`
- **Functions**: `snake_case`
- **Constants**: `UPPER_CASE_WITH_UNDERSCORES`
- **Private methods**: `_leading_underscore`

### Docstrings

Use Google-style docstrings:

```python
def create_tenant(building: int, apartment: int, name: str) -> Tenant:
    """Create a new tenant record.

    Args:
        building: Building number (11, 13, 15, 17).
        apartment: Apartment number within building.
        name: Tenant full name.

    Returns:
        Newly created Tenant instance.

    Raises:
        ValueError: If building or apartment is invalid.
        DuplicateError: If apartment already occupied.
    """
    # Implementation
```

### Type Hints

Use type hints for all function signatures:

```python
from typing import List, Optional

def get_tenants(building: int, current_only: bool = True) -> List[Tenant]:
    """Get tenants for a building."""
    # Implementation
```

### Error Handling

- Use specific exceptions (not bare `except:`)
- Create custom exceptions for domain errors
- Log errors with context
- Provide user-friendly error messages

```python
class ApartmentOccupiedError(Exception):
    """Raised when attempting to register tenant in occupied apartment."""
    pass

try:
    create_tenant(building=11, apartment=101, name="Jane Doe")
except ApartmentOccupiedError as e:
    logger.error(f"Failed to create tenant: {e}")
    return {"error": "Apartment is currently occupied"}
```

---

## Git Workflow

### Branch Naming

- **Feature**: `feature/short-description`
- **Bugfix**: `bugfix/issue-number-short-description`
- **Hotfix**: `hotfix/critical-issue`
- **Documentation**: `docs/what-was-updated`

### Commit Messages

Follow **Conventional Commits** format:

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types**:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code formatting (black, isort)
- `refactor`: Code restructuring without behavior change
- `test`: Test additions or modifications
- `chore`: Build process, dependencies, tooling

**Example**:
```
feat(api): add endpoint for tenant move-out

Implement POST /api/tenants/{id}/moveout endpoint to handle
tenant move-out process and preserve historical data.

- Add TenantService.move_out method
- Update tenant record with move_out_date
- Create history record
- Add integration tests

Closes #42
```

### Commit Frequency

- Commit logical units of work
- Aim for 5-10 commits per feature (not 1 massive commit)
- Each commit should be self-contained and pass tests

---

## Pull Request Process

### Before Submitting PR

1. **Update from upstream**:
   ```bash
   git fetch upstream
   git rebase upstream/main
   ```

2. **Run full test suite**:
   ```bash
   pytest tests/ --cov=src
   ```

3. **Check code quality**:
   ```bash
   pylint src/ --score=y     # Must be 10.00/10
   black --check src/ tests/
   isort --check-only --profile black src/ tests/
   ruff check src/ tests/
   ```

4. **Update documentation** if needed

### PR Template

Use this template for PR description:

```markdown
## Summary
Brief description of changes.

## Type of Change
- [ ] Bug fix (non-breaking change fixing an issue)
- [ ] New feature (non-breaking change adding functionality)
- [ ] Breaking change (fix or feature causing existing functionality to break)
- [ ] Documentation update

## Changes Made
- Bullet list of specific changes
- Include files modified
- Mention new dependencies

## Testing
- [ ] All existing tests pass
- [ ] Added new tests for new functionality
- [ ] Pylint score: 10.00/10
- [ ] Test coverage: >80%

## Screenshots (if UI changes)
[Add screenshots here]

## Checklist
- [ ] Code follows project style guidelines
- [ ] Self-reviewed my own code
- [ ] Commented code, particularly complex areas
- [ ] Updated documentation
- [ ] No new warnings
- [ ] Added tests that prove fix/feature works
- [ ] New and existing tests pass locally

## Related Issues
Closes #[issue number]
```

### Review Process

1. **Automated Checks**: CI runs tests, linting, security scans
2. **Code Review**: At least one maintainer review required
3. **Approval**: Changes requested or approved
4. **Merge**: Squash and merge to main

---

## Testing Requirements

### Test Coverage

- **Minimum**: 80% code coverage
- **Target**: 90% for critical modules
- **Run coverage report**:
  ```bash
  pytest tests/ --cov=src --cov-report=html
  open htmlcov/index.html
  ```

### Test Types

1. **Unit Tests**: Test individual functions/classes
   ```python
   def test_create_tenant_valid_data(sample_tenant_data):
       """Test tenant creation with valid data."""
       service = TenantService()
       tenant = service.create(sample_tenant_data)
       assert tenant.building == 11
       assert tenant.apartment == 101
   ```

2. **Integration Tests**: Test component interactions
   ```python
   def test_api_create_tenant_e2e(client):
       """Test full tenant creation flow through API."""
       response = client.post("/api/tenants", json=tenant_data)
       assert response.status_code == 201
       assert "tenant_id" in response.json()
   ```

3. **Fixtures**: Use pytest fixtures for test data
   ```python
   @pytest.fixture
   def sample_tenant_data():
       return {
           "building": 11,
           "apartment": 101,
           "owner_name": "John Doe",
           "tenant_name": "Jane Smith",
           "move_in_date": "2024-01-15",
       }
   ```

### Running Tests

```bash
# All tests
pytest tests/ -v

# Specific test file
pytest tests/unit/test_tenant_service.py -v

# Specific test
pytest tests/unit/test_tenant_service.py::test_create_tenant -v

# With coverage
pytest tests/ --cov=src --cov-report=term

# Parallel execution (if many tests)
pytest tests/ -n auto
```

---

## Documentation

### Required Documentation

When adding features, update:

1. **Docstrings**: All functions, classes, modules
2. **README.md**: If user-facing changes
3. **docs/Architecture.md**: If architectural changes
4. **docs/CONFIG.md**: If configuration options added
5. **ADRs**: Create `docs/ADRs/ADR-NNN-title.md` for significant decisions

### ADR Format

```markdown
# ADR-NNN: Title

**Status**: Proposed | Accepted | Deprecated
**Date**: YYYY-MM-DD
**Deciders**: Names

## Context
What is the issue we're facing?

## Decision
What did we decide?

## Rationale
Why did we make this decision?

## Alternatives Considered
What other options were there?

## Consequences
What are the implications?
```

---

## Questions or Issues?

- **Technical Questions**: Open a GitHub Discussion
- **Bug Reports**: Create an issue with bug template
- **Feature Requests**: Create an issue with feature template
- **Security Issues**: Email security@example.com (DO NOT open public issue)

---

## Recognition

Contributors will be recognized in:
- `CONTRIBUTORS.md` file
- Project documentation
- Release notes

Thank you for contributing!
