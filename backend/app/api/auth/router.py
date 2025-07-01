"""
Router de autenticación mejorado con endpoints claros y seguros
"""
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Optional

from ... import models, schemas, deps

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


@router.post("/register", response_model=schemas.UserResponse)
def register(
    user_data: schemas.UserRegister,
    db: Session = Depends(deps.get_db)
):
    """
    Registro de nuevos usuarios con validaciones mejoradas
    """
    # Validar que el username no exista
    if db.query(models.User).filter(models.User.username == user_data.username).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El nombre de usuario ya está registrado"
        )
    
    # Validar contraseña
    if len(user_data.password) < 8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La contraseña debe tener al menos 8 caracteres"
        )
    
    # Asignar rol por defecto según el tipo seleccionado
    role_mapping = {
        "analyst": "Analista de Pruebas con skill de automatización",
        "service_manager": "Gerente de servicios",
        "architect": "Arquitecto de Automatización"
    }
    
    role_name = role_mapping.get(user_data.user_type, "Analista de Pruebas con skill de automatización")
    role = db.query(models.Role).filter(models.Role.name == role_name).first()
    
    if not role:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error en la configuración de roles"
        )
    
    # Crear usuario
    hashed_password = deps.get_password_hash(user_data.password)
    new_user = models.User(
        username=user_data.username,
        hashed_password=hashed_password,
        role_id=role.id,
        is_active=True
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return schemas.UserResponse(
        id=new_user.id,
        username=new_user.username,
        role=schemas.RoleResponse(id=role.id, name=role.name),
        is_active=new_user.is_active
    )


@router.post("/login", response_model=schemas.TokenResponse)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(deps.get_db)
):
    """
    Login mejorado con respuesta clara
    """
    user = deps.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Usuario desactivado"
        )
    
    # Actualizar último login
    user.last_login = datetime.utcnow()
    db.commit()
    
    # Crear token
    access_token = deps.create_access_token(
        data={
            "sub": user.username,
            "user_id": user.id,
            "role_id": user.role_id,
            "role_name": user.role.name if user.role else None
        }
    )
    
    return schemas.TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user=schemas.UserResponse(
            id=user.id,
            username=user.username,
            role=schemas.RoleResponse(id=user.role.id, name=user.role.name) if user.role else None,
            is_active=user.is_active
        )
    )


@router.get("/me", response_model=schemas.UserResponse)
def get_current_user(
    current_user: models.User = Depends(deps.get_current_user)
):
    """
    Obtener información del usuario actual
    """
    return schemas.UserResponse(
        id=current_user.id,
        username=current_user.username,
        role=schemas.RoleResponse(
            id=current_user.role.id, 
            name=current_user.role.name
        ) if current_user.role else None,
        is_active=current_user.is_active
    )


@router.post("/logout")
def logout(
    current_user: models.User = Depends(deps.get_current_user)
):
    """
    Logout endpoint (principalmente para limpiar en el cliente)
    """
    # En JWT no hay logout real del lado del servidor
    # Este endpoint existe para que el frontend sepa que debe limpiar el token
    return {"message": "Sesión cerrada exitosamente"}


@router.get("/permissions")
def get_my_permissions(
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user)
):
    """
    Obtener permisos del usuario actual
    """
    if not current_user.role:
        return {"permissions": []}
    
    permissions = db.query(models.PagePermission).filter(
        models.PagePermission.role_id == current_user.role_id
    ).all()
    
    return {
        "permissions": [p.page for p in permissions],
        "role": current_user.role.name
    }
