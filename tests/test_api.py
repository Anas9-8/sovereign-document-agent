"""Tests for FastAPI endpoints (mocked backends)."""

from unittest.mock import patch

from fastapi.testclient import TestClient

from api.main import app

client = TestClient(app)


@patch("api.routes.registry")
def test_health_endpoint_returns_ok(mock_registry):
    """Health check should return status ok."""
    mock_registry.count.return_value = 0
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


@patch("api.routes.run_query")
def test_query_endpoint_validates_empty_question(mock_query):
    """An empty question should return a valid response."""
    mock_query.return_value = {
        "answer": "No answer found.",
        "sources": [],
        "latency_ms": 10,
        "chunks_used": 0,
    }
    response = client.post("/query", json={"question": "", "top_k": 3})
    assert response.status_code == 200


@patch("api.routes.registry")
def test_documents_endpoint_returns_list(mock_registry):
    """Documents endpoint should return a list and total count."""
    mock_registry.get_all.return_value = [
        {"filename": "test.pdf", "chunk_count": 5, "status": "ok"}
    ]

    response = client.get("/documents")
    assert response.status_code == 200
    data = response.json()
    assert "documents" in data
    assert "total" in data
    assert isinstance(data["documents"], list)
