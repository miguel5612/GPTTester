from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from .. import models, schemas


def get_scenarios(db: Session):
    return db.query(models.Scenario).all()


def get_scenario(db: Session, scenario_id: int):
    return db.query(models.Scenario).filter(models.Scenario.id == scenario_id).first()


def create_scenario(db: Session, scenario: schemas.scenario.ScenarioCreate):
    db_sc = models.Scenario(**scenario.dict())
    db.add(db_sc)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        return None
    db.refresh(db_sc)
    return db_sc


def update_scenario(db: Session, scenario_id: int, scenario: schemas.scenario.ScenarioUpdate):
    db_sc = get_scenario(db, scenario_id)
    if db_sc:
        for field, value in scenario.dict(exclude_unset=True).items():
            setattr(db_sc, field, value)
        try:
            db.commit()
        except IntegrityError:
            db.rollback()
            return None
        db.refresh(db_sc)
    return db_sc


def delete_scenario(db: Session, scenario_id: int):
    db_sc = get_scenario(db, scenario_id)
    if db_sc:
        db.delete(db_sc)
        db.commit()
    return db_sc
