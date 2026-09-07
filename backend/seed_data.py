from datetime import datetime, timezone

from sqlalchemy import text
from geoalchemy2.shape import from_shape
from shapely.geometry import Point

from app.core.database import SessionLocal
from app.models.spill import Spill
from app.models.drift import DriftPoint
from app.models.vessel import Vessel
from app.models.attribution import VesselAttribution
from app.models.origin import SpillOrigin
from app.models.vessel_track import VesselTrackPoint
from ais.attribution.scoring import rank_vessels


db = SessionLocal()

try:
    # Existing local demo databases need these columns added once. Fresh databases
    # receive them automatically from SQLAlchemy metadata.
    db.execute(text("ALTER TABLE spills ADD COLUMN IF NOT EXISTS perimeter_km DOUBLE PRECISION"))
    db.execute(text("ALTER TABLE spills ADD COLUMN IF NOT EXISTS compactness DOUBLE PRECISION"))
    db.execute(text("ALTER TABLE spills ADD COLUMN IF NOT EXISTS estimated_age_hours DOUBLE PRECISION"))
    db.commit()

    # -----------------------------
    # 0. Create/update demo spill
    # -----------------------------
    spill = db.query(Spill).filter(Spill.spill_id == "SP-001").first()
    spill_geometry = from_shape(Point(74.850, 10.450), srid=4326)
    acquisition_time = datetime(2026, 9, 7, 6, 30, tzinfo=timezone.utc)

    if not spill:
        spill = Spill(
            spill_id="SP-001",
            confidence=0.94,
            area_km2=14.7,
            acquisition_time=acquisition_time,
            perimeter_km=18.6,
            compactness=0.63,
            estimated_age_hours=2.0,
            geometry=spill_geometry,
        )
        db.add(spill)
    else:
        spill.confidence = 0.94
        spill.area_km2 = 14.7
        spill.acquisition_time = acquisition_time
        spill.perimeter_km = 18.6
        spill.compactness = 0.63
        spill.estimated_age_hours = 2.0
        spill.geometry = spill_geometry
    db.commit()

    # -----------------------------
    # 1. Demonstration AIS candidates
    # -----------------------------
    vessels = [
        Vessel("419001234", "OCEAN STAR", 10.420, 74.835, 12.5, 245.0),
        Vessel("419005678", "SEA HORIZON", 10.450, 74.855, 9.8, 180.0),
        Vessel("419009876", "MARINE EXPRESS", 10.540, 74.910, 15.2, 270.0),
    ]

    for vessel in vessels:
        existing = db.query(Vessel).filter(Vessel.mmsi == vessel.mmsi).first()
        if existing:
            existing.vessel_name = vessel.vessel_name
            existing.latitude = vessel.latitude
            existing.longitude = vessel.longitude
            existing.speed_knots = vessel.speed_knots
            existing.course = vessel.course
        else:
            db.add(vessel)
    db.commit()

    # -----------------------------
    # 2. Spill drift: backward + observation + future forecast
    # -----------------------------
    drift_points = [
        (-6, 10.420, 74.800, 1.2, 245, 8.5, 230),
        (-3, 10.435, 74.820, 1.3, 248, 8.8, 232),
        (0, 10.450, 74.850, 1.4, 250, 9.0, 235),
        (6, 10.465, 74.875, 1.3, 252, 9.2, 237),
        (12, 10.480, 74.900, 1.4, 255, 9.5, 240),
    ]
    db.query(DriftPoint).filter(DriftPoint.spill_id == "SP-001").delete()
    for hours, lat, lon, current_speed, current_direction, wind_speed, wind_direction in drift_points:
        db.add(DriftPoint(
            spill_id="SP-001",
            latitude=lat,
            longitude=lon,
            hours_from_detection=hours,
            current_speed=current_speed,
            current_direction=current_direction,
            wind_speed=wind_speed,
            wind_direction=wind_direction,
        ))
    db.commit()

    # -----------------------------
    # 3. Historic AIS track reconstruction around origin window
    # -----------------------------
    tracks = {
        "419001234": [
            (-6, 10.455, 74.875), (-3, 10.438, 74.850), (0, 10.421, 74.835),
            (3, 10.415, 74.828), (6, 10.410, 74.820),
        ],
        "419005678": [
            (-6, 10.470, 74.900), (-3, 10.460, 74.875), (0, 10.450, 74.855),
            (3, 10.445, 74.845), (6, 10.440, 74.835),
        ],
        "419009876": [
            (-6, 10.600, 75.000), (-3, 10.570, 74.960), (0, 10.540, 74.910),
            (3, 10.525, 74.890), (6, 10.510, 74.870),
        ],
    }
    db.query(VesselTrackPoint).delete()
    for mmsi, points in tracks.items():
        vessel = db.query(Vessel).filter(Vessel.mmsi == mmsi).first()
        for hours, lat, lon in points:
            db.add(VesselTrackPoint(
                mmsi=mmsi,
                timestamp_hours_from_origin=hours,
                latitude=lat,
                longitude=lon,
                speed_knots=vessel.speed_knots if vessel else None,
                course=vessel.course if vessel else None,
            ))
    db.commit()

    # -----------------------------
    # 4. Explainable attribution scoring
    # -----------------------------
    candidate_inputs = [
        {
            "mmsi": "419001234", "vessel_name": "OCEAN STAR", "latitude": 10.420,
            "longitude": 74.835, "origin_latitude": 10.420, "origin_longitude": 74.800,
            "time_difference_hours": 1.2, "course": 245.0, "expected_course": 250.0,
            "behavioral_anomaly_score": 0.82,
        },
        {
            "mmsi": "419005678", "vessel_name": "SEA HORIZON", "latitude": 10.450,
            "longitude": 74.855, "origin_latitude": 10.420, "origin_longitude": 74.800,
            "time_difference_hours": 3.5, "course": 180.0, "expected_course": 250.0,
            "behavioral_anomaly_score": 0.58,
        },
        {
            "mmsi": "419009876", "vessel_name": "MARINE EXPRESS", "latitude": 10.540,
            "longitude": 74.910, "origin_latitude": 10.420, "origin_longitude": 74.800,
            "time_difference_hours": 7.8, "course": 270.0, "expected_course": 250.0,
            "behavioral_anomaly_score": 0.31,
        },
    ]
    ranked = rank_vessels(candidate_inputs)

    for item in ranked:
        attribution_id = f"ATTR-{item['mmsi'][-3:]}"
        existing = db.query(VesselAttribution).filter(VesselAttribution.id == attribution_id).first()
        values = dict(
            id=attribution_id,
            spill_id="SP-001",
            mmsi=item["mmsi"],
            attribution_score=item["attribution_score"],
            distance_km=item["distance_km"],
            time_difference_hours=item["time_difference_hours"],
            trajectory_match_score=item["trajectory_match_score"],
            behavioral_anomaly_score=item["behavioral_anomaly_score"],
        )
        if existing:
            for key, value in values.items():
                if key != "id":
                    setattr(existing, key, value)
        else:
            db.add(VesselAttribution(**values))
    db.commit()

    # -----------------------------
    # 5. Probable origin + uncertainty region
    # -----------------------------
    origin = db.query(SpillOrigin).filter(SpillOrigin.spill_id == "SP-001").first()
    origin_geometry = from_shape(Point(74.800, 10.420), srid=4326)
    if origin:
        origin.geometry = origin_geometry
        origin.uncertainty_km = 8.5
        origin.method = "drift_hindcast"
    else:
        db.add(SpillOrigin(
            id="ORIGIN-001",
            spill_id="SP-001",
            geometry=origin_geometry,
            uncertainty_km=8.5,
            method="drift_hindcast",
        ))
    db.commit()

    print("OCEANNOVA complete offshore investigation demo data updated successfully.")
    print("Pipeline: detect -> characterize -> hindcast/forecast -> reconstruct AIS -> filter -> rank")
finally:
    db.close()
