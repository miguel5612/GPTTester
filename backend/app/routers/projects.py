from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from ..database import get_db
from .. import schemas
from ..crud import project as crud_project
from ..crud import user as crud_user
from ..utils import get_current_user, require_role

router = APIRouter(prefix="/projects", tags=["projects"])


def _is_admin(user: schemas.user.User) -> bool:
    return any(role.name == "Administrador" for role in user.roles)


@router.post("/", response_model=schemas.project.Project, status_code=201)
def create_project(
    project: schemas.project.ProjectCreate,
    db: Session = Depends(get_db),
    current_user: schemas.user.User = Depends(require_role("Administrador")),
):
    return crud_project.create_project(db, project)


@router.get("/", response_model=List[schemas.project.Project])
def read_projects(
    db: Session = Depends(get_db),
    current_user: schemas.user.User = Depends(get_current_user),
):
    if _is_admin(current_user):
        return crud_project.get_projects(db)
    return crud_project.get_projects_for_user(db, current_user.id)


@router.get("/{project_id}", response_model=schemas.project.Project)
def read_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.user.User = Depends(get_current_user),
):
    project = crud_project.get_project(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    if not _is_admin(current_user) and current_user not in project.analysts:
        raise HTTPException(status_code=403, detail="Operation not permitted")
    return project


@router.put("/{project_id}", response_model=schemas.project.Project)
def update_project(
    project_id: int,
    project: schemas.project.ProjectUpdate,
    db: Session = Depends(get_db),
    current_user: schemas.user.User = Depends(require_role("Administrador")),
):
    db_project = crud_project.update_project(db, project_id, project)
    if not db_project:
        raise HTTPException(status_code=404, detail="Project not found")
    return db_project


@router.post("/{project_id}/analysts/{user_id}", response_model=schemas.project.Project)
def add_analyst_to_project(
    project_id: int,
    user_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.user.User = Depends(require_role("Administrador")),
):
    user = crud_user.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    project = crud_project.add_analyst(db, project_id, user)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.delete("/{project_id}/analysts/{user_id}", response_model=schemas.project.Project)
def remove_analyst_from_project(
    project_id: int,
    user_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.user.User = Depends(require_role("Administrador")),
):
    user = crud_user.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    project = crud_project.remove_analyst(db, project_id, user)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project
