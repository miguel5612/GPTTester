from sqlalchemy import Column, Integer, String, Table, ForeignKey
from sqlalchemy.orm import relationship

from ..database import Base

scenario_elements = Table(
    "scenario_elements",
    Base.metadata,
    Column("scenario_id", Integer, ForeignKey("scenarios.id")),
    Column("element_id", Integer, ForeignKey("page_elements.id")),
)


class Scenario(Base):
    __tablename__ = "scenarios"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)

    elements = relationship(
        "PageElement", secondary=scenario_elements, back_populates="scenarios"
    )
