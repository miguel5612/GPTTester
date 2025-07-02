from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import models, schemas, deps
from ..crud import create_crud_router

router = create_crud_router("tasks", models.Task, schemas.Task)

perm_ti = lambda m: Depends(deps.require_api_permission("/taskhaveinteractions", m))


@router.get("/{task_id}/interactions", dependencies=[perm_ti("GET")])
def list_task_interactions(task_id: int, db: Session = Depends(deps.get_db)):
    if not db.query(models.Task).filter_by(id=task_id).first():
        raise HTTPException(status_code=404, detail="Task not found")
    links = db.query(models.TaskHaveInteraction).filter_by(taskId=task_id).all()
    return links


@router.post(
    "/{task_id}/interactions/{interaction_id}",
    response_model=schemas.TaskHaveInteraction,
    dependencies=[perm_ti("POST")],
)
def add_task_interaction(
    task_id: int, interaction_id: int, db: Session = Depends(deps.get_db)
):
    task = db.query(models.Task).filter_by(id=task_id).first()
    interaction = db.query(models.Interaction).filter_by(id=interaction_id).first()
    if not task or not interaction:
        raise HTTPException(status_code=404, detail="Task or interaction not found")
    existing = (
        db.query(models.TaskHaveInteraction)
        .filter_by(taskId=task_id, interactionId=interaction_id)
        .first()
    )
    if existing:
        raise HTTPException(status_code=409, detail="Relation already exists")
    obj = models.TaskHaveInteraction(taskId=task_id, interactionId=interaction_id)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete(
    "/{task_id}/interactions/{interaction_id}", dependencies=[perm_ti("DELETE")]
)
def remove_task_interaction(
    task_id: int, interaction_id: int, db: Session = Depends(deps.get_db)
):
    link = (
        db.query(models.TaskHaveInteraction)
        .filter_by(taskId=task_id, interactionId=interaction_id)
        .first()
    )
    if not link:
        raise HTTPException(status_code=404, detail="Relation not found")
    db.delete(link)
    db.commit()
    return {"ok": True}
