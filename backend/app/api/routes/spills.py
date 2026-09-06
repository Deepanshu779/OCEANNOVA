from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from geoalchemy2.shape import from_shape, to_shape
from shapely.geometry import Point

from app.core.database import get_db
from app.models.spill import Spill
from app.schemas.spill import SpillCreate, SpillResponse, GeoJSONPoint

router = APIRouter(prefix="/spills", tags=["Spills"])


@router.post("/", response_model=SpillResponse)
def create_spill(spill: SpillCreate, db: Session = Depends(get_db)):

    # Check if spill already exists
    existing_spill = db.query(Spill).filter(
        Spill.spill_id == spill.spill_id
    ).first()

    if existing_spill:
        raise HTTPException(
            status_code=409,
            detail="Spill ID already exists"
        )

    # Convert latitude/longitude to PostGIS Point
    point = from_shape(
        Point(spill.centroid.lon, spill.centroid.lat),
        srid=4326
    )

    # Create database record
    db_spill = Spill(
        spill_id=spill.spill_id,
        confidence=spill.confidence,
        area_km2=spill.area_km2,
        acquisition_time=spill.acquisition_time,
        geometry=point
    )

    db.add(db_spill)
    db.commit()
    db.refresh(db_spill)

    return SpillResponse(
        spill_id=db_spill.spill_id,
        confidence=db_spill.confidence,
        area_km2=db_spill.area_km2,
        centroid=spill.centroid,
        acquisition_time=db_spill.acquisition_time,
        status="detected",
        geometry=GeoJSONPoint(
            coordinates=[
                spill.centroid.lon,
                spill.centroid.lat
            ]
        )
    )


@router.get("/", response_model=list[SpillResponse])
def get_spills(db: Session = Depends(get_db)):

    spills = db.query(Spill).all()

    result = []

    for spill in spills:

        point = to_shape(spill.geometry)

        result.append(
            SpillResponse(
                spill_id=spill.spill_id,
                confidence=spill.confidence,
                area_km2=spill.area_km2,
                centroid={
                    "lat": point.y,
                    "lon": point.x
                },
                acquisition_time=spill.acquisition_time,
                status="detected",
                geometry=GeoJSONPoint(
                    coordinates=[
                        point.x,
                        point.y
                    ]
                )
            )
        )

    return result


@router.get("/{spill_id}", response_model=SpillResponse)
def get_spill(spill_id: str, db: Session = Depends(get_db)):

    spill = db.query(Spill).filter(
        Spill.spill_id == spill_id
    ).first()

    if not spill:
        raise HTTPException(
            status_code=404,
            detail="Spill not found"
        )

    point = to_shape(spill.geometry)

    return SpillResponse(
        spill_id=spill.spill_id,
        confidence=spill.confidence,
        area_km2=spill.area_km2,
        centroid={
            "lat": point.y,
            "lon": point.x
        },
        acquisition_time=spill.acquisition_time,
        status="detected",
        geometry=GeoJSONPoint(
            coordinates=[
                point.x,
                point.y
            ]
        )
    )