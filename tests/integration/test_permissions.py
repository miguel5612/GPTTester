import os
import tempfile
from fastapi.testclient import TestClient

os.environ["DATABASE_URL"] = "sqlite:///" + tempfile.mktemp(suffix=".db")

from backend.app.main import app
from backend.app.database import Base, engine, SessionLocal
from backend.app import models, deps

Base.metadata.create_all(bind=engine)
client = TestClient(app)


def login(username: str, password: str) -> str:
    resp = client.post("/token", data={"username": username, "password": password})
    assert resp.status_code == 200
    return resp.json()["access_token"]


def test_role_permissions_flow():
    admin_token = login("admin", "admin")

    # choose an existing role for testing
    resp = client.get("/roles/", headers={"Authorization": f"Bearer {admin_token}"})
    assert resp.status_code == 200
    data = resp.json()
    role_id = next(r["id"] for r in data if r["name"] != "Administrador")
    admin_role_id = next(r["id"] for r in data if r["name"] == "Administrador")

    # grant page permission
    resp = client.post(
        f"/roles/{role_id}/permissions",
        json={"page": "/extra"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert resp.status_code == 200

    # grant API permission
    resp = client.post(
        f"/roles/{role_id}/api-permissions",
        json={"route": "/roles", "method": "GET"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert resp.status_code == 200
    api_perm_id = resp.json()["id"]

    resp = client.post(
        f"/roles/{admin_role_id}/api-permissions",
        json={"route": "/roles", "method": "GET"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert resp.status_code == 200

    # create user directly in the database
    db = SessionLocal()
    user = models.User(
        username="temp",
        password=deps.get_password_hash("temp"),
        role_id=role_id,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    user_id = user.id
    db.close()

    # verify permissions endpoint
    user_token = login("temp", "temp")
    resp = client.get("/permissions", headers={"Authorization": f"Bearer {user_token}"})
    assert resp.status_code == 200
    assert "/extra" in resp.json()["permissions"]

    # user can access GET /roles thanks to permission
    resp = client.get("/roles/", headers={"Authorization": f"Bearer {user_token}"})
    assert resp.status_code == 200

    # remove API permission and ensure access denied
    resp = client.delete(
        f"/roles/{role_id}/api-permissions/{api_perm_id}",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert resp.status_code == 200

    resp = client.get("/roles/", headers={"Authorization": f"Bearer {user_token}"})
    assert resp.status_code == 403

    # remove page permission
    resp = client.delete(
        f"/roles/{role_id}/permissions/%2Fextra",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert resp.status_code == 200

    resp = client.get(
        "/roles/{role_id}/permissions".format(role_id=role_id),
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert resp.status_code == 200
    assert all(p["page"] != "/extra" for p in resp.json())
