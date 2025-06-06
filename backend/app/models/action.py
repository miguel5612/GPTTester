from sqlalchemy import Column, Integer, String, Text, JSON
from sqlalchemy.orm import relationship

from ..database import Base


class Action(Base):
    __tablename__ = "actions"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, unique=True, nullable=False)
    tipo = Column(String, nullable=False)
    codigo = Column(Text, nullable=False)
    argumentos = Column(JSON, nullable=False, default={})

    # In future this can be related to test cases or flows

