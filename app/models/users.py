from sqlalchemy import Column, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import BaseModel

class User(BaseModel):
    __tablename__ = "users"

    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    department_name = Column(String, nullable=True)
    phone_number = Column(String, nullable=True)
    notification_preference = Column(String, default="email")

    roles = relationship("Role", secondary="user_roles", back_populates="users")


class Role(BaseModel):
    __tablename__ = "roles"

    name = Column(String, unique=True, index=True, nullable=False)
    description = Column(String)

    users = relationship("User", secondary="user_roles", back_populates="roles")
    permissions = relationship("Permission", secondary="role_permissions", back_populates="roles")


class Permission(BaseModel):
    __tablename__ = "permissions"

    name = Column(String, unique=True, index=True, nullable=False)
    description = Column(String)

    roles = relationship("Role", secondary="role_permissions", back_populates="permissions")


class UserRole(BaseModel):
    __tablename__ = "user_roles"

    user_id = Column(ForeignKey("users.id"), primary_key=True)
    role_id = Column(ForeignKey("roles.id"), primary_key=True)


class RolePermission(BaseModel):
    __tablename__ = "role_permissions"

    role_id = Column(ForeignKey("roles.id"), primary_key=True)
    permission_id = Column(ForeignKey("permissions.id"), primary_key=True)
