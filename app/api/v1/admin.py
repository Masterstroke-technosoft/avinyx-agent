from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.users import User, Role
from app.schemas.users import UserCreate, UserResponse
from app.core.security import get_password_hash
from app.api.deps import RequirePermissions
from pydantic import BaseModel

router = APIRouter()

class DepartmentUserCreate(UserCreate):
    department_name: str

@router.post("/users", response_model=UserResponse, dependencies=[Depends(RequirePermissions(["users:create"]))])
def create_department_user(user_in: DepartmentUserCreate, db: Session = Depends(get_db)):
    """Admin endpoint to create a department user."""
    # Check if email exists
    user = db.query(User).filter(User.email == user_in.email).first()
    if user:
        raise HTTPException(status_code=400, detail="Email already registered")
        
    # Get department role
    dept_role = db.query(Role).filter(Role.name == "department").first()
    if not dept_role:
        raise HTTPException(status_code=500, detail="Department role not found in DB. Run seed_roles.py first.")
        
    new_user = User(
        email=user_in.email,
        hashed_password=get_password_hash(user_in.password),
        is_active=True,
        department_name=user_in.department_name
    )
    new_user.roles.append(dept_role)
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return new_user
