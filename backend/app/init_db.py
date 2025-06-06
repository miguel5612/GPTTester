from sqlalchemy.orm import Session
from passlib.context import CryptContext

from .database import SessionLocal
from . import models

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


DEFAULT_ROLES = [
    "Administrador",
    "Arquitecto de Automatización",
    "Automation Engineer",
    "Analista de Pruebas con skill de automatización",
]


def init_db():
    db: Session = SessionLocal()
    try:
        # create roles
        for role_name in DEFAULT_ROLES:
            role = db.query(models.Role).filter(models.Role.name == role_name).first()
            if not role:
                db.add(models.Role(name=role_name))
        db.commit()

        # create admin user
        admin = db.query(models.User).filter(models.User.username == "admin").first()
        if not admin:
            hashed_password = pwd_context.hash("admin")
            admin = models.User(
                username="admin",
                email="admin@example.com",
                hashed_password=hashed_password,
            )
            db.add(admin)
            db.commit()
            db.refresh(admin)

        # assign admin role
        admin_role = db.query(models.Role).filter(models.Role.name == "Administrador").first()
        if admin_role not in admin.roles:
            admin.roles.append(admin_role)
            db.commit()
    finally:
        db.close()
