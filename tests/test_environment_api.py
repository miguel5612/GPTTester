import os
import tempfile
from datetime import datetime, timedelta
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

os.environ["DATABASE_URL"] = "sqlite:///" + tempfile.mktemp(suffix=".db")

from backend.app.main import app
from backend.app.database import Base, engine, SessionLocal
from backend.app import models

Base.metadata.create_all(bind=engine)
client = TestClient(app)


def setup_env() -> tuple[int, int]:
    db: Session = SessionLocal()
    client_obj = models.Client(name="c")
    db.add(client_obj)
    db.commit()
    db.refresh(client_obj)
    project = models.Project(name="p", client_id=client_obj.id)
    db.add(project)
    db.commit()
    db.refresh(project)
    env = models.Environment(project_id=project.id, name=models.EnvironmentType.QA.value)
    db.add(env)
    db.commit()
    db.refresh(env)
    window = models.EnvironmentSchedule(
        environment_id=env.id,
        start_time=datetime.utcnow() - timedelta(hours=1),
        end_time=datetime.utcnow() + timedelta(hours=1),
        blackout=False,
    )
    db.add(window)
    db.commit()
    env_id = env.id
    project_id = project.id
    db.close()
    return env_id, project_id


def test_environment_endpoints():
    env_id, project_id = setup_env()

    resp = client.get(f"/environments/{project_id}")
    assert resp.status_code == 200
    assert len(resp.json()) == 1

    resp = client.put(
        f"/environments/{env_id}/credentials",
        json={"username": "user", "password": "Passw0rd!"},
    )
    assert resp.status_code == 200

    resp = client.get(f"/environments/{env_id}/availability")
    assert resp.status_code == 200
    assert resp.json()["available"] is True

    resp = client.post(f"/environments/{env_id}/promote")
    assert resp.status_code == 200
    assert resp.json()["name"] == models.EnvironmentType.UAT.value
