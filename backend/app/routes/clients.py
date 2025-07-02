from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .. import models, schemas, deps

router = APIRouter(prefix="/clients", tags=["clients"])


# Dependency to require Service Manager role

def require_service_manager(
    current_user: models.User = Depends(deps.get_current_user),
):
    if current_user.role.name != "Gerente de servicios" and current_user.role.name != "Administrador":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Manager only")
    return current_user


@router.post("/", response_model=schemas.Client)
def create_client(
    client: schemas.Client,
    db: Session = Depends(deps.get_db),
    _: models.User = Depends(require_service_manager),
):
    if not client.name or not client.mision or not client.vision:
        raise HTTPException(status_code=400, detail="Missing required fields")
    db_obj = models.Client(**client.dict())
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


@router.get("/", response_model=list[schemas.Client])
def list_clients(
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user),
):
    if current_user.role.name in ["Analista de Pruebas con skill de automatización", "Automatizador de Pruebas"]:
        projects = (
            db.query(models.Project)
            .join(models.ProjectEmployee, models.Project.id == models.ProjectEmployee.projectId)
            .filter(models.ProjectEmployee.userId == current_user.id)
            .all()
        )
        client_ids = {p.digitalAssetsId for p in projects}
        # map digital asset -> client
        assets = db.query(models.DigitalAsset).filter(models.DigitalAsset.id.in_(client_ids)).all()
        allowed_clients = {a.clientId for a in assets}
        return db.query(models.Client).filter(models.Client.id.in_(allowed_clients)).all()
    return db.query(models.Client).all()


@router.get("/{client_id}", response_model=schemas.Client)
def get_client(client_id: int, db: Session = Depends(deps.get_db)):
    obj = db.query(models.Client).filter_by(id=client_id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="Not found")
    return obj


@router.put("/{client_id}", response_model=schemas.Client)
def update_client(
    client_id: int,
    client: schemas.Client,
    db: Session = Depends(deps.get_db),
    _: models.User = Depends(require_service_manager),
):
    db_obj = db.query(models.Client).filter_by(id=client_id).first()
    if not db_obj:
        raise HTTPException(status_code=404, detail="Not found")
    data = client.dict()
    for k, v in data.items():
        setattr(db_obj, k, v)
    db.commit()
    db.refresh(db_obj)
    return db_obj


@router.delete("/{client_id}")
def delete_client(
    client_id: int,
    db: Session = Depends(deps.get_db),
    _: models.User = Depends(require_service_manager),
):
    obj = db.query(models.Client).filter_by(id=client_id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="Not found")
    obj.is_active = False
    db.commit()
    return {"ok": True}
