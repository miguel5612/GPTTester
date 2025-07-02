from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .. import models, schemas, deps

router = APIRouter(prefix="/interactions", tags=["interactions"])

perm = lambda method: Depends(deps.require_api_permission("/interactions", method))

@router.post("/", response_model=schemas.Interaction, status_code=status.HTTP_201_CREATED, dependencies=[perm("POST")])
def create_interaction(data: schemas.InteractionCreate, db: Session = Depends(deps.get_db)):
    if db.query(models.Interaction).filter_by(code=data.code).first():
        raise HTTPException(status_code=400, detail="Code exists")
    obj = models.Interaction(**data.dict())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj

@router.get("/", response_model=list[schemas.Interaction], dependencies=[perm("GET")])
def list_interactions(db: Session = Depends(deps.get_db)):
    return db.query(models.Interaction).all()

@router.get("/{interaction_id}", response_model=schemas.Interaction, dependencies=[perm("GET")])
def get_interaction(interaction_id: int, db: Session = Depends(deps.get_db)):
    obj = db.query(models.Interaction).filter_by(id=interaction_id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="Not found")
    return obj

@router.put("/{interaction_id}", response_model=schemas.Interaction, dependencies=[perm("PUT")])
def update_interaction(interaction_id: int, data: schemas.InteractionUpdate, db: Session = Depends(deps.get_db)):
    obj = db.query(models.Interaction).filter_by(id=interaction_id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="Not found")
    for field, value in data.dict(exclude_unset=True).items():
        setattr(obj, field, value)
    db.commit()
    db.refresh(obj)
    return obj

@router.delete("/{interaction_id}", dependencies=[perm("DELETE")])
def delete_interaction(interaction_id: int, db: Session = Depends(deps.get_db)):
    obj = db.query(models.Interaction).filter_by(id=interaction_id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="Not found")
    db.delete(obj)
    db.commit()
    return {"ok": True}

# ------------------ Parameters ------------------
param_router = APIRouter(prefix="/interactionparameters", tags=["interactionparameters"])
param_perm = lambda method: Depends(deps.require_api_permission("/interactionparameters", method))

@param_router.post("/", response_model=schemas.InteractionParameter, status_code=status.HTTP_201_CREATED, dependencies=[param_perm("POST")])
def create_parameter(data: schemas.InteractionParameterCreate, db: Session = Depends(deps.get_db)):
    if not db.query(models.Interaction).filter_by(id=data.interactionId).first():
        raise HTTPException(status_code=404, detail="Interaction not found")
    obj = models.InteractionParameter(**data.dict())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj

@param_router.get("/", response_model=list[schemas.InteractionParameter], dependencies=[param_perm("GET")])
def list_parameters(db: Session = Depends(deps.get_db)):
    return db.query(models.InteractionParameter).all()

@param_router.get("/{parameter_id}", response_model=schemas.InteractionParameter, dependencies=[param_perm("GET")])
def get_parameter(parameter_id: int, db: Session = Depends(deps.get_db)):
    obj = db.query(models.InteractionParameter).filter_by(id=parameter_id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="Not found")
    return obj

@param_router.put("/{parameter_id}", response_model=schemas.InteractionParameter, dependencies=[param_perm("PUT")])
def update_parameter(parameter_id: int, data: schemas.InteractionParameterUpdate, db: Session = Depends(deps.get_db)):
    obj = db.query(models.InteractionParameter).filter_by(id=parameter_id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="Not found")
    for field, value in data.dict(exclude_unset=True).items():
        setattr(obj, field, value)
    db.commit()
    db.refresh(obj)
    return obj

@param_router.delete("/{parameter_id}", dependencies=[param_perm("DELETE")])
def delete_parameter(parameter_id: int, db: Session = Depends(deps.get_db)):
    obj = db.query(models.InteractionParameter).filter_by(id=parameter_id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="Not found")
    db.delete(obj)
    db.commit()
    return {"ok": True}

# ------------------ Approvals ------------------
approval_router = APIRouter(prefix="/interactionapprovals", tags=["interactionapprovals"])
approval_perm = lambda method: Depends(deps.require_api_permission("/interactionapprovals", method))

@approval_router.post("/", response_model=schemas.InteractionApproval, status_code=status.HTTP_201_CREATED, dependencies=[approval_perm("POST")])
def create_approval(data: schemas.InteractionApprovalCreate, db: Session = Depends(deps.get_db)):
    interaction = db.query(models.Interaction).filter_by(id=data.interactionId).first()
    if not interaction:
        raise HTTPException(status_code=404, detail="Interaction not found")
    state = db.query(models.InteractionApprovalState).filter_by(id=data.interactionAprovalStateId).first()
    if not state:
        raise HTTPException(status_code=400, detail="Invalid state")

    approved = db.query(models.InteractionApprovalState).filter_by(name="aprobado").first()
    rejected = db.query(models.InteractionApprovalState).filter_by(name="rechazado").first()
    existing = (
        db.query(models.InteractionApproval)
        .filter(models.InteractionApproval.interactionId == data.interactionId)
        .filter(models.InteractionApproval.interactionAprovalStateId.in_([approved.id, rejected.id]))
        .first()
    )
    if existing:
        raise HTTPException(status_code=400, detail="Interaction already closed")

    obj = models.InteractionApproval(
        interactionId=data.interactionId,
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

@approval_router.get("/", response_model=list[schemas.InteractionApproval], dependencies=[approval_perm("GET")])
def list_approvals(db: Session = Depends(deps.get_db)):
    return db.query(models.InteractionApproval).all()

@approval_router.get("/{approval_id}", response_model=schemas.InteractionApproval, dependencies=[approval_perm("GET")])
def get_approval(approval_id: int, db: Session = Depends(deps.get_db)):
    obj = db.query(models.InteractionApproval).filter_by(id=approval_id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="Not found")
    return obj
