from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    ForeignKey,
    Table,
    Date,
    DateTime,
    UniqueConstraint,
)
import enum
from datetime import datetime
from sqlalchemy.orm import relationship
from .database import Base


class DataState(str, enum.Enum):
    NEW = "nuevo"
    USED = "usado"
    BLOCKED = "bloqueado"


class Role(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)


class PagePermission(Base):
    __tablename__ = "permissions"
    __table_args__ = (UniqueConstraint("role_id", "page", name="uix_role_page"),)

    id = Column(Integer, primary_key=True, index=True)
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=False)
    page = Column(String, nullable=False)

    role = relationship("Role", backref="permissions")


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role_id = Column(Integer, ForeignKey("roles.id"))
    last_login = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)
    role = relationship("Role")
    tests = relationship("TestCase", back_populates="owner")
    projects = relationship(
        "Project",
        secondary="project_analysts",
        back_populates="analysts",
    )
    clients = relationship(
        "Client",
        secondary="client_analysts",
        back_populates="analysts",
    )


class TestCase(Base):
    __tablename__ = "tests"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String, nullable=True)
    priority = Column(String, nullable=True)
    status = Column(String, nullable=True)
    given = Column(String, nullable=True)
    when = Column(String, nullable=True)
    then = Column(String, nullable=True)
    test_plan_id = Column(Integer, ForeignKey("testplans.id"), nullable=True)
    actor_id = Column(Integer, ForeignKey("actors.id"), nullable=True)
    owner_id = Column(Integer, ForeignKey("users.id"))

    owner = relationship("User", back_populates="tests")
    elements = relationship(
        "PageElement",
        secondary="element_flows",
        back_populates="tests",
    )
    actions = relationship(
        "AutomationAction",
        secondary="test_actions",
        back_populates="tests",
    )
    actor = relationship("Actor")
    plan = relationship("TestPlan")


project_analysts = Table(
    "project_analysts",
    Base.metadata,
    Column("project_id", Integer, ForeignKey("projects.id"), primary_key=True),
    Column("user_id", Integer, ForeignKey("users.id"), primary_key=True),
    Column("scripts_per_day", Integer, nullable=True),
    Column("test_types", String, nullable=True),
)


client_analysts = Table(
    "client_analysts",
    Base.metadata,
    Column("client_id", Integer, ForeignKey("clients.id"), primary_key=True),
    Column("user_id", Integer, ForeignKey("users.id"), primary_key=True),
    Column("dedication", Integer, nullable=True),
)


class Client(Base):
    __tablename__ = "clients"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    is_active = Column(Boolean, default=True)
    projects = relationship("Project", back_populates="client")
    actors = relationship("Actor", back_populates="client")
    analysts = relationship(
        "User",
        secondary=client_analysts,
        back_populates="clients",
    )


class Actor(Base):
    __tablename__ = "actors"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)

    client = relationship("Client", back_populates="actors")


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
    objetivo = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)

    client = relationship("Client", back_populates="projects")
    analysts = relationship(
        "User",
        secondary=project_analysts,
        back_populates="projects",
    )


class TestPlan(Base):
    __tablename__ = "testplans"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    objetivo = Column(String, nullable=True)
    alcance = Column(String, nullable=True)
    criterios_entrada = Column(String, nullable=True)
    criterios_salida = Column(String, nullable=True)
    estrategia = Column(String, nullable=True)
    responsables = Column(String, nullable=True)
    fecha_inicio = Column(Date, nullable=True)
    fecha_fin = Column(Date, nullable=True)
    historias_bdd = Column(String, nullable=True)


element_flows = Table(
    "element_flows",
    Base.metadata,
    Column("element_id", Integer, ForeignKey("page_elements.id"), primary_key=True),
    Column("test_id", Integer, ForeignKey("tests.id"), primary_key=True),
)


class Page(Base):
    __tablename__ = "pages"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)

    elements = relationship("PageElement", back_populates="page")


class PageElement(Base):
    __tablename__ = "page_elements"
    __table_args__ = (
        UniqueConstraint("page_id", "name", name="uix_page_element_name"),
    )

    id = Column(Integer, primary_key=True, index=True)
    page_id = Column(Integer, ForeignKey("pages.id"), nullable=False)
    name = Column(String, nullable=False)
    tipo = Column(String, nullable=False)
    estrategia = Column(String, nullable=False)
    valor = Column(String, nullable=False)
    descripcion = Column(String, nullable=True)

    page = relationship("Page", back_populates="elements")
    tests = relationship(
        "TestCase",
        secondary=element_flows,
        back_populates="elements",
    )


test_actions = Table(
    "test_actions",
    Base.metadata,
    Column("test_id", Integer, ForeignKey("tests.id"), primary_key=True),
    Column("action_id", Integer, ForeignKey("actions.id"), primary_key=True),
)


