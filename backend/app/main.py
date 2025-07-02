from fastapi import FastAPI, Depends, HTTPException
import logging
logging.basicConfig(level=logging.INFO)
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from .database import engine, SessionLocal
from . import models, schemas, deps
from .crud import create_crud_router

logger = logging.getLogger(__name__)


def seed_database() -> None:
    logger.info("Seeding database")
    db = SessionLocal()
    try:
        roles = [
            ("Administrador", "/dashboard"),
            ("Automation Engineer", "/dashboard"),
            ("Gerente de servicios", "/clients"),
            ("Analista de Performance", "/clients"),
            ("Automatizador de Pruebas", "/clients"),
            ("Arquitecto de Automatización", "/interactions"),
            ("Analista de Pruebas con skill de automatización", "/clients"),
        ]

        role_objs: list[tuple[models.Role, str]] = []
        for name, start_page in roles:
            role = db.query(models.Role).filter_by(name=name).first()
            if not role:
                role = models.Role(name=name, description=name)
                db.add(role)
                db.commit()
                db.refresh(role)
            role_objs.append((role, start_page))

        for role, page in role_objs:
            exists = (
                db.query(models.PagePermission)
                .filter_by(role_id=role.id, page=page, isStartPage=True)
                .first()
            )
            if not exists:
                db.add(
                    models.PagePermission(
                        page=page,
                        role_id=role.id,
                        isStartPage=True,
                        description="start",
                    )
                )

        role_map = {r.name: r for r, _ in role_objs}
        perms = [
            ("/clients", "POST", "Gerente de servicios"),
            ("/users", "PUT", "Arquitecto de Automatización"),
            ("/actors", "GET", "Gerente de servicios"),
            ("/digitalassets", "GET", "Gerente de servicios"),
        ]
        for route, method, role_name in perms:
            role = role_map.get(role_name)
            if role:
                if (
                    not db.query(models.ApiPermission)
                    .filter_by(route=route, method=method, role_id=role.id)
                    .first()
                ):
                    db.add(
                        models.ApiPermission(
                            route=route, method=method, role_id=role.id
                        )
                    )

        for name in ["web", "movil", "apis", "performance"]:
            if not db.query(models.Hability).filter_by(name=name).first():
                db.add(models.Hability(name=name))

        for desc in ["textbox", "button", "combobox", "selector"]:
            if not db.query(models.ElementType).filter_by(description=desc).first():
                db.add(models.ElementType(description=desc))

        for name in ["pendiente", "aprobado", "rechazado"]:
            if (
                not db.query(models.InteractionApprovalState)
                .filter_by(name=name)
                .first()
            ):
                db.add(models.InteractionApprovalState(name=name))

        field_types = [
            ("numerico", None, "numeric"),
            ("alfanumerico", None, "alphanumeric"),
            ("alfabeto", None, "alphabet"),
            ("uuid", None, "uuid"),
            ("fecha", "YYYY-MM-DD", "date"),
        ]
        for name, fmt, desc in field_types:
            if not db.query(models.FieldType).filter_by(name=name).first():
                db.add(models.FieldType(name=name, format=fmt, description=desc))

        admin_role = db.query(models.Role).filter_by(name="Administrador").first()
        admin_user = db.query(models.User).filter_by(username="admin").first()
        if admin_role and not admin_user:
            db.add(
                models.User(
                    username="admin",
                    password=deps.get_password_hash("admin"),
                    role_id=admin_role.id,
                )
            )

        default_users = [
            ("architect", "Arquitecto de Automatización"),
            ("AngelC", "Gerente de servicios"),
            ("T23AutoPerson", "Automatizador de Pruebas"),
        ]
        for username, role_name in default_users:
            role = role_map.get(role_name)
            if role and not db.query(models.User).filter_by(username=username).first():
                db.add(
                    models.User(
                        username=username,
                        password=deps.get_password_hash("admin"),
                        role_id=role.id,
                    )
                )

        db.commit()
        logger.info("Database seed commit successful")
    finally:
        db.close()
        logger.info("Seeding finished")


logger.info("Creating database tables")
models.Base.metadata.create_all(bind=engine)
logger.info("Tables created")
seed_database()

def validate_database() -> None:
    """Ensure critical tables exist and have data."""
    logger.info("Validating seeded tables")
    db = SessionLocal()
    try:
        roles = db.query(models.Role).count()
        types = db.query(models.ElementType).count()
        if roles < 1 or types < 1:
            raise RuntimeError("Database seeding failed")
        logger.info("Validation successful: %d roles, %d element types", roles, types)
    finally:
        db.close()

validate_database()

app = FastAPI(title="Test Automation API")

# Enable CORS for frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/token")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(deps.get_db)
):
    user = deps.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Invalid credentials")
    token = deps.create_access_token({"user_id": user.id})
    return {"access_token": token, "token_type": "bearer"}


@app.post("/logout")
def logout(token: str = Depends(deps.oauth2_scheme)):
    deps.revoke_token(token)
    return {"ok": True}


