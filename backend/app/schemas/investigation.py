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
    vessel_name: Optional[str] = None

    attribution_score: float

    distance_km: Optional[float] = None
    time_difference_hours: Optional[float] = None
    trajectory_match_score: Optional[float] = None
    behavioral_anomaly_score: Optional[float] = None


class InvestigationResponse(BaseModel):
    spill_id: str

    confidence: float
    area_km2: float

    centroid: dict

    origin: OriginResponse | None = None

    drift: list[DriftPointResponse]

    vessels: list[VesselInvestigationResponse]