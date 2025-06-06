from sqlalchemy import Column, Integer, String, Text, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship

from ..database import Base


class PageElement(Base):
    __tablename__ = "page_elements"
    __table_args__ = (UniqueConstraint("page_id", "name"),)

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    tipo = Column(String, nullable=False)
    estrategia = Column(String, nullable=False)
    valor = Column(String, nullable=False)
    descripcion = Column(Text)
    page_id = Column(Integer, ForeignKey("pages.id"), nullable=False)

    page = relationship("Page", back_populates="elements")
    scenarios = relationship(
        "Scenario", secondary="scenario_elements", back_populates="elements"
    )
