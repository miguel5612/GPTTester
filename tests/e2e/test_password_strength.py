import os
import tempfile
from fastapi.testclient import TestClient

os.environ["DATABASE_URL"] = "sqlite:///" + tempfile.mktemp(suffix=".db")

from backend.app.main import app
from backend.app.database import Base, engine

Base.metadata.create_all(bind=engine)
client = TestClient(app)


def _login() -> str:
    resp = client.post("/token", data={"username": "admin", "password": "admin"})
    assert resp.status_code == 200
    return resp.json()["access_token"]


def _first_role_id(token: str) -> int:
    resp = client.get("/roles/", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    return resp.json()[0]["id"]


def test_register_requires_strong_password():
    token = _login()
    role_id = _first_role_id(token)

    weak_user = {
        "id": 100,
        "username": "weakuser",
        "password": "weak",
        "role_id": role_id,
        "is_active": True,
        "last_login": None,
        "endSubscriptionDate": None,
    }
    resp = client.post("/users/", json=weak_user, headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 400

    strong_user = weak_user | {
        "id": 101,
        "username": "stronguser",
        "password": "Str0ngPass!",
    }
    resp = client.post("/users/", json=strong_user, headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    assert resp.json()["username"] == "stronguser"
