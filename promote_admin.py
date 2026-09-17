from app.core.database import SessionLocal
from app.models.users import User, Role

def promote_to_admin(email: str):
    db = SessionLocal()
    
    user = db.query(User).filter(User.email == email).first()
    if not user:
        print(f"Error: User {email} not found in database.")
        db.close()
        return

    admin_role = db.query(Role).filter(Role.name == "admin").first()
    if not admin_role:
        print("Error: Admin role not found. Did you run seed_roles.py?")
        db.close()
        return

    if admin_role not in user.roles:
        user.roles.append(admin_role)
        db.commit()
        print(f"Success! {email} has been promoted to Admin.")
    else:
        print(f"{email} is already an Admin.")

    db.close()

if __name__ == "__main__":
    # Change this email to whatever account you use to login!
    promote_to_admin("vipulsutar.mst@gmail.com")
