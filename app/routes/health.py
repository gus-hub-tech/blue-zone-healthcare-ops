"""Health check endpoints"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db

router = APIRouter(prefix="/health", tags=["health"])

@router.get("/")
def health_check():
    """Basic health check"""
    return {"status": "healthy"}

@router.get("/db")
def db_health_check(db: Session = Depends(get_db)):
    """Database health check"""
    try:
        db.execute("SELECT 1")
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "database": "disconnected", "error": str(e)}
