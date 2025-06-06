from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from ..database import get_db
from .. import schemas
from ..crud import scenario as crud_scenario
from ..utils import get_current_user, require_role

router = APIRouter(prefix="/scenarios", tags=["scenarios"])


@router.post("/", response_model=schemas.scenario.Scenario, status_code=201)
def create_scenario(
    scenario: schemas.scenario.ScenarioCreate,
    db: Session = Depends(get_db),
    current_user: schemas.user.User = Depends(require_role("Administrador")),
):
    db_sc = crud_scenario.create_scenario(db, scenario)
    if not db_sc:
        raise HTTPException(status_code=400, detail="Integrity error")
    return db_sc


@router.get("/", response_model=List[schemas.scenario.Scenario])
def read_scenarios(
    db: Session = Depends(get_db),
    current_user: schemas.user.User = Depends(get_current_user),
):
    return crud_scenario.get_scenarios(db)


@router.get("/{scenario_id}", response_model=schemas.scenario.Scenario)
def read_scenario(
    scenario_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.user.User = Depends(get_current_user),
):
    sc = crud_scenario.get_scenario(db, scenario_id)
    if not sc:
        raise HTTPException(status_code=404, detail="Scenario not found")
    return sc


@router.put("/{scenario_id}", response_model=schemas.scenario.Scenario)
def update_scenario(
    scenario_id: int,
    scenario: schemas.scenario.ScenarioUpdate,
    db: Session = Depends(get_db),
    current_user: schemas.user.User = Depends(require_role("Administrador")),
):
    sc = crud_scenario.update_scenario(db, scenario_id, scenario)
    if not sc:
        raise HTTPException(status_code=404, detail="Scenario not found or duplicate")
    return sc


@router.delete("/{scenario_id}", response_model=schemas.scenario.Scenario)
def delete_scenario(
    scenario_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.user.User = Depends(require_role("Administrador")),
):
    sc = crud_scenario.delete_scenario(db, scenario_id)
    if not sc:
        raise HTTPException(status_code=404, detail="Scenario not found")
    return sc
