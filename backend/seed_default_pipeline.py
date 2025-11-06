"""
Seed script to create a default pipeline in the database
Run this after starting the server to create a working pipeline
"""
import requests

BASE_URL = "http://localhost:8000"

def create_default_pipeline():
    """Create the default loan processing pipeline"""
    pipeline_data = {
        "name": "Standard Loan Pipeline",
        "description": "Default pipeline with DTI, Amount Policy, and Risk Scoring",
        "steps": [
            {
                "step_type": "dti_rule",
                "order": 1,
                "params": {"max_dti": 0.40}
            },
            {
                "step_type": "amount_policy",
                "order": 2,
                "params": {
                    "ES": 30000,
                    "FR": 25000,
                    "DE": 35000,
                    "OTHER": 20000
                }
            },
            {
                "step_type": "risk_scoring",
                "order": 3,
                "params": {
                    "approve_threshold": 45,
                    "country_caps": {
                        "ES": 30000,
                        "FR": 25000,
                        "DE": 35000,
                        "OTHER": 20000
                    }
                }
            }
        ],
        "terminal_rules": [
            {
                "condition": "dti_rule.failed OR amount_policy.failed",
                "outcome": "REJECTED",
                "order": 1
            },
            {
                "condition": "risk_scoring.risk <= 45",
                "outcome": "APPROVED",
                "order": 2
            },
            {
                "condition": "else",
                "outcome": "NEEDS_REVIEW",
                "order": 3
            }
        ]
    }

    response = requests.post(f"{BASE_URL}/api/pipelines", json=pipeline_data)

    if response.status_code == 201:
        pipeline = response.json()
        print(f"✓ Default pipeline created successfully!")
        print(f"  Pipeline ID: {pipeline['id']}")
        print(f"  Pipeline Name: {pipeline['name']}")
        return pipeline
    else:
        print(f"✗ Failed to create pipeline: {response.status_code}")
        print(f"  Error: {response.text}")
        return None


def create_test_applications():
    """Create the test applications from the spec"""
    applications = [
        {
            "applicant_name": "Ana",
            "amount": 12000,
            "monthly_income": 4000,
            "declared_debts": 500,
            "country": "ES",
            "loan_purpose": "home improvement"
        },
        {
            "applicant_name": "Luis",
            "amount": 28000,
            "monthly_income": 2000,
            "declared_debts": 1200,
            "country": "OTHER",
            "loan_purpose": "business"
        },
        {
            "applicant_name": "Mia",
            "amount": 20000,
            "monthly_income": 3000,
            "declared_debts": 900,
            "country": "FR",
            "loan_purpose": "education"
        },
        {
            "applicant_name": "Eva",
            "amount": 15000,
            "monthly_income": 5000,
            "declared_debts": 200,
            "country": "ES",
            "loan_purpose": "gambling"
        }
    ]

    created_apps = []
    for app_data in applications:
        response = requests.post(f"{BASE_URL}/api/applications", json=app_data)
        if response.status_code == 201:
            app = response.json()
            created_apps.append(app)
            print(f"✓ Created application for {app['applicant_name']} (ID: {app['id']})")
        else:
            print(f"✗ Failed to create application for {app_data['applicant_name']}")

    return created_apps


if __name__ == "__main__":
    print("Creating default pipeline and test applications...\n")

    # Create pipeline
    pipeline = create_default_pipeline()
    print()

    # Create test applications
    applications = create_test_applications()
    print()

    if pipeline and applications:
        print("=" * 60)
        print("Setup complete! You can now:")
        print(f"1. View API docs: {BASE_URL}/docs")
        print(f"2. Execute pipeline on applications:")
        for app in applications:
            print(f"   curl -X POST {BASE_URL}/api/runs -H 'Content-Type: application/json' -d '{{\"application_id\": {app['id']}, \"pipeline_id\": {pipeline['id']}}}'")
        print("=" * 60)
