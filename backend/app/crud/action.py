from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from .. import models, schemas


def get_actions(db: Session):
    return db.query(models.Action).all()


def get_action(db: Session, action_id: int):
    return db.query(models.Action).filter(models.Action.id == action_id).first()


def create_action(db: Session, action: schemas.action.ActionCreate):
    db_action = models.Action(**action.dict())
    db.add(db_action)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        return None
    db.refresh(db_action)
    return db_action


def update_action(db: Session, action_id: int, action: schemas.action.ActionUpdate):
    db_action = get_action(db, action_id)
    if db_action:
        for field, value in action.dict(exclude_unset=True).items():
            setattr(db_action, field, value)
        try:
            db.commit()
        except IntegrityError:
            db.rollback()
            return None
        db.refresh(db_action)
    return db_action


def delete_action(db: Session, action_id: int):
    db_action = get_action(db, action_id)
    if db_action:
        db.delete(db_action)
        db.commit()
    return db_action
