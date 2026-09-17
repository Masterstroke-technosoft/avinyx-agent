from app.core.database import SessionLocal
from app.models.users import Role, Permission

def seed():
    db = SessionLocal()
    
    # Permissions
    perm_read_all = db.query(Permission).filter_by(name="cases:read_all").first()
    if not perm_read_all:
        perm_read_all = Permission(name="cases:read_all", description="Read all cases across all departments")
        db.add(perm_read_all)
        
    perm_read_dept = db.query(Permission).filter_by(name="cases:read_department").first()
    if not perm_read_dept:
        perm_read_dept = Permission(name="cases:read_department", description="Read cases assigned to own department")
        db.add(perm_read_dept)
        
    perm_create_user = db.query(Permission).filter_by(name="users:create").first()
    if not perm_create_user:
        perm_create_user = Permission(name="users:create", description="Create new users")
        db.add(perm_create_user)
        
    db.commit()
    
    # Roles
    role_admin = db.query(Role).filter_by(name="admin").first()
    if not role_admin:
        role_admin = Role(name="admin", description="System Administrator")
        db.add(role_admin)
        
    role_dept = db.query(Role).filter_by(name="department").first()
    if not role_dept:
        role_dept = Role(name="department", description="Department User")
        db.add(role_dept)
        
    role_citizen = db.query(Role).filter_by(name="citizen").first()
    if not role_citizen:
        role_citizen = Role(name="citizen", description="Citizen")
        db.add(role_citizen)
        
    db.commit()
    
    # Assign Permissions
    if perm_read_all not in role_admin.permissions:
        role_admin.permissions.append(perm_read_all)
    if perm_create_user not in role_admin.permissions:
        role_admin.permissions.append(perm_create_user)
        
    if perm_read_dept not in role_dept.permissions:
        role_dept.permissions.append(perm_read_dept)
        
    db.commit()
    print("Roles and permissions seeded successfully!")

if __name__ == "__main__":
    seed()
