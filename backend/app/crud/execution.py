from datetime import datetime
from sqlalchemy.orm import Session
from .. import models

PENDING_STATUS = "Llamando al agente"


def get_pending_execution_by_agent(db: Session, agent_id: int):
    return (
        db.query(models.Execution)
        .filter(models.Execution.agent_id == agent_id)
        .filter(models.Execution.status == PENDING_STATUS)
        .first()
    )


def create_execution(db: Session, plan: models.ExecutionPlan):
    execution = models.Execution(plan_id=plan.id, agent_id=plan.agent_id)
    db.add(execution)
    db.commit()
    db.refresh(execution)
    return execution


def get_execution(db: Session, execution_id: int):
    return db.query(models.Execution).filter(models.Execution.id == execution_id).first()


def save_execution_report(db: Session, execution_id: int, path: str):
    execution = get_execution(db, execution_id)
    if execution:
        execution.report_file = path
        execution.report_received_at = datetime.utcnow()
        db.commit()
        db.refresh(execution)
    return execution

