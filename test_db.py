from app.core.database import SessionLocal
from app.models.users import User
from app.core.security import get_password_hash

def test():
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == "test@test.com").first()
        print("User query successful:", user)
        hash = get_password_hash("password")
        print("Hash successful:", hash)
    except Exception as e:
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    test()
