from sqlalchemy.orm import Session
from .. import models, schemas
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()


def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()


def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = pwd_context.hash(user.password)
    db_user = models.User(
        username=user.username, email=user.email, hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def assign_role(db: Session, user_id: int, role: models.Role):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user and role not in user.roles:
        user.roles.append(role)
        db.commit()
        db.refresh(user)
    return user


def remove_role(db: Session, user_id: int, role: models.Role):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user and role in user.roles:
        user.roles.remove(role)
        db.commit()
        db.refresh(user)
    return user
