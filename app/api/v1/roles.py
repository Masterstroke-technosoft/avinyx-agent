from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.users import Role, Permission, User
from app.schemas.roles import RoleCreate, RoleResponse
from typing import List
from uuid import UUID

router = APIRouter()

@router.post("/", response_model=RoleResponse)
def create_role(role_in: RoleCreate, db: Session = Depends(get_db)):
    role = db.query(Role).filter(Role.name == role_in.name).first()
    if role:
        raise HTTPException(status_code=400, detail="Role already exists.")
    
    new_role = Role(name=role_in.name, description=role_in.description)
    db.add(new_role)
    db.commit()
    db.refresh(new_role)
    return new_role

@router.get("/", response_model=List[RoleResponse])
def get_roles(db: Session = Depends(get_db)):
    return db.query(Role).all()

@router.post("/{role_id}/permissions/{permission_id}", response_model=RoleResponse)
def assign_permission_to_role(role_id: UUID, permission_id: UUID, db: Session = Depends(get_db)):
    role = db.query(Role).filter(Role.id == role_id).first()
    permission = db.query(Permission).filter(Permission.id == permission_id).first()
    
    if not role or not permission:
        raise HTTPException(status_code=404, detail="Role or Permission not found.")
        
    if permission not in role.permissions:
        role.permissions.append(permission)
        db.commit()
        db.refresh(role)
        
    return role

@router.post("/assign/{user_id}/{role_id}")
def assign_role_to_user(user_id: UUID, role_id: UUID, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    role = db.query(Role).filter(Role.id == role_id).first()
    
    if not user or not role:
        raise HTTPException(status_code=404, detail="User or Role not found.")
        
    if role not in user.roles:
        user.roles.append(role)
        db.commit()
        
    return {"message": f"Role '{role.name}' assigned to User '{user.email}'"}
