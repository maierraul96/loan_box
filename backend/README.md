# Loan Orchestrator Backend

A FastAPI-based loan application orchestrator that processes applications through configurable pipelines of business rules.

## Features

- **RESTful API** for managing loan applications and pipelines
- **Configurable pipelines** with reorderable steps and parameters
- **Extensible step system** for adding new business rules
- **Terminal rules** for determining final application status
- **Full test coverage** including unit and integration tests
- **Integer money amounts** to avoid floating-point precision issues

## Tech Stack

- **FastAPI** - Modern Python web framework
- **Pydantic** - Data validation and settings
- **SQLAlchemy** - ORM for database operations
- **SQLite** - Lightweight database
- **Pytest** - Testing framework

## Project Structure

```
backend/
├── app/
│   ├── api/              # API endpoints
│   ├── db_models/        # SQLAlchemy ORM models
│   ├── models/           # Pydantic schemas
│   ├── services/         # Business logic
│   ├── steps/            # Pipeline step implementations
│   ├── config.py         # Configuration
│   ├── database.py       # Database setup
│   └── main.py           # FastAPI app
├── tests/                # Test files
├── requirements.txt      # Dependencies
└── README.md            # This file
```

## Setup

### 1. Install uv (if not already installed)

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Or with pip/pipx
pip install uv
```

### 2. Create Virtual Environment and Install Dependencies

```bash
cd backend

# Create virtual environment
uv venv

# Activate virtual environment
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
uv pip install -r requirements.txt
```

**Alternative (without activating venv):**
```bash
cd backend
uv venv
uv pip install -r requirements.txt
# Run commands with 'uv run' prefix (see below)
```

### 3. Environment Configuration

Copy `.env.example` to `.env` and configure as needed:

```bash
cp .env.example .env
```

Default configuration:
- Database: SQLite (`loan_box.db`)
- CORS: Localhost ports 3000 and 5173

### 4. Run the Server

```bash
# If venv is activated
uvicorn app.main:app --reload

# Or use uv run (auto-activates venv)
uv run uvicorn app.main:app --reload
```

Server will start at: http://localhost:8000

API Documentation: http://localhost:8000/docs

## API Endpoints

### Applications

```bash
# Create a loan application
POST /api/applications
{
  "applicant_name": "John Doe",
  "amount": 15000,           # Integer (not float)
  "monthly_income": 5000,    # Integer (not float)
  "declared_debts": 1000,    # Integer (not float)
  "country": "ES",
  "loan_purpose": "home renovation"
}

# List all applications
GET /api/applications

# Get specific application
GET /api/applications/{id}
```

### Pipelines

```bash
# Create a pipeline
POST /api/pipelines
{
  "name": "Standard Pipeline",
  "description": "Default loan processing",
  "steps": [
    {"step_type": "dti_rule", "order": 1, "params": {"max_dti": 0.40}},
    {"step_type": "amount_policy", "order": 2, "params": {}},
    {"step_type": "risk_scoring", "order": 3, "params": {"approve_threshold": 45}}
  ],
  "terminal_rules": [
    {"condition": "dti_rule.failed OR amount_policy.failed", "outcome": "REJECTED", "order": 1},
    {"condition": "risk_scoring.risk <= 45", "outcome": "APPROVED", "order": 2},
    {"condition": "else", "outcome": "NEEDS_REVIEW", "order": 3}
  ]
}

# List all pipelines
GET /api/pipelines

# Get specific pipeline
GET /api/pipelines/{id}

# Update pipeline
PUT /api/pipelines/{id}
```

### Runs

```bash
# Execute a pipeline on an application
POST /api/runs
{
  "application_id": 1,
  "pipeline_id": 1
}

# List all runs (history)
GET /api/runs

# Get specific run with logs
GET /api/runs/{id}
```

### Catalog

```bash
# Get available step types and default parameters
GET /api/steps/catalog
```

## Example cURL Commands

### Create Application

```bash
curl -X POST http://localhost:8000/api/applications \
  -H "Content-Type: application/json" \
  -d '{
    "applicant_name": "Ana",
    "amount": 12000,
    "monthly_income": 4000,
    "declared_debts": 500,
    "country": "ES",
    "loan_purpose": "home improvement"
  }'
```

### Create Pipeline

```bash
curl -X POST http://localhost:8000/api/pipelines \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Standard Pipeline",
    "description": "Default loan processing pipeline",
    "steps": [
      {"step_type": "dti_rule", "order": 1, "params": {"max_dti": 0.40}},
      {"step_type": "amount_policy", "order": 2, "params": {}},
      {"step_type": "risk_scoring", "order": 3, "params": {"approve_threshold": 45}}
    ],
    "terminal_rules": [
      {"condition": "dti_rule.failed OR amount_policy.failed", "outcome": "REJECTED", "order": 1},
      {"condition": "risk_scoring.risk <= 45", "outcome": "APPROVED", "order": 2},
      {"condition": "else", "outcome": "NEEDS_REVIEW", "order": 3}
    ]
  }'
