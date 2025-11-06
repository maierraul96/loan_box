import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import Base, get_db

# Create test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_database():
    """Create tables before each test and drop after"""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


class TestApplicationsAPI:
    """Test Applications API endpoints"""

    def test_create_application(self):
        """Test creating a loan application"""
        response = client.post("/api/applications", json={
            "applicant_name": "John Doe",
            "amount": 15000,
            "monthly_income": 5000,
            "declared_debts": 1000,
            "country": "ES",
            "loan_purpose": "home renovation"
        })
        assert response.status_code == 201
        data = response.json()
        assert data["applicant_name"] == "John Doe"
        assert data["amount"] == 15000
        assert data["status"] == "PENDING"
        assert "id" in data
        # Verify amounts are integers
        assert isinstance(data["amount"], int)
        assert isinstance(data["monthly_income"], int)
        assert isinstance(data["declared_debts"], int)

    def test_list_applications(self):
        """Test listing applications"""
        # Create an application first
        client.post("/api/applications", json={
            "applicant_name": "Jane Smith",
            "amount": 10000,
            "monthly_income": 4000,
            "declared_debts": 500,
            "country": "FR",
            "loan_purpose": "education"
        })

        response = client.get("/api/applications")
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
        assert data[0]["applicant_name"] == "Jane Smith"

    def test_get_application(self):
        """Test getting a specific application"""
        # Create an application first
        create_response = client.post("/api/applications", json={
            "applicant_name": "Bob Johnson",
            "amount": 20000,
            "monthly_income": 6000,
            "declared_debts": 1500,
            "country": "DE",
            "loan_purpose": "car purchase"
        })
        app_id = create_response.json()["id"]

        response = client.get(f"/api/applications/{app_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["applicant_name"] == "Bob Johnson"
        assert data["id"] == app_id


class TestPipelinesAPI:
    """Test Pipelines API endpoints"""

    def test_create_pipeline(self):
        """Test creating a pipeline"""
        response = client.post("/api/pipelines", json={
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
        })
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Standard Pipeline"
        assert len(data["steps"]) == 3
        assert len(data["terminal_rules"]) == 3

    def test_get_pipeline(self):
        """Test getting a specific pipeline"""
        # Create a pipeline first
        create_response = client.post("/api/pipelines", json={
            "name": "Test Pipeline",
            "steps": [
                {"step_type": "dti_rule", "order": 1, "params": {}}
            ],
            "terminal_rules": [
                {"condition": "else", "outcome": "NEEDS_REVIEW", "order": 1}
            ]
        })
        pipeline_id = create_response.json()["id"]

        response = client.get(f"/api/pipelines/{pipeline_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Test Pipeline"
        assert data["id"] == pipeline_id


class TestCatalogAPI:
    """Test Catalog API endpoints"""

    def test_get_catalog(self):
        """Test getting step catalog"""
        response = client.get("/api/steps/catalog")
        assert response.status_code == 200
        data = response.json()
        assert "steps" in data
        assert len(data["steps"]) == 3  # dti_rule, amount_policy, risk_scoring

        # Verify each step has default params
        step_types = [s["step_type"] for s in data["steps"]]
        assert "dti_rule" in step_types
        assert "amount_policy" in step_types
        assert "risk_scoring" in step_types
