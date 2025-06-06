from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from ..database import get_db
from .. import schemas
from ..crud import user as crud_user
from ..utils import get_current_user, require_role
from ..crud import role as crud_role

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/", response_model=schemas.user.User, status_code=201)
def create_user(user: schemas.user.UserCreate, db: Session = Depends(get_db)):
    if crud_user.get_user_by_username(db, user.username) or crud_user.get_user_by_email(db, user.email):
        raise HTTPException(status_code=400, detail="Registration failed")
    return crud_user.create_user(db, user)


@router.get("/me", response_model=schemas.user.User)
def read_users_me(current_user: schemas.user.User = Depends(get_current_user)):
    return current_user


@router.post("/{user_id}/roles/{role_id}", response_model=schemas.user.User)
def assign_role_to_user(
    user_id: int,
    role_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.user.User = Depends(require_role("Administrador")),
):
    role = crud_role.get_role(db, role_id)
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    user = crud_user.assign_role(db, user_id, role)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.delete("/{user_id}/roles/{role_id}", response_model=schemas.user.User)
def remove_role_from_user(
    user_id: int,
    role_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.user.User = Depends(require_role("Administrador")),
):
    role = crud_role.get_role(db, role_id)
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    user = crud_user.remove_role(db, user_id, role)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
