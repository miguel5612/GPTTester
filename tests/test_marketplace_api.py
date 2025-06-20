import os
import tempfile
from fastapi.testclient import TestClient

os.environ["DATABASE_URL"] = "sqlite:///" + tempfile.mktemp(suffix=".db")

from backend.app.main import app
from backend.app.database import Base, engine

Base.metadata.create_all(bind=engine)
client = TestClient(app)


def test_marketplace_crud():
    resp = client.post(
        "/marketplace/components/",
        json={"name": "Comp", "description": "d", "code": "print('hi')", "version": "1.0"},
    )
    assert resp.status_code == 200
    comp_id = resp.json()["id"]

    resp = client.get("/marketplace/components/")
    assert resp.status_code == 200
    assert len(resp.json()) == 1

    resp = client.put(
        f"/marketplace/components/{comp_id}",
        json={"name": "Comp", "description": "d", "code": "print('x')", "version": "1.1"},
    )
    assert resp.status_code == 200
    assert resp.json()["version"] == "1.1"

    resp = client.delete(f"/marketplace/components/{comp_id}")
    assert resp.status_code == 200

    resp = client.get("/marketplace/components/")
    assert resp.status_code == 200
    assert resp.json() == []
