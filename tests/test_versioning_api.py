import os
import json
import tempfile
from fastapi.testclient import TestClient

os.environ["DATABASE_URL"] = "sqlite:///" + tempfile.mktemp(suffix=".db")

from backend.app.main import app
from backend.app.database import Base, engine

Base.metadata.create_all(bind=engine)

client = TestClient(app)


def get_token() -> str:
    resp = client.post("/token", data={"username": "admin", "password": "admin"})
    assert resp.status_code == 200
    return resp.json()["access_token"]


def auth_headers():
    token = get_token()
    return {"Authorization": f"Bearer {token}"}


def setup_test() -> int:
    resp = client.post(
        "/tests/",
        json={"name": "sample", "description": "d"},
        headers=auth_headers(),
    )
    assert resp.status_code == 200
    return resp.json()["id"]


def test_versioning_flow():
    test_id = setup_test()

    resp = client.post(
        f"/tests/{test_id}/branch",
        json={"name": "main"},
        headers=auth_headers(),
    )
    assert resp.status_code == 200
    branch_id = resp.json()["id"]

    resp = client.post(
        f"/tests/{test_id}/commit",
        json={"branch_id": branch_id, "message": "init"},
        headers=auth_headers(),
    )
    assert resp.status_code == 200

    resp = client.get(f"/tests/{test_id}/history", headers=auth_headers())
    assert resp.status_code == 200
    history = resp.json()
    assert len(history) == 1

    version_id = history[0]["version_id"]

    resp = client.get(
        f"/tests/{test_id}/diff",
        params={"from": version_id, "to": version_id},
        headers=auth_headers(),
    )
    assert resp.status_code == 200
    assert "diff" in resp.json()
