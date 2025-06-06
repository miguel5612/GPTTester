from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Table
from sqlalchemy.orm import relationship

from ..database import Base

project_analysts = Table(
    "project_analysts",
    Base.metadata,
    Column("project_id", Integer, ForeignKey("projects.id")),
    Column("user_id", Integer, ForeignKey("users.id")),
)


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    client_id = Column(Integer, ForeignKey("clients.id"))

    client = relationship("Client", back_populates="projects")
    analysts = relationship("User", secondary=project_analysts, back_populates="projects")
