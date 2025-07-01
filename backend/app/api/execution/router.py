"""
Router para gestión de ejecuciones de pruebas
"""
from fastapi import APIRouter, Depends, HTTPException, status, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from ... import models, schemas, deps
from ...execution_monitor import monitor_manager

router = APIRouter(prefix="/api/execution", tags=["Execution"])


@router.post("/plans", response_model=schemas.ExecutionPlanResponse)
def create_execution_plan(
    plan_data: schemas.ExecutionPlanCreate,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user)
):
    """
    Crear un plan de ejecución para un flujo
    """
    # Validar que el flujo existe y pertenece al usuario
    flow = db.query(models.TestCase).filter(
        models.TestCase.id == plan_data.test_id,
        models.TestCase.owner_id == current_user.id
    ).first()
    
    if not flow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Flujo no encontrado"
        )
    
    # Validar que el agente existe
    agent = db.query(models.ExecutionAgent).filter(
        models.ExecutionAgent.id == plan_data.agent_id
    ).first()
    
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agente no encontrado"
        )
    
    # Crear plan
    plan = models.ExecutionPlan(
        nombre=plan_data.nombre,
        test_id=flow.id,
        agent_id=agent.id
    )
    
    db.add(plan)
    db.commit()
    db.refresh(plan)
    
    return schemas.ExecutionPlanResponse(
        id=plan.id,
        nombre=plan.nombre,
        test_id=plan.test_id,
        test_name=flow.name,
        agent_id=plan.agent_id,
        agent_alias=agent.alias
    )


@router.get("/plans", response_model=List[schemas.ExecutionPlanResponse])
def get_execution_plans(
    test_id: Optional[int] = None,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user)
):
    """
    Obtener planes de ejecución
    """
    query = db.query(models.ExecutionPlan).join(models.TestCase).filter(
        models.TestCase.owner_id == current_user.id
    )
    
    if test_id:
        query = query.filter(models.ExecutionPlan.test_id == test_id)
    
    plans = query.all()
    
    return [
        schemas.ExecutionPlanResponse(
            id=p.id,
            nombre=p.nombre,
            test_id=p.test_id,
            test_name=p.test.name,
            agent_id=p.agent_id,
            agent_alias=p.agent.alias
        )
        for p in plans
    ]


@router.post("/run/{plan_id}", response_model=schemas.ExecutionResponse)
def run_execution_plan(
    plan_id: int,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user)
):
    """
    Ejecutar un plan de ejecución
    """
    # Validar que el plan existe y pertenece al usuario
    plan = db.query(models.ExecutionPlan).join(models.TestCase).filter(
        models.ExecutionPlan.id == plan_id,
        models.TestCase.owner_id == current_user.id
    ).first()
    
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Plan de ejecución no encontrado"
        )
    
    # Verificar que el agente esté disponible
    agent = plan.agent
    if not agent.last_seen or (datetime.utcnow() - agent.last_seen).seconds > 300:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El agente no está disponible"
        )
    
    # Verificar que no haya ejecuciones pendientes en el agente
    pending = db.query(models.PlanExecution).filter(
        models.PlanExecution.agent_id == agent.id,
        models.PlanExecution.status.in_([
            models.ExecutionStatus.CALLING.value,
            models.ExecutionStatus.RUNNING.value
        ])
    ).first()
    
    if pending:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El agente tiene una ejecución en curso"
        )
    
    # Crear registro de ejecución
    execution = models.PlanExecution(
        plan_id=plan.id,
        agent_id=agent.id,
        status=models.ExecutionStatus.CALLING.value,
        started_at=datetime.utcnow()
    )
    
    db.add(execution)
    db.commit()
    db.refresh(execution)
    
    return schemas.ExecutionResponse(
        id=execution.id,
        plan_id=execution.plan_id,
        plan_name=plan.nombre,
        test_name=plan.test.name,
        agent_alias=agent.alias,
        status=execution.status,
        started_at=execution.started_at
    )


