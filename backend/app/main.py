from fastapi import FastAPI

from app.core.database import Base, engine
from app.models.spill import Spill

from app.api.routes.health import router as health_router
from app.api.routes.spills import router as spills_router
from app.api.routes.investigation import router as investigation_router

from fastapi.middleware.cors import CORSMiddleware


Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="OCEANNOVA API",
    description="Marine Oil Spill Intelligence Platform",
    version="0.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(
    health_router,
    prefix="/api/v1"
)

app.include_router(
    spills_router,
    prefix="/api/v1"
)

app.include_router(
    investigation_router,
    prefix="/api/v1"
)

@app.get("/")
def root():
    return {
        "project": "OCEANNOVA",
        "message": "Marine Oil Spill Intelligence Platform",
        "version": "0.1.0"
    }