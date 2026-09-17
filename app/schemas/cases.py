from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID
from datetime import datetime

class MediaResponse(BaseModel):
    id: UUID
    file_url: str
    media_type: str
    stage: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class CaseBase(BaseModel):
    title: str
    description: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    ward: Optional[str] = None
    priority: int = 0

class CaseCreate(CaseBase):
    pass

class CaseResponse(CaseBase):
    id: UUID
    citizen_id: UUID
    status: str
    ai_severity: Optional[int] = None
    ai_intent: Optional[str] = None
    assigned_department: Optional[str] = None
    closed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    attachments: List[MediaResponse] = []

    class Config:
        from_attributes = True
