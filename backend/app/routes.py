from fastapi.security import OAuth2PasswordRequestForm
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import FileResponse
import json
from datetime import datetime
import os
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from . import models, schemas, deps, security

router = APIRouter()


@router.post("/roles/", response_model=schemas.Role)
def create_role(
    role: schemas.RoleCreate,
    db: Session = Depends(deps.get_db),
    current_user: models.User = deps.require_role(["Administrador"]),
):
    if db.query(models.Role).filter(models.Role.name == role.name).first():
        raise HTTPException(status_code=400, detail="Role already exists")
    db_role = models.Role(name=role.name)
    db.add(db_role)
    db.commit()
    db.refresh(db_role)
    return db_role


@router.get("/roles/", response_model=list[schemas.Role])
def read_roles(db: Session = Depends(deps.get_db), current_user: models.User = deps.require_role(["Administrador"])):
    return db.query(models.Role).all()


@router.put("/roles/{role_id}", response_model=schemas.Role)
def update_role(
    role_id: int,
    role: schemas.RoleCreate,
    db: Session = Depends(deps.get_db),
    current_user: models.User = deps.require_role(["Administrador"]),
):
    db_role = db.query(models.Role).filter(models.Role.id == role_id).first()
    if db_role is None:
        raise HTTPException(status_code=404, detail="Role not found")
    db_role.name = role.name
    db.commit()
    db.refresh(db_role)
    return db_role


@router.delete("/roles/{role_id}")
def delete_role(role_id: int, db: Session = Depends(deps.get_db), current_user: models.User = deps.require_role(["Administrador"])):
    db_role = db.query(models.Role).filter(models.Role.id == role_id).first()
    if db_role is None:
        raise HTTPException(status_code=404, detail="Role not found")
    db.delete(db_role)
    db.commit()
    return {"ok": True}


@router.get("/roles/{role_id}/permissions", response_model=list[schemas.Permission])
def read_role_permissions(
    role_id: int,
    db: Session = Depends(deps.get_db),
    current_user: models.User = deps.require_role(["Administrador"]),
):
    role = db.query(models.Role).filter(models.Role.id == role_id).first()
    if role is None:
        raise HTTPException(status_code=404, detail="Role not found")
    return role.permissions


@router.post("/roles/{role_id}/permissions", response_model=schemas.Permission)
def add_role_permission(
    role_id: int,
    perm: schemas.PermissionCreate,
    db: Session = Depends(deps.get_db),
    current_user: models.User = deps.require_role(["Administrador"]),
):
    if not db.query(models.Role).filter(models.Role.id == role_id).first():
        raise HTTPException(status_code=404, detail="Role not found")
    if db.query(models.PagePermission).filter(
        models.PagePermission.role_id == role_id,
        models.PagePermission.page == perm.page,
    ).first():
        raise HTTPException(status_code=400, detail="Permission already exists")
    db_perm = models.PagePermission(role_id=role_id, page=perm.page)
    db.add(db_perm)
    db.commit()
    db.refresh(db_perm)
    return db_perm


@router.delete("/roles/{role_id}/permissions/{page}")
def delete_role_permission(
    role_id: int,
    page: str,
    db: Session = Depends(deps.get_db),
    current_user: models.User = deps.require_role(["Administrador"]),
):
    perm = db.query(models.PagePermission).filter(
        models.PagePermission.role_id == role_id,
        models.PagePermission.page == page,
    ).first()
    if perm is None:
        raise HTTPException(status_code=404, detail="Permission not found")
    db.delete(perm)
    db.commit()
    return {"ok": True}

@router.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(deps.get_db)):
    try:
        security.validate_username(user.username)
        security.validate_password_strength(user.password)
    except HTTPException:
        raise

    if deps.get_user(db, username=user.username):
        raise HTTPException(status_code=400, detail="Invalid username or password")

    default_role = db.query(models.Role).filter(models.Role.name == "Analista de Pruebas con skill de automatización").first()
    hashed_password = deps.get_password_hash(user.password)
    new_user = models.User(username=user.username, hashed_password=hashed_password, role=default_role)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@router.get("/users/", response_model=list[schemas.User])
def read_users(db: Session = Depends(deps.get_db), current_user: models.User = deps.require_role(["Administrador"])):
    return db.query(models.User).all()


@router.get("/analysts/", response_model=list[schemas.User])
def read_analysts(
    search: str | None = None,
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(deps.get_db),
    current_user: models.User = deps.require_role([
        "Administrador",
        "Gerente de servicios",
    ]),
):
    analyst_roles = [
        "Analista de Pruebas con skill de automatización",
        "Automatizador de Pruebas",
    ]
    query = (
        db.query(models.User)
        .join(models.Role)
        .filter(models.Role.name.in_(analyst_roles))
    )
    if search:
        query = query.filter(models.User.username.ilike(f"%{search}%"))
    return query.offset(skip).limit(limit).all()


@router.get("/users/{user_id}", response_model=schemas.User)
def read_user(user_id: int, db: Session = Depends(deps.get_db), current_user: models.User = deps.require_role(["Administrador"])):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.put("/users/{user_id}/role", response_model=schemas.User)
def set_user_role(
    user_id: int,
    role_update: schemas.UserRoleUpdate,
    db: Session = Depends(deps.get_db),
    current_user: models.User = deps.require_role(["Administrador"]),
):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    role = db.query(models.Role).filter(models.Role.id == role_update.role_id).first()
    if role is None:
        raise HTTPException(status_code=404, detail="Role not found")
    user.role = role
    db.commit()
    db.refresh(user)
    return user


