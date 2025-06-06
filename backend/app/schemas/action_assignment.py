from typing import Dict
from pydantic import BaseModel


class ActionAssignmentBase(BaseModel):
    action_id: int
    element_id: int
    test_id: int
    parameters: Dict[str, str]


class ActionAssignmentCreate(ActionAssignmentBase):
    pass


class ActionAssignmentUpdate(ActionAssignmentBase):
    pass


class ActionAssignment(ActionAssignmentBase):
    id: int

    class Config:
        orm_mode = True

