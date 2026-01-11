# Python Environment Setup

This document provides detailed instructions for setting up the development environment for the Residential Complex Tenant Management System.

**CRITICAL**: This project uses venv (no conda). All dependencies are managed via pip and pyproject.toml.

---

## Python Version

- **Required**: Python 3.10 or higher
- **Recommended**: Python 3.10, 3.11, or 3.12
- **Verify**: `python3 --version`

---

## Environment Setup

### 1. Create Virtual Environment

```bash
# Navigate to project root
cd /path/to/tenant-management

# Create venv
python3 -m venv .venv

# Verify venv created
ls -la .venv/
```

### 2. Activate Virtual Environment

**Linux/macOS**:
```bash
source .venv/bin/activate
```

**Windows**:
```cmd
.venv\Scripts\activate
```

**Verification**:
```bash
# Should show .venv Python path
which python
# OR
python -c "import sys; print(sys.executable)"
```

### 3. Upgrade Core Tools

```bash
python -m pip install --upgrade pip setuptools wheel
```

### 4. Install Dependencies

```bash
# Install production dependencies
pip install -r requirements.txt

# Install development dependencies
pip install -r requirements-dev.txt

# Install package in editable mode (CRITICAL)
pip install -e .
```

**Why editable mode?**
- Allows importing `src` module without installation
- Changes to code immediately available
- Required for pytest to discover `src` package

### 5. Verify Installation

```bash
# Check for dependency conflicts
python -m pip check

# Verify src module is importable
python -c "import src; print(src)"

# Should output: <module 'src' from '/path/to/src/__init__.py'>
```

---

## Development Tools

### Install Pre-Commit Hooks

```bash
pre-commit install
```

**What pre-commit does**:
- Runs Black, isort, ruff on staged files
- Checks YAML/JSON syntax
- Detects secrets in commits
- Prevents large file commits

**Manual run**:
```bash
pre-commit run --all-files
```

### IDE Setup

#### VS Code

Install recommended extensions:
- Python (ms-python.python)
- Pylance (ms-python.vscode-pylance)
- Black Formatter (ms-python.black-formatter)
- Ruff (charliermarsh.ruff)

**Settings** (`.vscode/settings.json`):
```json
{
  "python.defaultInterpreterPath": "${workspaceFolder}/.venv/bin/python",
  "python.formatting.provider": "black",
  "python.linting.enabled": true,
  "python.linting.pylintEnabled": true,
  "python.linting.ruffEnabled": true,
  "[python]": {
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
      "source.organizeImports": true
    }
  }
}
```

#### PyCharm

1. File → Settings → Project → Python Interpreter
2. Add Interpreter → Existing Environment
3. Select `.venv/bin/python`
4. Enable Black formatter in File Watchers
5. Enable pylint inspection

---

## Quality Checks

### Before Every Commit

```bash
# 1. Format code
black src/ tests/
isort --profile black src/ tests/

# 2. Lint code
ruff check src/ tests/
pylint src/ --score=y  # Must be 10.00/10

# 3. Run tests
pytest tests/ --cov=src

# 4. Security scan
bandit -r src/
```

### Expected Results

```bash
# Pylint
Your code has been rated at 10.00/10 (previous run: 10.00/10, +0.00)

# Black
All done! ✨ 🍰 ✨
N files left unchanged.

# isort
Skipped 0 files

# Ruff
All checks passed!

# Pytest
================================ test session starts =================================
collected N items

tests/unit/test_example.py::test_example PASSED                             [100%]

---------- coverage: platform linux, python 3.10.x-final-0 -----------
Name                      Stmts   Miss  Cover
---------------------------------------------
src/__init__.py               1      0   100%
src/module.py                10      0   100%
---------------------------------------------
TOTAL                        11      0   100%
```

---

## Running Tests

### All Tests

```bash
pytest tests/ -v
```

### Unit Tests Only

```bash
pytest tests/unit/ -v
```

### Integration Tests Only

```bash
pytest tests/integration/ -v
```

### With Coverage Report

```bash
# Terminal report
pytest tests/ --cov=src --cov-report=term

# HTML report
pytest tests/ --cov=src --cov-report=html
open htmlcov/index.html

# XML report (for CI)
pytest tests/ --cov=src --cov-report=xml
```

