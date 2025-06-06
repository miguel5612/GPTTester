from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from ..database import get_db
from .. import schemas
from ..crud import role as crud_role
from ..utils import get_current_user, require_role

router = APIRouter(prefix="/roles", tags=["roles"])


@router.get("/", response_model=List[schemas.role.Role])
def read_roles(
    db: Session = Depends(get_db),
    current_user: schemas.user.User = Depends(require_role("Administrador")),
):
    return crud_role.get_roles(db)


@router.post("/", response_model=schemas.role.Role, status_code=201)
def create_role(
    role: schemas.role.RoleCreate,
    db: Session = Depends(get_db),
    current_user: schemas.user.User = Depends(require_role("Administrador")),
):
    if crud_role.get_role_by_name(db, role.name):
        raise HTTPException(status_code=400, detail="Role exists")
    return crud_role.create_role(db, role)


@router.put("/{role_id}", response_model=schemas.role.Role)
def update_role(
    role_id: int,
    role: schemas.role.RoleCreate,
    db: Session = Depends(get_db),
    current_user: schemas.user.User = Depends(require_role("Administrador")),
):
    db_role = crud_role.update_role(db, role_id, role)
    if not db_role:
        raise HTTPException(status_code=404, detail="Role not found")
    return db_role


@router.delete("/{role_id}", response_model=schemas.role.Role)
def delete_role(
    role_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.user.User = Depends(require_role("Administrador")),
):
    db_role = crud_role.delete_role(db, role_id)
    if not db_role:
        raise HTTPException(status_code=404, detail="Role not found")
    return db_role
