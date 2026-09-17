from app.core.database import SessionLocal
from app.models.users import User, Role
from app.core.security import get_password_hash

def setup():
    db = SessionLocal()
    
    # 1. Remove admin role from previous account
    old_admin = db.query(User).filter(User.email == "vipulsutar.mst@gmail.com").first()
    admin_role = db.query(Role).filter(Role.name == "admin").first()
    
    if old_admin and admin_role in old_admin.roles:
        old_admin.roles.remove(admin_role)
        print("Removed admin privileges from vipulsutar.mst@gmail.com")
        
    # 2. Create the new admin account
    new_admin = db.query(User).filter(User.email == "admin@city.com").first()
    if not new_admin:
        new_admin = User(
            email="admin@city.com",
            hashed_password=get_password_hash("admin123"), # Default password
            is_active=True
        )
        db.add(new_admin)
        db.commit()
        db.refresh(new_admin)
        print("Created new user: admin@city.com")
        
    # 3. Give new account the admin role
    if admin_role not in new_admin.roles:
        new_admin.roles.append(admin_role)
        db.commit()
        print("Successfully made admin@city.com a System Administrator!")
    else:
        print("admin@city.com is already an admin.")
        
    db.close()

if __name__ == "__main__":
    setup()
