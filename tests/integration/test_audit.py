import os
import tempfile
from fastapi.testclient import TestClient

os.environ["DATABASE_URL"] = "sqlite:///" + tempfile.mktemp(suffix=".db")

from backend.app.main import app
from backend.app.database import Base, engine, SessionLocal
from backend.app import models

Base.metadata.create_all(bind=engine)
client = TestClient(app)


def _login() -> str:
    resp = client.post("/token", data={"username": "admin", "password": "admin"})
    assert resp.status_code == 200
    return resp.json()["access_token"]


def test_audit_log_created_and_viewable():
    token = _login()
    resp = client.get("/roles/", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    db = SessionLocal()
    try:
        events = db.query(models.AuditEvent).all()
        assert len(events) >= 2
    finally:
        db.close()
    resp = client.get(
        "/audit-events",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    assert len(resp.json()) >= 2


def test_secret_crud():
    token = _login()
    resp = client.post(
        "/secrets/",
        json={"key": "api", "value": "123"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    resp = client.get(
        "/secrets/api",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    assert resp.json()["value"] == "123"
