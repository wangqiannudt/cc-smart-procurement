from fastapi.testclient import TestClient

from app.main import app
from app.core.deps import get_current_user


client = TestClient(app)


class DummyUser:
    def __init__(self, user_id: int, role: str = "handler"):
        self.id = user_id
        self.username = f"tester-{user_id}"
        self.role = role
        self.is_active = True


def _override_user(user_id: int, role: str = "handler"):
    app.dependency_overrides[get_current_user] = lambda: DummyUser(user_id, role)


def test_analysis_workflow_api_success():
    _override_user(1, "admin")

    # Use minimal payload; endpoint should still return structured data.
    response = client.post(
        "/api/analysis/workflow",
        json={
            "requirement_text": "采购服务器用于数据库集群",
            "product_keyword": "服务器",
            "budget": 150000,
        },
    )

    app.dependency_overrides.clear()

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "history_id" in data["data"]


def test_analysis_history_list_returns_created_record():
    _override_user(101, "handler")

    create_resp = client.post(
        "/api/analysis/workflow",
        json={
            "requirement_text": "采购服务器用于计算任务",
            "product_keyword": "服务器",
            "budget": 200000,
        },
    )
    assert create_resp.status_code == 200
    created_history_id = create_resp.json()["data"]["history_id"]

    list_resp = client.get("/api/analysis/history?page=1&page_size=10")
    app.dependency_overrides.clear()

    assert list_resp.status_code == 200
    payload = list_resp.json()
    assert payload["success"] is True
    assert payload["total"] >= 1
    assert payload["data"][0]["id"] == created_history_id


def test_reuse_history_creates_new_record():
    _override_user(102, "handler")

    create_resp = client.post(
        "/api/analysis/workflow",
        json={
            "requirement_text": "采购工作站",
            "product_keyword": "工作站",
            "budget": 100000,
        },
    )
    assert create_resp.status_code == 200
    source_id = create_resp.json()["data"]["history_id"]

    reuse_resp = client.post(f"/api/analysis/history/{source_id}/reuse")
    app.dependency_overrides.clear()

    assert reuse_resp.status_code == 200
    reused = reuse_resp.json()
    assert reused["success"] is True
    assert reused["data"]["history_id"] != source_id


def test_reuse_history_forbidden_for_other_user():
    _override_user(201, "handler")
    create_resp = client.post(
        "/api/analysis/workflow",
        json={
            "requirement_text": "采购仪器",
            "product_keyword": "仪器仪表",
            "budget": 300000,
        },
    )
    source_id = create_resp.json()["data"]["history_id"]

    _override_user(202, "handler")
    reuse_resp = client.post(f"/api/analysis/history/{source_id}/reuse")
    app.dependency_overrides.clear()

    assert reuse_resp.status_code == 404
