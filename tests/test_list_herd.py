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
