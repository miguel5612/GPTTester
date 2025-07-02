import os
import tempfile
import importlib
from fastapi.testclient import TestClient

# Use a temporary SQLite database for the test
os.environ["DATABASE_URL"] = "sqlite:///" + tempfile.mktemp(suffix=".db")

# Ensure expected attribute exists before importing app
routes_pkg = importlib.import_module("backend.app.routes")
if not hasattr(routes_pkg, "routers"):
    routes_pkg.routers = []

from backend.app.main import app
from backend.app.database import Base, engine

# Create all tables in the temporary database
Base.metadata.create_all(bind=engine)
client = TestClient(app)

def test_invalid_login_returns_friendly_message():
    resp = client.post("/token", data={"username": "wrong", "password": "bad"})
    assert resp.status_code == 400
    assert resp.json()["detail"] == "Invalid credentials"
