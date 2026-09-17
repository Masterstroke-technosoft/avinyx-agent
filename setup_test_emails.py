from app.core.database import SessionLocal
from app.models.users import User

def setup_emails():
    db = SessionLocal()
    
    # 1. Pratham -> Department of Transportation
    pratham = db.query(User).filter(User.department_name == "Department of Transportation").first()
    if pratham:
        pratham.email = "pratham.mst@gmail.com"
        
    # 2. Adityaa -> Water Department
    adityaa = db.query(User).filter(User.department_name == "Water Department").first()
    if adityaa:
        adityaa.email = "adityaa.mst@gmail.com"
        
    # 3. Aditya Isadkar -> Sanitation
    adityaisadkar = db.query(User).filter(User.department_name == "Sanitation").first()
    if adityaisadkar:
        adityaisadkar.email = "adityaisadkar.mst@gmail.com"
        
    db.commit()
    print("Successfully updated database with the new test emails!")
    db.close()

if __name__ == "__main__":
    setup_emails()
