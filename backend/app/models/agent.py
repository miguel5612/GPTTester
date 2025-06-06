import enum
from sqlalchemy import Column, Integer, String, Enum

from ..database import Base


class OSType(enum.Enum):
    Windows = "Windows"
    Linux = "Linux"
    Mac = "Mac"
    Android = "Android"
    iOS = "iOS"


class Agent(Base):
    __tablename__ = "agents"

    id = Column(Integer, primary_key=True, index=True)
    alias = Column(String, nullable=False)
    hostname = Column(String, unique=True, index=True, nullable=False)
    sistema_operativo = Column(Enum(OSType), nullable=False)
    categoria = Column(String, nullable=True)
