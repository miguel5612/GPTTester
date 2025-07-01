"""
Router para gestión de workspace
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from ... import models, schemas, deps

router = APIRouter(prefix="/api/workspace", tags=["Workspace"])


@router.get("/available", response_model=schemas.WorkspaceOptions)
def get_available_workspaces(
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user)
):
    """
    Obtener clientes y proyectos disponibles para el usuario
    """
    # Si es admin o gerente, ver todos los clientes
    if current_user.role and current_user.role.name in ["Administrador", "Gerente de servicios"]:
        clients = db.query(models.Client).filter(models.Client.is_active == True).all()
    else:
        # Solo clientes asignados
        clients = current_user.clients
    
    # Obtener proyectos del usuario
    if current_user.role and current_user.role.name in ["Administrador", "Gerente de servicios"]:
        projects = db.query(models.Project).filter(models.Project.is_active == True).all()
    else:
        projects = current_user.projects
    
    return schemas.WorkspaceOptions(
        clients=[
            schemas.ClientOption(
                id=c.id,
                name=c.name,
                projects=[
                    schemas.ProjectOption(
                        id=p.id,
                        name=p.name,
                        objetivo=p.objetivo
                    )
                    for p in projects if p.client_id == c.id
                ]
            )
            for c in clients
        ]
    )


@router.post("/select", response_model=schemas.WorkspaceInfo)
def select_workspace(
    selection: schemas.WorkspaceSelection,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user)
):
    """
    Seleccionar workspace activo
    """
    # Validar que el cliente existe
    client = db.query(models.Client).filter(
        models.Client.id == selection.client_id,
        models.Client.is_active == True
    ).first()
    
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cliente no encontrado"
        )
    
    # Validar que el proyecto pertenece al cliente
    project = None
    if selection.project_id:
        project = db.query(models.Project).filter(
            models.Project.id == selection.project_id,
            models.Project.client_id == client.id,
            models.Project.is_active == True
        ).first()
        
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Proyecto no encontrado o no pertenece al cliente"
            )
    
    # Buscar o crear workspace
    workspace = db.query(models.Workspace).filter(
        models.Workspace.user_id == current_user.id
    ).first()
    
    if workspace:
        workspace.client_id = client.id
        workspace.project_id = project.id if project else None
    else:
        workspace = models.Workspace(
            user_id=current_user.id,
            client_id=client.id,
            project_id=project.id if project else None
        )
        db.add(workspace)
    
    db.commit()
    db.refresh(workspace)
    
    return schemas.WorkspaceInfo(
        client_id=client.id,
        client_name=client.name,
        project_id=project.id if project else None,
        project_name=project.name if project else None,
        actors=[
            schemas.ActorOption(
                id=a.id,
                name=a.name
            )
            for a in db.query(models.Actor).filter(
                models.Actor.client_id == client.id
            ).all()
        ]
    )


@router.get("/current", response_model=schemas.WorkspaceInfo)
def get_current_workspace(
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user)
):
    """
    Obtener workspace actual
    """
    workspace = db.query(models.Workspace).filter(
        models.Workspace.user_id == current_user.id
    ).first()
    
    if not workspace:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No hay workspace seleccionado"
        )
    
    client = workspace.client
    project = workspace.project
    
    return schemas.WorkspaceInfo(
        client_id=client.id,
        client_name=client.name,
        project_id=project.id if project else None,
        project_name=project.name if project else None,
        actors=[
            schemas.ActorOption(
                id=a.id,
                name=a.name
            )
            for a in db.query(models.Actor).filter(
                models.Actor.client_id == client.id
            ).all()
        ]
    )


@router.post("/actors", response_model=schemas.ActorOption)
def create_actor(
    actor_data: schemas.ActorCreate,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user)
):
    """
    Crear un nuevo actor para el cliente actual
    """
    workspace = db.query(models.Workspace).filter(
        models.Workspace.user_id == current_user.id
    ).first()
    
    if not workspace:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Debe seleccionar un workspace primero"
        )
    
    # Crear actor
    actor = models.Actor(
        name=actor_data.name,
        client_id=workspace.client_id
    )
    
    db.add(actor)
    db.commit()
    db.refresh(actor)
    
    return schemas.ActorOption(
        id=actor.id,
        name=actor.name
    )