@router.put("/users/{user_id}/active", response_model=schemas.User)
def set_user_active(
    user_id: int,
    active: schemas.UserActiveUpdate,
    db: Session = Depends(deps.get_db),
    current_user: models.User = deps.require_role(["Administrador"]),
):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    if user.id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot modify your own status")
    user.is_active = active.is_active
    db.commit()
    db.refresh(user)
    return user


@router.post("/token")
def login_for_access_token(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(deps.get_db),
):
    ip = request.client.host
    try:
        security.rate_limit_login(ip)
    except HTTPException:
        raise

    user = deps.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Invalid username or password")
    user.last_login = datetime.utcnow()
    db.commit()
    token = deps.create_access_token({"sub": user.username})
    return {"access_token": token, "token_type": "bearer"}


@router.post("/clients/", response_model=schemas.Client)
def create_client(
    client: schemas.ClientCreate,
    db: Session = Depends(deps.get_db),
    current_user: models.User = deps.require_role(["Administrador", "Gerente de servicios"]),
):
    if db.query(models.Client).filter(models.Client.name == client.name).first():
        raise HTTPException(status_code=400, detail="Client already exists")
    db_client = models.Client(name=client.name)
    db.add(db_client)
    db.commit()
    db.refresh(db_client)
    return db_client


@router.get("/clients/", response_model=list[schemas.Client])
def read_clients(
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user),
):
    if current_user.role and current_user.role.name in ["Administrador", "Gerente de servicios"]:
        return db.query(models.Client).all()
    rows = (
        db.query(models.Client, models.client_analysts.c.dedication)
        .join(models.client_analysts)
        .filter(models.client_analysts.c.user_id == current_user.id)
        .all()
    )
    clients = []
    for client, dedication in rows:
        setattr(client, "dedication", dedication)
        clients.append(client)
    return clients


@router.put("/clients/{client_id}", response_model=schemas.Client)
def update_client(
    client_id: int,
    client: schemas.ClientCreate,
    db: Session = Depends(deps.get_db),
    current_user: models.User = deps.require_role(["Administrador", "Gerente de servicios"]),
):
    db_client = db.query(models.Client).filter(models.Client.id == client_id).first()
    if db_client is None:
        raise HTTPException(status_code=404, detail="Client not found")
    db_client.name = client.name
    db.commit()
    db.refresh(db_client)
    return db_client


@router.delete("/clients/{client_id}")
def delete_client(
    client_id: int,
    db: Session = Depends(deps.get_db),
    current_user: models.User = deps.require_role(["Administrador"]),
):
    db_client = db.query(models.Client).filter(models.Client.id == client_id).first()
    if db_client is None:
        raise HTTPException(status_code=404, detail="Client not found")
    db_client.is_active = False
    db.commit()
    return {"ok": True}


@router.post("/clients/{client_id}/analysts/{user_id}", response_model=schemas.Client)
def assign_client_analyst(
    client_id: int,
    user_id: int,
    dedication: int = 100,
    db: Session = Depends(deps.get_db),
    current_user: models.User = deps.require_role(["Administrador", "Gerente de servicios"]),
):
    client = db.query(models.Client).filter(models.Client.id == client_id).first()
    if client is None:
        raise HTTPException(status_code=404, detail="Client not found")
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    existing = (
        db.query(models.client_analysts)
        .filter(
            models.client_analysts.c.client_id == client_id,
            models.client_analysts.c.user_id == user_id,
        )
        .first()
    )
    if existing:
        db.execute(
            models.client_analysts.update()
            .where(
                models.client_analysts.c.client_id == client_id,
                models.client_analysts.c.user_id == user_id,
            )
            .values(dedication=dedication)
        )
    else:
        db.execute(
            models.client_analysts.insert().values(
                client_id=client_id, user_id=user_id, dedication=dedication
            )
        )
    db.commit()
    db.refresh(client)
    return client


@router.delete("/clients/{client_id}/analysts/{user_id}", response_model=schemas.Client)
def unassign_client_analyst(
    client_id: int,
    user_id: int,
    db: Session = Depends(deps.get_db),
    current_user: models.User = deps.require_role(["Administrador", "Gerente de servicios"]),
):
    client = db.query(models.Client).filter(models.Client.id == client_id).first()
    if client is None:
        raise HTTPException(status_code=404, detail="Client not found")
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    db.execute(
        models.client_analysts.delete().where(
            models.client_analysts.c.client_id == client_id,
            models.client_analysts.c.user_id == user_id,
        )
    )
    db.commit()
    db.refresh(client)
    return client


@router.post("/projects/", response_model=schemas.Project)
def create_project(
    project: schemas.ProjectCreate,
    db: Session = Depends(deps.get_db),
    current_user: models.User = deps.require_role(["Administrador", "Gerente de servicios"]),
):
    if not db.query(models.Client).filter(models.Client.id == project.client_id).first():
        raise HTTPException(status_code=404, detail="Client not found")
    db_project = models.Project(
        name=project.name,
        client_id=project.client_id,
        objetivo=project.objetivo,
    )
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project


@router.get("/projects/", response_model=list[schemas.Project])
def read_projects(
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user),
):
    if current_user.role and current_user.role.name in ["Administrador", "Gerente de servicios"]:
        return db.query(models.Project).all()
    rows = (
        db.query(
            models.Project,
            models.project_analysts.c.scripts_per_day,
            models.project_analysts.c.test_types,
        )
        .join(models.project_analysts)
        .filter(models.project_analysts.c.user_id == current_user.id)
        .all()
    )
    projects = []
    for project, scripts, types in rows:
        setattr(project, "scripts_per_day", scripts)
        setattr(project, "test_types", types)
        projects.append(project)
    return projects


