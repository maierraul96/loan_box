# Loan Orchestrator

A minimal loan application processing system where applications are processed through configurable pipelines of business rules and end in one of three statuses: **APPROVED**, **REJECTED**, or **NEEDS_REVIEW**.

## Overview

This project implements a loan orchestration system that:
- Creates loan applications via API (no application form UI required)
- Processes applications through configurable pipelines with business rule steps
- Evaluates terminal rules to determine final loan status
- Provides a UI for pipeline configuration and execution

### Loan Application Structure

Each loan application contains:
- `applicant_name` - Name of the loan applicant
- `amount` - Requested loan amount (integer)
- `monthly_income` - Monthly income (integer)
- `declared_debts` - Monthly debt obligations (integer)
- `country` - Country code (ES, FR, DE, or OTHER)
- `loan_purpose` - Text description of loan purpose

## Tech Stack

- **Backend**: Python, FastAPI, SQLAlchemy, Pydantic, SQLite, OpenAI API
- **Frontend**: React, Vite, TailwindCSS, shadcn/ui
- **Package Management**: uv (fast Python package manager)

## Project Structure

```
loan_box/
├── backend/                    # FastAPI backend
│   ├── app/
│   │   ├── api/               # API endpoints (applications, pipelines, runs, steps)
│   │   ├── db_models/         # SQLAlchemy ORM models
│   │   ├── models/            # Pydantic schemas for validation
│   │   ├── services/          # Business logic (pipeline executor)
│   │   ├── steps/             # Business rule steps
│   │   │   ├── dti_rule.py
│   │   │   ├── amount_policy.py
│   │   │   ├── risk_scoring.py
│   │   │   ├── sentiment_check.py
│   │   │   └── registry.py
│   │   ├── database.py        # Database configuration
│   │   └── main.py            # FastAPI app entry point
│   ├── tests/                 # Test suite
│   │   ├── test_scenarios.py
│   │   └── test_steps.py
│   ├── seed_default_pipeline.py
│   ├── requirements.txt
│   ├── .env                   # Environment variables (create from .env.example)
│   ├── .env.example           # Environment variables template
│   └── loan_orchestrator.db   # SQLite database
│
└── frontend/                  # React (JavaScript) frontend
    ├── src/
    │   ├── components/
    │   │   ├── applications/  # Application-related components
    │   │   ├── layout/        # Layout components
    │   │   │   └── Layout.jsx
    │   │   ├── pipelines/     # Pipeline-related components
    │   │   ├── runs/          # Run-related components
    │   │   └── ui/            # shadcn/ui components (JSX)
    │   │       ├── badge.jsx
    │   │       ├── button.jsx
    │   │       ├── card.jsx
    │   │       ├── input.jsx
    │   │       ├── label.jsx
    │   │       ├── select.jsx
    │   │       ├── table.jsx
    │   │       └── textarea.jsx
    │   ├── pages/             # Page components
    │   │   ├── ApplicationsPage.jsx
    │   │   ├── PipelineBuilderPage.jsx
    │   │   ├── PipelinesListPage.jsx
    │   │   ├── RunHistoryPage.jsx
    │   │   └── RunPipelinePage.jsx
    │   ├── lib/               # Utilities
    │   │   ├── api.js         # API client functions
    │   │   └── utils.js       # Helper utilities
    │   ├── assets/            # Static assets
    │   ├── App.jsx            # Main app component
    │   ├── main.jsx           # Application entry point
    │   └── index.css          # Global styles
    ├── public/                # Static public assets
    ├── index.html             # HTML template
    ├── vite.config.js         # Vite configuration
    ├── tailwind.config.js     # TailwindCSS configuration
    ├── postcss.config.js      # PostCSS configuration
    ├── components.json        # shadcn/ui configuration
    └── package.json           # Dependencies and scripts
```

## Quick Start

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Create virtual environment and install dependencies:
```bash
uv venv
uv pip install -r requirements.txt
```

3. Configure environment variables:
```bash
# Copy the example .env file
cp .env.example .env

# Edit .env and add your OpenAI API key
# Replace 'your-openai-api-key-here' with your actual API key
```

The `.env` file should contain:
```env
DATABASE_URL=sqlite:///./loan_box.db
CORS_ORIGINS=["http://localhost:3000","http://localhost:5173"]
OPENAI_API_KEY=your-openai-api-key-here
```

