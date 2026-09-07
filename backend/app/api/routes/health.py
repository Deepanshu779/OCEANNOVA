from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "OCEANNOVA Backend",
        "version": "0.1.0"
    }