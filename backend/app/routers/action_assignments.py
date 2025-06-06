from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from ..database import get_db
from .. import schemas
from ..crud import (
    action_assignment as crud_assignment,
    action as crud_action,
    page_element as crud_element,
    test as crud_test,
)
from ..utils import get_current_user, require_role

router = APIRouter(prefix="/assignments", tags=["assignments"])


@router.post("/", response_model=schemas.action_assignment.ActionAssignment, status_code=201)
def create_assignment(
    assignment: schemas.action_assignment.ActionAssignmentCreate,
    db: Session = Depends(get_db),
    current_user: schemas.user.User = Depends(require_role("Administrador")),
):
    action = crud_action.get_action(db, assignment.action_id)
    element = crud_element.get_element(db, assignment.element_id)
    test = crud_test.get_test(db, assignment.test_id)
    if not action or not element or not test:
        raise HTTPException(status_code=404, detail="Related entity not found")
    missing = set(action.argumentos.keys()) - set(assignment.parameters.keys())
    if missing:
        raise HTTPException(status_code=400, detail="Missing parameters")
    db_assignment = crud_assignment.create_assignment(db, assignment)
    if not db_assignment:
        raise HTTPException(status_code=400, detail="Integrity error")
    return db_assignment


@router.get("/", response_model=List[schemas.action_assignment.ActionAssignment])
def read_assignments(
    test_id: int | None = None,
    db: Session = Depends(get_db),
    current_user: schemas.user.User = Depends(get_current_user),
):
    return crud_assignment.get_assignments(db, test_id)


@router.get("/{assignment_id}", response_model=schemas.action_assignment.ActionAssignment)
def read_assignment(
    assignment_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.user.User = Depends(get_current_user),
):
    assignment = crud_assignment.get_assignment(db, assignment_id)
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    return assignment


@router.put("/{assignment_id}", response_model=schemas.action_assignment.ActionAssignment)
def update_assignment(
    assignment_id: int,
    assignment: schemas.action_assignment.ActionAssignmentUpdate,
    db: Session = Depends(get_db),
    current_user: schemas.user.User = Depends(require_role("Administrador")),
):
    action = crud_action.get_action(db, assignment.action_id)
    element = crud_element.get_element(db, assignment.element_id)
    test = crud_test.get_test(db, assignment.test_id)
    if not action or not element or not test:
        raise HTTPException(status_code=404, detail="Related entity not found")
    missing = set(action.argumentos.keys()) - set(assignment.parameters.keys())
    if missing:
        raise HTTPException(status_code=400, detail="Missing parameters")
    db_assignment = crud_assignment.update_assignment(db, assignment_id, assignment)
    if not db_assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    return db_assignment


@router.delete("/{assignment_id}", response_model=schemas.action_assignment.ActionAssignment)
def delete_assignment(
    assignment_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.user.User = Depends(require_role("Administrador")),
):
    assignment = crud_assignment.delete_assignment(db, assignment_id)
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    return assignment