def _client_with_analysts(client: models.Client, db: Session) -> models.Client:
    analysts = (
        db.query(models.User)
        .join(models.ClientAnalyst, models.ClientAnalyst.userId == models.User.id)
        .filter(models.ClientAnalyst.clientId == client.id)
        .all()
    )
    client.analysts = analysts
    return client


def _project_with_analysts(project: models.Project, db: Session) -> models.Project:
    analysts = (
        db.query(models.User)
        .join(models.ProjectEmployee, models.ProjectEmployee.userId == models.User.id)
        .filter(models.ProjectEmployee.projectId == project.id)
        .all()
    )
    project.analysts = analysts
    return project


# CRUD routers for main entities
def register_cruds():
    mappings = [
        ("roles", models.Role, schemas.Role),
        ("users", models.User, schemas.User),
        ("pagepermissions", models.PagePermission, schemas.PagePermission),
        ("apipermissions", models.ApiPermission, schemas.ApiPermission),
        ("clients", models.Client, schemas.Client),
        ("businessagreements", models.BusinessAgreement, schemas.BusinessAgreement),
        ("digitalassets", models.DigitalAsset, schemas.DigitalAsset),
        ("userinterfaces", models.UserInterface, schemas.UserInterface),
        ("elementtypes", models.ElementType, schemas.ElementType),
        ("elements", models.Element, schemas.Element),
        ("projects", models.Project, schemas.Project),
        ("projectemployees", models.ProjectEmployee, schemas.ProjectEmployee),
        ("actors", models.Actor, schemas.Actor),
        ("habilities", models.Hability, schemas.Hability),
        ("interactionapprovalstates", models.InteractionApprovalState, schemas.InteractionApprovalState),
        ("tasks", models.Task, schemas.Task),
        (
            "taskhaveinteractions",
            models.TaskHaveInteraction,
            schemas.TaskHaveInteraction,
        ),
        ("questions", models.Question, schemas.Question),
        (
            "questionhasvalidations",
            models.QuestionHasValidation,
            schemas.QuestionHasValidation,
        ),
        ("scenarios", models.Scenario, schemas.Scenario),
        ("scenariodata", models.ScenarioData, schemas.ScenarioData),
        ("rawdata", models.RawData, schemas.RawData),
        ("fieldtypes", models.FieldType, schemas.FieldType),
        ("features", models.Feature, schemas.Feature),
        ("clientanalysts", models.ClientAnalyst, schemas.ClientAnalyst),
        ("scenariohasfeatures", models.ScenarioHasFeature, schemas.ScenarioHasFeature),
        ("featuresteps", models.FeatureStep, schemas.FeatureStep),
        ("scenarioinfo", models.ScenarioInfo, schemas.ScenarioInfo),
    ]
    for prefix, model, schema in mappings:
        app.include_router(create_crud_router(prefix, model, schema))



register_cruds()

from .routes import interactions as interactions_routes
from .routes import validations as validations_routes

app.include_router(interactions_routes.router)
app.include_router(interactions_routes.param_router)
app.include_router(interactions_routes.approval_router)
app.include_router(validations_routes.router)
app.include_router(validations_routes.param_router)
app.include_router(validations_routes.approval_router)


@app.get("/users/me/", response_model=schemas.User)
def read_current_user(current_user: models.User = Depends(deps.get_current_user)):
    return current_user


@app.get("/permissions")
def read_permissions(
    current_user: models.User = Depends(deps.get_current_user),
    db: Session = Depends(deps.get_db),
):
    pages = (
        db.query(models.PagePermission.page)
        .filter_by(role_id=current_user.role_id)
        .all()
    )
    return {
        "permissions": [p.page for p in pages],
        "role": current_user.role.name,
    }


@app.get("/roles/{role_id}/permissions")
def list_role_page_permissions(role_id: int, db: Session = Depends(deps.get_db)):
    return db.query(models.PagePermission).filter_by(role_id=role_id).all()


@app.post("/roles/{role_id}/permissions", response_model=schemas.PagePermission)
def add_role_page_permission(
    role_id: int,
    perm: schemas.PagePermissionInput,
    db: Session = Depends(deps.get_db),
):
    if (
        db.query(models.PagePermission)
        .filter_by(role_id=role_id, page=perm.page)
        .first()
    ):
        raise HTTPException(status_code=400, detail="Permission exists")
    obj = models.PagePermission(
        page=perm.page,
        role_id=role_id,
        isStartPage=perm.isStartPage,
        description=perm.description,
    )
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@app.delete("/roles/{role_id}/permissions/{page:path}")
def remove_role_page_permission(
    role_id: int, page: str, db: Session = Depends(deps.get_db)
):
    perm = db.query(models.PagePermission).filter_by(role_id=role_id, page=page).first()
    if not perm:
        raise HTTPException(status_code=404, detail="Not found")
    db.delete(perm)
    db.commit()
    return {"ok": True}


