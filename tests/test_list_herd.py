"""Test herd API endpoints."""

import pytest
from fastapi.testclient import TestClient
from typing import Dict


def test_list_herd(test_client: TestClient, test_user_headers: Dict[str, str]):
    """Test listing herds with proper authentication."""
    response = test_client.get("/api/v1/herd", headers=test_user_headers)
    assert response.status_code == 200
    
    data = response.json()
    assert isinstance(data, dict)
    assert "items" in data
    assert "total" in data
    assert "skip" in data
    assert "limit" in data
    assert isinstance(data["items"], list)
    assert len(data["items"]) >= 2
    assert data["total"] >= 2

    # Check that the herds are in the items
    herd_names = [herd["name"] for herd in data["items"]]
    assert "Alpha Farm" in herd_names
    assert "Beta Farm" in herd_names


def test_list_herd_unauthorized(test_client: TestClient):
    """Test listing herds without authentication."""
    response = test_client.get("/api/v1/herd")
    assert response.status_code == 401


def test_list_herd_invalid_token(test_client: TestClient, invalid_token_headers: Dict[str, str]):
    """Test listing herds with invalid token."""
    response = test_client.get("/api/v1/herd", headers=invalid_token_headers)
    assert response.status_code == 401


def test_list_herd_pagination(test_client: TestClient, test_user_headers: Dict[str, str]):
    """Test herd listing with pagination."""
    response = test_client.get(
        "/api/v1/herd", 
        headers=test_user_headers,
        params={"limit": 1, "skip": 0}
    )
    assert response.status_code == 200
    
    data = response.json()
    assert len(data["items"]) == 1
    assert data["limit"] == 1
    assert data["skip"] == 0
