import os
import types
import logging

import bcrypt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from .database import SessionLocal

logger = logging.getLogger(__name__)
from . import models

SECRET_KEY = os.getenv("SECRET_KEY", "secret")
ALGORITHM = "HS256"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# store revoked JWT tokens
revoked_tokens: set[str] = set()


def revoke_token(token: str) -> None:
    """Mark a token as revoked so it can no longer be used."""
    revoked_tokens.add(token)


def is_token_revoked(token: str) -> bool:
    return token in revoked_tokens

# passlib<=1.7.4 expects `bcrypt.__about__.__version__`, which is no longer
# available starting with bcrypt 4.0. To remain compatible with newer bcrypt
# releases while keeping passlib untouched, emulate the old attribute if it is
# missing.
if not hasattr(bcrypt, "__about__"):
    bcrypt.__about__ = types.SimpleNamespace(__version__=bcrypt.__version__)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_db():
    db = SessionLocal()
    logger.debug("DB session opened")
    try:
        yield db
    finally:
        db.close()
        logger.debug("DB session closed")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def get_user(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()


def authenticate_user(db: Session, username: str, password: str):
    user = get_user(db, username)
    if not user:
        return False
    if not verify_password(password, user.password):
        return False
    return user


def create_access_token(data: dict) -> str:
    return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)


def get_current_user(
    db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int | None = payload.get("user_id")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    if is_token_revoked(token):
        raise credentials_exception
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user is None:
        raise credentials_exception
    return user


def require_api_permission(route: str, method: str):
    def _check(
        current_user: models.User = Depends(get_current_user),
        db: Session = Depends(get_db),
    ):
        perms = (
            db.query(models.ApiPermission).filter_by(route=route, method=method).all()
        )
        if perms:
            allowed = any(p.role_id == current_user.role_id for p in perms)
            if not allowed:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden"
                )

    return _check


def require_admin(current_user: models.User = Depends(get_current_user)):
    if current_user.role.name != "Administrador":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin only")
    return current_user


def require_page_permission(page: str):
    def _check(
        current_user: models.User = Depends(get_current_user),
        db: Session = Depends(get_db),
    ):
        perm = (
            db.query(models.PagePermission)
            .filter_by(page=page, role_id=current_user.role_id)
            .first()
        )
        if perm is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden"
            )

    return _check