### Specific Test

```bash
pytest tests/unit/test_tenant_service.py::test_create_tenant -v
```

### Watch Mode (Auto-Run on Changes)

```bash
pytest-watch tests/ -- --cov=src
```

---

## Dependency Management

### Adding New Dependency

**Production dependency**:
```bash
# 1. Install
pip install package-name

# 2. Add to requirements.txt
echo "package-name>=1.0.0" >> requirements.txt

# 3. Update pyproject.toml
# Add to [project.dependencies]

# 4. Commit both files
git add requirements.txt pyproject.toml
git commit -m "feat(deps): add package-name"
```

**Development dependency**:
```bash
# 1. Install
pip install package-name

# 2. Add to requirements-dev.txt
echo "package-name>=1.0.0" >> requirements-dev.txt

# 3. Update pyproject.toml
# Add to [project.optional-dependencies.dev]

# 4. Commit
git add requirements-dev.txt pyproject.toml
git commit -m "chore(deps): add dev dependency package-name"
```

### Updating Dependencies

```bash
# Show outdated packages
pip list --outdated

# Update specific package
pip install --upgrade package-name

# Update requirements files
pip freeze > requirements.lock  # Optional full lock
```

---

## Troubleshooting

### ImportError: No module named 'src'

**Cause**: Package not installed in editable mode

**Solution**:
```bash
pip install -e .
```

### Pylint Import Errors

**Cause**: Pylint not using venv Python

**Solution**:
```bash
# Verify pylint is from venv
which pylint

# Should show: /path/to/project/.venv/bin/pylint
```

### Pre-Commit Hooks Not Running

**Cause**: Not installed

**Solution**:
```bash
pre-commit install
pre-commit run --all-files
```

### Python Version Mismatch

**Cause**: Wrong Python used to create venv

**Solution**:
```bash
# Remove old venv
rm -rf .venv

# Create with specific Python
python3.10 -m venv .venv

# Re-install dependencies
source .venv/bin/activate
pip install -r requirements.txt -r requirements-dev.txt
pip install -e .
```

### Permission Denied on .venv

**Cause**: venv ownership issue

**Solution**:
```bash
# Fix ownership
sudo chown -R $USER:$USER .venv

# Or recreate
rm -rf .venv
python3 -m venv .venv
```

---

## Environment Variables

### Required Variables

Create `.env` from `.env.example`:

```bash
cp .env.example .env
```

**Critical variables**:
- `EXCEL_DATABASE_PATH`: Path to Excel database file
- `AI_API_KEY`: Anthropic API key (for AI reports)
- `SECRET_KEY`: JWT secret key (min 32 chars)

### Loading Variables

Python automatically loads `.env` via `python-dotenv`:

```python
from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv("AI_API_KEY")
```

---

## CI/CD Environment

GitHub Actions automatically:
1. Sets up Python 3.10, 3.11, 3.12
2. Installs dependencies with caching
3. Runs linting (black, isort, ruff, pylint)
4. Runs tests with coverage
5. Runs security scan (bandit)
6. Uploads coverage to Codecov

**Configuration**: `.github/workflows/ci.yml`

---

## Quality Gates

### Before Pull Request

- [ ] `pip install -e .` succeeds
- [ ] `python -c "import src"` works (no ImportError)
- [ ] `pylint src/ --score=y` shows 10.00/10
- [ ] `black --check src/ tests/` passes
- [ ] `isort --check-only --profile black src/ tests/` passes
- [ ] `ruff check src/ tests/` passes
- [ ] `pytest tests/` shows 100% passing
- [ ] `.gitignore` includes all temp files
- [ ] No `.venv/`, `__pycache__/`, `*.pyc` committed

---

## Deactivating Environment

```bash
deactivate
```

**Note**: Always deactivate before switching projects or creating new venvs.

---

## Additional Resources

- [Python venv Documentation](https://docs.python.org/3/library/venv.html)
- [pip User Guide](https://pip.pypa.io/en/stable/user_guide/)
- [Black Documentation](https://black.readthedocs.io/)
- [Pylint Documentation](https://pylint.readthedocs.io/)
- [pytest Documentation](https://docs.pytest.org/)

---

**Maintained by**: Development Team
**Last Updated**: 2026-01-10