class AutomationAction(Base):
    __tablename__ = "actions"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    tipo = Column(String, nullable=False)
    codigo = Column(String, nullable=False)
    argumentos = Column(String, nullable=True)

    tests = relationship(
        "TestCase",
        secondary=test_actions,
        back_populates="actions",
    )


class ActionAssignment(Base):
    __tablename__ = "action_assignments"
    __table_args__ = (
        UniqueConstraint("action_id", "element_id", "test_id", name="uix_assign"),
    )

    id = Column(Integer, primary_key=True, index=True)
    action_id = Column(Integer, ForeignKey("actions.id"), nullable=False)
    element_id = Column(Integer, ForeignKey("page_elements.id"), nullable=False)
    test_id = Column(Integer, ForeignKey("tests.id"), nullable=False)
    parametros = Column(String, nullable=True)

    action = relationship("AutomationAction")
    element = relationship("PageElement")
    test = relationship("TestCase")


class ExecutionAgent(Base):
    __tablename__ = "agents"
    id = Column(Integer, primary_key=True, index=True)
    alias = Column(String, nullable=False)
    hostname = Column(String, unique=True, nullable=False)
    os = Column(String, nullable=False)
    categoria = Column(String, nullable=True)
    api_key = Column(String, unique=True, nullable=False)
    last_seen = Column(DateTime, nullable=True)
    capabilities = Column(String, nullable=True)


class ExecutionPlan(Base):
    __tablename__ = "execution_plans"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    test_id = Column(Integer, ForeignKey("tests.id"), nullable=False)
    agent_id = Column(Integer, ForeignKey("agents.id"), nullable=False)

    test = relationship("TestCase")
    agent = relationship("ExecutionAgent")


class ExecutionStatus(str, enum.Enum):
    CALLING = "Llamando al agente"
    RUNNING = "En ejecucion"
    FINISHED = "Finalizado"


class ExecutionSchedule(Base):
    __tablename__ = "execution_schedules"

    id = Column(Integer, primary_key=True, index=True)
    plan_id = Column(Integer, ForeignKey("execution_plans.id"), nullable=False)
    agent_id = Column(Integer, ForeignKey("agents.id"), nullable=True)
    run_at = Column(DateTime, nullable=False)
    executed = Column(Boolean, default=False)

    plan = relationship("ExecutionPlan")
    agent = relationship("ExecutionAgent")


class PlanExecution(Base):
    __tablename__ = "execution_records"

    id = Column(Integer, primary_key=True, index=True)
    plan_id = Column(Integer, ForeignKey("execution_plans.id"), nullable=False)
    agent_id = Column(Integer, ForeignKey("agents.id"), nullable=False)
    status = Column(String, nullable=False, default=ExecutionStatus.CALLING.value)
    started_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    plan = relationship("ExecutionPlan")
    agent = relationship("ExecutionAgent")


class ExecutionLog(Base):
    __tablename__ = "execution_logs"

    id = Column(Integer, primary_key=True, index=True)
    execution_id = Column(Integer, ForeignKey("execution_records.id"), nullable=False)
    message = Column(String, nullable=False)
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow)

    execution = relationship("PlanExecution", backref="logs")


class Workspace(Base):
    __tablename__ = "workspaces"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=True)

    user = relationship("User")
    client = relationship("Client")
    project = relationship("Project")


class DataPool(Base):
    __tablename__ = "data_pools"

    id = Column(Integer, primary_key=True, index=True)
    type = Column(String, nullable=False)
    environment = Column(String, nullable=False)

    __table_args__ = (
        UniqueConstraint("type", "environment", name="uix_type_env"),
    )

    objects = relationship("TestDataObject", back_populates="pool")


class TestDataObject(Base):
    __tablename__ = "test_data_objects"

    id = Column(Integer, primary_key=True, index=True)
    pool_id = Column(Integer, ForeignKey("data_pools.id"), nullable=False)
    data = Column(String, nullable=False)
    state = Column(String, nullable=False, default=DataState.NEW.value)

    pool = relationship("DataPool", back_populates="objects")
    history = relationship(
        "DataObjectHistory",
        back_populates="obj",
        cascade="all, delete-orphan",
    )


class DataObjectHistory(Base):
    __tablename__ = "data_object_history"

    id = Column(Integer, primary_key=True, index=True)
    object_id = Column(Integer, ForeignKey("test_data_objects.id"), nullable=False)
    action = Column(String, nullable=False)
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow)

    obj = relationship("TestDataObject", back_populates="history")


# -----------------------------------------------------
# Environment management models
# -----------------------------------------------------

