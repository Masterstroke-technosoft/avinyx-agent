from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from app.models.base import BaseModel

class AgentTask(BaseModel):
    __tablename__ = "agent_tasks"

    case_id = Column(ForeignKey("cases.id"), nullable=False)
    agent_type = Column(String, nullable=False) # e.g., text, vision, priority
    status = Column(String, default="pending", nullable=False)
    payload = Column(JSONB, nullable=True)
    result_data = Column(JSONB, nullable=True)
