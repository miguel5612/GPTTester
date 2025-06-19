from __future__ import annotations

import json
from datetime import datetime

from sqlalchemy.orm import Session
from fastapi import HTTPException

from . import models


def execute_test(db: Session, test_id: int, agent_id: int) -> dict:
    """Generate execution payload for agent."""
    assignments = (
        db.query(models.ActionAssignment)
        .filter(models.ActionAssignment.test_id == test_id)
        .all()
    )
    lines = ["# Auto generated script"]
    for assign in assignments:
        params = json.loads(assign.parametros or "{}")
        lines.append(f"# {assign.action.name} -> {assign.element.name}")
        if params:
            lines.append(f"# params: {params}")
        lines.append(assign.action.codigo)
    script = "\n".join(lines)
    payload = {"test_id": test_id, "agent_id": agent_id, "script": script}
    return payload


def prepare_execution_payload(db: Session, test_id: int) -> dict:
    """Return script, context and configuration for execution."""
    base = execute_test(db, test_id, agent_id=0)
    return {"script": base["script"], "context": {}, "config": {}}


def get_available_agent(db: Session, categoria: str | None = None) -> models.ExecutionAgent | None:
    """Return first execution agent without pending tasks."""
    query = db.query(models.ExecutionAgent)
    if categoria is not None:
        query = query.filter(models.ExecutionAgent.categoria == categoria)
    agents = query.all()
    for agent in agents:
        pending = (
            db.query(models.PlanExecution)
            .filter(
                models.PlanExecution.agent_id == agent.id,
                models.PlanExecution.status.in_(
                    [
                        models.ExecutionStatus.CALLING.value,
                        models.ExecutionStatus.RUNNING.value,
                    ]
                ),
            )
            .first()
        )
        if not pending:
            return agent
    return None


def queue_execution(db: Session, test_id: int, categoria: str | None = None) -> int:
    """Create execution record using an available agent."""
    agent = get_available_agent(db, categoria)
    if not agent:
        raise HTTPException(status_code=404, detail="No available agents")

    plan = models.ExecutionPlan(
        nombre=f"Auto {datetime.utcnow().isoformat()}",
        test_id=test_id,
        agent_id=agent.id,
    )
    db.add(plan)
    db.commit()
    db.refresh(plan)

    record = models.PlanExecution(
        plan_id=plan.id,
        agent_id=agent.id,
        status=models.ExecutionStatus.CALLING.value,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record.id
