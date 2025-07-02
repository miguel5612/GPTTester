import os
import tempfile
from fastapi.testclient import TestClient

os.environ["DATABASE_URL"] = "sqlite:///" + tempfile.mktemp(suffix=".db")

from backend.app.main import app  # noqa: E402
from backend.app.database import Base, engine, SessionLocal  # noqa: E402
from backend.app import models, deps  # noqa: E402

Base.metadata.create_all(bind=engine)
client = TestClient(app)


def login(username: str, password: str) -> str:
    resp = client.post("/token", data={"username": username, "password": password})
    assert resp.status_code == 200
    return resp.json()["access_token"]


def test_permissions_editable_for_each_role():
    admin_token = login("admin", "admin")

    resp = client.get("/roles/", headers={"Authorization": f"Bearer {admin_token}"})
    assert resp.status_code == 200
    roles = resp.json()

    for role in roles:
        if role["name"] == "Administrador":
            continue
        role_id = role["id"]

        # grant page permission
        resp = client.post(
            f"/roles/{role_id}/permissions",
            json={"page": f"/extra-{role_id}"},
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

        # create user directly in database
        db = SessionLocal()
        user = models.User(
            username=f"temp_{role_id}",
            password=deps.get_password_hash("temp"),
            role_id=role_id,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        db.close()

        # verify permissions endpoint
        user_token = login(f"temp_{role_id}", "temp")
        resp = client.get("/permissions", headers={"Authorization": f"Bearer {user_token}"})
        assert resp.status_code == 200
        assert f"/extra-{role_id}" in resp.json()["permissions"]

        # user can access GET /roles thanks to API permission
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
            f"/roles/{role_id}/permissions/%2Fextra-{role_id}",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert resp.status_code == 200

        resp = client.get(
            f"/roles/{role_id}/permissions",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert resp.status_code == 200
        assert all(p["page"] != f"/extra-{role_id}" for p in resp.json())