@router.get("/active", response_model=List[schemas.ExecutionResponse])
def get_active_executions(
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user)
):
    """
    Obtener ejecuciones activas del usuario
    """
    executions = db.query(models.PlanExecution).join(
        models.ExecutionPlan
    ).join(
        models.TestCase
    ).filter(
        models.TestCase.owner_id == current_user.id,
        models.PlanExecution.status.in_([
            models.ExecutionStatus.CALLING.value,
            models.ExecutionStatus.RUNNING.value
        ])
    ).order_by(models.PlanExecution.started_at.desc()).all()
    
    return [
        schemas.ExecutionResponse(
            id=e.id,
            plan_id=e.plan_id,
            plan_name=e.plan.nombre,
            test_name=e.plan.test.name,
            agent_alias=e.agent.alias,
            status=e.status,
            started_at=e.started_at
        )
        for e in executions
    ]


@router.get("/history", response_model=List[schemas.ExecutionResponse])
def get_execution_history(
    limit: int = 20,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user)
):
    """
    Obtener historial de ejecuciones
    """
    executions = db.query(models.PlanExecution).join(
        models.ExecutionPlan
    ).join(
        models.TestCase
    ).filter(
        models.TestCase.owner_id == current_user.id
    ).order_by(
        models.PlanExecution.started_at.desc()
    ).limit(limit).all()
    
    return [
        schemas.ExecutionResponse(
            id=e.id,
            plan_id=e.plan_id,
            plan_name=e.plan.nombre,
            test_name=e.plan.test.name,
            agent_alias=e.agent.alias,
            status=e.status,
            started_at=e.started_at
        )
        for e in executions
    ]


@router.get("/{execution_id}/logs", response_model=List[schemas.ExecutionLogResponse])
def get_execution_logs(
    execution_id: int,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user)
):
    """
    Obtener logs de una ejecución
    """
    # Validar que la ejecución pertenece al usuario
    execution = db.query(models.PlanExecution).join(
        models.ExecutionPlan
    ).join(
        models.TestCase
    ).filter(
        models.PlanExecution.id == execution_id,
        models.TestCase.owner_id == current_user.id
    ).first()
    
    if not execution:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ejecución no encontrada"
        )
    
    logs = db.query(models.ExecutionLog).filter(
        models.ExecutionLog.execution_id == execution_id
    ).order_by(models.ExecutionLog.timestamp).all()
    
    return [
        schemas.ExecutionLogResponse(
            id=log.id,
            message=log.message,
            timestamp=log.timestamp
        )
        for log in logs
    ]


@router.post("/{execution_id}/cancel")
def cancel_execution(
    execution_id: int,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user)
):
    """
    Cancelar una ejecución
    """
    # Validar que la ejecución pertenece al usuario
    execution = db.query(models.PlanExecution).join(
        models.ExecutionPlan
    ).join(
        models.TestCase
    ).filter(
        models.PlanExecution.id == execution_id,
        models.TestCase.owner_id == current_user.id
    ).first()
    
    if not execution:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ejecución no encontrada"
        )
    
    if execution.status == models.ExecutionStatus.FINISHED.value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La ejecución ya finalizó"
        )
    
    execution.status = "Cancelado"
    
    # Agregar log
    log = models.ExecutionLog(
        execution_id=execution_id,
        message="Ejecución cancelada por el usuario"
    )
    db.add(log)
    
    db.commit()
    
    # Notificar via websocket
    monitor_manager.broadcast_sync(
        execution_id,
        {"type": "cancel", "status": execution.status}
    )
    
    return {"message": "Ejecución cancelada"}


@router.websocket("/ws/{execution_id}")
async def execution_websocket(
    websocket: WebSocket,
    execution_id: int,
    token: str
):
    """
    WebSocket para monitoreo en tiempo real de ejecuciones
    """
    # Validar token
    try:
        payload = deps.verify_token(token)
    except:
        await websocket.close(code=1008)
        return
    
    await monitor_manager.connect(execution_id, websocket)
    
    try:
        while True:
            # Mantener conexión abierta
            await websocket.receive_text()
    except WebSocketDisconnect:
        await monitor_manager.disconnect(execution_id, websocket)
