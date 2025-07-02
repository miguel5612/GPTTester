from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .. import models, schemas, deps
from .clients import require_service_manager

router = APIRouter(prefix="/projects", tags=["projects"])

MAX_DEDICATION_HOURS = 40


@router.post("/", response_model=schemas.Project)
def create_project(
    project: schemas.Project,
    db: Session = Depends(deps.get_db),
    _: models.User = Depends(require_service_manager),
):
    asset = db.query(models.DigitalAsset).filter_by(id=project.digitalAssetsId).first()
    if not asset:
        raise HTTPException(status_code=400, detail="Digital asset not found")
    client = db.query(models.Client).filter_by(id=asset.clientId, is_active=True).first()
    if not client:
        raise HTTPException(status_code=400, detail="Client inactive")
    db_obj = models.Project(**project.dict())
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


@router.get("/", response_model=list[schemas.Project])
def list_projects(
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user),
):
    if current_user.role.name in ["Analista de Pruebas con skill de automatización", "Automatizador de Pruebas"]:
        projs = (
            db.query(models.Project)
            .join(models.ProjectEmployee, models.Project.id == models.ProjectEmployee.projectId)
            .filter(models.ProjectEmployee.userId == current_user.id)
            .all()
        )
        return projs
    return db.query(models.Project).all()


@router.get("/{project_id}", response_model=schemas.Project)
def get_project(project_id: int, db: Session = Depends(deps.get_db)):
    obj = db.query(models.Project).filter_by(id=project_id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="Not found")
    return obj


@router.put("/{project_id}", response_model=schemas.Project)
def update_project(
    project_id: int,
    project: schemas.Project,
    db: Session = Depends(deps.get_db),
    _: models.User = Depends(require_service_manager),
):
    db_obj = db.query(models.Project).filter_by(id=project_id).first()
    if not db_obj:
        raise HTTPException(status_code=404, detail="Not found")
    asset = db.query(models.DigitalAsset).filter_by(id=project.digitalAssetsId).first()
    if not asset:
        raise HTTPException(status_code=400, detail="Digital asset not found")
    client = db.query(models.Client).filter_by(id=asset.clientId, is_active=True).first()
    if not client:
        raise HTTPException(status_code=400, detail="Client inactive")
    data = project.dict()
    for k, v in data.items():
        setattr(db_obj, k, v)
    db.commit()
    db.refresh(db_obj)
    return db_obj


@router.delete("/{project_id}")
def delete_project(
    project_id: int,
    db: Session = Depends(deps.get_db),
    _: models.User = Depends(require_service_manager),
):
    obj = db.query(models.Project).filter_by(id=project_id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="Not found")
    obj.is_active = False
    db.commit()
    return {"ok": True}


@router.post("/{project_id}/analysts/{user_id}")
def assign_analyst(
    project_id: int,
    user_id: int,
    data: schemas.ProjectEmployee,
    db: Session = Depends(deps.get_db),
    _: models.User = Depends(require_service_manager),
):
    project = db.query(models.Project).filter_by(id=project_id).first()
    user = db.query(models.User).filter_by(id=user_id, is_active=True).first()
    if not project or not user:
        raise HTTPException(status_code=404, detail="Not found")
    current_hours = (
        db.query(models.ProjectEmployee)
        .filter(models.ProjectEmployee.userId == user_id)
        .with_entities(models.ProjectEmployee.dedicationHours)
        .all()
    )
    total = sum(h[0] or 0 for h in current_hours) + (data.dedicationHours or 0)
    if total > MAX_DEDICATION_HOURS:
        raise HTTPException(status_code=400, detail="Dedication exceeded")
    db_obj = models.ProjectEmployee(
        projectId=project_id,
        userId=user_id,
        objective=data.objective,
        dedicationHours=data.dedicationHours,
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


@router.delete("/{project_id}/analysts/{user_id}")
def remove_analyst(
    project_id: int,
    user_id: int,
    db: Session = Depends(deps.get_db),
    _: models.User = Depends(require_service_manager),
):
    obj = (
        db.query(models.ProjectEmployee)
        .filter_by(projectId=project_id, userId=user_id)
        .first()
    )
    if not obj:
        raise HTTPException(status_code=404, detail="Not found")
    db.delete(obj)
    db.commit()
    return {"ok": True}
