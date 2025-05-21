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
