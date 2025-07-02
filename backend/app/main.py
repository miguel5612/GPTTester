from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from .database import engine, SessionLocal
from . import models, schemas, deps
from .crud import create_crud_router


def seed_database() -> None:
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

        db.commit()
    finally:
        db.close()


models.Base.metadata.create_all(bind=engine)
seed_database()

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
        ("interactions", models.Interaction, schemas.Interaction),
        (
            "interactionparameters",
            models.InteractionParameter,
            schemas.InteractionParameter,
        ),
        (
            "interactionapprovalstates",
            models.InteractionApprovalState,
            schemas.InteractionApprovalState,
        ),
        (
            "interactionapprovals",
            models.InteractionApproval,
            schemas.InteractionApproval,
        ),
        ("tasks", models.Task, schemas.Task),
        (
            "taskhaveinteractions",
            models.TaskHaveInteraction,
            schemas.TaskHaveInteraction,
        ),
        ("validations", models.Validation, schemas.Validation),
        (
            "validationparameters",
            models.ValidationParameter,
            schemas.ValidationParameter,
        ),
        ("validationapprovals", models.ValidationApproval, schemas.ValidationApproval),
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
        ("scenariohasfeatures", models.ScenarioHasFeature, schemas.ScenarioHasFeature),
        ("featuresteps", models.FeatureStep, schemas.FeatureStep),
        ("scenarioinfo", models.ScenarioInfo, schemas.ScenarioInfo),
    ]
    for prefix, model, schema in mappings:
        app.include_router(create_crud_router(prefix, model, schema))


register_cruds()


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