@router.get("/projects/{project_id}", response_model=schemas.Project)
def read_project(
    project_id: int,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user),
):
    query = db.query(models.Project).filter(models.Project.id == project_id)
    project = query.first()
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    if current_user.role and current_user.role.name in ["Administrador", "Gerente de servicios"]:
        return project
    row = (
        db.query(
            models.project_analysts.c.scripts_per_day,
            models.project_analysts.c.test_types,
        )
        .filter(
            models.project_analysts.c.project_id == project_id,
            models.project_analysts.c.user_id == current_user.id,
        )
        .first()
    )
    if row:
        scripts, types = row
        setattr(project, "scripts_per_day", scripts)
        setattr(project, "test_types", types)
        return project
    raise HTTPException(status_code=403, detail="Insufficient permissions")


@router.put("/projects/{project_id}", response_model=schemas.Project)
def update_project(
    project_id: int,
    project: schemas.ProjectCreate,
    db: Session = Depends(deps.get_db),
    current_user: models.User = deps.require_role(["Administrador", "Gerente de servicios"]),
):
    db_project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if db_project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    if not db.query(models.Client).filter(models.Client.id == project.client_id).first():
        raise HTTPException(status_code=404, detail="Client not found")
    db_project.name = project.name
    db_project.client_id = project.client_id
    db_project.objetivo = project.objetivo
    db.commit()
    db.refresh(db_project)
    return db_project


@router.delete("/projects/{project_id}")
def delete_project(
    project_id: int,
    db: Session = Depends(deps.get_db),
    current_user: models.User = deps.require_role(["Administrador", "Gerente de servicios"]),
):
    db_project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if db_project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    db_project.is_active = False
    db.commit()
    return {"ok": True}


@router.post("/projects/{project_id}/analysts/{user_id}", response_model=schemas.Project)
def assign_analyst(
    project_id: int,
    user_id: int,
    scripts_per_day: int = 0,
    test_types: str | None = None,
    db: Session = Depends(deps.get_db),
    current_user: models.User = deps.require_role(["Administrador", "Gerente de servicios"]),
):
    project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    existing = (
        db.query(models.project_analysts)
        .filter(
            models.project_analysts.c.project_id == project_id,
            models.project_analysts.c.user_id == user_id,
        )
        .first()
    )
    if existing:
        db.execute(
            models.project_analysts.update()
            .where(
                models.project_analysts.c.project_id == project_id,
                models.project_analysts.c.user_id == user_id,
            )
            .values(scripts_per_day=scripts_per_day, test_types=test_types)
        )
    else:
        db.execute(
            models.project_analysts.insert().values(
                project_id=project_id,
                user_id=user_id,
                scripts_per_day=scripts_per_day,
                test_types=test_types,
            )
        )
    db.commit()
    db.refresh(project)
    return project


@router.delete("/projects/{project_id}/analysts/{user_id}", response_model=schemas.Project)
def unassign_analyst(
    project_id: int,
    user_id: int,
    db: Session = Depends(deps.get_db),
    current_user: models.User = deps.require_role(["Administrador", "Gerente de servicios"]),
):
    project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    if user in project.analysts:
        project.analysts.remove(user)
        db.commit()
    db.refresh(project)
    return project


@router.post("/testplans/", response_model=schemas.TestPlan)
def create_testplan(
    plan: schemas.TestPlanCreate,
    db: Session = Depends(deps.get_db),
    current_user: models.User = deps.require_role(["Administrador"]),
):
    db_plan = models.TestPlan(**plan.dict())
    db.add(db_plan)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Integrity error")
    db.refresh(db_plan)
    return db_plan



@router.get("/testplans/", response_model=list[schemas.TestPlan])
def read_testplans(
    db: Session = Depends(deps.get_db),
    current_user: models.User = deps.require_role(["Administrador"]),
):
    return db.query(models.TestPlan).all()


@router.get("/testplans/{plan_id}", response_model=schemas.TestPlan)
def read_testplan(
    plan_id: int,
    db: Session = Depends(deps.get_db),
    current_user: models.User = deps.require_role(["Administrador"]),
):
    plan = db.query(models.TestPlan).filter(models.TestPlan.id == plan_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="TestPlan not found")
    return plan


@router.put("/testplans/{plan_id}", response_model=schemas.TestPlan)
def update_testplan(
    plan_id: int,
    plan_in: schemas.TestPlanCreate,
    db: Session = Depends(deps.get_db),
    current_user: models.User = deps.require_role(["Administrador"]),
):
    plan = db.query(models.TestPlan).filter(models.TestPlan.id == plan_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="TestPlan not found")
    if plan_in.fecha_inicio and plan_in.fecha_fin and plan_in.fecha_inicio > plan_in.fecha_fin:
        raise HTTPException(status_code=400, detail="fecha_inicio must be before fecha_fin")
    for field, value in plan_in.dict().items():
        setattr(plan, field, value)
    try:
        db.commit()
    except Exception:
        db.rollback()
        raise HTTPException(status_code=400, detail="Integrity error")
    db.refresh(plan)
    return plan


@router.delete("/testplans/{plan_id}")
def delete_testplan(
    plan_id: int,
    db: Session = Depends(deps.get_db),
    current_user: models.User = deps.require_role(["Administrador"]),
):
    plan = db.query(models.TestPlan).filter(models.TestPlan.id == plan_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="TestPlan not found")
    db.delete(plan)
    db.commit()
    return {"ok": True}


