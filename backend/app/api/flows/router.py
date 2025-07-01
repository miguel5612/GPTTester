"""
Router para gestión de flujos de prueba con proceso guiado
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from ... import models, schemas, deps

router = APIRouter(prefix="/api/flows", tags=["Test Flows"])


@router.post("/create", response_model=schemas.FlowResponse)
def create_flow(
    flow_data: schemas.FlowCreate,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user)
):
    """
    Crear un nuevo flujo de prueba
    """
    # Validar que el actor existe y pertenece al cliente del workspace
    workspace = db.query(models.Workspace).filter(
        models.Workspace.user_id == current_user.id
    ).first()
    
    if not workspace:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Debe seleccionar un workspace primero"
        )
    
    actor = db.query(models.Actor).filter(
        models.Actor.id == flow_data.actor_id,
        models.Actor.client_id == workspace.client_id
    ).first()
    
    if not actor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Actor no encontrado o no pertenece al cliente actual"
        )
    
    # Crear el flujo
    new_flow = models.TestCase(
        name=flow_data.name,
        description=flow_data.description,
        priority=flow_data.priority,
        status="nuevo",
        given=flow_data.given,
        when=flow_data.when,
        then=flow_data.then,
        actor_id=actor.id,
        owner_id=current_user.id,
        test_plan_id=flow_data.test_plan_id
    )
    
    db.add(new_flow)
    db.commit()
    db.refresh(new_flow)
    
    return _flow_to_response(new_flow)


@router.get("/my-flows", response_model=List[schemas.FlowResponse])
def get_my_flows(
    status: Optional[str] = None,
    priority: Optional[str] = None,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user)
):
    """
    Obtener flujos del usuario actual
    """
    query = db.query(models.TestCase).filter(
        models.TestCase.owner_id == current_user.id
    )
    
    if status:
        query = query.filter(models.TestCase.status == status)
    
    if priority:
        query = query.filter(models.TestCase.priority == priority)
    
    flows = query.order_by(models.TestCase.id.desc()).all()
    
    return [_flow_to_response(flow) for flow in flows]


@router.get("/{flow_id}", response_model=schemas.FlowDetailResponse)
def get_flow_detail(
    flow_id: int,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user)
):
    """
    Obtener detalle completo de un flujo
    """
    flow = db.query(models.TestCase).filter(
        models.TestCase.id == flow_id,
        models.TestCase.owner_id == current_user.id
    ).first()
    
    if not flow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Flujo no encontrado"
        )
    
    # Obtener elementos y acciones asociadas
    assignments = db.query(models.ActionAssignment).filter(
        models.ActionAssignment.test_id == flow_id
    ).all()
    
    return schemas.FlowDetailResponse(
        **_flow_to_response(flow).dict(),
        elements=[
            schemas.ElementResponse(
                id=element.id,
                name=element.name,
                page=element.page.name if element.page else None,
                tipo=element.tipo,
                estrategia=element.estrategia,
                valor=element.valor,
                descripcion=element.descripcion
            )
            for element in flow.elements
        ],
        actions=[
            schemas.ActionResponse(
                id=action.id,
                name=action.name,
                tipo=action.tipo,
                codigo=action.codigo,
                argumentos=action.argumentos
            )
            for action in flow.actions
        ],
        assignments=[
            schemas.AssignmentResponse(
                id=a.id,
                action_id=a.action_id,
                element_id=a.element_id,
                action_name=a.action.name,
                element_name=a.element.name,
                parametros=a.parametros
            )
            for a in assignments
        ]
    )


@router.post("/{flow_id}/map-element", response_model=schemas.ElementResponse)
def map_element_to_flow(
    flow_id: int,
    element_data: schemas.ElementMap,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user)
):
    """
    Mapear un elemento a un flujo
    """
    flow = db.query(models.TestCase).filter(
        models.TestCase.id == flow_id,
        models.TestCase.owner_id == current_user.id
    ).first()
    
    if not flow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Flujo no encontrado"
        )
    
    # Crear o buscar página
    page = db.query(models.Page).filter(
        models.Page.name == element_data.page_name
    ).first()
    
    if not page:
        page = models.Page(name=element_data.page_name)
        db.add(page)
        db.commit()
        db.refresh(page)
    
    # Crear elemento
    element = models.PageElement(
        page_id=page.id,
        name=element_data.name,
        tipo=element_data.tipo,
        estrategia=element_data.estrategia,
        valor=element_data.valor,
        descripcion=element_data.descripcion
    )
    
    try:
        db.add(element)
        db.commit()
        db.refresh(element)
    except Exception:
        db.rollback()
        # Si ya existe, buscar el elemento
        element = db.query(models.PageElement).filter(
            models.PageElement.page_id == page.id,
            models.PageElement.name == element_data.name
        ).first()
    
    # Asociar al flujo
    if element not in flow.elements:
        flow.elements.append(element)
        db.commit()
    
    return schemas.ElementResponse(
        id=element.id,
        name=element.name,
        page=page.name,
        tipo=element.tipo,
        estrategia=element.estrategia,
        valor=element.valor,
        descripcion=element.descripcion
    )


@router.post("/{flow_id}/assign-action", response_model=schemas.AssignmentResponse)
def assign_action_to_element(
    flow_id: int,
    assignment_data: schemas.ActionAssign,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user)
):
    """
    Asignar una acción a un elemento en el flujo
    """
    flow = db.query(models.TestCase).filter(
        models.TestCase.id == flow_id,
        models.TestCase.owner_id == current_user.id
    ).first()
    
    if not flow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Flujo no encontrado"
        )
    
    # Verificar que el elemento y la acción existen
    element = db.query(models.PageElement).filter(
        models.PageElement.id == assignment_data.element_id
    ).first()
    
    action = db.query(models.AutomationAction).filter(
        models.AutomationAction.id == assignment_data.action_id
    ).first()
    
    if not element or not action:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Elemento o acción no encontrados"
        )
    
    # Crear asignación
    assignment = models.ActionAssignment(
        action_id=action.id,
        element_id=element.id,
        test_id=flow_id,
        parametros=assignment_data.parametros
    )
    
    try:
        db.add(assignment)
        db.commit()
        db.refresh(assignment)
    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Esta asignación ya existe"
        )
    
    return schemas.AssignmentResponse(
        id=assignment.id,
        action_id=assignment.action_id,
        element_id=assignment.element_id,
        action_name=action.name,
        element_name=element.name,
        parametros=assignment.parametros
    )


@router.put("/{flow_id}/status", response_model=schemas.FlowResponse)
def update_flow_status(
    flow_id: int,
    status_data: schemas.FlowStatusUpdate,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user)
):
    """
    Actualizar el estado de un flujo
    """
    flow = db.query(models.TestCase).filter(
        models.TestCase.id == flow_id,
        models.TestCase.owner_id == current_user.id
    ).first()
    
    if not flow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Flujo no encontrado"
        )
    
    flow.status = status_data.status
    db.commit()
    db.refresh(flow)
    
    return _flow_to_response(flow)


@router.get("/{flow_id}/execute-info", response_model=schemas.FlowExecuteInfo)
def get_flow_execution_info(
    flow_id: int,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user)
):
    """
    Obtener información necesaria para ejecutar un flujo
    """
    flow = db.query(models.TestCase).filter(
        models.TestCase.id == flow_id,
        models.TestCase.owner_id == current_user.id
    ).first()
    
    if not flow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Flujo no encontrado"
        )
    
    # Verificar que el flujo está listo
    if flow.status != "listo":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El flujo debe estar en estado 'listo' para ejecutarse"
        )
    
    # Obtener agentes disponibles
    agents = db.query(models.ExecutionAgent).filter(
        models.ExecutionAgent.last_seen >= datetime.utcnow() - timedelta(minutes=5)
    ).all()
    
    # Obtener planes de ejecución existentes
    plans = db.query(models.ExecutionPlan).filter(
        models.ExecutionPlan.test_id == flow_id
    ).all()
    
    return schemas.FlowExecuteInfo(
        flow_id=flow_id,
        flow_name=flow.name,
        available_agents=[
            schemas.AgentInfo(
                id=a.id,
                alias=a.alias,
                hostname=a.hostname,
                os=a.os,
                categoria=a.categoria,
                online=True
            )
            for a in agents
        ],
        execution_plans=[
            schemas.ExecutionPlanInfo(
                id=p.id,
                nombre=p.nombre,
                agent_id=p.agent_id
            )
            for p in plans
        ]
    )


def _flow_to_response(flow: models.TestCase) -> schemas.FlowResponse:
    """Helper para convertir modelo a response"""
    return schemas.FlowResponse(
        id=flow.id,
        name=flow.name,
        description=flow.description,
        priority=flow.priority,
        status=flow.status,
        given=flow.given,
        when=flow.when,
        then=flow.then,
        actor_id=flow.actor_id,
        actor_name=flow.actor.name if flow.actor else None,
        test_plan_id=flow.test_plan_id,
        created_by=flow.owner.username
    )
