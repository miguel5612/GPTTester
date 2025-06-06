from sqlalchemy import Column, Integer, ForeignKey, JSON
from sqlalchemy.orm import relationship

from ..database import Base


class ActionAssignment(Base):
    __tablename__ = "action_assignments"

    id = Column(Integer, primary_key=True, index=True)
    action_id = Column(Integer, ForeignKey("actions.id"), nullable=False)
    element_id = Column(Integer, ForeignKey("page_elements.id"), nullable=False)
    test_id = Column(Integer, ForeignKey("tests.id"), nullable=False)
    parameters = Column(JSON, nullable=False, default={})

    action = relationship("Action")
    element = relationship("PageElement")
    test = relationship("Test")

