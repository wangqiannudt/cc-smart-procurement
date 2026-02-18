from fastapi.testclient import TestClient

from app.api import contract as contract_api
from app.main import app


client = TestClient(app)


def test_contract_analysis_success(monkeypatch):
    def fake_analyze(content):
        assert "违约责任" in content
        return {
            "elements": {"违约责任": {"found": True, "keywords": ["违约责任"], "contexts": []}},
            "risks": [],
            "risk_level": "风险可控",
            "risk_summary": {"高风险": 0, "中风险": 0, "需特别关注": 0},
            "completeness": 100,
            "suggestions": ["条款较完整"],
        }

    monkeypatch.setattr(contract_api.analyzer, "analyze", fake_analyze)

    response = client.post(
        "/api/contract-analysis",
        files={"file": ("contract.txt", "本合同约定违约责任条款。", "text/plain")},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["success"] is True
    assert payload["data"]["risk_level"] == "风险可控"


def test_contract_analysis_requires_file():
    response = client.post("/api/contract-analysis")
    assert response.status_code == 422
