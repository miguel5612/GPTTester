from sqlalchemy.orm import Session
from .. import models, schemas


def get_execution_plans(db: Session, nombre: str = None, test_id: int = None, agent_id: int = None):
    query = db.query(models.ExecutionPlan)
    if nombre:
        query = query.filter(models.ExecutionPlan.nombre.ilike(f"%{nombre}%"))
    if test_id:
        query = query.filter(models.ExecutionPlan.test_id == test_id)
    if agent_id:
        query = query.filter(models.ExecutionPlan.agent_id == agent_id)
    return query.all()


def get_execution_plan(db: Session, plan_id: int):
    return db.query(models.ExecutionPlan).filter(models.ExecutionPlan.id == plan_id).first()


def create_execution_plan(db: Session, plan: schemas.execution_plan.ExecutionPlanCreate):
    db_plan = models.ExecutionPlan(**plan.dict())
    db.add(db_plan)
    db.commit()
    db.refresh(db_plan)
    return db_plan


def update_execution_plan(db: Session, plan_id: int, plan: schemas.execution_plan.ExecutionPlanUpdate):
    db_plan = get_execution_plan(db, plan_id)
    if db_plan:
        for field, value in plan.dict(exclude_unset=True).items():
            setattr(db_plan, field, value)
        db.commit()
        db.refresh(db_plan)
    return db_plan


def delete_execution_plan(db: Session, plan_id: int):
    db_plan = get_execution_plan(db, plan_id)
    if db_plan:
        db.delete(db_plan)
        db.commit()
    return db_plan
