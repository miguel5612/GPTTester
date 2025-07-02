import os
import tempfile
from fastapi.testclient import TestClient
import pytest

# Use a temporary SQLite DB for isolation
os.environ["DATABASE_URL"] = "sqlite:///" + tempfile.mktemp(suffix=".db")

from backend.app.main import app  # noqa: E402
from backend.app.database import Base, engine  # noqa: E402

Base.metadata.create_all(bind=engine)
client = TestClient(app)


@pytest.mark.parametrize(
    "username",
    ["admin", "architect", "AngelC", "T23AutoPerson"],
)
def test_default_user_login(username: str) -> None:
    resp = client.post("/token", data={"username": username, "password": "admin"})
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
