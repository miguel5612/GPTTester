from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from ..database import get_db
from .. import schemas
from ..crud import action as crud_action
from ..utils import get_current_user, require_role

router = APIRouter(prefix="/actions", tags=["actions"])


@router.post("/", response_model=schemas.action.Action, status_code=201)
def create_action(
    action: schemas.action.ActionCreate,
    db: Session = Depends(get_db),
    current_user: schemas.user.User = Depends(require_role("Administrador")),
):
    db_action = crud_action.create_action(db, action)
    if not db_action:
        raise HTTPException(status_code=400, detail="Integrity error")
    return db_action


@router.get("/", response_model=List[schemas.action.Action])
def read_actions(
    db: Session = Depends(get_db),
    current_user: schemas.user.User = Depends(get_current_user),
):
    return crud_action.get_actions(db)


@router.get("/{action_id}", response_model=schemas.action.Action)
def read_action(
    action_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.user.User = Depends(get_current_user),
):
    ac = crud_action.get_action(db, action_id)
    if not ac:
        raise HTTPException(status_code=404, detail="Action not found")
    return ac


@router.put("/{action_id}", response_model=schemas.action.Action)
def update_action(
    action_id: int,
    action: schemas.action.ActionUpdate,
    db: Session = Depends(get_db),
    current_user: schemas.user.User = Depends(require_role("Administrador")),
):
    ac = crud_action.update_action(db, action_id, action)
    if not ac:
        raise HTTPException(status_code=404, detail="Action not found or duplicate")
    return ac


@router.delete("/{action_id}", response_model=schemas.action.Action)
def delete_action(
    action_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.user.User = Depends(require_role("Administrador")),
):
    ac = crud_action.delete_action(db, action_id)
    if not ac:
        raise HTTPException(status_code=404, detail="Action not found")
    return ac
