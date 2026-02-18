import uuid

from fastapi.testclient import TestClient

from app.core.database import SessionLocal
from app.core.security import get_password_hash
from app.main import app
from app.models.user import User


client = TestClient(app)


def _unique_username(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:8]}"


def test_register_success():
    username = _unique_username("register")
    response = client.post(
        "/api/auth/register",
        json={
            "username": username,
            "email": f"{username}@example.com",
            "password": "Passw0rd!",
            "role": "handler",
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["success"] is True
    assert "注册成功" in payload["data"]["message"]


def test_login_success_for_active_user():
    username = _unique_username("login")
    password = "Passw0rd!"

    db = SessionLocal()
    try:
        user = User(
            username=username,
            email=f"{username}@example.com",
            hashed_password=get_password_hash(password),
            role="handler",
            is_active=True,
        )
        db.add(user)
        db.commit()
    finally:
        db.close()

    response = client.post(
        "/api/auth/login",
        json={"username": username, "password": password},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["success"] is True
    assert payload["data"]["token_type"] == "bearer"
    assert payload["data"]["user"]["username"] == username


def test_login_returns_422_when_password_missing():
    response = client.post("/api/auth/login", json={"username": "missing-password"})
    assert response.status_code == 422
