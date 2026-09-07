from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.database import get_db

router = APIRouter()


@router.get("/health")
def health_check(db: Session = Depends(get_db)):
    database = "ok"
    try:
        db.execute(text("SELECT 1"))
    except Exception:
        database = "unavailable"

    return {
        "status": "healthy" if database == "ok" else "degraded",
        "service": "OCEANNOVA Backend",
        "version": "0.1.0",
        "database": database,
    }
