from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship

from ..database import Base


class Client(Base):
    __tablename__ = "clients"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    is_active = Column(Boolean, default=True)

    projects = relationship("Project", back_populates="client")
