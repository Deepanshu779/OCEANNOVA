from app.core.database import SessionLocal

from app.models.drift import DriftPoint
from app.models.vessel import Vessel
from app.models.attribution import VesselAttribution
from app.models.origin import SpillOrigin

from geoalchemy2.shape import from_shape
from shapely.geometry import Point


db = SessionLocal()


# -----------------------------
# 1. Create sample vessels
# -----------------------------

vessels = [
    Vessel(
        mmsi="419001234",
        vessel_name="OCEAN STAR",
        latitude=10.72,
        longitude=76.08,
        speed_knots=12.5,
        course=245.0,
    ),
    Vessel(
        mmsi="419005678",
        vessel_name="SEA HORIZON",
        latitude=10.65,
        longitude=76.20,
        speed_knots=9.8,
        course=180.0,
    ),
    Vessel(
        mmsi="419009876",
        vessel_name="MARINE EXPRESS",
        latitude=10.85,
        longitude=75.95,
        speed_knots=15.2,
        course=270.0,
    ),
]

for vessel in vessels:
    existing = db.query(Vessel).filter(
        Vessel.mmsi == vessel.mmsi
    ).first()

    if not existing:
        db.add(vessel)

# Commit vessels before creating attribution records
db.commit()

# -----------------------------
# 2. Create sample drift path
# -----------------------------

drift_points = [
    DriftPoint(
        spill_id="SP-001",
        latitude=10.710,
        longitude=76.050,
        hours_from_detection=0,
        current_speed=1.2,
        current_direction=245,
        wind_speed=8.5,
        wind_direction=230,
    ),
    DriftPoint(
        spill_id="SP-001",
        latitude=10.725,
        longitude=76.065,
        hours_from_detection=6,
        current_speed=1.3,
        current_direction=248,
        wind_speed=8.8,
        wind_direction=232,
    ),
    DriftPoint(
        spill_id="SP-001",
        latitude=10.740,
        longitude=76.082,
        hours_from_detection=12,
        current_speed=1.4,
        current_direction=250,
        wind_speed=9.0,
        wind_direction=235,
    ),
    DriftPoint(
        spill_id="SP-001",
        latitude=10.758,
        longitude=76.100,
        hours_from_detection=18,
        current_speed=1.3,
        current_direction=252,
        wind_speed=9.2,
        wind_direction=237,
    ),
    DriftPoint(
        spill_id="SP-001",
        latitude=10.775,
        longitude=76.120,
        hours_from_detection=24,
        current_speed=1.4,
        current_direction=255,
        wind_speed=9.5,
        wind_direction=240,
    ),
]

for point in drift_points:
    db.add(point)


# -----------------------------
# 3. Create attribution scores
# -----------------------------

attributions = [
    VesselAttribution(
        id="ATTR-001",
        spill_id="SP-001",
        mmsi="419001234",
        attribution_score=0.91,
        distance_km=3.4,
        time_difference_hours=1.2,
        trajectory_match_score=0.94,
        behavioral_anomaly_score=0.82,
    ),
    VesselAttribution(
        id="ATTR-002",
        spill_id="SP-001",
        mmsi="419005678",
        attribution_score=0.68,
        distance_km=8.7,
        time_difference_hours=3.5,
        trajectory_match_score=0.71,
        behavioral_anomaly_score=0.58,
    ),
    VesselAttribution(
        id="ATTR-003",
        spill_id="SP-001",
        mmsi="419009876",
        attribution_score=0.42,
        distance_km=17.2,
        time_difference_hours=7.8,
        trajectory_match_score=0.39,
        behavioral_anomaly_score=0.31,
    ),
]

for attribution in attributions:
    existing = db.query(VesselAttribution).filter(
        VesselAttribution.id == attribution.id
    ).first()

    if not existing:
        db.add(attribution)

# -----------------------------
# 4. Create probable spill origin
# -----------------------------

origin = db.query(SpillOrigin).filter(
    SpillOrigin.spill_id == "SP-001"
).first()

if not origin:
    origin = SpillOrigin(
        id="ORIGIN-001",
        spill_id="SP-001",
        geometry=from_shape(
            Point(76.035, 10.695),
            srid=4326
        ),
        uncertainty_km=8.5,
        method="drift_hindcast"
    )

    db.add(origin)

db.commit()

db.commit()
db.close()

print("OCEANNOVA sample investigation data inserted successfully.")