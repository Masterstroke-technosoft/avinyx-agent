from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.core.database import get_db

router = APIRouter()

@router.get("/health")
def health_check(db: Session = Depends(get_db)):
    """
    Check if the API and Database are running.
    """
    db_status = "offline"
    try:
        # Perform a simple query to verify db connection
        db.execute(text("SELECT 1"))
        db_status = "online"
    except Exception as e:
        db_status = f"error: {str(e)}"
        
    return {
        "status": "healthy",
        "database": db_status
    }
