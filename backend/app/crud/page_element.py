from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from .. import models, schemas


def get_elements(db: Session, page_id: int):
    return (
        db.query(models.PageElement)
        .filter(models.PageElement.page_id == page_id)
        .all()
    )


def get_element(db: Session, element_id: int):
    return (
        db.query(models.PageElement)
        .filter(models.PageElement.id == element_id)
        .first()
    )


def create_element(
    db: Session, page_id: int, element: schemas.page_element.PageElementCreate
):
    db_element = models.PageElement(**element.dict(), page_id=page_id)
    db.add(db_element)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        return None
    db.refresh(db_element)
    return db_element


def update_element(
    db: Session, element_id: int, element: schemas.page_element.PageElementUpdate
):
    db_element = get_element(db, element_id)
    if db_element:
        for field, value in element.dict(exclude_unset=True).items():
            setattr(db_element, field, value)
        try:
            db.commit()
        except IntegrityError:
            db.rollback()
            return None
        db.refresh(db_element)
    return db_element


def delete_element(db: Session, element_id: int):
    db_element = get_element(db, element_id)
    if db_element:
        db.delete(db_element)
        db.commit()
    return db_element


def add_element_to_scenario(
    db: Session, element: models.PageElement, scenario: models.Scenario
):
    if scenario not in element.scenarios:
        element.scenarios.append(scenario)
        db.commit()
        db.refresh(element)
    return element


def remove_element_from_scenario(
    db: Session, element: models.PageElement, scenario: models.Scenario
):
    if scenario in element.scenarios:
        element.scenarios.remove(scenario)
        db.commit()
        db.refresh(element)
    return element
