import os
import tempfile
from fastapi.testclient import TestClient

os.environ["DATABASE_URL"] = "sqlite:///" + tempfile.mktemp(suffix=".db")

from backend.app.main import app
from backend.app.database import Base, engine

Base.metadata.create_all(bind=engine)
client = TestClient(app)


def test_user_can_register_and_login():
    resp = client.post(
        "/register",
        json={"username": "newuser", "password": "newpass123", "user_type": "analyst"},
    )
    assert resp.status_code == 200
    user_id = resp.json()["id"]

    resp = client.post(
        "/token",
        data={"username": "newuser", "password": "newpass123"},
    )
    assert resp.status_code == 200
    assert "access_token" in resp.json()
