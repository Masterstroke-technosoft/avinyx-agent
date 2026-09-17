from app.core.database import engine, SessionLocal
from sqlalchemy import text
from app.models.users import User

with engine.begin() as conn:
    try:
        conn.execute(text('ALTER TABLE users ADD COLUMN phone_number VARCHAR;'))
        conn.execute(text("ALTER TABLE users ADD COLUMN notification_preference VARCHAR DEFAULT 'email';"))
    except Exception as e:
        pass

db = SessionLocal()
user = db.query(User).filter(User.department_name == 'Roads').first()
if user:
    user.notification_preference = 'both'
    user.phone_number = '+15551234567'
    db.commit()
    print("Mock user Roads updated")
db.close()
