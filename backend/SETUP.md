# Quick Setup Guide

## Prerequisites

- Python 3.14 (will be installed automatically by uv if needed)
- uv (fast Python package installer)

## Installation Steps

### 1. Install uv

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### 2. Setup Project

```bash
# Navigate to backend
cd backend

# Create virtual environment (uv will use Python 3.14 from .python-version)
uv venv

# Install dependencies
uv pip install -r requirements.txt
```

### 3. Start Development

```bash
# Start the server
uv run uvicorn app.main:app --reload
```

Visit http://localhost:8000/docs to see the API documentation.

### 4. Load Test Data (Optional)

```bash
# In a new terminal
cd backend
uv run python seed_default_pipeline.py
```

This creates:
- 1 default pipeline with all 3 steps
- 3 test applications (Ana, Luis, Mia)

### 5. Run Tests

```bash
uv run pytest -v
```

## Why uv?

- ⚡ **10-100x faster** than pip
- 🔒 **Better dependency resolution**
- 🛠️ **Simpler workflow** - no need to activate venv with `uv run`
- 📦 **Automatic Python version management**

## Common Commands

```bash
# Run server
uv run uvicorn app.main:app --reload

# Run tests
uv run pytest
uv run pytest -v
uv run pytest tests/test_scenarios.py

# Run seed script
uv run python seed_default_pipeline.py

# Add new dependency
uv pip install package-name
# Then update requirements.txt:
uv pip freeze > requirements.txt
```

## Troubleshooting

### uv not found
After installing uv, you may need to restart your terminal or add it to your PATH.

### Wrong Python version
uv will automatically install Python 3.14 if not available. To verify:
```bash
uv run python --version
```

If you've already installed Python 3.14:
```bash
uv python install 3.14
```

### Database locked
If you get "database is locked" errors, stop all running servers and try again.

### Tests failing
Make sure the server is NOT running when you run tests (tests use their own test database).
