from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from datetime import datetime
import logging
import os
import time

from . import models, schemas
from .database import SessionLocal

SECRET_KEY = os.getenv("SECRET_KEY", "secret")
ALGORITHM = "HS256"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# In-memory cache for permissions per role with TTL
_permission_cache: dict[int, tuple[list[str], float]] = {}
PERMISSION_TTL = 300  # seconds

logger = logging.getLogger("auth")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def get_user(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()


def get_role(db: Session, role_id: int):
    return db.query(models.Role).filter(models.Role.id == role_id).first()


def get_role_permissions(db: Session, role_id: int) -> list[str]:
    """Return list of permission names for a role, using cache with TTL."""
    entry = _permission_cache.get(role_id)
    now = time.time()
    if entry is None or now > entry[1]:
        perms = [
            p.page
            for p in db.query(models.PagePermission)
            .filter(models.PagePermission.role_id == role_id)
            .all()
        ]
        _permission_cache[role_id] = (perms, now + PERMISSION_TTL)
    else:
        perms = entry[0]
    return perms


def invalidate_role_permissions(role_id: int) -> None:
    """Remove cached permissions for a role."""
    _permission_cache.pop(role_id, None)


def authenticate_user(db: Session, username: str, password: str):
    user = get_user(db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def create_access_token(data: dict) -> str:
    """Generate JWT access token with provided payload."""
    return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)


def require_role(roles: list[str]):
    def dependency(current_user: models.User = Depends(get_current_user)):
        if current_user.role is None or current_user.role.name not in roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail="Insufficient permissions")
        return current_user

    return Depends(dependency)


def require_page_permission(page: str):
    def dependency(
        db: Session = Depends(get_db),
        current_user: models.User = Depends(get_current_user),
    ):
        if current_user.role is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )
        perm = (
            db.query(models.PagePermission)
            .filter(
                models.PagePermission.role_id == current_user.role.id,
                models.PagePermission.page == page,
            )
            .first()
        )
        if not perm:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )
        return current_user

    return Depends(dependency)


def get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str | None = payload.get("sub")
        user_id: int | None = payload.get("user_id")
        if username is None and user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    if user_id is not None:
        user = db.query(models.User).filter(models.User.id == user_id).first()
    else:
        user = get_user(db, username=username)
    if user is None:
        raise credentials_exception
    return user


def get_current_user_with_permissions(
    db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)
) -> models.User:
    """Return the authenticated user with a `permissions` attribute."""
    user = get_current_user(db, token)
    if user.role_id is not None:
        user.permissions = get_role_permissions(db, user.role_id)
    else:
        user.permissions = []
    return user


def require_permission(permission: str):
    """Dependency that ensures the user has a given permission."""

    def dependency(
        current_user: models.User = Depends(get_current_user_with_permissions),
    ) -> models.User:
        if permission not in getattr(current_user, "permissions", []):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )
        return current_user

    return Depends(dependency)


def can_access_client(db: Session, user_id: int, client_id: int) -> bool:
    """Return True if the user can access the given client."""
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        return False
    if user.role and user.role.name in ["Administrador", "Gerente de servicios"]:
        return True
    return (
        db.query(models.client_analysts)
        .filter(
            models.client_analysts.c.client_id == client_id,
            models.client_analysts.c.user_id == user_id,
        )
        .first()
        is not None
    )


def can_access_project(db: Session, user_id: int, project_id: int) -> bool:
    """Return True if the user can access the given project."""
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        return False
    if user.role and user.role.name in ["Administrador", "Gerente de servicios"]:
        return True
    return (
        db.query(models.project_analysts)
        .filter(
            models.project_analysts.c.project_id == project_id,
            models.project_analysts.c.user_id == user_id,
        )
        .first()
        is not None
    )


def require_workspace(
    request: Request,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
) -> models.Workspace:
    workspace = (
        db.query(models.Workspace)
        .filter(models.Workspace.user_id == current_user.id)
        .first()
    )
    if not workspace:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Workspace not selected")
    if not can_access_client(db, current_user.id, workspace.client_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Client access denied")
    if workspace.project_id and not can_access_project(db, current_user.id, workspace.project_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Project access denied")
    request.state.client_id = workspace.client_id
    request.state.project_id = workspace.project_id
    return workspace


def require_client_access(
    request: Request,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
) -> int:
    client_id = getattr(request.state, "client_id", None)
    if client_id is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="client_id missing")
    if not can_access_client(db, current_user.id, client_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Client access denied")
    return client_id


def require_project_access(
    request: Request,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
) -> int:
    project_id = getattr(request.state, "project_id", None)
    if project_id is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="project_id missing")
    if not can_access_project(db, current_user.id, project_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Project access denied")
    return project_id
