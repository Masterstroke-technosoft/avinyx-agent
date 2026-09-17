from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.users import Permission
from app.schemas.permissions import PermissionCreate, PermissionResponse
from typing import List

router = APIRouter()

@router.post("/", response_model=PermissionResponse)
def create_permission(permission_in: PermissionCreate, db: Session = Depends(get_db)):
    permission = db.query(Permission).filter(Permission.name == permission_in.name).first()
    if permission:
        raise HTTPException(status_code=400, detail="Permission already exists.")
    
    new_permission = Permission(name=permission_in.name, description=permission_in.description)
    db.add(new_permission)
    db.commit()
    db.refresh(new_permission)
    return new_permission

@router.get("/", response_model=List[PermissionResponse])
def get_permissions(db: Session = Depends(get_db)):
    return db.query(Permission).all()
