from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Table, Date, UniqueConstraint
from sqlalchemy.orm import relationship
from .database import Base


class Role(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role_id = Column(Integer, ForeignKey("roles.id"))
    is_active = Column(Boolean, default=True)
    role = relationship("Role")
    tests = relationship("TestCase", back_populates="owner")
    projects = relationship(
        "Project",
        secondary="project_analysts",
        back_populates="analysts",
    )

class TestCase(Base):
    __tablename__ = "tests"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String, nullable=True)
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


project_analysts = Table(
    "project_analysts",
    Base.metadata,
    Column("project_id", Integer, ForeignKey("projects.id"), primary_key=True),
    Column("user_id", Integer, ForeignKey("users.id"), primary_key=True),
)


class Client(Base):
    __tablename__ = "clients"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    is_active = Column(Boolean, default=True)
    projects = relationship("Project", back_populates="client")


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
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
