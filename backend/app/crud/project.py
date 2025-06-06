from sqlalchemy.orm import Session
from .. import models, schemas


def get_projects(db: Session):
    return db.query(models.Project).all()


def get_projects_for_user(db: Session, user_id: int):
    return (
        db.query(models.Project)
        .join(models.project_analysts)
        .filter(models.project_analysts.c.user_id == user_id)
        .all()
    )


def get_project(db: Session, project_id: int):
    return db.query(models.Project).filter(models.Project.id == project_id).first()


def create_project(db: Session, project: schemas.project.ProjectCreate):
    db_project = models.Project(
        name=project.name,
        client_id=project.client_id,
        is_active=project.is_active,
    )
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project


def update_project(db: Session, project_id: int, project: schemas.project.ProjectUpdate):
    db_project = get_project(db, project_id)
    if db_project:
        db_project.name = project.name
        db_project.client_id = project.client_id
        db_project.is_active = project.is_active
        db.commit()
        db.refresh(db_project)
    return db_project


def add_analyst(db: Session, project_id: int, user: models.User):
    project = get_project(db, project_id)
    if project and user not in project.analysts:
        project.analysts.append(user)
        db.commit()
        db.refresh(project)
    return project


def remove_analyst(db: Session, project_id: int, user: models.User):
    project = get_project(db, project_id)
    if project and user in project.analysts:
        project.analysts.remove(user)
        db.commit()
        db.refresh(project)
    return project
