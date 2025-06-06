from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from ..database import get_db
from .. import schemas
from ..crud import testplan as crud_testplan
from ..utils import get_current_user, require_role

router = APIRouter(prefix="/testplans", tags=["testplans"])


@router.post("/", response_model=schemas.testplan.TestPlan, status_code=201)
def create_testplan(
    testplan: schemas.testplan.TestPlanCreate,
    db: Session = Depends(get_db),
    current_user: schemas.user.User = Depends(require_role("Administrador")),
):
    if crud_testplan.get_testplan_by_nombre(db, testplan.nombre):
        raise HTTPException(status_code=400, detail="TestPlan exists")
    db_tp = crud_testplan.create_testplan(db, testplan)
    if not db_tp:
        raise HTTPException(status_code=400, detail="Integrity error")
    return db_tp


@router.get("/", response_model=List[schemas.testplan.TestPlan])
def read_testplans(
    db: Session = Depends(get_db),
    current_user: schemas.user.User = Depends(get_current_user),
):
    return crud_testplan.get_testplans(db)


@router.get("/{testplan_id}", response_model=schemas.testplan.TestPlan)
def read_testplan(
    testplan_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.user.User = Depends(get_current_user),
):
    tp = crud_testplan.get_testplan(db, testplan_id)
    if not tp:
        raise HTTPException(status_code=404, detail="TestPlan not found")
    return tp


@router.put("/{testplan_id}", response_model=schemas.testplan.TestPlan)
def update_testplan(
    testplan_id: int,
    testplan: schemas.testplan.TestPlanUpdate,
    db: Session = Depends(get_db),
    current_user: schemas.user.User = Depends(require_role("Administrador")),
):
    tp = crud_testplan.update_testplan(db, testplan_id, testplan)
    if not tp:
        raise HTTPException(status_code=404, detail="TestPlan not found or duplicate")
    return tp


@router.delete("/{testplan_id}", response_model=schemas.testplan.TestPlan)
def delete_testplan(
    testplan_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.user.User = Depends(require_role("Administrador")),
):
    tp = crud_testplan.delete_testplan(db, testplan_id)
    if not tp:
        raise HTTPException(status_code=404, detail="TestPlan not found")
    return tp
