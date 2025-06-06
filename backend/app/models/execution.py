from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship

from ..database import Base

class Execution(Base):
    __tablename__ = "executions"

    id = Column(Integer, primary_key=True, index=True)
    plan_id = Column(Integer, ForeignKey("execution_plans.id"), nullable=False)
    agent_id = Column(Integer, ForeignKey("agents.id"), nullable=False)
    status = Column(String, nullable=False, default="Llamando al agente")
    started_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    report_file = Column(String, nullable=True)
    report_received_at = Column(DateTime(timezone=True), nullable=True)

    plan = relationship("ExecutionPlan")
    agent = relationship("Agent")

