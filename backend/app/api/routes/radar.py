import hashlib
import json
import math
import re
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse, JSONResponse

from app.schemas.investigation import (
    InvestigationResponse,
    SpillCharacterizationResponse,
    TrafficSummaryResponse,
    VesselInvestigationResponse,
    VesselTrackPointResponse,
)

router = APIRouter(prefix="/radar", tags=["Radar_data"])
PROJECT_ROOT = Path(__file__).resolve().parents[4]
PROCESSED_ROOT = PROJECT_ROOT / "data" / "processed" / "all_scenes"
GITHUB_RAW_ROOT = "https://raw.githubusercontent.com/Deepanshu779/OCEANNOVA/main/data/processed/all_scenes"


def _safe_spill_id(spill_id: str) -> str:
    if not re.fullmatch(r"SP-\d{3,4}", spill_id):
        raise HTTPException(status_code=400, detail="Invalid Radar_data scene id")
    return spill_id


def _github_raw_text(spill_id: str, filename: str) -> str | None:
    """Read a committed processed artifact when the Render filesystem lacks data/."""
    url = f"{GITHUB_RAW_ROOT}/{spill_id}/{filename}"
    try:
        request = Request(url, headers={"User-Agent": "OCEANNOVA/1.0"})
        with urlopen(request, timeout=8) as response:
            return response.read().decode("utf-8")
    except (HTTPError, URLError, TimeoutError, UnicodeDecodeError, OSError):
        return None


def _load_characterization(spill_id: str) -> dict:
    spill_id = _safe_spill_id(spill_id)
    path = PROCESSED_ROOT / spill_id / "characterization.json"
    try:
        if path.exists():
            raw = path.read_text(encoding="utf-8")
        else:
            raw = _github_raw_text(spill_id, "characterization.json")
            if raw is None:
                raise HTTPException(status_code=404, detail="Processed Radar_data scene not found")
        return json.loads(raw)
    except json.JSONDecodeError as exc:
        raise HTTPException(status_code=500, detail="Invalid processed characterization JSON") from exc


def _demo_vessels(spill_id: str, latitude: float, longitude: float):
    """Create a deterministic vessel layer for every Radar_data scene.

    The project currently uses Radar_data only. These tracks are representative
    demo candidates so every scene has a usable vessel layer without pretending
    that external historical AIS has been loaded.
    """
    seed = int(hashlib.sha256(spill_id.encode("utf-8")).hexdigest()[:8], 16)
    names = ["OCEAN STAR", "SEA HORIZON", "MARINE EXPRESS", "COASTAL TRADER"]
    mmsi_base = 700000000 + (seed % 20000000)
    offsets = [(-0.010, 0.006), (0.008, -0.012), (0.026, 0.018), (-0.040, -0.032)]
    scores = [96.2, 87.7, 75.6, 54.3]
    speeds = [11.4, 13.1, 9.8, 7.6]
    courses = [92.0, 268.0, 141.0, 318.0]

    vessels = []
    tracks = []
    for i, (dlat, dlon) in enumerate(offsets):
        lat = latitude + dlat
        lon = longitude + dlon
        distance_km = math.hypot(dlat * 111.0, dlon * 111.0 * math.cos(math.radians(latitude)))
        vessel_id = str(mmsi_base + i)
        temporal = max(0.0, 1.0 - i * 0.12)
        proximity = max(0.0, 1.0 - min(distance_km / 8.0, 1.0))
        trajectory = max(0.0, 0.98 - i * 0.12)
        behavior = max(0.0, 0.82 - i * 0.16)

        vessels.append(
            VesselInvestigationResponse(
                mmsi=vessel_id,
                vessel_name=names[i],
                latitude=lat,
                longitude=lon,
                speed_knots=speeds[i],
                course=courses[i],
                attribution_score=scores[i],
                distance_km=round(distance_km, 2),
                time_difference_hours=float(i * 3),
                proximity_score=round(proximity, 3),
                temporal_score=round(temporal, 3),
                trajectory_match_score=round(trajectory, 3),
                behavioral_anomaly_score=round(behavior, 3),
                relevance="representative_demo_candidate",
            )
        )

        for hours, scale in [(-6.0, 1.55), (-3.0, 1.25), (0.0, 1.0), (3.0, 0.72)]:
            tracks.append(
                VesselTrackPointResponse(
                    mmsi=vessel_id,
                    timestamp_hours_from_origin=hours,
                    latitude=latitude + dlat * scale,
                    longitude=longitude + dlon * scale,
                    speed_knots=speeds[i],
                    course=courses[i],
                )
            )

    return vessels, tracks


@router.get("/spills/{spill_id}/investigation", response_model=InvestigationResponse)
def get_real_radar_investigation(spill_id: str):
    data = _load_characterization(spill_id)
    detection = data.get("detection", {})
    centroid = data.get("centroid", {})
    if "latitude" not in centroid or "longitude" not in centroid:
        raise HTTPException(status_code=500, detail="Processed Radar_data scene has no centroid")

    latitude = float(centroid["latitude"])
    longitude = float(centroid["longitude"])
    vessels, vessel_tracks = _demo_vessels(spill_id, latitude, longitude)

    return InvestigationResponse(
        spill_id=data.get("incident_id", spill_id),
        confidence=float(detection.get("mean_ai_confidence", 0.0)),
        area_km2=float(detection.get("area_km2", 0.0)),
        centroid={"lat": latitude, "lon": longitude},
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
            total_vessels_considered=len(vessels),
            filtered_irrelevant=0,
            ranked_candidates=len(vessels),
            filtering_rule="Representative vessel layer for demo; not historical AIS",
        ),
        vessels=vessels,
        vessel_tracks=vessel_tracks,
    )


@router.get("/spills/{spill_id}/geojson")
def get_real_radar_geojson(spill_id: str):
    spill_id = _safe_spill_id(spill_id)
    path = PROCESSED_ROOT / spill_id / "spill.geojson"
    if path.exists():
        return FileResponse(path, media_type="application/geo+json")

    raw = _github_raw_text(spill_id, "spill.geojson")
    if raw is None:
        raise HTTPException(status_code=404, detail="Processed Radar_data GeoJSON not found")
    try:
        return JSONResponse(content=json.loads(raw), media_type="application/geo+json")
    except json.JSONDecodeError as exc:
        raise HTTPException(status_code=500, detail="Invalid processed Radar_data GeoJSON") from exc
