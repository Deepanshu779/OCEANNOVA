from pydantic import BaseModel
from typing import Optional
from app.schemas.origin import OriginResponse


class DriftPointResponse(BaseModel):
    latitude: float
    longitude: float
    hours_from_detection: float

    current_speed: Optional[float] = None
    current_direction: Optional[float] = None

    wind_speed: Optional[float] = None
    wind_direction: Optional[float] = None


class VesselInvestigationResponse(BaseModel):
    mmsi: str
    vessel_name: str | None = None

    latitude: float | None = None
    longitude: float | None = None

    speed_knots: float | None = None
    course: float | None = None

    attribution_score: float

    distance_km: float | None = None
    time_difference_hours: float | None = None

    trajectory_match_score: float | None = None
    behavioral_anomaly_score: float | None = None


class InvestigationResponse(BaseModel):
    spill_id: str

    confidence: float
    area_km2: float

    centroid: dict

    origin: OriginResponse | None = None

    drift: list[DriftPointResponse]

    vessels: list[VesselInvestigationResponse]