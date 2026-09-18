from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.db.session import get_db

router = APIRouter()


@router.get("/health")
def health_check(db: Session = Depends(get_db)):
    """Confirms the API is up and can reach the database."""
    db.execute(text("SELECT 1"))
    return {"status": "ok", "database": "connected"}
