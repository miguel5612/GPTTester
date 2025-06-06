from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from .. import models, schemas


def get_testplans(db: Session):
    return db.query(models.TestPlan).all()


def get_testplan(db: Session, testplan_id: int):
    return db.query(models.TestPlan).filter(models.TestPlan.id == testplan_id).first()


def get_testplan_by_nombre(db: Session, nombre: str):
    return db.query(models.TestPlan).filter(models.TestPlan.nombre == nombre).first()


def create_testplan(db: Session, tp: schemas.testplan.TestPlanCreate):
    db_tp = models.TestPlan(**tp.dict())
    db.add(db_tp)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        return None
    db.refresh(db_tp)
    return db_tp


def update_testplan(db: Session, testplan_id: int, tp: schemas.testplan.TestPlanUpdate):
    db_tp = get_testplan(db, testplan_id)
    if db_tp:
        for field, value in tp.dict(exclude_unset=True).items():
            setattr(db_tp, field, value)
        try:
            db.commit()
        except IntegrityError:
            db.rollback()
            return None
        db.refresh(db_tp)
    return db_tp


def delete_testplan(db: Session, testplan_id: int):
    db_tp = get_testplan(db, testplan_id)
    if db_tp:
        db.delete(db_tp)
        db.commit()
    return db_tp
