"""
OCEANNOVA
Real AI Detection -> Drift Hindcast / Forecast

Consumes the centroid produced by the real Sentinel-1
segmentation + look-alike filtering pipeline.

IMPORTANT:
The current/wind values below are prototype demonstration
inputs. They are NOT claimed to be measured environmental
conditions for the Sentinel-1 acquisition.
"""

from pathlib import Path
import json
import math
from datetime import datetime, timezone


# ============================================================
# PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]

CHARACTERIZATION_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "ai_predictions"
    / "SP-001_characterization.json"
)

OUTPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "ai_predictions"
    / "SP-001_real_drift.json"
)


# ============================================================
# DEMONSTRATION ENVIRONMENTAL INPUTS
# ============================================================

CURRENT_EAST_MS = 0.20
CURRENT_NORTH_MS = 0.10

WIND_EAST_MS = 5.0
WIND_NORTH_MS = 2.0

WIND_DRIFT_FACTOR = 0.02

BACKWARD_HOURS = 12
FORWARD_HOURS = 12

STEP_HOURS = 1

UNCERTAINTY_KM = 8.5


# ============================================================
# GEO HELPERS
# ============================================================

EARTH_RADIUS_M = 6_371_000.0


def meters_to_latlon(
    latitude,
    longitude,
    east_m,
    north_m
):

    lat_rad = math.radians(
        latitude
    )

    new_lat = (
        latitude
        + math.degrees(
            north_m
            / EARTH_RADIUS_M
        )
    )

    cos_lat = max(
        math.cos(lat_rad),
        1e-8
    )

    new_lon = (
        longitude
        + math.degrees(
            east_m
            / (
                EARTH_RADIUS_M
                * cos_lat
            )
        )
    )

    return new_lat, new_lon


# ============================================================
# EFFECTIVE VELOCITY
# ============================================================

def effective_velocity():

    east = (
        CURRENT_EAST_MS
        + WIND_EAST_MS
        * WIND_DRIFT_FACTOR
    )

    north = (
        CURRENT_NORTH_MS
        + WIND_NORTH_MS
        * WIND_DRIFT_FACTOR
    )

    return east, north


# ============================================================
# SIMULATE TRAJECTORY
# ============================================================

