from pydantic import BaseModel
from typing import Optional


class ExecutionPlanBase(BaseModel):
    nombre: str
    test_id: int
    agent_id: int


class ExecutionPlanCreate(ExecutionPlanBase):
    pass


class ExecutionPlanUpdate(ExecutionPlanBase):
    pass


class ExecutionPlan(ExecutionPlanBase):
    id: int

    class Config:
        orm_mode = True
