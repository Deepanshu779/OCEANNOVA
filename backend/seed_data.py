from app.core.database import SessionLocal

from app.models.spill import Spill
from app.models.drift import DriftPoint
from app.models.vessel import Vessel
from app.models.attribution import VesselAttribution
from app.models.origin import SpillOrigin

from geoalchemy2.shape import from_shape
from shapely.geometry import Point


db = SessionLocal()


# -----------------------------
# 0. Create/update demo spill
# -----------------------------
spill = db.query(Spill).filter(
    Spill.spill_id == "SP-001"
).first()

spill_geometry = from_shape(
    Point(74.850, 10.450),
    srid=4326
)

if not spill:
    spill = Spill(
        spill_id="SP-001",
        confidence=0.94,
        area_km2=14.7,
        geometry=spill_geometry,
    )
    db.add(spill)
else:
    spill.confidence = 0.94
    spill.area_km2 = 14.7
    spill.geometry = spill_geometry

db.commit()


# -----------------------------
# 1. Create/update sample vessels
# -----------------------------
# These are demonstration AIS candidates positioned offshore.
vessels = [
    Vessel(
        mmsi="419001234",
        vessel_name="OCEAN STAR",
        latitude=10.420,
        longitude=74.835,
        speed_knots=12.5,
        course=245.0,
    ),
    Vessel(
        mmsi="419005678",
        vessel_name="SEA HORIZON",
        latitude=10.450,
        longitude=74.855,
        speed_knots=9.8,
        course=180.0,
    ),
    Vessel(
        mmsi="419009876",
        vessel_name="MARINE EXPRESS",
        latitude=10.540,
        longitude=74.910,
        speed_knots=15.2,
        course=270.0,
    ),
]

for vessel in vessels:
    existing = db.query(Vessel).filter(
        Vessel.mmsi == vessel.mmsi
    ).first()

    if existing:
        existing.vessel_name = vessel.vessel_name
        existing.latitude = vessel.latitude
        existing.longitude = vessel.longitude
        existing.speed_knots = vessel.speed_knots
        existing.course = vessel.course
    else:
        db.add(vessel)

# Commit vessels before creating attribution records
db.commit()


# -----------------------------
# 2. Create sample drift path
# -----------------------------
drift_points = [
    DriftPoint(
        spill_id="SP-001",
        latitude=10.420,
        longitude=74.800,
        hours_from_detection=-6,
        current_speed=1.2,
        current_direction=245,
        wind_speed=8.5,
        wind_direction=230,
    ),
    DriftPoint(
        spill_id="SP-001",
        latitude=10.435,
        longitude=74.820,
        hours_from_detection=-3,
        current_speed=1.3,
        current_direction=248,
        wind_speed=8.8,
        wind_direction=232,
    ),
    DriftPoint(
        spill_id="SP-001",
        latitude=10.450,
        longitude=74.850,
        hours_from_detection=0,
        current_speed=1.4,
        current_direction=250,
        wind_speed=9.0,
        wind_direction=235,
    ),
    DriftPoint(
        spill_id="SP-001",
        latitude=10.465,
        longitude=74.875,
        hours_from_detection=6,
        current_speed=1.3,
        current_direction=252,
        wind_speed=9.2,
        wind_direction=237,
    ),
    DriftPoint(
        spill_id="SP-001",
        latitude=10.480,
        longitude=74.900,
        hours_from_detection=12,
        current_speed=1.4,
        current_direction=255,
        wind_speed=9.5,
        wind_direction=240,
    ),
]

# Remove existing demo drift points for this spill
db.query(DriftPoint).filter(
    DriftPoint.spill_id == "SP-001"
).delete()

for point in drift_points:
    db.add(point)

db.commit()


# -----------------------------
# 3. Create/update attribution scores
# -----------------------------
attributions = [
    VesselAttribution(
        id="ATTR-001",
        spill_id="SP-001",
        mmsi="419001234",
        attribution_score=0.91,
        distance_km=3.8,
        time_difference_hours=1.2,
        trajectory_match_score=0.94,
        behavioral_anomaly_score=0.82,
    ),
    VesselAttribution(
        id="ATTR-002",
        spill_id="SP-001",
        mmsi="419005678",
        attribution_score=0.68,
        distance_km=6.9,
        time_difference_hours=3.5,
        trajectory_match_score=0.71,
        behavioral_anomaly_score=0.58,
    ),
    VesselAttribution(
        id="ATTR-003",
        spill_id="SP-001",
        mmsi="419009876",
        attribution_score=0.42,
        distance_km=17.9,
        time_difference_hours=7.8,
        trajectory_match_score=0.39,
        behavioral_anomaly_score=0.31,
    ),
]

for attribution in attributions:
    existing = db.query(VesselAttribution).filter(
        VesselAttribution.id == attribution.id
    ).first()

    if existing:
        existing.spill_id = attribution.spill_id
        existing.mmsi = attribution.mmsi
        existing.attribution_score = attribution.attribution_score
        existing.distance_km = attribution.distance_km
        existing.time_difference_hours = attribution.time_difference_hours
        existing.trajectory_match_score = attribution.trajectory_match_score
        existing.behavioral_anomaly_score = attribution.behavioral_anomaly_score
    else:
        db.add(attribution)


# -----------------------------
# 4. Create/update probable spill origin
# -----------------------------
origin = db.query(SpillOrigin).filter(
    SpillOrigin.spill_id == "SP-001"
).first()

origin_geometry = from_shape(
    Point(74.800, 10.420),
    srid=4326
)

if origin:
    origin.geometry = origin_geometry
    origin.uncertainty_km = 8.5
    origin.method = "drift_hindcast"
else:
    origin = SpillOrigin(
        id="ORIGIN-001",
        spill_id="SP-001",
        geometry=origin_geometry,
        uncertainty_km=8.5,
        method="drift_hindcast",
    )
    db.add(origin)

db.commit()
db.close()

print("OCEANNOVA offshore India demo investigation data updated successfully.")
