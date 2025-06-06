from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from ..database import Base


class ExecutionPlan(Base):
    __tablename__ = "execution_plans"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    test_id = Column(Integer, ForeignKey("tests.id"), nullable=False)
    agent_id = Column(Integer, ForeignKey("agents.id"), nullable=False)

    test = relationship("Test")
    agent = relationship("Agent")
