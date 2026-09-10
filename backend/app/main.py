import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.core.database import Base, engine
from app.models.spill import Spill
from app.models.vessel import Vessel
from app.models.attribution import VesselAttribution
from app.models.drift import DriftPoint
from app.models.origin import SpillOrigin
from app.models.vessel_track import VesselTrackPoint

from app.api.routes.health import router as health_router
from app.api.routes.spills import router as spills_router
from app.api.routes.investigation import router as investigation_router
from app.api.routes.datasets import router as datasets_router


with engine.begin() as connection:
    connection.execute(text("CREATE EXTENSION IF NOT EXISTS postgis"))

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="OCEANNOVA API",
    description="Marine Oil Spill Intelligence Platform",
    version="1.0.0",
)

allowed_origins = ["http://localhost:5173", "http://127.0.0.1:5173"]
frontend_url = os.getenv("FRONTEND_URL")
if frontend_url:
    allowed_origins.append(frontend_url.rstrip("/"))

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_origin_regex=r"https://.*\.vercel\.app$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router, prefix="/api/v1")
app.include_router(spills_router, prefix="/api/v1")
app.include_router(investigation_router, prefix="/api/v1")
app.include_router(datasets_router, prefix="/api/v1")


@app.get("/")
def root():
    return {
        "project": "OCEANNOVA",
        "message": "Marine Oil Spill Intelligence Platform",
        "version": "1.0.0",
        "status": "online",
    }
