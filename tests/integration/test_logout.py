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


def test_logout_revokes_token():
    token = _login()
    resp = client.post("/logout", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200

    resp = client.get("/roles/", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 401
