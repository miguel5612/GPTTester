import os
import tempfile
from fastapi.testclient import TestClient

os.environ["DATABASE_URL"] = "sqlite:///" + tempfile.mktemp(suffix=".db")

from backend.app.main import app
from backend.app.database import Base, engine

Base.metadata.create_all(bind=engine)
client = TestClient(app)

def test_private_routes_require_auth():
    resp = client.get("/clients/")
    assert resp.status_code == 401

    resp = client.get("/projects/")
    assert resp.status_code == 401
