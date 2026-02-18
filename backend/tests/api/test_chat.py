from fastapi.testclient import TestClient

from app.api import chat as chat_api
from app.main import app


client = TestClient(app)


def test_chat_conversation_success(monkeypatch):
    def fake_chat(message, session_id=None):
        assert message
        return {
            "response": "建议先明确预算和交付周期。",
            "session_id": session_id or "session-test",
        }

    monkeypatch.setattr(chat_api.chat_agent, "chat", fake_chat)

    response = client.post(
        "/api/chat/conversation",
        json={"message": "帮我分析一下服务器采购需求"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["success"] is True
    assert "建议先明确预算" in payload["data"]["response"]
    assert payload["data"]["session_id"] == "session-test"


def test_chat_conversation_rejects_empty_message():
    response = client.post("/api/chat/conversation", json={"message": ""})
    assert response.status_code == 400
    assert response.json()["detail"] == "消息不能为空"
