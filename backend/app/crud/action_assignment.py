from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from .. import models, schemas


def get_assignments(db: Session, test_id: int | None = None):
    query = db.query(models.ActionAssignment)
    if test_id is not None:
        query = query.filter(models.ActionAssignment.test_id == test_id)
    return query.all()


def get_assignment(db: Session, assignment_id: int):
    return (
        db.query(models.ActionAssignment)
        .filter(models.ActionAssignment.id == assignment_id)
        .first()
    )


def create_assignment(
    db: Session, assignment: schemas.action_assignment.ActionAssignmentCreate
):
    db_assignment = models.ActionAssignment(**assignment.dict())
    db.add(db_assignment)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        return None
    db.refresh(db_assignment)
    return db_assignment


def update_assignment(
    db: Session, assignment_id: int, assignment: schemas.action_assignment.ActionAssignmentUpdate
):
    db_assignment = get_assignment(db, assignment_id)
    if db_assignment:
        for field, value in assignment.dict(exclude_unset=True).items():
            setattr(db_assignment, field, value)
        try:
            db.commit()
        except IntegrityError:
            db.rollback()
            return None
        db.refresh(db_assignment)
    return db_assignment


def delete_assignment(db: Session, assignment_id: int):
    db_assignment = get_assignment(db, assignment_id)
    if db_assignment:
        db.delete(db_assignment)
        db.commit()
    return db_assignment
