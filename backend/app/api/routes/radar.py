import json
from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from app.schemas.investigation import (
    InvestigationResponse,
    SpillCharacterizationResponse,
    TrafficSummaryResponse,
)

router = APIRouter(prefix="/radar", tags=["Radar_data"])
PROJECT_ROOT = Path(__file__).resolve().parents[4]
PROCESSED_ROOT = PROJECT_ROOT / "data" / "processed" / "all_scenes"


def _load_characterization(spill_id: str) -> dict:
    path = PROCESSED_ROOT / spill_id / "characterization.json"
    if not path.exists():
        raise HTTPException(status_code=404, detail="Processed Radar_data scene not found")
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise HTTPException(status_code=500, detail="Invalid processed characterization JSON") from exc


@router.get("/spills/{spill_id}/investigation", response_model=InvestigationResponse)
def get_real_radar_investigation(spill_id: str):
    data = _load_characterization(spill_id)
    detection = data.get("detection", {})
    centroid = detection.get("centroid", {})
    if "latitude" not in centroid or "longitude" not in centroid:
        raise HTTPException(status_code=500, detail="Processed Radar_data scene has no centroid")

    return InvestigationResponse(
        spill_id=data.get("incident_id", spill_id),
        confidence=float(detection.get("mean_ai_confidence", 0.0)),
        area_km2=float(detection.get("area_km2", 0.0)),
        centroid={"lat": float(centroid["latitude"]), "lon": float(centroid["longitude"])},
        detection_time=None,
        origin_time=None,
        characterization=SpillCharacterizationResponse(
            area_km2=float(detection.get("area_km2", 0.0)),
            perimeter_estimate_km=detection.get("perimeter_km"),
            compactness_estimate=detection.get("compactness"),
            estimated_age_hours=None,
            age_status="not_available_from_single_radar_scene",
        ),
        origin=None,
        drift=[],
        traffic=TrafficSummaryResponse(
            total_vessels_considered=0,
            filtered_irrelevant=0,
            ranked_candidates=0,
            filtering_rule="Radar_data-only mode — no AIS source loaded",
        ),
        vessels=[],
        vessel_tracks=[],
    )


@router.get("/spills/{spill_id}/geojson")
def get_real_radar_geojson(spill_id: str):
    path = PROCESSED_ROOT / spill_id / "spill.geojson"
    if not path.exists():
        raise HTTPException(status_code=404, detail="Processed Radar_data GeoJSON not found")
    return FileResponse(path, media_type="application/geo+json")
