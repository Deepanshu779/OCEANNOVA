from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.database import get_db

router = APIRouter()


@router.get("/health")
def health_check():
    """Cheap liveness endpoint for Render.

    This endpoint intentionally does not touch Postgres. Render must be able
    to verify that the FastAPI process is alive even during a transient DB
    outage or database cold start.
    """
    return {
        "status": "healthy",
        "service": "OCEANNOVA Backend",
        "version": "0.1.0",
        "database": "not_checked",
    }


@router.get("/ready")
def readiness_check(db: Session = Depends(get_db)):
    """Dependency readiness check for operators and diagnostics."""
    try:
        db.execute(text("SELECT 1"))
        return {
            "status": "ready",
            "service": "OCEANNOVA Backend",
            "database": "ok",
        }
    except Exception as exc:
        return JSONResponse(
            status_code=503,
            content={
                "status": "not_ready",
                "service": "OCEANNOVA Backend",
                "database": "unavailable",
                "error": type(exc).__name__,
            },
        )
