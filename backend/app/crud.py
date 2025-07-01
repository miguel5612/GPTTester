from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Type, List

from . import models, deps


def create_crud_router(prefix: str, model: Type[models.Base], schema: Type):
    router = APIRouter(prefix=f"/{prefix}", tags=[prefix])

    @router.post("/", response_model=schema)
    def create(item: schema, db: Session = Depends(deps.get_db)):
        data = item.dict()
        if model is models.User:
            data["password"] = deps.get_password_hash(data["password"])
        db_obj = model(**data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    @router.get("/", response_model=List[schema])
    def read_all(db: Session = Depends(deps.get_db)):
        return db.query(model).all()

    @router.get("/{item_id}", response_model=schema)
    def read_one(item_id: int, db: Session = Depends(deps.get_db)):
        db_obj = db.query(model).filter(model.id == item_id).first()
        if not db_obj:
            raise HTTPException(status_code=404, detail="Not found")
        return db_obj

    @router.put("/{item_id}", response_model=schema)
    def update(item_id: int, item: schema, db: Session = Depends(deps.get_db)):
        db_obj = db.query(model).filter(model.id == item_id).first()
        if not db_obj:
            raise HTTPException(status_code=404, detail="Not found")
        data = item.dict()
        if model is models.User and "password" in data:
            data["password"] = deps.get_password_hash(data["password"])
        for field, value in data.items():
            setattr(db_obj, field, value)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    @router.delete("/{item_id}")
    def delete(item_id: int, db: Session = Depends(deps.get_db)):
        db_obj = db.query(model).filter(model.id == item_id).first()
        if not db_obj:
            raise HTTPException(status_code=404, detail="Not found")
        db.delete(db_obj)
        db.commit()
        return {"ok": True}

    return router