def simulate(
    start_lat,
    start_lon,
    start_hour,
    end_hour,
    east_ms,
    north_ms
):

    points = []

    lat = start_lat
    lon = start_lon

    direction = (
        1
        if end_hour >= start_hour
        else -1
    )

    hour = start_hour

    while True:

        points.append({
            "hours_from_detection": hour,
            "latitude": lat,
            "longitude": lon
        })

        if hour == end_hour:
            break

        delta_hours = (
            STEP_HOURS
            * direction
        )

        east_m = (
            east_ms
            * 3600
            * delta_hours
        )

        north_m = (
            north_ms
            * 3600
            * delta_hours
        )

        lat, lon = meters_to_latlon(
            lat,
            lon,
            east_m,
            north_m
        )

        hour += delta_hours

    return points


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 70)
    print(
        "OCEANNOVA - REAL AI TO DRIFT INTEGRATION"
    )
    print("=" * 70)

    # --------------------------------------------------------
    # Load AI characterization
    # --------------------------------------------------------

    with open(
        CHARACTERIZATION_FILE,
        "r",
        encoding="utf-8"
    ) as f:

        characterization = json.load(f)

    centroid = characterization[
        "centroid"
    ]

    detection = characterization[
        "detection"
    ]

    latitude = float(
        centroid["latitude"]
    )

    longitude = float(
        centroid["longitude"]
    )

    print()
    print("REAL AI DETECTION")
    print("-" * 70)

    print(
        f"Latitude  : {latitude:.6f}"
    )

    print(
        f"Longitude : {longitude:.6f}"
    )

    print(
        f"Area      : "
        f"{detection['area_km2']:.4f} km²"
    )

    print(
        f"Confidence: "
        f"{detection['mean_ai_confidence']:.4f}"
    )

    # --------------------------------------------------------
    # Effective environmental velocity
    # --------------------------------------------------------

    east_ms, north_ms = (
        effective_velocity()
    )

    print()
    print("ENVIRONMENTAL INPUT")
    print("-" * 70)

    print(
        f"Current east  : "
        f"{CURRENT_EAST_MS:.3f} m/s"
    )

    print(
        f"Current north : "
        f"{CURRENT_NORTH_MS:.3f} m/s"
    )

    print(
        f"Wind east     : "
        f"{WIND_EAST_MS:.3f} m/s"
    )

    print(
        f"Wind north    : "
        f"{WIND_NORTH_MS:.3f} m/s"
    )

    print(
        f"Wind factor   : "
        f"{WIND_DRIFT_FACTOR:.3f}"
    )

    print(
        f"Effective east: "
        f"{east_ms:.3f} m/s"
    )

    print(
        f"Effective north: "
        f"{north_ms:.3f} m/s"
    )

    # --------------------------------------------------------
    # Backward hindcast
    # --------------------------------------------------------

    backward = simulate(
        latitude,
        longitude,
        0,
        -BACKWARD_HOURS,
        east_ms,
        north_ms
    )

    # --------------------------------------------------------
    # Forward forecast
    # --------------------------------------------------------

    forward = simulate(
        latitude,
        longitude,
        0,
        FORWARD_HOURS,
        east_ms,
        north_ms
    )

    # --------------------------------------------------------
    # Probable origin
    # --------------------------------------------------------

    origin = backward[-1]

    print()
    print("PROBABLE ORIGIN")
    print("-" * 70)

    print(
        f"Latitude  : "
        f"{origin['latitude']:.6f}"
    )

    print(
        f"Longitude : "
        f"{origin['longitude']:.6f}"
    )

    print(
        f"Hindcast  : "
        f"{BACKWARD_HOURS} hours"
    )

    print(
        f"Uncertainty: "
        f"±{UNCERTAINTY_KM:.1f} km"
    )

    # --------------------------------------------------------
    # Build output
    # --------------------------------------------------------

    result = {

        "incident_id": (
            characterization[
                "incident_id"
            ]
        ),

        "source": {
            "type": "Sentinel-1 SAR",
            "scene": characterization[
                "source"
            ]["scene"]
        },

        "detection_centroid": {
            "latitude": latitude,
            "longitude": longitude
        },

        "environment": {

            "status": (
                "demonstration_inputs"
            ),

            "current_east_ms": (
                CURRENT_EAST_MS
            ),

            "current_north_ms": (
                CURRENT_NORTH_MS
            ),

            "wind_east_ms": (
                WIND_EAST_MS
            ),

            "wind_north_ms": (
                WIND_NORTH_MS
            ),

            "wind_drift_factor": (
                WIND_DRIFT_FACTOR
            )
        },

        "origin": {

            "latitude": (
                origin["latitude"]
            ),

            "longitude": (
                origin["longitude"]
            ),

            "uncertainty_km": (
                UNCERTAINTY_KM
            ),

            "method": (
                "backward_drift_hindcast"
            )
        },

        "hindcast": backward,

        "forecast": forward,

        "generated_at": (
            datetime.now(
                timezone.utc
            ).isoformat()
        ),

        "status": (
            "prototype_real_ai_drift_integration"
        )
    }

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            result,
            f,
            indent=2
        )

    print()
    print("=" * 70)
    print("DRIFT INTEGRATION COMPLETE")
    print("=" * 70)

    print(
        f"Hindcast points : "
        f"{len(backward)}"
    )

    print(
        f"Forecast points : "
        f"{len(forward)}"
    )

    print(
        f"Origin          : "
        f"{origin['latitude']:.6f}, "
        f"{origin['longitude']:.6f}"
    )

    print(
        f"Uncertainty     : "
        f"±{UNCERTAINTY_KM:.1f} km"
    )

    print()
    print(
        f"✓ Saved: {OUTPUT_FILE}"
    )


if __name__ == "__main__":
    main()