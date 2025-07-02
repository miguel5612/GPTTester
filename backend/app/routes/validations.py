from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .. import models, schemas, deps

router = APIRouter(prefix="/validations", tags=["validations"])
perm = lambda method: Depends(deps.require_api_permission("/validations", method))

@router.post("/", response_model=schemas.Validation, status_code=status.HTTP_201_CREATED, dependencies=[perm("POST")])
def create_validation(data: schemas.ValidationCreate, db: Session = Depends(deps.get_db)):
    if db.query(models.Validation).filter_by(code=data.code).first():
        raise HTTPException(status_code=400, detail="Code exists")
    obj = models.Validation(**data.dict())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj

@router.get("/", response_model=list[schemas.Validation], dependencies=[perm("GET")])
def list_validations(db: Session = Depends(deps.get_db)):
    return db.query(models.Validation).all()

@router.get("/{validation_id}", response_model=schemas.Validation, dependencies=[perm("GET")])
def get_validation(validation_id: int, db: Session = Depends(deps.get_db)):
    obj = db.query(models.Validation).filter_by(id=validation_id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="Not found")
    return obj

@router.put("/{validation_id}", response_model=schemas.Validation, dependencies=[perm("PUT")])
def update_validation(validation_id: int, data: schemas.ValidationUpdate, db: Session = Depends(deps.get_db)):
    obj = db.query(models.Validation).filter_by(id=validation_id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="Not found")
    for field, value in data.dict(exclude_unset=True).items():
        setattr(obj, field, value)
    db.commit()
    db.refresh(obj)
    return obj

@router.delete("/{validation_id}", dependencies=[perm("DELETE")])
def delete_validation(validation_id: int, db: Session = Depends(deps.get_db)):
    obj = db.query(models.Validation).filter_by(id=validation_id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="Not found")
    db.delete(obj)
    db.commit()
    return {"ok": True}

# ------------------ Parameters ------------------
param_router = APIRouter(prefix="/validationparameters", tags=["validationparameters"])
param_perm = lambda method: Depends(deps.require_api_permission("/validationparameters", method))

@param_router.post("/", response_model=schemas.ValidationParameter, status_code=status.HTTP_201_CREATED, dependencies=[param_perm("POST")])
def create_val_parameter(data: schemas.ValidationParameterCreate, db: Session = Depends(deps.get_db)):
    if not db.query(models.Validation).filter_by(id=data.interactionId).first():
        raise HTTPException(status_code=404, detail="Validation not found")
    obj = models.ValidationParameter(**data.dict())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj

@param_router.get("/", response_model=list[schemas.ValidationParameter], dependencies=[param_perm("GET")])
def list_val_parameters(db: Session = Depends(deps.get_db)):
    return db.query(models.ValidationParameter).all()

@param_router.get("/{parameter_id}", response_model=schemas.ValidationParameter, dependencies=[param_perm("GET")])
def get_val_parameter(parameter_id: int, db: Session = Depends(deps.get_db)):
    obj = db.query(models.ValidationParameter).filter_by(id=parameter_id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="Not found")
    return obj

@param_router.put("/{parameter_id}", response_model=schemas.ValidationParameter, dependencies=[param_perm("PUT")])
def update_val_parameter(parameter_id: int, data: schemas.ValidationParameterUpdate, db: Session = Depends(deps.get_db)):
    obj = db.query(models.ValidationParameter).filter_by(id=parameter_id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="Not found")
    for field, value in data.dict(exclude_unset=True).items():
        setattr(obj, field, value)
    db.commit()
    db.refresh(obj)
    return obj

@param_router.delete("/{parameter_id}", dependencies=[param_perm("DELETE")])
def delete_val_parameter(parameter_id: int, db: Session = Depends(deps.get_db)):
    obj = db.query(models.ValidationParameter).filter_by(id=parameter_id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="Not found")
    db.delete(obj)
    db.commit()
    return {"ok": True}

# ------------------ Approvals ------------------
approval_router = APIRouter(prefix="/validationapprovals", tags=["validationapprovals"])
approval_perm = lambda method: Depends(deps.require_api_permission("/validationapprovals", method))

@approval_router.post("/", response_model=schemas.ValidationApproval, status_code=status.HTTP_201_CREATED, dependencies=[approval_perm("POST")])
def create_val_approval(data: schemas.ValidationApprovalCreate, db: Session = Depends(deps.get_db)):
    validation = db.query(models.Validation).filter_by(id=data.validationId).first()
    if not validation:
        raise HTTPException(status_code=404, detail="Validation not found")
    state = db.query(models.InteractionApprovalState).filter_by(id=data.interactionAprovalStateId).first()
    if not state:
        raise HTTPException(status_code=400, detail="Invalid state")

    approved = db.query(models.InteractionApprovalState).filter_by(name="aprobado").first()
    rejected = db.query(models.InteractionApprovalState).filter_by(name="rechazado").first()
    existing = (
        db.query(models.ValidationApproval)
        .filter(models.ValidationApproval.validationId == data.validationId)
        .filter(models.ValidationApproval.interactionAprovalStateId.in_([approved.id, rejected.id]))
        .first()
    )
    if existing:
        raise HTTPException(status_code=400, detail="Validation already closed")

    obj = models.ValidationApproval(
        validationId=data.validationId,
        creatorId=data.creatorId,
        aprovalUserId=data.aprovalUserId,
        comment=data.comment,
        interactionAprovalStateId=data.interactionAprovalStateId,
        creationDate=datetime.utcnow(),
    )
    if data.interactionAprovalStateId in [approved.id, rejected.id]:
        obj.aprovalDate = datetime.utcnow()
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj

@approval_router.get("/", response_model=list[schemas.ValidationApproval], dependencies=[approval_perm("GET")])
def list_val_approvals(db: Session = Depends(deps.get_db)):
    return db.query(models.ValidationApproval).all()

@approval_router.get("/{approval_id}", response_model=schemas.ValidationApproval, dependencies=[approval_perm("GET")])
def get_val_approval(approval_id: int, db: Session = Depends(deps.get_db)):
    obj = db.query(models.ValidationApproval).filter_by(id=approval_id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="Not found")
    return obj
