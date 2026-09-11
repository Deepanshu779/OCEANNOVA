import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.health import router as health_router
from app.api.routes.spills import router as spills_router
from app.api.routes.investigation import router as investigation_router
from app.api.routes.datasets import router as datasets_router
from app.api.routes.radar import router as radar_router


# IMPORTANT: Do not connect to Postgres/PostGIS during module import.
# The Radar_data and dataset APIs are file-backed and must remain available
# even if the database has a transient outage or is waking up.
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
    # Match Vercel preview and production deployments.
    # Keep a single backslash before the regex dot: \\. means literal dot.
    allow_origin_regex=r"https://.*\.vercel\.app$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router, prefix="/api/v1")
app.include_router(spills_router, prefix="/api/v1")
app.include_router(investigation_router, prefix="/api/v1")
app.include_router(datasets_router, prefix="/api/v1")
app.include_router(radar_router, prefix="/api/v1")


@app.get("/")
def root():
    return {
        "project": "OCEANNOVA",
        "message": "Marine Oil Spill Intelligence Platform",
        "version": "1.0.0",
        "status": "online",
    }
