from pydantic import BaseModel, Field, root_validator
from typing import List, Optional
from datetime import date


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


class TestPlanBase(BaseModel):
    nombre: str = Field(..., min_length=5)
    objetivo: Optional[str] = None
    alcance: Optional[str] = None
    criterios_entrada: Optional[str] = None
    criterios_salida: Optional[str] = None
    estrategia: Optional[str] = None
    responsables: Optional[str] = None
    fecha_inicio: Optional[date] = None
    fecha_fin: Optional[date] = None
    historias_bdd: Optional[str] = None


class TestPlanCreate(TestPlanBase):
    @root_validator
    def validate_dates(cls, values):
        start = values.get("fecha_inicio")
        end = values.get("fecha_fin")
        if start and end and start > end:
            raise ValueError("fecha_inicio must be before fecha_fin")
        return values


class TestPlan(TestPlanBase):
    id: int

    class Config:
        orm_mode = True
