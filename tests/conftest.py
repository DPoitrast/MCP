"""Test configuration and fixtures."""

import os
import tempfile
import pytest
from fastapi.testclient import TestClient
from typing import Generator, Dict

# Set up test database before importing app
fd, db_path = tempfile.mkstemp(suffix=".db")
os.close(fd)
os.environ["DATABASE_PATH"] = db_path
os.environ["ENVIRONMENT"] = "testing"
os.environ["SECRET_KEY"] = "test-secret-key-for-testing-only"

from app.main import app
from app.seed import seed
from app.core.security import create_access_token
from datetime import timedelta


@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    """Set up test database for the entire test session."""
    seed()
    yield
    # Cleanup
    if os.path.exists(db_path):
        os.remove(db_path)


@pytest.fixture
def test_client() -> Generator[TestClient, None, None]:
    """Create a test client."""
    with TestClient(app) as client:
        yield client


@pytest.fixture
def test_user_token() -> str:
    """Create a valid JWT token for testing."""
    token_data = {"sub": "johndoe"}
    return create_access_token(
        data=token_data,
        expires_delta=timedelta(hours=1)
    )


@pytest.fixture
def test_user_headers(test_user_token: str) -> Dict[str, str]:
    """Create authorization headers with test token."""
    return {"Authorization": f"Bearer {test_user_token}"}


@pytest.fixture
def admin_user_token() -> str:
    """Create a valid JWT token for admin user."""
    token_data = {"sub": "alice"}
    return create_access_token(
        data=token_data,
        expires_delta=timedelta(hours=1)
    )


@pytest.fixture
def admin_user_headers(admin_user_token: str) -> Dict[str, str]:
    """Create authorization headers with admin token."""
    return {"Authorization": f"Bearer {admin_user_token}"}


@pytest.fixture
def invalid_token_headers() -> Dict[str, str]:
    """Create headers with invalid token."""
    return {"Authorization": "Bearer invalid-token-12345"}