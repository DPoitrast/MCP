from fastapi.testclient import TestClient

from app.main import app
from app.seed import seed

client = TestClient(app)


def setup_module(module):
    seed()


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
