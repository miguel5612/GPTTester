from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.responses import FileResponse
import os
from uuid import uuid4
from sqlalchemy.orm import Session
from typing import List

from ..database import get_db
from .. import schemas
from ..crud import (
    execution as crud_execution,
    agent as crud_agent,
    action_assignment as crud_assignment,
)
from ..utils import get_current_user

router = APIRouter(prefix="/executions", tags=["executions"])

@router.get("/pending", response_model=schemas.execution.ExecutionDetail)
def get_pending_execution(
    hostname: str,
    db: Session = Depends(get_db),
    current_user: schemas.user.User = Depends(get_current_user),
):
    if current_user.username != hostname:
        raise HTTPException(status_code=403, detail="Not authorized for this agent")

    agent = crud_agent.get_agent_by_hostname(db, hostname)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")

    execution = crud_execution.get_pending_execution_by_agent(db, agent.id)
    if not execution:
        raise HTTPException(status_code=404, detail="No pending executions")

    assignments = crud_assignment.get_assignments(db, test_id=execution.plan.test_id)

    assignment_details: List[schemas.execution.AssignmentDetail] = []
    for assign in assignments:
        element_with_page = schemas.execution.PageElementWithPage.from_orm(assign.element)
        element_with_page.page = schemas.page.Page.from_orm(assign.element.page)
        detail = schemas.execution.AssignmentDetail(
            id=assign.id,
            action=schemas.action.Action.from_orm(assign.action),
            element=element_with_page,
            parameters=assign.parameters,
        )
        assignment_details.append(detail)

    test_detail = schemas.execution.TestDetail(
        id=execution.plan.test.id,
        name=execution.plan.test.name,
        description=execution.plan.test.description,
        owner_id=execution.plan.test.owner_id,
        assignments=assignment_details,
    )

    return schemas.execution.ExecutionDetail(
        id=execution.id,
        status=execution.status,
        started_at=execution.started_at,
        report_file=execution.report_file,
        report_received_at=execution.report_received_at,
        plan=schemas.execution_plan.ExecutionPlan.from_orm(execution.plan),
        test=test_detail,
    )


@router.post("/{execution_id}/report", response_model=schemas.execution.Execution)
def upload_execution_report(
    execution_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: schemas.user.User = Depends(get_current_user),
):
    execution = crud_execution.get_execution(db, execution_id)
    if not execution:
        raise HTTPException(status_code=404, detail="Execution not found")
    if current_user.username != execution.agent.hostname:
        raise HTTPException(status_code=403, detail="Not authorized for this execution")

    if file.content_type not in ["application/pdf", "application/zip", "application/x-zip-compressed"]:
        raise HTTPException(status_code=400, detail="Invalid file type")

    contents = file.file.read()
    if len(contents) > 10 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File too large")

    os.makedirs("backend/reports", exist_ok=True)
    safe_name = f"{uuid4().hex}_{os.path.basename(file.filename)}"
    path = os.path.join("backend", "reports", safe_name)
    with open(path, "wb") as out:
        out.write(contents)

    updated = crud_execution.save_execution_report(db, execution_id, path)
    return schemas.execution.Execution.from_orm(updated)


@router.get("/{execution_id}/report")
def download_execution_report(
    execution_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.user.User = Depends(get_current_user),
):
    execution = crud_execution.get_execution(db, execution_id)
    if not execution or not execution.report_file:
        raise HTTPException(status_code=404, detail="Report not found")
    if current_user.username != execution.agent.hostname and "Administrador" not in [r.name for r in current_user.roles]:
        raise HTTPException(status_code=403, detail="Not authorized for this execution")
    if not os.path.exists(execution.report_file):
        raise HTTPException(status_code=404, detail="File missing")
    return FileResponse(execution.report_file, filename=os.path.basename(execution.report_file))
