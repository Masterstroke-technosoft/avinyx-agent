from app.core.database import SessionLocal
from app.models.users import User, Role
from app.core.security import get_password_hash

def setup():
    db = SessionLocal()
    
    dept_role = db.query(Role).filter(Role.name == "department").first()
    
    departments = [
        ("transport@city.com", "Department of Transportation"),
        ("sanitation@city.com", "Sanitation"),
        ("publicworks@city.com", "Public Works"),
        ("police@city.com", "Police"),
        ("fire@city.com", "Fire Department"),
        ("parks@city.com", "Parks & Recreation")
    ]
    
    for email, dept_name in departments:
        user = db.query(User).filter(User.email == email).first()
        if not user:
            user = User(
                email=email,
                hashed_password=get_password_hash("password123"), # Default password
                is_active=True,
                department_name=dept_name
            )
            user.roles.append(dept_role)
            db.add(user)
            print(f"Created {email} for {dept_name}")
        else:
            print(f"{email} already exists.")
            
    db.commit()
    db.close()

if __name__ == "__main__":
    setup()
