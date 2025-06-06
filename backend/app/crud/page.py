from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from .. import models, schemas


def get_pages(db: Session):
    return db.query(models.Page).all()


def get_page(db: Session, page_id: int):
    return db.query(models.Page).filter(models.Page.id == page_id).first()


def create_page(db: Session, page: schemas.page.PageCreate):
    db_page = models.Page(**page.dict())
    db.add(db_page)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        return None
    db.refresh(db_page)
    return db_page


def update_page(db: Session, page_id: int, page: schemas.page.PageUpdate):
    db_page = get_page(db, page_id)
    if db_page:
        for field, value in page.dict(exclude_unset=True).items():
            setattr(db_page, field, value)
        try:
            db.commit()
        except IntegrityError:
            db.rollback()
            return None
        db.refresh(db_page)
    return db_page


def delete_page(db: Session, page_id: int):
    db_page = get_page(db, page_id)
    if db_page:
        db.delete(db_page)
        db.commit()
    return db_page
