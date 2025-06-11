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
