from pydantic import BaseModel
from typing import List, Optional
from .user import User


class ProjectBase(BaseModel):
    name: str
    client_id: int
    is_active: Optional[bool] = True


class ProjectCreate(ProjectBase):
    pass


class ProjectUpdate(ProjectBase):
    pass


class Project(ProjectBase):
    id: int
    analysts: List[User] = []

    class Config:
        orm_mode = True
