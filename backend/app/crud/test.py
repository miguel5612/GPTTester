from sqlalchemy.orm import Session
from .. import models, schemas


def create_test(db: Session, test: schemas.TestCreate, user_id: int):
    db_test = models.Test(**test.dict(), owner_id=user_id)
    db.add(db_test)
    db.commit()
    db.refresh(db_test)
    return db_test


def get_tests(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Test).offset(skip).limit(limit).all()


def get_test(db: Session, test_id: int):
    return db.query(models.Test).filter(models.Test.id == test_id).first()


def delete_test(db: Session, test_id: int):
    test = get_test(db, test_id)
    if test:
        db.delete(test)
        db.commit()
    return test
