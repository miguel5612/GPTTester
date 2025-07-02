import os
import tempfile
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from uuid import uuid4

os.environ["DATABASE_URL"] = "sqlite:///" + tempfile.mktemp(suffix=".db")

from backend.app.main import app
from backend.app.database import Base, engine, SessionLocal
from backend.app import models, deps

Base.metadata.create_all(bind=engine)
client = TestClient(app)


def _login() -> str:
    resp = client.post("/token", data={"username": "admin", "password": "admin"})
    assert resp.status_code == 200
    return resp.json()["access_token"]


def _setup_projects() -> tuple[int, int, int]:
    """Create a user and two projects sharing a digital asset."""
    db: Session = SessionLocal()
    client_obj = models.Client(name="c")
    db.add(client_obj)
    db.commit()
    db.refresh(client_obj)

    asset = models.DigitalAsset(clientId=client_obj.id)
    db.add(asset)
    db.commit()
    db.refresh(asset)

    project1 = models.Project(name="p1", digitalAssetsId=asset.id)
    project2 = models.Project(name="p2", digitalAssetsId=asset.id)
    db.add(project1)
    db.add(project2)
    db.commit()
    db.refresh(project1)
    db.refresh(project2)

    user = models.User(
        username=f"temp_{uuid4().hex[:6]}",
        password=deps.get_password_hash("pwd"),
        role_id=1,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    user_id = user.id
    p1_id = project1.id
    p2_id = project2.id
    db.close()
    return user_id, p1_id, p2_id


def test_cannot_exceed_nine_hours():
    token = _login()
    user_id, p1, p2 = _setup_projects()

    resp = client.post(
        "/projectemployees/",
        json={"id": 1, "projectId": p1, "userId": user_id, "objective": "", "dedicationHours": 5},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200

    resp = client.post(
        "/projectemployees/",
        json={"id": 2, "projectId": p2, "userId": user_id, "objective": "", "dedicationHours": 5},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 400
    assert "dedication" in resp.json()["detail"]


def test_update_respects_limit():
    token = _login()
    user_id, p1, p2 = _setup_projects()

    resp = client.post(
        "/projectemployees/",
        json={"id": 3, "projectId": p1, "userId": user_id, "objective": "", "dedicationHours": 4},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    assignment_id = resp.json()["id"]

    resp = client.post(
        "/projectemployees/",
        json={"id": 4, "projectId": p2, "userId": user_id, "objective": "", "dedicationHours": 4},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200

    resp = client.put(
        f"/projectemployees/{assignment_id}",
        json={"id": assignment_id, "projectId": p1, "userId": user_id, "objective": "", "dedicationHours": 6},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 400
    assert "dedication" in resp.json()["detail"]
