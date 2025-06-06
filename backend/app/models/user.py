from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship
from ..database import Base
from .role import user_roles
from .project import project_analysts


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)

    tests = relationship("Test", back_populates="owner")
    roles = relationship("Role", secondary=user_roles, back_populates="users")
    projects = relationship(
        "Project", secondary=project_analysts, back_populates="analysts"
    )
