import pytest
from flask.testing import FlaskClient

from sciCalc.app import create_app


@pytest.fixture
def client() -> FlaskClient:
    app = create_app()
    app.config.update(TESTING=True)
    return app.test_client()


def test_index_page_loads(client: FlaskClient) -> None:
    response = client.get("/")
    assert response.status_code == 200
    assert b"calculator" in response.data.lower()


def test_health_check(client: FlaskClient) -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.get_json() == {"status": "ok"}


def test_calculate_valid_expression(client: FlaskClient) -> None:
    response = client.post("/api/calculate", json={"expression": "2 + 2"})
    assert response.status_code == 200
    assert response.get_json() == {"result": 4}


def test_calculate_invalid_expression(client: FlaskClient) -> None:
    response = client.post("/api/calculate", json={"expression": "1 / 0"})
    assert response.status_code == 400
    assert "error" in response.get_json()


def test_calculate_missing_expression(client: FlaskClient) -> None:
    response = client.post("/api/calculate", json={})
    assert response.status_code == 400


def test_calculate_non_string_expression(client: FlaskClient) -> None:
    response = client.post("/api/calculate", json={"expression": 42})
    assert response.status_code == 400
