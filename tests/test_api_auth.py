"""Test authentication endpoints."""

import pytest
from fastapi.testclient import TestClient
from typing import Dict


def test_token_endpoint_success(test_client: TestClient):
    """Test successful token generation."""
    response = test_client.post(
        "/api/v1/token",
        data={"username": "johndoe", "password": "secret"}
    )
    assert response.status_code == 200
    
    data = response.json()
    assert "access_token" in data
    assert "token_type" in data
    assert data["token_type"] == "bearer"
    assert isinstance(data["access_token"], str)
    assert len(data["access_token"]) > 0


def test_token_endpoint_invalid_credentials(test_client: TestClient):
    """Test token generation with invalid credentials."""
    response = test_client.post(
        "/api/v1/token",
        data={"username": "johndoe", "password": "wrongpassword"}
    )
    assert response.status_code == 401
    
    data = response.json()
    assert "detail" in data


def test_token_endpoint_nonexistent_user(test_client: TestClient):
    """Test token generation with non-existent user."""
    response = test_client.post(
        "/api/v1/token",
        data={"username": "nonexistent", "password": "password"}
    )
    assert response.status_code == 401


def test_token_endpoint_missing_fields(test_client: TestClient):
    """Test token generation with missing fields."""
    response = test_client.post(
        "/api/v1/token",
        data={"username": "johndoe"}
    )
    assert response.status_code == 422  # Validation error


def test_protected_endpoint_with_valid_token(test_client: TestClient, test_user_headers: Dict[str, str]):
    """Test accessing protected endpoint with valid token."""
    response = test_client.get("/api/v1/herd", headers=test_user_headers)
    assert response.status_code == 200


def test_protected_endpoint_without_token(test_client: TestClient):
    """Test accessing protected endpoint without token."""
    response = test_client.get("/api/v1/herd")
    assert response.status_code == 401


def test_protected_endpoint_with_invalid_token(test_client: TestClient):
    """Test accessing protected endpoint with invalid token."""
    headers = {"Authorization": "Bearer invalid-token"}
    response = test_client.get("/api/v1/herd", headers=headers)
    assert response.status_code == 401


def test_me_endpoint(test_client: TestClient, test_user_headers: Dict[str, str]):
    """Test the /me endpoint."""
    response = test_client.get("/api/v1/users/me", headers=test_user_headers)
    assert response.status_code == 200
    
    data = response.json()
    assert "username" in data
    assert "email" in data
    assert data["username"] == "johndoe"