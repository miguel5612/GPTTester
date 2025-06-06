from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from ..database import get_db
from .. import schemas
from ..crud import agent as crud_agent
from ..utils import get_current_user, require_role

router = APIRouter(prefix="/agents", tags=["agents"])


@router.post("/", response_model=schemas.agent.Agent, status_code=201)
def create_agent(
    agent: schemas.agent.AgentCreate,
    db: Session = Depends(get_db),
    current_user: schemas.user.User = Depends(require_role("Administrador")),
):
    if crud_agent.get_agent_by_hostname(db, agent.hostname):
        raise HTTPException(status_code=400, detail="Hostname already registered")
    db_agent = crud_agent.create_agent(db, agent)
    if not db_agent:
        raise HTTPException(status_code=400, detail="Integrity error")
    return db_agent


@router.get("/", response_model=List[schemas.agent.Agent])
def read_agents(
    db: Session = Depends(get_db),
    current_user: schemas.user.User = Depends(get_current_user),
):
    return crud_agent.get_agents(db)


@router.get("/{agent_id}", response_model=schemas.agent.Agent)
def read_agent(
    agent_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.user.User = Depends(get_current_user),
):
    ag = crud_agent.get_agent(db, agent_id)
    if not ag:
        raise HTTPException(status_code=404, detail="Agent not found")
    return ag


@router.put("/{agent_id}", response_model=schemas.agent.Agent)
def update_agent(
    agent_id: int,
    agent: schemas.agent.AgentUpdate,
    db: Session = Depends(get_db),
    current_user: schemas.user.User = Depends(require_role("Administrador")),
):
    db_agent = crud_agent.update_agent(db, agent_id, agent)
    if not db_agent:
        raise HTTPException(status_code=404, detail="Agent not found or duplicate")
    return db_agent


@router.delete("/{agent_id}", response_model=schemas.agent.Agent)
def delete_agent(
    agent_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.user.User = Depends(require_role("Administrador")),
):
    ag = crud_agent.delete_agent(db, agent_id)
    if not ag:
        raise HTTPException(status_code=404, detail="Agent not found")
    return ag
