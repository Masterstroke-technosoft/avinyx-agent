from pydantic import BaseModel
from uuid import UUID
from datetime import datetime

class PermissionBase(BaseModel):
    name: str
    description: str = None

class PermissionCreate(PermissionBase):
    pass

class PermissionResponse(PermissionBase):
    id: UUID
    created_at: datetime
    
    class Config:
        from_attributes = True
