from pydantic import BaseModel
from typing import List, Optional


class RoleBase(BaseModel):
    name: str


class RoleCreate(RoleBase):
    pass


class Role(RoleBase):
    id: int

    class Config:
        orm_mode = True

class TestBase(BaseModel):
    name: str
    description: Optional[str] = None

class TestCreate(TestBase):
    pass

class Test(TestBase):
    id: int
    owner_id: int

    class Config:
        orm_mode = True

class UserBase(BaseModel):
    username: str

class UserCreate(UserBase):
    password: str


class UserRoleUpdate(BaseModel):
    role_id: int

class User(UserBase):
    id: int
    is_active: bool
    role: Role
    tests: List[Test] = []
    projects: List["Project"] = []

    class Config:
        orm_mode = True


class ClientBase(BaseModel):
    name: str


class ClientCreate(ClientBase):
    pass


class Client(ClientBase):
    id: int
    is_active: bool

    class Config:
        orm_mode = True


class ProjectBase(BaseModel):
    name: str
    client_id: int


class ProjectCreate(ProjectBase):
    pass


class Project(ProjectBase):
    id: int
    is_active: bool
    analysts: List[User] = []

    class Config:
        orm_mode = True
