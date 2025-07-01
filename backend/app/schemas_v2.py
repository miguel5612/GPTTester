"""
Schemas mejorados para la API del MVP
"""
from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


# ==============================================
# Schemas de Autenticación
# ==============================================

class UserRegister(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8)
    user_type: str = Field(..., description="analyst, service_manager, architect")
    
    @validator('user_type')
    def validate_user_type(cls, v):
        valid_types = ["analyst", "service_manager", "architect"]
        if v not in valid_types:
            raise ValueError(f"user_type debe ser uno de: {', '.join(valid_types)}")
        return v


class RoleResponse(BaseModel):
    id: int
    name: str
    
    class Config:
        orm_mode = True


class UserResponse(BaseModel):
    id: int
    username: str
    role: Optional[RoleResponse] = None
    is_active: bool
    
    class Config:
        orm_mode = True


class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse


# ==============================================
# Schemas de Workspace
# ==============================================

class ProjectOption(BaseModel):
    id: int
    name: str
    objetivo: Optional[str] = None
    
    class Config:
        orm_mode = True


class ClientOption(BaseModel):
    id: int
    name: str
    projects: List[ProjectOption] = []
    
    class Config:
        orm_mode = True


class WorkspaceOptions(BaseModel):
    clients: List[ClientOption]


class WorkspaceSelection(BaseModel):
    client_id: int
    project_id: Optional[int] = None


class ActorOption(BaseModel):
    id: int
    name: str
    
    class Config:
        orm_mode = True


class ActorCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)


class WorkspaceInfo(BaseModel):
    client_id: int
    client_name: str
    project_id: Optional[int] = None
    project_name: Optional[str] = None
    actors: List[ActorOption] = []


# ==============================================
# Schemas de Flujos
# ==============================================

class FlowPriority(str, Enum):
    ALTA = "alta"
    MEDIA = "media"
    BAJA = "baja"


class FlowStatus(str, Enum):
    NUEVO = "nuevo"
    MAPEANDO = "mapeando"
    PARAMETRIZANDO = "parametrizando"
    LISTO = "listo"


class FlowCreate(BaseModel):
    name: str = Field(..., min_length=3, max_length=200)
    description: Optional[str] = None
    priority: FlowPriority = FlowPriority.MEDIA
    given: str = Field(..., description="Contexto inicial del escenario")
    when: str = Field(..., description="Acción o evento que ocurre")
    then: str = Field(..., description="Resultado esperado")
    actor_id: int
    test_plan_id: Optional[int] = None


class FlowResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    priority: str
    status: str
    given: str
    when: str
    then: str
    actor_id: int
    actor_name: Optional[str]
    test_plan_id: Optional[int]
    created_by: str
    
    class Config:
        orm_mode = True


class ElementMap(BaseModel):
    page_name: str = Field(..., description="Nombre de la página")
    name: str = Field(..., description="Nombre del elemento")
    tipo: str = Field(..., description="button, input, select, link, etc")
    estrategia: str = Field(..., description="id, css, xpath, name")
    valor: str = Field(..., description="Selector del elemento")
    descripcion: Optional[str] = None


class ElementResponse(BaseModel):
    id: int
    name: str
    page: str
    tipo: str
    estrategia: str
    valor: str
    descripcion: Optional[str]
    
    class Config:
        orm_mode = True


class ActionAssign(BaseModel):
    element_id: int
    action_id: int
    parametros: Optional[str] = None


class ActionResponse(BaseModel):
    id: int
    name: str
    tipo: str
    codigo: str
    argumentos: Optional[str]
    
    class Config:
        orm_mode = True


class AssignmentResponse(BaseModel):
    id: int
    action_id: int
    element_id: int
    action_name: str
    element_name: str
    parametros: Optional[str]
    
    class Config:
        orm_mode = True


class FlowDetailResponse(FlowResponse):
    elements: List[ElementResponse] = []
    actions: List[ActionResponse] = []
    assignments: List[AssignmentResponse] = []


class FlowStatusUpdate(BaseModel):
    status: FlowStatus


class AgentInfo(BaseModel):
    id: int
    alias: str
    hostname: str
    os: str
    categoria: Optional[str]
    online: bool
    
    class Config:
        orm_mode = True


class ExecutionPlanInfo(BaseModel):
    id: int
    nombre: str
    agent_id: int
    
    class Config:
        orm_mode = True


class FlowExecuteInfo(BaseModel):
    flow_id: int
    flow_name: str
    available_agents: List[AgentInfo]
    execution_plans: List[ExecutionPlanInfo]


# ==============================================
# Schemas de Ejecución
# ==============================================

class ExecutionPlanCreate(BaseModel):
    nombre: str = Field(..., min_length=3, max_length=100)
    test_id: int
    agent_id: int


class ExecutionPlanResponse(BaseModel):
    id: int
    nombre: str
    test_id: int
    test_name: str
    agent_id: int
    agent_alias: str
    
    class Config:
        orm_mode = True


class ExecutionResponse(BaseModel):
    id: int
    plan_id: int
    plan_name: str
    test_name: str
    agent_alias: str
    status: str
    started_at: datetime
    
    class Config:
        orm_mode = True


class ExecutionLogResponse(BaseModel):
    id: int
    message: str
    timestamp: datetime
    
    class Config:
        orm_mode = True


# ==============================================
# Schemas compartidos existentes que seguimos usando
# ==============================================

class TestPlanBase(BaseModel):
    nombre: str = Field(..., min_length=5)
    objetivo: Optional[str] = None
    alcance: Optional[str] = None
    criterios_entrada: Optional[str] = None
    criterios_salida: Optional[str] = None
    estrategia: Optional[str] = None
    responsables: Optional[str] = None
    fecha_inicio: Optional[datetime] = None
    fecha_fin: Optional[datetime] = None
    historias_bdd: Optional[str] = None


class TestPlanCreate(TestPlanBase):
    pass


class TestPlan(TestPlanBase):
    id: int
    
    class Config:
        orm_mode = True


# Mantener los schemas existentes que aún se usan
from .schemas import (
    Role, RoleCreate,
    Permission, PermissionCreate,
    User, UserCreate, UserRoleUpdate, UserActiveUpdate,
    Client, ClientCreate,
    Project, ProjectCreate,
    Actor,
    Page, PageCreate,
    PageElement, PageElementCreate,
    Action, ActionCreate,
    ActionAssignment, ActionAssignmentCreate,
    Agent, AgentCreate, AgentRegister, AgentRegisterResponse,
    ExecutionPlan, ExecutionPlanCreate as OldExecutionPlanCreate,
    PlanExecution,
    ExecutionSchedule, ExecutionScheduleCreate,
    ExecutionLog,
    ExecutionUpdate,
    PendingExecution,
    AssignmentDetail,
    Workspace, WorkspaceCreate as OldWorkspaceCreate,
    Test, TestCreate,
    Metrics,
    AuditEvent,
    Secret, SecretCreate,
    MarketplaceComponent, MarketplaceComponentCreate,
    TestSuite, TestSuiteCreate,
    TestDependency,
    TestBranch, BranchCreate,
    TestCommit, CommitCreate,
    TestMerge, MergeCreate,
    TestVersion,
    DataObject, DataObjectAction, DataObjectHistory,
    Environment, EnvironmentConfig, EnvironmentCredential, EnvironmentSchedule,
    JiraIssueCreate, JiraTransition, PipelineTrigger
)
