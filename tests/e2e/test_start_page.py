import os
import tempfile
from fastapi.testclient import TestClient

os.environ["DATABASE_URL"] = "sqlite:///" + tempfile.mktemp(suffix=".db")

from backend.app.main import app
from backend.app.database import Base, engine, SessionLocal
from backend.app import models, deps

Base.metadata.create_all(bind=engine)
client = TestClient(app)

def _login(username: str, password: str) -> str:
    resp = client.post("/token", data={"username": username, "password": password})
    assert resp.status_code == 200
    return resp.json()["access_token"]

def test_start_page_after_login():
    db = SessionLocal()
    role = models.Role(name="DemoRole", description="demo")
    db.add(role)
    db.commit()
    db.refresh(role)

    perm = models.PagePermission(page="/demo", role_id=role.id, isStartPage=True)
    db.add(perm)

    user = models.User(
        username="demouser",
        password=deps.get_password_hash("demo"),
        role_id=role.id,
    )
    db.add(user)
    db.commit()
    db.close()

    token = _login("demouser", "demo")
    resp = client.get(
        f"/roles/{role.id}/permissions",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    perms = resp.json()
    start = next((p for p in perms if p["isStartPage"]), None)
    assert start is not None
    assert start["page"] == "/demo"
