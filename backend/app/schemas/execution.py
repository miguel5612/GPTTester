from datetime import datetime
from typing import List, Dict
from pydantic import BaseModel

from .execution_plan import ExecutionPlan
from .test import Test
from .action import Action
from .page_element import PageElement
from .page import Page


class Execution(BaseModel):
    id: int
    plan_id: int
    agent_id: int
    status: str
    started_at: datetime
    report_file: str | None = None
    report_received_at: datetime | None = None

    class Config:
        orm_mode = True


class PageElementWithPage(PageElement):
    page: Page


class AssignmentDetail(BaseModel):
    id: int
    parameters: Dict[str, str]
    action: Action
    element: PageElementWithPage

    class Config:
        orm_mode = True


class TestDetail(Test):
    assignments: List[AssignmentDetail] = []


class ExecutionDetail(BaseModel):
    id: int
    status: str
    started_at: datetime
    report_file: str | None = None
    report_received_at: datetime | None = None
    plan: ExecutionPlan
    test: TestDetail

    class Config:
        orm_mode = True

