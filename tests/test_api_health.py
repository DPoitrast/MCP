"""Test health check endpoints."""

import pytest
from fastapi.testclient import TestClient


def test_health_endpoint(test_client: TestClient):
    """Test basic health endpoint."""
    response = test_client.get("/api/v1/health")
    assert response.status_code == 200
    
    data = response.json()
    assert "status" in data
    assert "timestamp" in data
    assert "version" in data
    assert data["status"] == "healthy"


def test_health_detailed_endpoint(test_client: TestClient):
    """Test detailed health endpoint."""
    response = test_client.get("/api/v1/health/detailed")
    assert response.status_code == 200
    
    data = response.json()
    assert "status" in data
    assert "checks" in data
    assert "timestamp" in data
    assert "version" in data
    assert isinstance(data["checks"], dict)


def test_root_endpoint(test_client: TestClient):
    """Test root endpoint redirect."""
    response = test_client.get("/", allow_redirects=False)
    # Should redirect to docs or return API info
    assert response.status_code in [200, 307, 308]


def test_openapi_schema(test_client: TestClient):
    """Test OpenAPI schema is accessible."""
    response = test_client.get("/openapi.json")
    assert response.status_code == 200
    
    data = response.json()
    assert "openapi" in data
    assert "info" in data
    assert "paths" in data