@app.get("/roles/{role_id}/api-permissions")
def list_role_api_permissions(role_id: int, db: Session = Depends(deps.get_db)):
    return db.query(models.ApiPermission).filter_by(role_id=role_id).all()


@app.post("/roles/{role_id}/api-permissions", response_model=schemas.ApiPermission)
def add_role_api_permission(
    role_id: int,
    perm: schemas.ApiPermissionInput,
    db: Session = Depends(deps.get_db),
):
    if (
        db.query(models.ApiPermission)
        .filter_by(role_id=role_id, route=perm.route, method=perm.method)
        .first()
    ):
        raise HTTPException(status_code=400, detail="Permission exists")
    obj = models.ApiPermission(
        route=perm.route,
        method=perm.method,
        role_id=role_id,
        description=perm.description,
    )
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@app.delete("/roles/{role_id}/api-permissions/{perm_id}")
def remove_role_api_permission(
    role_id: int, perm_id: int, db: Session = Depends(deps.get_db)
):
    perm = db.query(models.ApiPermission).filter_by(role_id=role_id, id=perm_id).first()
    if not perm:
        raise HTTPException(status_code=404, detail="Not found")
    db.delete(perm)
    db.commit()
    return {"ok": True}


@app.post("/users/{user_id}/role/{role_id}", response_model=schemas.User)
def assign_role(
    user_id: int,
    role_id: int,
    db: Session = Depends(deps.get_db),
    _: models.User = Depends(deps.require_admin),
):
    user = db.query(models.User).filter_by(id=user_id).first()
    role = db.query(models.Role).filter_by(id=role_id).first()
    if not user or not role:
        raise HTTPException(status_code=404, detail="Not found")
    user.role_id = role_id
    db.commit()
    db.refresh(user)
    return user


@app.put("/roles/{role_id}/active", response_model=schemas.Role)
def update_role_active(
    role_id: int,
    data: dict,
    db: Session = Depends(deps.get_db),
    _: models.User = Depends(deps.require_admin),
):
    role = db.query(models.Role).filter_by(id=role_id).first()
    if not role:
        raise HTTPException(status_code=404, detail="Not found")
    role.is_active = bool(data.get("is_active"))
    db.commit()
    db.refresh(role)
    return role


@app.post("/clients/{client_id}/analysts/{user_id}", response_model=schemas.Client)
def assign_client_analyst(
    client_id: int,
    user_id: int,
    dedication: int = 100,
    db: Session = Depends(deps.get_db),
):
    client = db.query(models.Client).filter_by(id=client_id).first()
    user = db.query(models.User).filter_by(id=user_id).first()
    if not client or not user:
        raise HTTPException(status_code=404, detail="Not found")
    link = (
        db.query(models.ClientAnalyst)
        .filter_by(clientId=client_id, userId=user_id)
        .first()
    )
    if not link:
        link = models.ClientAnalyst(clientId=client_id, userId=user_id, dedication=dedication)
        db.add(link)
    else:
        link.dedication = dedication
    db.commit()
    return _client_with_analysts(client, db)


@app.delete("/clients/{client_id}/analysts/{user_id}", response_model=schemas.Client)
def unassign_client_analyst(
    client_id: int,
    user_id: int,
    db: Session = Depends(deps.get_db),
):
    link = (
        db.query(models.ClientAnalyst)
        .filter_by(clientId=client_id, userId=user_id)
        .first()
    )
    if link:
        db.delete(link)
        db.commit()
    client = db.query(models.Client).filter_by(id=client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Not found")
    return _client_with_analysts(client, db)


@app.post("/projects/{project_id}/analysts/{user_id}", response_model=schemas.Project)
def assign_project_analyst(
    project_id: int,
    user_id: int,
    scripts_per_day: int = 0,
    db: Session = Depends(deps.get_db),
):
    project = db.query(models.Project).filter_by(id=project_id).first()
    user = db.query(models.User).filter_by(id=user_id).first()
    if not project or not user:
        raise HTTPException(status_code=404, detail="Not found")
    link = (
        db.query(models.ProjectEmployee)
        .filter_by(projectId=project_id, userId=user_id)
        .first()
    )
    if not link:
        link = models.ProjectEmployee(
            projectId=project_id,
            userId=user_id,
            dedicationHours=scripts_per_day,
        )
        db.add(link)
    else:
        link.dedicationHours = scripts_per_day
    db.commit()
    return _project_with_analysts(project, db)


@app.delete("/projects/{project_id}/analysts/{user_id}", response_model=schemas.Project)
def unassign_project_analyst(
    project_id: int,
    user_id: int,
    db: Session = Depends(deps.get_db),
):
    link = (
        db.query(models.ProjectEmployee)
        .filter_by(projectId=project_id, userId=user_id)
        .first()
    )
    if link:
        db.delete(link)
        db.commit()
    project = db.query(models.Project).filter_by(id=project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Not found")
    return _project_with_analysts(project, db)

