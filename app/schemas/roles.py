from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import List
from app.schemas.permissions import PermissionResponse

class RoleBase(BaseModel):
    name: str
    description: str = None

class RoleCreate(RoleBase):
    pass

class RoleResponse(RoleBase):
    id: UUID
    created_at: datetime
    permissions: List[PermissionResponse] = []
    
    class Config:
        from_attributes = True