**Note**: The `OPENAI_API_KEY` is required for the Sentiment Check step to work. Get your API key from [OpenAI Platform](https://platform.openai.com/api-keys).

4. Seed the database with default pipeline:
```bash
uv run python seed_default_pipeline.py
```

5. Run the backend server:
```bash
uv run uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`. API documentation is available at `http://localhost:8000/docs`.

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Run the development server:
```bash
npm run dev
```

The frontend will be available at `http://localhost:5173`.

## Business Rules (Step Catalog)

The system includes four configurable business rule steps:

### 1. Debt-to-Income Rule (`dti_rule`)

**Purpose**: Checks whether the applicant's debt burden is reasonable.

**Logic**: `dti = declared_debts / monthly_income`

**Parameters**:
- `max_dti` (default: 0.40)

**Outcome**: `pass = dti < max_dti`

**Business meaning**: If the applicant is spending more than 40% of their income on debt, they fail.

### 2. Amount Policy (`amount_policy`)

**Purpose**: Enforce country-specific loan limits.

**Parameters**:
- Country caps (defaults: ES=30k, FR=25k, DE=35k, OTHER=20k)

**Logic**: `pass = amount <= cap_for_country`

**Business meaning**: Applicants cannot borrow above the maximum allowed for their country.

### 3. Risk Scoring (`risk_scoring`)

**Purpose**: Combine previous checks into a simple risk metric.

**Logic**: `risk = (dti * 100) + (amount/max_allowed * 20)`

**Parameters**:
- `approve_threshold` (default: 45)

**Outcome**: `pass = risk <= approve_threshold`

**Business meaning**: Lower scores mean safer applicants. If risk ≤ threshold, approve.

### 4. Sentiment Check (`sentiment_check`) - AI Agent Step

**Purpose**: Analyze loan purpose text to detect risky or speculative purposes.

**Logic**: Uses OpenAI GPT model to analyze the `loan_purpose` field and assign a risk score based on detected patterns.

**Parameters**:
- `risk_threshold` (default: 45)
- `model` (default: "gpt-4o-mini")

**Outcome**: `pass = risk_score <= risk_threshold`

**Business meaning**: Detects risky keywords (e.g., "gambling", "crypto") and prevents loans for high-risk purposes.

**Risk Categories Detected**:
- Gambling (casinos, betting, poker)
- Cryptocurrency/speculative trading
- Illegal activities
- Unclear or vague purposes

## Terminal Rules

Configurable, ordered rules that map step outcomes to final status. The default pipeline uses:

1. If Sentiment Check fails → **REJECTED**
2. If DTI Rule or Amount Policy fails → **REJECTED**
3. If Risk Score ≤ threshold → **APPROVED**
4. Else → **NEEDS_REVIEW**

Terminal rules are evaluated in order, and the first matching rule determines the final status.

## API Examples

### Create an Application

```bash
curl -X POST "http://localhost:8000/api/applications" \
  -H "Content-Type: application/json" \
  -d '{
    "applicant_name": "Ana",
    "amount": 12000,
    "monthly_income": 4000,
    "declared_debts": 500,
    "country": "ES",
    "loan_purpose": "home renovation"
  }'
```

### List Pipelines

```bash
curl "http://localhost:8000/api/pipelines"
```

### Run a Pipeline

```bash
curl -X POST "http://localhost:8000/api/runs" \
  -H "Content-Type: application/json" \
  -d '{
    "application_id": 1,
    "pipeline_id": 1
  }'
```

### Get Run Details

```bash
curl "http://localhost:8000/api/runs/1"
```

### Get Step Catalog

```bash
curl "http://localhost:8000/api/steps/catalog"
```

## Running Tests

The project includes comprehensive tests for all business rules and scenarios.

```bash
cd backend

# Run all tests
uv run pytest

# Run with verbose output
uv run pytest -v

# Run specific test file
uv run pytest tests/test_scenarios.py

# Run specific test
uv run pytest -k "test_scenario_1"
```

## Review Scenarios

The system is tested against these required scenarios:

1. **Ana**: 12000 loan, 4000 income, 500 debts, ES, "home renovation" → **APPROVED**
2. **Luis**: 28000 loan, 2000 income, 1200 debts, OTHER, "business" → **REJECTED**
3. **Mia**: 20000 loan, 3000 income, 900 debts, FR, "education" → **NEEDS_REVIEW**
4. **Eva** (Bonus): 15000 loan, 5000 income, 200 debts, ES, "gambling" → **REJECTED**

## Architecture Highlights

### Extensibility Pattern

The system uses a registry-based pattern for business rules:
- All steps extend `BaseStep` abstract class
- Steps are registered in `STEP_REGISTRY` (app/steps/registry.py)
- New steps can be added without modifying core logic

### Database Design

SQLite database with pipeline-embedded approach:
- Pipeline configurations stored as JSON columns
- Simplifies full-config read/write operations
- Easy to version and backup entire pipeline configurations

### Frontend Features

- **Pipeline Builder**: Add/remove/reorder steps, edit parameters, configure terminal rules
- **Run Panel**: Select application and pipeline, execute, view detailed logs and final status
- **Step Catalog**: Browse available business rules with descriptions and default parameters

## AI Usage

This project leveraged AI tools extensively during development:

1. **Architecture Design**: Used Claude Code to design the extensible step system and registry pattern
2. **Code Generation**: Generated boilerplate for API endpoints, models, and database schemas
3. **Frontend Development**: Built React components and UI with shadcn/ui integration
4. **Testing**: Generated comprehensive test scenarios and edge cases
5. **Agent Integration**: Implemented OpenAI API integration for the Sentiment Check step
6. **Documentation**: AI-assisted README generation and code documentation

AI tools accelerated development by approximately 3-4x, particularly in:
- Rapid prototyping of the pipeline execution engine
- Generating type-safe Pydantic models
- Setting up React components with proper TypeScript typing
- Writing test fixtures and scenarios

## Development Notes

- Money amounts are stored as integers to avoid floating-point precision issues
- Pipeline steps and terminal rules are stored as JSON strings in the database
- Step execution receives application data as a dictionary
- The default pipeline is seeded via `seed_default_pipeline.py`
- Frontend uses React Query for efficient data fetching and caching

## License

This project was created as a take-home exercise for demonstrating full-stack development capabilities.
