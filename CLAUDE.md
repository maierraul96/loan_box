# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Loan Orchestrator - A loan application processing system with configurable pipelines of business rules. Applications are created via API and processed through pipelines to receive a final status: APPROVED, REJECTED, or NEEDS_REVIEW.

**Tech Stack:**
- Backend: Python, FastAPI, SQLAlchemy, Pydantic, SQLite
- Frontend: (To be implemented)

## Commands

### Backend Development

**This project uses `uv` for fast dependency management.**

```bash
# Setup (first time)
cd backend
uv venv                              # Create virtual environment
uv pip install -r requirements.txt  # Install dependencies

# Run server
uv run uvicorn app.main:app --reload

# Run tests
uv run pytest                          # All tests
uv run pytest -v                       # Verbose
uv run pytest tests/test_scenarios.py  # Specific file
uv run pytest -k "test_scenario_1"     # Specific test

# Seed database with default data
uv run python seed_default_pipeline.py

# Alternative: activate venv first, then run without 'uv run'
source .venv/bin/activate  # Windows: .venv\Scripts\activate
uvicorn app.main:app --reload
pytest
```

## Architecture

### Core Concepts

1. **Loan Applications** - Contain applicant data (name, amount, income, debts, country, purpose)
2. **Pipelines** - Configurable sequences of business rule steps with terminal rules
3. **Steps** - Individual business rules (DTI check, amount policy, risk scoring)
4. **Runs** - Execution instances of a pipeline on an application with step logs
5. **Terminal Rules** - Ordered rules that evaluate step outcomes to determine final status

### Pipeline Execution Flow

```
Application → Pipeline → Execute Steps in Order → Evaluate Terminal Rules → Final Status
                            ↓
                        Log Each Step
```

### Step System (Extensibility Pattern)

All business rules extend `BaseStep` abstract class:
- Implement `execute(application, params) → StepResult`
- Register in `STEP_REGISTRY` (app/steps/registry.py)
- Add to `StepType` enum (app/models/enums.py)

**Current Steps:**
1. `dti_rule` - Debt-to-Income ratio check (app/steps/dti_rule.py:12)
2. `amount_policy` - Country-specific loan limits (app/steps/amount_policy.py:12)
3. `risk_scoring` - Combined risk calculation (app/steps/risk_scoring.py:12)

### Database Schema

**SQLite with 3 main tables:**

- `applications` - Loan applications with status
- `pipelines` - Pipeline configurations (steps_config and terminal_rules as JSON)
- `pipeline_runs` - Execution history with step logs (JSON)

**Design Choice:** Pipeline-embedded approach stores steps and rules as JSON columns rather than normalized tables. This simplifies full-config read/write operations needed by the UI.

### API Structure

```
/api/applications  - Create, list, get applications
/api/pipelines     - Create, list, get, update pipelines
/api/runs          - Execute pipelines, view run history
/api/steps/catalog - Get available step types with default params
```

### Key Files

- `app/main.py` - FastAPI app entry point, router registration
- `app/database.py` - SQLAlchemy setup, session management
- `app/services/pipeline_executor.py` - Core orchestration logic (app/services/pipeline_executor.py:13)
- `app/steps/registry.py` - Step registry and catalog (app/steps/registry.py:13)
- `app/api/*` - API endpoint routers

### Terminal Rules Evaluation

Rules are evaluated in order after all steps complete. Condition syntax supports:

- `"else"` - Catch-all (always true)
- `"step_name.failed"` / `"step_name.passed"` - Check step status
- `"step_name.risk <= 45"` - Value comparisons
- `"A OR B"` / `"A AND B"` - Logical operators

Implementation in `app/services/pipeline_executor.py:89`

### Test Scenarios

Tests validate against 3 required scenarios (tests/test_scenarios.py):

1. **Ana** (12000, 4000 income, 500 debts, ES) → APPROVED
2. **Luis** (28000, 2000 income, 1200 debts, OTHER) → REJECTED
3. **Mia** (20000, 3000 income, 900 debts, FR) → NEEDS_REVIEW

## Development Patterns

1. **Separation of Concerns**
   - `app/db_models` - SQLAlchemy ORM (database layer)
   - `app/models` - Pydantic schemas (API/validation layer)
   - `app/services` - Business logic
   - `app/api` - HTTP endpoints

2. **Adding New Steps**
   - Create class in `app/steps/new_step.py` extending `BaseStep`
   - Add to `STEP_REGISTRY` in registry.py
   - Add enum value to `StepType` in models/enums.py
   - Write tests in `tests/test_steps.py`

3. **API Development**
   - Use FastAPI's dependency injection for database sessions
   - Return Pydantic models for automatic validation
   - Handle JSON serialization for pipeline configs

## Important Notes

- **Money amounts are integers** (amount, monthly_income, declared_debts) to avoid floating-point precision issues
- Pipeline steps and terminal rules are stored as JSON strings in the database
- Step execution receives application data as dict, not ORM object
- Terminal rule evaluation happens in `PipelineExecutor._evaluate_terminal_rules()`
- Risk scoring step needs country_caps to calculate max_allowed for risk formula
- All tests use an in-memory SQLite database that resets between tests
