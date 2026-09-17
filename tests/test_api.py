from unittest.mock import patch

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.llm import LLMError
from app.main import app
from app.schemas import TriageResult

# Temporary in-memory database used only by this test file.
TEST_DATABASE_URL = "sqlite://"

test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=test_engine,
)

Base.metadata.create_all(bind=test_engine)


def override_get_db():
    db = TestingSessionLocal()

    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


def test_llm_failure_is_handled():
    complaint = {
        "customer_name": "Test Customer",
        "customer_email": "test@example.com",
        "order_id": "ORD-TEST-FAIL",
        "product": "Industrial Sensor X1",
        "complaint_text": "The sensor stopped working.",
    }

    with patch(
        "app.main.triage_complaint",
        side_effect=LLMError("Test LLM failure"),
    ):
        response = client.post(
            "/complaints",
            json=complaint,
        )

    assert response.status_code == 200

    data = response.json()

    assert data["is_complete"] is True
    assert data["status"] == "AI_FAILED"
    assert data["category"] is None
    assert data["priority"] is None
    assert data["summary"] is None
    assert data["assigned_team"] is None


def test_incomplete_complaint():
    complaint = {
        "customer_name": "Sophie Weber",
        "customer_email": "sophie@example.com",
        "order_id": None,
        "product": "Control Module C4",
        "complaint_text": "The module arrived cracked.",
    }

    response = client.post(
        "/complaints",
        json=complaint,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["is_complete"] is False
    assert data["missing_fields"] == ["order_id"]
    assert data["status"] == "INCOMPLETE"

    assert data["category"] is None
    assert data["priority"] is None
    assert data["summary"] is None
    assert data["assigned_team"] is None
    assert data["processed_at"] is None


def test_successful_triage():
    complaint = {
        "customer_name": "Laura Becker",
        "customer_email": "laura@example.com",
        "order_id": "ORD-TEST-001",
        "product": "Power Unit P2",
        "complaint_text": "The unit started producing a burning smell.",
    }

    mock_triage = TriageResult(
        category="PRODUCT_QUALITY",
        priority="CRITICAL",
        summary="Power unit produced a burning smell during operation.",
    )

    with patch(
        "app.main.triage_complaint",
        return_value=mock_triage,
    ):
        response = client.post(
            "/complaints",
            json=complaint,
        )

    assert response.status_code == 200

    data = response.json()

    assert data["is_complete"] is True
    assert data["missing_fields"] == []
    assert data["status"] == "TRIAGED"

    assert data["category"] == "PRODUCT_QUALITY"
    assert data["priority"] == "CRITICAL"
    assert data["summary"] == (
        "Power unit produced a burning smell during operation."
    )
    assert data["assigned_team"] == "Quality Team"
    assert data["processed_at"] is not None 


def test_metrics_endpoint():
    response = client.get("/metrics")

    assert response.status_code == 200

    data = response.json()

    assert "total_complaints" in data
    assert "triaged_complaints" in data
    assert "incomplete_complaints" in data
    assert "ai_failed_complaints" in data

    assert "completion_rate" in data
    assert "automation_rate" in data
    assert "ai_failure_rate" in data

    assert data["total_complaints"] >= 0
    assert 0 <= data["completion_rate"] <= 100
    assert 0 <= data["automation_rate"] <= 100
    assert 0 <= data["ai_failure_rate"] <= 100


def test_get_complaints():
    response = client.get("/complaints")

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, list)

    if data:
        complaint = data[0]

        assert "case_id" in complaint
        assert "status" in complaint
        assert "category" in complaint
        assert "priority" in complaint
        assert "assigned_team" in complaint
        assert "summary" in complaint
        assert "submitted_at" in complaint