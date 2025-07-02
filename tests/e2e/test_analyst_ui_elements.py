import os
import tempfile
from fastapi.testclient import TestClient

os.environ["DATABASE_URL"] = "sqlite:///" + tempfile.mktemp(suffix=".db")

from backend.app.main import app
from backend.app.database import Base, engine, SessionLocal
from backend.app import models

Base.metadata.create_all(bind=engine)
client = TestClient(app)


def login(username: str, password: str) -> str:
    resp = client.post("/token", data={"username": username, "password": password})
    assert resp.status_code == 200
    return resp.json()["access_token"]


def test_analyst_can_create_ui_and_elements():
    admin_token = login("admin", "admin")

    # obtain role id for analyst
    resp = client.get("/roles/", headers={"Authorization": f"Bearer {admin_token}"})
    assert resp.status_code == 200
    roles = resp.json()
    analyst_role_id = next(r["id"] for r in roles if r["name"] == "Analista de Pruebas con skill de automatización")

    # create analyst user
    resp = client.post(
        "/users/",
        json={
            "id": 99,
            "username": "analyst",
            "password": "pwd",
            "role_id": analyst_role_id,
            "is_active": True,
            "last_login": None,
            "endSubscriptionDate": None,
        },
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert resp.status_code == 200
    user_id = resp.json()["id"]

    # create client, asset and project directly in the database
    db = SessionLocal()
    client_obj = models.Client(name="Client", idGerente=1, mision="m", vision="v", paginaInicio="p")
    db.add(client_obj)
    db.commit()
    db.refresh(client_obj)

    asset = models.DigitalAsset(clientId=client_obj.id, description="d")
    db.add(asset)
    db.commit()
    db.refresh(asset)

    project = models.Project(digitalAssetsId=asset.id, name="Proj", objective="o")
    db.add(project)
    db.commit()
    db.refresh(project)

    assignment = models.ProjectEmployee(projectId=project.id, userId=user_id)
    db.add(assignment)
    db.commit()
    asset_id = asset.id
    project_id = project.id
    db.close()

    # grant permissions for UI and elements
    for route in ("/userinterfaces", "/elements"):
        resp = client.post(
            f"/roles/{analyst_role_id}/api-permissions",
            json={"route": route, "method": "POST"},
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert resp.status_code == 200

    # obtain element type id as admin
    resp = client.get("/elementtypes/", headers={"Authorization": f"Bearer {admin_token}"})
    assert resp.status_code == 200
    element_type_id = resp.json()[0]["id"]

    user_token = login("analyst", "pwd")

    # create user interface
    resp = client.post(
        "/userinterfaces/",
        json={"id": 1, "digitalAssetsId": asset_id, "description": "ui", "status": True},
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert resp.status_code == 200
    ui_id = resp.json()["id"]

    # create element
    resp = client.post(
        "/elements/",
        json={
            "id": 1,
            "userInterfaceId": ui_id,
            "elementTypeId": element_type_id,
            "description": "el",
            "status": True,
        },
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert resp.status_code == 200
    assert resp.json()["userInterfaceId"] == ui_id
