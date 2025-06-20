import os
import json
import tempfile
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

os.environ["DATABASE_URL"] = "sqlite:///" + tempfile.mktemp(suffix=".db")

from backend.app.main import app
from backend.app.database import Base, engine, SessionLocal
from backend.app import models

Base.metadata.create_all(bind=engine)

client = TestClient(app)


def setup_pool():
    db = SessionLocal()
    pool = models.DataPool(type="user", environment="QA")
    db.add(pool)
    db.commit()
    db.refresh(pool)
    obj = models.TestDataObject(pool_id=pool.id, data=json.dumps({"u":"x"}), state=models.DataState.NEW.value)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    db.close()
    return obj.id


def test_data_object_lifecycle():
    obj_id = setup_pool()
    resp = client.get("/data-objects", params={"type": "user", "environment": "QA", "state": "available"})
    assert resp.status_code == 200
    assert len(resp.json()) == 1

    resp = client.post("/data-objects/reserve", json={"id": obj_id})
    assert resp.status_code == 200
    assert resp.json()["state"] == "bloqueado"

    resp = client.post("/data-objects/release", json={"id": obj_id})
    assert resp.status_code == 200
    assert resp.json()["state"] == "usado"

    resp = client.get(f"/data-objects/{obj_id}/history")
    assert resp.status_code == 200
    assert len(resp.json()) == 2
