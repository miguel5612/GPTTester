import os
import tempfile


def setup_temp_db():
    os.environ["DATABASE_URL"] = "sqlite:///" + tempfile.mktemp(suffix=".db")
    import backend.app.routes
    backend.app.routes.routers = []
    from backend.app.database import Base, engine
    Base.metadata.create_all(bind=engine)
    from backend.app.main import app  # noqa: F401
    from backend.app.database import SessionLocal
    from backend.app import models
    return SessionLocal, models


def test_seed_contains_minimum_data():
    SessionLocal, models = setup_temp_db()
    db = SessionLocal()
    try:
        assert db.query(models.Role).count() == 7
        assert db.query(models.User).count() >= 4
        assert db.query(models.ElementType).count() == 4
        assert db.query(models.Hability).count() == 4
        assert db.query(models.InteractionApprovalState).count() == 3
        assert db.query(models.FieldType).count() == 5
        start_pages = db.query(models.PagePermission).filter_by(isStartPage=True).count()
        assert start_pages == 7
    finally:
        db.close()


def test_admin_user_exists_with_role():
    SessionLocal, models = setup_temp_db()
    db = SessionLocal()
    try:
        admin = db.query(models.User).filter_by(username="admin").first()
        assert admin is not None
        assert admin.role.name == "Administrador"
    finally:
        db.close()
