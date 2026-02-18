from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_price_reference_success():
    response = client.get("/api/price-reference", params={"keyword": "服务器"})

    assert response.status_code == 200
    payload = response.json()
    assert payload["success"] is True
    assert payload["data"]["total"] >= 1
    assert isinstance(payload["data"]["records"], list)


def test_price_predict_returns_422_without_keyword():
    response = client.get("/api/price-reference/predict", params={"months": 3})
    assert response.status_code == 422
