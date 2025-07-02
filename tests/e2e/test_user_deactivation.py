import os
import tempfile
from fastapi.testclient import TestClient

os.environ["DATABASE_URL"] = "sqlite:///" + tempfile.mktemp(suffix=".db")

from backend.app.main import app
from backend.app.database import Base, engine

Base.metadata.create_all(bind=engine)
client = TestClient(app)


def login(username: str, password: str) -> str:
    resp = client.post("/token", data={"username": username, "password": password})
    assert resp.status_code == 200
    return resp.json()["access_token"]


def test_disabled_user_cannot_login():
    admin_token = login("admin", "admin")

    resp = client.get("/users/", headers={"Authorization": f"Bearer {admin_token}"})
    assert resp.status_code == 200
    users = resp.json()
    target = next(u for u in users if u["username"] == "architect")

    user_id = target["id"]
    role_id = target["role_id"]

    update = {
        "id": user_id,
        "username": "architect",
        "password": "admin",
        "last_login": None,
        "is_active": False,
        "endSubscriptionDate": None,
        "role_id": role_id,
    }
    resp = client.put(
        f"/users/{user_id}",
        json=update,
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert resp.status_code == 200

    resp = client.post("/token", data={"username": "architect", "password": "admin"})
    assert resp.status_code == 400
