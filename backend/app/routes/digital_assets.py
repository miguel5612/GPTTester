from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .. import models, schemas, deps
from .clients import require_service_manager

router = APIRouter(prefix="/digitalassets", tags=["digitalassets"])


@router.post("/", response_model=schemas.DigitalAsset)
def create_digital_asset(
    asset: schemas.DigitalAsset,
    db: Session = Depends(deps.get_db),
    _: models.User = Depends(require_service_manager),
):
    client = db.query(models.Client).filter_by(id=asset.clientId, is_active=True).first()
    if not client:
        raise HTTPException(status_code=400, detail="Client not found or inactive")
    db_obj = models.DigitalAsset(**asset.dict())
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


@router.get("/", response_model=list[schemas.DigitalAsset])
def list_digital_assets(db: Session = Depends(deps.get_db)):
    return db.query(models.DigitalAsset).all()


@router.get("/{asset_id}", response_model=schemas.DigitalAsset)
def get_digital_asset(asset_id: int, db: Session = Depends(deps.get_db)):
    obj = db.query(models.DigitalAsset).filter_by(id=asset_id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="Not found")
    return obj


@router.put("/{asset_id}", response_model=schemas.DigitalAsset)
def update_digital_asset(
    asset_id: int,
    asset: schemas.DigitalAsset,
    db: Session = Depends(deps.get_db),
    _: models.User = Depends(require_service_manager),
):
    db_obj = db.query(models.DigitalAsset).filter_by(id=asset_id).first()
    if not db_obj:
        raise HTTPException(status_code=404, detail="Not found")
    client = db.query(models.Client).filter_by(id=asset.clientId, is_active=True).first()
    if not client:
        raise HTTPException(status_code=400, detail="Client not found or inactive")
    data = asset.dict()
    for k, v in data.items():
        setattr(db_obj, k, v)
    db.commit()
    db.refresh(db_obj)
    return db_obj


@router.delete("/{asset_id}")
def delete_digital_asset(
    asset_id: int,
    db: Session = Depends(deps.get_db),
    _: models.User = Depends(require_service_manager),
):
    obj = db.query(models.DigitalAsset).filter_by(id=asset_id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="Not found")
    db.delete(obj)
    db.commit()
    return {"ok": True}
