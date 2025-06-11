from fastapi.security import OAuth2PasswordRequestForm
from fastapi import APIRouter, Depends, HTTPException, Request
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

@router.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(deps.get_db)):
    try:
        security.validate_username(user.username)
        security.validate_password_strength(user.password)
    except HTTPException:
        # re-raise to keep generic message
        raise

    if deps.get_user(db, username=user.username):
        raise HTTPException(status_code=400, detail="Invalid username or password")

    default_role = db.query(models.Role).filter(models.Role.name == "Analista de Pruebas con skill de automatizaci\u00f3n").first()
    new_user = models.User(username=user.username, hashed_password=hashed_password, role=default_role)
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(deps.get_db),
):
    ip = request.client.host
    try:
        security.rate_limit_login(ip)
    except HTTPException:
        # generic rate limit response
        raise

        raise HTTPException(status_code=400, detail="Invalid username or password")

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

        raise

    if deps.get_user(db, username=user.username):
        raise HTTPException(status_code=400, detail="Invalid username or password")

    hashed_password = deps.get_password_hash(user.password)
    new_user = models.User(username=user.username, hashed_password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.post("/token")
def login_for_access_token(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(deps.get_db),
):
    ip = request.client.host


@router.post("/clients/", response_model=schemas.Client)
def create_client(
    client: schemas.ClientCreate,
    db: Session = Depends(deps.get_db),
    current_user: models.User = deps.require_role(["Administrador"]),
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
    current_user: models.User = deps.require_role(["Administrador"]),
):
    return db.query(models.Client).all()


@router.put("/clients/{client_id}", response_model=schemas.Client)
def update_client(
    client_id: int,
    client: schemas.ClientCreate,
    db: Session = Depends(deps.get_db),
    current_user: models.User = deps.require_role(["Administrador"]),
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


@router.post("/projects/", response_model=schemas.Project)
def create_project(
    project: schemas.ProjectCreate,
    db: Session = Depends(deps.get_db),
    current_user: models.User = deps.require_role(["Administrador"]),
):
    if not db.query(models.Client).filter(models.Client.id == project.client_id).first():
        raise HTTPException(status_code=404, detail="Client not found")
    db_project = models.Project(name=project.name, client_id=project.client_id)
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project


@router.get("/projects/", response_model=list[schemas.Project])
def read_projects(
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user),
):
    if current_user.role and current_user.role.name == "Administrador":
        return db.query(models.Project).all()
    return (
        db.query(models.Project)
        .join(models.project_analysts)
        .filter(models.project_analysts.c.user_id == current_user.id)
        .all()
    )


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
    if (
        current_user.role and current_user.role.name == "Administrador"
    ) or (
        db.query(models.project_analysts)
        .filter(
            models.project_analysts.c.project_id == project_id,
            models.project_analysts.c.user_id == current_user.id,
        )
        .first()
    ):
        return project
    raise HTTPException(status_code=403, detail="Insufficient permissions")


@router.put("/projects/{project_id}", response_model=schemas.Project)
def update_project(
    project_id: int,
    project: schemas.ProjectCreate,
    db: Session = Depends(deps.get_db),
    current_user: models.User = deps.require_role(["Administrador"]),
):
    db_project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if db_project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    if not db.query(models.Client).filter(models.Client.id == project.client_id).first():
        raise HTTPException(status_code=404, detail="Client not found")
    db_project.name = project.name
    db_project.client_id = project.client_id
    db.commit()
    db.refresh(db_project)
    return db_project


@router.delete("/projects/{project_id}")
def delete_project(
    project_id: int,
    db: Session = Depends(deps.get_db),
    current_user: models.User = deps.require_role(["Administrador"]),
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
    db: Session = Depends(deps.get_db),
    current_user: models.User = deps.require_role(["Administrador"]),
):
    project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    if user not in project.analysts:
        project.analysts.append(user)
        db.commit()
    db.refresh(project)
    return project


@router.delete("/projects/{project_id}/analysts/{user_id}", response_model=schemas.Project)
def unassign_analyst(
    project_id: int,
    user_id: int,
    db: Session = Depends(deps.get_db),
    current_user: models.User = deps.require_role(["Administrador"]),
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
    if plan.fecha_inicio and plan.fecha_fin and plan.fecha_inicio > plan.fecha_fin:
        raise HTTPException(status_code=400, detail="fecha_inicio must be before fecha_fin")
    if plan_in.fecha_inicio and plan_in.fecha_fin and plan_in.fecha_inicio > plan_in.fecha_fin:
        raise HTTPException(status_code=400, detail="fecha_inicio must be before fecha_fin")
    if plan.fecha_inicio and plan.fecha_fin and plan.fecha_inicio > plan.fecha_fin:
        raise HTTPException(status_code=400, detail="fecha_inicio must be before fecha_fin")
    db_plan = models.TestPlan(**plan.dict())
    db.add(db_plan)
    try:
        db.commit()
    except Exception:
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

@router.post("/tests/", response_model=schemas.Test)
def create_test(test: schemas.TestCreate, db: Session = Depends(deps.get_db), current_user: models.User = Depends(deps.get_current_user)):
    db_test = models.TestCase(**test.dict(), owner_id=current_user.id)
    db.add(db_test)
    db.commit()
    db.refresh(db_test)
    return db_test

@router.get("/tests/", response_model=list[schemas.Test])
def read_tests(db: Session = Depends(deps.get_db), current_user: models.User = Depends(deps.get_current_user)):
    return db.query(models.TestCase).filter(models.TestCase.owner_id == current_user.id).all()

@router.get("/tests/{test_id}", response_model=schemas.Test)
def read_test(test_id: int, db: Session = Depends(deps.get_db), current_user: models.User = Depends(deps.get_current_user)):
    test = db.query(models.TestCase).filter(models.TestCase.id == test_id, models.TestCase.owner_id == current_user.id).first()
    if test is None:
        raise HTTPException(status_code=404, detail="Test not found")
    return test

@router.delete("/tests/{test_id}")
def delete_test(test_id: int, db: Session = Depends(deps.get_db), current_user: models.User = Depends(deps.get_current_user)):
    test = db.query(models.TestCase).filter(models.TestCase.id == test_id, models.TestCase.owner_id == current_user.id).first()
    if test is None:
        raise HTTPException(status_code=404, detail="Test not found")
    db.delete(test)
    db.commit()
    return {"ok": True}
