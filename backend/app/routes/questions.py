from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import models, schemas, deps
from ..crud import create_crud_router

router = create_crud_router("questions", models.Question, schemas.Question)

perm_qv = lambda m: Depends(deps.require_api_permission("/questionhasvalidations", m))


@router.get("/{question_id}/validations", dependencies=[perm_qv("GET")])
def list_question_validations(question_id: int, db: Session = Depends(deps.get_db)):
    if not db.query(models.Question).filter_by(id=question_id).first():
        raise HTTPException(status_code=404, detail="Question not found")
    links = (
        db.query(models.QuestionHasValidation).filter_by(questionId=question_id).all()
    )
    return links


@router.post(
    "/{question_id}/validations/{validation_id}",
    response_model=schemas.QuestionHasValidation,
    dependencies=[perm_qv("POST")],
)
def add_question_validation(
    question_id: int, validation_id: int, db: Session = Depends(deps.get_db)
):
    question = db.query(models.Question).filter_by(id=question_id).first()
    validation = db.query(models.Validation).filter_by(id=validation_id).first()
    if not question or not validation:
        raise HTTPException(status_code=404, detail="Question or validation not found")
    existing = (
        db.query(models.QuestionHasValidation)
        .filter_by(questionId=question_id, validationId=validation_id)
        .first()
    )
    if existing:
        raise HTTPException(status_code=409, detail="Relation already exists")
    obj = models.QuestionHasValidation(
        questionId=question_id, validationId=validation_id
    )
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete(
    "/{question_id}/validations/{validation_id}", dependencies=[perm_qv("DELETE")]
)
def remove_question_validation(
    question_id: int, validation_id: int, db: Session = Depends(deps.get_db)
):
    link = (
        db.query(models.QuestionHasValidation)
        .filter_by(questionId=question_id, validationId=validation_id)
        .first()
    )
    if not link:
        raise HTTPException(status_code=404, detail="Relation not found")
    db.delete(link)
    db.commit()
    return {"ok": True}
