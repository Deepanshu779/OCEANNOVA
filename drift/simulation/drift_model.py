"""
OCEANNOVA - Task 4
Ocean Drift & Spill-Origin Prediction

MVP drift engine:
- Forward drift simulation
- Backward/hindcast tracing
- Ensemble uncertainty
- Probable origin estimation
- Timestamped trajectory
- JSON-compatible output

No external packages required.
"""

from datetime import datetime, timedelta, timezone
from math import cos, radians
import random


# ---------------------------------------------------------
# Configuration
# ---------------------------------------------------------

EARTH_METERS_PER_DEGREE = 111_320.0


def meters_to_latlon(dx_m, dy_m, latitude):
    """
    Convert movement in meters to latitude/longitude degrees.

    dx_m = east/west movement
    dy_m = north/south movement
    """

    dlat = dy_m / EARTH_METERS_PER_DEGREE

    lon_scale = EARTH_METERS_PER_DEGREE * max(
        cos(radians(latitude)), 0.01
    )

    dlon = dx_m / lon_scale

    return dlat, dlon


# ---------------------------------------------------------
# Effective drift velocity
# ---------------------------------------------------------

def effective_velocity(
    current_east,
    current_north,
    wind_east,
    wind_north,
    wind_drift_factor=0.02
):
    """
    Simplified surface oil drift model.

    Effective velocity =
        ocean current +
        wind contribution
    """

    east = current_east + wind_east * wind_drift_factor
    north = current_north + wind_north * wind_drift_factor

    return east, north


# ---------------------------------------------------------
# Forward simulation
# ---------------------------------------------------------

def simulate_forward(
    start_lat,
    start_lon,
    start_time,
    hours=6,
    time_step_minutes=30,
    current_east=0.20,
    current_north=0.10,
    wind_east=5.0,
    wind_north=2.0,
    wind_drift_factor=0.02
):
    """
    Simulate where the oil slick moves in the future.
    """

    east_velocity, north_velocity = effective_velocity(
        current_east,
        current_north,
        wind_east,
        wind_north,
        wind_drift_factor
    )

    trajectory = []

    total_steps = int(
        hours * 60 / time_step_minutes
    )

    lat = start_lat
    lon = start_lon

    current_time = start_time

    trajectory.append({
        "timestamp": current_time.isoformat(),
        "lat": round(lat, 6),
        "lon": round(lon, 6)
    })

    for _ in range(total_steps):

        seconds = time_step_minutes * 60

        dx = east_velocity * seconds
        dy = north_velocity * seconds

        dlat, dlon = meters_to_latlon(
            dx,
            dy,
            lat
        )

        lat += dlat
        lon += dlon

        current_time += timedelta(
            minutes=time_step_minutes
        )

        trajectory.append({
            "timestamp": current_time.isoformat(),
            "lat": round(lat, 6),
            "lon": round(lon, 6)
        })

    return trajectory


# ---------------------------------------------------------
# Backward / Hindcast simulation
# ---------------------------------------------------------

def backtrack_origin(
    observed_lat,
    observed_lon,
    observed_time,
    hours_back=12,
    time_step_minutes=30,
    current_east=0.20,
    current_north=0.10,
    wind_east=5.0,
    wind_north=2.0,
    wind_drift_factor=0.02
):
    """
    Trace the observed oil slick backward in time.

    This estimates a probable source region rather
    than claiming an exact spill location.
    """

    east_velocity, north_velocity = effective_velocity(
        current_east,
        current_north,
        wind_east,
        wind_north,
        wind_drift_factor
    )

    trajectory = []

    lat = observed_lat
    lon = observed_lon

    current_time = observed_time

    trajectory.append({
        "timestamp": current_time.isoformat(),
        "lat": round(lat, 6),
        "lon": round(lon, 6)
    })

    total_steps = int(
        hours_back * 60 / time_step_minutes
    )

    for _ in range(total_steps):

        seconds = time_step_minutes * 60

        dx = east_velocity * seconds
        dy = north_velocity * seconds

        dlat, dlon = meters_to_latlon(
            dx,
            dy,
            lat
        )

        # Reverse the movement
        lat -= dlat
        lon -= dlon

        current_time -= timedelta(
            minutes=time_step_minutes
        )

        trajectory.append({
            "timestamp": current_time.isoformat(),
            "lat": round(lat, 6),
            "lon": round(lon, 6)
        })

    return trajectory


