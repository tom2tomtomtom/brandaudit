import pytest
from src.main import create_app


@pytest.fixture
def client():
    app = create_app("testing")
    with app.test_client() as client:
        yield client


def test_health_check(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json["status"] == "healthy"
