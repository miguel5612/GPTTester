from sqlalchemy.orm import Session
from .. import models, schemas


def get_role(db: Session, role_id: int):
    return db.query(models.Role).filter(models.Role.id == role_id).first()


def get_role_by_name(db: Session, name: str):
    return db.query(models.Role).filter(models.Role.name == name).first()


def get_roles(db: Session):
    return db.query(models.Role).all()


def create_role(db: Session, role: schemas.role.RoleCreate):
    db_role = models.Role(name=role.name)
    db.add(db_role)
    db.commit()
    db.refresh(db_role)
    return db_role


def update_role(db: Session, role_id: int, role: schemas.role.RoleCreate):
    db_role = get_role(db, role_id)
    if db_role:
        db_role.name = role.name
        db.commit()
        db.refresh(db_role)
    return db_role


def delete_role(db: Session, role_id: int):
    db_role = get_role(db, role_id)
    if db_role:
        db.delete(db_role)
        db.commit()
    return db_role