# ---------------------------------------------------------
# Uncertainty Ensemble
# ---------------------------------------------------------

def estimate_origin(
    observed_lat,
    observed_lon,
    observed_time,
    hours_back=12,
    ensemble_size=50
):
    """
    Run multiple backward simulations with small
    environmental perturbations.

    This gives an uncertainty region.
    """

    origins = []

    for _ in range(ensemble_size):

        # Environmental uncertainty
        current_east = 0.20 + random.gauss(0, 0.04)
        current_north = 0.10 + random.gauss(0, 0.04)

        wind_east = 5.0 + random.gauss(0, 1.0)
        wind_north = 2.0 + random.gauss(0, 1.0)

        trajectory = backtrack_origin(
            observed_lat,
            observed_lon,
            observed_time,
            hours_back=hours_back,
            current_east=current_east,
            current_north=current_north,
            wind_east=wind_east,
            wind_north=wind_north
        )

        origin = trajectory[-1]

        origins.append(origin)

    # Average origin
    avg_lat = sum(
        point["lat"] for point in origins
    ) / len(origins)

    avg_lon = sum(
        point["lon"] for point in origins
    ) / len(origins)

    # Approximate uncertainty using maximum
    # distance in latitude/longitude space.
    max_distance_km = 0.0

    for point in origins:

        dlat_km = (
            point["lat"] - avg_lat
        ) * 111.32

        dlon_km = (
            point["lon"] - avg_lon
        ) * 111.32 * cos(
            radians(avg_lat)
        )

        distance = (
            dlat_km ** 2 +
            dlon_km ** 2
        ) ** 0.5

        max_distance_km = max(
            max_distance_km,
            distance
        )

    return {
        "lat": round(avg_lat, 6),
        "lon": round(avg_lon, 6),
        "uncertainty_km": round(
            max_distance_km,
            2
        ),
        "ensemble_size": ensemble_size
    }


# ---------------------------------------------------------
# Complete spill analysis
# ---------------------------------------------------------

def analyze_spill(
    spill_id,
    observed_lat,
    observed_lon,
    observed_time
):
    """
    Complete Task 4 pipeline.
    """

    # Backward origin estimation
    origin = estimate_origin(
        observed_lat,
        observed_lon,
        observed_time,
        hours_back=12,
        ensemble_size=50
    )

    # Deterministic backward trajectory
    backward = backtrack_origin(
        observed_lat,
        observed_lon,
        observed_time,
        hours_back=12
    )

    # Forward forecast
    forward = simulate_forward(
        observed_lat,
        observed_lon,
        observed_time,
        hours=6
    )

    origin_time = (
        observed_time -
        timedelta(hours=12)
    )

    result = {
        "spill_id": spill_id,

        "origin": {
            "lat": origin["lat"],
            "lon": origin["lon"],
            "uncertainty_km": origin["uncertainty_km"],
            "confidence": "MEDIUM"
        },

        "origin_time_window": {
            "start": origin_time.isoformat(),
            "end": observed_time.isoformat()
        },

        "observed_spill": {
            "lat": observed_lat,
            "lon": observed_lon,
            "timestamp": observed_time.isoformat()
        },

        "backward_hindcast": {
            "type": "LineString",
            "coordinates": [
                [
                    point["lon"],
                    point["lat"]
                ]
                for point in backward
            ],
            "timestamps": [
                point["timestamp"]
                for point in backward
            ]
        },

        "forward_forecast": {
            "type": "LineString",
            "coordinates": [
                [
                    point["lon"],
                    point["lat"]
                ]
                for point in forward
            ],
            "timestamps": [
                point["timestamp"]
                for point in forward
            ]
        },

        "environment": {
            "current_east_ms": 0.20,
            "current_north_ms": 0.10,
            "wind_east_ms": 5.0,
            "wind_north_ms": 2.0,
            "wind_drift_factor": 0.02
        },

        "model": {
            "type": "Lagrangian surface drift MVP",
            "method": "current + wind-driven advection",
            "ensemble_runs": 50
        }
    }

    return result


# ---------------------------------------------------------
# Test
# ---------------------------------------------------------

if __name__ == "__main__":

    observed_time = datetime(
        2026,
        9,
        6,
        12,
        0,
        tzinfo=timezone.utc
    )

    result = analyze_spill(
        spill_id="SP-001",
        observed_lat=10.710,
        observed_lon=76.050,
        observed_time=observed_time
    )

    import json

    print(
        json.dumps(
            result,
            indent=2
        )
    )