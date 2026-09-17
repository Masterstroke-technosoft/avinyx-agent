from app.core.database import engine, SessionLocal
from sqlalchemy import text

with engine.begin() as conn:
    try:
        conn.execute(text("ALTER TABLE cases ADD COLUMN citizen_notification_preference VARCHAR DEFAULT 'email';"))
        print("Column added to cases.")
    except Exception as e:
        print("Column already exists or error:", e)