# Pages CRUD
@router.post("/pages/", response_model=schemas.Page)
def create_page(
    page: schemas.PageCreate,
    db: Session = Depends(deps.get_db),
    current_user: models.User = deps.require_role(["Administrador"]),
):
    if db.query(models.Page).filter(models.Page.name == page.name).first():
        raise HTTPException(status_code=400, detail="Page already exists")
    db_page = models.Page(name=page.name)
    db.add(db_page)
    db.commit()
    db.refresh(db_page)
    return db_page


@router.get("/pages/", response_model=list[schemas.Page])
def read_pages(
    db: Session = Depends(deps.get_db),
    current_user: models.User = deps.require_role(["Administrador"]),
):
    return db.query(models.Page).all()


@router.get("/pages/{page_id}", response_model=schemas.Page)
def read_page(
    page_id: int,
    db: Session = Depends(deps.get_db),
    current_user: models.User = deps.require_role(["Administrador"]),
):
    page = db.query(models.Page).filter(models.Page.id == page_id).first()
    if not page:
        raise HTTPException(status_code=404, detail="Page not found")
    return page


@router.put("/pages/{page_id}", response_model=schemas.Page)
def update_page(
    page_id: int,
    page_in: schemas.PageCreate,
    db: Session = Depends(deps.get_db),
    current_user: models.User = deps.require_role(["Administrador"]),
):
    page = db.query(models.Page).filter(models.Page.id == page_id).first()
    if not page:
        raise HTTPException(status_code=404, detail="Page not found")
    if (
        page_in.name != page.name
        and db.query(models.Page).filter(models.Page.name == page_in.name).first()
    ):
        raise HTTPException(status_code=400, detail="Page already exists")
    page.name = page_in.name
    db.commit()
    db.refresh(page)
    return page


@router.delete("/pages/{page_id}")
def delete_page(
    page_id: int,
    db: Session = Depends(deps.get_db),
    current_user: models.User = deps.require_role(["Administrador"]),
):
    page = db.query(models.Page).filter(models.Page.id == page_id).first()
    if not page:
        raise HTTPException(status_code=404, detail="Page not found")
    db.delete(page)
    db.commit()
    return {"ok": True}


# Page elements CRUD
@router.post("/elements/", response_model=schemas.PageElement)
def create_element(
    element: schemas.PageElementCreate,
    db: Session = Depends(deps.get_db),
    current_user: models.User = deps.require_role(["Administrador"]),
):
    if db.query(models.PageElement).filter(
        models.PageElement.page_id == element.page_id,
        models.PageElement.name == element.name,
    ).first():
        raise HTTPException(status_code=400, detail="Element already exists for page")
    db_element = models.PageElement(**element.dict())
    db.add(db_element)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Integrity error")
    db.refresh(db_element)
    return db_element


@router.get("/elements/", response_model=list[schemas.PageElement])
def read_elements(
    db: Session = Depends(deps.get_db),
    current_user: models.User = deps.require_role(["Administrador"]),
):
    return db.query(models.PageElement).all()


@router.get("/elements/{element_id}", response_model=schemas.PageElement)
def read_element(
    element_id: int,
    db: Session = Depends(deps.get_db),
    current_user: models.User = deps.require_role(["Administrador"]),
):
    element = (
        db.query(models.PageElement).filter(models.PageElement.id == element_id).first()
    )
    if not element:
        raise HTTPException(status_code=404, detail="Element not found")
    return element


@router.put("/elements/{element_id}", response_model=schemas.PageElement)
def update_element(
    element_id: int,
    element_in: schemas.PageElementCreate,
    db: Session = Depends(deps.get_db),
    current_user: models.User = deps.require_role(["Administrador"]),
):
    element = (
        db.query(models.PageElement).filter(models.PageElement.id == element_id).first()
    )
    if not element:
        raise HTTPException(status_code=404, detail="Element not found")
    if (
        (element_in.name != element.name or element_in.page_id != element.page_id)
        and db.query(models.PageElement)
        .filter(
            models.PageElement.page_id == element_in.page_id,
            models.PageElement.name == element_in.name,
        )
        .first()
    ):
        raise HTTPException(status_code=400, detail="Element already exists for page")
    for field, value in element_in.dict().items():
        setattr(element, field, value)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Integrity error")
    db.refresh(element)
    return element


@router.delete("/elements/{element_id}")
def delete_element(
    element_id: int,
    db: Session = Depends(deps.get_db),
    current_user: models.User = deps.require_role(["Administrador"]),
):
    element = (
        db.query(models.PageElement).filter(models.PageElement.id == element_id).first()
    )
    if not element:
        raise HTTPException(status_code=404, detail="Element not found")
    db.delete(element)
    db.commit()
    return {"ok": True}


# Associate elements with tests
@router.post("/elements/{element_id}/tests/{test_id}", response_model=schemas.PageElement)
def add_element_to_test(
    element_id: int,
    test_id: int,
    db: Session = Depends(deps.get_db),
    current_user: models.User = deps.require_role(["Administrador"]),
):
    element = (
        db.query(models.PageElement).filter(models.PageElement.id == element_id).first()
    )
    test = db.query(models.TestCase).filter(models.TestCase.id == test_id).first()
    if not element or not test:
        raise HTTPException(status_code=404, detail="Element or Test not found")
    if test not in element.tests:
        element.tests.append(test)
        db.commit()
    db.refresh(element)
    return element


