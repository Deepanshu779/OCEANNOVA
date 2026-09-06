from app.models.origin import SpillOrigin
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.spill import Spill
from app.models.drift import DriftPoint
from app.models.attribution import VesselAttribution
from app.models.vessel import Vessel
from app.schemas.investigation import (
    InvestigationResponse,
    DriftPointResponse,
    VesselInvestigationResponse,
)
from app.schemas.origin import OriginResponse
from geoalchemy2.shape import to_shape

router = APIRouter(
    prefix="/spills",
    tags=["Investigation"]
)


@router.get(
    "/{spill_id}/investigation",
    response_model=InvestigationResponse
)
def get_investigation(
    spill_id: str,
    db: Session = Depends(get_db)
):

    spill = db.query(Spill).filter(
        Spill.spill_id == spill_id
    ).first()

    if not spill:
        raise HTTPException(
            status_code=404,
            detail="Spill not found"
        )

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

    # Get drift points
    drift_points = (
        db.query(DriftPoint)
        .filter(DriftPoint.spill_id == spill_id)
        .order_by(DriftPoint.hours_from_detection)
        .all()
    )

    drift = [
        DriftPointResponse(
            latitude=point.latitude,
            longitude=point.longitude,
            hours_from_detection=point.hours_from_detection,
            current_speed=point.current_speed,
            current_direction=point.current_direction,
            wind_speed=point.wind_speed,
            wind_direction=point.wind_direction,
        )
        for point in drift_points
    ]

    # Get vessel attribution results
    vessel_rows = (
        db.query(VesselAttribution, Vessel)
        .join(
            Vessel,
            VesselAttribution.mmsi == Vessel.mmsi
        )
        .filter(
            VesselAttribution.spill_id == spill_id
        )
        .order_by(
            VesselAttribution.attribution_score.desc()
        )
        .all()
    )

    vessels = [
        VesselInvestigationResponse(
            mmsi=vessel.mmsi,
            vessel_name=vessel.vessel_name,
            attribution_score=attribution.attribution_score,
            distance_km=attribution.distance_km,
            time_difference_hours=attribution.time_difference_hours,
            trajectory_match_score=attribution.trajectory_match_score,
            behavioral_anomaly_score=attribution.behavioral_anomaly_score,
        )
        for attribution, vessel in vessel_rows
    ]

    point = to_shape(spill.geometry)

    return InvestigationResponse(
        spill_id=spill.spill_id,
        confidence=spill.confidence,
        area_km2=spill.area_km2,
        centroid={
            "lat": point.y,
            "lon": point.x
        },
        origin=origin,
        drift=drift,
        vessels=vessels
    )