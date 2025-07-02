import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Type, List, Optional

from . import models, deps, crypto


logger = logging.getLogger(__name__)


def create_crud_router(prefix: str, model: Type[models.Base], schema: Type):
    router = APIRouter(prefix=f"/{prefix}", tags=[prefix])

    def perm(method: str):
        return Depends(deps.require_api_permission(f"/{prefix}", method))

    def _validate_dedication(user_id: int, hours: int, db: Session, exclude_id: Optional[int] = None) -> None:
        """Ensure a user is not assigned more than 9 hours across projects."""
        if user_id is None or hours is None:
            return
        q = db.query(func.sum(models.ProjectEmployee.dedicationHours)).filter(models.ProjectEmployee.userId == user_id)
        if exclude_id is not None:
            q = q.filter(models.ProjectEmployee.id != exclude_id)
        total = q.scalar() or 0
        if total + hours > 9:
            raise HTTPException(status_code=400, detail="dedication hours exceed daily limit of 9")

    @router.post("/", response_model=schema, dependencies=[perm("POST")])
    def create(item: schema, db: Session = Depends(deps.get_db)):
        data = item.dict()
        if model is models.User:
            data["password"] = deps.get_password_hash(data["password"])
        if model is models.RawData and data.get("fieldValue") is not None:
            data["fieldValue"] = crypto.encrypt(data["fieldValue"])
        if model is models.ProjectEmployee:
            _validate_dedication(
                data.get("userId"),
                data.get("dedicationHours") or 0,
                db,
            )
        logger.debug("Creating %s with data: %s", model.__name__, data)
        db_obj = model(**data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        if model is models.RawData and db_obj.fieldValue is not None:
            db_obj.fieldValue = crypto.decrypt(db_obj.fieldValue)
        return db_obj

    @router.get("/", response_model=List[schema], dependencies=[perm("GET")])
    def read_all(db: Session = Depends(deps.get_db)):
        objs = db.query(model).all()
        if model is models.RawData:
            for o in objs:
                if o.fieldValue is not None:
                    o.fieldValue = crypto.decrypt(o.fieldValue)
        return objs

    @router.get("/{item_id}", response_model=schema, dependencies=[perm("GET")])
    def read_one(item_id: int, db: Session = Depends(deps.get_db)):
        db_obj = db.query(model).filter(model.id == item_id).first()
        if not db_obj:
            raise HTTPException(status_code=404, detail="Not found")
        if model is models.RawData and db_obj.fieldValue is not None:
            db_obj.fieldValue = crypto.decrypt(db_obj.fieldValue)
        return db_obj

    @router.put("/{item_id}", response_model=schema, dependencies=[perm("PUT")])
    def update(item_id: int, item: schema, db: Session = Depends(deps.get_db)):
        db_obj = db.query(model).filter(model.id == item_id).first()
        if not db_obj:
            raise HTTPException(status_code=404, detail="Not found")
        data = item.dict()
        if model is models.User and "password" in data:
            data["password"] = deps.get_password_hash(data["password"])
        if model is models.RawData and "fieldValue" in data and data["fieldValue"] is not None:
            data["fieldValue"] = crypto.encrypt(data["fieldValue"])
        if model is models.ProjectEmployee:
            _validate_dedication(
                data.get("userId", db_obj.userId),
                data.get("dedicationHours", db_obj.dedicationHours) or 0,
                db,
                exclude_id=item_id,
            )
        for field, value in data.items():
            setattr(db_obj, field, value)
        logger.debug("Updating %s %s with data: %s", model.__name__, item_id, data)
        db.commit()
        db.refresh(db_obj)
        if model is models.RawData and db_obj.fieldValue is not None:
            db_obj.fieldValue = crypto.decrypt(db_obj.fieldValue)
        return db_obj

    @router.delete("/{item_id}", dependencies=[perm("DELETE")])
    def delete(item_id: int, db: Session = Depends(deps.get_db)):
        db_obj = db.query(model).filter(model.id == item_id).first()
        if not db_obj:
            raise HTTPException(status_code=404, detail="Not found")
        db.delete(db_obj)
        db.commit()
        logger.debug("Deleted %s %s", model.__name__, item_id)
        return {"ok": True}

    return router