@router.delete("/elements/{element_id}/tests/{test_id}", response_model=schemas.PageElement)
def remove_element_from_test(
    element_id: int,
    test_id: int,
    db: Session = Depends(deps.get_db),
    current_user: models.User = deps.require_role(["Administrador"]),
):
    element = (
        db.query(models.PageElement).filter(models.PageElement.id == element_id).first()
    )
    test = db.query(models.TestCase).filter(models.TestCase.id == test_id).first()
    if not element or not test:
        raise HTTPException(status_code=404, detail="Element or Test not found")
    if test in element.tests:
        element.tests.remove(test)
        db.commit()
    db.refresh(element)
    return element


# Actions CRUD
@router.post("/actions/", response_model=schemas.Action)
def create_action(
    action: schemas.ActionCreate,
    db: Session = Depends(deps.get_db),
    current_user: models.User = deps.require_role(["Administrador"]),
):
    if db.query(models.AutomationAction).filter(models.AutomationAction.name == action.name).first():
        raise HTTPException(status_code=400, detail="Action already exists")
    try:
        security.validate_action_code(action.codigo)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid code")
    db_action = models.AutomationAction(**action.dict())
    db.add(db_action)
    db.commit()
    db.refresh(db_action)
    return db_action


@router.get("/actions/", response_model=list[schemas.Action])
def read_actions(
    db: Session = Depends(deps.get_db),
    current_user: models.User = deps.require_role(["Administrador"]),
):
    return db.query(models.AutomationAction).all()


@router.get("/actions/{action_id}", response_model=schemas.Action)
def read_action(
    action_id: int,
    db: Session = Depends(deps.get_db),
    current_user: models.User = deps.require_role(["Administrador"]),
):
    action = db.query(models.AutomationAction).filter(models.AutomationAction.id == action_id).first()
    if not action:
        raise HTTPException(status_code=404, detail="Action not found")
    return action


@router.put("/actions/{action_id}", response_model=schemas.Action)
def update_action(
    action_id: int,
    action_in: schemas.ActionCreate,
    db: Session = Depends(deps.get_db),
    current_user: models.User = deps.require_role(["Administrador"]),
):
    action = db.query(models.AutomationAction).filter(models.AutomationAction.id == action_id).first()
    if not action:
        raise HTTPException(status_code=404, detail="Action not found")
    if action_in.name != action.name and db.query(models.AutomationAction).filter(models.AutomationAction.name == action_in.name).first():
        raise HTTPException(status_code=400, detail="Action already exists")
    try:
        security.validate_action_code(action_in.codigo)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid code")
    for field, value in action_in.dict().items():
        setattr(action, field, value)
    db.commit()
    db.refresh(action)
    return action


@router.delete("/actions/{action_id}")
def delete_action(
    action_id: int,
    db: Session = Depends(deps.get_db),
    current_user: models.User = deps.require_role(["Administrador"]),
):
    action = db.query(models.AutomationAction).filter(models.AutomationAction.id == action_id).first()
    if not action:
        raise HTTPException(status_code=404, detail="Action not found")
    db.delete(action)
    db.commit()
    return {"ok": True}


# Associate actions with tests
@router.post("/actions/{action_id}/tests/{test_id}", response_model=schemas.Action)
def add_action_to_test(
    action_id: int,
    test_id: int,
    db: Session = Depends(deps.get_db),
    current_user: models.User = deps.require_role(["Administrador"]),
):
    action = db.query(models.AutomationAction).filter(models.AutomationAction.id == action_id).first()
    test = db.query(models.TestCase).filter(models.TestCase.id == test_id).first()
    if not action or not test:
        raise HTTPException(status_code=404, detail="Action or Test not found")
    if test not in action.tests:
        action.tests.append(test)
        db.commit()
    db.refresh(action)
    return action


@router.delete("/actions/{action_id}/tests/{test_id}", response_model=schemas.Action)
def remove_action_from_test(
    action_id: int,
    test_id: int,
    db: Session = Depends(deps.get_db),
    current_user: models.User = deps.require_role(["Administrador"]),
):
    action = db.query(models.AutomationAction).filter(models.AutomationAction.id == action_id).first()
    test = db.query(models.TestCase).filter(models.TestCase.id == test_id).first()
    if not action or not test:
        raise HTTPException(status_code=404, detail="Action or Test not found")
    if test in action.tests:
        action.tests.remove(test)
        db.commit()
    db.refresh(action)
    return action


# CRUD for action assignments
@router.post("/assignments/", response_model=schemas.ActionAssignment)
def create_assignment(
    assignment: schemas.ActionAssignmentCreate,
    db: Session = Depends(deps.get_db),
    current_user: models.User = deps.require_role(["Administrador"]),
):
    action = db.query(models.AutomationAction).filter(models.AutomationAction.id == assignment.action_id).first()
    element = db.query(models.PageElement).filter(models.PageElement.id == assignment.element_id).first()
    test = db.query(models.TestCase).filter(models.TestCase.id == assignment.test_id).first()
    if not action or not element or not test:
        raise HTTPException(status_code=404, detail="Related objects not found")
    security.validate_assignment_params(action.argumentos, assignment.parametros or {})
    db_assignment = models.ActionAssignment(
        action_id=assignment.action_id,
        element_id=assignment.element_id,
        test_id=assignment.test_id,
        parametros=json.dumps(assignment.parametros or {}),
    )
    try:
        db.add(db_assignment)
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Integrity error")
    db.refresh(db_assignment)
    return db_assignment


@router.get("/assignments/", response_model=list[schemas.ActionAssignment])
def read_assignments(
    db: Session = Depends(deps.get_db),
    current_user: models.User = deps.require_role(["Administrador"]),
):
    assignments = db.query(models.ActionAssignment).all()
    for a in assignments:
        a.parametros = json.loads(a.parametros or "{}")
    return assignments


