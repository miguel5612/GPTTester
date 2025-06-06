from pydantic import BaseModel
from typing import List, Optional
from .project import Project


class ClientBase(BaseModel):
    name: str
    is_active: Optional[bool] = True


class ClientCreate(ClientBase):
    pass


class ClientUpdate(ClientBase):
    pass


class Client(ClientBase):
    id: int
    projects: List[Project] = []

    class Config:
        orm_mode = True
