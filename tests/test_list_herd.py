import os
import tempfile
from fastapi.testclient import TestClient

fd, db_path = tempfile.mkstemp(suffix=".db")
os.close(fd)
os.environ["DATABASE_PATH"] = db_path

from app.main import app
from app.seed import seed

client: TestClient


def setup_module(module):
    seed()

    global client
    client = TestClient(app)


def teardown_module(module):
    if os.path.exists(db_path):
        os.remove(db_path)


def test_list_herd():
    response = client.get(
        "/api/v1/herd",
        headers={"Authorization": "Bearer fake-super-secret-token"},
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 2
    assert {"id": 1, "name": "Alpha Farm", "location": "Wisconsin"} in data


def test_create_herd_success():
    herd_data = {"name": "Sunset Acres", "location": "California"}
    response = client.post(
        "/api/v1/herd",
        json=herd_data,
        headers={"Authorization": "Bearer fake-super-secret-token"},
    )
    # This test is expected to fail until the endpoint is implemented
    assert response.status_code == 201  # Assuming 201 Created
    data = response.json()
    assert data["name"] == herd_data["name"]
    assert data["location"] == herd_data["location"]
    assert "id" in data
    # Optionally, verify in DB if possible and desired for this test stage
    # For now, focusing on the API response


def test_create_herd_invalid_payload():
    response = client.post(
        "/api/v1/herd",
        json={},  # Empty payload, missing required fields
        headers={"Authorization": "Bearer fake-super-secret-token"},
    )
    # This test is expected to fail until the endpoint is implemented
    # FastAPI should automatically return 422 if Pydantic model validation fails
    assert response.status_code == 422


# --- Authentication tests for GET /api/v1/herd ---

def test_list_herd_no_token():
    response = client.get("/api/v1/herd")  # No Authorization header
    assert response.status_code == 401
    # FastAPI's default for missing OAuth2PasswordBearer is 403, but our dummy check
    # is what raises 401 if the token is not 'fake-super-secret-token'.
    # If the dependency itself fails to extract a token, it might be 403.
    # Let's check the actual behavior of FastAPI's OAuth2PasswordBearer when no header is sent.
    # It actually results in a 403 Forbidden if the scheme is enforced but no token is provided.
    # However, our get_current_token is defined with `token: str = Depends(oauth2_scheme)`.
    # If no token is provided, Depends(oauth2_scheme) itself will raise an HTTPException(status_code=401)
    # if `auto_error=True` (default). So, 401 is correct.


def test_list_herd_invalid_token():
    response = client.get(
        "/api/v1/herd",
        headers={"Authorization": "Bearer invalid-token"},
    )
    assert response.status_code == 401


# --- Authentication tests for POST /api/v1/herd ---

def test_create_herd_no_token():
    herd_data = {"name": "NoToken Farm", "location": "NoAuthLand"}
    response = client.post(
        "/api/v1/herd",
        json=herd_data,
        # No Authorization header
    )
    assert response.status_code == 401


def test_create_herd_invalid_token():
    herd_data = {"name": "InvalidToken Farm", "location": "BadAuthLand"}
    response = client.post(
        "/api/v1/herd",
        json=herd_data,
        headers={"Authorization": "Bearer invalid-token-for-posting"},
    )
    assert response.status_code == 401
