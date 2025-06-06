from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from .. import models, schemas


def get_agents(db: Session):
    return db.query(models.Agent).all()


def get_agent(db: Session, agent_id: int):
    return db.query(models.Agent).filter(models.Agent.id == agent_id).first()


def get_agent_by_hostname(db: Session, hostname: str):
    return db.query(models.Agent).filter(models.Agent.hostname == hostname).first()


def create_agent(db: Session, agent: schemas.agent.AgentCreate):
    db_agent = models.Agent(**agent.dict())
    db.add(db_agent)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        return None
    db.refresh(db_agent)
    return db_agent


def update_agent(db: Session, agent_id: int, agent: schemas.agent.AgentUpdate):
    db_agent = get_agent(db, agent_id)
    if db_agent:
        for field, value in agent.dict(exclude_unset=True).items():
            setattr(db_agent, field, value)
        try:
            db.commit()
        except IntegrityError:
            db.rollback()
            return None
        db.refresh(db_agent)
    return db_agent


def delete_agent(db: Session, agent_id: int):
    db_agent = get_agent(db, agent_id)
    if db_agent:
        db.delete(db_agent)
        db.commit()
    return db_agent