class EnvironmentType(str, enum.Enum):
    QA = "QA"
    UAT = "UAT"
    PREPROD = "PREPROD"
    PROD = "PROD"


class Environment(Base):
    __tablename__ = "environments"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    name = Column(String, nullable=False)
    capacity_limit = Column(Integer, nullable=True)
    is_active = Column(Boolean, default=True)

    project = relationship("Project", backref="environments")
    config = relationship(
        "EnvironmentConfig", uselist=False, back_populates="environment"
    )
    credentials = relationship(
        "EnvironmentCredential", uselist=False, back_populates="environment"
    )
    schedules = relationship("EnvironmentSchedule", back_populates="environment")


class EnvironmentConfig(Base):
    __tablename__ = "environment_configs"

    id = Column(Integer, primary_key=True, index=True)
    environment_id = Column(Integer, ForeignKey("environments.id"), nullable=False)
    settings = Column(String, nullable=True)

    environment = relationship("Environment", back_populates="config")


class EnvironmentCredential(Base):
    __tablename__ = "environment_credentials"

    id = Column(Integer, primary_key=True, index=True)
    environment_id = Column(Integer, ForeignKey("environments.id"), nullable=False)
    username = Column(String, nullable=False)
    password = Column(String, nullable=False)

    environment = relationship("Environment", back_populates="credentials")


class EnvironmentSchedule(Base):
    __tablename__ = "environment_schedules"

    id = Column(Integer, primary_key=True, index=True)
    environment_id = Column(Integer, ForeignKey("environments.id"), nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    blackout = Column(Boolean, default=False)

    environment = relationship("Environment", back_populates="schedules")


# -----------------------------------------------------
# Intelligent orchestrator models
# -----------------------------------------------------


class DependencyType(str, enum.Enum):
    """Types of dependencies between tests."""

    REQUIRES = "REQUIRES"
    BLOCKS = "BLOCKS"
    OPTIONAL = "OPTIONAL"
    DATA_DEPENDENCY = "DATA_DEPENDENCY"


suite_tests = Table(
    "suite_tests",
    Base.metadata,
    Column("suite_id", Integer, ForeignKey("test_suites.id"), primary_key=True),
    Column("test_id", Integer, ForeignKey("tests.id"), primary_key=True),
)


class TestSuite(Base):
    __tablename__ = "test_suites"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    suite_type = Column(String, nullable=True)
    shared_context = Column(String, nullable=True)

    tests = relationship(
        "TestCase",
        secondary=suite_tests,
        backref="suites",
    )


class TestDependency(Base):
    __tablename__ = "test_dependencies"

    id = Column(Integer, primary_key=True, index=True)
    suite_id = Column(Integer, ForeignKey("test_suites.id"), nullable=True)
    test_id = Column(Integer, ForeignKey("tests.id"), nullable=False)
    depends_on_id = Column(Integer, ForeignKey("tests.id"), nullable=False)
    type = Column(String, nullable=False, default=DependencyType.REQUIRES.value)

    suite = relationship("TestSuite")
    test = relationship("TestCase", foreign_keys=[test_id])
    depends_on = relationship("TestCase", foreign_keys=[depends_on_id])

class TestBranch(Base):
    __tablename__ = "test_branches"

    id = Column(Integer, primary_key=True, index=True)
    test_id = Column(Integer, ForeignKey("tests.id"), nullable=False)
    name = Column(String, nullable=False)

    test = relationship("TestCase", backref="branches")


class TestVersion(Base):
    __tablename__ = "test_versions"

    id = Column(Integer, primary_key=True, index=True)
    test_id = Column(Integer, ForeignKey("tests.id"), nullable=False)
    snapshot = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    test = relationship("TestCase", backref="versions")


class TestCommit(Base):
    __tablename__ = "test_commits"

    id = Column(Integer, primary_key=True, index=True)
    branch_id = Column(Integer, ForeignKey("test_branches.id"), nullable=False)
    version_id = Column(Integer, ForeignKey("test_versions.id"), nullable=False)
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    message = Column(String, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)

    branch = relationship("TestBranch", backref="commits")
    version = relationship("TestVersion")
    author = relationship("User")


class TestMerge(Base):
    __tablename__ = "test_merges"

    id = Column(Integer, primary_key=True, index=True)
    source_branch_id = Column(Integer, ForeignKey("test_branches.id"), nullable=False)
    target_branch_id = Column(Integer, ForeignKey("test_branches.id"), nullable=False)
    commit_id = Column(Integer, ForeignKey("test_commits.id"), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)

    source_branch = relationship("TestBranch", foreign_keys=[source_branch_id])
    target_branch = relationship("TestBranch", foreign_keys=[target_branch_id])
    commit = relationship("TestCommit")

