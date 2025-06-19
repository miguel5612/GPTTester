from pydantic import BaseModel, Field, root_validator
from typing import List, Optional
from datetime import date, datetime


class RoleBase(BaseModel):
    name: str


class RoleCreate(RoleBase):
    pass


class Role(RoleBase):
    id: int

    class Config:
        orm_mode = True


class PermissionBase(BaseModel):
    page: str


class PermissionCreate(PermissionBase):
    pass


class Permission(PermissionBase):
    id: int
    role_id: int

    class Config:
        orm_mode = True


class TestBase(BaseModel):
    name: str
    description: Optional[str] = None
    priority: Optional[str] = None
    status: Optional[str] = None
    given: Optional[str] = None
    when: Optional[str] = None
    then: Optional[str] = None
    test_plan_id: Optional[int] = None
    actor_id: Optional[int] = None


class TestCreate(TestBase):
    pass


class Test(TestBase):
    id: int
    owner_id: int
    actions: List["Action"] = []

    class Config:
        orm_mode = True


class UserBase(BaseModel):
    username: str


class UserCreate(UserBase):
    password: str


class UserRoleUpdate(BaseModel):
    role_id: int


class UserActiveUpdate(BaseModel):
    is_active: bool


class User(UserBase):
    id: int
    last_login: Optional[datetime] = None
    is_active: bool
    role: Role

    class Config:
        orm_mode = True


class UserSummary(UserBase):
    id: int
    last_login: Optional[datetime] = None
    is_active: bool
    role: Role

    class Config:
        orm_mode = True


class ClientBase(BaseModel):
    name: str


class ClientCreate(ClientBase):
    pass


class Client(ClientBase):
    id: int
    is_active: bool
    analysts: List[UserSummary] = []
    dedication: int | None = None

    class Config:
        orm_mode = True


class ProjectBase(BaseModel):
    name: str
    client_id: int
    objetivo: Optional[str] = None


class ProjectCreate(ProjectBase):
    pass


class Project(ProjectBase):
    id: int
    is_active: bool
    analysts: List[UserSummary] = []
    scripts_per_day: Optional[int] = None
    test_types: Optional[str] = None

    class Config:
        orm_mode = True


class ActorBase(BaseModel):
    name: str
    client_id: int


class ActorCreate(ActorBase):
    pass


class Actor(ActorBase):
    id: int

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
    @root_validator(skip_on_failure=True)
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


class PageBase(BaseModel):
    name: str


class PageCreate(PageBase):
    pass


class Page(PageBase):
    id: int

    class Config:
        orm_mode = True


class PageElementBase(BaseModel):
    page_id: int
    name: str
    tipo: str
    estrategia: str
    valor: str
    descripcion: Optional[str] = None


class PageElementCreate(PageElementBase):
    pass


class PageElement(PageElementBase):
    id: int

    class Config:
        orm_mode = True


class ActionBase(BaseModel):
    name: str
    tipo: str
    codigo: str
    argumentos: Optional[str] = None


class ActionCreate(ActionBase):
    pass


class Action(ActionBase):
    id: int

    class Config:
        orm_mode = True


class ActionAssignmentBase(BaseModel):
    action_id: int
    element_id: int
    test_id: int
    parametros: dict[str, str] | None = None


class ActionAssignmentCreate(ActionAssignmentBase):
    pass


class ActionAssignment(ActionAssignmentBase):
    id: int

    class Config:
        orm_mode = True


class AgentBase(BaseModel):
    alias: str = Field(..., min_length=1)
    hostname: str = Field(..., min_length=1)
    os: str = Field(...)
    categoria: Optional[str] = None

    @root_validator(skip_on_failure=True)
    def validate_fields(cls, values):
        os_val = values.get("os")
        categoria = values.get("categoria")
        allowed = ["Windows", "Linux", "Mac", "Android", "iOS"]
        if os_val not in allowed:
            raise ValueError("Invalid operating system")
        if categoria:
            if categoria != "granja m\u00f3vil":
                raise ValueError("Invalid categoria")
            if os_val not in ["Android", "iOS"]:
                raise ValueError("categoria only allowed for Android/iOS agents")
        return values


class AgentCreate(AgentBase):
    pass


class Agent(AgentBase):
    id: int

    class Config:
        orm_mode = True


class AgentRegister(AgentBase):
    capabilities: Optional[str] = None


class AgentRegisterResponse(BaseModel):
    api_key: str
    agent_id: int


class AgentStatusUpdate(BaseModel):
    execution_id: int
    status: Optional[str] = None
    log: Optional[str] = None

    class Config:
        orm_mode = True


class ExecutionPlanBase(BaseModel):
    nombre: str
    test_id: int
    agent_id: int


class ExecutionPlanCreate(ExecutionPlanBase):
    pass


class ExecutionPlan(ExecutionPlanBase):
    id: int

    class Config:
        orm_mode = True


class PlanExecutionBase(BaseModel):
    plan_id: int
    agent_id: int
    status: str
    started_at: datetime


class PlanExecution(PlanExecutionBase):
    id: int

    class Config:
        orm_mode = True


class AssignmentDetail(BaseModel):
    action: Action
    element: PageElement
    parametros: dict[str, str] | None = None


class PendingExecution(BaseModel):
    execution_id: int
    plan: ExecutionPlan
    test: Test
    assignments: list[AssignmentDetail]


class ClientDetail(Client):
    projects: List[Project] = []


class Metrics(BaseModel):
    clients: List[ClientDetail]
    flows: List[Test]


class WorkspaceBase(BaseModel):
    client_id: int
    project_id: Optional[int] = None


class WorkspaceCreate(WorkspaceBase):
    pass


class Workspace(WorkspaceBase):
    id: int
    user_id: int

    class Config:
        orm_mode = True


class ExecutionLogBase(BaseModel):
    execution_id: int
    message: str
    timestamp: datetime


class ExecutionLog(ExecutionLogBase):
    id: int

    class Config:
        orm_mode = True


class ExecutionUpdate(BaseModel):
    status: Optional[str] = None
    log: Optional[str] = None
    progress: Optional[int] = None
    screenshot: Optional[str] = None


class ExecutionScheduleBase(BaseModel):
    plan_id: int
    run_at: datetime
    agent_id: Optional[int] = None


class ExecutionScheduleCreate(ExecutionScheduleBase):
    pass


class ExecutionSchedule(ExecutionScheduleBase):
    id: int
    executed: bool

    class Config:
        orm_mode = True
