from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional
from sqlalchemy.orm import Session

from ..database import get_db
from .. import schemas
from ..crud import execution_plan as crud_execution_plan, execution as crud_execution
from ..crud import test as crud_test
from ..crud import agent as crud_agent
from ..utils import get_current_user, require_role

router = APIRouter(prefix="/execution-plans", tags=["execution_plans"])


@router.post("/", response_model=schemas.execution_plan.ExecutionPlan, status_code=201)
def create_execution_plan(
    plan: schemas.execution_plan.ExecutionPlanCreate,
    db: Session = Depends(get_db),
    current_user: schemas.user.User = Depends(require_role("Administrador")),
):
    if not crud_test.get_test(db, plan.test_id):
        raise HTTPException(status_code=400, detail="TestCase not found")
    if not crud_agent.get_agent(db, plan.agent_id):
        raise HTTPException(status_code=400, detail="Agent not found")
    return crud_execution_plan.create_execution_plan(db, plan)


@router.get("/", response_model=List[schemas.execution_plan.ExecutionPlan])
def read_execution_plans(
    nombre: Optional[str] = None,
    test_id: Optional[int] = None,
    agent_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: schemas.user.User = Depends(get_current_user),
):
    return crud_execution_plan.get_execution_plans(db, nombre=nombre, test_id=test_id, agent_id=agent_id)


@router.get("/{plan_id}", response_model=schemas.execution_plan.ExecutionPlan)
def read_execution_plan(
    plan_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.user.User = Depends(get_current_user),
):
    plan = crud_execution_plan.get_execution_plan(db, plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Execution plan not found")
    return plan


@router.post("/{plan_id}/execute", response_model=schemas.execution.Execution, status_code=201)
def execute_plan(
    plan_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.user.User = Depends(get_current_user),
):
    plan = crud_execution_plan.get_execution_plan(db, plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Execution plan not found")
    pending = crud_execution.get_pending_execution_by_agent(db, plan.agent_id)
    if pending:
        raise HTTPException(status_code=400, detail="Agent already running a plan")
    execution = crud_execution.create_execution(db, plan)
    return execution


@router.put("/{plan_id}", response_model=schemas.execution_plan.ExecutionPlan)
def update_execution_plan(
    plan_id: int,
    plan: schemas.execution_plan.ExecutionPlanUpdate,
    db: Session = Depends(get_db),
    current_user: schemas.user.User = Depends(require_role("Administrador")),
):
    if not crud_test.get_test(db, plan.test_id):
        raise HTTPException(status_code=400, detail="TestCase not found")
    if not crud_agent.get_agent(db, plan.agent_id):
        raise HTTPException(status_code=400, detail="Agent not found")
    updated = crud_execution_plan.update_execution_plan(db, plan_id, plan)
    if not updated:
        raise HTTPException(status_code=404, detail="Execution plan not found")
    return updated


@router.delete("/{plan_id}", response_model=schemas.execution_plan.ExecutionPlan)
def delete_execution_plan(
    plan_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.user.User = Depends(require_role("Administrador")),
):
    plan = crud_execution_plan.delete_execution_plan(db, plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Execution plan not found")
    return plan
