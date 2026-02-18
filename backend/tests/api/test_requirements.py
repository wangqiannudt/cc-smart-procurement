from fastapi.testclient import TestClient

from app.api import requirements as requirements_api
from app.main import app


client = TestClient(app)


def test_review_requirements_text_success(monkeypatch):
    def fake_review(content, category_id=None, subtype_id=None):
        assert "采购" in content
        assert category_id == "server"
        return {
            "issues": [],
            "suggestions": ["指标描述清晰"],
            "completeness_score": 92,
            "issue_count": 0,
            "error_count": 0,
            "warning_count": 0,
            "info_count": 0,
            "extracted_fields": {"cpu": {"value": "32核"}},
            "field_count": 1,
        }

    monkeypatch.setattr(requirements_api.reviewer, "review", fake_review)

    response = client.post(
        "/api/review-requirements/text",
        json={
            "content": "采购服务器用于数据库集群，要求高可用",
            "category_id": "server",
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["success"] is True
    assert payload["data"]["completeness_score"] == 92


def test_review_requirements_text_rejects_blank_content():
    response = client.post("/api/review-requirements/text", json={"content": "   "})
    assert response.status_code == 400
    assert response.json()["detail"] == "内容不能为空"
