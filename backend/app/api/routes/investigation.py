from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from geoalchemy2.shape import to_shape

from app.core.database import get_db
from app.models.spill import Spill
from app.models.drift import DriftPoint
from app.models.origin import SpillOrigin
from app.models.attribution import VesselAttribution
from app.models.vessel import Vessel
from app.models.vessel_track import VesselTrackPoint
from app.schemas.investigation import (
    InvestigationResponse,
    DriftPointResponse,
    SpillCharacterizationResponse,
    TrafficSummaryResponse,
    VesselInvestigationResponse,
    VesselTrackPointResponse,
)
from app.schemas.origin import OriginResponse

router = APIRouter(prefix="/spills", tags=["Investigation"])


@router.get("/{spill_id}/investigation", response_model=InvestigationResponse)
def get_investigation(spill_id: str, db: Session = Depends(get_db)):
    spill = db.query(Spill).filter(Spill.spill_id == spill_id).first()
    if not spill:
        raise HTTPException(status_code=404, detail="Spill not found")

    origin_record = (
        db.query(SpillOrigin)
        .filter(SpillOrigin.spill_id == spill_id)
        .first()
    )
    origin = None
    if origin_record:
        origin_point = to_shape(origin_record.geometry)
        origin = OriginResponse(
            latitude=origin_point.y,
            longitude=origin_point.x,
            uncertainty_km=origin_record.uncertainty_km,
            method=origin_record.method,
        )

    drift_points = (
        db.query(DriftPoint)
        .filter(DriftPoint.spill_id == spill_id)
        .order_by(DriftPoint.hours_from_detection)
        .all()
    )
    drift = [
        DriftPointResponse(
            latitude=p.latitude,
            longitude=p.longitude,
            hours_from_detection=p.hours_from_detection,
            current_speed=p.current_speed,
            current_direction=p.current_direction,
            wind_speed=p.wind_speed,
            wind_direction=p.wind_direction,
        )
        for p in drift_points
    ]

    vessel_rows = (
        db.query(VesselAttribution, Vessel)
        .join(Vessel, VesselAttribution.mmsi == Vessel.mmsi)
        .filter(VesselAttribution.spill_id == spill_id)
        .order_by(VesselAttribution.attribution_score.desc())
        .all()
    )

    vessels = [
        VesselInvestigationResponse(
            mmsi=vessel.mmsi,
            vessel_name=vessel.vessel_name,
            latitude=vessel.latitude,
            longitude=vessel.longitude,
            speed_knots=vessel.speed_knots,
            course=vessel.course,
            attribution_score=attribution.attribution_score,
            distance_km=attribution.distance_km,
            time_difference_hours=attribution.time_difference_hours,
            proximity_score=(
                max(0.0, min(1.0, 1.0 - attribution.distance_km / 50.0))
                if attribution.distance_km is not None else None
            ),
            temporal_score=(
                max(0.0, min(1.0, 1.0 - abs(attribution.time_difference_hours) / 12.0))
                if attribution.time_difference_hours is not None else None
            ),
            trajectory_match_score=attribution.trajectory_match_score,
            behavioral_anomaly_score=attribution.behavioral_anomaly_score,
            relevance=(
                "high"
                if attribution.attribution_score >= 0.70
                else "medium"
                if attribution.attribution_score >= 0.45
                else "low"
            ),
        )
        for attribution, vessel in vessel_rows
    ]

    candidate_mmsis = [v.mmsi for v in vessels]
    track_rows = []
    if candidate_mmsis:
        track_rows = (
            db.query(VesselTrackPoint)
            .filter(VesselTrackPoint.mmsi.in_(candidate_mmsis))
            .order_by(VesselTrackPoint.mmsi, VesselTrackPoint.timestamp_hours_from_origin)
            .all()
        )

    vessel_tracks = [
        VesselTrackPointResponse(
            mmsi=track.mmsi,
            timestamp_hours_from_origin=track.timestamp_hours_from_origin,
            latitude=track.latitude,
            longitude=track.longitude,
            speed_knots=track.speed_knots,
            course=track.course,
        )
        for track in track_rows
    ]

    total_vessels = db.query(Vessel).count()
    ranked_candidates = len(vessels)
    filtered_irrelevant = max(0, total_vessels - ranked_candidates)

    point = to_shape(spill.geometry)
    characterization = SpillCharacterizationResponse(
        area_km2=spill.area_km2,
        perimeter_estimate_km=spill.perimeter_km,
        compactness_estimate=spill.compactness,
        estimated_age_hours=spill.estimated_age_hours,
        age_status=(
            "estimated_from_observation_timestamp"
            if spill.estimated_age_hours is not None
            else "not_available_insufficient_temporal_observations"
        ),
    )

    detection_time = spill.acquisition_time.isoformat() if spill.acquisition_time else None
    origin_time = None
    if spill.acquisition_time and drift_points:
        earliest_hindcast = min(p.hours_from_detection for p in drift_points)
        if earliest_hindcast < 0:
            origin_time = (spill.acquisition_time + timedelta(hours=earliest_hindcast)).isoformat()

    traffic = TrafficSummaryResponse(
        total_vessels_considered=total_vessels,
        filtered_irrelevant=filtered_irrelevant,
        ranked_candidates=ranked_candidates,
        filtering_rule="50 km origin-window proximity + temporal consistency + available AIS evidence",
    )

    return InvestigationResponse(
        spill_id=spill.spill_id,
        confidence=spill.confidence,
        area_km2=spill.area_km2,
        centroid={"lat": point.y, "lon": point.x},
        detection_time=detection_time,
        origin_time=origin_time,
        characterization=characterization,
        origin=origin,
        drift=drift,
        traffic=traffic,
        vessels=vessels,
        vessel_tracks=vessel_tracks,
    )