```

### Execute Pipeline

```bash
curl -X POST http://localhost:8000/api/runs \
  -H "Content-Type: application/json" \
  -d '{
    "application_id": 1,
    "pipeline_id": 1
  }'
```

## Quick Start with Seed Data

```bash
# 1. Start the server (in one terminal)
uv run uvicorn app.main:app --reload

# 2. Seed test data (in another terminal)
uv run python seed_default_pipeline.py

# 3. View API docs
# Open http://localhost:8000/docs in your browser
```

## Running Tests

```bash
# Run all tests
uv run pytest

# Run with verbose output
uv run pytest -v

# Run specific test file
uv run pytest tests/test_scenarios.py

# Run specific test
uv run pytest tests/test_scenarios.py::TestReviewScenarios::test_scenario_1_ana_approved

# Or if venv is activated
pytest
pytest -v
```

## Business Rules (Steps)

### 1. DTI Rule (`dti_rule`)

Checks debt-to-income ratio.

**Logic:** `dti = declared_debts / monthly_income`

**Parameters:**
- `max_dti` (default: 0.40)

**Pass condition:** `dti < max_dti`

### 2. Amount Policy (`amount_policy`)

Enforces country-specific loan limits.

**Parameters:**
- `ES` (default: 30000)
- `FR` (default: 25000)
- `DE` (default: 35000)
- `OTHER` (default: 20000)

**Pass condition:** `amount <= country_limit`

### 3. Risk Scoring (`risk_scoring`)

Calculates risk score combining DTI and amount.

**Logic:** `risk = (dti * 100) + (amount / max_allowed * 20)`

**Parameters:**
- `approve_threshold` (default: 45)
- `country_caps` (country limits)

**Pass condition:** `risk <= approve_threshold`

## Terminal Rules

Terminal rules are evaluated in order after all steps complete. Common patterns:

```python
# Reject if critical steps fail
{"condition": "dti_rule.failed OR amount_policy.failed", "outcome": "REJECTED", "order": 1}

# Approve if risk is acceptable
{"condition": "risk_scoring.risk <= 45", "outcome": "APPROVED", "order": 2}

# Default to manual review
{"condition": "else", "outcome": "NEEDS_REVIEW", "order": 3}
```

## Test Scenarios

The system is validated against these scenarios:

### Scenario 1: Ana - APPROVED
- Amount: 12000, Income: 4000, Debts: 500, Country: ES
- DTI: 0.125 (PASS), Amount: PASS, Risk: 20.5 (PASS)
- **Result: APPROVED**

### Scenario 2: Luis - REJECTED
- Amount: 28000, Income: 2000, Debts: 1200, Country: OTHER
- DTI: 0.6 (FAIL), Amount: FAIL, Risk: 88 (FAIL)
- **Result: REJECTED**

### Scenario 3: Mia - NEEDS_REVIEW
- Amount: 20000, Income: 3000, Debts: 900, Country: FR
- DTI: 0.3 (PASS), Amount: PASS, Risk: 46 (FAIL)
- **Result: NEEDS_REVIEW**

## Adding New Steps

To add a new business rule:

1. Create a new file in `app/steps/` (e.g., `credit_check.py`)
2. Extend `BaseStep` class
3. Implement `execute()` method
4. Add to `STEP_REGISTRY` in `app/steps/registry.py`
5. Add step type to `StepType` enum in `app/models/enums.py`

Example:

```python
from app.steps.base import BaseStep, StepResult

class CreditCheck(BaseStep):
    step_type = "credit_check"

    def execute(self, application, params):
        min_score = params.get("min_score", 650)
        # Your logic here
        return StepResult(
            passed=True,
            computed_values={"score": 700},
            message="Credit check passed"
        )

    @classmethod
    def get_default_params(cls):
        return {"min_score": 650}
```

## Development

### Code Structure

- **API Layer** (`app/api/`): FastAPI routers and endpoints
- **Models** (`app/models/`): Pydantic schemas for validation
- **DB Models** (`app/db_models/`): SQLAlchemy ORM models
- **Services** (`app/services/`): Core business logic
- **Steps** (`app/steps/`): Business rule implementations

### Key Design Patterns

- **Dependency Injection**: Database sessions via FastAPI Depends
- **Strategy Pattern**: Pluggable steps via registry
- **Repository Pattern**: Database operations in services
- **Model-Schema Separation**: ORM models vs. API schemas

## License

MIT
