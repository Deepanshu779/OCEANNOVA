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


class VesselTrackPointResponse(BaseModel):
    mmsi: str
    timestamp_hours_from_origin: float
    latitude: float
    longitude: float
    speed_knots: float | None = None
    course: float | None = None


class SpillCharacterizationResponse(BaseModel):
    area_km2: float
    perimeter_estimate_km: float | None = None
    compactness_estimate: float | None = None
    estimated_age_hours: float | None = None
    age_status: str


class TrafficSummaryResponse(BaseModel):
    total_vessels_considered: int
    filtered_irrelevant: int
    ranked_candidates: int
    filtering_rule: str


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
    proximity_score: float | None = None
    temporal_score: float | None = None
    trajectory_match_score: float | None = None
    behavioral_anomaly_score: float | None = None
    relevance: str = "candidate"


class InvestigationResponse(BaseModel):
    spill_id: str
    confidence: float
    area_km2: float
    centroid: dict
    characterization: SpillCharacterizationResponse
    origin: OriginResponse | None = None
    drift: list[DriftPointResponse]
    traffic: TrafficSummaryResponse
    vessels: list[VesselInvestigationResponse]
    vessel_tracks: list[VesselTrackPointResponse]
