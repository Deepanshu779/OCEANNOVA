"""Explainable AIS vessel scoring for oil-spill investigation.

This module is intentionally deterministic and transparent for the demo. It does
not claim legal responsibility; it ranks vessels by consistency with the
reconstructed spill origin and time window.
"""

from math import atan2, cos, radians, sin, sqrt


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Return great-circle distance in kilometres."""
    earth_radius_km = 6371.0088
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
    return 2 * earth_radius_km * atan2(sqrt(a), sqrt(max(0.0, 1 - a)))


def proximity_score(distance_km: float, scale_km: float = 50.0) -> float:
    """Convert distance to a 0..1 evidence score over the 50 km investigation radius."""
    return max(0.0, min(1.0, 1.0 - distance_km / scale_km))


def temporal_score(time_difference_hours: float, scale_hours: float = 12.0) -> float:
    """Convert time difference to a 0..1 evidence score."""
    return max(0.0, min(1.0, 1.0 - abs(time_difference_hours) / scale_hours))


def trajectory_match_score(
    vessel_course: float,
    expected_course: float,
) -> float:
    """Score course consistency using the smallest circular angle."""
    delta = abs((vessel_course - expected_course + 180.0) % 360.0 - 180.0)
    return max(0.0, 1.0 - delta / 180.0)


def attribution_score(
    proximity: float,
    temporal: float,
    trajectory: float,
    behavioral_anomaly: float,
) -> float:
    """Weighted explainable attribution score."""
    score = (
        0.35 * proximity
        + 0.20 * temporal
        + 0.30 * trajectory
        + 0.15 * behavioral_anomaly
    )
    return round(max(0.0, min(1.0, score)), 4)


def rank_vessels(candidates: list[dict]) -> list[dict]:
    """Filter irrelevant traffic and rank remaining candidates.

    Required candidate keys: mmsi, vessel_name, latitude, longitude,
    origin_latitude, origin_longitude, time_difference_hours, course,
    expected_course, behavioral_anomaly_score.
    """
    ranked: list[dict] = []
    for candidate in candidates:
        distance = haversine_km(
            candidate["latitude"], candidate["longitude"],
            candidate["origin_latitude"], candidate["origin_longitude"],
        )
        if distance > candidate.get("max_distance_km", 50.0):
            continue

        proximity = proximity_score(distance, candidate.get("proximity_scale_km", 50.0))
        temporal = temporal_score(candidate["time_difference_hours"])
        trajectory = trajectory_match_score(candidate["course"], candidate["expected_course"])
        behavior = max(0.0, min(1.0, candidate["behavioral_anomaly_score"]))
        score = attribution_score(proximity, temporal, trajectory, behavior)

        ranked.append({
            **candidate,
            "distance_km": round(distance, 2),
            "proximity_score": round(proximity, 4),
            "temporal_score": round(temporal, 4),
            "trajectory_match_score": round(trajectory, 4),
            "behavioral_anomaly_score": round(behavior, 4),
            "attribution_score": score,
            "relevance": "candidate",
        })

    return sorted(ranked, key=lambda item: item["attribution_score"], reverse=True)
