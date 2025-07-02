import os
import tempfile
import pytest

# Prepare isolated database before importing the app
os.environ["DATABASE_URL"] = "sqlite:///" + tempfile.mktemp(suffix=".db")

import backend.app.routes  # type: ignore
backend.app.routes.routers = []  # Avoid missing module during import

from backend.app.main import app
from backend.app.database import Base, engine

Base.metadata.create_all(bind=engine)

# Prefixes registered through create_crud_router in backend.app.main
CRUD_PREFIXES = [
    "roles",
    "users",
    "pagepermissions",
    "apipermissions",
    "businessagreements",
    "userinterfaces",
    "elementtypes",
    "elements",
    "projectemployees",
    "actors",
    "habilities",
    "interactions",
    "interactionparameters",
    "interactionapprovalstates",
    "interactionapprovals",
    "validations",
    "validationparameters",
    "validationapprovals",
    "tasks",
    "taskhaveinteractions",
    "fieldtypes",
    "features",
    "clientanalysts",
    "scenariohasfeatures",
    "featuresteps",
    "scenarioinfo",
]

@pytest.mark.parametrize("prefix", CRUD_PREFIXES)
def test_crud_routes_exist(prefix: str) -> None:
    paths = {(r.path, tuple(sorted(r.methods))) for r in app.routes}
    assert (f"/{prefix}/", ("GET",)) in paths
    assert (f"/{prefix}/", ("POST",)) in paths
    assert (f"/{prefix}/{{item_id}}", ("GET",)) in paths
    assert (f"/{prefix}/{{item_id}}", ("PUT",)) in paths
    assert (f"/{prefix}/{{item_id}}", ("DELETE",)) in paths