@router.get("/assignments/{assignment_id}", response_model=schemas.ActionAssignment)
def read_assignment(
    assignment_id: int,
    db: Session = Depends(deps.get_db),
    current_user: models.User = deps.require_role(["Administrador"]),
):
    a = db.query(models.ActionAssignment).filter(models.ActionAssignment.id == assignment_id).first()
    if not a:
        raise HTTPException(status_code=404, detail="Assignment not found")
    a.parametros = json.loads(a.parametros or "{}")
    return a


@router.put("/assignments/{assignment_id}", response_model=schemas.ActionAssignment)
def update_assignment(
    assignment_id: int,
    assignment_in: schemas.ActionAssignmentCreate,
    db: Session = Depends(deps.get_db),
    current_user: models.User = deps.require_role(["Administrador"]),
):
    a = db.query(models.ActionAssignment).filter(models.ActionAssignment.id == assignment_id).first()
    if not a:
        raise HTTPException(status_code=404, detail="Assignment not found")
    action = db.query(models.AutomationAction).filter(models.AutomationAction.id == assignment_in.action_id).first()
    element = db.query(models.PageElement).filter(models.PageElement.id == assignment_in.element_id).first()
    test = db.query(models.TestCase).filter(models.TestCase.id == assignment_in.test_id).first()
    if not action or not element or not test:
        raise HTTPException(status_code=404, detail="Related objects not found")
    security.validate_assignment_params(action.argumentos, assignment_in.parametros or {})
    for field, value in {
        "action_id": assignment_in.action_id,
        "element_id": assignment_in.element_id,
        "test_id": assignment_in.test_id,
        "parametros": json.dumps(assignment_in.parametros or {}),
    }.items():
        setattr(a, field, value)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Integrity error")
    db.refresh(a)
    a.parametros = json.loads(a.parametros or "{}")
    return a


@router.delete("/assignments/{assignment_id}")
def delete_assignment(
    assignment_id: int,
    db: Session = Depends(deps.get_db),
    current_user: models.User = deps.require_role(["Administrador"]),
):
    a = db.query(models.ActionAssignment).filter(models.ActionAssignment.id == assignment_id).first()
    if not a:
        raise HTTPException(status_code=404, detail="Assignment not found")
    db.delete(a)
    db.commit()
    return {"ok": True}

# CRUD for actors
@router.post("/actors/", response_model=schemas.Actor)
def create_actor(
    actor: schemas.ActorCreate,
    db: Session = Depends(deps.get_db),
    current_user: models.User = deps.require_role(["Administrador"]),
):
    if not db.query(models.Client).filter(models.Client.id == actor.client_id).first():
        raise HTTPException(status_code=404, detail="Client not found")
    db_actor = models.Actor(name=actor.name, client_id=actor.client_id)
    db.add(db_actor)
    db.commit()
    db.refresh(db_actor)
    return db_actor


@router.get("/actors/", response_model=list[schemas.Actor])
def read_actors(
    client_id: int | None = None,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user),
):
    query = db.query(models.Actor)
    if client_id is not None:
        query = query.filter(models.Actor.client_id == client_id)
    return query.all()


@router.put("/actors/{actor_id}", response_model=schemas.Actor)
def update_actor(
    actor_id: int,
    actor_in: schemas.ActorCreate,
    db: Session = Depends(deps.get_db),
    current_user: models.User = deps.require_role(["Administrador"]),
):
    actor = db.query(models.Actor).filter(models.Actor.id == actor_id).first()
    if not actor:
        raise HTTPException(status_code=404, detail="Actor not found")
    if not db.query(models.Client).filter(models.Client.id == actor_in.client_id).first():
        raise HTTPException(status_code=404, detail="Client not found")
    actor.name = actor_in.name
    actor.client_id = actor_in.client_id
    db.commit()
    db.refresh(actor)
    return actor


@router.delete("/actors/{actor_id}")
def delete_actor(
    actor_id: int,
    db: Session = Depends(deps.get_db),
    current_user: models.User = deps.require_role(["Administrador"]),
):
    actor = db.query(models.Actor).filter(models.Actor.id == actor_id).first()
    if not actor:
        raise HTTPException(status_code=404, detail="Actor not found")
    db.delete(actor)
    db.commit()
    return {"ok": True}

# CRUD for execution agents
@router.post("/agents/", response_model=schemas.Agent)
def create_agent(
    agent: schemas.AgentCreate,
    db: Session = Depends(deps.get_db),
    current_user: models.User = deps.require_role(["Administrador"]),
):
    if db.query(models.ExecutionAgent).filter(models.ExecutionAgent.hostname == agent.hostname).first():
        raise HTTPException(status_code=400, detail="Hostname already registered")
    db_agent = models.ExecutionAgent(**agent.dict())
    db.add(db_agent)
    db.commit()
    db.refresh(db_agent)
    return db_agent


@router.get("/agents/", response_model=list[schemas.Agent])
def read_agents(
    db: Session = Depends(deps.get_db),
    current_user: models.User = deps.require_role(["Administrador"]),
):
    return db.query(models.ExecutionAgent).all()


