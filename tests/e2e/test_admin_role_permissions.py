import os
import tempfile
from urllib.parse import quote

from fastapi.testclient import TestClient

# Configure isolated database before importing the app
os.environ["DATABASE_URL"] = "sqlite:///" + tempfile.mktemp(suffix=".db")

# Ensure optional routers collection exists to avoid import errors
import importlib
import sys
routes_pkg = importlib.import_module("backend.app.routes")
if not hasattr(routes_pkg, "routers"):
    routes_pkg.routers = []

from backend.app.main import app
from backend.app.database import Base, engine

Base.metadata.create_all(bind=engine)
client = TestClient(app)


def _login() -> str:
    resp = client.post("/token", data={"username": "admin", "password": "admin"})
    assert resp.status_code == 200
    return resp.json()["access_token"]


def test_admin_can_edit_role_permissions():
    token = _login()

    resp = client.get("/roles/", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    roles = resp.json()

    for role in roles:
        role_id = role["id"]
        page = f"/extra-{role_id}"
        route = f"/route-{role_id}"

        resp = client.post(
            f"/roles/{role_id}/permissions",
            json={"page": page},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 200

        resp = client.get(
            f"/roles/{role_id}/permissions",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert any(p["page"] == page for p in resp.json())

        resp = client.post(
            f"/roles/{role_id}/api-permissions",
            json={"route": route, "method": "GET"},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 200
        api_id = resp.json()["id"]

        resp = client.get(
            f"/roles/{role_id}/api-permissions",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert any(p["id"] == api_id for p in resp.json())

        resp = client.delete(
            f"/roles/{role_id}/api-permissions/{api_id}",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 200

        resp = client.delete(
            f"/roles/{role_id}/permissions/{quote(page, safe='')}",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 200
