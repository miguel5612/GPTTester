from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from ..database import get_db
from .. import schemas
from ..crud import test as crud_test
from ..utils import get_current_user

router = APIRouter(prefix="/tests", tags=["tests"])


@router.post("/", response_model=schemas.test.Test)
def create_test(
    test: schemas.test.TestCreate,
    db: Session = Depends(get_db),
    current_user: schemas.user.User = Depends(get_current_user),
):
    return crud_test.create_test(db, test, current_user.id)


@router.get("/", response_model=List[schemas.test.Test])
def read_tests(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: schemas.user.User = Depends(get_current_user),
):
    return crud_test.get_tests(db, skip=skip, limit=limit)


@router.delete("/{test_id}", response_model=schemas.test.Test)
def delete_test(
    test_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.user.User = Depends(get_current_user),
):
    test = crud_test.delete_test(db, test_id)
    if not test:
        raise HTTPException(status_code=404, detail="Test not found")
    return test