@router.get("/agents/{agent_id}", response_model=schemas.Agent)
def read_agent(
    agent_id: int,
    db: Session = Depends(deps.get_db),
    current_user: models.User = deps.require_role(["Administrador"]),
):
    agent = db.query(models.ExecutionAgent).filter(models.ExecutionAgent.id == agent_id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agent


@router.put("/agents/{agent_id}", response_model=schemas.Agent)
def update_agent(
    agent_id: int,
    agent_in: schemas.AgentCreate,
    db: Session = Depends(deps.get_db),
    current_user: models.User = deps.require_role(["Administrador"]),
):
    agent = db.query(models.ExecutionAgent).filter(models.ExecutionAgent.id == agent_id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    if agent.hostname != agent_in.hostname and db.query(models.ExecutionAgent).filter(models.ExecutionAgent.hostname == agent_in.hostname).first():
        raise HTTPException(status_code=400, detail="Hostname already registered")
    for field, value in agent_in.dict().items():
        setattr(agent, field, value)
    db.commit()
    db.refresh(agent)
    return agent


@router.delete("/agents/{agent_id}")
def delete_agent(
    agent_id: int,
    db: Session = Depends(deps.get_db),
    current_user: models.User = deps.require_role(["Administrador"]),
):
    agent = db.query(models.ExecutionAgent).filter(models.ExecutionAgent.id == agent_id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    db.delete(agent)
    db.commit()
    return {"ok": True}


# CRUD for execution plans

@router.post("/executionplans/", response_model=schemas.ExecutionPlan)
def create_execution_plan(
    plan: schemas.ExecutionPlanCreate,
    db: Session = Depends(deps.get_db),
    current_user: models.User = deps.require_role(["Administrador"]),
):
    if not db.query(models.TestCase).filter(models.TestCase.id == plan.test_id).first():
        raise HTTPException(status_code=404, detail="TestCase not found")
    if not db.query(models.ExecutionAgent).filter(models.ExecutionAgent.id == plan.agent_id).first():
        raise HTTPException(status_code=404, detail="Agent not found")
    db_plan = models.ExecutionPlan(**plan.dict())
    db.add(db_plan)
    db.commit()
    db.refresh(db_plan)
    return db_plan


@router.get("/executionplans/", response_model=list[schemas.ExecutionPlan])
def read_execution_plans(
    agent_id: int | None = None,
    test_id: int | None = None,
    nombre: str | None = None,
    db: Session = Depends(deps.get_db),
    current_user: models.User = deps.require_role(["Administrador"]),
):
    query = db.query(models.ExecutionPlan)
    if agent_id is not None:
        query = query.filter(models.ExecutionPlan.agent_id == agent_id)
    if test_id is not None:
        query = query.filter(models.ExecutionPlan.test_id == test_id)
    if nombre is not None:
        query = query.filter(models.ExecutionPlan.nombre.ilike(f"%{nombre}%"))
    return query.all()


@router.get("/executionplans/{plan_id}", response_model=schemas.ExecutionPlan)
def read_execution_plan(
    plan_id: int,
    db: Session = Depends(deps.get_db),
    current_user: models.User = deps.require_role(["Administrador"]),
):
    plan = db.query(models.ExecutionPlan).filter(models.ExecutionPlan.id == plan_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="ExecutionPlan not found")
    return plan


@router.put("/executionplans/{plan_id}", response_model=schemas.ExecutionPlan)
def update_execution_plan(
    plan_id: int,
    plan_in: schemas.ExecutionPlanCreate,
    db: Session = Depends(deps.get_db),
    current_user: models.User = deps.require_role(["Administrador"]),
):
    plan = db.query(models.ExecutionPlan).filter(models.ExecutionPlan.id == plan_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="ExecutionPlan not found")
    if not db.query(models.TestCase).filter(models.TestCase.id == plan_in.test_id).first():
        raise HTTPException(status_code=404, detail="TestCase not found")
    if not db.query(models.ExecutionAgent).filter(models.ExecutionAgent.id == plan_in.agent_id).first():
        raise HTTPException(status_code=404, detail="Agent not found")
    for field, value in plan_in.dict().items():
        setattr(plan, field, value)
    db.commit()
    db.refresh(plan)
    return plan


@router.delete("/executionplans/{plan_id}")
def delete_execution_plan(
    plan_id: int,
    db: Session = Depends(deps.get_db),
    current_user: models.User = deps.require_role(["Administrador"]),
):
    plan = db.query(models.ExecutionPlan).filter(models.ExecutionPlan.id == plan_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="ExecutionPlan not found")
    db.delete(plan)
    db.commit()
    return {"ok": True}

@router.post("/executionplans/{plan_id}/run", response_model=schemas.PlanExecution)
def run_execution_plan(
    plan_id: int,
    db: Session = Depends(deps.get_db),
    current_user: models.User = deps.require_role(["Administrador"]),
):
    plan = db.query(models.ExecutionPlan).filter(models.ExecutionPlan.id == plan_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="ExecutionPlan not found")
    pending = db.query(models.PlanExecution).filter(
        models.PlanExecution.agent_id == plan.agent_id,
        models.PlanExecution.status.in_(
            [
                models.ExecutionStatus.CALLING.value,
                models.ExecutionStatus.RUNNING.value,
            ]
        ),
    ).first()
    if pending:
        raise HTTPException(status_code=400, detail="Agent has a pending execution")
    record = models.PlanExecution(
        plan_id=plan.id,
        agent_id=plan.agent_id,
        status=models.ExecutionStatus.CALLING.value,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


@router.get("/executions/", response_model=list[schemas.PlanExecution])
def read_executions(
    plan_id: int | None = None,
    agent_id: int | None = None,
    db: Session = Depends(deps.get_db),
    current_user: models.User = deps.require_role(["Administrador"]),
):
    query = db.query(models.PlanExecution)
    if plan_id is not None:
        query = query.filter(models.PlanExecution.plan_id == plan_id)
    if agent_id is not None:
        query = query.filter(models.PlanExecution.agent_id == agent_id)
    return query.all()


@router.get("/executions/{execution_id}", response_model=schemas.PlanExecution)
def read_execution(
    execution_id: int,
    db: Session = Depends(deps.get_db),
    current_user: models.User = deps.require_role(["Administrador"]),
):
    record = db.query(models.PlanExecution).filter(models.PlanExecution.id == execution_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Execution not found")
    return record


@router.get("/executions/{execution_id}/{file_type}")
def get_execution_file(
    execution_id: int,
    file_type: str,
    db: Session = Depends(deps.get_db),
    current_user: models.User = deps.require_role(["Administrador"]),
):
    record = db.query(models.PlanExecution).filter(models.PlanExecution.id == execution_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Execution not found")
    filename = f"{file_type}_{execution_id}.{'pdf' if file_type == 'report' else 'zip'}"
    path = os.path.join('/tmp', filename)
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(path, filename=filename)


@router.get("/agents/{hostname}/pending", response_model=schemas.PendingExecution)
def get_pending_execution(
    hostname: str,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user),
):
    if current_user.username != hostname:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    agent = (
        db.query(models.ExecutionAgent)
        .filter(models.ExecutionAgent.hostname == hostname)
        .first()
    )
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    record = (
        db.query(models.PlanExecution)
        .filter(
            models.PlanExecution.agent_id == agent.id,
            models.PlanExecution.status.in_(
                [
                    models.ExecutionStatus.CALLING.value,
                    models.ExecutionStatus.RUNNING.value,
                ]
            ),
        )
        .order_by(models.PlanExecution.started_at)
        .first()
    )
    if not record:
        raise HTTPException(status_code=404, detail="No pending execution")
    test = record.plan.test
    assignments = (
        db.query(models.ActionAssignment)
        .filter(models.ActionAssignment.test_id == test.id)
        .all()
    )
    details = [
        schemas.AssignmentDetail(
            action=schemas.Action.from_orm(a.action),
            element=schemas.PageElement.from_orm(a.element),
            parametros=json.loads(a.parametros or "{}"),
        )
        for a in assignments
    ]
    return schemas.PendingExecution(
        execution_id=record.id,
        plan=schemas.ExecutionPlan.from_orm(record.plan),
        test=schemas.Test.from_orm(test),
        assignments=details,
    )
    try:
        security.rate_limit_login(ip)
    except HTTPException:
        # generic rate limit response
        raise

    user = deps.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Invalid username or password")
    token = deps.create_access_token({"sub": user.username})
    return {"access_token": token, "token_type": "bearer"}

@router.get("/users/me/", response_model=schemas.User)
def read_users_me(current_user: models.User = Depends(deps.get_current_user)):
    return current_user


@router.get("/users/me/permissions", response_model=list[schemas.Permission])
def read_my_permissions(
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user),
):
    if current_user.role is None:
        return []
    return (
        db.query(models.PagePermission)
        .filter(models.PagePermission.role_id == current_user.role.id)
        .all()
    )

@router.post("/tests/", response_model=schemas.Test)
def create_test(test: schemas.TestCreate, db: Session = Depends(deps.get_db), current_user: models.User = Depends(deps.get_current_user)):
    db_test = models.TestCase(**test.dict(), owner_id=current_user.id)
    db.add(db_test)
    db.commit()
    db.refresh(db_test)
    return db_test

@router.get("/tests/", response_model=list[schemas.Test])
def read_tests(
    search: str | None = None,
    priority: str | None = None,
    status: str | None = None,
    test_plan_id: int | None = None,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user),
):
    query = db.query(models.TestCase).filter(models.TestCase.owner_id == current_user.id)
    if search is not None:
        query = query.filter(models.TestCase.name.ilike(f"%{search}%"))
    if priority is not None:
        query = query.filter(models.TestCase.priority == priority)
    if status is not None:
        query = query.filter(models.TestCase.status == status)
    if test_plan_id is not None:
        query = query.filter(models.TestCase.test_plan_id == test_plan_id)
    return query.all()

@router.get("/tests/{test_id}", response_model=schemas.Test)
def read_test(test_id: int, db: Session = Depends(deps.get_db), current_user: models.User = Depends(deps.get_current_user)):
    test = db.query(models.TestCase).filter(models.TestCase.id == test_id, models.TestCase.owner_id == current_user.id).first()
    if test is None:
        raise HTTPException(status_code=404, detail="Test not found")
    return test


@router.put("/tests/{test_id}", response_model=schemas.Test)
def update_test(
    test_id: int,
    test_in: schemas.TestCreate,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user),
):
    test = db.query(models.TestCase).filter(models.TestCase.id == test_id, models.TestCase.owner_id == current_user.id).first()
    if test is None:
        raise HTTPException(status_code=404, detail="Test not found")
    for field, value in test_in.dict().items():
        setattr(test, field, value)
    db.commit()
    db.refresh(test)
    return test

@router.delete("/tests/{test_id}")
def delete_test(test_id: int, db: Session = Depends(deps.get_db), current_user: models.User = Depends(deps.get_current_user)):
    test = db.query(models.TestCase).filter(models.TestCase.id == test_id, models.TestCase.owner_id == current_user.id).first()
    if test is None:
        raise HTTPException(status_code=404, detail="Test not found")
    db.delete(test)
    db.commit()
    return {"ok": True}


@router.get("/metrics/overview", response_model=schemas.Metrics)
def get_metrics(
    db: Session = Depends(deps.get_db),
    current_user: models.User = deps.require_role(["Administrador", "Arquitecto de Automatización"]),
):
    clients = db.query(models.Client).all()
    flows = db.query(models.TestCase).all()
    return schemas.Metrics(clients=clients, flows=flows)
