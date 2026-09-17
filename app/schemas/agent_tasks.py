from pydantic import BaseModel
from typing import Optional, Dict, Any
from uuid import UUID
from datetime import datetime

class AgentTaskBase(BaseModel):
    agent_type: str
    status: str
    payload: Dict[str, Any] = {}

class AgentTaskCreate(AgentTaskBase):
    case_id: UUID

class AgentTaskResponse(AgentTaskBase):
    id: UUID
    case_id: UUID
    result_data: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class AgentTaskResult(BaseModel):
    status: str
    result_data: Dict[str, Any]
