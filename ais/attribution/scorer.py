import pandas as pd
import numpy as np
from ais.trajectory.builder import find_closest_point
def compute_proximity_score(min_distance_km: float, max_radius_km: float = 25.0) -> float:
    # 100 if right on origin, decaying to 0 at max_radius_km
    score = max(0.0, 100.0 * (1.0 - (min_distance_km / max_radius_km)))
    return round(score, 2)

def compute_temporal_score(closest_time, estimated_spill_time, max_window_hours: float = 12.0) -> float:
    diff_hours = abs((closest_time - estimated_spill_time).total_seconds()) / 3600.0
    score = max(0.0, 100.0 * (1.0 - (diff_hours / max_window_hours)))
    return round(score, 2)

def compute_trajectory_score(track: list) -> float:
    # Higher score for vessels that altered speed/course near area
    if len(track) < 2:
        return 50.0
    speeds = [pt.get('sog', 0.0) for pt in track if pt.get('sog') is not None]
    if not speeds:
        return 50.0
    speed_variance = float(np.var(speeds))
    # Slight speed anomaly gives a moderate boost to investigative suspicion
    return min(100.0, round(50.0 + min(speed_variance * 5.0, 50.0), 2))

def score_vessel(track: list, origin_lat: float, origin_lon: float, spill_time) -> dict:
    best_pt = find_closest_point(track, origin_lat, origin_lon)
    if not best_pt:
        return None

    prox = compute_proximity_score(best_pt['distance_km'])
    temp = compute_temporal_score(pd.to_datetime(best_pt['timestamp']), spill_time)
    traj = compute_trajectory_score(track)

    # Weighted final attribution score
    final_score = round(0.50 * prox + 0.35 * temp + 0.15 * traj, 2)

    return {
        "mmsi": str(track[0]['mmsi']),
        "name": track[0].get('vessel_name', f"Vessel-{track[0]['mmsi']}"),
        "score": final_score,
        "evidence": {
            "proximity_score": prox,
            "temporal_score": temp,
            "trajectory_score": traj,
            "closest_distance_km": round(best_pt['distance_km'], 2),
            "closest_timestamp": str(best_pt['timestamp'])
        }
    }